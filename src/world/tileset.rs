/// Numeric tile identifier.
#[repr(u16)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TileId {
    Empty = 0,
    Ground = 1,
    Wall = 2,
    WallTop = 3,
    Poison = 4,
}

impl TileId {
    pub fn from_u16(v: u16) -> Self {
        match v {
            0 => TileId::Empty,
            1 => TileId::Ground,
            2 => TileId::Wall,
            3 => TileId::WallTop,
            4 => TileId::Poison,
            _ => TileId::Empty,
        }
    }
}

/// Per-tile definition: UV rect within a tileset texture and solidity flag.
pub struct TileDef {
    pub uv_x: f32,
    pub uv_y: f32,
    pub uv_w: f32,
    pub uv_h: f32,
    pub solid: bool,
}

/// Pixel size of a single tile.
pub const TILE_SIZE: u32 = 16;

/// Collection of tile definitions referencing a single tileset texture.
pub struct Tileset {
    pub tiles: Vec<TileDef>,
}

impl Tileset {
    /// Build a test tileset with 4 tiles laid out horizontally in a 64x16 texture.
    ///
    /// Layout: `[Empty][Ground][Wall][WallTop]` each 16x16 px.
    pub fn test_tileset(tileset_w: u32, tileset_h: u32) -> Self {
        let tw = tileset_w as f32;
        let th = tileset_h as f32;
        let tile_w = TILE_SIZE as f32 / tw; // normalised width of one tile
        let tile_h = TILE_SIZE as f32 / th; // normalised height of one tile

        let tiles = vec![
            // Empty — UVs point at first tile slot, not solid
            TileDef {
                uv_x: 0.0 * tile_w,
                uv_y: 0.0,
                uv_w: tile_w,
                uv_h: tile_h,
                solid: false,
            },
            // Ground — second slot, not solid
            TileDef {
                uv_x: 1.0 * tile_w,
                uv_y: 0.0,
                uv_w: tile_w,
                uv_h: tile_h,
                solid: false,
            },
            // Wall — third slot, solid
            TileDef {
                uv_x: 2.0 * tile_w,
                uv_y: 0.0,
                uv_w: tile_w,
                uv_h: tile_h,
                solid: true,
            },
            // WallTop — fourth slot, solid
            TileDef {
                uv_x: 3.0 * tile_w,
                uv_y: 0.0,
                uv_w: tile_w,
                uv_h: tile_h,
                solid: true,
            },
            // Poison — fifth slot, not solid but toxic
            TileDef {
                uv_x: 4.0 * tile_w,
                uv_y: 0.0,
                uv_w: tile_w,
                uv_h: tile_h,
                solid: false,
            },
        ];

        Self { tiles }
    }

    /// Look up a tile definition by ID.
    pub fn get(&self, id: TileId) -> Option<&TileDef> {
        let idx = id as u16 as usize;
        self.tiles.get(idx)
    }
}
