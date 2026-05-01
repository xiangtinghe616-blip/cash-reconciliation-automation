from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def run(script: str, *args: str) -> None:
    script_path = BASE_DIR / "src" / script
    command = [sys.executable, str(script_path), *args]
    print(f"\nRunning: {' '.join(command)}")
    subprocess.run(command, check=True)


def main() -> None:
    run("generate_reconciliation_data_v2.py")
    run("reconciliation_engine_v2.py")
    run("llm_exception_assistant_ollama.py", "--mode", "template")


if __name__ == "__main__":
    main()
