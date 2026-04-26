use crate::world::chunk::CHUNK_SIZE;
use crate::world::chunk::Chunk;
use crate::world::tileset::TileId;
use crate::world::tileset::Tileset;
use crate::world::tileset::TILE_SIZE;

/// Grid of solidity flags for a single chunk, built from tile data.
pub struct CollisionGrid {
    pub solid: [[bool; CHUNK_SIZE]; CHUNK_SIZE],
}

impl CollisionGrid {
    /// Build a collision grid from a chunk and its tileset definitions.
    pub fn from_chunk(chunk: &Chunk, tileset: &Tileset) -> Self {
        let mut solid = [[false; CHUNK_SIZE]; CHUNK_SIZE];

        for y in 0..CHUNK_SIZE {
            for x in 0..CHUNK_SIZE {
                let tile_id = chunk.tiles[y][x];
                if tile_id == TileId::Empty {
                    continue;
                }
                if let Some(def) = tileset.get(tile_id) {
                    solid[y][x] = def.solid;
                }
            }
        }

        Self { solid }
    }

    /// Check if a tile at local chunk coordinates is solid.
    /// Out-of-bounds coordinates are treated as solid (wall).
    pub fn is_solid(&self, x: i32, y: i32) -> bool {
        if x < 0 || x >= CHUNK_SIZE as i32 || y < 0 || y >= CHUNK_SIZE as i32 {
            return true;
        }
        self.solid[y as usize][x as usize]
    }

    /// Resolve an AABB (center x,y with half-extents half_w, half_h) against
    /// solid tiles in this chunk. Returns the corrected (x, y) position by
    /// resolving the axis with the smallest penetration.
    ///
    /// `chunk_offset` is the world-space pixel offset of the chunk origin.
    pub fn resolve_aabb(
        &self,
        chunk_offset: (f32, f32),
        x: f32,
        y: f32,
        half_w: f32,
        half_h: f32,
    ) -> (f32, f32) {
        let tile_size = TILE_SIZE as f32;

        // Convert world AABB bounds to tile coordinates
        let left = (x - half_w - chunk_offset.0) / tile_size;
        let right = (x + half_w - chunk_offset.0) / tile_size;
        let top = (y - half_h - chunk_offset.1) / tile_size;
        let bottom = (y + half_h - chunk_offset.1) / tile_size;

        let tile_x_min = left.floor() as i32;
        let tile_x_max = right.floor() as i32;
        let tile_y_min = top.floor() as i32;
        let tile_y_max = bottom.floor() as i32;

        let mut resolved_x = x;
        let mut resolved_y = y;

        for ty in tile_y_min..=tile_y_max {
            for tx in tile_x_min..=tile_x_max {
                if !self.is_solid(tx, ty) {
                    continue;
                }

                // Tile AABB in world space
                let tile_left = chunk_offset.0 + tx as f32 * tile_size;
                let tile_right = tile_left + tile_size;
                let tile_top = chunk_offset.1 + ty as f32 * tile_size;
                let tile_bottom = tile_top + tile_size;

                // AABB overlap check
                let overlap_x = (resolved_x + half_w).min(tile_right) - (resolved_x - half_w).max(tile_left);
                let overlap_y = (resolved_y + half_h).min(tile_bottom) - (resolved_y - half_h).max(tile_top);

                if overlap_x <= 0.0 || overlap_y <= 0.0 {
                    continue;
                }

                // Resolve minimum penetration axis
                if overlap_x < overlap_y {
                    if resolved_x < tile_left + tile_size * 0.5 {
                        resolved_x = tile_left - half_w;
                    } else {
                        resolved_x = tile_right + half_w;
                    }
                } else {
                    if resolved_y < tile_top + tile_size * 0.5 {
                        resolved_y = tile_top - half_h;
                    } else {
                        resolved_y = tile_bottom + half_h;
                    }
                }
            }
        }

        (resolved_x, resolved_y)
    }
}
