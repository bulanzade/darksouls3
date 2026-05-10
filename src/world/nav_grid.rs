use std::collections::{BinaryHeap, HashMap};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NavCell {
    pub x: i32,
    pub y: i32,
}

impl NavCell {
    pub fn new(x: i32, y: i32) -> Self { Self { x, y } }
}

impl Ord for NavCell {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Reverse for min-heap
        other.x.cmp(&self.x).then(other.y.cmp(&self.y))
    }
}
impl PartialOrd for NavCell {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> { Some(self.cmp(other)) }
}

#[derive(Clone)]
pub struct NavGrid {
    pub width: i32,
    pub height: i32,
    pub walkable: Vec<bool>,
    pub cell_size: i32,  // World pixels per nav cell (e.g., 2 tiles per cell)
}

impl NavGrid {
    pub fn from_collision_grid(
        collision: &crate::world::collision::CollisionGrid,
        cell_size: i32,
    ) -> Self {
        let grid_w = (collision.width as i32 + cell_size - 1) / cell_size;
        let grid_h = (collision.height as i32 + cell_size - 1) / cell_size;
        let mut walkable = vec![true; (grid_w * grid_h) as usize];

        for cy in 0..grid_h {
            for cx in 0..grid_w {
                // Check if any tile in this cell is solid
                let mut blocked = false;
                for ty in 0..cell_size {
                    for tx in 0..cell_size {
                        let tile_x = cx * cell_size + tx;
                        let tile_y = cy * cell_size + ty;
                        if tile_x < collision.width as i32 && tile_y < collision.height as i32 {
                            if collision.is_solid(tile_x, tile_y) {
                                blocked = true;
                                break;
                            }
                        }
                    }
                    if blocked { break; }
                }
                walkable[(cy * grid_w + cx) as usize] = !blocked;
            }
        }

        Self { width: grid_w, height: grid_h, walkable, cell_size }
    }

    pub fn is_walkable(&self, x: i32, y: i32) -> bool {
        if x < 0 || y < 0 || x >= self.width || y >= self.height { return false; }
        self.walkable[(y * self.width + x) as usize]
    }

    pub fn world_to_cell(&self, world_x: f32, world_y: f32) -> NavCell {
        let tile_size = crate::world::tileset::TILE_SIZE as i32;
        NavCell::new(
            world_x as i32 / (tile_size * self.cell_size),
            world_y as i32 / (tile_size * self.cell_size),
        )
    }

    pub fn cell_to_world(&self, cell: NavCell) -> (f32, f32) {
        let tile_size = crate::world::tileset::TILE_SIZE as f32;
        let half = self.cell_size as f32 * tile_size * 0.5;
        (cell.x as f32 * self.cell_size as f32 * tile_size + half,
         cell.y as f32 * self.cell_size as f32 * tile_size + half)
    }

    /// A* pathfinding from start to goal
    pub fn find_path(&self, start: NavCell, goal: NavCell) -> Vec<NavCell> {
        if !self.is_walkable(start.x, start.y) || !self.is_walkable(goal.x, goal.y) {
            return vec![];
        }

        let mut open = BinaryHeap::new();
        let mut came_from: HashMap<(i32, i32), (i32, i32)> = HashMap::new();
        let mut g_score: HashMap<(i32, i32), i32> = HashMap::new();

        g_score.insert((start.x, start.y), 0);
        open.push((0i32, start));

        let neighbors = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)];

        while let Some((_, current)) = open.pop() {
            if current.x == goal.x && current.y == goal.y {
                // Reconstruct path
                let mut path = vec![goal];
                let mut pos = (goal.x, goal.y);
                while let Some(&prev) = came_from.get(&pos) {
                    path.push(NavCell::new(prev.0, prev.1));
                    pos = prev;
                }
                path.reverse();
                return path;
            }

            let current_g = *g_score.get(&(current.x, current.y)).unwrap_or(&i32::MAX);

            for &(dx, dy) in &neighbors {
                let nx = current.x + dx;
                let ny = current.y + dy;
                if !self.is_walkable(nx, ny) { continue; }

                // Diagonal: check that both adjacent cells are also walkable
                if dx != 0 && dy != 0 {
                    if !self.is_walkable(current.x + dx, current.y) || !self.is_walkable(current.x, current.y + dy) {
                        continue;
                    }
                }

                let move_cost = if dx != 0 && dy != 0 { 14 } else { 10 }; // 10 ~= 1.0, 14 ~= 1.414
                let new_g = current_g + move_cost;

                let key = (nx, ny);
                if new_g < *g_score.get(&key).unwrap_or(&i32::MAX) {
                    g_score.insert(key, new_g);
                    came_from.insert(key, (current.x, current.y));
                    let h = (nx - goal.x).abs() + (ny - goal.y).abs(); // Manhattan heuristic
                    open.push((-(new_g + h * 10), NavCell::new(nx, ny)));
                }
            }
        }

        vec![] // No path found
    }
}
