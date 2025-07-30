#!/bin/bash
# DevGuard Recovery Wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/devguard/recover.sh" "$@"
