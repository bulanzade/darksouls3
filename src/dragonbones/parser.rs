use serde::Deserialize;

/// Top-level DragonBones file structure (JSON 5.x format).
#[derive(Debug, Deserialize)]
pub struct DragonBonesFile {
    #[serde(default)]
    pub version: String,
    #[serde(default)]
    pub name: String,
    #[serde(default = "default_frame_rate")]
    pub frameRate: u32,
    #[serde(default)]
    pub armature: Vec<ArmatureDef>,
}

fn default_frame_rate() -> u32 {
    24
}

#[derive(Debug, Deserialize)]
pub struct ArmatureDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub bone: Vec<BoneDef>,
    #[serde(default)]
    pub slot: Vec<SlotDef>,
    #[serde(default)]
    pub skin: Vec<SkinDef>,
    #[serde(default)]
    pub animation: Vec<AnimationDef>,
    #[serde(default)]
    pub ik: Vec<IkDef>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct BoneDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub parent: Option<String>,
    #[serde(default)]
    pub transform: TransformDef,
}

#[derive(Debug, Deserialize, Clone)]
pub struct TransformDef {
    #[serde(default)]
    pub x: f32,
    #[serde(default)]
    pub y: f32,
    #[serde(default)]
    pub skX: f32,
    #[serde(default)]
    pub skY: f32,
    #[serde(default)]
    pub scX: f32,
    #[serde(default)]
    pub scY: f32,
}

impl Default for TransformDef {
    fn default() -> Self {
        Self {
            x: 0.0,
            y: 0.0,
            skX: 0.0,
            skY: 0.0,
            scX: 1.0,
            scY: 1.0,
        }
    }
}

#[derive(Debug, Deserialize, Clone)]
pub struct SlotDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub parent: String,
    #[serde(default)]
    pub displayIndex: i32,
    #[serde(default)]
    pub z: i32,
    #[serde(default)]
    pub color: Option<ColorDef>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ColorDef {
    #[serde(default = "default_alpha")]
    pub aM: f32,
    #[serde(default)]
    pub rM: f32,
    #[serde(default)]
    pub gM: f32,
    #[serde(default)]
    pub bM: f32,
}

fn default_alpha() -> f32 {
    100.0
}

impl Default for ColorDef {
    fn default() -> Self {
        Self {
            aM: 100.0,
            rM: 0.0,
            gM: 0.0,
            bM: 0.0,
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct SkinDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub slot: Vec<SkinSlotDef>,
}

#[derive(Debug, Deserialize)]
pub struct SkinSlotDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub display: Vec<DisplayDef>,
}

#[derive(Debug, Deserialize)]
pub struct DisplayDef {
    #[serde(default)]
    pub name: String,
    #[serde(rename = "type", default)]
    pub display_type: String,
    #[serde(default)]
    pub transform: Option<TransformDef>,
    #[serde(default)]
    pub pivot: Option<PivotDef>,
    #[serde(default)]
    pub path: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct PivotDef {
    #[serde(default)]
    pub x: f32,
    #[serde(default)]
    pub y: f32,
}

#[derive(Debug, Deserialize)]
pub struct AnimationDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub duration: f32,
    #[serde(default)]
    pub playTimes: i32,
    #[serde(default)]
    pub bone: Vec<BoneTimelineDef>,
    #[serde(default)]
    pub slot: Vec<SlotTimelineDef>,
}

#[derive(Debug, Deserialize)]
pub struct BoneTimelineDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub frame: Vec<BoneFrameDef>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct BoneFrameDef {
    #[serde(default)]
    pub duration: u32,
    #[serde(default)]
    pub transform: Option<TransformDef>,
    #[serde(default)]
    pub curve: Option<Vec<f32>>,
    #[serde(default)]
    pub tweenEasing: Option<f32>,
}

#[derive(Debug, Deserialize)]
pub struct SlotTimelineDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub frame: Vec<SlotFrameDef>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct SlotFrameDef {
    #[serde(default)]
    pub duration: u32,
    #[serde(default)]
    pub displayIndex: Option<i32>,
    #[serde(default)]
    pub color: Option<ColorDef>,
    #[serde(default)]
    pub tweenEasing: Option<f32>,
}

#[derive(Debug, Deserialize)]
pub struct IkDef {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub bone: String,
    #[serde(default)]
    pub target: String,
    #[serde(default)]
    pub bendPositive: Option<bool>,
    #[serde(default)]
    pub chain: Option<u32>,
    #[serde(default)]
    pub weight: Option<f32>,
}

pub fn parse(json: &str) -> Result<DragonBonesFile, serde_json::Error> {
    serde_json::from_str(json)
}
