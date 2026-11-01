-- Dracula Nocturne for Neovim. Generated from palette.toml by `nocturne build`: edit that, not this.
--
-- Dracula's colours for the editor, Pierre Dark's for the code (the same as VS Code and bat).
-- Code sits on a solid background; menus, floating windows and start screens have none, so a
-- see-through terminal shows through them.
--
--   require("dracula-nocturne").setup({ transparent = false })  -- optional, see M.options
--   vim.cmd.colorscheme("dracula-nocturne")

local M = {}

M.options = {
  -- menus, floating windows and start screens without a background of their own
  transparent = true,
  italic_comment = false,
  -- extra highlight groups, applied last: { GroupName = { fg = "#..." } }
  overrides = {},
}

function M.setup(opts)
  M.options = vim.tbl_deep_extend("force", M.options, opts or {})
end

-- a mixed with b: t = 0 is a, t = 1 is b
local function blend(a, b, t)
  local function rgb(hex)
    return tonumber(hex:sub(2, 3), 16), tonumber(hex:sub(4, 5), 16), tonumber(hex:sub(6, 7), 16)
  end
  local ar, ag, ab = rgb(a)
  local br, bg, bb = rgb(b)
  local function mix(x, y)
    return math.floor(x + (y - x) * t + 0.5)
  end
  return string.format("#%02x%02x%02x", mix(ar, br), mix(ag, bg), mix(ab, bb))
end

-- Pierre Dark's roles -> treesitter captures, LSP semantic tokens and the classic syntax groups
local syntax = {
  comment = { "Comment", "@comment", "@lsp.type.comment" },
  string = { "String", "Character", "@string", "@string.special", "@character", "@lsp.type.string" },
  regexp = { "@string.regexp", "@lsp.type.regexp" },
  escape = { "SpecialChar", "@string.escape", "@character.special" },
  number = { "Number", "Float", "Boolean", "@number", "@number.float", "@boolean", "@constant.builtin", "@lsp.type.number" },
  constant = { "Constant", "@constant", "@constant.macro", "@lsp.typemod.variable.readonly" },
  keyword = {
    "Keyword", "Statement", "Conditional", "Repeat", "Label", "Exception", "StorageClass", "Include", "PreProc",
    "Define", "Macro", "PreCondit", "@keyword", "@keyword.function", "@keyword.return", "@keyword.conditional",
    "@keyword.repeat", "@keyword.import", "@keyword.exception", "@keyword.operator", "@keyword.type",
    "@keyword.modifier", "@keyword.coroutine", "@keyword.directive", "@type.qualifier", "@lsp.type.keyword",
  },
  operator = { "Operator", "Delimiter", "@operator", "@punctuation.delimiter", "@punctuation.bracket", "@punctuation.special", "@tag.delimiter" },
  func = {
    "Function", "@function", "@function.call", "@function.method", "@function.method.call", "@function.builtin",
    "@function.macro", "@lsp.type.function", "@lsp.type.method",
  },
  type = { "Type", "Structure", "Typedef", "@type", "@type.builtin", "@type.definition", "@constructor", "@lsp.type.class", "@lsp.type.type", "@lsp.type.interface", "@lsp.type.enum" },
  variable = { "Identifier", "@variable", "@variable.member", "@property", "@lsp.type.variable", "@lsp.type.property" },
  parameter = { "@variable.parameter", "@lsp.type.parameter" },
  builtin = { "@variable.builtin", "@module", "@module.builtin", "@lsp.type.namespace", "@lsp.typemod.variable.defaultLibrary", "@lsp.typemod.function.defaultLibrary" },
  enum_member = { "@lsp.type.enumMember" },
  decorator = { "@attribute", "@lsp.type.decorator" },
  tag = { "Tag", "@tag", "@markup.heading" },
  attribute = { "@tag.attribute" },
}

local function editor(p, o)
  local float = o.transparent and "NONE" or p.surface
  local diag = { Error = p.red, Warn = p.yellow, Info = p.cyan, Hint = p.purple, Ok = p.green }
  local hl = {
    Normal = { fg = p.fg, bg = p.editor.bg },
    NormalNC = { link = "Normal" },
    NormalFloat = { fg = p.fg, bg = float },
    FloatBorder = { fg = p.comment, bg = float },
    FloatTitle = { fg = p.purple, bg = float, bold = true },
    FloatFooter = { fg = p.comment, bg = float },
    Pmenu = { fg = p.fg, bg = float },
    PmenuSel = { bg = p.selection, bold = true },
    PmenuMatch = { fg = p.pink, bold = true },
    PmenuMatchSel = { fg = p.pink, bg = p.selection, bold = true },
    PmenuKind = { fg = p.purple, bg = float },
    PmenuExtra = { fg = p.comment, bg = float },
    PmenuSbar = { bg = float },
    PmenuThumb = { bg = p.line },
    WildMenu = { fg = p.bg, bg = p.purple },
    StatusLine = { fg = p.fg, bg = p.surface },
    StatusLineNC = { fg = p.comment, bg = p.bg },
    TabLine = { fg = p.comment, bg = p.surface },
    TabLineSel = { fg = p.bg, bg = p.pink, bold = true },
    TabLineFill = { bg = p.bg },
    WinBar = { fg = p.fg },
    WinBarNC = { fg = p.comment },
    WinSeparator = { fg = p.surface },
    Cursor = { fg = p.bg, bg = p.pink },
    lCursor = { link = "Cursor" },
    CursorLine = { bg = p.editor.line_highlight },
    CursorColumn = { bg = p.editor.line_highlight },
    ColorColumn = { bg = p.surface },
    LineNr = { fg = p.editor.line_nr },
    CursorLineNr = { fg = p.editor.line_nr_active, bold = true },
    SignColumn = { bg = "NONE" },
    FoldColumn = { fg = p.comment },
    Folded = { fg = p.comment, bg = p.surface },
    Visual = { bg = p.selection },
    Search = { fg = p.bg, bg = p.orange },
    IncSearch = { fg = p.bg, bg = p.pink },
    CurSearch = { link = "IncSearch" },
    Substitute = { fg = p.bg, bg = p.green },
    MatchParen = { fg = p.pink, bold = true, underline = true },
    NonText = { fg = p.line },
    Whitespace = { fg = p.line },
    SpecialKey = { fg = p.line },
    EndOfBuffer = { fg = p.editor.bg },
    Conceal = { fg = p.comment },
    Directory = { fg = p.purple },
    Title = { fg = p.purple, bold = true },
    ErrorMsg = { fg = p.red },
    WarningMsg = { fg = p.yellow },
    MoreMsg = { fg = p.green },
    ModeMsg = { fg = p.fg, bold = true },
    Question = { fg = p.purple },
    QuickFixLine = { bg = p.selection },
    Special = { fg = p.syntax.escape },
    Underlined = { fg = p.cyan, underline = true },
    Todo = { fg = p.bg, bg = p.purple, bold = true },
    Error = { fg = p.red },
    DiffAdd = { bg = blend(p.editor.bg, p.green, 0.15) },
    DiffChange = { bg = blend(p.editor.bg, p.orange, 0.12) },
    DiffDelete = { fg = p.red, bg = blend(p.editor.bg, p.red, 0.15) },
    DiffText = { bg = blend(p.editor.bg, p.orange, 0.3) },
    Added = { fg = p.green },
    Changed = { fg = p.orange },
    Removed = { fg = p.red },
    SpellBad = { sp = p.red, undercurl = true },
    SpellCap = { sp = p.yellow, undercurl = true },
    SpellRare = { sp = p.cyan, undercurl = true },
    SpellLocal = { sp = p.cyan, undercurl = true },
    LspReferenceText = { bg = p.selection },
    LspReferenceRead = { bg = p.selection },
    LspReferenceWrite = { bg = p.selection },
    LspInlayHint = { fg = p.comment },
    LspCodeLens = { fg = p.comment },
    LspSignatureActiveParameter = { fg = p.pink, bold = true },
    ["@markup.strong"] = { bold = true },
    ["@markup.italic"] = { italic = true },
    ["@markup.strikethrough"] = { strikethrough = true },
    ["@markup.underline"] = { underline = true },
    ["@markup.link"] = { fg = p.cyan },
    ["@markup.link.url"] = { fg = p.cyan, underline = true },
    ["@markup.raw"] = { fg = p.syntax.string },
    ["@markup.list"] = { fg = p.pink },
    ["@markup.quote"] = { fg = p.comment, italic = true },
    ["@diff.plus"] = { fg = p.green },
    ["@diff.minus"] = { fg = p.red },
    ["@diff.delta"] = { fg = p.orange },
    ["@comment.todo"] = { link = "Todo" },
    ["@comment.note"] = { fg = p.bg, bg = p.cyan, bold = true },
    ["@comment.warning"] = { fg = p.bg, bg = p.yellow, bold = true },
    ["@comment.error"] = { fg = p.bg, bg = p.red, bold = true },
  }
  for name, color in pairs(diag) do
    hl["Diagnostic" .. name] = { fg = color }
    hl["DiagnosticVirtualText" .. name] = { fg = color, bg = blend(p.editor.bg, color, 0.1) }
    hl["DiagnosticUnderline" .. name] = { sp = color, undercurl = true }
    hl["DiagnosticSign" .. name] = { fg = color }
  end
  return hl
end

-- The plugins LazyVim comes with: snacks (dashboard, picker, explorer, notifier), which-key,
-- noice, blink.cmp, flash, gitsigns, mini.icons and bufferline
local function plugins(p, o)
  return {
    SnacksDashboardNormal = { link = "Normal" },
    SnacksDashboardHeader = { fg = p.purple },
    SnacksDashboardIcon = { fg = p.pink },
    SnacksDashboardDesc = { fg = p.fg },
    SnacksDashboardKey = { fg = p.pink, bold = true },
    SnacksDashboardFooter = { fg = p.comment, italic = true },
    SnacksDashboardSpecial = { fg = p.purple },
    SnacksPickerTitle = { link = "FloatTitle" },
    SnacksPickerBorder = { link = "FloatBorder" },
    SnacksPickerPrompt = { fg = p.pink },
    SnacksPickerMatch = { fg = p.pink, bold = true },
    SnacksPickerDir = { fg = p.comment },
    SnacksPickerTree = { fg = p.line },
    SnacksIndent = { fg = p.surface },
    SnacksIndentScope = { fg = p.purple },
    SnacksNotifierBorderInfo = { fg = p.purple },
    SnacksNotifierTitleInfo = { fg = p.purple, bold = true },
    SnacksNotifierIconInfo = { fg = p.purple },
    WhichKey = { fg = p.pink },
    WhichKeyGroup = { fg = p.purple },
    WhichKeyDesc = { fg = p.fg },
    WhichKeySeparator = { fg = p.comment },
    WhichKeyNormal = { link = "NormalFloat" },
    WhichKeyBorder = { link = "FloatBorder" },
    NoiceCmdlinePopupBorder = { fg = p.purple },
    NoiceCmdlinePopupTitle = { fg = p.purple, bold = true },
    NoiceCmdlineIcon = { fg = p.purple },
    NoiceCmdlinePopupBorderSearch = { fg = p.orange },
    NoiceCmdlineIconSearch = { fg = p.orange },
    BlinkCmpMenu = { link = "Pmenu" },
    BlinkCmpMenuBorder = { link = "FloatBorder" },
    BlinkCmpMenuSelection = { link = "PmenuSel" },
    BlinkCmpLabelMatch = { fg = p.pink, bold = true },
    BlinkCmpKind = { fg = p.purple },
    BlinkCmpDoc = { link = "NormalFloat" },
    BlinkCmpDocBorder = { link = "FloatBorder" },
    BlinkCmpSignatureHelp = { link = "NormalFloat" },
    BlinkCmpSignatureHelpBorder = { link = "FloatBorder" },
    BlinkCmpGhostText = { fg = p.comment },
    FlashLabel = { fg = p.bg, bg = p.pink, bold = true },
    FlashMatch = { fg = p.fg, bg = p.selection },
    FlashCurrent = { fg = p.bg, bg = p.orange },
    FlashBackdrop = { fg = p.comment },
    GitSignsAdd = { fg = p.green },
    GitSignsChange = { fg = p.orange },
    GitSignsDelete = { fg = p.red },
    MiniIconsAzure = { fg = p.cyan },
    MiniIconsBlue = { fg = p.purple },
    MiniIconsCyan = { fg = p.cyan },
    MiniIconsGreen = { fg = p.green },
    MiniIconsGrey = { fg = p.comment },
    MiniIconsOrange = { fg = p.orange },
    MiniIconsPurple = { fg = p.purple },
    MiniIconsRed = { fg = p.red },
    MiniIconsYellow = { fg = p.yellow },
    BufferLineFill = { bg = p.bg },
    BufferLineIndicatorSelected = { fg = p.pink },
  }
end

local dashboards = { "snacks_dashboard", "alpha", "dashboard", "ministarter" }

-- Neovim clears the empty part of every row with Normal's background, whatever a window maps
-- Normal to. So while a start screen shows, Normal itself goes see-through, and it comes back as
-- soon as a file is opened. So does StatusLine: a statusline hidden on start screens (lualine's)
-- still leaves its row in StatusLine's colour.
local function see_through_start_screens(group, p)
  local function see_through(on)
    vim.api.nvim_set_hl(0, "Normal", { fg = p.fg, bg = on and "NONE" or p.editor.bg })
    vim.api.nvim_set_hl(0, "StatusLine", { fg = p.fg, bg = on and "NONE" or p.surface })
  end
  local function on_start_screen()
    if vim.tbl_contains(dashboards, vim.bo.filetype) then
      see_through(true)
    end
  end
  -- snacks sets its dashboard's filetype without a FileType event, and says so with its own
  vim.api.nvim_create_autocmd({ "FileType", "BufWinEnter" }, { group = group, callback = on_start_screen })
  vim.api.nvim_create_autocmd("User", { group = group, pattern = "SnacksDashboardOpened", callback = on_start_screen })
  vim.api.nvim_create_autocmd("BufEnter", {
    group = group,
    callback = function(ev)
      if vim.bo[ev.buf].buftype == "" and not vim.tbl_contains(dashboards, vim.bo[ev.buf].filetype) then
        see_through(false)
      end
    end,
  })
end

function M.load()
  local p = require("dracula-nocturne.palette")
  local o = M.options
  if vim.g.colors_name then
    vim.cmd("highlight clear")
  end
  vim.o.termguicolors = true
  vim.g.colors_name = "dracula-nocturne"

  local hl = vim.tbl_extend("force", editor(p, o), plugins(p, o))
  for role, names in pairs(syntax) do
    for _, name in ipairs(names) do
      hl[name] = { fg = p.syntax[role] }
    end
  end
  hl.Comment.italic = o.italic_comment
  for name, spec in pairs(vim.tbl_extend("force", hl, o.overrides)) do
    vim.api.nvim_set_hl(0, name, spec)
  end
  for i, color in ipairs(p.ansi) do
    vim.g["terminal_color_" .. (i - 1)] = color
  end

  local group = vim.api.nvim_create_augroup("DraculaNocturne", { clear = true })
  if o.transparent then
    see_through_start_screens(group, p)
  end
end

return M
