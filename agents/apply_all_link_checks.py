"""Run link checks on all complete lessons."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENT = REPO_ROOT / "agents" / "link_checker_agent.py"


def main() -> int:
    extra = [a for a in sys.argv[1:] if a in ("--fix", "--offline")]
    cmd = [sys.executable, str(AGENT), "--all", *extra]
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
