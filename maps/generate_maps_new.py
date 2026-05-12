#!/usr/bin/env python3
"""Generate LDtk .ldtkl level files from the tile layouts defined in wasm_entry.rs."""
import json
import os
import uuid

CHUNK_SIZE = 160
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_WALL = 2
TILE_WALLTOP = 3
TILE_POISON = 4
LEVEL_UIDS = {
    "CemeteryOfAsh": 1,
    "LothricWall": 3,
    "UndeadSettlement": 4,
    "CathedralDeep": 5,
    "Irithyll": 6,
    "RoadOfSacrifices": 7,
    "FarronKeep": 8,
    "CatacombsOfCarthus": 9,
    "SmoulderingLake": 10,
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
    "Npc.appear_condition": 331,
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

# DS3 NPC appearance conditions — empty string = always available
# Format: "boss:BossName" = requires that boss defeated
NPC_CONDITIONS = {
    # FirelinkShrine — core NPCs always present
    '防火女': '',
    '铁匠安德烈': '',
    '祭祀场侍女': '',
    '脱逃者霍克伍德': '',
    '库尔兰的鲁德雷斯': '',
    # FirelinkShrine — progression-gated
    '小偷格雷瑞特': 'boss:Vordt',
    '大沼的柯尔尼克斯': 'boss:Vordt',
    '隆道尔的尤艾尔': 'boss:Vordt',
    '卡里姆的伊莉娜': 'boss:CrystalSage',
    '卡里姆的伊贡': 'boss:CrystalSage',
    '阿斯托拉的安里': 'boss:CrystalSage',
    '沉默的霍拉斯': 'boss:CrystalSage',
    '指头的列奥纳德': 'boss:AbyssWatchers',
    '维恩海姆的奥贝克': 'boss:CrystalSage',
    '啾啾·嘭嘭乌鸦': 'boss:Vordt',
    '啾啾乌鸦': 'boss:Vordt',
    '无火的太阳骑士希里斯': 'boss:CrystalSage',
    '不屈不挠的帕奇': 'boss:DeaconsOfTheDeep',
    '隆道尔的尤莉亚': 'boss:AbyssWatchers',
    '卡菈': 'boss:OldDemonKing',
    # Other area NPCs — progression-gated
    '罗莎莉亚': 'boss:DeaconsOfTheDeep',
    '卡塔利纳的杰克巴尔多': 'boss:Vordt',
    '杰克塔尔的洋葱骑士': 'boss:Vordt',
    '艾玛': 'boss:Vordt',
    '葛雷瑞特': '',
    '骑士团团长幽儿希卡': 'boss:PontiffSulyvahn',
    '骑士杀手崔索格': 'boss:AbyssWatchers',
    '法兰的老狼': 'boss:AbyssWatchers',
    # Variant NPC names used across different maps
    '商人': '',
    '杰克巴尔多': '',
    '不屈不挠的帕奇斯': 'boss:DeaconsOfTheDeep',
    '无光之地的希里斯': 'boss:CrystalSage',
    '沉默的霍雷斯': 'boss:Vordt',
    '彼海姆的欧贝克': 'boss:CrystalSage',
    '老狼法兰': 'boss:AbyssWatchers',
    '亚斯特拉的安里': 'boss:Vordt',
    '指环指·雷奥纳德': 'boss:AbyssWatchers',
    '隆德尔的苍白影子': 'boss:AbyssWatchers',
    '隆德尔的尤莉娅': 'boss:AbyssWatchers',
    '青教誓约': '',
    '霍克伍德': '',
    '霍拉斯': '',
    '骑士杀手崔索格': 'boss:AbyssWatchers',
    '卡露菈': 'boss:OldDemonKing',
    '祭祀场侍女（暗之版本）': '',
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


# ---- Enemy kind mapping: design doc name → Rust EnemyKind ----
ENEMY_KIND_MAP = {
    "HollowSoldier": "HollowSoldier", "HollowAssassin": "Assassin",
    "Assassin": "Assassin", "StarvedHound": "StarvedHound",
    "CrystalLizard": "CrystalLizard", "RavenousCrystalLizard": "CrystalLizard",
    "LothricKnight": "LothricKnight", "LothricPriest": "Deacon",
    "WingedKnight": "WingedKnight", "PusOfMan": "PusOfMan",
    "Darkwraith": "Darkwraith", "Evangelist": "Evangelist",
    "CathedralEvangelist": "Evangelist", "Thrall": "Thrall",
    "HollowThrall": "Thrall", "SilverKnight": "SilverKnight",
    "SilverKnightSword": "SilverKnight", "SilverKnightSpear": "SilverKnight",
    "SilverKnightRedEyed": "SilverKnight", "BlackKnight": "BlackKnight",
    "DeepAccursed": "DeepAccursed", "Deacon": "Deacon",
    "DeaconOfTheDeep": "Deacon", "Ghru": "Ghru", "ElderGhru": "Ghru",
    "Ghrus": "Ghru", "GhruConjurer": "DarkMage",
    "Skeleton": "Skeleton", "GraveWardenSkeleton": "Skeleton",
    "CarthusSkeleton": "Skeleton", "CarthusSwordsman": "Skeleton",
    "SkeletonSwordsman": "Skeleton", "SkeletonWheel": "Skeleton",
    "Jailer": "Jailer", "JailerHandmaid": "Jailer",
    "SerpentMan": "SerpentMan", "ManSerpent": "SerpentMan",
    "SerpentManSummoner": "DarkMage", "FireDemon": "FireDemon",
    "DemonCleric": "FireDemon", "Demon": "FireDemon",
    "CathedralKnight": "CathedralKnight", "ConsumedKingsKnight": "CathedralKnight",
    "ManGrub": "ManGrub", "Gargoyle": "Gargoyle",
    "Dog": "Dog", "HoundRat": "Dog", "Rat": "Dog",
    "GiantRat": "Dog", "GiantHoundRat": "Dog",
    "Basilisk": "Basilisk", "DemonStatue": "DemonStatue",
    "InfestedCorpse": "InfestedCorpse", "ReanimatedCorpse": "InfestedCorpse",
    "Wretch": "Wretch", "PeasantHollow": "PeasantHollow",
    "HollowSlave": "PeasantHollow", "DevoutHollow": "PeasantHollow",
    "Mimic": "Mimic", "PontiffKnight": "Knight",
    "FireWitch": "DarkMage", "IrithyllSlave": "Thrall",
    "IrithyllianBeasthound": "StarvedHound",
    "SewerCentipede": "DarkMage", "SulyvahnsBeast": "MiniBoss",
    "GiantSlave": "MiniBoss", "GiantCaptive": "MiniBoss",
    "AncientWyvernSecond": "MiniBoss", "StrayDemon": "MiniBoss",
    "LargeHollowSoldier": "Knight", "CarthusArcher": "Archer",
    "SwordMaster": "Assassin", "HavelNPC": "Knight",
    "DrakebloodKnight": "Knight", "BorealKnight": "Knight",
    "BorealOutriderKnight": "WingedKnight", "Alva": "Assassin",
    "Hodrick": "Knight", "LongfingerKirk": "Assassin",
    "KnightSlayerTsorig": "Knight", "RicardNPC": "Assassin",
    "YellowfingerHeysel": "Assassin", "AvariciousBeing": "MiniBoss",
    "CageSpider": "DarkMage", "CagedHollow": "PeasantHollow",
    "CarthusSandworm": "MiniBoss", "CathedralGraveWarden": "Skeleton",
    "ClawedCurse": "DarkMage", "CorpseGrub": "InfestedCorpse",
    "Corvian": "Assassin", "CorvianStoryteller": "DarkMage",
    "CourtSorcerer": "DarkMage", "CrystalSage": "DarkMage",
    "ExileWatchman": "Knight", "GreatCrab": "MiniBoss",
    "LesserCrab": "Dog", "Lycanthrope": "StarvedHound",
    "MonstrosityOfSin": "MiniBoss", "PoisonhornBug": "Dog",
    "ScholarMage": "DarkMage", "SmoulderingGhru": "Ghru",
    "SmolderingRottenFlesh": "InfestedCorpse", "WrithingRottenFlesh": "InfestedCorpse",
    "RottenSlug": "InfestedCorpse", "Wildwoman": "Assassin",
    "AscendedWingedKnight": "WingedKnight",
    "LothricWyvern": "MiniBoss", "SkeletonBall": "MiniBoss",
    "PrayingHollowSoldier": "HollowSoldier",
    "LargeHoundRat": "Dog", "LargeClub": "MiniBoss",
}

# ---- Item kind mapping: design doc kind → (Rust ItemKind, name_field) ----
ITEM_KIND_MAP = {
    "SoulOrb": ("SoulOrb", "value"), "SoulItem": ("SoulOrb", "value"),
    "NamedSoul": ("SoulOrb", "value"), "FadingSoul": ("SoulOrb", "value"),
    "BossSoul": ("SoulOrb", "value"), "SoulDrop": ("SoulOrb", "value"),
    "LargeSoulOrb": ("SoulOrb", "value"), "LargeSoulOfDesertedCorpse": ("SoulOrb", "value"),
    "SoulOfUnknownTraveler": ("SoulOrb", "value"), "SoulOfRottedGreatwood": ("SoulOrb", "value"),
    "AbyssWatchersSoul": ("SoulOrb", "value"),
    "EstusShard": ("EstusShard", None), "EstusFlask": ("Consumable", "name"),
    "EstusUpgrade": ("Consumable", "name"), "AshenEstusFlask": ("Consumable", "name"),
    "BoneShard": ("Consumable", "name"), "UndeadBoneShard": ("UndeadBoneShard", None),
    "HomewardBone": ("HomewardBone", None),
    "PurpleMoss": ("PurpleMoss", None),
    "Firebomb": ("Firebomb", None), "BlackFirebomb": ("Firebomb", None),
    "Ember": ("Ember", None),
    "TitaniteShard": ("TitaniteShard", None), "LargeTitaniteShard": ("TitaniteShard", None),
    "TitaniteChunk": ("TitaniteShard", None), "TitaniteScale": ("Consumable", "name"),
    "TwinklingTitanite": ("TitaniteShard", None),
    "CoiledSword": ("WeaponDrop", "name"), "CoiledSwordFragment": ("Consumable", "name"),
    "WeaponDrop": ("WeaponDrop", "name"), "Weapon": ("WeaponDrop", "name"),
    "ArmorDrop": ("ArmorDrop", "name"), "Armor": ("ArmorDrop", "name"),
    "RingDrop": ("RingDrop", "name"), "Ring": ("RingDrop", "name"),
    "Consumable": ("Consumable", "name"), "ItemDrop": ("Consumable", "name"),
    "KeyItem": ("Consumable", "name"), "KeyDrop": ("Consumable", "name"),
    "ThrowingKnife": ("Consumable", "name"), "AlluringSkull": ("Consumable", "name"),
    "DungPie": ("Consumable", "name"), "PurgingStone": ("Consumable", "name"),
    "RustedCoin": ("Consumable", "name"), "RepairPowder": ("Consumable", "name"),
    "CharcoalPineResin": ("Consumable", "name"), "CharcoalPineBundle": ("Consumable", "name"),
    "HumanPineResin": ("Consumable", "name"), "PalePineResin": ("Consumable", "name"),
    "GoldPineResin": ("Consumable", "name"),
    "FireGem": ("Consumable", "name"), "DarkGem": ("Consumable", "name"),
    "ChaosGem": ("Consumable", "name"), "PoisonGem": ("Consumable", "name"),
    "RefinedGem": ("Consumable", "name"), "GemDrop": ("Consumable", "name"),
    "CoalDrop": ("Consumable", "name"), "Ore": ("TitaniteShard", None),
    "UpgradeMaterial": ("TitaniteShard", None),
    "TomeDrop": ("Consumable", "name"), "SpellDrop": ("Consumable", "name"),
    "TalismanDrop": ("Consumable", "name"), "GestureDrop": ("Consumable", "name"),
    "ShieldDrop": ("WeaponDrop", "name"), "Shield": ("WeaponDrop", "name"),
    "DragonStone": ("Consumable", "name"),
    "TransposingKiln": ("Consumable", "name"),
    "Siegbrau": ("Consumable", "name"), "LorettaBone": ("Consumable", "name"),
    "DreamchaserAshes": ("Consumable", "name"), "MorticianAshes": ("Consumable", "name"),
    "PaleTongue": ("Consumable", "name"), "VertebraShackle": ("Consumable", "name"),
    "WolfBloodSwordgrass": ("Consumable", "name"),
    "WarriorOfSunlight": ("Consumable", "name"),
    "RedBugPellet": ("Consumable", "name"), "YellowBugPellet": ("Consumable", "name"),
    "WhiteWax": ("Consumable", "name"), "YoungWhiteBranch": ("Consumable", "name"),
    "ShrivingStone": ("Consumable", "name"),
    "RingOfSacrifice": ("RingDrop", "name"),
    "BloodbiteRing": ("RingDrop", "name"), "ChloranthyRing": ("RingDrop", "name"),
    "HawkRing": ("RingDrop", "name"), "FlynnRing": ("RingDrop", "name"),
    "FireClutchRing": ("RingDrop", "name"),
    "FlameStoneplateRing": ("RingDrop", "name"),
    "DragonscaleRing": ("RingDrop", "name"),
    "DarkmoonRing": ("RingDrop", "name"),
    "LifeRingPlus1": ("RingDrop", "name"),
    "WolfKnightGreatsword": ("WeaponDrop", "name"),
    "GreatScythe": ("WeaponDrop", "name"), "HandAxe": ("WeaponDrop", "name"),
    "Whip": ("WeaponDrop", "name"), "Claw": ("WeaponDrop", "name"),
    "Dagger": ("WeaponDrop", "name"), "Partizan": ("WeaponDrop", "name"),
    "LargeClub": ("WeaponDrop", "name"),
    "IrithyllStraightSword": ("WeaponDrop", "name"),
    "Ammo": ("Consumable", "name"),
    "ClericSet": ("ArmorDrop", "name"), "NorthernSet": ("ArmorDrop", "name"),
    "MirrahSet": ("ArmorDrop", "name"), "DrakebloodSet": ("ArmorDrop", "name"),
    "ShadowSet": ("ArmorDrop", "name"), "Loincloth": ("Consumable", "name"),
    "SaintsTalisman": ("Consumable", "name"),
    "BlessedRedWhiteShield": ("Consumable", "name"),
    "BlueWoodenShield": ("Consumable", "name"), "CaduceusRoundShield": ("Consumable", "name"),
    "SmallLeatherShield": ("Consumable", "name"), "PlankShield": ("Consumable", "name"),
    "WargodWoodenShield": ("Consumable", "name"),
    "EnemyDrop": ("Consumable", "name"),
}

# ---- Boss type mapping ----
BOSS_TYPE_MAP = {
    "IudexGundyr": "IudexGundyr", "Vordt": "Vordt",
    "CurseRottedGreatwood": "CurseRottedGreatwood", "CrystalSage": "CrystalSage",
    "AbyssWatchers": "AbyssWatchers", "Wolnir": "HighLordWolnir",
    "OldDemonKing": "OldDemonKing", "DeaconsOfTheDeep": "DeaconsOfTheDeep",
    "PontiffSulyvahn": "PontiffSulyvahn", "YhormTheGiant": "Yhorm",
    "AldrichDevourerOfGods": "Aldrich", "DragonslayerArmour": "DragonslayerArmour",
    "TwinPrinces": "TwinPrinces", "SoulOfCinder": "SoulOfCinder",
    "OceirosTheConsumedKing": "Oceiros", "ChampionGundyr": "ChampionGundyr",
    "AncientWyvern": "NamelessKing", "NamelessKing": "NamelessKing",
    "DancerOfTheBorealValley": "Dancer",
}

# ---- NPC kind mapping ----
NPC_KIND_MAP = {
    "LevelUp": "LevelUp", "Merchant": "Merchant",
    "Blacksmith": "Blacksmith", "Dialogue": "Dialogue",
    "Covenant": "Dialogue", "Summon": "Dialogue",
    "Event": "Dialogue", "Invader": "Dialogue",
    "Hawkwood": "Dialogue", "Trade": "Merchant",
    "": "Dialogue",
}

# ---- NPC color table ----
NPC_COLORS = {
    "防火女": "#f0e6d0", "铁匠安德烈": "#b87333", "祭祀场侍女": "#8a7a6a",
    "脱逃者霍克伍德": "#7a8a70", "库尔兰的鲁德雷斯": "#a08060",
    "卡里姆的伊莉娜": "#d0c0e0", "隆道尔的尤艾尔": "#505050",
    "小偷格雷瑞特": "#8b4513", "大沼的柯尔尼克斯": "#daa520",
    "阿斯托拉的安里": "#b0c4de", "沉默的霍拉斯": "#696969",
    "指头的列奥纳德": "#8b0000", "维恩海姆的奥贝克": "#4169e1",
    "无火的太阳骑士希里斯": "#c0c0c0", "不屈不挠的帕奇": "#cd853f",
    "隆道尔的尤莉亚": "#1a1a2e", "卡里姆的伊贡": "#4a5568",
    "卡菈": "#2f2f4f", "啾啾·嘭嘭乌鸦": "#ffd700",
}

# ---- Data-driven map generator ----
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "maps")

def load_doc(identifier):
    path = os.path.join(DOCS_DIR, f"{identifier}.json")
    with open(path) as f:
        return json.load(f)

def tile_from_doc(doc, dx, dy):
    """Convert design doc pixel coords to tile coords, scaled to fit 160x160."""
    mw = doc["map_size"]["width"]
    mh = doc["map_size"]["height"]
    return int(dx * 2560 / mw / 16), int(dy * 2560 / mh / 16)

def pixel_from_doc(doc, dx, dy):
    """Convert design doc pixel coords to map pixel coords, scaled to fit 2560x2560."""
    mw = doc["map_size"]["width"]
    mh = doc["map_size"]["height"]
    return int(dx * 2560 / mw), int(dy * 2560 / mh)

def sections_overlap(s1, s2):
    """Check if two sections overlap in tile space."""
    return not (s1[2] < s2[0] or s2[2] < s1[0] or s1[3] < s2[1] or s2[3] < s1[1])

def generate_terrain(chunk, doc):
    """Generate terrain from design doc sections. Each section becomes ground.
    Expand sections by EXPAND tiles in each direction to fill more of the grid.
    Add walls on section borders that don't overlap with neighbors."""
    mw = doc["map_size"]["width"]
    mh = doc["map_size"]["height"]
    sx, sy = 2560.0 / mw, 2560.0 / mh

    secs = doc.get("map_layout", {}).get("sections", [])
    # Convert to tile rects: (tx1, ty1, tx2, ty2)
    tile_secs = []
    for s in secs:
        tx1 = max(0, int(s["x"] * sx / 16))
        ty1 = max(0, int(s["y"] * sy / 16))
        tx2 = min(CHUNK_SIZE - 1, int((s["x"] + s["w"]) * sx / 16))
        ty2 = min(CHUNK_SIZE - 1, int((s["y"] + s["h"]) * sy / 16))
        tile_secs.append((tx1, ty1, tx2, ty2))

    # Expand each section by EXPAND tiles to fill gaps
    EXPAND = 3
    expanded = []
    for tx1, ty1, tx2, ty2 in tile_secs:
        expanded.append((max(0, tx1 - EXPAND), max(0, ty1 - EXPAND),
                         min(CHUNK_SIZE - 1, tx2 + EXPAND),
                         min(CHUNK_SIZE - 1, ty2 + EXPAND)))

    # Fill expanded sections with ground
    for tx1, ty1, tx2, ty2 in expanded:
        fill_tiles(chunk, TILE_GROUND, tx1, ty1, tx2, ty2)

    # Add corridors between non-overlapping adjacent sections
    for i in range(len(expanded)):
        for j in range(i + 1, len(expanded)):
            e1, e2 = expanded[i], expanded[j]
            if sections_overlap(e1, e2):
                continue
            # Find closest edges and carve a 4-tile wide corridor
            cx1 = (e1[0] + e1[2]) // 2
            cy1 = (e1[1] + e1[3]) // 2
            cx2 = (e2[0] + e2[2]) // 2
            cy2 = (e2[1] + e2[3]) // 2
            # L-shaped corridor
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                for dy in range(-1, 2):
                    yy = cy1 + dy
                    if 0 <= yy < CHUNK_SIZE:
                        chunk[yy][x] = TILE_GROUND
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                for dx in range(-1, 2):
                    xx = cx2 + dx
                    if 0 <= xx < CHUNK_SIZE:
                        chunk[y][xx] = TILE_GROUND

    # Add terrain features based on section tags
    for idx, s in enumerate(secs):
        features = " ".join(s.get("terrain_features", []))
        tx1, ty1, tx2, ty2 = tile_secs[idx]
        sw, sh = tx2 - tx1, ty2 - ty1
        if sw < 4 or sh < 4:
            continue

        # Poison terrain
        if any(k in features for k in ["毒沼", "深水毒沼", "沼泽", "浅毒沼", "有毒淤泥", "深渊沼泽", "毒水"]):
            # Fill inner portion with poison
            fill_tiles(chunk, TILE_POISON, tx1 + 2, ty1 + 2, tx2 - 2, ty2 - 2)

        # Lava (use poison tile as lava)
        if any(k in features for k in ["熔岩", "熔岩池", "熔岩浅滩"]):
            fill_tiles(chunk, TILE_POISON, tx1 + 3, ty1 + 3, tx2 - 3, ty2 - 3)

        # Gravestones — scatter wall dots
        if any(k in features for k in ["墓碑", "墓碑群", "坟墓群", "广阔墓地", "墓地"]):
            step = max(3, min(sw, sh) // 4)
            for y in range(ty1 + 2, ty2 - 1, step):
                for x in range(tx1 + 2, tx2 - 1, step):
                    chunk[y][x] = TILE_WALL

        # Arena — perimeter walls with gaps
        if any(k in features for k in ["竞技场", "圆形竞技场"]):
            gap_x = (tx1 + tx2) // 2
            for x in range(tx1, tx2 + 1):
                if abs(x - gap_x) > 3:
                    chunk[ty1][x] = TILE_WALL
                    chunk[ty2][x] = TILE_WALL
            gap_y = (ty1 + ty2) // 2
            for y in range(ty1, ty2 + 1):
                if abs(y - gap_y) > 3:
                    chunk[y][tx1] = TILE_WALL
                    chunk[y][tx2] = TILE_WALL

        # Buildings / narrow alleys
        if any(k in features for k in ["民房", "窄巷", "密集建筑", "密集矮房"]):
            # Add internal wall rows with gaps
            mid_y = (ty1 + ty2) // 2
            gap_x = (tx1 + tx2) // 2
            for x in range(tx1 + 1, tx2):
                if abs(x - gap_x) > 2:
                    chunk[mid_y][x] = TILE_WALL
                    if mid_y + 1 < CHUNK_SIZE:
                        chunk[mid_y + 1][x] = TILE_WALL
            mid_x = (tx1 + tx2) // 2
            gap_y = (ty1 + ty2) // 2
            for y in range(ty1 + 1, ty2):
                if abs(y - gap_y) > 2:
                    chunk[y][mid_x] = TILE_WALL

        # Church / altar — altar wall block
        if any(k in features for k in ["教堂", "祭坛", "祭坛大厅"]):
            cx = (tx1 + tx2) // 2
            fill_tiles(chunk, TILE_WALL, cx - 3, ty2 - 4, cx + 3, ty2 - 2)

        # Dungeon cells
        if any(k in features for k in ["牢房", "囚室", "铁栅牢房"]):
            step = max(5, sw // 3)
            for x in range(tx1 + step, tx2, step):
                gap_y = (ty1 + ty2) // 2
                for y in range(ty1, ty2 + 1):
                    if abs(y - gap_y) > 1:
                        chunk[y][x] = TILE_WALL

        # Bookshelves
        if any(k in features for k in ["书架", "密集书架", "巨型书架"]):
            for y in range(ty1 + 2, ty2 - 1, 3):
                for x in range(tx1 + 1, tx2):
                    chunk[y][x] = TILE_WALL

        # Crystal formations
        if any(k in features for k in ["水晶", "水晶簇", "水晶碎片"]):
            step = max(4, min(sw, sh) // 3)
            for y in range(ty1 + 2, ty2 - 1, step):
                for x in range(tx1 + 2, tx2 - 1, step):
                    fill_tiles(chunk, TILE_WALL, x, y, x + 1, y + 1)

        # Dead tree / large roots
        if any(k in features for k in ["枯树", "大树根", "巨树根"]):
            cx, cy = (tx1 + tx2) // 2, (ty1 + ty2) // 2
            fill_tiles(chunk, TILE_WALL, cx - 2, cy - 2, cx + 2, cy + 2)

        # Narrow path walls
        if any(k in features for k in ["窄路", "窄石径", "窄巷", "窄廊", "狭窄路径", "狭窄走廊", "狭窄隧道"]):
            for y in range(ty1, ty2 + 1):
                chunk[y][tx1] = TILE_WALL
                if tx1 + 1 < CHUNK_SIZE:
                    chunk[y][tx1 + 1] = TILE_WALL
                chunk[y][tx2] = TILE_WALL
                if tx2 - 1 >= 0:
                    chunk[y][tx2 - 1] = TILE_WALL

        # Castle walls / stone walls
        if any(k in features for k in ["城墙", "石墙", "残破城墙"]):
            for x in range(tx1, tx2 + 1):
                chunk[ty1][x] = TILE_WALL
                if ty1 + 1 < CHUNK_SIZE:
                    chunk[ty1 + 1][x] = TILE_WALL

        # Stairs — step pattern
        if any(k in features for k in ["阶梯", "石阶", "长阶梯", "螺旋阶梯", "上升阶梯", "下行阶梯"]):
            for i, y in enumerate(range(ty1, ty2 + 1, 2)):
                offset = (i % 2) * 2
                for x in range(tx1, tx2 + 1):
                    if (x - tx1) % 6 < 2 + offset:
                        chunk[y][x] = TILE_WALL

def generate_entities(doc, chunk):
    """Generate all entities from design doc data."""
    entities = []
    mw = doc["map_size"]["width"]
    mh = doc["map_size"]["height"]

    def px(dx, dy):
        return int(dx * 2560 / mw), int(dy * 2560 / mh)

    # Player spawn — first section origin
    secs = doc.get("map_layout", {}).get("sections", [])
    if secs:
        s0 = secs[0]
        entities.append(make_entity("PlayerSpawn", *px(s0["x"] + s0["w"]//4, s0["y"] + s0["h"]//4), [
            make_field("heal", "Bool", True),
        ]))
        # Bonfire near player spawn
        entities.append(make_entity("Bonfire", *px(s0["x"] + s0["w"]//2, s0["y"] + s0["h"]//2)))

    # Additional bonfires from design doc
    for bf in doc.get("bonfires", []):
        entities.append(make_entity("Bonfire", *px(bf["x"], bf["y"])))

    # Boss
    boss = doc.get("boss")
    if boss:
        bosses = boss if isinstance(boss, list) else [boss]
        for b in bosses:
            btype = BOSS_TYPE_MAP.get(b["type"], "IudexGundyr")
            entities.append(make_entity("BossSpawn", *px(b["x"], b["y"])))
            # Boss fog gate from arena
            arena = b.get("arena", {})
            if arena:
                ax, ay = arena.get("x", b["x"]), arena.get("y", b["y"])
                aw, ah = arena.get("w", 400), arena.get("h", 300)
                gate_px, gate_py = px(ax + aw // 2, ay)
                entities.append(make_entity("FogGate", gate_px, gate_py, [
                    make_field("dest_area", "String", doc["id"]),
                    make_field("dest_x", "Float", float(px(b["x"], b["y"])[0])),
                    make_field("dest_y", "Float", float(px(b["x"], b["y"])[1])),
                    make_field("width", "Float", float(int(aw * 2560 / mw))),
                    make_field("height", "Float", 32.0),
                ]))

    # Enemies
    for e in doc.get("enemies", []):
        kind = ENEMY_KIND_MAP.get(e["kind"], "HollowSoldier")
        count = e.get("count", 1)
        for i in range(count):
            ox = (i * 24) % 48 - 24
            oy = (i * 18) % 36 - 18
            ex, ey = px(e["x"], e["y"])
            entities.append(make_entity("Enemy", ex + ox, ey + oy, [
                make_field("kind", "LocalEnum.EnemyKind", kind),
            ]))

    # Items
    for item in doc.get("items", []):
        kind_raw = item.get("kind", "Consumable")
        mapped = ITEM_KIND_MAP.get(kind_raw, ("Consumable", "name"))
        item_kind, val_field = mapped
        fields = [make_field("kind", "LocalEnum.ItemKind", item_kind)]
        if val_field == "value" and "value" in item:
            fields.append(make_field("value", "Int", item["value"]))
        elif val_field == "name":
            name = item.get("name", kind_raw)
            fields.append(make_field("name", "String", name))
        if item_kind == "WeaponDrop":
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        if item_kind == "ArmorDrop":
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        if item_kind == "RingDrop":
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        entities.append(make_entity("Item", *px(item["x"], item["y"]), fields))

    # Chests
    for c in doc.get("chests", []):
        loot_kind_raw = c.get("loot_kind", c.get("kind", "Consumable"))
        mapped = ITEM_KIND_MAP.get(loot_kind_raw, ("Consumable", "name"))
        loot_kind, _ = mapped
        entities.append(make_entity("Chest", *px(c["x"], c["y"]), [
            make_field("loot_kind", "LocalEnum.ItemKind", loot_kind),
            make_field("loot_value", "Int", c.get("loot_value", c.get("value", 0))),
            make_field("loot_name", "String", c.get("loot_name", c.get("name", ""))),
            make_field("is_mimic", "Bool", c.get("is_mimic", False)),
        ]))

    # NPCs
    for n in doc.get("npcs", []):
        if "x" not in n or "y" not in n:
            continue
        name = n.get("name", "NPC")
        kind = NPC_KIND_MAP.get(n.get("kind", ""), "Dialogue")
        color = NPC_COLORS.get(name, "#FFFFFF")
        dialogue_list = n.get("dialogue", [])
        if isinstance(dialogue_list, list):
            dialogue = "|".join(str(d) for d in dialogue_list)
        else:
            dialogue = str(dialogue_list)
        condition = NPC_CONDITIONS.get(name, "")
        entities.append(make_entity("Npc", *px(n["x"], n["y"]), [
            make_field("name", "String", name),
            make_field("kind", "LocalEnum.NpcKind", kind),
            make_field("color", "Color", color),
            make_field("dialogue", "String", dialogue),
            make_field("appear_condition", "String", condition),
        ]))

    # Lights
    for l in doc.get("lights", []):
        entities.append(make_entity("Light", *px(l["x"], l["y"]), [
            make_field("radius", "Float", l.get("radius", 120)),
            make_field("r", "Float", l.get("r", 0.8)),
            make_field("g", "Float", l.get("g", 0.7)),
            make_field("b", "Float", l.get("b", 0.5)),
            make_field("intensity", "Float", l.get("intensity", 0.4)),
        ]))

    # Fog gates
    for fg in doc.get("fog_gates", []):
        dest = fg.get("dest_area", "")
        dx, dy = px(fg.get("dest_x", 0), fg.get("dest_y", 0))
        entities.append(make_entity("FogGate", *px(fg["x"], fg["y"]), [
            make_field("dest_area", "String", dest),
            make_field("dest_x", "Float", float(dx)),
            make_field("dest_y", "Float", float(dy)),
            make_field("width", "Float", float(fg.get("w", 64))),
            make_field("height", "Float", float(fg.get("h", 32))),
        ]))

    return entities


# ---- Special case: CemeteryOfAsh merges with FirelinkShrine ----
def make_cemetery():
    """CemeteryOfAsh + FirelinkShrine merged into one map."""
    cem_doc = load_doc("CemeteryOfAsh")
    fs_doc = load_doc("FirelinkShrine")

    chunk = new_chunk()

    # FirelinkShrine: placed at top of map, using its own coords scaled to fit
    fs_mw, fs_mh = fs_doc["map_size"]["width"], fs_doc["map_size"]["height"]
    fs_sx = min(2560.0 / fs_mw, 2560.0 / 700)  # limit to top 700px of map
    fs_sy = fs_sx
    # Scale FirelinkShrine sections to tile space (top portion, y:0-43 tiles)
    fs_secs = fs_doc.get("map_layout", {}).get("sections", [])
    for s in fs_secs:
        tx1 = max(0, int(s["x"] * fs_sx / 16))
        ty1 = max(0, int(s["y"] * fs_sy / 16))
        tx2 = min(CHUNK_SIZE - 1, int((s["x"] + s["w"]) * fs_sx / 16))
        ty2 = min(CHUNK_SIZE - 1, int((s["y"] + s["h"]) * fs_sy / 16))
        fill_tiles(chunk, TILE_GROUND, tx1, ty1, tx2, ty2)

    # CemeteryOfAsh: Y-flipped, placed at bottom of map (y:45-159)
    cem_mw, cem_mh = cem_doc["map_size"]["width"], cem_doc["map_size"]["height"]
    cem_sx = 2560.0 / cem_mw
    cem_sy = 2200.0 / cem_mh  # use 2200px for cemetery portion
    cem_y_offset = 45  # tiles
    cem_secs = cem_doc.get("map_layout", {}).get("sections", [])
    for s in cem_secs:
        tx1 = max(0, int(s["x"] * cem_sx / 16))
        ty1 = max(0, int(cem_y_offset + (cem_mh - s["y"] - s["h"]) * cem_sy / 16))
        tx2 = min(CHUNK_SIZE - 1, int((s["x"] + s["w"]) * cem_sx / 16))
        ty2 = min(CHUNK_SIZE - 1, int(cem_y_offset + (cem_mh - s["y"]) * cem_sy / 16))
        fill_tiles(chunk, TILE_GROUND, tx1, ty1, tx2, ty2)

    # Connecting corridor between FirelinkShrine and CemeteryOfAsh
    fill_tiles(chunk, TILE_GROUND, 30, 40, 50, 50)

    # Generate FirelinkShrine entities
    entities = []
    def fs_px(dx, dy):
        return int(dx * fs_sx), int(dy * fs_sy)
    def cem_px(dx, dy):
        return int(dx * cem_sx), int(cem_y_offset * 16 + (cem_mh - dy) * cem_sy)

    # FirelinkShrine entities
    for n in fs_doc.get("npcs", []):
        name = n.get("name", "NPC")
        kind = NPC_KIND_MAP.get(n.get("kind", ""), "Dialogue")
        color = NPC_COLORS.get(name, "#FFFFFF")
        dialogue_list = n.get("dialogue", [])
        dialogue = "|".join(dialogue_list) if isinstance(dialogue_list, list) else str(dialogue_list)
        condition = NPC_CONDITIONS.get(name, "")
        entities.append(make_entity("Npc", *fs_px(n["x"], n["y"]), [
            make_field("name", "String", name),
            make_field("kind", "LocalEnum.NpcKind", kind),
            make_field("color", "Color", color),
            make_field("dialogue", "String", dialogue),
            make_field("appear_condition", "String", condition),
        ]))

    for item in fs_doc.get("items", []):
        kind_raw = item.get("kind", "Consumable")
        mapped = ITEM_KIND_MAP.get(kind_raw, ("Consumable", "name"))
        item_kind, val_field = mapped
        fields = [make_field("kind", "LocalEnum.ItemKind", item_kind)]
        if val_field == "value" and "value" in item:
            fields.append(make_field("value", "Int", item["value"]))
        elif val_field == "name":
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        if item_kind in ("WeaponDrop", "ArmorDrop", "RingDrop"):
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        entities.append(make_entity("Item", *fs_px(item["x"], item["y"]), fields))

    for l in fs_doc.get("lights", []):
        entities.append(make_entity("Light", *fs_px(l["x"], l["y"]), [
            make_field("radius", "Float", l.get("radius", 120)),
            make_field("r", "Float", l.get("r", 0.8)),
            make_field("g", "Float", l.get("g", 0.7)),
            make_field("b", "Float", l.get("b", 0.5)),
            make_field("intensity", "Float", l.get("intensity", 0.4)),
        ]))

    # FirelinkShrine bonfire
    for bf in fs_doc.get("bonfires", []):
        entities.append(make_entity("Bonfire", *fs_px(bf["x"], bf["y"])))

    # FirelinkShrine enemies
    for e in fs_doc.get("enemies", []):
        kind = ENEMY_KIND_MAP.get(e["kind"], "HollowSoldier")
        count = e.get("count", 1)
        for i in range(count):
            ox = (i * 24) % 48 - 24
            oy = (i * 18) % 36 - 18
            ex, ey = fs_px(e["x"], e["y"])
            entities.append(make_entity("Enemy", ex + ox, ey + oy, [
                make_field("kind", "LocalEnum.EnemyKind", kind),
            ]))

    # FirelinkShrine fog gates
    for fg in fs_doc.get("fog_gates", []):
        dest = fg.get("dest_area", "")
        entities.append(make_entity("FogGate", *fs_px(fg["x"], fg["y"]), [
            make_field("dest_area", "String", dest),
            make_field("dest_x", "Float", float(fg.get("dest_x", 0))),
            make_field("dest_y", "Float", float(fg.get("dest_y", 0))),
            make_field("width", "Float", float(fg.get("w", 64))),
            make_field("height", "Float", float(fg.get("h", 32))),
        ]))

    # CemeteryOfAsh entities
    entities.append(make_entity("PlayerSpawn", *cem_px(200, 200), [
        make_field("heal", "Bool", True),
    ]))

    for bf in cem_doc.get("bonfires", []):
        entities.append(make_entity("Bonfire", *cem_px(bf["x"], bf["y"])))

    boss = cem_doc.get("boss")
    if boss:
        bosses = boss if isinstance(boss, list) else [boss]
        for b in bosses:
            entities.append(make_entity("BossSpawn", *cem_px(b["x"], b["y"])))
            arena = b.get("arena", {})
            if arena:
                gate_px, gate_py = cem_px(arena.get("x", b["x"]) + arena.get("w", 400) // 2, arena.get("y", b["y"]))
                entities.append(make_entity("FogGate", gate_px, gate_py, [
                    make_field("dest_area", "String", "CemeteryOfAsh"),
                    make_field("dest_x", "Float", float(cem_px(b["x"], b["y"])[0])),
                    make_field("dest_y", "Float", float(cem_px(b["x"], b["y"])[1])),
                    make_field("width", "Float", 80.0),
                    make_field("height", "Float", 32.0),
                ]))

    for e in cem_doc.get("enemies", []):
        kind = ENEMY_KIND_MAP.get(e["kind"], "HollowSoldier")
        count = e.get("count", 1)
        for i in range(count):
            ox = (i * 24) % 48 - 24
            oy = (i * 18) % 36 - 18
            ex, ey = cem_px(e["x"], e["y"])
            entities.append(make_entity("Enemy", ex + ox, ey + oy, [
                make_field("kind", "LocalEnum.EnemyKind", kind),
            ]))

    for item in cem_doc.get("items", []):
        kind_raw = item.get("kind", "Consumable")
        mapped = ITEM_KIND_MAP.get(kind_raw, ("Consumable", "name"))
        item_kind, val_field = mapped
        fields = [make_field("kind", "LocalEnum.ItemKind", item_kind)]
        if val_field == "value" and "value" in item:
            fields.append(make_field("value", "Int", item["value"]))
        elif val_field == "name":
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        if item_kind in ("WeaponDrop", "ArmorDrop", "RingDrop"):
            fields.append(make_field("name", "String", item.get("name", kind_raw)))
        entities.append(make_entity("Item", *cem_px(item["x"], item["y"]), fields))

    for l in cem_doc.get("lights", []):
        entities.append(make_entity("Light", *cem_px(l["x"], l["y"]), [
            make_field("radius", "Float", l.get("radius", 120)),
            make_field("r", "Float", l.get("r", 0.8)),
            make_field("g", "Float", l.get("g", 0.7)),
            make_field("b", "Float", l.get("b", 0.5)),
            make_field("intensity", "Float", l.get("intensity", 0.4)),
        ]))

    for fg in cem_doc.get("fog_gates", []):
        dest = fg.get("dest_area", "")
        entities.append(make_entity("FogGate", *cem_px(fg["x"], fg["y"]), [
            make_field("dest_area", "String", dest),
            make_field("dest_x", "Float", float(fg.get("dest_x", 0))),
            make_field("dest_y", "Float", float(fg.get("dest_y", 0))),
            make_field("width", "Float", float(fg.get("w", 64))),
            make_field("height", "Float", float(fg.get("h", 32))),
        ]))

    # Gundyr door tile patch
    entities.append(make_tile_patch(1200, 1664, "Ground", 75, 104, 81, 106, "gundyr_door_open"))

    return chunk, entities


def generate_map(identifier):
    """Generate a map from its design doc. Special case for CemeteryOfAsh."""
    if identifier == "CemeteryOfAsh":
        return make_cemetery()
    doc = load_doc(identifier)
    chunk = new_chunk()
    generate_terrain(chunk, doc)
    entities = generate_entities(doc, chunk)
    return chunk, entities


AREAS = [
    "CemeteryOfAsh",
    "LothricWall",
    "UndeadSettlement",
    "CathedralDeep",
    "Irithyll",
    "RoadOfSacrifices",
    "FarronKeep",
    "CatacombsOfCarthus",
    "SmoulderingLake",
    "IrithyllDungeon",
    "ProfanedCapital",
    "AnorLondo",
    "LothricCastle",
    "GrandArchives",
    "KilnOfTheFirstFlame",
    "ConsumedKingsGarden",
    "UntendedGraves",
    "ArchdragonPeak",
]

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
            {"id": "SilverKnight", "color": 0xC0C0C0},
            {"id": "BlackKnight", "color": 0x1A1A2E},
            {"id": "DeepAccursed", "color": 0x4A0E4E},
            {"id": "Evangelist", "color": 0x6B5B3D},
            {"id": "Thrall", "color": 0x4A3728},
            {"id": "LothricKnight", "color": 0x7F8CA0},
            {"id": "WingedKnight", "color": 0x6B6B75},
            {"id": "Ghru", "color": 0x7F6B4F},
            {"id": "Darkwraith", "color": 0x1A1A26},
            {"id": "Skeleton", "color": 0xD9D9C4},
            {"id": "Jailer", "color": 0x332633},
            {"id": "SerpentMan", "color": 0x998A5E},
            {"id": "Deacon", "color": 0x804D33},
            {"id": "FireDemon", "color": 0xB3401A},
            {"id": "StarvedHound", "color": 0x7F664D},
            {"id": "PusOfMan", "color": 0x1A0D26},
            {"id": "CathedralKnight", "color": 0x666659},
            {"id": "ManGrub", "color": 0x998A5E},
            {"id": "Gargoyle", "color": 0x737366},
            {"id": "Dog", "color": 0x7F5A40},
            {"id": "Basilisk", "color": 0x66994D},
            {"id": "DemonStatue", "color": 0x994D33},
            {"id": "InfestedCorpse", "color": 0x66594D},
            {"id": "Wretch", "color": 0x4D4033},
            {"id": "PeasantHollow", "color": 0x8C8073},
        ]),
        make_enum("ItemKind", ENUM_UIDS["ItemKind"], [
            {"id": "SoulOrb", "color": 0xF4D03F},
            {"id": "EstusShard", "color": 0xE67E22},
            {"id": "HomewardBone", "color": 0xD7DBDD},
            {"id": "PurpleMoss", "color": 0x27AE60},
            {"id": "WeaponDrop", "color": 0x95A5A6},
            {"id": "ArmorDrop", "color": 0x5D6D7E},
            {"id": "RingDrop", "color": 0xF1C40F},
            {"id": "TitaniteShard", "color": 0x7DCEA0},
            {"id": "Firebomb", "color": 0xE74C3C},
            {"id": "Ember", "color": 0xF39C12},
            {"id": "UndeadBoneShard", "color": 0xF5F5DC},
            {"id": "Consumable", "color": 0xBB8FCE},
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
            make_field_def("appear_condition", "String", FIELD_UIDS["Npc.appear_condition"], "", "F_String"),
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

def ensure_fog_gate_walls(chunk, entities):
    """Ensure fog gates sit in a doorway: ground under gate, walls on the cross-sides."""
    for ent in entities:
        if ent.get("__identifier") != "FogGate":
            continue
        px, py = ent["px"]
        w = h = 0
        for fld in ent["fieldInstances"]:
            if fld["__identifier"] == "width": w = fld["__value"]
            elif fld["__identifier"] == "height": h = fld["__value"]
        if w <= 0 or h <= 0:
            continue
        # Gate tile boundaries (inclusive)
        gx1 = max(0, int((px - w / 2) / 16))
        gy1 = max(0, int((py - h / 2) / 16))
        gx2 = min(CHUNK_SIZE - 1, int((px + w / 2) / 16))
        gy2 = min(CHUNK_SIZE - 1, int((py + h / 2) / 16))
        # 1) Carve the gate footprint as ground so the gate is walkable
        for y in range(gy1, gy2 + 1):
            for x in range(gx1, gx2 + 1):
                if chunk[y][x] not in (TILE_GROUND, TILE_POISON):
                    chunk[y][x] = TILE_GROUND
        # 2) Frame the doorway with walls on cross-sides
        ext = 2
        if w >= h:
            # Horizontal gate: walls on left and right columns
            for y in range(max(0, gy1 - ext), min(CHUNK_SIZE, gy2 + ext + 1)):
                if gx1 - 1 >= 0 and chunk[y][gx1 - 1] != TILE_GROUND and chunk[y][gx1 - 1] != TILE_POISON:
                    chunk[y][gx1 - 1] = TILE_WALL
                if gx2 + 1 < CHUNK_SIZE and chunk[y][gx2 + 1] != TILE_GROUND and chunk[y][gx2 + 1] != TILE_POISON:
                    chunk[y][gx2 + 1] = TILE_WALL
        else:
            # Vertical gate: walls on top and bottom rows
            for x in range(max(0, gx1 - ext), min(CHUNK_SIZE, gx2 + ext + 1)):
                if gy1 - 1 >= 0 and chunk[gy1 - 1][x] != TILE_GROUND and chunk[gy1 - 1][x] != TILE_POISON:
                    chunk[gy1 - 1][x] = TILE_WALL
                if gy2 + 1 < CHUNK_SIZE and chunk[gy2 + 1][x] != TILE_GROUND and chunk[gy2 + 1][x] != TILE_POISON:
                    chunk[gy2 + 1][x] = TILE_WALL



def snap_fog_gates_to_walkable(chunk, entities):
    """Move any FogGate that isn't on a walkable tile to the nearest walkable tile reachable from spawn."""
    from collections import deque
    def walkable(t):
        return t in (TILE_GROUND, TILE_POISON)
    # Find player spawn
    spawn_x, spawn_y = None, None
    for ent in entities:
        if ent.get("__identifier") == "PlayerSpawn":
            spawn_x = int(ent["px"][0] / 16)
            spawn_y = int(ent["px"][1] / 16)
            break
    if spawn_x is None:
        return
    # BFS from spawn to find all reachable tiles
    reachable = set()
    queue = deque([(spawn_x, spawn_y)])
    reachable.add((spawn_x, spawn_y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx,ny) not in reachable:
                if walkable(chunk[ny][nx]):
                    reachable.add((nx, ny))
                    queue.append((nx, ny))
    # Snap fog gates
    for ent in entities:
        if ent.get("__identifier") != "FogGate":
            continue
        px, py = ent["px"][0], ent["px"][1]
        tx, ty = int(px / 16), int(py / 16)
        if (tx, ty) in reachable:
            continue
        # Find nearest reachable tile to original position
        best = None
        best_dist = float('inf')
        for (rx, ry) in reachable:
            d = abs(rx - tx) + abs(ry - ty)
            if d < best_dist:
                best_dist = d
                best = (rx, ry)
        if best:
            ent["px"] = [best[0] * 16 + 8, best[1] * 16 + 8]

def snap_fog_gate_destinations(all_levels):
    """Fix fog gate dest_x/dest_y to land on walkable tiles in the destination map."""
    terrain_map = {}
    for identifier, level_data in all_levels.items():
        for layer in level_data["layerInstances"]:
            if layer.get("__identifier") == "Terrain":
                grid = layer["intGridCsv"]
                tiles = []
                for y in range(CHUNK_SIZE):
                    row = []
                    for x in range(CHUNK_SIZE):
                        row.append(grid[y * CHUNK_SIZE + x])
                    tiles.append(row)
                terrain_map[identifier] = tiles
                break

    for identifier, level_data in all_levels.items():
        for layer in level_data["layerInstances"]:
            if layer.get("__identifier") != "Entities":
                continue
            for ent in layer["entityInstances"]:
                if ent.get("__identifier") != "FogGate":
                    continue
                dest_area = ""
                dest_x, dest_y = 0.0, 0.0
                for fi in ent["fieldInstances"]:
                    if fi["__identifier"] == "dest_area":
                        dest_area = fi.get("__value", "")
                    elif fi["__identifier"] == "dest_x":
                        dest_x = fi["__value"] if isinstance(fi["__value"], (int, float)) else 0.0
                    elif fi["__identifier"] == "dest_y":
                        dest_y = fi["__value"] if isinstance(fi["__value"], (int, float)) else 0.0
                if not dest_area or dest_area not in terrain_map:
                    continue
                tiles = terrain_map[dest_area]
                tx, ty = int(dest_x / 16), int(dest_y / 16)
                def walkable(t):
                    return t in (TILE_GROUND, TILE_POISON)
                if 0 <= tx < CHUNK_SIZE and 0 <= ty < CHUNK_SIZE and walkable(tiles[ty][tx]):
                    continue
                # BFS to nearest walkable
                from collections import deque
                visited = set()
                queue = deque([(tx, ty)])
                visited.add((tx, ty))
                found = None
                while queue and found is None:
                    cx, cy = queue.popleft()
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = cx+dx, cy+dy
                        if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            if walkable(tiles[ny][nx]):
                                found = (nx, ny)
                                break
                            queue.append((nx, ny))
                if found:
                    for fi in ent["fieldInstances"]:
                        if fi["__identifier"] == "dest_x":
                            fi["__value"] = found[0] * 16 + 8
                        elif fi["__identifier"] == "dest_y":
                            fi["__value"] = found[1] * 16 + 8

def sync_boss_gate_dest(identifier, entities):
    """Update self-referential fog gate dest_x/dest_y to match BossSpawn position."""
    boss_spawn_pos = None
    for ent in entities:
        if ent.get("__identifier") == "BossSpawn":
            boss_spawn_pos = (ent["px"][0], ent["px"][1])
            break
    if not boss_spawn_pos:
        return
    for ent in entities:
        if ent.get("__identifier") != "FogGate":
            continue
        for fi in ent["fieldInstances"]:
            if fi["__identifier"] == "dest_area" and fi.get("__value") == identifier:
                # Self-referential = boss gate, sync dest to BossSpawn
                for fi2 in ent["fieldInstances"]:
                    if fi2["__identifier"] == "dest_x":
                        fi2["__value"] = boss_spawn_pos[0]
                    elif fi2["__identifier"] == "dest_y":
                        fi2["__value"] = boss_spawn_pos[1]
                break

def enhance_terrain_detail(identifier, chunk, entities):
    """Add terrain detail to make each map feel like its DS3 area.
    Creates internal walls to break rectangles into corridors, adds
    area-specific architectural features at high density.
    CemeteryOfAsh already has detailed terrain — skip it."""
    if identifier == "CemeteryOfAsh":
        return

    import hashlib
    from collections import deque

    seed_base = int(hashlib.md5(identifier.encode()).hexdigest()[:8], 16)
    def rng(i):
        x = (seed_base + i * 1103515245 + 12345) & 0x7FFFFFFF
        return x / 0x7FFFFFFF

    # Collect entity tile positions to avoid blocking them
    entity_tiles = set()
    for ent in entities:
        if isinstance(ent, dict) and "px" in ent:
            ex, ey = ent["px"][0], ent["px"][1]
            etx, ety = int(ex / 16), int(ey / 16)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    entity_tiles.add((etx + dx, ety + dy))

    def is_walkable(x, y):
        return 0 <= x < CHUNK_SIZE and 0 <= y < CHUNK_SIZE and chunk[y][x] in (TILE_GROUND, TILE_POISON)

    def check_connectivity():
        """BFS from first walkable tile, return reachable count."""
        start = None
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                    start = (x, y)
                    break
            if start:
                break
        if not start:
            return 0, 0
        visited = set()
        q = deque([start])
        visited.add(start)
        total = 0
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                    total += 1
        while q:
            cx, cy = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx,ny) not in visited:
                    if chunk[ny][nx] in (TILE_GROUND, TILE_POISON):
                        visited.add((nx, ny))
                        q.append((nx, ny))
        return len(visited), total

    # Get baseline connectivity
    reachable_before, total_walkable = check_connectivity()
    if total_walkable == 0:
        return

    # ---- Phase 1: Internal dividing walls ----
    # Find contiguous ground regions and add N-S or E-W walls with gaps
    # to break large open areas into corridors and rooms.
    ri = 0

    # Precompute: for each row, how many consecutive rows above/below are also walkable
    row_depth = [0] * CHUNK_SIZE
    for y in range(CHUNK_SIZE):
        has_walkable = any(chunk[y][x] in (TILE_GROUND, TILE_POISON) for x in range(CHUNK_SIZE))
        if has_walkable:
            row_depth[y] = 1
            # Check consecutive depth
            if y > 0 and row_depth[y - 1] > 0:
                # Transfer upward depth count
                pass
    # Simple: just count vertical span per row
    for y in range(CHUNK_SIZE):
        if row_depth[y] == 0:
            continue
        span = 1
        for dy in range(1, min(8, CHUNK_SIZE - y)):
            if any(chunk[y + dy][x] in (TILE_GROUND, TILE_POISON) for x in range(CHUNK_SIZE)):
                span += 1
            else:
                break
        row_depth[y] = span

    # Find horizontal extents per row
    for y in range(CHUNK_SIZE):
        left = None
        right = None
        for x in range(CHUNK_SIZE):
            if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                if left is None:
                    left = x
                right = x
        if left is None:
            continue
        # Skip rows that are part of narrow corridors (depth < 4)
        if row_depth[y] < 4:
            continue
        width = right - left + 1
        if width <= 10:
            continue
        # Add border walls to narrow wide rows
        narrow = min(width // 6, 4)
        for x in range(left, left + narrow):
            if (x, y) in entity_tiles:
                continue
            if not is_walkable(x, y):
                continue
            # Keep vertical connections (gaps every 6-10 tiles)
            gap = 6 + int(rng(ri) * 5)
            if (x - left) % gap < 3:
                continue
            chunk[y][x] = TILE_WALL
            ri += 1
        for x in range(right - narrow + 1, right + 1):
            if (x, y) in entity_tiles:
                continue
            if not is_walkable(x, y):
                continue
            gap = 6 + int(rng(ri) * 5)
            if (right - x) % gap < 3:
                continue
            chunk[y][x] = TILE_WALL
            ri += 1

    # Find vertical extents per column
    for x in range(CHUNK_SIZE):
        top = None
        bottom = None
        for y in range(CHUNK_SIZE):
            if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                if top is None:
                    top = y
                bottom = y
        if top is None:
            continue
        height = bottom - top + 1
        if height <= 10:
            continue
        # Check horizontal span — skip narrow vertical corridors
        col_width = 0
        for cx in range(max(0, x - 4), min(CHUNK_SIZE, x + 5)):
            if any(chunk[cy][cx] in (TILE_GROUND, TILE_POISON) for cy in range(top, bottom + 1)):
                col_width += 1
        if col_width < 4:
            continue
        height = bottom - top + 1
        if height <= 10:
            continue
        narrow = min(height // 6, 4)
        for y in range(top, top + narrow):
            if (x, y) in entity_tiles:
                continue
            if not is_walkable(x, y):
                continue
            gap = 6 + int(rng(ri) * 5)
            if (y - top) % gap < 3:
                continue
            chunk[y][x] = TILE_WALL
            ri += 1
        for y in range(bottom - narrow + 1, bottom + 1):
            if (x, y) in entity_tiles:
                continue
            if not is_walkable(x, y):
                continue
            gap = 6 + int(rng(ri) * 5)
            if (bottom - y) % gap < 3:
                continue
            chunk[y][x] = TILE_WALL
            ri += 1

    # ---- Phase 2: Interior cross-walls ----
    # Add N-S and E-W wall segments in the interior of large ground regions
    # to create rooms and corridors. Each wall has 1-2 gaps for passage.
    walkable_count = 0
    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                walkable_count += 1

    num_crosswalls = max(4, walkable_count // 200)
    for i in range(num_crosswalls):
        # Choose horizontal or vertical wall
        horiz = rng(ri + i * 100) > 0.5
        ri += 1
        if horiz:
            # Find a row with wide ground span
            wy = int(rng(ri) * CHUNK_SIZE)
            ri += 1
            left = right = None
            for x in range(CHUNK_SIZE):
                if is_walkable(x, wy):
                    if left is None: left = x
                    right = x
            if left is None or right - left < 8:
                continue
            # Place wall segment across ~60-80% of span with gaps
            span = right - left
            wall_start = left + int(span * 0.1)
            wall_end = left + int(span * 0.9)
            gap_pos = wall_start + int(rng(ri) * (wall_end - wall_start - 4))
            ri += 1
            for x in range(wall_start, wall_end + 1):
                if not is_walkable(x, wy):
                    continue
                if (x, wy) in entity_tiles:
                    continue
                if gap_pos <= x <= gap_pos + 3:
                    continue  # gap
                chunk[wy][x] = TILE_WALL
        else:
            wx = int(rng(ri) * CHUNK_SIZE)
            ri += 1
            top = bottom = None
            for y in range(CHUNK_SIZE):
                if is_walkable(wx, y):
                    if top is None: top = y
                    bottom = y
            if top is None or bottom - top < 8:
                continue
            span = bottom - top
            wall_start = top + int(span * 0.1)
            wall_end = top + int(span * 0.9)
            gap_pos = wall_start + int(rng(ri) * (wall_end - wall_start - 4))
            ri += 1
            for y in range(wall_start, wall_end + 1):
                if not is_walkable(wx, y):
                    continue
                if (wx, y) in entity_tiles:
                    continue
                if gap_pos <= y <= gap_pos + 3:
                    continue
                chunk[y][wx] = TILE_WALL

    # ---- Phase 3: Dense scatter features ----
    # Area-specific: gravestones, pillars, rubble, bookshelves, etc.
    feature_density = {
        "UntendedGraves": 0.15,    # dense graves (dark cemetery)
        "CatacombsOfCarthus": 0.12, # bones and skulls
        "KilnOfTheFirstFlame": 0.08, # ash debris
        "ConsumedKingsGarden": 0.10, # crystal formations
        "IrithyllDungeon": 0.10,     # cell walls
        "ArchdragonPeak": 0.08,      # stone dragon fragments
        "LothricWall": 0.08,         # castle debris
        "UndeadSettlement": 0.10,    # grave markers, wood
        "CathedralDeep": 0.08,       # cathedral debris
        "RoadOfSacrifices": 0.08,    # forest rocks/roots
        "FarronKeep": 0.08,          # swamp debris
        "SmoulderingLake": 0.08,     # lava rock
        "Irithyll": 0.08,            # city debris
        "ProfanedCapital": 0.08,     # ruined city
        "AnorLondo": 0.06,           # already has columns
        "LothricCastle": 0.08,       # castle debris
        "GrandArchives": 0.10,       # bookshelves
    }
    density = feature_density.get(identifier, 0.08)
    feature_count = int(walkable_count * density)
    placed = 0
    attempts = 0
    while placed < feature_count and attempts < feature_count * 8:
        attempts += 1
        fx = int(rng(ri + attempts) * (CHUNK_SIZE - 4)) + 2
        fy = int(rng(ri + attempts + 5000) * (CHUNK_SIZE - 4)) + 2
        ri += 1
        if not is_walkable(fx, fy) or not is_walkable(fx + 1, fy):
            continue
        if (fx, fy) in entity_tiles or (fx + 1, fy) in entity_tiles:
            continue
        # Don't block narrow passages
        wall_adj = sum(1 for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)] if not is_walkable(fx+dx, fy+dy))
        if wall_adj > 2:
            continue
        chunk[fy][fx] = TILE_WALL
        chunk[fy][fx + 1] = TILE_WALL
        placed += 1

    # ---- Phase 4: Large architectural blocks ----
    arch_count = max(3, walkable_count // 80)
    placed = 0
    attempts = 0
    while placed < arch_count and attempts < arch_count * 20:
        attempts += 1
        fx = int(rng(ri + attempts + 10000) * (CHUNK_SIZE - 8)) + 4
        fy = int(rng(ri + attempts + 15000) * (CHUNK_SIZE - 8)) + 4
        ri += 1
        w = 2 + int(rng(ri) * 2)  # 2-3
        h = 2 + int(rng(ri + 500) * 2)  # 2-3
        # Check all tiles are walkable
        ok = True
        for dy in range(h):
            for dx in range(w):
                if not is_walkable(fx + dx, fy + dy):
                    ok = False
                    break
                if (fx + dx, fy + dy) in entity_tiles:
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        # Ensure passage on at least 2 sides
        sides_free = 0
        if fy > 0 and any(is_walkable(fx + dx, fy - 1) for dx in range(w)):
            sides_free += 1
        if fy + h < CHUNK_SIZE and any(is_walkable(fx + dx, fy + h) for dx in range(w)):
            sides_free += 1
        if fx > 0 and any(is_walkable(fx - 1, fy + dy) for dy in range(h)):
            sides_free += 1
        if fx + w < CHUNK_SIZE and any(is_walkable(fx + w, fy + dy) for dy in range(h)):
            sides_free += 1
        if sides_free < 2:
            continue
        fill_tiles(chunk, TILE_WALL, fx, fy, fx + w - 1, fy + h - 1)
        placed += 1

    # ---- Phase 5: Verify connectivity, reopen if needed ----
    # Use player spawn as BFS start to match actual gameplay
    pspawn = None
    for ent in entities:
        if isinstance(ent, dict) and ent.get("__identifier") == "PlayerSpawn":
            px, py = ent["px"]
            pspawn = (int(px / 16), int(py / 16))
            break
    if not pspawn:
        pspawn = None
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                if chunk[y][x] in (TILE_GROUND, TILE_POISON):
                    pspawn = (x, y)
                    break
            if pspawn:
                break

    if pspawn:
        for iteration in range(5):  # retry up to 5 times
            visited = set()
            q = deque([pspawn])
            visited.add(pspawn)
            while q:
                cx, cy = q.popleft()
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = cx+dx, cy+dy
                    if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx,ny) not in visited:
                        if chunk[ny][nx] in (TILE_GROUND, TILE_POISON):
                            visited.add((nx, ny))
                            q.append((nx, ny))
            # Check if all ground is reachable
            total = sum(1 for y in range(CHUNK_SIZE) for x in range(CHUNK_SIZE) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
            if len(visited) >= total * 0.95:
                break
            # Group unreachable ground into connected regions
            unvisited = set()
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    if chunk[y][x] in (TILE_GROUND, TILE_POISON) and (x, y) not in visited:
                        unvisited.add((x, y))
            if not unvisited:
                break
            regions = []
            while unvisited:
                seed = next(iter(unvisited))
                region = set()
                rq = deque([seed])
                region.add(seed)
                unvisited.discard(seed)
                while rq:
                    cx, cy = rq.popleft()
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = cx+dx, cy+dy
                        if (nx, ny) in unvisited:
                            unvisited.discard((nx, ny))
                            region.add((nx, ny))
                            rq.append((nx, ny))
                regions.append(region)
            # Carve paths for each region
            any_carved = False
            for region in regions:
                # Find point in region closest to visited bounding box
                vcx = sum(x for x,y in visited) // len(visited)
                vcy = sum(y for x,y in visited) // len(visited)
                best_pt = min(region, key=lambda p: abs(p[0]-vcx)+abs(p[1]-vcy))
                # BFS through walls
                best_path = None
                q2 = deque([(best_pt[0], best_pt[1], [best_pt])])
                seen = {best_pt}
                while q2 and not best_path:
                    cx, cy, path = q2.popleft()
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = cx+dx, cy+dy
                        if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx,ny) not in seen:
                            seen.add((nx, ny))
                            if (nx, ny) in visited:
                                best_path = path + [(nx, ny)]
                                break
                            if chunk[ny][nx] == TILE_WALL:
                                q2.append((nx, ny, path + [(nx, ny)]))
                    if len(seen) > 5000:
                        break
                if best_path:
                    for px, py in best_path:
                        if chunk[py][px] == TILE_WALL:
                            chunk[py][px] = TILE_GROUND
                            any_carved = True
            if not any_carved:
                break


def snap_entities_to_walkable(chunk, entities):
    """Move any entity that isn't on a walkable tile to the nearest reachable walkable tile."""
    from collections import deque
    def walkable(t):
        return t in (TILE_GROUND, TILE_POISON)
    spawn_x, spawn_y = None, None
    for ent in entities:
        if ent.get("__identifier") == "PlayerSpawn":
            spawn_x = int(ent["px"][0] / 16)
            spawn_y = int(ent["px"][1] / 16)
            break
    if spawn_x is None:
        return
    reachable = set()
    queue = deque([(spawn_x, spawn_y)])
    reachable.add((spawn_x, spawn_y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and (nx,ny) not in reachable:
                if walkable(chunk[ny][nx]):
                    reachable.add((nx, ny))
                    queue.append((nx, ny))
    if not reachable:
        return
    for ent in entities:
        eid = ent.get("__identifier", "")
        if eid not in ("Enemy", "Item", "Chest", "Npc", "Light", "BossSpawn", "Bonfire"):
            continue
        px, py = ent["px"][0], ent["px"][1]
        tx, ty = int(px / 16), int(py / 16)
        if (tx, ty) in reachable:
            continue
        best = None
        best_dist = float('inf')
        for (rx, ry) in reachable:
            d = abs(rx - tx) + abs(ry - ty)
            if d < best_dist:
                best_dist = d
                best = (rx, ry)
        if best:
            ent["px"] = [best[0] * 16 + 8, best[1] * 16 + 8]

def add_design_doc_content(identifier, chunk, entities):
    """Read design doc and add missing items/enemies/npcs/chests."""
    import glob
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # script_dir = .../darksouls/maps, project_dir = .../darksouls
    project_dir = os.path.dirname(script_dir)
    doc_path = os.path.join(project_dir, "docs", "maps", f"{identifier}.json")
    if not os.path.exists(doc_path):
        return entities

    with open(doc_path) as f:
        doc = json.load(f)

    map_w = doc.get("map_size", {}).get("width", 2560)
    map_h = doc.get("map_size", {}).get("height", 2560)
    # Scale coordinates from design space to our 2560×2560 (160 tiles × 16px)
    sx = 2560.0 / map_w if map_w != 2560 else 1.0
    sy = 2560.0 / map_h if map_h != 2560 else 1.0

    # Count existing entities by type
    existing_counts = {}
    for ent in entities:
        eid = ent.get("__identifier", "")
        existing_counts[eid] = existing_counts.get(eid, 0) + 1

    # Design doc targets
    doc_items = doc.get('items', [])
    doc_enemies = doc.get('enemies', [])
    doc_chests = doc.get('chests', [])
    doc_npcs = doc.get('npcs', [])

    # Only add if current count is below design doc count
    need_items = max(0, len(doc_items) - existing_counts.get("Item", 0))
    need_enemies = max(0, len(doc_enemies) - existing_counts.get("Enemy", 0))
    need_chests = max(0, len(doc_chests) - existing_counts.get("Chest", 0))
    need_npcs = max(0, len(doc_npcs) - existing_counts.get("Npc", 0))

    if need_items == 0 and need_enemies == 0 and need_chests == 0 and need_npcs == 0:
        return entities

    # Collect existing positions and NPC names to avoid duplicates
    existing_positions = set()
    existing_npc_names = set()
    for ent in entities:
        eid = ent.get("__identifier", "")
        if eid in ("Enemy", "Item", "Chest", "Npc"):
            existing_positions.add((ent["px"][0], ent["px"][1]))
        if eid == "Npc":
            for f in ent.get("fieldInstances", []):
                if f.get("__identifier") == "name":
                    existing_npc_names.add(f["__value"])

    # Build BFS-reachable walkable tiles for scattering
    from collections import deque
    reachable_tiles = set()
    spawn_ent = next((e for e in entities if e.get("__identifier") == "PlayerSpawn"), None)
    if spawn_ent:
        sp_tx, sp_ty = int(spawn_ent["px"][0] / 16), int(spawn_ent["px"][1] / 16)
        q = deque([(sp_tx, sp_ty)])
        reachable_tiles.add((sp_tx, sp_ty))
        while q:
            tx, ty = q.popleft()
            for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nnx, nny = tx+ddx, ty+ddy
                if 0 <= nnx < CHUNK_SIZE and 0 <= nny < CHUNK_SIZE and (nnx,nny) not in reachable_tiles:
                    if chunk[nny][nnx] in (TILE_GROUND, TILE_POISON):
                        reachable_tiles.add((nnx, nny))
                        q.append((nnx, nny))

    def pos_exists(x, y, threshold=24):
        for ex, ey in existing_positions:
            if abs(ex - x) < threshold and abs(ey - y) < threshold:
                return True
        return False

    def scatter_pos(x, y, max_tries=20):
        """If position overlaps, find nearest unoccupied walkable tile."""
        if not pos_exists(x, y):
            return x, y
        # Try small offsets first
        for offset in range(1, max_tries):
            for dx, dy in [(offset*16,0),(-offset*16,0),(0,offset*16),(0,-offset*16),
                           (offset*16,offset*16),(-offset*16,offset*16),(offset*16,-offset*16),(-offset*16,-offset*16)]:
                nx, ny = x + dx, y + dy
                if not pos_exists(nx, ny):
                    tx, ty = int(nx/16), int(ny/16)
                    if (tx, ty) in reachable_tiles:
                        return nx, ny
        return x, y  # give up, snap_entities_to_walkable will fix it

    # Map design doc enemy types to our EnemyKind
    enemy_map = {
        'HollowAssassin': 'Assassin', 'HollowSoldier': 'HollowSoldier',
        'StarvedHound': 'StarvedHound', 'CrystalLizard': 'CrystalLizard',
        'LothricKnight': 'LothricKnight', 'Darkwraith': 'Darkwraith',
        'WingedKnight': 'WingedKnight', 'Evangelist': 'Evangelist',
        'Thrall': 'Thrall', 'PusOfMan': 'PusOfMan', 'Archer': 'Archer',
        'Knight': 'Knight', 'Assassin': 'Assassin', 'DarkMage': 'DarkMage',
        'SilverKnight': 'SilverKnight', 'BlackKnight': 'BlackKnight',
        'DeepAccursed': 'DeepAccursed', 'Ghru': 'Ghru', 'Skeleton': 'Skeleton',
        'Jailer': 'Jailer', 'SerpentMan': 'SerpentMan', 'Deacon': 'Deacon',
        'FireDemon': 'FireDemon', 'CathedralKnight': 'CathedralKnight',
        'ManGrub': 'ManGrub', 'Gargoyle': 'Gargoyle', 'Dog': 'Dog',
        'Basilisk': 'Basilisk', 'DemonStatue': 'DemonStatue',
        'InfestedCorpse': 'InfestedCorpse', 'Wretch': 'Wretch',
        'PeasantHollow': 'PeasantHollow', 'Mimic': 'Mimic',
        # Special mappings — design doc names → engine names
        'SwordMaster': 'Assassin', 'GraveWarden': 'HollowSoldier',
        'ParasiteLizard': 'CrystalLizard', 'Peasant': 'PeasantHollow',
        'Hollow': 'HollowSoldier', 'Spider': 'Dog',
        'Ghrul': 'Ghru', 'SkeletonSwordsman': 'Skeleton',
        'SkeletonBall': 'Skeleton', 'SkeletonWheel': 'Skeleton',
        'Hound': 'StarvedHound', 'RottenDog': 'Dog',
        'GreatCrab': 'Dog', 'HoundRat': 'Dog', 'LargeHoundRat': 'Dog',
        'Demon': 'FireDemon', 'DemonCleric': 'FireDemon',
        'CarthusSandworm': 'DarkMage', 'SmoulderingGhru': 'Ghru',
        'SmolderingRottenFlesh': 'InfestedCorpse',
        'GargoyleBeast': 'Gargoyle', 'GargoyleFlyer': 'Gargoyle',
        'RottenFlesh': 'InfestedCorpse', 'Rat': 'Dog',
        'LargeRat': 'Dog', 'Bat': 'Dog', 'Leech': 'Dog',
        'FeralHound': 'StarvedHound', 'Corvian': 'Assassin',
        'CorvianKnight': 'Knight', 'PaintedWorldKnight': 'Knight',
        'ConsumedKingKnight': 'Knight', 'DragonSlayer': 'SilverKnight',
        'WingedDemon': 'FireDemon', 'DemonSlave': 'FireDemon',
    }

    # Map design doc item types to our ItemKind
    def map_item_kind(item):
        kind = item.get('kind', '')
        name = item.get('name', '')
        name_en = item.get('name_en', '')
        value = item.get('value', 0)

        soul_kinds = ('SoulItem', 'SoulOrb', 'SoulDrop', 'LargeSoulOrb',
                      'NamedSoul', 'BossSoul', 'AbyssWatchersSoul',
                      'FadingSoul', 'LargeSoulOfDesertedCorpse',
                      'SoulOfUnknownTraveler', 'SoulOfRottedGreatwood')
        if kind in soul_kinds:
            return ('SoulOrb', value or 200, '')
        if kind in ('EstusShard', 'EstusFlask', 'EstusUpgrade'):
            return ('EstusShard', 0, '')
        if kind == 'AshenEstusFlask':
            return ('Consumable', 0, '灰色原素瓶')
        if kind == 'HomewardBone':
            return ('HomewardBone', 0, '')
        if kind == 'PurpleMoss':
            return ('PurpleMoss', 0, '')
        if kind in ('Firebomb', 'BlackFirebomb'):
            return ('Firebomb', 0, '')
        if kind == 'TitaniteShard':
            return ('TitaniteShard', 0, '')
        if kind in ('TitaniteScale', 'LargeTitaniteShard', 'TitaniteChunk',
                     'TwinklingTitanite', 'TitaniteDrop', 'UpgradeMaterial'):
            return ('Consumable', 0, name or name_en or kind)
        if kind == 'Ember':
            return ('Ember', 0, '')
        if kind in ('UndeadBoneShard', 'BoneShard'):
            return ('UndeadBoneShard', 0, '')
        if kind in ('TomeDrop', 'SpellDrop', 'MiracleDrop', 'PyromancyDrop', 'SorceryDrop'):
            return ('Consumable', 0, name or name_en or kind)
        weapon_types = {
            'Dagger':'Dagger','Spear':'Spear','Longsword':'Longsword',
            'Uchigatana':'Uchigatana','GreatAxe':'GreatAxe','Shield':'Shield',
            'HandAxe':'Longsword','GreatScythe':'Longsword','Whip':'Longsword',
            'Caestus':'Dagger','Partizan':'Spear','LargeClub':'GreatAxe',
            'Claw':'Dagger','WolfKnightGreatsword':'GreatAxe',
            'IrithyllStraightSword':'Longsword','RedHiltedHalberd':'Longsword',
        }
        if kind in ('WeaponDrop',) or kind in weapon_types:
            w = weapon_types.get(name_en, weapon_types.get(kind, 'Longsword'))
            return ('WeaponDrop', 0, w)
        if kind in ('ArmorDrop', 'Armor') or 'Set' in kind:
            return ('ArmorDrop', 0, name or name_en or kind)
        if kind in ('RingDrop', 'Ring') or 'Ring' in kind or 'ring' in name.lower():
            return ('RingDrop', 0, name or name_en or kind)
        if kind in ('ShieldDrop', 'Shield') or 'Shield' in name:
            return ('ArmorDrop', 0, name or name_en)
        if kind == 'CoiledSword':
            return ('WeaponDrop', 0, 'Longsword')
        # Everything else → generic Consumable
        return ('Consumable', 0, name or name_en or kind)

    new_entities = []

    # Add missing items
    items_added = 0
    for item in doc_items:
        if items_added >= need_items:
            break
        x = int(item.get('x', 0) * sx)
        y = int(item.get('y', 0) * sy)
        x, y = scatter_pos(x, y)
        if pos_exists(x, y):
            continue
        mapped = map_item_kind(item)
        kind, val, name = mapped
        fields = [make_field("kind", "LocalEnum.ItemKind", kind)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))
        if kind in ("WeaponDrop", "Consumable", "ArmorDrop", "RingDrop"):
            fields.append(make_field("name", "String", name))
        if kind == "ArmorDrop" and name:
            # Try to infer slot
            slot = "Chest"
            if any(w in name for w in ("Helm", "Helmet", "Crown", "头")):
                slot = "Head"
            elif any(w in name for w in ("Gauntlet", "Gloves", "手")):
                slot = "Hands"
            elif any(w in name for w in ("Legging", "Boots", "Greaves", "腿")):
                slot = "Legs"
            fields.append(make_field("slot", "String", slot))
        ent = make_entity("Item", x, y, fields)
        new_entities.append(ent)
        existing_positions.add((x, y))
        items_added += 1

    # Add missing enemies
    enemies_added = 0
    for enemy in doc_enemies:
        x = int(enemy.get('x', 0) * sx)
        y = int(enemy.get('y', 0) * sy)
        kind_str = enemy_map.get(enemy.get('kind', ''), 'HollowSoldier')
        count = enemy.get('count', 1)
        for i in range(count):
            if enemies_added >= need_enemies:
                break
            ex = x + i * 24
            if pos_exists(ex, y):
                continue
            ent = make_entity("Enemy", ex, y, [make_field("kind", "LocalEnum.EnemyKind", kind_str)])
            new_entities.append(ent)
            existing_positions.add((ex, y))
            enemies_added += 1
        if enemies_added >= need_enemies:
            break

    # Add missing NPCs
    npcs_added = 0
    for npc in doc_npcs:
        x = int(npc.get('x', 0) * sx)
        y = int(npc.get('y', 0) * sy)
        x, y = scatter_pos(x, y)
        if pos_exists(x, y):
            continue
        name = npc.get('name', npc.get('name_en', 'NPC'))
        if name in existing_npc_names:
            continue
        # Map design doc NPC kinds to our supported types
        npc_kind = npc.get('kind', 'Dialogue')
        kind = {'Dialogue':'Dialogue','Merchant':'Merchant','LevelUp':'LevelUp',
                'Blacksmith':'Blacksmith','Summon':'Dialogue','Covenant':'Merchant',
                'Event':'Dialogue','Invader':'Dialogue','HostileNPC':'Dialogue',
                'Trade':'Merchant','Hawkwood':'Dialogue','':'Dialogue',
               }.get(npc_kind, 'Dialogue')
        color = npc.get('color', '#FFFFFF')
        dialogue = '|'.join(npc.get('dialogue', []))
        if not dialogue:
            dialogue = '...'
        condition = NPC_CONDITIONS.get(name, '')
        ent = make_entity("Npc", x, y, [
            make_field("name", "String", name),
            make_field("kind", "LocalEnum.NpcKind", kind),
            make_field("color", "Color", color),
            make_field("dialogue", "String", dialogue),
            make_field("appear_condition", "String", condition),
        ])
        new_entities.append(ent)
        existing_positions.add((x, y))
        npcs_added += 1
        if npcs_added >= need_npcs:
            break

    # Add missing chests
    chests_added = 0
    for chest in doc_chests:
        x = int(chest.get('x', 0) * sx)
        y = int(chest.get('y', 0) * sy)
        x, y = scatter_pos(x, y)
        if pos_exists(x, y):
            continue
        loot = chest.get('loot', {})
        loot_item = map_item_kind(loot) if loot else ('SoulOrb', 100, '')
        is_mimic = chest.get('is_mimic', False)
        lk, lv, ln = loot_item
        fields = [
            make_field("loot_kind", "LocalEnum.ItemKind", lk),
            make_field("loot_value", "Int", lv),
            make_field("loot_name", "String", ln),
            make_field("is_mimic", "Bool", is_mimic),
        ]
        ent = make_entity("Chest", x, y, fields)
        new_entities.append(ent)
        existing_positions.add((x, y))
        chests_added += 1
        if chests_added >= need_chests:
            break

    entities.extend(new_entities)
    return entities

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    levels_dir = os.path.join(script_dir, "ds2d")
    os.makedirs(levels_dir, exist_ok=True)

    all_levels = {}
    level_summaries = []
    for uid, identifier in enumerate(AREAS, start=1):
        chunk, entities = generate_map(identifier)
        add_design_doc_content(identifier, chunk, entities)
        enhance_terrain_detail(identifier, chunk, entities)
        ensure_fog_gate_walls(chunk, entities)
        snap_fog_gates_to_walkable(chunk, entities)
        snap_entities_to_walkable(chunk, entities)
        sync_boss_gate_dest(identifier, entities)
        populate_entity_def_uids(entities)
        level = make_level(identifier, chunk, entities, uid)
        all_levels[identifier] = level
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

    # Post-process: fix fog gate destinations to land on walkable tiles
    snap_fog_gate_destinations(all_levels)

    # Write level files
    for identifier, level in all_levels.items():
        level_path = os.path.join(levels_dir, f"{identifier}.ldtkl")
        with open(level_path, "w") as f:
            json.dump(level, f, indent=2)
        print(f"  wrote {level_path}")

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
