#!/usr/bin/env python3
# 스테이징된 검증 세그먼트들에 대해 XModel 정합 에뮬레이터 실행 → emu/*.adc
import sys, os
sys.path.insert(0, '/home/soohwan/ECG-SoC/scripts')
from afe_emu import read_mem_signed, afe_adc_unsigned
W = '/home/soohwan/ECG-SoC/sim_out/afe_val'
os.makedirs(W + '/emu', exist_ok=True)
for line in open(W + '/list.txt'):
    f = line.strip()
    if not f:
        continue
    base = f[:-4]
    codes = read_mem_signed(W + '/raw/' + f)
    uns = afe_adc_unsigned(codes)
    with open(W + '/emu/' + base + '.adc', 'w') as o:
        for v in uns:
            o.write(f"{v}\n")
    print(f"emu {base}: n={len(uns)} range {min(uns)}~{max(uns)}")
print("EMU_VAL_DONE")
