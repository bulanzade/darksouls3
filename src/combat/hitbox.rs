use crate::entity::entity_trait::EntityId;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum HitGroup {
    Player,
    Enemy,
    Neutral,
}

#[derive(Clone, Copy, Debug)]
pub enum HitShape {
    Rect { half_w: f32, half_h: f32, offset_x: f32, offset_y: f32 },
    Circle { radius: f32, offset_x: f32, offset_y: f32 },
}

#[derive(Clone, Debug)]
pub struct Hitbox {
    pub shape: HitShape,
    pub damage: i32,
    pub knockback_x: f32,
    pub knockback_y: f32,
    pub poise_damage: f32,
    pub owner: EntityId,
    pub hit_group: HitGroup,
    pub active_frame_start: u32,
    pub active_frame_end: u32,
    pub spent: bool,
}

#[derive(Clone, Debug)]
pub struct Hurtbox {
    pub shape: HitShape,
    pub entity_id: EntityId,
    pub hit_group: HitGroup,
    pub iframe_count: u32,
    pub iframe_max: u32,
}

impl Hitbox {
    pub fn world_position(&self, owner_x: f32, owner_y: f32, owner_facing: f32) -> (f32, f32) {
        let (ox, oy) = self.shape.offset();
        let cos = owner_facing.cos();
        let sin = owner_facing.sin();
        (owner_x + ox * cos - oy * sin, owner_y + ox * sin + oy * cos)
    }

    pub fn intersects(&self, hx: f32, hy: f32, hurtbox: &Hurtbox, hurt_x: f32, hurt_y: f32) -> bool {
        if self.hit_group == hurtbox.hit_group { return false; }
        if hurtbox.iframe_count > 0 { return false; }
        if self.spent { return false; }

        let (hx2, hy2) = hurtbox.shape.offset();
        let (sx, sy) = (hurt_x + hx2, hurt_y + hy2);

        match (&self.shape, &hurtbox.shape) {
            (HitShape::Circle { radius: r1, .. }, HitShape::Circle { radius: r2, .. }) => {
                let dx = hx - sx;
                let dy = hy - sy;
                (dx * dx + dy * dy) < (r1 + r2).powi(2)
            }
            (HitShape::Rect { half_w: hw, half_h: hh, .. }, HitShape::Rect { half_w: hw2, half_h: hh2, .. }) => {
                (hx - sx).abs() < hw + hw2 && (hy - sy).abs() < hh + hh2
            }
            (HitShape::Circle { radius: r, .. }, HitShape::Rect { half_w: hw, half_h: hh, .. }) => {
                circle_rect_collision(hx, hy, *r, sx, sy, *hw, *hh)
            }
            (HitShape::Rect { half_w: hw, half_h: hh, .. }, HitShape::Circle { radius: r, .. }) => {
                circle_rect_collision(sx, sy, *r, hx, hy, *hw, *hh)
            }
        }
    }
}

impl HitShape {
    pub fn offset(&self) -> (f32, f32) {
        match self {
            HitShape::Rect { offset_x, offset_y, .. } => (*offset_x, *offset_y),
            HitShape::Circle { offset_x, offset_y, .. } => (*offset_x, *offset_y),
        }
    }
}

fn circle_rect_collision(cx: f32, cy: f32, r: f32, rx: f32, ry: f32, hw: f32, hh: f32) -> bool {
    let closest_x = (rx - hw).max(cx).min(rx + hw);
    let closest_y = (ry - hh).max(cy).min(ry + hh);
    let dx = cx - closest_x;
    let dy = cy - closest_y;
    (dx * dx + dy * dy) < r * r
}
