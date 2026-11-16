"""Compatibility entry point. Prefer `sentinela` or `python detect.py --help`."""

from sentinela.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
