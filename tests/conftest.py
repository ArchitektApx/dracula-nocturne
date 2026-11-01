import subprocess
from pathlib import Path

import pytest

from nocturne import paths, shells, system
from nocturne.build import outputs
from nocturne.palette import Palette, load

# Variables that would point the apps somewhere outside the test's home folder
FOREIGN = (
    "ZDOTDIR", "BAT_CONFIG_DIR", "BAT_CONFIG_PATH", "KITTY_CONFIG_DIRECTORY", "NVIM_APPNAME", "T3CODE_HOME",
    "CONFIG_DIR", "YAZI_CONFIG_HOME", "XDG_STATE_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME",
)  # fmt: skip


@pytest.fixture(scope="session")
def palette() -> Palette:
    return load(paths.PALETTE)


@pytest.fixture(scope="session")
def files(palette: Palette) -> dict[str, str]:
    return outputs(palette)


@pytest.fixture(autouse=True)
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Every test gets an empty home folder with every config location in it, so none can reach the
    real ones."""
    for var in FOREIGN:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path / "AppData" / "Roaming"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "AppData" / "Local"))
    # eza's folder differs between the systems; pin it so the tests read the same everywhere
    monkeypatch.setenv("EZA_CONFIG_DIR", str(tmp_path / ".config" / "eza"))
    monkeypatch.setattr(system, "ask", lambda _argv: None)
    monkeypatch.setattr(shells, "pwsh_profiles", list)
    return tmp_path


@pytest.fixture
def home(isolated: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """The test's home folder, for installs: tools aren't run (code --install-extension, bat cache
    --build), their commands just succeed."""
    monkeypatch.setattr(subprocess, "run", lambda argv, **_: subprocess.CompletedProcess(argv, 0, "", ""))
    return isolated


@pytest.fixture
def linux(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(system, "current", lambda: system.OS.LINUX)
