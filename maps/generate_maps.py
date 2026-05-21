#!/usr/bin/env python3
"""Generate LDtk .ldtkl level files from design docs in docs/maps/."""
import json
import os
import sys
import uuid
from collections import deque

# Ensure project root is in sys.path for package imports (maps.maps.*)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

CHUNK_SIZE = 160
TILE_SIZE = 16
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_WALL = 2
TILE_WALLTOP = 3
TILE_POISON = 4

POISON_KEYWORDS = (
    "毒", "沼泽", "沼", "污水", "浅水", "熔岩湖", "熔岩地面", "熔岩裂隙", "熔岩竞技场",
    "lava", "flooded", "stagnant", "sludge", "poison_water",
    "火焰废墟", "火焰大厅", "熔岩",
)

def poison_tile(features):
    return TILE_POISON if any(kw in features for kw in POISON_KEYWORDS) else TILE_GROUND

MARGIN = 6
USABLE = CHUNK_SIZE - 2 * MARGIN
BASE_MAP_PX = CHUNK_SIZE * TILE_SIZE

LEVEL_UIDS = {
    "CemeteryOfAsh": 1,
    "FirelinkShrine": 2,
    "LothricWall": 3,
    "UndeadSettlement": 4,
    "RoadOfSacrifices": 5,
    "FarronKeep": 6,
    "CathedralDeep": 7,
    "CatacombsOfCarthus": 8,
    "SmoulderingLake": 9,
    "Irithyll": 10,
    "IrithyllDungeon": 11,
    "ProfanedCapital": 12,
    "AnorLondo": 13,
    "LothricCastle": 14,
    "GrandArchives": 15,
    "KilnOfTheFirstFlame": 16,
    "ConsumedKingsGarden": 17,
    "UntendedGraves": 18,
    "ArchdragonPeak": 19,
}

ENTITY_UIDS = {
    "PlayerSpawn": 101, "BossSpawn": 102, "Bonfire": 103,
    "Enemy": 104, "Item": 105, "Chest": 106, "Npc": 107,
    "Light": 108, "FogGate": 109, "TilePatch": 110,
}

ENUM_UIDS = {
    "EnemyKind": 201, "ItemKind": 202, "NpcKind": 203, "TileKind": 204,
}

FIELD_UIDS = {
    "PlayerSpawn.heal": 301,
    "Enemy.kind": 302,
    "Item.kind": 303, "Item.value": 304, "Item.name": 305,
    "Chest.loot_kind": 306, "Chest.loot_value": 307, "Chest.loot_name": 308,
    "Chest.is_mimic": 309, "Chest.slot": 310,
    "Npc.name": 311, "Npc.kind": 312, "Npc.color": 313, "Npc.dialogue": 314,
    "Light.radius": 315, "Light.r": 316, "Light.g": 317, "Light.b": 318, "Light.intensity": 319,
    "FogGate.dest_area": 320, "FogGate.dest_x": 321, "FogGate.dest_y": 322,
    "FogGate.width": 323, "FogGate.height": 324,
    "TilePatch.tile": 325, "TilePatch.x1": 326, "TilePatch.y1": 327,
    "TilePatch.x2": 328, "TilePatch.y2": 329, "TilePatch.condition": 330,
}

ENEMY_KIND_MAP = {
    # Direct mappings (already in Rust enum)
    "HollowSoldier": "HollowSoldier", "Archer": "Archer", "Knight": "Knight",
    "Assassin": "Assassin", "DarkMage": "DarkMage", "CrystalLizard": "CrystalLizard",
    "SilverKnight": "SilverKnight", "BlackKnight": "BlackKnight",
    "DeepAccursed": "DeepAccursed", "Evangelist": "Evangelist", "Thrall": "Thrall",
    "LothricKnight": "LothricKnight", "WingedKnight": "WingedKnight",
    "Ghru": "Ghru", "Darkwraith": "Darkwraith", "Skeleton": "Skeleton",
    "Jailer": "Jailer", "SerpentMan": "SerpentMan", "Deacon": "Deacon",
    "FireDemon": "FireDemon", "StarvedHound": "StarvedHound", "PusOfMan": "PusOfMan",
    "CathedralKnight": "CathedralKnight", "ManGrub": "ManGrub", "Gargoyle": "Gargoyle",
    "Dog": "Dog", "Basilisk": "Basilisk", "DemonStatue": "DemonStatue",
    "InfestedCorpse": "InfestedCorpse", "InfectedCorpse": "InfestedCorpse", "Wretch": "Wretch", "PeasantHollow": "PeasantHollow",
    "Mimic": "Mimic", "GiantSlave": "GiantSlave", "HollowAssassin": "HollowAssassin",
    "CathedralGraveWarden": "CathedralGraveWarden", "Rat": "Rat", "MiniBoss": "MiniBoss",
    "LargeHollowSoldier": "LargeHollowSoldier",
    # Aliases for design-doc enemy kinds not in Rust enum
    "SwordMaster": "Assassin",
    "BorealKnight": "Knight",
    "LothricWyvern": "MiniBoss",
    "Hodrick": "MiniBoss",
    "CagedHollow": "PeasantHollow",
    "Ghrul": "Ghru",
    "DarkSpirit": "Knight",
    "Berengaria": "DarkMage",
    "SkeletonSwordman": "Skeleton",
    "SkeletonBall": "Skeleton",
    "SkeletonWheel": "Skeleton",
    "CarthusWorm": "MiniBoss",
    "GiantHollow": "GiantSlave",
    "AncientWyvern": "MiniBoss",
    "NamelessKing": "MiniBoss",
    "ConsumedKingKnight": "CathedralKnight",
    "ConsumedKingGuard": "WingedKnight",
    "FlyingDragon": "MiniBoss",
    "Harpe": "Skeleton",
    "Leech": "Dog",
    "Blowdart": "Archer",
    "GraveWarden": "CathedralGraveWarden",
    "CursedWood": "MiniBoss",
    "Demon": "FireDemon",
    "Spider": "Basilisk",
    "GargoyleDog": "Dog",
    "BorealOutriderKnight": "WingedKnight",
    "AscendedWingedKnight": "WingedKnight",
    "Corvian": "Assassin",
    "CorvianStoryteller": "DarkMage",
    "HollowSlave": "Thrall",
    "ClawedCurse": "Basilisk",
    "GrandArchivesScholar": "DarkMage",
    "CrystalSage": "DarkMage",
    "PoisonhornBug": "Basilisk",
    "RavenousCrystalLizard": "CrystalLizard",
    "RottenSlug": "Rat",
    "LesserCrab": "Dog",
    "RockLizard": "CrystalLizard",
    "Hollow": "HollowSoldier",
    "DrakebloodKnight": "Knight",
    "HavelKnight": "WingedKnight",
    "SewerCentipede": "Wretch",
    "IrithyllianSlave": "Assassin",
    "LycanthropeHunter": "Knight",
    "CageSpider": "Basilisk",
    "MonstrosityOfSin": "GiantSlave",
    "GreatCrab": "GiantSlave",
    "SulyvahnsBeast": "GiantSlave",
    "CarthusSandworm": "MiniBoss",
    "Lycanthrope": "PeasantHollow",
    "Madwoman": "PeasantHollow",
    "ExileWarrior": "Knight",
    "ElderGhru": "Ghru",
    "SmolderingGhru": "Ghru",
    "SmolderingRottenFlesh": "Rat",
    "DemonCleric": "FireDemon",
    "HollowPriest": "DarkMage",
    "BurningStakeWitch": "DarkMage",
    "DevoutHollow": "PeasantHollow",
    "ReanimatedCorpse": "InfestedCorpse",
    "CorpseGrub": "InfestedCorpse",
    "WrithingRottenFlesh": "Rat",
    "RottenFleshOfAldrich": "Rat",
    "HoundRat": "Rat",
    "LargeHoundRat": "Rat",
    "PontiffKnight": "Knight",
    "IrithyllianBeasthound": "Dog",
    "CathedralEvangelist": "Evangelist",
    "JailerHandmaid": "Jailer",
    "SerpentManSummoner": "DarkMage",
    "AvariciousBeing": "Mimic",
    "HeadlessGargoyle": "Gargoyle",
    "PaintingGuardian": "Assassin",
    "HollowManservant": "PeasantHollow",
    "StrayDemon": "MiniBoss",
    "LothricPriest": "DarkMage",
    "GiantRat": "Rat",
    "RootSkeleton": "Skeleton",
    "WorkerHollow": "PeasantHollow",
}

def new_chunk(width=CHUNK_SIZE, height=CHUNK_SIZE):
    return [[TILE_WALL for _ in range(width)] for _ in range(height)]

def fill_tiles(chunk, tile, x1, y1, x2, y2):
    h = len(chunk)
    w = len(chunk[0]) if h else 0
    for y in range(max(0, y1), min(h, y2 + 1)):
        for x in range(max(0, x1), min(w, x2 + 1)):
            chunk[y][x] = tile

def carve_ellipse(chunk, cx, cy, rx, ry):
    h = len(chunk)
    w = len(chunk[0]) if h else 0
    for y in range(max(0, cy - ry), min(h, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(w, cx + rx + 1)):
            dx = (x - cx) / rx if rx > 0 else 0
            dy = (y - cy) / ry if ry > 0 else 0
            if dx * dx + dy * dy <= 1.0:
                chunk[y][x] = TILE_GROUND

def cw(chunk, px, py, r=2):
    """Clear ground around a pixel position."""
    tx, ty = int(px) // TILE_SIZE, int(py) // TILE_SIZE
    fill_tiles(chunk, TILE_GROUND, tx - r, ty - r, tx + r, ty + r)

def chunk_to_csv(chunk):
    csv = []
    for y in range(len(chunk)):
        for x in range(len(chunk[0])):
            csv.append(chunk[y][x])
    return csv

def fix_terrain_connectivity(chunk):
    """Carve minimal wall paths to connect all ground/poison regions."""
    h = len(chunk)
    w = len(chunk[0]) if h > 0 else 0
    walkable = set()
    for y in range(h):
        for x in range(w):
            if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                walkable.add((x, y))
    if not walkable:
        return
    start = next(iter(walkable))
    visited = set()
    q = deque([start])
    visited.add(start)
    while q:
        x, y = q.popleft()
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) in walkable and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny))
    disconnected = walkable - visited
    if not disconnected:
        return
    remaining = set(disconnected)
    while remaining:
        s = next(iter(remaining))
        cv = set()
        q2 = deque([s])
        cv.add(s)
        remaining.discard(s)
        while q2:
            x, y = q2.popleft()
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if (nx, ny) in remaining:
                    remaining.discard((nx, ny))
                    cv.add((nx, ny))
                    q2.append((nx, ny))
        # Find shortest wall path from cv to visited
        wall_parent = {}
        q3 = deque()
        for (cx, cy) in cv:
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in cv and chunk[ny][nx] == TILE_WALL and (nx, ny) not in wall_parent:
                    wall_parent[(nx, ny)] = (cx, cy)
                    q3.append((nx, ny))
        found = None
        while q3 and found is None:
            x, y = q3.popleft()
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) in visited:
                        found = (x, y)
                        break
                    if chunk[ny][nx] == TILE_WALL and (nx, ny) not in wall_parent:
                        wall_parent[(nx, ny)] = (x, y)
                        q3.append((nx, ny))
        if found:
            path = []
            cur = found
            while cur not in cv:
                path.append(cur)
                cur = wall_parent[cur]
        else:
            path = []
        for px, py in path:
            chunk[py][px] = TILE_GROUND
            walkable.add((px, py))
            visited.add((px, py))
        # Expand visited through newly connected cluster
        q4 = deque(cv)
        visited.update(cv)
        while q4:
            x, y = q4.popleft()
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if (nx, ny) in walkable and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q4.append((nx, ny))

def chunk_width(chunk):
    return len(chunk[0]) if chunk else 0

def chunk_height(chunk):
    return len(chunk)

def make_field(identifier, field_type, value):
    return {
        "__identifier": identifier,
        "__type": field_type,
        "__value": value,
        "defUid": 0,
        "realEditorValues": [],
        "__tile": None,
    }

def make_entity(identifier, px, py, fields=None):
    return {
        "__identifier": identifier,
        "__grid": [int(px) // 16, int(py) // 16],
        "__pivot": [0.5, 1.0],
        "__smartColor": "#FFFFFF",
        "__tags": [],
        "__tile": None,
        "__worldX": None,
        "__worldY": None,
        "defUid": ENTITY_UIDS[identifier],
        "fieldInstances": fields or [],
        "height": 16,
        "iid": str(uuid.uuid4()),
        "px": [int(px), int(py)],
        "width": 16,
    }

def populate_entity_def_uids(entities):
    for ent in entities:
        ent["defUid"] = ENTITY_UIDS[ent["__identifier"]]
        for fld in ent.get("fieldInstances", []):
            key = f"{ent['__identifier']}.{fld['__identifier']}"
            fld["defUid"] = FIELD_UIDS.get(key, 0)

# --- Dynamic-size helpers ---

def clamp_tile(value, max_value):
    return max(0, min(max_value - 1, int(round(value))))

def doc_tile(px, py, width, height):
    return clamp_tile(px / TILE_SIZE, width), clamp_tile(py / TILE_SIZE, height)

def carve_corridor_dynamic(chunk, x1, y1, x2, y2, width=5):
    half = max(1, width // 2)
    for x in range(min(x1, x2), max(x1, x2) + 1):
        fill_tiles(chunk, TILE_GROUND, x, y1 - half, x, y1 + half)
    for y in range(min(y1, y2), max(y1, y2) + 1):
        fill_tiles(chunk, TILE_GROUND, x2 - half, y, x2 + half, y)

def section_center_tile(section):
    return ((section["x"] + section["w"] * 0.5) / TILE_SIZE,
            (section["y"] + section["h"] * 0.5) / TILE_SIZE)

def is_walkable_tile(tile):
    return tile in (TILE_GROUND, TILE_POISON)

def find_walkable_tile(chunk, tx, ty, max_radius=256):
    width = chunk_width(chunk)
    height = chunk_height(chunk)
    if width == 0 or height == 0:
        return None
    tx = clamp_tile(tx, width)
    ty = clamp_tile(ty, height)
    for radius in range(max_radius + 1):
        for y in range(max(0, ty - radius), min(height, ty + radius + 1)):
            for x in range(max(0, tx - radius), min(width, tx + radius + 1)):
                if abs(x - tx) != radius and abs(y - ty) != radius:
                    continue
                if is_walkable_tile(chunk[y][x]):
                    return x, y
    return None

def snap_entities_to_walkable(chunk, entities, skip_types=("FogGate", "PlayerSpawn", "TilePatch")):
    """Pre-compute walkable tiles then snap all entities to nearest one."""
    h = len(chunk)
    w = len(chunk[0]) if h else 0
    # Collect all walkable tile positions
    walkable = []
    for y in range(h):
        row = chunk[y]
        for x in range(w):
            if row[x] in (TILE_GROUND, TILE_POISON):
                walkable.append((x, y))
    if not walkable:
        return
    # For each entity, find nearest walkable tile by Manhattan distance
    import math
    for ent in entities:
        if ent["__identifier"] in skip_types:
            continue
        px = ent.get("px", [0, 0])
        if not isinstance(px, list) or len(px) < 2:
            continue
        tx, ty = int(px[0]) // TILE_SIZE, int(px[1]) // TILE_SIZE
        best = None
        best_d = float('inf')
        for wx, wy in walkable:
            d = abs(wx - tx) + abs(wy - ty)
            if d < best_d:
                best_d = d
                best = (wx, wy)
                if d == 0:
                    break
        if best:
            x, y = best
            ent["px"] = [x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2]
            ent["__grid"] = [x, y]

def snap_entity_to_walkable(chunk, entity):
    px = entity.get("px", [0, 0])
    if not isinstance(px, list) or len(px) < 2:
        return
    tx, ty = int(px[0]) // TILE_SIZE, int(px[1]) // TILE_SIZE
    found = find_walkable_tile(chunk, tx, ty)
    if not found:
        return
    x, y = found
    entity["px"] = [x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2]
    entity["__grid"] = [x, y]

def generate_official_terrain(doc):
    width = max(1, int(round(doc["map_size"]["width"] / TILE_SIZE)))
    height = max(1, int(round(doc["map_size"]["height"] / TILE_SIZE)))
    chunk = new_chunk(width, height)
    sections = doc.get("map_layout", {}).get("sections", [])

    centers = []
    for section in sections:
        x1, y1 = doc_tile(section["x"], section["y"], width, height)
        x2, y2 = doc_tile(section["x"] + section["w"], section["y"] + section["h"], width, height)
        features = " ".join(section.get("terrain_features", []))
        tile = poison_tile(features)
        fill_tiles(chunk, tile, x1, y1, x2, y2)
        cx, cy = section_center_tile(section)
        centers.append((clamp_tile(cx, width), clamp_tile(cy, height)))

    # The section order in docs/maps is authored as the canonical route, with
    # optional branches inserted at their real branching points.
    for (x1, y1), (x2, y2) in zip(centers, centers[1:]):
        carve_corridor_dynamic(chunk, x1, y1, x2, y2, width=7)

    # Keep bonfires, bosses, and fog gates anchored in walkable pockets even if
    # their exact coordinate lies on a section edge.
    for point in doc.get("bonfires", []):
        x, y = doc_tile(point["x"], point["y"], width, height)
        fill_tiles(chunk, TILE_GROUND, x - 3, y - 3, x + 3, y + 3)
    boss = doc.get("boss")
    if boss:
        if isinstance(boss, list):
            bosses = boss
        else:
            bosses = [boss]
        for item in bosses:
            x, y = doc_tile(item.get("x", 0), item.get("y", 0), width, height)
            fill_tiles(chunk, TILE_GROUND, x - 5, y - 5, x + 5, y + 5)
    for gate in doc.get("fog_gates", []):
        x, y = doc_tile(gate.get("x", 0), gate.get("y", 0), width, height)
        fill_tiles(chunk, TILE_GROUND, x - 3, y - 3, x + 3, y + 3)

    return chunk

# --- Connectivity ---

def bfs_reachable(chunk, sx, sy):
    """BFS from tile (sx,sy), return set of reachable ground tile positions."""
    h = len(chunk)
    w = len(chunk[0]) if h else 0
    if not (0 <= sx < w and 0 <= sy < h):
        return set()
    if chunk[sy][sx] not in (TILE_GROUND, TILE_POISON):
        return set()
    visited = set()
    q = deque([(sx, sy)])
    visited.add((sx, sy))
    while q:
        x, y = q.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if chunk[ny][nx] in (TILE_GROUND, TILE_POISON):
                    visited.add((nx, ny))
                    q.append((nx, ny))
    return visited

def carve_corridor(chunk, x1, y1, x2, y2, width=3):
    """Carve an L-shaped corridor between two tile positions."""
    cw = len(chunk[0]) if chunk else CHUNK_SIZE
    ch = len(chunk) if chunk else CHUNK_SIZE
    half = width // 2
    # Horizontal then vertical
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for dy in range(-half, half + 1):
            ny = y1 + dy
            if 0 <= x < cw and 0 <= ny < ch:
                chunk[ny][x] = TILE_GROUND
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for dx in range(-half, half + 1):
            nx = x2 + dx
            if 0 <= nx < cw and 0 <= y < ch:
                chunk[y][nx] = TILE_GROUND

def ensure_connected(chunk, spawn_px, spawn_py, entity_positions):
    """Ensure all entity tile positions are reachable from spawn. Returns coverage %."""
    sx, sy = int(spawn_px) // TILE_SIZE, int(spawn_py) // TILE_SIZE
    chw = len(chunk[0]) if chunk else CHUNK_SIZE
    chh = len(chunk) if chunk else CHUNK_SIZE
    # Make sure spawn is on ground
    cw(chunk, spawn_px, spawn_py, 2)

    targets = set()
    for px, py in entity_positions:
        tx, ty = int(px) // TILE_SIZE, int(py) // TILE_SIZE
        if 0 <= tx < chw and 0 <= ty < chh:
            targets.add((tx, ty))
            # Ensure each entity has ground
            fill_tiles(chunk, TILE_GROUND, tx - 1, ty - 1, tx + 1, ty + 1)

    for _ in range(3):  # retry up to 3 times
        reachable = bfs_reachable(chunk, sx, sy)
        unreachable = targets - reachable
        if not unreachable:
            return 100
        for tx, ty in unreachable:
            carve_corridor(chunk, sx, sy, tx, ty, width=3)

    reachable = bfs_reachable(chunk, sx, sy)
    if not targets:
        return 100
    return int(len(targets & reachable) / len(targets) * 100)


# --- Map functions (lazy-loaded from individual modules) ---
import importlib as _importlib

def _lazy(module_name, func_name):
    def _fn():
        mod = _importlib.import_module(f"maps.maps.{module_name}")
        return getattr(mod, func_name)()
    return _fn

_MAP_MODULES = {
    "CemeteryOfAsh": ("cemetery_of_ash", "make_cemetery_of_ash"),
    "FirelinkShrine": ("firelink_shrine", "make_firelink_shrine"),
    "LothricWall": ("lothric_wall", "make_lothric_wall"),
    "UndeadSettlement": ("undead_settlement", "make_undead_settlement"),
    "RoadOfSacrifices": ("road_of_sacrifices", "make_road_of_sacrifices"),
    "FarronKeep": ("farron_keep", "make_farron_keep"),
    "CathedralDeep": ("cathedral_deep", "make_cathedral_deep"),
    "CatacombsOfCarthus": ("catacombs_of_carthus", "make_catacombs_of_carthus"),
    "SmoulderingLake": ("smouldering_lake", "make_smouldering_lake"),
    "Irithyll": ("irithyll", "make_irithyll"),
    "IrithyllDungeon": ("irithyll_dungeon", "make_irithyll_dungeon"),
    "ProfanedCapital": ("profaned_capital", "make_profaned_capital"),
    "AnorLondo": ("anor_londo", "make_anor_londo"),
    "LothricCastle": ("lothric_castle", "make_lothric_castle"),
    "GrandArchives": ("grand_archives", "make_grand_archives"),
    "KilnOfTheFirstFlame": ("kiln_of_the_first_flame", "make_kiln_of_the_first_flame"),
    "ConsumedKingsGarden": ("consumed_kings_garden", "make_consumed_kings_garden"),
    "UntendedGraves": ("untended_graves", "make_untended_graves"),
    "ArchdragonPeak": ("archdragon_peak", "make_archdragon_peak"),
}

# Map ID -> terrain override function (lazy-loaded, returns (map_id, chunk, entities))
TERRAIN_OVERRIDES = {k: _lazy(mod, fn) for k, (mod, fn) in _MAP_MODULES.items()}

# --- Item kind mapping ---

def map_item_kind(item):
    kind = item.get("kind", "")
    if kind in ("EstusShard",): return "EstusShard"
    if kind in ("HomewardBone",): return "HomewardBone"
    if kind in ("PurpleMoss",): return "PurpleMoss"
    if kind in ("Ember",): return "Ember"
    if kind in ("TitaniteShard", "TitaniteScale"): return "TitaniteShard"
    if kind in ("UndeadBoneShard",): return "UndeadBoneShard"
    if kind in ("Firebomb",): return "Firebomb"
    if kind in ("CoiledSword",): return "Consumable"
    if "Soul" in kind or kind == "SoulItem": return "SoulOrb"
    if kind in ("Weapon", "WeaponDrop") or kind in (
        "Dagger", "Uchigatana", "Claymore", "Rapier", "Spear", "Longsword",
        "Broadsword", "AstoraStraightSword", "HandAxe", "Partizan", "Whip",
        "Caestus", "GreatScythe", "LargeClub", "RedHiltedHalberd",
        "IrithyllStraightSword", "MailBreaker", "BrokenStraightSword",
        "SwordSpear", "DragonslayerSwordSpear", "Estoc", "Flamberge",
    ):
        return "WeaponDrop"
    if "Shield" in kind or kind in ("SmallLeatherShield", "PlankShield",
        "BlueWoodenShield", "CaduceusRoundShield", "SilverEagleKiteShield",
        "EastWestShield", "WargodWoodenShield", "BlessedRedWhiteShield",
        "HawkwoodsShield", "SunsetShield", "ClericsSacredChime",
    ):
        return "ArmorDrop"
    if "Ring" in kind or "ring" in kind.lower():
        return "RingDrop"
    if "Set" in kind or "Armor" in kind or kind in (
        "Loincloth", "ClericSet", "NorthernSet", "MirrahSet",
        "FireKeeperSet", "MastersAttire", "MastersGloves",
    ):
        return "ArmorDrop"
    return "Consumable"

def map_npc_kind(npc):
    kind = npc.get("kind", "Dialogue")
    return {"LevelUp": "LevelUp", "Merchant": "Merchant", "Blacksmith": "Blacksmith",
            "Trade": "Merchant", "Summon": "Summon", "Hostile": "Hostile",
            "Invader": "Invader", "Covenant": "Dialogue"}.get(kind, "Dialogue")

def map_chest_kind(loot):
    kind = loot.get("kind", "")
    if kind in ("EstusShard", "TitaniteShard", "UndeadBoneShard", "Ember",
                "HomewardBone", "Consumable", "Firebomb", "PurpleMoss"):
        return kind
    if "Weapon" in kind: return "WeaponDrop"
    if "Armor" in kind: return "ArmorDrop"
    if "Ring" in kind: return "RingDrop"
    if "Shield" in kind: return "ArmorDrop"
    if "Key" in kind: return "Consumable"
    if "Item" in kind: return "Consumable"
    return "SoulOrb"

# --- Main map generation ---

def create_entities_from_doc(chunk, doc):
    """Create all entities (enemies, NPCs, items, etc.) from a JSON design doc,
    snap them to walkable terrain in the given chunk, and return the entity list."""
    entities = []

    def add_entity(identifier, x, y, fields=None):
        entity = make_entity(identifier, x, y, fields)
        snap_entity_to_walkable(chunk, entity)
        entities.append(entity)
        return entity

    bonfires = doc.get("bonfires", [])
    if bonfires:
        first = bonfires[0]
        # Ensure spawn position has walkable ground
        sx, sy = first["x"] // TILE_SIZE, first["y"] // TILE_SIZE
        fill_tiles(chunk, TILE_GROUND, sx - 3, sy - 3, sx + 3, sy + 3)
        add_entity("PlayerSpawn", first["x"], first["y"], [make_field("heal", "Bool", True)])
        for bonfire in bonfires[1:]:
            bx, by = bonfire["x"] // TILE_SIZE, bonfire["y"] // TILE_SIZE
            fill_tiles(chunk, TILE_GROUND, bx - 2, by - 2, bx + 2, by + 2)
            add_entity("Bonfire", bonfire["x"], bonfire["y"])
    else:
        sections = doc.get("map_layout", {}).get("sections", [])
        if sections:
            first = sections[0]
            px = first["x"] + first["w"] * 0.5
            py = first["y"] + first["h"] * 0.5
        else:
            px = doc["map_size"]["width"] * 0.5
            py = doc["map_size"]["height"] * 0.5
        add_entity("PlayerSpawn", px, py, [make_field("heal", "Bool", True)])

    boss = doc.get("boss")
    bosses = boss if isinstance(boss, list) else ([boss] if boss else [])
    for boss_def in bosses:
        if not isinstance(boss_def, dict):
            continue
        bx, by = boss_def.get("x", 0) // TILE_SIZE, boss_def.get("y", 0) // TILE_SIZE
        fill_tiles(chunk, TILE_GROUND, bx - 5, by - 5, bx + 5, by + 5)
        add_entity("BossSpawn", boss_def.get("x", 0), boss_def.get("y", 0))

    for enemy in doc.get("enemies", []):
        kind = ENEMY_KIND_MAP.get(enemy.get("kind", ""), enemy.get("kind", "HollowSoldier"))
        count = max(1, int(enemy.get("count", 1)))
        for i in range(count):
            add_entity("Enemy", enemy["x"] + i * 32, enemy["y"], [
                make_field("kind", "LocalEnum.EnemyKind", kind)
            ])

    for item in doc.get("items", []):
        kind = map_item_kind(item)
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb" and "value" in item:
            fields.append(make_field("value", "Int", item["value"]))
        if item.get("name_en") or item.get("name"):
            fields.append(make_field("name", "String", item.get("name_en", item.get("name", ""))))
        add_entity("Item", item["x"], item["y"], fields)

    for chest in doc.get("chests", []):
        loot = chest.get("loot", {})
        add_entity("Chest", chest["x"], chest["y"], [
            make_field("loot_kind", "LocalEnum.ItemKind", map_chest_kind(loot)),
            make_field("loot_value", "Int", loot.get("value", 0)),
            make_field("loot_name", "String", loot.get("name_en", loot.get("name", ""))),
            make_field("is_mimic", "Bool", chest.get("is_mimic", False)),
        ])

    for npc in doc.get("npcs", []):
        if "x" not in npc or "y" not in npc:
            continue
        add_entity("Npc", npc["x"], npc["y"], [
            make_field("name", "String", npc.get("name_en", npc.get("name", ""))),
            make_field("kind", "LocalEnum.NpcKind", map_npc_kind(npc)),
            make_field("color", "Color", npc.get("color", "#FFFFFF")),
            make_field("dialogue", "String", "|".join(npc.get("dialogue", []))),
        ])

    for light in doc.get("lights", []):
        add_entity("Light", light["x"], light["y"], [
            make_field("radius", "Float", light.get("radius", 160)),
            make_field("r", "Float", light.get("r", 1.0)),
            make_field("g", "Float", light.get("g", 1.0)),
            make_field("b", "Float", light.get("b", 1.0)),
            make_field("intensity", "Float", light.get("intensity", 0.2)),
        ])

    area_aliases = {"FirelinkShrine": "CemeteryOfAsh", "IrithyllOfTheBorealValley": "Irithyll"}
    for gate in doc.get("fog_gates", []):
        dest_area = area_aliases.get(gate.get("dest_area", ""), gate.get("dest_area", ""))
        if dest_area not in LEVEL_UIDS:
            continue
        add_entity("FogGate", gate.get("x", 0), gate.get("y", 0), [
            make_field("dest_area", "String", dest_area),
            make_field("dest_x", "Float", gate.get("dest_x", 0)),
            make_field("dest_y", "Float", gate.get("dest_y", 0)),
            make_field("width", "Float", max(TILE_SIZE, gate.get("w", 64))),
            make_field("height", "Float", max(TILE_SIZE, gate.get("h", 64))),
        ])

    snap_entities_to_walkable(chunk, entities)
    populate_entity_def_uids(entities)
    return entities

def generate_map_from_doc(doc_path):
    with open(doc_path, encoding="utf-8") as f:
        doc = json.load(f)

    map_id = map_id_from_doc(doc)
    if map_id not in LEVEL_UIDS:
        print(f"  SKIP {map_id} (not in LEVEL_UIDS)")
        return None

    chunk = generate_official_terrain(doc)
    entities = create_entities_from_doc(chunk, doc)

    ground_count = sum(1 for row in chunk for tile in row if tile in (TILE_GROUND, TILE_POISON))
    total = max(1, chunk_width(chunk) * chunk_height(chunk))
    pct = ground_count / total * 100
    print(f"  {map_id:30s} sections={len(doc.get('map_layout', {}).get('sections', [])):2d} "
          f"entities={len(entities):4d} ground={pct:5.1f}%")
    return map_id, chunk, entities

def make_level(identifier, chunk, entities, uid):
    fix_terrain_connectivity(chunk)
    width = chunk_width(chunk)
    height = chunk_height(chunk)
    return {
        "__header__": {
            "fileType": "LDtk Project JSON", "app": "LDtk",
            "doc": "https://ldtk.io/json",
            "schema": "https://ldtk.io/files/JSON_SCHEMA.json",
            "appAuthor": "Sebastien 'deepnight' Benard",
            "appVersion": "1.5.3", "url": "https://ldtk.io",
        },
        "__bgColor": "#696A79",
        "__neighbours": [],
        "__smartColor": "#696A79",
        "__bgPos": None,
        "bgColor": "#000000",
        "bgPivotX": 0.5, "bgPivotY": 0.5,
        "bgPos": None, "bgRelPath": None,
        "externalRelPath": None,
        "fieldInstances": [],
        "identifier": identifier,
        "iid": str(uuid.uuid4()),
        "layerInstances": [
            {
                "__cHei": height, "__cWid": width, "__gridSize": 16,
                "__identifier": "Terrain", "__opacity": 1,
                "__pxTotalOffsetX": 0, "__pxTotalOffsetY": 0,
                "__seed": 123456,
                "__tilesetDefUid": None, "__tilesetRelPath": None,
                "__type": "IntGrid",
                "autoLayerTiles": [], "entityInstances": [],
                "gridTiles": [], "iid": str(uuid.uuid4()),
                "intGridCsv": chunk_to_csv(chunk),
                "layerDefUid": 1, "levelId": uid,
                "optionalRules": [], "overrideTilesetUid": None,
                "pxOffsetX": 0, "pxOffsetY": 0,
                "seed": 0, "visible": True,
            },
            {
                "__cHei": height, "__cWid": width, "__gridSize": 16,
                "__identifier": "Entities", "__opacity": 1,
                "__pxTotalOffsetX": 0, "__pxTotalOffsetY": 0,
                "__seed": 123456,
                "__tilesetDefUid": None, "__tilesetRelPath": None,
                "__type": "Entities",
                "autoLayerTiles": [], "entityInstances": entities,
                "gridTiles": [], "iid": str(uuid.uuid4()),
                "intGridCsv": [],
                "layerDefUid": 2, "levelId": uid,
                "optionalRules": [], "overrideTilesetUid": None,
                "pxOffsetX": 0, "pxOffsetY": 0,
                "seed": 0, "visible": True,
            },
        ],
        "pxHei": height * 16,
        "pxWid": width * 16,
        "uid": uid,
        "useAutoIdentifier": True,
        "worldDepth": 0, "worldX": 0, "worldY": 0,
    }

def build_enum_defs():
    return [
        {"externalFileChecksum": None, "externalRelPath": None, "iconTilesetUid": None,
         "identifier": "EnemyKind", "tags": [], "uid": ENUM_UIDS["EnemyKind"],
         "values": [{"__tileSrcRect": None, "color": c, "id": eid, "tileId": None, "tileRect": None}
                    for eid, c in [
             ("HollowSoldier", 0xB08D57), ("Archer", 0x8C6239), ("Knight", 0x7F8C8D),
             ("MiniBoss", 0xC0392B), ("Assassin", 0x34495E), ("DarkMage", 0x6C3483),
             ("CrystalLizard", 0x48C9B0), ("SilverKnight", 0xC0C0C0), ("BlackKnight", 0x333333),
             ("DeepAccursed", 0x4A235A), ("Evangelist", 0x8B7355), ("Thrall", 0x566573),
             ("LothricKnight", 0x5D6D7E), ("WingedKnight", 0x4A5568), ("Ghru", 0x6B4226),
             ("Darkwraith", 0x1C2833), ("Skeleton", 0xD5D8DC), ("Jailer", 0x616A6B),
             ("SerpentMan", 0x7D6608), ("Deacon", 0x5B2C6F), ("FireDemon", 0xC0392B),
             ("StarvedHound", 0x7B7D7D), ("PusOfMan", 0x1B2631), ("CathedralKnight", 0x4A5568),
             ("ManGrub", 0x873624), ("Gargoyle", 0x6E7B8B), ("Dog", 0x8B7765),
             ("Basilisk", 0x2ECC71), ("DemonStatue", 0x839192), ("InfestedCorpse", 0x6B5B4E),
             ("Wretch", 0x5D5347), ("PeasantHollow", 0x8B7765), ("Mimic", 0xD4AC0D),
             ("GiantSlave", 0x7F6B52), ("HollowAssassin", 0x4A4A55), ("CathedralGraveWarden", 0x3D4A3D),
             ("Rat", 0x7B6B55), ("LargeHollowSoldier", 0x8B7355),
         ]]},
        {"externalFileChecksum": None, "externalRelPath": None, "iconTilesetUid": None,
         "identifier": "ItemKind", "tags": [], "uid": ENUM_UIDS["ItemKind"],
         "values": [{"__tileSrcRect": None, "color": c, "id": eid, "tileId": None, "tileRect": None}
                    for eid, c in [
             ("SoulOrb", 0xF4D03F), ("EstusShard", 0xE67E22), ("HomewardBone", 0xD7DBDD),
             ("PurpleMoss", 0x27AE60), ("WeaponDrop", 0x95A5A6), ("ArmorDrop", 0x5D6D7E),
             ("RingDrop", 0xF1C40F), ("Firebomb", 0xE74C3C), ("Ember", 0xF39C12),
             ("UndeadBoneShard", 0xE8D5B7), ("TitaniteShard", 0x85929E), ("Consumable", 0xBDC3C7),
         ]]},
        {"externalFileChecksum": None, "externalRelPath": None, "iconTilesetUid": None,
         "identifier": "NpcKind", "tags": [], "uid": ENUM_UIDS["NpcKind"],
         "values": [{"__tileSrcRect": None, "color": c, "id": eid, "tileId": None, "tileRect": None}
                    for eid, c in [
             ("LevelUp", 0x2ECC71), ("Merchant", 0xF1C40F), ("Blacksmith", 0xD35400), ("Dialogue", 0x5DADE2),
         ]]},
        {"externalFileChecksum": None, "externalRelPath": None, "iconTilesetUid": None,
         "identifier": "TileKind", "tags": [], "uid": ENUM_UIDS["TileKind"],
         "values": [{"__tileSrcRect": None, "color": c, "id": eid, "tileId": None, "tileRect": None}
                    for eid, c in [
             ("Empty", 0x000000), ("Ground", 0x4A3728), ("Wall", 0x1A1A2E),
             ("WallTop", 0x16213E), ("Poison", 0x2D6A4F),
         ]]},
    ]

def _load_doc_for_area(docs_dir, map_id):
    """Find and load the JSON design doc for a given map_id."""
    aliases = {}  # doc filenames match map_id names directly
    doc_name = aliases.get(map_id, map_id)
    doc_path = os.path.join(docs_dir, f"{doc_name}.json")
    if os.path.exists(doc_path):
        with open(doc_path, encoding="utf-8") as f:
            return json.load(f)
    return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(os.path.dirname(script_dir), "docs", "maps")
    levels_dir = os.path.join(script_dir, "ds2d")
    os.makedirs(levels_dir, exist_ok=True)

    level_summaries = []

    # First pass: generate maps with hand-authored terrain overrides.
    # Terrain comes from override functions; entity data comes from JSON docs.
    for map_id, override_fn in sorted(TERRAIN_OVERRIDES.items()):
        result = override_fn()
        if result is None:
            continue
        mid, chunk, _override_entities = result

        # Replace hardcoded entities with JSON doc entities
        doc = _load_doc_for_area(docs_dir, mid)
        if doc:
            entities = create_entities_from_doc(chunk, doc)
        else:
            entities = _override_entities

        uid = LEVEL_UIDS[mid]
        level = make_level(mid, chunk, entities, uid)
        level_path = os.path.join(levels_dir, f"{mid}.ldtkl")
        with open(level_path, "w") as f:
            json.dump(level, f, indent=2)

        ground_count = sum(1 for row in chunk for tile in row if tile in (TILE_GROUND, TILE_POISON))
        total = max(1, chunk_width(chunk) * chunk_height(chunk))
        pct = ground_count / total * 100
        label = f"{mid} (faithful DS3 layout)" if doc else f"{mid} (override, no doc)"
        print(f"  {label} ground={pct:.1f}% entities={len(entities)}")
        level_summaries.append({
            "__bgColor": level["__bgColor"],
            "__neighbours": [], "__smartColor": level["__smartColor"],
            "__bgPos": None, "bgColor": None,
            "bgPivotX": 0.5, "bgPivotY": 0.5,
            "bgPos": None, "bgRelPath": None,
            "externalRelPath": f"ds2d/{mid}.ldtkl",
            "fieldInstances": [], "identifier": mid,
            "iid": level["iid"], "layerInstances": None,
            "pxHei": level["pxHei"], "pxWid": level["pxWid"],
            "uid": uid, "useAutoIdentifier": True,
            "worldDepth": 0, "worldX": -1, "worldY": -1,
        })

    # Second pass: generate remaining maps from design docs (no terrain override)
    override_ids = set(TERRAIN_OVERRIDES.keys())
    for doc_file in sorted(os.listdir(docs_dir)):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(docs_dir, doc_file)
        with open(doc_path, encoding="utf-8") as f:
            doc = json.load(f)
        map_id = doc.get("id", "")
        map_id = {"IrithyllOfTheBorealValley": "Irithyll"}.get(map_id, map_id)
        if map_id in override_ids:
            continue
        if map_id not in LEVEL_UIDS:
            print(f"  SKIP {map_id} (not in LEVEL_UIDS)")
            continue
        result = generate_map_from_doc(doc_path)
        if result is None:
            continue
        mid, chunk, entities = result
        uid = LEVEL_UIDS[mid]
        level = make_level(mid, chunk, entities, uid)
        level_path = os.path.join(levels_dir, f"{mid}.ldtkl")
        with open(level_path, "w") as f:
            json.dump(level, f, indent=2)
        print(f"  wrote {level_path}")
        level_summaries.append({
            "__bgColor": level["__bgColor"],
            "__neighbours": [], "__smartColor": level["__smartColor"],
            "__bgPos": None, "bgColor": None,
            "bgPivotX": 0.5, "bgPivotY": 0.5,
            "bgPos": None, "bgRelPath": None,
            "externalRelPath": f"ds2d/{mid}.ldtkl",
            "fieldInstances": [], "identifier": mid,
            "iid": level["iid"], "layerInstances": None,
            "pxHei": level["pxHei"], "pxWid": level["pxWid"],
            "uid": uid, "useAutoIdentifier": True,
            "worldDepth": 0, "worldX": -1, "worldY": -1,
        })

    # Generate project file
    project = {
        "__header__": {
            "fileType": "LDtk Project JSON", "app": "LDtk",
            "doc": "https://ldtk.io/json",
            "schema": "https://ldtk.io/files/JSON_SCHEMA.json",
            "appAuthor": "Sebastien 'deepnight' Benard",
            "appVersion": "1.5.3", "url": "https://ldtk.io",
        },
        "__FORCED_REFS": None,
        "appBuildId": 473703, "backupLimit": 10, "backupOnSave": False, "backupRelPath": None,
        "bgColor": "#1a1a2e", "customCommands": [],
        "defaultEntityHeight": 16, "defaultEntityWidth": 16, "defaultGridSize": 16,
        "defaultLevelBgColor": "#1a1a2e",
        "defaultLevelHeight": BASE_MAP_PX, "defaultLevelWidth": BASE_MAP_PX,
        "defaultPivotX": 0, "defaultPivotY": 0,
        "defs": {
            "entities": [
                {"allowOutOfBounds": False, "color": "#7FDBFF", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "PlayerSpawn", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["PlayerSpawn"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#FF4136", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "BossSpawn", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["BossSpawn"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#FF851B", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "Bonfire", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["Bonfire"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#B08D57", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "Enemy", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["Enemy"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#F4D03F", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "Item", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["Item"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#8E6E53", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "Chest", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["Chest"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#33E6B3", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "Npc", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["Npc"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#FFF3B0", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "Light", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["Light"], "uiTileRect": None, "width": 16},
                {"allowOutOfBounds": False, "color": "#D4AF37", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 32, "hollow": False,
                 "identifier": "FogGate", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": True, "resizableY": True, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["FogGate"], "uiTileRect": None, "width": 64},
                {"allowOutOfBounds": False, "color": "#2ECC71", "doc": None, "exportToToc": False,
                 "fieldDefs": [], "fillOpacity": 0.8, "height": 16, "hollow": False,
                 "identifier": "TilePatch", "keepAspectRatio": False,
                 "limitBehavior": "MoveLastOne", "limitScope": "PerLevel",
                 "lineOpacity": 1.0, "maxCount": 0, "maxHeight": None, "maxWidth": None,
                 "minHeight": None, "minWidth": None, "nineSliceBorders": [],
                 "pivotX": 0.5, "pivotY": 1.0, "renderMode": "Rectangle",
                 "resizableX": False, "resizableY": False, "showName": True,
                 "tags": [], "tileId": None, "tileOpacity": 1.0, "tileRect": None,
                 "tileRenderMode": "Stretch", "tilesetId": None,
                 "uid": ENTITY_UIDS["TilePatch"], "uiTileRect": None, "width": 16},
            ],
            "enums": build_enum_defs(),
            "externalEnums": [],
            "layers": [
                {"__type": "IntGrid", "autoRuleGroups": [], "autoSourceLayerDefUid": None,
                 "autoTilesetDefUid": None, "autoTilesKilledByOtherLayerUid": None,
                 "biomeFieldUid": None, "canSelectWhenInactive": True, "displayOpacity": 1.0,
                 "doc": None, "excludedTags": [], "gridSize": 16,
                 "guideGridHei": 0, "guideGridWid": 0,
                 "hideFieldsWhenInactive": False, "hideInList": False,
                 "identifier": "Terrain", "inactiveOpacity": 0.3,
                 "intGridValues": [
                     {"color": "#000000", "groupUid": 0, "identifier": "Empty", "tile": None, "value": 0},
                     {"color": "#4a3728", "groupUid": 0, "identifier": "Ground", "tile": None, "value": 1},
                     {"color": "#1a1a2e", "groupUid": 0, "identifier": "Wall", "tile": None, "value": 2},
                     {"color": "#16213e", "groupUid": 0, "identifier": "WallTop", "tile": None, "value": 3},
                     {"color": "#2d6a4f", "groupUid": 0, "identifier": "Poison", "tile": None, "value": 4},
                 ],
                 "intGridValuesGroups": [], "parallaxFactorX": 0, "parallaxFactorY": 0,
                 "parallaxScaling": True, "pxOffsetX": 0, "pxOffsetY": 0,
                 "renderInWorldView": True, "requiredTags": [],
                 "tilePivotX": 0, "tilePivotY": 0, "tilesetDefUid": None,
                 "type": "IntGrid", "uiColor": None, "uid": 1,
                 "uiFilterTags": [], "useAsyncRender": False},
                {"__type": "Entities", "autoRuleGroups": [], "autoSourceLayerDefUid": None,
                 "autoTilesetDefUid": None, "autoTilesKilledByOtherLayerUid": None,
                 "biomeFieldUid": None, "canSelectWhenInactive": True, "displayOpacity": 1.0,
                 "doc": None, "excludedTags": [], "gridSize": 16,
                 "guideGridHei": 0, "guideGridWid": 0,
                 "hideFieldsWhenInactive": False, "hideInList": False,
                 "identifier": "Entities", "inactiveOpacity": 0.3,
                 "intGridValues": [], "intGridValuesGroups": [],
                 "parallaxFactorX": 0, "parallaxFactorY": 0,
                 "parallaxScaling": True, "pxOffsetX": 0, "pxOffsetY": 0,
                 "renderInWorldView": True, "requiredTags": [],
                 "tilePivotX": 0, "tilePivotY": 0, "tilesetDefUid": None,
                 "type": "Entities", "uiColor": None, "uid": 2,
                 "uiFilterTags": [], "useAsyncRender": False},
            ],
            "levelFields": [], "tilesets": [],
        },
        "dummyWorldIid": str(uuid.uuid4()),
        "exportLevelBg": False, "exportPng": None, "exportTiled": False,
        "externalLevels": True, "flags": [], "identifierStyle": "Free",
        "iid": str(uuid.uuid4()),
        "imageExportMode": "None", "jsonVersion": "1.5.3",
        "levelNamePattern": "%world_Level_%idx",
        "levels": level_summaries,
        "minifyJson": False, "nextUid": 1000, "pngFilePattern": None,
        "simplifiedExport": False, "toc": [],
        "tutorialDesc": "Generated DS2D project from design docs.",
        "worldGridHeight": BASE_MAP_PX, "worldGridWidth": BASE_MAP_PX,
        "worldLayout": "Free", "worlds": [],
    }

    project_path = os.path.join(script_dir, "ds2d.ldtk")
    with open(project_path, "w") as f:
        json.dump(project, f, indent=2)
    print(f"  wrote {project_path}")

if __name__ == "__main__":
    main()
