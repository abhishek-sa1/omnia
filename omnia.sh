#!/bin/bash
# Root wrapper — delegates to src/main/omnia.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/src/main/omnia.sh" "$@"
