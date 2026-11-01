"""The themed apps. Each one is a package here, named after its id, that defines APP (an App);
templates/ next to it are rendered into themes/<id>/. Adding an app means adding a package:
nothing else lists them."""

from __future__ import annotations

import importlib
import pkgutil
from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nocturne.app import App


@cache
def registry() -> dict[str, App]:
    apps: list[App] = []
    for info in pkgutil.iter_modules(__path__):
        app: App = importlib.import_module(f"{__name__}.{info.name}").APP
        if app.id != info.name:
            raise ValueError(f"nocturne/apps/{info.name} defines an app with the id {app.id!r}")
        apps.append(app)
    return {app.id: app for app in sorted(apps, key=lambda a: (a.group, a.title.lower()))}


def every() -> list[App]:
    return list(registry().values())
