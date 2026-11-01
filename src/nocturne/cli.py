"""Command line: `nocturne build | check | preview | install | doctor | list`."""

from __future__ import annotations

import argparse
import io
import sys
from typing import TYPE_CHECKING

from nocturne import __version__, build, installer, paths, preview, system
from nocturne.app import Level
from nocturne.apps import every, registry
from nocturne.palette import load
from nocturne.style import DIM, GREEN, PURPLE, RED, RESET, YELLOW, heading
from nocturne.template import TemplateError

if TYPE_CHECKING:
    from nocturne.app import App

EPILOG = f"""\
levels (each adds to the one before; an app gets the highest it has):
  theme    colours only
  look     adds the window settings that go with them, where an app has any: the terminals
           see-through with blur (Ghostty and kitty also a cursor trail, no title bar);
           AeroSpace's gaps (default)
  full     adds whole setups: LazyVim, a complete p10k config, Zen's mods, the font

examples:
  nocturne install --dry-run           show what installing every app would change
  nocturne install tmux fzf            theme just these
  nocturne install --level full nvim   LazyVim with the colorscheme
  nocturne doctor                      which apps are themed, and how far
  nocturne build                       regenerate themes/ after editing palette.toml

{DIM}dracula, but later at night{RESET}"""


def _apps(ids: list[str]) -> list[App] | None:
    unknown = [i for i in ids if i not in registry()]
    if unknown:
        print(f"nocturne: unknown app: {', '.join(unknown)} (see: nocturne list)", file=sys.stderr)
        return None
    return [registry()[i] for i in ids] if ids else every()


def cmd_build(_args: argparse.Namespace) -> int:
    files = build.build()
    print(f"{GREEN}✓{RESET} {len(files)} files in {paths.THEMES.name}/")
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    bad = build.stale()
    for rel in bad:
        print(f"  {RED}✗{RESET} themes/{rel}")
    if bad:
        print("themes/ is out of date: run nocturne build", file=sys.stderr)
        return 1
    print(f"{GREEN}✓{RESET} themes/ matches palette.toml")
    return 0


def cmd_preview(_args: argparse.Namespace) -> int:
    print(preview.render(load(paths.PALETTE)), end="")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    apps = _apps(args.apps)
    if apps is None:
        return 2
    opt = installer.Options(dry_run=args.dry_run, force=args.force, level=Level[args.level.upper()])
    if args.undo:
        return installer.undo(apps, opt, everything=not args.apps)
    if not args.apps and not args.dry_run and not args.yes:
        print(f"This themes every app it finds at --level {opt.level}: links and include lines, nothing overwritten.")
        print(f"{DIM}Preview it with --dry-run, take it out again with --undo.{RESET}")
        if input("Go ahead? [y/N] ").strip().lower() not in {"y", "yes"}:
            return 1
    return installer.install(apps, opt, named=bool(args.apps))


STATES = {
    "hooked up": GREEN,
    "partly": YELLOW,
    "stale": YELLOW,
    "not hooked up": YELLOW,
    "manual": PURPLE,
    "no app": DIM,
    "n/a": DIM,
}


def cmd_doctor(_args: argparse.Namespace) -> int:
    width = max(len(app.title) for app in every()) + 2
    for app in every():
        state, detail = installer.status(app)
        print(f"  {STATES[state]}{state:<15}{RESET}{app.title:<{width}}{DIM}{detail}{RESET}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    width = max(len(app.id) for app in every()) + 2
    for app in every():
        only = "" if app.platforms == system.EVERYWHERE else f" {DIM}({', '.join(sorted(app.platforms))}){RESET}"
        heading(f"{app.id:<{width}}{RESET}{app.title}{only}")
        for level, tier in sorted(app.tiers.items()):
            print(f"  {DIM}{level!s:<6}{RESET} {tier.about}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nocturne",
        description="Dracula Nocturne: one palette, a theme for every app.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--version", action="version", version=f"nocturne {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="regenerate themes/ from palette.toml").set_defaults(fn=cmd_build)
    sub.add_parser("check", help="fail if themes/ is out of date").set_defaults(fn=cmd_check)
    sub.add_parser("preview", help="show the palette in the terminal").set_defaults(fn=cmd_preview)
    sub.add_parser("doctor", help="which apps are hooked up to these themes").set_defaults(fn=cmd_doctor)
    sub.add_parser("list", help="the apps and their levels").set_defaults(fn=cmd_list)
    ins = sub.add_parser(
        "install",
        help="hook the themes into your configs",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ins.add_argument("apps", nargs="*", metavar="APP", help="only these (default: all)")
    ins.add_argument(
        "-l",
        "--level",
        choices=[str(lv) for lv in Level],
        default=str(Level.LOOK),
        help="how far to go (default: look)",
    )
    ins.add_argument("-n", "--dry-run", action="store_true", help="show what would change")
    ins.add_argument("--undo", action="store_true", help="take everything out again")
    ins.add_argument("--force", action="store_true", help="move files that are in the way aside")
    ins.add_argument("-y", "--yes", action="store_true", help="don't ask")
    ins.set_defaults(fn=cmd_install)
    return p


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # a console or pipe in a code page without ✓ or the icons
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="replace")
    args = parser().parse_args(argv)
    if not paths.PALETTE.exists():
        print("nocturne: runs from a clone of the repository (no palette.toml next to it)", file=sys.stderr)
        return 1
    try:
        return int(args.fn(args))
    except KeyError as e:  # a template or generator asked for a colour the palette doesn't have
        print(f"nocturne: {e.args[0]}", file=sys.stderr)
        return 1
    except (TemplateError, ValueError, OSError) as e:
        print(f"nocturne: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
