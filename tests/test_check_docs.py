from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import anchors, check_evidence, check_links


class DocumentationContractTests(unittest.TestCase):
    def test_duplicate_heading_anchors_have_distinct_suffixes(self) -> None:
        self.assertEqual(anchors("# Same heading\n## Same heading\n"), {"same-heading", "same-heading-1"})

    def test_missing_or_outside_local_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for target in ("missing.md", "../outside.md", "#missing-anchor"):
                with self.subTest(target=target):
                    (root / "README.md").write_text(f"# Title\n[link]({target})", encoding="utf-8")
                    with self.assertRaises(ValueError):
                        check_links(root)

    def test_empty_unsourced_or_duplicate_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            valid = "## 1. Claim\n**Source:** [Learn](https://learn.microsoft.com/example)\n"
            path = root / "docs" / "evidence.md"
            path.write_text(valid, encoding="utf-8")
            self.assertEqual(check_evidence(root), 1)
            for text in ("", "## 1. No source\n", valid + valid):
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        check_evidence(root)


if __name__ == "__main__":
    unittest.main()
