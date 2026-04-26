#version 300 es
precision highp float;

in vec2 v_uv;
in vec4 v_color;

uniform sampler2D u_texture;

out vec4 fragColor;

void main() {
    vec4 tex_color = texture(u_texture, v_uv);
    fragColor = tex_color * v_color;
}
