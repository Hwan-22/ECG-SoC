#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LTspice binary .raw -> 1ms 간격 ADC 샘플 10,000개 추출 (LTspice↔XMODEL 비교용)
#  출력: ltspice_xmodel_aligned_adc_samples.csv, ltspice_track_hold_adc_signed.mem
#  사용: python3 parse_ltspice_raw_adc.py <raw> <outdir> [n_samples=10000] [period_s=0.001]
import sys, os, csv, struct
import numpy as np

def read_ltspice_raw(path):
    """LTspice raw(binary/ascii) 파서. return (varnames, time[], data[nvar-1][npts])"""
    blob = open(path, "rb").read()
    # 헤더는 UTF-16LE. 'Binary:' 또는 'Values:' 마커까지.
    for marker, enc in ((b"B\x00i\x00n\x00a\x00r\x00y\x00:\x00\n\x00", "utf-16-le"),
                        (b"V\x00a\x00l\x00u\x00e\x00s\x00:\x00\n\x00", "utf-16-le"),
                        (b"Binary:\n", "latin-1"), (b"Values:\n", "latin-1")):
        idx = blob.find(marker)
        if idx >= 0:
            head = blob[:idx].decode(enc, errors="replace")
            body = blob[idx + len(marker):]
            ascii_mode = b"Values" in marker
            break
    else:
        raise RuntimeError("raw 마커(Binary:/Values:)를 찾지 못함")

    nvar = npts = None; flags = ""; names = []
    lines = [l.strip() for l in head.splitlines()]
    for i, l in enumerate(lines):
        if l.startswith("No. Variables:"): nvar = int(l.split(":")[1])
        elif l.startswith("No. Points:"):  npts = int(l.split(":")[1])
        elif l.startswith("Flags:"):       flags = l.split(":")[1].strip().lower()
        elif l.startswith("Variables:"):
            for j in range(i + 1, i + 1 + (nvar or 0)):
                parts = lines[j].split()
                if len(parts) >= 2: names.append(parts[1])
    if not (nvar and npts and len(names) == nvar):
        raise RuntimeError(f"헤더 파싱 실패 nvar={nvar} npts={npts} names={len(names)}")

    if ascii_mode:
        vals = np.fromstring(body.decode("latin-1").replace("\n", " "), sep=" ")
        raise RuntimeError("ASCII raw는 이 스크립트에서 미지원(현재 실행은 binary)")

    # binary: 'double' flag면 전부 double, 아니면 time=double + 나머지 float32
    if "double" in flags:
        rec = np.dtype([("t", "<f8")] + [(f"v{i}", "<f8") for i in range(nvar - 1)])
    else:
        rec = np.dtype([("t", "<f8")] + [(f"v{i}", "<f4") for i in range(nvar - 1)])
    need = rec.itemsize * npts
    if len(body) < need:
        raise RuntimeError(f"데이터 부족: {len(body)} < {need} (rec={rec.itemsize}B x {npts})")
    arr = np.frombuffer(body[:need], dtype=rec)
    t = np.abs(arr["t"].astype(np.float64))   # LTspice는 첫 필드 부호로 플래그를 쓰기도 함
    data = {names[i + 1]: arr[f"v{i}"].astype(np.float64) for i in range(nvar - 1)}
    return names, t, data, flags, npts

def quantize(v):
    """LTspice B-source와 동일: limit(floor((clip(v,-1.65,1.65)+1.65)/3.3*4095),0,4095)"""
    c = np.clip(v, -1.65, 1.65)
    return np.clip(np.floor((c + 1.65) / 3.3 * 4095.0), 0, 4095).astype(np.int64)

def main():
    raw, outdir = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    per = float(sys.argv[4]) if len(sys.argv) > 4 else 0.001
    os.makedirs(outdir, exist_ok=True)
    names, t, data, flags, npts = read_ltspice_raw(raw)
    print(f"raw: npts={npts} nvar={len(names)} flags='{flags}' t[0]={t[0]:.6g} t[-1]={t[-1]:.6g}")
    print("vars:", ", ".join(names))

    def get(nm):
        for k in data:
            if k.lower() == nm.lower(): return data[k]
        raise KeyError(f"{nm} 없음 (있는 것: {list(data)})")

    afe = get("V(afe_out)"); hold = get("V(adc_hold)"); clip = get("V(adc_clip)")
    code = get("V(adc_code)"); signed = get("V(adc_signed)")

    ts = np.array([(k + 1) * per for k in range(n)])          # 1ms ... 10.000s
    # 샘플 시각의 값 = 그 시각 이하 마지막 해석점 (held/staircase 신호에 맞는 sample-at-instant)
    idx = np.searchsorted(t, ts + 1e-12, side="right") - 1
    idx = np.clip(idx, 0, len(t) - 1)

    afe_s, hold_s, clip_s = afe[idx], hold[idx], clip[idx]
    th_code = np.rint(code[idx]).astype(np.int64)
    th_signed = np.rint(signed[idx]).astype(np.int64)
    direct_code = quantize(afe_s)                              # 진단용: AFE_OUT 직접 양자화
    direct_signed = direct_code - 2048

    rows = []
    for i in range(n):
        rows.append(dict(sample_index=i, time_s=round(ts[i], 6),
                         afe_out_v=f"{afe_s[i]:.12g}", adc_hold_v=f"{hold_s[i]:.12g}",
                         adc_clip_v=f"{clip_s[i]:.12g}",
                         th_adc_code=int(th_code[i]), th_adc_signed=int(th_signed[i]),
                         th_hex12=f"{int(th_signed[i]) & 0xFFF:03X}",
                         direct_adc_code=int(direct_code[i]), direct_adc_signed=int(direct_signed[i])))
    cols = ["sample_index", "time_s", "afe_out_v", "adc_hold_v", "adc_clip_v",
            "th_adc_code", "th_adc_signed", "th_hex12", "direct_adc_code", "direct_adc_signed"]
    csvp = os.path.join(outdir, "ltspice_xmodel_aligned_adc_samples.csv")
    with open(csvp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    memp = os.path.join(outdir, "ltspice_track_hold_adc_signed.mem")
    with open(memp, "w", newline="\n") as f:
        f.write("\n".join(f"{int(v) & 0xFFF:03x}" for v in th_signed) + "\n")

    print(f"샘플 {n}개  첫={ts[0]:.3f}s 끝={ts[-1]:.3f}s")
    print(f"th_adc_signed  min={th_signed.min()} max={th_signed.max()}")
    print(f"direct_signed  min={direct_signed.min()} max={direct_signed.max()}")
    print(f"th vs direct 일치: {int(np.sum(th_signed==direct_signed))}/{n}")
    print("CSV ->", csvp); print("MEM ->", memp)

if __name__ == "__main__":
    main()
