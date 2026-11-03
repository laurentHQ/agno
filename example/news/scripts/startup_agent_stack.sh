#!/usr/bin/env bash
set -euo pipefail

repo_root="/mnt/disks/additional-disk-1/agno/example/news"
cd "$repo_root"

./scripts/start_agentos.sh &
 AGENT_PID=$!

./scripts/start_webui.sh &
WEBUI_PID=$!

wait $AGENT_PID $WEBUI_PID
