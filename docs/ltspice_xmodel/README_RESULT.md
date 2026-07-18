# LTspice ↔ XMODEL ADC 비교 결과 (patient100, 10 s, 10,000 samples)

> 담당: 이수환 (XMODEL AFE+ADC verification) · 실행일 2026-07-18
> 요청 기준: `LTSPICE_TEAM_HANDOFF_2026-07-16_v2.zip`
> **두 시뮬레이션 모두 이번에 새로 실행**했으며, ZIP에 포함된 기존 결과는 사용하지 않았다.

---

## 1. 결론 요약

| 항목 | 결과 |
|---|---|
| 구조 정합 (샘플수/시각/주기/lag) | **완전 일치** — 10,000 / 10,000, 1 ms ~ 10.000 s, 1 ms, best lag **0** |
| Zero-lag correlation | **0.999518** |
| Mean error | **+0.022 LSB** (편향 없음) |
| RMS error | **1.302 LSB** |
| ±1 LSB 이내 | **91.19 %** |
| Bit-exact | 56.49 % |
| Clipping | **0** (양쪽 모두) |
| 판정 | **CORRELATED** — 구조·타이밍·극성·스케일 완전 정합, 잔차는 sub-2-LSB 수준 |

두 결과는 **동일 파형·동일 타이밍**이며, 잔차는 아래 §5에서 규명한 대로
**입력 50 µs 격자 정렬 차이(0.17 %)와 급경사 구간에서의 solver 양자화 차이**로 설명된다.
AFE/ADC 모델링(이득·필터·오프셋 변환·양자화식) 불일치는 **없다**.

---

## 2. 실행 내용 (신규)

### 2.1 XMODEL
| 항목 | 값 |
|---|---|
| Git commit SHA | **`4756a5086023547328ef44fd5fd87da3c250dc39`** |
| repo | `github.com/Hwan-22/ECG-SoC` (main) |
| DUT | `analog/ecg_afe_xmodel.sv` (sha256(LF) `79191b79…0846`) |
| TB | `reference/xmodel_alignment/tb_xmodel_correlation.sv` (팀 제공) |
| 시뮬레이터 | Questa Intel Starter FPGA Edition 2024.3 + XMODEL 2025.12 |
| 입력 | `patient100_ecg_10s.txt` (360 Hz, 3,600 pts), 50 µs마다 hold 갱신, ECG+=patient / ECG−=0 |
| 출력 | `xmodel/xmodel_adc_nominal.txt` (10,000 samples, `index code aperture_ns`) |

> handoff의 `xmodel_fixed_4756a50_subset` DUT는 CRLF 차이만 있을 뿐 **commit 4756a50의 파일과 내용 100 % 동일**함을 해시로 확인(CR 제거 후 동일 sha256, diff 0줄).

### 2.2 LTspice
| 항목 | 값 |
|---|---|
| 실행기 | **LTspiceXVII 17.0.37.0** (batch `-b`) |
| 넷리스트 | `xma_adc_10s_fresh.cir`, `.tran 0 10.001 0 5u` |
| 결과 | 2,417,098 points, 10.001 s 전구간, 오류/수렴실패 0 |
| 입력 | `patient100_xmodel_drive_10s.txt` (50 µs 격자 staircase PWL) |
| 경로 | `AFE_OUT → S1(SW_ADC) → C7(10 nF hold) → ADC_HOLD → ADC_CLIP → ADC_CODE → ADC_SIGNED` |
| 출력 | `ltspice/ltspice_xmodel_aligned_adc_samples.csv`, `ltspice_track_hold_adc_signed.mem` |

**⚠️ 실행 환경 관련 고지 (2건, 결과 해석에 영향 없음)**

1. 원본 `FULL_AFE_ADC_SH_xmodel_aligned.asc`는 **"Version 4.1"**(LTspice 26 포맷)이라 이쪽 환경의 LTspiceXVII로는 열리지 않았다. 그래서 **LTspice 26이 바로 그 .asc에서 생성해 ZIP에 포함시킨 넷리스트**(`xma_nominal_convergence_10u.cir`)를 사용하고, `.asc`에 명시된 조건과 동일하게 `.tran 0 10.001 0 5u`로만 변경했다. 소자·토폴로지·파라미터·ADC 체인은 원본과 동일하다.
2. `XOpAmp_XMODEL.lib`의 `BERR` 라인이 중첩 중괄호(`V={A_OL*(…)}`) 형태라 XVII에서 파싱 실패(op-amp 6개 전부 `undefined symbol`)했다. **수식 의미가 동일한 XVII 호환 형태**(`V={A_OL}*(…)+{A_CM}*(…)`)로 바꾼 `XOpAmp_XMODEL_XVII.lib`를 사용했다. 원본 lib는 수정하지 않았다.

> LTspice 26 환경에서 원본 `.asc`를 그대로 재실행하면 이 2건은 불필요하다. 필요하면 그쪽에서 교차 확인해 주면 좋겠다.

---

## 3. 공통 조건 검증

| 조건 | 요구 | XMODEL | LTspice | 일치 |
|---|---|---|---|---|
| 입력 | patient100 10 s | ✔ | ✔ | ✔ |
| 시뮬레이션 시간 | 10 s | 10.000 s | 10.001 s (여유) | ✔ |
| 첫 샘플 | 1 ms | 0.001 s | 0.001 s | ✔ |
| 마지막 샘플 | 10.000 s | 10.000 s | 10.000 s | ✔ |
| 총 샘플 수 | 10,000 | 10,000 | 10,000 | ✔ |
| 샘플 주기 | 1 kSPS | 1 ms | 1 ms | ✔ |
| ADC 해상도/범위 | 12-bit / ±1.65 V | ✔ | ✔ | ✔ |
| 양자화식 | `floor((V+1.65)/3.3×4095)` clip[0,4095] | ✔ | ✔ (B2) | ✔ |
| signed 변환 | code − 2048 | ✔ | ✔ (B3) | ✔ |

---

## 4. 정량 비교 요약표

**공식 비교: XMODEL `adc_signed` ↔ LTspice `th_adc_signed` (Sample-and-Hold 경로).** 오차 = LTspice − XMODEL.

| 비교 항목 | 전체 0~10 s | 정착 1~10 s |
|---|---|---|
| XMODEL sample count | 10,000 | 9,001 |
| LTspice sample count | 10,000 | 9,001 |
| First sample time | 0.001 s | 1.000 s |
| Last sample time | 10.000 s | 10.000 s |
| Sample period | 0.001 s | 0.001 s |
| XMODEL signed min/max | −96 / 302 | −68 / 302 |
| LTspice signed min/max | −96 / 303 | −68 / 303 |
| Clipping count | 0 | 0 |
| Mean error [LSB] | +0.0221 | +0.0270 |
| MAE [LSB] | 0.6445 | 0.6549 |
| RMS error [LSB] | 1.3020 | 1.3243 |
| Maximum absolute error [LSB] | 13 | 13 |
| Zero-lag correlation | 0.999518 | 0.999502 |
| Best lag [sample] | **0** | **0** |
| Best-lag correlation | 0.999518 | 0.999502 |
| Bit-exact sample count | 5,649 | 5,061 |
| Bit-exact match ratio [%] | 56.49 | 56.23 |

**오차 분포**

| 범위 | 샘플 수 | 비율 |
|---|---|---|
| |err| = 0 (bit-exact) | 5,649 | 56.49 % |
| |err| ≤ 1 LSB | 9,119 | **91.19 %** |
| |err| ≤ 2 LSB | 9,556 | 95.56 % |
| |err| ≤ 3 LSB | 9,720 | 97.20 % |
| |err| ≤ 5 LSB | 9,874 | 98.74 % |
| |err| ≤ 10 LSB | 9,989 | 99.89 % |

표준편차 1.302 LSB, 중앙값 0 LSB.
전체 구간과 정착 구간의 지표가 사실상 동일 → **초기 필터 과도응답은 비교 결과에 영향 없음**.

**(진단용) LTspice `direct_adc_signed` ↔ XMODEL**: bit-exact 56.46 %, RMS 1.3031, max 13 —
공식 S&H 결과와 거의 동일하므로 **S/H 경로가 잔차 원인이 아님**.

---

## 5. 잔차 원인 분석 (요청 체크리스트)

| 확인 항목 | 결과 |
|---|---|
| 두 결과의 샘플 수가 동일한가 | ✔ 10,000 = 10,000 |
| 첫 번째 샘플이 모두 1 ms인가 | ✔ 둘 다 0.001 s |
| 한 샘플 지연이 존재하는가 | ✔ 없음 — **best lag = 0**, zero-lag가 최대 상관 |
| offset-binary ↔ signed 변환이 맞는가 | ✔ 양쪽 `code − 2048`, min/max 정합(−96/302 vs −96/303) |
| ADC rounding/clipping 방식이 같은가 | ✔ 동일 식 `floor((V+1.65)/3.3×4095)`, clip[0,4095], clipping 0 |
| 입력 ECG와 입력 갱신 시점이 동일한가 | ⚠ **여기서 잔차 발생** — 아래 참조 |
| Sample-and-Hold 클록 타이밍이 맞는가 | ✔ S/H(900 µs 취득, 1 ms hold) 경로와 direct 경로 결과가 거의 동일 |
| 초기 필터 상태가 다른가 | ✔ 전체 vs 정착 구간 지표 동일 → 영향 없음 |

### 규명된 잔차 원인 (2가지, 모두 AFE/ADC 모델 불일치가 아님)

**(1) 입력 50 µs 격자 정렬 차이 — 0.17 %**
- XMODEL은 360 Hz ECG를 hold하여 **50 µs마다** `v_ecg_pos`를 갱신한다.
- LTspice는 같은 ECG를 **50 µs 격자 staircase PWL**(`patient100_xmodel_drive_10s.txt`)로 인가한다.
- 두 입력을 50 µs 격자에서 직접 비교: **200,000 tick 중 331개(0.17 %)만 불일치**, 평균 차이 4.0×10⁻⁸ V.
- 원인: 360 Hz 주기(2.7778 ms)가 50 µs의 정수배가 아니므로(55.5556틱) ECG 샘플 경계가 격자에 떨어지지 않아 **일부 지점에서 한 틱(50 µs)씩 어긋난다**. 최대 불일치 t = 1.850 s (XMODEL +50 µV vs LTspice +520 µV).

**(2) 급경사 구간의 solver 양자화 차이**
- |err| ≥ 5 LSB인 샘플의 평균 |dcode/dt| = **17.3** vs 전체 평균 **1.5** → **11.8배 급경사에 집중**.
- 최대 오차 8개 모두 QRS 상승/하강 에지(t = 1.857, 3.434, 5.020, 9.131 s …)에서 발생.
- 즉 SPICE 연속시간 solver와 XMODEL 이벤트 solver가 **최대 기울기 지점에서 sub-sample 타이밍 차이**를 내며, 이것이 1 ms 격자에서 수 LSB 차이로 증폭된다. 평탄 구간에서는 대부분 bit-exact.

> 두 요인 모두 **입력 표현/솔버 특성** 문제이며, 이득·필터 응답·오프셋·양자화식 불일치가 아니다.
> 이는 mean error ≈ 0(+0.022 LSB, 편향 없음)과 zero-lag 최대 상관으로도 뒷받침된다.

---

## 6. 그림

| 파일 | 내용 |
|---|---|
| `plots/adc_waveform_full.png` | 10 s 전체, XMODEL vs LTspice signed code 중첩 |
| `plots/adc_waveform_zoom_2_3s.png` | 2.0–3.0 s 확대(샘플 마커 포함) |
| `plots/adc_error_lsb.png` | 샘플별 LSB 오차 (LTspice − XMODEL) |
| `plots/adc_error_histogram.png` | ADC code error 히스토그램 |

---

## 7. 산출물

| 구분 | 파일 |
|---|---|
| ① LTspice ADC 결과 | `ltspice/ltspice_xmodel_aligned_adc_samples.csv`, `ltspice_track_hold_adc_signed.mem` |
| ② XMODEL ADC 결과 | `xmodel/xmodel_adc_nominal.txt` |
| ③ Sample-by-sample 비교 | `comparison/ltspice_vs_xmodel_sample_compare.csv` |
| ④ 정량 요약표 | `comparison/ltspice_xmodel_summary.csv` / `.md` |
| ⑤⑥ 그림 | `plots/*.png` (4종) |
| ⑦ 실행 로그 | `ltspice/ltspice_sim.log`, `ltspice_run_command.log`, `xmodel/xmodel_run.log`, `compile_*.log`, `simulate.log` |
| ⑧ 버전·해시 | `ARTIFACT_SHA256.md` (XMODEL commit SHA 포함) |

CSV 컬럼: `sample_index, time_s, afe_out_v, adc_hold_v, adc_clip_v, th_adc_code, th_adc_signed, th_hex12, direct_adc_code, direct_adc_signed`

---

## 8. 재현 방법

```bash
# XMODEL (Linux + Questa + XMODEL)
export XMODEL_HOME=/path/to/xmodel; export QUESTA_HOME=/path/to/questa
cd ltspice_validation && bash scripts/run_fixed_xmodel_correlation.sh
```
```powershell
# LTspice (배치)
& "<LTspice>" -b xma_adc_10s_fresh.cir      # LTspice 26이면 원본 .asc 그대로 사용 가능
```
```bash
# 파싱 + 비교
python3 parse_ltspice_raw_adc.py <raw> <outdir>
python3 compare_ltspice_xmodel_adc.py <ltspice_csv> <xmodel_txt> <outdir>
```

---

## 9. 보고서용 문구 (제안)

> 동일한 patient100 10초 ECG 입력에 대해 LTspice 회로 시뮬레이션과 XMODEL 시뮬레이션을 각각 새로 실행하고,
> 1 kSPS·12-bit·±1.65 V 조건에서 signed ADC code 10,000개를 sample-by-sample로 비교하였다.
> 두 결과는 샘플 수·샘플 시각·샘플 주기·극성·스케일이 완전히 일치하였고 지연은 0 sample이었으며,
> zero-lag 상관 0.9995, 평균오차 +0.02 LSB, RMS 오차 1.30 LSB, 전체 샘플의 91.2 %가 ±1 LSB 이내로 일치하였다.
> 잔여 차이는 입력 50 µs 격자 정렬 불일치(0.17 %)와 QRS 급경사 구간에서의 solver 간 sub-sample 타이밍 차이에
> 기인하며(오차 상위 구간의 신호 기울기가 평균의 11.8배), AFE 이득·필터 응답·ADC 양자화식 불일치는 확인되지 않았다.
> 따라서 LTspice 회로 구현과 XMODEL 행동 모델은 ADC 출력 수준에서 상호 검증(CORRELATED)된 것으로 판단한다.
