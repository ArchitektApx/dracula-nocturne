# Dracula Nocturne for fzf (PowerShell). Generated from palette.toml by `nocturne build`: edit that, not this.
# Goes in front of your own FZF_DEFAULT_OPTS, so anything you set yourself wins.
$opts = "--color=fg:#f8f8f2,hl:#bd93f9,fg+:#f8f8f2,bg+:#35374a,hl+:#ff79c6,info:#6272a4,prompt:#50fa7b,pointer:#ff79c6,marker:#ff79c6,spinner:#ffb86c,header:#6272a4,border:#6272a4,label:#bd93f9,query:#f8f8f2,bg:-1,gutter:-1 --border=rounded --prompt='$([char]0x276F) ' --pointer='$([char]0x258C)' --marker='$([char]0x2503)'"
if (-not "$env:FZF_DEFAULT_OPTS".Contains($opts)) {
    $env:FZF_DEFAULT_OPTS = "$opts $env:FZF_DEFAULT_OPTS".Trim()
}
Remove-Variable opts
