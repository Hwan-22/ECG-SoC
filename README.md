# ECG-SoC: 웨어러블 심전도 부정맥 감지 Mixed-Signal SoC

> 제27회 대한민국 반도체설계대전 출품작  
> 한양대학교 융합전자공학부

---

## 프로젝트 개요

웨어러블 심전도(ECG) 신호의 실시간 4클래스 부정맥 감지를 목표로, 저전력 AFE·SAR ADC 아날로그 프론트엔드와 뉴로모픽 LIF 뉴런 기반 SNN 하드웨어 가속기를 포함한 Mixed-Signal SoC를 설계합니다. LTspice·XModel을 활용한 아날로그-디지털 통합 시뮬레이션과 Nexys A7-100T FPGA 실시간 ECG 데이터 처리 검증을 통해 완성도를 입증합니다.

---

## 분류 대상 — 4클래스 ECG

| 클래스 | 명칭 | 핵심 특징 |
|---|---|---|
| NSR | 정상 심전도 | 규칙적 RR interval, 정상 QRS 폭 |
| ARR | 부정맥 계열 | 심방/심실 조기수축, 중간중간 이상 박동 |
| AFF | 심방세동 계열 | RR interval 완전 불규칙, QRS 타이밍 랜덤 |
| CHF | 울혈성 심부전 계열 | QRS 폭 증가, 전반적 전압 감소 |

분류 근거 특징값: **RR interval**, **RR variance**, **QRS width**, **slope/delta**

---

## 시스템 아키텍처

```
[ECG 전극]
    │  0.5~5mV, 0.05~150Hz
    ▼
[AFE: IA 증폭기 (Av=201) + HPF (fc=0.5Hz) + Notch (60Hz)]
    │  아날로그 처리 완료 신호
    ├──────────────────────────────────┐
    ▼                                  ▼
[SAR ADC: 12-bit, 1kSPS]        [Spike Encoder: I&F 뉴런]
    │  12-bit 디지털 코드              │  up_spike / down_spike
    ▼                                  ▼
[IIR Notch 필터 (Verilog)]      [LIF 뉴런 배열 (Verilog)]
    │                                  │
    ▼                                  ▼
[Pan-Tompkins R-peak 검출]      [SNN 분류 가속기]
    └──────────────┬───────────────────┘
                   ▼
          [4클래스 판정 출력]
          NSR / ARR / AFF / CHF
```

---

## 팀 구성 및 역할 분담

| 팀원 | 역할 | 주요 담당 | 주요 툴 |
|---|---|---|---|
| 이수환 (팀장) | 아날로그 설계 + 통합 검증 | AFE, SAR ADC, Spike Encoder, XModel 통합 시뮬레이션 | LTspice, XModel, Questa, MATLAB |
| 팀원 B | 디지털 RTL 설계 + FPGA | LIF 뉴런 배열, SNN 가속기, IIR 필터, Pan-Tompkins RTL, FPGA 구현 | Vivado, Verilog, Nexys A7 |
| 팀원 C | 알고리즘 + AI + 검증 | CSV 전처리, Spike 파라미터 최적화, SNN 학습, 가중치 변환, 성능 측정 | Python, MATLAB Simulink |

---

## 아날로그 설계 상세 (이수환)

### AFE 블록

**IA 증폭기 (3-op-amp 구조)**

```
전체 이득 Av = 1 + (2 × R_feedback) / Rgain = 201
R_feedback = 100 kΩ,  Rgain = 1 kΩ
입력 임피던스 > 10 MΩ (JFET 입력 구성)
CMRR 목표 > 100 dB  (IEC 60601-2-47 기준)
공급 전압 ±1.65V (3.3V 단전원, Nexys A7 Pmod 기준)
```

- 1단계: OA1, OA2 전치증폭기 — 차동 신호 증폭, 공통모드 통과
- 2단계: OA3 차동증폭기 — 공통모드 제거, R1=R2=R3=R4=100kΩ

**HPF (고역통과 필터)**
- 차단 주파수 fc = 0.5 Hz — DC 오프셋(±300mV) 제거
- 허용 DC 오프셋: IEC 60601-2-47 기준 ±300mV

**Notch 필터**
- 차단 주파수 60 Hz — 전원선 간섭 제거

### SAR ADC

- 해상도: 12-bit / 샘플링 속도: 1kSPS
- 검증 항목: DNL/INL 특성 (LTspice)

### Spike Encoder (아날로그 뉴로모픽 블록)

**delta 기반 스파이크 인코딩**

```
delta = 현재값 - 이전값  (slope 근사, 1kSPS 등속 샘플링 기준)

delta >  T_high  →  strong_up_spike   = 1
delta >  T_low   →  weak_up_spike     = 1
delta < -T_low   →  weak_down_spike   = 1
delta < -T_high  →  strong_down_spike = 1
```

**I&F 뉴런 회로 (LTspice)**
- 커패시터 적분 → Vth 도달 시 1-bit 펄스 발화
- 발화 임계전압 Vth = 0.9V (AFE 출력 1.8V 기준 50%)

아날로그-디지털 경계 신호:
```
SAR ADC  →  data[11:0]       (12-bit, 동기식)
Spike Encoder  →  up_spike   (1-bit, 비동기 이벤트)
               →  down_spike (1-bit, 비동기 이벤트)
```

---

## 디지털 설계 상세 (팀원 B)

### 뉴로모픽 LIF 뉴런 배열

**QRS LIF 뉴런 — R-peak 검출**

```
입력: up_spike, down_spike
V_mem += up_spike + down_spike
V_mem > T_qrs  →  발화 (R-peak 이벤트)
→ up_spike가 가장 많이 누산되는 QRS 정점에서 발화
```

**Width LIF 뉴런 배열 — QRS 폭 감지 (CHF 판별 핵심)**

```
입력: strong_spike (매 샘플 주기마다)
V_mem += strong_spike

short_width_LIF  : V_mem > T_low    →  발화  (좁은 QRS)
normal_width_LIF : V_mem > T_normal →  발화  (정상 QRS)
long_width_LIF   : V_mem > T_high   →  발화  (넓은 QRS → CHF 의심)
```

**RR interval 뉴런 — AFF/ARR 판별 핵심**
- QRS LIF 발화 시점 간 클럭 카운터로 RR interval 측정
- RR variance 계산 → AFF(높은 variance), ARR(이상치 포함) 판별
- *(구현 방식 확정 필요 — 타이머 카운터 방식 권장)*

### 주요 미결 사항 (팀원 B 작업 필요)
- LIF 누설(leak) 항 구현: `V_mem = V_mem × (1 - leak_rate)` — 없으면 잡신호에 오발화
- 발화 후 V_mem 리셋 타이밍 확정 (QRS LIF 발화 기준 or 고정 윈도우 300ms)
- 임계값 T_low, T_normal, T_high, T_qrs → 팀원 C로부터 `parameters.v`로 수신

### IIR Notch 필터
- 60Hz 디지털 노치 필터 (SAR ADC 경로)

### Pan-Tompkins RTL
- 팀원 C Python 구현 결과와 bit-exact 비교 검증

### SNN 분류 가속기
- LIF 뉴런 발화 패턴 → 4클래스 판정 로직
- 팀원 C 학습 가중치 → `parameters.v` 형태로 주입

---

## AI 및 알고리즘 상세 (팀원 C)

### 데이터셋 및 전처리
- 데이터셋: CSV 형식 ECG 데이터 (4클래스 레이블 포함)
- 클래스: NSR / ARR / AFF / CHF

### 스파이크 인코딩 파라미터 최적화
- Python으로 Spike Encoder 소프트웨어 구현
- T_high, T_low, T_normal 조합별 분류 정확도 측정
- 최적값 → `parameters.v`로 변환하여 팀원 B에게 전달

### SNN 학습 파이프라인
```
CSV 데이터 → Spike 인코딩 → LIF 시뮬레이션 → SNN 학습
                                              ↓
                               학습 가중치 → 8-bit 양자화
                                              ↓
                               parameters.v (Verilog parameter 선언)
```

### 최종 검증
- Sensitivity / Specificity 측정
- 4클래스별 Confusion Matrix

---

## 블록별 검증 흐름 (End-to-End)

```
[1] AFE + SAR ADC  →  LTspice SPICE 시뮬레이션
[2] Spike Encoder  →  LTspice + XModel 행동 모델
[3] LIF 뉴런 배열  →  Vivado xsim 기능 검증
[4] SNN 분류기    →  Python 결과와 교차 검증
[5] 전체 통합     →  Questa + XModel Mixed-Signal 시뮬레이션
[6] FPGA 검증     →  Nexys A7-100T 실시간 ECG 데모
```

---

## 저장소 구조

```
ECG-SoC/
├── analog/          # LTspice (.asc), XModel (.sv) — 이수환
│   ├── IA_amp.asc
│   ├── HPF.asc
│   ├── SAR_ADC.asc
│   └── spike_encoder.asc
├── digital/         # Verilog RTL — 팀원 B
│   ├── iir_notch.v
│   ├── pan_tompkins.v
│   ├── lif_neuron.v
│   ├── snn_accelerator.v
│   └── parameters.v   ← 팀원 C 전달 파일
├── algorithm/       # Python, MATLAB — 팀원 C
│   ├── pan_tompkins.py
│   ├── spike_encoder.py
│   ├── snn_train.py
│   └── export_weights.py
├── tb/              # 통합 테스트벤치
├── docs/            # 설계 문서, 회의록, 파형 이미지
└── data/            # MIT-BIH / CSV 샘플 데이터
```

---

## 월별 개발 로드맵

| 기간 | 이수환 (아날로그) | 팀원 B (디지털) | 팀원 C (알고리즘) |
|---|---|---|---|
| 3월 | IA 증폭기 LTspice 설계 | IIR Notch Verilog | CSV 전처리, Spike 인코딩 Python |
| 4월 | HPF·Notch·SAR ADC LTspice | Pan-Tompkins RTL, LIF 뉴런 Verilog | SNN 학습, T 파라미터 최적화 |
| 5월 | Spike Encoder XModel 모델 | SNN 가속기 통합, RR interval 뉴런 | parameters.v 생성, MATLAB 교차 검증 |
| 5월말 | Questa + XModel 통합 시뮬레이션 | ← 동일 | ← 동일 |
| 6월 | FPGA 통합 총괄 | Vivado 합성·구현, ILA 검증 | Sensitivity/Specificity 측정 |
| 7월 | 서류 작성 및 최종 제출 (마감: 7월 23일) | ← 동일 | ← 동일 |

---

## 주요 마일스톤

| 날짜 | 마일스톤 |
|---|---|
| 3월 말 | 아날로그 블록 LTspice 시뮬레이션 완료 |
| 4월 말 | 디지털 RTL 기능 검증 완료 |
| 5월 말 | Mixed-Signal 통합 시뮬레이션 완료 |
| 6월 말 | FPGA 실시간 ECG 데모 완성 |
| 7월 23일 | 최종 제출 |

---

## 사용 기술 스택

- **아날로그:** LTspice · XModel (Questa 연동) · MATLAB
- **디지털:** Vivado · Verilog HDL · Nexys A7-100T FPGA (XADC 내장)
- **알고리즘:** Python (wfdb · scikit-learn · numpy) · MATLAB Simulink
- **검증 데이터:** CSV ECG 데이터셋 (NSR/ARR/AFF/CHF 4클래스)

---

## 공모전 평가 전략

| 항목 | 배점 | 전략 |
|---|---|---|
| 창의성 | 30% | delta 기반 Spike 인코딩 + 뉴로모픽 LIF 뉴런 배열 — 기존 SAR ADC→DT 구조와 명확한 차별성 |
| 기술성 | 30% | Mixed-Signal 통합 검증 (XModel), IEC 60601-2-47 수치 근거, 4클래스 분류 정확도 |
| 완성도 | 30% | FPGA 실시간 데모 + 3단계 검증 체계 (LTspice → Questa → FPGA) |
| 사업성 | 10% | 웨어러블 ECG 4클래스 실시간 감지 → 스마트워치, 패치형 심전도 시장 |

---

## 팀원 간 인터페이스 규약

### 경계 1 — 이수환 → 팀원 B

```verilog
// SAR ADC 경로 (동기)
output [11:0] adc_data;      // 12-bit 디지털 코드, 1kHz 동기

// Spike Encoder 경로 (비동기 이벤트)
output strong_up_spike;      // 1-bit, 발화 시 1클럭 펄스
output weak_up_spike;
output weak_down_spike;
output strong_down_spike;
```

### 경계 2 — 팀원 C → 팀원 B

```verilog
// parameters.v (팀원 C 학습 후 생성)
parameter signed [7:0] T_low    = 8'd15;
parameter signed [7:0] T_normal = 8'd30;
parameter signed [7:0] T_high   = 8'd55;
parameter signed [7:0] T_qrs    = 8'd40;
// SNN 가중치 (8-bit 양자화)
parameter signed [7:0] W [0:15] = '{8'd12, 8'd-5, 8'd31, ...};
```
