# -27회 반도체설계대전-
한양대학교 융합전자공학부 (이수환, 서민우, 양건)
# ECG-SoC: 웨어러블 심전도 부정맥 감지 Mixed-Signal SoC

> 제27회 대한민국 반도체설계대전 출품작  
> 한양대학교 융합전자공학부

---

## 프로젝트 개요

웨어러블 심전도(ECG) 신호의 실시간 부정맥 감지를 목표로,
저전력 AFE·SAR ADC 아날로그 프론트엔드와 Pan-Tompkins 기반
R-peak 검출기 및 Decision Tree 하드웨어 가속기를 포함한
Mixed-Signal SoC를 설계합니다.

---

## 팀 구성 및 역할 분담

| 팀원 | 역할 | 주요 담당 | 주요 툴 |
|---|---|---|---|
| 이수환 (팀장) | 아날로그 설계 + 통합 검증 | AFE, SAR ADC, Mixed-Signal 통합 | LTspice, XModel, MATLAB |
| 팀원 양건 | 디지털 RTL 설계 + FPGA | IIR 필터, Pan-Tompkins RTL, FPGA 구현 | Vivado, Nexys A7 |
| 팀원 서민우 | 알고리즘 + AI + 검증 | Pan-Tompkins Python, DT 학습, 데이터 처리 | Python, MATLAB Simulink |

---

## 시스템 아키텍처
```
[ECG 전극]
    │
    ▼
[AFE: IA 증폭기 + HPF + Notch 필터]
    │  아날로그 신호
    ▼
[SAR ADC: 12-bit, 1kSPS]
    │  디지털 코드
    ▼
[디지털 IIR Notch 필터]
    │
    ▼
[Pan-Tompkins R-peak 검출기]
    │
    ▼
[Decision Tree 가속기]
    │
    ▼
[Normal / Arrhythmia 판정]
```

---

## 월별 개발 로드맵

| 기간 | 주요 작업 |
|---|---|
| 2월 | ECG 사양 확정, MIT-BIH 데이터 로드, 툴 환경 구축 |
| 3월 | IA 증폭기·필터 LTspice 설계, Pan-Tompkins Python 구현 |
| 4월 | SAR ADC LTspice 검증, 디지털 블록 Verilog 구현 |
| 5월 | XModel Mixed-Signal 통합 시뮬레이션, MATLAB 교차 검증 |
| 6월 | FPGA 합성·구현, Nexys A7 실시간 ECG 데모 |
| 7월 | 서류 작성 및 최종 제출 (마감: 7월 23일) |

---

## 검증 흐름
```
AFE(LTspice→XModel) → SAR ADC(LTspice→XModel)
    → IIR 필터(Verilog) → Pan-Tompkins(Verilog)
        → DT 가속기(Verilog) → FPGA 실시간 데모
```

---

## 저장소 구조
```
ECG-SoC/
├── analog/       # LTspice, XModel 파일 (이수환)
├── digital/      # Verilog RTL (양건)
├── algorithm/    # Python, MATLAB 스크립트 (서민우)
├── tb/           # 통합 테스트벤치
├── docs/         # 설계 문서, 발표 자료
└── data/         # MIT-BIH 샘플 데이터
```

---

## 사용 기술 스택

- **아날로그:** LTspice · XModel (GLISTER) · MATLAB
- **디지털:** Vivado · Verilog HDL · Nexys A7-100T FPGA
- **알고리즘:** Python (wfdb · scikit-learn) · MATLAB Simulink
- **검증 데이터:** MIT-BIH Arrhythmia Database

---

## 평가 목표 (대학생 부문)

| 항목 | 배점 | 전략 |
|---|---|---|
| 창의성 | 30% | DT 하드웨어 가속기, 도메인 특화 설계 |
| 기술성 | 30% | Mixed-Signal 통합 검증, SAR ADC 수치 근거 |
| 완성도 | 30% | FPGA 실시간 데모 + 3단계 검증 체계 |
| 사업성 | 10% | 웨어러블 ECG 시장 적용 가능성 |
```

→ Collaborators
→ "Add people"
→ 팀원 GitHub 아이디 입력 → 초대
