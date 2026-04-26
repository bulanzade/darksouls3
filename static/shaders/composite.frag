#version 300 es
precision highp float;
in vec2 v_uv;
uniform sampler2D u_scene;
uniform float u_vignette_intensity;
uniform vec4 u_fog_color;
uniform vec2 u_fog_distance;
uniform float u_brightness;
uniform float u_saturation;
out vec4 fragColor;
void main() {
    vec4 color = texture(u_scene, v_uv);
    // Vignette
    float vignette = 1.0 - distance(v_uv, vec2(0.5)) * u_vignette_intensity;
    vignette = clamp(vignette, 0.0, 1.0);
    color.rgb *= vignette;
    // Brightness
    color.rgb *= u_brightness;
    // Saturation
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    color.rgb = mix(vec3(gray), color.rgb, u_saturation);
    // Fog (distance-based, using vertical position as proxy)
    float fog_factor = smoothstep(u_fog_distance.x, u_fog_distance.y, v_uv.y);
    color.rgb = mix(color.rgb, u_fog_color.rgb, fog_factor * u_fog_color.a);
    fragColor = color;
}
