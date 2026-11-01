-- Dracula Nocturne for lualine (LazyVim's statusline picks it up by the colorscheme's name).
-- Generated from palette.toml by `nocturne build`: edit that, not this.
local p = require("dracula-nocturne.palette")
local middle = require("dracula-nocturne").options.transparent and "NONE" or p.bg

local function mode(color)
  return {
    a = { fg = p.bg, bg = color, gui = "bold" },
    b = { fg = color, bg = p.surface },
    c = { fg = p.comment, bg = middle },
  }
end

return {
  normal = mode(p.purple),
  insert = mode(p.green),
  visual = mode(p.pink),
  replace = mode(p.red),
  command = mode(p.orange),
  terminal = mode(p.cyan),
  inactive = { a = { fg = p.comment, bg = middle }, b = { fg = p.comment, bg = middle }, c = { fg = p.comment, bg = middle } },
}
