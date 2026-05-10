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

LEVEL_UIDS = {
    "CemeteryOfAsh": 1,
    "LothricWall": 2,
    "UndeadSettlement": 3,
    "RoadOfSacrifices": 4,
    "FarronKeep": 5,
    "CathedralDeep": 6,
    "CatacombsOfCarthus": 7,
    "SmoulderingLake": 8,
    "Irithyll": 9,
    "IrithyllDungeon": 10,
    "ProfanedCapital": 11,
    "AnorLondo": 12,
    "LothricCastle": 13,
    "GrandArchives": 14,
    "KilnOfTheFirstFlame": 15,
    "ConsumedKingsGarden": 16,
    "UntendedGraves": 17,
    "ArchdragonPeak": 18,
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
    "LothricWyvern": "PusOfMan",
    "Hodrick": "MiniBoss",
    "CagedHollow": "PeasantHollow",
    "Ghrul": "Ghru",
    "DarkSpirit": "Knight",
    "Berengaria": "DarkMage",
    "SkeletonSwordman": "Skeleton",
    "SkeletonBall": "Skeleton",
    "CarthusWorm": "MiniBoss",
    "GiantHollow": "GiantSlave",
    "AncientWyvern": "PusOfMan",
    "NamelessKing": "MiniBoss",
    "ConsumedKingKnight": "CathedralKnight",
    "ConsumedKingGuard": "WingedKnight",
    "FlyingDragon": "PusOfMan",
    "Harpe": "Skeleton",
    "Leech": "Dog",
    "Blowdart": "Archer",
    "GraveWarden": "CathedralGraveWarden",
    "CursedWood": "MiniBoss",
    "Demon": "FireDemon",
    "Spider": "Basilisk",
    "GargoyleDog": "Dog",
}


def new_chunk():
    return [[TILE_WALL for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]


def fill_tiles(chunk, tile, x1, y1, x2, y2):
    for y in range(max(0, y1), min(CHUNK_SIZE, y2 + 1)):
        for x in range(max(0, x1), min(CHUNK_SIZE, x2 + 1)):
            chunk[y][x] = tile


def carve_ellipse(chunk, cx, cy, rx, ry):
    for y in range(max(0, cy - ry), min(CHUNK_SIZE, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(CHUNK_SIZE, cx + rx + 1)):
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
    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            csv.append(chunk[y][x])
    return csv


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


# --- Coordinate scaling ---

def scale_tile(px, py, src_w, src_h):
    """Scale design doc pixel coords to tile coords in our 160x160 grid."""
    tx = MARGIN + int((px / src_w) * USABLE)
    ty = MARGIN + int((py / src_h) * USABLE)
    return max(1, min(CHUNK_SIZE - 2, tx)), max(1, min(CHUNK_SIZE - 2, ty))


def scale_px(px, py, src_w, src_h):
    """Scale design doc pixel coords to our map pixel coords."""
    tx = (MARGIN + (px / src_w) * USABLE) * TILE_SIZE
    ty = (MARGIN + (py / src_h) * USABLE) * TILE_SIZE
    return tx, ty


def scale_px_dim(dim, src_w, _src_h):
    """Scale a single dimension proportionally."""
    return max(TILE_SIZE, (dim / src_w) * USABLE * TILE_SIZE)


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
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 78, 22, 82, 34)

    # ================================================================
    # 17. FIRELINK SHRINE (y=6-22, x=50-110)
    # Central hub — warm firelight, NPCs, services
    # ================================================================
    carve_ellipse(chunk, 80, 16, 22, 10)
    # West wing — Andre's forge
    carve_ellipse(chunk, 50, 18, 10, 7)
    fill_tiles(chunk, TILE_GROUND, 56, 14, 62, 20)
    # East wing — Shrine Handmaiden
    carve_ellipse(chunk, 110, 18, 10, 7)
    fill_tiles(chunk, TILE_GROUND, 98, 14, 104, 20)
    # North exit to High Wall of Lothric
    fill_tiles(chunk, TILE_GROUND, 76, 6, 84, 10)

    # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    # --- Player Spawn — coffin at SW corner ---
    spawn_px, spawn_py = 25 * 16, 152 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    # Cemetery of Ash bonfire — dead tree clearing
    entities.append(make_entity("Bonfire", 72 * 16, 95 * 16))
    # Firelink Shrine bonfire — central hub
    entities.append(make_entity("Bonfire", 80 * 16, 16 * 16))

    # --- Boss — Iudex Gundyr at arena center ---
    entities.append(make_entity("BossSpawn", 80 * 16, 48 * 16))

    # --- Cemetery Enemies ---
    # Hollow Assassins — first encounter (crouching ambush at path start)
    entities.append(make_entity("Enemy", 56 * 16, 152 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowAssassin")]))
    entities.append(make_entity("Enemy", 64 * 16, 150 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowAssassin")]))
    # Hollow Assassin — broken fountain clearing
    entities.append(make_entity("Enemy", 74 * 16, 136 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowAssassin")]))
    # Hollow Assassin — broken arch (crossbow position)
    entities.append(make_entity("Enemy", 76 * 16, 116 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowAssassin")]))
    # Hollow Assassin — post-bonfire fork area
    entities.append(make_entity("Enemy", 66 * 16, 86 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "HollowAssassin")]))
    # Starved Hounds — near bonfire clearing, patrol the graves
    entities.append(make_entity("Enemy", 68 * 16, 96 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "StarvedHound")]))
    entities.append(make_entity("Enemy", 78 * 16, 96 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "StarvedHound")]))
    # Crystal Lizard — deep in the water chasm, drops titanite
    entities.append(make_entity("Enemy", 136 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", "CrystalLizard")]))

    # --- Firelink Shrine NPCs ---
    entities.append(make_entity("Npc", 78 * 16, 14 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "LevelUp"),
        make_field("color", "Color", "#FFFFFF"),
        make_field("dialogue", "String",
            "Welcome to Firelink Shrine|May the flames guide your way"),
    ]))
    entities.append(make_entity("Npc", 50 * 16, 18 * 16, [
        make_field("name", "String", "Andre"),
        make_field("kind", "LocalEnum.NpcKind", "Blacksmith"),
        make_field("color", "Color", "#C0C0C0"),
        make_field("dialogue", "String",
            "What do you need?|I can reinforce your weapons"),
    ]))
    entities.append(make_entity("Npc", 110 * 16, 18 * 16, [
        make_field("name", "String", "Shrine Handmaiden"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7355"),
        make_field("dialogue", "String",
            "What is it? Buy something|Or be on your way"),
    ]))
    entities.append(make_entity("Npc", 86 * 16, 12 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String",
            "Oh, another Unkindled|The Farron Keep... that is where you should go"),
    ]))

    # --- Cemetery Items ---
    # Estus Flask + Ashen Estus — next to coffin at start
    entities.append(make_entity("Item", 27 * 16, 150 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Estus Flask")]))
    entities.append(make_entity("Item", 23 * 16, 150 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Ashen Estus Flask")]))
    # Soul of a Deserted Corpse — side pocket south of first encounter
    entities.append(make_entity("Item", 62 * 16, 157 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("value", "Int", 200),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    # Firebomb x5 — firebomb cliff end pocket
    entities.append(make_entity("Item", 38 * 16, 88 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    # Titanite Shard — firebomb cliff, on a tomb
    entities.append(make_entity("Item", 42 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # Soul of an Unknown Traveler — water chasm mid-path
    entities.append(make_entity("Item", 118 * 16, 109 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("value", "Int", 400),
        make_field("name", "String", "Soul of an Unknown Traveler")]))
    # Titanite Scale — Crystal Lizard chasm end
    entities.append(make_entity("Item", 134 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Scale")]))
    # Coiled Sword — Gundyr arena center
    entities.append(make_entity("Item", 80 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Coiled Sword")]))

    # --- Firelink Items ---
    entities.append(make_entity("Item", 74 * 16, 14 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 86 * 16, 14 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))

    # --- Fog Gate to High Wall of Lothric ---
    entities.append(make_entity("FogGate", 80 * 16, 6 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 400.0),
        make_field("dest_y", "Float", 400.0),
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
    # Firelink Shrine — warm central firelight
    entities.append(make_entity("Light", 80 * 16, 16 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.6)]))
    # Andre's forge — orange glow
    entities.append(make_entity("Light", 50 * 16, 18 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))

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

    # Player spawn at entrance from south
    spawn_px, spawn_py = 80 * 16, 116 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfire in center
    entities.append(make_entity("Bonfire", 80 * 16, 80 * 16))

    # Fire Keeper NPC (level up)
    entities.append(make_entity("Npc", 78 * 16, 74 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "LevelUp"),
        make_field("color", "Color", "#FFFFFF"),
        make_field("dialogue", "String", "Welcome to Firelink Shrine|May the flames guide your way"),
    ]))

    # Blacksmith Andre
    entities.append(make_entity("Npc", 38 * 16, 82 * 16, [
        make_field("name", "String", "Andre"),
        make_field("kind", "LocalEnum.NpcKind", "Blacksmith"),
        make_field("color", "Color", "#C0C0C0"),
        make_field("dialogue", "String", "What do you need?|I can reinforce your weapons"),
    ]))

    # Shrine Handmaiden (merchant)
    entities.append(make_entity("Npc", 82 * 16, 50 * 16, [
        make_field("name", "String", "Shrine Handmaiden"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7355"),
        make_field("dialogue", "String", "What is it? Buy something|Or be on your way"),
    ]))

    # Hawkwood (dialogue)
    entities.append(make_entity("Npc", 108 * 16, 82 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String", "Oh, another Unkindled|The Farron Keep... that is where you should go"),
    ]))

    # Items around shrine
    entities.append(make_entity("Item", 74 * 16, 76 * 16, [make_field("kind", "LocalEnum.ItemKind", "EstusShard"), make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 88 * 16, 76 * 16, [make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"), make_field("name", "String", "Titanite Shard")]))

    # Fog Gate back to CemeteryOfAsh
    entities.append(make_entity("FogGate", 80 * 16, 128 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 580.0),
        make_field("dest_y", "Float", 320.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Fog Gate to LothricWall
    entities.append(make_entity("FogGate", 80 * 16, 46 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 200.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # Lights
    entities.append(make_entity("Light", 80 * 16, 80 * 16, [make_field("radius", "Float", 240.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.7), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.6)]))
    entities.append(make_entity("Light", 36 * 16, 80 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.7), make_field("g", "Float", 0.6), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))

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
    entities.append(make_entity("Bonfire", 100 * 16, 146 * 16))  # Vordt of the Boreal Valley

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 100 * 16, 144 * 16))

    # --- Enemies ---
    enemy_positions = [
        # Wall entrance (rampart)
        ("HollowSoldier", 14, 10), ("HollowSoldier", 22, 14),
        ("HollowSoldier", 30, 18), ("HollowSoldier", 16, 20),
        # Longbow balcony
        ("HollowSoldier", 48, 10), ("HollowSoldier", 54, 14),
        # Dragon walkway
        ("StarvedHound", 16, 24), ("StarvedHound", 20, 28),
        # Dragon bridge
        ("HollowSoldier", 18, 34), ("HollowSoldier", 28, 38),
        ("HollowSoldier", 40, 32), ("HollowSoldier", 52, 36),
        # Tower area
        ("WingedKnight", 62, 42),
        ("CrystalLizard", 58, 48),
        # Residential maze (alleys between houses)
        ("Assassin", 38, 56), ("HollowSoldier", 50, 56),
        ("HollowSoldier", 62, 56), ("LothricKnight", 74, 54),
        ("Darkwraith", 38, 66), ("HollowSoldier", 50, 66),
        ("Assassin", 62, 66), ("HollowSoldier", 74, 64),
        ("HollowSoldier", 40, 74), ("HollowSoldier", 56, 74),
        # Courtyard
        ("LothricKnight", 20, 84), ("LothricKnight", 44, 96),
        ("StarvedHound", 16, 92), ("StarvedHound", 46, 88),
        ("HollowSoldier", 34, 94), ("HollowSoldier", 52, 90),
        # Knight path
        ("LothricKnight", 62, 94), ("LothricKnight", 82, 102),
        ("HollowSoldier", 70, 100), ("HollowSoldier", 86, 96),
        # Cathedral
        ("HollowSoldier", 70, 106), ("HollowSoldier", 90, 108),
        ("PusOfMan", 78, 110),
        # Frost stairs
        ("LothricKnight", 80, 118), ("HollowSoldier", 88, 126),
        ("HollowSoldier", 76, 134), ("LothricKnight", 94, 138),
    ]
    for kind, tx, ty in enemy_positions:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- NPCs ---
    # Emma — inside cathedral chapel
    entities.append(make_entity("Npc", 80 * 16, 108 * 16, [
        make_field("name", "String", "Emma"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A0D0"),
        make_field("dialogue", "String",
            "Hello, Unkindled|I am Emma, High Priestess of Lothric|Find the Prince, give him this banner"),
    ]))
    # Greirat — cell in tower area
    entities.append(make_entity("Npc", 36 * 16, 60 * 16, [
        make_field("name", "String", "Greirat"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#A0A0A0"),
        make_field("dialogue", "String",
            "...Who are you? Can you let me out?|Find the cell key and I will serve you"),
    ]))

    # --- Items ---
    items = [
        # Wall entrance
        ("SoulOrb", "Soul of a Deserted Corpse", 12, 8, 200),
        ("Firebomb", "Firebomb", 26, 16, 0),
        # Longbow balcony
        ("WeaponDrop", "Longbow", 52, 10, 0),
        ("ArrowBundle", "Standard Arrow", 50, 8, 0),
        # Dragon bridge
        ("SoulOrb", "Soul of an Unknown Traveler", 30, 36, 400),
        ("TitaniteShard", "Titanite Shard", 50, 34, 0),
        # Tower area
        ("WeaponDrop", "Deep Battle Axe", 58, 46, 0),
        ("RingDrop", "Estus Ring", 64, 44, 0),
        # Residential
        ("WeaponDrop", "Claymore", 50, 34, 0),
        ("EstusShard", "Estus Shard", 72, 58, 0),
        ("Consumable", "Homeward Bone", 44, 70, 0),
        ("TitaniteShard", "Titanite Shard", 68, 76, 0),
        # Courtyard
        ("WeaponDrop", "Astora Straight Sword", 22, 90, 0),
        ("Consumable", "Firebomb", 40, 92, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 50, 94, 200),
        # Knight path / cathedral
        ("EstusShard", "Estus Shard", 74, 100, 0),
        ("TitaniteShard", "Titanite Shard", 88, 104, 0),
        ("RingDrop", "Blue Tearstone Ring", 80, 112, 0),
        # Frost stairs
        ("Consumable", "Homeward Bone", 84, 128, 0),
        ("SoulOrb", "Soul of a Nameless Soldier", 90, 136, 800),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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

    # --- Enemies ---
    enemy_data = [
        # Entrance
        ("HollowSoldier", 22, 14), ("HollowSoldier", 26, 22),
        # House Street
        ("HollowSoldier", 34, 28), ("PeasantHollow", 42, 36),
        ("PeasantHollow", 54, 42), ("Assassin", 48, 44),
        ("StarvedHound", 30, 36), ("StarvedHound", 58, 38),
        ("Evangelist", 62, 46),
        # Giant Tower
        ("HollowSoldier", 48, 24), ("Thrall", 56, 30),
        # Bonfire Square
        ("Evangelist", 66, 52), ("Evangelist", 76, 60),
        ("Thrall", 72, 50),
        # Cliffside
        ("HollowSoldier", 90, 42), ("HollowSoldier", 96, 44),
        # Fire Demon
        ("FireDemon", 102, 62),
        # Pilgrim Camp
        ("PeasantHollow", 120, 32), ("PeasantHollow", 126, 36),
        ("PeasantHollow", 134, 40),
        # Cliff Underside
        ("HollowSoldier", 58, 82), ("HollowSoldier", 68, 86),
        # Path to pit
        ("HollowSoldier", 78, 78), ("HollowSoldier", 84, 88),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- NPCs ---
    # Siegward — at Fire Demon square
    entities.append(make_entity("Npc", 96 * 16, 60 * 16, [
        make_field("name", "String", "Siegward"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A060"),
        make_field("dialogue", "String",
            "Aah, hello again|Let us fight this demon together!"),
    ]))

    # --- Items ---
    item_data = [
        ("SoulOrb", "Soul of a Deserted Corpse", 22, 12, 200),
        ("EstusShard", "Estus Shard", 44, 40, 0),
        ("TitaniteShard", "Titanite Shard", 56, 44, 0),
        ("Consumable", "Homeward Bone", 56, 32, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 62, 38, 400),
        ("Firebomb", "Firebomb", 68, 48, 0),
        ("EstusShard", "Estus Shard", 130, 38, 0),
        ("WeaponDrop", "Mace", 146, 56, 0),
        ("RingDrop", "Lloyd's Sword Ring", 60, 88, 0),
        ("TitaniteShard", "Titanite Shard", 82, 90, 0),
    ]
    for kind, name, tx, ty, val in item_data:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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

    # Enemies - corvians in woods, lycanthropes near fortress, Black Knight in corvian forest
    enemy_data = [
        ("HollowSoldier", 25, 20), ("HollowSoldier", 35, 24),     # Entry woods
        ("StarvedHound", 42, 26), ("StarvedHound", 48, 28),       # Near fortress
        ("HollowSoldier", 56, 35), ("HollowSoldier", 62, 40),     # Woods approach
        ("DarkMage", 70, 48), ("DarkMage", 88, 55),               # Woods mages
        ("HollowSoldier", 75, 52), ("HollowSoldier", 82, 58),     # Woods hollows
        ("CrystalLizard", 50, 26),                                 # Fortress crystal lizard
        ("BlackKnight", 108, 85),                                  # Corvian forest patrol
        ("Ghru", 118, 88), ("Ghru", 122, 92), ("Ghru", 125, 96), # Corvian forest ghru
        ("DarkMage", 125, 115), ("DarkMage", 135, 118),           # Crystal cave
        ("HollowSoldier", 68, 80), ("HollowSoldier", 72, 85),     # South path
        ("StarvedHound", 110, 95), ("StarvedHound", 115, 100),    # Corvian forest
        ("Archer", 100, 78), ("Archer", 120, 82),                 # Corvian forest archers
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # Items
    item_data = [
        ("SoulOrb", "Soul of a Deserted Corpse", 22, 20, 300),
        ("TitaniteShard", "Titanite Shard", 30, 22, 0),
        ("EstusShard", "Estus Shard", 52, 32, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 60, 42, 500),
        ("WeaponDrop", "Rapier", 72, 55, 0),
        ("PurpleMoss", "Purple Moss", 75, 90, 0),
        ("Consumable", "Homeward Bone", 85, 50, 0),
        ("RingDrop", "Sage Ring", 112, 88, 0),
        ("TitaniteShard", "Titanite Shard", 95, 70, 0),
        ("SoulOrb", "Soul of a Crestfallen Knight", 130, 108, 800),
        ("WeaponDrop", "Great Scythe", 105, 98, 0),
        ("Consumable", "Firebomb", 40, 26, 0),
    ]
    for kind, name, tx, ty, val in item_data:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # NPCs - Anri and Horace at Halfway Fortress
    entities.append(make_entity("Npc", 50 * 16, 30 * 16, [make_field("name", "String", "Anri"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Hello|I am Anri of Astora|Have you seen Horace?")]))

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
    entities.append(make_entity("Bonfire", 45 * 16, 105 * 16))    # Old Wolf
    entities.append(make_entity("Bonfire", 140 * 16, 118 * 16))   # Abyss Watchers

    # Boss - Abyss Watchers
    entities.append(make_entity("BossSpawn", 140 * 16, 112 * 16))

    # Enemies - many Ghru in swamp, Darkwraiths near boss, Basilisks in cave
    enemy_data = [
        ("Ghru", 35, 45), ("Ghru", 40, 48), ("Ghru", 48, 50),       # Left torch area
        ("Ghru", 68, 48), ("Ghru", 72, 52), ("Ghru", 75, 55),       # Center torch area
        ("Ghru", 95, 42), ("Ghru", 100, 45),                        # Right torch area
        ("Ghru", 65, 72), ("Ghru", 72, 76), ("Ghru", 78, 70),      # Keep Ruins
        ("Darkwraith", 100, 88), ("Darkwraith", 108, 95),           # Darkwraith patrol
        ("Basilisk", 24, 70), ("Basilisk", 30, 75), ("Basilisk", 32, 68),  # Curse cave
        ("Ghru", 50, 85), ("Ghru", 55, 90),                         # South swamp
        ("StarvedHound", 42, 55), ("StarvedHound", 62, 58),         # Swamp hounds
        ("CrystalLizard", 85, 82),                                   # Near gate
        ("Ghru", 115, 95), ("Ghru", 120, 100),                      # Gate approach
        ("Darkwraith", 125, 108),                                    # Near arena
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # Items
    item_data = [
        ("SoulOrb", "Soul of a Deserted Corpse", 18, 22, 500),
        ("PurpleMoss", "Purple Moss Clump", 38, 50, 0),
        ("EstusShard", "Estus Shard", 72, 70, 0),
        ("TitaniteShard", "Titanite Shard", 45, 108, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 65, 65, 800),
        ("Consumable", "Homeward Bone", 100, 40, 0),
        ("RingDrop", "Lingering Dragoncrest Ring", 28, 74, 0),
        ("WeaponDrop", "Greatsword", 92, 44, 0),
    ]
    for kind, name, tx, ty, val in item_data:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # NPC - Old Wolf of Farron
    entities.append(make_entity("Npc", 45 * 16, 103 * 16, [make_field("name", "String", "Old Wolf of Farron"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#8899AA"), make_field("dialogue", "String", "(The wolf gazes silently|Its eyes reflect distant flames)")]))

    # Fog Gate to CatacombsOfCarthus
    entities.append(make_entity("FogGate", 140 * 16, 130 * 16, [
        make_field("dest_area", "String", "CatacombsOfCarthus"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

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
    # SECTION 8: Siegward's well - doc: x=1400,y=1300,w=200,h=200
    # Small well area where Siegward is trapped
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

    # Bonfires
    entities.append(make_entity("Bonfire", 30 * 16, 8 * 16))       # Cemetery entry
    entities.append(make_entity("Bonfire", 32 * 16, 44 * 16))      # Cleansing Chapel
    entities.append(make_entity("Bonfire", 52 * 16, 75 * 16))      # Cathedral nave
    entities.append(make_entity("Bonfire", 38 * 16, 150 * 16))     # Rosaria's

    # Boss - Deacons of the Deep
    entities.append(make_entity("BossSpawn", 45 * 16, 114 * 16))

    # Enemies
    enemy_data = [
        ("PeasantHollow", 28, 6), ("PeasantHollow", 34, 8),        # Cemetery
        ("StarvedHound", 25, 10), ("StarvedHound", 35, 12),        # Cemetery dogs
        ("CathedralKnight", 40, 16), ("CathedralKnight", 45, 20),  # Outer graveyard
        ("InfestedCorpse", 30, 28), ("InfestedCorpse", 36, 30),    # Graveyard corpses
        ("Evangelist", 34, 42),                                    # Cleansing Chapel
        ("Thrall", 60, 60), ("Thrall", 64, 65), ("Thrall", 68, 62),# Side aisle
        ("HollowSoldier", 48, 54), ("HollowSoldier", 52, 56),      # Gate area
        ("CathedralKnight", 50, 70), ("CathedralKnight", 55, 72),  # Nave knights
        ("Evangelist", 66, 64), ("Evangelist", 72, 68),            # Upper gallery
        ("HollowSoldier", 70, 62),                                 # Gallery
        ("GiantSlave", 44, 92), ("GiantSlave", 56, 98),            # Giant room
        ("CathedralKnight", 48, 88), ("CathedralKnight", 52, 96),  # Giant room guards
        ("Evangelist", 40, 96),                                    # Giant room
        ("Thrall", 46, 100), ("Thrall", 54, 102),                  # Giant room thralls
        ("Deacon", 38, 110), ("Deacon", 42, 108), ("Deacon", 48, 112),  # Deacon hall
        ("Deacon", 52, 116), ("Deacon", 56, 114), ("Deacon", 40, 118),  # More deacons
        ("Deacon", 45, 122), ("Deacon", 50, 124),                  # More deacons
        ("Deacon", 55, 120), ("Deacon", 35, 124),                  # More deacons
        ("CathedralKnight", 60, 110),                               # Deacon hall guard
        ("ManGrub", 34, 135), ("ManGrub", 38, 138),                # Slug corridor
        ("ManGrub", 42, 140), ("ManGrub", 36, 142),                # More slugs
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    # Items
    items = [
        ("SoulOrb", "Soul of a Deserted Corpse", 28, 6, 200),
        ("EstusShard", "Estus Shard", 40, 22, 0),
        ("TitaniteShard", "Titanite Shard", 28, 26, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 45, 32, 500),
        ("Consumable", "Homeward Bone", 62, 58, 0),
        ("SoulOrb", "Soul of a Nameless Warrior", 50, 68, 300),
        ("TitaniteShard", "Titanite Shard", 66, 66, 0),
        ("Ember", "Ember", 44, 94, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 52, 76, 1000),
        ("SoulOrb", "Soul of a Crestfallen Knight", 48, 96, 1000),
        ("Consumable", "Titanite Shard", 42, 120, 0),
        ("EstusShard", "Estus Shard", 72, 66, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # NPCs
    entities.append(make_entity("Npc", 60 * 16, 85 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D4A840"), make_field("dialogue", "String", "Aah, you found me|I seem to have gotten myself stuck")]))
    entities.append(make_entity("Npc", 52 * 16, 78 * 16, [make_field("name", "String", "Patches"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#808080"), make_field("dialogue", "String", "What's the matter?|You fell for it!")]))
    entities.append(make_entity("Npc", 38 * 16, 148 * 16, [make_field("name", "String", "Rosaria"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D0A0B0"), make_field("dialogue", "String", "Welcome|I am Rosaria, Mother of Rebirth")]))

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

    # Enemies
    enemy_data = [
        ("Skeleton", 18, 18), ("Skeleton", 22, 22),                # Entry
        ("Skeleton", 25, 28), ("Skeleton", 35, 30), ("Skeleton", 42, 26),  # Ball corridor
        ("Skeleton", 48, 32), ("Skeleton", 52, 34),                # Ball corridor end
        ("Skeleton", 60, 30),                                       # Bridge area
        ("Skeleton", 20, 48), ("Skeleton", 28, 52),                # Lower tombs
        ("Skeleton", 35, 56), ("Skeleton", 40, 60), ("Skeleton", 45, 65),  # Tombs deep
        ("CathedralGraveWarden", 32, 58), ("CathedralGraveWarden", 38, 62),  # Grave wardens
        ("CrystalLizard", 48, 50),                                  # Crystal lizard
        ("Rat", 20, 78), ("Rat", 25, 82), ("Rat", 30, 88),       # Abandoned tomb rats
        ("FireDemon", 35, 98),                                      # Fire Demon
        ("Skeleton", 55, 62), ("Skeleton", 60, 68),                # Wheel area
        ("Skeleton", 65, 72),                                       # Wheel area
        ("Skeleton", 80, 60), ("Skeleton", 90, 70),                # Wolnir path
        ("Skeleton", 110, 85), ("Skeleton", 115, 90), ("Skeleton", 120, 95),  # Arena approach
        ("Skeleton", 130, 92), ("Skeleton", 135, 98),              # Arena
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    items = [("SoulOrb", "Soul of a Deserted Corpse", 18, 16, 500),
             ("TitaniteShard", "Titanite Shard", 40, 28, 0),
             ("SoulOrb", "Soul of an Unknown Traveler", 32, 55, 800),
             ("Consumable", "Homeward Bone", 65, 28, 0),
             ("RingDrop", "Carthus Milkring", 28, 62, 0),
             ("EstusShard", "Estus Shard", 25, 82, 0),
             ("SoulOrb", "Soul of a Crestfallen Knight", 85, 65, 1200),
             ("TitaniteShard", "Titanite Shard", 50, 65, 0)]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # NPC - Anri in the catacombs
    entities.append(make_entity("Npc", 50 * 16, 45 * 16, [make_field("name", "String", "Anri"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "We meet again|Have you seen Horace?")]))

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

    # Enemies
    enemy_data = [
        ("FireDemon", 58, 55),                                     # Demon ruins
        ("DemonStatue", 28, 42), ("DemonStatue", 50, 60), ("DemonStatue", 65, 50),  # Lake shore
        ("Basilisk", 52, 65), ("Basilisk", 58, 70), ("Basilisk", 55, 72),  # Near lava
        ("BlackKnight", 78, 58), ("BlackKnight", 108, 68),        # Demon ruins
        ("FireDemon", 95, 70), ("FireDemon", 100, 75),            # Cleric corridors
        ("HollowSoldier", 18, 32), ("HollowSoldier", 35, 40),     # Lake shore
        ("Dog", 15, 85), ("Dog", 20, 90), ("Dog", 25, 95),       # Ballista area
        ("StarvedHound", 40, 58), ("StarvedHound", 48, 64),      # Lake mid
        ("CrystalLizard", 82, 55),                                 # Crystal lizard
        ("Ghru", 62, 58), ("Ghru", 68, 62), ("Ghru", 72, 55),    # Demon ruins
        ("HollowSoldier", 112, 82), ("HollowSoldier", 118, 88),   # Arena approach
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    items = [("SoulOrb", "Soul of a Deserted Corpse", 18, 20, 500),
             ("TitaniteShard", "Titanite Shard", 60, 50, 0),
             ("SoulOrb", "Soul of an Unknown Traveler", 72, 55, 800),
             ("EstusShard", "Estus Shard", 22, 88, 0),
             ("Consumable", "Homeward Bone", 100, 70, 0),
             ("RingDrop", "Speckled Stoneplate Ring", 42, 55, 0),
             ("SoulOrb", "Soul of a Crestfallen Knight", 125, 92, 1000),
             ("TitaniteShard", "Titanite Shard", 90, 65, 0)]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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

    # Bonfires
    entities.append(make_entity("Bonfire", 10 * 16, 35 * 16))      # Entry bridge
    entities.append(make_entity("Bonfire", 62 * 16, 40 * 16))      # Church of Yorshka
    entities.append(make_entity("Bonfire", 30 * 16, 78 * 16))      # Distant Manor
    entities.append(make_entity("Bonfire", 120 * 16, 82 * 16))     # Pontiff Sulyvahn

    # Boss - Pontiff Sulyvahn
    entities.append(make_entity("BossSpawn", 120 * 16, 76 * 16))

    # Enemies
    enemy_data = [
        ("SilverKnight", 38, 50), ("SilverKnight", 55, 55),       # Boulevard
        ("SilverKnight", 75, 60), ("SilverKnight", 90, 58),       # Boulevard
        ("HollowSoldier", 15, 40), ("HollowSoldier", 22, 45),     # Bridge
        ("Evangelist", 42, 52), ("Evangelist", 95, 62),           # Near church
        ("StarvedHound", 50, 48), ("StarvedHound", 80, 55),       # City dogs
        ("CrystalLizard", 65, 42), ("CrystalLizard", 128, 75),    # Crystal lizards
        ("Darkwraith", 32, 72), ("Darkwraith", 40, 82),           # Manor area
        ("ManGrub", 68, 80), ("ManGrub", 78, 85), ("ManGrub", 88, 90),  # Sewers
        ("SilverKnight", 30, 100), ("SilverKnight", 42, 110),     # Silver Knight hall
        ("SilverKnight", 48, 118),                                 # Silver Knight hall
        ("Deacon", 35, 108), ("Deacon", 45, 115),                 # Near knights
        ("DeepAccursed", 132, 88),                                 # Arena entrance
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    items = [("SoulOrb", "Soul of a Deserted Corpse", 12, 38, 600),
             ("SoulOrb", "Soul of an Unknown Traveler", 62, 42, 800),
             ("TitaniteShard", "Titanite Shard", 35, 80, 0),
             ("EstusShard", "Estus Shard", 95, 60, 0),
             ("Consumable", "Homeward Bone", 120, 78, 0),
             ("RingDrop", "Pontiff's Right Eye", 14, 36, 0)]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    entities.append(make_entity("Npc", 62 * 16, 38 * 16, [make_field("name", "String", "Anri"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Hello|Have you seen Horace?")]))

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

    # Bonfires
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))     # Entry
    entities.append(make_entity("Bonfire", 135 * 16, 32 * 16))    # Exit

    # Enemies - many jailers, rats, basilisks
    enemy_data = [
        ("Jailer", 22, 20), ("Jailer", 35, 30), ("Jailer", 48, 38),   # Upper block
        ("Jailer", 55, 55), ("Jailer", 60, 60), ("Jailer", 68, 52),   # Central block
        ("Jailer", 88, 55),                                          # Siegward area
        ("Rat", 28, 78), ("Rat", 35, 82), ("Rat", 42, 88),         # Lower drains
        ("Basilisk", 55, 80), ("Basilisk", 62, 85),                 # Lower drains
        ("Gargoyle", 95, 42),                                        # Tower
        ("Wretch", 78, 60), ("Wretch", 82, 65),                     # Near Siegward
        ("HollowSoldier", 25, 25), ("HollowSoldier", 32, 32),       # Entry
        ("CrystalLizard", 52, 52),                                   # Central block
        ("PeasantHollow", 20, 28), ("PeasantHollow", 28, 35),       # Entry area
        ("Jailer", 85, 85), ("Jailer", 95, 90),                     # Karla area
        ("Gargoyle", 125, 30),                                       # Exit corridor
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    items = [("SoulOrb", "Soul of a Deserted Corpse", 20, 20, 400),
             ("TitaniteShard", "Titanite Shard", 52, 56, 0),
             ("SoulOrb", "Soul of an Unknown Traveler", 92, 60, 600),
             ("EstusShard", "Estus Shard", 90, 85, 0),
             ("Consumable", "Homeward Bone", 135, 30, 0),
             ("Consumable", "Purple Moss", 40, 82, 0)]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    entities.append(make_entity("Npc", 92 * 16, 56 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D4A520"), make_field("dialogue", "String", "Mmm|You have my thanks")]))
    entities.append(make_entity("Npc", 90 * 16, 84 * 16, [make_field("name", "String", "Karla"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#4A0080"), make_field("dialogue", "String", "What do you want?|I can teach you pyromancies")]))

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
    enemy_positions = [
        # Entry bridge gargoyle ambush
        ("Gargoyle", 8, 10),
        # Boss path bridge
        ("Gargoyle", 44, 12),
        # First jailer room
        ("Jailer", 52, 10), ("Jailer", 54, 14), ("Jailer", 60, 8), ("Jailer", 62, 18),
        ("Gargoyle", 64, 14),
        # Second jailer room
        ("Jailer", 72, 10), ("Jailer", 74, 16), ("Jailer", 80, 12), ("Jailer", 82, 20),
        ("Gargoyle", 88, 8),
        # Upper ruins
        ("HollowSoldier", 20, 38), ("HollowSoldier", 30, 42),
        ("Jailer", 38, 44), ("Jailer", 42, 46),
        # Ruins / streets
        ("Gargoyle", 34, 52), ("Gargoyle", 50, 60),
        ("HollowSoldier", 26, 56), ("HollowSoldier", 46, 62),
        # Toxic pool
        ("Rat", 52, 64), ("Rat", 60, 72), ("Rat", 66, 68),
        ("CrystalLizard", 56, 68), ("CrystalLizard", 62, 64),
        # Church (Monstrosities of Sin)
        ("ManGrub", 30, 72), ("ManGrub", 36, 78), ("ManGrub", 42, 74),
        # Court sorcerer roof
        ("DarkMage", 48, 42),
        ("CrystalLizard", 56, 44),
        # Siegward cell area
        ("Jailer", 62, 48),
        # Giant room
        ("Rat", 70, 60), ("Rat", 74, 66), ("Rat", 80, 62), ("Rat", 78, 68),
        ("GiantSlave", 76, 60),
        # Mimic in second jailer room
        ("Mimic", 86, 16),
        # Mimic near giant room
        ("Mimic", 72, 70),
    ]
    for kind, tx, ty in enemy_positions:
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

    # --- Items ---
    items = [
        # Bonfire area (Gilligan)
        ("Consumable", "Undead Bone Shard", 14, 10, 0),
        # Boss path bridge
        ("SoulOrb", "Large Soul of a Weary Warrior", 48, 14, 1000),
        ("Consumable", "Onislayer Greatarrow", 36, 12, 0),
        # First jailer room
        ("Consumable", "Rusted Coin", 62, 20, 0),
        # Second jailer room
        ("Consumable", "Rusted Coin", 90, 22, 0),
        ("Consumable", "Ember", 88, 20, 0),
        # Upper ruins
        ("Consumable", "Rusted Coin", 24, 40, 0),
        ("Consumable", "Rusted Gold Coin", 40, 44, 0),
        # Toxic pool
        ("Consumable", "Poison Gem", 54, 72, 0),
        ("RingDrop", "Cursebite Ring", 64, 76, 0),
        ("Consumable", "Purging Stone", 50, 70, 0),
        ("Consumable", "Shriving Stone", 68, 74, 0),
        # Church
        ("WeaponDrop", "Eleonora", 36, 76, 0),
        ("Consumable", "Purging Stone", 32, 80, 0),
        # Court sorcerer roof
        ("ArmorDrop", "Court Sorcerer Set", 48, 46, 0),
        ("WeaponDrop", "Court Sorcerer's Staff", 58, 46, 0),
        ("Consumable", "Logan's Scroll", 52, 40, 0),
        # Siegward's cell
        ("RingDrop", "Covetous Gold Serpent Ring", 64, 52, 0),
        ("Consumable", "Wrath of the Gods", 56, 48, 0),
        # Giant room
        ("Consumable", "Profaned Flame", 78, 62, 0),
        ("TitaniteShard", "Large Titanite Shard", 82, 64, 0),
        ("Consumable", "Titanite Chunk", 84, 60, 0),
        # Yhorm arena
        ("WeaponDrop", "Storm Ruler", 108, 16, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 10 * 16, 38 * 16))
    entities.append(make_entity("Bonfire", 62 * 16, 90 * 16))   # Prison Tower (hidden)
    entities.append(make_entity("Bonfire", 128 * 16, 85 * 16))  # Aldrich boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 128 * 16, 78 * 16))

    # --- Enemies ---
    enemy_data = [
        # Cathedral entrance
        ("SilverKnight", 20, 35), ("SilverKnight", 34, 42),
        # Royal avenue
        ("SilverKnight", 42, 38), ("SilverKnight", 55, 45),
        ("SilverKnight", 68, 40), ("Deacon", 45, 48), ("Deacon", 58, 50), ("Deacon", 70, 46),
        ("GiantSlave", 38, 52),
        # Silver Knight hall — Deep Accursed lair
        ("SilverKnight", 85, 35), ("SilverKnight", 98, 44),
        ("SilverKnight", 110, 42), ("DeepAccursed", 100, 40),
        # Staircase corridor — gauntlet
        ("SilverKnight", 125, 38), ("SilverKnight", 135, 44),
        ("SilverKnight", 138, 50),
        # Around arena
        ("SilverKnight", 115, 62),
        ("ManGrub", 142, 75), ("ManGrub", 148, 82),
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    # --- Items ---
    items = [
        ("SoulOrb", "Soul of a Deserted Corpse", 18, 36, 500),
        ("SoulOrb", "Soul of an Unknown Traveler", 52, 44, 700),
        ("HomewardBone", "Homeward Bone", 72, 46, 0),
        ("TitaniteShard", "Titanite Shard", 92, 42, 0),
        ("TitaniteShard", "Titanite Shard", 108, 40, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 130, 42, 800),
        ("EstusShard", "Estus Shard", 135, 52, 0),
        ("RingDrop", "Aldrich's Ruby", 100, 42, 0),
        ("TwinklingTitanite", "Twinkling Titanite", 60, 88, 0),
        ("RingDrop", "Sun Princess Ring", 130, 90, 0),
        ("WeaponDrop", "Crescent Moon Sword", 138, 85, 0),
        ("SoulOrb", "Soul of a Crestfallen Knight", 115, 60, 1000),
        ("Consumable", "Proof of a Concord Kept", 96, 48, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- Chests ---
    entities.append(make_entity("Chest", 125 * 16, 55 * 16, [
        make_field("loot_kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("is_mimic", "Bool", False),
    ]))

    # --- NPCs ---
    entities.append(make_entity("Npc", 62 * 16, 92 * 16, [
        make_field("name", "String", "Company Captain Yorshka"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#a0c0ff"),
        make_field("dialogue", "String",
            "I am Yorshka, Captain of the Darkmoon Knights.|"
            "This duty was given to me by my elder brother Gwyndolin.|"
            "But he has been devoured by that monster.|"
            "If you would serve the Darkmoon, swear the oath here."),
    ]))
    entities.append(make_entity("Npc", 128 * 16, 72 * 16, [
        make_field("name", "String", "Sirris of the Sunless Realms"),
        make_field("kind", "LocalEnum.NpcKind", "Summon"),
        make_field("color", "Color", "#d0d0ff"),
        make_field("dialogue", "String",
            "I can sense your kindness.|Please let me help you.|"
            "Together we shall defeat the Devourer of Gods."),
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

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 10 * 16, 30 * 16))    # Castle gate
    entities.append(make_entity("Bonfire", 42 * 16, 35 * 16))    # Corridor
    entities.append(make_entity("Bonfire", 80 * 16, 25 * 16))    # Dragon barracks
    entities.append(make_entity("Bonfire", 132 * 16, 68 * 16))   # Boss room

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 132 * 16, 62 * 16))  # Dragonslayer Armour

    # --- Enemies ---
    enemy_positions = [
        # Castle gate area
        ("LothricKnight", 18, 28),
        # Outer corridor
        ("LothricKnight", 35, 32),
        ("HollowAssassin", 32, 38),
        # Corridor -> barracks transition
        ("LothricKnight", 55, 38),
        ("WingedKnight", 50, 38),
        # Dragon barracks
        ("HollowSoldier", 68, 18),
        ("PusOfMan", 78, 18),
        ("HollowSoldier", 75, 22),
        ("CrystalLizard", 82, 22),
        ("HollowSoldier", 85, 28),
        # Inner stairs
        ("WingedKnight", 108, 48),
        ("CrystalLizard", 115, 45),
        # Arena approaches
        ("PusOfMan", 125, 55),
        ("LothricKnight", 132, 58),
    ]
    for kind, tx, ty in enemy_positions:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # --- Items ---
    items = [
        ("SoulOrb", "Soul of a Crestfallen Knight", 25, 25, 600),
        ("EstusShard", "Estus Shard", 55, 36, 0),
        ("TitaniteShard", "Titanite Shard", 80, 26, 0),
        ("SoulOrb", "Soul of a Nameless Soldier", 122, 52, 1000),
        ("RingDrop", "Red Tearstone Ring", 132, 75, 0),
        ("Consumable", "Homeward Bone", 48, 45, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- NPC ---
    # Emma — speaks of the princes and the fire linking
    entities.append(make_entity("Npc", 12 * 16, 28 * 16, [
        make_field("name", "String", "Emma"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0C0E0"),
        make_field("dialogue", "String",
            "The prince loathes his fire-linking destiny|"
            "but it falls to you to rouse him|"
            "however reluctant he may be"),
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

    # ================================================================
    # CONNECTIONS — vertical staircases between levels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 38, 120, 48, 130)    # Entry hall → First floor
    fill_tiles(chunk, TILE_GROUND, 55, 82, 65, 88)      # First floor → Wax pool
    fill_tiles(chunk, TILE_GROUND, 72, 52, 82, 58)      # Wax pool → Scholar tower
    fill_tiles(chunk, TILE_GROUND, 85, 30, 95, 35)      # Scholar tower → WK corridor
    fill_tiles(chunk, TILE_GROUND, 75, 15, 85, 22)      # WK corridor → Rooftop
    fill_tiles(chunk, TILE_GROUND, 98, 10, 105, 18)     # Rooftop → Princes chamber

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
    # ENEMIES
    # ================================================================
    enemy_data = [
        # Dark Mages — scholars of the archives
        ("DarkMage", 45, 130),
        ("DarkMage", 62, 95),
        ("DarkMage", 85, 40),
        ("DarkMage", 75, 28),
        # Hollow Soldiers — fallen scholars
        ("HollowSoldier", 35, 135),
        ("HollowSoldier", 50, 100),
        ("HollowSoldier", 55, 65),
        # Lothric Knights — garrison patrols
        ("LothricKnight", 70, 92),
        ("LothricKnight", 88, 45),
        # Gargoyles — rooftop guardians
        ("Gargoyle", 68, 12),
        ("Gargoyle", 82, 15),
        ("Gargoyle", 95, 10),
        # Man Grubs — transformed scholars
        ("ManGrub", 92, 48),
        ("ManGrub", 98, 52),
        # Crystal Lizards — rare spawns
        ("CrystalLizard", 52, 85),
        ("CrystalLizard", 78, 15),
        # Cathedral Knights — heavy guards
        ("CathedralKnight", 65, 38),
        ("CathedralKnight", 90, 28),
        # Deacons — cultists near entry
        ("Deacon", 32, 142),
        ("Deacon", 42, 145),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))

    # ================================================================
    # ITEMS
    # ================================================================
    items = [
        ("SoulOrb", "Soul of a Crestfallen Knight", 32, 138, 600),
        ("EstusShard", "Estus Shard", 68, 102, 0),
        ("TitaniteShard", "Titanite Shard", 85, 42, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 72, 15, 1000),
        ("RingDrop", "Fleshbite Ring", 90, 22, 0),
        ("Consumable", "Homeward Bone", 60, 108, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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
    items = [
        ("SoulOrb", "Soul of the Flame", 80, 38, 5000),
    ]
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
    entities.append(make_entity("Bonfire", 15 * 16, 15 * 16))    # Entry
    entities.append(make_entity("Bonfire", 120 * 16, 95 * 16))   # Oceiros boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 120 * 16, 88 * 16))  # Oceiros

    # --- Enemies ---
    enemy_data = [
        ("CathedralKnight", 32, 30), ("CathedralKnight", 55, 40),
        ("SerpentMan", 42, 38), ("SerpentMan", 80, 55),
        ("HollowSoldier", 35, 35),
        ("PusOfMan", 52, 42),
        ("Dog", 45, 70), ("Dog", 50, 75), ("Dog", 55, 78),
        ("WingedKnight", 98, 68),
        ("HollowSoldier", 88, 62),
        ("CathedralKnight", 112, 82),
        ("SerpentMan", 128, 90),
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    # --- Items ---
    items = [
        ("SoulOrb", "Soul of a Deserted Corpse", 20, 18, 400),
        ("TitaniteShard", "Titanite Shard", 48, 40, 0),
        ("EstusShard", "Estus Shard", 50, 72, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 100, 70, 800),
        ("RingDrop", "Dragonscale Ring", 120, 98, 0),
        ("Consumable", "Path of the Dragon", 65, 52, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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

    # --- Enemies ---
    enemy_data = [
        ("BlackKnight", 30, 28), ("BlackKnight", 45, 35),
        ("BlackKnight", 62, 45), ("BlackKnight", 75, 50),
        ("BlackKnight", 55, 60), ("BlackKnight", 88, 58),
        ("BlackKnight", 95, 68),
        ("CrystalLizard", 40, 32),
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    # --- Items ---
    items = [
        ("SoulOrb", "Soul of a Crestfallen Knight", 25, 25, 1000),
        ("Consumable", "Fire Keeper's Eyes", 132, 115, 0),
        ("TitaniteShard", "Titanite Shard", 50, 40, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

    # --- NPCs ---
    entities.append(make_entity("Npc", 132 * 16, 112 * 16, [
        make_field("name", "String", "Shrine Handmaid"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#606060"),
        make_field("dialogue", "String",
            "What is it?|The fire has long been out"),
    ]))

    # --- Fog Gate ---
    # To Cemetery of Ash (SE)
    entities.append(make_entity("FogGate", 148 * 16, 115 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 288.0),
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
    entities.append(make_entity("Bonfire", 18 * 16, 132 * 16))    # Entry
    entities.append(make_entity("Bonfire", 48 * 16, 100 * 16))    # Barracks
    entities.append(make_entity("Bonfire", 122 * 16, 22 * 16))    # Belfry
    entities.append(make_entity("Bonfire", 128 * 16, 92 * 16))    # Nameless King

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 128 * 16, 85 * 16))  # Nameless King

    # --- Enemies ---
    enemy_data = [
        ("SerpentMan", 22, 115), ("SerpentMan", 38, 98), ("SerpentMan", 45, 108),
        ("SerpentMan", 55, 75), ("SerpentMan", 68, 58), ("SerpentMan", 80, 48),
        ("SerpentMan", 95, 35), ("SerpentMan", 108, 28), ("SerpentMan", 118, 25),
        ("Dog", 22, 128), ("Dog", 32, 130),
        ("StarvedHound", 50, 72), ("StarvedHound", 62, 76),
        ("CrystalLizard", 35, 110), ("CrystalLizard", 118, 20),
        ("DarkMage", 110, 30), ("DarkMage", 135, 28),
        ("BlackKnight", 120, 75), ("BlackKnight", 142, 88),
        ("Gargoyle", 112, 68), ("Gargoyle", 148, 95),
    ]
    for kind, tx, ty in enemy_data:
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", kind)]))

    # --- Items ---
    items = [
        ("SoulOrb", "Soul of a Deserted Corpse", 22, 135, 400),
        ("TitaniteShard", "Titanite Shard", 55, 68, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 122, 25, 1000),
        ("EstusShard", "Estus Shard", 128, 95, 0),
        ("RingDrop", "Lightning Clutch Ring", 50, 62, 0),
        ("Consumable", "Homeward Bone", 118, 30, 0),
        ("TwinklingTitanite", "Twinkling Titanite", 82, 45, 0),
        ("TitaniteShard", "Titanite Shard", 100, 40, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))

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

    map_id = doc["id"]
    if map_id not in LEVEL_UIDS:
        # Try alternate IDs
        alt = {"IrithyllOfTheBorealValley": "Irithyll"}.get(map_id)
        if alt and alt in LEVEL_UIDS:
            map_id = alt
        else:
            print(f"  SKIP {map_id} (not in LEVEL_UIDS)")
            return None

    src_w = doc["map_size"]["width"]
    src_h = doc["map_size"]["height"]
    chunk = new_chunk()

    # --- Terrain from sections ---
    sections = doc.get("map_layout", {}).get("sections", [])
    for s in sections:
        x1, y1 = scale_tile(s["x"], s["y"], src_w, src_h)
        x2, y2 = scale_tile(s["x"] + s["w"], s["y"] + s["h"], src_w, src_h)
        fill_tiles(chunk, TILE_GROUND, x1, y1, x2, y2)

    # Connect consecutive sections with corridors
    for i in range(len(sections) - 1):
        s1, s2 = sections[i], sections[i + 1]
        cx1, cy1 = scale_tile(s1["x"] + s1["w"] // 2, s1["y"] + s1["h"] // 2, src_w, src_h)
        cx2, cy2 = scale_tile(s2["x"] + s2["w"] // 2, s2["y"] + s2["h"] // 2, src_w, src_h)
        carve_corridor(chunk, cx1, cy1, cx2, cy2, width=3)

    # Add some wall decorations (pillars, protrusions) for visual interest
    for s in sections:
        sx1, sy1 = scale_tile(s["x"], s["y"], src_w, src_h)
        sx2, sy2 = scale_tile(s["x"] + s["w"], s["y"] + s["h"], src_w, src_h)
        w = sx2 - sx1
        h = sy2 - sy1
        # Add 1-2 pillar decorations in larger rooms
        if w > 10 and h > 10:
            mid_x = (sx1 + sx2) // 2
            mid_y = (sy1 + sy2) // 2
            fill_tiles(chunk, TILE_WALL, mid_x - 1, mid_y - 1, mid_x + 1, mid_y + 1)

    # --- Entities ---
    entities = []
    entity_px_positions = []  # for connectivity check

    # Bonfires / PlayerSpawn
    bonfires = doc.get("bonfires", [])
    if bonfires:
        b = bonfires[0]
        px, py = scale_px(b["x"], b["y"], src_w, src_h)
        entities.append(make_entity("PlayerSpawn", px, py, [make_field("heal", "Bool", True)]))
        entities.append(make_entity("Bonfire", px, py))
        entity_px_positions.append((px, py))
        for b in bonfires[1:]:
            bx, by = scale_px(b["x"], b["y"], src_w, src_h)
            entities.append(make_entity("Bonfire", bx, by))
            entity_px_positions.append((bx, by))
    else:
        px, py = MARGIN * TILE_SIZE + TILE_SIZE, MARGIN * TILE_SIZE + TILE_SIZE
        entities.append(make_entity("PlayerSpawn", px, py, [make_field("heal", "Bool", True)]))
        entity_px_positions.append((px, py))

    spawn_px, spawn_py = entity_px_positions[0] if entity_px_positions else (256, 256)

    # Boss
    boss = doc.get("boss")
    if boss:
        if isinstance(boss, list):
            boss = boss[0]
        bx, by = scale_px(boss["x"], boss["y"], src_w, src_h)
        entities.append(make_entity("BossSpawn", bx, by))
        entity_px_positions.append((bx, by))

    # Enemies
    for e in doc.get("enemies", []):
        ex, ey = scale_px(e["x"], e["y"], src_w, src_h)
        kind = ENEMY_KIND_MAP.get(e["kind"], e["kind"])
        entities.append(make_entity("Enemy", ex, ey, [
            make_field("kind", "LocalEnum.EnemyKind", kind)
        ]))
        entity_px_positions.append((ex, ey))
        # Place multiple enemies if count > 1
        for j in range(1, e.get("count", 1)):
            offset = j * 32
            ex2, ey2 = ex + offset, ey
            entities.append(make_entity("Enemy", ex2, ey2, [
                make_field("kind", "LocalEnum.EnemyKind", kind)
            ]))
            entity_px_positions.append((ex2, ey2))

    # Items
    for it in doc.get("items", []):
        ix, iy = scale_px(it["x"], it["y"], src_w, src_h)
        kind = map_item_kind(it)
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb" and "value" in it:
            fields.append(make_field("value", "Int", it["value"]))
        if it.get("name_en"):
            fields.append(make_field("name", "String", it["name_en"]))
        elif it.get("name"):
            fields.append(make_field("name", "String", it["name"]))
        entities.append(make_entity("Item", ix, iy, fields))
        entity_px_positions.append((ix, iy))
        for j in range(1, it.get("count", 1)):
            ix2 = ix + j * 20
            entities.append(make_entity("Item", ix2, iy, list(fields)))
            entity_px_positions.append((ix2, iy))

    # Chests
    for c in doc.get("chests", []):
        cx, cy = scale_px(c["x"], c["y"], src_w, src_h)
        loot = c.get("loot", {})
        entities.append(make_entity("Chest", cx, cy, [
            make_field("loot_kind", "LocalEnum.ItemKind", map_chest_kind(loot)),
            make_field("loot_value", "Int", loot.get("value", 0)),
            make_field("loot_name", "String", loot.get("name_en", loot.get("name", ""))),
            make_field("is_mimic", "Bool", c.get("is_mimic", False)),
        ]))
        entity_px_positions.append((cx, cy))

    # NPCs
    for n in doc.get("npcs", []):
        if "x" not in n or "y" not in n:
            continue  # skip NPCs without positions (summons, etc.)
        nx, ny = scale_px(n["x"], n["y"], src_w, src_h)
        dialogue = "|".join(n.get("dialogue", []))
        entities.append(make_entity("Npc", nx, ny, [
            make_field("name", "String", n.get("name_en", n.get("name", ""))),
            make_field("kind", "LocalEnum.NpcKind", map_npc_kind(n)),
            make_field("color", "Color", n.get("color", "#FFFFFF")),
            make_field("dialogue", "String", dialogue),
        ]))
        entity_px_positions.append((nx, ny))

    # Lights
    for l in doc.get("lights", []):
        lx, ly = scale_px(l["x"], l["y"], src_w, src_h)
        entities.append(make_entity("Light", lx, ly, [
            make_field("radius", "Float", l.get("radius", 160)),
            make_field("r", "Float", l.get("r", 1.0)),
            make_field("g", "Float", l.get("g", 1.0)),
            make_field("b", "Float", l.get("b", 1.0)),
            make_field("intensity", "Float", l.get("intensity", 0.2)),
        ]))

    # Fog Gates
    AREA_ALIASES = {
        "FirelinkShrine": "CemeteryOfAsh",
        "IrithyllOfTheBorealValley": "Irithyll",
    }
    VALID_AREAS = set(LEVEL_UIDS.keys())
    for fg in doc.get("fog_gates", []):
        fx, fy = scale_px(fg["x"], fg["y"], src_w, src_h)
        fw = max(TILE_SIZE, scale_px_dim(fg.get("w", 40), src_w, src_h))
        fh = max(TILE_SIZE, scale_px_dim(fg.get("h", 40), src_h, src_w))
        dest_area = fg.get("dest_area", "")
        dest_area = AREA_ALIASES.get(dest_area, dest_area)
        if dest_area in ("", "None", None) or dest_area not in VALID_AREAS:
            continue  # skip invalid fog gates
        entities.append(make_entity("FogGate", fx, fy, [
            make_field("dest_area", "String", dest_area),
            make_field("dest_x", "Float", fg.get("dest_x", 0)),
            make_field("dest_y", "Float", fg.get("dest_y", 0)),
            make_field("width", "Float", fw),
            make_field("height", "Float", fh),
        ]))

    # --- Connectivity ---
    populate_entity_def_uids(entities)
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_px_positions)

    # Count ground tiles
    ground_count = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    total = CHUNK_SIZE * CHUNK_SIZE
    pct = ground_count / total * 100

    print(f"  {map_id:30s} sections={len(sections):2d} entities={len(entities):4d} ground={pct:5.1f}% connectivity={coverage}%")

    return map_id, chunk, entities


def make_level(identifier, chunk, entities, uid):
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
                "__cHei": CHUNK_SIZE, "__cWid": CHUNK_SIZE, "__gridSize": 16,
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
                "__cHei": CHUNK_SIZE, "__cWid": CHUNK_SIZE, "__gridSize": 16,
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
        "pxHei": CHUNK_SIZE * 16,
        "pxWid": CHUNK_SIZE * 16,
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
    # First, generate maps from terrain overrides
    for map_id, override_fn in TERRAIN_OVERRIDES.items():
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
            "externalRelPath": f"ds2d/{map_id}.ldtkl",
            "fieldInstances": [], "identifier": map_id,
            "iid": level["iid"], "layerInstances": None,
            "pxHei": level["pxHei"], "pxWid": level["pxWid"],
            "uid": uid, "useAutoIdentifier": True,
            "worldDepth": 0, "worldX": -1, "worldY": -1,
        })

    # Then, generate remaining maps from design docs (skip those already generated by overrides)
    override_ids = set(TERRAIN_OVERRIDES.keys())
    for doc_file in sorted(os.listdir(docs_dir)):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(docs_dir, doc_file)
        # Peek at the doc to get the map ID
        with open(doc_path, encoding="utf-8") as f:
            doc = json.load(f)
        map_id = doc.get("id", "")
        # Handle aliases
        map_id = {"IrithyllOfTheBorealValley": "Irithyll"}.get(map_id, map_id)
        if map_id in override_ids:
            continue  # already generated by override
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
        "defaultLevelHeight": CHUNK_SIZE * 16, "defaultLevelWidth": CHUNK_SIZE * 16,
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
        "worldGridHeight": CHUNK_SIZE * 16, "worldGridWidth": CHUNK_SIZE * 16,
        "worldLayout": "Free", "worlds": [],
    }

    project_path = os.path.join(script_dir, "ds2d.ldtk")
    with open(project_path, "w") as f:
        json.dump(project, f, indent=2)
    print(f"  wrote {project_path}")


if __name__ == "__main__":
    main()
