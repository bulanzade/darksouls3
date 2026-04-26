use std::collections::HashMap;

use crate::dragonbones::bone::Bone;
use crate::dragonbones::parser::{AnimationDef, BoneDef, DragonBonesFile};

/// Slot metadata — which bone it is attached to, draw order, display, and color.
#[derive(Clone, Debug)]
pub struct SlotInfo {
    pub name: String,
    pub bone_index: usize,
    pub z_order: i32,
    pub display_index: i32,
    pub color_alpha: f32,
}

/// A fully resolved animation clip with durations converted to seconds.
#[derive(Clone, Debug)]
pub struct AnimationClip {
    pub name: String,
    pub duration: f32,
    pub play_times: i32,
    pub bone_timelines: HashMap<String, BoneTimeline>,
    pub slot_timelines: HashMap<String, SlotTimeline>,
}

#[derive(Clone, Debug)]
pub struct BoneTimeline {
    pub frames: Vec<BoneKeyframe>,
}

#[derive(Clone, Debug)]
pub struct BoneKeyframe {
    pub duration: f32,
    pub x: f32,
    pub y: f32,
    pub rotation: f32,
    pub scale_x: f32,
    pub scale_y: f32,
    pub easing: Option<f32>,
}

#[derive(Clone, Debug)]
pub struct SlotTimeline {
    pub frames: Vec<SlotKeyframe>,
}

#[derive(Clone, Debug)]
pub struct SlotKeyframe {
    pub duration: f32,
    pub display_index: Option<i32>,
    pub alpha: f32,
    pub easing: Option<f32>,
}

/// The runtime armature: a bone tree plus slots and animation clips.
pub struct Armature {
    pub bones: Vec<Bone>,
    pub slots: Vec<SlotInfo>,
    pub animations: HashMap<String, AnimationClip>,
    pub frame_rate: u32,
}

impl Armature {
    /// Build an Armature from a parsed DragonBonesFile, looking up by armature name.
    pub fn from_def(file: &DragonBonesFile, armature_name: &str) -> Option<Self> {
        let arm_def = file.armature.iter().find(|a| a.name == armature_name)?;
        let frame_rate = file.frameRate.max(1);

        // Topological sort — parent before children
        let order = sort_bones(&arm_def.bone);

        // Build bones in sorted order, recording new indices
        let mut old_to_new: Vec<Option<usize>> = vec![None; arm_def.bone.len()];
        let mut bones: Vec<Bone> = Vec::with_capacity(arm_def.bone.len());

        for old_idx in &order {
            let def = &arm_def.bone[*old_idx];
            let parent_index = def
                .parent
                .as_ref()
                .and_then(|pname| {
                    arm_def
                        .bone
                        .iter()
                        .position(|b| b.name == *pname)
                        .and_then(|pi| old_to_new[pi])
                });

            let mut bone = Bone::new(def.name.clone(), parent_index);

            // Set rest pose from definition transform
            bone.rest_x = def.transform.x;
            bone.rest_y = def.transform.y;
            // skX is in degrees, convert to radians
            bone.rest_rotation = def.transform.skX.to_radians();
            // Treat 0 scale as 1.0
            bone.rest_scale_x = if def.transform.scX == 0.0 {
                1.0
            } else {
                def.transform.scX
            };
            bone.rest_scale_y = if def.transform.scY == 0.0 {
                1.0
            } else {
                def.transform.scY
            };

            let new_idx = bones.len();
            old_to_new[*old_idx] = Some(new_idx);
            bones.push(bone);
        }

        // Set up children indices
        for old_idx in &order {
            let def = &arm_def.bone[*old_idx];
            if let Some(ref pname) = def.parent {
                if let (Some(parent_old), Some(child_new)) =
                    (arm_def.bone.iter().position(|b| b.name == *pname), old_to_new[*old_idx])
                {
                    if let Some(parent_new) = old_to_new[parent_old] {
                        bones[parent_new].children.push(child_new);
                    }
                }
            }
        }

        // Build slots
        let mut slots: Vec<SlotInfo> = Vec::with_capacity(arm_def.slot.len());
        for slot_def in &arm_def.slot {
            let bone_index = bones
                .iter()
                .position(|b| b.name == slot_def.parent)
                .unwrap_or(0);
            let alpha = slot_def
                .color
                .as_ref()
                .map(|c| c.aM / 100.0)
                .unwrap_or(1.0);
            slots.push(SlotInfo {
                name: slot_def.name.clone(),
                bone_index,
                z_order: slot_def.z,
                display_index: slot_def.displayIndex,
                color_alpha: alpha,
            });
        }

        // Build animations
        let mut animations: HashMap<String, AnimationClip> = HashMap::new();
        for anim_def in &arm_def.animation {
            let clip = animation_from_def(anim_def, frame_rate);
            animations.insert(clip.name.clone(), clip);
        }

        // Initial world transform computation
        let mut armature = Self {
            bones,
            slots,
            animations,
            frame_rate,
        };
        armature.update_world_transforms();

        Some(armature)
    }

    /// Recompute world transforms for all bones (parent-first order is guaranteed).
    pub fn update_world_transforms(&mut self) {
        for i in 0..self.bones.len() {
            let bone = &self.bones[i];

            // Local transform = rest pose + animation delta
            let local_x = bone.rest_x + bone.local_x;
            let local_y = bone.rest_y + bone.local_y;
            let local_rotation = bone.rest_rotation + bone.local_rotation;
            let local_scale_x = bone.rest_scale_x + bone.local_scale_x;
            let local_scale_y = bone.rest_scale_y + bone.local_scale_y;

            let (world_x, world_y, world_rotation, world_scale_x, world_scale_y) =
                if let Some(pi) = bone.parent_index {
                    let parent = &self.bones[pi];
                    // Rotate local offset by parent world rotation
                    let cos = parent.world_rotation.cos();
                    let sin = parent.world_rotation.sin();
                    let rx = local_x * cos - local_y * sin;
                    let ry = local_x * sin + local_y * cos;

                    (
                        parent.world_x + rx * parent.world_scale_x,
                        parent.world_y + ry * parent.world_scale_y,
                        parent.world_rotation + local_rotation,
                        parent.world_scale_x * local_scale_x,
                        parent.world_scale_y * local_scale_y,
                    )
                } else {
                    (local_x, local_y, local_rotation, local_scale_x, local_scale_y)
                };

            // We need to borrow mutably after reading parent, so use direct indexing
            self.bones[i].world_x = world_x;
            self.bones[i].world_y = world_y;
            self.bones[i].world_rotation = world_rotation;
            self.bones[i].world_scale_x = world_scale_x;
            self.bones[i].world_scale_y = world_scale_y;
        }
    }
}

/// Topological sort of bone definitions ensuring parents come before children.
/// Returns a Vec of original indices in sorted order.
fn sort_bones(bones: &[BoneDef]) -> Vec<usize> {
    let n = bones.len();
    if n == 0 {
        return Vec::new();
    }

    // Build parent map: old_idx -> parent old_idx
    let mut parent: Vec<Option<usize>> = vec![None; n];
    let name_to_idx: HashMap<&str, usize> = bones
        .iter()
        .enumerate()
        .map(|(i, b)| (b.name.as_str(), i))
        .collect();

    for (i, b) in bones.iter().enumerate() {
        if let Some(ref pname) = b.parent {
            parent[i] = name_to_idx.get(pname.as_str()).copied();
        }
    }

    // DFS-based topological sort
    let mut visited = vec![false; n];
    let mut order = Vec::with_capacity(n);

    fn dfs(
        node: usize,
        bones: &[BoneDef],
        parent: &[Option<usize>],
        visited: &mut [bool],
        order: &mut Vec<usize>,
    ) {
        if visited[node] {
            return;
        }
        visited[node] = true;
        // Visit parent first (if any)
        if let Some(pi) = parent[node] {
            dfs(pi, bones, parent, visited, order);
        }
        // Then visit all bones that have this node as parent
        for (i, b) in bones.iter().enumerate() {
            if b.parent.as_deref() == Some(bones[node].name.as_str()) && !visited[i] {
                dfs(i, bones, parent, visited, order);
            }
        }
        order.push(node);
    }

    // Start DFS from root bones (no parent)
    for i in 0..n {
        if parent[i].is_none() {
            dfs(i, bones, &parent, &mut visited, &mut order);
        }
    }

    // Catch any unvisited (shouldn't happen in valid data, but be safe)
    for i in 0..n {
        if !visited[i] {
            dfs(i, bones, &parent, &mut visited, &mut order);
        }
    }

    order
}

/// Convert a parsed AnimationDef into a runtime AnimationClip.
fn animation_from_def(def: &AnimationDef, frame_rate: u32) -> AnimationClip {
    let rate = frame_rate as f32;

    let mut bone_timelines: HashMap<String, BoneTimeline> = HashMap::new();
    for bt in &def.bone {
        let mut frames: Vec<BoneKeyframe> = Vec::with_capacity(bt.frame.len());
        for f in &bt.frame {
            let t = f.transform.as_ref();
            let tx = t.map(|t| t.x).unwrap_or(0.0);
            let ty = t.map(|t| t.y).unwrap_or(0.0);
            let rot = t.map(|t| t.skX.to_radians()).unwrap_or(0.0);
            let sx_raw = t.map(|t| t.scX).unwrap_or(0.0);
            let sy_raw = t.map(|t| t.scY).unwrap_or(0.0);
            let sx = if sx_raw == 0.0 { 1.0 } else { sx_raw };
            let sy = if sy_raw == 0.0 { 1.0 } else { sy_raw };

            frames.push(BoneKeyframe {
                duration: f.duration as f32 / rate,
                x: tx,
                y: ty,
                rotation: rot,
                scale_x: sx,
                scale_y: sy,
                easing: f.tweenEasing,
            });
        }
        bone_timelines.insert(
            bt.name.clone(),
            BoneTimeline { frames },
        );
    }

    let mut slot_timelines: HashMap<String, SlotTimeline> = HashMap::new();
    for st in &def.slot {
        let mut frames: Vec<SlotKeyframe> = Vec::with_capacity(st.frame.len());
        for f in &st.frame {
            let alpha = f.color.as_ref().map(|c| c.aM / 100.0).unwrap_or(1.0);
            frames.push(SlotKeyframe {
                duration: f.duration as f32 / rate,
                display_index: f.displayIndex,
                alpha,
                easing: f.tweenEasing,
            });
        }
        slot_timelines.insert(
            st.name.clone(),
            SlotTimeline { frames },
        );
    }

    AnimationClip {
        name: def.name.clone(),
        duration: def.duration / rate,
        play_times: def.playTimes,
        bone_timelines,
        slot_timelines,
    }
}
