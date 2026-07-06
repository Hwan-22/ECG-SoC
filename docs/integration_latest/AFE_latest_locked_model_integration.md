# 1.5 최신 locked model 재통합 검증 (AFE → structural_guarded_silent_aff_1008710)

> 제27회 반도체설계대전 · 한양대 · 담당: 이수환(AFE) · 2026-07-06
> 요청 1.5: "최신 locked digital model 기준으로도 AFE→분류 path가 유지되는가"
> 결과: **우리 AFE+ADC 출력이 최신 locked model에서 bit-exact 재현 — final_pred/final_membrane 모두 일치**

---

## 0. 핵심 결론 (3줄)
1. 최신 locked model(`structural_guarded_silent_aff_1008710`)의 검증 입력 자체가 **우리 AFE+ADC 출력을 30분 윈도우로 자른 것**(`fullrec_afe_30min_...`) — 즉 test 80.56% / board replay 36/36은 이미 **우리 AFE 경로 위**의 결과다.
2. 우리 `fullrec_afe` ARR 3레코드의 w000(첫 30분)을 최신 locked RTL(`snn_ecg_30min_final_top`)에 Vivado XSim으로 직접 태워, 팀원 골든(fulltop XSim = board replay 정본)과 **final_pred 3/3, final_membrane 4값 전부 bit-exact 일치**.
3. **구버전 통합에서 유일하게 실패했던 ARR record 105(ARR→AFF 플립)가 최신 모델에서는 정답(ARR)으로 해소** — 구 통합 보고서의 "필터링 데이터 재학습" 권고가 반영된 것으로 확인.

---

## 1. 배경 — 왜 재통합이 필요했나
기존 `docs/integration_report.md`(2026-06-21)의 mixed-signal 통합은 **구버전 60초 core `snn_ecg_model_a_plus_core`** 기준이었고, ARR(record 105)이 AFE 대역통과 누적효과로 ARR→AFF 오분류됨을 보고했다.
그러나 팀원의 최종 모델은 완전히 다른 **30분 Snapshot→Final Membrane 아키텍처**(`snn_ecg_30min_final_top`, locked id `structural_guarded_silent_aff_1008710`)다. 구 통합 결과만으로는 최신 모델을 대변하지 못하므로 재검증이 필요했다.

## 2. 결정적 사실 — 최신 모델은 이미 우리 AFE 위에서 검증됨
최신 모델의 XSim/board replay 입력 경로(`digital_block/tools/board_replay/run_locked_fulltop_xsim_cases.py`, `reports/final/strict_recordwise/structural_final_test_predictions.csv`)를 분석한 결과, 입력이 전부
`fullrec_afe_30min_annotation_valid_balanced/<split>/<class>/<rec>/<rec>_30min_wXXX.mem` 형식이다.
`fullrec_afe` = **우리가 생성·전달한 full-record AFE+ADC stream**(afe_emu 파이프라인, `docs/AFE_fullrecord_conversion_conditions.md`)을 30분 윈도우로 자른 것.
∴ **최신 locked model의 최종 성능(final_test chunk 29/36=80.56%, board replay final_pred 36/36·final_mem exact 36/36)은 이미 우리 AFE+ADC 경로 위에서 산출된 것**이다. 형식도 정확히 일치: signed 12-bit, mid-code 2048, 1 kSPS (1.1 headroom 스캔·2.1 non-ideal에서 검증한 우리 ADC 사양과 동일).

## 3. 직접 재현 (우리 AFE 출력 → 최신 locked RTL XSim)
### 방법
- mitdb ARR 레코드는 정확히 30.1분(1,805,555 샘플)이라 **w000 = 첫 1,800,000 샘플이 명확** → windowing 모호성 없음.
- 우리 `datasets/fullrec_afe*/…/ARR/{105,118,214}.mem`의 첫 1.8M 샘플로 w000 입력 생성.
- 최신 locked RTL(`rtl/core/*`+`final_membrane_layer.v`+`snn_ecg_30min_final_top.v`) + `sim/tb_snn_ecg_30min_chunk_dataset.v`를 **Vivado 2020.2 XSim**으로 컴파일·elaborate·시뮬(케이스당 1.8M 샘플 스트리밍, 30 snapshot→final membrane).
- 출력 `final_pred_class`·`final_mem_{NSR,CHF,ARR,AFF}`를 팀원 골든과 대조.
- 재현 하네스: `xsim_harness/{manifest.txt, tb_locked.v, sources.prj, compare.py}`, 결과 `our_afe_w000_xsim_result.csv`.

### 결과 — bit-exact
| case | record | 우리 AFE→pred | 골든 pred | 우리 final_mem (N/C/A/F) | 골든 final_mem | 일치 |
|---|---|---|---|---|---|---|
| 37 | ARR 105 | ARR | ARR | 8 / 1 / 21 / 0 | 8 / 1 / 21 / 0 | ✅ bit-exact |
| 45 | ARR 118 | ARR | ARR | 7 / 1 / 21 / 1 | 7 / 1 / 21 / 1 | ✅ bit-exact |
| 56 | ARR 214 | ARR | ARR | 0 / 0 / 30 / 0 | 0 / 0 / 30 / 0 | ✅ bit-exact |

- 전 케이스 `samples_driven=1,800,000`, `windows=30`, `decisions=1` (전송·스냅샷·판정 정상).
- 골든 출처: `digital_block/reports/final/fulltop_xsim_final_test_36/locked_class_cases_fulltop_xsim_predictions.csv` (board replay 36/36과 일치한 정본).
- (참고) prof cycle 수는 driving cadence 차이로 다르나(우리 3.60M vs 골든 5.40M), 모델은 샘플 도메인에서 결정적이라 **분류 결과는 완전 동일**.

## 4. ARR 105 — 구 통합 실패가 해소됨
구 통합(`integration_report.md §7`): record 105 ARR이 AFE 경로에서 **ARR→AFF 플립**(score_arr 62704 → score_aff 33899로 역전), AFE-측 수정으로 해결 불가, 유일 해법=필터링 데이터 재학습(알고리즘팀).
최신 locked model: 동일 record 105의 우리 AFE w000 입력에서 **final_pred=ARR(정답), membrane NSR8/CHF1/ARR21/AFF0** (ARR 압도적 우세). → 구 통합 권고가 최신 모델에 반영되어 **취약 케이스가 실제로 해소**됨을 우리 AFE 출력으로 재현 확인.

## 5. 보고 문구
> "AFE+ADC XMODEL 출력이 최신 locked SNN Accelerator IP(`structural_guarded_silent_aff_1008710`) 입력 형식(signed 12-bit, mid-code 2048, 1 kSPS)과 일치하며, 최신 full-top RTL을 우리 AFE 출력으로 XSim 구동한 결과 final_pred·final_membrane이 팀원 골든과 bit-exact 일치함을 확인했다. 구버전 통합의 ARR-105 오분류는 최신 locked model에서 해소되었다."

## 6. 범위/한계
- 직접 재현은 windowing이 명확한 **ARR w000 3케이스**로 수행(mitdb=30분=단일 윈도우). NSR/CHF/AFF는 다-윈도우(24h급)라 `wXXX` 오프셋 정의(팀원 `fullrec_afe_30min_annotation_valid_balanced` 빌드 매니페스트)가 있어야 개별 chunk를 bit-exact 재현 가능 — 매니페스트 확보 시 36 chunk 전체로 확장 가능.
- 단, §2에서 보였듯 36 chunk **전체가 이미 우리 AFE 출력 기반**이므로, 전체 재현은 확증 절차이지 통합 성립 여부의 미결 사안이 아니다.

## 7. 재현 방법
```
# 1) w000 입력 생성 (우리 fullrec_afe ARR에서 첫 1.8M 샘플)
head -n 1800000 datasets/fullrec_afe_remaining/test/ARR/105.mem  > mems/105_w000.mem   # 118, 214 동일
# 2) Vivado 2020.2 XSim (Windows)
xvlog --nolog -i rtl -prj sources.prj
xelab --nolog -debug typical tb_locked -s tb_locked
xsim  tb_locked --nolog -tclbatch run.tcl            # -> result.csv
# 3) 골든 대조
python3 xsim_harness/compare.py
```
