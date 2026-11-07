"""Print Jezero site-grid metadata without loading elevation arrays."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "data" / "jez_hirise_site_detail_4m.json"


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    cut = raw.find(',"valid_mask"')
    meta = json.loads(raw[:cut] + "}")
    for key, value in meta.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
