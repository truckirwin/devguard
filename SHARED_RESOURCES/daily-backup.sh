#!/bin/bash
# DevGuard Daily Backup Wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/devguard/daily-backup.sh" "$@"
