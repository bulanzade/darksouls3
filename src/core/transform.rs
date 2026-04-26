use crate::render::vertex::InstanceData;

pub struct Transform {
    pub x: f32,
    pub y: f32,
    pub rotation: f32,
    pub scale_x: f32,
    pub scale_y: f32,
}

impl Transform {
    pub fn new(x: f32, y: f32) -> Self {
        Self {
            x,
            y,
            rotation: 0.0,
            scale_x: 1.0,
            scale_y: 1.0,
        }
    }

    /// Build an InstanceData from this transform, sprite dimensions, UV rect and color.
    ///
    /// The 3x3 row-major transform matrix is:
    ///   [ cos*sx  -sin*sx  0 ]
    ///   [ sin*sy   cos*sy  0 ]
    ///   [   tx       ty    1 ]
    pub fn to_instance_data(
        &self,
        w: f32,
        h: f32,
        uv_rect: [f32; 4],
        color: [f32; 4],
    ) -> InstanceData {
        let cos = self.rotation.cos();
        let sin = self.rotation.sin();
        let sx = self.scale_x * w;
        let sy = self.scale_y * h;

        InstanceData {
            transform: [
                cos * sx,  -sin * sx, 0.0,
                sin * sy,   cos * sy, 0.0,
                self.x,     self.y,   1.0,
            ],
            uv_rect,
            color,
        }
    }
}
