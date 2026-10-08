#!/bin/bash
# exp11: residual energy analysis.
# CPU-only; run from anywhere inside OrthoPurify.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

bash "$SCRIPT_DIR/run_residual.sh"
