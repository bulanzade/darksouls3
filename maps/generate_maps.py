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
    # Shallow water in the chasm (DS3: water channel, not poisonous)
    fill_tiles(chunk, TILE_GROUND, 92, 108, 102, 110)
    fill_tiles(chunk, TILE_GROUND, 110, 108, 120, 110)
    fill_tiles(chunk, TILE_GROUND, 128, 106, 132, 110)
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
    # Reflecting pool at center (DS3: shallow water, not poisonous)
    fill_tiles(chunk, TILE_GROUND, 76, 44, 84, 52)
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
    # ADDITIONAL CEMETERY OF ASH DETAILS — DS3 fidelity
    # More gravestones, ash dunes, and architectural ruins
    # ================================================================
    # First path — additional gravestones (DS3: cemetery packed with graves)
    fill_tiles(chunk, TILE_WALL, 34, 151, 35, 152)
    fill_tiles(chunk, TILE_WALL, 42, 149, 43, 150)
    fill_tiles(chunk, TILE_WALL, 50, 152, 51, 153)
    # Side pocket — rubble near soul body
    fill_tiles(chunk, TILE_WALL, 60, 155, 61, 156)
    # NE curve — cliff-side gravestones
    fill_tiles(chunk, TILE_WALL, 68, 142, 69, 143)
    fill_tiles(chunk, TILE_WALL, 74, 144, 75, 145)
    # Ashen Estus clearing — broken fountain debris (DS3: ruined fountain area)
    fill_tiles(chunk, TILE_WALL, 72, 132, 73, 133)
    fill_tiles(chunk, TILE_WALL, 82, 136, 83, 137)
    fill_tiles(chunk, TILE_WALL, 76, 138, 77, 139)
    # Stairs junction — stone step walls
    fill_tiles(chunk, TILE_WALL, 88, 122, 89, 123)
    fill_tiles(chunk, TILE_WALL, 92, 128, 93, 129)
    # Broken arch — arch stones
    fill_tiles(chunk, TILE_WALL, 74, 118, 75, 119)
    fill_tiles(chunk, TILE_WALL, 80, 112, 81, 113)
    # Major fork area — gravestone clusters
    fill_tiles(chunk, TILE_WALL, 70, 104, 71, 105)
    fill_tiles(chunk, TILE_WALL, 78, 106, 79, 107)
    fill_tiles(chunk, TILE_WALL, 82, 102, 83, 103)
    fill_tiles(chunk, TILE_WALL, 68, 108, 69, 109)
    # Water chasm — more rocky outcrops (DS3: narrow channel with rocks)
    fill_tiles(chunk, TILE_WALL, 100, 107, 101, 108)
    fill_tiles(chunk, TILE_WALL, 112, 109, 113, 110)
    fill_tiles(chunk, TILE_WALL, 122, 107, 123, 108)
    fill_tiles(chunk, TILE_WALL, 130, 109, 131, 110)
    # Bonfire clearing — dead tree roots (DS3: dead tree beside bonfire)
    fill_tiles(chunk, TILE_WALL, 66, 92, 67, 93)
    fill_tiles(chunk, TILE_WALL, 78, 94, 79, 95)
    # Post-bonfire fork — tombstone rows (DS3: many graves near bonfire)
    fill_tiles(chunk, TILE_WALL, 60, 84, 61, 85)
    fill_tiles(chunk, TILE_WALL, 64, 86, 65, 87)
    fill_tiles(chunk, TILE_WALL, 72, 88, 73, 89)
    fill_tiles(chunk, TILE_WALL, 76, 84, 77, 85)
    # Firebomb cliff — cliff face stones
    fill_tiles(chunk, TILE_WALL, 36, 86, 37, 87)
    fill_tiles(chunk, TILE_WALL, 48, 82, 49, 83)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 89)
    # Gundyr approach — additional gravestones (DS3: dense cemetery before boss)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    fill_tiles(chunk, TILE_WALL, 74, 76, 75, 77)
    fill_tiles(chunk, TILE_WALL, 80, 66, 81, 67)
    # Gundyr arena — more perimeter ruins (DS3: crumbling arena edges)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 44)
    fill_tiles(chunk, TILE_WALL, 98, 42, 99, 44)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 62)
    fill_tiles(chunk, TILE_WALL, 94, 60, 95, 62)
    fill_tiles(chunk, TILE_WALL, 74, 34, 75, 36)
    fill_tiles(chunk, TILE_WALL, 86, 34, 87, 36)

    # ================================================================
    # ADDITIONAL CEMETERY OF ASH — DS3 tutorial area fine details
    # ================================================================
    # First path — more gravestone rows (DS3: densely packed cemetery)
    fill_tiles(chunk, TILE_WALL, 30, 150, 31, 151)
    fill_tiles(chunk, TILE_WALL, 38, 148, 39, 149)
    fill_tiles(chunk, TILE_WALL, 46, 151, 47, 152)
    fill_tiles(chunk, TILE_WALL, 36, 153, 37, 154)
    fill_tiles(chunk, TILE_WALL, 48, 149, 49, 150)
    # First encounter — additional grave markers (DS3: hollows rise from graves)
    fill_tiles(chunk, TILE_WALL, 56, 149, 57, 150)
    fill_tiles(chunk, TILE_WALL, 60, 151, 61, 152)
    fill_tiles(chunk, TILE_WALL, 66, 149, 67, 150)
    # Side pocket — stone debris (DS3: small side path with soul item)
    fill_tiles(chunk, TILE_WALL, 64, 156, 65, 157)
    fill_tiles(chunk, TILE_WALL, 58, 154, 59, 155)
    # NE curve — mountain path gravestones (DS3: path curves up through graves)
    fill_tiles(chunk, TILE_WALL, 66, 144, 67, 145)
    fill_tiles(chunk, TILE_WALL, 70, 138, 71, 139)
    fill_tiles(chunk, TILE_WALL, 76, 140, 77, 141)
    fill_tiles(chunk, TILE_WALL, 80, 132, 81, 133)
    # Ashen Estus clearing — more fountain debris (DS3: broken stone fountain)
    fill_tiles(chunk, TILE_WALL, 74, 130, 75, 131)
    fill_tiles(chunk, TILE_WALL, 84, 134, 85, 135)
    fill_tiles(chunk, TILE_WALL, 70, 136, 71, 137)
    # Stairs junction — stone step edges (DS3: tutorial stairs with messages)
    fill_tiles(chunk, TILE_WALL, 86, 120, 87, 121)
    fill_tiles(chunk, TILE_WALL, 90, 126, 91, 127)
    fill_tiles(chunk, TILE_WALL, 82, 130, 83, 131)
    # Broken arch — more arch stones (DS3: narrow stone arch passage)
    fill_tiles(chunk, TILE_WALL, 72, 116, 73, 117)
    fill_tiles(chunk, TILE_WALL, 82, 110, 83, 111)
    # Water chasm — additional rocky debris (DS3: narrow water channel)
    fill_tiles(chunk, TILE_WALL, 88, 106, 89, 107)
    fill_tiles(chunk, TILE_WALL, 104, 108, 105, 109)
    fill_tiles(chunk, TILE_WALL, 118, 108, 119, 109)
    fill_tiles(chunk, TILE_WALL, 126, 106, 127, 107)
    # Bonfire clearing — dead tree roots and ash piles (DS3: bonfire beside dead tree)
    fill_tiles(chunk, TILE_WALL, 64, 94, 65, 95)
    fill_tiles(chunk, TILE_WALL, 74, 96, 75, 97)
    fill_tiles(chunk, TILE_WALL, 80, 92, 81, 93)
    # Gundyr approach — torch sconce stones (DS3: twin torch archway)
    fill_tiles(chunk, TILE_WALL, 70, 66, 71, 67)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    fill_tiles(chunk, TILE_WALL, 74, 74, 75, 75)
    # Gundyr arena — more perimeter crumbling walls (DS3: open arena with ruin edges)
    fill_tiles(chunk, TILE_WALL, 60, 36, 61, 38)
    fill_tiles(chunk, TILE_WALL, 96, 36, 97, 38)
    fill_tiles(chunk, TILE_WALL, 66, 62, 67, 64)
    fill_tiles(chunk, TILE_WALL, 92, 62, 93, 64)
    fill_tiles(chunk, TILE_WALL, 82, 32, 83, 34)

    # ================================================================
    # SESSION 9 FIDELITY PASS — CemeteryOfAsh architectural details
    # ================================================================
    # Coffin alcove — stone slab edges (DS3: coffin in stone alcove, not open)
    fill_tiles(chunk, TILE_WALL, 21, 150, 22, 151)
    fill_tiles(chunk, TILE_WALL, 27, 154, 28, 155)
    # First path — collapsed stone fence posts (DS3: cemetery boundary walls)
    fill_tiles(chunk, TILE_WALL, 32, 149, 33, 150)
    fill_tiles(chunk, TILE_WALL, 40, 153, 41, 154)
    fill_tiles(chunk, TILE_WALL, 44, 149, 45, 150)
    # NE curve — eroded cliff stones (DS3: path carved into mountainside)
    fill_tiles(chunk, TILE_WALL, 66, 146, 67, 147)
    fill_tiles(chunk, TILE_WALL, 76, 140, 77, 141)
    fill_tiles(chunk, TILE_WALL, 70, 136, 71, 137)
    # Broken arch — keystone debris (DS3: crumbling stone arch over path)
    fill_tiles(chunk, TILE_WALL, 76, 116, 77, 117)
    fill_tiles(chunk, TILE_WALL, 78, 112, 79, 113)
    # Major fork — dead tree stump (DS3: dead trees throughout cemetery)
    fill_tiles(chunk, TILE_WALL, 84, 104, 85, 105)
    fill_tiles(chunk, TILE_WALL, 74, 110, 75, 111)
    # Crystal Lizard chasm — dripping stalactites (DS3: damp underground canal)
    fill_tiles(chunk, TILE_WALL, 90, 107, 91, 108)
    fill_tiles(chunk, TILE_WALL, 108, 107, 109, 108)
    fill_tiles(chunk, TILE_WALL, 114, 109, 115, 110)
    fill_tiles(chunk, TILE_WALL, 124, 107, 125, 108)
    fill_tiles(chunk, TILE_WALL, 134, 110, 135, 111)
    # Bonfire clearing — ash mound and ember remnants (DS3: ash-covered clearing)
    fill_tiles(chunk, TILE_WALL, 68, 90, 69, 91)
    fill_tiles(chunk, TILE_WALL, 76, 98, 77, 99)
    fill_tiles(chunk, TILE_WALL, 82, 90, 83, 91)
    # Post-bonfire fork — weathered headstones (DS3: dense gravestones near bonfire)
    fill_tiles(chunk, TILE_WALL, 58, 90, 59, 91)
    fill_tiles(chunk, TILE_WALL, 66, 86, 67, 87)
    fill_tiles(chunk, TILE_WALL, 78, 82, 79, 83)
    # Firebomb cliff — eroded cliff face alcoves (DS3: narrow cliff path with drops)
    fill_tiles(chunk, TILE_WALL, 38, 82, 39, 83)
    fill_tiles(chunk, TILE_WALL, 52, 86, 53, 87)
    # Gundyr approach — fallen tombstone rows (DS3: packed cemetery before arena)
    fill_tiles(chunk, TILE_WALL, 68, 72, 69, 73)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    # Gundyr arena — shattered stone pillars (DS3: large open arena with ruins)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 42)
    fill_tiles(chunk, TILE_WALL, 96, 40, 97, 42)
    fill_tiles(chunk, TILE_WALL, 70, 56, 71, 58)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 58)
    fill_tiles(chunk, TILE_WALL, 78, 30, 79, 32)
    fill_tiles(chunk, TILE_WALL, 84, 64, 85, 66)

    # ================================================================
    # 16. ARENA EXIT CORRIDOR (x=76-84, y=22-34)
    # Blocked by Gundyr door (wall tiles 77-83, 29-30)
    # Opens when boss is defeated (combat.rs)
    # Leads to FirelinkShrine (separate area)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 78, 22, 82, 34)

    # SESSION 10 FIDELITY PASS — Cemetery of Ash
    # Additional DS3-faithful terrain: ash mound debris, crumbled path edges,
    # dead tree stumps, Gundyr arena pillar bases, water pool border stones
    # Coffin area — ash mound debris (DS3: pile of ash where player wakes)
    fill_tiles(chunk, TILE_WALL, 22, 153, 23, 154)
    fill_tiles(chunk, TILE_WALL, 26, 155, 27, 156)
    fill_tiles(chunk, TILE_WALL, 20, 148, 21, 149)
    # Cemetery path — crumbled stone edge debris (DS3: broken stone path edges)
    fill_tiles(chunk, TILE_WALL, 30, 146, 31, 147)
    fill_tiles(chunk, TILE_WALL, 38, 145, 39, 146)
    fill_tiles(chunk, TILE_WALL, 44, 147, 45, 148)
    fill_tiles(chunk, TILE_WALL, 50, 145, 51, 146)
    # Ash estus clearing — dead tree stump (DS3: dead tree near broken fountain)
    fill_tiles(chunk, TILE_WALL, 74, 98, 75, 99)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    # Stairs junction — broken stone steps (DS3: crumbling stairs)
    fill_tiles(chunk, TILE_WALL, 70, 108, 71, 109)
    fill_tiles(chunk, TILE_WALL, 80, 106, 81, 107)
    fill_tiles(chunk, TILE_WALL, 76, 110, 77, 111)
    # Broken arch — collapsed arch stones (DS3: ruined stone arch over path)
    fill_tiles(chunk, TILE_WALL, 74, 120, 75, 121)
    fill_tiles(chunk, TILE_WALL, 86, 118, 87, 119)
    # Water chasm — pool border stones (DS3: small water pools in chasm area)
    fill_tiles(chunk, TILE_WALL, 95, 102, 96, 103)
    fill_tiles(chunk, TILE_WALL, 105, 106, 106, 107)
    fill_tiles(chunk, TILE_WALL, 115, 104, 116, 105)
    fill_tiles(chunk, TILE_WALL, 125, 106, 126, 107)
    fill_tiles(chunk, TILE_WALL, 132, 108, 133, 109)
    # Bonfire clearing — dead tree roots (DS3: dead tree with exposed roots)
    fill_tiles(chunk, TILE_WALL, 66, 88, 67, 89)
    fill_tiles(chunk, TILE_WALL, 78, 86, 79, 87)
    fill_tiles(chunk, TILE_WALL, 70, 82, 71, 83)
    # Firebomb cliff — cliff edge stones (DS3: eroded cliff with hollows above)
    fill_tiles(chunk, TILE_WALL, 36, 80, 37, 81)
    fill_tiles(chunk, TILE_WALL, 42, 84, 43, 85)
    fill_tiles(chunk, TILE_WALL, 50, 88, 51, 89)
    # Gundyr arena — pillar base fragments (DS3: arena has stone pillars)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 43)
    fill_tiles(chunk, TILE_WALL, 94, 42, 95, 43)
    fill_tiles(chunk, TILE_WALL, 60, 52, 61, 53)
    fill_tiles(chunk, TILE_WALL, 98, 52, 99, 53)
    fill_tiles(chunk, TILE_WALL, 70, 38, 71, 39)
    fill_tiles(chunk, TILE_WALL, 88, 38, 89, 39)
    # Gundyr approach — twin torch stone bases (DS3: two torches before arena)
    fill_tiles(chunk, TILE_WALL, 74, 62, 75, 63)
    fill_tiles(chunk, TILE_WALL, 84, 62, 85, 63)
    # Arena exit — crumbled doorway stones (DS3: door frame to Firelink)
    fill_tiles(chunk, TILE_WALL, 78, 24, 79, 25)
    fill_tiles(chunk, TILE_WALL, 82, 24, 83, 25)

    # ================================================================
    # SESSION 11 FIDELITY PASS — CemeteryOfAsh fine architectural details
    # ================================================================
    # Coffin alcove — ash pile debris and stone fragments (DS3: ash covers everything)
    fill_tiles(chunk, TILE_WALL, 23, 149, 24, 150)
    fill_tiles(chunk, TILE_WALL, 19, 153, 20, 154)
    fill_tiles(chunk, TILE_WALL, 28, 156, 29, 157)
    # First path — collapsed iron fence posts (DS3: rusted fence along cemetery edge)
    fill_tiles(chunk, TILE_WALL, 36, 147, 37, 148)
    fill_tiles(chunk, TILE_WALL, 52, 148, 53, 149)
    fill_tiles(chunk, TILE_WALL, 42, 154, 43, 155)
    # Side pocket — mossy stone slab (DS3: small side path with soul corpse)
    fill_tiles(chunk, TILE_WALL, 56, 156, 57, 157)
    fill_tiles(chunk, TILE_WALL, 62, 153, 63, 154)
    # NE curve — cliff face erosion debris (DS3: path carved into eroded cliff)
    fill_tiles(chunk, TILE_WALL, 72, 146, 73, 147)
    fill_tiles(chunk, TILE_WALL, 68, 134, 69, 135)
    fill_tiles(chunk, TILE_WALL, 82, 142, 83, 143)
    # Ashen Estus clearing — stone basin fragments (DS3: broken stone fountain basin)
    fill_tiles(chunk, TILE_WALL, 80, 138, 81, 139)
    fill_tiles(chunk, TILE_WALL, 74, 134, 75, 135)
    fill_tiles(chunk, TILE_WALL, 84, 132, 85, 133)
    # Stairs junction — crumbled step edges (DS3: tutorial messages on worn steps)
    fill_tiles(chunk, TILE_WALL, 88, 124, 89, 125)
    fill_tiles(chunk, TILE_WALL, 82, 128, 83, 129)
    fill_tiles(chunk, TILE_WALL, 94, 130, 95, 131)
    # Broken arch — fallen keystone rubble (DS3: stone arch partially collapsed)
    fill_tiles(chunk, TILE_WALL, 76, 114, 77, 115)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Major fork — dead tree root cluster (DS3: dead trees at path intersections)
    fill_tiles(chunk, TILE_WALL, 72, 106, 73, 107)
    fill_tiles(chunk, TILE_WALL, 80, 100, 81, 101)
    fill_tiles(chunk, TILE_WALL, 66, 102, 67, 103)
    # Water chasm — stalagmite formations (DS3: underground canal with rock formations)
    fill_tiles(chunk, TILE_WALL, 92, 104, 93, 105)
    fill_tiles(chunk, TILE_WALL, 102, 110, 103, 111)
    fill_tiles(chunk, TILE_WALL, 120, 106, 121, 107)
    fill_tiles(chunk, TILE_WALL, 128, 110, 129, 111)
    # Bonfire clearing — ember char marks (DS3: bonfire burns amid ash)
    fill_tiles(chunk, TILE_WALL, 62, 96, 63, 97)
    fill_tiles(chunk, TILE_WALL, 84, 94, 85, 95)
    # Post-bonfire fork — tilted cross stones (DS3: cemetery cross markers)
    fill_tiles(chunk, TILE_WALL, 62, 82, 63, 83)
    fill_tiles(chunk, TILE_WALL, 74, 84, 75, 85)
    fill_tiles(chunk, TILE_WALL, 56, 88, 57, 89)
    # Firebomb cliff — hollow nest debris (DS3: hollow camp on cliff path)
    fill_tiles(chunk, TILE_WALL, 34, 84, 35, 85)
    fill_tiles(chunk, TILE_WALL, 46, 84, 47, 85)
    fill_tiles(chunk, TILE_WALL, 40, 90, 41, 91)
    # Gundyr approach — cemetery iron gate posts (DS3: gate before arena)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 82, 72, 83, 73)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    # Gundyr arena — scattered coffin debris (DS3: coffins scattered in arena)
    fill_tiles(chunk, TILE_WALL, 68, 36, 69, 37)
    fill_tiles(chunk, TILE_WALL, 90, 36, 91, 37)
    fill_tiles(chunk, TILE_WALL, 64, 50, 65, 51)
    fill_tiles(chunk, TILE_WALL, 96, 50, 97, 51)
    fill_tiles(chunk, TILE_WALL, 74, 62, 75, 63)
    fill_tiles(chunk, TILE_WALL, 86, 60, 87, 61)
    # Arena exit — lintel stone debris (DS3: crumbling arch to Firelink)
    fill_tiles(chunk, TILE_WALL, 76, 26, 77, 27)
    fill_tiles(chunk, TILE_WALL, 84, 26, 85, 27)

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
    entities.append(make_entity("Enemy", 80 * 16, 48 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "MiniBoss")]))  # Iudex Gundyr

    # --- Enemies (DS3 Cemetery of Ash: Hollow Soldiers rise from graves, Starved Hounds) ---
    # In DS3 the cemetery enemies are Hollow Soldiers that rise from the ground.
    # DS3 enemies: Hollow Soldiers (sword, shield, crossbow variants) + Starved Hounds + 1 Ravenous Crystal Lizard.
    # Layout follows the actual route: coffin → cemetery path → fountain → stairs → bonfire →
    # firebomb cliff → Gundyr approach → arena.

    # Section 1: Coffin wake-up area — first Hollow Soldier (sword+shield, stands up)
    entities.append(make_entity("Enemy", 40 * 16, 152 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 2: Cemetery path — pair of Hollow Soldiers (sword+shield)
    entities.append(make_entity("Enemy", 56 * 16, 152 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    entities.append(make_entity("Enemy", 64 * 16, 150 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 3: Ashen Estus fountain — Hollow Soldier facing away (sword)
    entities.append(make_entity("Enemy", 80 * 16, 136 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 4: Stairs junction — Hollow Soldier (sword+shield) on stairs
    entities.append(make_entity("Enemy", 76 * 16, 126 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 5: Broken arch — Hollow Soldier crossbow (ranged)
    entities.append(make_entity("Enemy", 78 * 16, 116 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 6: Major fork — two Hollow Soldiers (sword+shield) guarding path
    entities.append(make_entity("Enemy", 86 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    entities.append(make_entity("Enemy", 92 * 16, 109 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 7: Cemetery of Ash bonfire clearing — Hollow Soldier near dead tree
    entities.append(make_entity("Enemy", 68 * 16, 92 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 8: Firebomb cliff — Hollow Soldier sword+shield + Starved Hound
    entities.append(make_entity("Enemy", 50 * 16, 86 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Starved Hound near firebomb cliff (DS3: dogs ambush on cliff path)
    entities.append(make_entity("Enemy", 44 * 16, 90 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "StarvedHound")]))
    # Hollow Soldier at cliff end
    entities.append(make_entity("Enemy", 38 * 16, 86 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    entities.append(make_entity("Enemy", 40 * 16, 84 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Section 9: Twin-torch approach — Hollow Soldier crossbow before arena
    entities.append(make_entity("Enemy", 76 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    # Starved Hound on cliff path approach (DS3: hound ambushes near arena)
    entities.append(make_entity("Enemy", 48 * 16, 80 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "StarvedHound")]))
    # Ravenous Crystal Lizard — side path near water chasm (optional area)
    entities.append(make_entity("Enemy", 136 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "RavenousCrystalLizard")]))

    # --- Items (accurate DS3 placements) ---
    # Ashen Estus Flask — corpse by broken fountain
    entities.append(make_entity("Item", 82 * 16, 134 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
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
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
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
    DS3 Faithful layout: stone shrine with central bonfire chamber,
    throne room (5 Lord of Cinder thrones), Andre's forge alcove,
    Tower (locked door, Fire Keeper Soul at top), exterior graveyard
    with Sword Master, Shrine Handmaiden at back corner.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # TERRAIN — DS3 Firelink Shrine interior and exterior
    # ================================================================

    # === 1. CENTRAL SHRINE CHAMBER — main circular room with bonfire ===
    # DS3: large circular stone chamber, bonfire at center
    carve_ellipse(chunk, 80, 80, 22, 20)
    # Shrine interior walls — stone pillars flanking the bonfire
    fill_tiles(chunk, TILE_WALL, 64, 68, 66, 76)
    fill_tiles(chunk, TILE_WALL, 94, 68, 96, 76)
    fill_tiles(chunk, TILE_WALL, 64, 84, 66, 92)
    fill_tiles(chunk, TILE_WALL, 94, 84, 96, 92)
    # Interior stone column near bonfire (DS3: central structural pillar)
    fill_tiles(chunk, TILE_WALL, 78, 76, 82, 80)

    # === 2. THRONE ROOM (north) — 5 Lord of Cinder thrones ===
    # DS3: semicircular alcove behind the bonfire with empty thrones
    fill_tiles(chunk, TILE_GROUND, 68, 54, 92, 66)
    carve_ellipse(chunk, 80, 58, 14, 6)
    # Throne alcove walls
    fill_tiles(chunk, TILE_WALL, 68, 54, 70, 58)
    fill_tiles(chunk, TILE_WALL, 90, 54, 92, 58)
    # Throne bases (DS3: 5 thrones arranged in a semicircle)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    fill_tiles(chunk, TILE_WALL, 76, 55, 78, 57)
    fill_tiles(chunk, TILE_WALL, 82, 55, 84, 57)
    fill_tiles(chunk, TILE_WALL, 86, 56, 88, 58)

    # === 3. ANDRE'S FORGE (west) — blacksmith alcove ===
    # DS3: Andre sits at his anvil in an alcove to the left of the entrance
    fill_tiles(chunk, TILE_GROUND, 42, 72, 62, 90)
    carve_ellipse(chunk, 44, 80, 8, 7)
    # Forge anvil block
    fill_tiles(chunk, TILE_WALL, 46, 78, 48, 82)
    # Forge walls creating a workshop feel
    fill_tiles(chunk, TILE_WALL, 42, 72, 44, 80)
    fill_tiles(chunk, TILE_WALL, 42, 84, 44, 90)

    # === 4. EAST WING — Hawkwood's resting area ===
    # DS3: Hawkwood sits on the floor near the right side of the shrine
    fill_tiles(chunk, TILE_GROUND, 98, 72, 118, 90)
    carve_ellipse(chunk, 120, 80, 7, 6)
    # Interior divider wall
    fill_tiles(chunk, TILE_WALL, 98, 72, 100, 80)
    fill_tiles(chunk, TILE_WALL, 98, 84, 100, 90)

    # === 5. SHRINE HANDMAIDEN ALCOVE (NW corner) ===
    # DS3: Handmaiden stands in the back-left corner of the shrine
    fill_tiles(chunk, TILE_GROUND, 62, 62, 72, 72)
    # Wall divider between handmaiden and throne room
    fill_tiles(chunk, TILE_WALL, 68, 64, 70, 68)

    # === 6. TOWER PATH (upper west) — locked tower with Fire Keeper Soul ===
    # DS3: Tower Key required to open, bridge leads across to tower
    fill_tiles(chunk, TILE_GROUND, 34, 56, 48, 72)
    carve_ellipse(chunk, 32, 60, 6, 5)
    # Tower bridge (DS3: narrow stone bridge to the tower)
    fill_tiles(chunk, TILE_GROUND, 42, 64, 48, 68)
    # Tower interior
    fill_tiles(chunk, TILE_GROUND, 26, 56, 36, 64)
    # Tower top — Fire Keeper Soul location (DS3: elevator to top)
    carve_ellipse(chunk, 28, 58, 4, 3)

    # === 7. TOWER PATH (upper east) — rafter area ===
    # DS3: Rafters accessible by dropping from tower bridge
    fill_tiles(chunk, TILE_GROUND, 112, 56, 128, 68)
    carve_ellipse(chunk, 124, 60, 7, 5)
    # Rafter supports
    fill_tiles(chunk, TILE_WALL, 116, 58, 118, 62)
    fill_tiles(chunk, TILE_WALL, 122, 58, 124, 62)

    # === 8. ENTRANCE HALL (south) — main shrine doorway ===
    # DS3: wide entrance arch leading into the shrine
    fill_tiles(chunk, TILE_GROUND, 72, 92, 88, 100)
    # Entrance pillars (DS3: stone pillars framing the door)
    fill_tiles(chunk, TILE_WALL, 72, 92, 74, 96)
    fill_tiles(chunk, TILE_WALL, 86, 92, 88, 96)

    # === 9. EXTERIOR GRAVEYARD (south) — tombstones leading to Cemetery of Ash ===
    # DS3: open graveyard with many tombstones, Sword Master patrols here
    fill_tiles(chunk, TILE_GROUND, 68, 100, 92, 118)
    # Graveyard expansion — wider area with tombstones
    fill_tiles(chunk, TILE_GROUND, 62, 108, 100, 126)
    carve_ellipse(chunk, 80, 112, 14, 8)
    # Tombstone walls (DS3: rows of gravestones)
    fill_tiles(chunk, TILE_WALL, 72, 104, 74, 106)
    fill_tiles(chunk, TILE_WALL, 78, 106, 80, 108)
    fill_tiles(chunk, TILE_WALL, 84, 104, 86, 106)
    fill_tiles(chunk, TILE_WALL, 76, 110, 78, 112)
    fill_tiles(chunk, TILE_WALL, 82, 110, 84, 112)
    # Gravestone rows in lower graveyard
    fill_tiles(chunk, TILE_WALL, 68, 116, 70, 118)
    fill_tiles(chunk, TILE_WALL, 74, 118, 76, 120)
    fill_tiles(chunk, TILE_WALL, 80, 116, 82, 118)
    fill_tiles(chunk, TILE_WALL, 86, 118, 88, 120)

    # === 10. ENTRANCE PATH (far south) — path from Cemetery of Ash ===
    fill_tiles(chunk, TILE_GROUND, 74, 126, 86, 142)
    # Walls framing the path
    fill_tiles(chunk, TILE_WALL, 70, 128, 74, 136)
    fill_tiles(chunk, TILE_WALL, 86, 128, 90, 136)

    # === 11. SWORD MASTER AREA (SW exterior) ===
    # DS3: Sword Master patrols the left side stairs outside the shrine
    fill_tiles(chunk, TILE_GROUND, 58, 128, 76, 142)
    # Stair wall divider
    fill_tiles(chunk, TILE_WALL, 62, 132, 64, 138)

    # === 12. RIGHT SIDE EXTERIOR (SE) ===
    # DS3: ember pickup area to the right of the shrine
    fill_tiles(chunk, TILE_GROUND, 86, 128, 104, 140)
    # Tree/rock obstacles
    fill_tiles(chunk, TILE_WALL, 92, 132, 94, 136)
    fill_tiles(chunk, TILE_WALL, 98, 130, 100, 134)

    # === 13. CONNECTION CORRIDORS ===
    # Central chamber to throne room
    fill_tiles(chunk, TILE_GROUND, 74, 64, 86, 70)
    # Central chamber to Andre's forge
    fill_tiles(chunk, TILE_GROUND, 60, 76, 70, 84)
    # Central chamber to east wing
    fill_tiles(chunk, TILE_GROUND, 90, 76, 100, 84)
    # Central chamber to entrance hall
    fill_tiles(chunk, TILE_GROUND, 76, 88, 84, 94)
    # Entrance hall to graveyard
    fill_tiles(chunk, TILE_GROUND, 76, 98, 84, 102)
    # Forge to tower path
    fill_tiles(chunk, TILE_GROUND, 48, 66, 56, 74)
    # East wing to rafter area
    fill_tiles(chunk, TILE_GROUND, 108, 66, 114, 74)
    # Handmaiden alcove connection
    fill_tiles(chunk, TILE_GROUND, 66, 68, 72, 74)
    # Forge to handmaiden path
    fill_tiles(chunk, TILE_GROUND, 56, 64, 64, 70)

    # ================================================================
    # SESSION 9 FIDELITY PASS — FirelinkShrine architectural details
    # ================================================================
    # Main hall — stone pillar bases (DS3: thick stone pillars support the roof)
    fill_tiles(chunk, TILE_WALL, 78, 90, 79, 91)
    fill_tiles(chunk, TILE_WALL, 84, 90, 85, 91)
    fill_tiles(chunk, TILE_WALL, 90, 90, 91, 91)
    fill_tiles(chunk, TILE_WALL, 78, 96, 79, 97)
    fill_tiles(chunk, TILE_WALL, 84, 96, 85, 97)
    fill_tiles(chunk, TILE_WALL, 90, 96, 91, 97)
    # Fireplace alcove — charred stone surround (DS3: bonfire in stone hearth)
    fill_tiles(chunk, TILE_WALL, 80, 84, 81, 85)
    fill_tiles(chunk, TILE_WALL, 88, 84, 89, 85)
    fill_tiles(chunk, TILE_WALL, 82, 82, 87, 83)
    # Throne room — coiled sword base stones (DS3: fire keeper throne area)
    fill_tiles(chunk, TILE_WALL, 76, 76, 77, 77)
    fill_tiles(chunk, TILE_WALL, 92, 76, 93, 77)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    fill_tiles(chunk, TILE_WALL, 86, 74, 87, 75)
    # Courtyard — crumbled wall debris (DS3: ruined walls around courtyard)
    fill_tiles(chunk, TILE_WALL, 68, 100, 69, 101)
    fill_tiles(chunk, TILE_WALL, 96, 100, 97, 101)
    fill_tiles(chunk, TILE_WALL, 72, 108, 73, 109)
    fill_tiles(chunk, TILE_WALL, 92, 108, 93, 109)
    # Andre's forge — anvil stones (DS3: Andre works at a stone forge)
    fill_tiles(chunk, TILE_WALL, 50, 70, 51, 71)
    fill_tiles(chunk, TILE_WALL, 54, 68, 55, 69)
    fill_tiles(chunk, TILE_WALL, 48, 74, 49, 75)
    # Handmaiden area — shelf stones (DS3: Handmaiden near stone shelves)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 70, 72, 71, 73)
    # Entry stairs — worn stone steps (DS3: worn stairs leading up to shrine)
    fill_tiles(chunk, TILE_WALL, 76, 114, 77, 115)
    fill_tiles(chunk, TILE_WALL, 84, 116, 85, 117)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Tree root cluster (DS3: massive tree roots visible inside Firelink)
    fill_tiles(chunk, TILE_WALL, 74, 86, 75, 87)
    fill_tiles(chunk, TILE_WALL, 94, 86, 95, 87)
    fill_tiles(chunk, TILE_WALL, 76, 80, 77, 81)
    fill_tiles(chunk, TILE_WALL, 92, 80, 93, 81)

    # ================================================================
    # ENTITIES
    # ================================================================

    # --- Player spawn at entrance from south ---
    spawn_px, spawn_py = 80 * 16, 118 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfire in center ---
    entities.append(make_entity("Bonfire", 80 * 16, 80 * 16))

    # --- Enemies (DS3 Firelink Shrine exterior) ---
    # Sword Master — down the left stairs from shrine, wields Uchigatana
    entities.append(make_entity("Enemy", 68 * 16, 136 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP["SwordMaster"])]))
    # Crystal Lizard — behind the tower (upper east roof drop-down)
    entities.append(make_entity("Enemy", 122 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "CrystalLizard")]))

    # Exterior graveyard — Hollow Soldiers rise from graves (DS3: 4 hollows in graveyard)
    entities.append(make_entity("Enemy", 68 * 16, 112 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    entities.append(make_entity("Enemy", 80 * 16, 116 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    entities.append(make_entity("Enemy", 92 * 16, 114 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))
    entities.append(make_entity("Enemy", 72 * 16, 124 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowSoldier")]))

    # --- NPCs (DS3 Firelink Shrine inhabitants) ---
    # Fire Keeper (level up) — stands near bonfire, south side
    entities.append(make_entity("Npc", 78 * 16, 86 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "LevelUp"),
        make_field("color", "Color", "#FFFFFF"),
        make_field("dialogue", "String", "Welcome to Firelink Shrine, Ashen One|May the flames guide thee|Touch the darkness within me, and take in the excess souls"),
    ]))

    # Ludleth of Courland (dialogue) — sits on throne behind bonfire
    entities.append(make_entity("Npc", 80 * 16, 58 * 16, [
        make_field("name", "String", "Ludleth of Courland"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#DAA520"),
        make_field("dialogue", "String", "Peace. I am Ludleth of Courland|A Lord, yes, but little more than a cinder|I will not shirk my sworn duty"),
    ]))

    # Blacksmith Andre — forge alcove, west wing
    entities.append(make_entity("Npc", 44 * 16, 82 * 16, [
        make_field("name", "String", "Andre of Astora"),
        make_field("kind", "LocalEnum.NpcKind", "Blacksmith"),
        make_field("color", "Color", "#C0C0C0"),
        make_field("dialogue", "String", "What do you need? Speak freely|I can reinforce your weapons|You must persist, Undead, we are one and the same"),
    ]))

    # Shrine Handmaiden (merchant) — back-left corner of shrine
    entities.append(make_entity("Npc", 66 * 16, 68 * 16, [
        make_field("name", "String", "Shrine Handmaiden"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7355"),
        make_field("dialogue", "String", "What is it? Buy something|Or be on your way|I shall tend the flame|And tend to thee"),
    ]))

    # Hawkwood (dialogue) — sitting on floor in east wing
    entities.append(make_entity("Npc", 106 * 16, 82 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String", "Oh, another Unkindled|The Legion of Farron is in the Keep below|They were Lords, once... but now they are Unkindled"),
    ]))

    # Yuria of Londor — appears after Yoel dies (DS3: stands near east entrance)
    entities.append(make_entity("Npc", 114 * 16, 76 * 16, [
        make_field("name", "String", "Yuria of Londor"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#2A1A3A"),
        make_field("dialogue", "String",
            "I am Yuria of Londor, a servant of the Lord of Hollows|Thou art the Lord of Hollows|The fire has bent to thy will|Let us embrace the age of hollows, together"),
    ]))

    # Ringfinger Leonhard — gives Cracked Red Eye Orb (DS3: near lower stairway)
    entities.append(make_entity("Npc", 92 * 16, 94 * 16, [
        make_field("name", "String", "Ringfinger Leonhard"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#8B0000"),
        make_field("dialogue", "String",
            "You have a good look|I am Leonhard, I have a proposition for you|Take this Cracked Red Eye Orb|Invade and pillage the souls of others"),
    ]))

    # Yoel of Londor — after recruitment (DS3: stands near lower shrine, eventually dies)
    entities.append(make_entity("Npc", 56 * 16, 88 * 16, [
        make_field("name", "String", "Yoel of Londor"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#3A3A4A"),
        make_field("dialogue", "String",
            "I am Yoel of Londor, a pilgrim as they call me|I can draw out your true strength|Let me level you up|Come back when you need more"),
    ]))

    # Greirat — after rescue from Lothric Wall (DS3: thief merchant near lower shrine)
    entities.append(make_entity("Npc", 52 * 16, 92 * 16, [
        make_field("name", "String", "Greirat"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#5A5A5A"),
        make_field("dialogue", "String",
            "I am Greirat of the Undead Settlement|You saved me from that cell, I owe you everything|I can steal items for you, if you like|Just leave it to old Greirat"),
    ]))

    # Cornyx — after rescue from Undead Settlement (DS3: pyromancy teacher, sits near bonfire)
    entities.append(make_entity("Npc", 74 * 16, 80 * 16, [
        make_field("name", "String", "Cornyx"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B6914"),
        make_field("dialogue", "String",
            "I am Cornyx, a pyromancer of the Great Swamp|You freed me from my cage, and for that I am grateful|Bring me pyromancy tomes, and I shall teach you their arts|The flame is a wondrous thing"),
    ]))

    # Orbeck of Vinheim — after recruitment (DS3: sorcery teacher, near upper shrine)
    entities.append(make_entity("Npc", 86 * 16, 74 * 16, [
        make_field("name", "String", "Orbeck of Vinheim"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#7090B0"),
        make_field("dialogue", "String",
            "I am Orbeck of Vinheim. A sorcerer, and an assassin|I shall teach you sorceries, as promised|Bring me scrolls, and I shall decipher them|But if you prove talentless, our arrangement ends"),
    ]))

    # Sirris of the Sunless Realms — after oath (DS3: swears knighthood near shrine)
    entities.append(make_entity("Npc", 98 * 16, 88 * 16, [
        make_field("name", "String", "Sirris of the Sunless Realms"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#A0B0C0"),
        make_field("dialogue", "String",
            "I am Sirris of the Sunless Realms|I have sworn an oath to serve you|I shall come to your aid whenever you need|Thank you, for accepting my knightly vows"),
    ]))

    # --- Items (DS3 Firelink Shrine) ---
    # Estus Shard — on rafters above shrine (upper west, illusory wall)
    entities.append(make_entity("Item", 34 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    # Covetous Silver Serpent Ring — chest behind illusory wall on rafters (upper east)
    entities.append(make_entity("Chest", 124 * 16, 60 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("loot_value", "Int", 0),
        make_field("loot_name", "String", "Covetous Silver Serpent Ring"),
        make_field("is_mimic", "Bool", False)]))
    # Estus Ring — drop down from tower bridge ledge
    entities.append(make_entity("Item", 30 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "RingDrop"),
        make_field("name", "String", "Estus Ring")]))
    # Fire Keeper Soul — top of tower
    entities.append(make_entity("Item", 28 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Fire Keeper Soul")]))
    # Broken Straight Sword — by graves straight ahead from entrance
    entities.append(make_entity("Item", 78 * 16, 108 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Broken Straight Sword")]))
    # Homeward Bone x5 — along path from CemeteryOfAsh (near graves)
    entities.append(make_entity("Item", 76 * 16, 114 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 82 * 16, 114 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 80 * 16, 120 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 76 * 16, 122 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 84 * 16, 122 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    # Ember x2 — near Sword Master area and right path from shrine
    entities.append(make_entity("Item", 92 * 16, 134 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 98 * 16, 136 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    # East-West Shield — corpse in tree near Sword Master area
    entities.append(make_entity("Item", 64 * 16, 138 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "East-West Shield"),
        make_field("slot", "String", "Hands")]))
    # Uchigatana — dropped by Sword Master
    entities.append(make_entity("Item", 68 * 16, 138 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Uchigatana")]))
    # Master's Attire — dropped by Sword Master
    entities.append(make_entity("Item", 66 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Master's Attire"),
        make_field("slot", "String", "Chest")]))
    # Master's Gloves — dropped by Sword Master
    entities.append(make_entity("Item", 70 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Master's Gloves"),
        make_field("slot", "String", "Hands")]))
    # Soul of a Deserted Corpse — tower area corpse
    entities.append(make_entity("Item", 38 * 16, 64 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse"),
        make_field("value", "Int", 200)]))
    # Twinkling Titanite — Crystal Lizard drop
    entities.append(make_entity("Item", 120 * 16, 64 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Twinkling Titanite")]))
    # Fire Keeper Set — drop from tower bridge
    entities.append(make_entity("Item", 118 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"),
        make_field("name", "String", "Fire Keeper Set"),
        make_field("slot", "String", "Chest")]))
    # Seed of a Giant Tree — from Giant Tree near shrine exterior
    entities.append(make_entity("Item", 88 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Seed of a Giant Tree")]))

    # --- Fog Gates ---
    # Back to CemeteryOfAsh (south)
    entities.append(make_entity("FogGate", 80 * 16, 140 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 580.0),
        make_field("dest_y", "Float", 320.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # To LothricWall (north exit through throne room)
    entities.append(make_entity("FogGate", 80 * 16, 52 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 200.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # --- Lights ---
    # Central bonfire — warm light filling the chamber
    entities.append(make_entity("Light", 80 * 16, 80 * 16, [
        make_field("radius", "Float", 240.0), make_field("r", "Float", 0.9),
        make_field("g", "Float", 0.7), make_field("b", "Float", 0.4),
        make_field("intensity", "Float", 0.6)]))
    # Andre's forge — orange glow from anvil
    entities.append(make_entity("Light", 44 * 16, 80 * 16, [
        make_field("radius", "Float", 120.0), make_field("r", "Float", 0.8),
        make_field("g", "Float", 0.5), make_field("b", "Float", 0.2),
        make_field("intensity", "Float", 0.4)]))
    # Throne room — dim golden light on the empty thrones
    entities.append(make_entity("Light", 80 * 16, 58 * 16, [
        make_field("radius", "Float", 100.0), make_field("r", "Float", 0.7),
        make_field("g", "Float", 0.6), make_field("b", "Float", 0.3),
        make_field("intensity", "Float", 0.3)]))
    # Exterior graveyard — moonlit
    entities.append(make_entity("Light", 80 * 16, 112 * 16, [
        make_field("radius", "Float", 160.0), make_field("r", "Float", 0.5),
        make_field("g", "Float", 0.5), make_field("b", "Float", 0.6),
        make_field("intensity", "Float", 0.25)]))

    # === MORE FIRELINK SHRINE DETAILS — DS3 fidelity ===
    # Central chamber — additional interior pillars (DS3: stone shrine with pillars)
    fill_tiles(chunk, TILE_WALL, 70, 74, 72, 78)
    fill_tiles(chunk, TILE_WALL, 88, 74, 90, 78)
    fill_tiles(chunk, TILE_WALL, 74, 86, 76, 90)
    fill_tiles(chunk, TILE_WALL, 84, 86, 86, 90)
    # Throne room — additional throne detail walls
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 63)
    fill_tiles(chunk, TILE_WALL, 88, 60, 90, 63)
    fill_tiles(chunk, TILE_WALL, 74, 62, 76, 64)
    fill_tiles(chunk, TILE_WALL, 84, 62, 86, 64)
    # Andre's forge — workshop debris (DS3: forge with anvil, debris)
    fill_tiles(chunk, TILE_WALL, 50, 76, 52, 78)
    fill_tiles(chunk, TILE_WALL, 48, 84, 50, 86)
    fill_tiles(chunk, TILE_WALL, 54, 80, 56, 82)
    # East wing — sitting area walls (DS3: Hawkwood rests here)
    fill_tiles(chunk, TILE_WALL, 102, 76, 104, 78)
    fill_tiles(chunk, TILE_WALL, 110, 82, 112, 84)
    fill_tiles(chunk, TILE_WALL, 104, 86, 106, 88)
    # Tower path — bridge railing stones (DS3: narrow bridge to locked tower)
    fill_tiles(chunk, TILE_WALL, 36, 58, 38, 60)
    fill_tiles(chunk, TILE_WALL, 44, 66, 46, 68)
    fill_tiles(chunk, TILE_WALL, 40, 70, 42, 72)
    # Rafter area — more rafter beams (DS3: wooden rafters above shrine)
    fill_tiles(chunk, TILE_WALL, 114, 62, 116, 64)
    fill_tiles(chunk, TILE_WALL, 120, 64, 122, 66)
    fill_tiles(chunk, TILE_WALL, 126, 60, 128, 62)
    # Entrance hall — arch stones (DS3: stone archway into shrine)
    fill_tiles(chunk, TILE_WALL, 76, 94, 78, 96)
    fill_tiles(chunk, TILE_WALL, 82, 94, 84, 96)
    # Exterior graveyard — additional tombstone rows (DS3: many gravestones)
    fill_tiles(chunk, TILE_WALL, 64, 112, 66, 114)
    fill_tiles(chunk, TILE_WALL, 70, 114, 72, 116)
    fill_tiles(chunk, TILE_WALL, 78, 112, 80, 114)
    fill_tiles(chunk, TILE_WALL, 86, 114, 88, 116)
    fill_tiles(chunk, TILE_WALL, 92, 112, 94, 114)
    fill_tiles(chunk, TILE_WALL, 66, 120, 68, 122)
    fill_tiles(chunk, TILE_WALL, 74, 122, 76, 124)
    fill_tiles(chunk, TILE_WALL, 82, 120, 84, 122)
    fill_tiles(chunk, TILE_WALL, 90, 122, 92, 124)
    # Sword Master area — stone stairs (DS3: stairs down to left)
    fill_tiles(chunk, TILE_WALL, 60, 130, 62, 134)
    fill_tiles(chunk, TILE_WALL, 66, 136, 68, 140)
    fill_tiles(chunk, TILE_WALL, 72, 130, 74, 132)
    # Right side exterior — rock and tree debris (DS3: ember pickup area)
    fill_tiles(chunk, TILE_WALL, 88, 134, 90, 136)
    fill_tiles(chunk, TILE_WALL, 96, 138, 98, 140)
    fill_tiles(chunk, TILE_WALL, 100, 132, 102, 134)

    # === SESSION 6 FIDELITY PASS — Firelink Shrine ===
    # Central chamber — shrine wall buttresses (DS3: thick stone walls with alcoves)
    fill_tiles(chunk, TILE_WALL, 68, 70, 70, 72)
    fill_tiles(chunk, TILE_WALL, 90, 70, 92, 72)
    fill_tiles(chunk, TILE_WALL, 68, 90, 70, 92)
    fill_tiles(chunk, TILE_WALL, 90, 90, 92, 92)
    # Interior arch stone details (DS3: arched ceiling supports)
    fill_tiles(chunk, TILE_WALL, 76, 72, 78, 74)
    fill_tiles(chunk, TILE_WALL, 82, 72, 84, 74)
    fill_tiles(chunk, TILE_WALL, 76, 90, 78, 92)
    fill_tiles(chunk, TILE_WALL, 82, 90, 84, 92)
    # Throne room — wall sconces and alcove details (DS3: dim throne alcove)
    fill_tiles(chunk, TILE_WALL, 66, 56, 68, 58)
    fill_tiles(chunk, TILE_WALL, 92, 56, 94, 58)
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 54)
    fill_tiles(chunk, TILE_WALL, 86, 52, 88, 54)
    # Andre's forge — additional workbench stones (DS3: forge tools and debris)
    fill_tiles(chunk, TILE_WALL, 46, 74, 48, 76)
    fill_tiles(chunk, TILE_WALL, 52, 84, 54, 86)
    fill_tiles(chunk, TILE_WALL, 44, 86, 46, 88)
    # East wing — stone bench supports (DS3: Hawkwood's sitting area)
    fill_tiles(chunk, TILE_WALL, 100, 80, 102, 82)
    fill_tiles(chunk, TILE_WALL, 108, 78, 110, 80)
    fill_tiles(chunk, TILE_WALL, 114, 84, 116, 86)
    # Handmaiden alcove — shelf walls (DS3: shrine handmaiden's corner)
    fill_tiles(chunk, TILE_WALL, 64, 64, 66, 66)
    fill_tiles(chunk, TILE_WALL, 70, 70, 72, 72)
    # Tower path — additional bridge supports (DS3: narrow stone bridge)
    fill_tiles(chunk, TILE_WALL, 38, 62, 40, 64)
    fill_tiles(chunk, TILE_WALL, 32, 56, 34, 58)
    # Rafter area — more wooden beams (DS3: exposed rafters above main hall)
    fill_tiles(chunk, TILE_WALL, 112, 66, 114, 68)
    fill_tiles(chunk, TILE_WALL, 118, 62, 120, 64)
    fill_tiles(chunk, TILE_WALL, 124, 66, 126, 68)
    # Entrance hall — additional arch pillars (DS3: grand stone entrance)
    fill_tiles(chunk, TILE_WALL, 74, 96, 76, 98)
    fill_tiles(chunk, TILE_WALL, 84, 96, 86, 98)
    # Exterior graveyard — more gravestone rows (DS3: dense graveyard with many plots)
    fill_tiles(chunk, TILE_WALL, 62, 106, 64, 108)
    fill_tiles(chunk, TILE_WALL, 90, 106, 92, 108)
    fill_tiles(chunk, TILE_WALL, 96, 116, 98, 118)
    fill_tiles(chunk, TILE_WALL, 64, 124, 66, 126)
    fill_tiles(chunk, TILE_WALL, 88, 124, 90, 126)
    # Entrance path — path edge stones (DS3: stone-lined path to shrine)
    fill_tiles(chunk, TILE_WALL, 72, 130, 74, 134)
    fill_tiles(chunk, TILE_WALL, 86, 130, 88, 134)
    fill_tiles(chunk, TILE_WALL, 76, 138, 78, 140)
    fill_tiles(chunk, TILE_WALL, 82, 138, 84, 140)
    # SESSION 10 FIDELITY PASS — Firelink Shrine
    # Additional DS3-faithful terrain: Ludleth throne alcove, tower base,
    # shrine entrance steps, graveyard path stones, Hawkwood bench detail
    # Ludleth throne alcove — small throne stones (DS3: Ludleth sits on a throne)
    fill_tiles(chunk, TILE_WALL, 78, 62, 79, 63)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 63)
    # Shrine interior — additional column bases (DS3: stone columns support roof)
    fill_tiles(chunk, TILE_WALL, 72, 78, 73, 79)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    fill_tiles(chunk, TILE_WALL, 76, 86, 77, 87)
    fill_tiles(chunk, TILE_WALL, 84, 86, 85, 87)
    # Andre forge area — anvil stones (DS3: Andre's anvil and tools)
    fill_tiles(chunk, TILE_WALL, 48, 78, 49, 79)
    fill_tiles(chunk, TILE_WALL, 44, 82, 45, 83)
    # Shrine entrance — step stones (DS3: stone steps at main entrance)
    fill_tiles(chunk, TILE_WALL, 78, 98, 79, 99)
    fill_tiles(chunk, TILE_WALL, 82, 98, 83, 99)
    fill_tiles(chunk, TILE_WALL, 76, 102, 77, 103)
    fill_tiles(chunk, TILE_WALL, 84, 102, 85, 103)
    # Tower base — foundation stones (DS3: tower at Firelink shrine)
    fill_tiles(chunk, TILE_WALL, 34, 54, 35, 55)
    fill_tiles(chunk, TILE_WALL, 30, 60, 31, 61)
    fill_tiles(chunk, TILE_WALL, 36, 58, 37, 59)
    # East wing — Hawkwood sitting area stones (DS3: Hawkwood sits on steps)
    fill_tiles(chunk, TILE_WALL, 106, 76, 107, 77)
    fill_tiles(chunk, TILE_WALL, 110, 82, 111, 83)
    fill_tiles(chunk, TILE_WALL, 104, 84, 105, 85)
    # Graveyard — additional gravestone clusters (DS3: dense graveyard)
    fill_tiles(chunk, TILE_WALL, 68, 108, 69, 109)
    fill_tiles(chunk, TILE_WALL, 84, 108, 85, 109)
    fill_tiles(chunk, TILE_WALL, 94, 110, 95, 111)
    fill_tiles(chunk, TILE_WALL, 60, 118, 61, 119)
    fill_tiles(chunk, TILE_WALL, 86, 118, 87, 119)
    fill_tiles(chunk, TILE_WALL, 72, 126, 73, 127)
    fill_tiles(chunk, TILE_WALL, 82, 126, 83, 127)
    # Path to tower — cliff edge stones (DS3: narrow cliff path)
    fill_tiles(chunk, TILE_WALL, 40, 66, 41, 67)
    fill_tiles(chunk, TILE_WALL, 36, 70, 37, 71)
    # Sword Master area — debris stones (DS3: Sword Master's location)
    fill_tiles(chunk, TILE_WALL, 58, 128, 59, 129)
    fill_tiles(chunk, TILE_WALL, 64, 134, 65, 135)
    fill_tiles(chunk, TILE_WALL, 70, 132, 71, 133)
    # Shrine upper — rafters and beam supports (DS3: exposed wooden rafters)
    fill_tiles(chunk, TILE_WALL, 116, 64, 117, 65)
    fill_tiles(chunk, TILE_WALL, 122, 60, 123, 61)
    # SESSION 10 PASS B — Firelink Shrine
    # Additional DS3 terrain: shrine exterior stones, Ludleth throne detail,
    # grave wreath stones, tower base steps
    fill_tiles(chunk, TILE_WALL, 74, 66, 75, 67)
    fill_tiles(chunk, TILE_WALL, 86, 64, 87, 65)
    fill_tiles(chunk, TILE_WALL, 60, 72, 61, 73)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 80, 74, 81, 75)
    fill_tiles(chunk, TILE_WALL, 52, 76, 53, 77)
    fill_tiles(chunk, TILE_WALL, 98, 116, 99, 117)
    fill_tiles(chunk, TILE_WALL, 62, 126, 63, 127)
    fill_tiles(chunk, TILE_WALL, 84, 124, 85, 125)
    fill_tiles(chunk, TILE_WALL, 42, 60, 43, 61)
    fill_tiles(chunk, TILE_WALL, 30, 58, 31, 59)
    fill_tiles(chunk, TILE_WALL, 116, 62, 117, 63)
    fill_tiles(chunk, TILE_WALL, 120, 66, 121, 67)


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
    # Stone landings on the descent to Vordt (DS3: no frost damage, just stone stairs)
    fill_tiles(chunk, TILE_GROUND, 78, 120, 84, 122)
    fill_tiles(chunk, TILE_GROUND, 86, 132, 92, 134)

    # Connection: cathedral to frost stairs
    fill_tiles(chunk, TILE_GROUND, 76, 110, 82, 114)

    # 10. VORDT ARENA — large oval at south end
    carve_ellipse(chunk, 100, 144, 22, 12)
    # Entry funnel from frost stairs
    fill_tiles(chunk, TILE_GROUND, 86, 136, 114, 142)

    # ================================================================
    # SESSION 9 FIDELITY PASS — LothricWall architectural details
    # ================================================================
    # High Wall ramparts — crenellation stones (DS3: walkable battlements)
    fill_tiles(chunk, TILE_WALL, 20, 16, 21, 17)
    fill_tiles(chunk, TILE_WALL, 26, 20, 27, 21)
    fill_tiles(chunk, TILE_WALL, 16, 24, 17, 25)
    fill_tiles(chunk, TILE_WALL, 30, 14, 31, 15)
    # Dragon fire courtyard — scorched stone patches (DS3: dragon burns area)
    fill_tiles(chunk, TILE_WALL, 42, 28, 43, 29)
    fill_tiles(chunk, TILE_WALL, 46, 32, 47, 33)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    fill_tiles(chunk, TILE_WALL, 50, 26, 51, 27)
    fill_tiles(chunk, TILE_WALL, 44, 38, 45, 39)
    # Lothric Knight barracks — weapon rack stones (DS3: knight equipment room)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 49)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 43)
    # Treasury room — coffer debris (DS3: looted treasury with empty chests)
    fill_tiles(chunk, TILE_WALL, 70, 56, 71, 57)
    fill_tiles(chunk, TILE_WALL, 74, 60, 75, 61)
    fill_tiles(chunk, TILE_WALL, 66, 64, 67, 65)
    fill_tiles(chunk, TILE_WALL, 78, 54, 79, 55)
    # Frost bridge approach — ice-cracked stones (DS3: frost-covered path to Vordt)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    fill_tiles(chunk, TILE_WALL, 86, 74, 87, 75)
    fill_tiles(chunk, TILE_WALL, 78, 78, 79, 79)
    fill_tiles(chunk, TILE_WALL, 90, 68, 91, 69)
    fill_tiles(chunk, TILE_WALL, 84, 80, 85, 81)
    # Dancer's arena approach — tapestry stones (DS3: ornate hall before Emma)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 100, 90, 101, 91)
    fill_tiles(chunk, TILE_WALL, 92, 94, 93, 95)
    fill_tiles(chunk, TILE_WALL, 104, 84, 105, 85)
    # Vordt frost stairs — frozen step debris (DS3: icy descent to Vordt)
    fill_tiles(chunk, TILE_WALL, 88, 120, 89, 121)
    fill_tiles(chunk, TILE_WALL, 94, 124, 95, 125)
    fill_tiles(chunk, TILE_WALL, 90, 128, 91, 129)
    fill_tiles(chunk, TILE_WALL, 96, 132, 97, 133)
    fill_tiles(chunk, TILE_WALL, 86, 136, 87, 137)
    # Pus of Man tower — blackened bricks (DS3: wyvern with dark mass)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    fill_tiles(chunk, TILE_WALL, 38, 48, 39, 49)
    fill_tiles(chunk, TILE_WALL, 30, 52, 31, 53)

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
        ("HollowAssassin", 38, 56), ("LothricKnight", 50, 54),
        ("LothricKnight", 62, 54), ("LothricKnight", 74, 54),
        ("Darkwraith", 54, 50),                    # Darkwraith in locked cell under Tower (Lift Chamber Key)
        ("HollowSoldier", 50, 66),
        ("HollowAssassin", 62, 66), ("HollowSoldier", 74, 64),
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
        # Additional DS3 High Wall enemies — more hollow soldiers (DS3: dense with hollow soldiers)
        ("HollowSoldier", 34, 14), ("HollowSoldier", 60, 16),        # Wall rampart reinforcements
        ("HollowSoldier", 44, 44), ("HollowSoldier", 64, 58),        # Tower area hollows
        ("HollowSoldier", 28, 68), ("HollowSoldier", 72, 70),        # Residential maze hollows
        ("HollowSoldier", 26, 86), ("HollowSoldier", 58, 98),        # Courtyard hollows
    ]
    for kind, tx, ty in enemy_positions:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- NPCs ---
    # Greirat — locked in cell below tower (DS3: basement cell, asks for Loretta's Bone)
    entities.append(make_entity("Npc", 36 * 16, 60 * 16, [
        make_field("name", "String", "Greirat"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#A0A0A0"),
        make_field("dialogue", "String",
            "...Who are you?|Will you let me out of here?|I can show you a thing or two in return"),
    ]))
    # Emma — High Priestess in the cathedral (DS3: gives Small Lothric Banner, triggers Dancer)
    entities.append(make_entity("Npc", 80 * 16, 108 * 16, [
        make_field("name", "String", "Emma"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A0D0"),
        make_field("dialogue", "String",
            "Hello, Unkindled One|I am Emma, High Priestess of Lothric|Seek the Basin of Vow, and present it to the statue|To see the Prince, and hear his tale"),
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
        ("Consumable", "Firebomb", 74, 100, 0),                    # Replaces duplicate Estus Shard
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

    # === ADDITIONAL HIGH WALL DETAILS — DS3 fidelity ===
    # Wall entrance — battlement stones (DS3: stone ramparts with hollow soldiers)
    fill_tiles(chunk, TILE_WALL, 10, 8, 12, 10)
    fill_tiles(chunk, TILE_WALL, 20, 12, 22, 14)
    fill_tiles(chunk, TILE_WALL, 28, 16, 30, 18)
    fill_tiles(chunk, TILE_WALL, 14, 14, 16, 16)
    # Dragon bridge — more fire debris and cover pillars (DS3: wyvern burns sections)
    fill_tiles(chunk, TILE_WALL, 16, 32, 18, 34)
    fill_tiles(chunk, TILE_WALL, 28, 36, 30, 38)
    fill_tiles(chunk, TILE_WALL, 40, 34, 42, 36)
    fill_tiles(chunk, TILE_WALL, 48, 38, 50, 40)
    fill_tiles(chunk, TILE_WALL, 12, 38, 14, 40)
    # Tower area — more interior walls (DS3: Winged Knight room, Greirat's cell)
    fill_tiles(chunk, TILE_WALL, 54, 38, 56, 40)
    fill_tiles(chunk, TILE_WALL, 66, 44, 68, 46)
    fill_tiles(chunk, TILE_WALL, 58, 48, 60, 50)
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 50)
    # Residential maze — additional house walls (DS3: narrow alleys between houses)
    fill_tiles(chunk, TILE_WALL, 38, 58, 40, 60)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)
    fill_tiles(chunk, TILE_WALL, 62, 58, 64, 60)
    fill_tiles(chunk, TILE_WALL, 72, 66, 74, 68)
    fill_tiles(chunk, TILE_WALL, 34, 70, 36, 72)
    fill_tiles(chunk, TILE_WALL, 56, 70, 58, 72)
    fill_tiles(chunk, TILE_WALL, 44, 76, 46, 78)
    fill_tiles(chunk, TILE_WALL, 62, 76, 64, 78)
    fill_tiles(chunk, TILE_WALL, 36, 80, 38, 82)
    fill_tiles(chunk, TILE_WALL, 54, 80, 56, 82)
    # Courtyard — fountain detail and perimeter walls (DS3: central fountain area)
    fill_tiles(chunk, TILE_WALL, 30, 88, 36, 90)
    fill_tiles(chunk, TILE_WALL, 22, 94, 24, 96)
    fill_tiles(chunk, TILE_WALL, 44, 92, 46, 94)
    fill_tiles(chunk, TILE_WALL, 16, 86, 18, 88)
    fill_tiles(chunk, TILE_WALL, 50, 84, 52, 86)
    # Knight path — stone arches (DS3: stone path to cathedral)
    fill_tiles(chunk, TILE_WALL, 60, 90, 62, 92)
    fill_tiles(chunk, TILE_WALL, 70, 96, 72, 98)
    fill_tiles(chunk, TILE_WALL, 82, 100, 84, 102)
    fill_tiles(chunk, TILE_WALL, 88, 94, 90, 96)
    # Cathedral — chapel columns (DS3: Emma's chapel)
    fill_tiles(chunk, TILE_WALL, 68, 102, 70, 104)
    fill_tiles(chunk, TILE_WALL, 78, 108, 80, 110)
    fill_tiles(chunk, TILE_WALL, 90, 104, 92, 106)
    fill_tiles(chunk, TILE_WALL, 74, 110, 76, 112)
    # Frost stairs — ice-covered walls (DS3: cold descent to Vordt)
    fill_tiles(chunk, TILE_WALL, 74, 116, 76, 118)
    fill_tiles(chunk, TILE_WALL, 82, 124, 84, 126)
    fill_tiles(chunk, TILE_WALL, 90, 128, 92, 130)
    fill_tiles(chunk, TILE_WALL, 78, 134, 80, 136)
    fill_tiles(chunk, TILE_WALL, 86, 138, 88, 140)
    # Vordt arena perimeter — ruined walls (DS3: open arena below the wall)
    fill_tiles(chunk, TILE_WALL, 84, 142, 86, 144)
    fill_tiles(chunk, TILE_WALL, 108, 140, 110, 142)
    fill_tiles(chunk, TILE_WALL, 116, 146, 118, 148)
    fill_tiles(chunk, TILE_WALL, 92, 150, 94, 152)

    # === ADDITIONAL DS3 HIGH WALL TERRAIN — Session 6 fidelity pass ===
    # Wall entrance — stone parapet merlons (DS3: battlement crenellations along rampart)
    fill_tiles(chunk, TILE_WALL, 6, 10, 8, 12)
    fill_tiles(chunk, TILE_WALL, 38, 6, 40, 8)
    fill_tiles(chunk, TILE_WALL, 56, 10, 58, 12)
    fill_tiles(chunk, TILE_WALL, 34, 18, 36, 20)
    # Entry stairway edges (DS3: curved stone stairs from coiled sword to rampart)
    fill_tiles(chunk, TILE_WALL, 8, 4, 10, 6)
    fill_tiles(chunk, TILE_WALL, 12, 4, 14, 6)
    fill_tiles(chunk, TILE_WALL, 40, 14, 42, 16)
    # Dragon bridge — wyvern corpse debris (DS3: massive dead dragon body across bridge)
    fill_tiles(chunk, TILE_WALL, 20, 28, 22, 30)
    fill_tiles(chunk, TILE_WALL, 44, 32, 46, 34)
    fill_tiles(chunk, TILE_WALL, 52, 34, 54, 36)
    # Scorched walls near wyvern head (DS3: burned stone where wyvern breathes fire)
    fill_tiles(chunk, TILE_WALL, 14, 26, 16, 28)
    fill_tiles(chunk, TILE_WALL, 50, 30, 52, 32)
    # Tower area — Greirat's cell bars (DS3: iron bar divider in basement cell)
    fill_tiles(chunk, TILE_WALL, 60, 42, 62, 44)
    fill_tiles(chunk, TILE_WALL, 64, 46, 66, 48)
    fill_tiles(chunk, TILE_WALL, 72, 42, 74, 44)
    # Tower upper walkway rail (DS3: stone railing around tower on the wall bonfire)
    fill_tiles(chunk, TILE_WALL, 56, 36, 58, 38)
    fill_tiles(chunk, TILE_WALL, 68, 50, 70, 52)
    # Residential maze — wooden scaffolding supports (DS3: wooden scaffolding in narrow alleys)
    fill_tiles(chunk, TILE_WALL, 26, 56, 28, 58)
    fill_tiles(chunk, TILE_WALL, 46, 54, 48, 56)
    fill_tiles(chunk, TILE_WALL, 58, 62, 60, 64)
    fill_tiles(chunk, TILE_WALL, 68, 60, 70, 62)
    fill_tiles(chunk, TILE_WALL, 40, 68, 42, 70)
    fill_tiles(chunk, TILE_WALL, 52, 68, 54, 70)
    # Hanging corpse posts (DS3: bodies hanging from wooden frames throughout settlement)
    fill_tiles(chunk, TILE_WALL, 32, 60, 34, 62)
    fill_tiles(chunk, TILE_WALL, 64, 70, 66, 72)
    fill_tiles(chunk, TILE_WALL, 42, 80, 44, 82)
    # Courtyard — sewer grate pillars (DS3: sewer entrance with iron grate)
    fill_tiles(chunk, TILE_WALL, 56, 84, 58, 86)
    fill_tiles(chunk, TILE_WALL, 60, 92, 62, 94)
    # Lift mechanism housing (DS3: stone lift room with pressure plate)
    fill_tiles(chunk, TILE_WALL, 62, 96, 64, 98)
    fill_tiles(chunk, TILE_WALL, 56, 94, 58, 96)
    # Cathedral — altar block (DS3: stone altar where Emma sits)
    fill_tiles(chunk, TILE_WALL, 76, 104, 78, 106)
    # Chapel pews (DS3: wooden bench rows inside chapel)
    fill_tiles(chunk, TILE_WALL, 80, 100, 82, 102)
    fill_tiles(chunk, TILE_WALL, 86, 108, 88, 110)
    # Statue alcove (DS3: knight statue where Basin of Vows is placed)
    fill_tiles(chunk, TILE_WALL, 92, 108, 94, 110)
    # Frost stairs — ice-covered pillars (DS3: frozen columns along cold descent)
    fill_tiles(chunk, TILE_WALL, 80, 114, 82, 116)
    fill_tiles(chunk, TILE_WALL, 92, 120, 94, 122)
    fill_tiles(chunk, TILE_WALL, 76, 128, 78, 130)
    fill_tiles(chunk, TILE_WALL, 88, 134, 90, 136)
    fill_tiles(chunk, TILE_WALL, 94, 138, 96, 140)
    # Collapsed masonry debris (DS3: crumbling castle walls on the descent)
    fill_tiles(chunk, TILE_WALL, 72, 120, 74, 122)
    fill_tiles(chunk, TILE_WALL, 84, 130, 86, 132)
    fill_tiles(chunk, TILE_WALL, 96, 136, 98, 138)
    # Vordt arena — gate arch (DS3: massive stone gate at arena edge)
    fill_tiles(chunk, TILE_WALL, 96, 144, 98, 146)
    fill_tiles(chunk, TILE_WALL, 112, 144, 114, 146)
    fill_tiles(chunk, TILE_WALL, 100, 150, 102, 152)
    fill_tiles(chunk, TILE_WALL, 106, 148, 108, 150)
    # SESSION 10 FIDELITY PASS — Lothric Wall
    # Additional DS3-faithful terrain: crenellation debris, dragon scorch patches,
    # frost bridge stones, Pus of Man tower debris, Vordt arena details
    # Dragon bridge — scorch patches (DS3: dragon breathes fire on bridge)
    fill_tiles(chunk, TILE_WALL, 38, 38, 39, 39)
    fill_tiles(chunk, TILE_WALL, 42, 42, 43, 43)
    fill_tiles(chunk, TILE_WALL, 46, 36, 47, 37)
    fill_tiles(chunk, TILE_WALL, 50, 40, 51, 41)
    # Crenellation stones — battlement debris (DS3: castle battlements with gaps)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 29)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 33)
    fill_tiles(chunk, TILE_WALL, 34, 30, 35, 31)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    # Frost bridge — ice-cracked stones (DS3: frost-covered bridge near Vordt)
    fill_tiles(chunk, TILE_WALL, 58, 48, 59, 49)
    fill_tiles(chunk, TILE_WALL, 62, 52, 63, 53)
    fill_tiles(chunk, TILE_WALL, 66, 50, 67, 51)
    fill_tiles(chunk, TILE_WALL, 70, 54, 71, 55)
    # Pus of Man tower — tower debris (DS3: dragon with Pus of Man on tower)
    fill_tiles(chunk, TILE_WALL, 74, 42, 75, 43)
    fill_tiles(chunk, TILE_WALL, 78, 38, 79, 39)
    fill_tiles(chunk, TILE_WALL, 72, 36, 73, 37)
    # Vordt arena — frozen stone debris (DS3: frozen arena at wall base)
    fill_tiles(chunk, TILE_WALL, 82, 60, 83, 61)
    fill_tiles(chunk, TILE_WALL, 88, 64, 89, 65)
    fill_tiles(chunk, TILE_WALL, 94, 62, 95, 63)
    fill_tiles(chunk, TILE_WALL, 86, 66, 87, 67)
    fill_tiles(chunk, TILE_WALL, 92, 68, 93, 69)
    fill_tiles(chunk, TILE_WALL, 98, 64, 99, 65)
    # Residential area — house debris (DS3: residential quarter ruins)
    fill_tiles(chunk, TILE_WALL, 30, 58, 31, 59)
    fill_tiles(chunk, TILE_WALL, 36, 62, 37, 63)
    fill_tiles(chunk, TILE_WALL, 42, 60, 43, 61)
    fill_tiles(chunk, TILE_WALL, 48, 66, 49, 67)
    # Dancer lift — elevator shaft debris (DS3: lift mechanism stones)
    fill_tiles(chunk, TILE_WALL, 104, 88, 105, 89)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)
    fill_tiles(chunk, TILE_WALL, 100, 90, 101, 91)


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
    # Entry gate walls (DS3: stone archway entry)
    fill_tiles(chunk, TILE_WALL, 8, 10, 10, 18)
    fill_tiles(chunk, TILE_WALL, 32, 10, 34, 18)
    # Tombstones near entry (DS3: graveyard at entrance)
    fill_tiles(chunk, TILE_WALL, 14, 14, 15, 16)
    fill_tiles(chunk, TILE_WALL, 22, 16, 23, 18)

    # 2. HOUSE STREET — main street with wooden houses
    fill_tiles(chunk, TILE_GROUND, 30, 22, 62, 48)
    # House wall protrusions creating narrow alleys
    # DS3: densely packed wooden houses with narrow gaps between them
    fill_tiles(chunk, TILE_WALL, 36, 26, 42, 32)  # First house block (left)
    fill_tiles(chunk, TILE_WALL, 50, 34, 56, 40)  # Second house block (right)
    fill_tiles(chunk, TILE_WALL, 38, 40, 44, 46)  # Third house block (lower left)
    # Additional house walls for DS3 fidelity
    fill_tiles(chunk, TILE_WALL, 30, 30, 34, 36)  # Entry house
    fill_tiles(chunk, TILE_WALL, 44, 24, 48, 28)  # Upper house
    fill_tiles(chunk, TILE_WALL, 58, 42, 62, 48)  # Lower right house
    fill_tiles(chunk, TILE_WALL, 30, 44, 34, 48)  # Southwest corner house

    # 3. GIANT TOWER — circular tower (center-left)
    carve_ellipse(chunk, 52, 26, 10, 12)
    fill_tiles(chunk, TILE_GROUND, 44, 22, 56, 30)
    # Tower base walls (DS3: stone tower base)
    fill_tiles(chunk, TILE_WALL, 44, 24, 46, 28)
    fill_tiles(chunk, TILE_WALL, 54, 24, 56, 28)

    # 4. BONFIRE SQUARE — open area with large bonfire (center)
    carve_ellipse(chunk, 70, 56, 16, 12)
    fill_tiles(chunk, TILE_GROUND, 56, 42, 72, 50)
    # Square perimeter walls (DS3: buildings surrounding the square)
    fill_tiles(chunk, TILE_WALL, 58, 44, 60, 48)   # NW building corner
    fill_tiles(chunk, TILE_WALL, 68, 44, 70, 48)   # NE building corner
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 66)   # South building
    fill_tiles(chunk, TILE_WALL, 74, 58, 76, 62)   # SE building

    # 5. DILAPIDATED BRIDGE — connecting tower area to square
    fill_tiles(chunk, TILE_GROUND, 54, 34, 64, 42)
    # Bridge railing remnants (DS3: broken wooden bridge)
    fill_tiles(chunk, TILE_WALL, 56, 34, 57, 36)
    fill_tiles(chunk, TILE_WALL, 62, 38, 63, 40)

    # 6. CLIFFSIDE PATH — narrow path along cliff (east)
    fill_tiles(chunk, TILE_GROUND, 84, 38, 112, 48)
    carve_ellipse(chunk, 100, 42, 8, 6)
    # Cliff edge walls (DS3: sheer drops on one side)
    fill_tiles(chunk, TILE_WALL, 86, 38, 88, 42)
    fill_tiles(chunk, TILE_WALL, 94, 44, 96, 48)
    fill_tiles(chunk, TILE_WALL, 104, 38, 106, 42)
    # Sewer pipe exits (DS3: sewer grates along cliffside)
    fill_tiles(chunk, TILE_WALL, 90, 46, 92, 48)
    fill_tiles(chunk, TILE_WALL, 108, 46, 110, 48)

    # 7. FIRE DEMON SQUARE (center-right)
    carve_ellipse(chunk, 100, 64, 14, 10)
    fill_tiles(chunk, TILE_GROUND, 82, 56, 96, 66)
    # Building ruins around fire demon area (DS3: burnt structures)
    fill_tiles(chunk, TILE_WALL, 84, 58, 86, 62)
    fill_tiles(chunk, TILE_WALL, 92, 60, 94, 64)
    fill_tiles(chunk, TILE_WALL, 86, 66, 88, 70)

    # 8. PILGRIM CAMP (upper-right) — Yoel and pilgrims
    fill_tiles(chunk, TILE_GROUND, 114, 28, 140, 42)
    carve_ellipse(chunk, 128, 34, 10, 6)
    # Pilgrim stones (DS3: pilgrim bodies lying in rows)
    fill_tiles(chunk, TILE_WALL, 118, 32, 120, 34)
    fill_tiles(chunk, TILE_WALL, 124, 36, 126, 38)
    fill_tiles(chunk, TILE_WALL, 132, 30, 134, 32)
    fill_tiles(chunk, TILE_WALL, 136, 36, 138, 38)

    # 9. IRINA'S CELL (right edge)
    fill_tiles(chunk, TILE_GROUND, 140, 48, 152, 60)
    carve_ellipse(chunk, 146, 54, 6, 5)
    # Cell walls (DS3: locked room in graveyard)
    fill_tiles(chunk, TILE_WALL, 140, 50, 142, 54)
    fill_tiles(chunk, TILE_WALL, 150, 52, 152, 56)
    # Gravestones near Irina (DS3: graveyard area)
    fill_tiles(chunk, TILE_WALL, 144, 58, 145, 60)
    fill_tiles(chunk, TILE_WALL, 148, 48, 149, 50)

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
    # SESSION 9 FIDELITY PASS — UndeadSettlement architectural details
    # ================================================================
    # Entry houses — thatched roof debris (DS3: wooden houses with thatched roofs)
    fill_tiles(chunk, TILE_WALL, 20, 18, 21, 19)
    fill_tiles(chunk, TILE_WALL, 26, 22, 27, 23)
    fill_tiles(chunk, TILE_WALL, 16, 26, 17, 27)
    fill_tiles(chunk, TILE_WALL, 30, 16, 31, 17)
    fill_tiles(chunk, TILE_WALL, 22, 30, 23, 31)
    # Central square — bonfire well stones (DS3: well in center of settlement)
    fill_tiles(chunk, TILE_WALL, 44, 34, 45, 35)
    fill_tiles(chunk, TILE_WALL, 48, 38, 49, 39)
    fill_tiles(chunk, TILE_WALL, 40, 42, 41, 43)
    fill_tiles(chunk, TILE_WALL, 52, 32, 53, 33)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 45)
    # Evangelist house — overturned furniture stones (DS3: houses with evangelists)
    fill_tiles(chunk, TILE_WALL, 56, 48, 57, 49)
    fill_tiles(chunk, TILE_WALL, 60, 52, 61, 53)
    fill_tiles(chunk, TILE_WALL, 52, 56, 53, 57)
    fill_tiles(chunk, TILE_WALL, 64, 46, 65, 47)
    # Tree hollow area — dead tree roots (DS3: massive hollow tree)
    fill_tiles(chunk, TILE_WALL, 68, 58, 69, 59)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 63)
    fill_tiles(chunk, TILE_WALL, 64, 66, 65, 67)
    fill_tiles(chunk, TILE_WALL, 76, 56, 77, 57)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)
    # Cliffside path — wooden scaffold debris (DS3: wooden platforms along cliff)
    fill_tiles(chunk, TILE_WALL, 80, 64, 81, 65)
    fill_tiles(chunk, TILE_WALL, 84, 68, 85, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 88, 60, 89, 61)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    # Greatwood arena — roots and debris (DS3: Curse-rotted Greatwood arena pit)
    fill_tiles(chunk, TILE_WALL, 96, 100, 97, 101)
    fill_tiles(chunk, TILE_WALL, 100, 104, 101, 105)
    fill_tiles(chunk, TILE_WALL, 92, 108, 93, 109)
    fill_tiles(chunk, TILE_WALL, 104, 98, 105, 99)
    fill_tiles(chunk, TILE_WALL, 98, 110, 99, 111)
    # Fire Demon arena — scorched workshop (DS3: Siegward's demon encounter)
    fill_tiles(chunk, TILE_WALL, 110, 78, 111, 79)
    fill_tiles(chunk, TILE_WALL, 114, 82, 115, 83)
    fill_tiles(chunk, TILE_WALL, 106, 86, 107, 87)
    fill_tiles(chunk, TILE_WALL, 118, 76, 119, 77)

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
        ("PeasantHollow", 146, 52),                                   # DS3: Hollow in lift tower area
        # Holy Knight Hodrick invasion (DS3: Mad Spirit invades near Dilapidated Bridge if Embered)
        ("MiniBoss", 64, 66),                                         # DS3: Hodrick, Mound-Makers member
        # Irina's area — Skeletons (DS3: skeletons animate and attack in graveyard near Irina)
        ("Skeleton", 140, 52), ("Skeleton", 142, 54), ("Skeleton", 144, 48),
        # Crystal Lizard (DS3: near Hodrick invasion area / cliff path)
        ("CrystalLizard", 112, 46),
        # Additional DS3 enemies for fidelity
        ("PeasantHollow", 36, 34),                                   # DS3: hollow in house near entrance
        ("PeasantHollow", 72, 44),                                   # DS3: hollow in market square
        ("Thrall", 88, 48),                                          # DS3: thrall ambush on rooftops
        ("Thrall", 92, 52),                                          # DS3: thrall drops from ceiling
        ("HollowSoldier", 76, 64),                                   # DS3: soldier near fire demon area
        ("PeasantHollow", 100, 58),                                  # DS3: hollow near cliff edge
        ("HollowSoldier", 104, 66),                                  # DS3: soldier on lower cliff
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
            "I am Yoel of Londor, a pilgrim|Let me grant you true strength|Come. Touch the darkness within me"),
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
            "A pyromancy student? Very well|I can teach you the flame arts|Ah, the flame is a fickle thing, as unpredictable as a woman"),
    ]))
    # Irina of Carim — miracle teacher in cell (DS3: found through locked door in sewers, near skeletons)
    entities.append(make_entity("Npc", 146 * 16, 54 * 16, [
        make_field("name", "String", "Irina of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7D9B"),
        make_field("dialogue", "String",
            "I am Irina of Carim|I can teach you miracles, if you wish|Please, take me to the shrine"),
    ]))
    # Eygon of Carim — guards Irina (DS3: found outside near Irina, warns about the champion)
    entities.append(make_entity("Npc", 148 * 16, 50 * 16, [
        make_field("name", "String", "Eygon of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A3A2A"),
        make_field("dialogue", "String",
            "I am Eygon of Carim, of the Morne bloodline|Keep your hands off the woman|She is my responsibility, not yours"),
    ]))

    # --- Items (DS3 Undead Settlement) ---
    # Large Soul of a Deserted Corpse — entry rampart
    entities.append(make_entity("Item", 22 * 16, 12 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse"),
        make_field("value", "Int", 400)]))
    # Alluring Skull 2x — near dogs by overturned coach
    entities.append(make_entity("Item", 24 * 16, 18 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Charcoal Pine Bundle")]))
    # Loretta's Bone — hanging body outside house
    entities.append(make_entity("Item", 48 * 16, 36 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Loretta's Bone")]))
    # Repair Powder 2x — around corner from Loretta's Bone
    entities.append(make_entity("Item", 42 * 16, 34 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Repair Powder")]))
    # Charcoal Pine Bundle 2x — lower floor of house
    entities.append(make_entity("Item", 44 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Warriors of Sunlight")]))
    # Charcoal Pine Resin 2x — near caged limbs
    entities.append(make_entity("Item", 52 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Coin")]))
    # Fading Soul — path near Hodrick
    entities.append(make_entity("Item", 98 * 16, 52 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Fading Soul")]))
    # Red Bug Pellet 2x — open area after Fire Demon
    entities.append(make_entity("Item", 92 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Red Bug Pellet")]))
    # Large Club — open area after Fire Demon
    entities.append(make_entity("Item", 90 * 16, 44 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Large Club")]))
    # Alluring Skull 2x — structure near Fire Demon area
    entities.append(make_entity("Item", 96 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Fading Soul")]))
    # Ember — giant spear area
    entities.append(make_entity("Item", 110 * 16, 64 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Ember")]))
    # Young White Branch 2x — giant spear area
    entities.append(make_entity("Item", 106 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Young White Branch")]))
    # Large Soul of a Deserted Corpse — giant spear area
    entities.append(make_entity("Item", 112 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse"),
        make_field("value", "Int", 400)]))
    # Mortician's Ashes — graveyard up from giant area
    entities.append(make_entity("Item", 116 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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

    # === ADDITIONAL INTERNAL STRUCTURES — Undead Settlement DS3 fidelity ===
    # Entry street — wooden house interior walls (DS3: multi-room houses line the street)
    fill_tiles(chunk, TILE_WALL, 18, 38, 20, 42)
    fill_tiles(chunk, TILE_WALL, 28, 35, 30, 38)
    fill_tiles(chunk, TILE_WALL, 38, 40, 40, 42)
    # Hanging corpse posts along street (DS3: many hanging bodies on wooden frames)
    fill_tiles(chunk, TILE_WALL, 24, 30, 25, 33)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 37)
    # House street — additional narrow alley walls (DS3: cramped alleys between houses)
    fill_tiles(chunk, TILE_WALL, 46, 30, 48, 33)
    fill_tiles(chunk, TILE_WALL, 52, 38, 54, 41)
    fill_tiles(chunk, TILE_WALL, 40, 34, 42, 36)
    # Multi-story dwelling interior partitions (DS3: Cornyx cage building has rooms)
    fill_tiles(chunk, TILE_WALL, 42, 26, 43, 28)
    fill_tiles(chunk, TILE_WALL, 48, 32, 49, 35)
    # Burning tree square — pyre remnants and stone edges (DS3: massive blazing tree)
    fill_tiles(chunk, TILE_WALL, 22, 52, 24, 55)
    fill_tiles(chunk, TILE_WALL, 35, 48, 37, 50)
    fill_tiles(chunk, TILE_WALL, 62, 54, 64, 56)
    fill_tiles(chunk, TILE_WALL, 70, 50, 72, 52)
    # Giant tower — tower base reinforcement (DS3: tall circular stone tower)
    fill_tiles(chunk, TILE_WALL, 50, 24, 52, 26)
    fill_tiles(chunk, TILE_WALL, 56, 28, 58, 30)
    # Dilapidated bridge — broken plank remnants (DS3: rotting wooden bridge)
    fill_tiles(chunk, TILE_WALL, 58, 36, 59, 38)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 42)
    # Cliffside path — sewer grates and rock outcrops
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 57)
    fill_tiles(chunk, TILE_WALL, 55, 50, 57, 52)
    fill_tiles(chunk, TILE_WALL, 15, 62, 17, 65)
    fill_tiles(chunk, TILE_WALL, 28, 65, 30, 68)
    # Sewer tunnel walls (DS3: narrow tunnels beneath settlement leading to Irina)
    fill_tiles(chunk, TILE_WALL, 42, 62, 44, 65)
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 62)
    fill_tiles(chunk, TILE_WALL, 68, 55, 70, 58)
    fill_tiles(chunk, TILE_WALL, 78, 52, 80, 55)
    # Graveyard tombstone rows (DS3: dense graveyard near Dilapidated Bridge)
    fill_tiles(chunk, TILE_WALL, 74, 62, 75, 64)
    fill_tiles(chunk, TILE_WALL, 80, 66, 81, 68)
    fill_tiles(chunk, TILE_WALL, 86, 60, 87, 62)
    # Irina's cell area walls (DS3: locked cell with skeleton graveyard outside)
    fill_tiles(chunk, TILE_WALL, 142, 56, 144, 58)
    fill_tiles(chunk, TILE_WALL, 148, 54, 150, 56)
    # Cliff underside — underground passage walls (DS3: tunnels below the cliff)
    fill_tiles(chunk, TILE_WALL, 56, 80, 58, 83)
    fill_tiles(chunk, TILE_WALL, 70, 86, 72, 88)
    fill_tiles(chunk, TILE_WALL, 62, 76, 64, 78)
    # Pit of Hollows / Greatwood arena edge (DS3: circular pit with hollow worshippers)
    fill_tiles(chunk, TILE_WALL, 82, 100, 84, 103)
    fill_tiles(chunk, TILE_WALL, 96, 108, 98, 110)
    fill_tiles(chunk, TILE_WALL, 86, 114, 88, 116)
    fill_tiles(chunk, TILE_WALL, 94, 96, 96, 98)
    # Lift shaft walls (DS3: stone elevator to Road of Sacrifices, guarded by Boreal Knight)
    fill_tiles(chunk, TILE_WALL, 143, 48, 145, 51)
    fill_tiles(chunk, TILE_WALL, 149, 50, 151, 53)
    # Pilgrim camp stones (DS3: Yoel among collapsed pilgrims in stone alcoves)
    fill_tiles(chunk, TILE_WALL, 122, 38, 124, 40)
    fill_tiles(chunk, TILE_WALL, 130, 34, 132, 36)
    fill_tiles(chunk, TILE_WALL, 136, 32, 138, 34)
    # Fire Demon plaza ruins (DS3: Siegward helps fight demon among stone debris)
    fill_tiles(chunk, TILE_WALL, 88, 68, 90, 70)
    fill_tiles(chunk, TILE_WALL, 104, 60, 106, 62)
    fill_tiles(chunk, TILE_WALL, 98, 56, 100, 58)

    # === SESSION 6 FIDELITY PASS — Undead Settlement ===
    # Entry area — more tombstones and stone walls (DS3: graveyard at settlement entry)
    fill_tiles(chunk, TILE_WALL, 10, 22, 12, 24)
    fill_tiles(chunk, TILE_WALL, 28, 20, 30, 22)
    fill_tiles(chunk, TILE_WALL, 16, 24, 18, 26)
    fill_tiles(chunk, TILE_WALL, 26, 26, 28, 28)
    # House street — more interior walls (DS3: cramped multi-room wooden houses)
    fill_tiles(chunk, TILE_WALL, 34, 34, 36, 36)
    fill_tiles(chunk, TILE_WALL, 56, 36, 58, 38)
    fill_tiles(chunk, TILE_WALL, 44, 38, 46, 40)
    fill_tiles(chunk, TILE_WALL, 36, 42, 38, 44)
    fill_tiles(chunk, TILE_WALL, 52, 44, 54, 46)
    fill_tiles(chunk, TILE_WALL, 60, 40, 62, 42)
    # Giant tower — additional base stones (DS3: massive circular stone tower)
    fill_tiles(chunk, TILE_WALL, 48, 26, 50, 28)
    fill_tiles(chunk, TILE_WALL, 54, 30, 56, 32)
    fill_tiles(chunk, TILE_WALL, 46, 30, 48, 32)
    # Bonfire square — building corners (DS3: buildings surround the square)
    fill_tiles(chunk, TILE_WALL, 60, 46, 62, 48)
    fill_tiles(chunk, TILE_WALL, 66, 48, 68, 50)
    fill_tiles(chunk, TILE_WALL, 70, 54, 72, 56)
    fill_tiles(chunk, TILE_WALL, 56, 58, 58, 60)
    # Cliffside path — rock formations (DS3: sheer cliff with rock outcrops)
    fill_tiles(chunk, TILE_WALL, 92, 40, 94, 42)
    fill_tiles(chunk, TILE_WALL, 100, 44, 102, 46)
    fill_tiles(chunk, TILE_WALL, 108, 42, 110, 44)
    fill_tiles(chunk, TILE_WALL, 98, 48, 100, 50)
    # Fire Demon square — more burnt debris (DS3: scorched plaza after demon fight)
    fill_tiles(chunk, TILE_WALL, 84, 64, 86, 66)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    fill_tiles(chunk, TILE_WALL, 102, 66, 104, 68)
    fill_tiles(chunk, TILE_WALL, 88, 70, 90, 72)
    # Pilgrim camp — more stone markers (DS3: rows of turned pilgrims)
    fill_tiles(chunk, TILE_WALL, 116, 34, 118, 36)
    fill_tiles(chunk, TILE_WALL, 126, 32, 128, 34)
    fill_tiles(chunk, TILE_WALL, 134, 38, 136, 40)
    fill_tiles(chunk, TILE_WALL, 120, 40, 122, 42)
    # Irina's cell — more graveyard stones (DS3: graveyard near locked cell)
    fill_tiles(chunk, TILE_WALL, 136, 48, 138, 50)
    fill_tiles(chunk, TILE_WALL, 144, 52, 146, 54)
    fill_tiles(chunk, TILE_WALL, 140, 56, 142, 58)
    fill_tiles(chunk, TILE_WALL, 148, 58, 150, 60)
    # Cliff underside — more tunnel walls (DS3: underground passages below village)
    fill_tiles(chunk, TILE_WALL, 52, 78, 54, 80)
    fill_tiles(chunk, TILE_WALL, 66, 82, 68, 84)
    fill_tiles(chunk, TILE_WALL, 74, 88, 76, 90)
    fill_tiles(chunk, TILE_WALL, 58, 86, 60, 88)
    # Pit of Hollows — arena edge stones (DS3: circular hollow pit)
    fill_tiles(chunk, TILE_WALL, 80, 96, 82, 98)
    fill_tiles(chunk, TILE_WALL, 98, 102, 100, 104)
    fill_tiles(chunk, TILE_WALL, 84, 116, 86, 118)
    fill_tiles(chunk, TILE_WALL, 92, 112, 94, 114)
    # Lift area — stone shaft walls (DS3: elevator shaft to Road of Sacrifices)
    fill_tiles(chunk, TILE_WALL, 141, 46, 143, 48)
    fill_tiles(chunk, TILE_WALL, 151, 52, 153, 54)
    # Sewer tunnel details (DS3: underground sewer with rats)
    fill_tiles(chunk, TILE_WALL, 76, 74, 78, 76)
    fill_tiles(chunk, TILE_WALL, 82, 72, 84, 74)
    fill_tiles(chunk, TILE_WALL, 72, 70, 74, 72)
    # SESSION 10 FIDELITY PASS — Undead Settlement
    # Additional DS3-faithful terrain: thatched roof debris, bonfire well stones,
    # dead tree roots, Greatwood arena debris, Evangelist house stones
    # Entry area — cliff path debris (DS3: narrow cliff path from High Wall)
    fill_tiles(chunk, TILE_WALL, 18, 22, 19, 23)
    fill_tiles(chunk, TILE_WALL, 24, 26, 25, 27)
    fill_tiles(chunk, TILE_WALL, 30, 24, 31, 25)
    # First house — thatched roof debris (DS3: houses with thatched roofs)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 31)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    fill_tiles(chunk, TILE_WALL, 44, 32, 45, 33)
    # Bonfire well — well stones (DS3: well near Dilapidated Bridge bonfire)
    fill_tiles(chunk, TILE_WALL, 50, 38, 51, 39)
    fill_tiles(chunk, TILE_WALL, 56, 42, 57, 43)
    fill_tiles(chunk, TILE_WALL, 52, 44, 53, 45)
    fill_tiles(chunk, TILE_WALL, 48, 40, 49, 41)
    # Evangelist house — wall debris (DS3: Evangelists patrol houses)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 47)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 51)
    fill_tiles(chunk, TILE_WALL, 64, 52, 65, 53)
    fill_tiles(chunk, TILE_WALL, 72, 48, 73, 49)
    # Pit area — cage and tree debris (DS3: pit with cages and dead trees)
    fill_tiles(chunk, TILE_WALL, 78, 56, 79, 57)
    fill_tiles(chunk, TILE_WALL, 84, 60, 85, 61)
    fill_tiles(chunk, TILE_WALL, 76, 58, 77, 59)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 63)
    # Greatwood arena — arena debris (DS3: Greatwood arena with debris)
    fill_tiles(chunk, TILE_WALL, 88, 66, 89, 67)
    fill_tiles(chunk, TILE_WALL, 94, 70, 95, 71)
    fill_tiles(chunk, TILE_WALL, 90, 72, 91, 73)
    fill_tiles(chunk, TILE_WALL, 96, 68, 97, 69)
    fill_tiles(chunk, TILE_WALL, 86, 70, 87, 71)
    # Sewer area — wet debris (DS3: sewers beneath settlement)
    fill_tiles(chunk, TILE_WALL, 100, 74, 101, 75)
    fill_tiles(chunk, TILE_WALL, 106, 78, 107, 79)
    fill_tiles(chunk, TILE_WALL, 102, 76, 103, 77)
    # Tower path — stone steps (DS3: tower with Giant Archer)
    fill_tiles(chunk, TILE_WALL, 112, 82, 113, 83)
    fill_tiles(chunk, TILE_WALL, 118, 86, 119, 87)
    fill_tiles(chunk, TILE_WALL, 116, 84, 117, 85)
    # Dead tree area — tree root debris (DS3: dead trees near Greatwood)
    fill_tiles(chunk, TILE_WALL, 92, 64, 93, 65)
    fill_tiles(chunk, TILE_WALL, 80, 68, 81, 69)
    fill_tiles(chunk, TILE_WALL, 98, 72, 99, 73)


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
    # DS3: winding path through dark forest with multiple Corvian ambushes
    # ================================================================
    carve_ellipse(chunk, 18, 18, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 14, 16, 40, 28)
    # Tree root obstacles
    fill_tiles(chunk, TILE_WALL, 20, 20, 22, 22)
    fill_tiles(chunk, TILE_WALL, 32, 24, 34, 26)
    # Additional tree clusters (DS3: dense dark woods at entry)
    fill_tiles(chunk, TILE_WALL, 16, 16, 17, 18)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 24)
    fill_tiles(chunk, TILE_WALL, 36, 18, 37, 20)
    fill_tiles(chunk, TILE_WALL, 28, 26, 29, 28)

    # ================================================================
    # SECTION 2: Halfway Fortress - doc: x=1000,y=500,w=500,h=500
    # Ruined stone fortress with Anri and Horace, interior rooms
    # DS3: stone ruin with bonfire room, Anri and Horace sitting inside
    # ================================================================
    carve_ellipse(chunk, 52, 28, 12, 10)
    # Stone walls creating fortress rooms
    fill_tiles(chunk, TILE_WALL, 48, 24, 49, 30)
    fill_tiles(chunk, TILE_WALL, 56, 26, 57, 32)
    # Fortress doorway pillars (DS3: arched stone entry)
    fill_tiles(chunk, TILE_WALL, 46, 26, 47, 28)
    fill_tiles(chunk, TILE_WALL, 58, 28, 59, 30)
    # Interior wall divider (DS3: room partition)
    fill_tiles(chunk, TILE_WALL, 50, 30, 54, 31)
    # Corridor connecting entry to fortress
    fill_tiles(chunk, TILE_GROUND, 38, 22, 52, 30)

    # ================================================================
    # SECTION 3: Crucifixion Woods - doc: x=1700,y=300,w=600,h=500
    # Wide wetland forest with branching paths, large central hub
    # DS3: sprawling wetland with shallow water, fallen trees, ruin walls
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 50, 35, 110, 75)
    # Large tree root clusters as wall obstacles
    fill_tiles(chunk, TILE_WALL, 58, 42, 62, 46)
    fill_tiles(chunk, TILE_WALL, 78, 50, 82, 54)
    fill_tiles(chunk, TILE_WALL, 95, 40, 99, 44)
    fill_tiles(chunk, TILE_WALL, 68, 62, 72, 66)
    fill_tiles(chunk, TILE_WALL, 88, 65, 92, 69)
    # Additional forest detail (DS3: scattered ruins and fallen trees)
    fill_tiles(chunk, TILE_WALL, 52, 38, 54, 40)
    fill_tiles(chunk, TILE_WALL, 64, 50, 66, 52)
    fill_tiles(chunk, TILE_WALL, 85, 45, 87, 47)
    fill_tiles(chunk, TILE_WALL, 102, 55, 104, 57)
    fill_tiles(chunk, TILE_WALL, 74, 70, 76, 72)
    # Ruined stone wall (DS3: collapsed wall section in woods)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 58)
    fill_tiles(chunk, TILE_WALL, 92, 58, 94, 60)
    # Fallen tree trunks
    fill_tiles(chunk, TILE_WALL, 108, 48, 110, 50)
    fill_tiles(chunk, TILE_WALL, 62, 68, 64, 70)

    # ================================================================
    # SECTION 4: Corvian Forest - doc: x=2200,y=800,w=600,h=600
    # Dense forest toward Crystal Sage, Black Knight patrols here
    # DS3: path narrows through dense trees with Corvian ambushes
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 75, 130, 110)
    # Dense tree clusters
    fill_tiles(chunk, TILE_WALL, 95, 82, 98, 85)
    fill_tiles(chunk, TILE_WALL, 115, 90, 118, 93)
    fill_tiles(chunk, TILE_WALL, 100, 100, 103, 103)
    fill_tiles(chunk, TILE_WALL, 120, 78, 123, 81)
    # Additional dense tree walls (DS3: very dense forest section)
    fill_tiles(chunk, TILE_WALL, 88, 76, 90, 78)
    fill_tiles(chunk, TILE_WALL, 105, 85, 107, 87)
    fill_tiles(chunk, TILE_WALL, 125, 95, 127, 97)
    fill_tiles(chunk, TILE_WALL, 92, 95, 94, 97)
    fill_tiles(chunk, TILE_WALL, 110, 105, 112, 107)

    # ================================================================
    # SECTION 5: Crystal Sage cave - doc: x=2300,y=1200,w=800,h=600
    # Boss arena: open rocky cave with crystal obstacles
    # DS3: open arena with crystal growths and ruined pillars
    # ================================================================
    carve_ellipse(chunk, 130, 120, 20, 18)
    # Crystal obstacles inside the cave
    fill_tiles(chunk, TILE_WALL, 122, 114, 124, 116)
    fill_tiles(chunk, TILE_WALL, 138, 126, 140, 128)
    fill_tiles(chunk, TILE_WALL, 125, 130, 127, 132)
    # Additional crystal growths (DS3: scattered crystal formations)
    fill_tiles(chunk, TILE_WALL, 130, 115, 132, 117)
    fill_tiles(chunk, TILE_WALL, 118, 122, 120, 124)
    fill_tiles(chunk, TILE_WALL, 142, 118, 144, 120)
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

    # ================================================================
    # ADDITIONAL DS3 ROAD OF SACRIFICES — forest depth, ruin details
    # ================================================================
    # Entry dark woods — more tree clusters (DS3: dense dark forest with Corvians)
    fill_tiles(chunk, TILE_WALL, 18, 22, 19, 24)
    fill_tiles(chunk, TILE_WALL, 30, 18, 31, 20)
    fill_tiles(chunk, TILE_WALL, 22, 26, 23, 28)
    fill_tiles(chunk, TILE_WALL, 34, 22, 35, 24)
    # Halfway Fortress — more interior walls (DS3: multi-room stone ruin)
    fill_tiles(chunk, TILE_WALL, 44, 28, 45, 32)
    fill_tiles(chunk, TILE_WALL, 60, 30, 61, 34)
    fill_tiles(chunk, TILE_WALL, 50, 34, 52, 36)
    fill_tiles(chunk, TILE_WALL, 55, 24, 56, 26)
    # Crucifixion Woods — more wetland detail (DS3: sprawling marsh with ruins)
    fill_tiles(chunk, TILE_WALL, 56, 42, 57, 44)
    fill_tiles(chunk, TILE_WALL, 70, 48, 71, 50)
    fill_tiles(chunk, TILE_WALL, 80, 55, 81, 57)
    fill_tiles(chunk, TILE_WALL, 98, 48, 99, 50)
    fill_tiles(chunk, TILE_WALL, 65, 56, 66, 58)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 64)
    fill_tiles(chunk, TILE_WALL, 105, 60, 106, 62)
    fill_tiles(chunk, TILE_WALL, 75, 72, 76, 74)
    fill_tiles(chunk, TILE_WALL, 58, 65, 59, 67)
    # Corvian Forest — additional dense trees (DS3: very thick forest near Crystal Sage)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 82)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 90)
    fill_tiles(chunk, TILE_WALL, 112, 95, 113, 97)
    fill_tiles(chunk, TILE_WALL, 118, 82, 119, 84)
    fill_tiles(chunk, TILE_WALL, 96, 98, 97, 100)
    fill_tiles(chunk, TILE_WALL, 108, 102, 109, 104)
    fill_tiles(chunk, TILE_WALL, 128, 88, 129, 90)
    # Crystal Sage cave — more crystal formations (DS3: crystal growths everywhere)
    fill_tiles(chunk, TILE_WALL, 126, 118, 127, 120)
    fill_tiles(chunk, TILE_WALL, 134, 124, 135, 126)
    fill_tiles(chunk, TILE_WALL, 140, 114, 141, 116)
    fill_tiles(chunk, TILE_WALL, 122, 128, 123, 130)
    fill_tiles(chunk, TILE_WALL, 136, 130, 137, 132)
    # Farron Keep branch — swamp approach ruins (DS3: crumbling path to poison swamp)
    fill_tiles(chunk, TILE_WALL, 64, 78, 65, 80)
    fill_tiles(chunk, TILE_WALL, 70, 85, 71, 87)
    fill_tiles(chunk, TILE_WALL, 66, 95, 67, 97)
    fill_tiles(chunk, TILE_WALL, 72, 105, 73, 107)
    fill_tiles(chunk, TILE_WALL, 68, 115, 69, 117)
    # Cathedral branch — stone gate approach (DS3: path to Cathedral of the Deep)
    fill_tiles(chunk, TILE_WALL, 110, 62, 111, 64)
    fill_tiles(chunk, TILE_WALL, 115, 66, 116, 68)

    # ================================================================
    # SESSION 9 FIDELITY PASS — RoadOfSacrifices architectural details
    # ================================================================
    # Entry forest path — mossy root clusters (DS3: forest with exposed roots)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 19)
    fill_tiles(chunk, TILE_WALL, 26, 22, 27, 23)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 27)
    fill_tiles(chunk, TILE_WALL, 30, 16, 31, 17)
    # Halfway Fortress — collapsed stone arch (DS3: ruined fortress bridge)
    fill_tiles(chunk, TILE_WALL, 48, 28, 49, 29)
    fill_tiles(chunk, TILE_WALL, 52, 32, 53, 33)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 37)
    fill_tiles(chunk, TILE_WALL, 56, 26, 57, 27)
    fill_tiles(chunk, TILE_WALL, 50, 38, 51, 39)
    # Crucifixion Woods — crucified hollow posts (DS3: hollows crucified on trees)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 43)
    fill_tiles(chunk, TILE_WALL, 68, 46, 69, 47)
    fill_tiles(chunk, TILE_WALL, 60, 50, 61, 51)
    fill_tiles(chunk, TILE_WALL, 72, 40, 73, 41)
    fill_tiles(chunk, TILE_WALL, 66, 52, 67, 53)
    # Wetland shallows — submerged stone paths (DS3: flooded forest area)
    fill_tiles(chunk, TILE_WALL, 76, 56, 77, 57)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 72, 64, 73, 65)
    fill_tiles(chunk, TILE_WALL, 84, 54, 85, 55)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    # Black Knight ruins — ruined arch stones (DS3: Black Knight patrols ruins)
    fill_tiles(chunk, TILE_WALL, 88, 70, 89, 71)
    fill_tiles(chunk, TILE_WALL, 92, 74, 93, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    fill_tiles(chunk, TILE_WALL, 96, 68, 97, 69)
    # Corvian forest — fallen nest structures (DS3: Corvians in trees)
    fill_tiles(chunk, TILE_WALL, 100, 82, 101, 83)
    fill_tiles(chunk, TILE_WALL, 104, 86, 105, 87)
    fill_tiles(chunk, TILE_WALL, 96, 90, 97, 91)
    fill_tiles(chunk, TILE_WALL, 108, 80, 109, 81)
    fill_tiles(chunk, TILE_WALL, 102, 92, 103, 93)
    # Crystal Sage cave — crystal-encrusted pillars (DS3: crystal formations)
    fill_tiles(chunk, TILE_WALL, 112, 96, 113, 97)
    fill_tiles(chunk, TILE_WALL, 116, 100, 117, 101)
    fill_tiles(chunk, TILE_WALL, 108, 104, 109, 105)
    fill_tiles(chunk, TILE_WALL, 120, 94, 121, 95)
    fill_tiles(chunk, TILE_WALL, 114, 106, 115, 107)
    # Farron approach — mossy stone gate arch (DS3: stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 124, 110, 125, 111)
    fill_tiles(chunk, TILE_WALL, 128, 114, 129, 115)
    fill_tiles(chunk, TILE_WALL, 120, 118, 121, 119)
    fill_tiles(chunk, TILE_WALL, 132, 108, 133, 109)

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

    # Enemies - DS3 faithful: Corvians (many throughout forest), Lycanthropes,
    # Corvian Storytellers, Black Knight, Exiles, Crabs, Crystal Lizards
    enemy_data = [
        # Entry dark woods — Corvians (winged hollows) patrolling the path
        ("Corvian", 25, 20), ("Corvian", 35, 24),
        ("Dog", 28, 22),                                          # Dogs ambush near entry
        # Near Halfway Fortress — Lycanthropes (DS3: "two Lycanthropes" at fortress entrance)
        ("StarvedHound", 42, 26), ("StarvedHound", 48, 28),
        ("StarvedHound", 45, 32),                                 # DS3: third Lycanthrope nearby
        # Crucifixion Woods — DS3: Corvians everywhere in the woods, multiple groups
        ("Corvian", 56, 35), ("Corvian", 62, 40),               # Corvians in woods
        ("DarkMage", 70, 48),                                      # Corvian Storyteller (casts poison mist)
        ("DarkMage", 88, 55),                                      # Corvian Storyteller
        ("Corvian", 75, 52), ("Corvian", 82, 58),               # More Corvians
        ("Corvian", 65, 45), ("Corvian", 78, 48),               # Additional Corvians deeper in woods
        ("Corvian", 90, 50), ("Corvian", 58, 55),               # Corvians near crosses
        ("LycanthropeHunter", 72, 55), ("LycanthropeHunter", 85, 60),                   # DS3: Lycanthrope Hunters (spear wielders)
        ("CrystalLizard", 50, 26),                                 # Fortress crystal lizard
        ("CrystalLizard", 96, 62), ("CrystalLizard", 112, 88),    # Additional Crystal Lizards in ruins
        # Swamp area — Poisonhorn Bugs (poison mist mushrooms in lower woods)
        ("PoisonhornBug", 65, 62), ("PoisonhornBug", 70, 65),
        ("PoisonhornBug", 62, 70), ("PoisonhornBug", 58, 68),
        # Swamp area — Lesser Crabs and Great Crab
        ("GreatCrab", 76, 70),                                    # Great Crab in swamp (drops Great Swamp Ring)
        ("LesserCrab", 78, 68), ("LesserCrab", 80, 72),                    # Lesser Crabs in swamp
        # Black Knight guarding Farron Coal in ruins (DS3: "Black Knight in the ruins")
        ("BlackKnight", 108, 85),
        # Corvian forest — DS3: "dense forest with Corvians"
        ("Corvian", 118, 88), ("Corvian", 122, 92), ("Corvian", 125, 96),
        ("Corvian", 112, 82), ("Corvian", 128, 85),             # More Corvians in deep forest
        # Crystal Sage cave — hollow sorcerers
        ("DarkMage", 125, 115), ("DarkMage", 135, 118),
        # South path toward Farron Keep — DS3: Exile NPCs guard the Farron Keep gate
        ("Corvian", 68, 80), ("Corvian", 72, 85),
        ("StarvedHound", 110, 95), ("StarvedHound", 115, 100),    # Lycanthropes
        ("Archer", 100, 78), ("Archer", 120, 82),                 # Corvian archers
        # Exiles at Farron Keep gate (DS3: "two Exiles" guarding the gate with great weapons)
        ("DarkSpirit", 108, 100), ("DarkSpirit", 115, 105),    # DS3: Exiles guarding Farron Keep gate
        # Boss — Crystal Sage
        ("MiniBoss", 130, 112),                                     # Crystal Sage boss entity
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Road of Sacrifices) — accurate from wiki ---
    # Shriving Stone — end of left path in entry woods
    entities.append(make_entity("Item", 30 * 16, 22 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Blue Bug Pellet")]))
    # Blue Bug Pellet — second pellet in ruins
    entities.append(make_entity("Item", 88 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    # Green Blossom — swamp area near crabs
    entities.append(make_entity("Item", 80 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    # Green Blossom — swamp area
    entities.append(make_entity("Item", 72 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    # Green Blossom — swamp area
    entities.append(make_entity("Item", 85 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
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
    entities.append(make_entity("Npc", 50 * 16, 30 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Oh, hello. I am Anri of Astora|This is Horace the Hushed|We are travelling to find the Lords of Cinder|Won't you join us on our journey?")]))
    entities.append(make_entity("Npc", 54 * 16, 30 * 16, [make_field("name", "String", "Horace the Hushed"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#606060"), make_field("dialogue", "String", "...|(nods silently)|(gestures toward Anri)")]))

    # Orbeck of Vinheim — sorcery teacher in the ruins (DS3: found in a side room of the Crucifixion Woods ruins)
    entities.append(make_entity("Npc", 82 * 16, 60 * 16, [make_field("name", "String", "Orbeck of Vinheim"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#7090B0"), make_field("dialogue", "String", "I am Orbeck of Vinheim. A sorcerer, and an assassin|I wish to repay my debt to you|Bring me scrolls, and I shall teach you their sorceries")]))

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

    # === ADDITIONAL INTERNAL STRUCTURES — Road of Sacrifices DS3 fidelity ===
    # Entry dark woods — additional tree root clusters (DS3: dense forest entry)
    fill_tiles(chunk, TILE_WALL, 22, 25, 24, 28)
    fill_tiles(chunk, TILE_WALL, 38, 28, 40, 30)
    fill_tiles(chunk, TILE_WALL, 55, 22, 57, 24)
    fill_tiles(chunk, TILE_WALL, 30, 38, 32, 40)
    # Overturned coach debris (DS3: overturned carriage in entry path)
    fill_tiles(chunk, TILE_WALL, 26, 20, 28, 22)
    # Halfway Fortress — interior room partitions (DS3: stone ruin with multiple rooms)
    fill_tiles(chunk, TILE_WALL, 48, 42, 50, 44)
    fill_tiles(chunk, TILE_WALL, 65, 35, 67, 37)
    fill_tiles(chunk, TILE_WALL, 53, 28, 55, 30)
    fill_tiles(chunk, TILE_WALL, 46, 32, 48, 34)
    # Crucifixion Woods — wetland forest debris (DS3: sprawling wetland with ruins)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 57)
    fill_tiles(chunk, TILE_WALL, 52, 58, 54, 60)
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 50)
    fill_tiles(chunk, TILE_WALL, 42, 68, 44, 70)
    fill_tiles(chunk, TILE_WALL, 60, 72, 62, 74)
    fill_tiles(chunk, TILE_WALL, 80, 55, 82, 57)
    # Fallen trees across shallow water (DS3: horizontal logs in swamp)
    fill_tiles(chunk, TILE_WALL, 56, 64, 58, 66)
    fill_tiles(chunk, TILE_WALL, 84, 62, 86, 64)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    # Crucifixion crosses debris (DS3: crosses scattered throughout the woods)
    fill_tiles(chunk, TILE_WALL, 66, 42, 67, 44)
    fill_tiles(chunk, TILE_WALL, 78, 52, 79, 54)
    fill_tiles(chunk, TILE_WALL, 90, 46, 91, 48)
    # Ruined stone structure walls (DS3: Black Knight patrols these ruins)
    fill_tiles(chunk, TILE_WALL, 25, 78, 27, 80)
    fill_tiles(chunk, TILE_WALL, 90, 65, 92, 67)
    fill_tiles(chunk, TILE_WALL, 104, 78, 106, 82)
    fill_tiles(chunk, TILE_WALL, 112, 84, 114, 88)
    # Farron Keep gate fortress ruins (DS3: stone gate with Exile guards)
    fill_tiles(chunk, TILE_WALL, 66, 125, 70, 128)
    fill_tiles(chunk, TILE_WALL, 72, 130, 76, 133)
    fill_tiles(chunk, TILE_WALL, 64, 118, 66, 120)
    # Corvian forest dense trees (DS3: dense forest path narrows significantly)
    fill_tiles(chunk, TILE_WALL, 118, 102, 120, 104)
    fill_tiles(chunk, TILE_WALL, 135, 108, 137, 110)
    fill_tiles(chunk, TILE_WALL, 125, 115, 127, 118)
    fill_tiles(chunk, TILE_WALL, 96, 92, 98, 94)
    fill_tiles(chunk, TILE_WALL, 130, 95, 132, 98)
    fill_tiles(chunk, TILE_WALL, 116, 88, 118, 90)
    # Crystal Sage cave crystal formations (DS3: scattered crystal growths in boss arena)
    fill_tiles(chunk, TILE_WALL, 134, 120, 136, 122)
    fill_tiles(chunk, TILE_WALL, 122, 128, 124, 130)
    fill_tiles(chunk, TILE_WALL, 140, 114, 142, 116)
    # Cathedral road — dense tree walls (DS3: forest path to Cathedral of the Deep)
    fill_tiles(chunk, TILE_WALL, 114, 62, 116, 64)
    fill_tiles(chunk, TILE_WALL, 108, 68, 110, 70)
    # Orbeck's room interior (DS3: small side room in ruins with bookshelves)
    fill_tiles(chunk, TILE_WALL, 80, 58, 82, 60)
    fill_tiles(chunk, TILE_WALL, 84, 62, 86, 64)

    # === SESSION 8 FIDELITY PASS — Road of Sacrifices ===
    # Entry woods — mossy root clusters and fungus-covered stones (DS3: dark forest floor)
    fill_tiles(chunk, TILE_WALL, 14, 14, 15, 16)
    fill_tiles(chunk, TILE_WALL, 40, 16, 41, 18)
    fill_tiles(chunk, TILE_WALL, 26, 28, 27, 30)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 32)
    # Halfway Fortress — collapsed stone arch fragments (DS3: ruined stone tower)
    fill_tiles(chunk, TILE_WALL, 42, 26, 43, 28)
    fill_tiles(chunk, TILE_WALL, 62, 32, 63, 34)
    fill_tiles(chunk, TILE_WALL, 48, 36, 49, 38)
    # Crucifixion Woods — crucified hollow posts (DS3: multiple crucified corpses in woods)
    fill_tiles(chunk, TILE_WALL, 60, 38, 61, 40)
    fill_tiles(chunk, TILE_WALL, 84, 52, 85, 54)
    fill_tiles(chunk, TILE_WALL, 68, 54, 69, 56)
    fill_tiles(chunk, TILE_WALL, 92, 56, 93, 58)
    # Wetland shallows — submerged stone paths (DS3: shallow water with stepping stones)
    fill_tiles(chunk, TILE_WALL, 64, 66, 65, 68)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 70)
    fill_tiles(chunk, TILE_WALL, 70, 74, 71, 76)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 72)
    # Black Knight ruins — more ruined arch stones (DS3: stone ruin with Black Knight)
    fill_tiles(chunk, TILE_WALL, 106, 82, 107, 84)
    fill_tiles(chunk, TILE_WALL, 114, 86, 115, 88)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 92)
    # Corvian forest — fallen nest structures (DS3: Corvian nests in trees)
    fill_tiles(chunk, TILE_WALL, 122, 78, 123, 80)
    fill_tiles(chunk, TILE_WALL, 130, 92, 131, 94)
    fill_tiles(chunk, TILE_WALL, 114, 100, 115, 102)
    fill_tiles(chunk, TILE_WALL, 134, 102, 135, 104)
    # Crystal Sage cave — crystal-encrusted pillars (DS3: glowing crystal formations)
    fill_tiles(chunk, TILE_WALL, 132, 112, 133, 114)
    fill_tiles(chunk, TILE_WALL, 124, 134, 125, 136)
    fill_tiles(chunk, TILE_WALL, 138, 128, 139, 130)
    # Farron approach — mossy stone gate arch (DS3: stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 62, 122, 63, 124)
    fill_tiles(chunk, TILE_WALL, 74, 128, 75, 130)
    # SESSION 10 FIDELITY PASS — Road of Sacrifices
    # Additional DS3-faithful terrain: mossy root clusters, crucified hollow posts,
    # wetland submerged path edges, crystal pillar formations, ruin debris
    # Entry dark woods — root cluster debris (DS3: dark forest with exposed roots)
    fill_tiles(chunk, TILE_WALL, 20, 20, 21, 21)
    fill_tiles(chunk, TILE_WALL, 24, 24, 25, 25)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    fill_tiles(chunk, TILE_WALL, 16, 26, 17, 27)
    # Halfway Fortress — fortress wall debris (DS3: small fortress at midpoint)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 31)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    fill_tiles(chunk, TILE_WALL, 44, 32, 45, 33)
    # Crucifixion Woods — crucified hollow posts (DS3: crucified hollows on trees)
    fill_tiles(chunk, TILE_WALL, 52, 38, 53, 39)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 43)
    fill_tiles(chunk, TILE_WALL, 54, 44, 55, 45)
    fill_tiles(chunk, TILE_WALL, 60, 40, 61, 41)
    fill_tiles(chunk, TILE_WALL, 66, 38, 67, 39)
    # Wetland area — submerged path edges (DS3: flooded paths in woods)
    fill_tiles(chunk, TILE_WALL, 72, 46, 73, 47)
    fill_tiles(chunk, TILE_WALL, 78, 50, 79, 51)
    fill_tiles(chunk, TILE_WALL, 76, 52, 77, 53)
    fill_tiles(chunk, TILE_WALL, 82, 48, 83, 49)
    fill_tiles(chunk, TILE_WALL, 68, 54, 69, 55)
    # Crystal Sage area — crystal pillar formations (DS3: crystals near boss)
    fill_tiles(chunk, TILE_WALL, 108, 80, 109, 81)
    fill_tiles(chunk, TILE_WALL, 114, 84, 115, 85)
    fill_tiles(chunk, TILE_WALL, 120, 82, 121, 83)
    fill_tiles(chunk, TILE_WALL, 126, 86, 127, 87)
    fill_tiles(chunk, TILE_WALL, 110, 88, 111, 89)
    fill_tiles(chunk, TILE_WALL, 118, 90, 119, 91)
    # Corvian forest — fallen tree debris (DS3: dense forest with fallen trees)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)
    fill_tiles(chunk, TILE_WALL, 94, 66, 95, 67)
    fill_tiles(chunk, TILE_WALL, 100, 64, 101, 65)
    fill_tiles(chunk, TILE_WALL, 84, 68, 85, 69)
    fill_tiles(chunk, TILE_WALL, 92, 70, 93, 71)
    # Farron Keep gate — ruin wall debris (DS3: stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 104, 96, 105, 97)
    fill_tiles(chunk, TILE_WALL, 110, 100, 111, 101)
    fill_tiles(chunk, TILE_WALL, 106, 102, 107, 103)
    fill_tiles(chunk, TILE_WALL, 116, 98, 117, 99)


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
    # DS3: narrow stone path descending from Road of Sacrifices into the poison swamp
    # ================================================================
    carve_ellipse(chunk, 15, 18, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 20, 25, 35)
    # Broken stone wall at entry
    fill_tiles(chunk, TILE_WALL, 10, 14, 12, 16)
    # Entry path stones (DS3: stone steps down into swamp)
    fill_tiles(chunk, TILE_WALL, 16, 22, 18, 24)
    fill_tiles(chunk, TILE_WALL, 20, 28, 22, 30)

    # ================================================================
    # SECTION 2: Outer poison swamp - vast POISON area
    # Three torch platforms scattered across the swamp
    # DS3: massive poison swamp with three stone platforms holding flame altars
    # ================================================================
    carve_ellipse(chunk, 70, 70, 52, 48)
    # Convert much of the center to POISON tiles
    fill_tiles(chunk, TILE_POISON, 25, 35, 120, 110)

    # Left torch platform (NW) - doc: x=600,y=400,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 30, 30, 45, 42)
    fill_tiles(chunk, TILE_WALL, 34, 34, 36, 36)
    # Torch altar wall (DS3: stone platform with flame)
    fill_tiles(chunk, TILE_WALL, 36, 36, 38, 38)
    # Rubble on platform edge
    fill_tiles(chunk, TILE_WALL, 30, 38, 32, 40)

    # Center torch platform (N) - doc: x=1600,y=800,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 60, 42, 78, 55)
    fill_tiles(chunk, TILE_WALL, 66, 46, 68, 48)
    # Torch altar stone
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 50)
    # Rubble edges
    fill_tiles(chunk, TILE_WALL, 60, 50, 62, 52)
    fill_tiles(chunk, TILE_WALL, 75, 44, 77, 46)

    # Right torch platform (NE) - doc: x=2400,y=600,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 88, 35, 105, 48)
    fill_tiles(chunk, TILE_WALL, 94, 38, 96, 40)
    # Torch altar
    fill_tiles(chunk, TILE_WALL, 100, 42, 102, 44)
    # Rubble edges
    fill_tiles(chunk, TILE_WALL, 88, 44, 90, 46)
    fill_tiles(chunk, TILE_WALL, 103, 36, 105, 38)

    # Path from entry into swamp (poison corridor)
    fill_tiles(chunk, TILE_POISON, 22, 30, 35, 45)
    # Scattered rubble in swamp (DS3: sunken ruins visible in poison water)
    fill_tiles(chunk, TILE_WALL, 48, 40, 49, 42)
    fill_tiles(chunk, TILE_WALL, 55, 48, 56, 50)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 54)
    fill_tiles(chunk, TILE_WALL, 42, 55, 43, 57)
    fill_tiles(chunk, TILE_WALL, 75, 38, 76, 40)

    # ================================================================
    # SECTION 3: Keep Ruins (center) - doc: x=1800,y=1600,w=500,h=400
    # Solid ground island with ruined walls, central bonfire hub
    # DS3: stone ruin island with crumbling walls, bonfire inside
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 60, 60, 85, 80)
    fill_tiles(chunk, TILE_WALL, 65, 65, 68, 68)
    fill_tiles(chunk, TILE_WALL, 78, 72, 81, 75)
    fill_tiles(chunk, TILE_WALL, 70, 74, 72, 76)
    # Additional ruin walls (DS3: Keep Ruins has multiple broken walls)
    fill_tiles(chunk, TILE_WALL, 62, 70, 64, 73)
    fill_tiles(chunk, TILE_WALL, 80, 62, 82, 65)
    fill_tiles(chunk, TILE_WALL, 74, 78, 76, 80)
    fill_tiles(chunk, TILE_WALL, 83, 68, 85, 70)

    # ================================================================
    # SECTION 4: Old Wolf tower (south) - doc: x=1000,y=2200,w=400,h=500
    # High tower ruin accessed via ladder, covenant area
    # DS3: tall stone tower with the Old Wolf of Farron covenant
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 35, 95, 55, 115)
    carve_ellipse(chunk, 45, 105, 8, 7)
    # Tower walls
    fill_tiles(chunk, TILE_WALL, 38, 100, 40, 102)
    fill_tiles(chunk, TILE_WALL, 50, 108, 52, 110)
    # Tower base detail (DS3: stone tower with ladder access)
    fill_tiles(chunk, TILE_WALL, 36, 108, 38, 112)
    fill_tiles(chunk, TILE_WALL, 52, 96, 54, 100)

    # ================================================================
    # SECTION 5: Basilisk curse cave (west) - doc: x=400,y=1600,w=400,h=400
    # Dark cave with basilisks, hidden treasure
    # DS3: enclosed cave with multiple basilisks that cause curse
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 65, 38, 82)
    carve_ellipse(chunk, 28, 72, 7, 6)
    # Cave stalagmites (DS3: dark cave with stone formations)
    fill_tiles(chunk, TILE_WALL, 22, 68, 24, 70)
    fill_tiles(chunk, TILE_WALL, 34, 76, 36, 78)
    fill_tiles(chunk, TILE_WALL, 26, 78, 28, 80)

    # ================================================================
    # SECTION 6: Darkwraith patrol zone (SE) - doc: x=2200,y=2000,w=600,h=600
    # Abyss knights patrol between swamp and boss arena approach
    # DS3: Darkwraiths emerge from the swamp water and fight Ghrus
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 95, 80, 120, 105)
    fill_tiles(chunk, TILE_POISON, 98, 85, 115, 100)
    # Ruined stone structures in Darkwraith zone
    fill_tiles(chunk, TILE_WALL, 100, 88, 102, 92)
    fill_tiles(chunk, TILE_WALL, 110, 95, 112, 98)
    fill_tiles(chunk, TILE_WALL, 95, 98, 97, 102)

    # ================================================================
    # SECTION 7: Grand stone gate corridor - doc: x=2800,y=2400,w=300,h=400
    # Long corridor lined with Abyss Watcher armor
    # DS3: grand stone hallway with wolf-crested walls
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 120, 80, 135, 105)
    # Corridor walls (DS3: stone walls with Abyss Watcher insignia)
    fill_tiles(chunk, TILE_WALL, 120, 85, 122, 90)
    fill_tiles(chunk, TILE_WALL, 132, 95, 134, 100)
    fill_tiles(chunk, TILE_WALL, 125, 88, 127, 92)

    # ================================================================
    # SECTION 8: Abyss Watchers grand hall (far right) - doc: x=3000,y=2600,w=800,h=800
    # Large boss arena - grand stone hall with wolf crest
    # DS3: massive stone hall where Abyss Watchers fight among themselves
    # ================================================================
    carve_ellipse(chunk, 140, 115, 18, 16)
    fill_tiles(chunk, TILE_GROUND, 128, 105, 155, 130)
    # Arena pillars (DS3: grand stone columns in the hall)
    fill_tiles(chunk, TILE_WALL, 132, 110, 134, 114)
    fill_tiles(chunk, TILE_WALL, 145, 118, 147, 122)
    fill_tiles(chunk, TILE_WALL, 138, 108, 140, 110)
    fill_tiles(chunk, TILE_WALL, 150, 112, 152, 115)
    # Arena wall sections (DS3: stone walls framing the boss room)
    fill_tiles(chunk, TILE_WALL, 128, 120, 130, 124)
    fill_tiles(chunk, TILE_WALL, 152, 108, 154, 112)

    # Connection corridors
    fill_tiles(chunk, TILE_GROUND, 55, 80, 65, 95)   # Ruins to Old Wolf
    fill_tiles(chunk, TILE_GROUND, 82, 75, 100, 85)   # Ruins to Darkwraith zone
    fill_tiles(chunk, TILE_GROUND, 115, 100, 128, 112) # Gate to arena

    # ================================================================
    # ADDITIONAL DS3 FARRON KEEP — swamp details, ruin depth
    # ================================================================
    # Entry path — more stone steps (DS3: descent into poison swamp)
    fill_tiles(chunk, TILE_WALL, 12, 18, 13, 20)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 28)
    fill_tiles(chunk, TILE_WALL, 14, 30, 15, 32)
    # Left torch platform — additional rubble (DS3: stone ruin with flame altar)
    fill_tiles(chunk, TILE_WALL, 32, 32, 33, 34)
    fill_tiles(chunk, TILE_WALL, 40, 38, 41, 40)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 32)
    # Center torch platform — more altar stones (DS3: stone platform with Ghru)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 46)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 52)
    fill_tiles(chunk, TILE_WALL, 68, 52, 69, 54)
    # Right torch platform — debris (DS3: Ghru-infested torch platform)
    fill_tiles(chunk, TILE_WALL, 92, 40, 93, 42)
    fill_tiles(chunk, TILE_WALL, 98, 36, 99, 38)
    fill_tiles(chunk, TILE_WALL, 102, 44, 103, 46)
    # Poison swamp — sunken ruins (DS3: crumbled structures visible in swamp)
    fill_tiles(chunk, TILE_WALL, 46, 45, 47, 47)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 54)
    fill_tiles(chunk, TILE_WALL, 85, 48, 86, 50)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 60)
    fill_tiles(chunk, TILE_WALL, 68, 56, 69, 58)
    fill_tiles(chunk, TILE_WALL, 78, 44, 79, 46)
    fill_tiles(chunk, TILE_WALL, 90, 56, 91, 58)
    # Keep Ruins — more crumbled walls (DS3: central ruin island)
    fill_tiles(chunk, TILE_WALL, 66, 62, 67, 64)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 68)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 76)
    fill_tiles(chunk, TILE_WALL, 64, 76, 65, 78)
    # Old Wolf tower — tower stones (DS3: tall tower with covenant)
    fill_tiles(chunk, TILE_WALL, 40, 96, 41, 98)
    fill_tiles(chunk, TILE_WALL, 48, 102, 49, 104)
    fill_tiles(chunk, TILE_WALL, 42, 110, 43, 112)
    fill_tiles(chunk, TILE_WALL, 54, 98, 55, 100)
    # Basilisk cave — more stalagmites (DS3: dark curse cave)
    fill_tiles(chunk, TILE_WALL, 24, 72, 25, 74)
    fill_tiles(chunk, TILE_WALL, 32, 78, 33, 80)
    fill_tiles(chunk, TILE_WALL, 30, 66, 31, 68)
    # Darkwraith zone — more abyss ruins (DS3: dark knights emerge from swamp)
    fill_tiles(chunk, TILE_WALL, 98, 92, 99, 94)
    fill_tiles(chunk, TILE_WALL, 106, 90, 107, 92)
    fill_tiles(chunk, TILE_WALL, 112, 98, 113, 100)
    fill_tiles(chunk, TILE_WALL, 96, 102, 97, 104)
    # Grand gate corridor — wolf crest walls (DS3: Abyss Watcher hall)
    fill_tiles(chunk, TILE_WALL, 122, 82, 123, 84)
    fill_tiles(chunk, TILE_WALL, 130, 90, 131, 92)
    fill_tiles(chunk, TILE_WALL, 128, 98, 129, 100)
    fill_tiles(chunk, TILE_WALL, 134, 102, 135, 104)
    # Abyss Watchers arena — more grand columns (DS3: massive boss hall)
    fill_tiles(chunk, TILE_WALL, 136, 112, 137, 114)
    fill_tiles(chunk, TILE_WALL, 148, 114, 149, 116)
    fill_tiles(chunk, TILE_WALL, 130, 116, 131, 118)
    fill_tiles(chunk, TILE_WALL, 154, 118, 155, 120)

    # ================================================================
    # SESSION 9 FIDELITY PASS — FarronKeep architectural details
    # ================================================================
    # Swamp edge — rotting wooden posts (DS3: decayed fence posts along swamp)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 23)
    fill_tiles(chunk, TILE_WALL, 30, 16, 31, 17)
    # Ghru camp — bonfire stone ring (DS3: Ghru encampment with fire pit)
    fill_tiles(chunk, TILE_WALL, 36, 28, 37, 29)
    fill_tiles(chunk, TILE_WALL, 40, 32, 41, 33)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 35)
    # Great沼 swamp — submerged ruins (DS3: ruins visible above swamp water)
    fill_tiles(chunk, TILE_WALL, 60, 40, 61, 41)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 45)
    fill_tiles(chunk, TILE_WALL, 56, 48, 57, 49)
    fill_tiles(chunk, TILE_WALL, 68, 36, 69, 37)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 51)
    # Old Wolf of Farron tower — crumbling stairs (DS3: tower with wolf inside)
    fill_tiles(chunk, TILE_WALL, 90, 30, 91, 31)
    fill_tiles(chunk, TILE_WALL, 94, 34, 95, 35)
    fill_tiles(chunk, TILE_WALL, 86, 36, 87, 37)
    fill_tiles(chunk, TILE_WALL, 98, 28, 99, 29)
    # Abyss Watchers arena — broken greatswords (DS3: swords embedded in ground)
    fill_tiles(chunk, TILE_WALL, 120, 60, 121, 61)
    fill_tiles(chunk, TILE_WALL, 126, 64, 127, 65)
    fill_tiles(chunk, TILE_WALL, 132, 58, 133, 59)
    fill_tiles(chunk, TILE_WALL, 138, 62, 139, 63)
    fill_tiles(chunk, TILE_WALL, 116, 68, 117, 69)
    fill_tiles(chunk, TILE_WALL, 144, 66, 145, 67)
    # Grass-covered ruin arches (DS3: mossy stone arches throughout keep)
    fill_tiles(chunk, TILE_WALL, 42, 56, 43, 57)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    fill_tiles(chunk, TILE_WALL, 46, 64, 47, 65)
    fill_tiles(chunk, TILE_WALL, 54, 52, 55, 53)
    # Strangleroot clusters (DS3: dangerous root tendrils in swamp)
    fill_tiles(chunk, TILE_WALL, 66, 72, 67, 73)
    fill_tiles(chunk, TILE_WALL, 74, 68, 75, 69)
    fill_tiles(chunk, TILE_WALL, 70, 76, 71, 77)
    fill_tiles(chunk, TILE_WALL, 62, 80, 63, 81)
    # Keep perimeter — crumbling wall foundations (DS3: ruined fort walls)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 81)
    fill_tiles(chunk, TILE_WALL, 108, 84, 109, 85)
    fill_tiles(chunk, TILE_WALL, 104, 88, 105, 89)
    fill_tiles(chunk, TILE_WALL, 112, 76, 113, 77)
    # Farron Keep perimeter — darksign-tinged stones (DS3: abyss corruption visible)
    fill_tiles(chunk, TILE_WALL, 130, 100, 131, 101)
    fill_tiles(chunk, TILE_WALL, 136, 104, 137, 105)
    fill_tiles(chunk, TILE_WALL, 142, 96, 143, 97)
    fill_tiles(chunk, TILE_WALL, 148, 108, 149, 109)

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

    # Enemies - DS3 faithful: Ghru (swarm the swamp), Elder Ghru (elite horned beasts),
    # Darkwraiths (abyss knights), Basilisks (curse cave), Rotten Slugs (leeches everywhere),
    # Great Crabs, Corvians + Storyteller, Crystal Lizards (5-6 total), Ravenous Crystal Lizard
    enemy_data = [
        # Left torch area — Ghru swarm (DS3: groups of Ghru Grunts/Leapers throughout swamp)
        ("Ghru", 35, 45), ("Ghru", 40, 48), ("Ghru", 48, 50),
        ("Ghru", 33, 50), ("Ghru", 42, 55), ("Ghru", 46, 58),
        # Center torch area — more Ghru (DS3: crawling Ghru + Leaper near fire altar)
        ("Ghru", 68, 48), ("Ghru", 72, 52), ("Ghru", 75, 55),
        ("Ghru", 64, 55), ("Ghru", 70, 58),
        # Right torch area — Ghru Grunts with spears
        ("Ghru", 95, 42), ("Ghru", 100, 45), ("Ghru", 92, 48),
        ("Ghru", 98, 52), ("Ghru", 105, 50),
        # Keep Ruins — Ghru swarm + Ghru Shaman (DS3: "two Ghru Grunts + Shaman" at entrance)
        ("Ghru", 65, 72), ("Ghru", 72, 76), ("Ghru", 78, 70),
        ("Ghru", 68, 68), ("Ghru", 74, 65),
        ("DarkMage", 70, 74),                                        # Ghru Shaman (casts poison)
        # Darkwraith patrol — DS3: "first Darkwraith" on left path, one on stairs near boss,
        # one in second half wooded area, one fighting other enemies
        ("Darkwraith", 100, 88), ("Darkwraith", 108, 95),
        ("Darkwraith", 125, 108),                                    # Near arena gate (DS3: on stairs)
        ("Darkwraith", 88, 75),                                      # DS3: Darkwraith in second half wooded area
        ("Darkwraith", 115, 90),                                     # DS3: wraith fighting other enemies
        # Basilisk curse cave — DS3: "several basilisks" that cause curse
        ("Basilisk", 24, 70), ("Basilisk", 30, 75), ("Basilisk", 32, 68),
        ("Basilisk", 28, 78), ("Basilisk", 34, 72),                 # More basilisks in deep swamp
        # Rotten Slugs (leeches) — DS3: "group of leeches", "surrounding corpse", "at ladder base",
        # "crawling Ghru" areas, everywhere in the swamp water
        ("RottenSlug", 42, 82), ("RottenSlug", 45, 85), ("RottenSlug", 50, 88),    # DS3: Rotten Slugs near leech building
        ("RottenSlug", 48, 105), ("RottenSlug", 52, 110),                    # DS3: Rotten Slugs at ladder base
        ("RottenSlug", 38, 60), ("RottenSlug", 44, 65), ("RottenSlug", 55, 70), # DS3: Rotten Slugs in deeper swamp
        ("RottenSlug", 62, 75), ("RottenSlug", 70, 80), ("RottenSlug", 85, 75), # DS3: Rotten Slugs scattered
        ("RottenSlug", 40, 90), ("RottenSlug", 56, 95),                      # DS3: Rotten Slugs near wall edges
        # Elder Ghru — DS3: "three Elder Ghru huddled around an item", one near fire, more scattered
        ("GiantHollow", 55, 62), ("GiantHollow", 60, 68), ("GiantHollow", 58, 75), # Elder Ghru trio around Poison Gem (wiki)
        ("GiantHollow", 110, 100),                                        # Elder Ghru near gate
        ("GiantHollow", 82, 60),                                          # Elder Ghru near second torch (wiki: "another of these beasts")
        ("GiantHollow", 90, 55),                                          # Elder Ghru on ramp to third torch
        # Great Crab in swamp — DS3: "giant crab which drops Lingering Dragoncrest Ring"
        ("GreatCrab", 65, 62),                                      # Great Crab
        # Corvian and Corvian Storyteller — DS3: in second half wooded area
        ("Corvian", 115, 95), ("Corvian", 120, 100),              # Corvians in second half
        ("DarkMage", 118, 98),                                       # Corvian Storyteller
        # Crystal Lizards — DS3 wiki: 2 near dragon corpse, 1 near Old Wolf (illusory wall),
        # 1 giant Ravenous Crystal Lizard near Perimeter, 1 ramp Crystal Lizard
        ("CrystalLizard", 85, 82),                                   # Near gate
        ("CrystalLizard", 48, 112),                                  # Near Old Wolf tower (illusory wall)
        ("CrystalLizard", 122, 95), ("CrystalLizard", 128, 98),     # DS3: 2 near dragon corpse
        ("CrystalLizard", 56, 65),                                   # DS3: on ramp/stone bridge area
        # Ravenous Crystal Lizard — DS3: "giant Crystal Lizard" near Perimeter bonfire
        ("MiniBoss", 108, 85),                                       # Ravenous Crystal Lizard (giant variant)
        # Stray Demon — DS3: optional mini-boss accessed via lift, drops Soul of a Stray Demon
        ("MiniBoss", 120, 98),                                       # Stray Demon
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Farron Keep) — accurate from wiki ---
    # Pyromancies / Spells / Key items
    entities.append(make_entity("Item", 22 * 16, 45 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Iron Flesh")]))
    entities.append(make_entity("Item", 25 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Golden Scroll")]))
    entities.append(make_entity("Item", 30 * 16, 55 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Sage's Coal")]))
    # Farron Coal — behind illusory wall near Old Wolf of Farron (wiki: Farron Keep)
    entities.append(make_entity("Item", 32 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Farron Coal")]))
    entities.append(make_entity("Item", 45 * 16, 100 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Dreamchaser's Ashes")]))
    entities.append(make_entity("Item", 110 * 16, 85 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Lightning Spear")]))
    entities.append(make_entity("Item", 55 * 16, 82 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Sage's Scroll")]))
    entities.append(make_entity("Item", 60 * 16, 78 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Poison Gem")]))
    entities.append(make_entity("Item", 75 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Great Magic Weapon")]))
    entities.append(make_entity("Item", 88 * 16, 48 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Atonement")]))
    # Wolf's Blood Swordgrass (covenant item on ground before ladder)
    entities.append(make_entity("Item", 42 * 16, 98 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Wolf's Blood Swordgrass")]))
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
    entities.append(make_entity("Item", 48 * 16, 100 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 44 * 16, 96 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Young White Branch")]))
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

    # === ADDITIONAL INTERNAL STRUCTURES — Farron Keep DS3 fidelity ===
    # Torch platform rubble (DS3: three stone platforms with flame altars)
    fill_tiles(chunk, TILE_WALL, 25, 35, 27, 38)
    fill_tiles(chunk, TILE_WALL, 40, 42, 42, 44)
    fill_tiles(chunk, TILE_WALL, 55, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 44)
    # Sunken ruin walls in swamp (DS3: visible stone walls poking through poison)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 58)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)
    fill_tiles(chunk, TILE_WALL, 65, 55, 67, 57)
    fill_tiles(chunk, TILE_WALL, 80, 50, 82, 52)
    # Deep swamp debris (DS3: scattered rocks and sunken stonework)
    fill_tiles(chunk, TILE_WALL, 45, 72, 47, 74)
    fill_tiles(chunk, TILE_WALL, 60, 75, 62, 77)
    fill_tiles(chunk, TILE_WALL, 75, 68, 77, 70)
    fill_tiles(chunk, TILE_WALL, 90, 60, 92, 62)
    # Darkwraith zone rubble (DS3: ruins where Darkwraiths emerge)
    fill_tiles(chunk, TILE_WALL, 100, 68, 102, 70)
    fill_tiles(chunk, TILE_WALL, 110, 75, 112, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 122, 82)
    fill_tiles(chunk, TILE_WALL, 130, 85, 132, 88)
    # Entry path stone steps (DS3: narrow stone steps down into swamp)
    fill_tiles(chunk, TILE_WALL, 12, 20, 14, 22)
    fill_tiles(chunk, TILE_WALL, 20, 24, 22, 26)
    # Basilisk cave stalagmites (DS3: dark cave with stone formations)
    fill_tiles(chunk, TILE_WALL, 24, 66, 26, 68)
    fill_tiles(chunk, TILE_WALL, 32, 74, 34, 76)
    fill_tiles(chunk, TILE_WALL, 20, 78, 22, 80)
    # Old Wolf tower base stones (DS3: tall stone tower accessed by ladder)
    fill_tiles(chunk, TILE_WALL, 42, 98, 44, 100)
    fill_tiles(chunk, TILE_WALL, 48, 110, 50, 112)
    # Grand gate corridor walls (DS3: stone hallway with wolf-crested walls)
    fill_tiles(chunk, TILE_WALL, 118, 82, 120, 85)
    fill_tiles(chunk, TILE_WALL, 128, 90, 130, 93)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 98)
    # Abyss Watchers arena perimeter (DS3: grand stone hall columns)
    fill_tiles(chunk, TILE_WALL, 135, 110, 137, 112)
    fill_tiles(chunk, TILE_WALL, 145, 120, 147, 122)
    fill_tiles(chunk, TILE_WALL, 130, 118, 132, 120)
    # Poison swamp islands (DS3: safe ground patches in the poison)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 50)
    fill_tiles(chunk, TILE_WALL, 85, 55, 86, 57)
    fill_tiles(chunk, TILE_WALL, 58, 68, 59, 70)
    # SESSION 10 FIDELITY PASS — Farron Keep
    # Additional DS3-faithful terrain: rotting post debris, Ghru camp stones,
    # submerged ruin walls, Abyss Watchers sword fragments, swamp edge details
    # Left torch area — rotting post debris (DS3: rotting wooden posts everywhere)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    fill_tiles(chunk, TILE_WALL, 40, 52, 41, 53)
    fill_tiles(chunk, TILE_WALL, 28, 54, 29, 55)
    # Center torch — stone platform details (DS3: stone platform with fire)
    fill_tiles(chunk, TILE_WALL, 66, 46, 67, 47)
    fill_tiles(chunk, TILE_WALL, 70, 50, 71, 51)
    fill_tiles(chunk, TILE_WALL, 64, 52, 65, 53)
    fill_tiles(chunk, TILE_WALL, 72, 54, 73, 55)
    # Right torch — debris stones (DS3: crumbling stone platform)
    fill_tiles(chunk, TILE_WALL, 94, 40, 95, 41)
    fill_tiles(chunk, TILE_WALL, 98, 44, 99, 45)
    fill_tiles(chunk, TILE_WALL, 102, 48, 103, 49)
    fill_tiles(chunk, TILE_WALL, 92, 46, 93, 47)
    # Ghru camp — bonfire ring stones (DS3: Ghru encampment with fire pit)
    fill_tiles(chunk, TILE_WALL, 62, 70, 63, 71)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 66, 74, 67, 75)
    fill_tiles(chunk, TILE_WALL, 72, 72, 73, 73)
    # Keep Ruins — submerged ruin walls (DS3: flooded ruins of the keep)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    fill_tiles(chunk, TILE_WALL, 82, 68, 83, 69)
    fill_tiles(chunk, TILE_WALL, 86, 72, 87, 73)
    fill_tiles(chunk, TILE_WALL, 80, 76, 81, 77)
    # Darkwraith zone — abyss stone debris (DS3: dark knights emerge from abyss)
    fill_tiles(chunk, TILE_WALL, 96, 82, 97, 83)
    fill_tiles(chunk, TILE_WALL, 102, 86, 103, 87)
    fill_tiles(chunk, TILE_WALL, 108, 90, 109, 91)
    fill_tiles(chunk, TILE_WALL, 114, 94, 115, 95)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    # Abyss Watchers arena approach — broken sword fragments (DS3: scattered swords)
    fill_tiles(chunk, TILE_WALL, 120, 98, 121, 99)
    fill_tiles(chunk, TILE_WALL, 126, 102, 127, 103)
    fill_tiles(chunk, TILE_WALL, 122, 106, 123, 107)
    # Swamp water edges — submerged debris (DS3: debris visible in swamp water)
    fill_tiles(chunk, TILE_WALL, 38, 58, 39, 59)
    fill_tiles(chunk, TILE_WALL, 44, 64, 45, 65)
    fill_tiles(chunk, TILE_WALL, 50, 70, 51, 71)
    fill_tiles(chunk, TILE_WALL, 56, 76, 57, 77)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    fill_tiles(chunk, TILE_WALL, 94, 84, 95, 85)
    # Basilisk cave — stone formations (DS3: curse cave with stone formations)
    fill_tiles(chunk, TILE_WALL, 40, 88, 41, 89)
    fill_tiles(chunk, TILE_WALL, 46, 92, 47, 93)
    fill_tiles(chunk, TILE_WALL, 52, 96, 53, 97)


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

    # ================================================================
    # ADDITIONAL DS3 CATHEDRAL ARCHITECTURE — nave pillars, chapel details
    # ================================================================
    # Cemetery entry — additional tombstones and ruined walls (DS3: rain-soaked graveyard)
    fill_tiles(chunk, TILE_WALL, 30, 5, 31, 7)
    fill_tiles(chunk, TILE_WALL, 38, 10, 39, 12)
    fill_tiles(chunk, TILE_WALL, 24, 12, 25, 14)
    fill_tiles(chunk, TILE_WALL, 40, 14, 41, 16)
    # Outer graveyard — dead tree stumps and broken walls (DS3: muddy cemetery with rain)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 30)
    fill_tiles(chunk, TILE_WALL, 44, 30, 45, 32)
    fill_tiles(chunk, TILE_WALL, 34, 34, 35, 36)
    fill_tiles(chunk, TILE_WALL, 48, 34, 49, 36)
    fill_tiles(chunk, TILE_WALL, 26, 36, 27, 38)
    # Cleansing Chapel — altar and pews (DS3: small church with basin of cleansing water)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 44)
    fill_tiles(chunk, TILE_WALL, 34, 46, 35, 48)
    fill_tiles(chunk, TILE_WALL, 38, 44, 39, 46)
    fill_tiles(chunk, TILE_WALL, 26, 48, 27, 50)
    # Front gate — grand cathedral entrance pillars (DS3: massive stone gate)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 54)
    fill_tiles(chunk, TILE_WALL, 52, 54, 53, 56)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 54)
    # Side aisle — dark corridor walls (DS3: narrow passage with thrall ambush)
    fill_tiles(chunk, TILE_WALL, 58, 60, 59, 62)
    fill_tiles(chunk, TILE_WALL, 62, 66, 63, 68)
    fill_tiles(chunk, TILE_WALL, 66, 58, 67, 60)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 70)
    # Nave — additional columns (DS3: open-air courtyard with stone pillars)
    fill_tiles(chunk, TILE_WALL, 42, 70, 43, 72)
    fill_tiles(chunk, TILE_WALL, 48, 76, 49, 78)
    fill_tiles(chunk, TILE_WALL, 56, 72, 57, 74)
    fill_tiles(chunk, TILE_WALL, 60, 80, 61, 82)
    fill_tiles(chunk, TILE_WALL, 50, 82, 51, 84)
    # Giant room — additional cover pillars (DS3: arrows rain from giant tower)
    fill_tiles(chunk, TILE_WALL, 40, 94, 41, 96)
    fill_tiles(chunk, TILE_WALL, 52, 92, 53, 94)
    fill_tiles(chunk, TILE_WALL, 60, 98, 61, 100)
    fill_tiles(chunk, TILE_WALL, 44, 102, 45, 104)
    # Deacon altar — cathedral altar pillars (DS3: dark altar hall with deep fire)
    fill_tiles(chunk, TILE_WALL, 30, 110, 31, 112)
    fill_tiles(chunk, TILE_WALL, 50, 112, 51, 114)
    fill_tiles(chunk, TILE_WALL, 38, 120, 39, 122)
    fill_tiles(chunk, TILE_WALL, 55, 122, 56, 124)
    fill_tiles(chunk, TILE_WALL, 45, 128, 46, 130)
    # Slug corridor — ManGrub alcoves (DS3: narrow passage with slug enemies)
    fill_tiles(chunk, TILE_WALL, 32, 134, 33, 136)
    fill_tiles(chunk, TILE_WALL, 40, 136, 41, 138)
    fill_tiles(chunk, TILE_WALL, 36, 140, 37, 142)
    # Rosaria's bedchamber — ornate room walls (DS3: pale tongue offering chamber)
    fill_tiles(chunk, TILE_WALL, 34, 146, 35, 148)
    fill_tiles(chunk, TILE_WALL, 42, 148, 43, 150)
    fill_tiles(chunk, TILE_WALL, 38, 152, 39, 154)

    # ================================================================
    # SESSION 9 FIDELITY PASS B — CathedralDeep additional DS3 details
    # ================================================================
    # Rain-soaked entry steps — drainage channels (DS3: perpetual rain)
    fill_tiles(chunk, TILE_WALL, 26, 6, 27, 7)
    fill_tiles(chunk, TILE_WALL, 32, 10, 33, 11)
    fill_tiles(chunk, TILE_WALL, 28, 14, 29, 15)
    fill_tiles(chunk, TILE_WALL, 36, 8, 37, 9)
    # Outer graveyard — broken coffin stones (DS3: cemetery with Infested Corpses)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 19)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 27)
    fill_tiles(chunk, TILE_WALL, 34, 20, 35, 21)
    fill_tiles(chunk, TILE_WALL, 24, 30, 25, 31)
    # Cleansing Chapel — stone basin alcoves (DS3: chapel with bonfire)
    fill_tiles(chunk, TILE_WALL, 36, 34, 37, 35)
    fill_tiles(chunk, TILE_WALL, 40, 38, 41, 39)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    fill_tiles(chunk, TILE_WALL, 44, 32, 45, 33)
    # Front gate — iron portcullis remnants (DS3: massive cathedral gate)
    fill_tiles(chunk, TILE_WALL, 48, 46, 49, 47)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 55)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    # Side aisle — hanging banner stones (DS3: cathedral interior banners)
    fill_tiles(chunk, TILE_WALL, 58, 58, 59, 59)
    fill_tiles(chunk, TILE_WALL, 62, 62, 63, 63)
    fill_tiles(chunk, TILE_WALL, 54, 66, 55, 67)
    fill_tiles(chunk, TILE_WALL, 66, 56, 67, 57)
    # Upper gallery — overlook balustrade (DS3: upper level overlooking nave)
    fill_tiles(chunk, TILE_WALL, 68, 60, 69, 61)
    fill_tiles(chunk, TILE_WALL, 72, 64, 73, 65)
    fill_tiles(chunk, TILE_WALL, 64, 68, 65, 69)
    fill_tiles(chunk, TILE_WALL, 76, 58, 77, 59)
    # Nave — flying buttress bases (DS3: gothic cathedral architecture)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 77)
    fill_tiles(chunk, TILE_WALL, 74, 80, 75, 81)
    fill_tiles(chunk, TILE_WALL, 86, 70, 87, 71)
    fill_tiles(chunk, TILE_WALL, 80, 82, 81, 83)
    # Giant's room — arrow-scarred pillars (DS3: giant shoots arrows from above)
    fill_tiles(chunk, TILE_WALL, 42, 86, 43, 87)
    fill_tiles(chunk, TILE_WALL, 46, 90, 47, 91)
    fill_tiles(chunk, TILE_WALL, 38, 94, 39, 95)
    fill_tiles(chunk, TILE_WALL, 50, 84, 51, 85)
    fill_tiles(chunk, TILE_WALL, 44, 98, 45, 99)
    # Deacon hall — candle cluster stones (DS3: mass of deacons in dark hall)
    fill_tiles(chunk, TILE_WALL, 36, 106, 37, 107)
    fill_tiles(chunk, TILE_WALL, 42, 110, 43, 111)
    fill_tiles(chunk, TILE_WALL, 48, 114, 49, 115)
    fill_tiles(chunk, TILE_WALL, 54, 108, 55, 109)
    fill_tiles(chunk, TILE_WALL, 58, 118, 59, 119)
    # Slug corridor — slime-coated walls (DS3: Man Grubs along the corridor)
    fill_tiles(chunk, TILE_WALL, 30, 132, 31, 133)
    fill_tiles(chunk, TILE_WALL, 36, 136, 37, 137)
    fill_tiles(chunk, TILE_WALL, 42, 140, 43, 141)
    fill_tiles(chunk, TILE_WALL, 48, 134, 49, 135)
    fill_tiles(chunk, TILE_WALL, 54, 142, 55, 143)

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
        ("Rat", 36, 84), ("Rat", 44, 86),                             # Writhing Rotten Flesh
        ("InfestedCorpse", 38, 86), ("InfestedCorpse", 42, 88),                   # DS3: Writhing Rotten Flesh
        ("GiantSlave", 44, 92), ("GiantSlave", 56, 98),
        ("CathedralKnight", 48, 88), ("CathedralKnight", 52, 96),
        ("Evangelist", 40, 96),
        ("Thrall", 46, 100), ("Thrall", 54, 102),
        # Cage Spider area (DS3: basilisks in dark room near giant)
        ("Thrall", 36, 94), ("Thrall", 40, 98),                       # Hollow Slaves in dark room near giant
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
        # Boss — Deacons of the Deep
        ("MiniBoss", 45, 114),                                      # Deacons of the Deep boss entity
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items (DS3 Cathedral of the Deep) — accurate from wiki ---
    # Cemetery / approach area
    entities.append(make_entity("Item", 28 * 16, 6 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Fading Soul"), make_field("value", "Int", 50)]))
    entities.append(make_entity("Item", 30 * 16, 35 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Paladin's Ashes")]))
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
    entities.append(make_entity("Item", 48 * 16, 40 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 50 * 16, 42 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Large Soul of an Unknown Traveler"), make_field("value", "Int", 800)]))
    entities.append(make_entity("Item", 52 * 16, 44 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Repair Powder")]))
    entities.append(make_entity("Item", 54 * 16, 46 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Repair Powder")]))
    entities.append(make_entity("Item", 56 * 16, 48 * 16, [make_field("kind", "LocalEnum.ItemKind", "UndeadBoneShard"), make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 58 * 16, 50 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 60 * 16, 52 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Curse Ward Greatshield"), make_field("slot", "String", "Hands")]))
    entities.append(make_entity("Item", 62 * 16, 54 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 64 * 16, 56 * 16, [make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"), make_field("name", "String", "Saint-tree Bellvine")]))
    entities.append(make_entity("Item", 36 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Poisonbite Ring")]))
    # Cathedral interior
    entities.append(make_entity("Item", 50 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 52 * 16, 62 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 66 * 16, 58 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 68 * 16, 60 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 54 * 16, 64 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Soul of an Unknown Traveler"), make_field("value", "Int", 500)]))
    entities.append(make_entity("Item", 56 * 16, 66 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 70 * 16, 62 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Undead Hunter Charm")]))
    entities.append(make_entity("Item", 58 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "SoulOrb"), make_field("name", "String", "Soul of a Nameless Soldier"), make_field("value", "Int", 800)]))
    entities.append(make_entity("Item", 60 * 16, 70 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 62 * 16, 72 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Duel Charm")]))
    entities.append(make_entity("Item", 64 * 16, 74 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Duel Charm")]))
    # Giant room
    entities.append(make_entity("Item", 44 * 16, 94 * 16, [make_field("kind", "LocalEnum.ItemKind", "Ember"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 46 * 16, 96 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Seek Guidance")]))
    entities.append(make_entity("Item", 48 * 16, 98 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Lloyd's Sword Ring")]))
    entities.append(make_entity("Item", 50 * 16, 100 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Deep Braille Divine Tome")]))
    entities.append(make_entity("Item", 52 * 16, 90 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Drang Set"), make_field("slot", "String", "Chest")]))
    # Pale Tongue removed (duplicate — wiki says 1x for Cathedral of the Deep)
    entities.append(make_entity("Item", 40 * 16, 102 * 16, [make_field("kind", "LocalEnum.ItemKind", "ArmorDrop"), make_field("name", "String", "Maiden Set"), make_field("slot", "String", "Chest")]))
    entities.append(make_entity("Item", 42 * 16, 104 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 44 * 16, 106 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Duel Charm")]))
    entities.append(make_entity("Item", 46 * 16, 108 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Duel Charm")]))
    entities.append(make_entity("Item", 48 * 16, 110 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 50 * 16, 112 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 52 * 16, 114 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 54 * 16, 116 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 56 * 16, 118 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 58 * 16, 120 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 42 * 16, 122 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Large Titanite Shard")]))
    # Deep Accursed area
    entities.append(make_entity("Item", 24 * 16, 40 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Aldrich's Sapphire")]))
    # Rafter / upper areas
    entities.append(make_entity("Item", 72 * 16, 66 * 16, [make_field("kind", "LocalEnum.ItemKind", "RingDrop"), make_field("name", "String", "Deep Ring")]))
    entities.append(make_entity("Item", 74 * 16, 68 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Red Sign Soapstone")]))
    entities.append(make_entity("Item", 76 * 16, 70 * 16, [make_field("kind", "LocalEnum.ItemKind", "Consumable"), make_field("name", "String", "Pale Tongue")]))
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
    entities.append(make_entity("Npc", 52 * 16, 78 * 16, [make_field("name", "String", "Patches"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#808080"), make_field("dialogue", "String", "You're a parasite, only thinking of yourself|I know your kind, you're nothing but trouble|What's wrong? Something the matter?|Heh heh heh")]))
    entities.append(make_entity("Npc", 38 * 16, 148 * 16, [make_field("name", "String", "Rosaria"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D0A0B0"), make_field("dialogue", "String", "(No tongue, but a voice is not needed)|Offer me pale tongues|And I shall grant your desire|I am Rosaria, Mother of Rebirth")]))
    # Siegward of Catarina — stuck in the well outside Cathedral (DS3: freed via lift mechanism)
    entities.append(make_entity("Npc", 24 * 16, 56 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A060"), make_field("dialogue", "String", "Aah, hello! Up here!|I seem to be stuck in this well|Could you find a way to get me out?")]))

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

    # === MORE CATHEDRAL DETAILS — DS3 fidelity ===
    # Cathedral approach — cemetery gravestones (DS3: graveyard with tombstones)
    fill_tiles(chunk, TILE_WALL, 14, 14, 16, 16)
    fill_tiles(chunk, TILE_WALL, 22, 18, 24, 20)
    fill_tiles(chunk, TILE_WALL, 28, 12, 30, 14)
    fill_tiles(chunk, TILE_WALL, 16, 28, 18, 30)
    # Giant's graveyard — more tombstones and ruined walls
    # DS3: open graveyard area with giant shooting arrows
    fill_tiles(chunk, TILE_WALL, 22, 48, 24, 50)
    fill_tiles(chunk, TILE_WALL, 32, 52, 34, 54)
    fill_tiles(chunk, TILE_WALL, 42, 56, 44, 58)
    fill_tiles(chunk, TILE_WALL, 28, 58, 30, 60)
    fill_tiles(chunk, TILE_WALL, 46, 46, 48, 48)
    # Cathedral nave — more stone pillars (DS3: massive cathedral interior)
    fill_tiles(chunk, TILE_WALL, 30, 66, 32, 68)
    fill_tiles(chunk, TILE_WALL, 44, 72, 46, 74)
    fill_tiles(chunk, TILE_WALL, 56, 66, 58, 68)
    fill_tiles(chunk, TILE_WALL, 66, 62, 68, 64)
    fill_tiles(chunk, TILE_WALL, 38, 76, 40, 78)
    fill_tiles(chunk, TILE_WALL, 52, 80, 54, 82)
    # Rooftops — more buttress stones (DS3: flying buttresses and gargoyles)
    fill_tiles(chunk, TILE_WALL, 72, 48, 74, 50)
    fill_tiles(chunk, TILE_WALL, 82, 52, 84, 54)
    fill_tiles(chunk, TILE_WALL, 68, 56, 70, 58)
    fill_tiles(chunk, TILE_WALL, 76, 60, 78, 62)
    # Rosaria route — slug corridor walls (DS3: Man Grubs in corridor to bedchamber)
    fill_tiles(chunk, TILE_WALL, 32, 132, 34, 134)
    fill_tiles(chunk, TILE_WALL, 40, 136, 42, 138)
    fill_tiles(chunk, TILE_WALL, 48, 142, 50, 144)
    fill_tiles(chunk, TILE_WALL, 36, 146, 38, 148)
    # Patches bridge — stone bridge pillars (DS3: bridge over cemetery)
    fill_tiles(chunk, TILE_WALL, 20, 56, 22, 58)
    fill_tiles(chunk, TILE_WALL, 28, 60, 30, 62)
    # Deacons altar — more altar stones (DS3: dark altar with deacon swarm)
    fill_tiles(chunk, TILE_WALL, 42, 100, 44, 102)
    fill_tiles(chunk, TILE_WALL, 50, 112, 52, 114)
    fill_tiles(chunk, TILE_WALL, 36, 118, 38, 120)
    fill_tiles(chunk, TILE_WALL, 46, 124, 48, 126)

    # === SESSION 8 FIDELITY PASS — Cathedral of the Deep ===
    # Cathedral entry — rain-soaked steps and drainage channels (DS3: perpetual rain)
    fill_tiles(chunk, TILE_WALL, 20, 6, 21, 8)
    fill_tiles(chunk, TILE_WALL, 34, 4, 35, 6)
    fill_tiles(chunk, TILE_WALL, 26, 14, 27, 16)
    fill_tiles(chunk, TILE_WALL, 40, 8, 41, 10)
    # Outer graveyard — broken coffin stones (DS3: disturbed graves with infested corpses)
    fill_tiles(chunk, TILE_WALL, 20, 32, 21, 34)
    fill_tiles(chunk, TILE_WALL, 46, 26, 47, 28)
    fill_tiles(chunk, TILE_WALL, 28, 36, 29, 38)
    fill_tiles(chunk, TILE_WALL, 50, 36, 51, 38)
    # Cleansing Chapel — stone basin and candle alcoves (DS3: cleansing water basin)
    fill_tiles(chunk, TILE_WALL, 24, 46, 25, 48)
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 52)
    fill_tiles(chunk, TILE_WALL, 32, 52, 33, 54)
    # Cathedral front gate — iron portcullis remnants (DS3: massive cathedral door)
    fill_tiles(chunk, TILE_WALL, 44, 56, 45, 58)
    fill_tiles(chunk, TILE_WALL, 56, 56, 57, 58)
    fill_tiles(chunk, TILE_WALL, 50, 48, 51, 50)
    # Side aisle — hanging banners and dark alcoves (DS3: narrow passage with thralls above)
    fill_tiles(chunk, TILE_WALL, 57, 64, 58, 66)
    fill_tiles(chunk, TILE_WALL, 68, 70, 69, 72)
    fill_tiles(chunk, TILE_WALL, 63, 56, 64, 58)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 70)
    # Upper gallery — overlook balustrade (DS3: overlooks nave from above)
    fill_tiles(chunk, TILE_WALL, 65, 58, 66, 60)
    fill_tiles(chunk, TILE_WALL, 77, 66, 78, 68)
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 72)
    # Nave — additional flying buttress bases (DS3: Gothic cathedral architecture)
    fill_tiles(chunk, TILE_WALL, 40, 84, 41, 86)
    fill_tiles(chunk, TILE_WALL, 62, 84, 63, 86)
    fill_tiles(chunk, TILE_WALL, 34, 80, 35, 82)
    fill_tiles(chunk, TILE_WALL, 64, 76, 65, 78)
    # Giant room — arrow-scarred pillars (DS3: giant shoots massive arrows from tower)
    fill_tiles(chunk, TILE_WALL, 36, 92, 37, 94)
    fill_tiles(chunk, TILE_WALL, 62, 96, 63, 98)
    fill_tiles(chunk, TILE_WALL, 48, 104, 49, 106)
    fill_tiles(chunk, TILE_WALL, 56, 90, 57, 92)
    # Rosaria corridor — slime-coated walls (DS3: Man Grub secretions on walls)
    fill_tiles(chunk, TILE_WALL, 28, 138, 29, 140)
    fill_tiles(chunk, TILE_WALL, 44, 140, 45, 142)
    fill_tiles(chunk, TILE_WALL, 40, 144, 41, 146)
    # Rosaria bedchamber — ornate bed curtains and candelabras (DS3: pale light chamber)
    fill_tiles(chunk, TILE_WALL, 30, 150, 31, 152)
    fill_tiles(chunk, TILE_WALL, 44, 150, 45, 152)
    fill_tiles(chunk, TILE_WALL, 36, 154, 37, 156)

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

    # === MORE CATACOMBS DETAILS — DS3 fidelity ===
    # Entry stairs — more sarcophagi (DS3: stone coffins line the entry)
    fill_tiles(chunk, TILE_WALL, 10, 12, 11, 14)
    fill_tiles(chunk, TILE_WALL, 18, 16, 19, 18)
    fill_tiles(chunk, TILE_WALL, 24, 12, 25, 14)
    # Skeleton ball corridor — more bone pile walls and alcove barriers
    # DS3: narrow corridor with side alcoves to dodge rolling balls
    fill_tiles(chunk, TILE_WALL, 32, 24, 34, 26)
    fill_tiles(chunk, TILE_WALL, 45, 26, 47, 28)
    fill_tiles(chunk, TILE_WALL, 52, 30, 54, 32)
    fill_tiles(chunk, TILE_WALL, 22, 34, 24, 36)
    fill_tiles(chunk, TILE_WALL, 46, 34, 48, 36)
    # Rope bridge area — bridge support pillars and cliff edges
    # DS3: narrow rope bridge over dark abyss
    fill_tiles(chunk, TILE_WALL, 58, 28, 60, 30)
    fill_tiles(chunk, TILE_WALL, 68, 26, 70, 28)
    fill_tiles(chunk, TILE_WALL, 72, 32, 74, 34)
    fill_tiles(chunk, TILE_WALL, 82, 28, 84, 30)
    # Lower tomb chambers — more sarcophagus and tomb walls
    # DS3: interconnected tomb rooms with skeleton ambushes
    fill_tiles(chunk, TILE_WALL, 16, 50, 18, 52)
    fill_tiles(chunk, TILE_WALL, 26, 56, 28, 58)
    fill_tiles(chunk, TILE_WALL, 36, 54, 38, 56)
    fill_tiles(chunk, TILE_WALL, 45, 58, 47, 60)
    fill_tiles(chunk, TILE_WALL, 22, 64, 24, 66)
    fill_tiles(chunk, TILE_WALL, 38, 66, 40, 68)
    fill_tiles(chunk, TILE_WALL, 50, 68, 52, 70)
    fill_tiles(chunk, TILE_WALL, 42, 72, 44, 74)
    # Skeleton wheel area — rubble obstacles (DS3: rolling skeleton wheels)
    fill_tiles(chunk, TILE_WALL, 58, 58, 60, 60)
    fill_tiles(chunk, TILE_WALL, 68, 64, 70, 66)
    fill_tiles(chunk, TILE_WALL, 62, 70, 64, 72)
    fill_tiles(chunk, TILE_WALL, 72, 68, 74, 70)
    # Abandoned tomb — tunnel walls (DS3: descent to Smouldering Lake)
    fill_tiles(chunk, TILE_WALL, 12, 78, 14, 80)
    fill_tiles(chunk, TILE_WALL, 22, 82, 24, 84)
    fill_tiles(chunk, TILE_WALL, 32, 88, 34, 90)
    fill_tiles(chunk, TILE_WALL, 18, 92, 20, 94)
    fill_tiles(chunk, TILE_WALL, 28, 98, 30, 100)
    fill_tiles(chunk, TILE_WALL, 20, 106, 22, 108)
    fill_tiles(chunk, TILE_WALL, 35, 95, 37, 97)
    # Wolnir path — more bone pillars and ancient walls
    # DS3: dark corridor approaching Wolnir's arena
    fill_tiles(chunk, TILE_WALL, 78, 60, 80, 62)
    fill_tiles(chunk, TILE_WALL, 85, 58, 87, 60)
    fill_tiles(chunk, TILE_WALL, 95, 65, 97, 67)
    fill_tiles(chunk, TILE_WALL, 110, 72, 112, 74)
    fill_tiles(chunk, TILE_WALL, 100, 78, 102, 80)
    # Wolnir arena — more ancient pillars and ruins
    # DS3: dark arena where Wolnir emerges from the abyss
    fill_tiles(chunk, TILE_WALL, 118, 90, 120, 93)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 98)
    fill_tiles(chunk, TILE_WALL, 125, 105, 127, 108)
    fill_tiles(chunk, TILE_WALL, 142, 102, 144, 105)
    fill_tiles(chunk, TILE_WALL, 115, 115, 117, 118)
    fill_tiles(chunk, TILE_WALL, 132, 112, 134, 115)

    # === SESSION 6 FIDELITY PASS — Catacombs of Carthus ===
    # Entry stairs — stone urn decorations (DS3: burial urns flanking entry path)
    fill_tiles(chunk, TILE_WALL, 8, 16, 9, 18)
    fill_tiles(chunk, TILE_WALL, 26, 14, 27, 16)
    fill_tiles(chunk, TILE_WALL, 14, 22, 15, 24)
    # Entry arch pillars (DS3: stone archway at catacomb entrance)
    fill_tiles(chunk, TILE_WALL, 10, 8, 12, 10)
    fill_tiles(chunk, TILE_WALL, 24, 8, 26, 10)
    # Skeleton ball corridor — more alcove barriers (DS3: niches to dodge boulder)
    fill_tiles(chunk, TILE_WALL, 17, 26, 19, 28)
    fill_tiles(chunk, TILE_WALL, 38, 20, 40, 22)
    fill_tiles(chunk, TILE_WALL, 53, 22, 55, 24)
    # Skull pile formations (DS3: bone piles throughout corridors)
    fill_tiles(chunk, TILE_WALL, 30, 30, 32, 32)
    fill_tiles(chunk, TILE_WALL, 48, 28, 50, 30)
    fill_tiles(chunk, TILE_WALL, 56, 36, 58, 38)
    # Rope bridge — bridge cable anchor points (DS3: rope bridge over deep abyss)
    fill_tiles(chunk, TILE_WALL, 60, 22, 62, 24)
    fill_tiles(chunk, TILE_WALL, 76, 28, 78, 30)
    fill_tiles(chunk, TILE_WALL, 85, 32, 87, 34)
    fill_tiles(chunk, TILE_WALL, 80, 36, 82, 38)
    # Lower tombs — additional tomb chamber dividers (DS3: interlinked stone rooms)
    fill_tiles(chunk, TILE_WALL, 14, 46, 16, 48)
    fill_tiles(chunk, TILE_WALL, 24, 48, 26, 50)
    fill_tiles(chunk, TILE_WALL, 40, 52, 42, 54)
    fill_tiles(chunk, TILE_WALL, 48, 56, 50, 58)
    fill_tiles(chunk, TILE_WALL, 16, 68, 18, 70)
    fill_tiles(chunk, TILE_WALL, 34, 70, 36, 72)
    # Skeleton wheel tracks (DS3: grooves in stone from rolling wheels)
    fill_tiles(chunk, TILE_WALL, 52, 64, 54, 66)
    fill_tiles(chunk, TILE_WALL, 66, 62, 68, 64)
    fill_tiles(chunk, TILE_WALL, 70, 70, 72, 72)
    # Abandoned tomb — stalactite formations (DS3: underground cave with rock formations)
    fill_tiles(chunk, TILE_WALL, 16, 76, 18, 78)
    fill_tiles(chunk, TILE_WALL, 26, 86, 28, 88)
    fill_tiles(chunk, TILE_WALL, 34, 92, 36, 94)
    fill_tiles(chunk, TILE_WALL, 24, 100, 26, 102)
    # Wolnir path — dark corridor ancient stonework (DS3: ancient carved passage)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    fill_tiles(chunk, TILE_WALL, 82, 64, 84, 66)
    fill_tiles(chunk, TILE_WALL, 98, 70, 100, 72)
    fill_tiles(chunk, TILE_WALL, 108, 76, 110, 78)
    # Wolnir arena — abyss edge pillars (DS3: dark arena with glowing bracelets)
    fill_tiles(chunk, TILE_WALL, 110, 88, 112, 90)
    fill_tiles(chunk, TILE_WALL, 128, 94, 130, 96)
    fill_tiles(chunk, TILE_WALL, 138, 106, 140, 108)
    fill_tiles(chunk, TILE_WALL, 122, 118, 124, 120)
    fill_tiles(chunk, TILE_WALL, 145, 110, 147, 112)
    fill_tiles(chunk, TILE_WALL, 130, 118, 132, 120)

    # ================================================================
    # SESSION 9 FIDELITY PASS — CatacombsOfCarthus architectural details
    # ================================================================
    # Entry stairs — bone pile debris (DS3: bones scattered on entry stairs)
    fill_tiles(chunk, TILE_WALL, 12, 10, 13, 11)
    fill_tiles(chunk, TILE_WALL, 18, 14, 19, 15)
    # Skeleton ball corridor — skull niches (DS3: wall-mounted skull alcoves)
    fill_tiles(chunk, TILE_WALL, 22, 20, 23, 21)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    fill_tiles(chunk, TILE_WALL, 34, 18, 35, 19)
    # Rope bridge approach — crumbling pillar bases (DS3: stone pillars supporting bridge)
    fill_tiles(chunk, TILE_WALL, 40, 32, 41, 33)
    fill_tiles(chunk, TILE_WALL, 44, 34, 45, 35)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    # Lower tombs — collapsed coffin lids (DS3: broken sarcophagi in lower chambers)
    fill_tiles(chunk, TILE_WALL, 20, 50, 21, 51)
    fill_tiles(chunk, TILE_WALL, 26, 52, 27, 53)
    fill_tiles(chunk, TILE_WALL, 14, 54, 15, 55)
    fill_tiles(chunk, TILE_WALL, 30, 56, 31, 57)
    # Skeleton horde room — bone wall formations (DS3: walls of stacked bones)
    fill_tiles(chunk, TILE_WALL, 48, 60, 49, 61)
    fill_tiles(chunk, TILE_WALL, 52, 64, 53, 65)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 44, 66, 45, 67)
    # Abandoned tomb alcove — ritual stones (DS3: dark ritual area)
    fill_tiles(chunk, TILE_WALL, 18, 80, 19, 81)
    fill_tiles(chunk, TILE_WALL, 22, 84, 23, 85)
    fill_tiles(chunk, TILE_WALL, 16, 88, 17, 89)
    # Wolnir arena approach — giant sword fragments (DS3: Wolnir's swords in sand)
    fill_tiles(chunk, TILE_WALL, 30, 94, 31, 95)
    fill_tiles(chunk, TILE_WALL, 36, 96, 37, 97)
    fill_tiles(chunk, TILE_WALL, 42, 92, 43, 93)
    # Wolnir arena — skeleton mound base (DS3: massive pile of skeletons)
    fill_tiles(chunk, TILE_WALL, 60, 98, 61, 99)
    fill_tiles(chunk, TILE_WALL, 64, 102, 65, 103)
    fill_tiles(chunk, TILE_WALL, 70, 96, 71, 97)
    fill_tiles(chunk, TILE_WALL, 56, 104, 57, 105)
    fill_tiles(chunk, TILE_WALL, 68, 106, 69, 107)
    # Smouldering Lake side path — volcanic rock (DS3: lava-adjacent tunnels)
    fill_tiles(chunk, TILE_WALL, 8, 108, 9, 109)
    fill_tiles(chunk, TILE_WALL, 14, 110, 15, 111)
    fill_tiles(chunk, TILE_WALL, 20, 106, 21, 107)
    # Irithyll exit — frost-touched stone (DS3: cold stone near Irithyll entrance)
    fill_tiles(chunk, TILE_WALL, 140, 88, 141, 89)
    fill_tiles(chunk, TILE_WALL, 148, 92, 149, 93)
    fill_tiles(chunk, TILE_WALL, 136, 96, 137, 97)

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
        ("SkeletonSwordman", 16, 22),                                  # Skeleton Swordsman (curved sword variant)
        # Skeleton ball corridor — Skeletons in side alcoves
        ("Skeleton", 25, 28), ("Skeleton", 35, 30), ("Skeleton", 42, 26),
        ("Archer", 20, 21),                                    # Skeleton Swordsman (archer)
        ("SkeletonSwordman", 36, 22), ("SkeletonSwordman", 50, 21),           # Skeleton Swordsmen in alcoves
        ("Skeleton", 48, 32), ("Skeleton", 52, 34),
        # Rope bridge area
        ("Skeleton", 60, 30), ("SkeletonSwordman", 64, 32),
        # Lower tomb chambers — dense skeleton groups
        ("Skeleton", 20, 48), ("Skeleton", 28, 52),
        ("SkeletonSwordman", 24, 55), ("SkeletonSwordman", 32, 50),           # Skeleton Swordsmen in tomb chambers
        ("Skeleton", 35, 56), ("Skeleton", 40, 60), ("Skeleton", 45, 65),
        ("Skeleton", 32, 58), ("Skeleton", 38, 62),
        # Skeleton Wheel area — rapid rolling skeletons (use MiniBoss for wheels)
        ("MiniBoss", 55, 62), ("MiniBoss", 60, 68),           # Skeleton Wheels
        ("MiniBoss", 65, 72),                                  # Skeleton Wheel
        ("Skeleton", 58, 66), ("Skeleton", 63, 70),
        # Abandoned Tomb / Smouldering Lake passage — rats and Writhing Rotten Flesh
        ("Rat", 20, 78), ("Rat", 25, 82), ("Rat", 30, 88),   # Hound-Rats
        ("Rat", 18, 85), ("Rat", 22, 92),                     # More Hound-Rats
        ("Skeleton", 28, 95),                                        # Skeleton in abandoned tomb passage
        ("Skeleton", 35, 98),                                        # Skeleton patrol near lake entrance
        ("LesserCrab", 22, 96),                                 # Lesser Crab (Smouldering Lake passage, wiki-confirmed)
        # Crystal Lizard
        ("CrystalLizard", 48, 50),
        # Path to Wolnir — Knight Slayer Tsorig invasion
        ("BlackKnight", 80, 60),                               # Knight Slayer Tsorig (Black Knight set)
        ("Skeleton", 90, 70), ("SkeletonSwordman", 95, 66),
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
    entities.append(make_entity("Npc", 15 * 16, 18 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Oh, hello, we meet again|Have you seen Horace anywhere?|I have been separated from him|I am worried... Please tell me if you find him")]))
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
    # SESSION 10 FIDELITY PASS — Catacombs of Carthus
    # Additional DS3-faithful terrain: bone pile debris, skull niche alcoves,
    # collapsed coffin lids, skeleton mound clusters, Wolnir approach bones
    # Entry stairs — skull niche alcoves (DS3: skulls embedded in walls)
    fill_tiles(chunk, TILE_WALL, 16, 16, 17, 17)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 19)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    # Skeleton ball corridor — bone pile debris (DS3: bone piles throughout corridor)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 29)
    fill_tiles(chunk, TILE_WALL, 38, 32, 39, 33)
    fill_tiles(chunk, TILE_WALL, 44, 26, 45, 27)
    fill_tiles(chunk, TILE_WALL, 28, 24, 29, 25)
    # Side alcoves — collapsed coffin lids (DS3: broken coffins in alcoves)
    fill_tiles(chunk, TILE_WALL, 48, 22, 49, 23)
    fill_tiles(chunk, TILE_WALL, 54, 28, 55, 29)
    fill_tiles(chunk, TILE_WALL, 42, 30, 43, 31)
    # Rope bridge area — cliff edge bones (DS3: bones on cliff edges near bridge)
    fill_tiles(chunk, TILE_WALL, 58, 28, 59, 29)
    fill_tiles(chunk, TILE_WALL, 62, 32, 63, 33)
    fill_tiles(chunk, TILE_WALL, 66, 34, 67, 35)
    # Lower tomb chambers — skeleton mound clusters (DS3: dense bone mounds)
    fill_tiles(chunk, TILE_WALL, 18, 46, 19, 47)
    fill_tiles(chunk, TILE_WALL, 24, 50, 25, 51)
    fill_tiles(chunk, TILE_WALL, 30, 54, 31, 55)
    fill_tiles(chunk, TILE_WALL, 36, 58, 37, 59)
    fill_tiles(chunk, TILE_WALL, 42, 62, 43, 63)
    fill_tiles(chunk, TILE_WALL, 22, 56, 23, 57)
    fill_tiles(chunk, TILE_WALL, 34, 60, 35, 61)
    # Carthus Wyvern area — bone and ash debris (DS3: smoldering remains)
    fill_tiles(chunk, TILE_WALL, 50, 68, 51, 69)
    fill_tiles(chunk, TILE_WALL, 56, 72, 57, 73)
    fill_tiles(chunk, TILE_WALL, 62, 70, 63, 71)
    # Wolnir approach — skull wall niches (DS3: giant skull wall before arena)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 81)
    fill_tiles(chunk, TILE_WALL, 108, 84, 109, 85)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 122, 92, 123, 93)
    fill_tiles(chunk, TILE_WALL, 112, 86, 113, 87)
    fill_tiles(chunk, TILE_WALL, 104, 82, 105, 83)

    # SESSION 10 PASS B — CatacombsOfCarthus
    # Additional DS3 terrain: bone pile clusters, Wolnir approach bones, skeleton alcove debris
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 51)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 59)
    fill_tiles(chunk, TILE_WALL, 92, 52, 93, 53)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 61)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 57)
    fill_tiles(chunk, TILE_WALL, 128, 64, 129, 65)
    fill_tiles(chunk, TILE_WALL, 140, 58, 141, 59)
    fill_tiles(chunk, TILE_WALL, 136, 72, 137, 73)
    fill_tiles(chunk, TILE_WALL, 120, 68, 121, 69)
    fill_tiles(chunk, TILE_WALL, 108, 74, 109, 75)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 84, 66, 85, 67)


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
    DS3: vast underground cavern with ballista firing across the lake, demon ruins
    below, and the Old Demon King boss at the deepest point.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # SECTION 1: Underground cave entry - doc: x=0,y=0,w=600,h=600
    # Dark tunnel from Catacombs, air getting hotter
    # DS3: player drops down from the Catacombs rope bridge shortcut
    # ================================================================
    carve_ellipse(chunk, 15, 15, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 10, 25, 25)
    # Cave stalactites (DS3: rocky cave ceiling)
    fill_tiles(chunk, TILE_WALL, 10, 10, 12, 12)
    fill_tiles(chunk, TILE_WALL, 18, 8, 19, 10)
    fill_tiles(chunk, TILE_WALL, 22, 12, 23, 14)

    # ================================================================
    # SECTION 2: Smouldering lake shore - doc: x=400,y=600,w=1400,h=1000
    # Vast underground lake with shallow lava, ballista in distance
    # DS3: enormous underground cavern with a lake of lava, ballista tower visible
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 10, 28, 75, 80)
    # Lava patches across the lake surface (DS3: magma covering large portions)
    fill_tiles(chunk, TILE_POISON, 20, 38, 40, 52)
    fill_tiles(chunk, TILE_POISON, 45, 55, 60, 68)
    fill_tiles(chunk, TILE_POISON, 30, 60, 42, 72)
    # Additional lava patches (DS3: lava covers most of the lake floor)
    fill_tiles(chunk, TILE_POISON, 55, 42, 68, 50)
    fill_tiles(chunk, TILE_POISON, 15, 55, 25, 65)
    # Ruin cover points (stone islands in lava)
    fill_tiles(chunk, TILE_GROUND, 25, 42, 32, 48)
    fill_tiles(chunk, TILE_GROUND, 48, 58, 55, 64)
    # Additional safe islands (DS3: stone platforms to dodge ballista bolts)
    fill_tiles(chunk, TILE_GROUND, 38, 48, 44, 54)
    fill_tiles(chunk, TILE_GROUND, 60, 65, 68, 72)
    fill_tiles(chunk, TILE_GROUND, 15, 45, 20, 52)
    # Demon statues along shore (DS3: petrified demon corpses)
    fill_tiles(chunk, TILE_WALL, 18, 32, 20, 34)
    fill_tiles(chunk, TILE_WALL, 28, 40, 30, 42)
    fill_tiles(chunk, TILE_WALL, 42, 50, 44, 52)
    fill_tiles(chunk, TILE_WALL, 58, 58, 60, 60)
    # Corridor from cave to lake
    fill_tiles(chunk, TILE_GROUND, 15, 22, 22, 32)

    # ================================================================
    # SECTION 3: Demon ruins outer hall - doc: x=1200,y=1400,w=800,h=600
    # Collapsed stone pillars, demon carvings, fire demons patrol
    # DS3: large stone hall with demon architecture, basilisks lurk
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 55, 50, 90, 68)
    carve_ellipse(chunk, 72, 58, 12, 8)
    # Collapsed pillars as obstacles
    fill_tiles(chunk, TILE_WALL, 62, 54, 64, 57)
    fill_tiles(chunk, TILE_WALL, 80, 62, 82, 65)
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 62)
    # Additional demon ruin walls (DS3: crumbling demon architecture)
    fill_tiles(chunk, TILE_WALL, 56, 52, 58, 55)
    fill_tiles(chunk, TILE_WALL, 86, 55, 88, 58)
    fill_tiles(chunk, TILE_WALL, 75, 66, 77, 68)
    fill_tiles(chunk, TILE_WALL, 64, 62, 66, 64)
    # Corridor from lake to demon ruins
    fill_tiles(chunk, TILE_GROUND, 45, 45, 58, 55)

    # ================================================================
    # SECTION 4: Demon cleric corridors - doc: x=1800,y=1600,w=600,h=500
    # Winding corridors with demon clerics performing rituals
    # DS3: maze-like passages with basilisks and rats
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 60, 115, 80)
    # Room walls creating cell-like spaces
    fill_tiles(chunk, TILE_WALL, 92, 64, 94, 67)
    fill_tiles(chunk, TILE_WALL, 102, 70, 104, 73)
    fill_tiles(chunk, TILE_WALL, 96, 76, 98, 78)
    # Additional corridor walls (DS3: narrow passages between rooms)
    fill_tiles(chunk, TILE_WALL, 88, 72, 90, 75)
    fill_tiles(chunk, TILE_WALL, 108, 65, 110, 68)
    fill_tiles(chunk, TILE_WALL, 98, 60, 100, 62)
    fill_tiles(chunk, TILE_WALL, 112, 74, 114, 77)
    # Corridor from outer hall to cleric corridors
    fill_tiles(chunk, TILE_GROUND, 85, 55, 92, 62)

    # ================================================================
    # SECTION 5: Old Demon King arena - doc: x=2200,y=2000,w=1000,h=700
    # Grand hall deep in the demon ruins, lava pools at edges
    # DS3: large circular arena with lava pools, demon throne at center
    # ================================================================
    carve_ellipse(chunk, 135, 108, 20, 18)
    fill_tiles(chunk, TILE_GROUND, 115, 90, 155, 128)
    # Lava pools at arena edges
    fill_tiles(chunk, TILE_POISON, 120, 95, 128, 100)
    fill_tiles(chunk, TILE_POISON, 142, 118, 150, 124)
    # Central broken altar
    fill_tiles(chunk, TILE_WALL, 132, 105, 138, 111)
    # Arena pillars (DS3: massive stone columns in the demon throne room)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 106)
    fill_tiles(chunk, TILE_WALL, 146, 112, 148, 116)
    fill_tiles(chunk, TILE_WALL, 128, 118, 130, 122)
    fill_tiles(chunk, TILE_WALL, 140, 100, 142, 104)
    # Corridor from cleric area to arena
    fill_tiles(chunk, TILE_GROUND, 110, 75, 125, 95)

    # ================================================================
    # Side area: Ballista tunnel (NW corner) - skeletons near ballista
    # DS3: narrow tunnel leads to ballista tower, override lever inside
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 8, 80, 35, 100)
    carve_ellipse(chunk, 22, 90, 8, 6)
    # Ballista tower walls (DS3: stone tower with the great ballista)
    fill_tiles(chunk, TILE_WALL, 10, 82, 12, 86)
    fill_tiles(chunk, TILE_WALL, 30, 88, 32, 92)
    fill_tiles(chunk, TILE_WALL, 18, 96, 20, 99)
    # Ballista mechanism (DS3: the ballista fires across the entire lake)
    fill_tiles(chunk, TILE_WALL, 24, 86, 26, 88)

    # Connection from lake to ballista area
    fill_tiles(chunk, TILE_GROUND, 15, 75, 25, 82)

    # ================================================================
    # ADDITIONAL INTERNAL STRUCTURES — Smouldering Lake DS3 fidelity
    # ================================================================
    # Lake shore rock formations (DS3: craggy volcanic rocks along lava shore)
    fill_tiles(chunk, TILE_WALL, 15, 35, 17, 37)
    fill_tiles(chunk, TILE_WALL, 22, 45, 24, 47)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 57)
    fill_tiles(chunk, TILE_WALL, 55, 42, 57, 44)
    fill_tiles(chunk, TILE_WALL, 68, 52, 70, 54)
    # More collapsed pillars in demon ruins (DS3: crumbled demon architecture)
    fill_tiles(chunk, TILE_WALL, 58, 56, 60, 58)
    fill_tiles(chunk, TILE_WALL, 75, 52, 77, 54)
    fill_tiles(chunk, TILE_WALL, 84, 58, 86, 60)
    fill_tiles(chunk, TILE_WALL, 65, 64, 67, 66)
    # Cleric corridor ritual stones (DS3: demon worship alcoves)
    fill_tiles(chunk, TILE_WALL, 88, 66, 90, 68)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    fill_tiles(chunk, TILE_WALL, 108, 72, 110, 74)
    # Arena edge debris (DS3: destroyed demon throne room)
    fill_tiles(chunk, TILE_WALL, 118, 95, 120, 97)
    fill_tiles(chunk, TILE_WALL, 148, 110, 150, 112)
    fill_tiles(chunk, TILE_WALL, 125, 118, 127, 120)
    # Ballista area rocks (DS3: rocky cave leading to ballista tower)
    fill_tiles(chunk, TILE_WALL, 12, 85, 14, 87)
    fill_tiles(chunk, TILE_WALL, 28, 92, 30, 94)
    # Entry cave stalagmite details (DS3: rocky descent from Catacombs)
    fill_tiles(chunk, TILE_WALL, 14, 14, 15, 16)
    fill_tiles(chunk, TILE_WALL, 20, 10, 21, 12)
    # Lava shore volcanic debris (DS3: cooled magma formations)
    fill_tiles(chunk, TILE_WALL, 42, 40, 43, 42)
    fill_tiles(chunk, TILE_WALL, 50, 48, 51, 50)
    fill_tiles(chunk, TILE_WALL, 62, 45, 63, 47)
    fill_tiles(chunk, TILE_WALL, 32, 50, 33, 52)
    # Demon ruins inner walls (DS3: more crumbled demon stonework)
    fill_tiles(chunk, TILE_WALL, 78, 56, 80, 58)
    fill_tiles(chunk, TILE_WALL, 68, 58, 70, 60)
    # Cleric corridor dead-end alcoves (DS3: ritual rooms off main corridor)
    fill_tiles(chunk, TILE_WALL, 94, 70, 96, 72)
    fill_tiles(chunk, TILE_WALL, 104, 66, 106, 68)
    fill_tiles(chunk, TILE_WALL, 100, 76, 102, 78)
    # Arena broken throne fragments (DS3: Old Demon King's destroyed throne)
    fill_tiles(chunk, TILE_WALL, 130, 112, 132, 114)
    fill_tiles(chunk, TILE_WALL, 138, 104, 140, 106)
    fill_tiles(chunk, TILE_WALL, 144, 116, 146, 118)
    # Lake center volcanic rock islands (DS3: cover points from ballista bolts)
    fill_tiles(chunk, TILE_WALL, 40, 60, 41, 62)
    fill_tiles(chunk, TILE_WALL, 52, 55, 53, 57)
    fill_tiles(chunk, TILE_WALL, 60, 70, 61, 72)

    # ================================================================
    # ADDITIONAL DS3 SMOULDERING LAKE — lava formations, demon architecture
    # ================================================================
    # Entry cave — more stalactites and volcanic rock (DS3: hot dark cave from Catacombs)
    fill_tiles(chunk, TILE_WALL, 10, 10, 11, 12)
    fill_tiles(chunk, TILE_WALL, 18, 8, 19, 10)
    fill_tiles(chunk, TILE_WALL, 12, 18, 13, 20)
    fill_tiles(chunk, TILE_WALL, 24, 16, 25, 18)
    # Lake shore — lava crust formations (DS3: cooled lava creates rocky shore)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 40)
    fill_tiles(chunk, TILE_WALL, 38, 42, 39, 44)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 54)
    fill_tiles(chunk, TILE_WALL, 58, 48, 59, 50)
    fill_tiles(chunk, TILE_WALL, 44, 58, 45, 60)
    fill_tiles(chunk, TILE_WALL, 66, 56, 67, 58)
    # Demon ruins — crumbled archways (DS3: ancient demon architecture)
    fill_tiles(chunk, TILE_WALL, 72, 48, 73, 50)
    fill_tiles(chunk, TILE_WALL, 82, 54, 83, 56)
    fill_tiles(chunk, TILE_WALL, 90, 60, 91, 62)
    fill_tiles(chunk, TILE_WALL, 76, 62, 77, 64)
    fill_tiles(chunk, TILE_WALL, 86, 68, 87, 70)
    # Cleric corridor — ritual alcove walls (DS3: demon worship chambers)
    fill_tiles(chunk, TILE_WALL, 92, 64, 93, 66)
    fill_tiles(chunk, TILE_WALL, 100, 68, 101, 70)
    fill_tiles(chunk, TILE_WALL, 106, 74, 107, 76)
    fill_tiles(chunk, TILE_WALL, 112, 70, 113, 72)
    # Old Demon King arena — volcanic throne debris (DS3: destroyed demon throne)
    fill_tiles(chunk, TILE_WALL, 122, 100, 123, 102)
    fill_tiles(chunk, TILE_WALL, 132, 108, 133, 110)
    fill_tiles(chunk, TILE_WALL, 142, 114, 143, 116)
    fill_tiles(chunk, TILE_WALL, 128, 114, 129, 116)
    fill_tiles(chunk, TILE_WALL, 136, 118, 137, 120)
    # Ballista tunnel — additional cave walls (DS3: narrow tunnel to ballista)
    fill_tiles(chunk, TILE_WALL, 8, 90, 9, 92)
    fill_tiles(chunk, TILE_WALL, 16, 94, 17, 96)
    fill_tiles(chunk, TILE_WALL, 26, 86, 27, 88)
    fill_tiles(chunk, TILE_WALL, 32, 96, 33, 98)

    # ================================================================
    # DS3 SMOULDERING LAKE — final architectural fidelity pass
    # ================================================================
    # Ballista bolt impact craters — stone debris from giant bolts (DS3: bolts rain from ballista)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 38)
    fill_tiles(chunk, TILE_WALL, 35, 42, 36, 44)
    fill_tiles(chunk, TILE_WALL, 48, 46, 49, 48)
    fill_tiles(chunk, TILE_WALL, 60, 52, 61, 54)
    fill_tiles(chunk, TILE_WALL, 42, 62, 43, 64)
    # Demon ruin archways — curved stone arches (DS3: distinctive demon architecture)
    fill_tiles(chunk, TILE_WALL, 58, 50, 60, 51)
    fill_tiles(chunk, TILE_WALL, 72, 54, 74, 55)
    fill_tiles(chunk, TILE_WALL, 84, 58, 86, 59)
    fill_tiles(chunk, TILE_WALL, 66, 62, 68, 63)
    # Lava channel walls — narrow streams between stone (DS3: lava flows through cracks)
    fill_tiles(chunk, TILE_WALL, 28, 44, 29, 46)
    fill_tiles(chunk, TILE_WALL, 52, 56, 53, 58)
    fill_tiles(chunk, TILE_WALL, 62, 64, 63, 66)
    fill_tiles(chunk, TILE_WALL, 46, 68, 47, 70)
    # Demon cleric ritual circle stones (DS3: clerics perform rituals around stone circles)
    fill_tiles(chunk, TILE_WALL, 90, 66, 92, 67)
    fill_tiles(chunk, TILE_WALL, 102, 72, 104, 73)
    fill_tiles(chunk, TILE_WALL, 96, 78, 98, 79)
    # Old Demon King throne debris — massive stone throne fragments (DS3: destroyed demon throne)
    fill_tiles(chunk, TILE_WALL, 134, 106, 136, 108)
    fill_tiles(chunk, TILE_WALL, 126, 114, 128, 116)
    fill_tiles(chunk, TILE_WALL, 148, 120, 150, 122)
    # Hidden basilisk cave alcove walls (DS3: narrow caves with basilisk ambushes)
    fill_tiles(chunk, TILE_WALL, 50, 70, 51, 72)
    fill_tiles(chunk, TILE_WALL, 56, 74, 57, 76)
    fill_tiles(chunk, TILE_WALL, 64, 72, 65, 74)
    # Tsorig invasion corridor walls (DS3: Knight Slayer Tsorig invades in narrow passage)
    fill_tiles(chunk, TILE_WALL, 80, 56, 82, 57)
    fill_tiles(chunk, TILE_WALL, 88, 62, 90, 63)
    # Lake center volcanic islands — additional cover (DS3: dodge ballista behind stone islands)
    fill_tiles(chunk, TILE_WALL, 34, 48, 35, 50)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 56)
    fill_tiles(chunk, TILE_WALL, 58, 60, 59, 62)

    # ================================================================
    # SESSION 9 FIDELITY PASS — SmoulderingLake architectural details
    # ================================================================
    # Ballista platform — bolt-scarred stone (DS3: massive ballista fires at you)
    fill_tiles(chunk, TILE_WALL, 18, 14, 19, 15)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 19)
    fill_tiles(chunk, TILE_WALL, 14, 22, 15, 23)
    fill_tiles(chunk, TILE_WALL, 26, 12, 27, 13)
    # Lava shore — blackened rock formations (DS3: lava lake edge)
    fill_tiles(chunk, TILE_WALL, 38, 28, 39, 29)
    fill_tiles(chunk, TILE_WALL, 42, 32, 43, 33)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 46, 26, 47, 27)
    fill_tiles(chunk, TILE_WALL, 36, 40, 37, 41)
    # Demon ruins archway — collapsed demon architecture (DS3: Izalith-style ruins)
    fill_tiles(chunk, TILE_WALL, 52, 44, 53, 45)
    fill_tiles(chunk, TILE_WALL, 56, 48, 57, 49)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 60, 42, 61, 43)
    fill_tiles(chunk, TILE_WALL, 54, 56, 55, 57)
    # Underground lake — stalactite debris (DS3: cave system beneath lake)
    fill_tiles(chunk, TILE_WALL, 28, 60, 29, 61)
    fill_tiles(chunk, TILE_WALL, 32, 64, 33, 65)
    fill_tiles(chunk, TILE_WALL, 24, 68, 25, 69)
    fill_tiles(chunk, TILE_WALL, 36, 58, 37, 59)
    fill_tiles(chunk, TILE_WALL, 30, 72, 31, 73)
    # Old Demon King arena — scorched earth pillars (DS3: fiery boss arena)
    fill_tiles(chunk, TILE_WALL, 100, 84, 101, 85)
    fill_tiles(chunk, TILE_WALL, 104, 88, 105, 89)
    fill_tiles(chunk, TILE_WALL, 96, 92, 97, 93)
    fill_tiles(chunk, TILE_WALL, 108, 80, 109, 81)
    fill_tiles(chunk, TILE_WALL, 102, 94, 103, 95)
    # Lake volcanic islands — additional cover stones
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 51)
    fill_tiles(chunk, TILE_WALL, 48, 56, 49, 57)
    fill_tiles(chunk, TILE_WALL, 56, 52, 57, 53)

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
    # Smouldering Rotten Flesh, Great Crab, Carthus Sandworm,
    # Skeleton Swordsmen, Skeleton Wheels, Knight Slayer Tsorig NPC
    enemy_data = [
        # Entry cave
        ("DemonStatue", 18, 18), ("DemonStatue", 22, 22),
        # Lake shore — Demon Statues and Smouldering Rotten Flesh
        ("DemonStatue", 28, 42), ("DemonStatue", 50, 60), ("DemonStatue", 65, 50),
        ("DemonStatue", 18, 32), ("DemonStatue", 35, 40),
        ("InfestedCorpse", 62, 58), ("InfestedCorpse", 68, 62), ("InfestedCorpse", 72, 55),
        ("InfestedCorpse", 42, 48), ("InfestedCorpse", 55, 52),                    # Smouldering Rotten Flesh (DS3: corpse-like enemies)
        # Smouldering Rotten Flesh — DS3 wiki: 6 in corridor, 3 in demon ruins room (9 total)
        ("InfestedCorpse", 48, 55), ("InfestedCorpse", 58, 62),
        ("InfestedCorpse", 65, 60), ("InfestedCorpse", 70, 58),
        ("InfestedCorpse", 72, 62), ("InfestedCorpse", 68, 65),
        ("InfestedCorpse", 95, 62), ("InfestedCorpse", 98, 65), ("InfestedCorpse", 100, 60),
        # Basilisks near lava pools
        ("Basilisk", 52, 65), ("Basilisk", 58, 70), ("Basilisk", 55, 72),
        # Great Crab in lake (rare giant enemy)
        ("GreatCrab", 38, 45),                                 # Great Crab
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
        ("CarthusSandworm", 45, 68),                                 # Carthus Sandworm
        # Crystal Lizards — wiki: 3 total (1 near bonfire, 2 in cavern after ballista)
        ("CrystalLizard", 82, 55), ("CrystalLizard", 112, 78), ("CrystalLizard", 22, 98),
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
        ("Ember", "Ember", 70, 53, 0),  # wiki: 3x Ember
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

    # NPCs — DS3 Smouldering Lake: Knight Slayer Tsorig
    entities.append(make_entity("Npc", 30 * 16, 92 * 16, [make_field("name", "String", "Knight Slayer Tsorig"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#804020"), make_field("dialogue", "String", "Forgive me, I was absorbed in my conquest|We meet again, Unkindled|I am Tsorig, the Knight Slayer|The arbitrary distinction between right and wrong is irrelevant")]))
    # Horace the Hushed — hostile hollow in DS3 (attacks player in Smouldering Lake cave)
    # Represented as enemy rather than friendly NPC
    entities.append(make_entity("Enemy", 20 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Skeleton", "Skeleton"))]))

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
    # SESSION 10 FIDELITY PASS — Smouldering Lake
    # Additional DS3-faithful terrain: ballista-scarred stone, lava blackened rock,
    # demon ruins archway debris, volcanic island formations, scorched earth
    # Ballista area — bolt-scarred stones (DS3: giant ballista shoots bolts)
    fill_tiles(chunk, TILE_WALL, 22, 16, 23, 17)
    fill_tiles(chunk, TILE_WALL, 28, 20, 29, 21)
    fill_tiles(chunk, TILE_WALL, 18, 24, 19, 25)
    # Lake shore — lava blackened rock (DS3: lava pools at lake edges)
    fill_tiles(chunk, TILE_WALL, 48, 56, 49, 57)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    fill_tiles(chunk, TILE_WALL, 62, 54, 63, 55)
    fill_tiles(chunk, TILE_WALL, 68, 58, 69, 59)
    fill_tiles(chunk, TILE_WALL, 74, 62, 75, 63)
    # Demon ruins archways — collapsed arch debris (DS3: demon ruins architecture)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    fill_tiles(chunk, TILE_WALL, 50, 52, 51, 53)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 57)
    fill_tiles(chunk, TILE_WALL, 46, 62, 47, 63)
    fill_tiles(chunk, TILE_WALL, 54, 66, 55, 67)
    # Volcanic island formations (DS3: scattered rock islands in lava)
    fill_tiles(chunk, TILE_WALL, 80, 70, 81, 71)
    fill_tiles(chunk, TILE_WALL, 86, 74, 87, 75)
    fill_tiles(chunk, TILE_WALL, 92, 72, 93, 73)
    fill_tiles(chunk, TILE_WALL, 78, 78, 79, 79)
    # Black Knight patrol area — scorched earth (DS3: Black Knights patrol ruins)
    fill_tiles(chunk, TILE_WALL, 102, 82, 103, 83)
    fill_tiles(chunk, TILE_WALL, 108, 86, 109, 87)
    fill_tiles(chunk, TILE_WALL, 96, 80, 97, 81)
    # Carthus Sandworm area — burrow debris (DS3: sandworm emerges from ground)
    fill_tiles(chunk, TILE_WALL, 118, 92, 119, 93)
    fill_tiles(chunk, TILE_WALL, 124, 88, 125, 89)
    fill_tiles(chunk, TILE_WALL, 112, 90, 113, 91)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 87)
    # Tsorig's area — tunnel debris (DS3: Knight Slayer Tsorig invades)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    fill_tiles(chunk, TILE_WALL, 40, 46, 41, 47)
    fill_tiles(chunk, TILE_WALL, 28, 44, 29, 45)

    # SESSION 10 PASS B — SmoulderingLake
    # Additional DS3 terrain: ballista bolt debris, lava island stones, demon archway fragments
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 51)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 59)
    fill_tiles(chunk, TILE_WALL, 92, 52, 93, 53)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 61)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 57)
    fill_tiles(chunk, TILE_WALL, 128, 64, 129, 65)
    fill_tiles(chunk, TILE_WALL, 140, 58, 141, 59)
    fill_tiles(chunk, TILE_WALL, 136, 72, 137, 73)
    fill_tiles(chunk, TILE_WALL, 120, 68, 121, 69)
    fill_tiles(chunk, TILE_WALL, 108, 74, 109, 75)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 84, 66, 85, 67)


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

    # ================================================================
    # ADDITIONAL DS3 IRITHYLL ARCHITECTURE — city buildings, cathedral details
    # ================================================================
    # Entry bridge — stone railing pillars (DS3: narrow bridge over moonlit valley)
    fill_tiles(chunk, TILE_WALL, 10, 34, 11, 36)
    fill_tiles(chunk, TILE_WALL, 18, 38, 19, 40)
    fill_tiles(chunk, TILE_WALL, 24, 42, 25, 44)
    fill_tiles(chunk, TILE_WALL, 8, 44, 9, 46)
    fill_tiles(chunk, TILE_WALL, 22, 46, 23, 48)
    # Main boulevard — additional building facades (DS3: gothic buildings line the street)
    fill_tiles(chunk, TILE_WALL, 42, 54, 44, 56)
    fill_tiles(chunk, TILE_WALL, 55, 58, 57, 60)
    fill_tiles(chunk, TILE_WALL, 70, 52, 72, 54)
    fill_tiles(chunk, TILE_WALL, 80, 48, 82, 50)
    fill_tiles(chunk, TILE_WALL, 90, 54, 92, 56)
    fill_tiles(chunk, TILE_WALL, 95, 58, 97, 60)
    # Church of Yorshka — interior chapel walls (DS3: bonfire church with altar)
    fill_tiles(chunk, TILE_WALL, 55, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 65, 42, 67, 44)
    fill_tiles(chunk, TILE_WALL, 48, 44, 50, 46)
    fill_tiles(chunk, TILE_WALL, 70, 40, 72, 42)
    # Distant Manor — Siegward's kitchen interior (DS3: kitchen with estus soup)
    fill_tiles(chunk, TILE_WALL, 24, 74, 26, 76)
    fill_tiles(chunk, TILE_WALL, 32, 78, 34, 80)
    fill_tiles(chunk, TILE_WALL, 28, 84, 30, 86)
    fill_tiles(chunk, TILE_WALL, 36, 86, 38, 88)
    fill_tiles(chunk, TILE_WALL, 18, 80, 20, 82)
    # Sewers — underground tunnel walls (DS3: flooded basement with centipedes)
    fill_tiles(chunk, TILE_WALL, 64, 78, 65, 80)
    fill_tiles(chunk, TILE_WALL, 75, 82, 76, 84)
    fill_tiles(chunk, TILE_WALL, 85, 86, 86, 88)
    fill_tiles(chunk, TILE_WALL, 92, 92, 93, 94)
    fill_tiles(chunk, TILE_WALL, 70, 90, 71, 92)
    fill_tiles(chunk, TILE_WALL, 80, 94, 81, 96)
    # Silver Knight hall — ornate hall columns (DS3: knights guard paintings and treasure)
    fill_tiles(chunk, TILE_WALL, 25, 102, 27, 104)
    fill_tiles(chunk, TILE_WALL, 35, 106, 37, 108)
    fill_tiles(chunk, TILE_WALL, 42, 110, 44, 112)
    fill_tiles(chunk, TILE_WALL, 50, 114, 52, 116)
    fill_tiles(chunk, TILE_WALL, 30, 118, 32, 120)
    fill_tiles(chunk, TILE_WALL, 48, 120, 50, 122)
    # Pontiff cathedral — grand cathedral interior (DS3: massive stone hall)
    fill_tiles(chunk, TILE_WALL, 105, 65, 107, 68)
    fill_tiles(chunk, TILE_WALL, 125, 70, 127, 73)
    fill_tiles(chunk, TILE_WALL, 135, 78, 137, 81)
    fill_tiles(chunk, TILE_WALL, 118, 84, 120, 87)
    fill_tiles(chunk, TILE_WALL, 128, 90, 130, 93)
    fill_tiles(chunk, TILE_WALL, 110, 78, 112, 80)
    fill_tiles(chunk, TILE_WALL, 140, 85, 142, 88)
    # Exit to dungeon — castle corridor walls (DS3: path to Irithyll Dungeon)
    fill_tiles(chunk, TILE_WALL, 135, 42, 137, 44)
    fill_tiles(chunk, TILE_WALL, 142, 48, 144, 50)
    fill_tiles(chunk, TILE_WALL, 132, 50, 134, 52)

    # ================================================================
    # SESSION 9 FIDELITY PASS B — Irithyll additional architectural details
    # ================================================================
    # Entry bridge — frozen lamppost bases (DS3: iconic snow bridge with lampposts)
    fill_tiles(chunk, TILE_WALL, 14, 37, 15, 38)
    fill_tiles(chunk, TILE_WALL, 18, 39, 19, 40)
    fill_tiles(chunk, TILE_WALL, 10, 41, 11, 42)
    fill_tiles(chunk, TILE_WALL, 22, 35, 23, 36)
    # Central square — ice-cracked paving (DS3: frozen town square)
    fill_tiles(chunk, TILE_WALL, 26, 43, 27, 44)
    fill_tiles(chunk, TILE_WALL, 30, 47, 31, 48)
    fill_tiles(chunk, TILE_WALL, 22, 51, 23, 52)
    fill_tiles(chunk, TILE_WALL, 34, 41, 35, 42)
    fill_tiles(chunk, TILE_WALL, 28, 53, 29, 54)
    # Church of Yorshka — frosted window alcoves (DS3: small church interior)
    fill_tiles(chunk, TILE_WALL, 58, 38, 59, 39)
    fill_tiles(chunk, TILE_WALL, 62, 42, 63, 43)
    fill_tiles(chunk, TILE_WALL, 54, 46, 55, 47)
    fill_tiles(chunk, TILE_WALL, 66, 36, 67, 37)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 49)
    # Silver Knight hall — armor stand alcoves (DS3: suits of armor lining halls)
    fill_tiles(chunk, TILE_WALL, 70, 52, 71, 53)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 66, 60, 67, 61)
    fill_tiles(chunk, TILE_WALL, 78, 50, 79, 51)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 63)
    # Sewer channels — slime-coated drain covers (DS3: Sewer Centipedes lurk here)
    fill_tiles(chunk, TILE_WALL, 82, 66, 83, 67)
    fill_tiles(chunk, TILE_WALL, 86, 70, 87, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 90, 64, 91, 65)
    # Pontiff cathedral — altar railing stones (DS3: massive cathedral interior)
    fill_tiles(chunk, TILE_WALL, 94, 78, 95, 79)
    fill_tiles(chunk, TILE_WALL, 98, 82, 99, 83)
    fill_tiles(chunk, TILE_WALL, 90, 86, 91, 87)
    fill_tiles(chunk, TILE_WALL, 102, 76, 103, 77)
    fill_tiles(chunk, TILE_WALL, 96, 88, 97, 89)
    # Distant Manor — crumbling fireplace (DS3: manor with Siegward soup)
    fill_tiles(chunk, TILE_WALL, 32, 80, 33, 81)
    fill_tiles(chunk, TILE_WALL, 36, 84, 37, 85)
    fill_tiles(chunk, TILE_WALL, 28, 88, 29, 89)
    fill_tiles(chunk, TILE_WALL, 40, 78, 41, 79)

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

    # Enemies — DS3 Irithyll of the Boreal Valley (wiki-verified walkthrough):
    # Pontiff Knights (hags/dancers with fire swords), Fire Witches (ranged fire magic),
    # Irithyllian Slaves (invisible cloaked ambushers in many rooms), Sulyvahn's Beasts,
    # Irithyllian Beast-hounds (dogs in packs), Sewer Centipedes, Silver Knights,
    # Giant Slaves (giants in post-Pontiff courtyard), Mimic, Evangelist, Deep Accursed
    enemy_data = [
        # Bridge entrance — Sulyvahn's Beast ambush (DS3: attacks on entry bridge)
        ("SulyvahnsBeast", 12, 38),                                 # Sulyvahn's Beast at bridge
        ("BorealKnight", 18, 42),                                      # Pontiff Knight patrol
        # Main boulevard — Pontiff Knights (DS3: "encounter Pontiff Knights", "fast attack movements")
        ("BorealKnight", 38, 50), ("BorealKnight", 55, 55),
        ("BorealKnight", 75, 60), ("BorealKnight", 90, 58),
        # Irithyllian Slaves (invisible hags) — DS3: "dispatch the other hag", "group of hags",
        # "another group of hags", "invisible hag in corner", "slightly hidden hags",
        # "eyes of hags in dark room", "many of these hags", "hags in each alcove"
        ("IrithyllianSlave", 42, 48), ("IrithyllianSlave", 60, 52),
        ("IrithyllianSlave", 78, 56),
        ("IrithyllianSlave", 36, 44), ("IrithyllianSlave", 46, 46),             # More hags on upper streets
        ("IrithyllianSlave", 52, 50), ("IrithyllianSlave", 56, 48),             # Hags near fountain area
        ("IrithyllianSlave", 62, 56), ("IrithyllianSlave", 82, 52),             # More invisible hags
        # Fire Witches (DarkMage) — DS3: "fire casting knight", "fire caster"
        ("DarkMage", 42, 52), ("DarkMage", 95, 62),
        ("DarkMage", 68, 58),
        # Irithyllian Beast-hounds (Dog) — DS3: "three dogs (one sleeping in corner)",
        # "two dogs" later, "several dogs" in upper area
        ("Dog", 50, 48), ("Dog", 80, 55), ("Dog", 65, 54),
        ("Dog", 48, 60), ("Dog", 52, 62), ("Dog", 76, 58),     # More dogs including sleeping one
        ("Dog", 38, 65), ("Dog", 42, 68),                       # Dogs near staircase (wiki: "two dogs")
        # Crystal Lizards (DS3: 1 near illusory wall stairs, 2 post-Pontiff courtyard, 1 lever path)
        ("CrystalLizard", 65, 42), ("CrystalLizard", 128, 75),
        ("CrystalLizard", 135, 80), ("CrystalLizard", 140, 72),
        # Distant Manor area — Irithyllian Slaves and Pontiff Knights
        ("IrithyllianSlave", 28, 70), ("IrithyllianSlave", 35, 75),            # Slaves near manor
        ("BorealKnight", 32, 72), ("BorealKnight", 40, 82),
        # Corvian near the manor gardens
        ("Corvian", 22, 68),
        # Church of Yorshka area — Pontiff Knights guarding church
        ("BorealKnight", 70, 45), ("BorealKnight", 72, 42),
        ("IrithyllianSlave", 64, 44),                                   # Invisible hag near church entrance
        # Irithyll Slave near hidden staircase (DS3: invisible ambushers in Irithyll)
        ("IrithyllianSlave", 45, 55),
        # Dark room / staircase area — DS3: "take stairs down, encounter many hags",
        # "hags in each of these alcoves", "two more hags at foot of tree"
        ("IrithyllianSlave", 48, 54), ("IrithyllianSlave", 54, 56),             # Hags in dark room
        ("IrithyllianSlave", 50, 58), ("IrithyllianSlave", 56, 60),             # Hags in alcoves along stairs
        # Sewers — Sewer Centipedes (DS3: "few Sewer Centipedes in the water")
        ("SewerCentipede", 68, 80), ("SewerCentipede", 78, 85), ("SewerCentipede", 88, 90),
        ("SewerCentipede", 72, 88), ("SewerCentipede", 82, 82),
        # Sulyvahn's Beasts at sewer reservoir — DS3 wiki: 2 beasts in flooded chamber
        ("SulyvahnsBeast", 72, 90), ("SulyvahnsBeast", 78, 94),
        # Silver Knight hall / rooftops — DS3: "several Silver Knights",
        # "Silver Knight straight ahead and another to the left",
        # "two archer Silver Knights"
        ("SilverKnight", 30, 100), ("SilverKnight", 42, 110),
        ("SilverKnight", 48, 118), ("SilverKnight", 36, 108),
        ("SilverKnight", 44, 105), ("SilverKnight", 32, 104),  # More Silver Knights in hall
        ("SilverKnight", 138, 64), ("SilverKnight", 146, 64),  # Archer Silver Knights on rooftops
        # Post-Pontiff courtyard — DS3: "Giant will rise... Another Giant to your right"
        ("GiantSlave", 126, 78), ("GiantSlave", 134, 82),      # Two Giants in courtyard
        # Arena approach — Pontiff Knights + Fire Witch guard
        ("BorealKnight", 105, 65), ("DarkMage", 110, 70),
        ("BorealKnight", 100, 62),
        ("BorealKnight", 108, 68),                                    # DS3: "2 Pontiff Knights" near fog gate
        # Silver Knights on bridge to Anor Londo (DS3: knights guard the path to cathedral)
        ("SilverKnight", 140, 50), ("SilverKnight", 142, 48), ("SilverKnight", 144, 52),
        ("SilverKnight", 146, 54), ("SilverKnight", 148, 56),              # More knights on bridge
        # Pontiff arena entrance — Deep Accursed (DS3: near revolving switch)
        ("DeepAccursed", 132, 88),
        # Mimic near boulevard (DS3: drops Golden Ritual Spear)
        ("Mimic", 58, 56),
        # Boss — Pontiff Sulyvahn
        ("MiniBoss", 120, 76),                                      # Pontiff Sulyvahn boss entity
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
        ("Consumable", "Rime-blue Moss Clump", 28, 82, 0),
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
    entities.append(make_entity("Npc", 62 * 16, 38 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Hello again. We seem destined to cross paths|Are you also headed for Anor Londo?|I must reach Aldrich of the Deep|To avenge my companions who fell to him")]))
    entities.append(make_entity("Npc", 28 * 16, 80 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A060"), make_field("dialogue", "String", "Oh, hello there! Fancy meeting you here|I'm cooking up some estus soup, my specialty|Care to join me? It's quite good, you know|Oh, very good indeed, to see a friendly face")]))
    # Sirris — appears near Church of Yorshka after Rosaria covenant
    entities.append(make_entity("Npc", 58 * 16, 44 * 16, [make_field("name", "String", "Sirris of the Sunless Realms"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#A0B0C0"), make_field("dialogue", "String", "I am Sirris of the Sunless Realms|I was once a knight, but no longer|Let me swear to you my knightly vows|I shall serve you faithfully until death"), make_field("appear_condition", "String", "rosaria_covenant")]))

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

    # === MORE IRITHYLL DETAILS — DS3 fidelity ===
    # Ice bridge entry — frozen archway and ice crystals (DS3: stone bridge with frost)
    fill_tiles(chunk, TILE_WALL, 8, 34, 10, 36)
    fill_tiles(chunk, TILE_WALL, 18, 38, 20, 40)
    fill_tiles(chunk, TILE_WALL, 16, 42, 18, 44)
    # Main boulevard — more building facades (DS3: lined with gothic buildings)
    fill_tiles(chunk, TILE_WALL, 38, 42, 40, 45)
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 58)
    fill_tiles(chunk, TILE_WALL, 62, 42, 64, 45)
    fill_tiles(chunk, TILE_WALL, 72, 48, 74, 51)
    fill_tiles(chunk, TILE_WALL, 80, 55, 82, 58)
    fill_tiles(chunk, TILE_WALL, 88, 48, 90, 51)
    fill_tiles(chunk, TILE_WALL, 92, 55, 94, 58)
    # Church of Yorshka — altar and nave walls (DS3: small church with bonfire)
    fill_tiles(chunk, TILE_WALL, 48, 34, 50, 36)
    fill_tiles(chunk, TILE_WALL, 55, 36, 57, 38)
    fill_tiles(chunk, TILE_WALL, 65, 38, 67, 40)
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 44)
    # Distant Manor — kitchen and hall walls (DS3: Siegward's cooking area)
    fill_tiles(chunk, TILE_WALL, 22, 75, 24, 78)
    fill_tiles(chunk, TILE_WALL, 32, 78, 34, 80)
    fill_tiles(chunk, TILE_WALL, 38, 86, 40, 88)
    fill_tiles(chunk, TILE_WALL, 18, 82, 20, 84)
    # Sewers — more drainage pillars (DS3: underground water channels)
    fill_tiles(chunk, TILE_WALL, 65, 78, 67, 80)
    fill_tiles(chunk, TILE_WALL, 75, 82, 77, 84)
    fill_tiles(chunk, TILE_WALL, 85, 88, 87, 90)
    fill_tiles(chunk, TILE_WALL, 95, 85, 97, 87)
    fill_tiles(chunk, TILE_WALL, 70, 92, 72, 94)
    fill_tiles(chunk, TILE_WALL, 90, 95, 92, 97)
    # Silver Knight hall — hall pillars and arches (DS3: knights in dark hall)
    fill_tiles(chunk, TILE_WALL, 25, 102, 27, 105)
    fill_tiles(chunk, TILE_WALL, 35, 108, 37, 111)
    fill_tiles(chunk, TILE_WALL, 42, 115, 44, 118)
    fill_tiles(chunk, TILE_WALL, 50, 110, 52, 113)
    fill_tiles(chunk, TILE_WALL, 30, 115, 32, 118)
    # Pontiff cathedral — massive pillars (DS3: grand cathedral with tall columns)
    fill_tiles(chunk, TILE_WALL, 105, 68, 107, 71)
    fill_tiles(chunk, TILE_WALL, 125, 72, 127, 75)
    fill_tiles(chunk, TILE_WALL, 140, 78, 142, 81)
    fill_tiles(chunk, TILE_WALL, 115, 85, 117, 88)
    fill_tiles(chunk, TILE_WALL, 130, 90, 132, 93)
    fill_tiles(chunk, TILE_WALL, 142, 88, 144, 91)
    # Exit corridor to dungeon — stone arches (DS3: dark passage to dungeon)
    fill_tiles(chunk, TILE_WALL, 135, 42, 137, 45)
    fill_tiles(chunk, TILE_WALL, 142, 48, 144, 50)

    # === SESSION 8 FIDELITY PASS — Irithyll of the Boreal Valley ===
    # Bridge approach — frozen lamppost bases (DS3: lined with broken street lamps)
    fill_tiles(chunk, TILE_WALL, 6, 12, 7, 14)
    fill_tiles(chunk, TILE_WALL, 16, 14, 17, 16)
    fill_tiles(chunk, TILE_WALL, 26, 18, 27, 20)
    # Central square — ice-cracked paving stones (DS3: frozen fountain square)
    fill_tiles(chunk, TILE_WALL, 48, 48, 49, 50)
    fill_tiles(chunk, TILE_WALL, 56, 52, 57, 54)
    fill_tiles(chunk, TILE_WALL, 44, 56, 45, 58)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 48)
    # Church of Yorshka — frosted window alcoves (DS3: beautiful stained glass, now dark)
    fill_tiles(chunk, TILE_WALL, 100, 32, 101, 34)
    fill_tiles(chunk, TILE_WALL, 110, 38, 111, 40)
    fill_tiles(chunk, TILE_WALL, 95, 40, 96, 42)
    # Side streets — broken railings and ice-covered debris (DS3: frozen side alleys)
    fill_tiles(chunk, TILE_WALL, 22, 62, 23, 64)
    fill_tiles(chunk, TILE_WALL, 36, 68, 37, 70)
    fill_tiles(chunk, TILE_WALL, 14, 72, 15, 74)
    fill_tiles(chunk, TILE_WALL, 28, 88, 29, 90)
    # Sewer channels — slime-coated drain covers (DS3: Sewer Centipedes in dark water)
    fill_tiles(chunk, TILE_WALL, 68, 86, 69, 88)
    fill_tiles(chunk, TILE_WALL, 80, 90, 81, 92)
    fill_tiles(chunk, TILE_WALL, 72, 94, 73, 96)
    fill_tiles(chunk, TILE_WALL, 88, 92, 89, 94)
    # Silver Knight hall — suit of armor alcoves (DS3: mounted knight armor displays)
    fill_tiles(chunk, TILE_WALL, 20, 108, 21, 110)
    fill_tiles(chunk, TILE_WALL, 40, 112, 41, 114)
    fill_tiles(chunk, TILE_WALL, 55, 108, 56, 110)
    fill_tiles(chunk, TILE_WALL, 48, 116, 49, 118)
    # Pontiff cathedral — altar railing and communion alcoves (DS3: desecrated cathedral)
    fill_tiles(chunk, TILE_WALL, 110, 74, 111, 76)
    fill_tiles(chunk, TILE_WALL, 135, 82, 136, 84)
    fill_tiles(chunk, TILE_WALL, 120, 90, 121, 92)
    fill_tiles(chunk, TILE_WALL, 145, 86, 146, 88)
    # SESSION 10 FIDELITY PASS — Irithyll
    # Additional DS3-faithful terrain: frozen lamppost bases, ice-cracked paving,
    # church frosted windows, Silver Knight alcoves, Pontiff cathedral debris
    # Entry bridge — bridge railing stones (DS3: iconic bridge into Irithyll)
    fill_tiles(chunk, TILE_WALL, 14, 36, 15, 37)
    fill_tiles(chunk, TILE_WALL, 18, 40, 19, 41)
    fill_tiles(chunk, TILE_WALL, 12, 38, 13, 39)
    # Main boulevard — frozen lamppost bases (DS3: lampposts line the streets)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    fill_tiles(chunk, TILE_WALL, 42, 52, 43, 53)
    fill_tiles(chunk, TILE_WALL, 48, 50, 49, 51)
    fill_tiles(chunk, TILE_WALL, 54, 54, 55, 55)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 49)
    # Ice-cracked paving — cracked stone (DS3: frozen cracked streets)
    fill_tiles(chunk, TILE_WALL, 66, 52, 67, 53)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 57)
    fill_tiles(chunk, TILE_WALL, 78, 54, 79, 55)
    fill_tiles(chunk, TILE_WALL, 84, 58, 85, 59)
    fill_tiles(chunk, TILE_WALL, 90, 52, 91, 53)
    # Church of Yorshka — frosted window stones (DS3: church with frosted windows)
    fill_tiles(chunk, TILE_WALL, 68, 44, 69, 45)
    fill_tiles(chunk, TILE_WALL, 74, 42, 75, 43)
    fill_tiles(chunk, TILE_WALL, 70, 40, 71, 41)
    fill_tiles(chunk, TILE_WALL, 64, 46, 65, 47)
    # Silver Knight hall — alcove walls (DS3: knights guard alcoves)
    fill_tiles(chunk, TILE_WALL, 30, 98, 31, 99)
    fill_tiles(chunk, TILE_WALL, 36, 102, 37, 103)
    fill_tiles(chunk, TILE_WALL, 42, 100, 43, 101)
    fill_tiles(chunk, TILE_WALL, 48, 104, 49, 105)
    fill_tiles(chunk, TILE_WALL, 34, 106, 35, 107)
    fill_tiles(chunk, TILE_WALL, 46, 108, 47, 109)
    # Pontiff cathedral — cathedral debris (DS3: Pontiff Sulyvahn's cathedral)
    fill_tiles(chunk, TILE_WALL, 96, 64, 97, 65)
    fill_tiles(chunk, TILE_WALL, 102, 68, 103, 69)
    fill_tiles(chunk, TILE_WALL, 108, 66, 109, 67)
    fill_tiles(chunk, TILE_WALL, 114, 70, 115, 71)
    fill_tiles(chunk, TILE_WALL, 100, 72, 101, 73)
    fill_tiles(chunk, TILE_WALL, 106, 74, 107, 75)
    # Sewer area — sewer channel stones (DS3: sewers beneath Irithyll)
    fill_tiles(chunk, TILE_WALL, 66, 78, 67, 79)
    fill_tiles(chunk, TILE_WALL, 72, 82, 73, 83)
    fill_tiles(chunk, TILE_WALL, 78, 80, 79, 81)
    fill_tiles(chunk, TILE_WALL, 84, 84, 85, 85)
    # Distant Manor area — manor garden stones (DS3: Distant Manor garden)
    fill_tiles(chunk, TILE_WALL, 26, 68, 27, 69)
    fill_tiles(chunk, TILE_WALL, 32, 72, 33, 73)
    fill_tiles(chunk, TILE_WALL, 38, 70, 39, 71)
    fill_tiles(chunk, TILE_WALL, 24, 74, 25, 75)


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

    # ================================================================
    # ADDITIONAL DS3 IRITHYLL DUNGEON — cell walls, prison architecture
    # ================================================================
    # Entry passage — dripping water and broken masonry (DS3: damp stone corridor)
    fill_tiles(chunk, TILE_WALL, 10, 12, 12, 14)
    fill_tiles(chunk, TILE_WALL, 22, 16, 24, 18)
    fill_tiles(chunk, TILE_WALL, 16, 22, 18, 24)
    fill_tiles(chunk, TILE_WALL, 28, 20, 30, 22)
    # Upper cell block — additional cell dividers (DS3: many small cells with jailers)
    fill_tiles(chunk, TILE_WALL, 20, 30, 22, 34)
    fill_tiles(chunk, TILE_WALL, 32, 32, 34, 36)
    fill_tiles(chunk, TILE_WALL, 45, 30, 47, 34)
    fill_tiles(chunk, TILE_WALL, 58, 32, 60, 36)
    fill_tiles(chunk, TILE_WALL, 62, 38, 64, 42)
    # Central cell block — watchtower supports and cell partitions (DS3: multi-level prison)
    fill_tiles(chunk, TILE_WALL, 30, 48, 32, 52)
    fill_tiles(chunk, TILE_WALL, 42, 52, 44, 56)
    fill_tiles(chunk, TILE_WALL, 58, 55, 60, 58)
    fill_tiles(chunk, TILE_WALL, 70, 52, 72, 55)
    fill_tiles(chunk, TILE_WALL, 48, 62, 50, 65)
    fill_tiles(chunk, TILE_WALL, 62, 65, 64, 68)
    fill_tiles(chunk, TILE_WALL, 75, 58, 77, 62)
    # Siegward's cell — cell bars and chain hooks (DS3: Siegward trapped behind bars)
    fill_tiles(chunk, TILE_WALL, 88, 52, 90, 55)
    fill_tiles(chunk, TILE_WALL, 95, 62, 97, 65)
    fill_tiles(chunk, TILE_WALL, 82, 58, 84, 60)
    # Lower drain — tunnel walls and grates (DS3: flooded drain tunnels with rats)
    fill_tiles(chunk, TILE_WALL, 25, 75, 27, 78)
    fill_tiles(chunk, TILE_WALL, 40, 80, 42, 82)
    fill_tiles(chunk, TILE_WALL, 55, 88, 57, 90)
    fill_tiles(chunk, TILE_WALL, 35, 90, 37, 92)
    fill_tiles(chunk, TILE_WALL, 60, 75, 62, 78)
    fill_tiles(chunk, TILE_WALL, 48, 92, 50, 94)
    # Karla's cell — dark alcove walls (DS3: Karla imprisoned behind illusory wall)
    fill_tiles(chunk, TILE_WALL, 78, 80, 80, 84)
    fill_tiles(chunk, TILE_WALL, 88, 88, 90, 92)
    fill_tiles(chunk, TILE_WALL, 95, 82, 97, 85)
    # Exit corridor — stone arch supports (DS3: path to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 110, 28, 112, 32)
    fill_tiles(chunk, TILE_WALL, 125, 30, 127, 34)
    fill_tiles(chunk, TILE_WALL, 135, 36, 137, 40)
    fill_tiles(chunk, TILE_WALL, 140, 32, 142, 36)

    # ================================================================
    # SESSION 9 FIDELITY PASS — IrithyllDungeon architectural details
    # ================================================================
    # Entry cell corridor — iron bar debris (DS3: prison cell corridors)
    fill_tiles(chunk, TILE_WALL, 18, 16, 19, 17)
    fill_tiles(chunk, TILE_WALL, 24, 20, 25, 21)
    fill_tiles(chunk, TILE_WALL, 14, 24, 15, 25)
    fill_tiles(chunk, TILE_WALL, 28, 14, 29, 15)
    fill_tiles(chunk, TILE_WALL, 20, 28, 21, 29)
    # Jailer patrol corridor — hanging cage stones (DS3: cages hanging from ceiling)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 38, 40, 39, 41)
    fill_tiles(chunk, TILE_WALL, 30, 44, 31, 45)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    # Giant rat cellar — slime-coated stones (DS3: wet dungeon basement)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 42, 60, 43, 61)
    fill_tiles(chunk, TILE_WALL, 54, 50, 55, 51)
    fill_tiles(chunk, TILE_WALL, 48, 64, 49, 65)
    # Siegward cell block — iron door frame stones (DS3: Siegward locked in cell)
    fill_tiles(chunk, TILE_WALL, 58, 44, 59, 45)
    fill_tiles(chunk, TILE_WALL, 62, 48, 63, 49)
    fill_tiles(chunk, TILE_WALL, 54, 52, 55, 53)
    fill_tiles(chunk, TILE_WALL, 66, 42, 67, 43)
    # Karla cell area — abyss-tinged stones (DS3: Karla imprisoned in deepest cell)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 68, 76, 69, 77)
    fill_tiles(chunk, TILE_WALL, 80, 66, 81, 67)
    fill_tiles(chunk, TILE_WALL, 74, 78, 75, 79)
    # Profaned Capital exit — dragon-crest stones (DS3: passage to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 90, 30, 91, 31)
    fill_tiles(chunk, TILE_WALL, 95, 34, 96, 35)
    fill_tiles(chunk, TILE_WALL, 86, 38, 87, 39)
    fill_tiles(chunk, TILE_WALL, 100, 28, 101, 29)

    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3: only Irithyll Dungeon bonfire
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))     # Irithyll Dungeon

    # Enemies — DS3 Irithyll Dungeon (wiki-verified walkthrough):
    # Jailers (branding iron wardens — many throughout), Reanimated Corpses in cells,
    # Wretches (screaming enemies), Rats (swarms in drains), Basilisks (curse spawners),
    # Infested Corpses (corpse-grubs), Lycanthropes (Dog), Monstrosity of Sin (MonstrosityOfSin),
    # Sewer Centipedes (ManGrub), Gargoyles (tower guard), Crystal Lizards, Mimics
    enemy_data = [
        # Upper prison block — DS3: "3 jailers down stairs", jailers patrol corridors
        ("Jailer", 22, 20), ("Jailer", 35, 30), ("Jailer", 48, 38),
        ("Jailer", 25, 25), ("Jailer", 32, 32),
        ("Jailer", 42, 28), ("Jailer", 58, 42),                 # More jailers on upper level
        # Reanimated Corpses in cells (Wretches — DS3: bloated prisoners in cells)
        ("Wretch", 20, 30), ("Wretch", 28, 35),
        ("Wretch", 38, 28), ("Wretch", 45, 34),
        # Central prison block — DS3: "room infested with jailers", "several jailers in large room"
        ("Jailer", 55, 55), ("Jailer", 60, 60), ("Jailer", 68, 52),
        ("Jailer", 48, 58), ("Jailer", 62, 65), ("Jailer", 70, 58),  # More jailers in central block
        ("Jailer", 58, 70), ("Jailer", 65, 68),                 # DS3: "2 in next room"
        ("Wretch", 50, 50), ("Wretch", 62, 55),
        ("CrystalLizard", 52, 52),
        # Siegward cell area — Wretches and Reanimated Corpses
        ("Jailer", 88, 55), ("Jailer", 95, 62),                 # Jailer guards near Siegward
        ("Wretch", 78, 60), ("Wretch", 82, 65),
        ("Wretch", 85, 62), ("Wretch", 92, 58),
        # Lower drains — DS3: rats, basilisks, corpse-grubs in sewer area
        ("Rat", 28, 78), ("Rat", 35, 82), ("Rat", 42, 88),
        ("Rat", 32, 85), ("Rat", 48, 90),
        ("Rat", 25, 90), ("Rat", 55, 92),                       # More rats in deep drains
        # Basilisks — DS3: "10+ basilisks spawn behind you" in drain area
        ("Basilisk", 55, 80), ("Basilisk", 62, 85),
        ("Basilisk", 40, 88), ("Basilisk", 65, 78),             # More basilisks in drains
        ("Basilisk", 48, 82), ("Basilisk", 58, 90),             # Additional curse-spawners
        ("InfestedCorpse", 38, 80), ("InfestedCorpse", 45, 86), # Corpse-grubs
        # Sewer Centipede in drain area (DS3: Sewer Centipedes in Irithyll Dungeon drains)
        ("SewerCentipede", 60, 75), ("SewerCentipede", 50, 78),
        # Cage Spider in drain area
        ("CageSpider", 55, 88),                                       # DS3: Cage Spider in drain area (→ Basilisk)
        # Monstrosity of Sin — DS3: sleeping giant near lower level
        ("MonstrosityOfSin", 42, 75),
        # Lycanthrope (Dog) in rat tunnels
        ("Dog", 22, 82), ("Dog", 38, 85),
        # Exit corridor — DS3: Wretches (bloated prisoners) guard the upper exit path
        ("Wretch", 95, 42), ("Wretch", 125, 30),
        # Karla's cell area — DS3: jailers guard the lower cells
        ("Jailer", 85, 85), ("Jailer", 95, 90),
        ("Jailer", 82, 90),                                    # Additional jailer near Karla
        ("Wretch", 88, 88), ("Wretch", 92, 82),
        # Alva Seeker of the Spurned — invades near exit corridor (MiniBoss)
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
    entities.append(make_entity("Npc", 92 * 16, 56 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D4A520"), make_field("dialogue", "String", "Oh! You have my thanks, my deepest thanks|I seem to have gotten myself locked in this cell|A brave warrior like yourself, I knew you would come")]))
    entities.append(make_entity("Npc", 90 * 16, 84 * 16, [make_field("name", "String", "Karla"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#4A0080"), make_field("dialogue", "String", "What do you want? I'm a prisoner, same as you|I can teach you dark sorceries, if you bring me tomes|But nothing that could harm the Fire Keeper, understand|I am Karla, a humble student of the dark arts")]))

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

    # === ADDITIONAL DUNGEON DETAILS — DS3 fidelity ===
    # Upper cell block — additional cell bars (DS3: cramped cells with iron bars)
    fill_tiles(chunk, TILE_WALL, 18, 28, 20, 30)
    fill_tiles(chunk, TILE_WALL, 28, 32, 30, 34)
    fill_tiles(chunk, TILE_WALL, 35, 26, 37, 28)
    fill_tiles(chunk, TILE_WALL, 48, 30, 50, 32)
    fill_tiles(chunk, TILE_WALL, 60, 36, 62, 38)
    # Central cell block — more prison cell dividers
    # DS3: large room with many cells, jailers patrol between them
    fill_tiles(chunk, TILE_WALL, 30, 54, 32, 56)
    fill_tiles(chunk, TILE_WALL, 42, 60, 44, 62)
    fill_tiles(chunk, TILE_WALL, 55, 64, 57, 66)
    fill_tiles(chunk, TILE_WALL, 68, 55, 70, 57)
    fill_tiles(chunk, TILE_WALL, 72, 62, 74, 64)
    fill_tiles(chunk, TILE_WALL, 38, 66, 40, 68)
    # Siegward's cell area — cell interior walls (DS3: Siegward locked in a cell)
    fill_tiles(chunk, TILE_WALL, 82, 56, 84, 58)
    fill_tiles(chunk, TILE_WALL, 88, 60, 90, 62)
    fill_tiles(chunk, TILE_WALL, 95, 64, 97, 66)
    fill_tiles(chunk, TILE_WALL, 100, 58, 102, 60)
    # Lower drains — sewage pipes and grates (DS3: rat-infested sewer tunnels)
    fill_tiles(chunk, TILE_WALL, 25, 75, 27, 77)
    fill_tiles(chunk, TILE_WALL, 35, 80, 37, 82)
    fill_tiles(chunk, TILE_WALL, 45, 88, 47, 90)
    fill_tiles(chunk, TILE_WALL, 55, 82, 57, 84)
    fill_tiles(chunk, TILE_WALL, 62, 90, 64, 92)
    fill_tiles(chunk, TILE_WALL, 30, 88, 32, 90)
    # Karla's cell — deep prison walls (DS3: Karla locked in deepest cell)
    fill_tiles(chunk, TILE_WALL, 78, 82, 80, 84)
    fill_tiles(chunk, TILE_WALL, 85, 88, 87, 90)
    fill_tiles(chunk, TILE_WALL, 92, 84, 94, 86)
    fill_tiles(chunk, TILE_WALL, 98, 90, 100, 92)
    # Gargoyle tower — stone platforms (DS3: gargoyles on tower roof)
    fill_tiles(chunk, TILE_WALL, 88, 38, 90, 40)
    fill_tiles(chunk, TILE_WALL, 95, 42, 97, 44)
    fill_tiles(chunk, TILE_WALL, 102, 40, 104, 42)
    # Exit corridor — stone arches (DS3: long corridor to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 112, 30, 114, 32)
    fill_tiles(chunk, TILE_WALL, 125, 28, 127, 30)
    fill_tiles(chunk, TILE_WALL, 132, 32, 134, 34)
    fill_tiles(chunk, TILE_WALL, 142, 28, 144, 30)
    # Additional Irithyll Dungeon DS3 details
    # Entry guard room walls (DS3: wretches attack from cells on entry)
    fill_tiles(chunk, TILE_WALL, 10, 14, 12, 16)
    fill_tiles(chunk, TILE_WALL, 16, 16, 18, 18)
    # Main hall watchtower supports (DS3: tall dark corridor with Jailers carrying lanterns)
    fill_tiles(chunk, TILE_WALL, 36, 42, 38, 44)
    fill_tiles(chunk, TILE_WALL, 50, 46, 52, 48)
    fill_tiles(chunk, TILE_WALL, 65, 52, 67, 54)
    # Jailer patrol obstacles (DS3: jailers carry branding irons, patrol between cells)
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 62)
    fill_tiles(chunk, TILE_WALL, 100, 62, 102, 64)
    fill_tiles(chunk, TILE_WALL, 110, 56, 112, 58)
    # Deep drain tunnel walls (DS3: narrow tunnels beneath the prison)
    fill_tiles(chunk, TILE_WALL, 20, 82, 22, 84)
    fill_tiles(chunk, TILE_WALL, 40, 86, 42, 88)
    fill_tiles(chunk, TILE_WALL, 50, 78, 52, 80)
    fill_tiles(chunk, TILE_WALL, 65, 86, 67, 88)
    # Profaned Capital exit ramp stones (DS3: stone ramp leading out of dungeon)
    fill_tiles(chunk, TILE_WALL, 120, 34, 122, 36)
    fill_tiles(chunk, TILE_WALL, 135, 26, 137, 28)

    # ================================================================
    # DS3 IRITHYLL DUNGEON — final architectural fidelity pass
    # ================================================================
    # Entry passage — dripping water stalactites (DS3: damp stone entry from Irithyll)
    fill_tiles(chunk, TILE_WALL, 12, 10, 13, 12)
    fill_tiles(chunk, TILE_WALL, 20, 14, 21, 16)
    fill_tiles(chunk, TILE_WALL, 26, 18, 27, 20)
    # Upper cell block — iron bar dividers (DS3: rows of cramped cells with iron bars)
    fill_tiles(chunk, TILE_WALL, 30, 26, 31, 28)
    fill_tiles(chunk, TILE_WALL, 38, 34, 39, 36)
    fill_tiles(chunk, TILE_WALL, 52, 36, 53, 38)
    fill_tiles(chunk, TILE_WALL, 60, 28, 61, 30)
    # Central prison hall — additional support columns (DS3: dark hall with tall pillars)
    fill_tiles(chunk, TILE_WALL, 40, 48, 41, 50)
    fill_tiles(chunk, TILE_WALL, 55, 52, 56, 54)
    fill_tiles(chunk, TILE_WALL, 68, 58, 69, 60)
    fill_tiles(chunk, TILE_WALL, 45, 64, 46, 66)
    # Siegward cell — broken bars and chain rings (DS3: Siegward's cell with Old Cell Key)
    fill_tiles(chunk, TILE_WALL, 85, 56, 86, 58)
    fill_tiles(chunk, TILE_WALL, 92, 60, 93, 62)
    fill_tiles(chunk, TILE_WALL, 98, 56, 99, 58)
    # Lower drain — slime-coated tunnel walls (DS3: toxic water in drain tunnels)
    fill_tiles(chunk, TILE_WALL, 28, 84, 29, 86)
    fill_tiles(chunk, TILE_WALL, 38, 78, 39, 80)
    fill_tiles(chunk, TILE_WALL, 58, 82, 59, 84)
    fill_tiles(chunk, TILE_WALL, 48, 92, 49, 94)
    # Karla's cell — deep prison stone walls (DS3: illusory wall conceals Karla)
    fill_tiles(chunk, TILE_WALL, 82, 86, 83, 88)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 84)
    fill_tiles(chunk, TILE_WALL, 96, 88, 97, 90)
    # Gargoyle tower ledge — narrow parapet walls (DS3: exterior ledge with gargoyles)
    fill_tiles(chunk, TILE_WALL, 90, 36, 91, 38)
    fill_tiles(chunk, TILE_WALL, 98, 44, 99, 46)
    # Exit corridor — dungeon gate stones (DS3: long stone corridor to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 118, 32, 119, 34)
    fill_tiles(chunk, TILE_WALL, 128, 26, 129, 28)
    fill_tiles(chunk, TILE_WALL, 140, 30, 141, 32)
    # SESSION 10 FIDELITY PASS — Irithyll Dungeon
    # Additional DS3-faithful terrain: iron bar debris, hanging cage stones,
    # Siegward cell block, Karla abyss stones, jailer corridor debris
    # Entry stairs — stone step debris (DS3: crumbling dungeon stairs)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 22, 22, 23, 23)
    fill_tiles(chunk, TILE_WALL, 26, 20, 27, 21)
    # Jailer corridor — iron bar debris (DS3: iron bars and prison cells)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 29)
    fill_tiles(chunk, TILE_WALL, 38, 32, 39, 33)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 37)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 35)
    fill_tiles(chunk, TILE_WALL, 56, 38, 57, 39)
    # Hanging cage area — cage support stones (DS3: cages hanging from ceiling)
    fill_tiles(chunk, TILE_WALL, 62, 42, 63, 43)
    fill_tiles(chunk, TILE_WALL, 68, 46, 69, 47)
    fill_tiles(chunk, TILE_WALL, 72, 44, 73, 45)
    fill_tiles(chunk, TILE_WALL, 66, 48, 67, 49)
    # Siegward cell block — cell wall debris (DS3: Siegward's prison cell)
    fill_tiles(chunk, TILE_WALL, 78, 52, 79, 53)
    fill_tiles(chunk, TILE_WALL, 82, 56, 83, 57)
    fill_tiles(chunk, TILE_WALL, 76, 54, 77, 55)
    # Karla's cell — abyss stones (DS3: Karla's cell in the abyss area)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)
    fill_tiles(chunk, TILE_WALL, 92, 66, 93, 67)
    fill_tiles(chunk, TILE_WALL, 86, 64, 87, 65)
    fill_tiles(chunk, TILE_WALL, 94, 68, 95, 69)
    # Main cell block — prison door debris (DS3: rows of prison cells)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    fill_tiles(chunk, TILE_WALL, 40, 46, 41, 47)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 45)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 46, 59, 47)
    # Basilisk pit — wet stone debris (DS3: curse frog pit)
    fill_tiles(chunk, TILE_WALL, 98, 72, 99, 73)
    fill_tiles(chunk, TILE_WALL, 102, 76, 103, 77)
    fill_tiles(chunk, TILE_WALL, 96, 74, 97, 75)
    fill_tiles(chunk, TILE_WALL, 106, 78, 107, 79)
    # Profaned Capital exit — corridor stones (DS3: path to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 110, 82, 111, 83)
    fill_tiles(chunk, TILE_WALL, 114, 86, 115, 87)
    fill_tiles(chunk, TILE_WALL, 118, 84, 119, 85)


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

    # === SESSION 6 FIDELITY PASS — Profaned Capital ===
    # Entry bridge — stone arch supports (DS3: narrow stone bridge from dungeon)
    fill_tiles(chunk, TILE_WALL, 6, 10, 8, 12)
    fill_tiles(chunk, TILE_WALL, 12, 6, 14, 8)
    # Bonfire tower — ladder alcove walls (DS3: Gilligan's broken ladder)
    fill_tiles(chunk, TILE_WALL, 12, 8, 14, 10)
    fill_tiles(chunk, TILE_WALL, 24, 18, 26, 20)
    fill_tiles(chunk, TILE_WALL, 14, 20, 16, 22)
    # Boss path bridge — more fire debris (DS3: burning debris on bridge)
    fill_tiles(chunk, TILE_WALL, 34, 8, 36, 10)
    fill_tiles(chunk, TILE_WALL, 46, 14, 48, 16)
    fill_tiles(chunk, TILE_WALL, 42, 8, 44, 10)
    # First jailer room — cell dividers (DS3: jailer handmaids patrol rooms)
    fill_tiles(chunk, TILE_WALL, 50, 8, 52, 10)
    fill_tiles(chunk, TILE_WALL, 60, 16, 62, 18)
    fill_tiles(chunk, TILE_WALL, 66, 10, 68, 12)
    # Second jailer room — more pillars (DS3: stone pillars in jailer chamber)
    fill_tiles(chunk, TILE_WALL, 72, 14, 74, 16)
    fill_tiles(chunk, TILE_WALL, 82, 10, 84, 12)
    fill_tiles(chunk, TILE_WALL, 78, 18, 80, 20)
    # Yhorm arena — throne room pillars (DS3: grand throne room with Storm Ruler)
    fill_tiles(chunk, TILE_WALL, 92, 6, 94, 10)
    fill_tiles(chunk, TILE_WALL, 100, 12, 102, 16)
    fill_tiles(chunk, TILE_WALL, 114, 20, 116, 24)
    fill_tiles(chunk, TILE_WALL, 122, 14, 124, 18)
    fill_tiles(chunk, TILE_WALL, 104, 28, 106, 32)
    fill_tiles(chunk, TILE_WALL, 126, 10, 128, 14)
    # Upper ruins — crumbled walls (DS3: ruined capital buildings)
    fill_tiles(chunk, TILE_WALL, 18, 36, 20, 38)
    fill_tiles(chunk, TILE_WALL, 28, 40, 30, 42)
    fill_tiles(chunk, TILE_WALL, 38, 38, 40, 40)
    # Main streets — more ruined house walls (DS3: collapsed capital buildings)
    fill_tiles(chunk, TILE_WALL, 24, 52, 26, 54)
    fill_tiles(chunk, TILE_WALL, 36, 56, 38, 58)
    fill_tiles(chunk, TILE_WALL, 44, 60, 46, 62)
    fill_tiles(chunk, TILE_WALL, 54, 54, 56, 56)
    fill_tiles(chunk, TILE_WALL, 32, 62, 34, 64)
    # Toxic pool — more stone platforms (DS3: stepping stones through toxic water)
    fill_tiles(chunk, TILE_WALL, 46, 66, 48, 68)
    fill_tiles(chunk, TILE_WALL, 56, 72, 58, 74)
    fill_tiles(chunk, TILE_WALL, 64, 76, 66, 78)
    fill_tiles(chunk, TILE_WALL, 50, 74, 52, 76)
    # Church — ornate door frames (DS3: church with monstrosities)
    fill_tiles(chunk, TILE_WALL, 26, 72, 28, 74)
    fill_tiles(chunk, TILE_WALL, 40, 76, 42, 78)
    fill_tiles(chunk, TILE_WALL, 34, 82, 36, 84)
    # Siegward's cell — cell bars (DS3: iron bars trapping Siegward)
    fill_tiles(chunk, TILE_WALL, 58, 46, 60, 48)
    fill_tiles(chunk, TILE_WALL, 64, 52, 66, 54)
    # Court sorcerer roof — rooftop debris (DS3: rooftop area above church)
    fill_tiles(chunk, TILE_WALL, 48, 40, 50, 42)
    fill_tiles(chunk, TILE_WALL, 56, 44, 58, 46)
    fill_tiles(chunk, TILE_WALL, 60, 38, 62, 40)
    # Giant room — treasure room walls (DS3: room with giant and treasure)
    fill_tiles(chunk, TILE_WALL, 70, 58, 72, 60)
    fill_tiles(chunk, TILE_WALL, 78, 64, 80, 66)
    fill_tiles(chunk, TILE_WALL, 84, 60, 86, 62)
    fill_tiles(chunk, TILE_WALL, 76, 68, 78, 70)
    # Shortcut path — stone corridor walls (DS3: shortcut back to Irithyll Dungeon)
    fill_tiles(chunk, TILE_WALL, 86, 60, 88, 62)
    fill_tiles(chunk, TILE_WALL, 90, 64, 92, 66)

    # ================================================================
    # SESSION 9 FIDELITY PASS B+C — ProfanedCapital full DS3 details
    # ================================================================
    # Tower staircase — crumbling spiral stones (DS3: tower with Gilligan's ladder)
    fill_tiles(chunk, TILE_WALL, 16, 8, 17, 9)
    fill_tiles(chunk, TILE_WALL, 22, 10, 23, 11)
    fill_tiles(chunk, TILE_WALL, 14, 16, 15, 17)
    fill_tiles(chunk, TILE_WALL, 24, 14, 25, 15)
    # Collapsed exterior — ruined house foundations (DS3: destroyed buildings)
    fill_tiles(chunk, TILE_WALL, 32, 32, 33, 33)
    fill_tiles(chunk, TILE_WALL, 36, 36, 37, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 40, 30, 41, 31)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    # Palace ruins — fire-scorched masonry (DS3: profaned flame damage)
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 48, 50, 49, 51)
    fill_tiles(chunk, TILE_WALL, 40, 54, 41, 55)
    fill_tiles(chunk, TILE_WALL, 52, 44, 53, 45)
    # Flooded cells — stagnant pool stones (DS3: waterlogged prison cells)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    fill_tiles(chunk, TILE_WALL, 60, 64, 61, 65)
    fill_tiles(chunk, TILE_WALL, 52, 68, 53, 69)
    fill_tiles(chunk, TILE_WALL, 64, 58, 65, 59)
    # Yhorm bridge — fire vessel pedestals (DS3: fire containers on bridge)
    fill_tiles(chunk, TILE_WALL, 68, 74, 69, 75)
    fill_tiles(chunk, TILE_WALL, 72, 78, 73, 79)
    fill_tiles(chunk, TILE_WALL, 64, 82, 65, 83)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    # Yhorm throne room — throne pillars (DS3: massive throne room)
    fill_tiles(chunk, TILE_WALL, 82, 86, 83, 87)
    fill_tiles(chunk, TILE_WALL, 86, 90, 87, 91)
    fill_tiles(chunk, TILE_WALL, 78, 94, 79, 95)
    fill_tiles(chunk, TILE_WALL, 90, 84, 91, 85)
    fill_tiles(chunk, TILE_WALL, 84, 96, 85, 97)
    # Entry bridge — gargoyle perch stones (DS3: gargoyles attack on bridge)
    fill_tiles(chunk, TILE_WALL, 6, 10, 7, 11)
    fill_tiles(chunk, TILE_WALL, 12, 12, 13, 13)
    # Bonfire tower — spiral stair stones (DS3: Gilligan's ladder room)
    fill_tiles(chunk, TILE_WALL, 18, 12, 19, 13)
    fill_tiles(chunk, TILE_WALL, 26, 16, 27, 17)
    # Boss path bridge — fire sconce stones (DS3: fire vessels line the bridge)
    fill_tiles(chunk, TILE_WALL, 30, 12, 31, 13)
    fill_tiles(chunk, TILE_WALL, 34, 14, 35, 15)
    fill_tiles(chunk, TILE_WALL, 42, 10, 43, 11)
    fill_tiles(chunk, TILE_WALL, 46, 14, 47, 15)
    # Jailer room 1 — cage cell walls (DS3: prison cells with jailers)
    fill_tiles(chunk, TILE_WALL, 50, 8, 51, 9)
    fill_tiles(chunk, TILE_WALL, 56, 10, 57, 11)
    fill_tiles(chunk, TILE_WALL, 52, 16, 53, 17)
    fill_tiles(chunk, TILE_WALL, 60, 14, 61, 15)
    # Jailer room 2 — iron bar partitions (DS3: more prison cells)
    fill_tiles(chunk, TILE_WALL, 72, 8, 73, 9)
    fill_tiles(chunk, TILE_WALL, 78, 10, 79, 11)
    fill_tiles(chunk, TILE_WALL, 74, 16, 75, 17)
    fill_tiles(chunk, TILE_WALL, 82, 14, 83, 15)
    # Yhorm throne room — Storm Ruler pedestal area (DS3: giant throne room)
    fill_tiles(chunk, TILE_WALL, 100, 6, 101, 7)
    fill_tiles(chunk, TILE_WALL, 110, 10, 111, 11)
    fill_tiles(chunk, TILE_WALL, 104, 18, 105, 19)
    fill_tiles(chunk, TILE_WALL, 114, 22, 115, 23)
    fill_tiles(chunk, TILE_WALL, 98, 26, 99, 27)
    fill_tiles(chunk, TILE_WALL, 120, 14, 121, 15)
    # Explore path descent — crumbling steps (DS3: descent into lower capital)
    fill_tiles(chunk, TILE_WALL, 14, 24, 15, 25)
    fill_tiles(chunk, TILE_WALL, 18, 28, 19, 29)
    fill_tiles(chunk, TILE_WALL, 12, 32, 13, 33)
    # Upper ruins — broken archways (DS3: ruined city buildings)
    fill_tiles(chunk, TILE_WALL, 20, 36, 21, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 36, 38, 37, 39)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    # Church exterior — buttress stones (DS3: gothic church architecture)
    fill_tiles(chunk, TILE_WALL, 26, 68, 27, 69)
    fill_tiles(chunk, TILE_WALL, 34, 72, 35, 73)
    fill_tiles(chunk, TILE_WALL, 42, 76, 43, 77)
    fill_tiles(chunk, TILE_WALL, 48, 80, 49, 81)

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
    # Monstrosities of Sin (MonstrosityOfSin), Sewer Centipedes (SewerCentipede),
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
        # Ruins/streets — Gargoyle patrols + jailer (DS3: no Fire Witches here, those are in Irithyll)
        ("Gargoyle", 34, 52), ("Gargoyle", 50, 60),
        ("Jailer", 26, 56),
        ("Jailer", 24, 48), ("Jailer", 40, 55), ("Jailer", 32, 60),
        # Toxic pool — Sewer Centipedes (DS3: centipede creatures in flooded cells)
        ("SewerCentipede", 52, 64), ("SewerCentipede", 60, 72), ("SewerCentipede", 66, 68),
        # Crystal Lizards (wiki: 3 — one at hole jump, one in left tunnel, one down hallway)
        ("CrystalLizard", 56, 68), ("CrystalLizard", 62, 64), ("CrystalLizard", 56, 44),
        # Church — Monstrosities of Sin (wiki: 3 in the church + 1 in separate room = 4)
        ("MonstrosityOfSin", 30, 72), ("MonstrosityOfSin", 36, 78), ("MonstrosityOfSin", 42, 74),
        # Monstrosity of Sin — separate room above church (wiki: "single Monstrosity of Sin")
        ("MonstrosityOfSin", 48, 46),
        # Monstrosities of Sin in toxic pool (DS3: bloated creatures in flooded cells)
        ("MonstrosityOfSin", 58, 70), ("MonstrosityOfSin", 64, 74),
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

    # === MORE PROFANED CAPITAL DETAILS — DS3 fidelity ===
    # Entry bridge — stone arch from Irithyll Dungeon (DS3: narrow stone bridge)
    fill_tiles(chunk, TILE_WALL, 6, 10, 8, 12)
    fill_tiles(chunk, TILE_WALL, 12, 6, 14, 8)
    fill_tiles(chunk, TILE_WALL, 24, 8, 26, 10)
    # Bonfire tower — interior walls (DS3: Gilligan's body room)
    fill_tiles(chunk, TILE_WALL, 16, 10, 18, 12)
    fill_tiles(chunk, TILE_WALL, 22, 16, 24, 18)
    # Boss path — more bridge supports and ruined walls
    # DS3: stone bridge with gargoyle ambush, jailer rooms
    fill_tiles(chunk, TILE_WALL, 32, 12, 34, 14)
    fill_tiles(chunk, TILE_WALL, 42, 8, 44, 10)
    fill_tiles(chunk, TILE_WALL, 50, 14, 52, 16)
    # First jailer room — cell dividers (DS3: 4 jailers in white room)
    fill_tiles(chunk, TILE_WALL, 52, 8, 54, 10)
    fill_tiles(chunk, TILE_WALL, 60, 16, 62, 18)
    fill_tiles(chunk, TILE_WALL, 66, 10, 68, 12)
    fill_tiles(chunk, TILE_WALL, 54, 20, 56, 22)
    # Second jailer room — more cell walls
    # DS3: 2 mimics + 1 real chest, jailers guard
    fill_tiles(chunk, TILE_WALL, 72, 14, 74, 16)
    fill_tiles(chunk, TILE_WALL, 80, 18, 82, 20)
    fill_tiles(chunk, TILE_WALL, 86, 10, 88, 12)
    fill_tiles(chunk, TILE_WALL, 76, 22, 78, 24)
    # Upper ruins — more broken walls (DS3: ruined capital buildings)
    fill_tiles(chunk, TILE_WALL, 18, 36, 20, 38)
    fill_tiles(chunk, TILE_WALL, 26, 44, 28, 46)
    fill_tiles(chunk, TILE_WALL, 38, 36, 40, 38)
    fill_tiles(chunk, TILE_WALL, 32, 46, 34, 48)
    # Main ruins streets — building facades (DS3: ruined city streets)
    fill_tiles(chunk, TILE_WALL, 24, 54, 26, 56)
    fill_tiles(chunk, TILE_WALL, 36, 58, 38, 60)
    fill_tiles(chunk, TILE_WALL, 44, 52, 46, 54)
    fill_tiles(chunk, TILE_WALL, 52, 56, 54, 58)
    fill_tiles(chunk, TILE_WALL, 30, 62, 32, 64)
    fill_tiles(chunk, TILE_WALL, 46, 64, 48, 66)
    # Toxic pool — more stone islands and rubble
    # DS3: toxic swamp with stone platforms
    fill_tiles(chunk, TILE_WALL, 50, 66, 52, 68)
    fill_tiles(chunk, TILE_WALL, 62, 72, 64, 74)
    fill_tiles(chunk, TILE_WALL, 46, 76, 48, 78)
    fill_tiles(chunk, TILE_WALL, 66, 68, 68, 70)
    # Church — more interior pillars (DS3: church with monstrosities)
    fill_tiles(chunk, TILE_WALL, 30, 70, 32, 72)
    fill_tiles(chunk, TILE_WALL, 40, 76, 42, 78)
    fill_tiles(chunk, TILE_WALL, 34, 80, 36, 82)
    # Siegward's cell — cell walls (DS3: Siegward locked up)
    fill_tiles(chunk, TILE_WALL, 56, 48, 58, 50)
    fill_tiles(chunk, TILE_WALL, 64, 46, 66, 48)
    # Court sorcerer roof — roof tiles and pillars
    fill_tiles(chunk, TILE_WALL, 46, 40, 48, 42)
    fill_tiles(chunk, TILE_WALL, 56, 44, 58, 46)
    # Giant room — treasure room walls (DS3: giant guards treasure room)
    fill_tiles(chunk, TILE_WALL, 70, 58, 72, 60)
    fill_tiles(chunk, TILE_WALL, 80, 64, 82, 66)
    fill_tiles(chunk, TILE_WALL, 74, 68, 76, 70)
    fill_tiles(chunk, TILE_WALL, 86, 62, 88, 64)
    # Yhorm arena — more throne room pillars (DS3: massive throne room)
    fill_tiles(chunk, TILE_WALL, 92, 6, 94, 10)
    fill_tiles(chunk, TILE_WALL, 100, 22, 102, 26)
    fill_tiles(chunk, TILE_WALL, 110, 28, 112, 32)
    fill_tiles(chunk, TILE_WALL, 120, 8, 122, 12)
    fill_tiles(chunk, TILE_WALL, 130, 16, 132, 20)
    fill_tiles(chunk, TILE_WALL, 128, 26, 130, 30)

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
    # Dark stone floor in center of arena (DS3: no poison/swamp in Anor Londo)
    fill_tiles(chunk, TILE_GROUND, 116, 70, 140, 94)
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

    # ================================================================
    # ADDITIONAL DS3 ANOR LONDO — cathedral grandeur, golden architecture
    # ================================================================
    # Cathedral entrance — more grand pillars (DS3: massive stone pillars in entry hall)
    fill_tiles(chunk, TILE_WALL, 10, 30, 12, 34)
    fill_tiles(chunk, TILE_WALL, 18, 42, 20, 46)
    fill_tiles(chunk, TILE_WALL, 30, 48, 32, 52)
    fill_tiles(chunk, TILE_WALL, 8, 40, 10, 44)
    fill_tiles(chunk, TILE_WALL, 34, 38, 36, 42)
    # Royal avenue — knight statue bases (DS3: statues line the golden corridor)
    fill_tiles(chunk, TILE_WALL, 42, 32, 44, 36)
    fill_tiles(chunk, TILE_WALL, 56, 44, 58, 48)
    fill_tiles(chunk, TILE_WALL, 68, 38, 70, 42)
    fill_tiles(chunk, TILE_WALL, 78, 46, 80, 50)
    fill_tiles(chunk, TILE_WALL, 54, 50, 56, 54)
    fill_tiles(chunk, TILE_WALL, 66, 52, 68, 56)
    # Yorshka side path — invisible platform debris (DS3: drop down to invisible bridge)
    fill_tiles(chunk, TILE_WALL, 54, 60, 56, 64)
    fill_tiles(chunk, TILE_WALL, 62, 76, 64, 80)
    fill_tiles(chunk, TILE_WALL, 58, 88, 60, 92)
    fill_tiles(chunk, TILE_WALL, 66, 96, 68, 100)
    # Silver Knight hall — display alcove walls (DS3: ornate chamber with paintings)
    fill_tiles(chunk, TILE_WALL, 82, 28, 84, 32)
    fill_tiles(chunk, TILE_WALL, 94, 34, 96, 38)
    fill_tiles(chunk, TILE_WALL, 102, 42, 104, 46)
    fill_tiles(chunk, TILE_WALL, 112, 32, 114, 36)
    fill_tiles(chunk, TILE_WALL, 90, 48, 92, 52)
    fill_tiles(chunk, TILE_WALL, 110, 44, 112, 48)
    # Staircase corridor — wall sconces and debris (DS3: Silver Knight gauntlet)
    fill_tiles(chunk, TILE_WALL, 116, 36, 118, 40)
    fill_tiles(chunk, TILE_WALL, 126, 38, 128, 42)
    fill_tiles(chunk, TILE_WALL, 136, 44, 138, 48)
    fill_tiles(chunk, TILE_WALL, 140, 52, 142, 56)
    # Aldrich arena — throne room pillars (DS3: Gwyndolin's chamber with abyss)
    fill_tiles(chunk, TILE_WALL, 104, 58, 106, 62)
    fill_tiles(chunk, TILE_WALL, 114, 66, 116, 70)
    fill_tiles(chunk, TILE_WALL, 136, 62, 138, 66)
    fill_tiles(chunk, TILE_WALL, 142, 78, 144, 82)
    fill_tiles(chunk, TILE_WALL, 128, 96, 130, 100)
    fill_tiles(chunk, TILE_WALL, 148, 92, 150, 96)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 106)
    # Deep Accursed corner — web-covered debris (DS3: spider ambush in side room)
    fill_tiles(chunk, TILE_WALL, 96, 36, 98, 40)
    fill_tiles(chunk, TILE_WALL, 100, 44, 102, 48)

    # ================================================================
    # SESSION 9 FIDELITY PASS — AnorLondo architectural details
    # ================================================================
    # Main cathedral entrance — grand staircase debris (DS3: iconic Anor Londo steps)
    fill_tiles(chunk, TILE_WALL, 14, 40, 15, 41)
    fill_tiles(chunk, TILE_WALL, 18, 44, 19, 45)
    fill_tiles(chunk, TILE_WALL, 10, 48, 11, 49)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    fill_tiles(chunk, TILE_WALL, 16, 50, 17, 51)
    # Silver Knight hall — ornate pillar bases (DS3: massive pillars in great hall)
    fill_tiles(chunk, TILE_WALL, 28, 54, 29, 55)
    fill_tiles(chunk, TILE_WALL, 32, 58, 33, 59)
    fill_tiles(chunk, TILE_WALL, 24, 62, 25, 63)
    fill_tiles(chunk, TILE_WALL, 36, 52, 37, 53)
    fill_tiles(chunk, TILE_WALL, 30, 64, 31, 65)
    # Deacon corridor — burned banner stones (DS3: path to Aldrich with paintings)
    fill_tiles(chunk, TILE_WALL, 40, 68, 41, 69)
    fill_tiles(chunk, TILE_WALL, 44, 72, 45, 73)
    fill_tiles(chunk, TILE_WALL, 36, 76, 37, 77)
    fill_tiles(chunk, TILE_WALL, 48, 66, 49, 67)
    fill_tiles(chunk, TILE_WALL, 42, 78, 43, 79)
    # Gwyndolin chamber — illusion mirror fragments (DS3: Gwyndolin's chamber)
    fill_tiles(chunk, TILE_WALL, 52, 82, 53, 83)
    fill_tiles(chunk, TILE_WALL, 56, 86, 57, 87)
    fill_tiles(chunk, TILE_WALL, 48, 90, 49, 91)
    fill_tiles(chunk, TILE_WALL, 60, 80, 61, 81)
    fill_tiles(chunk, TILE_WALL, 54, 92, 55, 93)
    # Darkmoon Tomb — candle alcoves (DS3: Darkmoon covenant area)
    fill_tiles(chunk, TILE_WALL, 64, 96, 65, 97)
    fill_tiles(chunk, TILE_WALL, 68, 100, 69, 101)
    fill_tiles(chunk, TILE_WALL, 60, 104, 61, 105)
    fill_tiles(chunk, TILE_WALL, 72, 94, 73, 95)
    # Aldrich arena — consumed throne room debris (DS3: Gwyndolin consumed by Aldrich)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 126, 84, 127, 85)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 130, 78, 131, 79)
    fill_tiles(chunk, TILE_WALL, 122, 90, 123, 91)
    # Man Grub corridors — slime-coated wall stones (DS3: Man Grubs roam the halls)
    fill_tiles(chunk, TILE_WALL, 76, 60, 77, 61)
    fill_tiles(chunk, TILE_WALL, 80, 64, 81, 65)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 84, 58, 85, 59)
    fill_tiles(chunk, TILE_WALL, 78, 70, 79, 71)

        # --- Spawn from Irithyll rotating staircase ---
    spawn_px, spawn_py = 10 * 16, 38 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires --- DS3: Anor Londo, Prison Tower, Aldrich Devourer of Gods
    entities.append(make_entity("Bonfire", 10 * 16, 38 * 16))
    entities.append(make_entity("Bonfire", 62 * 16, 90 * 16))   # Prison Tower (invisible bridge area)
    entities.append(make_entity("Bonfire", 128 * 16, 85 * 16))  # Aldrich boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 128 * 16, 78 * 16))

    # --- Enemies — DS3 Anor Londo: Silver Knights, Giant Slave (archer),
    # Deep Accursed, Deacons (pyromancers + 3 before fog), Rotten Flesh of Aldrich (slimes)
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
        # Silver Knight archers in upper hallway — DS3: "two archer Silver Knights"
        ("SilverKnight", 108, 34), ("SilverKnight", 118, 36),
        # Giant Slave — giant archer on upper level (wiki: Giant Slave enemy)
        ("GiantSlave", 38, 52),
        # Main chamber — Deacon pyromancers casting fireballs from other side
        ("Deacon", 55, 45), ("Deacon", 68, 40), ("Deacon", 70, 46),
        # Additional Deacon pyromancers in dark chamber (wiki: "deacon pyromancers and slimes")
        ("Deacon", 72, 52), ("Deacon", 76, 48),
        # Main chamber — Rotten Flesh of Aldrich / slimes (wiki: "dispatch slimes and deacons")
        ("ManGrub", 142, 75), ("ManGrub", 148, 82), ("ManGrub", 136, 68),
        ("ManGrub", 124, 88), ("ManGrub", 132, 92),
        # Additional slimes in dark corners of main hall
        ("ManGrub", 130, 65), ("ManGrub", 115, 72),
        ("ManGrub", 140, 95), ("ManGrub", 112, 80),  # More slimes in Aldrich arena corners
        # Corner — Deep Accursed at revolving switch (wiki: "Deep Accursed waiting for you")
        ("DeepAccursed", 100, 40),
        # Hallway to fog gate — 3 Deacons (wiki: "three enemies from Deacons of the Deep boss fight")
        ("Deacon", 125, 38), ("Deacon", 135, 44), ("Deacon", 138, 50),
        # Crystal Lizard near Yorshka path (DS3: crystal lizard on tower ledge)
        ("CrystalLizard", 56, 84),
        # Boss — Aldrich, Devourer of Gods
        ("MiniBoss", 128, 78),                                      # Aldrich boss entity
        # Additional DS3 enemies for fidelity
        ("SilverKnight", 28, 48),                                   # DS3: knight in side corridor
        ("SilverKnight", 58, 54),                                   # DS3: knight in royal chamber
        ("Deacon", 65, 55),                                         # DS3: deacon in upper chamber
        ("Deacon", 78, 52),                                         # DS3: deacon near dark room
        ("Deacon", 82, 58),                                         # DS3: deacon in dark corners
        ("ManGrub", 145, 88),                                       # DS3: slime near Aldrich arena
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
            "Hello again, we meet at last in this grand cathedral|I am Anri of Astora|Will you help me defeat Aldrich, together?|I cannot do this alone"),
    ]))
    # Company Captain Yorshka — Darkmoon Tomb, reached from Prison Tower bonfire
    entities.append(make_entity("Npc", 62 * 16, 92 * 16, [
        make_field("name", "String", "Company Captain Yorshka"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#E0E8F0"),
        make_field("dialogue", "String",
            "I am Yorshka, Captain of the Darkmoon Knights|The Darkmoon remains true to its duty, even now|Will you swear the oath of the Darkmoon?|Then let us join hands, and take the oath"),
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

    # === MORE ANOR LONDO DETAILS — DS3 fidelity ===
    # Cathedral entrance — grand archway stones (DS3: massive cathedral doors)
    fill_tiles(chunk, TILE_WALL, 8, 28, 10, 32)
    fill_tiles(chunk, TILE_WALL, 32, 42, 34, 46)
    fill_tiles(chunk, TILE_WALL, 24, 50, 26, 54)
    fill_tiles(chunk, TILE_WALL, 36, 48, 38, 52)
    # Royal avenue — more decorative pillars (DS3: avenue lined with columns)
    fill_tiles(chunk, TILE_WALL, 44, 34, 46, 37)
    fill_tiles(chunk, TILE_WALL, 58, 38, 60, 41)
    fill_tiles(chunk, TILE_WALL, 70, 35, 72, 38)
    fill_tiles(chunk, TILE_WALL, 52, 52, 54, 55)
    fill_tiles(chunk, TILE_WALL, 66, 50, 68, 53)
    fill_tiles(chunk, TILE_WALL, 76, 45, 78, 48)
    # Silver Knight hall — council chamber details (DS3: large hall with paintings)
    fill_tiles(chunk, TILE_WALL, 82, 32, 84, 35)
    fill_tiles(chunk, TILE_WALL, 90, 45, 92, 48)
    fill_tiles(chunk, TILE_WALL, 104, 42, 106, 45)
    fill_tiles(chunk, TILE_WALL, 112, 38, 114, 41)
    fill_tiles(chunk, TILE_WALL, 95, 48, 97, 51)
    # Staircase corridor — more railing sections (DS3: narrow staircase with Silver Knights)
    fill_tiles(chunk, TILE_WALL, 116, 35, 118, 38)
    fill_tiles(chunk, TILE_WALL, 124, 40, 126, 43)
    fill_tiles(chunk, TILE_WALL, 130, 45, 132, 48)
    fill_tiles(chunk, TILE_WALL, 136, 50, 138, 53)
    # Aldrich arena — more cathedral columns (DS3: Gwynevere's chamber, massive pillars)
    fill_tiles(chunk, TILE_WALL, 105, 70, 107, 74)
    fill_tiles(chunk, TILE_WALL, 115, 65, 117, 68)
    fill_tiles(chunk, TILE_WALL, 145, 75, 147, 78)
    fill_tiles(chunk, TILE_WALL, 150, 85, 152, 88)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 98)
    fill_tiles(chunk, TILE_WALL, 120, 85, 122, 88)
    # Yorshka path — more invisible platform stones (DS3: narrow drop-down path)
    fill_tiles(chunk, TILE_WALL, 54, 78, 56, 80)
    fill_tiles(chunk, TILE_WALL, 64, 82, 66, 84)
    fill_tiles(chunk, TILE_WALL, 60, 92, 62, 94)
    fill_tiles(chunk, TILE_WALL, 70, 90, 72, 92)
    # Additional Anor Londo DS3 details
    # Cathedral entrance — more grand archway stones (DS3: massive doors to Anor Londo)
    fill_tiles(chunk, TILE_WALL, 14, 36, 16, 39)
    fill_tiles(chunk, TILE_WALL, 22, 42, 24, 45)
    # Deacon corridor walls (DS3: deacons line the path to the cathedral)
    fill_tiles(chunk, TILE_WALL, 38, 55, 40, 58)
    fill_tiles(chunk, TILE_WALL, 46, 60, 48, 63)
    # Royal avenue — stone bench debris (DS3: ruined avenue with Silver Knight patrols)
    fill_tiles(chunk, TILE_WALL, 50, 44, 52, 46)
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 54)
    # Silver Knight hall — display alcoves (DS3: paintings and armor displays)
    fill_tiles(chunk, TILE_WALL, 86, 48, 88, 50)
    fill_tiles(chunk, TILE_WALL, 102, 36, 104, 38)
    # Deep Accursed corner — web-covered debris (DS3: spider-like enemy lurks in corner)
    fill_tiles(chunk, TILE_WALL, 96, 42, 98, 44)
    fill_tiles(chunk, TILE_WALL, 108, 44, 110, 46)
    # Aldrich arena — more throne room pillars (DS3: Gwyndolin's chamber with massive columns)
    fill_tiles(chunk, TILE_WALL, 122, 80, 124, 83)
    fill_tiles(chunk, TILE_WALL, 148, 90, 150, 93)
    fill_tiles(chunk, TILE_WALL, 140, 78, 142, 80)
    fill_tiles(chunk, TILE_WALL, 115, 90, 117, 92)
    # Yorshka's church — altar and nave walls (DS3: Darkmoon Tomb)
    fill_tiles(chunk, TILE_WALL, 48, 84, 50, 86)
    fill_tiles(chunk, TILE_WALL, 66, 88, 68, 90)
    fill_tiles(chunk, TILE_WALL, 56, 94, 58, 96)

    # === SESSION 8 FIDELITY PASS — Anor Londo ===
    # Cathedral entrance — grand staircase debris (DS3: massive steps to cathedral doors)
    fill_tiles(chunk, TILE_WALL, 10, 38, 11, 40)
    fill_tiles(chunk, TILE_WALL, 18, 40, 19, 42)
    fill_tiles(chunk, TILE_WALL, 8, 32, 9, 34)
    # Deacon corridor — burned banners and ash (DS3: corrupted passage to Aldrich)
    fill_tiles(chunk, TILE_WALL, 34, 52, 35, 54)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 60)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 58)
    fill_tiles(chunk, TILE_WALL, 30, 60, 31, 62)
    # Royal avenue — collapsed archway stones (DS3: grand avenue with Silver Knights)
    fill_tiles(chunk, TILE_WALL, 56, 40, 57, 42)
    fill_tiles(chunk, TILE_WALL, 68, 48, 69, 50)
    fill_tiles(chunk, TILE_WALL, 62, 50, 63, 52)
    fill_tiles(chunk, TILE_WALL, 76, 44, 77, 46)
    # Silver Knight hall — ornate pillar bases (DS3: grand hall with mounted banners)
    fill_tiles(chunk, TILE_WALL, 82, 50, 83, 52)
    fill_tiles(chunk, TILE_WALL, 94, 46, 95, 48)
    fill_tiles(chunk, TILE_WALL, 88, 54, 89, 56)
    fill_tiles(chunk, TILE_WALL, 100, 40, 101, 42)
    # Gwyndolin chamber — illusion-shattered mirror fragments (DS3: Aldrich's lair)
    fill_tiles(chunk, TILE_WALL, 118, 84, 119, 86)
    fill_tiles(chunk, TILE_WALL, 144, 86, 145, 88)
    fill_tiles(chunk, TILE_WALL, 130, 92, 131, 94)
    fill_tiles(chunk, TILE_WALL, 138, 76, 139, 78)
    # Darkmoon Tomb — candle alcoves and prayer stones (DS3: hidden covenant area)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 90)
    fill_tiles(chunk, TILE_WALL, 62, 82, 63, 84)
    fill_tiles(chunk, TILE_WALL, 52, 90, 53, 92)
    fill_tiles(chunk, TILE_WALL, 70, 92, 71, 94)
    # SESSION 10 FIDELITY PASS — Anor Londo
    # Additional DS3-faithful terrain: grand staircase debris, silver knight hall
    # pillars, Gwyndolin mirror fragments, Darkmoon candle clusters, Aldrich arena
    # Grand staircase — step debris (DS3: iconic grand staircase with broken steps)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 29)
    fill_tiles(chunk, TILE_WALL, 38, 32, 39, 33)
    fill_tiles(chunk, TILE_WALL, 44, 30, 45, 31)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 35)
    fill_tiles(chunk, TILE_WALL, 56, 32, 57, 33)
    # Silver Knight hall — pillar bases (DS3: pillars in great hall)
    fill_tiles(chunk, TILE_WALL, 62, 38, 63, 39)
    fill_tiles(chunk, TILE_WALL, 68, 42, 69, 43)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 45)
    fill_tiles(chunk, TILE_WALL, 70, 40, 71, 41)
    fill_tiles(chunk, TILE_WALL, 66, 36, 67, 37)
    # Gwyndolin chamber — mirror fragments (DS3: Dark Sun Gwyndolin's chamber)
    fill_tiles(chunk, TILE_WALL, 76, 48, 77, 49)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 53)
    fill_tiles(chunk, TILE_WALL, 78, 54, 79, 55)
    fill_tiles(chunk, TILE_WALL, 84, 50, 85, 51)
    # Darkmoon chamber — candle clusters (DS3: Darkmoon chamber with candles)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    fill_tiles(chunk, TILE_WALL, 94, 60, 95, 61)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 63)
    fill_tiles(chunk, TILE_WALL, 96, 58, 97, 59)
    # Aldrich arena — cathedral debris (DS3: Aldrich's cathedral arena)
    fill_tiles(chunk, TILE_WALL, 100, 66, 101, 67)
    fill_tiles(chunk, TILE_WALL, 106, 70, 107, 71)
    fill_tiles(chunk, TILE_WALL, 102, 72, 103, 73)
    fill_tiles(chunk, TILE_WALL, 108, 68, 109, 69)
    fill_tiles(chunk, TILE_WALL, 104, 64, 105, 65)
    fill_tiles(chunk, TILE_WALL, 110, 72, 111, 73)
    # Deacon corridor — cathedral stones (DS3: Deacons patrol corridors)
    fill_tiles(chunk, TILE_WALL, 114, 76, 115, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 118, 78, 119, 79)
    fill_tiles(chunk, TILE_WALL, 124, 82, 125, 83)
    # Man Grub area — ooze debris (DS3: Man Grubs in cathedral corridors)
    fill_tiles(chunk, TILE_WALL, 36, 36, 37, 37)
    fill_tiles(chunk, TILE_WALL, 42, 40, 43, 41)
    fill_tiles(chunk, TILE_WALL, 48, 38, 49, 39)
    fill_tiles(chunk, TILE_WALL, 54, 42, 55, 43)
    # Exterior — silver knight roof debris (DS3: knights patrol rooftops)
    fill_tiles(chunk, TILE_WALL, 128, 84, 129, 85)
    fill_tiles(chunk, TILE_WALL, 134, 88, 135, 89)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 87)


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
    # ADDITIONAL DS3 CASTLE ARCHITECTURE — Lothric Castle fidelity
    # ================================================================
    # Castle gate — entrance arch walls (DS3: grand stone archway from Anor Londo)
    fill_tiles(chunk, TILE_WALL, 8, 22, 10, 26)
    fill_tiles(chunk, TILE_WALL, 20, 32, 22, 36)
    fill_tiles(chunk, TILE_WALL, 16, 38, 18, 42)
    fill_tiles(chunk, TILE_WALL, 30, 40, 32, 44)
    # Outer corridor — stone arches and buttresses (DS3: vaulted corridor)
    fill_tiles(chunk, TILE_WALL, 34, 24, 36, 28)
    fill_tiles(chunk, TILE_WALL, 52, 28, 54, 32)
    fill_tiles(chunk, TILE_WALL, 60, 34, 62, 38)
    fill_tiles(chunk, TILE_WALL, 44, 40, 46, 44)
    fill_tiles(chunk, TILE_WALL, 55, 42, 57, 46)
    # Dragon barracks — dragon ribcage and skull debris (DS3: two dead wyverns)
    fill_tiles(chunk, TILE_WALL, 70, 22, 71, 24)
    fill_tiles(chunk, TILE_WALL, 74, 26, 75, 28)
    fill_tiles(chunk, TILE_WALL, 80, 20, 81, 22)
    fill_tiles(chunk, TILE_WALL, 86, 24, 87, 26)
    fill_tiles(chunk, TILE_WALL, 90, 18, 91, 20)
    fill_tiles(chunk, TILE_WALL, 94, 30, 95, 32)
    fill_tiles(chunk, TILE_WALL, 78, 32, 79, 34)
    fill_tiles(chunk, TILE_WALL, 84, 36, 85, 38)
    # Inner stairs — narrow passage walls (DS3: tight staircase with hollows)
    fill_tiles(chunk, TILE_WALL, 96, 36, 98, 38)
    fill_tiles(chunk, TILE_WALL, 100, 42, 102, 44)
    fill_tiles(chunk, TILE_WALL, 108, 46, 110, 48)
    fill_tiles(chunk, TILE_WALL, 114, 52, 116, 54)
    fill_tiles(chunk, TILE_WALL, 120, 56, 122, 58)
    # Arena perimeter — Dragonslayer Armour fights on castle wall (DS3: open parapet)
    fill_tiles(chunk, TILE_WALL, 112, 62, 114, 65)
    fill_tiles(chunk, TILE_WALL, 130, 55, 132, 58)
    fill_tiles(chunk, TILE_WALL, 148, 60, 150, 63)
    fill_tiles(chunk, TILE_WALL, 155, 72, 157, 75)
    fill_tiles(chunk, TILE_WALL, 148, 82, 150, 85)
    fill_tiles(chunk, TILE_WALL, 135, 85, 137, 88)
    fill_tiles(chunk, TILE_WALL, 120, 82, 122, 85)
    fill_tiles(chunk, TILE_WALL, 112, 78, 114, 80)
    # Garden side path — overgrown ruin walls (DS3: consumed garden area)
    fill_tiles(chunk, TILE_WALL, 36, 48, 38, 50)
    fill_tiles(chunk, TILE_WALL, 44, 56, 46, 58)
    fill_tiles(chunk, TILE_WALL, 52, 62, 54, 64)
    fill_tiles(chunk, TILE_WALL, 48, 66, 50, 68)
    # Grand Archives approach — bookshelves and stone arches
    fill_tiles(chunk, TILE_WALL, 150, 58, 152, 60)
    fill_tiles(chunk, TILE_WALL, 154, 64, 156, 66)

    # ================================================================
    # ADDITIONAL DS3 LOTHRIC CASTLE DETAILS — wyvern bones, church, parapets
    # ================================================================
    # Castle gate — fortified entry (DS3: grand stone archway with Lothric banners)
    fill_tiles(chunk, TILE_WALL, 6, 22, 8, 24)
    fill_tiles(chunk, TILE_WALL, 12, 26, 14, 28)
    fill_tiles(chunk, TILE_WALL, 22, 28, 24, 30)
    fill_tiles(chunk, TILE_WALL, 26, 36, 28, 38)
    fill_tiles(chunk, TILE_WALL, 15, 40, 17, 42)
    fill_tiles(chunk, TILE_WALL, 32, 42, 34, 44)
    # Dragon barracks — wyvern ribcage arches and burning debris (DS3: two dead wyverns, one with Pus of Man)
    fill_tiles(chunk, TILE_WALL, 60, 14, 62, 16)
    fill_tiles(chunk, TILE_WALL, 64, 20, 66, 22)
    fill_tiles(chunk, TILE_WALL, 84, 14, 86, 16)
    fill_tiles(chunk, TILE_WALL, 88, 20, 90, 22)
    fill_tiles(chunk, TILE_WALL, 96, 26, 98, 28)
    fill_tiles(chunk, TILE_WALL, 100, 30, 102, 32)
    fill_tiles(chunk, TILE_WALL, 78, 26, 80, 28)
    fill_tiles(chunk, TILE_WALL, 72, 34, 74, 36)
    fill_tiles(chunk, TILE_WALL, 68, 10, 70, 12)
    # Church interior — stone pews and altar walls (DS3: Emma's cathedral with Lothric banners)
    fill_tiles(chunk, TILE_WALL, 120, 60, 122, 62)
    fill_tiles(chunk, TILE_WALL, 126, 64, 128, 66)
    fill_tiles(chunk, TILE_WALL, 132, 70, 134, 72)
    fill_tiles(chunk, TILE_WALL, 136, 74, 138, 76)
    fill_tiles(chunk, TILE_WALL, 124, 68, 126, 70)
    fill_tiles(chunk, TILE_WALL, 130, 66, 132, 68)
    # Inner stairs — narrow castle passage (DS3: tight spiral staircase with hollows)
    fill_tiles(chunk, TILE_WALL, 106, 40, 108, 42)
    fill_tiles(chunk, TILE_WALL, 118, 50, 120, 52)
    # Arena perimeter — castle parapet walls (DS3: Dragonslayer Armour on open castle bridge)
    fill_tiles(chunk, TILE_WALL, 116, 70, 118, 72)
    fill_tiles(chunk, TILE_WALL, 140, 76, 142, 78)
    fill_tiles(chunk, TILE_WALL, 146, 80, 148, 82)
    fill_tiles(chunk, TILE_WALL, 125, 85, 127, 87)
    fill_tiles(chunk, TILE_WALL, 150, 74, 152, 76)
    # Grand Archives approach — stone staircase and fountain (DS3: grand fountain before Archives)
    fill_tiles(chunk, TILE_WALL, 144, 56, 146, 58)
    fill_tiles(chunk, TILE_WALL, 148, 62, 150, 64)
    fill_tiles(chunk, TILE_WALL, 152, 70, 154, 72)
    # Garden path — overgrown arches and crumbling walls (DS3: consumed garden ruins)
    fill_tiles(chunk, TILE_WALL, 34, 54, 36, 56)
    fill_tiles(chunk, TILE_WALL, 42, 60, 44, 62)
    fill_tiles(chunk, TILE_WALL, 54, 64, 56, 66)

    # === SESSION 6 FIDELITY PASS — Lothric Castle ===
    # Castle gate — more entry fortification (DS3: grand Lothric Castle gate)
    fill_tiles(chunk, TILE_WALL, 8, 18, 10, 20)
    fill_tiles(chunk, TILE_WALL, 22, 36, 24, 38)
    fill_tiles(chunk, TILE_WALL, 14, 42, 16, 44)
    fill_tiles(chunk, TILE_WALL, 28, 44, 30, 46)
    # Outer corridor — more stone arches (DS3: vaulted corridor with knight statues)
    fill_tiles(chunk, TILE_WALL, 36, 30, 38, 32)
    fill_tiles(chunk, TILE_WALL, 46, 36, 48, 38)
    fill_tiles(chunk, TILE_WALL, 58, 38, 60, 40)
    fill_tiles(chunk, TILE_WALL, 50, 44, 52, 46)
    fill_tiles(chunk, TILE_WALL, 40, 42, 42, 44)
    # Dragon barracks — more wyvern debris (DS3: massive dragon skeletons)
    fill_tiles(chunk, TILE_WALL, 62, 16, 64, 18)
    fill_tiles(chunk, TILE_WALL, 66, 22, 68, 24)
    fill_tiles(chunk, TILE_WALL, 82, 28, 84, 30)
    fill_tiles(chunk, TILE_WALL, 92, 20, 94, 22)
    fill_tiles(chunk, TILE_WALL, 98, 32, 100, 34)
    fill_tiles(chunk, TILE_WALL, 76, 34, 78, 36)
    # Inner stairs — more passage walls (DS3: tight castle staircase)
    fill_tiles(chunk, TILE_WALL, 104, 44, 106, 46)
    fill_tiles(chunk, TILE_WALL, 112, 48, 114, 50)
    fill_tiles(chunk, TILE_WALL, 116, 54, 118, 56)
    fill_tiles(chunk, TILE_WALL, 122, 58, 124, 60)
    # Arena — more parapet walls (DS3: open castle wall bridge)
    fill_tiles(chunk, TILE_WALL, 110, 66, 112, 68)
    fill_tiles(chunk, TILE_WALL, 126, 62, 128, 64)
    fill_tiles(chunk, TILE_WALL, 144, 66, 146, 68)
    fill_tiles(chunk, TILE_WALL, 152, 76, 154, 78)
    fill_tiles(chunk, TILE_WALL, 142, 84, 144, 86)
    fill_tiles(chunk, TILE_WALL, 118, 80, 120, 82)
    fill_tiles(chunk, TILE_WALL, 132, 88, 134, 90)
    fill_tiles(chunk, TILE_WALL, 150, 88, 152, 90)
    # Garden side path — more overgrown walls (DS3: consumed garden)
    fill_tiles(chunk, TILE_WALL, 38, 56, 40, 58)
    fill_tiles(chunk, TILE_WALL, 46, 64, 48, 66)
    fill_tiles(chunk, TILE_WALL, 56, 60, 58, 62)
    # Grand Archives approach — stone pillars (DS3: grand fountain courtyard)
    fill_tiles(chunk, TILE_WALL, 146, 60, 148, 62)
    fill_tiles(chunk, TILE_WALL, 156, 68, 158, 70)

    # ================================================================
    # SESSION 9 FIDELITY PASS — LothricCastle architectural details
    # ================================================================
    # Dragon courtyard — burnt stone debris (DS3: dragon breath scorches area)
    fill_tiles(chunk, TILE_WALL, 20, 34, 21, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 16, 42, 17, 43)
    fill_tiles(chunk, TILE_WALL, 28, 30, 29, 31)
    fill_tiles(chunk, TILE_WALL, 22, 46, 23, 47)
    # Lothric Knight barracks — weapon rack stones (DS3: knight garrison area)
    fill_tiles(chunk, TILE_WALL, 36, 50, 37, 51)
    fill_tiles(chunk, TILE_WALL, 40, 54, 41, 55)
    fill_tiles(chunk, TILE_WALL, 32, 58, 33, 59)
    fill_tiles(chunk, TILE_WALL, 44, 48, 45, 49)
    fill_tiles(chunk, TILE_WALL, 38, 62, 39, 63)
    # Wyvern perch — scorched tower stones (DS3: wyvern roosts on castle wall)
    fill_tiles(chunk, TILE_WALL, 50, 40, 51, 41)
    fill_tiles(chunk, TILE_WALL, 54, 44, 55, 45)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 58, 38, 59, 39)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    # Grand Archives fountain courtyard — ornate fountain stones
    fill_tiles(chunk, TILE_WALL, 142, 56, 143, 57)
    fill_tiles(chunk, TILE_WALL, 150, 64, 151, 65)
    fill_tiles(chunk, TILE_WALL, 138, 68, 139, 69)
    fill_tiles(chunk, TILE_WALL, 154, 60, 155, 61)
    # Dragonslayer Armour arena — shattered monument stones (DS3: storm-swept rooftop)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 126, 84, 127, 85)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 130, 76, 131, 77)
    fill_tiles(chunk, TILE_WALL, 122, 90, 123, 91)
    # Dancer's cathedral — stained glass debris (DS3: cathedral with stained glass)
    fill_tiles(chunk, TILE_WALL, 60, 28, 61, 29)
    fill_tiles(chunk, TILE_WALL, 66, 32, 67, 33)
    fill_tiles(chunk, TILE_WALL, 56, 36, 57, 37)
    fill_tiles(chunk, TILE_WALL, 70, 26, 71, 27)
    fill_tiles(chunk, TILE_WALL, 64, 38, 65, 39)

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
    entities.append(make_entity("Enemy", 132 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "MiniBoss")]))  # Dragonslayer Armour

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
        # Additional DS3 Lothric Castle enemies — more knights, dogs, hollows (DS3: dense with enemies)
        ("LothricKnight", 22, 32), ("LothricKnight", 42, 38),       # Knights at gate courtyard
        ("Dog", 32, 34), ("Dog", 46, 42), ("Dog", 52, 48),         # DS3: dogs in castle corridors
        ("Dog", 65, 30), ("Dog", 72, 25), ("Dog", 98, 38),         # DS3: 8 dogs total
        ("LothricKnight", 75, 30), ("LothricKnight", 82, 26),      # Knights patrolling wyvern area
        ("LothricKnight", 95, 36), ("LothricKnight", 108, 44),     # Knights on inner stairs
        ("HollowSoldier", 60, 36), ("HollowSoldier", 85, 32),      # More hollows in barracks
        ("LothricKnight", 130, 64), ("LothricKnight", 136, 68),    # Knights near arena
        ("DarkMage", 122, 60),                                        # Priest healing knights near arena
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
            "I am Emma, High Priestess of Lothric|The Prince has refused his duty as a Lord of Cinder|Please, I beg of you, save Prince Lothric|He must be made to see his duty through"),
    ]))
    # Eygon of Carim — summon sign near Dragonslayer Armour arena approach
    # DS3: can be summoned for Dragonslayer Armour if Irina quest is in correct state
    entities.append(make_entity("Npc", 115 * 16, 56 * 16, [
        make_field("name", "String", "Eygon of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A4A4A"),
        make_field("dialogue", "String",
            "What do you want? I am Eygon of Carim|I am bound by duty to protect Irina|Keep your hands off her|She is under my protection"),
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
    # SESSION 10 FIDELITY PASS — Lothric Castle
    # Additional DS3-faithful terrain: dragon courtyard scorch debris, knight barracks,
    # wyvern perch stones, Dancer cathedral pillars, Grand Archives approach
    # Dragon courtyard — scorch debris (DS3: dragon burns the courtyard)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 56, 55, 57)
    fill_tiles(chunk, TILE_WALL, 60, 54, 61, 55)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 59)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    # Knight barracks — barrack walls (DS3: Lothric Knight barracks)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 74, 58, 75, 59)
    fill_tiles(chunk, TILE_WALL, 80, 64, 81, 65)
    fill_tiles(chunk, TILE_WALL, 72, 66, 73, 67)
    # Wyvern perch — cliff stones (DS3: wyvern perches on castle wall)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    fill_tiles(chunk, TILE_WALL, 94, 60, 95, 61)
    fill_tiles(chunk, TILE_WALL, 84, 62, 85, 63)
    fill_tiles(chunk, TILE_WALL, 90, 58, 91, 59)
    # Dancer cathedral — cathedral pillars (DS3: grand cathedral entrance)
    fill_tiles(chunk, TILE_WALL, 100, 68, 101, 69)
    fill_tiles(chunk, TILE_WALL, 106, 72, 107, 73)
    fill_tiles(chunk, TILE_WALL, 112, 70, 113, 71)
    fill_tiles(chunk, TILE_WALL, 104, 74, 105, 75)
    fill_tiles(chunk, TILE_WALL, 110, 76, 111, 77)
    # Grand Archives approach — book and crystal debris (DS3: path to archives)
    fill_tiles(chunk, TILE_WALL, 118, 80, 119, 81)
    fill_tiles(chunk, TILE_WALL, 124, 84, 125, 85)
    fill_tiles(chunk, TILE_WALL, 130, 82, 131, 83)
    fill_tiles(chunk, TILE_WALL, 122, 88, 123, 89)
    fill_tiles(chunk, TILE_WALL, 128, 86, 129, 87)
    # Castle ramparts — wall stones (DS3: castle battlements)
    fill_tiles(chunk, TILE_WALL, 36, 54, 37, 55)
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 51)
    fill_tiles(chunk, TILE_WALL, 56, 48, 57, 49)
    fill_tiles(chunk, TILE_WALL, 64, 52, 65, 53)
    # Lothric throne room — throne debris (DS3: Lothric's empty throne room)
    fill_tiles(chunk, TILE_WALL, 134, 90, 135, 91)
    fill_tiles(chunk, TILE_WALL, 140, 88, 141, 89)
    fill_tiles(chunk, TILE_WALL, 136, 94, 137, 95)
    fill_tiles(chunk, TILE_WALL, 132, 92, 133, 93)


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
    # SESSION 9 FIDELITY PASS — GrandArchives architectural details
    # ================================================================
    # Main hall — bookshelf alcove walls (DS3: towering bookshelves)
    fill_tiles(chunk, TILE_WALL, 28, 130, 29, 131)
    fill_tiles(chunk, TILE_WALL, 34, 134, 35, 135)
    fill_tiles(chunk, TILE_WALL, 22, 138, 23, 139)
    fill_tiles(chunk, TILE_WALL, 40, 126, 41, 127)
    fill_tiles(chunk, TILE_WALL, 30, 142, 31, 143)
    # Wax pool room — candle cluster stones (DS3: wax-scholar pool area)
    fill_tiles(chunk, TILE_WALL, 48, 118, 49, 119)
    fill_tiles(chunk, TILE_WALL, 54, 122, 55, 123)
    fill_tiles(chunk, TILE_WALL, 44, 126, 45, 127)
    fill_tiles(chunk, TILE_WALL, 56, 114, 57, 115)
    # Crystal sages room — crystal formation debris (DS3: crystal growths in archives)
    fill_tiles(chunk, TILE_WALL, 62, 100, 63, 101)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    fill_tiles(chunk, TILE_WALL, 58, 104, 59, 105)
    fill_tiles(chunk, TILE_WALL, 72, 92, 73, 93)
    # Twin Princes chamber — throne debris (DS3: Lothric's chamber with throne)
    fill_tiles(chunk, TILE_WALL, 100, 12, 101, 13)
    fill_tiles(chunk, TILE_WALL, 104, 16, 105, 17)
    fill_tiles(chunk, TILE_WALL, 96, 18, 97, 19)
    fill_tiles(chunk, TILE_WALL, 108, 10, 109, 11)
    # Winged Knight corridor — armor stand stones (DS3: suits of armor in halls)
    fill_tiles(chunk, TILE_WALL, 78, 28, 79, 29)
    fill_tiles(chunk, TILE_WALL, 82, 32, 83, 33)
    fill_tiles(chunk, TILE_WALL, 74, 36, 75, 37)
    fill_tiles(chunk, TILE_WALL, 86, 24, 87, 25)
    # Rooftop — gargoyle perch stones (DS3: gargoyles patrol the rooftops)
    fill_tiles(chunk, TILE_WALL, 90, 14, 91, 15)
    fill_tiles(chunk, TILE_WALL, 94, 18, 95, 19)
    fill_tiles(chunk, TILE_WALL, 88, 22, 89, 23)
    # Bridge shortcut — broken railing stones (DS3: lift bridge connects areas)
    fill_tiles(chunk, TILE_WALL, 130, 24, 131, 25)
    fill_tiles(chunk, TILE_WALL, 134, 28, 135, 29)
    fill_tiles(chunk, TILE_WALL, 126, 30, 127, 31)

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
        # DS3: ~10 scholars throughout, wax-headed, cast magic and melee
        ("DarkMage", 45, 130), ("DarkMage", 62, 95),
        ("DarkMage", 85, 40), ("DarkMage", 75, 28),
        ("DarkMage", 50, 100), ("DarkMage", 55, 75),
        ("DarkMage", 48, 85), ("DarkMage", 72, 55),
        ("DarkMage", 62, 112),  # Mage Kriemhild (hostile NPC, DarkMage type)
        # Hollow Slaves (Thrall — drop from ceilings, walls)
        # DS3: ambush enemies throughout the library, NOT Hollow Soldiers
        ("HollowSlave", 42, 132), ("HollowSlave", 55, 98),
        ("HollowSlave", 68, 108), ("HollowSlave", 75, 50),
        ("HollowSlave", 62, 65), ("HollowSlave", 40, 138),
        ("HollowSlave", 52, 92), ("HollowSlave", 58, 80),
        # Lothric Knights — including red-eyed knight guard
        ("LothricKnight", 70, 92), ("LothricKnight", 88, 45),
        ("LothricKnight", 55, 65), ("LothricKnight", 78, 48),
        # Ascended Winged Knights (golden, 3 — DS3: drop Titanite Slab when all 3 killed)
        ("AscendedWingedKnight", 82, 38), ("AscendedWingedKnight", 92, 35),
        ("AscendedWingedKnight", 75, 32),
        # Boreal Outrider Knight (DS3: dead/frozen in entry, drops Outrider Armor Set)
        ("BorealOutriderKnight", 58, 68),
        # Gargoyles — DS3: rooftop guardians (3 on roof)
        ("Gargoyle", 68, 12), ("Gargoyle", 82, 15), ("Gargoyle", 95, 10),
        # Crystal Lizards (DS3: ~4 throughout)
        ("CrystalLizard", 52, 85), ("CrystalLizard", 48, 72),
        ("CrystalLizard", 65, 55), ("CrystalLizard", 88, 22),
        # Black Hand Gotthard's party — hostile NPCs in courtyard
        # (DS3: 3 Black Hand NPCs — warrior, mage, dual katana)
        ("MiniBoss", 60, 110),
        ("MiniBoss", 64, 108),
        # Bridge of Glory — barricade gauntlet
        # DS3: Hollow Slaves and Lothric Knights guard the bridge to Twin Princes
        ("HollowSlave", 112, 8), ("HollowSlave", 114, 10),
        ("HollowSlave", 119, 15), ("HollowSlave", 121, 18),
        ("HollowSlave", 125, 7), ("HollowSlave", 127, 12),
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
        ("Ember", "Ember", 57, 96, 0),
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
            "Black Hand Gotthard's journey ends here|He was one of the King's Black Hands"),
    ]))
    # Siegward of Catarina — summon sign at bonfire (wiki: helps clear path to Twin Princes)
    entities.append(make_entity("Npc", 28 * 16, 140 * 16, [
        make_field("name", "String", "Siegward of Catarina"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C8A832"),
        make_field("dialogue", "String",
            "I shall join you on this final journey|To reach the Twin Princes at the top|Let us see this through together, my friend"),
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

    # === MORE GRAND ARCHIVES DETAILS — DS3 fidelity ===
    # Entry hall — more bookshelf rows (DS3: towering bookshelves)
    fill_tiles(chunk, TILE_WALL, 35, 125, 37, 127)
    fill_tiles(chunk, TILE_WALL, 45, 128, 47, 130)
    fill_tiles(chunk, TILE_WALL, 52, 132, 54, 134)
    fill_tiles(chunk, TILE_WALL, 42, 140, 44, 142)
    fill_tiles(chunk, TILE_WALL, 55, 138, 57, 140)
    fill_tiles(chunk, TILE_WALL, 32, 132, 34, 134)
    # First floor corridors — dense bookshelf maze (DS3: labyrinthine library)
    fill_tiles(chunk, TILE_WALL, 45, 88, 47, 90)
    fill_tiles(chunk, TILE_WALL, 58, 95, 60, 97)
    fill_tiles(chunk, TILE_WALL, 68, 90, 70, 92)
    fill_tiles(chunk, TILE_WALL, 82, 95, 84, 97)
    fill_tiles(chunk, TILE_WALL, 48, 100, 50, 102)
    fill_tiles(chunk, TILE_WALL, 65, 105, 67, 107)
    fill_tiles(chunk, TILE_WALL, 75, 110, 77, 112)
    fill_tiles(chunk, TILE_WALL, 90, 108, 92, 110)
    fill_tiles(chunk, TILE_WALL, 55, 115, 57, 117)
    fill_tiles(chunk, TILE_WALL, 72, 120, 74, 122)
    fill_tiles(chunk, TILE_WALL, 85, 118, 87, 120)
    fill_tiles(chunk, TILE_WALL, 95, 112, 97, 114)
    # Wax pool hall — more wax features (DS3: central wax pool)
    fill_tiles(chunk, TILE_WALL, 35, 58, 37, 60)
    fill_tiles(chunk, TILE_WALL, 48, 56, 50, 58)
    fill_tiles(chunk, TILE_WALL, 60, 58, 62, 60)
    fill_tiles(chunk, TILE_WALL, 75, 62, 77, 64)
    fill_tiles(chunk, TILE_WALL, 38, 82, 40, 84)
    fill_tiles(chunk, TILE_WALL, 72, 82, 74, 84)
    fill_tiles(chunk, TILE_WALL, 58, 85, 60, 87)
    # Scholar tower — crystal formations and book stacks (DS3: Crystal Sage arena)
    fill_tiles(chunk, TILE_WALL, 70, 32, 72, 34)
    fill_tiles(chunk, TILE_WALL, 82, 32, 84, 34)
    fill_tiles(chunk, TILE_WALL, 88, 48, 90, 50)
    fill_tiles(chunk, TILE_WALL, 100, 38, 102, 40)
    fill_tiles(chunk, TILE_WALL, 72, 45, 74, 47)
    fill_tiles(chunk, TILE_WALL, 95, 50, 97, 52)
    fill_tiles(chunk, TILE_WALL, 104, 44, 106, 46)
    # Winged Knight corridor — armor displays (DS3: golden Winged Knights)
    fill_tiles(chunk, TILE_WALL, 55, 22, 57, 24)
    fill_tiles(chunk, TILE_WALL, 68, 20, 70, 22)
    fill_tiles(chunk, TILE_WALL, 78, 25, 80, 27)
    fill_tiles(chunk, TILE_WALL, 90, 22, 92, 24)
    fill_tiles(chunk, TILE_WALL, 58, 30, 60, 32)
    fill_tiles(chunk, TILE_WALL, 82, 30, 84, 32)
    # Gargoyle rooftop — more roof structures (DS3: open rooftop with gargoyles)
    fill_tiles(chunk, TILE_WALL, 62, 10, 64, 12)
    fill_tiles(chunk, TILE_WALL, 78, 12, 80, 14)
    fill_tiles(chunk, TILE_WALL, 88, 8, 90, 10)
    fill_tiles(chunk, TILE_WALL, 100, 12, 102, 14)
    fill_tiles(chunk, TILE_WALL, 74, 16, 76, 18)
    fill_tiles(chunk, TILE_WALL, 92, 16, 94, 18)
    # Twin Princes chamber — throne room pillars (DS3: grand throne room)
    fill_tiles(chunk, TILE_WALL, 92, 15, 94, 18)
    fill_tiles(chunk, TILE_WALL, 108, 22, 110, 25)
    fill_tiles(chunk, TILE_WALL, 122, 18, 124, 20)
    fill_tiles(chunk, TILE_WALL, 130, 12, 132, 14)
    fill_tiles(chunk, TILE_WALL, 135, 20, 137, 22)
    fill_tiles(chunk, TILE_WALL, 98, 28, 100, 30)

    # ================================================================
    # DS3 GRAND ARCHIVES — final architectural fidelity pass
    # ================================================================
    # Grand staircase — landing walls between floors (DS3: main spiral staircase)
    fill_tiles(chunk, TILE_WALL, 48, 122, 50, 124)
    fill_tiles(chunk, TILE_WALL, 52, 118, 54, 120)
    fill_tiles(chunk, TILE_WALL, 58, 108, 60, 110)
    # Reading alcoves — desk and chair clusters (DS3: scholars study at desks)
    fill_tiles(chunk, TILE_WALL, 42, 92, 44, 94)
    fill_tiles(chunk, TILE_WALL, 56, 98, 58, 100)
    fill_tiles(chunk, TILE_WALL, 70, 102, 72, 104)
    fill_tiles(chunk, TILE_WALL, 88, 96, 90, 98)
    # Balcony railings overlooking lower floors (DS3: library has open balconies)
    fill_tiles(chunk, TILE_WALL, 62, 82, 64, 84)
    fill_tiles(chunk, TILE_WALL, 70, 78, 72, 80)
    fill_tiles(chunk, TILE_WALL, 48, 68, 50, 70)
    # Archive storage rooms — locked rooms with scrolls (DS3: side rooms full of scrolls)
    fill_tiles(chunk, TILE_WALL, 32, 62, 34, 64)
    fill_tiles(chunk, TILE_WALL, 78, 60, 80, 62)
    fill_tiles(chunk, TILE_WALL, 38, 75, 40, 77)
    # Crystal Sage crystal formations (DS3: crystal sage arena has crystal clusters)
    fill_tiles(chunk, TILE_WALL, 68, 38, 70, 40)
    fill_tiles(chunk, TILE_WALL, 84, 46, 86, 48)
    fill_tiles(chunk, TILE_WALL, 76, 42, 78, 44)
    # Candle-lined corridor sconces (DS3: candles everywhere, scholars carry them)
    fill_tiles(chunk, TILE_WALL, 36, 135, 38, 136)
    fill_tiles(chunk, TILE_WALL, 48, 142, 50, 143)
    fill_tiles(chunk, TILE_WALL, 28, 128, 30, 129)
    fill_tiles(chunk, TILE_WALL, 55, 125, 57, 126)
    # Wax pool edge — more wax formations (DS3: molten wax drips from ceiling)
    fill_tiles(chunk, TILE_WALL, 42, 58, 44, 59)
    fill_tiles(chunk, TILE_WALL, 64, 84, 66, 85)
    fill_tiles(chunk, TILE_WALL, 52, 88, 54, 89)
    # Lift mechanism walls (DS3: hidden lift for Titanite Slab)
    fill_tiles(chunk, TILE_WALL, 134, 34, 136, 36)
    fill_tiles(chunk, TILE_WALL, 140, 38, 142, 40)
    fill_tiles(chunk, TILE_WALL, 130, 40, 132, 42)

    # ================================================================
    # FINALIZE — connectivity check
    # SESSION 10 FIDELITY PASS — Grand Archives
    # Additional DS3-faithful terrain: bookshelf alcove walls, scholar desk debris,
    # crystal formation clusters, Twin Princes tower stones, wax pool edge details
    # Entrance hall — bookshelf alcove walls (DS3: massive bookshelves line halls)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 50, 65, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    # Scholar desks — study area debris (DS3: scholars at desks throughout)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 57)
    fill_tiles(chunk, TILE_WALL, 78, 60, 79, 61)
    fill_tiles(chunk, TILE_WALL, 66, 58, 67, 59)
    fill_tiles(chunk, TILE_WALL, 84, 54, 85, 55)
    # Crystal formations — crystal sage area (DS3: crystals near Crystal Sage)
    fill_tiles(chunk, TILE_WALL, 92, 62, 93, 63)
    fill_tiles(chunk, TILE_WALL, 98, 66, 99, 67)
    fill_tiles(chunk, TILE_WALL, 88, 68, 89, 69)
    fill_tiles(chunk, TILE_WALL, 102, 64, 103, 65)
    # Wax pool edges — candle cluster stones (DS3: wax pools with candles)
    fill_tiles(chunk, TILE_WALL, 108, 72, 109, 73)
    fill_tiles(chunk, TILE_WALL, 114, 68, 115, 69)
    fill_tiles(chunk, TILE_WALL, 104, 76, 105, 77)
    # Twin Princes tower — tower base stones (DS3: Lothric's tower at top)
    fill_tiles(chunk, TILE_WALL, 118, 82, 119, 83)
    fill_tiles(chunk, TILE_WALL, 124, 78, 125, 79)
    fill_tiles(chunk, TILE_WALL, 130, 84, 131, 85)
    fill_tiles(chunk, TILE_WALL, 122, 86, 123, 87)
    fill_tiles(chunk, TILE_WALL, 128, 80, 129, 81)
    # Dragon head — bridge debris (DS3: dragon head on bridge)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 47)
    # Upper archive — more book clusters (DS3: books everywhere)
    fill_tiles(chunk, TILE_WALL, 136, 88, 137, 89)
    fill_tiles(chunk, TILE_WALL, 142, 84, 143, 85)
    fill_tiles(chunk, TILE_WALL, 132, 92, 133, 93)
    fill_tiles(chunk, TILE_WALL, 138, 90, 139, 91)
    # Gargoyle perch — roof stones (DS3: gargoyles on archive roof)
    fill_tiles(chunk, TILE_WALL, 146, 78, 147, 79)
    fill_tiles(chunk, TILE_WALL, 140, 76, 141, 77)

    # SESSION 10 PASS B — GrandArchives
    # Additional DS3 terrain: scholar desk debris, crystal sage formations, Twin Princes tower stones
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 51)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 59)
    fill_tiles(chunk, TILE_WALL, 92, 52, 93, 53)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 61)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 57)
    fill_tiles(chunk, TILE_WALL, 128, 64, 129, 65)
    fill_tiles(chunk, TILE_WALL, 140, 58, 141, 59)
    fill_tiles(chunk, TILE_WALL, 136, 72, 137, 73)
    fill_tiles(chunk, TILE_WALL, 120, 68, 121, 69)
    fill_tiles(chunk, TILE_WALL, 108, 74, 109, 75)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 84, 66, 85, 67)

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
    Faithful DS3 layout: Flameless Shrine entry (south) -> winding ash path through
    collapsed ruins -> twisted girder hall (middle) -> First Flame arena (north).
    No regular enemies. The end of all things.
    """
    chunk = new_chunk()
    entities = []

    # ================================================================
    # TERRAIN — DS3 Kiln is a linear descent through ash and ruin
    # ================================================================

    # === 1. FLAMELESS SHRINE (south) — entry area from Grand Archives ===
    # Wide ash platform with ruined walls framing the entry
    fill_tiles(chunk, TILE_GROUND, 62, 140, 98, 158)
    # Collapsed entry arch — remnants of the kiln door
    fill_tiles(chunk, TILE_WALL, 64, 140, 68, 146)
    fill_tiles(chunk, TILE_WALL, 92, 140, 96, 146)
    # Ash dunes around the entry (elevated terrain framing the path)
    fill_tiles(chunk, TILE_WALL, 58, 142, 62, 152)
    fill_tiles(chunk, TILE_WALL, 98, 142, 102, 152)
    # Rubble pile near shrine bonfire
    fill_tiles(chunk, TILE_WALL, 78, 144, 82, 148)

    # === 2. ASH CORRIDOR — winding path through collapsed kiln walls ===
    # DS3: narrow path flanked by towering ash dunes and twisted metal
    fill_tiles(chunk, TILE_GROUND, 66, 128, 94, 142)
    # Left ash dune wall (tall, forces player through narrow gap)
    fill_tiles(chunk, TILE_WALL, 56, 118, 70, 130)
    fill_tiles(chunk, TILE_WALL, 72, 122, 76, 128)
    # Right ash dune wall
    fill_tiles(chunk, TILE_WALL, 84, 122, 88, 128)
    fill_tiles(chunk, TILE_WALL, 90, 118, 104, 130)
    # Twisted girder remnant across the path
    fill_tiles(chunk, TILE_WALL, 74, 126, 78, 128)
    # Rubble at corridor edges
    fill_tiles(chunk, TILE_WALL, 66, 130, 68, 134)
    fill_tiles(chunk, TILE_WALL, 92, 130, 94, 134)

    # === 3. COLLAPSED CHAMBER — first open area with ruined structures ===
    fill_tiles(chunk, TILE_GROUND, 52, 104, 108, 120)
    carve_ellipse(chunk, 80, 112, 18, 6)
    # Fallen pillar remnants (DS3: huge stone pillars collapsed across the hall)
    fill_tiles(chunk, TILE_WALL, 58, 106, 62, 114)
    fill_tiles(chunk, TILE_WALL, 98, 106, 102, 114)
    # Crossed girders on the ground
    fill_tiles(chunk, TILE_WALL, 68, 108, 72, 110)
    fill_tiles(chunk, TILE_WALL, 88, 110, 92, 112)
    # Ash drifts along walls
    fill_tiles(chunk, TILE_WALL, 54, 108, 56, 116)
    fill_tiles(chunk, TILE_WALL, 104, 108, 106, 116)
    # Scattered rubble
    fill_tiles(chunk, TILE_WALL, 76, 114, 78, 116)
    fill_tiles(chunk, TILE_WALL, 82, 114, 84, 116)

    # === 4. TWISTED GIRDER HALL — dense collapsed metal structure ===
    # DS3: the most iconic section — massive twisted iron beams everywhere
    fill_tiles(chunk, TILE_GROUND, 48, 78, 112, 106)
    carve_ellipse(chunk, 80, 92, 20, 10)
    # Main girder structures — diagonal collapsed beams
    fill_tiles(chunk, TILE_WALL, 52, 82, 56, 96)
    fill_tiles(chunk, TILE_WALL, 108, 82, 112, 96)
    # Cross-beams (DS3: massive iron beams crossing the corridor)
    fill_tiles(chunk, TILE_WALL, 60, 86, 64, 88)
    fill_tiles(chunk, TILE_WALL, 96, 86, 100, 88)
    fill_tiles(chunk, TILE_WALL, 66, 92, 68, 94)
    fill_tiles(chunk, TILE_WALL, 92, 92, 94, 94)
    # Fallen wall sections creating choke points
    fill_tiles(chunk, TILE_WALL, 58, 78, 66, 82)
    fill_tiles(chunk, TILE_WALL, 94, 78, 102, 82)
    # Twisted metal debris
    fill_tiles(chunk, TILE_WALL, 72, 96, 74, 98)
    fill_tiles(chunk, TILE_WALL, 86, 96, 88, 98)
    fill_tiles(chunk, TILE_WALL, 76, 100, 78, 102)
    fill_tiles(chunk, TILE_WALL, 82, 100, 84, 102)
    # Ash pile against north wall of hall
    fill_tiles(chunk, TILE_WALL, 60, 78, 62, 80)
    fill_tiles(chunk, TILE_WALL, 98, 78, 100, 80)
    # Elevated ash platform (left)
    fill_tiles(chunk, TILE_WALL, 48, 80, 52, 90)
    # Elevated ash platform (right)
    fill_tiles(chunk, TILE_WALL, 108, 80, 112, 90)

    # === 5. SECOND ASH CORRIDOR — narrowing approach to arena ===
    fill_tiles(chunk, TILE_GROUND, 58, 60, 102, 80)
    # Funnel walls — ash dunes pushing player toward arena
    fill_tiles(chunk, TILE_WALL, 50, 62, 60, 78)
    fill_tiles(chunk, TILE_WALL, 100, 62, 110, 78)
    # Girder fragments in corridor
    fill_tiles(chunk, TILE_WALL, 64, 68, 66, 72)
    fill_tiles(chunk, TILE_WALL, 94, 68, 96, 72)
    fill_tiles(chunk, TILE_WALL, 76, 72, 78, 76)
    fill_tiles(chunk, TILE_WALL, 82, 72, 84, 76)
    # Rubble
    fill_tiles(chunk, TILE_WALL, 68, 64, 70, 66)
    fill_tiles(chunk, TILE_WALL, 90, 64, 92, 66)

    # === 6. FIRST FLAME ARENA (north) — circular boss arena ===
    fill_tiles(chunk, TILE_GROUND, 46, 6, 114, 62)
    carve_ellipse(chunk, 80, 34, 28, 22)
    # Arena perimeter — collapsed arches framing the arena
    fill_tiles(chunk, TILE_WALL, 48, 8, 54, 20)
    fill_tiles(chunk, TILE_WALL, 106, 8, 112, 20)
    fill_tiles(chunk, TILE_WALL, 48, 48, 54, 58)
    fill_tiles(chunk, TILE_WALL, 106, 48, 112, 58)
    # Broken pillars around arena edge (DS3: stone column stumps)
    fill_tiles(chunk, TILE_WALL, 56, 14, 58, 18)
    fill_tiles(chunk, TILE_WALL, 102, 14, 104, 18)
    fill_tiles(chunk, TILE_WALL, 52, 36, 54, 40)
    fill_tiles(chunk, TILE_WALL, 106, 36, 108, 40)
    fill_tiles(chunk, TILE_WALL, 56, 48, 58, 52)
    fill_tiles(chunk, TILE_WALL, 102, 48, 104, 52)
    # Ember pit at center edge (DS3: glowing coals at arena center)
    fill_tiles(chunk, TILE_WALL, 78, 30, 82, 36)
    # Ash dunes at arena corners
    fill_tiles(chunk, TILE_WALL, 46, 6, 50, 12)
    fill_tiles(chunk, TILE_WALL, 110, 6, 114, 12)
    fill_tiles(chunk, TILE_WALL, 46, 54, 50, 60)
    fill_tiles(chunk, TILE_WALL, 110, 54, 114, 60)

    # === 7. Connecting corridors between sections ===
    # Entry to ash corridor
    fill_tiles(chunk, TILE_GROUND, 72, 134, 88, 142)
    # Ash corridor to collapsed chamber
    fill_tiles(chunk, TILE_GROUND, 70, 118, 90, 128)
    # Collapsed chamber to girder hall
    fill_tiles(chunk, TILE_GROUND, 66, 102, 94, 108)
    # Girder hall to second corridor
    fill_tiles(chunk, TILE_GROUND, 64, 76, 96, 82)
    # Second corridor to arena
    fill_tiles(chunk, TILE_GROUND, 64, 58, 96, 64)

    # ================================================================
    # SESSION 9 FIDELITY PASS — KilnOfTheFirstFlame architectural details
    # ================================================================
    # Ashen path — ember fragment debris (DS3: scorched earth fragments)
    fill_tiles(chunk, TILE_WALL, 74, 148, 75, 149)
    fill_tiles(chunk, TILE_WALL, 82, 146, 83, 147)
    fill_tiles(chunk, TILE_WALL, 78, 152, 79, 153)
    fill_tiles(chunk, TILE_WALL, 86, 144, 87, 145)
    # First collapsed corridor — iron girder debris (DS3: twisted metal structures)
    fill_tiles(chunk, TILE_WALL, 68, 128, 69, 129)
    fill_tiles(chunk, TILE_WALL, 76, 124, 77, 125)
    fill_tiles(chunk, TILE_WALL, 72, 132, 73, 133)
    fill_tiles(chunk, TILE_WALL, 80, 120, 81, 121)
    fill_tiles(chunk, TILE_WALL, 84, 130, 85, 131)
    # Ash field — scattered coiled sword fragments (DS3: remains of past kilns)
    fill_tiles(chunk, TILE_WALL, 70, 108, 71, 109)
    fill_tiles(chunk, TILE_WALL, 78, 104, 79, 105)
    fill_tiles(chunk, TILE_WALL, 74, 112, 75, 113)
    fill_tiles(chunk, TILE_WALL, 82, 100, 83, 101)
    fill_tiles(chunk, TILE_WALL, 66, 116, 67, 117)
    # Second corridor — burnt stone pillars (DS3: smoldering architecture)
    fill_tiles(chunk, TILE_WALL, 68, 90, 69, 91)
    fill_tiles(chunk, TILE_WALL, 76, 86, 77, 87)
    fill_tiles(chunk, TILE_WALL, 72, 94, 73, 95)
    fill_tiles(chunk, TILE_WALL, 80, 82, 81, 83)
    fill_tiles(chunk, TILE_WALL, 84, 92, 85, 93)
    # Girder hall — twisted iron beams (DS3: industrial hellscape)
    fill_tiles(chunk, TILE_WALL, 66, 76, 67, 77)
    fill_tiles(chunk, TILE_WALL, 74, 78, 75, 79)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    fill_tiles(chunk, TILE_WALL, 70, 80, 71, 81)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    # Soul of Cinder arena — scorched throne remnants (DS3: final arena)
    fill_tiles(chunk, TILE_WALL, 64, 58, 65, 59)
    fill_tiles(chunk, TILE_WALL, 92, 58, 93, 59)
    fill_tiles(chunk, TILE_WALL, 72, 54, 73, 55)
    fill_tiles(chunk, TILE_WALL, 86, 54, 87, 55)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)

    # ================================================================
    # SESSION 11 FIDELITY PASS — KilnOfTheFirstFlame fine architectural details
    # ================================================================
    # Flameless Shrine — scorched doorway debris (DS3: burnt entry arch)
    fill_tiles(chunk, TILE_WALL, 66, 150, 67, 151)
    fill_tiles(chunk, TILE_WALL, 90, 150, 91, 151)
    fill_tiles(chunk, TILE_WALL, 70, 154, 71, 155)
    fill_tiles(chunk, TILE_WALL, 86, 154, 87, 155)
    fill_tiles(chunk, TILE_WALL, 74, 142, 75, 143)
    fill_tiles(chunk, TILE_WALL, 84, 142, 85, 143)
    # Ash corridor — slag mound debris (DS3: molten metal slag along path)
    fill_tiles(chunk, TILE_WALL, 58, 124, 59, 125)
    fill_tiles(chunk, TILE_WALL, 100, 124, 101, 125)
    fill_tiles(chunk, TILE_WALL, 62, 126, 63, 127)
    fill_tiles(chunk, TILE_WALL, 96, 126, 97, 127)
    fill_tiles(chunk, TILE_WALL, 70, 130, 71, 131)
    fill_tiles(chunk, TILE_WALL, 88, 130, 89, 131)
    # Collapsed chamber — crumbled arch stones (DS3: massive fallen architecture)
    fill_tiles(chunk, TILE_WALL, 56, 110, 57, 111)
    fill_tiles(chunk, TILE_WALL, 102, 110, 103, 111)
    fill_tiles(chunk, TILE_WALL, 62, 118, 63, 119)
    fill_tiles(chunk, TILE_WALL, 96, 118, 97, 119)
    fill_tiles(chunk, TILE_WALL, 72, 106, 73, 107)
    fill_tiles(chunk, TILE_WALL, 86, 106, 87, 107)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Girder hall — twisted rebar fragments (DS3: industrial hellscape with rebar)
    fill_tiles(chunk, TILE_WALL, 54, 84, 55, 85)
    fill_tiles(chunk, TILE_WALL, 106, 84, 107, 85)
    fill_tiles(chunk, TILE_WALL, 58, 88, 59, 89)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 64, 96, 65, 97)
    fill_tiles(chunk, TILE_WALL, 94, 96, 95, 97)
    fill_tiles(chunk, TILE_WALL, 68, 102, 69, 103)
    fill_tiles(chunk, TILE_WALL, 90, 102, 91, 103)
    fill_tiles(chunk, TILE_WALL, 74, 90, 75, 91)
    fill_tiles(chunk, TILE_WALL, 84, 90, 85, 91)
    # Second corridor — collapsed ceiling fragments (DS3: debris from above)
    fill_tiles(chunk, TILE_WALL, 54, 66, 55, 67)
    fill_tiles(chunk, TILE_WALL, 104, 66, 105, 67)
    fill_tiles(chunk, TILE_WALL, 60, 70, 61, 71)
    fill_tiles(chunk, TILE_WALL, 98, 70, 99, 71)
    fill_tiles(chunk, TILE_WALL, 72, 74, 73, 75)
    fill_tiles(chunk, TILE_WALL, 86, 74, 87, 75)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    # Arena — scorched stone debris (DS3: final arena with burnt offerings)
    fill_tiles(chunk, TILE_WALL, 50, 10, 51, 12)
    fill_tiles(chunk, TILE_WALL, 108, 10, 109, 12)
    fill_tiles(chunk, TILE_WALL, 52, 42, 53, 44)
    fill_tiles(chunk, TILE_WALL, 106, 42, 107, 44)
    fill_tiles(chunk, TILE_WALL, 58, 22, 59, 24)
    fill_tiles(chunk, TILE_WALL, 100, 22, 101, 24)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 58)
    fill_tiles(chunk, TILE_WALL, 84, 56, 85, 58)
    fill_tiles(chunk, TILE_WALL, 66, 48, 67, 50)
    fill_tiles(chunk, TILE_WALL, 92, 48, 93, 50)

        # ================================================================
    # ENTITIES
    # ================================================================

    # --- Player spawn at Flameless Shrine ---
    spawn_px, spawn_py = 80 * 16, 150 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 80 * 16, 150 * 16))   # Flameless Shrine
    entities.append(make_entity("Bonfire", 80 * 16, 30 * 16))    # Kiln boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 80 * 16, 26 * 16))  # Soul of Cinder
    entities.append(make_entity("Enemy", 80 * 16, 26 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "MiniBoss")]))  # Soul of Cinder

    # --- NPCs ---
    # Fire Keeper — appears at Kiln for the final scene (DS3: summons Fire Keeper for ending)
    entities.append(make_entity("Npc", 78 * 16, 28 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#E0E0F0"),
        make_field("dialogue", "String",
            "Ashen One, thou hast come to the end|I will remain beside thee|May the fire find thee worthy|Farewell, my Ashen One"),
    ]))

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
    entities.append(make_entity("FogGate", 80 * 16, 156 * 16, [
        make_field("dest_area", "String", "GrandArchives"),
        make_field("dest_x", "Float", 300.0),
        make_field("dest_y", "Float", 3800.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Dim firelight at Flameless Shrine — dying embers
    entities.append(make_entity("Light", 80 * 16, 150 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.5)]))
    # Flickering embers in collapsed chamber
    entities.append(make_entity("Light", 80 * 16, 112 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.85), make_field("g", "Float", 0.45),
        make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.3)]))
    # Dim glow through twisted girders
    entities.append(make_entity("Light", 72 * 16, 90 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.1), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 88 * 16, 90 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.1), make_field("intensity", "Float", 0.25)]))
    # Second corridor — dying ember light
    entities.append(make_entity("Light", 80 * 16, 70 * 16, [
        make_field("radius", "Float", 130.0),
        make_field("r", "Float", 0.85), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.3)]))
    # Brilliant golden at First Flame arena — the final light
    entities.append(make_entity("Light", 80 * 16, 26 * 16, [
        make_field("radius", "Float", 260.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.8)]))
    # Warm glow at arena perimeter
    entities.append(make_entity("Light", 80 * 16, 50 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.35)]))

    # === ADDITIONAL INTERNAL STRUCTURES — Kiln DS3 fidelity ===
    # Flameless Shrine — ash dune detail and ruined pillar fragments
    fill_tiles(chunk, TILE_WALL, 70, 148, 72, 150)
    fill_tiles(chunk, TILE_WALL, 88, 148, 90, 150)
    fill_tiles(chunk, TILE_WALL, 74, 142, 75, 144)
    fill_tiles(chunk, TILE_WALL, 85, 142, 86, 144)
    # Ash corridor — additional twisted metal and ash drifts
    fill_tiles(chunk, TILE_WALL, 70, 124, 71, 126)
    fill_tiles(chunk, TILE_WALL, 88, 124, 89, 126)
    fill_tiles(chunk, TILE_WALL, 76, 130, 77, 132)
    fill_tiles(chunk, TILE_WALL, 82, 130, 83, 132)
    # Collapsed chamber — more fallen pillar sections and rubble
    fill_tiles(chunk, TILE_WALL, 64, 112, 66, 114)
    fill_tiles(chunk, TILE_WALL, 94, 112, 96, 114)
    fill_tiles(chunk, TILE_WALL, 74, 108, 76, 110)
    fill_tiles(chunk, TILE_WALL, 84, 108, 86, 110)
    # Girder hall — additional twisted iron beams (DS3: iconic metal forest)
    fill_tiles(chunk, TILE_WALL, 68, 84, 70, 86)
    fill_tiles(chunk, TILE_WALL, 90, 84, 92, 86)
    fill_tiles(chunk, TILE_WALL, 64, 90, 65, 92)
    fill_tiles(chunk, TILE_WALL, 95, 90, 96, 92)
    fill_tiles(chunk, TILE_WALL, 78, 94, 80, 96)
    fill_tiles(chunk, TILE_WALL, 82, 98, 84, 100)
    # Second ash corridor — narrowing rubble (DS3: funnel toward final arena)
    fill_tiles(chunk, TILE_WALL, 72, 66, 73, 68)
    fill_tiles(chunk, TILE_WALL, 88, 66, 89, 68)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 76)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 76)
    # First Flame arena — additional broken column stumps and ash piles
    fill_tiles(chunk, TILE_WALL, 60, 24, 62, 26)
    fill_tiles(chunk, TILE_WALL, 98, 24, 100, 26)
    fill_tiles(chunk, TILE_WALL, 68, 42, 70, 44)
    fill_tiles(chunk, TILE_WALL, 90, 42, 92, 44)
    fill_tiles(chunk, TILE_WALL, 74, 18, 76, 20)
    fill_tiles(chunk, TILE_WALL, 84, 18, 86, 20)
    fill_tiles(chunk, TILE_WALL, 64, 52, 66, 54)
    fill_tiles(chunk, TILE_WALL, 94, 52, 96, 54)

    # === SESSION 6 FIDELITY PASS — Kiln of the First Flame ===
    # Flameless Shrine — more ash dune ridges (DS3: desolate ash wasteland)
    fill_tiles(chunk, TILE_WALL, 66, 144, 68, 146)
    fill_tiles(chunk, TILE_WALL, 92, 144, 94, 146)
    fill_tiles(chunk, TILE_WALL, 76, 146, 78, 148)
    fill_tiles(chunk, TILE_WALL, 82, 146, 84, 148)
    fill_tiles(chunk, TILE_WALL, 60, 148, 62, 150)
    fill_tiles(chunk, TILE_WALL, 98, 148, 100, 150)
    # Ash corridor — more twisted metal debris (DS3: collapsed iron structures)
    fill_tiles(chunk, TILE_WALL, 68, 120, 69, 122)
    fill_tiles(chunk, TILE_WALL, 90, 120, 91, 122)
    fill_tiles(chunk, TILE_WALL, 78, 128, 80, 130)
    fill_tiles(chunk, TILE_WALL, 80, 132, 82, 134)
    fill_tiles(chunk, TILE_WALL, 72, 136, 74, 138)
    fill_tiles(chunk, TILE_WALL, 86, 136, 88, 138)
    # Collapsed chamber — more fallen masonry (DS3: ruined cathedral-like hall)
    fill_tiles(chunk, TILE_WALL, 56, 104, 58, 106)
    fill_tiles(chunk, TILE_WALL, 102, 104, 104, 106)
    fill_tiles(chunk, TILE_WALL, 70, 116, 72, 118)
    fill_tiles(chunk, TILE_WALL, 88, 116, 90, 118)
    fill_tiles(chunk, TILE_WALL, 60, 118, 62, 120)
    fill_tiles(chunk, TILE_WALL, 98, 118, 100, 120)
    # Girder hall — more twisted iron forest (DS3: dense collapsed beams)
    fill_tiles(chunk, TILE_WALL, 54, 84, 56, 86)
    fill_tiles(chunk, TILE_WALL, 104, 84, 106, 86)
    fill_tiles(chunk, TILE_WALL, 72, 88, 74, 90)
    fill_tiles(chunk, TILE_WALL, 86, 88, 88, 90)
    fill_tiles(chunk, TILE_WALL, 66, 96, 68, 98)
    fill_tiles(chunk, TILE_WALL, 92, 96, 94, 98)
    fill_tiles(chunk, TILE_WALL, 76, 102, 78, 104)
    fill_tiles(chunk, TILE_WALL, 82, 102, 84, 104)
    # Second corridor — narrowing funnel walls (DS3: claustrophobic approach)
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 64)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    fill_tiles(chunk, TILE_WALL, 68, 70, 70, 72)
    fill_tiles(chunk, TILE_WALL, 90, 70, 92, 72)
    fill_tiles(chunk, TILE_WALL, 74, 76, 76, 78)
    fill_tiles(chunk, TILE_WALL, 84, 76, 86, 78)
    # First Flame arena — more broken columns (DS3: ancient ruined circular arena)
    fill_tiles(chunk, TILE_WALL, 52, 28, 54, 30)
    fill_tiles(chunk, TILE_WALL, 106, 28, 108, 30)
    fill_tiles(chunk, TILE_WALL, 58, 44, 60, 46)
    fill_tiles(chunk, TILE_WALL, 100, 44, 102, 46)
    fill_tiles(chunk, TILE_WALL, 66, 10, 68, 12)
    fill_tiles(chunk, TILE_WALL, 92, 10, 94, 12)
    fill_tiles(chunk, TILE_WALL, 70, 56, 72, 58)
    fill_tiles(chunk, TILE_WALL, 88, 56, 90, 58)
    fill_tiles(chunk, TILE_WALL, 62, 14, 64, 16)
    fill_tiles(chunk, TILE_WALL, 96, 14, 98, 16)
    # SESSION 10 FIDELITY PASS — Kiln of the First Flame
    # Additional DS3-faithful terrain: ember fragment debris, iron girder remnants,
    # scorched throne stones, ash dune ridges, coiled sword base debris
    # Ash dunes — ridges and debris (DS3: ash-covered landscape)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 50, 65, 51)
    fill_tiles(chunk, TILE_WALL, 70, 54, 71, 55)
    fill_tiles(chunk, TILE_WALL, 76, 48, 77, 49)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 53)
    # Iron girder remnants (DS3: twisted metal structures from ruined kiln)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    fill_tiles(chunk, TILE_WALL, 94, 52, 95, 53)
    fill_tiles(chunk, TILE_WALL, 100, 58, 101, 59)
    fill_tiles(chunk, TILE_WALL, 106, 54, 107, 55)
    # Ember fragments — glowing debris (DS3: ember fragments scattered)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 92, 64, 93, 65)
    fill_tiles(chunk, TILE_WALL, 104, 62, 105, 63)
    # Scorched throne area — throne debris (DS3: ruined throne at kiln center)
    fill_tiles(chunk, TILE_WALL, 112, 68, 113, 69)
    fill_tiles(chunk, TILE_WALL, 118, 72, 119, 73)
    fill_tiles(chunk, TILE_WALL, 124, 70, 125, 71)
    fill_tiles(chunk, TILE_WALL, 116, 76, 117, 77)
    fill_tiles(chunk, TILE_WALL, 122, 74, 123, 75)
    # Coiled sword base — remnant stones (DS3: coiled sword at kiln center)
    fill_tiles(chunk, TILE_WALL, 128, 78, 129, 79)
    fill_tiles(chunk, TILE_WALL, 134, 82, 135, 83)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 87)
    fill_tiles(chunk, TILE_WALL, 136, 80, 137, 81)
    # Path edges — ash ridge stones (DS3: ash ridges along path)
    fill_tiles(chunk, TILE_WALL, 48, 56, 49, 57)
    fill_tiles(chunk, TILE_WALL, 62, 58, 63, 59)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 86, 62, 87, 63)
    fill_tiles(chunk, TILE_WALL, 98, 60, 99, 61)


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

    # === ADDITIONAL CRYSTAL GARDEN DETAILS — DS3 fidelity ===
    # Entry staircase — stone steps with crystal encrustation (DS3: crystal-covered descent)
    fill_tiles(chunk, TILE_WALL, 10, 8, 12, 10)
    fill_tiles(chunk, TILE_WALL, 22, 12, 24, 14)
    fill_tiles(chunk, TILE_WALL, 32, 18, 34, 20)
    fill_tiles(chunk, TILE_WALL, 16, 20, 18, 22)
    # Crystal courtyard — large crystal clusters (DS3: courtyard full of crystal growths)
    fill_tiles(chunk, TILE_WALL, 30, 36, 32, 38)
    fill_tiles(chunk, TILE_WALL, 36, 42, 38, 44)
    fill_tiles(chunk, TILE_WALL, 45, 36, 47, 38)
    fill_tiles(chunk, TILE_WALL, 52, 40, 54, 42)
    fill_tiles(chunk, TILE_WALL, 62, 48, 64, 50)
    fill_tiles(chunk, TILE_WALL, 68, 38, 70, 40)
    fill_tiles(chunk, TILE_WALL, 56, 55, 58, 57)
    # Poison swamp — more dead trees and rotten logs (DS3: toxic garden with dead foliage)
    fill_tiles(chunk, TILE_WALL, 42, 72, 44, 74)
    fill_tiles(chunk, TILE_WALL, 55, 70, 57, 72)
    fill_tiles(chunk, TILE_WALL, 48, 80, 50, 82)
    fill_tiles(chunk, TILE_WALL, 62, 85, 64, 87)
    fill_tiles(chunk, TILE_WALL, 38, 84, 40, 86)
    fill_tiles(chunk, TILE_WALL, 66, 78, 68, 80)
    # Serpent corridor — more serpent statue pillars (DS3: man-serpent guards line the path)
    fill_tiles(chunk, TILE_WALL, 76, 54, 78, 56)
    fill_tiles(chunk, TILE_WALL, 85, 62, 87, 64)
    fill_tiles(chunk, TILE_WALL, 98, 68, 100, 70)
    fill_tiles(chunk, TILE_WALL, 108, 58, 110, 60)
    # Oceiros throne room — throne structure and baby crib area
    # DS3: Oceiros guards a crib, throne room has crystal throne
    fill_tiles(chunk, TILE_WALL, 118, 85, 122, 87)
    fill_tiles(chunk, TILE_WALL, 128, 88, 130, 90)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 97)
    fill_tiles(chunk, TILE_WALL, 105, 88, 107, 90)
    fill_tiles(chunk, TILE_WALL, 142, 102, 144, 104)
    fill_tiles(chunk, TILE_WALL, 120, 105, 122, 107)
    # Lift mid-way ledge — crystal outcroppings (DS3: exterior ledge with crystals)
    fill_tiles(chunk, TILE_WALL, 110, 56, 112, 58)
    fill_tiles(chunk, TILE_WALL, 118, 60, 120, 62)
    # Additional Consumed King's Garden DS3 details
    # Entry passage — crystal-encrusted walls (DS3: crystals grow on the stonework)
    fill_tiles(chunk, TILE_WALL, 14, 14, 15, 16)
    fill_tiles(chunk, TILE_WALL, 28, 10, 29, 12)
    # Crystal courtyard — scattered crystal shards (DS3: broken crystal debris)
    fill_tiles(chunk, TILE_WALL, 40, 30, 41, 32)
    fill_tiles(chunk, TILE_WALL, 58, 46, 59, 48)
    fill_tiles(chunk, TILE_WALL, 48, 44, 49, 46)
    # Poison swamp edge — reeds and toxic plants (DS3: toxic garden overgrowth)
    fill_tiles(chunk, TILE_WALL, 35, 76, 36, 78)
    fill_tiles(chunk, TILE_WALL, 70, 82, 71, 84)
    fill_tiles(chunk, TILE_WALL, 52, 88, 53, 90)
    # Serpent corridor — additional man-serpent alcoves (DS3: serpent warriors lurk in alcoves)
    fill_tiles(chunk, TILE_WALL, 80, 66, 82, 68)
    fill_tiles(chunk, TILE_WALL, 92, 72, 94, 74)
    fill_tiles(chunk, TILE_WALL, 115, 62, 117, 64)
    # Oceiros throne — baby crib stones (DS3: Oceiros cradles an invisible baby)
    fill_tiles(chunk, TILE_WALL, 125, 92, 127, 94)
    fill_tiles(chunk, TILE_WALL, 132, 98, 134, 100)
    fill_tiles(chunk, TILE_WALL, 115, 98, 117, 100)

    # ================================================================
    # ADDITIONAL DS3 CONSUMED KING'S GARDEN — descent details, crystal growths
    # ================================================================
    # Entry — crystal-encrusted stair walls (DS3: crystals grow on descent)
    fill_tiles(chunk, TILE_WALL, 8, 12, 10, 14)
    fill_tiles(chunk, TILE_WALL, 20, 18, 22, 20)
    fill_tiles(chunk, TILE_WALL, 14, 22, 16, 24)
    fill_tiles(chunk, TILE_WALL, 26, 14, 28, 16)
    # Crystal courtyard — more crystal clusters (DS3: garden full of crystal growths)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 42)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 38)
    fill_tiles(chunk, TILE_WALL, 62, 44, 63, 46)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 50)
    fill_tiles(chunk, TILE_WALL, 40, 54, 41, 56)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 52)
    # Poison swamp — dead roots and fallen logs (DS3: toxic garden with dead foliage)
    fill_tiles(chunk, TILE_WALL, 46, 74, 47, 76)
    fill_tiles(chunk, TILE_WALL, 56, 80, 57, 82)
    fill_tiles(chunk, TILE_WALL, 64, 76, 65, 78)
    fill_tiles(chunk, TILE_WALL, 40, 86, 41, 88)
    fill_tiles(chunk, TILE_WALL, 60, 88, 61, 90)
    # Corridor — dragon statue pillars (DS3: path to Oceiros has dragon motifs)
    fill_tiles(chunk, TILE_WALL, 75, 56, 76, 58)
    fill_tiles(chunk, TILE_WALL, 88, 64, 89, 66)
    fill_tiles(chunk, TILE_WALL, 98, 68, 99, 70)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 62)
    # Throne room — additional crystal throne debris (DS3: Oceiros guards his invisible child)
    fill_tiles(chunk, TILE_WALL, 110, 76, 111, 78)
    fill_tiles(chunk, TILE_WALL, 122, 80, 123, 82)
    fill_tiles(chunk, TILE_WALL, 135, 86, 136, 88)
    fill_tiles(chunk, TILE_WALL, 140, 92, 141, 94)
    fill_tiles(chunk, TILE_WALL, 128, 102, 129, 104)
    fill_tiles(chunk, TILE_WALL, 138, 106, 139, 108)
    # Lift mid-way ledge — crystal outcrops (DS3: hidden ledge with Dragonscale Ring)
    fill_tiles(chunk, TILE_WALL, 112, 54, 113, 56)
    fill_tiles(chunk, TILE_WALL, 120, 60, 121, 62)

    # ================================================================
    # DS3 CONSUMED KING'S GARDEN — final architectural fidelity pass
    # ================================================================
    # Entry descent — switchback stair walls (DS3: winding crystal stairs down)
    fill_tiles(chunk, TILE_WALL, 10, 18, 11, 20)
    fill_tiles(chunk, TILE_WALL, 24, 20, 25, 22)
    fill_tiles(chunk, TILE_WALL, 18, 14, 19, 16)
    # Crystal courtyard — central crystal fountain ruin (DS3: courtyard fountain with crystals)
    fill_tiles(chunk, TILE_WALL, 50, 42, 52, 45)
    fill_tiles(chunk, TILE_WALL, 46, 38, 48, 40)
    fill_tiles(chunk, TILE_WALL, 54, 46, 56, 48)
    # Lift shaft — elevator mechanism walls (DS3: lift descends between garden floors)
    fill_tiles(chunk, TILE_WALL, 100, 58, 102, 60)
    fill_tiles(chunk, TILE_WALL, 106, 64, 108, 66)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    # Poison swamp — collapsed bridge pilings (DS3: rotten wooden bridge remains in toxic pool)
    fill_tiles(chunk, TILE_WALL, 38, 78, 39, 80)
    fill_tiles(chunk, TILE_WALL, 64, 84, 65, 86)
    fill_tiles(chunk, TILE_WALL, 56, 72, 57, 74)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 90)
    # Oceiros approach — crumbled stair edge walls (DS3: broken stairs lead to throne room)
    fill_tiles(chunk, TILE_WALL, 108, 66, 109, 68)
    fill_tiles(chunk, TILE_WALL, 114, 70, 115, 72)
    fill_tiles(chunk, TILE_WALL, 122, 74, 123, 76)
    fill_tiles(chunk, TILE_WALL, 128, 80, 129, 82)
    # Oceiros throne room — baby crib stone circle (DS3: Oceiros cradles invisible child)
    fill_tiles(chunk, TILE_WALL, 118, 88, 120, 90)
    fill_tiles(chunk, TILE_WALL, 124, 94, 126, 96)
    fill_tiles(chunk, TILE_WALL, 130, 102, 132, 104)
    fill_tiles(chunk, TILE_WALL, 136, 108, 138, 110)
    # Exterior ledge — Dragonscale Ring path walls (DS3: narrow ledge with crystal outcrops)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 58)
    fill_tiles(chunk, TILE_WALL, 120, 60, 121, 62)
    # Garden hedgerow — overgrown walls (DS3: wild garden consumed by crystal growth)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 46)
    fill_tiles(chunk, TILE_WALL, 60, 50, 61, 52)
    fill_tiles(chunk, TILE_WALL, 68, 40, 69, 42)

    # ================================================================
    # SESSION 9 FIDELITY PASS — ConsumedKingsGarden architectural details
    # ================================================================
    # Crystal garden path — crystallized flower beds (DS3: crystal formations everywhere)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 23)
    fill_tiles(chunk, TILE_WALL, 14, 26, 15, 27)
    fill_tiles(chunk, TILE_WALL, 28, 16, 29, 17)
    # Consumed King's throne — shattered throne stones (DS3: Oceiros's ruined throne room)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 84, 64, 85, 65)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 69)
    fill_tiles(chunk, TILE_WALL, 88, 58, 89, 59)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    # Crystal cavern — glowing crystal pillars (DS3: crystal cave beneath garden)
    fill_tiles(chunk, TILE_WALL, 50, 80, 51, 81)
    fill_tiles(chunk, TILE_WALL, 54, 84, 55, 85)
    fill_tiles(chunk, TILE_WALL, 46, 88, 47, 89)
    fill_tiles(chunk, TILE_WALL, 58, 78, 59, 79)
    fill_tiles(chunk, TILE_WALL, 52, 90, 53, 91)
    # Oceiros arena — baby crib stones (DS3: Oceiros cradles invisible child)
    fill_tiles(chunk, TILE_WALL, 100, 40, 101, 41)
    fill_tiles(chunk, TILE_WALL, 104, 44, 105, 45)
    fill_tiles(chunk, TILE_WALL, 96, 48, 97, 49)
    fill_tiles(chunk, TILE_WALL, 108, 38, 109, 39)
    fill_tiles(chunk, TILE_WALL, 102, 50, 103, 51)
    # Overgrown hedge maze — twisted roots (DS3: wild garden with crystal-infused plants)
    fill_tiles(chunk, TILE_WALL, 32, 36, 33, 37)
    fill_tiles(chunk, TILE_WALL, 38, 40, 39, 41)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    fill_tiles(chunk, TILE_WALL, 40, 34, 41, 35)
    # Untended Graves passage — dark stone arch (DS3: hidden passage behind Oceiros)
    fill_tiles(chunk, TILE_WALL, 120, 56, 121, 57)
    fill_tiles(chunk, TILE_WALL, 124, 60, 125, 61)
    fill_tiles(chunk, TILE_WALL, 116, 64, 117, 65)

        # --- Player spawn ---
    spawn_px, spawn_py = 15 * 16, 15 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    # DS3: only 1 bonfire — Oceiros the Consumed King (after defeating boss)
    entities.append(make_entity("Bonfire", 120 * 16, 95 * 16))   # Oceiros boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 120 * 16, 88 * 16))  # Oceiros

    # --- Enemies — DS3 Consumed King's Garden (wiki-accurate):
    # Cathedral Knights patrol the garden. Hollow Slaves ambush from dark corners.
    # Pus of Man on wyvern-like creatures. Rotten Slugs in toxic water.
    # No Serpent Men here (those are only in Archdragon Peak).
    enemy_data = [
        # Cathedral Knights — heavy armor guards throughout the garden (DS3: 8+ knights)
        ("CathedralKnight", 32, 30), ("CathedralKnight", 55, 40), ("CathedralKnight", 112, 82),
        ("CathedralKnight", 98, 68), ("CathedralKnight", 42, 38), ("CathedralKnight", 72, 48),
        ("CathedralKnight", 80, 55), ("CathedralKnight", 95, 72),
        # Hollow Slaves (Thrall) — ambush throughout the garden
        ("Thrall", 35, 35), ("Thrall", 88, 62),
        ("Thrall", 22, 22), ("Thrall", 60, 32),
        ("Thrall", 90, 58), ("Thrall", 100, 64), ("Thrall", 108, 70),
        ("Thrall", 118, 78),
        # Pus of Man — x3 on wyvern corpses (DS3 accurate count)
        ("PusOfMan", 52, 42), ("PusOfMan", 48, 76), ("PusOfMan", 58, 84),
        # Rotten Slugs in poison swamp (DS3: several slugs in toxic mist)
        ("RottenSlug", 45, 70), ("RottenSlug", 50, 75), ("RottenSlug", 55, 78),
        ("RottenSlug", 42, 78), ("RottenSlug", 60, 82), ("RottenSlug", 52, 84),
        ("RottenSlug", 48, 72), ("RottenSlug", 56, 68), ("RottenSlug", 44, 82),
        # Crystal Lizard
        ("CrystalLizard", 68, 42),
        # Boss — Oceiros, the Consumed King
        ("MiniBoss", 120, 88),                                      # Oceiros boss entity
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
            "I came to see Oceiros, the Consumed King|He holds the secret of the Path of the Dragon|But it seems I am too late|The dragon stones may still be of use"),
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
    # SESSION 10 FIDELITY PASS — Consumed King's Garden
    # Additional DS3-faithful terrain: crystal shard debris, consumed throne stones,
    # garden pool edges, crystal growth formations, consumed knight patrol debris
    # Crystal formations near entrance (DS3: crystal growths everywhere)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    # Garden pool edge stones (DS3: stagnant water pools with crystal growths)
    fill_tiles(chunk, TILE_WALL, 60, 58, 61, 59)
    fill_tiles(chunk, TILE_WALL, 66, 62, 67, 63)
    fill_tiles(chunk, TILE_WALL, 72, 60, 73, 61)
    # Consumed throne area — throne debris (DS3: Oceiros throne room with crystal growths)
    fill_tiles(chunk, TILE_WALL, 108, 82, 109, 83)
    fill_tiles(chunk, TILE_WALL, 114, 84, 115, 85)
    fill_tiles(chunk, TILE_WALL, 102, 78, 103, 79)
    fill_tiles(chunk, TILE_WALL, 118, 80, 119, 81)
    # Crystal cavern stalactites (DS3: crystal cave area behind Oceiros)
    fill_tiles(chunk, TILE_WALL, 128, 72, 129, 73)
    fill_tiles(chunk, TILE_WALL, 134, 68, 135, 69)
    fill_tiles(chunk, TILE_WALL, 138, 74, 139, 75)
    fill_tiles(chunk, TILE_WALL, 130, 78, 131, 79)
    fill_tiles(chunk, TILE_WALL, 136, 82, 137, 83)
    fill_tiles(chunk, TILE_WALL, 142, 70, 143, 71)
    # Knight patrol path debris (DS3: Cathedral Knights patrol garden paths)
    fill_tiles(chunk, TILE_WALL, 82, 64, 83, 65)
    fill_tiles(chunk, TILE_WALL, 88, 60, 89, 61)
    fill_tiles(chunk, TILE_WALL, 94, 66, 95, 67)
    fill_tiles(chunk, TILE_WALL, 78, 70, 79, 71)
    fill_tiles(chunk, TILE_WALL, 90, 72, 91, 73)
    # Crystal growth clusters (DS3: large crystal formations in garden)
    fill_tiles(chunk, TILE_WALL, 44, 68, 45, 69)
    fill_tiles(chunk, TILE_WALL, 50, 74, 51, 75)
    fill_tiles(chunk, TILE_WALL, 64, 70, 65, 71)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    # Lower garden — Thrall ambush debris (DS3: Thralls hide among crystal debris)
    fill_tiles(chunk, TILE_WALL, 86, 76, 87, 77)
    fill_tiles(chunk, TILE_WALL, 96, 78, 97, 79)
    fill_tiles(chunk, TILE_WALL, 100, 74, 101, 75)

    # SESSION 10 FIDELITY PASS B — Consumed King's Garden
    # Additional DS3-faithful terrain: crystal growth clusters, Oceiros throne room,
    # consumed knight path debris, garden bridge stones, crystal cavern details
    # Entrance garden — crystal growth clusters (DS3: crystals grow wild in garden)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 55)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 40, 60, 41, 61)
    fill_tiles(chunk, TILE_WALL, 46, 62, 47, 63)
    # Garden bridge — stone bridge debris (DS3: stone bridge over garden)
    fill_tiles(chunk, TILE_WALL, 70, 56, 71, 57)
    fill_tiles(chunk, TILE_WALL, 76, 58, 77, 59)
    fill_tiles(chunk, TILE_WALL, 82, 56, 83, 57)
    fill_tiles(chunk, TILE_WALL, 74, 60, 75, 61)
    # Oceiros throne room — throne debris (DS3: Oceiros guards his throne)
    fill_tiles(chunk, TILE_WALL, 104, 76, 105, 77)
    fill_tiles(chunk, TILE_WALL, 110, 78, 111, 79)
    fill_tiles(chunk, TILE_WALL, 116, 76, 117, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 106, 82, 107, 83)
    fill_tiles(chunk, TILE_WALL, 112, 84, 113, 85)
    # Crystal cavern — deep crystal formations (DS3: crystal cave behind throne)
    fill_tiles(chunk, TILE_WALL, 126, 70, 127, 71)
    fill_tiles(chunk, TILE_WALL, 132, 74, 133, 75)
    fill_tiles(chunk, TILE_WALL, 138, 72, 139, 73)
    fill_tiles(chunk, TILE_WALL, 144, 76, 145, 77)
    fill_tiles(chunk, TILE_WALL, 130, 78, 131, 79)
    fill_tiles(chunk, TILE_WALL, 140, 80, 141, 81)
    # Consumed knight patrol — path debris (DS3: Cathedral Knights patrol garden)
    fill_tiles(chunk, TILE_WALL, 62, 66, 63, 67)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 78, 70, 79, 71)
    fill_tiles(chunk, TILE_WALL, 84, 72, 85, 73)
    fill_tiles(chunk, TILE_WALL, 92, 74, 93, 75)
    fill_tiles(chunk, TILE_WALL, 98, 72, 99, 73)
    # Pus of Man area — consumed growth debris (DS3: Pus of Man creatures)
    fill_tiles(chunk, TILE_WALL, 52, 72, 53, 73)
    fill_tiles(chunk, TILE_WALL, 58, 76, 59, 77)
    fill_tiles(chunk, TILE_WALL, 64, 74, 65, 75)
    # Lower garden — Thrall ambush stones (DS3: Thralls hide among debris)
    fill_tiles(chunk, TILE_WALL, 88, 80, 89, 81)
    fill_tiles(chunk, TILE_WALL, 94, 82, 95, 83)
    fill_tiles(chunk, TILE_WALL, 100, 78, 101, 79)
    fill_tiles(chunk, TILE_WALL, 96, 84, 97, 85)


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

    # === EVEN MORE TOMBSTONES — dense DS3 cemetery ===
    # Cemetery path — additional rows of graves (DS3: graveyard packed with headstones)
    fill_tiles(chunk, TILE_WALL, 30, 24, 31, 26)
    fill_tiles(chunk, TILE_WALL, 33, 32, 34, 34)
    fill_tiles(chunk, TILE_WALL, 46, 30, 47, 32)
    fill_tiles(chunk, TILE_WALL, 52, 38, 53, 40)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 44)
    fill_tiles(chunk, TILE_WALL, 63, 34, 64, 36)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 38)
    # Courtyard — broken walls and debris (DS3: ruined courtyard near Gundyr)
    fill_tiles(chunk, TILE_WALL, 72, 46, 73, 48)
    fill_tiles(chunk, TILE_WALL, 80, 54, 81, 56)
    fill_tiles(chunk, TILE_WALL, 85, 58, 86, 60)
    fill_tiles(chunk, TILE_WALL, 95, 62, 96, 64)
    fill_tiles(chunk, TILE_WALL, 78, 64, 79, 66)
    # Black Knight cemetery — dense tombstone rows
    fill_tiles(chunk, TILE_WALL, 44, 58, 45, 60)
    fill_tiles(chunk, TILE_WALL, 52, 62, 53, 64)
    fill_tiles(chunk, TILE_WALL, 60, 58, 61, 60)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 68)
    fill_tiles(chunk, TILE_WALL, 46, 72, 47, 74)
    fill_tiles(chunk, TILE_WALL, 56, 68, 57, 70)
    fill_tiles(chunk, TILE_WALL, 64, 74, 65, 76)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 72)

    # === Champion Gundyr arena — broken fountain and ruins ===
    # DS3: Gundyr fights in a dark version of the Cemetery of Ash arena
    # Broken fountain in center
    fill_tiles(chunk, TILE_WALL, 100, 78, 108, 80)
    fill_tiles(chunk, TILE_WALL, 103, 75, 105, 83)
    # Arena perimeter ruins
    fill_tiles(chunk, TILE_WALL, 85, 68, 87, 72)
    fill_tiles(chunk, TILE_WALL, 120, 85, 122, 88)
    fill_tiles(chunk, TILE_WALL, 110, 95, 112, 98)
    fill_tiles(chunk, TILE_WALL, 125, 92, 127, 95)
    fill_tiles(chunk, TILE_WALL, 90, 90, 92, 93)
    fill_tiles(chunk, TILE_WALL, 115, 98, 117, 100)
    # Scattered debris
    fill_tiles(chunk, TILE_WALL, 108, 88, 110, 90)
    fill_tiles(chunk, TILE_WALL, 98, 92, 100, 94)

    # === Dark coffin entry details ===
    # DS3: you wake up in a coffin, small enclosed stone chamber
    fill_tiles(chunk, TILE_WALL, 10, 12, 12, 14)
    fill_tiles(chunk, TILE_WALL, 18, 10, 20, 12)
    fill_tiles(chunk, TILE_WALL, 14, 18, 16, 20)

    # === Dark Firelink Shrine (SE) — dark mirror of Firelink ===
    fill_tiles(chunk, TILE_GROUND, 115, 95, 150, 130)
    carve_ellipse(chunk, 132, 112, 12, 10)
    # Shrine interior walls — dark coiled sword spot (DS3: no fire, just dark)
    fill_tiles(chunk, TILE_WALL, 128, 108, 132, 110)
    fill_tiles(chunk, TILE_WALL, 136, 108, 140, 110)
    # Throne room walls — 5 empty Lord of Cinder thrones (DS3: dark version)
    fill_tiles(chunk, TILE_WALL, 118, 98, 120, 102)
    fill_tiles(chunk, TILE_WALL, 125, 96, 127, 100)
    fill_tiles(chunk, TILE_WALL, 138, 96, 140, 100)
    fill_tiles(chunk, TILE_WALL, 145, 98, 147, 102)
    # Dark Handmaid alcove
    fill_tiles(chunk, TILE_WALL, 130, 118, 132, 122)
    # Shrine exterior walls
    fill_tiles(chunk, TILE_WALL, 122, 100, 124, 105)
    fill_tiles(chunk, TILE_WALL, 140, 115, 142, 120)
    # Dark shrine entrance pillars
    fill_tiles(chunk, TILE_WALL, 116, 104, 118, 108)
    fill_tiles(chunk, TILE_WALL, 146, 104, 148, 108)

    # === ADDITIONAL DS3 UNTENDED GRAVES — shrine architecture, cemetery depth ===
    # Dark Firelink Shrine — Andre's anvil alcove (DS3: dark Andre works silently)
    fill_tiles(chunk, TILE_WALL, 134, 110, 136, 114)
    fill_tiles(chunk, TILE_WALL, 130, 114, 132, 118)
    # Shrine — Ludleth's throne seat (DS3: Ludleth present in dark shrine)
    fill_tiles(chunk, TILE_WALL, 142, 106, 144, 109)
    # Shrine — Fire Keeper's enclosure (DS3: dark Fire Keeper stands in silence)
    fill_tiles(chunk, TILE_WALL, 136, 120, 138, 124)
    fill_tiles(chunk, TILE_WALL, 142, 122, 144, 126)
    # Shrine — shattered coiled sword debris (DS3: sword present but unlit)
    fill_tiles(chunk, TILE_WALL, 128, 114, 130, 116)
    fill_tiles(chunk, TILE_WALL, 134, 116, 136, 118)
    # Cemetery — collapsed grave walls (DS3: dark cemetery with fallen headstones)
    fill_tiles(chunk, TILE_WALL, 30, 32, 31, 34)
    fill_tiles(chunk, TILE_WALL, 36, 36, 37, 38)
    fill_tiles(chunk, TILE_WALL, 54, 40, 55, 42)
    fill_tiles(chunk, TILE_WALL, 48, 44, 49, 46)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 48)
    # Gundyr arena — collapsed arch stones (DS3: mirror of Cemetery of Ash arena)
    fill_tiles(chunk, TILE_WALL, 92, 74, 94, 76)
    fill_tiles(chunk, TILE_WALL, 112, 82, 114, 84)
    fill_tiles(chunk, TILE_WALL, 102, 90, 104, 92)
    fill_tiles(chunk, TILE_WALL, 122, 88, 124, 90)
    fill_tiles(chunk, TILE_WALL, 96, 86, 98, 88)
    # Dark path — dead tree stumps (DS3: withered trees in darkness)
    fill_tiles(chunk, TILE_WALL, 22, 18, 24, 20)
    fill_tiles(chunk, TILE_WALL, 68, 42, 70, 44)

    # === SESSION 6 FIDELITY PASS — Untended Graves ===
    # Dark coffin entry — stone lid debris (DS3: coffin you wake up in breaks open)
    fill_tiles(chunk, TILE_WALL, 12, 8, 14, 10)
    fill_tiles(chunk, TILE_WALL, 22, 14, 24, 16)
    fill_tiles(chunk, TILE_WALL, 8, 16, 10, 18)
    fill_tiles(chunk, TILE_WALL, 26, 10, 28, 12)
    # Dark cemetery path — more fallen headstones (DS3: destroyed graveyard)
    fill_tiles(chunk, TILE_WALL, 34, 26, 36, 28)
    fill_tiles(chunk, TILE_WALL, 40, 32, 42, 34)
    fill_tiles(chunk, TILE_WALL, 56, 36, 58, 38)
    fill_tiles(chunk, TILE_WALL, 50, 40, 52, 42)
    fill_tiles(chunk, TILE_WALL, 60, 44, 62, 46)
    fill_tiles(chunk, TILE_WALL, 44, 42, 46, 44)
    # Dark courtyard — more broken walls (DS3: ruined structure near Gundyr approach)
    fill_tiles(chunk, TILE_WALL, 64, 52, 66, 54)
    fill_tiles(chunk, TILE_WALL, 74, 56, 76, 58)
    fill_tiles(chunk, TILE_WALL, 84, 60, 86, 62)
    fill_tiles(chunk, TILE_WALL, 90, 64, 92, 66)
    fill_tiles(chunk, TILE_WALL, 78, 66, 80, 68)
    # Black Knight cemetery — more dense graves (DS3: dark mirror cemetery)
    fill_tiles(chunk, TILE_WALL, 40, 56, 42, 58)
    fill_tiles(chunk, TILE_WALL, 54, 60, 56, 62)
    fill_tiles(chunk, TILE_WALL, 62, 64, 64, 66)
    fill_tiles(chunk, TILE_WALL, 66, 72, 68, 74)
    fill_tiles(chunk, TILE_WALL, 52, 70, 54, 72)
    fill_tiles(chunk, TILE_WALL, 74, 68, 76, 70)
    # Gundyr arena — more collapsed arch stones (DS3: mirror of Cemetery of Ash arena)
    fill_tiles(chunk, TILE_WALL, 86, 72, 88, 74)
    fill_tiles(chunk, TILE_WALL, 116, 84, 118, 86)
    fill_tiles(chunk, TILE_WALL, 100, 88, 102, 90)
    fill_tiles(chunk, TILE_WALL, 120, 92, 122, 94)
    fill_tiles(chunk, TILE_WALL, 106, 94, 108, 96)
    # Dark Firelink — more shrine interior walls (DS3: exact dark mirror of Firelink)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 104)
    fill_tiles(chunk, TILE_WALL, 148, 102, 150, 104)
    fill_tiles(chunk, TILE_WALL, 124, 110, 126, 112)
    fill_tiles(chunk, TILE_WALL, 144, 110, 146, 112)
    fill_tiles(chunk, TILE_WALL, 132, 124, 134, 126)
    fill_tiles(chunk, TILE_WALL, 138, 126, 140, 128)
    # Dark path connections — more debris along route
    fill_tiles(chunk, TILE_WALL, 20, 22, 22, 24)
    fill_tiles(chunk, TILE_WALL, 72, 48, 74, 50)
    fill_tiles(chunk, TILE_WALL, 82, 70, 84, 72)

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

    # ================================================================
    # SESSION 9 FIDELITY PASS — UntendedGraves architectural details
    # ================================================================
    # Dark cemetery entry — collapsed coffin stones (DS3: broken coffins at entrance)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 23)
    fill_tiles(chunk, TILE_WALL, 14, 26, 15, 27)
    fill_tiles(chunk, TILE_WALL, 28, 16, 29, 17)
    # Dark cemetery path — tilted gravestones (DS3: dark version of Cemetery of Ash)
    fill_tiles(chunk, TILE_WALL, 34, 32, 35, 33)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    fill_tiles(chunk, TILE_WALL, 30, 40, 31, 41)
    fill_tiles(chunk, TILE_WALL, 40, 28, 41, 29)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 45)
    # Knight cemetery — black knight armor stands (DS3: suits of armor as decoration)
    fill_tiles(chunk, TILE_WALL, 46, 50, 47, 51)
    fill_tiles(chunk, TILE_WALL, 50, 54, 51, 55)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 59)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 49)
    fill_tiles(chunk, TILE_WALL, 48, 60, 49, 61)
    # Gundyr arena approach — eroded stone arches (DS3: same layout as Cemetery of Ash but darker)
    fill_tiles(chunk, TILE_WALL, 60, 66, 61, 67)
    fill_tiles(chunk, TILE_WALL, 64, 70, 65, 71)
    fill_tiles(chunk, TILE_WALL, 56, 74, 57, 75)
    fill_tiles(chunk, TILE_WALL, 68, 64, 69, 65)
    # Gundyr arena — darkened perimeter ruins (DS3: identical to Iudex arena but unlit)
    fill_tiles(chunk, TILE_WALL, 80, 72, 81, 73)
    fill_tiles(chunk, TILE_WALL, 84, 76, 85, 77)
    fill_tiles(chunk, TILE_WALL, 76, 80, 77, 81)
    fill_tiles(chunk, TILE_WALL, 88, 70, 89, 71)
    fill_tiles(chunk, TILE_WALL, 82, 82, 83, 83)
    # Dark Firelink Shrine — extinguished coiled sword stump (DS3: dark version of Firelink)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 93)
    fill_tiles(chunk, TILE_WALL, 96, 96, 97, 97)
    fill_tiles(chunk, TILE_WALL, 108, 86, 109, 87)
    fill_tiles(chunk, TILE_WALL, 102, 98, 103, 99)
    fill_tiles(chunk, TILE_WALL, 112, 94, 113, 95)
    # Shrine interior — darkened stone pillars (DS3: same layout but no fire)
    fill_tiles(chunk, TILE_WALL, 118, 90, 119, 91)
    fill_tiles(chunk, TILE_WALL, 124, 94, 125, 95)
    fill_tiles(chunk, TILE_WALL, 116, 98, 117, 99)

    # ================================================================
    # SESSION 11 FIDELITY PASS — UntendedGraves fine architectural details
    # ================================================================
    # Dark coffin entry — shattered lid fragments (DS3: coffin breaks open in darkness)
    fill_tiles(chunk, TILE_WALL, 9, 10, 10, 11)
    fill_tiles(chunk, TILE_WALL, 16, 12, 17, 13)
    fill_tiles(chunk, TILE_WALL, 12, 16, 13, 17)
    # Dark cemetery path — sunken grave pits (DS3: collapsed graves in dark soil)
    fill_tiles(chunk, TILE_WALL, 26, 30, 27, 31)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 35)
    fill_tiles(chunk, TILE_WALL, 38, 28, 39, 29)
    fill_tiles(chunk, TILE_WALL, 44, 34, 45, 35)
    fill_tiles(chunk, TILE_WALL, 48, 38, 49, 39)
    fill_tiles(chunk, TILE_WALL, 56, 32, 57, 33)
    # Dark courtyard — eroded stone floor debris (DS3: worn stone courtyard in darkness)
    fill_tiles(chunk, TILE_WALL, 66, 48, 67, 49)
    fill_tiles(chunk, TILE_WALL, 74, 52, 75, 53)
    fill_tiles(chunk, TILE_WALL, 82, 56, 83, 57)
    fill_tiles(chunk, TILE_WALL, 90, 60, 91, 61)
    fill_tiles(chunk, TILE_WALL, 78, 62, 79, 63)
    fill_tiles(chunk, TILE_WALL, 86, 66, 87, 67)
    # Black Knight cemetery — broken iron fence (DS3: rusted fence around graves)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 55)
    fill_tiles(chunk, TILE_WALL, 56, 56, 57, 57)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    fill_tiles(chunk, TILE_WALL, 48, 68, 49, 69)
    fill_tiles(chunk, TILE_WALL, 58, 72, 59, 73)
    fill_tiles(chunk, TILE_WALL, 68, 76, 69, 77)
    # Gundyr arena — darkened coffin debris (DS3: scattered coffins in dark arena)
    fill_tiles(chunk, TILE_WALL, 84, 74, 85, 75)
    fill_tiles(chunk, TILE_WALL, 92, 78, 93, 79)
    fill_tiles(chunk, TILE_WALL, 116, 86, 117, 87)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)
    fill_tiles(chunk, TILE_WALL, 126, 90, 127, 91)
    # Dark Firelink — extinguished bonfire ash pile (DS3: cold ash where bonfire should be)
    fill_tiles(chunk, TILE_WALL, 130, 112, 131, 113)
    fill_tiles(chunk, TILE_WALL, 126, 116, 127, 117)
    fill_tiles(chunk, TILE_WALL, 134, 120, 135, 121)
    fill_tiles(chunk, TILE_WALL, 140, 118, 141, 119)
    # Dark shrine — collapsed rafter debris (DS3: rafters in darkness)
    fill_tiles(chunk, TILE_WALL, 122, 106, 123, 107)
    fill_tiles(chunk, TILE_WALL, 146, 108, 147, 109)
    fill_tiles(chunk, TILE_WALL, 128, 122, 129, 123)
    fill_tiles(chunk, TILE_WALL, 142, 124, 143, 125)
    # Path connections — eroded stone path edges (DS3: crumbling path borders)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 64, 46, 65, 47)
    fill_tiles(chunk, TILE_WALL, 76, 50, 77, 51)
    fill_tiles(chunk, TILE_WALL, 84, 68, 85, 69)
    fill_tiles(chunk, TILE_WALL, 110, 90, 111, 91)

        # --- Player spawn ---
    spawn_px, spawn_py = 15 * 16, 15 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))    # Entry
    entities.append(make_entity("Bonfire", 105 * 16, 82 * 16))   # Champion Gundyr

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 105 * 16, 78 * 16))  # Champion Gundyr

    # --- Enemies — DS3 Untended Graves (wiki-accurate):
    # Black Knights are the primary enemies — dark mirror of Cemetery of Ash.
    # No Grave Wardens, Corvians, or Pus of Man in this area (those belong elsewhere).
    # Champion Gundyr is the boss.
    enemy_data = [
        # Black Knights — DS3: 4 Black Knights patrol the dark cemetery
        # (1 near cemetery path, 1 in middle courtyard, 1 near Gundyr approach, 1 near dark Firelink)
        ("BlackKnight", 45, 35),                                     # Cemetery path (greatsword)
        ("BlackKnight", 62, 45),                                     # Middle courtyard (sword+shield)
        ("BlackKnight", 75, 55),                                     # Gundyr approach (halberd)
        ("BlackKnight", 88, 58),                                     # Near arena edge (greatsword)
        # Starved Hounds — DS3: 2 hounds in the dark cemetery
        ("StarvedHound", 48, 42), ("StarvedHound", 70, 52),
        # Crystal Lizard — DS3: 1 near cemetery path
        ("CrystalLizard", 40, 32),
        # Ravenous Crystal Lizard — DS3: 2 near Dark Firelink area
        ("CrystalLizard", 125, 105), ("CrystalLizard", 130, 110),
        # Boss — Champion Gundyr
        ("MiniBoss", 105, 78),                                      # Champion Gundyr boss entity
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
            "What is it? There is only dark here|The fire has long been out|I will tend to the ash, as I always have|There is nothing else for it"),
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
    # SESSION 10 FIDELITY PASS — Untended Graves
    # Additional DS3-faithful terrain: collapsed coffin stones, tilted gravestones,
    # Dark Firelink pillar fragments, Gundyr arena debris, dark cemetery path edges
    # Dark cemetery path — tilted gravestones (DS3: tilted broken gravestones)
    fill_tiles(chunk, TILE_WALL, 52, 88, 53, 89)
    fill_tiles(chunk, TILE_WALL, 58, 92, 59, 93)
    fill_tiles(chunk, TILE_WALL, 64, 86, 65, 87)
    fill_tiles(chunk, TILE_WALL, 70, 90, 71, 91)
    fill_tiles(chunk, TILE_WALL, 76, 94, 77, 95)
    fill_tiles(chunk, TILE_WALL, 82, 88, 83, 89)
    # Cemetery approach — collapsed coffins (DS3: broken coffins along path)
    fill_tiles(chunk, TILE_WALL, 88, 96, 89, 97)
    fill_tiles(chunk, TILE_WALL, 94, 100, 95, 101)
    fill_tiles(chunk, TILE_WALL, 84, 104, 85, 105)
    fill_tiles(chunk, TILE_WALL, 90, 108, 91, 109)
    # Gundyr arena — arena debris (DS3: ruined arena with debris)
    fill_tiles(chunk, TILE_WALL, 108, 112, 109, 113)
    fill_tiles(chunk, TILE_WALL, 114, 116, 115, 117)
    fill_tiles(chunk, TILE_WALL, 118, 120, 119, 121)
    fill_tiles(chunk, TILE_WALL, 104, 118, 105, 119)
    fill_tiles(chunk, TILE_WALL, 122, 114, 123, 115)
    fill_tiles(chunk, TILE_WALL, 110, 124, 111, 125)
    # Gundyr approach — more tombstone clusters (DS3: dense dark cemetery)
    fill_tiles(chunk, TILE_WALL, 96, 104, 97, 105)
    fill_tiles(chunk, TILE_WALL, 102, 108, 103, 109)
    fill_tiles(chunk, TILE_WALL, 98, 112, 99, 113)
    fill_tiles(chunk, TILE_WALL, 106, 110, 107, 111)
    # Dark Firelink — collapsed pillar fragments (DS3: ruined version of Firelink)
    fill_tiles(chunk, TILE_WALL, 132, 128, 133, 129)
    fill_tiles(chunk, TILE_WALL, 138, 132, 139, 133)
    fill_tiles(chunk, TILE_WALL, 144, 128, 145, 129)
    fill_tiles(chunk, TILE_WALL, 136, 136, 137, 137)
    fill_tiles(chunk, TILE_WALL, 142, 140, 143, 141)
    fill_tiles(chunk, TILE_WALL, 148, 134, 149, 135)
    # Dark Firelink interior — shrine debris (DS3: dark version of Firelink interior)
    fill_tiles(chunk, TILE_WALL, 128, 140, 129, 141)
    fill_tiles(chunk, TILE_WALL, 134, 144, 135, 145)
    fill_tiles(chunk, TILE_WALL, 140, 138, 141, 139)
    fill_tiles(chunk, TILE_WALL, 146, 142, 147, 143)


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

    # === MORE ARCHDRAGON PEAK DETAILS — DS3 fidelity ===
    # Mountain entry — stone steps and cliff walls (DS3: path winds up the mountain)
    fill_tiles(chunk, TILE_WALL, 10, 115, 12, 118)
    fill_tiles(chunk, TILE_WALL, 22, 128, 24, 130)
    fill_tiles(chunk, TILE_WALL, 30, 135, 32, 138)
    fill_tiles(chunk, TILE_WALL, 16, 140, 18, 142)
    fill_tiles(chunk, TILE_WALL, 28, 142, 30, 145)
    # Serpent barracks — more training grounds walls
    # DS3: outdoor training area with serpent-man warriors
    fill_tiles(chunk, TILE_WALL, 30, 88, 32, 90)
    fill_tiles(chunk, TILE_WALL, 45, 95, 47, 97)
    fill_tiles(chunk, TILE_WALL, 55, 98, 57, 100)
    fill_tiles(chunk, TILE_WALL, 40, 108, 42, 110)
    fill_tiles(chunk, TILE_WALL, 62, 108, 64, 110)
    fill_tiles(chunk, TILE_WALL, 35, 115, 37, 118)
    fill_tiles(chunk, TILE_WALL, 50, 112, 52, 114)
    # Wyvern arena — more dragon skeleton debris (DS3: massive dead dragon bones)
    fill_tiles(chunk, TILE_WALL, 38, 58, 40, 60)
    fill_tiles(chunk, TILE_WALL, 48, 65, 50, 67)
    fill_tiles(chunk, TILE_WALL, 60, 58, 62, 60)
    fill_tiles(chunk, TILE_WALL, 70, 72, 72, 74)
    fill_tiles(chunk, TILE_WALL, 42, 78, 44, 80)
    fill_tiles(chunk, TILE_WALL, 75, 82, 77, 84)
    # Dragon-Kin Mausoleum — altar and dragon statue walls
    # DS3: interior with dragon altar, serpent-man summoners
    fill_tiles(chunk, TILE_WALL, 65, 40, 67, 42)
    fill_tiles(chunk, TILE_WALL, 75, 45, 77, 47)
    fill_tiles(chunk, TILE_WALL, 82, 52, 84, 54)
    fill_tiles(chunk, TILE_WALL, 92, 45, 94, 47)
    fill_tiles(chunk, TILE_WALL, 88, 55, 90, 57)
    # Storm path — wind-sculpted rocks and ruins (DS3: ascending path with lightning)
    fill_tiles(chunk, TILE_WALL, 92, 30, 94, 32)
    fill_tiles(chunk, TILE_WALL, 102, 35, 104, 37)
    fill_tiles(chunk, TILE_WALL, 110, 45, 112, 47)
    fill_tiles(chunk, TILE_WALL, 120, 38, 122, 40)
    fill_tiles(chunk, TILE_WALL, 98, 50, 100, 52)
    # Great Belfry — bell tower architecture (DS3: massive bell structure)
    fill_tiles(chunk, TILE_WALL, 110, 14, 112, 16)
    fill_tiles(chunk, TILE_WALL, 125, 15, 127, 18)
    fill_tiles(chunk, TILE_WALL, 135, 18, 137, 20)
    fill_tiles(chunk, TILE_WALL, 120, 30, 122, 32)
    fill_tiles(chunk, TILE_WALL, 132, 28, 134, 30)
    # Nameless arena — more storm debris (DS3: lightning-scorched mountaintop)
    fill_tiles(chunk, TILE_WALL, 105, 78, 107, 80)
    fill_tiles(chunk, TILE_WALL, 118, 82, 120, 84)
    fill_tiles(chunk, TILE_WALL, 138, 85, 140, 88)
    fill_tiles(chunk, TILE_WALL, 125, 98, 127, 100)
    fill_tiles(chunk, TILE_WALL, 145, 105, 147, 108)
    fill_tiles(chunk, TILE_WALL, 132, 108, 134, 110)
    fill_tiles(chunk, TILE_WALL, 148, 95, 150, 98)

    # === SESSION 6 FIDELITY PASS — Archdragon Peak ===
    # Mountain entry — rocky cliff faces (DS3: steep mountain path with stone steps)
    fill_tiles(chunk, TILE_WALL, 8, 112, 10, 114)
    fill_tiles(chunk, TILE_WALL, 14, 125, 16, 127)
    fill_tiles(chunk, TILE_WALL, 24, 132, 26, 134)
    fill_tiles(chunk, TILE_WALL, 32, 140, 34, 142)
    fill_tiles(chunk, TILE_WALL, 12, 138, 14, 140)
    # Serpent barracks — weapon racks and pillars (DS3: outdoor arena with stone pillars)
    fill_tiles(chunk, TILE_WALL, 28, 92, 30, 94)
    fill_tiles(chunk, TILE_WALL, 44, 100, 46, 102)
    fill_tiles(chunk, TILE_WALL, 56, 102, 58, 104)
    fill_tiles(chunk, TILE_WALL, 64, 112, 66, 114)
    fill_tiles(chunk, TILE_WALL, 42, 112, 44, 114)
    fill_tiles(chunk, TILE_WALL, 54, 115, 56, 117)
    # Wyvern arena — massive dragon ribs (DS3: huge dragon skeleton on bridge)
    fill_tiles(chunk, TILE_WALL, 36, 52, 38, 54)
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 64)
    fill_tiles(chunk, TILE_WALL, 74, 76, 76, 78)
    fill_tiles(chunk, TILE_WALL, 46, 76, 48, 78)
    fill_tiles(chunk, TILE_WALL, 56, 80, 58, 82)
    # Mausoleum — dragon stone altar details (DS3: dragon-kin meditation chamber)
    fill_tiles(chunk, TILE_WALL, 68, 44, 70, 46)
    fill_tiles(chunk, TILE_WALL, 76, 50, 78, 52)
    fill_tiles(chunk, TILE_WALL, 84, 46, 86, 48)
    fill_tiles(chunk, TILE_WALL, 94, 42, 96, 44)
    fill_tiles(chunk, TILE_WALL, 66, 56, 68, 58)
    # Storm path — lightning-charred rocks (DS3: storm-swept mountain ridge)
    fill_tiles(chunk, TILE_WALL, 90, 34, 92, 36)
    fill_tiles(chunk, TILE_WALL, 108, 38, 110, 40)
    fill_tiles(chunk, TILE_WALL, 116, 40, 118, 42)
    fill_tiles(chunk, TILE_WALL, 96, 44, 98, 46)
    fill_tiles(chunk, TILE_WALL, 124, 35, 126, 37)
    # Belfry — tower arch buttresses (DS3: massive bell tower with stone arches)
    fill_tiles(chunk, TILE_WALL, 106, 12, 108, 14)
    fill_tiles(chunk, TILE_WALL, 122, 12, 124, 14)
    fill_tiles(chunk, TILE_WALL, 138, 20, 140, 22)
    fill_tiles(chunk, TILE_WALL, 116, 32, 118, 34)
    fill_tiles(chunk, TILE_WALL, 130, 30, 132, 32)
    # Nameless arena — storm-battered summit (DS3: open sky arena on peak)
    fill_tiles(chunk, TILE_WALL, 102, 72, 104, 74)
    fill_tiles(chunk, TILE_WALL, 130, 78, 132, 80)
    fill_tiles(chunk, TILE_WALL, 142, 88, 144, 90)
    fill_tiles(chunk, TILE_WALL, 136, 98, 138, 100)
    fill_tiles(chunk, TILE_WALL, 148, 102, 150, 104)
    fill_tiles(chunk, TILE_WALL, 122, 112, 124, 114)

    # ================================================================
    # SESSION 9 FIDELITY PASS — ArchdragonPeak architectural details
    # ================================================================
    # Entry path — dragon-crest pillars (DS3: ornate pillars with dragon motifs)
    fill_tiles(chunk, TILE_WALL, 16, 128, 17, 129)
    fill_tiles(chunk, TILE_WALL, 22, 130, 23, 131)
    fill_tiles(chunk, TILE_WALL, 12, 134, 13, 135)
    fill_tiles(chunk, TILE_WALL, 26, 126, 27, 127)
    # Ancient dragon ruins — petrified dragon bones (DS3: massive skeletal remains)
    fill_tiles(chunk, TILE_WALL, 34, 118, 35, 119)
    fill_tiles(chunk, TILE_WALL, 38, 122, 39, 123)
    fill_tiles(chunk, TILE_WALL, 30, 124, 31, 125)
    fill_tiles(chunk, TILE_WALL, 42, 116, 43, 117)
    fill_tiles(chunk, TILE_WALL, 36, 126, 37, 127)
    # Serpent-Man temple — carved stone serpents (DS3: serpent imagery everywhere)
    fill_tiles(chunk, TILE_WALL, 52, 108, 53, 109)
    fill_tiles(chunk, TILE_WALL, 56, 112, 57, 113)
    fill_tiles(chunk, TILE_WALL, 48, 114, 49, 115)
    fill_tiles(chunk, TILE_WALL, 60, 106, 61, 107)
    # Belfry — giant bell stone supports (DS3: massive bell structure)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    fill_tiles(chunk, TILE_WALL, 72, 100, 73, 101)
    fill_tiles(chunk, TILE_WALL, 64, 102, 65, 103)
    fill_tiles(chunk, TILE_WALL, 76, 94, 77, 95)
    fill_tiles(chunk, TILE_WALL, 70, 104, 71, 105)
    # Dragon-Kin Mausoleum — ritual altar stones (DS3: meditation area)
    fill_tiles(chunk, TILE_WALL, 80, 86, 81, 87)
    fill_tiles(chunk, TILE_WALL, 84, 90, 85, 91)
    fill_tiles(chunk, TILE_WALL, 76, 92, 77, 93)
    fill_tiles(chunk, TILE_WALL, 88, 84, 89, 85)
    # Nameless King arena — storm-worn pillars (DS3: arena atop the peak)
    fill_tiles(chunk, TILE_WALL, 120, 72, 121, 73)
    fill_tiles(chunk, TILE_WALL, 126, 76, 127, 77)
    fill_tiles(chunk, TILE_WALL, 132, 70, 133, 71)
    fill_tiles(chunk, TILE_WALL, 138, 74, 139, 75)
    fill_tiles(chunk, TILE_WALL, 116, 80, 117, 81)
    fill_tiles(chunk, TILE_WALL, 144, 78, 145, 79)
    # Twisted stone formations (DS3: wind-sculpted rock on the peak)
    fill_tiles(chunk, TILE_WALL, 100, 92, 101, 93)
    fill_tiles(chunk, TILE_WALL, 108, 88, 109, 89)
    fill_tiles(chunk, TILE_WALL, 104, 96, 105, 97)
    fill_tiles(chunk, TILE_WALL, 112, 84, 113, 85)

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
        ("DrakebloodKnight", 110, 30), ("DrakebloodKnight", 142, 88),
        ("DrakebloodKnight", 78, 52),                                     # Additional summoned knight
        # Havel Knight — appears at Great Belfry area (DS3: tough NPC near fallen wyvern)
        ("HavelKnight", 128, 70),
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
        ("RingDrop", "Calamity Ring", 80, 52, 0),                  # Altar dragon gesture
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
            "The Nameless King awaits atop this peak|He is the firstborn of Gwyn, Lord of Cinder|I have come this far to face him|The dragons and their secrets end here"),
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
    # SESSION 10 FIDELITY PASS — Archdragon Peak
    # Additional DS3-faithful terrain: dragon-crest altar stones, serpent temple
    # pillars, belfry step stones, wyvern perch debris, summoner altar stones
    # Dragon-crest altar stones (DS3: dragon crest medallion at entrance)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 33)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    # Serpent temple pillars (DS3: serpentine architecture throughout)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 49)
    fill_tiles(chunk, TILE_WALL, 46, 56, 47, 57)
    # Ancient dragon head stones (DS3: petrified dragon heads line the path)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 41)
    fill_tiles(chunk, TILE_WALL, 68, 44, 69, 45)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    # Belfry area — step stones and bell debris (DS3: great belfry with bell)
    fill_tiles(chunk, TILE_WALL, 122, 64, 123, 65)
    fill_tiles(chunk, TILE_WALL, 126, 68, 127, 69)
    fill_tiles(chunk, TILE_WALL, 130, 72, 131, 73)
    fill_tiles(chunk, TILE_WALL, 118, 70, 119, 71)
    fill_tiles(chunk, TILE_WALL, 134, 66, 135, 67)
    # Wyvern perch — cliff debris (DS3: wyvern perches on cliff edge)
    fill_tiles(chunk, TILE_WALL, 78, 38, 79, 39)
    fill_tiles(chunk, TILE_WALL, 84, 42, 85, 43)
    fill_tiles(chunk, TILE_WALL, 90, 38, 91, 39)
    # Summoner altar stones (DS3: Serpent-Man Summoners at altars)
    fill_tiles(chunk, TILE_WALL, 106, 28, 107, 29)
    fill_tiles(chunk, TILE_WALL, 112, 32, 113, 33)
    fill_tiles(chunk, TILE_WALL, 140, 84, 141, 85)
    fill_tiles(chunk, TILE_WALL, 146, 88, 147, 89)
    # Path edge stones (DS3: stone-lined mountain paths)
    fill_tiles(chunk, TILE_WALL, 38, 42, 39, 43)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 59)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 51)
    fill_tiles(chunk, TILE_WALL, 98, 44, 99, 45)
    # Nameless King gate — ancient stones (DS3: gate to boss arena)
    fill_tiles(chunk, TILE_WALL, 124, 88, 125, 89)
    fill_tiles(chunk, TILE_WALL, 130, 92, 131, 93)
    fill_tiles(chunk, TILE_WALL, 136, 86, 137, 87)

    # SESSION 10 PASS B — ArchdragonPeak
    # Additional DS3 terrain: dragon-crest steps, serpent altar stones, wyvern bridge debris
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 51)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 59)
    fill_tiles(chunk, TILE_WALL, 92, 52, 93, 53)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 61)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 57)
    fill_tiles(chunk, TILE_WALL, 128, 64, 129, 65)
    fill_tiles(chunk, TILE_WALL, 140, 58, 141, 59)
    fill_tiles(chunk, TILE_WALL, 136, 72, 137, 73)
    fill_tiles(chunk, TILE_WALL, 120, 68, 121, 69)
    fill_tiles(chunk, TILE_WALL, 108, 74, 109, 75)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 84, 66, 85, 67)


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
