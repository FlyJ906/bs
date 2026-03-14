@echo off
REM 禁用 oneDNN/MKLDNN 以避免 PIR 兼容性问题
set FLAGS_use_mkldnn=0
set FLAGS_use_mkldnn_int8=0
set FLAGS_use_onednn=0
set MKLDNN_DISABLE=1
set PADDLE_ENABLE_ONEDNN_OPTS=0
set FLAGS_enable_pir=0
set FLAGS_enable_pir_in_executor=0
set FLAGS_enable_pir_api=0
set FLAGS_enable_new_ir_in_executor=0
set FLAGS_use_pir_onednn=0
set FLAGS_enable_new_executor=0
set OMP_NUM_THREADS=1
set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=1
set GLOG_minloglevel=2

echo PaddlePaddle environment variables set, starting app...
D:\python\python.exe app.py