#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LTspice(th_adc_signed, S&H) ↔ XMODEL(adc_signed) ADC 비교 (10s / 10,000 samples)
#  공식 비교: XMODEL signed ↔ LTspice th_adc_signed. direct는 진단용.
#  출력: 비교 CSV, 요약표(CSV/MD), 플롯 4종
# 사용: python3 compare_ltspice_xmodel_adc.py <ltspice_csv> <xmodel_txt> <outdir>
import sys, os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LT, XM, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, "plots"), exist_ok=True)

# ---- load ----
rows = list(csv.DictReader(open(LT, encoding="utf-8-sig")))
lt_t = np.array([float(r["time_s"]) for r in rows])
lt_th = np.array([int(r["th_adc_signed"]) for r in rows])
lt_dir = np.array([int(r["direct_adc_signed"]) for r in rows])
lt_afe = np.array([float(r["afe_out_v"]) for r in rows])

xi, xc, xt = [], [], []
for line in open(XM):
    if not line.strip() or line.lstrip().startswith("#"): continue
    a = line.split()
    xi.append(int(a[0])); xc.append(int(a[1])); xt.append(float(a[2]) * 1e-9)
xm_code = np.array(xc); xm_signed = xm_code - 2048; xm_t = np.array(xt)

n = min(len(lt_th), len(xm_signed))

def lag_metrics(a, b, maxlag=5):
    """a=LTspice, b=XMODEL. zero-lag + best-lag 상관/오차"""
    def corr(x, y):
        if x.std() == 0 or y.std() == 0: return float("nan")
        return float(np.corrcoef(x, y)[0, 1])
    c0 = corr(a.astype(float), b.astype(float))
    best_lag, best_c = 0, c0
    for L in range(-maxlag, maxlag + 1):
        if L >= 0: x, y = a[L:], b[:len(b) - L] if L else b
        else:      x, y = a[:L], b[-L:]
        m = min(len(x), len(y))
        if m < 10: continue
        c = corr(x[:m].astype(float), y[:m].astype(float))
        if not np.isnan(c) and c > best_c: best_lag, best_c = L, c
    return c0, best_lag, best_c

def summarize(scope, mask, lt, xm, t):
    a, b, tt = lt[mask], xm[mask], t[mask]
    err = a.astype(float) - b.astype(float)          # LTspice - XMODEL
    c0, bl, bc = lag_metrics(a, b)
    exact = int(np.sum(a == b))
    clip = int(np.sum((a <= -2048) | (a >= 2047)) + np.sum((b <= -2048) | (b >= 2047)))
    dt = np.diff(tt)
    return {
        "scope": scope,
        "XMODEL sample count": len(b),
        "LTspice sample count": len(a),
        "First sample time [s]": f"{tt[0]:.6g}",
        "Last sample time [s]": f"{tt[-1]:.6g}",
        "Sample period [s]": f"{np.median(dt):.6g}" if len(dt) else "n/a",
        "XMODEL signed min/max": f"{int(b.min())} / {int(b.max())}",
        "LTspice signed min/max": f"{int(a.min())} / {int(a.max())}",
        "Clipping count": clip,
        "Mean error [LSB]": f"{err.mean():.4f}",
        "MAE [LSB]": f"{np.abs(err).mean():.4f}",
        "RMS error [LSB]": f"{np.sqrt((err**2).mean()):.4f}",
        "Max abs error [LSB]": f"{np.abs(err).max():.0f}",
        "Zero-lag correlation": f"{c0:.6f}",
        "Best lag [sample]": bl,
        "Best-lag correlation": f"{bc:.6f}",
        "Bit-exact sample count": exact,
        "Bit-exact match ratio [%]": f"{100.0*exact/len(a):.2f}",
    }

t = lt_t[:n]
full = np.ones(n, bool)
settled = t >= 1.0
summ = [summarize("full_0_10s", full, lt_th[:n], xm_signed[:n], t),
        summarize("settled_1_10s", settled, lt_th[:n], xm_signed[:n], t)]
# 진단용 direct
summ_dir = [summarize("DIAG_direct_full", full, lt_dir[:n], xm_signed[:n], t),
            summarize("DIAG_direct_settled", settled, lt_dir[:n], xm_signed[:n], t)]

# ---- sample-by-sample CSV ----
cmp_csv = os.path.join(OUT, "ltspice_vs_xmodel_sample_compare.csv")
with open(cmp_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sample_index", "time_s", "xmodel_adc_code", "xmodel_adc_signed",
                "ltspice_th_adc_signed", "error_lsb_ltspice_minus_xmodel",
                "ltspice_direct_adc_signed", "bit_exact", "afe_out_v"])
    for i in range(n):
        w.writerow([i, f"{t[i]:.6f}", int(xm_code[i]), int(xm_signed[i]), int(lt_th[i]),
                    int(lt_th[i]) - int(xm_signed[i]), int(lt_dir[i]),
                    int(lt_th[i] == xm_signed[i]), f"{lt_afe[i]:.9g}"])

# ---- summary table ----
keys = list(summ[0].keys())
with open(os.path.join(OUT, "ltspice_xmodel_summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
    for s in summ + summ_dir: w.writerow(s)

with open(os.path.join(OUT, "ltspice_xmodel_summary.md"), "w", encoding="utf-8") as f:
    f.write("# LTspice ↔ XMODEL ADC 비교 요약\n\n")
    f.write("공식 비교: **XMODEL adc_signed ↔ LTspice th_adc_signed (Sample-and-Hold 경로)**. "
            "오차 정의 = LTspice − XMODEL.\n\n")
    f.write("| 비교 항목 | 전체 0~10s | 정착 1~10s |\n|---|---|---|\n")
    for k in keys[1:]:
        f.write(f"| {k} | {summ[0][k]} | {summ[1][k]} |\n")
    f.write("\n## (진단용) LTspice direct_adc_signed ↔ XMODEL\n\n")
    f.write("| 비교 항목 | 전체 0~10s | 정착 1~10s |\n|---|---|---|\n")
    for k in keys[1:]:
        f.write(f"| {k} | {summ_dir[0][k]} | {summ_dir[1][k]} |\n")

# ---- plots ----
P = os.path.join(OUT, "plots")
err = lt_th[:n].astype(float) - xm_signed[:n].astype(float)

fig, ax = plt.subplots(figsize=(12, 4.2))
ax.plot(t, xm_signed[:n], lw=0.8, label="XMODEL signed code")
ax.plot(t, lt_th[:n], lw=0.8, alpha=0.75, label="LTspice S&H signed code")
ax.set_xlabel("time (s)"); ax.set_ylabel("signed ADC code")
ax.set_title("ADC signed code — XMODEL vs LTspice (10 s, 10,000 samples)")
ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
fig.savefig(os.path.join(P, "adc_waveform_full.png"), dpi=140); plt.close(fig)

m = (t >= 2.0) & (t <= 3.0)
fig, ax = plt.subplots(figsize=(12, 4.2))
ax.plot(t[m], xm_signed[:n][m], marker=".", ms=3, lw=0.9, label="XMODEL")
ax.plot(t[m], lt_th[:n][m], marker=".", ms=3, lw=0.9, alpha=0.75, label="LTspice S&H")
ax.set_xlabel("time (s)"); ax.set_ylabel("signed ADC code")
ax.set_title("ADC signed code — zoom 2.0–3.0 s")
ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
fig.savefig(os.path.join(P, "adc_waveform_zoom_2_3s.png"), dpi=140); plt.close(fig)

fig, ax = plt.subplots(figsize=(12, 3.6))
ax.plot(t, err, lw=0.6, color="crimson")
ax.axhline(0, color="k", lw=0.6)
ax.set_xlabel("time (s)"); ax.set_ylabel("error (LSB)")
ax.set_title("Per-sample error: LTspice S&H − XMODEL")
ax.grid(alpha=0.3); fig.tight_layout()
fig.savefig(os.path.join(P, "adc_error_lsb.png"), dpi=140); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.2))
lo, hi = int(err.min()), int(err.max())
bins = np.arange(lo - 0.5, hi + 1.5, 1.0)
ax.hist(err, bins=bins, color="steelblue", edgecolor="k", lw=0.3)
ax.set_xlabel("error (LSB), LTspice − XMODEL"); ax.set_ylabel("count")
ax.set_title("ADC code error histogram")
ax.grid(alpha=0.3, axis="y"); fig.tight_layout()
fig.savefig(os.path.join(P, "adc_error_histogram.png"), dpi=140); plt.close(fig)

# ---- console ----
print("=== 공식 비교 (XMODEL ↔ LTspice th_adc_signed) ===")
for k in keys[1:]:
    print(f"  {k:28} full={summ[0][k]:>14}   settled={summ[1][k]:>14}")
print("\n=== 진단 (direct) ===")
for k in ["Bit-exact match ratio [%]", "RMS error [LSB]", "Max abs error [LSB]"]:
    print(f"  {k:28} full={summ_dir[0][k]:>14}   settled={summ_dir[1][k]:>14}")
print("\n출력:", OUT)
