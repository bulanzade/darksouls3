from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

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
    chunk = new_chunk(256, 256)

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

    # Connection: tower area to residential north (wider for route connectivity)
    fill_tiles(chunk, TILE_GROUND, 44, 44, 62, 56)

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

    # Connection: cathedral to frost stairs (wider for route connectivity)
    fill_tiles(chunk, TILE_GROUND, 70, 108, 92, 116)

    # 10. VORDT ARENA — large oval at south end
    carve_ellipse(chunk, 100, 144, 22, 12)
    # Entry funnel from frost stairs to Vordt (wider for connectivity)
    fill_tiles(chunk, TILE_GROUND, 80, 130, 120, 148)

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

    # ================================================================
    # SESSION 11 FIDELITY PASS — LothricWall fine architectural details
    # ================================================================
    # Wall entrance — stone parapet debris (DS3: crumbling castle battlements)
    fill_tiles(chunk, TILE_WALL, 10, 8, 11, 9)
    fill_tiles(chunk, TILE_WALL, 32, 12, 33, 13)
    fill_tiles(chunk, TILE_WALL, 16, 16, 17, 17)
    fill_tiles(chunk, TILE_WALL, 28, 18, 29, 19)
    # Dragon walkway — scorched stone fragments (DS3: burned by wyvern fire)
    fill_tiles(chunk, TILE_WALL, 12, 22, 13, 23)
    fill_tiles(chunk, TILE_WALL, 22, 26, 23, 27)
    fill_tiles(chunk, TILE_WALL, 18, 30, 19, 31)
    fill_tiles(chunk, TILE_WALL, 26, 28, 27, 29)
    # Dragon bridge — fire-charred pillars (DS3: stone pillars scorched by dragon breath)
    fill_tiles(chunk, TILE_WALL, 14, 32, 15, 33)
    fill_tiles(chunk, TILE_WALL, 30, 36, 31, 37)
    fill_tiles(chunk, TILE_WALL, 38, 34, 39, 35)
    fill_tiles(chunk, TILE_WALL, 50, 38, 51, 39)
    fill_tiles(chunk, TILE_WALL, 42, 30, 43, 31)
    # Tower area — stone stair debris (DS3: spiral staircase in tower)
    fill_tiles(chunk, TILE_WALL, 50, 36, 51, 37)
    fill_tiles(chunk, TILE_WALL, 56, 40, 57, 41)
    fill_tiles(chunk, TILE_WALL, 68, 44, 69, 45)
    fill_tiles(chunk, TILE_WALL, 72, 48, 73, 49)
    # Residential maze — collapsed brick walls (DS3: narrow alleyways with ruined houses)
    fill_tiles(chunk, TILE_WALL, 28, 52, 29, 53)
    fill_tiles(chunk, TILE_WALL, 40, 54, 41, 55)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 64, 54, 65, 55)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 51)
    fill_tiles(chunk, TILE_WALL, 26, 60, 27, 61)
    fill_tiles(chunk, TILE_WALL, 38, 62, 39, 63)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    fill_tiles(chunk, TILE_WALL, 62, 58, 63, 59)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 61)
    fill_tiles(chunk, TILE_WALL, 34, 70, 35, 71)
    fill_tiles(chunk, TILE_WALL, 46, 72, 47, 73)
    fill_tiles(chunk, TILE_WALL, 58, 70, 59, 71)
    fill_tiles(chunk, TILE_WALL, 28, 76, 29, 77)
    fill_tiles(chunk, TILE_WALL, 42, 80, 43, 81)
    fill_tiles(chunk, TILE_WALL, 54, 76, 55, 77)
    # Courtyard — fountain basin stones (DS3: stone fountain in central square)
    fill_tiles(chunk, TILE_WALL, 12, 80, 13, 81)
    fill_tiles(chunk, TILE_WALL, 24, 88, 25, 89)
    fill_tiles(chunk, TILE_WALL, 40, 90, 41, 91)
    fill_tiles(chunk, TILE_WALL, 32, 94, 33, 95)
    fill_tiles(chunk, TILE_WALL, 48, 84, 49, 85)
    fill_tiles(chunk, TILE_WALL, 16, 92, 17, 93)
    fill_tiles(chunk, TILE_WALL, 52, 92, 53, 93)
    # Knight path — stone column bases (DS3: ornate columns along cathedral approach)
    fill_tiles(chunk, TILE_WALL, 60, 90, 61, 91)
    fill_tiles(chunk, TILE_WALL, 68, 94, 69, 95)
    fill_tiles(chunk, TILE_WALL, 80, 100, 81, 101)
    fill_tiles(chunk, TILE_WALL, 72, 102, 73, 103)
    # Cathedral — chapel column fragments (DS3: gothic chapel with stone pillars)
    fill_tiles(chunk, TILE_WALL, 66, 100, 67, 101)
    fill_tiles(chunk, TILE_WALL, 78, 104, 79, 105)
    fill_tiles(chunk, TILE_WALL, 90, 108, 91, 109)
    fill_tiles(chunk, TILE_WALL, 70, 110, 71, 111)
    fill_tiles(chunk, TILE_WALL, 86, 112, 87, 113)
    # Frost stairs — ice-cracked stone (DS3: frozen stairs leading to Vordt)
    fill_tiles(chunk, TILE_WALL, 94, 116, 95, 117)
    fill_tiles(chunk, TILE_WALL, 102, 120, 103, 121)
    fill_tiles(chunk, TILE_WALL, 98, 124, 99, 125)
    fill_tiles(chunk, TILE_WALL, 106, 128, 107, 129)
    fill_tiles(chunk, TILE_WALL, 92, 130, 93, 131)
    # Vordt arena — perimeter ice pillars (DS3: open snowy arena)
    fill_tiles(chunk, TILE_WALL, 88, 134, 89, 135)
    fill_tiles(chunk, TILE_WALL, 112, 134, 113, 135)
    fill_tiles(chunk, TILE_WALL, 92, 140, 93, 141)
    fill_tiles(chunk, TILE_WALL, 108, 140, 109, 141)
    fill_tiles(chunk, TILE_WALL, 96, 148, 97, 149)
    fill_tiles(chunk, TILE_WALL, 104, 148, 105, 149)

    # ENTITIES
    # ================================================================
    entities = []

    spawn_px, spawn_py = 18 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))
    entities.append(make_entity("BossSpawn", 197 * 16, 221 * 16, [make_field("name", "String", "Vordt of the Boreal Valley")]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 35 * 16, 22 * 16))    # Wall Entrance
    entities.append(make_entity("Bonfire", 96 * 16, 56 * 16))    # Tower on the Wall
    entities.append(make_entity("Bonfire", 197 * 16, 221 * 16))  # Dancer of the Boreal Valley
    entities.append(make_entity("Bonfire", 172 * 16, 161 * 16))  # Vordt of the Boreal Valley

    # --- Bosses ---
    # Vordt of the Boreal Valley — main boss at south arena

    # --- Enemies (DS3 High Wall of Lothric: Lothric Knights, Dogs, Hollow Soldiers) ---


    # ================================================================
    # Boss-to-main-cluster corridor (critical for playability)
    fill_tiles(chunk, TILE_GROUND, 140, 34, 190, 42)  # Twin Princes → main cluster
    fill_tiles(chunk, TILE_GROUND, 100, 34, 145, 50)  # Rooftop → Princes path
    fill_tiles(chunk, TILE_GROUND, 45, 50, 70, 65)    # Wax pool → Scholar tower

    # LATE CONNECTIVITY — corridors carved AFTER all wall placement
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 42, 42, 62, 56)     # Tower → Residential
    fill_tiles(chunk, TILE_GROUND, 20, 72, 40, 84)     # Residential → Courtyard
    fill_tiles(chunk, TILE_GROUND, 54, 84, 72, 96)     # Courtyard → Knight path
    fill_tiles(chunk, TILE_GROUND, 66, 94, 92, 108)    # Knight path → Cathedral
    fill_tiles(chunk, TILE_GROUND, 72, 108, 98, 118)   # Cathedral → Frost stairs
    fill_tiles(chunk, TILE_GROUND, 78, 118, 110, 145)  # Frost stairs → Vordt arena
    # Boss-to-main-cluster corridor
    fill_tiles(chunk, TILE_GROUND, 185, 180, 205, 230) # Vordt → main cluster

    # --- DS3 faithful enemies (LothricWall) ---
    # HollowSoldier (29)
    for tx, ty in [(14, 10), (22, 14), (16, 20), (48, 10), (18, 34), (28, 38), (40, 32), (52, 36), (50, 66), (74, 64), (40, 74), (56, 74), (34, 94), (52, 90), (70, 100), (88, 126), (34, 14), (60, 16), (44, 44), (64, 58), (28, 68), (72, 70), (26, 86), (58, 98), (85, 28), (96, 37), (83, 61), (94, 70), (120, 79)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowSoldier", "HollowSoldier"))]))
    # LothricKnight (20)
    for tx, ty in [(30, 18), (50, 54), (62, 54), (74, 54), (20, 84), (44, 96), (62, 94), (84, 98), (86, 96), (70, 106), (90, 108), (92, 115), (80, 118), (76, 134), (94, 138), (82, 14), (106, 18), (93, 23), (88, 42), (107, 65)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LothricKnight", "LothricKnight"))]))
    # Archer (1)
    entities.append(make_entity("Enemy", 54 * 16, 14 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Archer", "Archer"))]))
    # PusOfMan (2)
    entities.append(make_entity("Enemy", 50 * 16, 12 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    entities.append(make_entity("Enemy", 42 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    # LothricWyvern (1)
    entities.append(make_entity("Enemy", 24 * 16, 32 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LothricWyvern", "LothricWyvern"))]))
    # StarvedHound (6)
    entities.append(make_entity("Enemy", 16 * 16, 24 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 20 * 16, 28 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 18 * 16, 22 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 16 * 16, 92 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 46 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 100 * 16, 51 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    # WingedKnight (1)
    entities.append(make_entity("Enemy", 62 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("WingedKnight", "WingedKnight"))]))
    # CrystalLizard (2)
    entities.append(make_entity("Enemy", 58 * 16, 48 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 48 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # Mimic (1)
    entities.append(make_entity("Enemy", 42 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Mimic", "Mimic"))]))
    # LargeHollowSoldier (1)
    entities.append(make_entity("Enemy", 56 * 16, 46 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LargeHollowSoldier", "LargeHollowSoldier"))]))
    # HollowAssassin (5)
    entities.append(make_entity("Enemy", 38 * 16, 56 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 62 * 16, 66 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 44 * 16, 40 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 60 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 86 * 16, 75 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    # Darkwraith (1)
    entities.append(make_entity("Enemy", 54 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Darkwraith", "Darkwraith"))]))
    # Red-eyed LothricKnight — DS3: tough variant near Emma with buffed weapon
    entities.append(make_entity("Enemy", 82 * 16, 102 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LothricKnight", "LothricKnight"))]))

# --- NPCs ---
    # Greirat — locked in cell below tower (DS3: basement cell, asks for Loretta's Bone)
    entities.append(make_entity("Npc", 142 * 16, 118 * 16, [
        make_field("name", "String", "Greirat"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#A0A0A0"),
        make_field("dialogue", "String",
            "...Who are you?|Will you let me out of here?|I can show you a thing or two in return|I am Greirat of the Undead Settlement|If you could find Loretta... I owe her so much|Please, take this Blue Tearstone Ring as a token of my gratitude"),
    ]))
    # Emma — High Priestess in the cathedral (DS3: gives Small Lothric Banner, triggers Dancer)
    entities.append(make_entity("Npc", 170 * 16, 166 * 16, [
        make_field("name", "String", "Emma"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A0D0"),
        make_field("dialogue", "String",
            "Hello, Unkindled One|I am Emma, High Priestess of Lothric|Seek the Basin of Vows and present it to the statue behind me|Then you may see the Prince"),
    ]))

    # --- Chests (DS3 High Wall of Lothric) ---

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 30 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Longbow")]))
    entities.append(make_entity("Item", 38 * 16, 21 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 46 * 16, 26 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 26 * 16, 18 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 50 * 16, 35 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 56 * 16, 31 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 85 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Gold Pine Resin")]))
    entities.append(make_entity("Item", 101 * 16, 62 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    entities.append(make_entity("Item", 91 * 16, 67 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 111 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Throwing Knives")]))
    entities.append(make_entity("Item", 150 * 16, 52 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 158 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 87 * 16, 108 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 105 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 137 * 16, 87 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Cell Key")]))
    entities.append(make_entity("Item", 118 * 16, 108 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 155 * 16, 142 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Gold Pine Resin")]))
    entities.append(make_entity("Item", 168 * 16, 151 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 162 * 16, 168 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 158 * 16, 177 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 170 * 16, 159 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Small Lothric Banner")]))
    entities.append(make_entity("Item", 187 * 16, 206 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss")]))
    entities.append(make_entity("Item", 200 * 16, 217 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 191 * 16, 146 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 45 * 16, 28 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 102 * 16, 42 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 116 * 16, 98 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 163 * 16, 156 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 146 * 16, 125 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 193 * 16, 207 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    # Back to CemeteryOfAsh (NW entry point)
    entities.append(make_entity("FogGate", 35 * 16, 18 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 288.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))
    # To Undead Settlement (south of Vordt arena)
    entities.append(make_entity("FogGate", 197 * 16, 233 * 16, [
        make_field("dest_area", "String", "UndeadSettlement"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 80.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Lothric Castle (Dancer lift — post-Dancer area NE)
    entities.append(make_entity("FogGate", 191 * 16, 138 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 500.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Lothric Castle (post-Dancer path — DS3: Dancer defeat opens castle)
    entities.append(make_entity("FogGate", 182 * 16, 147 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    # Bonfire warm glow at entry
    entities.append(make_entity("Light", 35 * 16, 22 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.95), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.5)]))
    # Tower bonfire light
    entities.append(make_entity("Light", 96 * 16, 56 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.95), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.55), make_field("intensity", "Float", 0.5)]))
    # Wyvern fire glow on bridge
    entities.append(make_entity("Light", 135 * 16, 38 * 16, [
        make_field("radius", "Float", 320.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.1), make_field("intensity", "Float", 0.7)]))
    # Scorched bridge ambient fire
    entities.append(make_entity("Light", 118 * 16, 48 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.4)]))
    # Courtyard ambient daylight
    entities.append(make_entity("Light", 81 * 16, 100 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.85), make_field("g", "Float", 0.82),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.35)]))
    # Dim cell interior light
    entities.append(make_entity("Light", 142 * 16, 118 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.55),
        make_field("b", "Float", 0.45), make_field("intensity", "Float", 0.4)]))
    # Darkwraith cell abyss glow
    entities.append(make_entity("Light", 146 * 16, 112 * 16, [
        make_field("radius", "Float", 80.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.3),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.5)]))
    # Rooftop courtyard daylight
    entities.append(make_entity("Light", 165 * 16, 146 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.88),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.4)]))
    # Emma chapel candle glow
    entities.append(make_entity("Light", 170 * 16, 166 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.95), make_field("g", "Float", 0.9),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.55)]))
    # Dancer bonfire / chapel altar light
    entities.append(make_entity("Light", 172 * 16, 161 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.5)]))
    # Vordt arena icy blue frost glow
    entities.append(make_entity("Light", 197 * 16, 221 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.75),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.6)]))
    # Frost-covered stairs ambient cold light
    entities.append(make_entity("Light", 185 * 16, 210 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.55), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.95), make_field("intensity", "Float", 0.4)]))
    # Dancer arena dark twilight
    entities.append(make_entity("Light", 172 * 16, 161 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.45)]))
    # Vordt arena — cold boreal blue

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

    # ================================================================
    # SESSION 15 FIDELITY PASS — LothricWall additional DS3 details
    # ================================================================
    # High Wall ramparts — battlement merlons (DS3: crenellated stone walls)
    fill_tiles(chunk, TILE_WALL, 22, 20, 23, 21)
    fill_tiles(chunk, TILE_WALL, 28, 24, 29, 25)
    fill_tiles(chunk, TILE_WALL, 34, 22, 35, 23)
    fill_tiles(chunk, TILE_WALL, 40, 26, 41, 27)
    # Dragon bridge — scorched masonry (DS3: wyvern-scorched stone bridge)
    fill_tiles(chunk, TILE_WALL, 62, 34, 63, 35)
    fill_tiles(chunk, TILE_WALL, 68, 38, 69, 39)
    fill_tiles(chunk, TILE_WALL, 56, 36, 57, 37)
    # Greirat's cell — iron bar debris (DS3: locked cell below tower)
    fill_tiles(chunk, TILE_WALL, 38, 56, 39, 57)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 59)
    fill_tiles(chunk, TILE_WALL, 34, 54, 35, 55)
    # Lower plaza — market stall debris (DS3: market area with hollows)
    fill_tiles(chunk, TILE_WALL, 48, 70, 49, 71)
    fill_tiles(chunk, TILE_WALL, 54, 74, 55, 75)
    fill_tiles(chunk, TILE_WALL, 44, 72, 45, 73)
    # Winged Knight courtyard — tower base stones (DS3: courtyard with patrolling knight)
    fill_tiles(chunk, TILE_WALL, 62, 80, 63, 81)
    fill_tiles(chunk, TILE_WALL, 66, 84, 67, 85)
    fill_tiles(chunk, TILE_WALL, 58, 82, 59, 83)

    # SESSION 18 FIDELITY PASS — LothricWall DS3 high wall details
    # High wall battlements — stone crenellations (DS3: castle battlements with hollows)
    fill_tiles(chunk, TILE_WALL, 22, 22, 23, 24)
    fill_tiles(chunk, TILE_WALL, 30, 26, 31, 28)
    fill_tiles(chunk, TILE_WALL, 38, 30, 39, 32)
    fill_tiles(chunk, TILE_WALL, 46, 28, 47, 30)
    # Dragon perch — scorched stone debris (DS3: dragon roosts on high wall)
    fill_tiles(chunk, TILE_WALL, 54, 34, 55, 36)
    fill_tiles(chunk, TILE_WALL, 62, 38, 63, 40)
    fill_tiles(chunk, TILE_WALL, 70, 36, 71, 38)
    fill_tiles(chunk, TILE_WALL, 78, 40, 79, 42)
    # Lower wall — collapsed stair debris (DS3: crumbling stairs to lower area)
    fill_tiles(chunk, TILE_WALL, 86, 44, 87, 46)
    fill_tiles(chunk, TILE_WALL, 94, 48, 95, 50)
    fill_tiles(chunk, TILE_WALL, 82, 50, 83, 52)
    fill_tiles(chunk, TILE_WALL, 90, 54, 91, 56)
    # Emma's cathedral — altar stone fragments (DS3: Emma's cathedral with Basin of Vows)
    fill_tiles(chunk, TILE_WALL, 78, 106, 79, 108)
    fill_tiles(chunk, TILE_WALL, 84, 110, 85, 112)
    fill_tiles(chunk, TILE_WALL, 74, 112, 75, 114)
    fill_tiles(chunk, TILE_WALL, 82, 114, 83, 116)

    # ================================================================
    # SESSION 19 FIDELITY PASS — LothricWall DS3 high wall depth
    # ================================================================
    # High wall battlements — parapet stone debris (DS3: long wall with hollow soldiers)
    fill_tiles(chunk, TILE_WALL, 14, 16, 15, 18)
    fill_tiles(chunk, TILE_WALL, 22, 20, 23, 22)
    fill_tiles(chunk, TILE_WALL, 30, 24, 31, 26)
    fill_tiles(chunk, TILE_WALL, 38, 28, 39, 30)
    fill_tiles(chunk, TILE_WALL, 46, 32, 47, 34)
    # Tower interior — spiral stair stones (DS3: tower rooms with Lothric Knights)
    fill_tiles(chunk, TILE_WALL, 52, 36, 53, 38)
    fill_tiles(chunk, TILE_WALL, 58, 40, 59, 42)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 46)
    fill_tiles(chunk, TILE_WALL, 70, 48, 71, 50)
    fill_tiles(chunk, TILE_WALL, 76, 52, 77, 54)
    # Greirat's cell — prison cell walls (DS3: cell below the high wall)
    fill_tiles(chunk, TILE_WALL, 18, 56, 19, 58)
    fill_tiles(chunk, TILE_WALL, 24, 60, 25, 62)
    fill_tiles(chunk, TILE_WALL, 30, 64, 31, 66)
    fill_tiles(chunk, TILE_WALL, 36, 68, 37, 70)
    fill_tiles(chunk, TILE_WALL, 42, 72, 43, 74)
    # Vordt approach — frozen flagstones (DS3: cold stone path to Vordt)
    fill_tiles(chunk, TILE_WALL, 88, 128, 89, 130)
    fill_tiles(chunk, TILE_WALL, 96, 132, 97, 134)
    fill_tiles(chunk, TILE_WALL, 104, 136, 105, 138)
    fill_tiles(chunk, TILE_WALL, 112, 140, 113, 142)
    fill_tiles(chunk, TILE_WALL, 120, 144, 121, 146)

    # ================================================================
    # SESSION 23 FIDELITY PASS — LothricWall DS3 castle details
    # ================================================================
    # Rampart stairway debris (DS3: stone fragments on the wall stairways)
    fill_tiles(chunk, TILE_WALL, 110, 40, 111, 41)
    fill_tiles(chunk, TILE_WALL, 115, 44, 116, 45)
    fill_tiles(chunk, TILE_WALL, 120, 48, 121, 49)
    fill_tiles(chunk, TILE_WALL, 125, 52, 126, 53)
    # Dragon perch stones (DS3: wyvern perching spots on the wall)
    fill_tiles(chunk, TILE_WALL, 130, 56, 131, 57)
    fill_tiles(chunk, TILE_WALL, 135, 60, 136, 61)
    fill_tiles(chunk, TILE_WALL, 140, 64, 141, 65)
    fill_tiles(chunk, TILE_WALL, 145, 68, 146, 69)
    # Vordt arena stone debris (DS3: shattered stones in boss arena)
    fill_tiles(chunk, TILE_WALL, 92, 125, 93, 126)
    fill_tiles(chunk, TILE_WALL, 98, 130, 99, 131)
    fill_tiles(chunk, TILE_WALL, 104, 135, 105, 136)
    fill_tiles(chunk, TILE_WALL, 110, 140, 111, 141)

    # ================================================================
    # SESSION 28 FIDELITY PASS — LothricWall DS3 castle details
    # ================================================================
    # Castle gate portcullis debris (DS3: iron portcullis at castle gate)
    fill_tiles(chunk, TILE_WALL, 18, 32, 19, 33)
    fill_tiles(chunk, TILE_WALL, 24, 36, 25, 37)
    fill_tiles(chunk, TILE_WALL, 30, 40, 31, 41)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 45)
    # Dragon breath scorch marks (DS3: scorch marks from wyvern fire)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 56, 55, 57)
    fill_tiles(chunk, TILE_WALL, 60, 60, 61, 61)
    # Vordt arena frost debris (DS3: frost-covered stones in boss arena)
    fill_tiles(chunk, TILE_WALL, 66, 64, 67, 65)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    fill_tiles(chunk, TILE_WALL, 84, 76, 85, 77)
    # Emma's cathedral debris (DS3: debris near Emma's cathedral)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 81)
    fill_tiles(chunk, TILE_WALL, 96, 84, 97, 85)
    fill_tiles(chunk, TILE_WALL, 102, 88, 103, 89)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)

    # ================================================================
    # SESSION 31 FIDELITY PASS — LothricWall DS3 castle details
    # ================================================================
    # Castle armory debris (DS3: weapon racks in the castle armory)
    fill_tiles(chunk, TILE_WALL, 115, 42, 116, 43)
    fill_tiles(chunk, TILE_WALL, 120, 46, 121, 47)
    fill_tiles(chunk, TILE_WALL, 125, 50, 126, 51)
    fill_tiles(chunk, TILE_WALL, 130, 54, 131, 55)
    # Dragon roost ledges (DS3: ledges where dragons perch on the wall)
    fill_tiles(chunk, TILE_WALL, 135, 58, 136, 59)
    fill_tiles(chunk, TILE_WALL, 140, 62, 141, 63)
    fill_tiles(chunk, TILE_WALL, 145, 66, 146, 67)
    fill_tiles(chunk, TILE_WALL, 148, 70, 149, 71)
    # Dancer's chamber pillars (DS3: pillars in the Dancer boss room)
    fill_tiles(chunk, TILE_WALL, 95, 130, 96, 131)
    fill_tiles(chunk, TILE_WALL, 100, 135, 101, 136)
    fill_tiles(chunk, TILE_WALL, 105, 140, 106, 141)
    fill_tiles(chunk, TILE_WALL, 110, 145, 111, 146)
    # Oceiros path stones (DS3: stones along the path to Consumed King's Garden)
    fill_tiles(chunk, TILE_WALL, 120, 130, 121, 131)
    fill_tiles(chunk, TILE_WALL, 125, 135, 126, 136)
    fill_tiles(chunk, TILE_WALL, 130, 140, 131, 141)
    fill_tiles(chunk, TILE_WALL, 135, 145, 136, 146)

    # SESSION 38 FIDELITY PASS — High Wall of Lothric DS3 details
    # DS3: Dragon scorch marks, portcullis gates, frost debris near Vordt
    for tx in range(15, 45, 6):
        fill_tiles(chunk, TILE_WALL, tx, 32, tx+2, 33)             # Dragon scorch marks
        fill_tiles(chunk, TILE_WALL, tx, 72, tx+2, 73)
    for tx in range(60, 90, 5):
        fill_tiles(chunk, TILE_WALL, tx, 28, tx+1, 29)             # Wall embrasures
        fill_tiles(chunk, TILE_WALL, tx, 68, tx+1, 69)
    for ty in range(35, 65, 8):
        fill_tiles(chunk, TILE_WALL, 20, ty, 21, ty+1)             # Interior column bases
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 55, 52, 57)                    # Portcullis frame
    fill_tiles(chunk, TILE_WALL, 110, 45, 112, 47)                  # Frost debris near Vordt
    for tx in range(80, 120, 7):
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+1, 81)             # Courtyard cobblestones
    fill_tiles(chunk, TILE_WALL, 70, 90, 72, 92)                    # Tower rubble
    # SESSION 40 FIDELITY PASS — High Wall of Lothric DS3 details
    for tx in range(25, 65, 5):
        fill_tiles(chunk, TILE_WALL, tx, 38, tx+1, 39)
        fill_tiles(chunk, TILE_WALL, tx, 78, tx+1, 79)
    for tx in range(70, 110, 5):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+1, 43)
        fill_tiles(chunk, TILE_WALL, tx, 82, tx+1, 83)
    for ty in range(35, 65, 7):
        fill_tiles(chunk, TILE_WALL, 25, ty, 26, ty+1)
        fill_tiles(chunk, TILE_WALL, 105, ty, 106, ty+1)
    fill_tiles(chunk, TILE_WALL, 45, 58, 47, 60)
    fill_tiles(chunk, TILE_WALL, 90, 65, 92, 67)
    fill_tiles(chunk, TILE_WALL, 120, 50, 122, 52)
    # --- SESSION 43 terrain (High Wall of Lothric) ---
    # DS3: Dragon scorch marks on the bridge section
    for tx in range(46, 54):
        for ty in [14, 15]:
            chunk[ty][tx] = TILE_WALLTOP
    # Portcullis gate frame at castle entrance
    for ty in range(18, 22):
        chunk[ty][42] = TILE_WALL
    # Hollow burial alcoves in the lower passage walls
    for tx in range(20, 30):
        chunk[40][tx] = TILE_WALLTOP
        chunk[48][tx] = TILE_WALLTOP
    # Tower interior stone framework
    for ty in range(8, 14):
        chunk[ty][38] = TILE_WALL
        chunk[ty][40] = TILE_WALL
    # Rampart battlements (crenellations)
    for tx in range(30, 44):
        if tx % 2 == 0:
            chunk[6][tx] = TILE_WALLTOP
    # Vordt arena pillars
    for tx, ty in [(70, 58), (75, 62), (80, 58)]:
        chunk[ty][tx] = TILE_WALL
    # Courtyard well and cart debris
    chunk[34][22] = TILE_WALL
    chunk[34][23] = TILE_WALLTOP
    # Dancer cathedral approach columns
    for ty in range(60, 68):
        chunk[ty][68] = TILE_WALL

    # --- SESSION 58 terrain (High Wall of Lothric) ---
    # DS3: Vordt arena perimeter stones
    for tx in range(70, 82):
        if tx % 3 == 0:
            chunk[62][tx] = TILE_WALL  # arena boundary
    # Distant castle view balcony (DS3: you can see Lothric Castle from the wall)
    for ty in range(8, 12):
        chunk[ty][60] = TILE_WALL  # balcony rail
    # Courtyard fountain basin
    chunk[32][28] = TILE_WALL
    chunk[32][29] = TILE_WALLTOP
    # Prison cell bars near Greirat's cell
    for ty in range(58, 64):
        chunk[ty][34] = TILE_WALL  # cell bar
    # Tower staircase interior
    for ty in range(22, 28):
        chunk[ty][44] = TILE_WALL  # staircase wall

    # --- SESSION 86 DS3 terrain (Lothric Wall detail pass) ---
    # DS3: Dragon perch platform (the dead dragon spot)
    for tx in range(65, 78):
        for ty in range(8, 12):
            chunk[tx][ty] = TILE_WALL
    for tx in range(65, 78):
        chunk[tx][7] = TILE_WALLTOP
    # DS3: Scorch marks from dragon fire on the bridge
    for tx in range(45, 65):
        for ty in range(14, 18):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Vordt's arena - open area with pillars
    for tx in [85, 90, 95]:
        for ty in range(58, 68):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Portcullis gates at key passages
    for ty in range(20, 30):
        chunk[18][ty] = TILE_WALL
        chunk[48][ty] = TILE_WALL
    # DS3: Greirat's cell (basement area)
    for tx in range(10, 16):
        for ty in [45, 52]:
            chunk[tx][ty] = TILE_WALL
    for tx in [10, 16]:
        for ty in range(45, 53):
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 90 DS3 terrain round 2 (Lothric Wall) ---
    # DS3: Castle battlement crenellations
    for tx in range(10, 110):
        if tx % 4 < 2:
            chunk[tx][5] = TILE_WALL
            chunk[tx][4] = TILE_WALLTOP
    # DS3: Dragon scorch marks on bridge (burned ground)
    for tx in range(48, 62):
        for ty in range(15, 20):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Burial alcoves in the wall interior
    for tx in [25, 30, 35, 40, 55, 60, 65]:
        for ty in [40, 41]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Tower framework at the corner
    for tx in range(95, 105):
        for ty in [15, 25]:
            chunk[tx][ty] = TILE_WALL
    for tx in [95, 105]:
        for ty in range(15, 26):
            chunk[tx][ty] = TILE_WALL
    for tx in range(95, 106):
        chunk[tx][14] = TILE_WALLTOP
    # DS3: Emma's chapel interior
    for tx in range(80, 92):
        for ty in [32, 40]:
            chunk[tx][ty] = TILE_WALL
    for tx in [80, 92]:
        for ty in range(32, 41):
            chunk[tx][ty] = TILE_WALL
    for tx in range(80, 93):
        chunk[tx][31] = TILE_WALLTOP
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/LothricWall.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("LothricWall", chunk, entities, spawn_px, spawn_py)
