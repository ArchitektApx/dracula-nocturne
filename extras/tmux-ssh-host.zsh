# Shows the server in the tmux tab while ssh runs (the orange tabs of the Dracula Nocturne tmux
# theme). Works in zsh and bash: source it from your .zshrc or .bashrc.

if [[ -n "$TMUX" ]]; then
  ssh() {
    local host
    host=$(command ssh -G "$@" 2>/dev/null | awk '$1 == "host" { print $2; exit }')
    [[ -n "$host" ]] && tmux set -w -t "$TMUX_PANE" @ssh_host "$host"
    command ssh "$@"
    local ret=$?
    tmux set -wu -t "$TMUX_PANE" @ssh_host
    return $ret
  }
fi
