<div align="center">

<img src="assets/hero.svg" width="760" alt="Dracula Nocturne: the name over its palette, from near-black to Dracula's accents">

**Dracula on near-black for terminals, editors, prompts and the browser, all from one palette.**

[![tests](https://img.shields.io/github/actions/workflow/status/ArchitektApx/dracula-nocturne/ci.yml?branch=master&style=flat-square&label=tests&color=50fa7b&labelColor=21222c)](https://github.com/ArchitektApx/dracula-nocturne/actions)
[![license](https://img.shields.io/badge/license-MIT-bd93f9?style=flat-square&labelColor=21222c)](LICENSE)
[![python](https://img.shields.io/badge/python-3.12+-ff79c6?style=flat-square&labelColor=21222c)](https://www.python.org)
[![platforms](https://img.shields.io/badge/platform-macOS%20%C2%B7%20Linux%20%C2%B7%20Windows-8be9fd?style=flat-square&labelColor=21222c)](#apps)
[![apps](https://img.shields.io/badge/apps-21-f1fa8c?style=flat-square&labelColor=21222c)](#apps)

</div>

Every theme is generated from [`palette.toml`](palette.toml), so a change there reaches every app. `nocturne install` adds the themes to your configs at one of three levels and never overwrites a file of yours.

<img src="assets/desktop.png" width="100%" alt="The whole look on one desktop: Ghostty with tmux, the prompt and Neovim, Zen next to it, JankyBorders around the focused window">

## Install

```sh
git clone https://github.com/ArchitektApx/dracula-nocturne && cd dracula-nocturne
uv run nocturne install --dry-run     # what would change
uv run nocturne install               # every app it finds; or name some: install tmux fzf
```

You'll need [uv](https://docs.astral.sh/uv/) (it brings Python 3.12+) and a [Nerd Font](https://www.nerdfonts.com) for the icons and rounded tabs. You can also copy the files in [`themes/`](themes) by hand.

| Level | What it adds |
| :-- | :-- |
| `theme` | Colours only. |
| `look` *(default)* | Adds window settings: the terminals become see-through with blur (Ghostty and kitty also get a cursor trail and no title bar), and AeroSpace gets gaps. |
| `full` | Adds complete setups: LazyVim, a full Powerlevel10k prompt, Zen's mods and the Nerd Font. |

Each level includes the ones before it, and installing a lower level removes the extras again. If a file of yours is in the way, install leaves it alone; `--force` moves it aside. `nocturne install --undo` removes everything, and `nocturne doctor` shows what is installed where. Config folders are found the same way each app finds them: through `$XDG_CONFIG_HOME`, the app's own variables (`KITTY_CONFIG_DIRECTORY`, `NVIM_APPNAME`, `YAZI_CONFIG_HOME`, `EZA_CONFIG_DIR`, `T3CODE_HOME` and so on) and `%APPDATA%` on Windows.

## Apps

### Terminals

| | theme | look | full |
| :-- | :-: | :-: | :-: |
| **[Ghostty](https://ghostty.org)**<br><sub>macOS · Linux</sub> | <img src="assets/apps/ghostty-theme.png" width="250" alt="Ghostty with the colours"><br><sub>the colours</sub> | <img src="assets/apps/ghostty-look.png" width="250" alt="Ghostty see-through over a wallpaper"><br><sub>blur, cursor trail, no title bar</sub> | <img src="assets/apps/ghostty-full.png" width="250" alt="Ghostty with tmux and the prompt"><br><sub>MesloLGS Nerd Font</sub> |
| **[kitty](https://sw.kovidgoyal.net/kitty)**<br><sub>macOS · Linux</sub> | <img src="assets/apps/kitty-theme.png" width="250" alt="kitty with the colours"><br><sub>colours, tabs, split borders</sub> | <img src="assets/apps/kitty-look.png" width="250" alt="kitty see-through over a wallpaper"><br><sub>blur, cursor trail, powerline tabs</sub> | <img src="assets/apps/kitty-full.png" width="250" alt="kitty with tmux and the prompt"><br><sub>MesloLGS Nerd Font</sub> |
| **[Windows Terminal](https://github.com/microsoft/terminal)**<br><sub>Windows</sub> | <sub>the colours, on the PowerShell, Command Prompt and Git Bash profiles</sub> | <sub>acrylic see-through, block cursor, padding</sub> | <sub>MesloLGS Nerd Font</sub> |
| **[tmux](https://github.com/tmux/tmux)** 3.3+<br><sub>macOS · Linux</sub> | <img src="assets/apps/tmux-theme.png" width="250" alt="tmux tab bar"><br><sub>pill tabs, prefix badge, popups</sub> | | |

### Shell

| | theme | full |
| :-- | :-: | :-: |
| **[Powerlevel10k](https://github.com/romkatv/powerlevel10k)**<br><sub>macOS · Linux</sub> | <img src="assets/apps/p10k-theme.png" width="380" alt="p10k's lean style with the colours"><br><sub>colours and rounded tiles over your config</sub> | <img src="assets/apps/p10k-full.png" width="380" alt="the complete two-line prompt"><br><sub>the whole prompt: two lines, transient</sub> |
| **[oh-my-posh](https://ohmyposh.dev)** | <img src="assets/apps/omp-theme.png" width="380" alt="the oh-my-posh prompt"><br><sub>the same tiles, for any shell</sub> | |
| **LS_COLORS**<br><sub>macOS · Linux</sub> | <img src="assets/apps/ls_colors-theme.png" width="380" alt="ls with the file colours"><br><sub>eza's file colours for ls, fd, tree</sub> | |
| **[iris](https://github.com/versenilvis/iris)**<br><sub>macOS · Linux</sub> | <img src="assets/apps/iris-theme.png" width="380" alt="iris completion menu"><br><sub>completion menus</sub> | |

### Editors

| | theme | full |
| :-- | :-: | :-: |
| **[Neovim](https://neovim.io)** | <img src="assets/apps/nvim-theme.png" width="380" alt="Neovim with a see-through float"><br><sub>Pierre Dark code, see-through menus</sub> | <img src="assets/apps/nvim-full.png" width="380" alt="the LazyVim dashboard, see-through"><br><sub>LazyVim with it</sub> |
| **[VS Code](https://code.visualstudio.com)** | <img src="assets/apps/vscode-theme.png" width="380" alt="VS Code"><br><sub>window chrome and Pierre Dark code</sub> | |
| **[Cursor](https://cursor.com)** | <img src="assets/apps/cursor-theme.png" width="380" alt="Cursor"><br><sub>the VS Code theme</sub> | |
| **[T3 Code](https://github.com/pingdotgg/t3code)** | <img src="assets/apps/t3code-theme.png" width="380" alt="T3 Code"><br><sub>every role of its theme editor</sub> | |

### Tools

| | | |
| :-: | :-: | :-: |
| <img src="assets/apps/bat-theme.png" width="250" alt="bat"><br>**[bat](https://github.com/sharkdp/bat)**<br><sub>Pierre Dark code</sub> | <img src="assets/apps/eza-theme.png" width="250" alt="eza"><br>**[eza](https://eza.rocks)**<br><sub>files, permissions, git</sub> | <img src="assets/apps/fzf-theme.png" width="250" alt="fzf"><br>**[fzf](https://github.com/junegunn/fzf)**<br><sub>colours; your options still win</sub> |
| <img src="assets/apps/yazi-theme.png" width="250" alt="yazi"><br>**[yazi](https://yazi-rs.github.io)**<br><sub>a flavor, bat's code colours</sub> | <img src="assets/apps/lazygit-theme.png" width="250" alt="lazygit"><br>**[lazygit](https://github.com/jesseduffield/lazygit)**<br><sub>borders, selection, commits</sub> | <img src="assets/apps/btop-theme.png" width="250" alt="btop"><br>**[btop](https://github.com/aristocratos/btop)**<br><sub>meters as gradients</sub> |

### Desktop

| | theme | look | full |
| :-- | :-: | :-: | :-: |
| **[Zen](https://zen-browser.app)** | <sub>the accent colour, and the colours of its mods</sub> | | <img src="assets/apps/zen-full.png" width="250" alt="Zen with the halos"><br><sub>halos, Arc 2.0, see-through</sub> |
| **[JankyBorders](https://github.com/FelixKratz/JankyBorders)**<br><sub>macOS</sub> | <img src="assets/apps/borders-theme.png" width="250" alt="a window border"><br><sub>purple-to-pink window border</sub> | | |
| **[AeroSpace](https://github.com/nikitabobko/AeroSpace)**<br><sub>macOS</sub> | | gaps between the windows, JankyBorders started with it (see the desktop above) | |

`nocturne list` shows which of these your system supports.

## Goes well with

<a href="https://github.com/ArchitektApx/nekofetch"><img src="https://raw.githubusercontent.com/ArchitektApx/nekofetch/main/assets/screenshot.gif" width="560" alt="nekofetch: system info next to a pixel-art catgirl typing on a keyboard"></a>

[nekofetch](https://github.com/ArchitektApx/nekofetch) is fastfetch with catgirls, in the same colours. It opens every new shell with your system info, the weather and a cat.

## Notes

<details>
<summary><b>Neovim</b>: no plugin manager needed</summary>

`install` links the colorscheme into your config folder; select it with `vim.cmd.colorscheme("dracula-nocturne")`. At `full` it sets up [LazyVim](https://lazyvim.org) with the colorscheme. If you already use LazyVim, it only adds the colorscheme's spec. To use it as a lazy.nvim plugin without cloning this repo:

```lua
{
  "ArchitektApx/dracula-nocturne",
  lazy = false,
  priority = 1000,
  config = function(plugin)
    vim.opt.rtp:append(plugin.dir .. "/themes/nvim")
    require("dracula-nocturne").setup({ transparent = true }) -- optional
    vim.cmd.colorscheme("dracula-nocturne")
  end,
}
```

`setup()` takes `transparent`, `italic_comment` and `overrides`. `transparent` is on by default and leaves menus, floats and start screens without a background, so a see-through terminal shows through. Code keeps its solid background either way.
</details>

<details>
<summary><b>Powerlevel10k</b>: an overlay, or the whole prompt</summary>

p10k has no themes, only the settings in your `~/.p10k.zsh`. So `theme` adds an overlay that loads after it and sets the colours, rounded tiles and folder icons, made for the Lean style. Your segments and number of lines stay as they are. If you don't have a `~/.p10k.zsh`, `full` puts a complete one there, as a copy you can change.
</details>

<details>
<summary><b>Windows Terminal</b>: fragments, and see-through</summary>

The theme is a set of [JSON fragments](https://learn.microsoft.com/windows/terminal/json-fragment-extensions) in `%LOCALAPPDATA%\Microsoft\Windows Terminal\Fragments` that update the built-in profiles. Anything your `settings.json` sets for a profile takes precedence. Restart Windows Terminal after installing. The see-through look needs Windows' own Settings > Personalization > Colors > Transparency effects.
</details>

<details>
<summary><b>tmux</b>: options and ssh tabs</summary>

Set before the `source-file` line: `set -g @nocturne-spacer off` drops the empty line above the tabs, `set -g @nocturne-position top` moves the bar up. Tabs running ssh turn orange and show the host if your shell sets the window option `@ssh_host`; [`extras/tmux-ssh-host.zsh`](extras/tmux-ssh-host.zsh) does that for zsh and bash.
</details>

<details>
<summary><b>Zen</b>: mods and extensions for <code>full</code></summary>

The halos in `userChrome.css` need a few mods, which you install from wherever their authors publish them. `nocturne install zen --level full` lists the ones you're missing.

1. [Sine](https://github.com/CosmoCreeper/Sine), with its installer.
2. From Sine's marketplace: **Arc 2.0** (its README lists one more mod it needs) and **Better Find Bar**.
3. **Transparent Zen**: in Sine, `sameerasw/zen-themes`, folder `TransparentZen`, or from [Zen's mods page](https://zen-browser.app/mods/642854b5-88b4-4c40-b256-e035532109df).
4. The extensions [Zen Internet](https://addons.mozilla.org/firefox/addon/zen-internet/) and [Dark Reader](https://addons.mozilla.org/firefox/addon/darkreader/).
5. Optional: [Container Halo](https://zen-browser.app/mods/cb5efa80-f1e1-43ce-8c0b-fece8462d225), so container tabs keep their colour.

See-through works as is on macOS and on Windows 11 22H2 or newer. Linux needs Transparent Zen's Linux option and a compositor that blurs (KDE does; its guide covers Hyprland). `theme` alone sets Zen's accent colour and the mods' colours in `user.js`, which Zen reads at every start. Zen keeps those settings after `--undo`; reset them in `about:config` if you want them gone.
</details>

<details>
<summary><b>VS Code, Cursor, T3 Code</b></summary>

`install` packs the theme into an extension and installs it with `code` or `cursor`; pick it under **Preferences: Color Theme**. T3 Code won't read a link, so it gets a copy; run `install` again after changing the palette, then pick it in **Settings → Appearance** or with `t3 theme set dracula-nocturne`.
</details>

<details>
<summary><b>AeroSpace, JankyBorders</b></summary>

JankyBorders gets its `bordersrc`. AeroSpace can't include other files, so `install` prints what to add to your `aerospace.toml`: the gaps, and `borders` started with it.
</details>

## One palette

[`palette.toml`](palette.toml) has a section per kind of colour, and each app takes what it can use:

| Section | What it is | Who uses it |
| :-- | :-- | :-- |
| `[base]` `[accent]` | backgrounds, text and Dracula's seven accents | everything |
| `[bright]` `[ansi]` | the 16 terminal colours | Ghostty, kitty, the terminals in VS Code and Neovim |
| `[syntax]` | code colours from [Pierre Dark](https://github.com/pierrecomputer/theme) | Neovim, VS Code, bat, yazi |
| `[editor]` | code background, current line, line numbers | Neovim, VS Code, bat |
| `[ui]` | the 61 roles of a T3 Code theme | T3 Code, VS Code's window |
| `[tint]` | tinted rows | iris |

Code sits on `#111111`, a step above the `#0a0a0a` of terminals and windows. Terminal colour 0 is the surface grey, so programs that print black text stay readable, and BSD `ls` only knows 8 colours, so yellow stands in for orange there.

## Hacking

```sh
uv run nocturne preview         # the palette, a code sample and contrast checks
uv run nocturne build           # regenerate themes/ after editing palette.toml
uv run pytest                   # tests
uv run ruff check && uv run pyright
uv run tools/screenshots        # the pictures above, from the real apps
tools/linux-test.sh             # tests, install and undo in Debian, Fedora and Alpine
```

Each app is one package in [`src/nocturne/apps/`](src/nocturne/apps), and no other file lists the apps. The package has an `APP` that says how to find the app and what each level does, plus `templates/` (files with `{{purple}}`, `{{syntax.string}}` or `{{bg|rgb}}` in them) or a `generate()` function. The install steps are a few classes in [`steps/`](src/nocturne/steps) (`Link`, `Copy`, `Line`, `Touch`, `Run`, `Note`), and each one installs, undoes and checks itself. [`tools/templatize.py`](tools/templatize.py) turns a config you themed by hand into a template.

## License

[MIT](LICENSE). The accents are [Dracula](https://draculatheme.com)'s; this is a fan variant, not part of the official theme. The code colours come from [Pierre Dark](https://github.com/pierrecomputer/theme) (MIT, see [`src/nocturne/data`](src/nocturne/data)), the full p10k config from Powerlevel10k's wizard (MIT), and the LazyVim setup from [LazyVim's starter](https://github.com/LazyVim/starter) (Apache-2.0).

<div align="center"><br><sub>made by <a href="https://github.com/ArchitektApx">ArchitektApx</a></sub></div>
