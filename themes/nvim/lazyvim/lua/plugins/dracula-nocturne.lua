-- Dracula Nocturne for LazyVim: the colorscheme (linked into this config by `nocturne install nvim`)
-- in place of LazyVim's default. require("dracula-nocturne").setup({ ... }) in an init function
-- here changes its options (see its M.options).
return {
  { "LazyVim/LazyVim", opts = { colorscheme = "dracula-nocturne" } },
  -- LazyVim's bundled colorschemes, unused
  { "folke/tokyonight.nvim", enabled = false },
  { "catppuccin/nvim", name = "catppuccin", enabled = false },
}
