from __future__ import annotations

from pathlib import Path


def test_repository_does_not_contain_private_drive_paths():
    repo = Path(__file__).resolve().parents[1]
    forbidden = ["F:" + "\\", "E:" + "\\", "We" + "chat", "xwe" + "chat_files"]
    checked_suffixes = {".py", ".md", ".yaml", ".yml", ".toml", ".cff", ".txt"}
    offenders: list[str] = []
    for path in repo.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            if token in text:
                offenders.append(str(path.relative_to(repo)))
                break
    assert offenders == []
