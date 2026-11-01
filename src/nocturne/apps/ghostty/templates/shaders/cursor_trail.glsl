// Dracula Nocturne for Ghostty: a cursor trail, like kitty's cursor_trail.
// A fading streak from the old cursor position to the new one on bigger jumps, in the cursor colour.

const float DURATION = 0.25;    // seconds until the trail is gone
const float MIN_DISTANCE = 2.5; // in cell widths; shorter moves (normal typing) get no trail
const float STRENGTH = 0.6;     // trail opacity at its start

float sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    fragColor = texture(iChannel0, fragCoord / iResolution.xy);

    // Cursor xy is the top-left corner (y grows upwards), zw is width/height
    vec2 size = iCurrentCursor.zw;
    vec2 cur = iCurrentCursor.xy + vec2(0.5, -0.5) * size;
    vec2 prev = iPreviousCursor.xy + vec2(0.5, -0.5) * iPreviousCursor.zw;
    float t = (iTime - iTimeCursorChange) / DURATION;
    if (t >= 1.0 || distance(cur, prev) < MIN_DISTANCE * size.x) return;

    // Leave the cursor cell itself untouched so the character under it stays readable
    vec2 inCursor = abs(fragCoord - cur) - size * 0.5;
    if (max(inCursor.x, inCursor.y) < 0.0) return;

    // The tail starts at the old position and catches up with the cursor
    vec2 tail = mix(prev, cur, 1.0 - pow(1.0 - t, 3.0));
    float d = sdSegment(fragCoord, tail, cur) - min(size.x, size.y) * 0.5;
    float alpha = (1.0 - smoothstep(-1.0, 1.0, d)) * (1.0 - t) * STRENGTH;
    fragColor = mix(fragColor, vec4(iCurrentCursorColor.rgb, 1.0), alpha);
}
