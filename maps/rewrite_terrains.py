#!/usr/bin/env python3
"""Batch rewrite all remaining map terrain functions for faithful DS3 layouts.
Outputs the new function bodies to stdout for each map.
"""
import sys

# Terrain tile constants
CHUNK_SIZE = 160
TILE_GROUND = 1
TILE_WALL = 2
TILE_POISON = 4

# Map functions to generate - each returns (terrain_code, entities_code, print_label)
MAPS = [
    # (func_name, print_label, docstring, terrain_lines, entity_lines)
]

def gen_fill(tile_var, x1, y1, x2, y2):
    return f'    fill_tiles(chunk, {tile_var}, {x1}, {y1}, {x2}, {y2})'

def gen_ellipse(cx, cy, rx, ry):
    return f'    carve_ellipse(chunk, {cx}, {cy}, {rx}, {ry})'

def gen_corridor(x1, y1, x2, y2, w=3):
    return f'    carve_corridor(chunk, {x1}, {y1}, {x2}, {y2}, width={w})'

def gen_enemy(kind, tx, ty):
    return f'        ("{kind}", {tx}, {ty}),'

def gen_item(kind, name, tx, ty, val=0):
    if val:
        return f'        ("{kind}", "{name}", {tx}, {ty}, {val}),'
    return f'        ("{kind}", "{name}", {tx}, {ty}, 0),'

# ========================================================================
# ROAD OF SACRIFICES - dark forest, Crystal Sage boss
# ========================================================================
road_of_sacrifices_terrain = """    # 1. Entry dense forest (top-left)
    fill_tiles(chunk, TILE_GROUND, 8, 8, 40, 30)
    fill_tiles(chunk, TILE_WALL, 16, 14, 18, 16)
    fill_tiles(chunk, TILE_WALL, 30, 22, 32, 24)
    # 2. Forest path east
    fill_tiles(chunk, TILE_GROUND, 36, 16, 60, 34)
    # 3. Halfway Fortress
    fill_tiles(chunk, TILE_GROUND, 55, 28, 75, 50)
    carve_ellipse(chunk, 64, 38, 8, 10)
    # 4. Crucifixion Woods - large hub
    fill_tiles(chunk, TILE_GROUND, 30, 50, 130, 95)
    fill_tiles(chunk, TILE_WALL, 44, 56, 48, 60)
    fill_tiles(chunk, TILE_WALL, 72, 62, 76, 66)
    fill_tiles(chunk, TILE_WALL, 100, 58, 104, 62)
    fill_tiles(chunk, TILE_WALL, 56, 78, 60, 82)
    fill_tiles(chunk, TILE_WALL, 88, 82, 92, 86)
    # 5. Corvian forest path to sage
    fill_tiles(chunk, TILE_GROUND, 110, 95, 135, 120)
    fill_tiles(chunk, TILE_WALL, 118, 100, 120, 102)
    # 6. Crystal Sage arena
    carve_ellipse(chunk, 130, 132, 16, 14)
    # 7. Path south to Farron
    fill_tiles(chunk, TILE_GROUND, 48, 95, 58, 135)
    carve_ellipse(chunk, 52, 132, 8, 6)
    # 8. Path east to Cathedral
    fill_tiles(chunk, TILE_GROUND, 130, 80, 150, 92)
    carve_ellipse(chunk, 148, 86, 6, 5)
    # Connections
    fill_tiles(chunk, TILE_GROUND, 50, 36, 56, 52)
    fill_tiles(chunk, TILE_GROUND, 115, 92, 122, 98)"""

road_of_sacrifices_entities = """
    spawn_px, spawn_py = 18 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))
    entities.append(make_entity("Bonfire", 18 * 16, 18 * 16))
    entities.append(make_entity("Bonfire", 64 * 16, 40 * 16))
    entities.append(make_entity("Bonfire", 80 * 16, 60 * 16))
    entities.append(make_entity("BossSpawn", 130 * 16, 128 * 16))
    enemy_data = [
        ("HollowSoldier", 22, 14), ("HollowSoldier", 34, 22),
        ("DarkMage", 50, 34), ("DarkMage", 58, 38),
        ("HollowSoldier", 66, 44), ("HollowSoldier", 70, 48),
        ("HollowSoldier", 46, 58), ("HollowSoldier", 80, 64),
        ("DarkMage", 94, 68), ("Archer", 108, 60),
        ("Archer", 120, 64), ("CrystalLizard", 62, 72),
        ("BlackKnight", 122, 104),
        ("Ghru", 52, 115), ("Ghru", 56, 120),
        ("HollowSoldier", 84, 78), ("HollowSoldier", 96, 80),
        ("StarvedHound", 114, 98), ("StarvedHound", 128, 112),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))
    item_data = [
        ("SoulOrb", "Soul of a Deserted Corpse", 28, 12, 200),
        ("EstusShard", "Estus Shard", 80, 56, 0),
        ("TitaniteShard", "Titanite Shard", 68, 68, 0),
        ("WeaponDrop", "Rapier", 90, 76, 0),
        ("PurpleMoss", "Purple Moss", 54, 125, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 120, 62, 400),
        ("RingDrop", "Flynn's Ring", 126, 110, 0),
        ("TitaniteShard", "Titanite Shard", 100, 72, 0),
    ]
    for kind, name, tx, ty, val in item_data:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))
    entities.append(make_entity("FogGate", 52 * 16, 136 * 16, [make_field("dest_area", "String", "FarronKeep"), make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0), make_field("width", "Float", 64.0), make_field("height", "Float", 80.0)]))
    entities.append(make_entity("FogGate", 150 * 16, 86 * 16, [make_field("dest_area", "String", "CathedralDeep"), make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0), make_field("width", "Float", 64.0), make_field("height", "Float", 80.0)]))
    entities.append(make_entity("Light", 18 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.4), make_field("g", "Float", 0.5), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.2)]))
    entities.append(make_entity("Light", 80 * 16, 60 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.5), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 130 * 16, 128 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.4), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.35)]))"""

# ========================================================================
# FARRON KEEP - poison swamp, Abyss Watchers boss
# ========================================================================
farron_keep_terrain = """    # 1. Entry from Road (top-left)
    carve_ellipse(chunk, 20, 20, 10, 8)
    # 2. Poison swamp - large central area
    fill_tiles(chunk, TILE_POISON, 15, 30, 120, 110)
    # Safe ground islands in the swamp
    fill_tiles(chunk, TILE_GROUND, 20, 35, 40, 50)
    fill_tiles(chunk, TILE_GROUND, 55, 45, 75, 60)
    fill_tiles(chunk, TILE_GROUND, 85, 55, 105, 70)
    fill_tiles(chunk, TILE_GROUND, 35, 70, 55, 85)
    fill_tiles(chunk, TILE_GROUND, 65, 75, 85, 90)
    fill_tiles(chunk, TILE_GROUND, 95, 80, 115, 95)
    # 3. Old Demon ruins (center)
    fill_tiles(chunk, TILE_GROUND, 40, 55, 60, 70)
    fill_tiles(chunk, TILE_WALL, 44, 58, 48, 62)
    fill_tiles(chunk, TILE_WALL, 52, 64, 56, 68)
    # 4. Abyss Watchers arena (bottom-right)
    carve_ellipse(chunk, 120, 120, 20, 18)
    fill_tiles(chunk, TILE_GROUND, 105, 100, 120, 108)
    # 5. Path from swamp to arena
    fill_tiles(chunk, TILE_GROUND, 100, 90, 110, 105)
    # 6. Perimeter path (edges)
    fill_tiles(chunk, TILE_GROUND, 10, 25, 25, 40)
    fill_tiles(chunk, TILE_GROUND, 110, 40, 130, 55)
    # Connection from entry to swamp
    fill_tiles(chunk, TILE_GROUND, 14, 24, 24, 36)"""

farron_keep_entities = """
    spawn_px, spawn_py = 20 * 16, 18 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))
    entities.append(make_entity("Bonfire", 20 * 16, 18 * 16))
    entities.append(make_entity("Bonfire", 65 * 16, 50 * 16))
    entities.append(make_entity("BossSpawn", 120 * 16, 116 * 16))
    enemy_data = [
        ("Ghru", 28, 40), ("Ghru", 36, 45), ("Ghru", 60, 52),
        ("Ghru", 70, 56), ("Ghru", 90, 62), ("Ghru", 42, 76),
        ("Ghru", 72, 82), ("Ghru", 100, 86), ("Darkwraith", 48, 64),
        ("Darkwraith", 80, 72), ("HollowSoldier", 32, 38), ("HollowSoldier", 96, 60),
        ("CrystalLizard", 108, 84), ("Ghru", 110, 92), ("Ghru", 115, 96),
        ("Basilisk", 55, 68), ("Basilisk", 85, 78), ("Rat", 30, 60),
        ("Rat", 65, 85), ("Dog", 95, 70),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))
    item_data = [
        ("SoulOrb", "Soul of a Deserted Corpse", 24, 34, 200),
        ("PurpleMoss", "Purple Moss", 50, 48, 0),
        ("EstusShard", "Estus Shard", 70, 54, 0),
        ("TitaniteShard", "Titanite Shard", 88, 66, 0),
        ("WeaponDrop", "Great Axe", 46, 72, 0),
        ("RingDrop", "Farron Ring", 110, 90, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 80, 80, 400),
        ("PurpleMoss", "Purple Moss", 60, 74, 0),
    ]
    for kind, name, tx, ty, val in item_data:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))
    entities.append(make_entity("FogGate", 120 * 16, 138 * 16, [make_field("dest_area", "String", "CatacombsOfCarthus"), make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0), make_field("width", "Float", 64.0), make_field("height", "Float", 80.0)]))
    entities.append(make_entity("FogGate", 8 * 16, 18 * 16, [make_field("dest_area", "String", "RoadOfSacrifices"), make_field("dest_x", "Float", 800.0), make_field("dest_y", "Float", 2100.0), make_field("width", "Float", 64.0), make_field("height", "Float", 64.0)]))
    entities.append(make_entity("Light", 20 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.4), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.2)]))
    entities.append(make_entity("Light", 65 * 16, 50 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.4), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.2)]))
    entities.append(make_entity("Light", 120 * 16, 116 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.4), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.35)]))"""

# ========================================================================
# CATHEDRAL OF THE DEEP - cathedral interior, Deacons boss
# ========================================================================
cathedral_deep_terrain = """    # 1. Entry from Road of Sacrifices (top-left)
    carve_ellipse(chunk, 20, 20, 10, 8)
    # 2. Cemetery entry (top)
    fill_tiles(chunk, TILE_GROUND, 15, 15, 60, 40)
    fill_tiles(chunk, TILE_WALL, 28, 22, 32, 28)
    fill_tiles(chunk, TILE_WALL, 44, 30, 48, 36)
    # 3. Outer cemetery (center-left)
    fill_tiles(chunk, TILE_GROUND, 30, 40, 70, 70)
    fill_tiles(chunk, TILE_WALL, 40, 48, 44, 52)
    fill_tiles(chunk, TILE_WALL, 55, 56, 59, 60)
    # 4. Cleansing Chapel (center)
    fill_tiles(chunk, TILE_GROUND, 60, 50, 100, 80)
    carve_ellipse(chunk, 80, 64, 16, 12)
    # 5. Giant Room (left)
    carve_ellipse(chunk, 24, 65, 12, 10)
    fill_tiles(chunk, TILE_GROUND, 30, 58, 40, 68)
    # 6. Deacon halls (right)
    fill_tiles(chunk, TILE_GROUND, 95, 50, 140, 85)
    fill_tiles(chunk, TILE_WALL, 104, 58, 108, 64)
    fill_tiles(chunk, TILE_WALL, 120, 68, 124, 74)
    fill_tiles(chunk, TILE_WALL, 132, 56, 136, 62)
    # 7. Rosaria's chamber (far right)
    fill_tiles(chunk, TILE_GROUND, 138, 70, 152, 90)
    carve_ellipse(chunk, 146, 80, 8, 8)
    # 8. Deacons of the Deep arena (bottom-center)
    carve_ellipse(chunk, 80, 120, 22, 18)
    fill_tiles(chunk, TILE_GROUND, 70, 85, 90, 105)
    # 9. Deep Accursed ambush (center-right)
    fill_tiles(chunk, TILE_GROUND, 110, 88, 130, 100)
    carve_ellipse(chunk, 120, 94, 8, 5)
    # Connections
    fill_tiles(chunk, TILE_GROUND, 55, 42, 65, 52)
    fill_tiles(chunk, TILE_GROUND, 96, 64, 105, 72)
    fill_tiles(chunk, TILE_GROUND, 130, 80, 140, 82)"""

cathedral_deep_entities = """
    spawn_px, spawn_py = 20 * 16, 18 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))
    entities.append(make_entity("Bonfire", 20 * 16, 18 * 16))
    entities.append(make_entity("Bonfire", 80 * 16, 62 * 16))
    entities.append(make_entity("BossSpawn", 80 * 16, 116 * 16))
    enemy_data = [
        ("HollowSoldier", 24, 22), ("HollowSoldier", 36, 26), ("HollowSoldier", 48, 34),
        ("CathedralKnight", 42, 50), ("CathedralKnight", 60, 60),
        ("Thrall", 34, 46), ("Thrall", 50, 54), ("Thrall", 68, 66),
        ("Evangelist", 76, 70), ("Evangelist", 92, 58),
        ("Deacon", 100, 62), ("Deacon", 110, 66), ("Deacon", 128, 60),
        ("Deacon", 114, 72), ("Deacon", 130, 76),
        ("DeepAccursed", 122, 92),
        ("ManGrub", 142, 78), ("ManGrub", 148, 84),
        ("StarvedHound", 56, 64), ("StarvedHound", 86, 74),
        ("CathedralGraveWarden", 38, 58), ("CathedralGraveWarden", 64, 68),
        ("HollowSoldier", 98, 78), ("HollowSoldier", 136, 66),
        ("Deacon", 76, 100), ("Deacon", 84, 104), ("Deacon", 88, 108),
        ("Thrall", 74, 92), ("Thrall", 86, 96),
        ("CathedralKnight", 100, 84),
        ("ManGrub", 140, 86),
    ]
    for kind, tx, ty in enemy_data:
        mapped = ENEMY_KIND_MAP.get(kind, kind)
        entities.append(make_entity("Enemy", tx * 16, ty * 16, [make_field("kind", "LocalEnum.EnemyKind", mapped)]))
    entities.append(make_entity("Npc", 146 * 16, 78 * 16, [make_field("name", "String", "Rosaria"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A0C0"), make_field("dialogue", "String", "Welcome to Rosaria's Bed Chamber|Offer pale tongues to reallocate stats")]))
    item_data = [
        ("SoulOrb", "Soul of a Deserted Corpse", 30, 20, 200),
        ("EstusShard", "Estus Shard", 80, 58, 0),
        ("TitaniteShard", "Titanite Shard", 56, 56, 0),
        ("WeaponDrop", "Great Sword", 108, 64, 0),
        ("SoulOrb", "Soul of an Unknown Traveler", 126, 70, 400),
        ("RingDrop", "Deep Ring", 72, 96, 0),
        ("TitaniteShard", "Titanite Shard", 94, 76, 0),
    ]
    for kind, name, tx, ty, val in item_data:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", tx * 16, ty * 16, fields))
    entities.append(make_entity("FogGate", 80 * 16, 138 * 16, [make_field("dest_area", "String", "CatacombsOfCarthus"), make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0), make_field("width", "Float", 64.0), make_field("height", "Float", 80.0)]))
    entities.append(make_entity("FogGate", 8 * 16, 18 * 16, [make_field("dest_area", "String", "RoadOfSacrifices"), make_field("dest_x", "Float", 2400.0), make_field("dest_y", "Float", 500.0), make_field("width", "Float", 64.0), make_field("height", "Float", 64.0)]))
    entities.append(make_entity("Light", 20 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.4), make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 80 * 16, 62 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.5), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 80 * 16, 116 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.3), make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.35)]))"""

# Print all the terrain/entity code
print("ROAD_TERRAIN:")
print(road_of_sacrifices_terrain)
print("\nROAD_ENTITIES:")
print(road_of_sacrifices_entities)
print("\nFARRON_TERRAIN:")
print(farron_keep_terrain)
print("\nFARRON_ENTITIES:")
print(farron_keep_entities)
print("\nCATHEDRAL_TERRAIN:")
print(cathedral_deep_terrain)
print("\nCATHEDRAL_ENTITIES:")
print(cathedral_deep_entities)
