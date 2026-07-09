#!/usr/bin/env python3
# plugin/hooks/scripts/hook_detect.py
"""Thin PostToolUse shim: stdin payload -> `uvx nobots detect FILE` -> exit code.

Propagates detect's exit code (2 = tells found -> nudge, 0 = silent). Fails
open on any error so a hook bug never blocks a Write/Edit. The CLI engine lives
in the installed `nobots` package; this file carries no detection logic.

Set NOBOTS_SOURCE to override the uvx --from source (defaults to the PyPI
package "nobots"). Useful pre-publish: NOBOTS_SOURCE=. for a local checkout,
or a git+https://... URL.
"""

import json
import os
import subprocess
import sys

NOBOTS_SOURCE = os.environ.get("NOBOTS_SOURCE", "nobots")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        file_path = payload.get("tool_input", {}).get("file_path", "") or ""
        if not file_path:
            return 0
        proc = subprocess.run(
            ["uvx", "--from", NOBOTS_SOURCE, "nobots", "detect", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.stderr:
            print(proc.stderr, file=sys.stderr, end="")
        return proc.returncode
    except Exception:
        return 0  # fail open


if __name__ == "__main__":
    sys.exit(main())
