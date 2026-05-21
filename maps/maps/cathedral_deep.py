from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_cathedral_deep():
    """Cathedral of the Deep - vertical labyrinth from cemetery to Rosaria's bedchamber.
    Faithful DS3 layout: cemetery entry -> outer graveyard -> Cleansing Chapel ->
    cathedral side aisles -> cathedral nave -> Giant room -> Deacon altar hall ->
    slug corridor -> Rosaria's bedchamber. Connected by spine corridor along x=80.
    Design doc: 4000x3600, 11 sections forming a vertical descent.
    """
    chunk = new_chunk(320, 288)
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

    # ================================================================
    # SESSION 12 FIDELITY PASS — CathedralDeep fine architectural details
    # ================================================================
    # Entry bridge — stone railing debris (DS3: bridge into cathedral)
    fill_tiles(chunk, TILE_WALL, 10, 6, 11, 7)
    fill_tiles(chunk, TILE_WALL, 18, 10, 19, 11)
    fill_tiles(chunk, TILE_WALL, 26, 8, 27, 9)
    fill_tiles(chunk, TILE_WALL, 34, 12, 35, 13)
    fill_tiles(chunk, TILE_WALL, 42, 10, 43, 11)
    # Cathedral exterior — flying buttress bases (DS3: gothic cathedral buttresses)
    fill_tiles(chunk, TILE_WALL, 6, 14, 7, 15)
    fill_tiles(chunk, TILE_WALL, 14, 18, 15, 19)
    fill_tiles(chunk, TILE_WALL, 22, 16, 23, 17)
    fill_tiles(chunk, TILE_WALL, 30, 20, 31, 21)
    fill_tiles(chunk, TILE_WALL, 38, 18, 39, 19)
    fill_tiles(chunk, TILE_WALL, 46, 22, 47, 23)
    # Graveyard — tilted headstones (DS3: cemetery with fallen headstones)
    fill_tiles(chunk, TILE_WALL, 8, 24, 9, 25)
    fill_tiles(chunk, TILE_WALL, 16, 28, 17, 29)
    fill_tiles(chunk, TILE_WALL, 24, 26, 25, 27)
    fill_tiles(chunk, TILE_WALL, 32, 30, 33, 31)
    fill_tiles(chunk, TILE_WALL, 40, 28, 41, 29)
    fill_tiles(chunk, TILE_WALL, 12, 32, 13, 33)
    # Cathedral nave — pillar bases (DS3: grand stone pillars)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 39)
    fill_tiles(chunk, TILE_WALL, 36, 42, 37, 43)
    fill_tiles(chunk, TILE_WALL, 44, 40, 45, 41)
    fill_tiles(chunk, TILE_WALL, 52, 44, 53, 45)
    fill_tiles(chunk, TILE_WALL, 60, 42, 61, 43)
    fill_tiles(chunk, TILE_WALL, 68, 46, 69, 47)
    fill_tiles(chunk, TILE_WALL, 76, 44, 77, 45)
    # Roof rafters — wooden beam debris (DS3: rafters above cathedral)
    fill_tiles(chunk, TILE_WALL, 70, 50, 71, 51)
    fill_tiles(chunk, TILE_WALL, 78, 52, 79, 53)
    fill_tiles(chunk, TILE_WALL, 86, 50, 87, 51)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 82, 54, 83, 55)
    # Giant's room — collapsed ceiling stones (DS3: room with sleeping giant)
    fill_tiles(chunk, TILE_WALL, 40, 90, 41, 91)
    fill_tiles(chunk, TILE_WALL, 46, 94, 47, 95)
    fill_tiles(chunk, TILE_WALL, 52, 88, 53, 89)
    fill_tiles(chunk, TILE_WALL, 58, 96, 59, 97)
    fill_tiles(chunk, TILE_WALL, 62, 92, 63, 93)
    # Deacon hall — pews and candle stands (DS3: dark hall with mass of deacons)
    fill_tiles(chunk, TILE_WALL, 34, 108, 35, 109)
    fill_tiles(chunk, TILE_WALL, 40, 112, 41, 113)
    fill_tiles(chunk, TILE_WALL, 46, 116, 47, 117)
    fill_tiles(chunk, TILE_WALL, 52, 110, 53, 111)
    fill_tiles(chunk, TILE_WALL, 56, 120, 57, 121)
    fill_tiles(chunk, TILE_WALL, 38, 118, 39, 119)
    # Rosaria's chamber — chamber wall fragments (DS3: bed chamber area)
    fill_tiles(chunk, TILE_WALL, 32, 138, 33, 139)
    fill_tiles(chunk, TILE_WALL, 38, 142, 39, 143)
    fill_tiles(chunk, TILE_WALL, 44, 146, 45, 147)
    fill_tiles(chunk, TILE_WALL, 50, 140, 51, 141)
    fill_tiles(chunk, TILE_WALL, 56, 148, 57, 149)


    # DS3: Cathedral of the Deep has NO poison terrain — all water is regular water
    # (cleansing chapel basin, exterior puddles, slug corridor are non-toxic)

    # ================================================================
    # DS3 CATHEDRAL NAVE — Cathedral of the Deep interior architecture
    # DS3: massive gothic cathedral with long nave, side aisles,
    # flying buttresses, grand altar, and deep water pools
    # ================================================================
    # Cathedral nave — long central aisle walls (DS3: grand cathedral nave)
    fill_tiles(chunk, TILE_WALL, 38, 55, 42, 65)    # Nave pillar row left
    fill_tiles(chunk, TILE_WALL, 58, 55, 62, 65)    # Nave pillar row right
    fill_tiles(chunk, TILE_WALL, 48, 62, 52, 72)    # Nave center column
    # Side aisle walls (DS3: narrow aisles along cathedral sides)
    fill_tiles(chunk, TILE_WALL, 34, 70, 38, 80)    # Left aisle wall
    fill_tiles(chunk, TILE_WALL, 62, 70, 66, 80)    # Right aisle wall
    # Deacon altar hall — altar architecture (DS3: dark altar hall with deep fire)
    fill_tiles(chunk, TILE_WALL, 34, 108, 38, 118)  # Altar wall left
    fill_tiles(chunk, TILE_WALL, 56, 108, 60, 118)  # Altar wall right
    fill_tiles(chunk, TILE_WALL, 44, 118, 50, 128)  # Altar front wall
    fill_tiles(chunk, TILE_WALL, 64, 115, 68, 125)  # Altar side wall
    # Giant room — massive stone pillars (DS3: room where giant shoots arrows)
    fill_tiles(chunk, TILE_WALL, 38, 88, 42, 98)    # Giant room pillar 1
    fill_tiles(chunk, TILE_WALL, 50, 92, 54, 102)   # Giant room pillar 2
    fill_tiles(chunk, TILE_WALL, 60, 88, 64, 98)    # Giant room pillar 3
    # Upper gallery — overlook walls (DS3: gallery overlooking nave)
    fill_tiles(chunk, TILE_WALL, 64, 60, 68, 68)    # Gallery wall left
    fill_tiles(chunk, TILE_WALL, 76, 64, 80, 72)    # Gallery wall right
    fill_tiles(chunk, TILE_WALL, 70, 56, 74, 62)    # Gallery divider
        # --- ENTITIES ---
    spawn_px, spawn_py = 30 * 16, 8 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3: Cathedral of the Deep, Cleansing Chapel, Deacons of the Deep, Rosaria's Bed Chamber
    entities.append(make_entity("Bonfire", 35 * 16, 38 * 16))       # Cathedral of the Deep (entry)
    entities.append(make_entity("Bonfire", 97 * 16, 94 * 16))      # Cleansing Chapel
    entities.append(make_entity("Bonfire", 255 * 16, 91 * 16))     # Deacons of the Deep (boss arena)
    entities.append(make_entity("Bonfire", 190 * 16, 213 * 16))     # Rosaria's Bed Chamber

    # Boss - Deacons of the Deep
    entities.append(make_entity("BossSpawn", 190 * 16, 213 * 16))

    # Enemies (DS3 Cathedral of the Deep: Cathedral Knights, Thralls/Hollow Slaves,
    # Evangelists, Deacons, Infested Corpses, Reanimated Corpses, Devout Hollows,
    # Writhing Rotten Flesh, Cage Spiders, Man-grubs, Deep Accursed, Mimic,
    # Longfinger Kirk invader, Starved Hounds, Corpse-grubs, Crystal Lizards,
    # Cathedral Grave Wardens, Ravenous Crystal Lizards)

    
    # --- DS3 faithful enemies (CathedralDeep) ---
    # InfestedCorpse (13)
    for tx, ty in [(28, 6), (34, 8), (25, 10), (35, 12), (30, 28), (36, 30), (76, 66), (36, 84), (44, 86), (38, 86), (42, 88), (30, 108), (28, 114)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("InfestedCorpse", "InfestedCorpse"))]))
    # CrystalLizard (2)
    entities.append(make_entity("Enemy", 38 * 16, 4 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 60 * 16, 76 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # CathedralKnight (10)
    for tx, ty in [(40, 16), (45, 20), (48, 54), (52, 56), (50, 70), (55, 72), (70, 62), (48, 88), (52, 96), (60, 110)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CathedralKnight", "CathedralKnight"))]))
    # StarvedHound (2)
    entities.append(make_entity("Enemy", 22 * 16, 24 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 26 * 16, 28 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    # CathedralGraveWarden (4)
    entities.append(make_entity("Enemy", 34 * 16, 26 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CathedralGraveWarden", "CathedralGraveWarden"))]))
    entities.append(make_entity("Enemy", 38 * 16, 32 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CathedralGraveWarden", "CathedralGraveWarden"))]))
    entities.append(make_entity("Enemy", 58 * 16, 106 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CathedralGraveWarden", "CathedralGraveWarden"))]))
    entities.append(make_entity("Enemy", 62 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CathedralGraveWarden", "CathedralGraveWarden"))]))
    # Evangelist (6)
    entities.append(make_entity("Enemy", 34 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    entities.append(make_entity("Enemy", 46 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    entities.append(make_entity("Enemy", 42 * 16, 74 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    entities.append(make_entity("Enemy", 66 * 16, 64 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    entities.append(make_entity("Enemy", 72 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    entities.append(make_entity("Enemy", 40 * 16, 96 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    # DevoutHollow (2) — DS3: praying hollows in cathedral corridors
    for tx, ty in [(28, 40), (58, 64)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DevoutHollow", "DevoutHollow"))]))
    # Thrall (13)
    for tx, ty in [(60, 60), (64, 65), (68, 62), (62, 68), (48, 76), (56, 78), (52, 73), (58, 75), (54, 77), (46, 100), (54, 102), (36, 94), (40, 98)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Thrall", "Thrall"))]))
    # DeepAccursed (1)
    entities.append(make_entity("Enemy", 22 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DeepAccursed", "DeepAccursed"))]))
    # GiantSlave (2)
    entities.append(make_entity("Enemy", 44 * 16, 92 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))
    entities.append(make_entity("Enemy", 56 * 16, 98 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))
    # Deacon (12)
    for tx, ty in [(38, 110), (42, 108), (48, 118), (52, 116), (56, 114), (40, 118), (45, 122), (50, 124), (55, 120), (35, 124), (58, 118), (32, 120)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Deacon", "Deacon"))]))
    # ManGrub (5)
    entities.append(make_entity("Enemy", 34 * 16, 135 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    entities.append(make_entity("Enemy", 38 * 16, 138 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    entities.append(make_entity("Enemy", 42 * 16, 140 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    entities.append(make_entity("Enemy", 36 * 16, 142 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    entities.append(make_entity("Enemy", 40 * 16, 144 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    # ReanimatedCorpse (1) — DS3: corpses that reanimate in cathedral halls
    entities.append(make_entity("Enemy", 64 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ReanimatedCorpse", "ReanimatedCorpse"))]))
    # CorpseGrub (3) — DS3: grub-like creatures in cathedral corridors
    for tx, ty in [(52, 73), (56, 78), (36, 94)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CorpseGrub", "CorpseGrub"))]))
    # CageSpider (2) — DS3: spider-like enemies in cathedral upper levels
    for tx, ty in [(68, 62), (62, 68)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CageSpider", "CageSpider"))]))
    # WrithingRottenFlesh (2) — DS3: fleshy creatures in cathedral depths
    for tx, ty in [(40, 98), (54, 102)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("WrithingRottenFlesh", "WrithingRottenFlesh"))]))
    # RavenousCrystalLizard (1) — DS3: ravenous crystal lizard near Rosaria's chamber
    entities.append(make_entity("Enemy", 42 * 16, 140 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("RavenousCrystalLizard", "RavenousCrystalLizard"))]))
    # MiniBoss (1) — DS3: Deacons of the Deep (boss encounter)
    entities.append(make_entity("Enemy", 45 * 16, 114 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- Items (DS3 Cathedral of the Deep) — accurate from wiki ---

    entities.append(make_entity("Npc", 100 * 16, 137 * 16, [make_field("name", "String", "Patches"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#808080"), make_field("dialogue", "String", "You're a parasite, only thinking of yourself|I know your kind, you're nothing but trouble|What's wrong? Something the matter?|Heh heh heh|I'm Patches, the one and only|You know what I'm talking about, don't you?")]))
    entities.append(make_entity("Npc", 255 * 16, 91 * 16, [make_field("name", "String", "Rosaria"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D0A0B0"), make_field("dialogue", "String", "(No tongue, but her will is clear)|Offer me pale tongues, and I shall grant your desire|Rebirth, or fingers to invade others|I am Rosaria, Mother of Rebirth|The fingers of the gods stretch far and wide|Each rebirth costs a pale tongue")]))
    # Siegward of Catarina — stuck in the well outside Cathedral (DS3: freed via lift mechanism)
    entities.append(make_entity("Npc", 87 * 16, 134 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A060"), make_field("dialogue", "String", "Aah, hello! Up here!|I seem to be stuck in this well|Could you find a way to get me out?|Oh, very good! My thanks, friend|Let me repay you with a sip of Siegbräu")]))

    # Fog Gate to Road of Sacrifices (DS3: shortcut back from Cathedral)
    entities.append(make_entity("FogGate", 35 * 16, 32 * 16, [
        make_field("dest_area", "String", "RoadOfSacrifices"),
        make_field("dest_x", "Float", 2400.0),
        make_field("dest_y", "Float", 600.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 97 * 16, 94 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 175 * 16, 100 * 16, [
        make_field("radius", "Float", 220.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 190 * 16, 213 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.3),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 255 * 16, 91 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))
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

    # ================================================================
    # SESSION 14 FIDELITY PASS — CathedralDeep DS3 terrain details
    # ================================================================
    # Rain-soaked cemetery — tilted headstone rows (DS3: perpetual rain in graveyard)
    fill_tiles(chunk, TILE_WALL, 14, 8, 15, 9)
    fill_tiles(chunk, TILE_WALL, 20, 12, 21, 13)
    fill_tiles(chunk, TILE_WALL, 28, 6, 29, 7)
    fill_tiles(chunk, TILE_WALL, 38, 14, 39, 15)
    # Outer graveyard — broken coffin lids (DS3: disturbed graves everywhere)
    fill_tiles(chunk, TILE_WALL, 20, 26, 21, 27)
    fill_tiles(chunk, TILE_WALL, 36, 24, 37, 25)
    fill_tiles(chunk, TILE_WALL, 46, 28, 47, 29)
    fill_tiles(chunk, TILE_WALL, 16, 30, 17, 31)
    # Cathedral nave — gothic pillar bases (DS3: massive stone columns)
    fill_tiles(chunk, TILE_WALL, 50, 74, 51, 75)
    fill_tiles(chunk, TILE_WALL, 56, 80, 57, 81)
    fill_tiles(chunk, TILE_WALL, 62, 76, 63, 77)
    fill_tiles(chunk, TILE_WALL, 46, 82, 47, 83)
    # Deacon altar — candle cluster bases (DS3: mass of candles in dark hall)
    fill_tiles(chunk, TILE_WALL, 30, 116, 31, 117)
    fill_tiles(chunk, TILE_WALL, 44, 126, 45, 127)
    fill_tiles(chunk, TILE_WALL, 56, 116, 57, 117)
    fill_tiles(chunk, TILE_WALL, 38, 122, 39, 123)
    # Giant's room — arrow-scarred rubble (DS3: giant shoots arrows from above)
    fill_tiles(chunk, TILE_WALL, 62, 94, 63, 95)
    fill_tiles(chunk, TILE_WALL, 68, 100, 69, 101)
    fill_tiles(chunk, TILE_WALL, 58, 98, 59, 99)
    fill_tiles(chunk, TILE_WALL, 72, 96, 73, 97)

    # ================================================================
    # SESSION 17 FIDELITY PASS — CathedralDeep DS3 cathedral architecture
    # ================================================================
    # Cemetery — tombstone clusters (DS3: large cemetery at cathedral entrance)
    fill_tiles(chunk, TILE_WALL, 14, 40, 15, 42)
    fill_tiles(chunk, TILE_WALL, 22, 44, 23, 46)
    fill_tiles(chunk, TILE_WALL, 30, 38, 31, 40)
    fill_tiles(chunk, TILE_WALL, 18, 48, 19, 50)
    fill_tiles(chunk, TILE_WALL, 26, 50, 27, 52)
    # Cleansing Chapel — chapel altar stones (DS3: cleansing chapel with bonfire)
    fill_tiles(chunk, TILE_WALL, 34, 54, 35, 56)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 60)
    fill_tiles(chunk, TILE_WALL, 50, 52, 51, 54)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 58)
    # Cathedral nave — gothic pillar bases (DS3: massive cathedral interior)
    fill_tiles(chunk, TILE_WALL, 66, 60, 67, 62)
    fill_tiles(chunk, TILE_WALL, 74, 64, 75, 66)
    fill_tiles(chunk, TILE_WALL, 82, 58, 83, 60)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 64)
    # Side aisle — broken bench debris (DS3: pews and debris along cathedral sides)
    fill_tiles(chunk, TILE_WALL, 98, 66, 99, 68)
    fill_tiles(chunk, TILE_WALL, 106, 70, 107, 72)
    fill_tiles(chunk, TILE_WALL, 114, 64, 115, 66)
    fill_tiles(chunk, TILE_WALL, 122, 68, 123, 70)
    # Rosaria's chamber — bedchamber debris (DS3: Rosaria's bedchamber with slimes)
    fill_tiles(chunk, TILE_WALL, 40, 130, 41, 132)
    fill_tiles(chunk, TILE_WALL, 48, 134, 49, 136)
    fill_tiles(chunk, TILE_WALL, 54, 128, 55, 130)
    # Slug corridor — slime trail stones (DS3: slug-infested passage)
    fill_tiles(chunk, TILE_WALL, 62, 108, 63, 110)
    fill_tiles(chunk, TILE_WALL, 70, 112, 71, 114)
    fill_tiles(chunk, TILE_WALL, 78, 106, 79, 108)
    fill_tiles(chunk, TILE_WALL, 86, 110, 87, 112)

    # ================================================================
    # SESSION 22 FIDELITY PASS — CathedralDeep DS3 cathedral details
    # ================================================================
    # Cathedral column bases (DS3: stone column foundations in the cathedral)
    fill_tiles(chunk, TILE_WALL, 22, 32, 23, 33)
    fill_tiles(chunk, TILE_WALL, 28, 36, 29, 37)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 41)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    # Graveyard tombstone debris (DS3: tombstones in the cathedral graveyard)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 57)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    # Deacon prayer bench debris (DS3: pews and benches in the cathedral)
    fill_tiles(chunk, TILE_WALL, 70, 64, 71, 65)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 69)
    fill_tiles(chunk, TILE_WALL, 82, 72, 83, 73)
    fill_tiles(chunk, TILE_WALL, 88, 76, 89, 77)
    # Rosaria's chamber debris (DS3: broken glass and debris in Rosaria's chamber)
    fill_tiles(chunk, TILE_WALL, 94, 80, 95, 81)
    fill_tiles(chunk, TILE_WALL, 100, 84, 101, 85)
    fill_tiles(chunk, TILE_WALL, 106, 88, 107, 89)
    fill_tiles(chunk, TILE_WALL, 112, 92, 113, 93)

    # ================================================================
    # SESSION 26 FIDELITY PASS — CathedralDeep DS3 cathedral details
    # ================================================================
    # Cathedral exterior buttresses (DS3: flying buttresses on cathedral)
    fill_tiles(chunk, TILE_WALL, 20, 34, 21, 35)
    fill_tiles(chunk, TILE_WALL, 26, 38, 27, 39)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    fill_tiles(chunk, TILE_WALL, 38, 46, 39, 47)
    # Graveyard tombstone rows (DS3: tombstones in cathedral graveyard)
    fill_tiles(chunk, TILE_WALL, 44, 50, 45, 51)
    fill_tiles(chunk, TILE_WALL, 50, 54, 51, 55)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 62, 62, 63, 63)
    # Rosaria's chamber glass (DS3: stained glass in Rosaria's bedchamber)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 67)
    fill_tiles(chunk, TILE_WALL, 74, 70, 75, 71)
    fill_tiles(chunk, TILE_WALL, 80, 74, 81, 75)
    fill_tiles(chunk, TILE_WALL, 86, 78, 87, 79)
    # Deacon congregation hall debris (DS3: pews and altar debris)
    fill_tiles(chunk, TILE_WALL, 92, 82, 93, 83)
    fill_tiles(chunk, TILE_WALL, 98, 86, 99, 87)
    fill_tiles(chunk, TILE_WALL, 104, 90, 105, 91)
    fill_tiles(chunk, TILE_WALL, 110, 94, 111, 95)

    # ================================================================
    # SESSION 30 FIDELITY PASS — CathedralDeep DS3 cathedral details
    # ================================================================
    # Cathedral main nave columns (DS3: massive columns in the nave)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    # Deacon congregation pews (DS3: wooden pews in the cathedral)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    # Deep Accursed nest debris (DS3: debris near the Deep Accursed's lair)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    # Cathedral rooftops debris (DS3: debris on the cathedral rooftops)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)

    # SESSION 36 FIDELITY PASS — Cathedral of the Deep DS3 details
    # DS3: Cathedral buttresses, tombstone rows, pew lines, altar debris
    for tx in range(20, 50, 6):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+2, 42)             # Exterior buttresses
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+2, 82)
    for tx in range(60, 100, 4):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+1, 51)             # Pew row markers
        fill_tiles(chunk, TILE_WALL, tx, 90, tx+1, 91)
    for ty in range(30, 70, 8):
        fill_tiles(chunk, TILE_WALL, 45, ty, 46, ty+1)             # Interior columns
        fill_tiles(chunk, TILE_WALL, 85, ty, 86, ty+1)
    fill_tiles(chunk, TILE_WALL, 65, 35, 67, 37)                    # Altar platform
    fill_tiles(chunk, TILE_WALL, 110, 55, 112, 57)                  # Rosaria chamber entrance
    fill_tiles(chunk, TILE_WALL, 120, 70, 122, 72)                  # Grave warden area
    for tx in range(100, 130, 5):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)             # Exterior tombstones
    fill_tiles(chunk, TILE_WALL, 50, 95, 52, 97)                    # Cathedral entrance debris
    # SESSION 41 FIDELITY PASS — Cathedral of the Deep DS3 details
    # DS3: Deacon chamber, Rosaria's area, exterior graveyard, bridge supports
    for tx in range(25, 60, 5):
        fill_tiles(chunk, TILE_WALL, tx, 55, tx+1, 56)             # Deacon chamber floor tiles
        fill_tiles(chunk, TILE_WALL, tx, 95, tx+1, 96)
    for tx in range(65, 100, 5):
        fill_tiles(chunk, TILE_WALL, tx, 60, tx+1, 61)             # Cathedral interior tiles
        fill_tiles(chunk, TILE_WALL, tx, 100, tx+1, 101)
    for ty in range(35, 65, 7):
        fill_tiles(chunk, TILE_WALL, 50, ty, 51, ty+1)             # Interior arch columns
        fill_tiles(chunk, TILE_WALL, 90, ty, 91, ty+1)
    fill_tiles(chunk, TILE_WALL, 115, 50, 117, 52)                  # Rosaria's chamber entry
    fill_tiles(chunk, TILE_WALL, 130, 65, 132, 67)                  # Exterior graveyard stone
    fill_tiles(chunk, TILE_WALL, 40, 85, 42, 87)                    # Bridge support pillars
    for tx in range(105, 135, 6):
        fill_tiles(chunk, TILE_WALL, tx, 55, tx+1, 56)             # Cathedral approach stones
    # --- SESSION 47 terrain (Cathedral of the Deep) ---
    # DS3: Cathedral exterior buttresses
    for ty in range(20, 28):
        chunk[ty][35] = TILE_WALL
    for ty in range(22, 30):
        chunk[ty][55] = TILE_WALL
    # Pew rows inside the cathedral
    for tx in range(40, 50):
        chunk[35][tx] = TILE_WALLTOP
        chunk[37][tx] = TILE_WALLTOP
    # Altar platform
    for tx in range(60, 68):
        chunk[30][tx] = TILE_WALLTOP
    # Tombstones in the cemetery exterior
    for tx in range(15, 25):
        if tx % 3 == 0:
            chunk[40][tx] = TILE_WALLTOP

    # --- SESSION 55 terrain (Cathedral of the Deep final) ---
    # DS3: Cathedral exterior ravine bridge (DS3: the bridge over the ravine)
    for tx in range(20, 30):
        chunk[55][tx] = TILE_WALLTOP  # bridge planks
    # Rosaria's chamber alcove (DS3: the candlelit chamber)
    for ty in range(65, 72):
        chunk[ty][38] = TILE_WALL  # alcove wall
    # Cathedral ceiling arch supports
    for ty in range(25, 30):
        chunk[ty][48] = TILE_WALL  # arch support
    # Deacon prayer candles (DS3: candles in the Deacons' chamber)
    for tx, ty in [(82, 48), (88, 52), (94, 48)]:
        chunk[ty][tx] = TILE_WALLTOP  # candle debris
    # Cemetery gate pillars (DS3: the gate to the graveyard)
    for ty in range(32, 38):
        chunk[ty][12] = TILE_WALL  # gate pillar
        chunk[ty][16] = TILE_WALL  # gate pillar

    # --- SESSION 87 DS3 terrain (Cathedral of the Deep detail pass) ---
    # DS3: Main cathedral buttresses (flying buttresses)
    for tx in [20, 35, 50, 65, 80, 95]:
        for ty in range(15, 30):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Cathedral nave (long hall with pillars)
    for tx in [30, 40, 50, 60, 70, 80, 90, 100]:
        for ty in [35, 36]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][34] = TILE_WALLTOP
    # DS3: Pew rows in the nave
    for tx in [32, 34, 36, 38, 42, 44, 46, 48, 52, 54, 56, 58, 62, 64, 66, 68]:
        for ty in [40, 41]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Altar platform at the far end
    for tx in range(45, 60):
        for ty in [50, 51]:
            chunk[tx][ty] = TILE_WALL
    for tx in range(45, 61):
        chunk[tx][49] = TILE_WALLTOP
    # DS3: Exterior graveyard tombstones
    for tx in [15, 17, 19, 21, 23, 25, 27, 29]:
        for ty in [55, 57, 59]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Rosaria's chamber alcove
    for tx in range(85, 95):
        for ty in [65, 72]:
            chunk[tx][ty] = TILE_WALL
    for tx in [85, 95]:
        for ty in range(65, 73):
            chunk[tx][ty] = TILE_WALL
    for tx in range(85, 96):
        chunk[tx][64] = TILE_WALLTOP
    # DS3: Giant's room (large open chamber)
    for tx in range(100, 120):
        for ty in [75, 88]:
            chunk[tx][ty] = TILE_WALL
    for tx in [100, 120]:
        for ty in range(75, 89):
            chunk[tx][ty] = TILE_WALL
    # DS3: Deep puddles throughout the exterior (non-toxic water in DS3)
    # Removed TILE_POISON — Cathedral of the Deep has no poison terrain

    # --- SESSION 91 DS3 terrain round 2 (Cathedral of the Deep) ---
    # DS3: Cathedral exterior buttresses (arched supports)
    for tx in [18, 30, 42, 54, 66, 78]:
        for ty in range(10, 18):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Deep puddles (non-toxic water in DS3 cemetery)
    # Removed TILE_POISON — Cathedral of the Deep has no poison terrain
    # DS3: Patches' bridge (the spot where he kicks you)
    for tx in range(40, 55):
        chunk[tx][58] = TILE_WALL
        chunk[tx][57] = TILE_WALLTOP
    # DS3: Deacon ritual chamber
    for tx in range(70, 85):
        for ty in range(55, 65):
            chunk[tx][ty] = TILE_GROUND
    for tx in [70, 85]:
        for ty in range(55, 66):
            chunk[tx][ty] = TILE_WALL
    # DS3: Giant's archer position
    for tx in range(100, 108):
        for ty in [15, 25]:
            chunk[tx][ty] = TILE_WALL
    for tx in [100, 108]:
        for ty in range(15, 26):
            chunk[tx][ty] = TILE_WALL
    for tx in range(100, 109):
        chunk[tx][14] = TILE_WALLTOP
    # DS3: Cathedral roof access path
    for tx in range(85, 100):
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_GROUND
    for tx in [85, 100]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Rosaria's bed chamber (inner sanctum)
    for tx in range(88, 95):
        for ty in range(68, 74):
            chunk[tx][ty] = TILE_GROUND
    for tx in [88, 95]:
        for ty in range(68, 75):
            chunk[tx][ty] = TILE_WALL
    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 37 * 16, 31 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 43 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 56 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 93 * 16, 87 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Astora Straight Sword")]))
    entities.append(make_entity("Item", 106 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 143 * 16, 125 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 125 * 16, 131 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Deep Ring")]))
    entities.append(make_entity("Item", 131 * 16, 143 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Red Tearstone Ring")]))
    entities.append(make_entity("Item", 168 * 16, 103 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Cathedral Knight Set")]))
    entities.append(make_entity("Item", 187 * 16, 96 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 206 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 212 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Sunlight Straight Sword")]))
    entities.append(make_entity("Item", 254 * 16, 85 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Pale Tongue")]))
    entities.append(make_entity("Item", 187 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Paladin's Ashes")]))
    entities.append(make_entity("Item", 190 * 16, 215 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Boreal Valley")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 225 * 16, 53 * 16, [
        make_field("name", "String", "Unknown")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/CathedralDeep.json") as _f:

        _doc = _json.load(_f)

    for _sec in _doc.get("map_layout", {}).get("sections", []):

        _sx, _sy = _sec["x"] // 16, _sec["y"] // 16

        _sw, _sh = _sec["w"] // 16, _sec["h"] // 16

        _features = " ".join(f for f in _sec.get("terrain_features", []) if isinstance(f, str))

        _tile = poison_tile(_features)

        fill_tiles(chunk, _tile, _sx + 1, _sy + 1, _sx + _sw - 2, _sy + _sh - 2)

    # Connect sections with corridors

    _centers = []

    for _sec in _doc.get("map_layout", {}).get("sections", []):

        _cx = (_sec["x"] + _sec["w"] // 2) // 16

        _cy = (_sec["y"] + _sec["h"] // 2) // 16

        _centers.append((_cx, _cy))

    for _i in range(len(_centers) - 1):

        _cx1, _cy1 = _centers[_i]

        _cx2, _cy2 = _centers[_i + 1]

        carve_corridor(chunk, _cx1, _cy1, _cx2, _cy2, width=5)

    # Ensure bonfire/boss positions have ground

    for _bf in _doc.get("bonfires", []):

        _bx, _by = _bf["x"] // 16, _bf["y"] // 16

        fill_tiles(chunk, TILE_GROUND, _bx - 3, _by - 3, _bx + 3, _by + 3)

    _boss = _doc.get("boss")

    if _boss:

        for _b in (_boss if isinstance(_boss, list) else [_boss]):

            _bx, _by = _b.get("x", 0) // 16, _b.get("y", 0) // 16

            fill_tiles(chunk, TILE_GROUND, _bx - 5, _by - 5, _bx + 5, _by + 5)

    for _fg in _doc.get("fog_gates", []):

        _fx, _fy = _fg["x"] // 16, _fg["y"] // 16

        fill_tiles(chunk, TILE_GROUND, _fx - 3, _fy - 3, _fx + 3, _fy + 3)
    # Add terrain feature obstacles (walls) from JSON doc
    for _sec in _doc.get("map_layout", {}).get("sections", []):
        for _feat in _sec.get("terrain_features", []):
            if not isinstance(_feat, dict):
                continue
            _fk = _feat.get("kind", "")
            if _fk in ("tombstone", "bookshelf_wall", "pillar", "throne_pillar",
                        "barracks_wall", "bell_tower_column", "shrine_wall", "broken_wall",
                        "barricade", "collapsed_wall", "desk_cluster",
                        "roof_structure", "chimney", "armor_display", "iron_girder",
                        "coffin", "dragon_altar", "serpent_statue",
                        "arena_ruin", "ruined_pillar"):
                _fx2 = _feat["x"] // 16
                _fy2 = _feat["y"] // 16
                _fw = max(1, _feat["w"] // 16)
                _fh = max(1, _feat["h"] // 16)
                fill_tiles(chunk, TILE_WALL, _fx2, _fy2, _fx2 + _fw - 1, _fy2 + _fh - 1)

    # === SECTION-BASED GROUND EXPANSION (DS3 fidelity) ===
    # Cathedral of the Deep: massive cathedral with graveyard, rooftops, and Deacons altar
    fill_tiles(chunk, TILE_GROUND, 22, 26, 87, 72)   # Cathedral Approach Graveyard
    fill_tiles(chunk, TILE_GROUND, 78, 80, 121, 115)  # Cleansing Chapel
    fill_tiles(chunk, TILE_GROUND, 115, 111, 172, 158) # Giant Graveyard
    fill_tiles(chunk, TILE_GROUND, 153, 82, 215, 130)  # Cathedral Main Hall
    fill_tiles(chunk, TILE_GROUND, 193, 35, 255, 76)   # Rooftops and Buttresses
    fill_tiles(chunk, TILE_GROUND, 238, 67, 287, 106)  # Rosaria Route
    fill_tiles(chunk, TILE_GROUND, 73, 128, 128, 161)   # Patches Bridge and Well
    fill_tiles(chunk, TILE_GROUND, 162, 195, 226, 240)  # Deacons Altar
    # Corridors connecting sections
    fill_tiles(chunk, TILE_GROUND, 53, 47, 102, 99)
    fill_tiles(chunk, TILE_GROUND, 98, 95, 145, 137)
    fill_tiles(chunk, TILE_GROUND, 141, 104, 186, 137)
    fill_tiles(chunk, TILE_GROUND, 182, 53, 226, 108)
    fill_tiles(chunk, TILE_GROUND, 222, 53, 265, 88)
    fill_tiles(chunk, TILE_GROUND, 99, 84, 265, 147)
    fill_tiles(chunk, TILE_GROUND, 99, 143, 196, 219)

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0])) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100
    # print(f"  CathedralDeep (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "CathedralDeep", chunk, entities
