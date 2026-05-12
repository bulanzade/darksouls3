#!/usr/bin/env python3
"""Generate LDtk .ldtkl level files from design docs in docs/maps/."""
import json
import os
import uuid
from collections import deque

CHUNK_SIZE = 160
TILE_SIZE = 16
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_WALL = 2
TILE_WALLTOP = 3
TILE_POISON = 4

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
    "InfestedCorpse": "InfestedCorpse", "Wretch": "Wretch", "PeasantHollow": "PeasantHollow",
    "Mimic": "Mimic", "GiantSlave": "GiantSlave", "HollowAssassin": "HollowAssassin",
    "CathedralGraveWarden": "CathedralGraveWarden", "Rat": "Rat", "MiniBoss": "MiniBoss",
    # Aliases for design-doc enemy kinds not in Rust enum
    "SwordMaster": "Assassin",
    "BorealKnight": "Knight",
    "LargeHollowSoldier": "Knight",
    "LothricWyvern": "MiniBoss",
    "Hodrick": "MiniBoss",
    "CagedHollow": "PeasantHollow",
    "Ghrul": "Ghru",
    "DarkSpirit": "Knight",
    "Berengaria": "DarkMage",
    "SkeletonSwordman": "Skeleton",
    "SkeletonBall": "Skeleton",
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
    "ConsumedKingKnight": "CathedralKnight",
    "Hollow": "HollowSoldier",
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


def find_walkable_tile(chunk, tx, ty, max_radius=64):
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
        tile = TILE_POISON if any(word in features for word in ("毒", "沼", "污水", "浅水")) else TILE_GROUND
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
    if not (0 <= sx < CHUNK_SIZE and 0 <= sy < CHUNK_SIZE):
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
            if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx, ny) not in visited:
                if chunk[ny][nx] in (TILE_GROUND, TILE_POISON):
                    visited.add((nx, ny))
                    q.append((nx, ny))
    return visited


def carve_corridor(chunk, x1, y1, x2, y2, width=3):
    """Carve an L-shaped corridor between two tile positions."""
    half = width // 2
    # Horizontal then vertical
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for dy in range(-half, half + 1):
            ny = y1 + dy
            if 0 <= x < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE:
                chunk[ny][x] = TILE_GROUND
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for dx in range(-half, half + 1):
            nx = x2 + dx
            if 0 <= nx < CHUNK_SIZE and 0 <= y < CHUNK_SIZE:
                chunk[y][nx] = TILE_GROUND


def ensure_connected(chunk, spawn_px, spawn_py, entity_positions):
    """Ensure all entity tile positions are reachable from spawn. Returns coverage %."""
    sx, sy = int(spawn_px) // TILE_SIZE, int(spawn_py) // TILE_SIZE
    # Make sure spawn is on ground
    cw(chunk, spawn_px, spawn_py, 2)

    targets = set()
    for px, py in entity_positions:
        tx, ty = int(px) // TILE_SIZE, int(py) // TILE_SIZE
        if 0 <= tx < CHUNK_SIZE and 0 <= ty < CHUNK_SIZE:
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


# --- Hand-designed terrain overrides (faithful to real DS3) ---

def make_cemetery_of_ash():
    """Cemetery of Ash + Firelink Shrine — combined into one map.

    Faithful DS3 layout: the path winds from the southwest coffin eastward
    through the cemetery, then curves northeast and north, with real branching
    detours matching the actual game's spatial progression:

    1. Coffin wake-up at SW corner → narrow path east
    2. First hollow encounter + side pocket (Soul of Deserted Corpse)
    3. NE curve through ash estus clearing (broken fountain)
    4. Stairs junction (parry/backstab tutorial) with side dead-end
    5. Broken arch passage (crossbow hollow, pair of hollows)
    6. Major fork: east → Crystal Lizard water chasm (long detour)
    7. Cemetery of Ash bonfire clearing (dead tree)
    8. Fork: west → firebomb cliff path (shield grunt, crossbow)
    9. Twin-torch approach to Gundyr arena
    10. Iudex Gundyr boss arena (large oval)
    11. Exit north to Firelink Shrine (door opens post-boss)
    12. Firelink Shrine hub (Andre west, Handmaiden east, Fire Keeper)

    Arena exit at tiles (77-83, 29-30) matches combat.rs fill_tiles.
    """
    chunk = new_chunk()

    # ================================================================
    # 1. COFFIN START (SW corner, x=19-31, y=148-156)
    # Small stone coffin alcove — player wakes here
    # ================================================================
    carve_ellipse(chunk, 25, 152, 6, 4)

    # ================================================================
    # 2. FIRST PATH — narrow east corridor (x=28-54, y=150-154)
    # 3-tile wide path through ash-covered ground
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 28, 150, 54, 154)

    # ================================================================
    # 3. FIRST ENCOUNTER (x=52-66, y=148-154)
    # Widens — pair of crouching Hollow Assassins ambush from graves
    # In DS3: first hollow lies in the path, springs up
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 52, 148, 66, 154)
    # Gravestone obstacles flanking the path
    fill_tiles(chunk, TILE_WALL, 54, 150, 55, 151)
    fill_tiles(chunk, TILE_WALL, 62, 150, 63, 151)

    # ================================================================
    # 4. SIDE POCKET — Soul of Deserted Corpse (x=58-68, y=154-158)
    # Small dead-end south of first encounter — body with soul item
    # In DS3: branch right leads to a body with Soul of a Deserted Corpse
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 58, 154, 66, 158)
    carve_ellipse(chunk, 62, 158, 4, 2)

    # ================================================================
    # 5. NE CURVE — path turns northeast (x=64-78, y=132-150)
    # The path bends from east-heading to north-heading (L-shape)
    # In DS3: the path curves around the mountain toward the fountain
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 64, 140, 78, 150)  # east-west leg
    fill_tiles(chunk, TILE_GROUND, 72, 132, 78, 150)  # north-south leg

    # ================================================================
    # 6. ASHEN ESTUS CLEARING (x=70-86, y=130-140)
    # Wider clearing — broken fountain pillar in center
    # In DS3: Ashen Estus Flask found at a broken stone fountain
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 70, 130, 86, 140)
    # Broken fountain ruin (wall obstacle)
    fill_tiles(chunk, TILE_WALL, 77, 134, 79, 136)

    # ================================================================
    # 7. STAIRS JUNCTION (x=74-90, y=120-132)
    # Wider area — small stairs east (dead-end), main path continues north
    # In DS3: small stairs to the right, longer stairs to the left
    # Parry and backstab tutorial enemies
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 74, 120, 90, 132)
    # Side stairs dead-end (east) — hollow ambush
    fill_tiles(chunk, TILE_GROUND, 86, 126, 96, 130)
    carve_ellipse(chunk, 98, 128, 5, 3)
    # Gravestone walls on the stairs
    fill_tiles(chunk, TILE_WALL, 78, 124, 79, 125)
    fill_tiles(chunk, TILE_WALL, 84, 124, 85, 125)

    # ================================================================
    # 8. BROKEN ARCH (x=72-82, y=112-120)
    # Narrow 5-tile passage — crossbow hollow under the arch
    # In DS3: crossbow hollow fires from under a broken stone arch,
    # then a pair of hollows appear past it (two-hand tutorial)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 72, 112, 82, 120)
    # Arch walls narrowing the passage
    fill_tiles(chunk, TILE_WALL, 72, 114, 73, 116)
    fill_tiles(chunk, TILE_WALL, 81, 114, 82, 116)

    # ================================================================
    # 9. MAJOR FORK AREA (x=66-86, y=100-112)
    # Path splits: main continues north, Crystal Lizard branch goes east
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 66, 100, 86, 112)

    # ================================================================
    # 10. CRYSTAL LIZARD WATER PATH (x=84-138, y=107-111)
    # Narrow waist-deep water channel — DS3 research confirms this is a
    # narrow canal carved between rock walls, with stagnant water
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 84, 108, 128, 110)  # narrow 3-tile corridor
    carve_ellipse(chunk, 136, 108, 8, 6)  # chasm end pocket
    fill_tiles(chunk, TILE_GROUND, 128, 104, 136, 112)  # connect to pocket
    # Poison pools (waist-deep stagnant water throughout the chasm)
    fill_tiles(chunk, TILE_POISON, 92, 108, 102, 110)
    fill_tiles(chunk, TILE_POISON, 110, 108, 120, 110)
    fill_tiles(chunk, TILE_POISON, 128, 106, 132, 110)
    # Rocky outcrops flanking the narrow channel
    fill_tiles(chunk, TILE_WALL, 96, 107, 97, 108)
    fill_tiles(chunk, TILE_WALL, 106, 109, 107, 110)
    fill_tiles(chunk, TILE_WALL, 116, 107, 117, 108)

    # ================================================================
    # 11. CEMETERY OF ASH BONFIRE CLEARING (x=60-84, y=89-101)
    # Open clearing — dead tree, first bonfire
    # In DS3: bonfire beside a dead tree, roughly midway through the area
    # ================================================================
    carve_ellipse(chunk, 72, 95, 12, 6)
    fill_tiles(chunk, TILE_GROUND, 66, 98, 78, 100)  # connect to fork above

    # ================================================================
    # 12. POST-BONFIRE FORK (x=56-82, y=78-92)
    # Path splits: west → firebomb cliff, north → Gundyr approach
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 56, 82, 82, 92)

    # ================================================================
    # 13. FIREBOMB CLIFF PATH (x=34-58, y=82-92)
    # Narrow cliff-side path — winds west then turns south
    # In DS3: cliff path with tomb jump, shield grunt, crossbow → 5 firebombs
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 34, 82, 58, 88)  # narrow corridor west
    fill_tiles(chunk, TILE_GROUND, 34, 84, 42, 92)  # L-turn south at end
    carve_ellipse(chunk, 38, 88, 5, 3)  # end pocket with firebombs
    # Cliff edge walls (create narrow corridor feeling)
    fill_tiles(chunk, TILE_WALL, 46, 80, 47, 81)
    fill_tiles(chunk, TILE_WALL, 40, 80, 41, 81)

    # ================================================================
    # 14. GUNDYR APPROACH (x=68-82, y=66-80)
    # Wider approach that narrows at twin-torch arch
    # In DS3: stone archway with torches on both sides
    # Gravestones along the cliffside approach
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 68, 66, 82, 80)
    # Twin-torch narrowing
    fill_tiles(chunk, TILE_WALL, 68, 74, 69, 76)
    fill_tiles(chunk, TILE_WALL, 81, 74, 82, 76)
    # Gravestones along the approach path
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 71)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 72, 78, 73, 79)
    fill_tiles(chunk, TILE_WALL, 79, 68, 80, 69)

    # ================================================================
    # 15. IUDEX GUNDYR BOSS ARENA (x=52-108, y=30-66)
    # Large oval arena — DS3 research confirms: reflecting pool at center,
    # crumbling low walls and gravestone clusters around perimeter,
    # cliff drop-off on portions of the circumference.
    # Player enters from south, boss spawns at center
    # ================================================================
    carve_ellipse(chunk, 80, 48, 28, 18)
    # Reflecting pool at center (shallow water — POISON tiles)
    fill_tiles(chunk, TILE_POISON, 76, 44, 84, 52)
    # Arena perimeter — crumbling wall sections and gravestone clusters
    fill_tiles(chunk, TILE_WALL, 56, 38, 58, 40)   # NW crumbling wall
    fill_tiles(chunk, TILE_WALL, 100, 38, 102, 40)  # NE crumbling wall
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)    # SW gravestone cluster
    fill_tiles(chunk, TILE_WALL, 102, 55, 104, 57)   # SE gravestone cluster
    fill_tiles(chunk, TILE_WALL, 68, 32, 70, 34)     # N gravestones
    fill_tiles(chunk, TILE_WALL, 90, 32, 92, 34)     # N gravestones
    fill_tiles(chunk, TILE_WALL, 62, 58, 64, 60)     # S tombstones
    fill_tiles(chunk, TILE_WALL, 95, 58, 97, 60)     # S tombstones

    # ================================================================
    # 16. ARENA EXIT CORRIDOR (x=76-84, y=22-34)
    # Blocked by Gundyr door (wall tiles 77-83, 29-30)
    # Opens when boss is defeated (combat.rs)
    # Leads to FirelinkShrine (separate area)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 78, 22, 82, 34)

    # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    # --- Player Spawn — coffin at SW corner ---
    spawn_px, spawn_py = 25 * 16, 152 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    # Cemetery of Ash bonfire — dead tree clearing (midpoint)
    entities.append(make_entity("Bonfire", 72 * 16, 95 * 16))
    # Iudex Gundyr bonfire — arena entrance
    entities.append(make_entity("Bonfire", 80 * 16, 66 * 16))

    # --- Boss — Iudex Gundyr at arena center ---
    entities.append(make_entity("BossSpawn", 80 * 16, 48 * 16))

    # --- Enemies (DS3 Cemetery of Ash: Hollow Soldiers with swords/shields/bows) ---
    # In DS3 the cemetery enemies are hollow soldiers that rise from the ground.
    # DS3 enemies: Grave Wardens (sword, shield, crossbow variants) + 1 Ravenous Crystal Lizard.
    # Layout follows the actual route: coffin → cemetery path → fountain → stairs → bonfire →
    # firebomb cliff → Gundyr approach → arena.

    # Section 1: Coffin wake-up area — first Grave Warden (sword+shield, stands up)
    entities.append(make_entity("Enemy", 40 * 16, 152 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 2: Cemetery path — pair of Grave Wardens (sword+shield)
    entities.append(make_entity("Enemy", 56 * 16, 152 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    entities.append(make_entity("Enemy", 64 * 16, 150 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 3: Ashen Estus fountain — Grave Warden facing away (sword)
    entities.append(make_entity("Enemy", 80 * 16, 136 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 4: Stairs junction — Grave Warden (sword+shield) on stairs
    entities.append(make_entity("Enemy", 76 * 16, 126 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 5: Broken arch — Grave Warden crossbow (ranged)
    entities.append(make_entity("Enemy", 78 * 16, 116 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 6: Major fork — two Grave Wardens (sword+shield) guarding path
    entities.append(make_entity("Enemy", 86 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    entities.append(make_entity("Enemy", 92 * 16, 109 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 7: Cemetery of Ash bonfire clearing — Grave Warden near dead tree
    entities.append(make_entity("Enemy", 68 * 16, 92 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 8: Firebomb cliff — Grave Warden sword+shield
    entities.append(make_entity("Enemy", 50 * 16, 86 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Drop-down Grave Warden near firebomb cliff (drops Cleric's Sacred Chime)
    entities.append(make_entity("Enemy", 44 * 16, 90 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Grave Warden at cliff end
    entities.append(make_entity("Enemy", 38 * 16, 86 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    entities.append(make_entity("Enemy", 40 * 16, 84 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Section 9: Twin-torch approach — Grave Warden crossbow before arena
    entities.append(make_entity("Enemy", 76 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "GraveWarden")]))
    # Ravenous Crystal Lizard — side path near water chasm (optional area)
    entities.append(make_entity("Enemy", 136 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "RavenousCrystalLizard")]))

    # --- Items (accurate DS3 placements) ---
    # Ashen Estus Flask — corpse by broken fountain
    entities.append(make_entity("Item", 82 * 16, 134 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Ashen Estus Flask")]))
    # Soul of a Deserted Corpse — right branch after first enemy
    entities.append(make_entity("Item", 62 * 16, 157 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("value", "Int", 200),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    # Firebomb x5 — cliff end, behind sword+shield and crossbow hollows
    entities.append(make_entity("Item", 38 * 16, 88 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    # Titanite Shard — small ravine jump, cliff side
    entities.append(make_entity("Item", 42 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Soul of an Unknown Traveler — water chasm wider area
    entities.append(make_entity("Item", 118 * 16, 109 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("value", "Int", 400),
        make_field("name", "String", "Soul of an Unknown Traveler")]))
    # Titanite Scale — Crystal Lizard drop location
    entities.append(make_entity("Item", 134 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Scale")]))
    # Coiled Sword — Iudex Gundyr arena, obtained after defeating boss
    entities.append(make_entity("Item", 80 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Coiled Sword")]))

    # --- Fog Gate to Firelink Shrine (arena exit) ---
    entities.append(make_entity("FogGate", 80 * 16, 22 * 16, [
        make_field("dest_area", "String", "FirelinkShrine"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 1856.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # --- Gundyr door TilePatch ---
    # Wall tiles at arena north exit; opened when Gundyr defeated
    entities.append(make_entity("TilePatch", 80 * 16, 30 * 16, [
        make_field("tile", "LocalEnum.TileKind", "Ground"),
        make_field("x1", "Int", 78),
        make_field("y1", "Int", 29),
        make_field("x2", "Int", 82),
        make_field("y2", "Int", 30),
        make_field("condition", "String", "gundyr_door_open"),
    ]))

    # --- Lights ---
    # Coffin start — dim warm light
    entities.append(make_entity("Light", 25 * 16, 152 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))
    # Cemetery bonfire — warm ash glow
    entities.append(make_entity("Light", 72 * 16, 95 * 16, [
        make_field("radius", "Float", 128.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.45),
        make_field("b", "Float", 0.35), make_field("intensity", "Float", 0.25)]))
    # Water chasm — cold blue-green light
    entities.append(make_entity("Light", 124 * 16, 109 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.45),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.2)]))
    # Gundyr arena — bright coiled sword light
    entities.append(make_entity("Light", 80 * 16, 48 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.75),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.5)]))

    populate_entity_def_uids(entities)

    # Ensure connectivity from spawn to all entities
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)

    # Gundyr's closed door — wall tiles blocking north exit from arena
    # Added AFTER connectivity check so ensure_connected doesn't carve through
    fill_tiles(chunk, TILE_WALL, 78, 29, 82, 30)

    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  CemeteryOfAsh (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")

    return "CemeteryOfAsh", chunk, entities


def make_firelink_shrine():
    """Firelink Shrine - central hub area.
    Layout: Central circular chamber with bonfire, surrounded by alcoves for NPCs.
    Short paths to NPC locations. Stairs leading up.
    """
    chunk = new_chunk()
    entities = []

    # Central shrine chamber - large circle
    carve_ellipse(chunk, 80, 80, 24, 22)

    # Entrance path from south (from CemeteryOfAsh)
    fill_tiles(chunk, TILE_GROUND, 76, 102, 84, 128)

    # Shrine entrance antechamber
    carve_ellipse(chunk, 80, 120, 10, 8)

    # West wing - blacksmith area
    fill_tiles(chunk, TILE_GROUND, 40, 72, 56, 88)
    carve_ellipse(chunk, 36, 80, 8, 7)

    # East wing - merchant / level-up area
    fill_tiles(chunk, TILE_GROUND, 104, 72, 120, 88)
    carve_ellipse(chunk, 124, 80, 8, 7)

    # North alcove - handmaiden / storage
    fill_tiles(chunk, TILE_GROUND, 72, 52, 88, 60)
    carve_ellipse(chunk, 80, 48, 7, 5)

    # Upper west path - tower stairs
    fill_tiles(chunk, TILE_GROUND, 56, 60, 66, 72)
    carve_ellipse(chunk, 50, 56, 6, 5)

    # Upper east path
    fill_tiles(chunk, TILE_GROUND, 94, 60, 104, 72)
    carve_ellipse(chunk, 110, 56, 6, 5)

    # --- Enemies (DS3 Firelink Shrine exterior) ---
    # Sword Master — down the left stairs from shrine, wields Uchigatana
    fill_tiles(chunk, TILE_GROUND, 74, 130, 86, 140)
    entities.append(make_entity("Enemy", 80 * 16, 136 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "Assassin")]))
    # Starved Hound — graveyard near shrine entrance (DS3: undead dog)
    fill_tiles(chunk, TILE_GROUND, 92, 126, 100, 136)
    entities.append(make_entity("Enemy", 96 * 16, 130 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "StarvedHound")]))
    # Second Starved Hound — further along the cliff path
    entities.append(make_entity("Enemy", 98 * 16, 134 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "StarvedHound")]))
    # Grave Warden — patrols shrine exterior graves
    fill_tiles(chunk, TILE_GROUND, 60, 130, 70, 140)
    entities.append(make_entity("Enemy", 64 * 16, 134 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "CathedralGraveWarden")]))
    entities.append(make_entity("Enemy", 66 * 16, 138 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "CathedralGraveWarden")]))
    # Crystal Lizard — behind the tower (upper east roof drop-down)
    fill_tiles(chunk, TILE_GROUND, 114, 60, 120, 66)
    entities.append(make_entity("Enemy", 116 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "CrystalLizard")]))

    # Player spawn at entrance from south
    spawn_px, spawn_py = 80 * 16, 116 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfire in center
    entities.append(make_entity("Bonfire", 80 * 16, 80 * 16))

    # --- NPCs (DS3 Firelink Shrine inhabitants) ---
    # Fire Keeper (level up) — stands near bonfire
    entities.append(make_entity("Npc", 78 * 16, 74 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "LevelUp"),
        make_field("color", "Color", "#FFFFFF"),
        make_field("dialogue", "String", "Welcome to Firelink Shrine|May the flames guide your way|Touch the darkness within me"),
    ]))

    # Ludleth of Courland (dialogue) — sits on throne at bonfire
    entities.append(make_entity("Npc", 82 * 16, 84 * 16, [
        make_field("name", "String", "Ludleth of Courland"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#DAA520"),
        make_field("dialogue", "String", "Peace. I am Ludleth of Courland|A Lord, yes, but little more than a cinder|I will wait to see what you can do"),
    ]))

    # Blacksmith Andre — west wing, anvil area
    entities.append(make_entity("Npc", 38 * 16, 82 * 16, [
        make_field("name", "String", "Andre of Astora"),
        make_field("kind", "LocalEnum.NpcKind", "Blacksmith"),
        make_field("color", "Color", "#C0C0C0"),
        make_field("dialogue", "String", "What do you need?|I can reinforce your weapons|Only in the age of fire do we have purpose"),
    ]))

    # Shrine Handmaiden (merchant) — north alcove
    entities.append(make_entity("Npc", 82 * 16, 50 * 16, [
        make_field("name", "String", "Shrine Handmaiden"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7355"),
        make_field("dialogue", "String", "What is it? Buy something|Or be on your way|I shall tend the flame|And tend to thee"),
    ]))

    # Hawkwood (dialogue) — east wing, crestfallen warrior
    entities.append(make_entity("Npc", 108 * 16, 82 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String", "Oh, another Unkindled|The Farron Keep... that is where you should go|Unkindled are unfit to tend the fire"),
    ]))

    # --- Items (DS3 Firelink Shrine) ---
    # Estus Shard — on rafters above shrine (upper west, illusory wall area)
    entities.append(make_entity("Item", 50 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    # Covetous Silver Serpent Ring — chest behind illusory wall on rafters (upper east)
    entities.append(make_entity("Chest", 110 * 16, 56 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Covetous Silver Serpent Ring"),
        make_field("is_mimic", "Bool", False)]))
    # Estus Ring — drop down from tower bridge ledge (upper west tower)
    entities.append(make_entity("Item", 54 * 16, 54 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Estus Ring")]))
    # Fire Keeper Soul — top of tower (upper east tower top)
    entities.append(make_entity("Item", 120 * 16, 54 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Fire Keeper Soul")]))
    # Broken Straight Sword — by graves straight ahead from entrance (south graves)
    entities.append(make_entity("Item", 76 * 16, 124 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Broken Straight Sword")]))
    # Homeward Bone — along path from CemeteryOfAsh (near graves, 5 in DS3)
    entities.append(make_entity("Item", 78 * 16, 120 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 80 * 16, 124 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 82 * 16, 120 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 76 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 84 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Ember — near dog area (right path from shrine, 2 in DS3)
    entities.append(make_entity("Item", 94 * 16, 128 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 98 * 16, 136 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # East-West Shield — corpse in tree near Sword Master area (junction of stairs)
    entities.append(make_entity("Item", 86 * 16, 138 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "East-West Shield"),
        make_field("slot", "String", "Hands")]))
    # Uchigatana — dropped by Sword Master (near Sword Master enemy position)
    entities.append(make_entity("Item", 80 * 16, 138 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Uchigatana")]))
    # Master's Attire — dropped by Sword Master
    entities.append(make_entity("Item", 78 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Master's Attire"),
        make_field("slot", "String", "Chest")]))
    # Master's Gloves — dropped by Sword Master
    entities.append(make_entity("Item", 82 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Master's Gloves"),
        make_field("slot", "String", "Hands")]))
    # Soul of a Deserted Corpse — tower area corpse (upper path)
    entities.append(make_entity("Item", 48 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse"),
        make_field("value", "Int", 200)]))
    # Twinkling Titanite — Crystal Lizard drop (near crystal lizard area)
    entities.append(make_entity("Item", 116 * 16, 64 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Twinkling Titanite")]))
    # Fire Keeper Set — drop from tower bridge (upper area)
    entities.append(make_entity("Item", 108 * 16, 54 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Fire Keeper Set"),
        make_field("slot", "String", "Chest")]))
    # Seed of a Giant Tree — from Giant Tree near shrine exterior
    entities.append(make_entity("Item", 62 * 16, 126 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Seed of a Giant Tree")]))

    # --- Fog Gates ---
    # Back to CemeteryOfAsh
    entities.append(make_entity("FogGate", 80 * 16, 128 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 580.0),
        make_field("dest_y", "Float", 320.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # To LothricWall (north exit)
    entities.append(make_entity("FogGate", 80 * 16, 46 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 200.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # --- Lights ---
    # Central bonfire — warm light
    entities.append(make_entity("Light", 80 * 16, 80 * 16, [
        make_field("radius", "Float", 240.0), make_field("r", "Float", 0.9),
        make_field("g", "Float", 0.7), make_field("b", "Float", 0.4),
        make_field("intensity", "Float", 0.6)]))
    # Andre's forge — orange glow
    entities.append(make_entity("Light", 36 * 16, 80 * 16, [
        make_field("radius", "Float", 120.0), make_field("r", "Float", 0.8),
        make_field("g", "Float", 0.5), make_field("b", "Float", 0.2),
        make_field("intensity", "Float", 0.4)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)

    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  FirelinkShrine (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "FirelinkShrine", chunk, entities


def make_lothric_wall():
    """High Wall of Lothric — faithful DS3 layout.

    Real DS3 progression from speedrun/walkthrough data:
    1. Wall Entrance rampart (arrive from CemeteryOfAsh)
    2. Longbow dead-end balcony (south of entry)
    3. Dragon walkway + bridge (descend south through fire zone)
    4. Tower area (Winged Knight room, Greirat's cell)
    5. Residential maze (house alleys with Assassins, Darkwraith)
    6. Courtyard (Lothric Knights, fountain, sewer passage)
    7. Knight path + Cathedral (Emma's chapel)
    8. Frost stairs (icy descent with poison cold patches)
    9. Vordt arena (large oval boss fight at south end)

    Design doc reference: docs/maps/LothricWall.json (3600x2800)
    Grid: 160x160, progression NW→SE
    """
    chunk = new_chunk()

    # 1. WALL ENTRANCE RAMPART — NW corner, arrive from CemeteryOfAsh
    fill_tiles(chunk, TILE_GROUND, 8, 6, 36, 22)
    # Small alcove for Longbow pickup (south of entry)
    fill_tiles(chunk, TILE_GROUND, 36, 8, 44, 14)
    fill_tiles(chunk, TILE_GROUND, 42, 6, 58, 20)
    carve_ellipse(chunk, 52, 12, 6, 5)

    # 2. DRAGON WALKWAY — descend south from entry
    fill_tiles(chunk, TILE_GROUND, 14, 20, 24, 34)
    fill_tiles(chunk, TILE_GROUND, 10, 26, 28, 32)

    # 3. DRAGON BRIDGE — wide horizontal bridge with fire obstacles
    fill_tiles(chunk, TILE_GROUND, 10, 30, 56, 40)
    # Dragon fire obstacles (wall pillars creating cover spots)
    fill_tiles(chunk, TILE_WALL, 22, 30, 24, 34)
    fill_tiles(chunk, TILE_WALL, 34, 36, 36, 40)
    fill_tiles(chunk, TILE_WALL, 46, 30, 48, 35)

    # 4. TOWER AREA — east of dragon bridge
    fill_tiles(chunk, TILE_GROUND, 48, 34, 54, 38)
    fill_tiles(chunk, TILE_GROUND, 52, 36, 74, 52)
    carve_ellipse(chunk, 62, 42, 8, 6)
    # Greirat's cell alcove (south of tower)
    fill_tiles(chunk, TILE_GROUND, 56, 44, 62, 50)

    # 5. RESIDENTIAL MAZE — large area with house wall blocks
    fill_tiles(chunk, TILE_GROUND, 24, 50, 80, 82)
    # House walls creating narrow alleys (thinner for entity fit)
    fill_tiles(chunk, TILE_WALL, 30, 54, 35, 58)   # House A
    fill_tiles(chunk, TILE_WALL, 42, 52, 47, 56)   # House B
    fill_tiles(chunk, TILE_WALL, 54, 54, 59, 58)   # House C
    fill_tiles(chunk, TILE_WALL, 66, 52, 71, 56)   # House D
    fill_tiles(chunk, TILE_WALL, 30, 64, 35, 68)   # House E
    fill_tiles(chunk, TILE_WALL, 42, 62, 47, 66)   # House F
    fill_tiles(chunk, TILE_WALL, 54, 64, 59, 68)   # House G
    fill_tiles(chunk, TILE_WALL, 66, 62, 71, 66)   # House H
    fill_tiles(chunk, TILE_WALL, 36, 72, 41, 76)   # House I
    fill_tiles(chunk, TILE_WALL, 48, 74, 53, 78)   # House J
    fill_tiles(chunk, TILE_WALL, 60, 72, 65, 76)   # House K
    fill_tiles(chunk, TILE_WALL, 30, 78, 35, 82)   # House L
    fill_tiles(chunk, TILE_WALL, 48, 78, 53, 82)   # House M (partial)

    # Connection: tower area to residential north
    fill_tiles(chunk, TILE_GROUND, 50, 48, 56, 52)

    # 6. COURTYARD — south of residential, with fountain and sewer alcove
    fill_tiles(chunk, TILE_GROUND, 10, 78, 58, 100)
    # Fountain island obstacle at center
    fill_tiles(chunk, TILE_WALL, 28, 86, 38, 92)
    # Sewer alcove (east of courtyard)
    fill_tiles(chunk, TILE_GROUND, 54, 82, 62, 96)

    # Lift shortcut shaft — DS3: pressure plate lift connects lower area to Tower on the Wall
    # The player goes up past crossbow hollow, through falling leaves archway, finds lift room
    fill_tiles(chunk, TILE_GROUND, 58, 90, 64, 100)
    # Lift shaft (narrow vertical corridor representing elevator shaft)
    fill_tiles(chunk, TILE_GROUND, 60, 40, 62, 90)
    # Falling leaves area — between fountain and lift (DS3: area covered in falling leaves)
    fill_tiles(chunk, TILE_GROUND, 54, 88, 60, 96)
    # Darkwraith locked cell — under Tower on the Wall (DS3: behind locked door, Lift Chamber Key)
    fill_tiles(chunk, TILE_GROUND, 50, 48, 56, 52)

    # Connection: residential south to courtyard
    fill_tiles(chunk, TILE_GROUND, 24, 78, 30, 82)

    # 7. KNIGHT PATH — east from courtyard to cathedral
    fill_tiles(chunk, TILE_GROUND, 56, 88, 90, 108)
    # Stone wall obstacles along the path
    fill_tiles(chunk, TILE_WALL, 64, 92, 66, 96)
    fill_tiles(chunk, TILE_WALL, 76, 98, 78, 104)

    # 8. CATHEDRAL — Emma's chapel area
    fill_tiles(chunk, TILE_GROUND, 64, 98, 96, 114)
    fill_tiles(chunk, TILE_WALL, 72, 100, 76, 104)  # Chapel column
    fill_tiles(chunk, TILE_WALL, 84, 106, 88, 110)  # Chapel column
    carve_ellipse(chunk, 80, 106, 6, 4)

    # Connection: knight path to cathedral
    fill_tiles(chunk, TILE_GROUND, 68, 106, 76, 110)

    # 9. FROST STAIRS — icy descent south from cathedral to Vordt
    fill_tiles(chunk, TILE_GROUND, 72, 112, 98, 142)
    # Wider landings at intervals
    fill_tiles(chunk, TILE_GROUND, 68, 118, 100, 124)
    fill_tiles(chunk, TILE_GROUND, 68, 130, 100, 136)
    # Icy patches (poison tiles as cold damage)
    fill_tiles(chunk, TILE_POISON, 78, 120, 84, 122)
    fill_tiles(chunk, TILE_POISON, 86, 132, 92, 134)

    # Connection: cathedral to frost stairs
    fill_tiles(chunk, TILE_GROUND, 76, 110, 82, 114)

    # 10. VORDT ARENA — large oval at south end
    carve_ellipse(chunk, 100, 144, 22, 12)
    # Entry funnel from frost stairs
    fill_tiles(chunk, TILE_GROUND, 86, 136, 114, 142)

    # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    spawn_px, spawn_py = 18 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 18 * 16, 12 * 16))    # Wall Entrance
    entities.append(make_entity("Bonfire", 62 * 16, 40 * 16))    # Tower on the Wall
    entities.append(make_entity("Bonfire", 107 * 16, 100 * 16))  # Dancer of the Boreal Valley
    entities.append(make_entity("Bonfire", 100 * 16, 146 * 16))  # Vordt of the Boreal Valley

    # --- Bosses ---
    # Vordt of the Boreal Valley — main boss at south arena
    entities.append(make_entity("BossSpawn", 100 * 16, 144 * 16))
    # Dancer of the Boreal Valley — appears in cathedral area after Emma
    # DS3: triggered by approaching the statue after receiving Basin of Vows from Emma
    # Represented as MiniBoss since engine supports one BossSpawn per area
    entities.append(make_entity("Enemy", 82 * 16, 102 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "MiniBoss")]))

    # --- Enemies (DS3 High Wall of Lothric: Lothric Knights, Dogs, Hollow Soldiers) ---
    enemy_positions = [
        # Wall entrance rampart — hollow soldiers on guard
        ("HollowSoldier", 14, 10), ("HollowSoldier", 22, 14),
        ("LothricKnight", 30, 18), ("HollowSoldier", 16, 20),
        # Longbow balcony — hollow soldier + archer
        ("HollowSoldier", 48, 10), ("Archer", 54, 14),
        # Pus of Man — praying hollow transforms (DS3: on balcony near Longbow)
        ("PusOfMan", 50, 12),
        # Lothric Wyvern — breathes fire on the bridge (DS3: key encounter)
        ("LothricWyvern", 24, 32),
        # Dragon walkway — dogs patrol near dead dragon
        ("StarvedHound", 16, 24), ("StarvedHound", 20, 28),           # DS3: Starved Hounds patrol near dead dragon
        ("StarvedHound", 18, 22),                          # Starved Hound near wyvern
        # Dragon bridge — hollows burned by dragon fire
        ("HollowSoldier", 18, 34), ("HollowSoldier", 28, 38),
        ("HollowSoldier", 40, 32), ("HollowSoldier", 52, 36),
        # Tower area — Winged Knight patrols the roof
        ("WingedKnight", 62, 42),
        ("CrystalLizard", 58, 48),
        ("CrystalLizard", 48, 50),                         # Second crystal lizard on rooftops
        # Mimic — chest near wyvern area (DS3: Deep Battle Axe mimic)
        ("Mimic", 42, 38),
        # Large Hollow Soldier — in tower with halberd
        ("LargeHollowSoldier", 56, 46),                    # Halberd-wielding large hollow
        # Residential maze — Assassins hide in alleys, Lothric Knights patrol
        ("Assassin", 38, 56), ("LothricKnight", 50, 54),
        ("LothricKnight", 62, 54), ("LothricKnight", 74, 54),
        ("Darkwraith", 54, 50),                    # Darkwraith in locked cell under Tower (Lift Chamber Key)
        ("HollowSoldier", 50, 66),
        ("Assassin", 62, 66), ("HollowSoldier", 74, 64),
        ("HollowSoldier", 40, 74), ("HollowSoldier", 56, 74),
        # Courtyard — Lothric Knights guard the fountain area
        ("LothricKnight", 20, 84), ("LothricKnight", 44, 96),
        ("StarvedHound", 16, 92), ("StarvedHound", 46, 88),           # DS3: Starved Hounds near lower walls
        ("HollowSoldier", 34, 94), ("HollowSoldier", 52, 90),
        # Second Pus of Man — rooftop praying hollow (DS3: rooftop area)
        ("PusOfMan", 42, 60),                             # Rooftop pus of man
        # Knight path — heavy Lothric Knight presence
        ("LothricKnight", 62, 94), ("LothricKnight", 82, 102),
        ("HollowSoldier", 70, 100), ("LothricKnight", 86, 96),
        # Cathedral area
        ("LothricKnight", 70, 106), ("LothricKnight", 90, 108),
        # Red-eyed Lothric Knight — tough variant (DS3: before Vordt)
        ("LothricKnight", 92, 115),                       # Red-eyed knight near Emma
        # Frost stairs descent
        ("LothricKnight", 80, 118), ("HollowSoldier", 88, 126),
        ("LothricKnight", 76, 134), ("LothricKnight", 94, 138),
        # Hollow Assassins on rooftops (DS3: ambush near wyvern)
        ("HollowAssassin", 44, 40), ("HollowAssassin", 60, 50),
    ]
    for kind, tx, ty in enemy_positions:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- NPCs ---
    # Greirat — locked in cell below tower (DS3: basement cell)
    entities.append(make_entity("Npc", 36 * 16, 60 * 16, [
        make_field("name", "String", "Greirat"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#A0A0A0"),
        make_field("dialogue", "String",
            "...Who are you? Can you let me out?|Find the cell key and I will serve you"),
    ]))
    # Emma — High Priestess in the cathedral (DS3: gives Small Lothric Banner)
    entities.append(make_entity("Npc", 80 * 16, 108 * 16, [
        make_field("name", "String", "Emma"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A0D0"),
        make_field("dialogue", "String",
            "Hello, Unkindled|I am Emma, High Priestess of Lothric|Find the Prince, give him this banner"),
    ]))

    # --- Items (DS3 High Wall of Lothric) ---
    items = [
        # Wall entrance — early pickups
        ("SoulOrb", "Soul of a Deserted Corpse", 12, 8, 200),
        ("Firebomb", "Firebomb", 26, 16, 0),
        ("Consumable", "Throwing Knife", 20, 8, 0),
        ("Consumable", "Firebomb", 32, 12, 0),
        # Longbow balcony
        ("WeaponDrop", "Longbow", 52, 10, 0),
        ("Consumable", "Standard Arrow", 50, 8, 0),
        ("Consumable", "Binoculars", 46, 8, 0),
        # Dragon walkway — wyvern area
        ("Consumable", "Gold Pine Resin", 16, 26, 0),
        ("TitaniteShard", "Large Titanite Shard", 20, 30, 0),
        ("Consumable", "Gold Pine Resin", 22, 28, 0),
        # Dragon bridge
        ("SoulOrb", "Large Soul of a Deserted Corpse", 30, 36, 400),
        ("TitaniteShard", "Titanite Shard", 50, 34, 0),
        ("Consumable", "Green Blossom", 38, 38, 0),
        ("Consumable", "Black Firebomb", 44, 32, 0),
        ("Consumable", "Black Firebomb", 28, 40, 0),
        ("Consumable", "Black Firebomb", 36, 34, 0),
        # Tower area
        ("Consumable", "Cell Key", 56, 48, 0),
        ("Consumable", "Throwing Knife", 60, 38, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 58, 44, 200),
        ("SoulOrb", "Soul of a Deserted Corpse", 44, 58, 200),
        # Residential maze
        ("EstusShard", "Estus Shard", 72, 58, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 44, 70, 200),
        ("TitaniteShard", "Titanite Shard", 68, 76, 0),
        ("Consumable", "Firebomb", 36, 60, 0),
        ("Consumable", "Throwing Knife", 58, 68, 0),
        ("Consumable", "Alluring Skull", 46, 72, 0),
        ("WeaponDrop", "Broadsword", 32, 56, 0),
        ("WeaponDrop", "Mail Breaker", 64, 62, 0),
        ("Consumable", "Red Eye Orb", 76, 58, 0),
        ("Consumable", "Undead Hunter Charm", 38, 62, 0),
        ("Consumable", "Undead Hunter Charm", 42, 66, 0),
        # Courtyard
        ("Consumable", "Firebomb", 40, 92, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 50, 94, 200),
        ("Consumable", "Green Blossom", 14, 86, 0),
        ("Consumable", "Green Blossom", 48, 84, 0),
        ("Consumable", "Green Blossom", 52, 96, 0),
        ("Consumable", "Green Blossom", 18, 96, 0),
        ("RingDrop", "Way of Blue", 34, 88, 0),
        ("TitaniteShard", "Titanite Shard", 42, 90, 0),
        ("Ember", "Ember", 30, 90, 0),
        ("Ember", "Ember", 44, 94, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 22, 88, 200),
        ("SoulOrb", "Soul of a Deserted Corpse", 54, 86, 200),
        ("SoulOrb", "Soul of a Deserted Corpse", 48, 92, 200),
        # Knight path / cathedral
        ("EstusShard", "Estus Shard", 74, 100, 0),
        ("TitaniteShard", "Titanite Shard", 88, 104, 0),
        ("RingDrop", "Blue Tearstone Ring", 80, 112, 0),
        ("Consumable", "Small Lothric Banner", 82, 108, 0),
        ("WeaponDrop", "Lucerne", 90, 98, 0),
        ("Consumable", "Firebomb", 66, 96, 0),
        ("WeaponDrop", "Rapier", 76, 94, 0),
        ("Consumable", "Refined Gem", 84, 102, 0),
        ("SoulOrb", "Large Soul of a Deserted Corpse", 86, 100, 400),
        ("RingDrop", "Ring of Sacrifice", 78, 98, 0),
        # Frost stairs
        ("Consumable", "Throwing Knife", 78, 132, 0),
        ("TitaniteShard", "Titanite Shard", 96, 130, 0),
        ("WeaponDrop", "Club", 88, 118, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests (DS3 High Wall of Lothric) ---
    # Silver Eagle Kite Shield — chest on rampart near dragon bridge
    entities.append(make_entity("Chest", 14 * 16, 32 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Silver Eagle Kite Shield"),
        make_field("is_mimic", "Bool", False)]))
    # Astora Straight Sword — chest in tower basement
    entities.append(make_entity("Chest", 60 * 16, 50 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Astora Straight Sword"),
        make_field("is_mimic", "Bool", False)]))
    # Deep Battle Axe — mimic in room below dragon
    entities.append(make_entity("Chest", 42 * 16, 38 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Deep Battle Axe"),
        make_field("is_mimic", "Bool", True)]))
    # Titanite Shard — chest in residential area
    entities.append(make_entity("Chest", 38 * 16, 64 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Shard"),
        make_field("is_mimic", "Bool", False)]))
    # Claymore — chest on rooftop near cathedral
    entities.append(make_entity("Chest", 72 * 16, 82 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Claymore"),
        make_field("is_mimic", "Bool", False)]))

    # --- Fog Gates ---
    # Back to CemeteryOfAsh (NW entry point)
    entities.append(make_entity("FogGate", 12 * 16, 8 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 288.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))
    # To Undead Settlement (south of Vordt arena)
    entities.append(make_entity("FogGate", 100 * 16, 154 * 16, [
        make_field("dest_area", "String", "UndeadSettlement"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 80.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Lothric Castle (Dancer lift — post-Dancer area NE)
    entities.append(make_entity("FogGate", 107 * 16, 95 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 500.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Consumed King's Garden (post-Dancer, SE path)
    entities.append(make_entity("FogGate", 120 * 16, 115 * 16, [
        make_field("dest_area", "String", "ConsumedKingsGarden"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 200.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Entry rampart — cool stone light
    entities.append(make_entity("Light", 18 * 16, 12 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.55),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.3)]))
    # Dragon bridge — orange firelight
    entities.append(make_entity("Light", 34 * 16, 36 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.4)]))
    # Tower area — cold blue light
    entities.append(make_entity("Light", 62 * 16, 42 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.25)]))
    # Courtyard — warm firelight
    entities.append(make_entity("Light", 34 * 16, 90 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.55),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))
    # Cathedral — soft candlelight
    entities.append(make_entity("Light", 80 * 16, 106 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.25)]))
    # Frost stairs — icy blue glow
    entities.append(make_entity("Light", 86 * 16, 126 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.35)]))
    # Vordt arena — cold boreal blue
    entities.append(make_entity("Light", 100 * 16, 144 * 16, [
        make_field("radius", "Float", 220.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.4)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)

    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  LothricWall (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "LothricWall", chunk, entities


def make_undead_settlement():
    """Undead Settlement — faithful DS3 layout.

    Progression: Entry (top-left) → House Street → Giant Tower → Bonfire Square
    → Cliffside Path → Fire Demon Square → Pilgrim Camp → Irina's Cell.
    Pit of Hollows (Greatwood boss) below Bonfire Square.

    Real DS3 features: narrow alleys between wooden houses, Giant throwing spears,
    Siegward assisting vs Fire Demon, Evangelists with maces, hanging corpses.
    """
    chunk = new_chunk()

    # 1. SETTLEMENT ENTRANCE (top-left) — from High Wall
    fill_tiles(chunk, TILE_GROUND, 8, 8, 35, 28)
    carve_ellipse(chunk, 18, 18, 10, 8)

    # 2. HOUSE STREET — main street with wooden houses
    fill_tiles(chunk, TILE_GROUND, 30, 22, 62, 48)
    # House wall protrusions creating narrow alleys
    fill_tiles(chunk, TILE_WALL, 36, 26, 42, 32)
    fill_tiles(chunk, TILE_WALL, 50, 34, 56, 40)
    fill_tiles(chunk, TILE_WALL, 38, 40, 44, 46)

    # 3. GIANT TOWER — circular tower (center-left)
    carve_ellipse(chunk, 52, 26, 10, 12)
    fill_tiles(chunk, TILE_GROUND, 44, 22, 56, 30)

    # 4. BONFIRE SQUARE — open area with large bonfire (center)
    carve_ellipse(chunk, 70, 56, 16, 12)
    fill_tiles(chunk, TILE_GROUND, 56, 42, 72, 50)

    # 5. DILAPIDATED BRIDGE — connecting tower area to square
    fill_tiles(chunk, TILE_GROUND, 54, 34, 64, 42)

    # 6. CLIFFSIDE PATH — narrow path along cliff (east)
    fill_tiles(chunk, TILE_GROUND, 84, 38, 112, 48)
    carve_ellipse(chunk, 100, 42, 8, 6)

    # 7. FIRE DEMON SQUARE (center-right)
    carve_ellipse(chunk, 100, 64, 14, 10)
    fill_tiles(chunk, TILE_GROUND, 82, 56, 96, 66)

    # 8. PILGRIM CAMP (upper-right) — Yoel and pilgrims
    fill_tiles(chunk, TILE_GROUND, 114, 28, 140, 42)
    carve_ellipse(chunk, 128, 34, 10, 6)

    # 9. IRINA'S CELL (right edge)
    fill_tiles(chunk, TILE_GROUND, 140, 48, 152, 60)
    carve_ellipse(chunk, 146, 54, 6, 5)

    # Connection: cliffside to pilgrim camp
    fill_tiles(chunk, TILE_GROUND, 110, 38, 118, 44)

    # Connection: fire demon to Irina's cell
    fill_tiles(chunk, TILE_GROUND, 112, 52, 140, 58)

    # 10. CLIFF UNDERSIDE (below village)
    fill_tiles(chunk, TILE_GROUND, 50, 76, 78, 92)
    carve_ellipse(chunk, 64, 84, 10, 7)

    # 11. PIT OF HOLLOWS / GREATWOOD ARENA (bottom-center)
    carve_ellipse(chunk, 90, 110, 22, 20)
    # Path down from bonfire square
    fill_tiles(chunk, TILE_GROUND, 72, 66, 82, 82)
    carve_corridor(chunk, 78, 68, 84, 92, width=4)

    # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    spawn_px, spawn_py = 18 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 18 * 16, 16 * 16))   # Foot of the High Wall
    entities.append(make_entity("Bonfire", 46 * 16, 36 * 16))   # Undead Settlement
    entities.append(make_entity("Bonfire", 64 * 16, 84 * 16))   # Cliff Underside
    entities.append(make_entity("Bonfire", 58 * 16, 36 * 16))   # Dilapidated Bridge
    entities.append(make_entity("Bonfire", 90 * 16, 112 * 16))  # Pit of Hollows

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 90 * 16, 106 * 16))

    # --- Enemies (DS3 Undead Settlement: Peasant Hollows, Evangelists, Thralls) ---
    enemy_data = [
        # Entrance — hollow soldiers + Starved Hounds at portcullis (DS3: 3 hounds released through gate)
        ("HollowSoldier", 22, 14), ("HollowSoldier", 26, 22),
        ("StarvedHound", 18, 18), ("StarvedHound", 20, 20), ("StarvedHound", 16, 22),
        # House streets — Peasant Hollows are the main enemy (DS3: pitchfork hollows, hat-wearing hollows)
        ("PeasantHollow", 34, 28), ("PeasantHollow", 42, 36),
        ("PeasantHollow", 54, 42), ("PeasantHollow", 48, 44),
        ("PeasantHollow", 60, 34), ("PeasantHollow", 66, 38),
        ("HollowSoldier", 38, 32),
        # Starved Hounds in the streets (DS3: dogs behind overturned coach, near sewers)
        ("StarvedHound", 30, 36), ("StarvedHound", 58, 38),
        ("StarvedHound", 82, 50),                                    # DS3: dog guarding ember near sewers
        # Evangelists — heavy mace women patrol the squares
        ("Evangelist", 62, 46), ("Evangelist", 66, 52),
        ("Evangelist", 76, 60), ("Evangelist", 86, 54),
        # Thralls hiding on rooftops and rafters (DS3: many thrall drop ambushes)
        ("Thrall", 56, 30), ("Thrall", 72, 50),
        ("Thrall", 46, 38), ("Thrall", 80, 58),
        ("Thrall", 50, 36), ("Thrall", 64, 42),                      # DS3: thralls drop from ceiling in houses
        # Cliffside — more hollows
        ("HollowSoldier", 90, 42), ("HollowSoldier", 96, 44),
        ("PeasantHollow", 94, 50),
        # Fire Demon (DS3: fights alongside Siegward)
        ("FireDemon", 102, 62),
        # Cliff Underside area
        ("PeasantHollow", 58, 82), ("PeasantHollow", 68, 86),
        ("HollowSoldier", 64, 78),
        # Sewers — rats (DS3: 3 small rats + 1 big rat in sewers, drops Bloodbite Ring)
        ("Rat", 78, 76), ("Rat", 80, 78), ("Rat", 82, 80),          # DS3: small rats in sewers
        ("Dog", 84, 76),                                              # DS3: big rat (Dog for larger enemy)
        # Path to pit / Curse-Rotted Greatwood area
        ("HollowSoldier", 78, 78), ("HollowSoldier", 84, 88),
        ("Thrall", 82, 82),
        # Giant Slave on tower (DS3: shoots great arrows at player throughout the level)
        ("GiantSlave", 52, 22),                                       # DS3: Giant atop tower with great bow
        # Boreal Outrider Knight at lift (DS3: Knight of the Boreal Valley guarding Road of Sacrifices exit)
        ("WingedKnight", 146, 52),                                    # DS3: Irithyll Straight Sword drop
        # Holy Knight Hodrick invasion (DS3: Mad Spirit invades near Dilapidated Bridge if Embered)
        ("MiniBoss", 64, 66),                                         # DS3: Hodrick, Mound-Makers member
        # Irina's area — Skeletons (DS3: skeletons animate and attack in graveyard near Irina)
        ("Skeleton", 140, 52), ("Skeleton", 142, 54), ("Skeleton", 144, 48),
        # Crystal Lizard (DS3: near Hodrick invasion area / cliff path)
        ("CrystalLizard", 112, 46),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- NPCs (DS3 Undead Settlement: Yoel, Siegward, Cornyx) ---
    # Yoel of Londor — among the pilgrims at the entrance (DS3: offers free levels)
    entities.append(make_entity("Npc", 120 * 16, 34 * 16, [
        make_field("name", "String", "Yoel of Londor"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A4A5A"),
        make_field("dialogue", "String",
            "I am Yoel of Londor|Let me grant you true strength|Come. Touch the darkness within me"),
    ]))
    # Siegward of Catarina — at Fire Demon square (DS3: helps fight the demon)
    entities.append(make_entity("Npc", 96 * 16, 60 * 16, [
        make_field("name", "String", "Siegward"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A060"),
        make_field("dialogue", "String",
            "Aah, hello again|Let us fight this demon together!|Oh, very good. Very good indeed"),
    ]))
    # Cornyx — pyromancy trainer in cage on rooftop (DS3: freed from cage, offers pyromancies)
    entities.append(make_entity("Npc", 44 * 16, 28 * 16, [
        make_field("name", "String", "Cornyx"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#B8860B"),
        make_field("dialogue", "String",
            "You are a Pyromancy student?|I can teach you the flame arts|The flame is both a blessing and a curse"),
    ]))
    # Irina of Carim — miracle teacher in cell (DS3: found through locked door in sewers, near skeletons)
    entities.append(make_entity("Npc", 146 * 16, 54 * 16, [
        make_field("name", "String", "Irina of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7D9B"),
        make_field("dialogue", "String",
            "I am Irina of Carim|I can teach you miracles|Please, take me to Firelink Shrine"),
    ]))
    # Eygon of Carim — guards Irina (DS3: found outside near Irina, warns about the champion)
    entities.append(make_entity("Npc", 148 * 16, 50 * 16, [
        make_field("name", "String", "Eygon of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A3A2A"),
        make_field("dialogue", "String",
            "I am Eygon of Carim|Keep your hands off the woman|She is under my protection"),
    ]))

    # --- Items (DS3 Undead Settlement) ---
    # Large Soul of a Deserted Corpse — entry rampart
    entities.append(make_entity("Item", 22 * 16, 12 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse"),
        make_field("value", "Int", 400)]))
    # Alluring Skull 2x — near dogs by overturned coach
    entities.append(make_entity("Item", 24 * 16, 18 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Alluring Skull")]))
    # Homeward Bone 2x — end of broken road near Yoel
    entities.append(make_entity("Item", 30 * 16, 22 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Small Leather Shield — hanging body in first house
    entities.append(make_entity("Item", 44 * 16, 28 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Small Leather Shield"),
        make_field("slot", "String", "Hands")]))
    # Charcoal Pine Bundle 2x — first house balcony
    entities.append(make_entity("Item", 46 * 16, 32 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Charcoal Pine Bundle")]))
    # Loretta's Bone — hanging body outside house
    entities.append(make_entity("Item", 48 * 16, 36 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Loretta's Bone")]))
    # Repair Powder 2x — around corner from Loretta's Bone
    entities.append(make_entity("Item", 42 * 16, 34 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Repair Powder")]))
    # Charcoal Pine Bundle 2x — lower floor of house
    entities.append(make_entity("Item", 44 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Charcoal Pine Bundle")]))
    # Firebomb 6x — corpse in front of blazing fire (wiki: 6x Firebomb)
    entities.append(make_entity("Item", 44 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    # Ember — behind the blazing fire
    entities.append(make_entity("Item", 46 * 16, 42 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # Large Soul of a Deserted Corpse — settlement house
    entities.append(make_entity("Item", 56 * 16, 34 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse"),
        make_field("value", "Int", 400)]))
    # Homeward Bone 2x — rooftop path
    entities.append(make_entity("Item", 58 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Caduceus Round Shield — cliff corner near double doors
    entities.append(make_entity("Item", 62 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Caduceus Round Shield"),
        make_field("slot", "String", "Hands")]))
    # Plank Shield — near caged hollow NPC
    entities.append(make_entity("Item", 66 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Plank Shield"),
        make_field("slot", "String", "Hands")]))
    # Reinforced Club — hanging body near cage hollow (wiki: weapon pickup)
    entities.append(make_entity("Item", 70 * 16, 44 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Reinforced Club")]))
    # Titanite Shard — ledge near Cornyx bridge
    entities.append(make_entity("Item", 72 * 16, 32 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Partizan — hanging corpse shot down near Cornyx roof
    entities.append(make_entity("Item", 76 * 16, 28 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Partizan")]))
    # Hand Axe — balcony near Cornyx cage
    entities.append(make_entity("Item", 80 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Hand Axe")]))
    # Soul of an Unknown Traveler — wooden torture platform
    entities.append(make_entity("Item", 82 * 16, 36 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler"),
        make_field("value", "Int", 400)]))
    # Fire Clutch Ring — end of half-broken bridge
    entities.append(make_entity("Item", 86 * 16, 34 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Fire Clutch Ring")]))
    # Large Soul of a Deserted Corpse — around corner from Fire Clutch
    entities.append(make_entity("Item", 88 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse"),
        make_field("value", "Int", 400)]))
    # Ember — past sewers, dog guarding
    entities.append(make_entity("Item", 64 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # Bloodbite Ring — dropped by big rat in sewers
    entities.append(make_entity("Item", 68 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Bloodbite Ring")]))
    # Caestus — corpse in sewer hallway
    entities.append(make_entity("Item", 66 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Caestus")]))
    # Loincloth — behind locked door (Grave Key)
    entities.append(make_entity("Item", 72 * 16, 76 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Loincloth"),
        make_field("slot", "String", "Legs")]))
    # Red Hilted Halberd — hallway behind locked door
    entities.append(make_entity("Item", 74 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Red Hilted Halberd")]))
    # Soul of an Unknown Traveler — skeleton room behind locked door
    entities.append(make_entity("Item", 78 * 16, 78 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler"),
        make_field("value", "Int", 400)]))
    # Titanite Shard 2x — beyond skeleton room
    entities.append(make_entity("Item", 80 * 16, 82 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 82 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Saint's Talisman — room with rats near Irina
    entities.append(make_entity("Item", 84 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Saint's Talisman")]))
    # Estus Shard — house near Dilapidated Bridge bonfire
    entities.append(make_entity("Item", 58 * 16, 36 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    # Warriors of Sunlight Covenant — drop down hole in dwelling
    entities.append(make_entity("Item", 50 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Warriors of Sunlight")]))
    # Charcoal Pine Resin 2x — near caged limbs
    entities.append(make_entity("Item", 52 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Charcoal Pine Resin")]))
    # Titanite Shard — lower level house
    entities.append(make_entity("Item", 56 * 16, 44 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Whip — open dwelling
    entities.append(make_entity("Item", 60 * 16, 54 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Whip")]))
    # Titanite Shard — ladder up to bridge
    entities.append(make_entity("Item", 64 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Rusted Coin — roof after Hodrick invasion
    entities.append(make_entity("Item", 100 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Rusted Coin")]))
    # Fading Soul — path near Hodrick
    entities.append(make_entity("Item", 98 * 16, 52 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Fading Soul")]))
    # Red Bug Pellet 2x — open area after Fire Demon
    entities.append(make_entity("Item", 92 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Red Bug Pellet")]))
    # Large Club — open area after Fire Demon
    entities.append(make_entity("Item", 90 * 16, 44 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Large Club")]))
    # Alluring Skull 2x — structure near Fire Demon area
    entities.append(make_entity("Item", 96 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Alluring Skull")]))
    # Flynn's Ring — roof of structure near Fire Demon
    entities.append(make_entity("Item", 98 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Flynn's Ring")]))
    # Homeward Bone 2x — drop from wooden scaffolding
    entities.append(make_entity("Item", 94 * 16, 42 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Chloranthy Ring — drop down tower near Fire Demon
    entities.append(make_entity("Item", 96 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Chloranthy Ring")]))
    # Irithyll Straight Sword — from Boreal Knight at lift
    entities.append(make_entity("Item", 130 * 16, 52 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Irithyll Straight Sword")]))
    # Fading Soul — giant spear area
    entities.append(make_entity("Item", 108 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Fading Soul")]))
    # Ember — giant spear area
    entities.append(make_entity("Item", 110 * 16, 64 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # Young White Branch 2x — giant spear area
    entities.append(make_entity("Item", 106 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Young White Branch")]))
    # Large Soul of a Deserted Corpse — giant spear area
    entities.append(make_entity("Item", 112 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse"),
        make_field("value", "Int", 400)]))
    # Mortician's Ashes — graveyard up from giant area
    entities.append(make_entity("Item", 116 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Mortician's Ashes")]))
    # Cleric Set (armor) — hut near graveyard
    entities.append(make_entity("Item", 118 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Cleric Set"),
        make_field("slot", "String", "Chest")]))
    # Blue Wooden Shield — same hut
    entities.append(make_entity("Item", 120 * 16, 64 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Blue Wooden Shield"),
        make_field("slot", "String", "Hands")]))
    # Undead Bone Shard — jump across gap near giant
    entities.append(make_entity("Item", 114 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "UndeadBoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    # Great Scythe — jump to ledge in building
    entities.append(make_entity("Item", 124 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Great Scythe")]))
    # Homeward Bone — Pit of Hollows
    entities.append(make_entity("Item", 90 * 16, 112 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Soul of a Deserted Corpse — lower path
    entities.append(make_entity("Item", 54 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse"),
        make_field("value", "Int", 200)]))
    # Titanite Shard — base of wall near Warriors of Sunlight
    entities.append(make_entity("Item", 50 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))

    # --- Chests (DS3 Undead Settlement) ---
    # Human Pine Resin x4 — chest in Fire Demon area structures
    entities.append(make_entity("Chest", 96 * 16, 50 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Human Pine Resin"),
        make_field("is_mimic", "Bool", False)]))

    # --- Fog Gates ---
    entities.append(make_entity("FogGate", 148 * 16, 55 * 16, [
        make_field("dest_area", "String", "RoadOfSacrifices"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 10 * 16, 12 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 2080.0),
        make_field("dest_y", "Float", 1600.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # --- Lights ---
    entities.append(make_entity("Light", 18 * 16, 18 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 70 * 16, 56 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 100 * 16, 62 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 90 * 16, 106 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))

    # === ADDITIONAL INTERNAL STRUCTURES — Undead Settlement houses ===
    fill_tiles(chunk, TILE_WALL, 18, 38, 20, 42)
    fill_tiles(chunk, TILE_WALL, 28, 35, 30, 38)
    fill_tiles(chunk, TILE_WALL, 38, 40, 40, 42)
    fill_tiles(chunk, TILE_WALL, 22, 52, 24, 55)
    fill_tiles(chunk, TILE_WALL, 35, 48, 37, 50)
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 57)
    fill_tiles(chunk, TILE_WALL, 55, 50, 57, 52)
    fill_tiles(chunk, TILE_WALL, 15, 62, 17, 65)
    fill_tiles(chunk, TILE_WALL, 28, 65, 30, 68)
    fill_tiles(chunk, TILE_WALL, 42, 62, 44, 65)
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 62)
    fill_tiles(chunk, TILE_WALL, 68, 55, 70, 58)
    fill_tiles(chunk, TILE_WALL, 78, 52, 80, 55)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  UndeadSettlement (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "UndeadSettlement", chunk, entities


def make_road_of_sacrifices():
    """Road of Sacrifices - dark forest with Crucifixion Woods hub.
    Faithful DS3 layout: narrow entry woods -> Halfway Fortress -> wide woods
    -> Corvian forest -> Crystal Sage cave. Branches to Farron Keep and Cathedral.
    Design doc: 3200x2400, sections define the progression west-to-east.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Entry dark woods (top-left) - doc: x=0,y=0,w=800,h=800
    # Narrow forest path with root obstacles, player enters from Undead Settlement
    # ================================================================
    carve_ellipse(chunk, 18, 18, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 14, 16, 40, 28)
    # Tree root obstacles
    fill_tiles(chunk, TILE_WALL, 20, 20, 22, 22)
    fill_tiles(chunk, TILE_WALL, 32, 24, 34, 26)

    # ================================================================
    # SECTION 2: Halfway Fortress - doc: x=1000,y=500,w=500,h=500
    # Ruined stone fortress with Anri and Horace, interior rooms
    # ================================================================
    carve_ellipse(chunk, 52, 28, 12, 10)
    # Stone walls creating fortress rooms
    fill_tiles(chunk, TILE_WALL, 48, 24, 49, 30)
    fill_tiles(chunk, TILE_WALL, 56, 26, 57, 32)
    # Corridor connecting entry to fortress
    fill_tiles(chunk, TILE_GROUND, 38, 22, 52, 30)

    # ================================================================
    # SECTION 3: Crucifixion Woods - doc: x=1700,y=300,w=600,h=500
    # Wide wetland forest with branching paths, large central hub
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 50, 35, 110, 75)
    # Large tree root clusters as wall obstacles
    fill_tiles(chunk, TILE_WALL, 58, 42, 62, 46)
    fill_tiles(chunk, TILE_WALL, 78, 50, 82, 54)
    fill_tiles(chunk, TILE_WALL, 95, 40, 99, 44)
    fill_tiles(chunk, TILE_WALL, 68, 62, 72, 66)
    fill_tiles(chunk, TILE_WALL, 88, 65, 92, 69)

    # ================================================================
    # SECTION 4: Corvian Forest - doc: x=2200,y=800,w=600,h=600
    # Dense forest toward Crystal Sage, Black Knight patrols here
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 75, 130, 110)
    # Dense tree clusters
    fill_tiles(chunk, TILE_WALL, 95, 82, 98, 85)
    fill_tiles(chunk, TILE_WALL, 115, 90, 118, 93)
    fill_tiles(chunk, TILE_WALL, 100, 100, 103, 103)
    fill_tiles(chunk, TILE_WALL, 120, 78, 123, 81)

    # ================================================================
    # SECTION 5: Crystal Sage cave - doc: x=2300,y=1200,w=800,h=600
    # Boss arena: open rocky cave with crystal obstacles
    # ================================================================
    carve_ellipse(chunk, 130, 120, 20, 18)
    # Crystal obstacles inside the cave
    fill_tiles(chunk, TILE_WALL, 122, 114, 124, 116)
    fill_tiles(chunk, TILE_WALL, 138, 126, 140, 128)
    fill_tiles(chunk, TILE_WALL, 125, 130, 127, 132)
    # Corridor from Corvian Forest to Crystal Sage
    fill_tiles(chunk, TILE_GROUND, 120, 108, 135, 118)

    # ================================================================
    # BRANCH: Path south to Farron Keep
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 62, 72, 74, 135)
    carve_ellipse(chunk, 68, 132, 10, 8)

    # ================================================================
    # BRANCH: Path east to Cathedral Deep
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 108, 60, 120, 70)
    carve_ellipse(chunk, 118, 65, 8, 6)

    # ================================================================
    # Connection corridors to ensure flow
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 42, 30, 55, 38)

    # --- ENTITIES ---
    spawn_px, spawn_py = 18 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 18 * 16, 18 * 16))    # Road of Sacrifices entry
    entities.append(make_entity("Bonfire", 52 * 16, 30 * 16))    # Halfway Fortress
    entities.append(make_entity("Bonfire", 80 * 16, 45 * 16))    # Crucifixion Woods
    entities.append(make_entity("Bonfire", 130 * 16, 115 * 16))  # Crystal Sage

    # Boss - Crystal Sage
    entities.append(make_entity("BossSpawn", 130 * 16, 112 * 16))

    # Enemies - DS3 faithful: Corvians in woods, Lycanthropes near fortress, Black Knight near Farron Coal
    # Corvians (Assassin closest match — winged hollow enemies), Corvian Storytellers (DarkMage),
    # Lycanthrope Hunters (Knight), Lycanthropes (StarvedHound), Dogs, Crabs (GiantSlave closest)
    enemy_data = [
        # Entry dark woods — Corvians (winged hollows) patrolling the path
        ("Assassin", 25, 20), ("Assassin", 35, 24),
        ("Dog", 28, 22),                                          # Dogs ambush near entry
        # Near Halfway Fortress — Lycanthropes (large beast enemies)
        ("StarvedHound", 42, 26), ("StarvedHound", 48, 28),
        # Crucifixion Woods — Corvians and Corvian Storytellers
        ("Assassin", 56, 35), ("Assassin", 62, 40),               # Corvians in woods
        ("DarkMage", 70, 48),                                      # Corvian Storyteller (casts poison mist)
        ("DarkMage", 88, 55),                                      # Corvian Storyteller
        ("Assassin", 75, 52), ("Assassin", 82, 58),               # More Corvians
        ("Knight", 72, 55), ("Knight", 85, 60),                   # Lycanthrope Hunters (spear wielders)
        ("CrystalLizard", 50, 26),                                 # Fortress crystal lizard
        # Swamp area — Poisonhorn Bugs (poison mist mushrooms in lower woods)
        ("PoisonhornBug", 65, 62), ("PoisonhornBug", 70, 65),
        ("PoisonhornBug", 62, 70), ("PoisonhornBug", 58, 68),
        # Swamp area — Lesser Crabs and Great Crab
        ("GiantSlave", 76, 70),                                    # Great Crab in swamp (drops Great Swamp Ring)
        ("LesserCrab", 78, 68), ("LesserCrab", 80, 72),                    # Lesser Crabs in swamp
        # Black Knight guarding Farron Coal in ruins
        ("BlackKnight", 108, 85),
        # Corvian forest — more Corvians and Storytellers
        ("Assassin", 118, 88), ("Assassin", 122, 92), ("Assassin", 125, 96),
        # Crystal Sage cave — hollow sorcerers
        ("DarkMage", 125, 115), ("DarkMage", 135, 118),
        # South path toward Farron Keep
        ("Assassin", 68, 80), ("Assassin", 72, 85),
        ("StarvedHound", 110, 95), ("StarvedHound", 115, 100),    # Lycanthropes
        ("Archer", 100, 78), ("Archer", 120, 82),                 # Corvian archers
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Road of Sacrifices) — accurate from wiki ---
    # Shriving Stone — end of left path in entry woods
    entities.append(make_entity("Item", 30 * 16, 22 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Shriving Stone")]))
    # Soul of an Unknown Traveler — overturned coach in entry woods
    entities.append(make_entity("Item", 22 * 16, 20 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler"),
        make_field("value", "Int", 500)]))
    # Brigand Axe — ledge below entry path
    entities.append(make_entity("Item", 28 * 16, 25 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Brigand Axe")]))
    # Brigand Set — end of lower entry path
    entities.append(make_entity("Item", 26 * 16, 28 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Brigand Set"),
        make_field("slot", "String", "Chest")]))
    # Brigand Twindaggers — very end of entry path
    entities.append(make_entity("Item", 26 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Brigand Twindaggers")]))
    # Titanite Shard — cavern path along cliff
    entities.append(make_entity("Item", 38 * 16, 26 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Braille Divine Tome of Carim — ledge with dogs ambush
    entities.append(make_entity("Item", 40 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Braille Divine Tome of Carim")]))
    # Morne's Ring — same ledge area as tome
    entities.append(make_entity("Item", 42 * 16, 32 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Morne's Ring")]))
    # Ember — mound near storyteller at Halfway Fortress
    entities.append(make_entity("Item", 52 * 16, 32 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # Blue Sentinels Covenant — from Horace at Halfway Fortress
    entities.append(make_entity("Item", 55 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Blue Sentinels")]))
    # Titanite Shard — near poison brumers in woods
    entities.append(make_entity("Item", 60 * 16, 42 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Titanite Shard — near crosses in woods
    entities.append(make_entity("Item", 64 * 16, 45 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Twin Dragon Greatshield — base of tree in woods
    entities.append(make_entity("Item", 68 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Twin Dragon Greatshield"),
        make_field("slot", "String", "Hands")]))
    # Fading Soul — in the woods area
    entities.append(make_entity("Item", 70 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Fading Soul"),
        make_field("value", "Int", 50)]))
    # Estus Shard — drop down from ledges in woods
    entities.append(make_entity("Item", 52 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    # Ember — blazing fire with crucified hollows
    entities.append(make_entity("Item", 62 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # Soul of an Unknown Traveler — drop from ledge near bonfire
    entities.append(make_entity("Item", 55 * 16, 42 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler"),
        make_field("value", "Int", 500)]))
    # Heretic's Staff — under overhang in ruins
    entities.append(make_entity("Item", 90 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Heretic's Staff")]))
    # Blue Bug Pellet — near Orbeck's room
    entities.append(make_entity("Item", 82 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Blue Bug Pellet")]))
    # Blue Bug Pellet — second pellet in ruins
    entities.append(make_entity("Item", 88 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Blue Bug Pellet")]))
    # Ring of Sacrifice — ledge drop in ruins
    entities.append(make_entity("Item", 92 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Ring of Sacrifice")]))
    # Sorcerer Set — flooded room below ruins
    entities.append(make_entity("Item", 95 * 16, 65 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Sorcerer Set"),
        make_field("slot", "String", "Chest")]))
    # Sage Ring — flooded room below ruins
    entities.append(make_entity("Item", 95 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Sage Ring")]))
    # Crystal Gem — ruins upper area
    entities.append(make_entity("Item", 98 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Crystal Gem")]))
    # Twinkling Titanite — in ruins
    entities.append(make_entity("Item", 100 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Twinkling Titanite")]))
    # Twinkling Titanite — in ruins
    entities.append(make_entity("Item", 100 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Twinkling Titanite")]))
    # Green Blossom — swamp edge
    entities.append(make_entity("Item", 75 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Green Blossom")]))
    # Green Blossom — swamp area near crabs
    entities.append(make_entity("Item", 80 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Green Blossom")]))
    # Green Blossom — swamp area
    entities.append(make_entity("Item", 72 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Green Blossom")]))
    # Green Blossom — swamp area
    entities.append(make_entity("Item", 85 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Green Blossom")]))
    # Grass Crest Shield — before giant crab at tree base
    entities.append(make_entity("Item", 72 * 16, 70 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Grass Crest Shield"),
        make_field("slot", "String", "Hands")]))
    # Fallen Knight Set — in the swamp
    entities.append(make_entity("Item", 78 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Fallen Knight Set"),
        make_field("slot", "String", "Chest")]))
    # Titanite Shard — swamp area
    entities.append(make_entity("Item", 95 * 16, 70 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Great Club — Exile NPC drop at Farron Keep entrance
    entities.append(make_entity("Item", 110 * 16, 90 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Great Club")]))
    # Exile Greatsword — Exile NPC drop at Farron Keep entrance
    entities.append(make_entity("Item", 115 * 16, 95 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Exile Greatsword")]))
    # Homeward Bone — corpse in Farron Keep castle
    entities.append(make_entity("Item", 112 * 16, 92 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Homeward Bone — corpse in Farron Keep castle
    entities.append(make_entity("Item", 114 * 16, 93 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Golden Falcon Shield — ledge drop near Farron entrance
    entities.append(make_entity("Item", 105 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Golden Falcon Shield"),
        make_field("slot", "String", "Hands")]))
    # Great Swamp Pyromancy Tome — base of large tree in swamp
    entities.append(make_entity("Item", 90 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Great Swamp Pyromancy Tome")]))
    # Conjurator Set — near pyromancy tome area
    entities.append(make_entity("Item", 92 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Conjurator Set"),
        make_field("slot", "String", "Chest")]))
    # Farron Coal moved to Farron Keep (wiki: behind illusory wall near Old Wolf)
    # Sellsword Set — corpse in ruins near Farron Coal
    entities.append(make_entity("Item", 118 * 16, 88 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Sellsword Set"),
        make_field("slot", "String", "Chest")]))
    # Sellsword Twinblades — drop down in ruins
    entities.append(make_entity("Item", 120 * 16, 90 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Sellsword Twinblades")]))
    # Herald Set — past boss near fire
    entities.append(make_entity("Item", 130 * 16, 105 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Herald Set"),
        make_field("slot", "String", "Chest")]))
    # Titanite Shard — Crystal Sage area
    entities.append(make_entity("Item", 128 * 16, 110 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))

    # NPCs - Anri and Horace at Halfway Fortress (DS3: they sit together at the bonfire)
    entities.append(make_entity("Npc", 50 * 16, 30 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Hello|I am Anri of Astora|We are on a journey to find the Lords of Cinder")]))
    entities.append(make_entity("Npc", 54 * 16, 30 * 16, [make_field("name", "String", "Horace the Hushed"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#606060"), make_field("dialogue", "String", "...|...Anri is my companion|I will protect them")]))

    # Orbeck of Vinheim — sorcery teacher in the ruins (DS3: found in a side room of the Crucifixion Woods ruins)
    entities.append(make_entity("Npc", 82 * 16, 60 * 16, [make_field("name", "String", "Orbeck of Vinheim"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#7090B0"), make_field("dialogue", "String", "I am Orbeck of Vinheim|Bring me scrolls and I shall teach you sorceries")]))

    # Fog Gate to FarronKeep
    entities.append(make_entity("FogGate", 68 * 16, 134 * 16, [
        make_field("dest_area", "String", "FarronKeep"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Fog Gate to CathedralDeep
    entities.append(make_entity("FogGate", 120 * 16, 65 * 16, [
        make_field("dest_area", "String", "CathedralDeep"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights
    entities.append(make_entity("Light", 18 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.4), make_field("g", "Float", 0.5), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 52 * 16, 30 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 80 * 16, 45 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.5), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 130 * 16, 112 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.4), make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — forest terrain ===
    fill_tiles(chunk, TILE_WALL, 22, 25, 24, 28)
    fill_tiles(chunk, TILE_WALL, 38, 28, 40, 30)
    fill_tiles(chunk, TILE_WALL, 55, 22, 57, 24)
    fill_tiles(chunk, TILE_WALL, 30, 38, 32, 40)
    fill_tiles(chunk, TILE_WALL, 48, 42, 50, 44)
    fill_tiles(chunk, TILE_WALL, 65, 35, 67, 37)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 57)
    fill_tiles(chunk, TILE_WALL, 52, 58, 54, 60)
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 50)
    fill_tiles(chunk, TILE_WALL, 42, 68, 44, 70)
    fill_tiles(chunk, TILE_WALL, 60, 72, 62, 74)
    fill_tiles(chunk, TILE_WALL, 80, 55, 82, 57)
    fill_tiles(chunk, TILE_WALL, 25, 78, 27, 80)
    fill_tiles(chunk, TILE_WALL, 90, 65, 92, 67)
    fill_tiles(chunk, TILE_WALL, 118, 102, 120, 104)
    fill_tiles(chunk, TILE_WALL, 135, 108, 137, 110)
    fill_tiles(chunk, TILE_WALL, 125, 115, 127, 118)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  RoadOfSacrifices (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "RoadOfSacrifices", chunk, entities


def make_farron_keep():
    """Farron Keep - sprawling poison swamp with three torches.
    Faithful DS3 layout: entry highland -> poison swamp with torch platforms ->
    Keep Ruins center -> Old Wolf tower -> Abyss Watchers grand hall.
    Design doc: 4000x3600, swamp dominates center with torch islands.
    """
    chunk = new_chunk()

    # ================================================================
    # SECTION 1: Keep entry highland (top-left) - doc: x=0,y=0,w=600,h=600
    # Stone steps leading down into the swamp
    # ================================================================
    carve_ellipse(chunk, 15, 18, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 20, 25, 35)
    # Broken stone wall at entry
    fill_tiles(chunk, TILE_WALL, 10, 14, 12, 16)

    # ================================================================
    # SECTION 2: Outer poison swamp - vast POISON area
    # Three torch platforms scattered across the swamp
    # ================================================================
    carve_ellipse(chunk, 70, 70, 52, 48)
    # Convert much of the center to POISON tiles
    fill_tiles(chunk, TILE_POISON, 25, 35, 120, 110)

    # Left torch platform (NW) - doc: x=600,y=400,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 30, 30, 45, 42)
    fill_tiles(chunk, TILE_WALL, 34, 34, 36, 36)

    # Center torch platform (N) - doc: x=1600,y=800,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 60, 42, 78, 55)
    fill_tiles(chunk, TILE_WALL, 66, 46, 68, 48)

    # Right torch platform (NE) - doc: x=2400,y=600,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 88, 35, 105, 48)
    fill_tiles(chunk, TILE_WALL, 94, 38, 96, 40)

    # Path from entry into swamp (poison corridor)
    fill_tiles(chunk, TILE_POISON, 22, 30, 35, 45)

    # ================================================================
    # SECTION 3: Keep Ruins (center) - doc: x=1800,y=1600,w=500,h=400
    # Solid ground island with ruined walls, central bonfire hub
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 60, 60, 85, 80)
    fill_tiles(chunk, TILE_WALL, 65, 65, 68, 68)
    fill_tiles(chunk, TILE_WALL, 78, 72, 81, 75)
    fill_tiles(chunk, TILE_WALL, 70, 74, 72, 76)

    # ================================================================
    # SECTION 4: Old Wolf tower (south) - doc: x=1000,y=2200,w=400,h=500
    # High tower ruin accessed via ladder, covenant area
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 35, 95, 55, 115)
    carve_ellipse(chunk, 45, 105, 8, 7)
    # Tower walls
    fill_tiles(chunk, TILE_WALL, 38, 100, 40, 102)
    fill_tiles(chunk, TILE_WALL, 50, 108, 52, 110)

    # ================================================================
    # SECTION 5: Basilisk curse cave (west) - doc: x=400,y=1600,w=400,h=400
    # Dark cave with basilisks, hidden treasure
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 65, 38, 82)
    carve_ellipse(chunk, 28, 72, 7, 6)

    # ================================================================
    # SECTION 6: Darkwraith patrol zone (SE) - doc: x=2200,y=2000,w=600,h=600
    # Abyss knights patrol between swamp and boss arena approach
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 95, 80, 120, 105)
    fill_tiles(chunk, TILE_POISON, 98, 85, 115, 100)

    # ================================================================
    # SECTION 7: Grand stone gate corridor - doc: x=2800,y=2400,w=300,h=400
    # Long corridor lined with Abyss Watcher armor
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 120, 80, 135, 105)

    # ================================================================
    # SECTION 8: Abyss Watchers grand hall (far right) - doc: x=3000,y=2600,w=800,h=800
    # Large boss arena - grand stone hall with wolf crest
    # ================================================================
    carve_ellipse(chunk, 140, 115, 18, 16)
    fill_tiles(chunk, TILE_GROUND, 128, 105, 155, 130)

    # Connection corridors
    fill_tiles(chunk, TILE_GROUND, 55, 80, 65, 95)   # Ruins to Old Wolf
    fill_tiles(chunk, TILE_GROUND, 82, 75, 100, 85)   # Ruins to Darkwraith zone
    fill_tiles(chunk, TILE_GROUND, 115, 100, 128, 112) # Gate to arena

    entities = []

    spawn_px, spawn_py = 15 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 15 * 16, 18 * 16))     # Keep entry
    entities.append(make_entity("Bonfire", 72 * 16, 68 * 16))     # Keep Ruins
    entities.append(make_entity("Bonfire", 120 * 16, 94 * 16))    # Keep Perimeter
    entities.append(make_entity("Bonfire", 45 * 16, 105 * 16))    # Old Wolf
    entities.append(make_entity("Bonfire", 140 * 16, 118 * 16))   # Abyss Watchers

    # Boss - Abyss Watchers
    entities.append(make_entity("BossSpawn", 140 * 16, 112 * 16))

    # Enemies - DS3 faithful: Ghru (swamp), Elder Ghru (elite), Darkwraiths (abyss),
    # Basilisks (curse cave), Rotten Slugs (leeches), Great Crabs, Corvians, Crystal Lizards
    enemy_data = [
        # Left torch area — Ghru swarm (regular Ghru leap/gaunt variants)
        ("Ghru", 35, 45), ("Ghru", 40, 48), ("Ghru", 48, 50),
        # Center torch area — more Ghru
        ("Ghru", 68, 48), ("Ghru", 72, 52), ("Ghru", 75, 55),
        # Right torch area
        ("Ghru", 95, 42), ("Ghru", 100, 45),
        # Keep Ruins — Ghru and Ghru Shaman
        ("Ghru", 65, 72), ("Ghru", 72, 76), ("Ghru", 78, 70),
        ("DarkMage", 70, 74),                                        # Ghru Shaman (casts poison)
        # Darkwraith patrol — deep in swamp and near boss approach
        ("Darkwraith", 100, 88), ("Darkwraith", 108, 95),
        ("Darkwraith", 125, 108),                                    # Near arena gate
        # Basilisk curse cave (SE corner)
        ("Basilisk", 24, 70), ("Basilisk", 30, 75), ("Basilisk", 32, 68),
        # Rotten Slugs (leeches) in swamp water and around Old Wolf tower
        ("Rat", 42, 82), ("Rat", 45, 85), ("Rat", 50, 88),         # Rotten Slugs near leech building
        ("Rat", 48, 105), ("Rat", 52, 110),                         # Rotten Slugs at ladder base
        # Elder Ghru — elite horned beasts with tree weapons (Knight closest match)
        ("Knight", 55, 62), ("Knight", 60, 68), ("Knight", 58, 75), # Elder Ghru trio around Poison Gem
        ("Knight", 110, 100),                                        # Elder Ghru near gate
        # Great Crab in swamp (GiantSlave closest — large enemy)
        ("GiantSlave", 65, 62),                                      # Great Crab (drops Lingering Dragoncrest Ring)
        # Corvian and Corvian Storyteller in second half
        ("Assassin", 115, 95), ("Assassin", 120, 100),              # Corvians in second half
        ("DarkMage", 118, 98),                                       # Corvian Storyteller
        # Crystal Lizards — rare spawns
        ("CrystalLizard", 85, 82),                                   # Near gate
        ("CrystalLizard", 48, 112),                                  # Near Old Wolf tower
        # Stray Demon (DS3: optional mini-boss in Keep Ruins area, drops Soul of a Stray Demon)
        ("MiniBoss", 120, 98),                                    # Stray Demon
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Farron Keep) — accurate from wiki ---
    # Pyromancies / Spells / Key items
    entities.append(make_entity("Item", 22 * 16, 45 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Iron Flesh")]))
    entities.append(make_entity("Item", 25 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Golden Scroll")]))
    entities.append(make_entity("Item", 30 * 16, 55 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Sage's Coal")]))
    # Farron Coal — behind illusory wall near Old Wolf of Farron (wiki: Farron Keep)
    entities.append(make_entity("Item", 32 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Farron Coal")]))
    entities.append(make_entity("Item", 45 * 16, 100 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Dreamchaser's Ashes")]))
    entities.append(make_entity("Item", 110 * 16, 85 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Lightning Spear")]))
    entities.append(make_entity("Item", 55 * 16, 82 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Sage's Scroll")]))
    entities.append(make_entity("Item", 60 * 16, 78 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Poison Gem")]))
    entities.append(make_entity("Item", 75 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Great Magic Weapon")]))
    entities.append(make_entity("Item", 88 * 16, 48 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Atonement")]))
    # Wolf's Blood Swordgrass (covenant item on ground before ladder)
    entities.append(make_entity("Item", 42 * 16, 98 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Wolf's Blood Swordgrass")]))
    # Upgrade materials
    entities.append(make_entity("Item", 50 * 16, 85 * 16, [make_field("kind", "LocalEnum.ItemKind", "UndeadBoneShard"), make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 72 * 16, 70 * 16, [make_field("kind", "LocalEnum.ItemKind", "EstusShard"), make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 45 * 16, 108 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 55 * 16, 95 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 85 * 16, 82 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 48 * 16, 112 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 52 * 16, 95 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 58 * 16, 65 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Heavy Gem")]))
    entities.append(make_entity("Item", 62 * 16, 72 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Hollow Gem")]))
    # Weapons
    entities.append(make_entity("Item", 92 * 16, 44 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Greatsword")]))
    entities.append(make_entity("Item", 48 * 16, 115 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Greataxe")]))
    entities.append(make_entity("Item", 70 * 16, 56 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Sunlight Talisman")]))
    entities.append(make_entity("Item", 35 * 16, 62 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Black Bow of Pharis")]))
    entities.append(make_entity("Item", 40 * 16, 58 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Stone Parma"), make_field("slot", "String", "Hands")]))
    entities.append(make_entity("Item", 105 * 16, 55 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Dragon Crest Shield"), make_field("slot", "String", "Hands")]))
    # Rings
    entities.append(make_entity("Item", 28 * 16, 74 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Lingering Dragoncrest Ring")]))
    # Armor sets and pieces
    entities.append(make_entity("Item", 35 * 16, 50 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Dark Set"), make_field("slot", "String", "Chest")]))
    entities.append(make_entity("Item", 68 * 16, 95 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Crown of Dusk"), make_field("slot", "String", "Head")]))
    entities.append(make_entity("Item", 42 * 16, 65 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Ragged Mask"), make_field("slot", "String", "Head")]))
    entities.append(make_entity("Item", 50 * 16, 72 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Antiquated Set"), make_field("slot", "String", "Chest")]))
    entities.append(make_entity("Item", 32 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Pharis's Hat"), make_field("slot", "String", "Head")]))
    entities.append(make_entity("Item", 82 * 16, 55 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Nameless Knight Set"), make_field("slot", "String", "Chest")]))
    # Consumables
    entities.append(make_entity("Item", 105 * 16, 50 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 38 * 16, 50 * 16, [make_field("kind", "LocalEnum.ItemKind", "PurpleMoss"), make_field("name", "String", "Purple Moss Clump")]))
    entities.append(make_entity("Item", 38 * 16, 54 * 16, [make_field("kind", "LocalEnum.ItemKind", "PurpleMoss"), make_field("name", "String", "Purple Moss Clump")]))
    entities.append(make_entity("Item", 38 * 16, 58 * 16, [make_field("kind", "LocalEnum.ItemKind", "PurpleMoss"), make_field("name", "String", "Purple Moss Clump")]))
    entities.append(make_entity("Item", 48 * 16, 100 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 44 * 16, 96 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 65 * 16, 65 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Soul of a Nameless Soldier"), make_field("value", "Int", 800)]))
    entities.append(make_entity("Item", 78 * 16, 50 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Large Soul of a Nameless Soldier"), make_field("value", "Int", 1200)]))
    entities.append(make_entity("Item", 130 * 16, 108 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Soul of a Stray Demon"), make_field("value", "Int", 20000)]))
    # Shriving Stone (used for reverse weapon infusions)
    entities.append(make_entity("Item", 68 * 16, 78 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Shriving Stone")]))

    # NPC - Old Wolf of Farron
    entities.append(make_entity("Npc", 45 * 16, 103 * 16, [make_field("name", "String", "Old Wolf of Farron"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#8899AA"), make_field("dialogue", "String", "(The wolf gazes silently|Its eyes reflect distant flames)")]))

    # NPC - Hawkwood (event: he meditates at Farron Keep, relating to Abyss Watchers)
    entities.append(make_entity("Npc", 68 * 16, 72 * 16, [make_field("name", "String", "Hawkwood"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#8B7355"), make_field("dialogue", "String", "The Undead Legion used to be around here|They were a fierce bunch|They linked the fire long ago")]))

    # Fog Gate to CatacombsOfCarthus
    entities.append(make_entity("FogGate", 140 * 16, 130 * 16, [
        make_field("dest_area", "String", "CatacombsOfCarthus"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # No chests in Farron Keep per DS3 wiki — all items are ground pickups

    # Lights - torch fires and bonfire glow
    entities.append(make_entity("Light", 15 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 37 * 16, 36 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 69 * 16, 48 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 96 * 16, 40 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 72 * 16, 68 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 45 * 16, 105 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 140 * 16, 112 * 16, [make_field("radius", "Float", 220.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.5), make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — Farron Keep swamp ===
    # Torch platforms, ruined walls, swamp debris
    fill_tiles(chunk, TILE_WALL, 25, 35, 27, 38)
    fill_tiles(chunk, TILE_WALL, 40, 42, 42, 44)
    fill_tiles(chunk, TILE_WALL, 55, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 44)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 58)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)
    fill_tiles(chunk, TILE_WALL, 65, 55, 67, 57)
    fill_tiles(chunk, TILE_WALL, 80, 50, 82, 52)
    fill_tiles(chunk, TILE_WALL, 45, 72, 47, 74)
    fill_tiles(chunk, TILE_WALL, 60, 75, 62, 77)
    fill_tiles(chunk, TILE_WALL, 75, 68, 77, 70)
    fill_tiles(chunk, TILE_WALL, 90, 60, 92, 62)
    fill_tiles(chunk, TILE_WALL, 100, 68, 102, 70)
    fill_tiles(chunk, TILE_WALL, 110, 75, 112, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 122, 82)
    fill_tiles(chunk, TILE_WALL, 130, 85, 132, 88)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  FarronKeep (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "FarronKeep", chunk, entities


def make_cathedral_deep():
    """Cathedral of the Deep - vertical labyrinth from cemetery to Rosaria's bedchamber.
    Faithful DS3 layout: cemetery entry -> outer graveyard -> Cleansing Chapel ->
    cathedral side aisles -> cathedral nave -> Giant room -> Deacon altar hall ->
    slug corridor -> Rosaria's bedchamber. Connected by spine corridor along x=80.
    Design doc: 4000x3600, 11 sections forming a vertical descent.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Cemetery entry (top) - doc: x=0,y=0,w=600,h=600
    # Flooded graveyard with tombstones, Cathedral Knights patrol
    # ================================================================
    carve_ellipse(chunk, 30, 10, 12, 8)
    fill_tiles(chunk, TILE_GROUND, 22, 4, 42, 18)
    # Tombstone obstacles
    fill_tiles(chunk, TILE_WALL, 26, 7, 27, 9)
    fill_tiles(chunk, TILE_WALL, 36, 8, 37, 10)

    # ================================================================
    # SECTION 2: Outer graveyard - doc: x=600,y=500,w=700,h=600
    # Wide cemetery with dead trees, muddy paths, Deep Accursed spider
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 18, 20, 52, 38)
    # Tombstone clusters
    fill_tiles(chunk, TILE_WALL, 24, 24, 26, 26)
    fill_tiles(chunk, TILE_WALL, 38, 28, 40, 30)
    fill_tiles(chunk, TILE_WALL, 30, 32, 32, 34)
    # Corridor from entry to graveyard
    fill_tiles(chunk, TILE_GROUND, 32, 16, 38, 22)

    # ================================================================
    # SECTION 3: Cleansing Chapel - doc: x=200,y=300,w=400,h=300
    # Small church with bonfire and NPCs, supply station
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 38, 42, 52)
    carve_ellipse(chunk, 32, 44, 10, 6)
    # Chapel walls creating interior
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 42)
    fill_tiles(chunk, TILE_WALL, 36, 40, 37, 42)
    # Corridor from graveyard to chapel
    fill_tiles(chunk, TILE_GROUND, 28, 36, 36, 40)

    # ================================================================
    # SECTION 4: Cathedral front gate - doc: x=1200,y=800,w=500,h=400
    # Grand locked front door, heavy Cathedral Knight guards
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 44, 48, 60, 58)
    fill_tiles(chunk, TILE_WALL, 48, 50, 49, 52)
    fill_tiles(chunk, TILE_WALL, 55, 50, 56, 52)
    # Corridor from chapel to gate
    fill_tiles(chunk, TILE_GROUND, 36, 50, 46, 54)

    # ================================================================
    # SECTION 5: Cathedral side aisle - doc: x=1500,y=900,w=400,h=500
    # Narrow dark corridor with thrall ambush points
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 56, 55, 70, 72)
    fill_tiles(chunk, TILE_WALL, 60, 58, 61, 60)
    fill_tiles(chunk, TILE_WALL, 65, 64, 66, 66)

    # ================================================================
    # SECTION 6: Cathedral nave/atrium - doc: x=1300,y=1000,w=600,h=500
    # Open-air courtyard connecting multiple passages and shortcuts
    # Patches kicks player into Giant room from here
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 38, 68, 65, 84)
    carve_ellipse(chunk, 52, 75, 12, 7)
    # Column obstacles
    fill_tiles(chunk, TILE_WALL, 44, 72, 45, 74)
    fill_tiles(chunk, TILE_WALL, 58, 78, 59, 80)

    # ================================================================
    # SECTION 7: Upper gallery - doc: x=1600,y=800,w=600,h=400
    # Ring corridor overlooking the nave, evangelists and knights
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 62, 58, 80, 70)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 64)
    fill_tiles(chunk, TILE_WALL, 74, 64, 75, 66)
    # Corridor from nave to upper gallery
    fill_tiles(chunk, TILE_GROUND, 58, 65, 64, 70)

    # ================================================================
    # SECTION 8: Well / drop area - doc: x=1400,y=1300,w=200,h=200
    # Area where Patches kicks player down into Giant room
    # ================================================================
    carve_ellipse(chunk, 58, 85, 5, 4)

    # ================================================================
    # SECTION 9: Giant room - doc: spans large area
    # Two giant slaves, dangerous open area
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 35, 86, 68, 104)
    # Pillar obstacles
    fill_tiles(chunk, TILE_WALL, 42, 90, 44, 92)
    fill_tiles(chunk, TILE_WALL, 55, 95, 57, 97)
    fill_tiles(chunk, TILE_WALL, 48, 100, 50, 102)
    # Corridor from nave to giant room
    fill_tiles(chunk, TILE_GROUND, 45, 82, 55, 88)

    # ================================================================
    # SECTION 10: Deacon altar hall - doc: x=1800,y=1600,w=700,h=500
    # Boss arena: wide hall packed with deacons
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 25, 105, 65, 132)
    carve_ellipse(chunk, 45, 118, 18, 14)
    # Corridor from giant room to deacon hall
    fill_tiles(chunk, TILE_GROUND, 40, 102, 52, 108)

    # ================================================================
    # SECTION 11: Slug corridor - doc: x=2600,y=2000,w=400,h=400
    # Dark corridor with ManGrubs crawling on walls
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 28, 132, 48, 144)
    # Corridor from deacon hall to slug corridor
    fill_tiles(chunk, TILE_GROUND, 32, 130, 42, 134)

    # ================================================================
    # SECTION 12: Rosaria's Bedchamber - doc: x=3000,y=2200,w=400,h=400
    # Ornate bedroom with Rosaria, covenant area
    # ================================================================
    carve_ellipse(chunk, 38, 150, 10, 7)
    fill_tiles(chunk, TILE_GROUND, 30, 145, 48, 156)
    # Corridor from slug to bedchamber
    fill_tiles(chunk, TILE_GROUND, 32, 142, 42, 148)

    # --- ENTITIES ---
    spawn_px, spawn_py = 30 * 16, 8 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3: Cathedral of the Deep, Cleansing Chapel, Deacons of the Deep, Rosaria's Bed Chamber
    entities.append(make_entity("Bonfire", 30 * 16, 8 * 16))       # Cathedral of the Deep (entry)
    entities.append(make_entity("Bonfire", 32 * 16, 44 * 16))      # Cleansing Chapel
    entities.append(make_entity("Bonfire", 45 * 16, 124 * 16))     # Deacons of the Deep (boss arena)
    entities.append(make_entity("Bonfire", 38 * 16, 150 * 16))     # Rosaria's Bed Chamber

    # Boss - Deacons of the Deep
    entities.append(make_entity("BossSpawn", 45 * 16, 114 * 16))

    # Enemies (DS3 Cathedral of the Deep: Cathedral Knights, Thralls/Hollow Slaves,
    # Evangelists, Deacons, Infested Corpses, Reanimated Corpses, Devout Hollows,
    # Writhing Rotten Flesh, Cage Spiders, Man-grubs, Deep Accursed, Mimic,
    # Longfinger Kirk invader, Starved Hounds, Corpse-grubs, Crystal Lizards,
    # Cathedral Grave Wardens, Ravenous Crystal Lizards)
    enemy_data = [
        # Cemetery entry — Infested Corpses among the graves (DS3: 4-5 infested corpses)
        ("InfestedCorpse", 28, 6), ("InfestedCorpse", 34, 8),
        ("InfestedCorpse", 25, 10), ("InfestedCorpse", 35, 12),
        ("CrystalLizard", 38, 4),                                     # Ravenous Crystal Lizard
        # Outer graveyard — Cathedral Knights, Starved Hounds, Grave Wardens
        ("CathedralKnight", 40, 16), ("CathedralKnight", 45, 20),    # Cathedral Knight patrols
        ("InfestedCorpse", 30, 28), ("InfestedCorpse", 36, 30),      # Graveyard corpses
        ("StarvedHound", 22, 24), ("StarvedHound", 26, 28),                   # DS3: Starved Hounds prowl the graveyard
        ("CathedralGraveWarden", 34, 26), ("CathedralGraveWarden", 38, 32),         # DS3: dual-wielding grave wardens
        # Cleansing Chapel — Evangelist guards bonfire area
        ("Evangelist", 34, 42),
        ("PeasantHollow", 28, 40),                                    # Reanimated Corpse near chapel
        # Side aisle — Thralls/Hollow Slaves ambush from above (DS3: drop from ceiling)
        ("Thrall", 60, 60), ("Thrall", 64, 65), ("Thrall", 68, 62),
        ("Thrall", 62, 68),                                           # Extra thrall in dark corner
        ("PeasantHollow", 58, 64),                                    # Devout Hollow in side aisle
        # Gate area — Cathedral Knights guard locked door
        ("CathedralKnight", 48, 54), ("CathedralKnight", 52, 56),
        ("Evangelist", 46, 50),                                       # Evangelist near gate
        # Nave — heavy knight and evangelist presence (DS3: multiple knight patrols)
        ("CathedralKnight", 50, 70), ("CathedralKnight", 55, 72),
        ("Evangelist", 42, 74),                                       # Evangelist in nave corner
        ("Thrall", 48, 76), ("Thrall", 56, 78),                       # Thrall ambush in nave
        ("Thrall", 52, 73), ("Thrall", 58, 75), ("Thrall", 54, 77),       # DS3: rafter ambush (3 thralls on curved rafters)
        # Upper gallery — Evangelists and knights
        ("Evangelist", 66, 64), ("Evangelist", 72, 68),
        ("CathedralKnight", 70, 62),                                  # Gallery guard
        ("InfestedCorpse", 76, 66),                                   # Corpse in gallery
        # Deep Accursed — lurks in side room (DS3: giant spider enemy near entrance shortcut)
        ("DeepAccursed", 22, 38),
        # Writhing Rotten Flesh in swampy area near giant room
        ("Rat", 38, 86), ("Rat", 42, 88),                             # Writhing Rotten Flesh
        ("InfestedCorpse", 38, 86), ("InfestedCorpse", 42, 88),                   # DS3: Writhing Rotten Flesh
        ("GiantSlave", 44, 92), ("GiantSlave", 56, 98),
        ("CathedralKnight", 48, 88), ("CathedralKnight", 52, 96),
        ("Evangelist", 40, 96),
        ("Thrall", 46, 100), ("Thrall", 54, 102),
        # Cage Spider area (DS3: basilisks in dark room near giant)
        ("Basilisk", 36, 94), ("Basilisk", 40, 98),                   # Cage Spiders
        # Deacon hall — mass of Deacons before the boss (DS3: dozens of deacons)
        ("Deacon", 38, 110), ("Deacon", 42, 108), ("Deacon", 48, 112),
        ("Deacon", 52, 116), ("Deacon", 56, 114), ("Deacon", 40, 118),
        ("Deacon", 45, 122), ("Deacon", 50, 124),
        ("Deacon", 55, 120), ("Deacon", 35, 124),
        ("Deacon", 58, 118), ("Deacon", 32, 120),                     # More deacons
        ("CathedralKnight", 60, 110),                                 # Deacon hall guard
        ("CathedralGraveWarden", 58, 106), ("CathedralGraveWarden", 62, 108),   # DS3: 2 grave wardens before Deacon stairs
        # Slug corridor to Rosaria — Man-grubs (DS3: 4-5 along the corridor)
        ("ManGrub", 34, 135), ("ManGrub", 38, 138),
        ("ManGrub", 42, 140), ("ManGrub", 36, 142),
        ("ManGrub", 40, 144),                                         # Extra man-grub near Rosaria
        # Longfinger Kirk invasion (DS3: dark spirit invader in cathedral, Darkwraith closest match)
        ("Darkwraith", 64, 70),                                       # Longfinger Kirk (wears Dark Set)
        # Mimic in upper gallery handled as Chest entity below
        # Corpse-grubs near deacon hall entrance
        ("InfestedCorpse", 30, 108), ("InfestedCorpse", 28, 114),     # Corpse-grubs
        # Crystal Lizard near nave
        ("CrystalLizard", 60, 76),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Cathedral of the Deep) — accurate from wiki ---
    # Cemetery / approach area
    entities.append(make_entity("Item", 28 * 16, 6 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Fading Soul"), make_field("value", "Int", 50)]))
    entities.append(make_entity("Item", 30 * 16, 35 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Paladin's Ashes")]))
    # Outer graveyard
    entities.append(make_entity("Item", 28 * 16, 26 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 45 * 16, 32 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Large Soul of an Unknown Traveler"), make_field("value", "Int", 800)]))
    entities.append(make_entity("Item", 42 * 16, 30 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Crest Shield"), make_field("slot", "String", "Hands")]))
    entities.append(make_entity("Item", 44 * 16, 36 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Astora Greatsword")]))
    entities.append(make_entity("Item", 46 * 16, 34 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Executioner's Greatsword")]))
    entities.append(make_entity("Item", 26 * 16, 28 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Fading Soul"), make_field("value", "Int", 50)]))
    # Cleansing Chapel
    entities.append(make_entity("Item", 40 * 16, 22 * 16, [make_field("kind", "LocalEnum.ItemKind", "EstusShard"), make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 38 * 16, 42 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Notched Whip")]))
    # Graveyard paths
    entities.append(make_entity("Item", 48 * 16, 40 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 50 * 16, 42 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Large Soul of an Unknown Traveler"), make_field("value", "Int", 800)]))
    entities.append(make_entity("Item", 52 * 16, 44 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Repair Powder")]))
    entities.append(make_entity("Item", 54 * 16, 46 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Repair Powder")]))
    entities.append(make_entity("Item", 56 * 16, 48 * 16, [make_field("kind", "LocalEnum.ItemKind", "UndeadBoneShard"), make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 58 * 16, 50 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 60 * 16, 52 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Curse Ward Greatshield"), make_field("slot", "String", "Hands")]))
    entities.append(make_entity("Item", 62 * 16, 54 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 64 * 16, 56 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Saint-tree Bellvine")]))
    entities.append(make_entity("Item", 36 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Poisonbite Ring")]))
    # Cathedral interior
    entities.append(make_entity("Item", 50 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 52 * 16, 62 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 66 * 16, 58 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 68 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 54 * 16, 64 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Soul of an Unknown Traveler"), make_field("value", "Int", 500)]))
    entities.append(make_entity("Item", 56 * 16, 66 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 70 * 16, 62 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Undead Hunter Charm")]))
    entities.append(make_entity("Item", 58 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Soul of a Nameless Soldier"), make_field("value", "Int", 800)]))
    entities.append(make_entity("Item", 60 * 16, 70 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 62 * 16, 72 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Duel Charm")]))
    entities.append(make_entity("Item", 64 * 16, 74 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Duel Charm")]))
    # Giant room
    entities.append(make_entity("Item", 44 * 16, 94 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 46 * 16, 96 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Seek Guidance")]))
    entities.append(make_entity("Item", 48 * 16, 98 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Lloyd's Sword Ring")]))
    entities.append(make_entity("Item", 50 * 16, 100 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Deep Braille Divine Tome")]))
    entities.append(make_entity("Item", 52 * 16, 90 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Drang Set"), make_field("slot", "String", "Chest")]))
    # Pale Tongue removed (duplicate — wiki says 1x for Cathedral of the Deep)
    entities.append(make_entity("Item", 40 * 16, 102 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Maiden Set"), make_field("slot", "String", "Chest")]))
    entities.append(make_entity("Item", 42 * 16, 104 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 44 * 16, 106 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Duel Charm")]))
    entities.append(make_entity("Item", 46 * 16, 108 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Duel Charm")]))
    entities.append(make_entity("Item", 48 * 16, 110 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 50 * 16, 112 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 52 * 16, 114 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 54 * 16, 116 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 56 * 16, 118 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 58 * 16, 120 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 42 * 16, 122 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    # Deep Accursed area
    entities.append(make_entity("Item", 24 * 16, 40 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Aldrich's Sapphire")]))
    # Rafter / upper areas
    entities.append(make_entity("Item", 72 * 16, 66 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Deep Ring")]))
    entities.append(make_entity("Item", 74 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Red Sign Soapstone")]))
    entities.append(make_entity("Item", 76 * 16, 70 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Pale Tongue")]))
    entities.append(make_entity("Item", 78 * 16, 72 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Blessed Gem")]))
    entities.append(make_entity("Item", 70 * 16, 64 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Arbalest")]))
    entities.append(make_entity("Item", 68 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Drang Hammers")]))
    # Rosaria's Bedchamber
    entities.append(make_entity("Item", 38 * 16, 136 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Saint Bident")]))
    entities.append(make_entity("Item", 40 * 16, 138 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 42 * 16, 140 * 16, [make_field("kind", "LocalEnum.ItemKind", "HomewardBone"), make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 36 * 16, 142 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Small Doll")]))
    entities.append(make_entity("Item", 34 * 16, 148 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Armor of Thorns"), make_field("slot", "String", "Chest")]))
    entities.append(make_entity("Item", 38 * 16, 152 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Archdeacon Set"), make_field("slot", "String", "Chest")]))
    # Longfinger Kirk invasion drops
    entities.append(make_entity("Item", 62 * 16, 72 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Barbed Straight Sword")]))
    entities.append(make_entity("Item", 64 * 16, 74 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Spiked Shield"), make_field("slot", "String", "Hands")]))
    # Consumables scattered through walkthrough
    entities.append(make_entity("Item", 22 * 16, 20 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Repair Powder")]))
    # Titanite Shard removed (duplicate — wiki says 2x for Cathedral of the Deep)
    entities.append(make_entity("Item", 66 * 16, 76 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 68 * 16, 78 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Twinkling Titanite")]))

    # NPCs - DS3 Cathedral of the Deep: Patches, Rosaria
    entities.append(make_entity("Npc", 52 * 16, 78 * 16, [make_field("name", "String", "Patches"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#808080"), make_field("dialogue", "String", "What's the matter?|You fell for it!")]))
    entities.append(make_entity("Npc", 38 * 16, 148 * 16, [make_field("name", "String", "Rosaria"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D0A0B0"), make_field("dialogue", "String", "Welcome|I am Rosaria, Mother of Rebirth")]))
    # Siegward of Catarina — stuck in the well outside Cathedral (DS3: freed via lift mechanism)
    entities.append(make_entity("Npc", 24 * 16, 56 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A060"), make_field("dialogue", "String", "Aah, hello|I seem to be stuck in this well|Could you find a way to get me out?")]))

    # Chests - DS3 Cathedral of the Deep: Mimic in rafters drops Lightning Stake
    entities.append(make_entity("Chest", 74 * 16, 60 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Lightning Stake"),
        make_field("is_mimic", "Bool", True)]))

    # Fog Gate to Irithyll
    entities.append(make_entity("FogGate", 38 * 16, 154 * 16, [
        make_field("dest_area", "String", "Irithyll"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights
    entities.append(make_entity("Light", 30 * 16, 8 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.5), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 32 * 16, 44 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 52 * 16, 75 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.3), make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 45 * 16, 114 * 16, [make_field("radius", "Float", 220.0), make_field("r", "Float", 0.4), make_field("g", "Float", 0.2), make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.45)]))
    entities.append(make_entity("Light", 38 * 16, 150 * 16, [make_field("radius", "Float", 150.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.4), make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — Cathedral of the Deep ===
    # Cathedral pillars, pews, altar stones
    fill_tiles(chunk, TILE_WALL, 18, 22, 20, 25)
    fill_tiles(chunk, TILE_WALL, 30, 28, 32, 30)
    fill_tiles(chunk, TILE_WALL, 42, 22, 44, 24)
    fill_tiles(chunk, TILE_WALL, 55, 30, 57, 32)
    fill_tiles(chunk, TILE_WALL, 25, 42, 27, 44)
    fill_tiles(chunk, TILE_WALL, 38, 48, 40, 50)
    fill_tiles(chunk, TILE_WALL, 50, 42, 52, 44)
    fill_tiles(chunk, TILE_WALL, 62, 50, 64, 52)
    fill_tiles(chunk, TILE_WALL, 35, 62, 37, 64)
    fill_tiles(chunk, TILE_WALL, 48, 68, 50, 70)
    fill_tiles(chunk, TILE_WALL, 60, 62, 62, 64)
    fill_tiles(chunk, TILE_WALL, 72, 55, 74, 57)
    fill_tiles(chunk, TILE_WALL, 40, 82, 42, 84)
    fill_tiles(chunk, TILE_WALL, 55, 88, 57, 90)
    fill_tiles(chunk, TILE_WALL, 30, 100, 32, 102)
    fill_tiles(chunk, TILE_WALL, 45, 108, 47, 110)
    fill_tiles(chunk, TILE_WALL, 38, 130, 40, 132)
    fill_tiles(chunk, TILE_WALL, 50, 138, 52, 140)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  CathedralDeep (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "CathedralDeep", chunk, entities


def make_catacombs_of_carthus():
    """Catacombs of Carthus - underground tunnels with skeleton ball traps.
    Faithful DS3 layout: entry stairs -> skeleton ball corridor -> rope bridge ->
    lower tombs -> abandoned tomb -> Wolnir arena. Side path to Smouldering Lake.
    Design doc: 3600x3200, tight underground corridors with multiple levels.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Entry stairs - doc: x=0,y=0,w=600,h=700
    # Stone steps descending into the catacombs, skeletons line the walls
    # ================================================================
    carve_ellipse(chunk, 15, 15, 10, 8)
    fill_tiles(chunk, TILE_GROUND, 8, 10, 28, 25)
    # Sarcophagi lining the walls
    fill_tiles(chunk, TILE_WALL, 12, 14, 13, 16)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 20)

    # ================================================================
    # SECTION 2: Skeleton ball corridor - doc: x=400,y=600,w=1000,h=400
    # Long straight corridor where a rolling skeleton ball attacks
    # Niches on sides for躲避, skeleton ambushes
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 22, 55, 38)
    # Side alcoves for dodging
    fill_tiles(chunk, TILE_GROUND, 20, 20, 26, 22)
    fill_tiles(chunk, TILE_GROUND, 35, 20, 41, 22)
    fill_tiles(chunk, TILE_GROUND, 48, 20, 54, 22)
    # Corridor walls (barriers in middle creating narrow passages)
    fill_tiles(chunk, TILE_WALL, 28, 26, 30, 30)
    fill_tiles(chunk, TILE_WALL, 42, 28, 44, 32)

    # ================================================================
    # SECTION 3: Rope bridge over abyss - doc: x=1200,y=400,w=1000,h=600
    # Narrow bridge, can be cut to create shortcut
    # ================================================================
    carve_ellipse(chunk, 65, 28, 14, 10)
    fill_tiles(chunk, TILE_GROUND, 52, 25, 72, 35)
    # Bridge approach corridor
    fill_tiles(chunk, TILE_GROUND, 50, 30, 58, 38)

    # ================================================================
    # SECTION 4: Lower tomb chambers - doc: x=400,y=900,w=800,h=700
    # Connected stone rooms full of skeleton swordsmen
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 42, 50, 72)
    carve_ellipse(chunk, 32, 55, 14, 12)
    # Cell walls creating tomb chambers
    fill_tiles(chunk, TILE_WALL, 22, 46, 24, 50)
    fill_tiles(chunk, TILE_WALL, 38, 48, 40, 52)
    fill_tiles(chunk, TILE_WALL, 28, 60, 30, 64)
    # Corridor from skeleton ball area down to tombs
    fill_tiles(chunk, TILE_GROUND, 25, 36, 35, 44)

    # ================================================================
    # SECTION 5: Skeleton wheel area - connects to lower levels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 48, 55, 75, 72)
    # Obstacles
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 63)
    fill_tiles(chunk, TILE_WALL, 65, 65, 67, 68)

    # ================================================================
    # SECTION 6: Abandoned tomb / Smouldering Lake passage - doc: x=800,y=1500
    # Side path with Fire Demon guarding descent to Smouldering Lake
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 10, 72, 40, 100)
    carve_ellipse(chunk, 25, 85, 10, 8)
    # Tight tunnel toward Smouldering Lake
    fill_tiles(chunk, TILE_GROUND, 30, 90, 48, 105)
    fill_tiles(chunk, TILE_GROUND, 15, 100, 35, 112)
    carve_ellipse(chunk, 25, 108, 8, 6)

    # ================================================================
    # SECTION 7: Path to Wolnir - wide corridor approaching boss
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 70, 55, 100, 80)
    fill_tiles(chunk, TILE_GROUND, 85, 70, 115, 90)

    # ================================================================
    # SECTION 8: Wolnir arena - doc: x=2500,y=2300,w=1000,h=800
    # Dark arena where Wolnir emerges from the abyss
    # ================================================================
    carve_ellipse(chunk, 125, 105, 22, 20)
    fill_tiles(chunk, TILE_GROUND, 105, 88, 148, 125)
    # Dark wall barriers at arena edges
    fill_tiles(chunk, TILE_WALL, 108, 92, 110, 95)
    fill_tiles(chunk, TILE_WALL, 140, 98, 142, 101)

    # Exit corridor to Irithyll
    fill_tiles(chunk, TILE_GROUND, 135, 85, 150, 100)

    # Connection from lower tombs to Wolnir path
    fill_tiles(chunk, TILE_GROUND, 45, 68, 55, 75)
    # Connection from bridge area to Wolnir path
    fill_tiles(chunk, TILE_GROUND, 68, 40, 78, 55)

    # === ADDITIONAL INTERNAL STRUCTURES — catacombs ===
    # Skeleton ball corridor — skull piles and bone walls
    fill_tiles(chunk, TILE_WALL, 25, 18, 27, 20)
    fill_tiles(chunk, TILE_WALL, 40, 22, 42, 24)
    fill_tiles(chunk, TILE_WALL, 55, 18, 57, 20)
    fill_tiles(chunk, TILE_WALL, 35, 32, 37, 34)
    fill_tiles(chunk, TILE_WALL, 50, 35, 52, 37)
    # Rope bridge area — cliff edges
    fill_tiles(chunk, TILE_WALL, 62, 25, 64, 28)
    fill_tiles(chunk, TILE_WALL, 78, 30, 80, 32)
    fill_tiles(chunk, TILE_WALL, 88, 35, 90, 37)
    # Lower tombs — sarcophagus walls
    fill_tiles(chunk, TILE_WALL, 20, 55, 22, 58)
    fill_tiles(chunk, TILE_WALL, 32, 60, 34, 62)
    fill_tiles(chunk, TILE_WALL, 42, 55, 44, 57)
    fill_tiles(chunk, TILE_WALL, 55, 62, 57, 64)
    fill_tiles(chunk, TILE_WALL, 28, 72, 30, 74)
    fill_tiles(chunk, TILE_WALL, 48, 78, 50, 80)
    # Wolnir path — bone pillars
    fill_tiles(chunk, TILE_WALL, 75, 55, 77, 57)
    fill_tiles(chunk, TILE_WALL, 90, 62, 92, 64)
    fill_tiles(chunk, TILE_WALL, 105, 68, 107, 70)
    fill_tiles(chunk, TILE_WALL, 115, 75, 117, 77)
    # Wolnir arena — ancient pillars
    fill_tiles(chunk, TILE_WALL, 112, 95, 114, 98)
    fill_tiles(chunk, TILE_WALL, 130, 100, 132, 103)
    fill_tiles(chunk, TILE_WALL, 120, 112, 122, 115)
    fill_tiles(chunk, TILE_WALL, 138, 108, 140, 110)

    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))     # Entry
    entities.append(make_entity("Bonfire", 25 * 16, 85 * 16))     # Abandoned Tomb
    entities.append(make_entity("Bonfire", 125 * 16, 108 * 16))   # Wolnir

    # Boss - Wolnir
    entities.append(make_entity("BossSpawn", 125 * 16, 100 * 16))

    # Enemies — DS3 Catacombs of Carthus: Skeleton Swordsmen, Skeleton Wheels,
    # Hound-Rats, Writhing Rotten Flesh, Black Knight (Tsorig invasion), Crystal Lizard
    enemy_data = [
        # Entry stairs — Skeleton Swordsman ambush
        ("Skeleton", 18, 18), ("Skeleton", 22, 20),
        ("Assassin", 16, 22),                                  # Skeleton Swordsman (curved sword variant)
        # Skeleton ball corridor — Skeletons in side alcoves
        ("Skeleton", 25, 28), ("Skeleton", 35, 30), ("Skeleton", 42, 26),
        ("Archer", 20, 21),                                    # Skeleton Swordsman (archer)
        ("Assassin", 36, 22), ("Assassin", 50, 21),           # Skeleton Swordsmen in alcoves
        ("Skeleton", 48, 32), ("Skeleton", 52, 34),
        # Rope bridge area
        ("Skeleton", 60, 30), ("Assassin", 64, 32),
        # Lower tomb chambers — dense skeleton groups
        ("Skeleton", 20, 48), ("Skeleton", 28, 52),
        ("Assassin", 24, 55), ("Assassin", 32, 50),           # Skeleton Swordsmen in tomb chambers
        ("Skeleton", 35, 56), ("Skeleton", 40, 60), ("Skeleton", 45, 65),
        ("Skeleton", 32, 58), ("Skeleton", 38, 62),
        # Skeleton Wheel area — rapid rolling skeletons (use MiniBoss for wheels)
        ("MiniBoss", 55, 62), ("MiniBoss", 60, 68),           # Skeleton Wheels
        ("MiniBoss", 65, 72),                                  # Skeleton Wheel
        ("Skeleton", 58, 66), ("Skeleton", 63, 70),
        # Abandoned Tomb / Smouldering Lake passage — rats and Writhing Rotten Flesh
        ("Rat", 20, 78), ("Rat", 25, 82), ("Rat", 30, 88),   # Hound-Rats
        ("Rat", 18, 85), ("Rat", 22, 92),                     # More Hound-Rats
        ("InfestedCorpse", 28, 95),                            # Writhing Rotten Flesh
        ("FireDemon", 35, 98),                                 # Fire Demon (guards Smouldering Lake)
        ("LesserCrab", 22, 96),                                 # Lesser Crab (Smouldering Lake passage, wiki-confirmed)
        # Crystal Lizard
        ("CrystalLizard", 48, 50),
        # Path to Wolnir — Knight Slayer Tsorig invasion
        ("BlackKnight", 80, 60),                               # Knight Slayer Tsorig (Black Knight set)
        ("Skeleton", 90, 70), ("Assassin", 95, 66),
        # Wolnir arena approach
        ("Skeleton", 110, 85), ("Skeleton", 115, 90), ("Skeleton", 120, 95),
        ("Skeleton", 130, 92), ("Skeleton", 135, 98),
        ("Archer", 125, 88),                                   # Skeleton archer at arena entry
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # Items — DS3 Catacombs of Carthus (verified against wiki)
    # 2x Sharp Gem, Dark Gem, Carthus Pyromancy Tome, Grave Warden Pyromancy Tome,
    # Grave Warden's Ashes, Witch's Ring, Carthus Bloodring, Carthus Milkring,
    # Carthus Rouge x2, Old Sage's Blindfold, Knight Slayer's Ring,
    # Undead Bone Shard, Titanite Shard x2, Large Titanite Shard x2, Twinkling Titanite,
    # Yellow Bug Pellet x3, Black Bug Pellet x2, Bloodred Moss Clump x3,
    # Ember x2, Soul of a Deserted Corpse x2, Soul of a Nameless Soldier x2,
    # Large Soul of an Unknown Traveler
    for kind, name, tx, ty, val in [
        # Upper Catacombs — entry area
        ("Consumable", "Sharp Gem", 18, 16, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 22, 20, 200),
        ("Consumable", "Carthus Rouge", 25, 22, 0),
        ("Consumable", "Yellow Bug Pellet", 30, 18, 0),
        ("Consumable", "Yellow Bug Pellet", 32, 19, 0),
        ("Consumable", "Yellow Bug Pellet", 34, 20, 0),
        ("Consumable", "Black Bug Pellet", 36, 22, 0),
        ("Consumable", "Black Bug Pellet", 38, 23, 0),
        ("Consumable", "Bloodred Moss Clump", 40, 19, 0),
        ("Consumable", "Bloodred Moss Clump", 42, 20, 0),
        ("Consumable", "Bloodred Moss Clump", 44, 21, 0),
        # Skeleton ball corridor area
        ("Consumable", "Carthus Pyromancy Tome", 40, 28, 0),
        ("TitaniteShard", "Titanite Shard", 48, 30, 0),
        ("Consumable", "Carthus Rouge", 50, 32, 0),
        ("Consumable", "Dark Gem", 52, 36, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 20, 30, 200),
        # Lower tomb chambers
        ("Consumable", "Grave Warden's Ashes", 28, 50, 0),
        ("Consumable", "Old Sage's Blindfold", 48, 48, 0),
        ("TitaniteShard", "Large Titanite Shard", 35, 55, 0),
        # Large Titanite Shard removed (extra — wiki says 1x for Catacombs)
        ("SoulOrb", "Soul of a Nameless Soldier", 32, 55, 800),
        # Deep tomb — Grave Warden area
        ("Consumable", "Grave Warden Pyromancy Tome", 40, 64, 0),
        ("RingDrop", "Carthus Milkring", 28, 62, 0),
        ("RingDrop", "Carthus Bloodring", 55, 58, 0),
        ("TitaniteShard", "Twinkling Titanite", 42, 66, 0),
        # Skeleton bridge area
        ("Consumable", "Sharp Gem", 58, 40, 0),
        ("TitaniteShard", "Titanite Shard", 62, 45, 0),
        ("Ember", "Ember", 65, 50, 0),
        # Ember removed (duplicate — wiki says 1x Ember for Catacombs of Carthus)
        ("SoulOrb", "Soul of a Nameless Soldier", 70, 52, 800),
        ("SoulOrb", "Large Soul of an Unknown Traveler", 72, 55, 800),
        # Knight Slayer Tsorig area
        ("RingDrop", "Knight Slayer's Ring", 45, 70, 0),
        # Abandoned Tomb / Wolnir approach
        ("RingDrop", "Witch's Ring", 25, 90, 0),
        ("UndeadBoneShard", "Undead Bone Shard", 30, 85, 0),
        # Titanite Shard removed (extra — wiki says 2x for Catacombs)
        # Titanite Shard removed (extra — wiki says 2x for Catacombs)
    ]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # Chests — DS3 Catacombs: Mimic drops Black Blade (only chest in area)
    entities.append(make_entity("Chest", 38 * 16, 58 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_name", "String", "Black Blade"),
        make_field("is_mimic", "Bool", True),
    ]))

    # NPCs — DS3 Catacombs: Anri at the first bonfire area, Horace deeper in
    entities.append(make_entity("Npc", 15 * 16, 18 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "We meet again|Have you seen Horace anywhere?|I am worried about him")]))
    entities.append(make_entity("Npc", 50 * 16, 45 * 16, [make_field("name", "String", "Horace the Hushed"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#606060"), make_field("dialogue", "String", "...|(nods slowly)")]))

    entities.append(make_entity("FogGate", 25 * 16, 112 * 16, [
        make_field("dest_area", "String", "SmoulderingLake"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 145 * 16, 92 * 16, [
        make_field("dest_area", "String", "Irithyll"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))

    # Lights - warm torch light in dark catacombs
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 35 * 16, 30 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.5), make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 25 * 16, 85 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 125 * 16, 100 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.3), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.35)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  CatacombsOfCarthus (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "CatacombsOfCarthus", chunk, entities


def make_smouldering_lake():
    """Smouldering Lake - lava cavern beneath Carthus catacombs.
    Faithful DS3 layout: underground cave -> smouldering lake shore with lava ->
    demon ruins outer hall -> demon cleric corridors -> Old Demon King arena.
    Design doc: 3600x3000, volcanic cavern with lava (POISON tiles).
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Underground cave entry - doc: x=0,y=0,w=600,h=600
    # Dark tunnel from Catacombs, air getting hotter
    # ================================================================
    carve_ellipse(chunk, 15, 15, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 10, 25, 25)

    # ================================================================
    # SECTION 2: Smouldering lake shore - doc: x=400,y=600,w=1400,h=1000
    # Vast underground lake with shallow lava, ballista in distance
    # Lava patches (POISON) scattered across the area
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 10, 28, 75, 80)
    # Lava patches across the lake surface
    fill_tiles(chunk, TILE_POISON, 20, 38, 40, 52)
    fill_tiles(chunk, TILE_POISON, 45, 55, 60, 68)
    fill_tiles(chunk, TILE_POISON, 30, 60, 42, 72)
    # Ruin cover points (stone islands in lava)
    fill_tiles(chunk, TILE_GROUND, 25, 42, 32, 48)
    fill_tiles(chunk, TILE_GROUND, 48, 58, 55, 64)
    # Corridor from cave to lake
    fill_tiles(chunk, TILE_GROUND, 15, 22, 22, 32)

    # ================================================================
    # SECTION 3: Demon ruins outer hall - doc: x=1200,y=1400,w=800,h=600
    # Collapsed stone pillars, demon carvings, fire demons patrol
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 55, 50, 90, 68)
    carve_ellipse(chunk, 72, 58, 12, 8)
    # Collapsed pillars as obstacles
    fill_tiles(chunk, TILE_WALL, 62, 54, 64, 57)
    fill_tiles(chunk, TILE_WALL, 80, 62, 82, 65)
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 62)
    # Corridor from lake to demon ruins
    fill_tiles(chunk, TILE_GROUND, 45, 45, 58, 55)

    # ================================================================
    # SECTION 4: Demon cleric corridors - doc: x=1800,y=1600,w=600,h=500
    # Winding corridors with demon clerics performing rituals
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 60, 115, 80)
    # Room walls creating cell-like spaces
    fill_tiles(chunk, TILE_WALL, 92, 64, 94, 67)
    fill_tiles(chunk, TILE_WALL, 102, 70, 104, 73)
    fill_tiles(chunk, TILE_WALL, 96, 76, 98, 78)
    # Corridor from outer hall to cleric corridors
    fill_tiles(chunk, TILE_GROUND, 85, 55, 92, 62)

    # ================================================================
    # SECTION 5: Old Demon King arena - doc: x=2200,y=2000,w=1000,h=700
    # Grand hall deep in the demon ruins, lava pools at edges
    # ================================================================
    carve_ellipse(chunk, 135, 108, 20, 18)
    fill_tiles(chunk, TILE_GROUND, 115, 90, 155, 128)
    # Lava pools at arena edges
    fill_tiles(chunk, TILE_POISON, 120, 95, 128, 100)
    fill_tiles(chunk, TILE_POISON, 142, 118, 150, 124)
    # Central broken altar
    fill_tiles(chunk, TILE_WALL, 132, 105, 138, 111)
    # Corridor from cleric area to arena
    fill_tiles(chunk, TILE_GROUND, 110, 75, 125, 95)

    # ================================================================
    # Side area: Ballista tunnel (NW corner) - skeletons near ballista
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 8, 80, 35, 100)
    carve_ellipse(chunk, 22, 90, 8, 6)

    # Connection from lake to ballista area
    fill_tiles(chunk, TILE_GROUND, 15, 75, 25, 82)

    # ================================================================
    # ADDITIONAL INTERNAL STRUCTURES — dense obstacles for DS3 feel
    # ================================================================
    # Cave entry stalactites
    fill_tiles(chunk, TILE_WALL, 12, 14, 13, 16)
    fill_tiles(chunk, TILE_WALL, 18, 12, 19, 14)
    # Lake shore rock formations
    fill_tiles(chunk, TILE_WALL, 15, 35, 17, 37)
    fill_tiles(chunk, TILE_WALL, 22, 45, 24, 47)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 57)
    fill_tiles(chunk, TILE_WALL, 55, 42, 57, 44)
    fill_tiles(chunk, TILE_WALL, 68, 52, 70, 54)
    # More collapsed pillars in demon ruins
    fill_tiles(chunk, TILE_WALL, 58, 56, 60, 58)
    fill_tiles(chunk, TILE_WALL, 75, 52, 77, 54)
    fill_tiles(chunk, TILE_WALL, 84, 58, 86, 60)
    fill_tiles(chunk, TILE_WALL, 65, 64, 67, 66)
    # Cleric corridor ritual stones
    fill_tiles(chunk, TILE_WALL, 88, 66, 90, 68)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    fill_tiles(chunk, TILE_WALL, 108, 72, 110, 74)
    # Arena edge debris
    fill_tiles(chunk, TILE_WALL, 118, 95, 120, 97)
    fill_tiles(chunk, TILE_WALL, 148, 110, 150, 112)
    fill_tiles(chunk, TILE_WALL, 125, 118, 127, 120)
    # Ballista area rocks
    fill_tiles(chunk, TILE_WALL, 12, 85, 14, 87)
    fill_tiles(chunk, TILE_WALL, 28, 92, 30, 94)

    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))     # Abandoned Tomb
    entities.append(make_entity("Bonfire", 72 * 16, 58 * 16))     # Old King's Antechamber
    entities.append(make_entity("Bonfire", 100 * 16, 72 * 16))    # Demon Ruins
    entities.append(make_entity("Bonfire", 135 * 16, 110 * 16))   # Old Demon King

    # Boss - Old Demon King
    entities.append(make_entity("BossSpawn", 135 * 16, 105 * 16))

    # Enemies — DS3 Smouldering Lake: Demon Clerics, Demon Statues, Basilisks,
    # Smouldering Ghru, Smouldering Rotten Flesh, Great Crab, Carthus Sandworm,
    # Skeleton Swordsmen, Skeleton Wheels, Knight Slayer Tsorig NPC
    enemy_data = [
        # Entry cave
        ("DemonStatue", 18, 18), ("DemonStatue", 22, 22),
        # Lake shore — Demon Statues and Ghru
        ("DemonStatue", 28, 42), ("DemonStatue", 50, 60), ("DemonStatue", 65, 50),
        ("DemonStatue", 18, 32), ("DemonStatue", 35, 40),
        ("Ghru", 62, 58), ("Ghru", 68, 62), ("Ghru", 72, 55),
        ("Ghru", 42, 48), ("Ghru", 55, 52),                    # Smouldering Ghru
        # Smouldering Rotten Flesh — DS3 wiki: 6 in corridor, 3 in demon ruins room (9 total)
        ("InfestedCorpse", 48, 55), ("InfestedCorpse", 58, 62),
        ("InfestedCorpse", 65, 60), ("InfestedCorpse", 70, 58),
        ("InfestedCorpse", 72, 62), ("InfestedCorpse", 68, 65),
        ("InfestedCorpse", 95, 62), ("InfestedCorpse", 98, 65), ("InfestedCorpse", 100, 60),
        # Basilisks near lava pools
        ("Basilisk", 52, 65), ("Basilisk", 58, 70), ("Basilisk", 55, 72),
        # Great Crab in lake (rare giant enemy)
        ("GiantSlave", 38, 45),                                 # Great Crab
        # Demon Clerics (FireDemon) at demon ruins
        ("FireDemon", 58, 55),                                  # Demon ruins entrance
        ("FireDemon", 95, 70), ("FireDemon", 100, 75),         # Inner demon ruins
        ("FireDemon", 118, 88),                                 # Arena approach
        # Black Knights (rare in demon ruins)
        ("BlackKnight", 78, 58), ("BlackKnight", 108, 68),
        # Skeleton remains from Carthus — walkthrough: group + red-eyed with shotels
        ("Skeleton", 82, 52), ("Skeleton", 88, 60),            # Skeleton Swordsmen
        ("Skeleton", 18, 92), ("Skeleton", 25, 88),            # Skeletons in ballista area
        ("Skeleton", 30, 90),                                   # Red-eyed skeleton swordsman
        ("MiniBoss", 75, 50),                                   # Skeleton Wheel 1
        ("MiniBoss", 22, 88), ("MiniBoss", 28, 92),            # Skeleton Wheels 2-3 (ballista area)
        # Hound-rats in ballista caves (DS3: Hound-rats, not Dogs)
        ("Rat", 15, 85), ("Rat", 20, 90), ("Rat", 25, 95),
        ("Rat", 40, 58), ("Rat", 48, 64),
        # Large Hound-rat in lower ruins
        ("Rat", 62, 68),
        # Carthus Sandworm (giant enemy at lake center)
        ("GiantSlave", 45, 68),                                 # Carthus Sandworm
        # Crystal Lizards — wiki: 3 total (1 near bonfire, 2 in cavern after ballista)
        ("CrystalLizard", 82, 55), ("CrystalLizard", 112, 78), ("CrystalLizard", 25, 95),
        # Demon Statues at arena approach
        ("DemonStatue", 112, 82),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # Items — DS3 Smouldering Lake: Black Knight Sword, Izalith Staff, Fume Ultra Greatsword,
    # Dragonrider Bow, Shield of Want, Chaos Gem, Quelana/Izalith Pyromancy Tomes, etc.
    items = [
        ("Ember", "Ember", 18, 20, 0),  # wiki: 3x Ember in Smouldering Lake
        ("Consumable", "Quelana Pyromancy Tome", 28, 38, 0),    # Lake shore
        ("Consumable", "Izalith Pyromancy Tome", 65, 52, 0),    # Near demon ruins
        ("Consumable", "Chaos Gem", 58, 60, 0),                 # Lake mid area
        ("Consumable", "Toxic Mist", 52, 68, 0),                # Near basilisks
        ("Consumable", "Lightning Stake", 90, 68, 0),           # Demon ruins
        ("Consumable", "Sacred Flame", 105, 72, 0),             # Inner ruins
        ("Consumable", "White Hair Talisman", 98, 78, 0),       # Deep ruins
        ("TitaniteShard", "Large Titanite Shard", 60, 50, 0),  # wiki: 10x Large Titanite
        ("TitaniteShard", "Large Titanite Shard", 90, 65, 0),
        ("Ember", "Ember", 72, 55, 0),  # wiki: 3x Ember
        ("EstusShard", "Estus Shard", 22, 88, 0),               # Ballista caves
        ("UndeadBoneShard", "Undead Bone Shard", 48, 72, 0),    # Lake hidden area
        ("HomewardBone", "Homeward Bone", 100, 70, 0),
        ("RingDrop", "Speckled Stoneplate Ring", 42, 55, 0),
        ("SoulOrb", "Soul of a Crestfallen Knight", 125, 92, 1000),
        ("WeaponDrop", "Dragonrider Bow", 130, 92, 0),        # Ledge drop near ballista path
        ("WeaponDrop", "Izalith Staff", 88, 78, 0),           # Drop down behind illusory wall in demon ruins
        ("WeaponDrop", "Fume Ultra Greatsword", 32, 92, 0),   # Knight Slayer Tsorig drop
        ("Consumable", "Black Iron Greatshield", 32, 90, 0),  # Knight Slayer Tsorig drop
        ("Consumable", "Llewellyn Shield", 20, 86, 0),        # Horace drop
        ("Consumable", "Yellow Bug Pellet", 18, 84, 0),       # Horace cavern corpse
        ("Consumable", "Yellow Bug Pellet", 18, 82, 0),       # Horace cavern corpse
        # Additional items from wiki verification
        ("Ember", "Ember", 65, 55, 0),                      # 3rd Ember (wiki: 3x)
        ("UndeadBoneShard", "Undead Bone Shard", 110, 80, 0), # 2nd Undead Bone Shard (wiki: 2x)
        ("HomewardBone", "Homeward Bone", 55, 62, 0),          # 2nd Homeward Bone (wiki: 2x)
        ("WeaponDrop", "Black Knight Sword", 108, 70, 0),    # wiki: weapon pickup
        ("Consumable", "Shield of Want", 115, 85, 0),        # wiki: shield pickup
        ("TitaniteShard", "Large Titanite Shard", 42, 52, 0), # Large Titanite (wiki: 10x)
        ("TitaniteShard", "Large Titanite Shard", 55, 56, 0),
        ("TitaniteShard", "Large Titanite Shard", 62, 60, 0),
        ("TitaniteShard", "Large Titanite Shard", 95, 75, 0),
        ("TitaniteShard", "Large Titanite Shard", 102, 68, 0),
        ("Consumable", "Yellow Bug Pellet", 35, 45, 0),      # wiki: 4x Yellow Bug Pellet
        ("Consumable", "Yellow Bug Pellet", 48, 58, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # Chests — DS3 Smouldering Lake
    # Black Knight Sword (corpse in demon ruins, behind illusory wall)
    entities.append(make_entity("Chest", 80 * 16, 60 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_name", "String", "Black Knight Sword"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Shield of Want (corpse near sandworm area)
    entities.append(make_entity("Chest", 95 * 16, 75 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_name", "String", "Shield of Want"),
        make_field("is_mimic", "Bool", False),
    ]))

    # NPCs — DS3 Smouldering Lake: Knight Slayer Tsorig, Horace
    entities.append(make_entity("Npc", 30 * 16, 92 * 16, [make_field("name", "String", "Knight Slayer Tsorig"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#804020"), make_field("dialogue", "String", "Heh heh|Forgive me|I was just finishing a conquest")]))
    entities.append(make_entity("Npc", 20 * 16, 88 * 16, [make_field("name", "String", "Horace the Hushed"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#606060"), make_field("dialogue", "String", "...|(shakes head sadly)")]))

    entities.append(make_entity("FogGate", 135 * 16, 125 * 16, [
        make_field("dest_area", "String", "CatacombsOfCarthus"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))

    # Lights - intense firelight from lava
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 35 * 16, 45 * 16, [make_field("radius", "Float", 220.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.4), make_field("b", "Float", 0.1), make_field("intensity", "Float", 0.6)]))
    entities.append(make_entity("Light", 72 * 16, 58 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.5), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 135 * 16, 105 * 16, [make_field("radius", "Float", 240.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.5), make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.7)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  SmoulderingLake (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "SmoulderingLake", chunk, entities


def make_irithyll():
    """Irithyll of the Boreal Valley - frozen city with Pontiff Sulyvahn boss.
    Faithful DS3 layout: entry ice bridge -> main boulevard -> Church of Yorshka ->
    Distant Manor -> sewers -> Pontiff cathedral -> exit to dungeon.
    Design doc: 3200x2400, gothic city with icy blue moonlight.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Entry ice bridge - from Catacombs
    # Narrow stone bridge over a frozen valley
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 6, 32, 28, 48)

    # ================================================================
    # SECTION 2: Main boulevard - wide central path through the city
    # Silver Knights patrol, buildings (wall obstacles) line the street
    # ================================================================
    carve_ellipse(chunk, 40, 50, 16, 14)
    fill_tiles(chunk, TILE_GROUND, 30, 42, 100, 65)
    # Building walls lining the boulevard
    fill_tiles(chunk, TILE_WALL, 32, 44, 35, 48)
    fill_tiles(chunk, TILE_WALL, 32, 56, 35, 60)
    fill_tiles(chunk, TILE_WALL, 65, 46, 68, 50)
    fill_tiles(chunk, TILE_WALL, 85, 52, 88, 56)

    # ================================================================
    # SECTION 3: Church of Yorshka - central church with bonfire
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 45, 32, 78, 48)
    carve_ellipse(chunk, 62, 40, 12, 7)
    # Church walls
    fill_tiles(chunk, TILE_WALL, 50, 35, 52, 38)
    fill_tiles(chunk, TILE_WALL, 72, 35, 74, 38)

    # ================================================================
    # SECTION 4: Distant Manor - Siegward cooking in kitchen
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 68, 45, 90)
    carve_ellipse(chunk, 30, 78, 10, 8)
    # Manor walls
    fill_tiles(chunk, TILE_WALL, 20, 72, 22, 75)
    fill_tiles(chunk, TILE_WALL, 38, 82, 40, 85)

    # ================================================================
    # SECTION 5: Sewer area - underground passage with ManGrubs
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 60, 75, 100, 100)

    # ================================================================
    # SECTION 6: Silver Knight hall - doc: south area
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 95, 55, 125)
    carve_ellipse(chunk, 38, 108, 12, 10)
    fill_tiles(chunk, TILE_WALL, 28, 100, 30, 104)
    fill_tiles(chunk, TILE_WALL, 45, 112, 47, 116)

    # ================================================================
    # SECTION 7: Pontiff Sulyvahn cathedral - large boss arena
    # ================================================================
    carve_ellipse(chunk, 120, 80, 20, 18)
    fill_tiles(chunk, TILE_GROUND, 100, 62, 142, 100)
    # Cathedral pillars
    fill_tiles(chunk, TILE_WALL, 108, 70, 110, 74)
    fill_tiles(chunk, TILE_WALL, 132, 86, 134, 90)
    fill_tiles(chunk, TILE_WALL, 115, 92, 117, 96)

    # Path from boulevard to Pontiff arena
    fill_tiles(chunk, TILE_GROUND, 95, 55, 105, 68)

    # ================================================================
    # Exit to Irithyll Dungeon (upper right)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 130, 40, 148, 55)
    carve_ellipse(chunk, 144, 45, 6, 5)

    # Connection corridors
    fill_tiles(chunk, TILE_GROUND, 25, 60, 35, 70)   # Boulevard to Distant Manor
    fill_tiles(chunk, TILE_GROUND, 45, 48, 60, 55)    # Yorshka to boulevard
    fill_tiles(chunk, TILE_GROUND, 55, 65, 65, 75)    # Boulevard to sewers
    fill_tiles(chunk, TILE_GROUND, 45, 90, 55, 100)   # Manor to Silver Knight hall
    fill_tiles(chunk, TILE_GROUND, 100, 75, 110, 82)  # Sewers to arena approach

    spawn_px, spawn_py = 10 * 16, 35 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3 Irithyll of the Boreal Valley: 6 bonfires
    entities.append(make_entity("Bonfire", 10 * 16, 35 * 16))      # Irithyll of the Boreal Valley (entry bridge)
    entities.append(make_entity("Bonfire", 62 * 16, 40 * 16))      # Church of Yorshka
    entities.append(make_entity("Bonfire", 46 * 16, 52 * 16))      # Central Irithyll
    entities.append(make_entity("Bonfire", 30 * 16, 78 * 16))      # Distant Manor
    entities.append(make_entity("Bonfire", 75 * 16, 92 * 16))      # Water Reserve (sewer area)
    entities.append(make_entity("Bonfire", 120 * 16, 82 * 16))     # Pontiff Sulyvahn (boss)

    # Boss - Pontiff Sulyvahn
    entities.append(make_entity("BossSpawn", 120 * 16, 76 * 16))

    # Enemies — DS3 Irithyll of the Boreal Valley:
    # Pontiff Knights (wield fire swords), Fire Witches (ranged fire magic),
    # Irithyllian Slaves (cloaked ambushers), Sulyvahn's Beasts,
    # Irithyllian Beast-hounds, Sewer Centipedes, Silver Knights, Mimic,
    # Cathedral Evangelist (near hidden staircase)
    enemy_data = [
        # Bridge entrance — Sulyvahn's Beast ambush (DS3: attacks on entry bridge)
        ("GiantSlave", 12, 38),                                 # Sulyvahn's Beast at bridge
        ("Knight", 18, 42),                                      # Pontiff Knight patrol
        # Main boulevard — Pontiff Knights (Knight = closest to Pontiff Knight)
        ("Knight", 38, 50), ("Knight", 55, 55),
        ("Knight", 75, 60), ("Knight", 90, 58),
        # Irithyllian Slaves — cloaked ambushers (Assassin = closest match)
        ("Assassin", 42, 48), ("Assassin", 60, 52),
        ("Assassin", 78, 56),
        # Fire Witches (DarkMage) — cast fire spells from balconies
        ("DarkMage", 42, 52), ("DarkMage", 95, 62),
        ("DarkMage", 68, 58),
        # Irithyllian Beast-hounds (Dog) in alleys
        ("Dog", 50, 48), ("Dog", 80, 55), ("Dog", 65, 54),
        ("Dog", 48, 60),
        # Crystal Lizards (DS3: 1 near illusory wall stairs, 2 post-Pontiff courtyard, 1 lever path)
        ("CrystalLizard", 65, 42), ("CrystalLizard", 128, 75),
        ("CrystalLizard", 135, 80), ("CrystalLizard", 140, 72),
        # Distant Manor area — Irithyllian Slaves and Pontiff Knights
        ("Assassin", 28, 70), ("Assassin", 35, 75),            # Slaves near manor
        ("Knight", 32, 72), ("Knight", 40, 82),
        # Corvian near the manor gardens
        ("Assassin", 22, 68),
        # Church of Yorshka area — Pontiff Knight guard
        ("Knight", 70, 45), ("Knight", 72, 42),
        # Cathedral Evangelist near hidden staircase (DS3: drops Dorhys' Gnawing)
        ("Evangelist", 45, 55),
        # Sewers — Sewer Centipedes (ManGrub = closest to centipede)
        ("ManGrub", 68, 80), ("ManGrub", 78, 85), ("ManGrub", 88, 90),
        ("ManGrub", 72, 88), ("ManGrub", 82, 82),
        # Sulyvahn's Beasts at sewer reservoir (GiantSlave) — DS3 wiki: 2 beasts
        ("GiantSlave", 72, 90), ("GiantSlave", 78, 94),
        # Silver Knight hall / rooftops — Silver Knights guard the path to Anor Londo
        ("SilverKnight", 30, 100), ("SilverKnight", 42, 110),
        ("SilverKnight", 48, 118), ("SilverKnight", 36, 108),
        # Arena approach — Pontiff Knight + Fire Witch guard
        ("Knight", 105, 65), ("DarkMage", 110, 70),
        ("Knight", 100, 62),
        # Deacons on bridge to Anor Londo (DS3: "several deacons along the way")
        ("Deacon", 140, 50), ("Deacon", 142, 48), ("Deacon", 144, 52),
        # Pontiff arena entrance — Deep Accursed (DS3: lurks near arena)
        ("DeepAccursed", 132, 88),
        # Mimic near boulevard (DS3: drops Golden Ritual Spear)
        ("Mimic", 58, 56),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # Items — DS3 Irithyll of the Boreal Valley (verified against wiki)
    # Major items: Pontiff's Right Eye, Magic Clutch Ring, Ring of the Sun's First Born,
    # Leo Ring, Dark Stoneplate Ring, Ring of Favor, Sun Princess Ring, Aldrich's Ruby,
    # Giant's Coal, Easterner's Ashes, Smough's Great Hammer, Dragonslayer Greatbow,
    # Drang Twinspears, Yorshka's Spear, Dorhys' Gnawing, Great Heal, Witchtree Branch,
    # Brass Set, Painting Guardian Set, Painting Guardian's Curved Sword, Golden Ritual Spear
    for kind, name, tx, ty, val in [
        # Bridge — Sulyvahn's Beast drops Pontiff's Right Eye
        ("RingDrop", "Pontiff's Right Eye", 14, 36, 0),
        ("HomewardBone", "Homeward Bone", 16, 34, 0),
        # Central Irithyll courtyard
        ("Consumable", "Rime-blue Moss Clump", 20, 38, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 22, 40, 2000),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 24, 42, 800),
        # Upper streets — Pontiff Knight area
        ("SoulOrb", "Soul of a Weary Warrior", 30, 38, 2000),
        ("TitaniteShard", "Large Titanite Shard", 35, 36, 0),
        ("Consumable", "Budding Green Blossom", 38, 38, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 42, 40, 800),
        ("Consumable", "Rime-blue Moss Clump", 44, 42, 0),
        ("Consumable", "Rime-blue Moss Clump", 46, 44, 0),
        ("TitaniteShard", "Large Titanite Shard", 48, 38, 0),
        # Hidden staircase area — Evangelist
        ("Consumable", "Dorhys' Gnawing", 40, 50, 0),
        ("WeaponDrop", "Witchtree Branch", 42, 52, 0),
        ("TitaniteShard", "Large Titanite Shard", 38, 48, 0),
        # Church of Yorshka vicinity
        ("SoulOrb", "Large Soul of a Nameless Soldier", 55, 40, 800),
        ("TitaniteShard", "Large Titanite Shard", 58, 42, 0),
        ("TitaniteShard", "Large Titanite Shard", 60, 44, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 62, 42, 2000),
        # Altar area (illusory wall → Magic Clutch Ring)
        ("Consumable", "Lightning Gem", 65, 46, 0),
        ("RingDrop", "Magic Clutch Ring", 66, 48, 0),
        ("RingDrop", "Ring of the Sun's First Born", 68, 44, 0),
        # Church interior
        ("Consumable", "Proof of Concord Kept", 70, 38, 0),
        ("Consumable", "Roster of Knights", 72, 40, 0),
        # Graveyard behind church
        ("Consumable", "Fading Soul", 64, 52, 0),
        ("HomewardBone", "Homeward Bone", 62, 54, 0),
        ("HomewardBone", "Homeward Bone", 60, 56, 0),
        ("HomewardBone", "Homeward Bone", 58, 58, 0),
        ("UndeadBoneShard", "Undead Bone Shard", 66, 55, 0),
        # Dark room / hags
        ("Consumable", "Blue Bug Pellet", 50, 58, 0),
        ("Consumable", "Blue Bug Pellet", 52, 60, 0),
        ("Consumable", "Shriving Stone", 48, 56, 0),
        # Sewer area
        ("Consumable", "Kukri", 46, 65, 0),
        ("Consumable", "Kukri", 47, 66, 0),
        ("Consumable", "Kukri", 48, 67, 0),
        ("Consumable", "Kukri", 49, 68, 0),
        ("Consumable", "Kukri", 50, 69, 0),
        ("Consumable", "Kukri", 51, 70, 0),
        ("Consumable", "Kukri", 52, 71, 0),
        ("Consumable", "Kukri", 53, 72, 0),
        ("Consumable", "Rusted Gold Coin", 44, 62, 0),
        ("Consumable", "Dung Pie", 56, 68, 0),
        ("Consumable", "Dung Pie", 57, 69, 0),
        ("Consumable", "Dung Pie", 58, 70, 0),
        ("Consumable", "Dung Pie", 60, 72, 0),
        ("Consumable", "Dung Pie", 62, 74, 0),
        ("Consumable", "Dung Pie", 64, 76, 0),
        ("Consumable", "Excrement-covered Ashes", 52, 78, 0),
        # Dark room stairs — Blood Gem at foot of tree (DS3: alcove with tree/hags)
        ("TitaniteShard", "Blood Gem", 54, 72, 0),
        # Water / sewer underground
        ("RingDrop", "Ring of Sacrifice", 70, 78, 0),
        ("Consumable", "Green Blossom", 72, 80, 0),
        ("Consumable", "Green Blossom", 74, 82, 0),
        ("Consumable", "Green Blossom", 76, 84, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 78, 80, 800),
        ("Consumable", "Great Heal", 80, 82, 0),
        ("Consumable", "Green Blossom", 82, 78, 0),
        ("Consumable", "Green Blossom", 84, 80, 0),
        ("Consumable", "Green Blossom", 86, 82, 0),
        ("Consumable", "Green Blossom", 88, 84, 0),
        # Distant Manor — Siegward's kitchen
        ("EstusShard", "Estus Shard", 28, 82, 0),
        ("TitaniteShard", "Large Titanite Shard", 32, 85, 0),
        # Silver Knight hall — three chests area (Leo Ring, Smough's Great Hammer, Divine Blessing)
        # Leo Ring and Smough's Great Hammer are in chests, not ground items
        # Post-Silver Knight outdoor area
        ("Consumable", "Rusted Gold Coin", 36, 100, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 34, 98, 800),
        ("TitaniteShard", "Large Titanite Shard", 42, 105, 0),
        ("TitaniteShard", "Large Titanite Shard", 44, 102, 0),
        ("Consumable", "Blue Bug Pellet", 46, 108, 0),
        ("Consumable", "Blue Bug Pellet", 48, 110, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 50, 106, 2000),
        ("Ember", "Ember", 52, 108, 0),
        # Shortcut lift area
        ("TitaniteShard", "Large Titanite Shard", 56, 100, 0),
        ("TitaniteShard", "Large Titanite Shard", 58, 98, 0),
        # Pontiff approach
        ("Ember", "Ember", 120, 72, 0),
        ("Ember", "Ember", 125, 75, 0),
        ("RingDrop", "Dark Stoneplate Ring", 130, 80, 0),
        ("WeaponDrop", "Drang Twinspears", 135, 78, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 132, 85, 2000),
        # Post-Pontiff area
        ("TitaniteShard", "Large Titanite Shard", 128, 90, 0),
        ("Consumable", "Deep Gem", 132, 92, 0),
        ("RingDrop", "Ring of Favor", 130, 95, 0),
        ("Consumable", "Human Dregs", 128, 98, 0),
        ("RingDrop", "Aldrich's Ruby", 134, 96, 0),
        # Silver Knight rooftops
        ("Consumable", "Easterner's Ashes", 140, 68, 0),
        ("TitaniteShard", "Titanite Scale", 142, 70, 0),
        ("TitaniteShard", "Large Titanite Shard", 144, 72, 0),
        ("Consumable", "Dragonslayer Greatarrow", 146, 68, 0),
        ("Consumable", "Dragonslayer Greatarrow", 147, 69, 0),
        ("Consumable", "Dragonslayer Greatarrow", 148, 70, 0),
        ("Consumable", "Dragonslayer Greatarrow", 149, 71, 0),
        ("Consumable", "Dragonslayer Greatarrow", 150, 72, 0),
        ("WeaponDrop", "Dragonslayer Greatbow", 145, 66, 0),
        ("TitaniteShard", "Large Titanite Shard", 143, 64, 0),
        ("TitaniteShard", "Twinkling Titanite", 138, 62, 0),
        ("TitaniteShard", "Twinkling Titanite", 140, 60, 0),
        ("TitaniteShard", "Twinkling Titanite", 142, 58, 0),
        # Darkmoon Tomb — Brass Set
        ("ArmorDrop", "Brass Set", 112, 95, 0),
        # Painting Guardian items are in AnorLondo map (near Prison Tower/Yorshka church)
        # Silver Knight rooftops — additional Soul
        ("SoulOrb", "Large Soul of a Weary Warrior", 148, 66, 5000),
    ]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # Chests — DS3 Irithyll
    # Three chests in Silver Knight hall: Leo Ring, Smough's Great Hammer, Divine Blessing
    entities.append(make_entity("Chest", 36 * 16, 108 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_name", "String", "Divine Blessing"),
        make_field("is_mimic", "Bool", False),
    ]))
    entities.append(make_entity("Chest", 40 * 16, 108 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("loot_name", "String", "Leo Ring"),
        make_field("is_mimic", "Bool", False),
    ]))
    entities.append(make_entity("Chest", 38 * 16, 110 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_name", "String", "Smough's Great Hammer"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Mimic after Pontiff shortcut lever area (Golden Ritual Spear)
    entities.append(make_entity("Chest", 132 * 16, 88 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_name", "String", "Golden Ritual Spear"),
        make_field("is_mimic", "Bool", True),
    ]))
    # Yorshka's Spear chest in dark room beams
    entities.append(make_entity("Chest", 54 * 16, 56 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_name", "String", "Yorshka's Spear"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Reversal Ring chest in Darkmoon Tomb
    entities.append(make_entity("Chest", 114 * 16, 96 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("loot_name", "String", "Reversal Ring"),
        make_field("is_mimic", "Bool", False),
    ]))

    # NPCs — DS3 Irithyll: Anri (Church of Yorshka), Siegward (Distant Manor kitchen), Sirris
    entities.append(make_entity("Npc", 62 * 16, 38 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Hello|I am Anri of Astora|Have you seen Horace?|We must find the Lords of Cinder")]))
    entities.append(make_entity("Npc", 28 * 16, 80 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A060"), make_field("dialogue", "String", "Oh! Hello again|I seem to have gotten lost|But I found some estus soup!")]))
    # Sirris — appears near Church of Yorshka after Rosaria covenant
    entities.append(make_entity("Npc", 58 * 16, 44 * 16, [make_field("name", "String", "Sirris of the Sunless Realms"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#A0B0C0"), make_field("dialogue", "String", "I am Sirris|I offer my services as a knight|I will not forget this debt"), make_field("appear_condition", "String", "rosaria_covenant")]))

    entities.append(make_entity("FogGate", 144 * 16, 45 * 16, [
        make_field("dest_area", "String", "IrithyllDungeon"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # To Anor Londo (rotating staircase, after defeating Pontiff)
    entities.append(make_entity("FogGate", 148 * 16, 25 * 16, [
        make_field("dest_area", "String", "AnorLondo"),
        make_field("dest_x", "Float", 160.0),
        make_field("dest_y", "Float", 608.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights - icy blue moonlight throughout
    entities.append(make_entity("Light", 10 * 16, 35 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 62 * 16, 40 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 40 * 16, 55 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 120 * 16, 76 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.3), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — frozen city ===
    # Ice bridge — ice crystal pillars
    fill_tiles(chunk, TILE_WALL, 12, 36, 14, 38)
    fill_tiles(chunk, TILE_WALL, 22, 40, 24, 42)
    # Boulevard — lamp posts, market stalls, building walls
    fill_tiles(chunk, TILE_WALL, 35, 38, 37, 40)
    fill_tiles(chunk, TILE_WALL, 48, 42, 50, 44)
    fill_tiles(chunk, TILE_WALL, 58, 38, 60, 40)
    fill_tiles(chunk, TILE_WALL, 40, 48, 42, 50)
    fill_tiles(chunk, TILE_WALL, 55, 52, 57, 54)
    fill_tiles(chunk, TILE_WALL, 68, 45, 70, 47)
    # Yorshka church — pews
    fill_tiles(chunk, TILE_WALL, 62, 82, 64, 84)
    fill_tiles(chunk, TILE_WALL, 72, 85, 74, 87)
    # Distant Manor — furniture
    fill_tiles(chunk, TILE_WALL, 28, 58, 30, 60)
    fill_tiles(chunk, TILE_WALL, 35, 62, 37, 64)
    fill_tiles(chunk, TILE_WALL, 42, 58, 44, 60)
    # Sewers — support pillars
    fill_tiles(chunk, TILE_WALL, 82, 68, 84, 70)
    fill_tiles(chunk, TILE_WALL, 92, 72, 94, 74)
    fill_tiles(chunk, TILE_WALL, 100, 68, 102, 70)
    # Pontiff cathedral — cathedral pillars
    fill_tiles(chunk, TILE_WALL, 112, 72, 114, 75)
    fill_tiles(chunk, TILE_WALL, 128, 75, 130, 78)
    fill_tiles(chunk, TILE_WALL, 120, 82, 122, 85)
    fill_tiles(chunk, TILE_WALL, 135, 80, 137, 82)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  Irithyll (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "Irithyll", chunk, entities


def make_irithyll_dungeon():
    """Irithyll Dungeon - dark prison with jailers, Siegward's cell, Karla's cell.
    No boss. Tight corridors with cell walls creating a maze-like layout.
    Design doc: 3200x2800, spiral prison descending underground.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Underground passage entry - doc: x=0,y=0,w=600,h=600
    # Damp stone corridor from Irithyll, two jailers patrol
    # ================================================================
    carve_ellipse(chunk, 15, 15, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 10, 30, 28)

    # ================================================================
    # SECTION 2: Upper cell block - wide corridor with cells
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 25, 65, 45)
    # Cell walls creating prison cells
    fill_tiles(chunk, TILE_WALL, 25, 28, 27, 35)
    fill_tiles(chunk, TILE_WALL, 40, 28, 42, 35)
    fill_tiles(chunk, TILE_WALL, 55, 28, 57, 35)

    # ================================================================
    # SECTION 3: Central cell block - main hub with tight passages
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 25, 45, 80, 72)
    carve_ellipse(chunk, 52, 58, 14, 12)
    # More cell walls
    fill_tiles(chunk, TILE_WALL, 35, 50, 37, 57)
    fill_tiles(chunk, TILE_WALL, 50, 50, 52, 57)
    fill_tiles(chunk, TILE_WALL, 65, 50, 67, 57)

    # ================================================================
    # SECTION 4: Siegward's cell (east side)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 80, 50, 105, 68)
    carve_ellipse(chunk, 92, 58, 8, 6)
    fill_tiles(chunk, TILE_WALL, 85, 54, 87, 58)

    # ================================================================
    # SECTION 5: Lower drain / rat tunnels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 72, 70, 95)
    fill_tiles(chunk, TILE_WALL, 30, 78, 32, 82)
    fill_tiles(chunk, TILE_WALL, 50, 85, 52, 89)

    # ================================================================
    # SECTION 6: Karla's cell (deep southeast)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 75, 78, 105, 95)
    carve_ellipse(chunk, 90, 86, 8, 6)
    fill_tiles(chunk, TILE_WALL, 82, 82, 84, 86)

    # ================================================================
    # SECTION 7: Exit corridor to Profaned Capital (upper right)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 105, 25, 145, 42)
    carve_ellipse(chunk, 135, 32, 8, 8)
    fill_tiles(chunk, TILE_WALL, 118, 28, 120, 35)

    # ================================================================
    # SECTION 8: Gargoyle tower (connection upper to exit)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 35, 110, 48)

    # Connection corridors
    fill_tiles(chunk, TILE_GROUND, 45, 42, 55, 48)    # Upper to central
    fill_tiles(chunk, TILE_GROUND, 55, 68, 65, 78)    # Central to lower
    fill_tiles(chunk, TILE_GROUND, 70, 72, 82, 80)    # Lower to Karla
    fill_tiles(chunk, TILE_GROUND, 100, 45, 108, 52)  # Siegward to tower
    fill_tiles(chunk, TILE_GROUND, 105, 38, 115, 35)  # Tower to exit

    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3: only Irithyll Dungeon bonfire
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))     # Irithyll Dungeon

    # Enemies — DS3 Irithyll Dungeon: Jailers, Reanimated Corpses, Wretches,
    # Rats, Basilisks, Infested Corpses, Lycanthropes, Monstrosities of Sin,
    # Corpse-grubs, Sewer Centipedes, Mimics
    enemy_data = [
        # Upper prison block — jailers patrol with branding irons
        ("Jailer", 22, 20), ("Jailer", 35, 30), ("Jailer", 48, 38),
        ("Jailer", 25, 25), ("Jailer", 32, 32),
        # Reanimated Corpses in cells (PeasantHollow)
        ("PeasantHollow", 20, 30), ("PeasantHollow", 28, 35),
        ("PeasantHollow", 38, 28), ("PeasantHollow", 45, 34),
        # Central prison block — heavy jailer presence
        ("Jailer", 55, 55), ("Jailer", 60, 60), ("Jailer", 68, 52),
        ("PeasantHollow", 50, 50), ("PeasantHollow", 62, 55),
        ("CrystalLizard", 52, 52),
        # Siegward cell area — Wretches and Reanimated Corpses
        ("Jailer", 88, 55),
        ("Wretch", 78, 60), ("Wretch", 82, 65),
        ("PeasantHollow", 85, 62), ("PeasantHollow", 92, 58),
        # Lower drains — rats, basilisks, Infested Corpses
        ("Rat", 28, 78), ("Rat", 35, 82), ("Rat", 42, 88),
        ("Rat", 32, 85), ("Rat", 48, 90),                             # More rats
        ("Basilisk", 55, 80), ("Basilisk", 62, 85),
        ("InfestedCorpse", 38, 80), ("InfestedCorpse", 45, 86),       # Corpse-grubs
        # Sewer Centipede (ManGrub) in drain area
        ("ManGrub", 60, 75), ("ManGrub", 50, 78),
        # Cage Spider in drain area
        ("Spider", 55, 88),                                    # Cage Spider → Basilisk via ENEMY_KIND_MAP
        # Monstrosity of Sin (GiantSlave) near lower level
        ("GiantSlave", 42, 75),                               # Monstrosity of Sin
        # Lycanthrope (Dog) in rat tunnels
        ("Dog", 22, 82), ("Dog", 38, 85),
        # Gargoyle tower and exit corridor
        ("Gargoyle", 95, 42), ("Gargoyle", 125, 30),
        # Karla's cell area — jailers guard
        ("Jailer", 85, 85), ("Jailer", 95, 90),
        ("PeasantHollow", 88, 88), ("PeasantHollow", 92, 82),
        # Alva Seeker of the Spurned — invades near Karla's cell (MiniBoss)
        ("MiniBoss", 78, 82),
        # Mimic near exit corridor (drops Lightning Blade)
        ("Mimic", 118, 32),
        # Mimic in sewer area (DS3 wiki: drops Dark Clutch Ring)
        ("Mimic", 45, 82),
        # Mimic near hooded enemies (DS3 wiki: drops Estus Shard)
        ("Mimic", 62, 68),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # Items — DS3 Irithyll Dungeon (verified against wiki)
    for kind, name, tx, ty, val in [
        # Upper prison cells
        ("Consumable", "Rusted Coin", 20, 16, 0),            # First cell near bonfire (wiki walkthrough)
        ("Consumable", "Fading Soul", 18, 22, 0),
        ("TitaniteShard", "Large Titanite Shard", 28, 32, 0),
        ("TitaniteShard", "Large Titanite Shard", 48, 40, 0),
        ("Consumable", "Pale Pine Resin", 38, 35, 0),
        ("Consumable", "Pale Pine Resin", 40, 36, 0),
        ("ArmorDrop", "Old Sorcerer Hat", 35, 42, 0),
        ("ArmorDrop", "Old Sorcerer Coat", 36, 43, 0),
        ("ArmorDrop", "Old Sorcerer Gauntlets", 37, 44, 0),
        ("ArmorDrop", "Old Sorcerer Boots", 38, 45, 0),
        ("Consumable", "Great Magic Shield", 42, 38, 0),
        # Central cell block
        ("Consumable", "Rusted Gold Coin", 52, 56, 0),
        ("TitaniteShard", "Large Titanite Shard", 60, 60, 0),
        ("RingDrop", "Bellowing Dragoncrest Ring", 55, 62, 0),
        ("Consumable", "Jailbreaker's Key", 58, 58, 0),
        # Siegward area
        ("Consumable", "Simple Gem", 82, 60, 0),
        ("Consumable", "Profaned Coal", 75, 58, 0),
        ("TitaniteShard", "Large Titanite Shard", 78, 62, 0),
        # Lower sewers
        ("SoulOrb", "Large Soul of a Nameless Soldier", 30, 80, 800),
        ("Consumable", "Dung Pie", 34, 82, 0),
        ("Consumable", "Dung Pie", 36, 84, 0),
        ("Consumable", "Dung Pie", 38, 86, 0),
        ("Consumable", "Dung Pie", 40, 88, 0),
        ("TitaniteShard", "Large Titanite Shard", 45, 85, 0),
        ("HomewardBone", "Homeward Bone", 55, 75, 0),
        ("HomewardBone", "Homeward Bone", 57, 77, 0),
        # Old Cell Key is in the chest at (58,78), not a ground pickup
        # Dragon Stone area
        ("Consumable", "Dragon Torso Stone", 105, 38, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 110, 35, 800),
        ("Consumable", "Lightning Blade", 108, 32, 0),
        # Karla area
        ("Consumable", "Xanthous Ashes", 82, 88, 0),
        ("RingDrop", "Dusk Crown Ring", 84, 90, 0),
        ("Ember", "Ember", 88, 85, 0),
        ("Ember", "Ember", 92, 88, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 95, 92, 2000),
        # Exit area
        ("WeaponDrop", "Pickaxe", 115, 32, 0),
        ("SoulOrb", "Large Soul of a Weary Warrior", 130, 28, 2000),
        ("UndeadBoneShard", "Undead Bone Shard", 135, 30, 0),
    ]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # Chests — DS3 Irithyll Dungeon: 4 Mimics, 1 regular chest
    # Mimic drops Estus Shard (upper cells)
    entities.append(make_entity("Chest", 65 * 16, 48 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("loot_name", "String", "Estus Shard"),
        make_field("is_mimic", "Bool", True),
    ]))
    # Mimic drops Dark Clutch Ring (sewer area)
    entities.append(make_entity("Chest", 62 * 16, 82 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("loot_name", "String", "Dark Clutch Ring"),
        make_field("is_mimic", "Bool", True),
    ]))
    # Mimic drops Dragonslayer Lightning Arrow (near giant)
    entities.append(make_entity("Chest", 85 * 16, 78 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_name", "String", "Dragonslayer Lightning Arrow"),
        make_field("is_mimic", "Bool", True),
    ]))
    # Mimic drops Titanite Scale x2 (Karla area)
    entities.append(make_entity("Chest", 78 * 16, 85 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", True),
    ]))
    # Regular chest with Old Cell Key (sewer)
    entities.append(make_entity("Chest", 58 * 16, 78 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_name", "String", "Old Cell Key"),
        make_field("is_mimic", "Bool", False),
    ]))

    # NPCs — DS3 Irithyll Dungeon: Siegward in cell, Karla in deep cell
    entities.append(make_entity("Npc", 92 * 16, 56 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D4A520"), make_field("dialogue", "String", "Mmm|You have my thanks|I seem to be trapped in this cell")]))
    entities.append(make_entity("Npc", 90 * 16, 84 * 16, [make_field("name", "String", "Karla"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#4A0080"), make_field("dialogue", "String", "What do you want?|I can teach you sorceries and pyromancies")]))

    entities.append(make_entity("FogGate", 142 * 16, 32 * 16, [
        make_field("dest_area", "String", "ProfanedCapital"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # To Archdragon Peak (dragon gesture path)
    entities.append(make_entity("FogGate", 135 * 16, 8 * 16, [
        make_field("dest_area", "String", "ArchdragonPeak"),
        make_field("dest_x", "Float", 280.0),
        make_field("dest_y", "Float", 2160.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights - dim cold prison lighting
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.7), make_field("g", "Float", 0.7), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 52 * 16, 58 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.6), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 135 * 16, 32 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.7), make_field("g", "Float", 0.7), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))

    # === ADDITIONAL INTERNAL STRUCTURES — dungeon ===
    # Entry cells — cell bars and walls
    fill_tiles(chunk, TILE_WALL, 12, 18, 14, 20)
    fill_tiles(chunk, TILE_WALL, 22, 22, 24, 24)
    fill_tiles(chunk, TILE_WALL, 30, 18, 32, 20)
    # Main prison hall — support pillars
    fill_tiles(chunk, TILE_WALL, 40, 38, 42, 40)
    fill_tiles(chunk, TILE_WALL, 52, 42, 54, 44)
    fill_tiles(chunk, TILE_WALL, 62, 48, 64, 50)
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 57)
    fill_tiles(chunk, TILE_WALL, 58, 58, 60, 60)
    # Jailer corridors — cell dividers
    fill_tiles(chunk, TILE_WALL, 75, 55, 77, 57)
    fill_tiles(chunk, TILE_WALL, 85, 52, 87, 54)
    fill_tiles(chunk, TILE_WALL, 95, 58, 97, 60)
    fill_tiles(chunk, TILE_WALL, 105, 55, 107, 57)
    fill_tiles(chunk, TILE_WALL, 80, 65, 82, 67)
    fill_tiles(chunk, TILE_WALL, 90, 68, 92, 70)
    # Dungeon depths — cages and torture equipment
    fill_tiles(chunk, TILE_WALL, 108, 22, 110, 24)
    fill_tiles(chunk, TILE_WALL, 118, 28, 120, 30)
    fill_tiles(chunk, TILE_WALL, 128, 25, 130, 27)
    fill_tiles(chunk, TILE_WALL, 115, 35, 117, 37)
    fill_tiles(chunk, TILE_WALL, 138, 30, 140, 32)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  IrithyllDungeon (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "IrithyllDungeon", chunk, entities


def make_profaned_capital():
    """Profaned Capital — faithful DS3 layout.

    Real DS3 progression (from walkthrough):
    1. Enter from Irithyll Dungeon via stone bridge (Gargoyle ambush)
    2. Bonfire tower (Gilligan's body, stretch out gesture)
    3. BOSS PATH (east): bridge → jailer room 1 → jailer room 2 → Yhorm arena
    4. EXPLORE PATH (south): descent → upper ruins → toxic pool → church
       (Monstrosities) → Siegward's cell → Court Sorcerer roof → giant room

    Design doc reference: docs/maps/ProfanedCapital.json (3400x3200)
    Grid: 160x160, entry NW, Yhorm arena NE
    """
    chunk = new_chunk()

    # 1. ENTRY BRIDGE from Irithyll Dungeon — NW narrow corridor
    fill_tiles(chunk, TILE_GROUND, 4, 8, 14, 14)

    # 2. BONFIRE TOWER — small room near entry
    fill_tiles(chunk, TILE_GROUND, 10, 6, 30, 24)
    carve_ellipse(chunk, 20, 14, 8, 6)

    # 3. BOSS PATH — bridge east from tower to Yhorm arena
    fill_tiles(chunk, TILE_GROUND, 28, 10, 50, 16)
    # Bridge gap (drop-down shortcut)
    fill_tiles(chunk, TILE_WALL, 38, 11, 40, 15)

    # First jailer room (4 jailers + fire gargoyle)
    fill_tiles(chunk, TILE_GROUND, 48, 6, 68, 24)
    # Fire vessel obstacle
    fill_tiles(chunk, TILE_WALL, 56, 12, 58, 16)

    # Connection bridge between jailer rooms
    fill_tiles(chunk, TILE_GROUND, 65, 10, 70, 20)

    # Second jailer room (jailers + gargoyle + 2 mimics + 1 real chest)
    fill_tiles(chunk, TILE_GROUND, 68, 6, 90, 24)
    # Pillar
    fill_tiles(chunk, TILE_WALL, 76, 10, 78, 14)
    # Side chests area
    fill_tiles(chunk, TILE_WALL, 84, 16, 86, 20)

    # Connection to Yhorm arena
    fill_tiles(chunk, TILE_GROUND, 86, 12, 96, 18)

    # Yhorm's throne room — large NE arena
    carve_ellipse(chunk, 108, 18, 20, 16)
    fill_tiles(chunk, TILE_GROUND, 88, 4, 130, 36)
    # Throne pillars
    fill_tiles(chunk, TILE_WALL, 96, 8, 98, 12)
    fill_tiles(chunk, TILE_WALL, 118, 24, 120, 28)

    # 4. EXPLORE PATH — descent south from bonfire tower
    fill_tiles(chunk, TILE_GROUND, 12, 22, 22, 38)

    # Upper ruins — connecting area
    fill_tiles(chunk, TILE_GROUND, 16, 34, 44, 48)
    # Broken wall obstacles
    fill_tiles(chunk, TILE_WALL, 22, 38, 24, 42)
    fill_tiles(chunk, TILE_WALL, 34, 40, 36, 44)

    # Main ruins / streets
    fill_tiles(chunk, TILE_GROUND, 20, 46, 58, 66)
    # Ruined house walls
    fill_tiles(chunk, TILE_WALL, 28, 50, 32, 54)
    fill_tiles(chunk, TILE_WALL, 40, 52, 44, 56)
    fill_tiles(chunk, TILE_WALL, 48, 58, 52, 62)

    # Toxic pool — SE area with POISON tiles
    fill_tiles(chunk, TILE_POISON, 42, 56, 72, 80)
    # Ground edges around pool
    fill_tiles(chunk, TILE_GROUND, 44, 58, 70, 78)
    # Stone platforms in pool
    fill_tiles(chunk, TILE_GROUND, 48, 62, 54, 66)
    fill_tiles(chunk, TILE_GROUND, 58, 70, 64, 74)

    # Church (Monstrosities of Sin building) — south
    fill_tiles(chunk, TILE_GROUND, 22, 64, 50, 84)
    carve_ellipse(chunk, 36, 74, 10, 8)
    # Church ornate door walls
    fill_tiles(chunk, TILE_WALL, 28, 68, 30, 72)
    fill_tiles(chunk, TILE_WALL, 42, 80, 44, 84)

    # Siegward's cell — east of upper ruins
    fill_tiles(chunk, TILE_GROUND, 52, 44, 68, 56)
    carve_ellipse(chunk, 60, 50, 6, 4)
    # Cell wall
    fill_tiles(chunk, TILE_WALL, 54, 46, 56, 50)

    # Court Sorcerer roof — above church area
    fill_tiles(chunk, TILE_GROUND, 44, 38, 64, 50)
    # Roof obstacles
    fill_tiles(chunk, TILE_WALL, 50, 42, 52, 46)

    # Connection: upper ruins to court sorcerer roof
    fill_tiles(chunk, TILE_GROUND, 38, 42, 48, 48)

    # Connection: roof to Siegward's cell
    fill_tiles(chunk, TILE_GROUND, 58, 42, 64, 46)

    # Giant room — east side
    fill_tiles(chunk, TILE_GROUND, 66, 54, 88, 72)
    # Giant's tunnel
    fill_tiles(chunk, TILE_GROUND, 74, 64, 82, 70)

    # Shortcut back to Irithyll Dungeon
    fill_tiles(chunk, TILE_GROUND, 84, 58, 94, 66)

    # Connection: streets to church
    fill_tiles(chunk, TILE_GROUND, 28, 62, 34, 66)

    # Connection: streets to toxic pool
    fill_tiles(chunk, TILE_GROUND, 52, 58, 58, 62)

    # Connection: church to giant room
    fill_tiles(chunk, TILE_GROUND, 46, 78, 68, 64)

    # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    spawn_px, spawn_py = 18 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 18 * 16, 12 * 16))     # Profaned Capital
    entities.append(make_entity("Bonfire", 108 * 16, 18 * 16))    # Yhorm the Giant

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 108 * 16, 14 * 16))

    # --- Enemies ---
    # DS3 Profaned Capital enemies: Handmaids (Jailer), Gargoyles (Headless),
    # Monstrosities of Sin (GiantSlave), Sewer Centipedes (ManGrub),
    # Rats, Crystal Lizards, Mimic
    enemy_data = [
        # Entry bridge — Headless Gargoyle ambush (DS3: gargoyle on bridge)
        ("Gargoyle", 10, 11),
        # Boss path bridge — Gargoyle patrol
        ("Gargoyle", 44, 12), ("Gargoyle", 48, 14),
        # First jailer room — Jailer Handmaids + fire-casting Gargoyle (wiki: 4 jailers in white + gargoyle)
        ("Jailer", 52, 10), ("Jailer", 54, 14), ("Jailer", 60, 8),
        ("Jailer", 62, 18), ("Gargoyle", 64, 14),
        # Second jailer room — more jailers + gargoyle lurks up and to the right
        ("Jailer", 72, 10), ("Jailer", 74, 16), ("Jailer", 80, 12),
        ("Gargoyle", 88, 8),
        # Upper ruins — Jailer patrols (wiki: 2 invisible jailers near Jailer's Key Ring)
        ("Jailer", 20, 38), ("Jailer", 30, 42),
        ("Jailer", 38, 44),
        # Ruins/streets — Gargoyle patrols + jailer
        ("Gargoyle", 34, 52), ("Gargoyle", 50, 60),
        ("Jailer", 26, 56),
        # Toxic pool — Rats (wiki: rats respawn in giant's room)
        ("Rat", 52, 64), ("Rat", 60, 72), ("Rat", 66, 68),
        # Crystal Lizards (wiki: 3 — one at hole jump, one in left tunnel, one down hallway)
        ("CrystalLizard", 56, 68), ("CrystalLizard", 62, 64), ("CrystalLizard", 56, 44),
        # Church — Monstrosities of Sin (wiki: 3 in the church + 1 in separate room = 4)
        ("GiantSlave", 30, 72), ("GiantSlave", 36, 78), ("GiantSlave", 42, 74),
        # Monstrosity of Sin — separate room above church (wiki: "single Monstrosity of Sin")
        ("GiantSlave", 48, 46),
        # Sewer Centipedes in toxic pool (wiki: insect-like creatures)
        ("ManGrub", 58, 70), ("ManGrub", 64, 74),
        # Avaricious Being — hostile NPC with Gargoyle Flame Hammer (wiki: drops Logan's Scroll)
        ("MiniBoss", 48, 42),
        # Siegward cell area — Jailer guard
        ("Jailer", 62, 48),
        # Giant room — rats and Giant Slave (wiki: giant in treasure room, rats respawn)
        ("Rat", 70, 60), ("Rat", 74, 66), ("Rat", 80, 62),
        ("GiantSlave", 76, 60),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- NPCs ---
    # Siegward — in cell
    entities.append(make_entity("Npc", 60 * 16, 50 * 16, [
        make_field("name", "String", "Siegward"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#D4A520"),
        make_field("dialogue", "String",
            "...Yhorm, old friend|I promised you|On the day you lost your mind|I would be there to end it"),
    ]))

    # --- Items — DS3 Profaned Capital (wiki-verified) ---
    items = [
        # Gilligan's ladder area
        ("UndeadBoneShard", "Undead Bone Shard", 14, 10, 0),
        ("Consumable", "Poison Arrow", 50, 38, 0),  # near Avaricious Being roof (wiki)
        # Boss path bridge
        ("SoulOrb", "Large Soul of a Weary Warrior", 48, 14, 1000),
        ("Consumable", "Onislayer Greatarrow", 36, 12, 0),
        # First jailer room
        ("Consumable", "Rusted Coin", 62, 20, 0),
        ("Consumable", "Dung Pie", 68, 58, 0),  # giant room (wiki: all 4 in giant room)
        # Second jailer room
        ("Consumable", "Rusted Coin", 90, 22, 0),
        ("Consumable", "Blooming Purple Moss Clump", 84, 18, 0),
        ("Consumable", "Blooming Purple Moss Clump", 86, 20, 0),
        ("Consumable", "Blooming Purple Moss Clump", 88, 22, 0),
        ("Consumable", "Dung Pie", 72, 62, 0),  # giant room
        # Upper ruins
        ("Consumable", "Lightning Bolt", 28, 42, 0),
        ("Consumable", "Dung Pie", 84, 68, 0),  # giant room
        ("Consumable", "Dung Pie", 82, 56, 0),  # giant room
        ("TitaniteShard", "Large Titanite Shard", 86, 60, 0),  # giant room (wiki: 2x in giant room)
        # Toxic pool / sewer
        ("Consumable", "Purging Stone", 50, 70, 0),
        ("Consumable", "Purging Stone", 32, 80, 0),
        ("Consumable", "Poison Gem", 54, 72, 0),
        ("RingDrop", "Cursebite Ring", 64, 76, 0),
        ("Consumable", "Shriving Stone", 68, 74, 0),
        ("Consumable", "Dragonslayer Lightning Arrow", 60, 70, 0),
        ("Consumable", "Rusted Gold Coin", 40, 44, 0),
        # Church — Monstrosity of Sin area
        ("WeaponDrop", "Eleonora", 36, 76, 0),
        # Court sorcerer rooftop
        ("ArmorDrop", "Court Sorcerer Set", 48, 46, 0),
        ("Consumable", "Logan's Scroll", 52, 40, 0),
        ("Consumable", "Rubbish", 54, 42, 0),
        ("Consumable", "Stretch Out Gesture", 14, 14, 0),  # Gilligan body at bonfire tower (wiki)
        # Siegward's cell area
        ("RingDrop", "Covetous Gold Serpent Ring", 64, 52, 0),
        ("Consumable", "Jailer's Key Ring", 58, 50, 0),
        ("Consumable", "Prisoner Chief's Ashes", 60, 54, 0),
        ("Consumable", "Wrath of the Gods", 56, 48, 0),
        # Giant room / treasure room
        ("Consumable", "Profaned Flame", 78, 62, 0),
        ("TitaniteShard", "Large Titanite Shard", 82, 64, 0),
        ("TitaniteShard", "Titanite Chunk", 84, 60, 0),
        # Yhorm arena
        ("WeaponDrop", "Storm Ruler", 108, 16, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests — DS3 Profaned Capital (wiki-verified) ---
    # Mimic: Court Sorcerer's Staff (upper capital building)
    entities.append(make_entity("Chest", 80 * 16, 45 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Court Sorcerer's Staff"),
        make_field("is_mimic", "Bool", True)]))
    # Mimic: Greatshield of Glory (second jailer room, side by side with Rusted Gold Coin mimic)
    entities.append(make_entity("Chest", 76 * 16, 22 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Greatshield of Glory"),
        make_field("is_mimic", "Bool", True)]))
    # Mimic: Rusted Gold Coin (second jailer room, side by side with Greatshield of Glory)
    entities.append(make_entity("Chest", 70 * 16, 24 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Rusted Gold Coin"),
        make_field("is_mimic", "Bool", True)]))
    # Mimic: Dragonslayer Lightning Arrow (wiki: ladder room above giant area)
    entities.append(make_entity("Chest", 80 * 16, 56 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Dragonslayer Lightning Arrow"),
        make_field("is_mimic", "Bool", True)]))
    # Regular chest: Ember (second jailer room, wiki: "solitary legitimate chest")
    entities.append(make_entity("Chest", 82 * 16, 20 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Ember"),
        make_field("is_mimic", "Bool", False)]))

    # --- Fog Gates ---
    # Back to Irithyll Dungeon (NW entry)
    entities.append(make_entity("FogGate", 6 * 16, 10 * 16, [
        make_field("dest_area", "String", "IrithyllDungeon"),
        make_field("dest_x", "Float", 2700.0),
        make_field("dest_y", "Float", 2300.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Bonfire tower — warm torchlight
    entities.append(make_entity("Light", 18 * 16, 12 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    # Toxic pool — sickly green glow
    entities.append(make_entity("Light", 56 * 16, 68 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    # Church — dim orange
    entities.append(make_entity("Light", 36 * 16, 74 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    # Yhorm arena — profaned flame glow
    entities.append(make_entity("Light", 108 * 16, 14 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.5)]))
    # Siegward cell — moonlight
    entities.append(make_entity("Light", 60 * 16, 50 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.3)]))

    # === ADDITIONAL INTERNAL STRUCTURES — profaned capital ===
    # Entry bonfire tower — ruined walls
    fill_tiles(chunk, TILE_WALL, 12, 38, 14, 40)
    fill_tiles(chunk, TILE_WALL, 22, 42, 24, 44)
    fill_tiles(chunk, TILE_WALL, 30, 38, 32, 40)
    # Gargoyle bridge — bridge supports
    fill_tiles(chunk, TILE_WALL, 45, 35, 47, 37)
    fill_tiles(chunk, TILE_WALL, 55, 32, 57, 34)
    fill_tiles(chunk, TILE_WALL, 65, 35, 67, 37)
    # Upper capital — building ruins
    fill_tiles(chunk, TILE_WALL, 72, 40, 74, 42)
    fill_tiles(chunk, TILE_WALL, 82, 45, 84, 47)
    fill_tiles(chunk, TILE_WALL, 92, 42, 94, 44)
    fill_tiles(chunk, TILE_WALL, 78, 50, 80, 52)
    fill_tiles(chunk, TILE_WALL, 88, 52, 90, 54)
    # Yhorm arena — throne room pillars
    fill_tiles(chunk, TILE_WALL, 95, 12, 97, 15)
    fill_tiles(chunk, TILE_WALL, 115, 10, 117, 13)
    fill_tiles(chunk, TILE_WALL, 105, 18, 107, 20)
    fill_tiles(chunk, TILE_WALL, 125, 14, 127, 16)
    fill_tiles(chunk, TILE_WALL, 135, 18, 137, 20)
    # Underground — rubble and columns
    fill_tiles(chunk, TILE_WALL, 42, 58, 44, 60)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)
    fill_tiles(chunk, TILE_WALL, 65, 60, 67, 62)
    fill_tiles(chunk, TILE_WALL, 50, 68, 52, 70)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)

    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  ProfanedCapital (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "ProfanedCapital", chunk, entities


def make_anor_londo():
    """Anor Londo - grand cathedral with Aldrich, Devourer of Gods boss.
    Faithful DS3 layout: entrance hall (rotating staircase) -> royal avenue ->
    Silver Knight hall (with Deep Accursed) -> staircase corridor ->
    Darkmoon Temple (Aldrich arena with abyss swamp). Side path to Yorshka's
    church via invisible platforms. DS1 nostalgia with faded golden grandeur.
    """
    chunk = new_chunk()
    entities = []

    # === Cathedral entrance hall (west, from Irithyll rotating staircase) ===
    fill_tiles(chunk, TILE_GROUND, 6, 26, 40, 55)
    # High stone pillars (decorative wall obstacles)
    fill_tiles(chunk, TILE_WALL, 14, 32, 16, 38)
    fill_tiles(chunk, TILE_WALL, 26, 34, 28, 40)
    fill_tiles(chunk, TILE_WALL, 20, 46, 22, 50)

    # === Royal avenue (wide golden corridor east) ===
    fill_tiles(chunk, TILE_GROUND, 36, 30, 82, 58)
    # Knight statue pillars along the avenue
    fill_tiles(chunk, TILE_WALL, 48, 35, 50, 40)
    fill_tiles(chunk, TILE_WALL, 62, 42, 64, 47)
    fill_tiles(chunk, TILE_WALL, 74, 36, 76, 41)

    # === Yorshka side path (south from royal avenue) ===
    fill_tiles(chunk, TILE_GROUND, 52, 56, 68, 82)
    # Narrow invisible-platform-style path
    fill_tiles(chunk, TILE_GROUND, 56, 80, 72, 100)
    # Yorshka's church (hidden prayer room)
    carve_ellipse(chunk, 62, 92, 10, 8)
    fill_tiles(chunk, TILE_GROUND, 50, 82, 76, 104)

    # === Silver Knight hall (large council chamber) ===
    fill_tiles(chunk, TILE_GROUND, 78, 26, 118, 56)
    carve_ellipse(chunk, 98, 40, 14, 10)
    # Hall pillars
    fill_tiles(chunk, TILE_WALL, 86, 30, 88, 36)
    fill_tiles(chunk, TILE_WALL, 106, 38, 108, 44)

    # === Staircase corridor (Silver Knight gauntlet to boss) ===
    fill_tiles(chunk, TILE_GROUND, 114, 32, 142, 58)
    # Corridor walls creating narrow passage
    fill_tiles(chunk, TILE_WALL, 120, 34, 122, 38)
    fill_tiles(chunk, TILE_WALL, 132, 42, 134, 46)

    # === Darkmoon Temple / Aldrich arena (SE) ===
    fill_tiles(chunk, TILE_GROUND, 100, 55, 155, 110)
    carve_ellipse(chunk, 128, 82, 24, 20)
    # Abyss swamp (poison tiles) in center of arena
    fill_tiles(chunk, TILE_POISON, 116, 70, 140, 94)
    # Arena stone pillars
    fill_tiles(chunk, TILE_WALL, 108, 62, 110, 68)
    fill_tiles(chunk, TILE_WALL, 146, 88, 148, 94)
    fill_tiles(chunk, TILE_WALL, 122, 98, 124, 103)

    # === Connections ===
    # Entrance hall to Royal avenue (already adjacent at x=36-40)
    # Royal avenue to Silver Knight hall
    fill_tiles(chunk, TILE_GROUND, 78, 36, 82, 52)
    # Silver Knight hall to Staircase corridor
    fill_tiles(chunk, TILE_GROUND, 114, 38, 118, 52)
    # Staircase corridor down to Aldrich arena
    fill_tiles(chunk, TILE_GROUND, 136, 55, 144, 62)
    # Royal avenue south to Yorshka path
    fill_tiles(chunk, TILE_GROUND, 56, 55, 62, 62)

    # --- Spawn from Irithyll rotating staircase ---
    spawn_px, spawn_py = 10 * 16, 38 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires --- DS3: Anor Londo, Prison Tower, Aldrich Devourer of Gods
    entities.append(make_entity("Bonfire", 10 * 16, 38 * 16))
    entities.append(make_entity("Bonfire", 62 * 16, 90 * 16))   # Prison Tower (invisible bridge area)
    entities.append(make_entity("Bonfire", 128 * 16, 85 * 16))  # Aldrich boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 128 * 16, 78 * 16))

    # --- Enemies — DS3 Anor Londo: Silver Knights (~8), Giant Slave (1),
    # Deep Accursed (1), Deacons (pyromancers + 3 before fog), Rotten Flesh (ManGrub)
    enemy_data = [
        # Cathedral entrance stairs — 2 Silver Knights (wiki: "two silver knights attack")
        ("SilverKnight", 20, 35), ("SilverKnight", 34, 42),
        # Right side — red-eyed Silver Knight (wiki: "red eyed Silver Knight")
        ("SilverKnight", 42, 38),
        # Royal avenue patrol — Silver Knights guard the corridor (DS3: knights throughout)
        ("SilverKnight", 52, 42), ("SilverKnight", 64, 48),
        ("SilverKnight", 48, 50), ("SilverKnight", 70, 44),
        # Silver Knight hall — knight pair guarding council chamber entrance
        ("SilverKnight", 82, 38), ("SilverKnight", 90, 42),
        # Giant Slave — giant archer on upper level (wiki: Giant Slave enemy)
        ("GiantSlave", 38, 52),
        # Main chamber — Deacon pyromancers casting fireballs from other side
        ("Deacon", 55, 45), ("Deacon", 68, 40), ("Deacon", 70, 46),
        # Main chamber — Rotten Flesh of Aldrich / slimes (wiki: "dispatch slimes and deacons")
        ("ManGrub", 142, 75), ("ManGrub", 148, 82), ("ManGrub", 136, 68),
        ("ManGrub", 124, 88), ("ManGrub", 132, 92),
        # Additional slimes in dark corners of main hall
        ("ManGrub", 130, 65), ("ManGrub", 115, 72),
        # Corner — Deep Accursed at revolving switch (wiki: "Deep Accursed waiting for you")
        ("DeepAccursed", 100, 40),
        # Hallway to fog gate — 3 Deacons (wiki: "three enemies from Deacons of the Deep boss fight")
        ("Deacon", 125, 38), ("Deacon", 135, 44), ("Deacon", 138, 50),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items — DS3 Anor Londo (wiki-verified) ---
    items = [
        # Top of stairs — left side (DS3: after climbing stairs past Silver Knights)
        ("SoulOrb", "Large Soul of a Weary Warrior", 18, 40, 1000),
        # Right side — red-eyed Silver Knight corpse (DS3: loot corpse)
        ("SoulOrb", "Soul of a Crestfallen Knight", 22, 42, 1000),
        # Dead giant blacksmith room (DS3: Giant's Coal in his hand)
        ("Consumable", "Giant's Coal", 26, 48, 0),
        # Main chamber — near pyromancers (DS3: corpse near fireball casters)
        ("Consumable", "Proof of a Concord Kept", 96, 48, 0),
        # Opposite staircase (DS3: corpse with Moonlight Arrow x5)
        ("Consumable", "Moonlight Arrow", 120, 60, 0),
        ("Consumable", "Moonlight Arrow", 121, 61, 0),
        ("Consumable", "Moonlight Arrow", 122, 60, 0),
        ("Consumable", "Moonlight Arrow", 120, 62, 0),
        ("Consumable", "Moonlight Arrow", 122, 62, 0),
        # Deep Accursed area near revolving platform (DS3: ring drop)
        ("RingDrop", "Aldrich's Ruby", 100, 50, 0),
        # Yorshka tower beam (DS3: drop down from invisible bridge)
        ("WeaponDrop", "Painting Guardian's Curved Sword", 58, 88, 0),
        # Below beam in tower (DS3: further drop)
        ("ArmorDrop", "Painting Guardian Set", 60, 94, 0),
        # Post-boss elevator — Gwynevere's chamber (DS3: after defeating Aldrich)
        ("RingDrop", "Sun Princess Ring", 130, 90, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests — DS3 Anor Londo (wiki-verified) ---
    # Regular chest: Estus Shard (main hall, left wall facing from stairs)
    entities.append(make_entity("Chest", 125 * 16, 55 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("loot_name", "String", "Estus Shard"),
        make_field("is_mimic", "Bool", False),
    ]))

    # --- NPCs ---
    # Anri of Astora — summon sign near main doors (wiki: "purple sign on the floor")
    entities.append(make_entity("Npc", 128 * 16, 72 * 16, [
        make_field("name", "String", "Anri of Astora"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#d0d0ff"),
        make_field("dialogue", "String",
            "Good day|I am Anri of Astora|Would you help me|defeat Aldrich together?"),
    ]))
    # Company Captain Yorshka — Darkmoon Tomb, reached from Prison Tower bonfire
    entities.append(make_entity("Npc", 62 * 16, 92 * 16, [
        make_field("name", "String", "Company Captain Yorshka"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#E0E8F0"),
        make_field("dialogue", "String",
            "I am Yorshka|Captain of the Darkmoon Knights|"
            "The Darkmoon remains true to its duty"),
    ]))

    # --- Fog Gates ---
    # Back to Irithyll (rotating staircase, west)
    entities.append(make_entity("FogGate", 5 * 16, 34 * 16, [
        make_field("dest_area", "String", "Irithyll"),
        make_field("dest_x", "Float", 2400.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Lothric Castle (after defeating Aldrich, east)
    entities.append(make_entity("FogGate", 152 * 16, 88 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Cathedral entrance — faded golden
    entities.append(make_entity("Light", 10 * 16, 38 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.5)]))
    # Royal avenue — false sunlight
    entities.append(make_entity("Light", 60 * 16, 44 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.9),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    # Yorshka church — darkmoon blue
    entities.append(make_entity("Light", 62 * 16, 90 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.6),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.5)]))
    # Silver Knight hall — dim gold
    entities.append(make_entity("Light", 98 * 16, 40 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.9),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.35)]))
    # Deep Accursed lair — abyss purple
    entities.append(make_entity("Light", 100 * 16, 40 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.1),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.5)]))
    # Aldrich arena — dark abyss glow
    entities.append(make_entity("Light", 128 * 16, 82 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.6)]))

    # === ADDITIONAL INTERNAL STRUCTURES — AnorLondo cathedral ===
    # Cathedral entrance pillars
    fill_tiles(chunk, TILE_WALL, 18, 32, 20, 36)
    fill_tiles(chunk, TILE_WALL, 28, 28, 30, 32)
    # Royal avenue — stone pillars and silver knight positions
    fill_tiles(chunk, TILE_WALL, 42, 38, 44, 42)
    fill_tiles(chunk, TILE_WALL, 55, 35, 57, 39)
    fill_tiles(chunk, TILE_WALL, 68, 40, 70, 44)
    fill_tiles(chunk, TILE_WALL, 48, 48, 50, 52)
    fill_tiles(chunk, TILE_WALL, 62, 46, 64, 50)
    # Yorshka side path — church pews and altar stones
    fill_tiles(chunk, TILE_WALL, 58, 80, 60, 84)
    fill_tiles(chunk, TILE_WALL, 68, 85, 70, 88)
    fill_tiles(chunk, TILE_WALL, 52, 88, 54, 92)
    # Silver Knight hall — hall pillars
    fill_tiles(chunk, TILE_WALL, 92, 35, 94, 38)
    fill_tiles(chunk, TILE_WALL, 100, 38, 102, 42)
    fill_tiles(chunk, TILE_WALL, 108, 35, 110, 38)
    fill_tiles(chunk, TILE_WALL, 96, 44, 98, 48)
    # Staircase corridor — stone railings
    fill_tiles(chunk, TILE_WALL, 112, 52, 114, 55)
    fill_tiles(chunk, TILE_WALL, 118, 58, 120, 62)
    fill_tiles(chunk, TILE_WALL, 125, 65, 127, 68)
    # Aldrich arena — cathedral columns and debris
    fill_tiles(chunk, TILE_WALL, 118, 78, 120, 82)
    fill_tiles(chunk, TILE_WALL, 138, 82, 140, 86)
    fill_tiles(chunk, TILE_WALL, 128, 92, 130, 96)
    fill_tiles(chunk, TILE_WALL, 142, 88, 144, 92)
    fill_tiles(chunk, TILE_WALL, 132, 76, 134, 79)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  AnorLondo (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "AnorLondo", chunk, entities


def make_lothric_castle():
    """Lothric Castle - Dragonslayer Armour boss arena.

    Faithful DS3 layout (spatial progression on 160x160 grid):
    Entry from AnorLondo (west) -> castle gate -> outer corridor -> dragon barracks
    (open, with dragon wall obstacles) -> inner castle stairs -> wall bridge
    (Dragonslayer Armour arena, large open area) -> Grand Archives exit (NE).
    Side path south to ConsumedKingsGarden.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # TERRAIN
    # ================================================================

    # 1. Castle gate (SW entry from AnorLondo)
    fill_tiles(chunk, TILE_GROUND, 6, 18, 35, 45)
    # Pillar walls flanking the gate
    fill_tiles(chunk, TILE_WALL, 12, 24, 14, 30)
    fill_tiles(chunk, TILE_WALL, 24, 28, 26, 34)

    # 2. Outer corridor (east from gate)
    fill_tiles(chunk, TILE_GROUND, 30, 22, 68, 48)
    # Statue walls along corridor
    fill_tiles(chunk, TILE_WALL, 42, 28, 44, 33)
    fill_tiles(chunk, TILE_WALL, 56, 35, 58, 40)

    # 3. Dragon barracks (open area NE)
    fill_tiles(chunk, TILE_GROUND, 58, 10, 102, 40)
    # Dragon skeleton wall obstacles
    fill_tiles(chunk, TILE_WALL, 68, 15, 72, 20)
    fill_tiles(chunk, TILE_WALL, 88, 28, 92, 33)

    # 4. Inner stairs (narrow passage NE)
    fill_tiles(chunk, TILE_GROUND, 95, 35, 118, 58)
    # Wall obstacles along stairs
    fill_tiles(chunk, TILE_WALL, 102, 40, 104, 44)
    fill_tiles(chunk, TILE_WALL, 110, 48, 112, 52)

    # 5. Wall bridge / Dragonslayer Armour arena (NE large)
    fill_tiles(chunk, TILE_GROUND, 108, 50, 155, 88)
    # Rounded arena shape
    carve_ellipse(chunk, 132, 68, 20, 16)
    # Arena pillars
    fill_tiles(chunk, TILE_WALL, 118, 58, 120, 63)
    fill_tiles(chunk, TILE_WALL, 145, 72, 147, 77)

    # 6. Garden side path (south)
    fill_tiles(chunk, TILE_GROUND, 35, 45, 55, 68)
    carve_ellipse(chunk, 45, 56, 8, 6)

    # 7. Grand Archives exit (far NE)
    fill_tiles(chunk, TILE_GROUND, 148, 55, 158, 72)

    # --- Connections between areas ---
    fill_tiles(chunk, TILE_GROUND, 58, 28, 62, 42)     # Corridor -> Dragon barracks
    fill_tiles(chunk, TILE_GROUND, 95, 25, 102, 38)    # Barracks -> Inner stairs
    fill_tiles(chunk, TILE_GROUND, 112, 52, 120, 58)   # Stairs -> Arena
    fill_tiles(chunk, TILE_GROUND, 42, 45, 48, 50)     # Corridor -> Garden side path

    # ================================================================
    # ADDITIONAL INTERNAL STRUCTURES — castle architecture
    # ================================================================
    # Castle gate battlements
    fill_tiles(chunk, TILE_WALL, 10, 20, 11, 24)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 26)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 38)
    # Corridor pillars
    fill_tiles(chunk, TILE_WALL, 38, 28, 39, 32)
    fill_tiles(chunk, TILE_WALL, 48, 34, 49, 38)
    fill_tiles(chunk, TILE_WALL, 62, 30, 63, 34)
    # Dragon barracks — more dragon bones and debris
    fill_tiles(chunk, TILE_WALL, 72, 12, 74, 15)
    fill_tiles(chunk, TILE_WALL, 82, 16, 84, 18)
    fill_tiles(chunk, TILE_WALL, 92, 22, 94, 25)
    fill_tiles(chunk, TILE_WALL, 76, 30, 78, 32)
    fill_tiles(chunk, TILE_WALL, 96, 34, 98, 37)
    fill_tiles(chunk, TILE_WALL, 65, 18, 67, 20)
    # Inner stairs — wall buttresses
    fill_tiles(chunk, TILE_WALL, 98, 38, 100, 40)
    fill_tiles(chunk, TILE_WALL, 105, 45, 107, 47)
    fill_tiles(chunk, TILE_WALL, 115, 52, 117, 55)
    # Arena — Dragonslayer Armour arena pillars
    fill_tiles(chunk, TILE_WALL, 122, 55, 124, 58)
    fill_tiles(chunk, TILE_WALL, 138, 60, 140, 63)
    fill_tiles(chunk, TILE_WALL, 152, 68, 154, 72)
    fill_tiles(chunk, TILE_WALL, 128, 78, 130, 82)
    fill_tiles(chunk, TILE_WALL, 142, 82, 144, 86)
    fill_tiles(chunk, TILE_WALL, 135, 72, 137, 75)
    # Garden side path — overgrown walls
    fill_tiles(chunk, TILE_WALL, 40, 52, 42, 55)
    fill_tiles(chunk, TILE_WALL, 50, 58, 52, 60)
    fill_tiles(chunk, TILE_WALL, 38, 62, 40, 65)

    # ================================================================
    # ENTITIES
    # ================================================================

    # --- Player Spawn ---
    spawn_px, spawn_py = 10 * 16, 30 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires --- DS3: Dragon Barracks, Lothric Castle, Grand Archives, Dragonslayer Armour
    entities.append(make_entity("Bonfire", 42 * 16, 35 * 16))    # Dragon Barracks (entry)
    entities.append(make_entity("Bonfire", 80 * 16, 25 * 16))    # Lothric Castle
    entities.append(make_entity("Bonfire", 132 * 16, 68 * 16))   # Dragonslayer Armour (boss)
    entities.append(make_entity("Bonfire", 146 * 16, 85 * 16))   # Grand Archives

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 132 * 16, 62 * 16))  # Dragonslayer Armour

    # --- Enemies ---
    # DS3 Lothric Castle enemies: Lothric Knights, Hollow Soldiers, Hollow Assassins,
    # Hollow Priests (DarkMage), Winged Knights, Pus of Man, Boreal Outrider Knight,
    # Mimic, Crystal Lizards, Lothric Wyverns
    enemy_positions = [
        # Castle gate area — Lothric Knight + Hollow Priest healing combo
        ("LothricKnight", 18, 28), ("DarkMage", 22, 30),              # Priest heals knight (DS3)
        ("HollowSoldier", 14, 34), ("HollowSoldier", 20, 40),        # Crossbow hollows at gate
        # Outer corridor — Lothric Knights, Hollow Assassins, Starved Hounds
        ("LothricKnight", 35, 32), ("HollowAssassin", 32, 38),
        ("HollowSoldier", 28, 36),                                    # Crossbow hollow
        ("StarvedHound", 30, 30), ("StarvedHound", 38, 36),         # DS3: dogs in corridors
        ("HollowSoldier", 40, 40), ("HollowAssassin", 44, 44),      # Hollow ambushes in corridor
        # Corridor -> barracks transition
        ("LothricKnight", 55, 38), ("WingedKnight", 50, 38),
        ("DarkMage", 48, 42),                                         # Priest healer
        ("LothricKnight", 58, 44), ("LothricKnight", 62, 34),       # Knight pair guards stairs
        # Dragon barracks — Wyvern area (Pus of Man on dragon corpses)
        ("HollowSoldier", 68, 18), ("PusOfMan", 78, 18),
        ("HollowSoldier", 75, 22), ("CrystalLizard", 82, 22),
        ("HollowSoldier", 85, 28), ("PusOfMan", 95, 32),             # Second Pus of Man
        ("HollowSoldier", 70, 25), ("HollowSoldier", 92, 28),       # More hollows in barracks
        ("LothricKnight", 88, 34),                                    # Knight patrolling barracks
        # Boreal Outrider Knight (DS3: in a room with chests, frost damage)
        ("BorealOutriderKnight", 45, 55),                             # DS3: frost knight in side room
        ("StarvedHound", 48, 60),                                     # DS3: dog in side path
        # Inner stairs — Winged Knight gauntlet
        ("WingedKnight", 108, 48), ("CrystalLizard", 115, 45),
        ("LothricKnight", 112, 52),                                   # Knight on stairs
        ("LothricKnight", 100, 42),                                   # Red-eyed Lothric Knight
        ("HollowAssassin", 105, 54), ("HollowAssassin", 118, 50),   # Assassin ambush on stairs
        # Arena approaches
        ("PusOfMan", 125, 55), ("LothricKnight", 132, 58),
        ("HollowSoldier", 128, 62), ("HollowAssassin", 135, 65),      # Hollow gauntlet to boss
        ("WingedKnight", 140, 60),                                    # Ascended Winged Knight near arena
        ("HollowSoldier", 138, 68), ("HollowSoldier", 142, 72),     # Hollows at arena entrance
    ]
    for kind, tx, ty in enemy_positions:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items - DS3 Lothric Castle (wiki-verified) ---
    items = [
        # Souls
        ("SoulOrb", "Soul of a Crestfallen Knight", 25, 25, 600),      # Altar room
        ("SoulOrb", "Soul of a Crestfallen Knight", 128, 62, 600),     # After wyvern dead
        ("SoulOrb", "Soul of a Weary Warrior", 55, 36, 1000),          # Right of stairs
        ("SoulOrb", "Soul of a Weary Warrior", 90, 35, 2000),          # Lever room
        ("SoulOrb", "Large Soul of a Nameless Soldier", 75, 18, 1500), # Hanging corpse
        ("SoulOrb", "Large Soul of a Nameless Soldier", 98, 28, 1500), # Tower top
        ("SoulOrb", "Large Soul of a Nameless Soldier", 105, 40, 1500),# Over ledge
        ("SoulOrb", "Large Soul of a Weary Warrior", 88, 30, 2000),    # Lever room
        # Lightning Urn x7
        ("Consumable", "Lightning Urn", 72, 15, 0),
        ("Consumable", "Lightning Urn", 78, 12, 0),
        ("Consumable", "Lightning Urn", 74, 18, 0),
        ("Consumable", "Lightning Urn", 76, 14, 0),
        ("Consumable", "Lightning Urn", 80, 16, 0),
        ("Consumable", "Lightning Urn", 82, 18, 0),
        ("Consumable", "Lightning Urn", 84, 15, 0),
        # Other consumables
        ("Consumable", "Sniper Bolt", 88, 25, 11),                     # Near sniper crossbow (11x)
        ("Consumable", "Pale Pine Resin", 115, 55, 0),                 # Mimic room
        ("Consumable", "Black Firebomb", 125, 62, 0),                  # Lower ladder room
        ("Consumable", "Black Firebomb", 126, 63, 0),                  # Same pickup (3x total)
        ("Consumable", "Black Firebomb", 124, 64, 0),                  # Same pickup (3x total)
        ("Consumable", "Sunlight Medal", 138, 68, 0),                  # Corpse outside church
        ("Consumable", "Rusted Coin", 125, 70, 0),                     # Church room
        ("Consumable", "Rusted Coin", 128, 72, 0),                     # Church room
        ("UndeadBoneShard", "Undead Bone Shard", 70, 20, 0),                # Under wyvern bridge
        # Embers x5
        ("Ember", "Ember", 68, 22, 0),                                 # Dragon barracks
        ("Ember", "Ember", 62, 30, 0),                                 # Wyvern bridge
        ("Ember", "Ember", 130, 65, 0),                                # Corner corpse
        ("Ember", "Ember", 82, 20, 0),                                 # Wyvern area
        ("Ember", "Ember", 135, 58, 0),                                # Post-wyvern
        # Weapons
        ("WeaponDrop", "Greatlance", 62, 28, 0),                       # Red-eye knight guards
        ("WeaponDrop", "Sniper Crossbow", 85, 28, 0),                  # Tower top near WK
        ("WeaponDrop", "Irithyll Rapier", 45, 55, 0),                  # Boreal Knight area
        ("WeaponDrop", "Caitha's Chime", 128, 75, 0),                  # Church roof
        ("WeaponDrop", "Sacred Bloom Shield", 52, 42, 0),              # Illusory wall
        # Armor
        ("ArmorDrop", "Winged Knight Set", 55, 42, 0),                 # Illusory wall
        # Upgrade materials — Large Titanite Shard x2
        ("TitaniteShard", "Large Titanite Shard", 75, 16, 0),
        ("TitaniteShard", "Large Titanite Shard", 95, 30, 0),
        # Titanite Chunk x10
        ("TitaniteShard", "Titanite Chunk", 42, 40, 0),
        ("TitaniteShard", "Titanite Chunk", 92, 30, 0),
        ("TitaniteShard", "Titanite Chunk", 72, 25, 0),
        ("TitaniteShard", "Titanite Chunk", 115, 48, 0),
        ("TitaniteShard", "Titanite Chunk", 135, 60, 0),
        ("TitaniteShard", "Titanite Chunk", 65, 20, 0),
        ("TitaniteShard", "Titanite Chunk", 125, 55, 0),
        ("TitaniteShard", "Titanite Chunk", 132, 42, 0),
        ("TitaniteShard", "Titanite Chunk", 140, 60, 0),
        ("TitaniteShard", "Titanite Chunk", 50, 44, 0),
        # Twinkling Titanite (ground pickups)
        ("TitaniteShard", "Twinkling Titanite", 52, 38, 0),            # Winged Knight room corpse
        ("TitaniteShard", "Twinkling Titanite", 118, 55, 0),           # Wyvern bridge far side
        # Titanite Scale (ground pickup)
        ("TitaniteShard", "Titanite Scale", 116, 50, 0),               # Outside mimic room corpse
        ("TitaniteShard", "Titanite Scale", 130, 68, 0),               # Shortcut path
        ("TitaniteShard", "Titanite Scale", 142, 62, 0),               # Shortcut path near Archives
        # Titanite Slab (DS3: elevator shortcut going down from Prince fight)
        ("TitaniteShard", "Titanite Slab", 148, 68, 0),                # Near Grand Archives exit
        # Rings & key items
        ("RingDrop", "Red Tearstone Ring", 132, 75, 0),                # Church jump
        ("RingDrop", "Knight's Ring", 108, 48, 0),                     # Ladder room
        ("Consumable", "Braille Divine Tome of Lothric", 102, 32, 0),  # Up stairs from mimic
        # Gems
        ("Consumable", "Raw Gem", 82, 35, 0),                          # Side room
        ("Consumable", "Refined Gem", 76, 22, 0),                      # After wyvern kill
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests - DS3 Lothric Castle (wiki-verified, 9 chests: 7 regular + 2 mimics) ---
    # Prayer Set (regular, early room)
    entities.append(make_entity("Chest", 38 * 16, 35 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Prayer Set"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Twinkling Titanite (regular, Boreal Knight room)
    entities.append(make_entity("Chest", 45 * 16, 58 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Twinkling Titanite"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Spirit Tree Crest Shield (regular, Boreal Knight room)
    entities.append(make_entity("Chest", 47 * 16, 56 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Spirit Tree Crest Shield"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Titanite Scale (regular, Boreal Knight room)
    entities.append(make_entity("Chest", 48 * 16, 54 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Twinkling Titanite (regular, hidden behind boxes, Boreal room)
    entities.append(make_entity("Chest", 50 * 16, 52 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Twinkling Titanite"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Titanite Scale (MIMIC, wyvern fire room)
    entities.append(make_entity("Chest", 115 * 16, 52 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", True),
    ]))
    # Titanite Scale (regular, church room)
    entities.append(make_entity("Chest", 125 * 16, 72 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Titanite Scale (regular, Sunlight Altar room)
    entities.append(make_entity("Chest", 120 * 16, 58 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Sunlight Straight Sword (MIMIC, near wyvern dead area)
    entities.append(make_entity("Chest", 100 * 16, 34 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Sunlight Straight Sword"),
        make_field("is_mimic", "Bool", True),
    ]))

    # --- NPCs - DS3 Lothric Castle ---
    # Emma, High Priestess of Lothric — in the cathedral/church area
    # DS3: gives Basin of Vows and Way of Blue covenant
    entities.append(make_entity("Npc", 122 * 16, 62 * 16, [
        make_field("name", "String", "Emma"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#D4AF37"),
        make_field("dialogue", "String",
            "I am Emma|High Priestess of Lothric|The Prince has refused his duty|Please save him"),
    ]))
    # Eygon of Carim — summon sign near Dragonslayer Armour arena approach
    # DS3: can be summoned for Dragonslayer Armour if Irina quest is in correct state
    entities.append(make_entity("Npc", 115 * 16, 56 * 16, [
        make_field("name", "String", "Eygon of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A4A4A"),
        make_field("dialogue", "String",
            "What do you want?|I am Eygon of Carim|I am bound by duty to protect Irina"),
    ]))

    # --- Fog Gates ---
    # Back to AnorLondo (west entry)
    entities.append(make_entity("FogGate", 6 * 16, 30 * 16, [
        make_field("dest_area", "String", "AnorLondo"),
        make_field("dest_x", "Float", 160.0),
        make_field("dest_y", "Float", 608.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Grand Archives (NE exit)
    entities.append(make_entity("FogGate", 156 * 16, 62 * 16, [
        make_field("dest_area", "String", "GrandArchives"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 2300.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Consumed King's Garden (south side path)
    entities.append(make_entity("FogGate", 42 * 16, 66 * 16, [
        make_field("dest_area", "String", "ConsumedKingsGarden"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Castle gate — warm torchlight
    entities.append(make_entity("Light", 10 * 16, 30 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.35)]))
    # Dragon barracks — fire glow
    entities.append(make_entity("Light", 80 * 16, 25 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.4)]))
    # Dragonslayer Armour arena — lightning blue
    entities.append(make_entity("Light", 132 * 16, 68 * 16, [
        make_field("radius", "Float", 220.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.6),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.5)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)

    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  LothricCastle (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "LothricCastle", chunk, entities


def make_grand_archives():
    """Grand Archives — vertical library climb with Twin Princes boss.

    Faithful DS3 layout: the Grand Archives is a towering library ascent.
    Entry at the south from Lothric Castle, climbing through bookshelf mazes,
    a wax-pool hall, the scholar tower, winged knight corridors, gargoyle
    rooftops, and finally the Twin Princes chamber at the summit. Exit north
    to the Kiln of the First Flame.

    Vertical progression (y decreases = higher):
      1. Entry hall (south) — arrive from Lothric Castle
      2. First floor corridors — bookshelf maze
      3. Wax pool hall — slow wading through molten wax
      4. Scholar tower — crystal sage arena
      5. Winged Knight corridor — gauntlet to rooftop
      6. Gargoyle rooftop — open-air encounter
      7. Twin Princes chamber (north) — Lorian & Lothric boss fight
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # TERRAIN — carved from wall, south (high y) to north (low y)
    # ================================================================

    # 1. Entry hall (south, x=15-60, y=125-152)
    fill_tiles(chunk, TILE_GROUND, 15, 125, 60, 152)
    # Bookshelf walls
    fill_tiles(chunk, TILE_WALL, 25, 130, 27, 138)
    fill_tiles(chunk, TILE_WALL, 48, 134, 50, 140)

    # 2. First floor corridors — bookshelf maze (x=40-98, y=85-128)
    fill_tiles(chunk, TILE_GROUND, 40, 85, 98, 128)
    carve_ellipse(chunk, 68, 105, 16, 12)
    # Bookshelf walls
    fill_tiles(chunk, TILE_WALL, 52, 90, 54, 96)
    fill_tiles(chunk, TILE_WALL, 78, 100, 80, 106)
    fill_tiles(chunk, TILE_WALL, 60, 112, 62, 118)

    # 3. Wax pool hall (x=30-85, y=55-88)
    fill_tiles(chunk, TILE_GROUND, 30, 55, 85, 88)
    # Wax pool — slows movement
    fill_tiles(chunk, TILE_POISON, 42, 62, 72, 80)
    # Walls around pool
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 65)
    fill_tiles(chunk, TILE_WALL, 68, 72, 70, 76)

    # 4. Scholar tower (x=65-108, y=30-58)
    fill_tiles(chunk, TILE_GROUND, 65, 30, 108, 58)
    carve_ellipse(chunk, 86, 44, 14, 10)
    # Tower walls
    fill_tiles(chunk, TILE_WALL, 74, 35, 76, 40)
    fill_tiles(chunk, TILE_WALL, 96, 42, 98, 47)

    # 5. Winged Knight corridor (x=50-100, y=18-35)
    fill_tiles(chunk, TILE_GROUND, 50, 18, 100, 35)
    # Corridor walls
    fill_tiles(chunk, TILE_WALL, 62, 22, 64, 26)
    fill_tiles(chunk, TILE_WALL, 85, 26, 87, 30)

    # 6. Gargoyle rooftop (x=58-108, y=5-22)
    fill_tiles(chunk, TILE_GROUND, 58, 5, 108, 22)
    # Rooftop walls
    fill_tiles(chunk, TILE_WALL, 70, 8, 72, 12)
    fill_tiles(chunk, TILE_WALL, 92, 14, 94, 18)

    # 7. Twin Princes chamber (x=80-140, y=5-35)
    fill_tiles(chunk, TILE_GROUND, 80, 5, 140, 35)
    carve_ellipse(chunk, 110, 18, 22, 14)

    # 8. Lift shortcut alcove — Lothric Castle shortcut off the Bridge of Glory
    fill_tiles(chunk, TILE_GROUND, 128, 28, 148, 38)
    # Hidden lift platform alcove (Titanite Slab from lift trick)
    fill_tiles(chunk, TILE_GROUND, 132, 36, 142, 46)

    # ================================================================
    # CONNECTIONS — vertical staircases between levels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 38, 120, 48, 130)    # Entry hall → First floor
    fill_tiles(chunk, TILE_GROUND, 55, 82, 65, 88)      # First floor → Wax pool
    fill_tiles(chunk, TILE_GROUND, 72, 52, 82, 58)      # Wax pool → Scholar tower
    fill_tiles(chunk, TILE_GROUND, 85, 30, 95, 35)      # Scholar tower → WK corridor
    fill_tiles(chunk, TILE_GROUND, 75, 15, 85, 22)      # WK corridor → Rooftop
    fill_tiles(chunk, TILE_GROUND, 98, 10, 105, 18)     # Rooftop → Princes chamber
    fill_tiles(chunk, TILE_GROUND, 128, 22, 135, 30)    # Bridge → Lift shortcut alcove

    # ================================================================
    # PLAYER SPAWN & BONFIRES
    # ================================================================
    spawn_px, spawn_py = 25 * 16, 142 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    entities.append(make_entity("Bonfire", 25 * 16, 142 * 16))     # Entry bonfire
    entities.append(make_entity("Bonfire", 110 * 16, 18 * 16))     # Twin Princes bonfire

    # ================================================================
    # BOSS SPAWN — Twin Princes (Lorian & Lothric)
    # ================================================================
    entities.append(make_entity("BossSpawn", 110 * 16, 12 * 16))

    # ================================================================
    # ENEMIES — DS3 Grand Archives (wiki-complete)
    # ================================================================
    enemy_data = [
        # Grand Archives Scholars (DarkMage — candle-wielding wax priests)
        # Wiki walkthrough: wax priests at altar, next room, stairs, upper level (~8 total)
        ("DarkMage", 45, 130), ("DarkMage", 62, 95),
        ("DarkMage", 85, 40), ("DarkMage", 75, 28),
        ("DarkMage", 50, 100), ("DarkMage", 55, 75),
        ("DarkMage", 48, 85), ("DarkMage", 72, 55),
        # Crystal Sage (teleports around area, first encounter in entry hall)
        ("CrystalSage", 48, 128),
        # Hollow Slaves (Thrall — drop from ceilings, walls)
        ("HollowSlave", 42, 132), ("HollowSlave", 55, 98),
        ("HollowSlave", 68, 108), ("HollowSlave", 75, 50),
        ("HollowSlave", 62, 65),
        # Hollow Soldiers — generic hollows in library
        ("HollowSoldier", 40, 138), ("HollowSoldier", 52, 92),
        ("HollowSoldier", 58, 80),
        # Lothric Knights — including red-eyed knight guard
        ("LothricKnight", 70, 92), ("LothricKnight", 88, 45),
        ("LothricKnight", 55, 65), ("LothricKnight", 78, 48),
        # Ascended Winged Knights (golden, 3 on tower rooftop — drop Titanite Slab)
        ("AscendedWingedKnight", 82, 38), ("AscendedWingedKnight", 92, 35),
        ("AscendedWingedKnight", 75, 32),
        # Boreal Outrider Knight — behind illusory wall (drops Outrider Armor Set)
        ("BorealOutriderKnight", 58, 68),
        # Clawed Curse (Basilisk — curse hands from walls/books)
        ("ClawedCurse", 48, 70), ("ClawedCurse", 65, 78),
        ("ClawedCurse", 55, 82),
        # Man-grubs — caster on beam below cage
        ("ManGrub", 90, 25), ("ManGrub", 95, 30),
        # Gargoyles — rooftop guardians (wiki: 3 gargoyles on roof)
        ("Gargoyle", 68, 12), ("Gargoyle", 82, 15), ("Gargoyle", 95, 10),
        # Corvians — bird people near storyteller on rooftops
        ("Corvian", 78, 18), ("Corvian", 85, 12),
        # Corvian Storyteller — leading corvian flock
        ("CorvianStoryteller", 72, 15),
        # Crystal Lizards (wiki walkthrough: ~6 throughout — entry room, 2 in secret room, 1 mid-level, 2 on roof)
        ("CrystalLizard", 52, 85), ("CrystalLizard", 48, 72),
        ("CrystalLizard", 50, 75), ("CrystalLizard", 65, 55),
        ("CrystalLizard", 78, 15), ("CrystalLizard", 88, 22),
        # Black Hand NPC trio — hostile NPCs in courtyard with statue
        # Faraam armor warrior (drops Golden Wing Crest Shield)
        ("MiniBoss", 60, 110),
        # Mage Kriemhild (drops Sage's Crystal Staff)
        ("DarkMage", 62, 112),
        # Dual katana wielder (drops Onikiri and Ubadachi)
        ("MiniBoss", 64, 108),
        # Bridge of Glory — barricade gauntlet (wiki: "series of blockades with many hollows, then knights")
        ("HollowSoldier", 112, 8), ("HollowSoldier", 114, 10),
        ("HollowSoldier", 119, 15), ("HollowSoldier", 121, 18),
        ("HollowSoldier", 125, 7), ("HollowSoldier", 127, 12),
        ("LothricKnight", 130, 10), ("LothricKnight", 132, 15),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # ================================================================
    # ITEMS — DS3 Grand Archives (wiki-complete)
    # ================================================================
    items = [
        # Spells
        ("Consumable", "Power Within", 55, 80, 0),
        ("Consumable", "Soul Stream", 60, 70, 0),
        ("Consumable", "Divine Pillars of Light", 88, 32, 0),
        # Consumables — souls
        ("SoulOrb", "Soul of a Crestfallen Knight", 32, 138, 600),
        ("SoulOrb", "Soul of a Crestfallen Knight", 78, 35, 600),
        ("SoulOrb", "Soul of a Nameless Soldier", 52, 78, 1000),
        ("SoulOrb", "Soul of a Weary Warrior", 72, 15, 1000),
        ("SoulOrb", "Large Soul of a Crestfallen Knight", 82, 30, 1500),
        # Consumables
        ("HomewardBone", "Homeward Bone", 60, 108, 0),
        ("HomewardBone", "Homeward Bone", 65, 88, 0),
        ("HomewardBone", "Homeward Bone", 72, 92, 0),
        ("Ember", "Ember", 55, 98, 0),
        # Weapons
        ("WeaponDrop", "Avelyn", 68, 85, 0),
        ("WeaponDrop", "Golden Wing Crest Shield", 80, 32, 0),
        ("WeaponDrop", "Sage's Crystal Staff", 82, 28, 0),
        ("WeaponDrop", "Onikiri and Ubadachi", 84, 30, 0),
        ("WeaponDrop", "Crystal Chime", 70, 60, 0),
        # Scrolls
        ("Consumable", "Crystal Scroll", 48, 125, 0),
        # Armor
        ("ArmorDrop", "Outrider Knight Armor Set", 58, 68, 0),
        # Upgrade materials — Titanite Chunks (8x)
        ("TitaniteShard", "Titanite Chunk", 42, 90, 0),
        ("TitaniteShard", "Titanite Chunk", 55, 95, 0),
        ("TitaniteShard", "Titanite Chunk", 65, 60, 0),
        ("TitaniteShard", "Titanite Chunk", 75, 42, 0),
        ("TitaniteShard", "Titanite Chunk", 88, 18, 0),
        ("TitaniteShard", "Titanite Chunk", 95, 22, 0),
        ("TitaniteShard", "Titanite Chunk", 70, 125, 0),
        ("TitaniteShard", "Titanite Chunk", 62, 75, 0),
        # Titanite Scales (5x ground pickups)
        ("TitaniteShard", "Titanite Scale", 58, 95, 0),
        ("TitaniteShard", "Titanite Scale", 52, 72, 0),
        ("TitaniteShard", "Titanite Scale", 68, 68, 0),
        ("TitaniteShard", "Titanite Scale", 75, 55, 0),
        ("TitaniteShard", "Titanite Scale", 65, 50, 0),
        # Titanite Slabs (3x — elevator secret + Winged Knights trio + lift trick)
        ("TitaniteShard", "Titanite Slab", 108, 15, 0),
        ("TitaniteShard", "Titanite Slab", 95, 35, 0),
        # Titanite Slab from lift trick (activate lift, roll off, ride second platform down)
        ("TitaniteShard", "Titanite Slab", 137, 42, 0),
        # Greirat's Ashes (adjacent rooftop — only obtainable by jumping)
        ("Consumable", "Greirat's Ashes", 92, 8, 0),
        # Third Soul of a Crestfallen Knight (near Winged Knights / rooftops)
        ("SoulOrb", "Soul of a Crestfallen Knight", 85, 8, 600),
        # Other upgrade materials
        ("Consumable", "Shriving Stone", 82, 45, 0),
        ("Consumable", "Hollow Gem", 100, 15, 0),
        ("Consumable", "Blessed Gem", 90, 30, 0),
        ("UndeadBoneShard", "Undead Bone Shard", 55, 100, 0),
        ("EstusShard", "Estus Shard", 82, 20, 0),
        # Rings
        ("RingDrop", "Fleshbite Ring", 90, 22, 0),
        ("RingDrop", "Hunter's Ring", 88, 18, 0),
        ("RingDrop", "Scholar Ring", 68, 72, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # ================================================================
    # CHESTS — DS3 Grand Archives (5 chests, 0 mimics)
    # ================================================================
    # Witch's Locks (secret room, lever-activated)
    entities.append(make_entity("Chest", 50 * 16, 75 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("loot_name", "String", "Witch's Locks"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Titanite Scale x3 (upper level room)
    entities.append(make_entity("Chest", 78 * 16, 38 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Titanite Slab (near giant wax pool)
    entities.append(make_entity("Chest", 60 * 16, 82 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_name", "String", "Titanite Slab"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Divine Blessing (beam, lower level)
    entities.append(make_entity("Chest", 92 * 16, 28 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("loot_name", "String", "Divine Blessing"),
        make_field("is_mimic", "Bool", False),
    ]))
    # Twinkling Titanite x3 (beam, lower level)
    entities.append(make_entity("Chest", 95 * 16, 25 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_name", "String", "Twinkling Titanite"),
        make_field("is_mimic", "Bool", False),
    ]))

    # ================================================================
    # NPC — DS3 Grand Archives
    # ================================================================
    # Black Hand Gotthard (dead body at entrance — drops Grand Archives Key)
    entities.append(make_entity("Npc", 30 * 16, 140 * 16, [
        make_field("name", "String", "Black Hand Gotthard"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#606060"),
        make_field("dialogue", "String",
            "A corpse with the Grand Archives Key|"
            "Gotthard's journey ends here"),
    ]))
    # Siegward of Catarina — summon sign at bonfire (wiki: helps clear path to Twin Princes)
    entities.append(make_entity("Npc", 28 * 16, 140 * 16, [
        make_field("name", "String", "Siegward of Catarina"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C8A832"),
        make_field("dialogue", "String",
            "I shall assist you|On this final journey|To the Twin Princes"),
    ]))

    # ================================================================
    # FOG GATES — area transitions
    # ================================================================
    # South: back to Lothric Castle
    entities.append(make_entity("FogGate", 25 * 16, 152 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 3200.0), make_field("dest_y", "Float", 1500.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # North: to Kiln of the First Flame
    entities.append(make_entity("FogGate", 110 * 16, 5 * 16, [
        make_field("dest_area", "String", "KilnOfTheFirstFlame"),
        make_field("dest_x", "Float", 1280.0), make_field("dest_y", "Float", 2320.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # Lift shortcut to Lothric Castle (from bridge area near Twin Princes)
    entities.append(make_entity("FogGate", 138 * 16, 32 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 3500.0), make_field("dest_y", "Float", 800.0),
        make_field("width", "Float", 48.0), make_field("height", "Float", 80.0),
    ]))

    # ================================================================
    # LIGHTS — candlelight, wax glow, golden sunlight
    # ================================================================
    # Entry hall — warm candlelight
    entities.append(make_entity("Light", 25 * 16, 142 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.7), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    # Wax pool hall — orange molten-wax glow
    entities.append(make_entity("Light", 57 * 16, 72 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.5), make_field("b", "Float", 0.1), make_field("intensity", "Float", 0.35)]))
    # Scholar tower — cool candlelight
    entities.append(make_entity("Light", 86 * 16, 44 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.4), make_field("g", "Float", 0.5), make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.35)]))
    # Twin Princes chamber — golden sunlight from above
    entities.append(make_entity("Light", 110 * 16, 12 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.95), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.5)]))

    # ================================================================
    # ADDITIONAL INTERNAL STRUCTURES — bookshelf maze, desks, pillars
    # ================================================================
    # Entry hall — bookshelf walls
    fill_tiles(chunk, TILE_WALL, 20, 135, 22, 138)
    fill_tiles(chunk, TILE_WALL, 30, 138, 32, 142)
    fill_tiles(chunk, TILE_WALL, 25, 128, 27, 130)
    fill_tiles(chunk, TILE_WALL, 38, 130, 40, 132)
    # Wax pool hall — wax pillars and bookshelves
    fill_tiles(chunk, TILE_WALL, 45, 65, 47, 68)
    fill_tiles(chunk, TILE_WALL, 55, 70, 57, 72)
    fill_tiles(chunk, TILE_WALL, 62, 78, 64, 80)
    fill_tiles(chunk, TILE_WALL, 50, 80, 52, 82)
    fill_tiles(chunk, TILE_WALL, 40, 72, 42, 74)
    fill_tiles(chunk, TILE_WALL, 68, 68, 70, 70)
    # Scholar tower — desk and shelf clusters
    fill_tiles(chunk, TILE_WALL, 78, 35, 80, 38)
    fill_tiles(chunk, TILE_WALL, 85, 40, 87, 42)
    fill_tiles(chunk, TILE_WALL, 92, 36, 94, 38)
    fill_tiles(chunk, TILE_WALL, 80, 48, 82, 50)
    fill_tiles(chunk, TILE_WALL, 90, 50, 92, 52)
    fill_tiles(chunk, TILE_WALL, 98, 42, 100, 44)
    # Winged Knight corridors — suit of armor displays
    fill_tiles(chunk, TILE_WALL, 38, 55, 40, 58)
    fill_tiles(chunk, TILE_WALL, 50, 52, 52, 55)
    fill_tiles(chunk, TILE_WALL, 60, 55, 62, 58)
    fill_tiles(chunk, TILE_WALL, 42, 45, 44, 48)
    # Gargoyle rooftops — chimney and roof structures
    fill_tiles(chunk, TILE_WALL, 65, 18, 67, 22)
    fill_tiles(chunk, TILE_WALL, 75, 22, 77, 26)
    fill_tiles(chunk, TILE_WALL, 85, 18, 87, 22)
    fill_tiles(chunk, TILE_WALL, 95, 20, 97, 24)
    fill_tiles(chunk, TILE_WALL, 70, 28, 72, 30)
    fill_tiles(chunk, TILE_WALL, 80, 30, 82, 32)
    # Twin Princes chamber — throne room pillars
    fill_tiles(chunk, TILE_WALL, 100, 8, 102, 10)
    fill_tiles(chunk, TILE_WALL, 115, 10, 117, 12)
    fill_tiles(chunk, TILE_WALL, 125, 8, 127, 10)
    fill_tiles(chunk, TILE_WALL, 105, 20, 107, 22)
    fill_tiles(chunk, TILE_WALL, 118, 22, 120, 24)
    # Bridge of Glory — barricade walls (zigzag gauntlet before Twin Princes)
    # Wiki: "series of blockades with many hollows behind them, then knights"
    fill_tiles(chunk, TILE_WALL, 110, 5, 112, 11)     # Barricade 1 (north gap)
    fill_tiles(chunk, TILE_WALL, 116, 13, 118, 20)    # Barricade 2 (south gap)
    fill_tiles(chunk, TILE_WALL, 122, 5, 124, 12)     # Barricade 3 (north gap)
    # Lift shortcut alcove walls
    fill_tiles(chunk, TILE_WALL, 130, 30, 132, 34)
    fill_tiles(chunk, TILE_WALL, 144, 30, 146, 36)

    # ================================================================
    # FINALIZE — connectivity check
    # ================================================================
    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  GrandArchives (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "GrandArchives", chunk, entities


def make_kiln_of_the_first_flame():
    """Kiln of the First Flame - ash wasteland with Soul of Cinder boss.
    Faithful DS3 layout: ash entry path (south) -> collapsed fire hall (middle)
    -> First Flame arena (north). Very sparse, no regular enemies.
    The end of all things.
    """
    chunk = new_chunk()
    entities = []

    # === Ash entry path (south) ===
    fill_tiles(chunk, TILE_GROUND, 68, 128, 92, 155)

    # === Collapsed fire hall (middle) ===
    fill_tiles(chunk, TILE_GROUND, 45, 55, 115, 128)
    carve_ellipse(chunk, 80, 90, 22, 18)
    # Iron remnants — twisted girders from the ruined kiln
    fill_tiles(chunk, TILE_WALL, 58, 78, 60, 85)
    fill_tiles(chunk, TILE_WALL, 98, 92, 100, 98)
    fill_tiles(chunk, TILE_WALL, 72, 100, 74, 105)

    # === First Flame arena (north) ===
    fill_tiles(chunk, TILE_GROUND, 50, 8, 110, 58)
    carve_ellipse(chunk, 80, 32, 28, 22)

    # --- Player spawn ---
    spawn_px, spawn_py = 80 * 16, 148 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 80 * 16, 148 * 16))   # Flameless Shrine
    entities.append(make_entity("Bonfire", 80 * 16, 30 * 16))    # Kiln boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 80 * 16, 25 * 16))  # Soul of Cinder

    # --- No regular enemies ---

    # --- Items ---
    # DS3 Kiln has no item pickups — only the Soul of Cinder boss fight and endings
    items = []
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Fog Gate back to Grand Archives (south) ---
    entities.append(make_entity("FogGate", 80 * 16, 155 * 16, [
        make_field("dest_area", "String", "GrandArchives"),
        make_field("dest_x", "Float", 300.0),
        make_field("dest_y", "Float", 3800.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Dim firelight at entry — dying embers
    entities.append(make_entity("Light", 80 * 16, 148 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.5)]))
    # Brilliant golden at arena — the First Flame
    entities.append(make_entity("Light", 80 * 16, 25 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.8)]))
    # Dim hall remnants
    entities.append(make_entity("Light", 80 * 16, 90 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.3)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  KilnOfTheFirstFlame (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "KilnOfTheFirstFlame", chunk, entities


def make_consumed_kings_garden():
    """Consumed King's Garden - descending crystal garden with Oceiros boss.
    Faithful DS3 layout: entry (NW) -> crystal courtyard -> poison swamp ->
    serpent corridor -> Oceiros throne room (SE). Crystal growths throughout.
    """
    chunk = new_chunk()
    entities = []

    # === Garden entry (NW) ===
    fill_tiles(chunk, TILE_GROUND, 8, 8, 38, 32)
    # Vines — overgrown garden walls
    fill_tiles(chunk, TILE_WALL, 15, 14, 17, 18)
    fill_tiles(chunk, TILE_WALL, 28, 20, 30, 24)

    # === Crystal courtyard ===
    fill_tiles(chunk, TILE_GROUND, 28, 28, 72, 58)
    carve_ellipse(chunk, 50, 42, 14, 10)
    # Crystal growth walls
    fill_tiles(chunk, TILE_WALL, 38, 34, 40, 38)
    fill_tiles(chunk, TILE_WALL, 58, 45, 60, 49)
    fill_tiles(chunk, TILE_WALL, 48, 50, 50, 53)

    # === Poison swamp (center-south) ===
    fill_tiles(chunk, TILE_POISON, 35, 62, 72, 88)
    # Safe paths through the swamp
    fill_tiles(chunk, TILE_GROUND, 40, 65, 68, 85)

    # === Serpent corridor ===
    fill_tiles(chunk, TILE_GROUND, 68, 48, 105, 72)
    # Lift mid-way ledge (wiki: roll off lift halfway to reach exterior ledge → Dragonscale Ring)
    fill_tiles(chunk, TILE_GROUND, 108, 55, 122, 64)
    # Corridor walls
    fill_tiles(chunk, TILE_WALL, 78, 52, 80, 56)
    fill_tiles(chunk, TILE_WALL, 92, 60, 94, 64)

    # === Oceiros throne room (SE) ===
    fill_tiles(chunk, TILE_GROUND, 95, 70, 145, 115)
    carve_ellipse(chunk, 120, 92, 22, 18)
    # Crystal walls in throne room
    fill_tiles(chunk, TILE_WALL, 102, 78, 104, 82)
    fill_tiles(chunk, TILE_WALL, 132, 95, 134, 100)
    fill_tiles(chunk, TILE_WALL, 115, 100, 117, 106)

    # === Connections ===
    # Entry -> Courtyard
    fill_tiles(chunk, TILE_GROUND, 28, 28, 35, 32)
    # Courtyard -> Poison
    fill_tiles(chunk, TILE_GROUND, 42, 56, 50, 65)
    # Courtyard -> Corridor
    fill_tiles(chunk, TILE_GROUND, 65, 48, 72, 55)
    # Corridor -> Arena
    fill_tiles(chunk, TILE_GROUND, 100, 65, 108, 75)
    # Lift mid-way ledge connection (serpent corridor → ledge → arena approach)
    fill_tiles(chunk, TILE_GROUND, 105, 55, 112, 64)

    # === ADDITIONAL INTERNAL STRUCTURES — crystal garden ===
    # Entry — overgrown stone pillars
    fill_tiles(chunk, TILE_WALL, 12, 10, 14, 12)
    fill_tiles(chunk, TILE_WALL, 25, 15, 27, 17)
    fill_tiles(chunk, TILE_WALL, 18, 24, 20, 26)
    # Crystal courtyard — crystal growth clusters
    fill_tiles(chunk, TILE_WALL, 32, 32, 34, 35)
    fill_tiles(chunk, TILE_WALL, 42, 38, 44, 40)
    fill_tiles(chunk, TILE_WALL, 55, 35, 57, 37)
    fill_tiles(chunk, TILE_WALL, 65, 42, 67, 44)
    fill_tiles(chunk, TILE_WALL, 38, 48, 40, 50)
    fill_tiles(chunk, TILE_WALL, 60, 52, 62, 54)
    # Poison swamp — dead tree stumps
    fill_tiles(chunk, TILE_WALL, 45, 68, 47, 70)
    fill_tiles(chunk, TILE_WALL, 58, 75, 60, 77)
    fill_tiles(chunk, TILE_WALL, 50, 82, 52, 84)
    fill_tiles(chunk, TILE_WALL, 62, 80, 64, 82)
    # Serpent corridor — serpent statues
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 55)
    fill_tiles(chunk, TILE_WALL, 82, 58, 84, 60)
    fill_tiles(chunk, TILE_WALL, 95, 65, 97, 68)
    fill_tiles(chunk, TILE_WALL, 88, 70, 90, 72)
    # Throne room — crystal pillars and throne debris
    fill_tiles(chunk, TILE_WALL, 100, 75, 102, 78)
    fill_tiles(chunk, TILE_WALL, 112, 82, 114, 84)
    fill_tiles(chunk, TILE_WALL, 125, 78, 127, 80)
    fill_tiles(chunk, TILE_WALL, 138, 88, 140, 90)
    fill_tiles(chunk, TILE_WALL, 108, 92, 110, 95)
    fill_tiles(chunk, TILE_WALL, 130, 100, 132, 102)
    fill_tiles(chunk, TILE_WALL, 140, 108, 142, 110)

    # --- Player spawn ---
    spawn_px, spawn_py = 15 * 16, 15 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    # DS3: only 1 bonfire — Oceiros the Consumed King (after defeating boss)
    entities.append(make_entity("Bonfire", 120 * 16, 95 * 16))   # Oceiros boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 120 * 16, 88 * 16))  # Oceiros

    # --- Enemies — DS3 Consumed King's Garden: Cathedral Knights, Serpent Men,
    # Hollow Slaves (Thrall), Pus of Man (x3), Rotten Slugs, Lothric Priests
    enemy_data = [
        # Consumed King's Knights (Cathedral Knight type) — heavy armor guards
        ("ConsumedKingKnight", 32, 30), ("ConsumedKingKnight", 55, 40), ("ConsumedKingKnight", 112, 82),
        ("ConsumedKingKnight", 98, 68),
        # Serpent Men guard the path to Oceiros (correct — they serve Oceiros)
        ("SerpentMan", 42, 38), ("SerpentMan", 80, 55), ("SerpentMan", 128, 90),
        ("SerpentMan", 72, 48), ("SerpentMan", 95, 72),
        # Hollow Slaves (Thrall) — ambush throughout the garden (DS3: Hollow Slaves not Soldiers)
        ("Thrall", 35, 35), ("Thrall", 88, 62),
        ("Thrall", 22, 22), ("Thrall", 60, 32),
        # Hollow Slaves (Thrall) — ambush in upper rooms
        ("Thrall", 90, 58), ("Thrall", 100, 64), ("Thrall", 108, 70),
        ("Thrall", 118, 78),
        # Pus of Man — x3 in toxic swamp area (DS3 accurate count)
        ("PusOfMan", 52, 42), ("PusOfMan", 48, 76), ("PusOfMan", 58, 84),
        # Rotten Slugs in poison swamp (Rat type for small creature)
        # DS3 walkthrough: "several slugs" throughout toxic mist area
        ("Rat", 45, 70), ("Rat", 50, 75), ("Rat", 55, 78),
        ("Rat", 42, 78), ("Rat", 60, 82), ("Rat", 52, 84),
        ("Rat", 48, 72), ("Rat", 56, 68), ("Rat", 44, 82),
        # Lothric Priests (DarkMage type)
        ("DarkMage", 30, 28), ("DarkMage", 65, 44),
        # Crystal Lizard
        ("CrystalLizard", 68, 42),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items — DS3 Consumed King's Garden (complete per wiki) ---
    # Wiki items: Estus Shard, Titanite Chunk x3, Titanite Scale x3 (1 ground + 2 chests),
    # Dark Gem, Black Firebomb x2, Human Pine Resin, Claw weapon, Shadow Set,
    # Ring of Sacrifice, Dragonscale Ring, Path of the Dragon gesture
    items = [
        ("EstusShard", "Estus Shard", 50, 72, 0),
        # Dragonscale Ring — wiki: on exterior ledge accessed from lift mid-way roll-off
        ("RingDrop", "Dragonscale Ring", 115, 60, 0),
        # Path of the Dragon gesture — wiki: found in room AFTER defeating Oceiros, not in courtyard
        ("Consumable", "Path of the Dragon", 130, 100, 0),
        # Toxic swamp loot per walkthrough
        ("WeaponDrop", "Claw", 45, 74, 0),
        ("ArmorDrop", "Shadow Set", 52, 78, 0),
        ("Consumable", "Black Firebomb", 48, 76, 0),
        ("Consumable", "Black Firebomb", 56, 80, 0),
        ("Consumable", "Human Pine Resin", 50, 82, 0),
        ("RingDrop", "Ring of Sacrifice", 54, 70, 0),
        ("Consumable", "Dark Gem", 42, 68, 0),
        # Magic Stoneplate Ring (wiki: dropped by Cathedral Knight near courtyard)
        ("RingDrop", "Magic Stoneplate Ring", 52, 40, 0),
        # Tower area — from lift and staircase
        ("TitaniteShard", "Titanite Chunk", 40, 58, 0),
        ("TitaniteShard", "Titanite Chunk", 105, 72, 0),
        ("TitaniteShard", "Titanite Chunk", 92, 66, 0),
        # 4th Titanite Chunk (wiki comments: right side of courtyard near Hawkwood summon)
        ("TitaniteShard", "Titanite Chunk", 118, 85, 0),
        # Ground Titanite Scale (room before Oceiros)
        ("TitaniteShard", "Titanite Scale", 108, 75, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests — DS3 Consumed King's Garden ---
    # Post-Oceiros room chest with Titanite Scale
    entities.append(make_entity("Chest", 135 * 16, 95 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False)]))
    # Second chest behind illusory wall (Titanite Scale)
    entities.append(make_entity("Chest", 140 * 16, 100 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False)]))

    # --- NPCs ---
    # Hawkwood — summon sign before Oceiros (DS3: he can be summoned for Oceiros)
    entities.append(make_entity("Npc", 115 * 16, 82 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String",
            "I came to see Oceiros|The Consumed King|He holds the Path of the Dragon"),
    ]))

    # --- Fog Gates ---
    # Back to Lothric Castle (NW)
    entities.append(make_entity("FogGate", 8 * 16, 12 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 1000.0),
        make_field("dest_y", "Float", 900.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Untended Graves (E)
    entities.append(make_entity("FogGate", 142 * 16, 92 * 16, [
        make_field("dest_area", "String", "UntendedGraves"),
        make_field("dest_x", "Float", 300.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))
    # Shortcut to Lothric Castle (wiki: door in upper room, near Titanite Chunk corpse)
    entities.append(make_entity("FogGate", 95 * 16, 52 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 1200.0),
        make_field("dest_y", "Float", 800.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Entry — blue crystal glow
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.35)]))
    # Poison swamp — sickly green
    entities.append(make_entity("Light", 52 * 16, 75 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.3)]))
    # Oceiros arena — dark crystal
    entities.append(make_entity("Light", 120 * 16, 88 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.4)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  ConsumedKingsGarden (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "ConsumedKingsGarden", chunk, entities


def make_untended_graves():
    """Untended Graves - dark mirror of Cemetery of Ash with Champion Gundyr boss.
    Faithful DS3 layout: dark coffin entry (NW) -> dark cemetery path ->
    dark courtyard -> Black Knight cemetery -> Champion Gundyr arena ->
    Dark Firelink Shrine (SE). Extremely dim lighting throughout.
    """
    chunk = new_chunk()
    entities = []

    # === Dark coffin entry (NW) ===
    fill_tiles(chunk, TILE_GROUND, 8, 8, 35, 30)

    # === Dark cemetery path ===
    fill_tiles(chunk, TILE_GROUND, 25, 22, 75, 52)
    # Tombstone walls
    fill_tiles(chunk, TILE_WALL, 32, 28, 34, 31)
    fill_tiles(chunk, TILE_WALL, 48, 35, 50, 38)
    fill_tiles(chunk, TILE_WALL, 60, 40, 62, 43)
    fill_tiles(chunk, TILE_WALL, 40, 45, 42, 48)

    # === Dark courtyard ===
    fill_tiles(chunk, TILE_GROUND, 58, 40, 98, 68)
    carve_ellipse(chunk, 78, 54, 16, 10)
    # Courtyard walls
    fill_tiles(chunk, TILE_WALL, 68, 48, 70, 52)
    fill_tiles(chunk, TILE_WALL, 88, 55, 90, 59)

    # === Black Knight cemetery ===
    fill_tiles(chunk, TILE_GROUND, 38, 48, 75, 78)
    # Cemetery walls
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 58)
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 65)
    fill_tiles(chunk, TILE_WALL, 55, 70, 57, 73)

    # === Champion Gundyr arena ===
    fill_tiles(chunk, TILE_GROUND, 82, 65, 130, 100)
    carve_ellipse(chunk, 105, 82, 20, 15)
    # Arena edge ruins
    fill_tiles(chunk, TILE_WALL, 88, 70, 90, 73)
    fill_tiles(chunk, TILE_WALL, 118, 90, 120, 93)
    fill_tiles(chunk, TILE_WALL, 95, 95, 97, 98)

    # === ADDITIONAL TOMBSTONES (dense cemetery feel) ===
    # Dark cemetery path — many tombstones
    fill_tiles(chunk, TILE_WALL, 28, 25, 29, 27)
    fill_tiles(chunk, TILE_WALL, 35, 30, 36, 32)
    fill_tiles(chunk, TILE_WALL, 42, 28, 43, 30)
    fill_tiles(chunk, TILE_WALL, 55, 34, 56, 36)
    fill_tiles(chunk, TILE_WALL, 50, 42, 51, 44)
    fill_tiles(chunk, TILE_WALL, 65, 38, 66, 40)
    fill_tiles(chunk, TILE_WALL, 38, 38, 39, 40)
    # Dark courtyard — broken walls
    fill_tiles(chunk, TILE_WALL, 62, 44, 63, 46)
    fill_tiles(chunk, TILE_WALL, 75, 50, 76, 52)
    fill_tiles(chunk, TILE_WALL, 92, 58, 93, 60)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 64)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 62)
    # Black Knight cemetery — dense tombstones
    fill_tiles(chunk, TILE_WALL, 42, 52, 43, 54)
    fill_tiles(chunk, TILE_WALL, 50, 58, 51, 60)
    fill_tiles(chunk, TILE_WALL, 58, 55, 59, 57)
    fill_tiles(chunk, TILE_WALL, 65, 68, 66, 70)
    fill_tiles(chunk, TILE_WALL, 48, 65, 49, 67)
    fill_tiles(chunk, TILE_WALL, 70, 72, 71, 74)

    # === Dark Firelink Shrine (SE) ===
    fill_tiles(chunk, TILE_GROUND, 115, 95, 150, 130)
    carve_ellipse(chunk, 132, 112, 12, 10)
    # Shrine walls
    fill_tiles(chunk, TILE_WALL, 122, 100, 124, 105)
    fill_tiles(chunk, TILE_WALL, 140, 115, 142, 120)

    # === Connections ===
    # Entry -> Cemetery path (already adjacent)
    # Cemetery -> Courtyard
    fill_tiles(chunk, TILE_GROUND, 58, 42, 65, 48)
    # Courtyard -> Arena
    fill_tiles(chunk, TILE_GROUND, 82, 55, 90, 68)
    # Cemetery -> Knight cemetery
    fill_tiles(chunk, TILE_GROUND, 42, 48, 50, 55)
    # Arena -> Dark Firelink
    fill_tiles(chunk, TILE_GROUND, 115, 88, 122, 98)

    # --- Player spawn ---
    spawn_px, spawn_py = 15 * 16, 15 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))    # Entry
    entities.append(make_entity("Bonfire", 105 * 16, 82 * 16))   # Champion Gundyr

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 105 * 16, 78 * 16))  # Champion Gundyr

    # --- Enemies — DS3 Untended Graves: Black Knights, Pus of Man, Cathedral Grave Wardens,
    # Grave Wardens, Starved Hounds, Corvians, Corvian Storytellers, Ravenous Crystal Lizard.
    # Champion Gundyr is the boss. Daughter of Crystal Kriemhild invades (MiniBoss).
    enemy_data = [
        # Dark cemetery path — Black Knights patrol (DS3: 5 Black Knights total)
        ("BlackKnight", 45, 35), ("BlackKnight", 62, 45),
        ("BlackKnight", 75, 50), ("BlackKnight", 55, 60),
        ("BlackKnight", 88, 58),
        # Starved Hounds — undead dogs in the dark graveyard (DS3: multiple packs)
        ("StarvedHound", 30, 25), ("StarvedHound", 48, 42),
        ("StarvedHound", 60, 38), ("StarvedHound", 70, 52),
        ("StarvedHound", 42, 48),
        # Crystal Lizard near entry
        ("CrystalLizard", 40, 32),
        # Ravenous Crystal Lizard — larger variant near Dark Firelink (DS3: 2 Ravenous Crystal Lizards)
        ("CrystalLizard", 125, 105), ("CrystalLizard", 130, 110),
        # Pus of Man — dark infected enemies in cemetery area (DS3 has 2)
        ("PusOfMan", 35, 30), ("PusOfMan", 72, 56),
        # Cathedral Grave Wardens — dual-wielding grave wardens in the dark cemetery
        ("CathedralGraveWarden", 50, 38), ("CathedralGraveWarden", 65, 45),
        ("CathedralGraveWarden", 42, 55), ("CathedralGraveWarden", 80, 60),
        ("CathedralGraveWarden", 55, 68),
        # Corvians (Assassin type) — lurk in the dark cemetery corners
        ("Assassin", 38, 40), ("Assassin", 58, 52), ("Assassin", 45, 62),
        # Corvian Storyteller (DarkMage type) — perched near tombstones
        ("DarkMage", 48, 48), ("DarkMage", 70, 62),
        # Daughter of Crystal Kriemhild — invader near Dark Firelink area
        ("MiniBoss", 120, 98),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Untended Graves) ---
    # Hidden Blessing — behind dark Firelink, on a corpse
    entities.append(make_entity("Item", 135 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Hidden Blessing")]))
    # Eyes of a Fire Keeper — inside dark Firelink Shrine, on the floor near coiled sword
    entities.append(make_entity("Item", 130 * 16, 112 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Eyes of a Fire Keeper")]))
    # Coiled Sword Fragment — given by dark Fire Keeper in Dark Firelink
    entities.append(make_entity("Item", 128 * 16, 114 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Coiled Sword Fragment")]))
    # Ashen Estus Ring — in dark cemetery area, behind illusory wall
    entities.append(make_entity("Item", 40 * 16, 35 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Ashen Estus Ring")]))
    # Hornet Ring — dark Firelink tower ledge area
    entities.append(make_entity("Item", 145 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Hornet Ring")]))
    # Black Knight Glaive — dropped by Black Knight in cemetery
    entities.append(make_entity("Item", 62 * 16, 45 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Black Knight Glaive")]))
    # Black Knight Sword removed — not a ground pickup in Untended Graves (wiki)
    # Chaos Blade — in dark courtyard area
    entities.append(make_entity("Item", 78 * 16, 52 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Chaos Blade")]))
    # Blacksmith Hammer — near dark Firelink Shrine
    entities.append(make_entity("Item", 120 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Blacksmith Hammer")]))
    # Soul of a Crestfallen Knight x2 — one in cemetery, one near arena
    entities.append(make_entity("Item", 30 * 16, 28 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight"),
        make_field("value", "Int", 2000)]))
    entities.append(make_entity("Item", 95 * 16, 70 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight"),
        make_field("value", "Int", 2000)]))
    # Titanite Chunk x2 — in Black Knight cemetery and near Gundyr arena
    entities.append(make_entity("Item", 50 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 110 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Chunk")]))

    # --- NPCs ---
    # Dark Shrine Handmaid in Dark Firelink Shrine (different from normal Firelink)
    entities.append(make_entity("Npc", 132 * 16, 112 * 16, [
        make_field("name", "String", "Shrine Handmaid"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#606060"),
        make_field("dialogue", "String",
            "What is it?|The fire has long been out|I will tend to the ash"),
    ]))

    # --- Fog Gate ---
    # To Firelink Shrine (DS3: dark Firelink connects back to normal Firelink)
    entities.append(make_entity("FogGate", 148 * 16, 115 * 16, [
        make_field("dest_area", "String", "FirelinkShrine"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 1280.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights (extremely dim — this area is in total darkness) ---
    # Entry — barely visible
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [
        make_field("radius", "Float", 70.0),
        make_field("r", "Float", 0.25), make_field("g", "Float", 0.25),
        make_field("b", "Float", 0.25), make_field("intensity", "Float", 0.1)]))
    # Cemetery — faint glow
    entities.append(make_entity("Light", 50 * 16, 38 * 16, [
        make_field("radius", "Float", 80.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.25), make_field("intensity", "Float", 0.1)]))
    # Gundyr arena — slightly brighter
    entities.append(make_entity("Light", 105 * 16, 78 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.3),
        make_field("b", "Float", 0.25), make_field("intensity", "Float", 0.15)]))
    # Dark Firelink — minimal
    entities.append(make_entity("Light", 132 * 16, 112 * 16, [
        make_field("radius", "Float", 60.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.1)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  UntendedGraves (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "UntendedGraves", chunk, entities


def make_archdragon_peak():
    """Archdragon Peak - mountain peak with Nameless King boss.
    Faithful DS3 layout: mountain entry (NW) -> serpent barracks -> wyvern arena ->
    Dragon-Kin Mausoleum -> storm path -> Great Belfry -> Nameless King arena (SE).
    Lightning storms and dragon ruins throughout.
    """
    chunk = new_chunk()
    entities = []

    # === Mountain entry (NW) ===
    fill_tiles(chunk, TILE_GROUND, 6, 108, 35, 145)
    carve_ellipse(chunk, 20, 126, 12, 10)

    # === Serpent barracks ===
    fill_tiles(chunk, TILE_GROUND, 25, 85, 70, 120)
    carve_ellipse(chunk, 48, 102, 14, 10)
    # Barracks walls
    fill_tiles(chunk, TILE_WALL, 32, 90, 34, 95)
    fill_tiles(chunk, TILE_WALL, 58, 105, 60, 110)

    # === Wyvern arena (center) ===
    fill_tiles(chunk, TILE_GROUND, 30, 48, 80, 85)
    carve_ellipse(chunk, 55, 66, 18, 14)
    # Dragon ruin walls
    fill_tiles(chunk, TILE_WALL, 40, 55, 44, 60)
    fill_tiles(chunk, TILE_WALL, 65, 70, 68, 75)

    # === Dragon-Kin Mausoleum (center-right) ===
    fill_tiles(chunk, TILE_GROUND, 62, 38, 98, 62)
    carve_ellipse(chunk, 80, 50, 12, 8)

    # === Storm path (ascending ridge) ===
    fill_tiles(chunk, TILE_GROUND, 88, 28, 125, 55)
    # Ridge walls
    fill_tiles(chunk, TILE_WALL, 95, 32, 97, 36)
    fill_tiles(chunk, TILE_WALL, 112, 42, 114, 46)

    # === Great Belfry (upper) ===
    fill_tiles(chunk, TILE_GROUND, 105, 12, 140, 35)
    carve_ellipse(chunk, 122, 22, 14, 10)
    # Bell tower walls
    fill_tiles(chunk, TILE_WALL, 112, 16, 114, 20)
    fill_tiles(chunk, TILE_WALL, 130, 25, 132, 30)

    # === Nameless King arena (SE) ===
    fill_tiles(chunk, TILE_GROUND, 100, 62, 155, 118)
    carve_ellipse(chunk, 128, 90, 24, 22)
    # Storm walls
    fill_tiles(chunk, TILE_WALL, 108, 70, 110, 75)
    fill_tiles(chunk, TILE_WALL, 145, 95, 147, 100)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 108)

    # === Connections ===
    # Entry -> Barracks
    fill_tiles(chunk, TILE_GROUND, 25, 108, 35, 115)
    # Barracks -> Wyvern
    fill_tiles(chunk, TILE_GROUND, 38, 80, 48, 90)
    # Wyvern -> Mausoleum
    fill_tiles(chunk, TILE_GROUND, 62, 48, 72, 58)
    # Mausoleum -> Storm path
    fill_tiles(chunk, TILE_GROUND, 88, 38, 98, 48)
    # Storm path -> Belfry
    fill_tiles(chunk, TILE_GROUND, 115, 28, 125, 35)
    # Belfry -> Nameless arena
    fill_tiles(chunk, TILE_GROUND, 125, 35, 135, 62)

    # === ADDITIONAL INTERNAL STRUCTURES — dense DS3 mountain terrain ===
    # Serpent barracks — training dummies and serpent statues
    fill_tiles(chunk, TILE_WALL, 35, 92, 37, 95)
    fill_tiles(chunk, TILE_WALL, 42, 98, 44, 100)
    fill_tiles(chunk, TILE_WALL, 52, 108, 54, 110)
    fill_tiles(chunk, TILE_WALL, 60, 95, 62, 97)
    fill_tiles(chunk, TILE_WALL, 38, 105, 40, 107)
    fill_tiles(chunk, TILE_WALL, 48, 92, 50, 94)
    # Wyvern arena — dragon bone walls
    fill_tiles(chunk, TILE_WALL, 45, 52, 47, 55)
    fill_tiles(chunk, TILE_WALL, 58, 60, 60, 63)
    fill_tiles(chunk, TILE_WALL, 50, 72, 52, 75)
    fill_tiles(chunk, TILE_WALL, 68, 65, 70, 68)
    fill_tiles(chunk, TILE_WALL, 35, 68, 37, 70)
    fill_tiles(chunk, TILE_WALL, 72, 78, 74, 80)
    # Mausoleum — dragon altar walls
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 45)
    fill_tiles(chunk, TILE_WALL, 85, 48, 87, 50)
    fill_tiles(chunk, TILE_WALL, 78, 55, 80, 57)
    fill_tiles(chunk, TILE_WALL, 90, 40, 92, 42)
    # Storm path — cliff edges and wind-swept rocks
    fill_tiles(chunk, TILE_WALL, 95, 35, 97, 38)
    fill_tiles(chunk, TILE_WALL, 105, 40, 107, 42)
    fill_tiles(chunk, TILE_WALL, 118, 32, 120, 34)
    fill_tiles(chunk, TILE_WALL, 100, 48, 102, 50)
    fill_tiles(chunk, TILE_WALL, 112, 38, 114, 40)
    # Belfry — bell tower columns and arches
    fill_tiles(chunk, TILE_WALL, 108, 18, 110, 22)
    fill_tiles(chunk, TILE_WALL, 118, 20, 120, 24)
    fill_tiles(chunk, TILE_WALL, 128, 18, 130, 22)
    fill_tiles(chunk, TILE_WALL, 115, 28, 117, 30)
    fill_tiles(chunk, TILE_WALL, 135, 22, 137, 26)
    # Nameless arena — storm debris and lightning-scorched rocks
    fill_tiles(chunk, TILE_WALL, 112, 75, 114, 78)
    fill_tiles(chunk, TILE_WALL, 135, 82, 137, 85)
    fill_tiles(chunk, TILE_WALL, 120, 95, 122, 98)
    fill_tiles(chunk, TILE_WALL, 140, 90, 142, 93)
    fill_tiles(chunk, TILE_WALL, 115, 105, 117, 108)
    fill_tiles(chunk, TILE_WALL, 150, 100, 152, 103)

    # --- Player spawn ---
    spawn_px, spawn_py = 18 * 16, 132 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 18 * 16, 132 * 16))    # Entry: Archdragon Peak
    entities.append(make_entity("Bonfire", 80 * 16, 50 * 16))     # Dragonkin Mausoleum
    entities.append(make_entity("Bonfire", 122 * 16, 22 * 16))    # Great Belfry
    entities.append(make_entity("Bonfire", 128 * 16, 92 * 16))    # Nameless King

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 128 * 16, 85 * 16))  # Nameless King

    # --- Enemies (DS3 Archdragon Peak: dense Serpent-Men, Summoners, Drakeblood Knights,
    # Havel Knight, Rock Lizards, Wyvern) ---
    enemy_data = [
        # Serpent-Men — main enemy throughout the peak
        # DS3 walkthrough: 2 at entry, several fire-casters, 2 on overhang, many in buildings,
        # 3 big ones at end before altar — total ~23 Serpent-Men across the peak
        # Mountain entry — 2 guarding the path
        ("SerpentMan", 22, 115), ("SerpentMan", 28, 120),
        # Serpent barracks — fire-casting group and patrols
        ("SerpentMan", 38, 98), ("SerpentMan", 45, 108), ("SerpentMan", 42, 102),
        ("SerpentMan", 48, 95), ("SerpentMan", 55, 100),
        # Barracks overhang — 2 on top (wiki: "2 more Man-serpents on top of overhang")
        ("SerpentMan", 52, 88), ("SerpentMan", 58, 92),
        # Wyvern arena — dragon bone guards
        ("SerpentMan", 55, 75), ("SerpentMan", 62, 80), ("SerpentMan", 48, 68),
        ("SerpentMan", 65, 72), ("SerpentMan", 72, 78),
        # Dragon-Kin Mausoleum — interior guards
        ("SerpentMan", 68, 58), ("SerpentMan", 80, 48), ("SerpentMan", 75, 55),
        ("SerpentMan", 85, 50),
        # Mausoleum side room (wiki: "2 Man-serpents in room leading out")
        ("SerpentMan", 90, 45), ("SerpentMan", 92, 48),
        # Storm path — patrols along the ridge
        ("SerpentMan", 95, 35), ("SerpentMan", 100, 42), ("SerpentMan", 105, 38),
        # Great Belfry area — guarding the bell tower approach
        ("SerpentMan", 108, 28), ("SerpentMan", 118, 25), ("SerpentMan", 115, 30),
        # Path to altar — 3 big Serpent-Men (wiki: "three big ones" before altar)
        ("SerpentMan", 120, 75), ("SerpentMan", 135, 28), ("SerpentMan", 125, 82),
        # Altar approach — additional guards
        ("SerpentMan", 130, 35), ("SerpentMan", 132, 40),
        # Serpent-Man Summoners (DarkMage type — they cast spells and summon NPC phantoms)
        # DS3: Serpent-Man Sorcerers in upper rooms (Dragonkin Mausoleum + Belfry)
        ("DarkMage", 72, 52), ("DarkMage", 85, 42), ("DarkMage", 98, 45),
        # Rock Lizards — passive lizard enemies found throughout peak (DS3: ~6-8)
        ("RockLizard", 35, 110), ("RockLizard", 42, 95),
        ("RockLizard", 118, 20), ("RockLizard", 130, 25),
        ("RockLizard", 142, 85), ("RockLizard", 112, 72),
        ("RockLizard", 148, 95),
        # Regular Crystal Lizards — drop titanite
        ("CrystalLizard", 50, 72), ("CrystalLizard", 28, 118),
        # Drakeblood Knights (Knight type) — summoned by Serpent-Man Summoners
        # DS3: Drakeblood Knight + Ricard can be summoned by the sorcerers
        ("Knight", 110, 30), ("Knight", 142, 88),
        ("Knight", 78, 52),                                     # Additional summoned knight
        # Havel Knight — appears at Great Belfry area (DS3: tough NPC near fallen wyvern)
        ("Knight", 128, 70),
        # Ancient Wyvern — DS3: sleeps on bridge, must be sniped or dropped onto
        # Two wyverns in the dragon-path area; MiniBoss fits the "dragon" role
        ("MiniBoss", 55, 66),                                   # Ancient Wyvern (bridge)
        ("MiniBoss", 62, 76),                                   # Wyvern (path approach)
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items — DS3 Archdragon Peak (complete per wiki walkthrough) ---
    items = [
        # Mountain entry area
        ("SoulOrb", "Soul of a Weary Warrior", 22, 135, 2000),
        ("Consumable", "Lightning Gem", 35, 112, 0),                # Entry path
        ("HomewardBone", "Homeward Bone", 42, 118, 0),                # Path to barracks
        ("TitaniteShard", "Titanite Chunk", 55, 68, 0),             # Near bonfire
        ("Ember", "Ember", 28, 125, 0),                             # Near entry bonfire
        # Barracks area
        ("SoulOrb", "Soul of a Nameless Soldier", 50, 98, 1000),
        ("TitaniteShard", "Titanite Chunk", 52, 95, 0),             # Stairs landing
        ("WeaponDrop", "Ancient Dragon Greatshield", 62, 102, 0),   # Near overhang
        ("TitaniteShard", "Titanite Chunk", 45, 108, 0),            # Left stairs
        ("TitaniteShard", "Large Titanite Shard", 38, 115, 0),      # Hop down short stairs
        # Wyvern arena
        ("Ember", "Ember", 55, 62, 0),                              # Wyvern arena
        ("Ember", "Ember", 65, 78, 0),                              # Wyvern arena
        ("Consumable", "Stalk Dung Pie", 58, 70, 0),
        ("Consumable", "Stalk Dung Pie", 60, 72, 0),
        ("Consumable", "Stalk Dung Pie", 62, 74, 0),
        ("Consumable", "Stalk Dung Pie", 64, 68, 0),
        ("Consumable", "Stalk Dung Pie", 66, 70, 0),
        ("Consumable", "Stalk Dung Pie", 68, 72, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 70, 82, 2000),       # Wyvern arena
        ("RingDrop", "Ring of Steel Protection", 52, 60, 0),        # Right side steps
        ("Consumable", "Lightning Urn", 72, 78, 0),                 # Up stairs left
        ("TitaniteShard", "Titanite Chunk", 75, 55, 0),             # Building interior
        ("TitaniteShard", "Twinkling Titanite", 78, 48, 0),         # Ladder top
        ("TitaniteShard", "Twinkling Titanite", 80, 45, 0),         # Ladder top x2
        # Upper wyvern path — plank ledges
        ("TitaniteShard", "Titanite Chunk", 85, 40, 0),
        ("TitaniteShard", "Titanite Chunk", 88, 38, 0),
        ("Consumable", "Lightning Bolt", 90, 35, 0),                # 12x Lightning Bolt
        # Dragon-Kin Mausoleum
        ("Consumable", "Dragon Head Stone", 42, 100, 0),            # After Wyvern defeat
        ("TitaniteShard", "Titanite Scale", 75, 45, 0),             # Corpse over railing
        ("TitaniteShard", "Titanite Scale", 78, 42, 0),             # Left side
        ("TitaniteShard", "Titanite Scale", 82, 48, 0),             # Room leading out
        ("SoulOrb", "Soul of a Crestfallen Knight", 85, 50, 1500),  # Corner corpse
        ("Consumable", "Calamity Ring", 80, 52, 0),                  # Altar dragon gesture
        # Storm path / Great Belfry
        ("RingDrop", "Thunder Stoneplate Ring", 98, 32, 0),         # Ladder top
        ("Ember", "Ember", 118, 28, 0),                             # Ruins doorway
        ("SoulOrb", "Soul of a Weary Warrior", 130, 25, 2000),      # After wyvern area
        # Belfry area — Havel area
        ("Consumable", "Great Magic Barrier", 138, 82, 0),          # Drop down from Havel area
        ("TitaniteShard", "Titanite Slab", 132, 78, 0),             # Next to wyvern claw
        ("SoulOrb", "Large Soul of a Crestfallen Knight", 125, 85, 2500),
        # Path to altar
        ("Consumable", "Dragon Chaser's Ashes", 110, 40, 0),        # Behind Rock Lizard
        ("Consumable", "Twinkling Dragon Torso Stone", 120, 55, 0),  # Altar at top of stairs
        # Nameless King arena — post-boss
        ("TitaniteShard", "Titanite Slab", 128, 95, 0),             # After Nameless King
        ("ArmorDrop", "Dragonslayer Set", 125, 100, 0),             # After Nameless King
        # Weapons from drops/transposition
        ("WeaponDrop", "Dragonslayer Spear", 128, 92, 0),           # Gate before Nameless King
        ("WeaponDrop", "Dragon Tooth", 132, 80, 0),                 # Havel NPC drop
        ("WeaponDrop", "Havel's Greatshield", 135, 82, 0),          # Havel NPC drop
        ("RingDrop", "Lightning Clutch Ring", 50, 62, 0),           # Left of wyvern gate
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests — DS3 Archdragon Peak ---
    # Chest with Titanite Scale x3 (upper building after belfry)
    entities.append(make_entity("Chest", 108 * 16, 25 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Titanite Scale"),
        make_field("is_mimic", "Bool", False)]))
    # Chest with Twinkling Titanite x3 (near belfry bonfire)
    entities.append(make_entity("Chest", 118 * 16, 32 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Twinkling Titanite"),
        make_field("is_mimic", "Bool", False)]))

    # --- NPCs ---
    # Hawkwood — can be summoned for Nameless King (DS3: summon sign at Great Belfry)
    entities.append(make_entity("Npc", 122 * 16, 22 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String",
            "The Nameless King awaits|He is the firstborn of Gwyn|I must face him alone"),
    ]))

    # --- Fog Gate ---
    # Back to Irithyll Dungeon (NW)
    entities.append(make_entity("FogGate", 6 * 16, 120 * 16, [
        make_field("dest_area", "String", "IrithyllDungeon"),
        make_field("dest_x", "Float", 2160.0),
        make_field("dest_y", "Float", 128.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Mountain entry — golden sunlight
    entities.append(make_entity("Light", 18 * 16, 132 * 16, [
        make_field("radius", "Float", 150.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    # Barracks — orange torch glow
    entities.append(make_entity("Light", 48 * 16, 102 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.35)]))
    # Wyvern arena — pale daylight
    entities.append(make_entity("Light", 55 * 16, 66 * 16, [
        make_field("radius", "Float", 170.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.3)]))
    # Belfry — blue lightning
    entities.append(make_entity("Light", 122 * 16, 22 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.7),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.45)]))
    # Nameless King arena — storm blue/white
    entities.append(make_entity("Light", 128 * 16, 85 * 16, [
        make_field("radius", "Float", 220.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.75),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.5)]))

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(CHUNK_SIZE)
                       for x in range(CHUNK_SIZE)
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (CHUNK_SIZE * CHUNK_SIZE) * 100
    print(f"  ArchdragonPeak (faithful DS3 layout) "
          f"ground={pct:.1f}% connectivity={coverage}%")
    return "ArchdragonPeak", chunk, entities



# Map ID -> terrain override function (returns (map_id, chunk, entities))
TERRAIN_OVERRIDES = {
    "CemeteryOfAsh": make_cemetery_of_ash,
    "FirelinkShrine": make_firelink_shrine,
    "LothricWall": make_lothric_wall,
    "UndeadSettlement": make_undead_settlement,
    "RoadOfSacrifices": make_road_of_sacrifices,
    "FarronKeep": make_farron_keep,
    "CathedralDeep": make_cathedral_deep,
    "CatacombsOfCarthus": make_catacombs_of_carthus,
    "SmoulderingLake": make_smouldering_lake,
    "Irithyll": make_irithyll,
    "IrithyllDungeon": make_irithyll_dungeon,
    "ProfanedCapital": make_profaned_capital,
    "AnorLondo": make_anor_londo,
    "LothricCastle": make_lothric_castle,
    "GrandArchives": make_grand_archives,
    "KilnOfTheFirstFlame": make_kiln_of_the_first_flame,
    "ConsumedKingsGarden": make_consumed_kings_garden,
    "UntendedGraves": make_untended_graves,
    "ArchdragonPeak": make_archdragon_peak,
}


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
            "Trade": "Merchant", "Covenant": "Dialogue"}.get(kind, "Dialogue")


def map_chest_kind(loot):
    kind = loot.get("kind", "")
    if kind == "EstusShard": return "EstusShard"
    if "Weapon" in kind: return "WeaponDrop"
    if "Armor" in kind: return "ArmorDrop"
    if "Ring" in kind: return "RingDrop"
    if "Key" in kind: return "Consumable"
    if "Item" in kind: return "Consumable"
    return "SoulOrb"


# --- Main map generation ---

def generate_map_from_doc(doc_path):
    with open(doc_path, encoding="utf-8") as f:
        doc = json.load(f)

    map_id = map_id_from_doc(doc)
    if map_id not in LEVEL_UIDS:
        print(f"  SKIP {map_id} (not in LEVEL_UIDS)")
        return None

    chunk = generate_official_terrain(doc)
    entities = []

    def add_entity(identifier, x, y, fields=None):
        entity = make_entity(identifier, x, y, fields)
        snap_entity_to_walkable(chunk, entity)
        entities.append(entity)
        return entity

    bonfires = doc.get("bonfires", [])
    if bonfires:
        first = bonfires[0]
        add_entity("PlayerSpawn", first["x"], first["y"], [make_field("heal", "Bool", True)])
        for bonfire in bonfires:
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
        add_entity("BossSpawn", boss_def.get("x", 0), boss_def.get("y", 0))

    # Only include explicit entities if a map doc intentionally provides them.
    # Clean DS3 topology docs leave these empty until sourced encounter data is added.
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

    populate_entity_def_uids(entities)
    ground_count = sum(1 for row in chunk for tile in row if tile in (TILE_GROUND, TILE_POISON))
    total = max(1, chunk_width(chunk) * chunk_height(chunk))
    pct = ground_count / total * 100
    print(f"  {map_id:30s} sections={len(doc.get('map_layout', {}).get('sections', [])):2d} "
          f"entities={len(entities):4d} ground={pct:5.1f}%")
    return map_id, chunk, entities


def make_level(identifier, chunk, entities, uid):
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
             ("Rat", 0x7B6B55),
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


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(os.path.dirname(script_dir), "docs", "maps")
    levels_dir = os.path.join(script_dir, "ds2d")
    os.makedirs(levels_dir, exist_ok=True)

    level_summaries = []

    # First pass: generate maps with hand-authored terrain overrides (detailed enemies/items)
    for map_id, override_fn in sorted(TERRAIN_OVERRIDES.items()):
        result = override_fn()
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
