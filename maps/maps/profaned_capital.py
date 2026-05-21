from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

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
    chunk = new_chunk(256, 256)

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

    # Connection bridge between jailer rooms (wider for route connectivity)
    fill_tiles(chunk, TILE_GROUND, 42, 4, 72, 26)

    # Second jailer room (jailers + gargoyle + 2 mimics + 1 real chest)
    fill_tiles(chunk, TILE_GROUND, 68, 6, 90, 24)
    # Pillar
    fill_tiles(chunk, TILE_WALL, 76, 10, 78, 14)
    # Side chests area
    fill_tiles(chunk, TILE_WALL, 84, 16, 86, 20)

    # Connection to Yhorm arena (wider for route connectivity)
    fill_tiles(chunk, TILE_GROUND, 82, 8, 102, 22)

    # Yhorm's throne room — large NE arena
    carve_ellipse(chunk, 108, 18, 20, 16)
    fill_tiles(chunk, TILE_GROUND, 88, 4, 130, 36)
    # Throne pillars
    fill_tiles(chunk, TILE_WALL, 96, 8, 98, 12)
    fill_tiles(chunk, TILE_WALL, 118, 24, 120, 28)

    # 4. EXPLORE PATH — descent south from bonfire tower (wider for route)
    fill_tiles(chunk, TILE_GROUND, 8, 18, 28, 42)

    # Upper ruins — connecting area (wider for route connectivity)
    fill_tiles(chunk, TILE_GROUND, 12, 30, 50, 52)
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

    # Giant room — east side (wider for route connectivity)
    fill_tiles(chunk, TILE_GROUND, 58, 50, 92, 76)
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
    # SESSION 12 FIDELITY PASS — ProfanedCapital fine architectural details
    # ================================================================
    # Entry bridge — iron gate debris (DS3: gate from Irithyll Dungeon)
    fill_tiles(chunk, TILE_WALL, 5, 9, 6, 10)
    fill_tiles(chunk, TILE_WALL, 8, 11, 9, 12)
    fill_tiles(chunk, TILE_WALL, 3, 13, 4, 14)
    # Bonfire tower — spiral stair rubble (DS3: Gilligan's body room)
    fill_tiles(chunk, TILE_WALL, 15, 7, 16, 8)
    fill_tiles(chunk, TILE_WALL, 21, 15, 22, 16)
    fill_tiles(chunk, TILE_WALL, 17, 19, 18, 20)
    fill_tiles(chunk, TILE_WALL, 25, 11, 26, 12)
    # Boss path bridge — fire vessel pedestals (DS3: fire containers line bridge)
    fill_tiles(chunk, TILE_WALL, 31, 11, 32, 12)
    fill_tiles(chunk, TILE_WALL, 35, 13, 36, 14)
    fill_tiles(chunk, TILE_WALL, 43, 9, 44, 10)
    fill_tiles(chunk, TILE_WALL, 47, 15, 48, 16)
    fill_tiles(chunk, TILE_WALL, 51, 7, 52, 8)
    fill_tiles(chunk, TILE_WALL, 57, 11, 58, 12)
    fill_tiles(chunk, TILE_WALL, 63, 9, 64, 10)
    fill_tiles(chunk, TILE_WALL, 67, 13, 68, 14)
    # Jailer rooms — cell bar debris (DS3: prison cells with branding irons)
    fill_tiles(chunk, TILE_WALL, 51, 9, 52, 10)
    fill_tiles(chunk, TILE_WALL, 57, 15, 58, 16)
    fill_tiles(chunk, TILE_WALL, 63, 11, 64, 12)
    fill_tiles(chunk, TILE_WALL, 73, 9, 74, 10)
    fill_tiles(chunk, TILE_WALL, 79, 15, 80, 16)
    fill_tiles(chunk, TILE_WALL, 85, 11, 86, 12)
    fill_tiles(chunk, TILE_WALL, 71, 17, 72, 18)
    fill_tiles(chunk, TILE_WALL, 81, 13, 82, 14)
    # Yhorm arena — throne pedestal stones (DS3: massive throne room)
    fill_tiles(chunk, TILE_WALL, 99, 5, 100, 6)
    fill_tiles(chunk, TILE_WALL, 111, 9, 112, 10)
    fill_tiles(chunk, TILE_WALL, 103, 19, 104, 20)
    fill_tiles(chunk, TILE_WALL, 115, 23, 116, 24)
    fill_tiles(chunk, TILE_WALL, 97, 27, 98, 28)
    fill_tiles(chunk, TILE_WALL, 121, 13, 122, 14)
    fill_tiles(chunk, TILE_WALL, 107, 29, 108, 30)
    fill_tiles(chunk, TILE_WALL, 129, 17, 130, 18)
    # Upper ruins — collapsed fountain (DS3: ruined capital square)
    fill_tiles(chunk, TILE_WALL, 19, 35, 20, 36)
    fill_tiles(chunk, TILE_WALL, 25, 39, 26, 40)
    fill_tiles(chunk, TILE_WALL, 33, 37, 34, 38)
    fill_tiles(chunk, TILE_WALL, 39, 43, 40, 44)
    fill_tiles(chunk, TILE_WALL, 29, 41, 30, 42)
    fill_tiles(chunk, TILE_WALL, 37, 35, 38, 36)
    # Streets — overturned cart debris (DS3: ruined capital streets)
    fill_tiles(chunk, TILE_WALL, 25, 53, 26, 54)
    fill_tiles(chunk, TILE_WALL, 37, 57, 38, 58)
    fill_tiles(chunk, TILE_WALL, 45, 61, 46, 62)
    fill_tiles(chunk, TILE_WALL, 55, 55, 56, 56)
    fill_tiles(chunk, TILE_WALL, 33, 63, 34, 64)
    # Toxic pool — corroded metal debris (DS3: flooded toxic area)
    fill_tiles(chunk, TILE_WALL, 47, 67, 48, 68)
    fill_tiles(chunk, TILE_WALL, 57, 73, 58, 74)
    fill_tiles(chunk, TILE_WALL, 65, 77, 66, 78)
    fill_tiles(chunk, TILE_WALL, 51, 75, 52, 76)
    fill_tiles(chunk, TILE_WALL, 61, 69, 62, 70)
    # Church — altar stone fragments (DS3: church with Monstrosities)
    fill_tiles(chunk, TILE_WALL, 27, 73, 28, 74)
    fill_tiles(chunk, TILE_WALL, 41, 77, 42, 78)
    fill_tiles(chunk, TILE_WALL, 35, 83, 36, 84)
    fill_tiles(chunk, TILE_WALL, 29, 69, 30, 70)
    # Siegward cell — iron bar fragments (DS3: cell holding Siegward)
    fill_tiles(chunk, TILE_WALL, 59, 47, 60, 48)
    fill_tiles(chunk, TILE_WALL, 65, 53, 66, 54)
    fill_tiles(chunk, TILE_WALL, 55, 49, 56, 50)
    # Court sorcerer roof — chimney debris (DS3: rooftop above church)
    fill_tiles(chunk, TILE_WALL, 49, 41, 50, 42)
    fill_tiles(chunk, TILE_WALL, 57, 45, 58, 46)
    fill_tiles(chunk, TILE_WALL, 61, 39, 62, 40)
    fill_tiles(chunk, TILE_WALL, 45, 43, 46, 44)
    # Giant room — chain debris (DS3: treasure room with giant)
    fill_tiles(chunk, TILE_WALL, 71, 59, 72, 60)
    fill_tiles(chunk, TILE_WALL, 79, 65, 80, 66)
    fill_tiles(chunk, TILE_WALL, 85, 61, 86, 62)
    fill_tiles(chunk, TILE_WALL, 77, 69, 78, 70)
    fill_tiles(chunk, TILE_WALL, 83, 57, 84, 58)
    # Shortcut corridor — stone arch debris (DS3: shortcut back to dungeon)
    fill_tiles(chunk, TILE_WALL, 87, 61, 88, 62)
    fill_tiles(chunk, TILE_WALL, 91, 65, 92, 66)
    fill_tiles(chunk, TILE_WALL, 93, 59, 94, 60)

    # ================================================================
    # DS3 POISON TERRAIN — Profaned Capital flooded cells and toxic pool
    # ================================================================
    # Flooded cells — stagnant water (DS3: waterlogged prison cells below capital)
    fill_tiles(chunk, TILE_POISON, 66, 60, 82, 70)
    fill_tiles(chunk, TILE_POISON, 70, 68, 78, 76)
    fill_tiles(chunk, TILE_POISON, 74, 72, 86, 80)
    # Toxic pool expansion — more POISON tiles in SE area
    fill_tiles(chunk, TILE_POISON, 45, 70, 58, 78)
    fill_tiles(chunk, TILE_POISON, 50, 76, 65, 84)
    # Fire-scorched ground near palace ruins (DS3: profaned flame damage)
    fill_tiles(chunk, TILE_POISON, 46, 48, 56, 54)

        # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    spawn_px, spawn_py = 18 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 56 * 16, 51 * 16))     # Profaned Capital
    entities.append(make_entity("Bonfire", 187 * 16, 201 * 16))    # Yhorm the Giant

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 187 * 16, 201 * 16))

    # --- Enemies ---
    # DS3 Profaned Capital enemies: Handmaids (Jailer), Gargoyles (Headless),
    # Monstrosities of Sin (MonstrosityOfSin), Sewer Centipedes (SewerCentipede),
    # Rats, Crystal Lizards, Mimic

    
    # ================================================================
    # LATE CONNECTIVITY — corridors carved AFTER all wall placement
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 8, 8, 30, 30)      # Bonfire tower → upper
    fill_tiles(chunk, TILE_GROUND, 20, 20, 50, 40)     # Upper → Explore path
    fill_tiles(chunk, TILE_GROUND, 30, 36, 60, 52)     # Explore → Upper ruins
    fill_tiles(chunk, TILE_GROUND, 40, 48, 68, 62)     # Upper ruins → Siegward
    fill_tiles(chunk, TILE_GROUND, 55, 52, 85, 70)     # Siegward → Giant room
    fill_tiles(chunk, TILE_GROUND, 10, 30, 48, 50)     # Bonfire → First jailer
    fill_tiles(chunk, TILE_GROUND, 42, 2, 90, 26)      # First jailer → Second → Yhorm
    fill_tiles(chunk, TILE_GROUND, 82, 4, 135, 36)     # Jailer rooms → Yhorm arena
    # Boss-to-main-cluster corridor
    fill_tiles(chunk, TILE_GROUND, 100, 170, 200, 210) # Yhorm → main cluster
    fill_tiles(chunk, TILE_GROUND, 60, 170, 110, 200)  # Upper ruins → Yhorm path

    # --- DS3 faithful enemies (ProfanedCapital) ---
    # Gargoyle (10)
    for tx, ty in [(10, 11), (44, 12), (48, 14), (64, 14), (88, 8), (34, 52), (50, 60), (108, 2), (129, 15), (124, 34)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Gargoyle", "Gargoyle"))]))
    # Jailer (17)
    for tx, ty in [(52, 10), (54, 14), (60, 8), (62, 18), (72, 10), (74, 16), (80, 12), (20, 38), (30, 42), (38, 44), (26, 56), (24, 48), (40, 55), (32, 60), (62, 48), (90, 7), (128, 22)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Jailer", "Jailer"))]))
    # SewerCentipede (9)
    for tx, ty in [(52, 64), (60, 72), (66, 68), (70, 60), (74, 66), (80, 62), (95, 11), (115, 26), (94, 31)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SewerCentipede", "SewerCentipede"))]))
    # CrystalLizard (3)
    entities.append(make_entity("Enemy", 56 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 62 * 16, 64 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 56 * 16, 44 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # MonstrosityOfSin (6)
    entities.append(make_entity("Enemy", 30 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MonstrosityOfSin", "MonstrosityOfSin"))]))
    entities.append(make_entity("Enemy", 36 * 16, 78 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MonstrosityOfSin", "MonstrosityOfSin"))]))
    entities.append(make_entity("Enemy", 42 * 16, 74 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MonstrosityOfSin", "MonstrosityOfSin"))]))
    entities.append(make_entity("Enemy", 48 * 16, 46 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MonstrosityOfSin", "MonstrosityOfSin"))]))
    entities.append(make_entity("Enemy", 58 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MonstrosityOfSin", "MonstrosityOfSin"))]))
    entities.append(make_entity("Enemy", 64 * 16, 74 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MonstrosityOfSin", "MonstrosityOfSin"))]))
    # JailerHandmaid (4 â DS3: stronger jailer variant in upper prison rooms)
    for tx, ty in [(56, 10), (62, 18), (80, 12), (38, 44)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("JailerHandmaid", "Jailer"))]))
    # AvariciousBeing (1 â DS3: on rooftop near bonfire, drops items when killed)
    entities.append(make_entity("Enemy", 18 * 16, 12 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("AvariciousBeing", "Mimic"))]))
    # MiniBoss (1)
    entities.append(make_entity("Enemy", 48 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    # GiantSlave (1)
    entities.append(make_entity("Enemy", 76 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))

# --- NPCs ---
    # Siegward — in cell
    entities.append(make_entity("Npc", 115 * 16, 111 * 16, [
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
        ("SoulOrb", "Large Soul of a Weary Warrior", 50, 12, 1000),
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
        ("ArmorDrop", "Court Sorcerer Set", 46, 44, 0),
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

    # --- Chests — DS3 Profaned Capital (wiki-verified) ---

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 52 * 16, 43 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 103 * 16, 102 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Arrow"),
        make_field("name", "String", "Poison Arrow")]))
    entities.append(make_entity("Item", 101 * 16, 151 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 86 * 16, 147 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Arrow"),
        make_field("name", "String", "Onislayer Greatarrow")]))
    entities.append(make_entity("Item", 130 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 186 * 16, 162 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 181 * 16, 156 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Blooming Purple Moss Clump")]))
    entities.append(make_entity("Item", 82 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Bolt"),
        make_field("name", "String", "Lightning Bolt")]))
    entities.append(make_entity("Item", 136 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 106 * 16, 121 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purging Stone")]))
    entities.append(make_entity("Item", 110 * 16, 121 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Poison Gem")]))
    entities.append(make_entity("Item", 117 * 16, 147 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Cursebite Ring")]))
    entities.append(make_entity("Item", 118 * 16, 148 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Shriving Stone")]))
    entities.append(make_entity("Item", 113 * 16, 121 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Arrow"),
        make_field("name", "String", "Dragonslayer Lightning Arrow")]))
    entities.append(make_entity("Item", 93 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Gold Coin")]))
    entities.append(make_entity("Item", 81 * 16, 155 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Eleonora")]))
    entities.append(make_entity("Item", 100 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Court Sorcerer Set")]))
    entities.append(make_entity("Item", 106 * 16, 98 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Logan's Scroll")]))
    entities.append(make_entity("Item", 108 * 16, 101 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Rubbish")]))
    entities.append(make_entity("Item", 53 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gesture"),
        make_field("name", "String", "Stretch Out Gesture")]))
    entities.append(make_entity("Item", 117 * 16, 110 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Covetous Gold Serpent Ring")]))
    entities.append(make_entity("Item", 112 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Jailer's Key Ring")]))
    entities.append(make_entity("Item", 115 * 16, 112 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Prisoner Chief's Ashes")]))
    entities.append(make_entity("Item", 111 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Wrath of the Gods")]))
    entities.append(make_entity("Item", 128 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Spell"),
        make_field("name", "String", "Profaned Flame")]))
    entities.append(make_entity("Item", 135 * 16, 116 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 138 * 16, 116 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 187 * 16, 200 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Storm Ruler")]))
    entities.append(make_entity("Item", 187 * 16, 202 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of Yhorm the Giant")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 137 * 16, 106 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 171 * 16, 157 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 167 * 16, 160 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 133 * 16, 115 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 178 * 16, 155 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    # Back to Irithyll Dungeon (NW entry)
    entities.append(make_entity("FogGate", 56 * 16, 45 * 16, [
        make_field("dest_area", "String", "IrithyllDungeon"),
        make_field("dest_x", "Float", 2500.0),
        make_field("dest_y", "Float", 2300.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 56 * 16, 51 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 107 * 16, 132 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 81 * 16, 153 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 187 * 16, 201 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    # Church — dim orange

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

    # ================================================================
    # SESSION 18 FIDELITY PASS — ProfanedCapital DS3 throne and prison details
    # ================================================================
    # Yhorm's throne room — fallen columns and debris (DS3: crumbling massive throne room)
    fill_tiles(chunk, TILE_WALL, 96, 12, 98, 14)
    fill_tiles(chunk, TILE_WALL, 104, 18, 106, 20)
    fill_tiles(chunk, TILE_WALL, 116, 14, 118, 16)
    fill_tiles(chunk, TILE_WALL, 124, 22, 126, 24)
    fill_tiles(chunk, TILE_WALL, 134, 10, 136, 12)
    # Jailer patrol corridors — cell dividers (DS3: narrow prison corridors with cells)
    fill_tiles(chunk, TILE_WALL, 34, 50, 36, 52)
    fill_tiles(chunk, TILE_WALL, 42, 54, 44, 56)
    fill_tiles(chunk, TILE_WALL, 50, 50, 52, 52)
    fill_tiles(chunk, TILE_WALL, 58, 56, 60, 58)
    fill_tiles(chunk, TILE_WALL, 38, 58, 40, 60)
    # Gargoyle roosts — perch pillars (DS3: gargoyles perch on high ledges)
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 54)
    fill_tiles(chunk, TILE_WALL, 82, 56, 84, 58)
    fill_tiles(chunk, TILE_WALL, 76, 60, 78, 62)
    # Monstrosity church — broken pews (DS3: ruined church with monstrosities of sin)
    fill_tiles(chunk, TILE_WALL, 28, 74, 30, 76)
    fill_tiles(chunk, TILE_WALL, 36, 78, 38, 80)
    fill_tiles(chunk, TILE_WALL, 44, 74, 46, 76)
    # Sewer centipede pools — slime edges (DS3: sewer centipedes lurk in pools)
    fill_tiles(chunk, TILE_WALL, 54, 70, 56, 72)
    fill_tiles(chunk, TILE_WALL, 64, 74, 66, 76)
    fill_tiles(chunk, TILE_WALL, 60, 80, 62, 82)

    # ================================================================
    # SESSION 21 FIDELITY PASS — ProfanedCapital DS3 ruins details
    # ================================================================
    # Yhorm arena pillar fragments (DS3: massive shattered pillars in Yhorm's hall)
    fill_tiles(chunk, TILE_WALL, 94, 10, 96, 12)
    fill_tiles(chunk, TILE_WALL, 100, 14, 102, 16)
    fill_tiles(chunk, TILE_WALL, 106, 18, 108, 20)
    fill_tiles(chunk, TILE_WALL, 112, 22, 114, 24)
    # Collapsed roof tile piles (DS3: destroyed rooftop debris from Profaned Flame)
    fill_tiles(chunk, TILE_WALL, 30, 22, 32, 24)
    fill_tiles(chunk, TILE_WALL, 36, 26, 38, 28)
    fill_tiles(chunk, TILE_WALL, 42, 30, 44, 32)
    fill_tiles(chunk, TILE_WALL, 48, 34, 50, 36)
    # Sewer grate debris (DS3: rusted grates in the toxic lower passage)
    fill_tiles(chunk, TILE_WALL, 54, 42, 56, 44)
    fill_tiles(chunk, TILE_WALL, 60, 46, 62, 48)
    fill_tiles(chunk, TILE_WALL, 66, 50, 68, 52)
    fill_tiles(chunk, TILE_WALL, 72, 54, 74, 56)
    # Gargoyle perch stones (DS3: gargoyle landing spots on building ledges)
    fill_tiles(chunk, TILE_WALL, 22, 48, 24, 50)
    fill_tiles(chunk, TILE_WALL, 28, 52, 30, 54)
    fill_tiles(chunk, TILE_WALL, 34, 56, 36, 58)
    fill_tiles(chunk, TILE_WALL, 40, 60, 42, 62)
    # Profaned Flame scorch marks (DS3: burned ground near the flame's origin)
    fill_tiles(chunk, TILE_WALL, 46, 64, 48, 66)
    fill_tiles(chunk, TILE_WALL, 52, 68, 54, 70)
    fill_tiles(chunk, TILE_WALL, 58, 72, 60, 74)
    fill_tiles(chunk, TILE_WALL, 64, 76, 66, 78)

    # ================================================================
    # SESSION 24 FIDELITY PASS — ProfanedCapital DS3 capital details
    # ================================================================
    # Yhorm's machete marks (DS3: Yhorm's giant blade marks on walls)
    fill_tiles(chunk, TILE_WALL, 22, 32, 23, 33)
    fill_tiles(chunk, TILE_WALL, 28, 36, 29, 37)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 41)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    # Profaned Flame scorch marks (DS3: burned areas from the Profaned Flame)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 57)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    # Sewer grate debris (DS3: rusted grates in the lower passages)
    fill_tiles(chunk, TILE_WALL, 70, 64, 71, 65)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 69)
    fill_tiles(chunk, TILE_WALL, 82, 72, 83, 73)
    fill_tiles(chunk, TILE_WALL, 88, 76, 89, 77)
    # Gargoyle perch ledges (DS3: stone ledges where gargoyles land)
    fill_tiles(chunk, TILE_WALL, 94, 80, 95, 81)
    fill_tiles(chunk, TILE_WALL, 100, 84, 101, 85)
    fill_tiles(chunk, TILE_WALL, 106, 88, 107, 89)
    fill_tiles(chunk, TILE_WALL, 112, 92, 113, 93)

    # ================================================================
    # SESSION 30 FIDELITY PASS — ProfanedCapital DS3 capital details
    # ================================================================
    # Yhorm's great machete marks (DS3: deep cuts in walls from Yhorm's blade)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    # Profaned Flame embers (DS3: smoldering embers from the Profaned Flame)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    # Capital rooftop debris (DS3: shattered rooftops from the flame)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    # Siegward's cell debris (DS3: debris near Siegward's imprisonment)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)

    # ================================================================
    # SESSION 33 FIDELITY PASS — ProfanedCapital DS3 capital details
    # ================================================================
    # Yhorm's arena column bases (DS3: massive columns in Yhorm's hall)
    fill_tiles(chunk, TILE_WALL, 16, 34, 17, 35)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    fill_tiles(chunk, TILE_WALL, 28, 42, 29, 43)
    fill_tiles(chunk, TILE_WALL, 34, 46, 35, 47)
    # Profaned Flame crystal growth (DS3: flame crystals in the capital)
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 51)
    fill_tiles(chunk, TILE_WALL, 46, 54, 47, 55)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 59)
    fill_tiles(chunk, TILE_WALL, 58, 62, 59, 63)
    # Capital courtyard stones (DS3: scattered stones in the courtyard)
    fill_tiles(chunk, TILE_WALL, 64, 66, 65, 67)
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 71)
    fill_tiles(chunk, TILE_WALL, 76, 74, 77, 75)
    fill_tiles(chunk, TILE_WALL, 82, 78, 83, 79)
    # Sewer passage debris (DS3: debris in the toxic sewers)
    fill_tiles(chunk, TILE_WALL, 88, 82, 89, 83)
    fill_tiles(chunk, TILE_WALL, 94, 86, 95, 87)
    fill_tiles(chunk, TILE_WALL, 100, 90, 101, 91)
    fill_tiles(chunk, TILE_WALL, 106, 94, 107, 95)

    # SESSION 40 FIDELITY PASS — Profaned Capital DS3 details
    for tx in range(25, 65, 6):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+2, 37)
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+2, 77)
    for tx in range(70, 110, 6):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 41)
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+1, 81)
    for ty in range(30, 70, 8):
        fill_tiles(chunk, TILE_WALL, 40, ty, 41, ty+1)
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)
    fill_tiles(chunk, TILE_WALL, 120, 50, 122, 52)
    fill_tiles(chunk, TILE_WALL, 80, 90, 82, 92)
    # SESSION 42 FIDELITY PASS — Profaned Capital DS3 details
    # DS3: Yhorm arena details, sewer tunnels, gargoyle roosts, earthen peak ruins
    for tx in range(25, 60, 5):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+1, 43)             # Sewer tunnel markers
        fill_tiles(chunk, TILE_WALL, tx, 82, tx+1, 83)
    for tx in range(65, 100, 5):
        fill_tiles(chunk, TILE_WALL, tx, 47, tx+1, 48)             # Gargoyle roost posts
        fill_tiles(chunk, TILE_WALL, tx, 87, tx+1, 88)
    for ty in range(35, 70, 7):
        fill_tiles(chunk, TILE_WALL, 45, ty, 46, ty+1)             # Capital column bases
        fill_tiles(chunk, TILE_WALL, 105, ty, 106, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 62)                    # Earthen peak ruin
    fill_tiles(chunk, TILE_WALL, 120, 55, 122, 57)                  # Toxic pool edge
    fill_tiles(chunk, TILE_WALL, 80, 95, 82, 97)                    # Collapsed tower
    for tx in range(110, 140, 6):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+1, 51)             # Capital wall debris
    # --- SESSION 53 terrain (Profaned Capital final) ---
    # DS3: Yhorm's throne room debris (the giant's throne area)
    for tx in range(80, 90):
        chunk[60][tx] = TILE_WALLTOP  # throne debris
    # Profaned flame pools (DS3: fire pools that burn eternally)
    for tx, ty in [(45, 50), (60, 55)]:
        chunk[ty][tx] = TILE_WALLTOP  # flame pool edge
    # Sewer channel grating (DS3: the sewers beneath the capital)
    for tx in range(30, 40):
        chunk[65][tx] = TILE_WALLTOP  # grate
    # Gargoyle perch ledges (DS3: gargoyles sit on building edges)
    for tx, ty in [(70, 45), (85, 50)]:
        chunk[ty][tx] = TILE_WALL  # ledge
    # Capital wall buttress
    for ty in range(35, 42):
        chunk[ty][55] = TILE_WALL  # buttress

    # --- SESSION 89 DS3 terrain (Profaned Capital detail pass) ---
    # DS3: Yhorm's arena pillars (the giant stone columns)
    for tx in [25, 40, 55, 70]:
        for ty in range(15, 35):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Arena floor (open boss chamber)
    for tx in range(20, 75):
        for ty in range(38, 55):
            chunk[tx][ty] = TILE_GROUND
    for tx in [20, 75]:
        for ty in range(38, 56):
            chunk[tx][ty] = TILE_WALL
    for tx in range(20, 76):
        for ty in [38, 55]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Roof tiles on upper structures
    for tx in range(80, 100):
        chunk[tx][20] = TILE_WALL
        chunk[tx][19] = TILE_WALLTOP
    # DS3: Sewer grates in the lower section
    for tx in range(30, 50):
        for ty in range(60, 68):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Gargoyle perch points on rooftops
    for tx in [85, 90, 95, 100, 105]:
        for ty in [22, 23]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][21] = TILE_WALLTOP
    # DS3: Toxic pools in the lower area
    for tx in range(50, 70):
        for ty in range(70, 80):
            chunk[tx][ty] = TILE_POISON
    # DS3: Staircase connecting levels
    for tx in range(75, 82):
        for ty in range(25, 45):
            chunk[tx][ty] = TILE_GROUND
    for tx in [75, 82]:
        for ty in range(25, 46):
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 92 DS3 terrain round 2 (Profaned Capital) ---
    # DS3: Yhorm's throne (stone seat in the arena)
    for tx in range(42, 50):
        for ty in [42, 43]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][41] = TILE_WALLTOP
    # DS3: Upper walkway with Sewer Centipedes
    for tx in range(60, 85):
        chunk[tx][25] = TILE_WALL
        chunk[tx][24] = TILE_WALLTOP
    # DS3: Dungeon cells below the capital
    for tx in [20, 28, 36, 44]:
        for ty in range(60, 70):
            chunk[tx][ty] = TILE_WALL
    # DS3: Gargoyle perch platform
    for tx in range(85, 100):
        for ty in [15, 18]:
            chunk[tx][ty] = TILE_WALL
    for tx in [85, 100]:
        for ty in range(15, 19):
            chunk[tx][ty] = TILE_WALL
    for tx in range(85, 101):
        chunk[tx][14] = TILE_WALLTOP
    # DS3: Monstrosity lair (dark chamber)
    for tx in range(40, 60):
        for ty in range(75, 88):
            chunk[tx][ty] = TILE_GROUND
    for tx in [40, 60]:
        for ty in range(75, 89):
            chunk[tx][ty] = TILE_WALL
    # DS3: Entrance staircase from Irithyll Dungeon
    for tx in range(10, 18):
        for ty in range(30, 42):
            chunk[tx][ty] = TILE_GROUND
    for tx in [10, 18]:
        for ty in range(30, 43):
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/ProfanedCapital.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("ProfanedCapital", chunk, entities, spawn_px, spawn_py)
