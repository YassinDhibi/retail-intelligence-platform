from __future__ import annotations

try:
    from .load_to_postgres import main
except ImportError:
    from load_to_postgres import main


if __name__ == "__main__":
    main()
