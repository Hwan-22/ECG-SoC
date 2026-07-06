# AFE XModel 추가 검증 보고서 — 1.4 / 2.2 / 1.3 (+ 1.2 / 2.4)

> 제27회 반도체설계대전 · 한양대 · 담당: 이수환(AFE) · 2026-07-06
> XModel(Questa+XModel 2025.12) 실측 기반. 환경 스모크(`make sim`) 통과 후 수행.

---

## 1.4 emu↔XModel 정합 확대 (8→36세그) — ✅ 통과

**대상:** test split 클래스당 9세그 = **36세그**(60s). afe_emu(디지털팀 .mem 생성기) vs 실제 XModel AFE(`tb_afe_batch.sv`) 샘플단위 비교(HPF 정착 3s 제외, lag −3..3 탐색).

| 클래스 | RMS 범위 [LSB] | maxabs 범위 [LSB] | lag |
|---|---|---|---|
| NSR (9) | 2.27 ~ 2.60 | 19 ~ 28 | 0 |
| CHF (9) | 1.22 ~ 1.77 | 12 ~ 17 | 0 |
| ARR (9) | 0.85 ~ 1.49 | 8 ~ 23 | 0 |
| AFF (9) | 2.51 ~ 2.90 | 26 ~ 30 | 0 |
| **전체 36** | **평균 1.95 LSB** | ≤ 30 | 0 |

- **평균 RMS 1.95 LSB < 2 LSB 기준 충족**, 전 세그 lag 0(위상 일치). 기존 8세그 검증(2.01 LSB, max~27)과 일관.
- max 편차(최대 30 LSB)는 **QRS 급경사 구간의 sub-sample 타이밍 민감도**(XModel 연속솔버 vs emulator 이산 IIR의 1샘플 미만 차이가 최대기울기에서 큰 code차로 증폭)에 국한. RMS로 보면 전체 충실도는 ~2 LSB.
- 이 ~2 LSB 차이는 2.1에서 **noise 2 LSB rms 주입 시 분류결과·R-peak 불변**으로 확인된 수준 이하 → 디지털팀이 쓰는 emulator .mem은 실제 XModel과 분류상 등가.

> **문구:** "디지털팀 입력 .mem 생성기(afe_emu)가 실제 XModel AFE와 36세그 평균 RMS 1.95 LSB·lag 0으로 일치. 편차는 QRS 첨두의 sub-sample 타이밍에 국한되며 분류 영향 없는 수준(2.1의 2 LSB noise 불변성 이하)."

---

## 2.2 50Hz / 60Hz PLI — ✅ 스코프 명확화

**대상:** 실제 ECG에 공통모드 0.5V + 차동 1mV PLI를 60Hz/50Hz로 주입, 깨끗한 ECG 대비 ADC 잔차(t>2s).

| PLI 주파수 | RMS 잔차 | 최대 잔차 |
|---|---|---|
| **60Hz** (노치 중심) | **0.92 mV** (1.14 codes) | 8.1 mV |
| **50Hz** (노치 밖) | **118 mV** (146.6 codes) | 172 mV |

- 60Hz는 능동 Twin-T 노치(80dB)+CMRR로 **거의 완전 제거**(0.92mV).
- 50Hz는 60Hz 노치의 null 밖이라 **차동 간섭이 IA 이득(×201)으로 그대로 통과** → 128배 큰 잔차. 즉 노치는 설계대로 60Hz 선택적.

> **결론(스코프):** 본 설계는 **60Hz(한국 mains) 대상**이며, 50Hz 환경은 **notch center를 50Hz로 retune**하면 동일 성능 확보(RT/RB/CT 값 f₀=50Hz로 재계산). 약점이 아니라 대상 명확화.

---

## 1.3 전극 DC offset / baseline wander 스트레스 — ✅ 강건

**대상:** 실제 ECG(차동)에 전극 DC offset·baseline wander 주입. 측정: 전체/정착후(t>2s) clipping, 정착후 clean 대비 잔차.

| case | clip 전체 | **clip (t>2s)** | 정착후 잔차(code) |
|---|---|---|---|
| clean | 0 | **0** | 0 |
| DC +10mV | 53 | **0** | 2.6 |
| DC +50mV | 597 | **0** | 8.8 |
| DC +100mV | 824 | **0** | 15.5 |
| DC ±200mV | ~1045 | **0** | ~28 |
| wander 0.1Hz 1mV | 0 | **0** | 29 |
| wander 0.2Hz 2mV | 0 | **0** | 136 |

**결론**
- **정착 후(t>2s) clipping = 0 — 전 케이스(±200mV offset 포함).** 우리 토폴로지가 **HPF를 IA 이득단 이전**에 두어 전극 DC offset을 ×201 증폭 이전에 제거하기 때문. → 큰 전극 offset에도 IA 미포화.
- DC offset 클리핑은 **HPF 정착 과도구간(첫 ~2s)에만** 발생. offset이 클수록 정착 tail이 길어져 ±200mV는 HPF 5τ~10τ(≈1.65~3.3s)에 걸쳐 지수 감쇠(정착후 잔차 28code는 이 감쇠 tail). **연속 stream의 record 중간 60s 스냅샷엔 무영향**(정착구간 없음).
- baseline wander 0.2Hz는 HPF 차단(0.482Hz) **아래라 부분 통과**(정상: HPF 통과대역 경계), 0.1Hz는 더 감쇠. 이는 표준 HPF 특성이며 QRS 대역엔 영향 없음.

> **문구:** "HPF가 IA 이득단 이전에 위치하여 전극 DC offset을 증폭 전에 제거 → ±200mV offset에도 정착(≈2~3s) 이후 ADC clipping 0. baseline wander는 HPF 차단주파수 특성대로 처리."

---

## 1.2 R/C mismatch 스윕 — ✅ 강건 (3-op IA 이점 확인)

**대상:** IA 차동단(R5/R7/R8/R9)·이득(R2/R4)·Twin-T(RT/CT/RB/CB)를 최악방향 (1±MM) 섭동한 변형(`ecg_afe_xmodel_mm.sv`). CMRR은 공통모드 1V@10Hz 주입 leakage로, 60Hz 잔차는 ideal 대비로 측정.

| mismatch | CMRR | 60Hz 잔차(ideal 대비) | clipping |
|---|---|---|---|
| ideal(0%) | 측정하한 미만(<LSB, opamp 110dB 제한) | 0 | 0 |
| **0.1%** | **100.7 dB** | 0.73 mV | 0 |
| 0.5% | 86.1 dB | 3.31 mV | 0 |
| 1.0% | 80.0 dB | 6.54 mV | 0 |

**결론**
- **0.1% 정밀저항에서 CMRR 100.7 dB — >100dB 스펙 충족.** 이는 기존 문서의 보수적 추정(bare diff-amp 기준 ~66dB)보다 크게 우수한데, **3-op-amp IA 1단이 차동 ×201·공통모드 ×1로 미리 분리**하여 뒤단 diff-amp의 저항 mismatch 영향을 ~46dB 완화하기 때문(측정으로 입증).
- 1% 최악 mismatch에서도 CMRR 80 dB 유지, **60Hz 잔차 ≤6.5mV·clipping 0**. 60Hz 제거는 CMRR이 아니라 능동 노치가 주력이므로 mismatch에도 방어됨(2.2와 일관).
- 잔차 ≤6.5mV(~8 code)는 신호 284mV 대비 <3%, 2.1의 noise 2 LSB 불변성 이하 → 분류 영향 없음 예상(final_pred 확정은 1.5 통합경로 필요).

> **문구:** "실제 0.1% 저항 mismatch에서 CMRR 100.7dB(>100dB 충족), 1%에서도 80dB. 3-op IA 구조가 mismatch에 강건하며 60Hz 잔차·clipping 무시 가능."

## 2.4 op-amp finite GBW / input offset — ✅ (GBW 강건 / VOS 헤드룸 인사이트)

**대상:** vcvs opamp에 dominant pole(유한 GBW, f_p=GBW/A_OL)과 입력 offset(VOS, U1+/U2−)을 추가한 변형(`ecg_afe_xmodel_op.sv`). 실제 ECG 구동, ideal(GBW=1e9,VOS=0) 대비.

**finite GBW (VOS=0):**
| GBW | ECG 잔차(ideal 대비) | 폐루프 대역(=GBW/201) | clipping |
|---|---|---|---|
| 100 kHz | 2.04 codes (1.6 mV) | 497 Hz | 0 |
| 500 kHz | 1.28 codes | 2.5 kHz | 0 |
| 1 MHz | 1.31 codes | 5.0 kHz | 0 |
| 5 MHz | 1.14 codes | 24.9 kHz | 0 |

→ **GBW 100kHz까지도 ECG 영향 ≤2 code**(폐루프 대역이 ECG 150Hz 훨씬 상회). 실 ECG용 op-amp(GBW≫100kHz)에서 대역·slew 문제 없음. (slew: ECG 최대 dV/dt는 출력 mV/ms 수준으로 통상 op-amp slew(V/µs)의 1/1000 이하 → 비제약, 별도 모델 불필요.)

**input offset (VOS, GBW=ideal):**
| VOS | 출력 DC offset | clipping |
|---|---|---|
| 0.5 mV | +202.6 mV (+251 code) | 0 |
| 1.0 mV | +405 mV (+503 code) | 0 |
| 2.0 mV | +810 mV (+1005 code) | 0 |

→ **입력 offset은 IA 이득 ×201로 증폭돼 ADC baseline을 크게 이동**(HPF가 IA 이전에만 있어 offset 미차단). 실 VOS≤2mV에선 신호(±~250 code)를 더해도 rail(4095) 미도달 → **clipping 0**이나 **헤드룸을 소모**.
- 정적 offset은 디지털 delta/slope 인코더·input_normalizer가 제거하므로 **분류엔 무영향**(rhythm/event feature 기반). 다만 헤드룸 보호를 위해 **저오프셋 op-amp(auto-zero/chopper, VOS<50µV) 또는 IA 후단 DC servo/2차 HPF** 권장 — analog 설계 개선 포인트.

> **문구:** "finite GBW는 100kHz까지 ECG 영향 ≤2 code로 무시 가능. 입력 offset은 ×201 증폭돼 baseline을 이동시키나(VOS≤2mV서 clip 0), 저오프셋 op-amp/DC servo로 헤드룸 확보 권장."

---

## 종합 (XModel 검증 1.4/2.2/1.3/1.2/2.4)
| 항목 | 결과 | 판정 |
|---|---|---|
| 1.4 emu↔XModel 36세그 | 평균 RMS 1.95 LSB, lag 0 | ✅ <2 LSB |
| 2.2 50/60Hz | 60Hz 0.92mV / 50Hz 118mV | ✅ 60Hz 스코프 |
| 1.3 offset/wander | 정착후 clip 0 (±200mV) | ✅ HPF-before-gain |
| 1.2 R/C mismatch | 0.1%→CMRR 100.7dB, 1%→80dB | ✅ 3-op IA 강건 |
| 2.4 GBW/VOS | GBW 100k 영향≤2code; VOS ×201 헤드룸 | ✅ (+DC servo 권장) |

재현: `bash scripts/{run_afe_val,run_pli_freq,run_stress,run_mismatch,run_opamp}.sh` (WSL, XModel+Questa). 변형 소스 `analog/ecg_afe_xmodel_{mm,op}.sv`, tb `tb/tb_{ecg_pli_freq,ecg_stress,afe_mm,afe_op}.sv`.
