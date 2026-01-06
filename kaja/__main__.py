from __future__ import annotations

def _run_main() -> int:
    from main import main as _main_func

    return _main_func()


if __name__ == "__main__":
    raise SystemExit(_run_main())
