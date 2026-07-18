# 실행 버전 및 해시 증빙

## XMODEL
- Git commit SHA : 4756a5086023547328ef44fd5fd87da3c250dc39
- repo           : github.com/Hwan-22/ECG-SoC (main)
- DUT            : analog/ecg_afe_xmodel.sv
- DUT sha256(LF) : 79191b79d9730f10789bca06b5a3cff3ab9e5c94dad28aa51b3dc1d98d470846
- TB             : reference/xmodel_alignment/tb_xmodel_correlation.sv
- TB sha256      : 31ee06b1ff0ee8c6ff244b53301fc416d4eb4cdd9b4441e7e6ab61e057b18c4c
- simulator      : Questa Intel Starter FPGA Edition 2024.3 + XMODEL 2025.12

## LTspice
- executable     : LTspiceXVII 17.0.37.0 (XVIIx64.exe, batch -b)
- netlist        : xma_adc_10s_fresh.cir (.tran 0 10.001 0 5u)
- netlist sha256 : eeba7a389689e70a4b99fef9b0329f9ab89d54baee8cedd873bf97f7c9bc28d5
- 원본 회로      : schematics/xmodel_aligned/FULL_AFE_ADC_SH_xmodel_aligned.asc (Version 4.1)
- 입력 PWL       : patient100_xmodel_drive_10s.txt

## 산출물 해시

```
9b48c5c52bf84af9496c4ef68ee17e12e28cd146e32de8efff472a581e91e3c6  ./ARTIFACT_SHA256.md.tmp
3de8ee7f95adcc636653b83ca0cbc30ac8598ceb03fb8ba9202c21e86220cdff  ./README_RESULT.md
3a9776c97e91b7cfffa8e77349c9cc90779031fad91a85369e0a4e975d87ef0e  ./comparison/ltspice_vs_xmodel_sample_compare.csv
6bd56b927c2b0a61d841f9a4df0d19999331dc2025a14d0f823a315967973bac  ./comparison/ltspice_xmodel_summary.csv
4956c6b6e92a892ef0c4a6406b5e54c3c4b75794a32ad2a07d744b39a67e57e9  ./comparison/ltspice_xmodel_summary.md
73f06e075cbaf157ec452f553789f21ae81daa97e085b69452285361f9c56f49  ./ltspice/XOpAmp_XMODEL_XVII.lib
3094d479139ad1007339cae83b80a84b90a2dda6296cde2394aa68ba9bf2e024  ./ltspice/ltspice_run_command.log
098ca27afd35112b6708ad5793808628620c00bb6338ac3b6f3b73ecd471c4c5  ./ltspice/ltspice_sim.log
157b754889f68dece5853dab445b1d149e7c257022700cd4b5d438054d940592  ./ltspice/ltspice_track_hold_adc_signed.mem
d16632e24bfe5a2695d166e7f5784c6ef6f4e9011ac9f621ab1904e54dad0451  ./ltspice/ltspice_xmodel_aligned_adc_samples.csv
eeba7a389689e70a4b99fef9b0329f9ab89d54baee8cedd873bf97f7c9bc28d5  ./ltspice/xma_adc_10s_fresh.cir
f076853dce4cb35a71c073a56071d3e327ef81b55a8cb53e43c553082a7a3b49  ./plots/adc_error_histogram.png
b431c7511b8e62ce71206103304563975e7833b99832855f04eae05fa29bb34f  ./plots/adc_error_lsb.png
405c99c24da8637bf63516db9b433d1f41d8af109cdb23a1be2600eac168bb27  ./plots/adc_waveform_full.png
bd1794967515cebc76cfd186a5e20443f4337a889fa4ef0c6d1af2bcaab72ee6  ./plots/adc_waveform_zoom_2_3s.png
22dd69d860fa91a7e00f7f465fe952f19add86b71a009efda6eefbd14581efa1  ./xmodel/compile_dut.log
16b00a876d9adaf35964db7cca90284fb286ba5633dc9ba4ff96e792da1b8371  ./xmodel/compile_pkg.log
bcf74d3a9d08041b71afe4cbc5540ec7f9ebe384a47dfd1b1c58742bee8f2358  ./xmodel/compile_primitives.log
24c4bc96884ddc2e9c08031e8cd153e93374f2cf97d5515e8272d99f948eb676  ./xmodel/compile_tb.log
792320138c15c23a36af2c46da8b59aec082e5d96dac42d05316cd4925c34080  ./xmodel/simulate.log
31ee06b1ff0ee8c6ff244b53301fc416d4eb4cdd9b4441e7e6ab61e057b18c4c  ./xmodel/tb_xmodel_correlation.sv
dc47bc7f76835b428705e824ba486b0b159dac5071dc205756abcc587f266a97  ./xmodel/xmodel_adc_nominal.txt
f43b93c89cb388805baa79485a8508cbf91bee746eaba9470505ec789d775ea0  ./xmodel/xmodel_run.log
```

> 주: 실행 로그(*.log) 내 개인 절대경로는 <HOME> / <WORKSPACE> / <WINUSER> 로 마스킹되어 있으며,
> 위 해시는 마스킹 후 파일 기준이다. 명령행·툴 버전 등 증빙 내용은 그대로 보존되었다.
