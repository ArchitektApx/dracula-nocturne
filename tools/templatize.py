"""Turn an existing themed config into a template: every palette colour becomes {{name}}.

    uv run tools/templatize.py FILE > src/nocturne/apps/APP/templates/NAME

When a hex value has several names, the first in PRIORITY wins. Hex values that aren't in the
palette are reported on stderr and left as they are.
"""

import re
import sys
from pathlib import Path

from nocturne.palette import load

PRIORITY = ("", "bright.", "tint.", "syntax.", "editor.", "ui.")
ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    pal = load(ROOT / "palette.toml")
    names: dict[str, str] = {}
    for prefix in PRIORITY:
        for name, color in pal.colors.items():
            flat = "." not in name
            if (prefix == "" and flat) or (prefix and name.startswith(prefix)):
                names.setdefault(color.hex, name)
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    unknown: set[str] = set()

    def sub(m: re.Match[str]) -> str:
        h = m.group(0).lower()
        if h in names:
            return "{{" + names[h] + "}}"
        unknown.add(h)
        return m.group(0)

    sys.stdout.write(re.sub(r"#[0-9a-fA-F]{6}\b", sub, text))
    if unknown:
        print("not in the palette:", " ".join(sorted(unknown)), file=sys.stderr)


main()
