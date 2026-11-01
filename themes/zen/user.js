// Dracula Nocturne for Zen: the colour settings. Generated from palette.toml by `nocturne build`:
// edit that, not this. Zen reads user.js at every start, so these win over the same settings
// changed in Zen's or the mods' settings pages.

// Zen loads userChrome.css only with this on, and new profiles start with it off
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Zen: the purple accent
user_pref("zen.theme.accent-color", "#bd93f9");

// Better Find Bar mod: the background, slightly see-through, and the text
user_pref("better_findbar.enable_custom_background", true);
user_pref("better_findbar.custom_background", "rgba(10,10,10,0.75)");
user_pref("better_findbar.enable_custom_text_color", true);
user_pref("better_findbar.custom_text_color", "#f8f8f2");

// Arc 2.0 mod: the loading bar, if you turn it on (arc.detaloadingbar.enabled)
user_pref("arc.detaloadingbar.maincolor", "#bd93f9");
user_pref("arc.detaloadingbar.middlecolor", "#ff79c6");
user_pref("arc.detaloadingbar.rightcolor", "#bd93f9");
