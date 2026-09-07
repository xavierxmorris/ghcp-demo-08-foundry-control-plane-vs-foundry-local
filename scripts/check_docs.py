"""Check local documentation integrity without making external truth claims."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ("README.md", "WORKSHOP.md", "docs/evidence.md")


def anchors(text: str) -> set[str]:
    result = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    counts: dict[str, int] = {}
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", text):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def check_links(root: Path) -> int:
    count = 0
    for relative in DOCUMENTS:
        document = root / relative
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            path = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                raise ValueError(f"{relative}: missing or out-of-repository link {target}")
            if parsed.fragment and unquote(parsed.fragment) not in anchors(path.read_text(encoding="utf-8")):
                raise ValueError(f"{relative}: missing anchor {target}")
            count += 1
    return count


def check_evidence(root: Path) -> int:
    text = (root / "docs" / "evidence.md").read_text(encoding="utf-8")
    sections = list(re.finditer(r"(?m)^## (\d+)\. .+$", text))
    if not sections:
        raise ValueError("The evidence register contains no numbered claims")
    numbers = [int(section[1]) for section in sections]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Evidence claim numbers must be unique and consecutive")
    for index, section in enumerate(sections):
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        body = text[section.end():end]
        if not re.search(r"\*\*Sources?:\*\*[\s\S]*?https://learn\.microsoft\.com/", body):
            raise ValueError(f"Evidence claim {section[1]} has no Microsoft Learn source")
    return len(sections)


if __name__ == "__main__":
    print(f"Validated {check_links(ROOT)} local links and {check_evidence(ROOT)} sourced evidence sections.")
    print("External availability and the currency of platform claims are not assessed by this offline gate.")
