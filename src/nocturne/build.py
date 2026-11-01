"""Build every theme into themes/<app>/: the app's templates rendered, plus what its generate() writes."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from nocturne import paths
from nocturne.apps import every
from nocturne.palette import load
from nocturne.template import render

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.app import App
    from nocturne.palette import Palette

UTF8 = "utf-8"
IGNORED = {".DS_Store", "Thumbs.db"}


def app_files(app: App, palette: Palette) -> dict[str, str]:
    """One app's theme files, as {path relative to themes/<id>/: content}."""
    files: dict[str, str] = {}
    templates = paths.APPS / app.id / "templates"
    for src in sorted(templates.rglob("*")) if templates.is_dir() else []:
        if src.is_file() and src.name not in IGNORED:
            rel = src.relative_to(templates).as_posix()
            files[rel] = render(src.read_text(encoding=UTF8), palette, f"{app.id}/templates/{rel}")
    for rel, content in (app.generate(palette) if app.generate else {}).items():
        if rel in files:
            raise ValueError(f"{app.id}/{rel} comes from a template and from generate()")
        files[rel] = content
    return files


def outputs(palette: Palette) -> dict[str, str]:
    """Every theme file, as {path relative to themes/: content}."""
    return {f"{app.id}/{rel}": content for app in every() for rel, content in app_files(app, palette).items()}


def build(out: Path = paths.THEMES, palette_file: Path = paths.PALETTE) -> list[str]:
    """Write themes/ from scratch. Returns the files written."""
    files = outputs(load(palette_file))
    if out.exists():
        shutil.rmtree(out)
    for rel, content in files.items():
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding=UTF8, newline="\n")
        if content.startswith("#!"):
            dest.chmod(0o755)  # scripts (bordersrc) stay runnable
    return sorted(files)


def stale(out: Path = paths.THEMES, palette_file: Path = paths.PALETTE) -> list[str]:
    """Files in themes/ that differ from a fresh build, are missing or shouldn't be there."""
    files = outputs(load(palette_file))
    on_disk = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file() and p.name not in IGNORED}
    changed = [
        rel for rel, content in files.items() if rel not in on_disk or (out / rel).read_text(encoding=UTF8) != content
    ]
    return sorted(changed + list(on_disk - files.keys()))
