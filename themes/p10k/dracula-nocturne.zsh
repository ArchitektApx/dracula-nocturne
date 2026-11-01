# Dracula Nocturne for Powerlevel10k. Generated from palette.toml by `nocturne build`: edit that, not this.
#
# The colours and the rounded tiles, on top of any p10k config: source this after your own
# ~/.p10k.zsh (`nocturne install p10k` adds the line). Your layout (which segments, one or two lines, icons, transient prompt) stays yours.
# Made for the Lean style; the tiles turn its segments into pills like the tmux tabs.

'builtin' 'local' '-a' 'p10k_config_opts'
[[ ! -o 'aliases'         ]] || p10k_config_opts+=('aliases')
[[ ! -o 'sh_glob'         ]] || p10k_config_opts+=('sh_glob')
[[ ! -o 'no_brace_expand' ]] || p10k_config_opts+=('no_brace_expand')
'builtin' 'setopt' 'no_aliases' 'no_sh_glob' 'brace_expand'

() {
  emulate -L zsh -o extended_glob

  # Prompt frame and character
  typeset -g POWERLEVEL9K_RULER_FOREGROUND='#6272a4'
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_FOREGROUND='#6272a4'
  typeset -g POWERLEVEL9K_OS_ICON_FOREGROUND='#ff79c6'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND='#bd93f9'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND='#ff5555'

  # Directory
  typeset -g POWERLEVEL9K_DIR_FOREGROUND='#bd93f9'
  typeset -g POWERLEVEL9K_DIR_SHORTENED_FOREGROUND='#e2e4f0'
  typeset -g POWERLEVEL9K_DIR_ANCHOR_FOREGROUND='#d6acff'

  # Git
  typeset -g POWERLEVEL9K_VCS_VISUAL_IDENTIFIER_COLOR='#50fa7b'
  typeset -g POWERLEVEL9K_VCS_LOADING_VISUAL_IDENTIFIER_COLOR='#6272a4'
  typeset -g POWERLEVEL9K_VCS_CLEAN_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_VCS_UNTRACKED_FOREGROUND='#8be9fd'
  typeset -g POWERLEVEL9K_VCS_MODIFIED_FOREGROUND='#ffb86c'

  # Exit status
  typeset -g POWERLEVEL9K_STATUS_OK_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_STATUS_OK_PIPE_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_STATUS_ERROR_FOREGROUND='#ff5555'
  typeset -g POWERLEVEL9K_STATUS_ERROR_SIGNAL_FOREGROUND='#ff5555'
  typeset -g POWERLEVEL9K_STATUS_ERROR_PIPE_FOREGROUND='#ff5555'

  # Other segments
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND='#f1fa8c'
  typeset -g POWERLEVEL9K_BACKGROUND_JOBS_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_DIRENV_FOREGROUND='#ffb86c'
  typeset -g POWERLEVEL9K_CONTEXT_ROOT_FOREGROUND='#ff5555'
  typeset -g POWERLEVEL9K_CONTEXT_FOREGROUND='#8be9fd'
  typeset -g POWERLEVEL9K_VIRTUALENV_FOREGROUND='#8be9fd'
  typeset -g POWERLEVEL9K_NODENV_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_NVM_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_NODEENV_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_NODE_VERSION_FOREGROUND='#50fa7b'
  typeset -g POWERLEVEL9K_BATTERY_LOW_FOREGROUND='#ff5555'
  typeset -g POWERLEVEL9K_TIME_FOREGROUND='#e2e4f0'

  # Git status text: p10k's own formatter with the palette's colours (it replaces the one in your config)
  function my_git_formatter() {
    emulate -L zsh

    if [[ -n $P9K_CONTENT ]]; then
      # If P9K_CONTENT is not empty, use it. It's either "loading" or from vcs_info (not from
      # gitstatus plugin). VCS_STATUS_* parameters are not available in this case.
      typeset -g my_git_format=$P9K_CONTENT
      return
    fi

    if (( $1 )); then
      # Styling for up-to-date Git status.
      local       meta='%f'     # default foreground
      local      clean='%F{#50fa7b}'   # green foreground
      local   modified='%F{#ffb86c}'  # orange foreground
      local  untracked='%F{#8be9fd}'   # cyan foreground
      local conflicted='%F{#ff5555}'  # red foreground
    else
      # Styling for incomplete and stale Git status.
      local       meta='%F{#6272a4}'  # grey foreground
      local      clean='%F{#6272a4}'  # grey foreground
      local   modified='%F{#6272a4}'  # grey foreground
      local  untracked='%F{#6272a4}'  # grey foreground
      local conflicted='%F{#6272a4}'  # grey foreground
    fi

    local res

    if [[ -n $VCS_STATUS_LOCAL_BRANCH ]]; then
      local branch=${(V)VCS_STATUS_LOCAL_BRANCH}
      # If local branch name is at most 32 characters long, show it in full.
      # Otherwise show the first 12 … the last 12.
      # Tip: To always show local branch name in full without truncation, delete the next line.
      (( $#branch > 32 )) && branch[13,-13]="…"  # <-- this line
      res+="${clean}${(g::)POWERLEVEL9K_VCS_BRANCH_ICON}${branch//\%/%%}"
    fi

    if [[ -n $VCS_STATUS_TAG
          # Show tag only if not on a branch.
          # Tip: To always show tag, delete the next line.
          && -z $VCS_STATUS_LOCAL_BRANCH  # <-- this line
        ]]; then
      local tag=${(V)VCS_STATUS_TAG}
      # If tag name is at most 32 characters long, show it in full.
      # Otherwise show the first 12 … the last 12.
      # Tip: To always show tag name in full without truncation, delete the next line.
      (( $#tag > 32 )) && tag[13,-13]="…"  # <-- this line
      res+="${meta}#${clean}${tag//\%/%%}"
    fi

    # Display the current Git commit if there is no branch and no tag.
    # Tip: To always display the current Git commit, delete the next line.
    [[ -z $VCS_STATUS_LOCAL_BRANCH && -z $VCS_STATUS_TAG ]] &&  # <-- this line
      res+="${meta}@${clean}${VCS_STATUS_COMMIT[1,8]}"

    # Show tracking branch name if it differs from local branch.
    if [[ -n ${VCS_STATUS_REMOTE_BRANCH:#$VCS_STATUS_LOCAL_BRANCH} ]]; then
      res+="${meta}:${clean}${(V)VCS_STATUS_REMOTE_BRANCH//\%/%%}"
    fi

    # Display "wip" if the latest commit's summary contains "wip" or "WIP".
    if [[ $VCS_STATUS_COMMIT_SUMMARY == (|*[^[:alnum:]])(wip|WIP)(|[^[:alnum:]]*) ]]; then
      res+=" ${modified}wip"
    fi

    if (( VCS_STATUS_COMMITS_AHEAD || VCS_STATUS_COMMITS_BEHIND )); then
      # ⇣42 if behind the remote.
      (( VCS_STATUS_COMMITS_BEHIND )) && res+=" ${clean}⇣${VCS_STATUS_COMMITS_BEHIND}"
      # ⇡42 if ahead of the remote; no leading space if also behind the remote: ⇣42⇡42.
      (( VCS_STATUS_COMMITS_AHEAD && !VCS_STATUS_COMMITS_BEHIND )) && res+=" "
      (( VCS_STATUS_COMMITS_AHEAD  )) && res+="${clean}⇡${VCS_STATUS_COMMITS_AHEAD}"
    elif [[ -n $VCS_STATUS_REMOTE_BRANCH ]]; then
      # Tip: Uncomment the next line to display '=' if up to date with the remote.
      # res+=" ${clean}="
    fi

    # ⇠42 if behind the push remote.
    (( VCS_STATUS_PUSH_COMMITS_BEHIND )) && res+=" ${clean}⇠${VCS_STATUS_PUSH_COMMITS_BEHIND}"
    (( VCS_STATUS_PUSH_COMMITS_AHEAD && !VCS_STATUS_PUSH_COMMITS_BEHIND )) && res+=" "
    # ⇢42 if ahead of the push remote; no leading space if also behind: ⇠42⇢42.
    (( VCS_STATUS_PUSH_COMMITS_AHEAD  )) && res+="${clean}⇢${VCS_STATUS_PUSH_COMMITS_AHEAD}"
    # *42 if have stashes.
    (( VCS_STATUS_STASHES        )) && res+=" ${clean}*${VCS_STATUS_STASHES}"
    # 'merge' if the repo is in an unusual state.
    [[ -n $VCS_STATUS_ACTION     ]] && res+=" ${conflicted}${VCS_STATUS_ACTION}"
    # ~42 if have merge conflicts.
    (( VCS_STATUS_NUM_CONFLICTED )) && res+=" ${conflicted}~${VCS_STATUS_NUM_CONFLICTED}"
    # +42 if have staged changes.
    (( VCS_STATUS_NUM_STAGED     )) && res+=" ${modified}+${VCS_STATUS_NUM_STAGED}"
    # !42 if have unstaged changes.
    (( VCS_STATUS_NUM_UNSTAGED   )) && res+=" ${modified}!${VCS_STATUS_NUM_UNSTAGED}"
    # ?42 if have untracked files. It's really a question mark, your font isn't broken.
    # See POWERLEVEL9K_VCS_UNTRACKED_ICON above if you want to use a different icon.
    # Remove the next line if you don't want to see untracked files at all.
    (( VCS_STATUS_NUM_UNTRACKED  )) && res+=" ${untracked}${(g::)POWERLEVEL9K_VCS_UNTRACKED_ICON}${VCS_STATUS_NUM_UNTRACKED}"
    # "─" if the number of unstaged files is unknown. This can happen due to
    # POWERLEVEL9K_VCS_MAX_INDEX_SIZE_DIRTY (see below) being set to a non-negative number lower
    # than the number of files in the Git index, or due to bash.showDirtyState being set to false
    # in the repository config. The number of staged and untracked files may also be unknown
    # in this case.
    (( VCS_STATUS_HAS_UNSTAGED == -1 )) && res+=" ${modified}─"

    typeset -g my_git_format=$res
  }
  functions -M my_git_formatter 2>/dev/null

  # --- Dracula Nocturne tiles: rounded caps, like the tmux tabs ---
  # Each tile gets a background, a left cap in PREFIX and a right cap in SUFFIX.
  # %k before a cap clears the background so the cap's curve shows; the gap between
  # tiles is a plain space outside of them (after the tile on the left, before it on the right).
  typeset -g POWERLEVEL9K_{LEFT,RIGHT}_{,SUB}SEGMENT_SEPARATOR=
  typeset -g POWERLEVEL9K_{LEFT,RIGHT}_PROMPT_FIRST_SEGMENT_START_SYMBOL=
  typeset -g POWERLEVEL9K_{LEFT,RIGHT}_PROMPT_LAST_SEGMENT_END_SYMBOL=
  local _seg _bg
  for _seg _bg in OS_ICON '#ff79c6' DIR '#bd93f9' VCS '#21222c'; do
    typeset -g POWERLEVEL9K_${_seg}_BACKGROUND=$_bg
    typeset -g POWERLEVEL9K_${_seg}_PREFIX="%k%F{$_bg}"$''"%K{$_bg} "
    typeset -g POWERLEVEL9K_${_seg}_SUFFIX=" %k%F{$_bg}"$''"%f "
  done
  for _seg in STATUS COMMAND_EXECUTION_TIME BACKGROUND_JOBS CONTEXT BATTERY TIME; do
    typeset -g POWERLEVEL9K_${_seg}_BACKGROUND='#21222c'
    typeset -g POWERLEVEL9K_${_seg}_PREFIX="%k %F{#21222c}"$''"%K{#21222c} "
    typeset -g POWERLEVEL9K_${_seg}_SUFFIX=" %k%F{#21222c}"$''"%f"
  done
  # Dark text on the colored tiles
  typeset -g POWERLEVEL9K_OS_ICON_FOREGROUND='#0a0a0a'
  typeset -g POWERLEVEL9K_DIR_FOREGROUND='#21222c'
  typeset -g POWERLEVEL9K_DIR_SHORTENED_FOREGROUND='#44475a'
  typeset -g POWERLEVEL9K_DIR_ANCHOR_FOREGROUND='#0a0a0a'

  # Folder icons: known folders get their own icon in the path tile (first match wins). On Linux
  # their names can be translated; user-dirs.dirs says what they're called here.
  local -A _xdg=(DOWNLOAD Downloads DOCUMENTS Documents DESKTOP Desktop PICTURES Pictures MUSIC Music)
  local _dirs=${XDG_CONFIG_HOME:-$HOME/.config}/user-dirs.dirs _line
  if [[ -r $_dirs ]]; then
    for _line in "${(@f)$(<$_dirs)}"; do
      [[ $_line == (#b)XDG_([A-Z]##)_DIR=\"\$HOME/([^\"]##)\" && -n ${_xdg[$match[1]]-} ]] && _xdg[$match[1]]=$match[2]
    done
  fi
  typeset -g POWERLEVEL9K_DIR_CLASSES=(
    '~/(Developer|Development|Projects|projects|code|src|dev)(|/*)'  DEV  ''
    "~/${(b)_xdg[DOWNLOAD]}(|/*)"   DOWNLOADS  ''
    "~/${(b)_xdg[DOCUMENTS]}(|/*)"  DOCUMENTS  ''
    "~/${(b)_xdg[DESKTOP]}(|/*)"    DESKTOP    ''
    "~/${(b)_xdg[PICTURES]}(|/*)"   PICTURES   ''
    "~/${(b)_xdg[MUSIC]}(|/*)"      MUSIC      ''
    '~/.config(|/*)'                CONFIG     ''
    '~'                             HOME       ''
    '*'                             DEFAULT    ''
  )
  local _cls _icon
  for _cls _icon in DEV $'' DOWNLOADS $'' DOCUMENTS $'' DESKTOP $'' \
                    PICTURES $'' MUSIC $'' CONFIG $'' HOME $'' DEFAULT $''; do
    for _seg in DIR_$_cls DIR_${_cls}_NOT_WRITABLE DIR_${_cls}_NON_EXISTENT; do
      typeset -g POWERLEVEL9K_${_seg}_VISUAL_IDENTIFIER_EXPANSION=$_icon
      typeset -g POWERLEVEL9K_${_seg}_BACKGROUND='#bd93f9'
      typeset -g POWERLEVEL9K_${_seg}_FOREGROUND='#21222c'
      typeset -g POWERLEVEL9K_${_seg}_SHORTENED_FOREGROUND='#44475a'
      typeset -g POWERLEVEL9K_${_seg}_ANCHOR_FOREGROUND='#0a0a0a'
      typeset -g POWERLEVEL9K_${_seg}_PREFIX=$POWERLEVEL9K_DIR_PREFIX
      typeset -g POWERLEVEL9K_${_seg}_SUFFIX=$POWERLEVEL9K_DIR_SUFFIX
    done
  done

  # The battery tile, when it shows (p10k's LOW state)
  typeset -g POWERLEVEL9K_BATTERY_LOW_BACKGROUND='#21222c'
  typeset -g POWERLEVEL9K_BATTERY_LOW_PREFIX=$POWERLEVEL9K_BATTERY_PREFIX
  typeset -g POWERLEVEL9K_BATTERY_LOW_SUFFIX=$POWERLEVEL9K_BATTERY_SUFFIX

  (( ! $+functions[p10k] )) || p10k reload
}

(( ${#p10k_config_opts} )) && setopt ${p10k_config_opts[@]}
'builtin' 'unset' 'p10k_config_opts'
