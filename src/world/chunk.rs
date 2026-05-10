use crate::world::tileset::TileId;
use crate::world::tileset::TILE_SIZE;

/// Default tile dimensions used by the built-in test map.
pub const DEFAULT_CHUNK_SIZE: usize = 160;

/// A single loaded map. Older maps were fixed at 160x160 tiles; production
/// maps now keep their LDtk dimensions so DS3 areas can use their own scale.
#[derive(Debug, Clone)]
pub struct Chunk {
    pub coord: (i32, i32),
    pub width: usize,
    pub height: usize,
    pub tiles: Vec<Vec<TileId>>,
}

impl Chunk {
    pub fn new(coord: (i32, i32)) -> Self {
        Self::with_size(coord, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_SIZE)
    }

    pub fn with_size(coord: (i32, i32), width: usize, height: usize) -> Self {
        Self {
            coord,
            width,
            height,
            tiles: vec![vec![TileId::Empty; width]; height],
        }
    }

    pub fn world_width(&self) -> f32 {
        self.width as f32 * TILE_SIZE as f32
    }

    pub fn world_height(&self) -> f32 {
        self.height as f32 * TILE_SIZE as f32
    }

    /// 7-room dungeon with extra-wide corridors:
    /// Room 1 (Bonfire): (3,3)-(25,25) — player spawns at pixel (200,200)
    /// Corridor 1→2: (22,3)-(40,25) — overlaps room 1 east wall, wide east
    /// Room 2 (Enemies): (34,3)-(58,28) — hollow soldiers + archer
    /// Corridor 2→3: (34,24)-(58,42) — overlaps room 2 south wall, wide south
    /// Room 3 (Treasure): (28,38)-(58,60) — item pickups
    /// Corridor 3→4: (56,38)-(75,60) — overlaps room 3 east wall, wide east
    /// Room 4 (Enemies): (70,28)-(100,60) — more enemies
    /// Corridor 4→5: (70,56)-(100,75) — overlaps room 4 south, wide south
    /// Room 5 (Mini-boss): (58,68)-(100,92) — tough enemy
    /// Corridor 5→7: (96,28)-(118,68) — wide east to boss
    /// Room 7 (Boss): (100,3)-(118,48) — boss arena
    pub fn test_chunk(coord: (i32, i32)) -> Self {
        let mut chunk = Self::new(coord);

        for y in 0..chunk.height {
            for x in 0..chunk.width {
                chunk.tiles[y][x] = TileId::Wall;
            }
        }

        let carve = |tiles: &mut [Vec<TileId>],
                      x1: usize, y1: usize, x2: usize, y2| {
            for y in y1..=y2 {
                for x in x1..=x2 {
                    tiles[y][x] = TileId::Ground;
                }
            }
        };

        // Room 1: Bonfire room (enlarged)
        carve(&mut chunk.tiles, 3, 3, 25, 25);
        // Corridor 1→2 (overlapping east wall)
        carve(&mut chunk.tiles, 22, 3, 40, 25);
        // Room 2: Enemy hall
        carve(&mut chunk.tiles, 34, 3, 58, 28);
        // Corridor 2→3 (overlapping south wall)
        carve(&mut chunk.tiles, 34, 24, 58, 42);
        // Room 3: Treasure room
        carve(&mut chunk.tiles, 28, 38, 58, 60);
        // Corridor 3→4 (overlapping east wall, widened north for smooth transition)
        carve(&mut chunk.tiles, 56, 34, 75, 60);
        // Room 4: More enemies
        carve(&mut chunk.tiles, 70, 28, 100, 60);
        // Corridor 4→5 (overlapping south wall, widened for smooth transition)
        carve(&mut chunk.tiles, 68, 54, 102, 75);
        // Room 5: Mini-boss chamber
        carve(&mut chunk.tiles, 58, 68, 100, 92);
        // Corridor 5→7 (wide east to boss, widened for smooth transition)
        carve(&mut chunk.tiles, 96, 20, 118, 75);
        // Room 7: Boss arena (top-right, extra large)
        carve(&mut chunk.tiles, 98, 3, 118, 48);

        // Poison patches (Room 3 treasure room — partial coverage)
        for y in 42..55 {
            for x in 32..45 {
                if (x + y) % 3 != 0 { // Patchy coverage
                    chunk.tiles[y][x] = TileId::Poison;
                }
            }
        }
        // Poison patch in corridor 4→5
        for y in 60..68 {
            for x in 75..82 {
                if (x + y) % 2 == 0 {
                    chunk.tiles[y][x] = TileId::Poison;
                }
            }
        }

        chunk
    }

    /// Pixel offset of this chunk in world space.
    pub fn world_offset(&self) -> (f32, f32) {
        let px = self.coord.0 as f32 * self.world_width();
        let py = self.coord.1 as f32 * self.world_height();
        (px, py)
    }
}
