// Dracula Nocturne for Zen: the colour settings. Generated from palette.toml by `nocturne build`:
// edit that, not this. Zen reads user.js at every start, so these win over the same settings
// changed in Zen's or the mods' settings pages.

// Zen loads userChrome.css only with this on, and new profiles start with it off
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Zen: the purple accent
user_pref("zen.theme.accent-color", "{{purple}}");

// Better Find Bar mod: the background, slightly see-through, and the text
user_pref("better_findbar.enable_custom_background", true);
user_pref("better_findbar.custom_background", "rgba({{bg|rgb_comma}},0.75)");
user_pref("better_findbar.enable_custom_text_color", true);
user_pref("better_findbar.custom_text_color", "{{fg}}");

// Arc 2.0 mod: the loading bar, if you turn it on (arc.detaloadingbar.enabled)
user_pref("arc.detaloadingbar.maincolor", "{{purple}}");
user_pref("arc.detaloadingbar.middlecolor", "{{pink}}");
user_pref("arc.detaloadingbar.rightcolor", "{{purple}}");
