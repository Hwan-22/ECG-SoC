# LTspice ↔ XMODEL ADC 비교 요약

공식 비교: **XMODEL adc_signed ↔ LTspice th_adc_signed (Sample-and-Hold 경로)**. 오차 정의 = LTspice − XMODEL.

| 비교 항목 | 전체 0~10s | 정착 1~10s |
|---|---|---|
| XMODEL sample count | 10000 | 9001 |
| LTspice sample count | 10000 | 9001 |
| First sample time [s] | 0.001 | 1 |
| Last sample time [s] | 10 | 10 |
| Sample period [s] | 0.001 | 0.001 |
| XMODEL signed min/max | -96 / 302 | -68 / 302 |
| LTspice signed min/max | -96 / 303 | -68 / 303 |
| Clipping count | 0 | 0 |
| Mean error [LSB] | 0.0221 | 0.0270 |
| MAE [LSB] | 0.6445 | 0.6549 |
| RMS error [LSB] | 1.3020 | 1.3243 |
| Max abs error [LSB] | 13 | 13 |
| Zero-lag correlation | 0.999518 | 0.999502 |
| Best lag [sample] | 0 | 0 |
| Best-lag correlation | 0.999518 | 0.999502 |
| Bit-exact sample count | 5649 | 5061 |
| Bit-exact match ratio [%] | 56.49 | 56.23 |

## (진단용) LTspice direct_adc_signed ↔ XMODEL

| 비교 항목 | 전체 0~10s | 정착 1~10s |
|---|---|---|
| XMODEL sample count | 10000 | 9001 |
| LTspice sample count | 10000 | 9001 |
| First sample time [s] | 0.001 | 1 |
| Last sample time [s] | 10 | 10 |
| Sample period [s] | 0.001 | 0.001 |
| XMODEL signed min/max | -96 / 302 | -68 / 302 |
| LTspice signed min/max | -96 / 303 | -68 / 303 |
| Clipping count | 0 | 0 |
| Mean error [LSB] | 0.0216 | 0.0266 |
| MAE [LSB] | 0.6454 | 0.6558 |
| RMS error [LSB] | 1.3031 | 1.3254 |
| Max abs error [LSB] | 13 | 13 |
| Zero-lag correlation | 0.999517 | 0.999501 |
| Best lag [sample] | 0 | 0 |
| Best-lag correlation | 0.999517 | 0.999501 |
| Bit-exact sample count | 5646 | 5059 |
| Bit-exact match ratio [%] | 56.46 | 56.20 |
