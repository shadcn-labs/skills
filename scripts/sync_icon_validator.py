#!/usr/bin/env python3
"""Keep the standalone icon validator copies in sync.

The generator copy is authoritative. Each skill keeps a bundled copy so it still works when
installed alone. Run without flags to check drift or with --write to refresh the extend copy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills/icon-set-generator/scripts/validate_icons.py"
REPLICA = ROOT / "skills/icon-set-extend/scripts/validate_icons.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="replace the standalone extend copy with the authoritative generator copy",
    )
    args = parser.parse_args()

    source = SOURCE.read_bytes()
    if args.write:
        REPLICA.write_bytes(source)
        print(f"updated {REPLICA.relative_to(ROOT)}")
        return 0

    if REPLICA.read_bytes() == source:
        print("icon validator copies are in sync")
        return 0

    print("icon validator copies differ; run with --write")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
