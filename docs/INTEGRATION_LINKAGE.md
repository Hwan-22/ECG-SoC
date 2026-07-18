# 통합 저장소 연계 (ECG-SoC-Integrated ↔ 본 저장소)

> 갱신 2026-07-18 · 담당 이수환(XMODEL/integration)
> 통합 저장소: **https://github.com/Sheep-gun/ECG-SoC-Integrated**
> 본 저장소는 통합 저장소의 component **`afe_xmodel`** 으로 import된다.

## 1. 연계 상태

| 항목 | 값 |
|---|---|
| 통합 component 이름 | `afe_xmodel` |
| upstream repository | `github.com/Hwan-22/ECG-SoC` (본 저장소) |
| **고정 import commit (pin)** | **`4756a5086023547328ef44fd5fd87da3c250dc39`** |
| pin commit title | "2차 리뷰 반영: claim 강도 조정 + threshold artifact + path portability" |
| contributor | 이수환 |
| import 방식 | curated `git archive <fixed_commit>` (raw dataset·private 경로는 별도 제외 등록) |

통합 저장소의 다른 component 고정 commit:
- MATLAB nominal pre-validation (서민우): `907f7e1f081a9d6a5703a32095d962143315a192`
- Digital RTL/IP/FPGA (양건): `c6b80de19cdcad5b7e43fe7835588b629d847f75`

## 2. 본 저장소가 근거를 제공하는 claim

통합 저장소 `source_of_truth/claim_registry.csv` 기준. **evidence 경로가 바뀌면 통합 claim이 깨지므로 이동/삭제 금지.**

| claim | 내용 | status | evidence (본 저장소 경로) |
|---|---|---|---|
| **CLM-012** | AFE-generated final-test 입력이 board-replay 입력과 SHA256 36/36 동일 | SAFE | `docs/integration_latest/afe36_sha256_bitidentity.csv` |
| **CLM-013** | canonical `sample_gap_cycles=2`에서 AFE→RTL final_pred·final_mem 36/36 bit-exact | SAFE | `docs/integration_latest/afe_locked_rtl_integration_36case_compare.csv` |
| **CLM-014** | emu↔XMODEL 36세그 평균 RMS 1.95 LSB, lag 0 | **CAREFUL** | `docs/afe_stress/AFE_xmodel_verification.md` |

`ownership_matrix.csv` 상 본인 범위: AFE+ADC XMODEL / non-ideal·stress 모델 / full-record AFE 생성 · XMODEL 파형·스트레스 검증 / AFE chunk SHA256 identity / canonical AFE→RTL 재현 · AFE→digital signed-stream handoff 근거.
한계 표기: *model-based XMODEL/emulator verification; no transistor-level, PCB, or silicon evidence.*

## 3. 용어·claim 경계 (통합 `terminology.yaml` 준수)

**금지·회피 표현** — 본 저장소 문서에서도 사용하지 않는다:
`clinical diagnosis` · `medical-device validation` · `physical mixed-signal SoC` · `fabricated chip` ·
`silicon-proven` · `physical analog measurement` · `four diseases diagnosed` ·
`real-time diagnosis in milliseconds` · `commercial clinical superiority` ·
`100 percent accuracy based on hardware equivalence`

**핵심 규칙**
- **board/AFE→RTL의 36/36(functional equivalence)과 29/36=80.56%(classification accuracy)를 절대 합쳐 쓰지 않는다.**
- `functional equivalence` = 같은 입력에서 출력이 기준과 일치함(정확도와 별개).
- `SNN-inspired` = 이벤트·누적 상태 구조이며 학습형 deep SNN/생물학적 등가 주장이 아님.
- `Holter` 철자를 유지한다(‘hotler’ 금지).
- MATLAB(nominal intent)과 XMODEL(non-ideal/stress·long-stream handoff)은 **대체 관계가 아니라 역할 분리**이며, 둘 다 physical AFE/ADC 계측이 아니다.

> 준수 점검(2026-07-18): 본 저장소 `docs/`·`README.md`에 금지 용어 **0건**, Holter 철자 정상.
> 단, 통합 규칙에 맞춰 `docs/integration_latest/AFE_latest_locked_model_integration.md`의 29/36·36/36 병기 문장을 분리 서술로 수정함.

## 4. pin 이후 추가된 증거 (통합 저장소 미반영)

통합 저장소는 `4756a50`에 고정되어 있으므로, 그 **이후** 본 저장소에 추가된 아래 결과는 아직 통합본에 없다.

| 추가 결과 | 커밋 | 산출물 |
|---|---|---|
| **LTspice ↔ XMODEL ADC 교차검증** (patient100 10 s, 10,000 samples) | `b9ebfec` | `docs/ltspice_xmodel/` (보고서·비교 CSV·요약표·플롯 4종·실행 로그·SHA 증빙) |

요지: 동일 입력으로 LTspice 회로와 XMODEL을 각각 신규 실행해 signed ADC code를 sample-by-sample 비교 →
샘플수·시각·주기·극성·스케일 완전 일치, **lag 0**, zero-lag correlation **0.999518**,
mean **+0.022 LSB**, RMS **1.302 LSB**, **±1 LSB 이내 91.19 %**, clipping 0.
잔차는 입력 50 µs 격자 정렬 차이(0.17 %)와 QRS 급경사 구간 solver 간 sub-sample 타이밍 차이로 규명되었으며,
AFE 이득·필터·양자화식 불일치는 없다.

**통합 반영 시 제안 claim (초안)**

| 항목 | 제안 값 |
|---|---|
| 제안 claim (KR) | 동일 patient100 10초 입력에서 LTspice 회로 구현과 XMODEL은 signed ADC code 기준 lag 0, zero-lag 상관 0.9995, RMS 1.30 LSB, ±1 LSB 이내 91.2 %로 일치한다 |
| 제안 claim (EN) | For the same patient100 10-second input, the LTspice circuit implementation and the XMODEL agree on signed ADC codes with zero lag, 0.9995 zero-lag correlation, 1.30 LSB RMS error, and 91.2 % of samples within ±1 LSB |
| status | **CAREFUL** (bit-exact 아님; model-to-model 상호검증) |
| evidence | `docs/ltspice_xmodel/comparison/ltspice_xmodel_summary.csv` |
| scope | patient100 10 s, 10,000 samples, 1 kSPS / 12-bit / ±1.65 V |
| limitations | circuit-model ↔ behavioral-model agreement; physical AFE/ADC 계측 아님. LTspiceXVII 실행을 위해 (i) LTspice 26이 생성한 동일 회로 넷리스트 사용 (ii) op-amp lib의 XVII 호환 표기 사용 — 둘 다 소자·파라미터·양자화식 불변 |

> 통합 반영을 원하면 `afe_xmodel` pin을 `b9ebfec` 이후 commit으로 갱신하면 된다.

## 5. 재현·정합성

- 본 저장소 검증 요약: `docs/VALIDATION_STATUS.md`
- AFE→locked RTL 통합: `docs/integration_latest/AFE_latest_locked_model_integration.md`
- XMODEL stress: `docs/afe_stress/AFE_xmodel_verification.md`
- LTspice 교차검증: `docs/ltspice_xmodel/README_RESULT.md`
- 개인 절대경로 미포함(`ECG_SOC_ROOT` 또는 repo-root 자동탐색), 스크립트는 clone 위치 무관하게 동작.
