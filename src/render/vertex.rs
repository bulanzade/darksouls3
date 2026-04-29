#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct SpriteVertex {
    pub pos: [f32; 2],
    pub uv: [f32; 2],
}

pub const QUAD_VERTICES: [SpriteVertex; 4] = [
    SpriteVertex { pos: [-0.5, -0.5], uv: [0.0, 0.0] },
    SpriteVertex { pos: [ 0.5, -0.5], uv: [1.0, 0.0] },
    SpriteVertex { pos: [ 0.5,  0.5], uv: [1.0, 1.0] },
    SpriteVertex { pos: [-0.5,  0.5], uv: [0.0, 1.0] },
];

pub const QUAD_INDICES: [u16; 6] = [0, 1, 2, 0, 2, 3];

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct InstanceData {
    pub transform: [f32; 9],   // 3x3 row-major
    pub uv_rect: [f32; 4],     // min_u, min_v, max_u, max_v
    pub color: [f32; 4],       // r, g, b, a
}

impl InstanceData {
    pub fn new(x: f32, y: f32, w: f32, h: f32, uv_rect: [f32; 4], color: [f32; 4]) -> Self {
        Self {
            transform: [
                w,   0.0, 0.0,
                0.0, h,   0.0,
                x,   y,   1.0,
            ],
            uv_rect,
            color,
        }
    }
}

pub const MAX_INSTANCES: usize = 16384;
