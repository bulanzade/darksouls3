/// A single bone in the armature's bone tree.
#[derive(Clone, Debug)]
pub struct Bone {
    pub name: String,
    pub parent_index: Option<usize>,
    pub children: Vec<usize>,

    // Rest pose (from DragonBones definition)
    pub rest_x: f32,
    pub rest_y: f32,
    pub rest_rotation: f32,
    pub rest_scale_x: f32,
    pub rest_scale_y: f32,

    // Current world transform (computed each frame by armature)
    pub world_x: f32,
    pub world_y: f32,
    pub world_rotation: f32,
    pub world_scale_x: f32,
    pub world_scale_y: f32,

    // Local delta from animation (added to rest pose)
    pub local_x: f32,
    pub local_y: f32,
    pub local_rotation: f32,
    pub local_scale_x: f32,
    pub local_scale_y: f32,
}

impl Bone {
    pub fn new(name: String, parent_index: Option<usize>) -> Self {
        Self {
            name,
            parent_index,
            children: Vec::new(),

            rest_x: 0.0,
            rest_y: 0.0,
            rest_rotation: 0.0,
            rest_scale_x: 1.0,
            rest_scale_y: 1.0,

            world_x: 0.0,
            world_y: 0.0,
            world_rotation: 0.0,
            world_scale_x: 1.0,
            world_scale_y: 1.0,

            local_x: 0.0,
            local_y: 0.0,
            local_rotation: 0.0,
            local_scale_x: 0.0,
            local_scale_y: 0.0,
        }
    }

    /// Reset animation deltas to identity (zero offset from rest pose).
    pub fn reset_local(&mut self) {
        self.local_x = 0.0;
        self.local_y = 0.0;
        self.local_rotation = 0.0;
        self.local_scale_x = 0.0;
        self.local_scale_y = 0.0;
    }
}
