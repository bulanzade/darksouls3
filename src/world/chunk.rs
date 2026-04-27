use crate::world::tileset::TILE_SIZE;
use crate::world::tileset::TileId;

/// Tiles per side of a chunk.
pub const CHUNK_SIZE: usize = 80;

/// A square region of the world made of `CHUNK_SIZE x CHUNK_SIZE` tiles.
pub struct Chunk {
    pub coord: (i32, i32),
    pub tiles: [[TileId; CHUNK_SIZE]; CHUNK_SIZE],
}

impl Chunk {
    pub fn new(coord: (i32, i32)) -> Self {
        Self {
            coord,
            tiles: [[TileId::Empty; CHUNK_SIZE]; CHUNK_SIZE],
        }
    }

    /// 3 rooms with wide archways.
    /// Room 1 (Bonfire): tiles (3,3)-(25,25) — player spawns at pixel (200,200)
    /// Archway 1->2: tiles (26,8)-(29,20)
    /// Room 2 (Enemies): tiles (30,3)-(55,25) — enemies here
    /// Archway 2->3: tiles (38,26)-(47,29)
    /// Room 3 (Boss): tiles (30,30)-(60,55) — boss arena
    pub fn test_chunk(coord: (i32, i32)) -> Self {
        let mut chunk = Self::new(coord);

        for y in 0..CHUNK_SIZE {
            for x in 0..CHUNK_SIZE {
                chunk.tiles[y][x] = TileId::Wall;
            }
        }

        let carve = |tiles: &mut [[TileId; CHUNK_SIZE]; CHUNK_SIZE],
                      x1: usize, y1: usize, x2: usize, y2: usize| {
            for y in y1..=y2 {
                for x in x1..=x2 {
                    tiles[y][x] = TileId::Ground;
                }
            }
        };

        carve(&mut chunk.tiles, 3, 3, 25, 25);   // Room 1
        carve(&mut chunk.tiles, 26, 8, 29, 20);  // Arch 1→2
        carve(&mut chunk.tiles, 30, 3, 55, 25);  // Room 2
        carve(&mut chunk.tiles, 38, 26, 47, 29);  // Arch 2→3
        carve(&mut chunk.tiles, 30, 30, 60, 55);  // Room 3

        chunk
    }

    /// Pixel offset of this chunk in world space.
    pub fn world_offset(&self) -> (f32, f32) {
        let px = self.coord.0 as f32 * CHUNK_SIZE as f32 * TILE_SIZE as f32;
        let py = self.coord.1 as f32 * CHUNK_SIZE as f32 * TILE_SIZE as f32;
        (px, py)
    }
}
