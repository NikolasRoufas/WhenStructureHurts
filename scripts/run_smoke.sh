#!/usr/bin/env bash
# Bounded real-model smoke test (Qwen2.5-0.5B-Instruct, CPU, 3 real examples per dataset).
# Pipeline validation only. Every run writes to a NEW directory under results/smoke/.
set -euo pipefail
cd "$(dirname "$0")/.."
WSH=".venv/bin/wsh"
CFG="${1:-configs/smoke.yaml}"
mkdir -p logs
$WSH validate-config "$CFG"
for e in exp0 exp1 exp2 exp3; do
  echo "=== $e $(date +%T)"
  /usr/bin/time -p $WSH run "$e" --config "$CFG" 2>&1 | grep -v -e "Loading weights" -e "Batches" | tee "logs/smoke_$e.log" | tail -4
done
EXP1=$(ls -td results/smoke/exp1/*/ | head -1)
echo "=== exp4 plumbing check on $EXP1"
$WSH exp4 --config "$CFG" --source-run "$EXP1" --plumbing-check
