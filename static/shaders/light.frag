#version 300 es
precision highp float;
uniform vec2 u_light_pos;
uniform vec3 u_light_color;
uniform float u_light_radius;
uniform float u_light_intensity;
uniform vec2 u_screen_size;
out vec4 fragColor;
void main() {
    // Convert fragment coords to world-ish space
    vec2 frag_pos = gl_FragCoord.xy;
    vec2 light_screen = (u_light_pos / u_screen_size + 0.5) * u_screen_size;
    float dist = distance(frag_pos, light_screen);
    float attenuation = 1.0 - smoothstep(0.0, u_light_radius, dist);
    float intensity = attenuation * attenuation * u_light_intensity;
    fragColor = vec4(u_light_color * intensity, intensity);
}
