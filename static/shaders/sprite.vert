#version 300 es
precision highp float;

layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec4 a_color;
layout(location = 3) in mat3 a_transform;
layout(location = 6) in vec4 a_uv_rect; // min_u, min_v, max_u, max_v

uniform mat4 u_projection;

out vec2 v_uv;
out vec4 v_color;

void main() {
    vec3 world_pos = a_transform * vec3(a_pos, 1.0);
    gl_Position = u_projection * vec4(world_pos.xy, 0.0, 1.0);
    // Remap quad UVs (0..1) into the tile's sub-region of the atlas
    vec2 uv_min = a_uv_rect.xy;
    vec2 uv_max = a_uv_rect.zw;
    v_uv = mix(uv_min, uv_max, a_uv);
    v_color = a_color;
}
