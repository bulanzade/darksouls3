#!/usr/bin/env python3
"""Generate LDtk .ldtkl level files from the tile layouts defined in wasm_entry.rs."""
import json
import os
import uuid

CHUNK_SIZE = 120
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_WALL = 2
TILE_WALLTOP = 3
TILE_POISON = 4
LEVEL_UIDS = {
    "CemeteryOfAsh": 1,
    "FirelinkShrine": 2,
    "LothricWall": 3,
    "UndeadSettlement": 4,
    "CathedralDeep": 5,
    "Irithyll": 6,
}

ENTITY_UIDS = {
    "PlayerSpawn": 101,
    "BossSpawn": 102,
    "Bonfire": 103,
    "Enemy": 104,
    "Item": 105,
    "Chest": 106,
    "Npc": 107,
    "Light": 108,
    "FogGate": 109,
    "TilePatch": 110,
}

ENUM_UIDS = {
    "EnemyKind": 201,
    "ItemKind": 202,
    "NpcKind": 203,
    "TileKind": 204,
}

FIELD_UIDS = {
    "PlayerSpawn.heal": 301,
    "Enemy.kind": 302,
    "Item.kind": 303,
    "Item.value": 304,
    "Item.name": 305,
    "Chest.loot_kind": 306,
    "Chest.loot_value": 307,
    "Chest.loot_name": 308,
    "Chest.is_mimic": 309,
    "Chest.slot": 310,
    "Npc.name": 311,
    "Npc.kind": 312,
    "Npc.color": 313,
    "Npc.dialogue": 314,
    "Light.radius": 315,
    "Light.r": 316,
    "Light.g": 317,
    "Light.b": 318,
    "Light.intensity": 319,
    "FogGate.dest_area": 320,
    "FogGate.dest_x": 321,
    "FogGate.dest_y": 322,
    "FogGate.width": 323,
    "FogGate.height": 324,
    "TilePatch.tile": 325,
    "TilePatch.x1": 326,
    "TilePatch.y1": 327,
    "TilePatch.x2": 328,
    "TilePatch.y2": 329,
    "TilePatch.condition": 330,
}

def new_chunk():
    return [[TILE_WALL for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

def fill_tiles(chunk, tile, x1, y1, x2, y2):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= y < CHUNK_SIZE and 0 <= x < CHUNK_SIZE:
                chunk[y][x] = tile

def carve_ellipse(chunk, cx, cy, rx, ry):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if 0 <= y < CHUNK_SIZE and 0 <= x < CHUNK_SIZE:
                dx = (x - cx) / rx if rx > 0 else 0
                dy = (y - cy) / ry if ry > 0 else 0
                if dx * dx + dy * dy <= 1.0:
                    chunk[y][x] = TILE_GROUND

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
    ent = {
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
    return ent

def populate_entity_def_uids(entities):
    for ent in entities:
        ent["defUid"] = ENTITY_UIDS[ent["__identifier"]]
        for fld in ent.get("fieldInstances", []):
            key = f"{ent['__identifier']}.{fld['__identifier']}"
            fld["defUid"] = FIELD_UIDS.get(key, 0)

def make_tile_patch(px, py, tile, x1, y1, x2, y2, condition):
    return make_entity("TilePatch", px, py, [
        make_field("tile", "LocalEnum.TileKind", tile),
        make_field("x1", "Int", x1),
        make_field("y1", "Int", y1),
        make_field("x2", "Int", x2),
        make_field("y2", "Int", y2),
        make_field("condition", "String", condition),
    ])

def make_enum(identifier, uid, values):
    return {
        "externalFileChecksum": None,
        "externalRelPath": None,
        "iconTilesetUid": None,
        "identifier": identifier,
        "tags": [],
        "uid": uid,
        "values": [
            {
                "__tileSrcRect": None,
                "color": value.get("color", 0xFFFFFF),
                "id": value["id"],
                "tileId": None,
                "tileRect": None,
            }
            for value in values
        ],
    }

def wrap_default(field_type, default):
    if default is None:
        return None
    if field_type == "Bool":
        return {"id": "V_Bool", "params": [bool(default)]}
    if field_type == "Int":
        return {"id": "V_Int", "params": [int(default)]}
    if field_type == "Float":
        return {"id": "V_Float", "params": [float(default)]}
    if field_type == "Color":
        s = str(default)
        if s.startswith("#"):
            s = s[1:]
        return {"id": "V_Int", "params": [int(s, 16)]}
    if field_type == "String" or field_type.startswith("LocalEnum."):
        return {"id": "V_String", "params": [str(default)]}
    return None

def make_field_def(identifier, field_type, uid, default, purple_type, doc=None):
    return {
        "__type": field_type,
        "acceptFileTypes": None,
        "allowedRefs": "Any",
        "allowedRefsEntityUid": None,
        "allowedRefTags": [],
        "allowOutOfLevelRef": False,
        "arrayMaxLength": None,
        "arrayMinLength": None,
        "autoChainRef": True,
        "canBeNull": False,
        "defaultOverride": wrap_default(field_type, default),
        "doc": doc,
        "editorAlwaysShow": False,
        "editorCutLongValues": True,
        "editorDisplayColor": None,
        "editorDisplayMode": "Hidden",
        "editorDisplayPos": "Above",
        "editorDisplayScale": 1.0,
        "editorLinkStyle": "StraightArrow",
        "editorShowInWorld": True,
        "editorTextPrefix": None,
        "editorTextSuffix": None,
        "exportToToc": False,
        "identifier": identifier,
        "isArray": False,
        "max": None,
        "min": None,
        "regex": None,
        "searchable": True,
        "symmetricalRef": False,
        "textLanguageMode": None,
        "tilesetUid": None,
        "type": purple_type,
        "uid": uid,
        "useForSmartColor": False,
    }

def make_entity_def(identifier, uid, width=16, height=16, resizable_x=False, resizable_y=False, render_mode="Rectangle", color="#FFFFFF", field_defs=None):
    return {
        "allowOutOfBounds": False,
        "color": color,
        "doc": None,
        "exportToToc": False,
        "fieldDefs": field_defs or [],
        "fillOpacity": 0.8,
        "height": height,
        "hollow": False,
        "identifier": identifier,
        "keepAspectRatio": False,
        "limitBehavior": "MoveLastOne",
        "limitScope": "PerLevel",
        "lineOpacity": 1.0,
        "maxCount": 0,
        "maxHeight": None,
        "maxWidth": None,
        "minHeight": None,
        "minWidth": None,
        "nineSliceBorders": [],
        "pivotX": 0.5,
        "pivotY": 1.0,
        "renderMode": render_mode,
        "resizableX": resizable_x,
        "resizableY": resizable_y,
        "showName": True,
        "tags": [],
        "tileId": None,
        "tileOpacity": 1.0,
        "tileRect": None,
        "tileRenderMode": "Stretch",
        "tilesetId": None,
        "uid": uid,
        "uiTileRect": None,
        "width": width,
    }

# ---- Area generators ----

def make_cemetery():
    chunk = new_chunk()
    # Player wakes in the lower-left grave pocket
    carve_ellipse(chunk, 12, 103, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 12, 96, 23, 108)
    carve_ellipse(chunk, 28, 91, 12, 8)
    fill_tiles(chunk, TILE_GROUND, 22, 86, 39, 98)
    # Main cemetery route bends upward and right toward Gundyr
    fill_tiles(chunk, TILE_GROUND, 34, 76, 47, 91)
    carve_ellipse(chunk, 48, 70, 15, 10)
    fill_tiles(chunk, TILE_GROUND, 45, 62, 64, 76)
    carve_ellipse(chunk, 65, 56, 17, 10)
    fill_tiles(chunk, TILE_GROUND, 61, 48, 77, 64)
    carve_ellipse(chunk, 79, 41, 13, 9)
    # Right-lower optional branch
    fill_tiles(chunk, TILE_GROUND, 38, 84, 58, 94)
    fill_tiles(chunk, TILE_GROUND, 56, 90, 78, 102)
    carve_ellipse(chunk, 91, 104, 19, 12)
    fill_tiles(chunk, TILE_POISON, 86, 99, 97, 109)
    fill_tiles(chunk, TILE_GROUND, 88, 101, 94, 106)
    # Gundyr arena
    fill_tiles(chunk, TILE_GROUND, 76, 33, 88, 42)
    carve_ellipse(chunk, 96, 30, 22, 18)
    carve_ellipse(chunk, 96, 30, 16, 12)
    for x in range(72, CHUNK_SIZE): chunk[10][x] = TILE_WALL
    for y in range(10, 51): chunk[y][71] = TILE_WALL; chunk[y][CHUNK_SIZE - 1] = TILE_WALL
    for y in range(43, 51): chunk[y][118] = TILE_WALL
    # Post-Gundyr route
    fill_tiles(chunk, TILE_GROUND, 84, 28, 96, 44)
    fill_tiles(chunk, TILE_GROUND, 62, 18, 88, 34)
    fill_tiles(chunk, TILE_GROUND, 36, 10, 66, 24)
    fill_tiles(chunk, TILE_GROUND, 16, 8, 40, 18)
    for y in range(6, 21): chunk[y][15] = TILE_WALL
    for x in range(16, 41): chunk[7][x] = TILE_WALL
    # Gravestones
    fill_tiles(chunk, TILE_WALL, 42, 84, 45, 87)
    fill_tiles(chunk, TILE_WALL, 30, 88, 33, 91)
    fill_tiles(chunk, TILE_WALL, 58, 64, 61, 67)
    fill_tiles(chunk, TILE_WALL, 88, 20, 91, 23)
    fill_tiles(chunk, TILE_WALL, 106, 35, 109, 38)
    # South wall of arena (MUST come after all ground fills)
    for x in range(70, CHUNK_SIZE): chunk[43][x] = TILE_WALL
    fill_tiles(chunk, TILE_GROUND, 78, 41, 90, 45)

    entities = []
    entities.append(make_entity("PlayerSpawn", 200, 1660, [
        make_field("heal", "Bool", True),
    ]))
    entities.append(make_entity("BossSpawn", 1540, 470))
    # Enemies
    for kind, x, y in [("HollowSoldier",470,1450),("HollowSoldier",760,1120),
                       ("Archer",1120,880),("Knight",1180,730),("HollowSoldier",1040,850),
                       ("CrystalLizard",1450,1660)]:
        entities.append(make_entity("Enemy", x, y, [make_field("kind", "LocalEnum.EnemyKind", kind)]))
    # Items
    for kind, x, y, val in [("SoulOrb",210,1620,100),("SoulOrb",760,1140,150),
                             ("HomewardBone",1360,650,0),("EstusShard",1500,1700,0),
                             ("SoulOrb",1800,640,300)]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", x, y, fields))
    # Chests
    entities.append(make_entity("Chest", 1570, 1710, [
        make_field("loot_kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("loot_value", "Int", 500),
        make_field("is_mimic", "Bool", False),
    ]))
    # Lights
    for x, y, r, cr, cg, cb, intensity in [
        (200,1660,190,0.82,0.78,0.62,0.22),(760,1120,170,0.78,0.58,0.34,0.14),
        (1450,1660,210,0.55,0.75,0.9,0.18),(1460,620,360,0.55,0.52,0.62,0.22),
        (1800,720,220,0.72,0.62,0.48,0.18)]:
        entities.append(make_entity("Light", x, y, [
            make_field("radius", "Float", r),
            make_field("r", "Float", cr), make_field("g", "Float", cg), make_field("b", "Float", cb),
            make_field("intensity", "Float", intensity),
        ]))
    # Fog gates
    entities.append(make_entity("FogGate", 1352, 688, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 1470), make_field("dest_y", "Float", 520),
        make_field("width", "Float", 208), make_field("height", "Float", 28),
    ], ))
    entities.append(make_entity("FogGate", 360, 160, [
        make_field("dest_area", "String", "FirelinkShrine"),
        make_field("dest_x", "Float", 960), make_field("dest_y", "Float", 160),
        make_field("width", "Float", 120), make_field("height", "Float", 32),
    ]))
    entities.append(make_tile_patch(224, 128, "Ground", 16, 8, 40, 18, "gundyr_door_open"))

    return chunk, entities

def make_firelink():
    chunk = new_chunk()
    for y in range(8, 40):
        for x in range(10, 50): chunk[y][x] = TILE_GROUND
    for y in range(15, 25):
        for x in range(2, 12): chunk[y][x] = TILE_GROUND
    for y in range(20, 35):
        for x in range(50, 65): chunk[y][x] = TILE_GROUND
    for y in range(5, 15):
        for x in range(20, 35): chunk[y][x] = TILE_GROUND
    for y in range(0, 10):
        for x in range(50, 70): chunk[y][x] = TILE_GROUND
    for y in range(8, 15):
        for x in range(28, 70): chunk[y][x] = TILE_GROUND
    for y in range(38, 55):
        for x in range(20, 35): chunk[y][x] = TILE_GROUND
    for y in range(35, 50):
        for x in range(40, 55): chunk[y][x] = TILE_GROUND
    for y in range(30, 40):
        for x in range(42, 50): chunk[y][x] = TILE_POISON

    entities = []
    entities.append(make_entity("PlayerSpawn", 320, 320, [make_field("heal", "Bool", True)]))
    entities.append(make_entity("Bonfire", 320, 320))
    entities.append(make_entity("Item", 450, 200, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("value", "Int", 100),
    ]))
    # NPCs
    for name, kind, x, y, color, dialogue in [
        ("防火女", "LevelUp", 360, 300, "#33E6B3", "欢迎来到传火祭祀场，无火的余灰。|薪王们已离开了他们的王座。|请将他们带回原本的位置。|[Enter] 升级"),
        ("安德烈", "Blacksmith", 300, 380, "#B38033", "我是安德烈，祭祀场的铁匠。|交给我吧，你的武器会焕然一新。|[Enter] 强化武器 (1000灵魂)"),
        ("侍女", "Merchant", 380, 400, "#CCB34D", "你好啊，无火的余灰。|我这里有各种各样好东西。|[Enter] 购买原素碎片 (500灵魂)"),
    ]:
        entities.append(make_entity("Npc", x, y, [
            make_field("name", "String", name),
            make_field("kind", "LocalEnum.NpcKind", kind),
            make_field("color", "Color", color),
            make_field("dialogue", "String", dialogue),
        ]))
    # Lights
    for x, y, r, cr, cg, cb, intensity in [
        (320,320,300,0.95,0.9,0.7,0.5),(300,380,150,0.9,0.6,0.3,0.2),(380,400,150,0.9,0.6,0.3,0.2)]:
        entities.append(make_entity("Light", x, y, [
            make_field("radius", "Float", r),
            make_field("r", "Float", cr), make_field("g", "Float", cg), make_field("b", "Float", cb),
            make_field("intensity", "Float", intensity),
        ]))
    # Fog gates
    for da, dx, dy, x, y, w, h in [
        ("UndeadSettlement",200,200,855,380,64,120),
        ("CathedralDeep",200,200,380,700,80,32),
        ("CemeteryOfAsh",360,220,960,64,120,32)]:
        entities.append(make_entity("FogGate", x, y, [
            make_field("dest_area", "String", da),
            make_field("dest_x", "Float", dx), make_field("dest_y", "Float", dy),
            make_field("width", "Float", w), make_field("height", "Float", h),
        ]))

    return chunk, entities

def make_lothric_wall():
    chunk = new_chunk()
    for y in range(5, 25):
        for x in range(5, 35): chunk[y][x] = TILE_GROUND
    for y in range(10, 40):
        for x in range(30, 70): chunk[y][x] = TILE_GROUND
    for y in range(15, 20):
        for x in range(55, 65): chunk[y][x] = TILE_WALL
    for y in range(35, 55):
        for x in range(20, 55): chunk[y][x] = TILE_GROUND
    for y in range(20, 35):
        for x in range(65, 90): chunk[y][x] = TILE_GROUND
    for y in range(45, 70):
        for x in range(40, 80): chunk[y][x] = TILE_GROUND
    for y in range(65, 80):
        for x in range(50, 65): chunk[y][x] = TILE_GROUND
    for y in range(80, 105):
        for x in range(35, 65): chunk[y][x] = TILE_GROUND
    for x in range(35, 45): chunk[79][x] = TILE_WALL
    for x in range(55, 65): chunk[79][x] = TILE_WALL
    for x in range(35, 65): chunk[105][x] = TILE_WALL
    for y in range(79, 106): chunk[y][34] = TILE_WALL
    for y in range(79, 106): chunk[y][65] = TILE_WALL
    for x in range(25, 30):
        for y in range(40, 45): chunk[y][x] = TILE_WALL
    for x in range(70, 75):
        for y in range(55, 60): chunk[y][x] = TILE_WALL

    entities = []
    entities.append(make_entity("PlayerSpawn", 200, 200, [make_field("heal", "Bool", False)]))
    entities.append(make_entity("Bonfire", 200, 200))
    entities.append(make_entity("BossSpawn", 960, 1500))
    for kind, x, y in [("HollowSoldier",300,150),("Archer",400,250),("Knight",600,300),
                       ("HollowSoldier",700,400),("Archer",800,350),("Assassin",1200,400),
                       ("HollowSoldier",1100,500),("Knight",500,650),("DarkMage",600,750),
                       ("HollowSoldier",700,950),("Knight",900,1000),("Archer",1000,1100),
                       ("DarkMage",800,1150),("Knight",750,1300),("MiniBoss",800,1400)]:
        entities.append(make_entity("Enemy", x, y, [make_field("kind", "LocalEnum.EnemyKind", kind)]))
    for kind, x, y, val in [("SoulOrb",250,200,200),("SoulOrb",700,350,300),
                             ("EstusShard",1200,450,0),("SoulOrb",500,700,200),
                             ("PurpleMoss",800,1000,0),("SoulOrb",950,1100,500),
                             ("SoulOrb",700,1350,1000),("EstusShard",600,1500,0)]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb": fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", x, y, fields))
    for lk, lv, x, y, mimic in [
        ("SoulOrb",300,350,300,False),
        ("WeaponDrop",0,1100,500,False),  # Spear
        ("ArmorDrop",0,900,1050,True),   # Knight Armor chest, mimic
        ("RingDrop",0,650,1450,False),
    ]:
        name = ""
        if lk == "WeaponDrop": name = "Spear"
        elif lk == "ArmorDrop": name = "Knight Armor"
        elif lk == "RingDrop": name = "Steel Protection"
        entities.append(make_entity("Chest", x, y, [
            make_field("loot_kind", "LocalEnum.ItemKind", lk),
            make_field("loot_value", "Int", lv),
            make_field("loot_name", "String", name),
            make_field("is_mimic", "Bool", mimic),
        ]))
    for x, y, r, cr, cg, cb, intensity in [
        (200,200,250,0.9,0.8,0.6,0.4),(700,350,200,0.5,0.5,0.7,0.2),
        (1000,500,180,0.9,0.6,0.3,0.15),(600,700,200,0.9,0.6,0.3,0.15),
        (800,1050,200,0.9,0.6,0.3,0.15),(900,1400,220,0.4,0.5,0.8,0.25)]:
        entities.append(make_entity("Light", x, y, [
            make_field("radius", "Float", r),
            make_field("r", "Float", cr), make_field("g", "Float", cg), make_field("b", "Float", cb),
            make_field("intensity", "Float", intensity),
        ]))
    entities.append(make_entity("FogGate", 800, 1264, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 960), make_field("dest_y", "Float", 1500),
        make_field("width", "Float", 128), make_field("height", "Float", 32),
    ]))

    return chunk, entities

def make_undead_settlement():
    chunk = new_chunk()
    for y in range(5, 25):
        for x in range(5, 30): chunk[y][x] = TILE_GROUND
    for y in range(15, 40):
        for x in range(20, 55): chunk[y][x] = TILE_GROUND
    for y in range(35, 55):
        for x in range(15, 40): chunk[y][x] = TILE_GROUND
    for y in range(40, 50):
        for x in range(40, 65): chunk[y][x] = TILE_GROUND
    for y in range(50, 80):
        for x in range(30, 75): chunk[y][x] = TILE_GROUND
    for y in range(75, 90):
        for x in range(40, 55): chunk[y][x] = TILE_GROUND
    for y in range(90, 110):
        for x in range(35, 65): chunk[y][x] = TILE_GROUND
    for x in range(35, 45): chunk[89][x] = TILE_WALL
    for x in range(55, 65): chunk[89][x] = TILE_WALL
    for x in range(35, 65): chunk[110][x] = TILE_WALL
    for y in range(89, 111): chunk[y][34] = TILE_WALL
    for y in range(89, 111): chunk[y][65] = TILE_WALL
    for y in range(8, 20):
        for x in range(50, 75): chunk[y][x] = TILE_GROUND
    for y in range(42, 52):
        for x in range(55, 70): chunk[y][x] = TILE_POISON

    entities = []
    entities.append(make_entity("PlayerSpawn", 200, 200, [make_field("heal", "Bool", False)]))
    entities.append(make_entity("Bonfire", 200, 200))
    entities.append(make_entity("BossSpawn", 960, 1600))
    for kind, x, y in [("HollowSoldier",350,150),("HollowSoldier",400,300),("Archer",420,200),
                       ("Assassin",1000,250),("HollowSoldier",850,350),("HollowSoldier",400,550),
                       ("Knight",500,650),("Archer",450,750),("Assassin",550,850),
                       ("DarkMage",800,1000),("Knight",650,1100),("HollowSoldier",750,1200),
                       ("Archer",900,1250),("Knight",700,1450),("DarkMage",850,1500)]:
        entities.append(make_entity("Enemy", x, y, [make_field("kind", "LocalEnum.EnemyKind", kind)]))
    for kind, x, y, val in [("SoulOrb",300,250,200),("EstusShard",450,400,0),
                             ("SoulOrb",950,200,300),("PurpleMoss",950,250,0),
                             ("SoulOrb",500,600,200),("HomewardBone",550,900,0),
                             ("SoulOrb",700,1100,400),("PurpleMoss",800,1350,0),
                             ("SoulOrb",850,1550,800),("EstusShard",600,1500,0)]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb": fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", x, y, fields))
    for lk, lv, ln, x, y, mimic in [
        ("WeaponDrop",0,"Dagger",1050,200,False),
        ("ArmorDrop",0,"Hollow Soldier Helm",500,700,False),
        ("ArmorDrop",0,"Hollow Soldier Armor",750,1200,True),
        ("RingDrop",0,"Life Ring",900,1600,False),
        ("WeaponDrop",0,"Spear",650,1550,False),
    ]:
        entities.append(make_entity("Chest", x, y, [
            make_field("loot_kind", "LocalEnum.ItemKind", lk),
            make_field("loot_value", "Int", lv), make_field("loot_name", "String", ln),
            make_field("is_mimic", "Bool", mimic),
        ]))
    entities.append(make_entity("Npc", 250, 150, [
        make_field("name", "String", "商人"), make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#CCB34D"),
        make_field("dialogue", "String", "嘘！过来！|我有聚落里的好东西。|[Enter] 购买紫苔藓 (200灵魂)"),
    ]))
    for x, y, r, cr, cg, cb, intensity in [
        (200,200,250,0.7,0.85,0.5,0.35),(1000,300,180,0.8,0.7,0.4,0.15),
        (500,400,200,0.9,0.6,0.3,0.15),(500,700,200,0.8,0.5,0.2,0.2),
        (750,1000,180,0.9,0.6,0.3,0.15),(900,1300,200,0.9,0.5,0.2,0.15),
        (800,1550,220,0.8,0.2,0.4,0.25)]:
        entities.append(make_entity("Light", x, y, [
            make_field("radius", "Float", r),
            make_field("r", "Float", cr), make_field("g", "Float", cg), make_field("b", "Float", cb),
            make_field("intensity", "Float", intensity),
        ]))
    for da, dx, dy, x, y, w, h in [
        ("FirelinkShrine",500,350,200,100,80,32),
        ("CathedralDeep",200,200,600,1350,64,80),
        ("UndeadSettlement",800,1520,800,1416,128,32)]:
        entities.append(make_entity("FogGate", x, y, [
            make_field("dest_area", "String", da),
            make_field("dest_x", "Float", dx), make_field("dest_y", "Float", dy),
            make_field("width", "Float", w), make_field("height", "Float", h),
        ]))

    return chunk, entities

def make_cathedral_deep():
    chunk = new_chunk()
    for y in range(15, 25):
        for x in range(3, 25): chunk[y][x] = TILE_GROUND
    for y in range(10, 35):
        for x in range(22, 50): chunk[y][x] = TILE_GROUND
    for y in range(18, 28):
        for x in range(45, 80): chunk[y][x] = TILE_GROUND
    for y in range(5, 40):
        for x in range(75, 105): chunk[y][x] = TILE_GROUND
    for y in range(25, 50):
        for x in range(70, 100): chunk[y][x] = TILE_GROUND
    for y in range(35, 50):
        for x in range(40, 65): chunk[y][x] = TILE_GROUND
    for y in range(55, 75):
        for x in range(65, 95): chunk[y][x] = TILE_GROUND
    for x in range(65, 75): chunk[54][x] = TILE_WALL
    for x in range(85, 95): chunk[54][x] = TILE_WALL
    for x in range(65, 95): chunk[75][x] = TILE_WALL
    for y in range(54, 76): chunk[y][64] = TILE_WALL
    for y in range(54, 76): chunk[y][95] = TILE_WALL
    for y in range(12, 18):
        for x in range(10, 20): chunk[y][x] = TILE_POISON
    for y in range(28, 35):
        for x in range(50, 70): chunk[y][x] = TILE_POISON

    entities = []
    entities.append(make_entity("PlayerSpawn", 400, 400, [make_field("heal", "Bool", False)]))
    entities.append(make_entity("Bonfire", 400, 400))
    entities.append(make_entity("BossSpawn", 1280, 1040))
    for kind, x, y in [("Knight",500,300),("Knight",700,250),("Archer",600,400),
                       ("Archer",1000,350),("Knight",1400,200),("Knight",1500,400),
                       ("DarkMage",1300,300),("Knight",1150,600),("Archer",1300,700),
                       ("Assassin",800,650),("MiniBoss",1100,900)]:
        entities.append(make_entity("Enemy", x, y, [make_field("kind", "LocalEnum.EnemyKind", kind)]))
    for kind, x, y, val in [("SoulOrb",300,250,200),("SoulOrb",600,350,300),
                             ("EstusShard",700,700,0),("PurpleMoss",850,650,0),
                             ("SoulOrb",1200,550,500),("HomewardBone",1350,600,0),
                             ("SoulOrb",1100,850,1000)]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb": fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", x, y, fields))
    for lk, lv, ln, x, y, mimic in [
        ("SoulOrb",500,"",500,320,False),
        ("WeaponDrop",0,"Uchigatana",800,700,False),
        ("ArmorDrop",0,"Knight Armor",1500,350,True),
        ("WeaponDrop",0,"GreatAxe",1100,950,False),
    ]:
        entities.append(make_entity("Chest", x, y, [
            make_field("loot_kind", "LocalEnum.ItemKind", lk),
            make_field("loot_value", "Int", lv), make_field("loot_name", "String", ln),
            make_field("is_mimic", "Bool", mimic),
        ]))
    for x, y, r, cr, cg, cb, intensity in [
        (400,400,250,0.9,0.8,0.6,0.4),(600,300,200,0.5,0.5,0.8,0.2),
        (1000,350,150,0.5,0.5,0.8,0.15),(1400,300,200,0.5,0.5,0.8,0.2),
        (1100,650,180,0.9,0.6,0.3,0.15),(1300,1000,250,0.8,0.2,0.4,0.25)]:
        entities.append(make_entity("Light", x, y, [
            make_field("radius", "Float", r),
            make_field("r", "Float", cr), make_field("g", "Float", cg), make_field("b", "Float", cb),
            make_field("intensity", "Float", intensity),
        ]))
    for da, dx, dy, x, y, w, h in [
        ("FirelinkShrine",380,600,80,320,64,80),
        ("Irithyll",200,200,1550,300,64,80),
        ("CathedralDeep",1280,1040,1280,856,128,32)]:
        entities.append(make_entity("FogGate", x, y, [
            make_field("dest_area", "String", da),
            make_field("dest_x", "Float", dx), make_field("dest_y", "Float", dy),
            make_field("width", "Float", w), make_field("height", "Float", h),
        ]))

    return chunk, entities

def make_irithyll():
    chunk = new_chunk()
    for y in range(5, 20):
        for x in range(5, 40): chunk[y][x] = TILE_GROUND
    for y in range(20, 30):
        for x in range(15, 50): chunk[y][x] = TILE_GROUND
    for y in range(30, 55):
        for x in range(5, 45): chunk[y][x] = TILE_GROUND
    for y in range(35, 45):
        for x in range(45, 70): chunk[y][x] = TILE_GROUND
    for y in range(45, 75):
        for x in range(50, 90): chunk[y][x] = TILE_GROUND
    for y in range(75, 85):
        for x in range(40, 80): chunk[y][x] = TILE_GROUND
    for y in range(90, 110):
        for x in range(40, 80): chunk[y][x] = TILE_GROUND
    for x in range(40, 52): chunk[89][x] = TILE_WALL
    for x in range(62, 80): chunk[89][x] = TILE_WALL
    for x in range(40, 80): chunk[110][x] = TILE_WALL
    for y in range(89, 111): chunk[y][39] = TILE_WALL
    for y in range(89, 111): chunk[y][80] = TILE_WALL
    for y in range(55, 65):
        for x in range(10, 20): chunk[y][x] = TILE_POISON
    for y in range(60, 68):
        for x in range(75, 85): chunk[y][x] = TILE_POISON

    entities = []
    entities.append(make_entity("PlayerSpawn", 200, 200, [make_field("heal", "Bool", False)]))
    entities.append(make_entity("Bonfire", 200, 200))
    entities.append(make_entity("BossSpawn", 960, 1600))
    for kind, x, y in [("HollowSoldier",300,150),("Archer",450,200),("HollowSoldier",350,350),
                       ("Assassin",200,500),("DarkMage",600,450),("Knight",500,600),
                       ("Assassin",700,550),("HollowSoldier",650,700),("Archer",800,650),
                       ("Knight",850,800),("DarkMage",850,900),("HollowSoldier",900,1000),
                       ("Knight",950,1100)]:
        entities.append(make_entity("Enemy", x, y, [make_field("kind", "LocalEnum.EnemyKind", kind)]))
    for kind, x, y, val in [("SoulOrb",250,300,300),("HomewardBone",350,400,0),
                             ("EstusShard",500,500,0),("SoulOrb",300,600,200),
                             ("PurpleMoss",200,750,0),("SoulOrb",700,650,500),
                             ("PurpleMoss",900,750,0),("SoulOrb",1050,900,800),
                             ("SoulOrb",850,1050,1500),("EstusShard",700,1250,0)]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb": fields.append(make_field("value", "Int", val))
        entities.append(make_entity("Item", x, y, fields))
    for lk, lv, ln, x, y, mimic in [
        ("ArmorDrop",0,"Knight Armor",300,450,False),
        ("WeaponDrop",0,"Spear",650,600,False),
        ("RingDrop",0,"Chloranthy Ring",850,850,False),
        ("ArmorDrop",0,"Knight Helm",900,1100,True),
        ("WeaponDrop",0,"Uchigatana",1000,1250,False),
    ]:
        entities.append(make_entity("Chest", x, y, [
            make_field("loot_kind", "LocalEnum.ItemKind", lk),
            make_field("loot_value", "Int", lv), make_field("loot_name", "String", ln),
            make_field("is_mimic", "Bool", mimic),
        ]))
    for x, y, r, cr, cg, cb, intensity in [
        (200,200,200,0.6,0.6,0.7,0.3),(350,200,120,0.4,0.3,0.7,0.15),
        (400,350,150,0.9,0.6,0.3,0.15),(600,500,180,0.9,0.6,0.3,0.15),
        (750,700,180,0.9,0.6,0.3,0.15),(900,900,200,0.7,0.4,0.8,0.2),
        (1000,1100,180,0.5,0.5,0.6,0.15),(800,1350,220,0.3,0.3,0.8,0.25)]:
        entities.append(make_entity("Light", x, y, [
            make_field("radius", "Float", r),
            make_field("r", "Float", cr), make_field("g", "Float", cg), make_field("b", "Float", cb),
            make_field("intensity", "Float", intensity),
        ]))
    for da, dx, dy, x, y, w, h in [
        ("CathedralDeep",1700,400,80,100,64,80),
        ("Irithyll",912,1520,912,1416,128,32)]:
        entities.append(make_entity("FogGate", x, y, [
            make_field("dest_area", "String", da),
            make_field("dest_x", "Float", dx), make_field("dest_y", "Float", dy),
            make_field("width", "Float", w), make_field("height", "Float", h),
        ]))

    return chunk, entities

def make_level(identifier, chunk, entities, uid):
    return {
        "__header__": {
            "fileType": "LDtk Project JSON",
            "app": "LDtk",
            "doc": "https://ldtk.io/json",
            "schema": "https://ldtk.io/files/JSON_SCHEMA.json",
            "appAuthor": "Sebastien 'deepnight' Benard",
            "appVersion": "1.5.3",
            "url": "https://ldtk.io",
        },
        "__bgColor": "#1a1a2e",
        "__neighbours": [],
        "__smartColor": "#4a3728",
        "__bgPos": None,
        "bgColor": "#1a1a2e",
        "bgPivotX": 0.5, "bgPivotY": 0.5,
        "bgPos": None,
        "bgRelPath": None,
        "externalRelPath": None,
        "fieldInstances": [],
        "identifier": identifier,
        "iid": str(uuid.uuid4()),
        "layerInstances": [
            {
                "__cHei": CHUNK_SIZE, "__cWid": CHUNK_SIZE,
                "__gridSize": 16,
                "__identifier": "Terrain",
                "__opacity": 1,
                "__pxTotalOffsetX": 0, "__pxTotalOffsetY": 0,
                "__tilesetDefUid": None, "__tilesetRelPath": None,
                "__type": "IntGrid",
                "autoLayerTiles": [],
                "entityInstances": [],
                "gridTiles": [],
                "iid": str(uuid.uuid4()),
                "intGridCsv": chunk_to_csv(chunk),
                "layerDefUid": 1,
                "levelId": uid,
                "optionalRules": [],
                "overrideTilesetUid": None,
                "pxOffsetX": 0, "pxOffsetY": 0,
                "seed": 0,
                "visible": True,
            },
            {
                "__cHei": CHUNK_SIZE, "__cWid": CHUNK_SIZE,
                "__gridSize": 16,
                "__identifier": "Entities",
                "__opacity": 1,
                "__pxTotalOffsetX": 0, "__pxTotalOffsetY": 0,
                "__tilesetDefUid": None, "__tilesetRelPath": None,
                "__type": "Entities",
                "autoLayerTiles": [],
                "entityInstances": entities,
                "gridTiles": [],
                "iid": str(uuid.uuid4()),
                "intGridCsv": [],
                "layerDefUid": 2,
                "levelId": uid,
                "optionalRules": [],
                "overrideTilesetUid": None,
                "pxOffsetX": 0, "pxOffsetY": 0,
                "seed": 0,
                "visible": True,
            },
        ],
        "pxHei": CHUNK_SIZE * 16,
        "pxWid": CHUNK_SIZE * 16,
        "uid": uid,
        "useAutoIdentifier": True,
        "worldDepth": 0,
        "worldX": 0,
        "worldY": 0,
    }

AREAS = [
    ("CemeteryOfAsh", make_cemetery),
    ("FirelinkShrine", make_firelink),
    ("LothricWall", make_lothric_wall),
    ("UndeadSettlement", make_undead_settlement),
    ("CathedralDeep", make_cathedral_deep),
    ("Irithyll", make_irithyll),
]

def build_enum_defs():
    return [
        make_enum("EnemyKind", ENUM_UIDS["EnemyKind"], [
            {"id": "HollowSoldier", "color": 0xB08D57},
            {"id": "Archer", "color": 0x8C6239},
            {"id": "Knight", "color": 0x7F8C8D},
            {"id": "MiniBoss", "color": 0xC0392B},
            {"id": "Assassin", "color": 0x34495E},
            {"id": "DarkMage", "color": 0x6C3483},
            {"id": "CrystalLizard", "color": 0x48C9B0},
        ]),
        make_enum("ItemKind", ENUM_UIDS["ItemKind"], [
            {"id": "SoulOrb", "color": 0xF4D03F},
            {"id": "EstusShard", "color": 0xE67E22},
            {"id": "HomewardBone", "color": 0xD7DBDD},
            {"id": "PurpleMoss", "color": 0x27AE60},
            {"id": "WeaponDrop", "color": 0x95A5A6},
            {"id": "ArmorDrop", "color": 0x5D6D7E},
            {"id": "RingDrop", "color": 0xF1C40F},
        ]),
        make_enum("NpcKind", ENUM_UIDS["NpcKind"], [
            {"id": "LevelUp", "color": 0x2ECC71},
            {"id": "Merchant", "color": 0xF1C40F},
            {"id": "Blacksmith", "color": 0xD35400},
            {"id": "Dialogue", "color": 0x5DADE2},
        ]),
        make_enum("TileKind", ENUM_UIDS["TileKind"], [
            {"id": "Empty", "color": 0x000000},
            {"id": "Ground", "color": 0x4A3728},
            {"id": "Wall", "color": 0x1A1A2E},
            {"id": "WallTop", "color": 0x16213E},
            {"id": "Poison", "color": 0x2D6A4F},
        ]),
    ]

def build_entity_defs():
    return [
        make_entity_def("PlayerSpawn", ENTITY_UIDS["PlayerSpawn"], color="#7FDBFF", field_defs=[
            make_field_def("heal", "Bool", FIELD_UIDS["PlayerSpawn.heal"], False, "F_Bool", "Heal player to full on spawn."),
        ]),
        make_entity_def("BossSpawn", ENTITY_UIDS["BossSpawn"], color="#FF4136"),
        make_entity_def("Bonfire", ENTITY_UIDS["Bonfire"], color="#FF851B"),
        make_entity_def("Enemy", ENTITY_UIDS["Enemy"], color="#B08D57", field_defs=[
            make_field_def("kind", "LocalEnum.EnemyKind", FIELD_UIDS["Enemy.kind"], "HollowSoldier", f"F_Enum({ENUM_UIDS['EnemyKind']})"),
        ]),
        make_entity_def("Item", ENTITY_UIDS["Item"], color="#F4D03F", field_defs=[
            make_field_def("kind", "LocalEnum.ItemKind", FIELD_UIDS["Item.kind"], "SoulOrb", f"F_Enum({ENUM_UIDS['ItemKind']})"),
            make_field_def("value", "Int", FIELD_UIDS["Item.value"], 100, "F_Int"),
            make_field_def("name", "String", FIELD_UIDS["Item.name"], "", "F_String"),
        ]),
        make_entity_def("Chest", ENTITY_UIDS["Chest"], color="#8E6E53", field_defs=[
            make_field_def("loot_kind", "LocalEnum.ItemKind", FIELD_UIDS["Chest.loot_kind"], "SoulOrb", f"F_Enum({ENUM_UIDS['ItemKind']})"),
            make_field_def("loot_value", "Int", FIELD_UIDS["Chest.loot_value"], 100, "F_Int"),
            make_field_def("loot_name", "String", FIELD_UIDS["Chest.loot_name"], "", "F_String"),
            make_field_def("is_mimic", "Bool", FIELD_UIDS["Chest.is_mimic"], False, "F_Bool"),
            make_field_def("slot", "String", FIELD_UIDS["Chest.slot"], "", "F_String"),
        ]),
        make_entity_def("Npc", ENTITY_UIDS["Npc"], color="#33E6B3", field_defs=[
            make_field_def("name", "String", FIELD_UIDS["Npc.name"], "", "F_String"),
            make_field_def("kind", "LocalEnum.NpcKind", FIELD_UIDS["Npc.kind"], "Dialogue", f"F_Enum({ENUM_UIDS['NpcKind']})"),
            make_field_def("color", "Color", FIELD_UIDS["Npc.color"], "#FFFFFF", "F_Color"),
            make_field_def("dialogue", "String", FIELD_UIDS["Npc.dialogue"], "", "F_String"),
        ]),
        make_entity_def("Light", ENTITY_UIDS["Light"], color="#FFF3B0", field_defs=[
            make_field_def("radius", "Float", FIELD_UIDS["Light.radius"], 160.0, "F_Float"),
            make_field_def("r", "Float", FIELD_UIDS["Light.r"], 1.0, "F_Float"),
            make_field_def("g", "Float", FIELD_UIDS["Light.g"], 1.0, "F_Float"),
            make_field_def("b", "Float", FIELD_UIDS["Light.b"], 1.0, "F_Float"),
            make_field_def("intensity", "Float", FIELD_UIDS["Light.intensity"], 0.2, "F_Float"),
        ]),
        make_entity_def("FogGate", ENTITY_UIDS["FogGate"], width=64, height=32, resizable_x=True, resizable_y=True, color="#D4AF37", field_defs=[
            make_field_def("dest_area", "String", FIELD_UIDS["FogGate.dest_area"], "", "F_String"),
            make_field_def("dest_x", "Float", FIELD_UIDS["FogGate.dest_x"], 0.0, "F_Float"),
            make_field_def("dest_y", "Float", FIELD_UIDS["FogGate.dest_y"], 0.0, "F_Float"),
            make_field_def("width", "Float", FIELD_UIDS["FogGate.width"], 64.0, "F_Float"),
            make_field_def("height", "Float", FIELD_UIDS["FogGate.height"], 32.0, "F_Float"),
        ]),
        make_entity_def("TilePatch", ENTITY_UIDS["TilePatch"], color="#2ECC71", field_defs=[
            make_field_def("tile", "LocalEnum.TileKind", FIELD_UIDS["TilePatch.tile"], "Ground", f"F_Enum({ENUM_UIDS['TileKind']})"),
            make_field_def("x1", "Int", FIELD_UIDS["TilePatch.x1"], 0, "F_Int"),
            make_field_def("y1", "Int", FIELD_UIDS["TilePatch.y1"], 0, "F_Int"),
            make_field_def("x2", "Int", FIELD_UIDS["TilePatch.x2"], 0, "F_Int"),
            make_field_def("y2", "Int", FIELD_UIDS["TilePatch.y2"], 0, "F_Int"),
            make_field_def("condition", "String", FIELD_UIDS["TilePatch.condition"], "always", "F_String"),
        ]),
    ]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    levels_dir = os.path.join(script_dir, "ds2d")
    os.makedirs(levels_dir, exist_ok=True)

    level_summaries = []
    for uid, (identifier, gen_fn) in enumerate(AREAS, start=1):
        chunk, entities = gen_fn()
        populate_entity_def_uids(entities)
        level = make_level(identifier, chunk, entities, uid)
        level_path = os.path.join(levels_dir, f"{identifier}.ldtkl")
        with open(level_path, "w") as f:
            json.dump(level, f, indent=2)
        print(f"  wrote {level_path}")
        level_summaries.append({
            "__bgColor": level["__bgColor"],
            "__neighbours": [],
            "__smartColor": level["__smartColor"],
            "__bgPos": None,
            "bgColor": None,
            "bgPivotX": 0.5, "bgPivotY": 0.5,
            "bgPos": None,
            "bgRelPath": None,
            "externalRelPath": f"ds2d/{identifier}.ldtkl",
            "fieldInstances": [],
            "identifier": identifier,
            "iid": level["iid"],
            "layerInstances": None,
            "pxHei": level["pxHei"],
            "pxWid": level["pxWid"],
            "uid": uid,
            "useAutoIdentifier": True,
            "worldDepth": 0,
            "worldX": -1,
            "worldY": -1,
        })

    # Generate project file
    project = {
        "__header__": {
            "fileType": "LDtk Project JSON",
            "app": "LDtk",
            "doc": "https://ldtk.io/json",
            "schema": "https://ldtk.io/files/JSON_SCHEMA.json",
            "appAuthor": "Sebastien 'deepnight' Benard",
            "appVersion": "1.5.3",
            "url": "https://ldtk.io",
        },
        "__FORCED_REFS": None,
        "appBuildId": 473703,
        "backupLimit": 10,
        "backupOnSave": False,
        "backupRelPath": None,
        "bgColor": "#1a1a2e",
        "customCommands": [],
        "defaultEntityHeight": 16,
        "defaultEntityWidth": 16,
        "defaultGridSize": 16,
        "defaultLevelBgColor": "#1a1a2e",
        "defaultLevelHeight": CHUNK_SIZE * 16,
        "defaultLevelWidth": CHUNK_SIZE * 16,
        "defaultPivotX": 0,
        "defaultPivotY": 0,
        "defs": {
            "entities": build_entity_defs(),
            "enums": build_enum_defs(),
            "externalEnums": [],
            "layers": [
                {
                    "__type": "IntGrid",
                    "autoRuleGroups": [], "autoSourceLayerDefUid": None,
                    "autoTilesetDefUid": None, "autoTilesKilledByOtherLayerUid": None,
                    "biomeFieldUid": None, "canSelectWhenInactive": True,
                    "displayOpacity": 1.0, "doc": None,
                    "excludedTags": [], "gridSize": 16,
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
                    "intGridValuesGroups": [],
                    "parallaxFactorX": 0, "parallaxFactorY": 0,
                    "parallaxScaling": True, "pxOffsetX": 0, "pxOffsetY": 0,
                    "renderInWorldView": True, "requiredTags": [],
                    "tilePivotX": 0, "tilePivotY": 0,
                    "tilesetDefUid": None,
                    "type": "IntGrid",
                    "uiColor": None, "uid": 1,
                    "uiFilterTags": [], "useAsyncRender": False,
                },
                {
                    "__type": "Entities",
                    "autoRuleGroups": [], "autoSourceLayerDefUid": None,
                    "autoTilesetDefUid": None, "autoTilesKilledByOtherLayerUid": None,
                    "biomeFieldUid": None, "canSelectWhenInactive": True,
                    "displayOpacity": 1.0, "doc": None,
                    "excludedTags": [], "gridSize": 16,
                    "guideGridHei": 0, "guideGridWid": 0,
                    "hideFieldsWhenInactive": False, "hideInList": False,
                    "identifier": "Entities", "inactiveOpacity": 0.3,
                    "intGridValues": [], "intGridValuesGroups": [],
                    "parallaxFactorX": 0, "parallaxFactorY": 0,
                    "parallaxScaling": True, "pxOffsetX": 0, "pxOffsetY": 0,
                    "renderInWorldView": True, "requiredTags": [],
                    "tilePivotX": 0, "tilePivotY": 0,
                    "tilesetDefUid": None,
                    "type": "Entities",
                    "uiColor": None, "uid": 2,
                    "uiFilterTags": [], "useAsyncRender": False,
                },
            ],
            "levelFields": [],
            "tilesets": [],
        },
        "dummyWorldIid": str(uuid.uuid4()),
        "exportLevelBg": False,
        "exportPng": None,
        "exportTiled": False,
        "externalLevels": True,
        "flags": [],
        "identifierStyle": "Free",
        "iid": str(uuid.uuid4()),
        "imageExportMode": "None",
        "jsonVersion": "1.5.3",
        "levelNamePattern": "%world_Level_%idx",
        "levels": level_summaries,
        "minifyJson": False,
        "nextUid": 1000,
        "pngFilePattern": None,
        "simplifiedExport": False,
        "toc": [],
        "tutorialDesc": "Generated DS2D project with separate level files.",
        "worldGridHeight": CHUNK_SIZE * 16,
        "worldGridWidth": CHUNK_SIZE * 16,
        "worldLayout": "Free",
        "worlds": [],
    }

    project_path = os.path.join(script_dir, "ds2d.ldtk")
    with open(project_path, "w") as f:
        json.dump(project, f, indent=2)
    print(f"  wrote {project_path}")

if __name__ == "__main__":
    main()
