# MATLAB-Based AFE+ADC Validation

본 폴더는 ECG-SoC 프로젝트의 **AFE 입력 데이터셋**을 MATLAB 기반 AFE+ADC 모델에 통과시켜, schematic 기반 AFE 파라미터가 SystemVerilog XModel 구현에 사용하기 적절한지 검증하기 위한 코드와 결과를 정리한다.

검증 흐름은 다음과 같다.

```text
Existing AFE schematic parameters
        ↓
MATLAB AFE+ADC validation
        ↓
SystemVerilog XModel parameterization
        ↓
Mixed-signal integration with SNN accelerator
```

MATLAB 검증의 목적은 단순히 ECG 파형을 출력하는 것이 아니라, 실제 AFE 입력 신호가 HPF, instrumentation amplifier, 60 Hz notch filter, LPF, ADC quantizer를 거친 뒤에도 ADC 입력 범위 내에서 안정적으로 동작하고, 디지털 블록에서 사용할 수 있는 12-bit stream으로 정상 변환되는지 확인하는 것이다.

---

## 1. Input Dataset

검증에는 `afe_input_dataset/`에 저장된 AFE 입력단 ECG 데이터를 사용한다. 해당 데이터는 AFE 처리 이전의 원본 digitized ECG를 analog-equivalent voltage로 변환한 신호이다.

```text
afe_input_dataset/
├─ afe_input_NSR.csv
├─ afe_input_CHF.csv
├─ afe_input_ARR.csv
├─ afe_input_AFF.csv
├─ afe_input_NSR.pwl
├─ afe_input_CHF.pwl
├─ afe_input_ARR.pwl
├─ afe_input_AFF.pwl
└─ afe_input_record100_NSR.csv / .pwl
```

각 CSV 파일은 다음 컬럼으로 구성된다.

| Column | Description |
|---|---|
| `sample_index` | sample index |
| `time_s` | time in seconds |
| `code_signed` | signed ECG code |
| `voltage_V` | AFE input voltage in volts |

전압 스케일은 다음과 같다.

```text
voltage_V = code_signed / 200000
1 code ≈ 5 µV
```

MATLAB 검증에서는 CSV 파일의 `voltage_V`를 AFE 입력 전압으로 사용한다. PWL 파일은 XModel 또는 SPICE 주입용으로 사용할 수 있으며, 형식은 다음과 같다.

```text
time[s]    voltage[V]
```

---

## 2. AFE+ADC Parameters

MATLAB 검증 모델은 기존 AFE schematic 및 SystemVerilog XModel에서 사용한 파라미터와 동일한 값을 사용한다.

| Block | Parameter | Value |
|---|---:|---:|
| HPF | `R = 10 MΩ`, `C = 33 nF` | `fc ≈ 0.482 Hz` |
| Instrumentation Amplifier | `Rfb = 100 kΩ`, `Rg = 1 kΩ` | `Av = 201` |
| Notch Filter | active Twin-T notch | `f0 = 60 Hz`, `Q ≈ 5` |
| LPF | `R = 1 kΩ`, `C = 1.06 µF` | `fc ≈ 150 Hz` |
| ADC | input range | `±1.65 V` |
| ADC | resolution | `12 bit` |
| ADC output | offset-binary | `0 ~ 4095` |
| Digital stream | signed conversion | `adc_signed = adc_code - 2048` |

The MATLAB model uses the following signal chain.

```text
ECG voltage_V
    → HPF 0.482 Hz
    → Instrumentation Amplifier ×201
    → 60 Hz Notch Filter, Q≈5
    → LPF 150 Hz
    → ADC input saturation check, ±1.65 V
    → 12-bit offset-binary ADC code
    → signed 12-bit stream
```

---

## 3. MATLAB Files

| File | Description |
|---|---|
| `run_afe_dataset_validation.m` | Main script for validating NSR/CHF/ARR/AFF dataset |
| `run_afe_adc_validation.m` | Single-record quick validation script |
| `afe_adc_params.m` | AFE+ADC parameter definition |
| `design_afe_filters.m` | HPF, notch, LPF model generation |
| `load_afe_input_record.m` | CSV/PWL input loader |
| `parse_pwl_file.m` | PWL file parser |
| `afe_adc_model.m` | Main AFE+ADC signal chain model |
| `plot_afe_frequency_response.m` | Frequency response plotting |
| `plot_afe_time_domain.m` | Time-domain plotting |
| `save_afe_outputs.m` | CSV, MEM, signed stream output saving |

---

## 4. How to Run

MATLAB Current Folder를 `matlab_afe_validation/`으로 설정한 뒤, Command Window에서 다음 명령을 실행한다.

```matlab
run_afe_dataset_validation
```

`afe_input_dataset/` 폴더는 `matlab_afe_validation/` 바로 아래에 위치해야 한다.

```text
matlab_afe_validation/
├─ afe_input_dataset/
│  ├─ afe_input_NSR.csv
│  ├─ afe_input_CHF.csv
│  ├─ afe_input_ARR.csv
│  └─ afe_input_AFF.csv
├─ run_afe_dataset_validation.m
├─ afe_adc_model.m
└─ ...
```

단일 입력만 빠르게 확인할 경우에는 다음을 실행할 수 있다.

```matlab
run_afe_adc_validation
```

---

## 5. Generated Outputs

`run_afe_dataset_validation` 실행 후 `results_dataset/` 폴더가 생성된다.

```text
results_dataset/
├─ NSR/
├─ CHF/
├─ ARR/
├─ AFF/
├─ record100_NSR/
├─ afe_adc_spec_summary.csv
├─ afe_dataset_input_summary.csv
└─ afe_dataset_dynamic_range_summary.csv
```

각 클래스 폴더에는 다음 파일들이 저장된다.

| Output file | Description |
|---|---|
| `matlab_afe_adc_output.csv` | AFE+ADC 단계별 출력 전체 저장 |
| `matlab_adc_offset_binary_hex.mem` | 12-bit offset-binary ADC code, hex memory format |
| `matlab_adc_signed_decimal.txt` | signed 12-bit decimal stream |
| `afe_adc_dynamic_range_metrics.csv` | clipping 및 ADC dynamic range 요약 |
| `fig_input_differential_ecg.png` | AFE 입력 ECG 파형 |
| `fig_after_hpf.png` | HPF 통과 후 파형 |
| `fig_after_ia_gain.png` | IA ×201 증폭 후 파형 |
| `fig_afe_output_before_adc.png` | ADC 직전 AFE 출력 파형 |
| `fig_adc_code_time_domain.png` | ADC code 시간영역 파형 |
| `fig_adc_code_distribution.png` | ADC code 분포 |

`matlab_afe_adc_output.csv`에는 다음 신호들이 포함된다.

| Signal | Meaning |
|---|---|
| `v_diff` | AFE input ECG voltage |
| `v_hpf` | HPF output |
| `v_ia` | IA gain output |
| `v_notch` | 60 Hz notch output |
| `v_lpf` | LPF output |
| `v_adc_in` | ADC input voltage after saturation check |
| `adc_code` | 12-bit offset-binary ADC code |
| `adc_signed` | signed 12-bit stream |

---

## 6. Validation Results

### 6.1 Dataset Summary

| Record | Duration | Sampling Rate | Input Min [V] | Input Max [V] | Input P-P [V] |
|---|---:|---:|---:|---:|---:|
| NSR | 60 s | 1 kSPS | -0.000490 | 0.002120 | 0.002610 |
| CHF | 60 s | 1 kSPS | -0.001590 | 0.003130 | 0.004720 |
| ARR | 60 s | 1 kSPS | -0.003020 | 0.002510 | 0.005530 |
| AFF | 60 s | 1 kSPS | -0.001945 | 0.001840 | 0.003785 |
| record100_NSR | 10 s | 1 kSPS after interpolation | -0.000645 | 0.000960 | 0.001605 |

### 6.2 Dynamic Range and Clipping

| Record | AFE Output Peak [V] | Clip Ratio [%] | ADC Min | ADC Max | ADC P-P |
|---|---:|---:|---:|---:|---:|
| NSR | 0.385184 | 0 | 1909 | 2525 | 616 |
| CHF | 0.557422 | 0 | 1701 | 2739 | 1038 |
| ARR | 0.630367 | 0 | 1265 | 2626 | 1361 |
| AFF | 0.350374 | 0 | 1612 | 2452 | 840 |
| record100_NSR | 0.241954 | 0 | 1954 | 2347 | 393 |

모든 대표 ECG 입력에 대해 AFE 출력은 ADC 입력 범위인 `±1.65 V` 안에 존재하였다. 또한 모든 클래스에서 clipping ratio가 `0%`로 확인되었다. 따라서 IA gain `×201` 및 필터 체인은 4클래스 대표 ECG 입력에 대해 saturation 없이 안정적으로 동작한다.

ADC code 역시 `0` 또는 `4095`에 붙지 않고 중앙 code인 `2048` 근처를 기준으로 ECG morphology를 반영하였다. 이는 MATLAB AFE+ADC 모델이 SNN accelerator 입력으로 사용할 수 있는 signed 12-bit stream을 정상적으로 생성했음을 의미한다.

---

## 7. Interpretation

MATLAB 검증 결과는 다음과 같이 해석할 수 있다.

1. **Gain validation**  
   IA gain `×201`을 적용해도 모든 클래스에서 AFE 출력이 `±1.65 V` 범위를 넘지 않았다.

2. **Filter-chain validation**  
   HPF, notch filter, LPF를 거친 뒤에도 ECG의 주요 morphology가 유지되었다.

3. **ADC dynamic range validation**  
   ADC code가 0 또는 4095로 포화되지 않았고, 각 클래스별로 충분한 code variation을 보였다.

4. **Digital stream generation**  
   12-bit offset-binary ADC output과 signed stream이 모두 생성되어, 이후 SystemVerilog XModel 및 SNN accelerator 검증에 사용할 수 있다.

---

## 8. Connection to SystemVerilog XModel

MATLAB 검증에서 사용한 AFE+ADC 블록 구조와 파라미터는 SystemVerilog XModel 구현의 기준으로 사용된다.

```text
MATLAB validation parameter
        ↓
SystemVerilog XModel block parameter
        ↓
Mixed-signal simulation
        ↓
SNN accelerator input stream
```

SystemVerilog XModel에서는 MATLAB에서 검증한 다음 블록을 동일하게 반영한다.

```text
HPF 0.482 Hz
IA gain ×201
60 Hz active Twin-T notch, Q≈5
LPF 150 Hz
12-bit ADC, ±1.65 V
```

이후 XModel 출력은 digital SNN accelerator에 입력되는 1 kSPS signed 12-bit ECG stream으로 사용된다.

---

## 9. Notes and Limitations

- 본 MATLAB 모델은 schematic 기반 AFE+ADC의 system-level validation을 목적으로 한다.
- Op-amp transistor-level nonideality, PCB parasitic, electrode impedance variation, thermal noise, layout mismatch 등은 본 검증 범위에 포함하지 않는다.
- Active Twin-T notch plot은 frequency sweep 해상도에 따라 notch depth가 다소 얕게 보일 수 있다. 정확한 notch depth를 보고서에 기재할 경우 60 Hz 주변을 더 촘촘히 sweep하거나, 정확히 60 Hz에서의 attenuation을 별도로 계산하는 것이 좋다.
- 본 검증은 clinical validation이 아니라 AFE+ADC XModel 및 digital accelerator integration을 위한 engineering validation이다.

---

## 10. Report Summary

MATLAB 검증에는 NSR, CHF, ARR, AFF 4클래스 대표 ECG 입력 데이터셋을 사용하였다. 각 데이터는 60초 길이의 1 kSPS ECG 신호이며, `voltage_V` 컬럼을 AFE 입력 전압으로 사용하였다. MATLAB에서는 schematic 기반 AFE 파라미터를 사용하여 HPF, instrumentation amplifier, 60 Hz notch filter, LPF, ADC quantizer를 순차적으로 모델링하였다.

검증 결과, 모든 클래스에서 AFE 출력은 ADC 입력 범위인 `±1.65 V` 내에서 동작했으며 clipping ratio는 `0%`였다. ADC 출력은 12-bit offset-binary code 및 signed 12-bit stream으로 정상 변환되었다. 따라서 MATLAB 검증을 통해 AFE+ADC 파라미터가 SystemVerilog XModel 구현 및 SNN accelerator 입력 stream 생성에 사용하기 적절함을 확인하였다.
