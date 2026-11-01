# Dracula Nocturne for fzf (bash, zsh). Generated from palette.toml by `nocturne build`: edit that, not this.
# Goes in front of your own FZF_DEFAULT_OPTS, so anything you set yourself wins.
_nocturne_fzf="--color=fg:#f8f8f2,hl:#bd93f9,fg+:#f8f8f2,bg+:#35374a,hl+:#ff79c6,info:#6272a4,prompt:#50fa7b,pointer:#ff79c6,marker:#ff79c6,spinner:#ffb86c,header:#6272a4,border:#6272a4,label:#bd93f9,query:#f8f8f2,bg:-1,gutter:-1 --border=rounded --prompt='❯ ' --pointer='▌' --marker='┃'"
case "$FZF_DEFAULT_OPTS" in
  *"$_nocturne_fzf"*) ;;  # already there (a nested shell, or sourced twice)
  *) export FZF_DEFAULT_OPTS="$_nocturne_fzf${FZF_DEFAULT_OPTS:+ $FZF_DEFAULT_OPTS}" ;;
esac
unset _nocturne_fzf
