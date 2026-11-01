"""install, undo and doctor against an empty home folder."""

import io
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

from nocturne import cli, paths, shells, system
from nocturne.apps import lazygit, registry, windows_terminal, yazi
from nocturne.apps import nvim as nvim_app
from nocturne.installer import status
from nocturne.ledger import Ledger
from nocturne.steps import BACKUP, MARKER

# zsh, bash, fish, XDG, and the apps that only run on macOS and Linux
posix = pytest.mark.skipif(sys.platform == "win32", reason="macOS and Linux only")


def can_symlink() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            (Path(tmp) / "link").symlink_to(tmp, target_is_directory=True)
        except OSError:
            return False
        return True


# tests that make symbolic links of their own (Windows allows them in Developer Mode, or to admins)
symlinks = pytest.mark.skipif(not can_symlink(), reason="no permission to make symbolic links")


@pytest.fixture
def profile(home: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An empty PowerShell profile: the shell file every system can have, so line edits get tested on all."""
    file = home / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
    file.parent.mkdir(parents=True)
    file.write_bytes(b"")
    monkeypatch.setattr(shells, "pwsh_profiles", lambda: [file])
    return file


def run(*argv: str) -> int:
    return cli.main(list(argv))


def tree(home: Path) -> list[Path]:
    return sorted(p.relative_to(home) for p in home.rglob("*"))


def test_dry_run_changes_nothing(home: Path):
    assert run("install", "--dry-run", "--level", "full") == 0
    assert tree(home) == []


@posix
def test_install_and_undo(home: Path):
    zshrc = home / ".zshrc"
    zshrc.write_text("# mine\n")
    tmux = home / ".config" / "tmux" / "tmux.conf"
    tmux.parent.mkdir(parents=True)
    tmux.write_text("set -g mouse on\n")

    assert run("install", "-y", "ghostty", "kitty", "tmux", "fzf", "eza", "btop") == 0
    assert (home / ".config" / "dracula-nocturne").is_symlink()
    assert (home / ".config" / "ghostty" / "themes" / "dracula-nocturne").is_symlink()
    assert "theme = dracula-nocturne" in (home / ".config" / "ghostty" / "config.ghostty").read_text()
    assert (
        "include ~/.config/dracula-nocturne/kitty/dracula-nocturne.conf"
        in (home / ".config/kitty/kitty.conf").read_text()
    )
    assert "source-file -q ~/.config/dracula-nocturne/tmux/dracula-nocturne.conf" in tmux.read_text()
    fzf = "$HOME/.config/dracula-nocturne/fzf/fzf.sh"
    assert f'[ -r "{fzf}" ] && . "{fzf}"' in zshrc.read_text()
    assert not (home / ".bashrc").exists()  # a zsh user doesn't get a .bashrc
    for app in ("ghostty", "kitty", "tmux", "fzf"):
        assert status(registry()[app])[0] in {"hooked up", "no app"}

    before = tmux.read_text()
    assert run("install", "-y", "tmux") == 0
    assert tmux.read_text() == before  # twice is the same as once

    assert run("install", "--undo") == 0
    assert tmux.read_text() == "set -g mouse on\n"
    assert zshrc.read_text() == "# mine\n"
    assert not (home / ".config" / "dracula-nocturne").exists()
    # what install created is gone again; the user's folders stay
    assert not (home / ".config" / "ghostty").exists()
    assert not (home / ".config" / "kitty").exists()
    assert (home / ".config" / "tmux").is_dir()


@posix
def test_levels_add_up_and_come_out_again(home: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("nocturne.app.App.present", lambda _self: True)  # doctor asks whether Ghostty is there
    config = home / ".config" / "ghostty" / "config.ghostty"
    assert run("install", "-y", "--level", "full", "ghostty") == 0
    text = config.read_text()
    assert "theme = dracula-nocturne" in text
    assert "look.ghostty" in text
    assert "full.ghostty" in text
    assert status(registry()["ghostty"]) == ("hooked up", "full")
    assert run("install", "-y", "--level", "theme", "ghostty") == 0
    text = config.read_text()
    assert "theme = dracula-nocturne" in text
    assert "look.ghostty" not in text
    assert "full.ghostty" not in text
    assert status(registry()["ghostty"]) == ("hooked up", "theme")


@posix
def test_look_is_the_default(home: Path):
    assert run("install", "-y", "kitty") == 0
    text = (home / ".config" / "kitty" / "kitty.conf").read_text()
    assert "kitty/look.conf" in text
    assert "kitty/full.conf" not in text


@pytest.mark.usefixtures("home")
def test_an_app_that_starts_above_the_level_is_left_out(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(system, "current", lambda: system.OS.MACOS)  # AeroSpace is macOS only
    assert run("install", "-y", "--level", "theme", "aerospace") == 0
    assert "starts at --level look" in capsys.readouterr().out


def test_existing_files_are_left_alone(home: Path):
    theme = home / ".config" / "eza" / "theme.yml"
    theme.parent.mkdir(parents=True)
    theme.write_text("mine")
    assert run("install", "-y", "eza") == 1
    assert theme.read_text() == "mine"


def test_force_moves_aside_and_undo_restores(home: Path):
    theme = home / ".config" / "eza" / "theme.yml"
    theme.parent.mkdir(parents=True)
    theme.write_text("mine")
    assert run("install", "-y", "--force", "eza") == 0
    assert theme.read_text() != "mine"
    assert (theme.parent / f"theme.yml{BACKUP}").read_text() == "mine"
    assert run("install", "--undo", "eza") == 0
    assert theme.read_text() == "mine"


def test_force_never_overwrites_a_backup(home: Path):
    theme = home / ".config" / "eza" / "theme.yml"
    theme.parent.mkdir(parents=True)
    theme.write_text("first")
    assert run("install", "-y", "--force", "eza") == 0
    theme.unlink()
    theme.write_text("second")
    assert run("install", "-y", "--force", "eza") == 1
    assert theme.read_text() == "second"
    assert (theme.parent / f"theme.yml{BACKUP}").read_text() == "first"


@symlinks
def test_undo_leaves_a_broken_symlink_of_the_user_alone(home: Path):
    theme = home / ".config" / "eza" / "theme.yml"
    theme.parent.mkdir(parents=True)
    (theme.parent / f"theme.yml{BACKUP}").write_text("old")
    theme.symlink_to(home / "gone")
    assert run("install", "--undo", "eza") == 0
    assert theme.is_symlink()
    assert (theme.parent / f"theme.yml{BACKUP}").exists()


def test_lines_go_into_an_empty_file_without_a_blank_first_line(profile: Path):
    assert run("install", "-y", "fzf") == 0
    assert profile.read_text().startswith(f"# {MARKER}")


def test_undo_of_one_app_leaves_the_others(profile: Path):
    assert run("install", "-y", "fzf", "lazygit") == 0
    assert run("install", "--undo", "fzf") == 0
    assert "fzf.ps1" not in profile.read_text()
    assert "LG_CONFIG_FILE" in profile.read_text()


def test_undo_keeps_a_line_the_user_changed(profile: Path):
    assert run("install", "-y", "fzf") == 0
    edited = profile.read_bytes().replace(b"Test-Path", b"Test-Path -LiteralPath") + b"$env:MINE = 1\n"
    profile.write_bytes(edited)
    assert run("install", "--undo") == 0
    assert profile.read_bytes() == edited


@posix
def test_undo_finds_lines_after_the_file_choice_changed(home: Path):
    """install wrote to ~/.tmux.conf; a ~/.config/tmux/tmux.conf that appears later doesn't hide it."""
    classic = home / ".tmux.conf"
    classic.write_text("set -g mouse on\n")
    assert run("install", "-y", "tmux") == 0
    assert "source-file" in classic.read_text()
    xdg = home / ".config" / "tmux" / "tmux.conf"
    xdg.parent.mkdir(parents=True)
    xdg.write_text("")
    assert run("install", "--undo", "tmux") == 0
    assert classic.read_text() == "set -g mouse on\n"


def test_full_undo_leaves_no_trace(home: Path, profile: Path):
    profile.write_text("# mine\n")
    apps = ["fzf", "yazi", "nvim", "eza", "lazygit", "windows_terminal"]  # (bat: its own test, as its cache needs bat)
    if sys.platform != "win32":  # (btop4win keeps its themes next to its program, outside any home folder)
        (home / ".zshrc").write_text("# mine\n")
        apps += ["ghostty", "kitty", "tmux", "btop"]
    before = tree(home)
    assert run("install", "-y", "--level", "full", *apps) == 0
    assert run("install", "--undo") == 0
    assert tree(home) == before
    assert profile.read_text() == "# mine\n"


@posix
def test_relative_xdg_paths_are_ignored(home: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", "relative")
    monkeypatch.chdir(home)
    assert run("install", "-y", "kitty") == 0
    assert (home / ".config" / "kitty" / "kitty.conf").is_file()
    assert not (home / "relative").exists()


def test_apps_follow_their_own_variables(home: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("YAZI_CONFIG_HOME", str(home / "yazi-here"))
    monkeypatch.setenv("NVIM_APPNAME", "lazy")
    apps = ["yazi", "nvim"]
    if sys.platform != "win32":
        monkeypatch.setenv("KITTY_CONFIG_DIRECTORY", str(home / "kitty-here"))
        apps.append("kitty")
    assert run("install", "-y", *apps) == 0
    assert (home / "yazi-here" / "flavors" / "dracula-nocturne.yazi").exists()
    assert nvim_app.config_dir().name == "lazy"
    assert (nvim_app.config_dir() / "colors" / "dracula-nocturne.lua").exists()
    if "kitty" in apps:
        assert (home / "kitty-here" / "kitty.conf").is_file()


@posix
def test_no_fish_files_without_fish(home: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(shells, "fish_used", lambda: False)
    (home / ".zshrc").write_text("")
    assert run("install", "-y", "fzf") == 0
    assert not (home / ".config" / "fish").exists()


@posix
def test_full_install_skips_apps_that_are_not_there(home: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    monkeypatch.setattr("nocturne.app.App.present", lambda self: self.binary is None and self.detect is None)
    (home / ".zshrc").write_text("")
    assert run("install", "-y") == 0
    # only LS_COLORS, which needs no program
    assert (home / ".zshrc").read_text().count(MARKER) == 1
    assert not (home / ".config" / "kitty").exists()


@pytest.mark.usefixtures("home")
def test_bat_selects_its_theme():
    assert run("install", "-y", "bat") in {0, 1}  # 1 where bat isn't there to rebuild its cache
    assert '--theme="Dracula Nocturne"' in (system.app_config() / "bat" / "config").read_text()


@pytest.mark.usefixtures("home")
def test_yazi_gets_a_theme_toml_only_if_it_has_none():
    theme = yazi.config_dir() / "theme.toml"
    assert run("install", "-y", "yazi") == 0
    assert 'dark = "dracula-nocturne"' in theme.read_text()
    assert run("install", "--undo", "yazi") == 0
    theme.parent.mkdir(parents=True, exist_ok=True)
    theme.write_text("[mgr]\n")
    assert run("install", "-y", "yazi") == 0
    assert theme.read_text() == "[mgr]\n"


def test_copies_are_refreshed_and_removed_only_while_unchanged(home: Path):
    (home / ".t3" / "userdata").mkdir(parents=True)
    dest = home / ".t3" / "userdata" / "themes" / "dracula-nocturne.json"
    assert run("install", "-y", "t3code") == 0
    assert dest.is_file()
    assert not dest.is_symlink()  # T3 Code won't read a link
    dest.write_text("{}")  # an older copy, as after a build
    Ledger().record_copy(dest)
    assert status(registry()["t3code"])[0] == "stale"
    assert run("install", "-y", "t3code") == 0
    assert dest.read_text() != "{}"
    assert run("install", "--undo", "t3code") == 0
    assert not dest.exists()
    assert (home / ".t3" / "userdata").is_dir()  # T3's own folder stays


def test_a_copy_the_user_edited_is_theirs(home: Path):
    dest = home / ".t3" / "userdata" / "themes" / "dracula-nocturne.json"
    assert run("install", "-y", "t3code") == 0
    dest.write_text("edited")
    assert run("install", "-y", "t3code") == 1  # not overwritten
    assert run("install", "--undo", "t3code") == 0  # nor deleted
    assert dest.read_text() == "edited"
    assert run("install", "-y", "--force", "t3code") == 0
    assert (dest.parent / f"dracula-nocturne.json{BACKUP}").read_text() == "edited"


@posix
def test_p10k_only_for_p10k_users(home: Path):
    (home / ".zshrc").write_text("export FOO=1\n")
    assert run("install", "-y") == 0
    assert "p10k" not in (home / ".zshrc").read_text()
    (home / ".p10k.zsh").write_text("")
    assert run("install", "-y") == 0
    assert "p10k/dracula-nocturne.zsh" in (home / ".zshrc").read_text()


@posix
def test_p10k_full_leaves_a_config_of_the_user_alone(home: Path):
    (home / ".zshrc").write_text("source ~/.p10k.zsh\n")
    (home / ".p10k.zsh").write_text("# mine\n")
    assert run("install", "-y", "--level", "full", "p10k") == 1
    assert (home / ".p10k.zsh").read_text() == "# mine\n"
    (home / ".p10k.zsh").unlink()
    assert run("install", "-y", "--level", "full", "p10k") == 0
    assert "POWERLEVEL9K_LEFT_PROMPT_ELEMENTS" in (home / ".p10k.zsh").read_text()


@pytest.mark.usefixtures("home")
def test_nvim_full_sets_up_lazyvim_in_an_empty_config():
    nvim = nvim_app.config_dir()
    assert run("install", "-y", "--level", "full", "nvim") == 0
    assert (nvim / "colors" / "dracula-nocturne.lua").exists()
    assert (nvim / "init.lua").is_file()
    assert 'colorscheme = "dracula-nocturne"' in (nvim / "lua" / "plugins" / "dracula-nocturne.lua").read_text()


@pytest.mark.usefixtures("home")
def test_nvim_full_only_adds_the_spec_to_a_lazyvim_config():
    nvim = nvim_app.config_dir()
    (nvim / "lua" / "config").mkdir(parents=True)
    (nvim / "lua" / "config" / "lazy.lua").write_text("-- mine\n")
    (nvim / "init.lua").write_text("-- mine\n")
    assert run("install", "-y", "--level", "full", "nvim") == 0
    assert (nvim / "init.lua").read_text() == "-- mine\n"
    assert (nvim / "lua" / "plugins" / "dracula-nocturne.lua").is_file()


@posix
@pytest.mark.usefixtures("linux")
def test_zen_finds_the_profile_and_links_into_it(home: Path):
    root = home / ".config" / "zen"
    profile = root / "abc.Default (release)"
    profile.mkdir(parents=True)
    (root / "installs.ini").write_text("[ABCDEF]\nDefault=abc.Default (release)\nLocked=1\n")
    assert run("install", "-y", "zen") == 0
    assert (profile / "user.js").is_symlink()
    assert not (profile / "chrome").exists()  # the halos are full only
    assert run("install", "-y", "--level", "full", "zen") == 0
    assert (profile / "chrome" / "userChrome.css").is_symlink()


@pytest.mark.usefixtures("linux")
def test_zen_profile_survives_odd_ini_files(home: Path):
    (home / ".zen").mkdir()
    (home / ".zen" / "profiles.ini").write_bytes(b"[Profile0]\nName=caf\xe9\nPath=x\nDefault=1\n")
    assert run("doctor") == 0


def test_powershell_gets_the_lines_and_on_windows_a_profile(home: Path, monkeypatch: pytest.MonkeyPatch):
    profile = home / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
    monkeypatch.setattr(shells, "pwsh_profiles", lambda: [profile])
    monkeypatch.setattr(system, "current", lambda: system.OS.WINDOWS)
    assert run("install", "-y", "fzf", "lazygit") == 0
    text = profile.read_text()
    assert '. "$env:APPDATA/dracula-nocturne/fzf/fzf.ps1"' in text
    assert "$env:LG_CONFIG_FILE = " in text
    assert run("install", "--undo") == 0
    assert not profile.exists()


def test_links_fall_back_to_copies_where_windows_refuses_them(home: Path, monkeypatch: pytest.MonkeyPatch):
    original = Path.symlink_to

    def picky(self: Path, target: Path, target_is_directory: bool = False) -> None:
        if self.name != "dracula-nocturne":  # the folder link is a junction there, out of reach here
            raise OSError("symbolic link privilege not held")
        original(self, target, target_is_directory)

    monkeypatch.setattr(system, "current", lambda: system.OS.WINDOWS)
    monkeypatch.setattr(Path, "symlink_to", picky)
    theme = home / "AppData" / "Roaming" / "eza" / "theme.yml"
    monkeypatch.setenv("EZA_CONFIG_DIR", str(theme.parent))
    assert run("install", "-y", "eza") == 0
    assert theme.is_file()
    assert not theme.is_symlink()
    assert run("install", "--undo") == 0
    assert not theme.exists()


@pytest.mark.usefixtures("home")
def test_unknown_app(capsys: pytest.CaptureFixture[str]):
    assert run("install", "wezterm") == 2
    assert "unknown app" in capsys.readouterr().err


@pytest.mark.parametrize("command", ["list", "doctor", "check", "preview"])
@pytest.mark.usefixtures("home")
def test_commands_run(command: str):
    assert run(command) == 0


@pytest.mark.usefixtures("home")
def test_undo_takes_out_the_starter_after_the_user_edited_part_of_it():
    nvim = nvim_app.config_dir()
    assert run("install", "-y", "--level", "full", "nvim") == 0
    (nvim / "lua" / "config" / "lazy.lua").write_text("-- edited\n")
    assert run("install", "--undo", "nvim") == 0
    assert not (nvim / "init.lua").exists()  # unchanged starter files go
    assert (nvim / "lua" / "config" / "lazy.lua").read_text() == "-- edited\n"  # the edited one stays


@symlinks
def test_a_stale_link_of_ours_is_replaced(home: Path):
    theme = home / ".config" / "eza" / "theme.yml"
    theme.parent.mkdir(parents=True)
    assert run("install", "-y", "eza") == 0
    theme.unlink()
    theme.symlink_to(paths.link_dir() / "eza" / "old-name.yml")  # a theme renamed since
    assert run("install", "-y", "eza") == 0
    assert theme.resolve().name == "theme.yml"


@symlinks
@pytest.mark.usefixtures("home")
def test_a_moved_checkout_is_followed(tmp_path: Path):
    link = paths.link_dir()
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(tmp_path / "where-the-checkout-was", target_is_directory=True)
    assert run("install", "-y", "eza") == 0
    assert (link / "eza" / "theme.yml").is_file()


def test_configs_in_other_encodings_survive(profile: Path):
    profile.write_bytes(b"# caf\xe9\n")  # Latin-1, as older editors on Windows save it
    assert run("install", "-y", "fzf") == 0
    assert profile.read_bytes().startswith(b"# caf\xe9\n")
    assert run("install", "--undo") == 0
    assert profile.read_bytes() == b"# caf\xe9\n"


@pytest.mark.parametrize("end", [b"\n", b"\r\n"])
def test_lines_keep_the_files_line_ends(profile: Path, end: bytes):
    profile.write_bytes(b"# mine" + end)
    assert run("install", "-y", "fzf", "lazygit") == 0
    added = profile.read_bytes()
    assert added.count(end) == added.count(b"\n")  # every line ends the same way
    assert run("install", "--undo") == 0
    assert profile.read_bytes() == b"# mine" + end


def test_a_utf16_powershell_profile_stays_utf16(home: Path, monkeypatch: pytest.MonkeyPatch):
    profile = home / "profile.ps1"
    profile.write_text("# mine\n", encoding="utf-16")
    monkeypatch.setattr(shells, "pwsh_profiles", lambda: [profile])
    assert run("install", "-y", "fzf") == 0
    assert "fzf.ps1" in profile.read_text(encoding="utf-16")


def test_an_edited_copy_is_not_called_stale(home: Path):
    (home / ".t3" / "userdata").mkdir(parents=True)
    assert run("install", "-y", "t3code") == 0
    (home / ".t3" / "userdata" / "themes" / "dracula-nocturne.json").write_text("{}")
    assert status(registry()["t3code"])[0] != "stale"


def test_a_line_whose_path_changed_is_replaced_not_doubled(home: Path, profile: Path, monkeypatch: pytest.MonkeyPatch):
    assert run("install", "-y", "lazygit") == 0
    monkeypatch.setenv("CONFIG_DIR", str(home / "elsewhere"))
    assert run("install", "-y", "lazygit") == 0
    assert profile.read_text().count("LG_CONFIG_FILE") == 1
    assert "elsewhere" in profile.read_text()
    assert run("install", "--undo") == 0
    assert profile.read_text() == ""


@pytest.mark.usefixtures("home")
def test_lazygit_gets_a_config_to_start_with_and_keeps_a_filled_one():
    config = lazygit.config_dir() / "config.yml"
    assert run("install", "-y", "lazygit") == 0
    assert config.read_text() == ""  # lazygit won't start while a file in LG_CONFIG_FILE is missing
    assert run("install", "--undo") == 0
    assert not config.exists()
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("gui:\n  nerdFontsVersion: '3'\n")
    assert run("install", "-y", "lazygit") == 0
    assert run("install", "--undo") == 0
    assert config.read_text() == "gui:\n  nerdFontsVersion: '3'\n"


@pytest.mark.usefixtures("home")
def test_windows_terminal_levels_add_up_and_come_out_again(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(system, "current", lambda: system.OS.WINDOWS)
    monkeypatch.setattr("nocturne.app.App.present", lambda _self: True)
    fragments = windows_terminal.fragments()
    assert run("install", "-y", "windows_terminal") == 0
    assert sorted(f.name for f in fragments.iterdir()) == ["dracula-nocturne.json", "look.json"]
    assert run("install", "-y", "--level", "full", "windows_terminal") == 0
    assert status(registry()["windows_terminal"]) == ("hooked up", "full")
    assert run("install", "-y", "--level", "theme", "windows_terminal") == 0
    assert [f.name for f in fragments.iterdir()] == ["dracula-nocturne.json"]
    assert run("install", "--undo") == 0
    assert not fragments.exists()


def test_output_in_a_code_page_without_the_symbols(monkeypatch: pytest.MonkeyPatch):
    """Windows writes to a pipe, and some consoles, in cp1252, which has no ✓."""
    out = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", out)
    assert run("check") == 0
    out.flush()
    assert b"themes/ matches" in out.buffer.getvalue()  # pyright: ignore[reportAttributeAccessIssue]
