#!/bin/bash
# DevGuard Smart Save Wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/devguard/smart-save.sh" "$@"
