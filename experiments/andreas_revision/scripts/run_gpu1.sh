#!/usr/bin/env bash
# Journal-revision launcher (interstellar): runs one `wsh run` on PHYSICAL GPU 1 through the shared MPS daemon.
# GPU 0 is never used. Refuses to start if GPU 1 is not the expected device, or if any process other than the
# user's own MPS server is on it. Appends START/END lines to the status log. Call inside tmux:
#   experiments/andreas_revision/scripts/run_gpu1.sh <exp> <config.yaml> [--resume <run_dir>] [extra wsh args]
set -euo pipefail
EXP=$1; CFG=$2; shift 2
WORK=${WSH_ANDREAS_DIR:-/data/roufas/wsh_andreas}
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$REPO"
mkdir -p "$WORK/logs" "$WORK/results" "$WORK/cache" "$WORK/tmp"
GPU1_UUID=GPU-42ddde80-b3bc-7eeb-6c1f-20b4a1684ace

export HF_HOME=/data/roufas/hf_cache HF_HUB_OFFLINE=1 TMPDIR=$WORK/tmp
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps CUDA_VISIBLE_DEVICES=0
export WSH_RESULTS_ROOT=$WORK/results WSH_CACHE_PATH=${WSH_CACHE_PATH:-$WORK/cache/gen.sqlite}
export WSH_COMPUTE_AUTHORIZED=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 PYTHONUNBUFFERED=1 PYTHONPATH=$REPO/src
PY=${WSH_PY:-/data/roufas/when-structure-hurts/.venv/bin/python}

# 1) other users / unknown processes on GPU 1?
OTHERS=$(nvidia-smi -i 1 --query-compute-apps=pid,process_name --format=csv,noheader | grep -v "nvidia-cuda-mps-server" || true)
if [ -n "$OTHERS" ]; then echo "GPU 1 is busy: $OTHERS" >&2; exit 3; fi
# 2) the device torch sees is physical GPU 1
$PY - <<PYEOF
import torch
assert torch.cuda.device_count() == 1, torch.cuda.device_count()
p = torch.cuda.get_device_properties(0)
uuid = "GPU-" + str(p.uuid)
assert uuid == "$GPU1_UUID", f"wrong GPU {uuid}"
torch.ones(1, device="cuda").sum().item()
print(f"GPU check OK: {p.name} bus {p.pci_bus_id} {uuid} via MPS, {p.total_memory/1e9:.1f} GB")
PYEOF

TS=$(date +%Y%m%d-%H%M%S)
LOG=$WORK/logs/${EXP}_$(basename "$CFG" .yaml)_$TS.log
echo "$(date -Is) START $EXP $CFG $* commit=$(git rev-parse --short HEAD) log=$LOG" | tee -a "$WORK/status.log"
T0=$(date +%s)
nvidia-smi -i 1 --query-gpu=timestamp,utilization.gpu,memory.used,power.draw --format=csv,noheader -l 30 \
  > "$WORK/logs/gpu_${EXP}_$TS.csv" 2>&1 & SMI=$!
set +e
$PY -m wsh.cli run "$EXP" --config "$CFG" --authorized-compute "$@" > "$LOG" 2>&1
RC=$?
set -e
kill $SMI 2>/dev/null || true
RUN_DIR=$(grep -oE "$WORK/results/[^ ]+/${EXP}/[0-9]{8}-[0-9]{6}_[0-9a-f]{8}(-[0-9]+)?" "$LOG" | tail -1 || true)
echo "$(date -Is) END   $EXP rc=$RC wall_s=$(( $(date +%s) - T0 )) run_dir=${RUN_DIR:-?}" | tee -a "$WORK/status.log"
exit $RC
