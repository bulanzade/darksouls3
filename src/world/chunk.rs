use crate::world::tileset::TILE_SIZE;
use crate::world::tileset::TileId;

/// Tiles per side of a chunk.
pub const CHUNK_SIZE: usize = 32;

/// A square region of the world made of `CHUNK_SIZE x CHUNK_SIZE` tiles.
pub struct Chunk {
    pub coord: (i32, i32),
    pub tiles: [[TileId; CHUNK_SIZE]; CHUNK_SIZE],
}

impl Chunk {
    /// Create a chunk filled entirely with Empty tiles.
    pub fn new(coord: (i32, i32)) -> Self {
        Self {
            coord,
            tiles: [[TileId::Empty; CHUNK_SIZE]; CHUNK_SIZE],
        }
    }

    /// Create a test chunk with walls around edges and ground inside.
    ///
    /// Layout (row-major, y increases downward):
    ///   - Top row (y=0): Wall
    ///   - Rows 1..CHUNK_SIZE-3: Wall at x=0 and x=CHUNK_SIZE-1, Ground inside
    ///   - Second-to-last row: WallTop
    ///   - Last row: Wall
    pub fn test_chunk(coord: (i32, i32)) -> Self {
        let mut chunk = Self::new(coord);
        let last = CHUNK_SIZE - 1;
        let second_last = CHUNK_SIZE - 2;

        for x in 0..CHUNK_SIZE {
            // Top row
            chunk.tiles[0][x] = TileId::Wall;
            // Bottom row
            chunk.tiles[last][x] = TileId::Wall;
            // Second-to-last row (wall-top)
            chunk.tiles[second_last][x] = TileId::WallTop;
        }

        for y in 1..second_last {
            chunk.tiles[y][0] = TileId::Wall;
            chunk.tiles[y][last] = TileId::Wall;
            for x in 1..last {
                chunk.tiles[y][x] = TileId::Ground;
            }
        }

        chunk
    }

    /// Pixel offset of this chunk in world space.
    pub fn world_offset(&self) -> (f32, f32) {
        let px = self.coord.0 as f32 * CHUNK_SIZE as f32 * TILE_SIZE as f32;
        let py = self.coord.1 as f32 * CHUNK_SIZE as f32 * TILE_SIZE as f32;
        (px, py)
    }
}
