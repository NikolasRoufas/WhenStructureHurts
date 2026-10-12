#!/usr/bin/env bash
# Campaign driver for the authorised Qwen2.5-7B GPU pilot on interstellar (docs/GPU_PREFLIGHT_REPORT.md).
# Runs one experiment per call, on PHYSICAL GPU 0 only, and appends a line to the status log.
#   scripts/campaign/run.sh <exp0|exp1|exp2|exp3> <config.yaml> [--resume <run_dir>] [extra wsh args]
# Meant to be called inside tmux. Never touches GPU 1, the MPS daemon or Ollama.
set -euo pipefail
EXP=$1; CFG=$2; shift 2
CAMPAIGN=${WSH_CAMPAIGN_DIR:-/data/roufas/wsh_campaign}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
cd "$REPO"
mkdir -p "$CAMPAIGN/logs" "$CAMPAIGN/no_mps" "$CAMPAIGN/results" "$CAMPAIGN/cache"

export HF_HOME=/data/roufas/hf_cache HF_HUB_OFFLINE=1
export CUDA_MPS_PIPE_DIRECTORY=$CAMPAIGN/no_mps CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
export WSH_RESULTS_ROOT=$CAMPAIGN/results WSH_CACHE_PATH=$CAMPAIGN/cache/gen.sqlite
export WSH_COMPUTE_AUTHORIZED=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 PYTHONUNBUFFERED=1
PY=$REPO/.venv/bin/python

# 1) physical GPU identity: must be bus 01:00.0 (GPU 0), reached directly (no MPS), nothing else on it
$PY - <<'EOF'
import os, subprocess, sys, torch
from wsh.artifacts import mps_control_pipe
assert mps_control_pipe() is None, "CUDA would be routed through MPS"
assert torch.cuda.device_count() == 1, torch.cuda.device_count()
p = torch.cuda.get_device_properties(0)
assert p.pci_bus_id == 1, f"wrong physical GPU: bus {p.pci_bus_id}"
apps = subprocess.run(["nvidia-smi", "-i", "0", "--query-compute-apps=pid,process_name", "--format=csv,noheader"],
                      capture_output=True, text=True).stdout.strip()
assert not apps, f"GPU 0 is busy: {apps}"
print(f"GPU check OK: {p.name}, bus {p.pci_bus_id}, {p.total_memory/1e9:.1f} GB, no MPS, idle")
EOF

# 2) the run itself (stage gpu_pilot needs both authorisation switches)
TS=$(date +%Y%m%d-%H%M%S)
LOG=$CAMPAIGN/logs/${EXP}_$(basename "$CFG" .yaml)_$TS.log
echo "$(date -Is) START $EXP $CFG $* commit=$(git rev-parse --short HEAD) log=$LOG" | tee -a "$CAMPAIGN/status.log"
T0=$(date +%s)
nvidia-smi -i 0 --query-gpu=timestamp,utilization.gpu,memory.used,power.draw --format=csv,noheader -l 30 \
  > "$CAMPAIGN/logs/gpu_${EXP}_$TS.csv" 2>&1 & SMI=$!
set +e
"$REPO/.venv/bin/wsh" run "$EXP" --config "$CFG" --authorized-compute "$@" > "$LOG" 2>&1
RC=$?
set -e
kill $SMI 2>/dev/null || true
RUN_DIR=$(grep -oE "$CAMPAIGN/results/[^ ]+/${EXP}/[0-9]{8}-[0-9]{6}_[0-9a-f]{8}(-[0-9]+)?" "$LOG" | tail -1 || true)
echo "$(date -Is) END   $EXP rc=$RC wall_s=$(( $(date +%s) - T0 )) run_dir=${RUN_DIR:-?}" | tee -a "$CAMPAIGN/status.log"
exit $RC
