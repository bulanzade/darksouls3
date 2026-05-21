from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_undead_settlement():
    """Undead Settlement — faithful DS3 layout.

    Progression: Entry (top-left) → House Street → Giant Tower → Bonfire Square
    → Cliffside Path → Fire Demon Square → Pilgrim Camp → Irina's Cell.
    Pit of Hollows (Greatwood boss) below Bonfire Square.

    Real DS3 features: narrow alleys between wooden houses, Giant throwing spears,
    Siegward assisting vs Fire Demon, Evangelists with maces, hanging corpses.
    """
    chunk = new_chunk(320, 256)

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

    # Connection: cliffside to pilgrim camp (wider for route)
    fill_tiles(chunk, TILE_GROUND, 105, 34, 125, 48)

    # Connection: fire demon to Irina's cell
    fill_tiles(chunk, TILE_GROUND, 112, 52, 140, 58)

    # 10. CLIFF UNDERSIDE (below village)
    fill_tiles(chunk, TILE_GROUND, 50, 76, 78, 92)
    carve_ellipse(chunk, 64, 84, 10, 7)
    # Connection: cliff underside to Greatwood (wider for route)
    fill_tiles(chunk, TILE_GROUND, 58, 88, 82, 105)

    # 11. PIT OF HOLLOWS / GREATWOOD ARENA (bottom-center)
    carve_ellipse(chunk, 90, 110, 24, 22)
    # Path down from bonfire square to Greatwood (wider for connectivity)
    fill_tiles(chunk, TILE_GROUND, 62, 60, 100, 100)
    carve_corridor(chunk, 78, 68, 84, 92, width=8)

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
    # SESSION 13 FIDELITY PASS — Undead Settlement DS3 architecture
    # ================================================================
    # Pilgrim camp — body wrappings and prayer stones (DS3: pilgrims in rows)
    fill_tiles(chunk, TILE_WALL, 116, 28, 117, 29)
    fill_tiles(chunk, TILE_WALL, 122, 34, 123, 35)
    fill_tiles(chunk, TILE_WALL, 130, 32, 131, 33)
    fill_tiles(chunk, TILE_WALL, 126, 38, 127, 39)
    fill_tiles(chunk, TILE_WALL, 134, 34, 135, 35)
    fill_tiles(chunk, TILE_WALL, 120, 40, 121, 41)
    fill_tiles(chunk, TILE_WALL, 138, 30, 139, 31)
    # Irina's graveyard — scattered tombstones (DS3: small graveyard outside cell)
    fill_tiles(chunk, TILE_WALL, 142, 52, 143, 53)
    fill_tiles(chunk, TILE_WALL, 148, 56, 149, 57)
    fill_tiles(chunk, TILE_WALL, 144, 48, 145, 49)
    fill_tiles(chunk, TILE_WALL, 150, 54, 151, 55)
    fill_tiles(chunk, TILE_WALL, 142, 58, 143, 59)
    fill_tiles(chunk, TILE_WALL, 146, 46, 147, 47)
    # Cliff underside — hanging cages (DS3: cages hanging from cliff underside)
    fill_tiles(chunk, TILE_WALL, 54, 78, 55, 79)
    fill_tiles(chunk, TILE_WALL, 62, 82, 63, 83)
    fill_tiles(chunk, TILE_WALL, 70, 80, 71, 81)
    fill_tiles(chunk, TILE_WALL, 58, 88, 59, 89)
    fill_tiles(chunk, TILE_WALL, 66, 90, 67, 91)
    fill_tiles(chunk, TILE_WALL, 74, 86, 75, 87)
    # Sewer grate area — drainage stones (DS3: sewer grates near rats)
    fill_tiles(chunk, TILE_WALL, 76, 78, 77, 79)
    fill_tiles(chunk, TILE_WALL, 80, 82, 81, 83)
    fill_tiles(chunk, TILE_WALL, 84, 80, 85, 81)
    fill_tiles(chunk, TILE_WALL, 78, 84, 79, 85)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 77)
    # House street — second floor balconies (DS3: houses have upper floors)
    fill_tiles(chunk, TILE_WALL, 40, 22, 41, 23)
    fill_tiles(chunk, TILE_WALL, 46, 28, 47, 29)
    fill_tiles(chunk, TILE_WALL, 54, 30, 55, 31)
    fill_tiles(chunk, TILE_WALL, 60, 38, 61, 39)
    fill_tiles(chunk, TILE_WALL, 42, 36, 43, 37)
    fill_tiles(chunk, TILE_WALL, 52, 44, 53, 45)
    fill_tiles(chunk, TILE_WALL, 36, 42, 37, 43)
    # Giant tower — arrow slits (DS3: tower with arrow slits)
    fill_tiles(chunk, TILE_WALL, 48, 20, 49, 21)
    fill_tiles(chunk, TILE_WALL, 52, 22, 53, 23)
    fill_tiles(chunk, TILE_WALL, 46, 28, 47, 29)
    # Greatwood pit — hanging bodies and roots (DS3: pit has bodies hanging from ceiling)
    fill_tiles(chunk, TILE_WALL, 86, 96, 87, 97)
    fill_tiles(chunk, TILE_WALL, 94, 94, 95, 95)
    fill_tiles(chunk, TILE_WALL, 90, 112, 91, 113)
    fill_tiles(chunk, TILE_WALL, 102, 106, 103, 107)
    fill_tiles(chunk, TILE_WALL, 88, 108, 89, 109)
    fill_tiles(chunk, TILE_WALL, 96, 102, 97, 103)
    # Cliffside path — hanging corpse posts (DS3: corpses hang from posts)
    fill_tiles(chunk, TILE_WALL, 88, 36, 89, 37)
    fill_tiles(chunk, TILE_WALL, 96, 40, 97, 41)
    fill_tiles(chunk, TILE_WALL, 100, 44, 101, 45)
    fill_tiles(chunk, TILE_WALL, 106, 36, 107, 37)
    fill_tiles(chunk, TILE_WALL, 112, 42, 113, 43)


    # ================================================================
    # DS3 STRUCTURAL WALLS — Undead Settlement village architecture
    # DS3: village with wooden houses, narrow alleys, hanging corpses,
    # burning tree square, greatwood pit, and giant tower
    # ================================================================
    # Settlement entry — wooden house facades (DS3: houses line narrow streets)
    fill_tiles(chunk, TILE_WALL, 24, 28, 28, 34)    # House wall left
    fill_tiles(chunk, TILE_WALL, 40, 26, 44, 32)    # House wall right
    fill_tiles(chunk, TILE_WALL, 32, 36, 36, 42)    # Back alley wall
    # Burning tree square — building walls (DS3: open square with blazing tree)
    fill_tiles(chunk, TILE_WALL, 50, 44, 54, 50)    # Square building left
    fill_tiles(chunk, TILE_WALL, 66, 42, 70, 48)    # Square building right
    fill_tiles(chunk, TILE_WALL, 56, 52, 60, 58)    # Square center wall
    # Multi-story house interior (DS3: house shortcut through village)
    fill_tiles(chunk, TILE_WALL, 28, 54, 32, 60)    # House interior wall 1
    fill_tiles(chunk, TILE_WALL, 38, 56, 42, 62)    # House interior wall 2
    fill_tiles(chunk, TILE_WALL, 32, 64, 36, 68)    # House floor divider
    # Evangelist patrol area — church-like structure (DS3: Evangelists in building)
    fill_tiles(chunk, TILE_WALL, 60, 60, 64, 66)    # Church wall left
    fill_tiles(chunk, TILE_WALL, 74, 58, 78, 64)    # Church wall right
    fill_tiles(chunk, TILE_WALL, 66, 66, 70, 72)    # Church rear wall
    # Giant tower area — stone tower walls (DS3: giant with greatbow)
    fill_tiles(chunk, TILE_WALL, 82, 44, 86, 50)    # Tower base wall
    fill_tiles(chunk, TILE_WALL, 94, 46, 98, 52)    # Tower support wall
    # Greatwood pit — arena walls (DS3: Curse-rotted Greatwood boss pit)
    fill_tiles(chunk, TILE_WALL, 76, 86, 80, 92)    # Pit wall NW
    fill_tiles(chunk, TILE_WALL, 96, 84, 100, 90)   # Pit wall NE
    fill_tiles(chunk, TILE_WALL, 78, 100, 82, 106)   # Pit wall SW
    fill_tiles(chunk, TILE_WALL, 94, 98, 98, 104)    # Pit wall SE
    # Cliffside path — stone retaining walls (DS3: path along cliff edge)
    fill_tiles(chunk, TILE_WALL, 90, 32, 94, 36)    # Retaining wall
    fill_tiles(chunk, TILE_WALL, 104, 38, 108, 42)   # Cliff wall
        # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    spawn_px, spawn_py = 18 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 26 * 16, 22 * 16))   # Foot of the High Wall
    entities.append(make_entity("Bonfire", 156 * 16, 106 * 16))   # Undead Settlement
    entities.append(make_entity("Bonfire", 205 * 16, 136 * 16))   # Cliff Underside
    entities.append(make_entity("Bonfire", 187 * 16, 206 * 16))   # Dilapidated Bridge
    entities.append(make_entity("Bonfire", 90 * 16, 112 * 16))  # Pit of Hollows

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 187 * 16, 206 * 16))

    # --- Enemies (DS3 Undead Settlement: Peasant Hollows, Evangelists, Thralls) ---

    
    # ================================================================
    # LATE CONNECTIVITY — corridors carved AFTER all wall placement
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 14, 18, 30, 30)     # Entry → Settlement street
    fill_tiles(chunk, TILE_GROUND, 30, 28, 55, 42)     # Street → Central square
    fill_tiles(chunk, TILE_GROUND, 50, 40, 75, 55)     # Square → Burning tree
    fill_tiles(chunk, TILE_GROUND, 70, 50, 100, 65)    # Burning tree → Fire demon
    fill_tiles(chunk, TILE_GROUND, 60, 58, 95, 80)     # Central → Cliff underside
    fill_tiles(chunk, TILE_GROUND, 55, 78, 100, 100)   # Cliff → Greatwood arena
    fill_tiles(chunk, TILE_GROUND, 96, 95, 115, 120)   # Greatwood arena wider
    # Boss-to-main-cluster corridor
    fill_tiles(chunk, TILE_GROUND, 180, 160, 205, 215) # Greatwood → main cluster

    # --- DS3 faithful enemies (UndeadSettlement) ---
    # DS3 wiki: Hollow Soldiers, Peasant Hollows, Starved Hounds, Evangelists,
    # Thralls, Rats, Fire Demon, Giant Slave, Skeletons, Crystal Lizard,
    # Boreal Knight, Holy Knight Hodrick

    # StarvedHound (7) — DS3: 3 at portcullis, 2 behind overturned coach, 1 guarding ember, 1 at ladder
    for tx, ty in [(20, 15), (22, 16), (18, 17),   # portcullis release (3)
                   (36, 25), (38, 27),               # behind overturned coach (2)
                   (88, 42),                          # guarding ember near sewers
                   (168, 108)]:                       # at ladder near sewers
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))

    # PeasantHollow (8 additional — DS3: pitchfork/torch hollows at gate, rooftops, cliff side)
    for tx, ty in [(28, 20),    # gate lever hollow
                   (34, 26),    # road hollow near pilgrims
                   (52, 30),    # short hollow in house
                   (80, 45),    # rooftop hollow
                   (108, 48),   # second rooftop hollow
                   (160, 105),  # hollow near dilapidated bridge
                   (200, 140),  # cliff underside hollow
                   (175, 190)]: # hollow near Greatwood courtyard
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PeasantHollow", "PeasantHollow"))]))

    # PeasantHollow (15) — DS3: pitchfork/hat hollows throughout settlement
    for tx, ty in [(42, 28),    # first house pitchfork hollow
                   (46, 32),    # first house second
                   (58, 38),    # house street
                   (62, 42),    # house street lower
                   (68, 48),    # near burning tree square
                   (130, 80),   # gang of enemies beyond fire
                   (135, 85),   # gang second
                   (140, 82),   # gang third
                   (92, 62),    # Cornyx area ledge
                   (96, 66),    # Cornyx area ledge second
                   (122, 70),   # mindless hollows sitting around
                   (160, 195),  # Greatwood prayer hollows
                   (170, 190),  # Greatwood prayer second
                   (180, 195),  # Greatwood prayer third
                   (148, 115)]: # lower settlement hollow
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PeasantHollow", "PeasantHollow"))]))

    # Evangelist (3) — DS3: 1 praying at blazing fire, 2 on upper structure near Fire Demon
    entities.append(make_entity("Enemy", 132 * 16, 82 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))
    for tx, ty in [(230, 95), (240, 100)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Evangelist", "Evangelist"))]))

    # Thrall (10) — DS3: many drop ambushes from ceilings in houses and rooftops
    for tx, ty in [(50, 30),    # drops in first house
                   (55, 35),    # drops in house street
                   (65, 40),    # drops near square
                   (70, 46),    # ceiling drop near bonfire square
                   (100, 55),   # thrall on rooftop path
                   (105, 60),   # second rooftop thrall
                   (150, 112),  # drops in hallway near sewers
                   (156, 116),  # short hollow drops from ceiling
                   (126, 76),   # thrall ambush near Cornyx area
                   (166, 122)]: # thrall in lower area
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Thrall", "Thrall"))]))

    # Rat (6) — DS3: 3 small + 1 big in sewers, 2 more near sewer entrance
    for tx, ty in [(155, 120), (158, 123), (162, 126),   # 3 small rats in sewers
                   (166, 118),                             # big rat (drops Bloodbite Ring)
                   (148, 116), (152, 119)]:                # 2 near sewer entrance
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Rat", "Rat"))]))

    # FireDemon (1) — DS3: fights alongside Siegward in lower area
    entities.append(make_entity("Enemy", 220 * 16, 95 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))

    # GiantSlave (1) — DS3: Giant atop tower with greatbow, shoots spears
    entities.append(make_entity("Enemy", 195 * 16, 58 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))

    # Skeleton (5) — DS3: near Irina's cell behind Grave Key door, in graveyard
    for tx, ty in [(188, 135), (192, 138), (196, 142), (200, 140), (204, 136)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Skeleton", "Skeleton"))]))

    # CrystalLizard (1) — DS3: near Hodrick invasion area / cliff path
    entities.append(make_entity("Enemy", 172 * 16, 110 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))

    # BorealKnight (1) — DS3: Outrider Knight of the Boreal Valley at lift
    entities.append(make_entity("Enemy", 265 * 16, 155 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BorealKnight", "Knight"))]))

    # Hodrick (1) — DS3: Holy Knight Hodrick, Mad Spirit invades near Dilapidated Bridge
    entities.append(make_entity("Enemy", 172 * 16, 115 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Hodrick", "MiniBoss"))]))

# --- NPCs (DS3 Undead Settlement: Yoel, Siegward, Cornyx) ---
    # Yoel of Londor — among the pilgrims at the entrance (DS3: offers free levels)
    entities.append(make_entity("Npc", 219 * 16, 63 * 16, [
        make_field("name", "String", "Yoel of Londor"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A4A5A"),
        make_field("dialogue", "String",
            "Ahh, a kind soul. I am Yoel of Londor, a pilgrim|Let me grant you true strength|Come. Touch the darkness within me|We are pilgrims, drawn to the fire|When the time comes, I shall die peacefully|The Abyss beckons, do you feel it?"),
    ]))
    # Siegward of Catarina — at Fire Demon square (DS3: helps fight the demon)
    entities.append(make_entity("Npc", 211 * 16, 96 * 16, [
        make_field("name", "String", "Siegward"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#C0A060"),
        make_field("dialogue", "String",
            "Aah, hello again|Let us fight this demon together!|Oh, very good. Very good indeed|I am Siegward of Catarina, a knight|This demon has been giving me trouble|Care for some Estus soup after the battle?"),
    ]))
    # Cornyx — pyromancy trainer in cage on rooftop (DS3: freed from cage, offers pyromancies)
    entities.append(make_entity("Npc", 90 * 16, 60 * 16, [
        make_field("name", "String", "Cornyx"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#B8860B"),
        make_field("dialogue", "String",
            "A pyromancy student? Very well|I can teach you the flame arts|Ah, the flame is a fickle thing, as unpredictable as a woman|I am Cornyx, pyromancer of the Great Swamp|Thank you for freeing me from this cage|Bring me tomes, and I shall share my knowledge"),
    ]))
    # Irina of Carim — miracle teacher in cell (DS3: found through locked door in sewers, near skeletons)
    entities.append(make_entity("Npc", 235 * 16, 141 * 16, [
        make_field("name", "String", "Irina of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7D9B"),
        make_field("dialogue", "String",
            "Oh, hello there. I am Irina of Carim|I can teach you miracles, if you bring me braille divine tomes|Please, take me to the shrine, I beg of you|I cannot see, but I can feel the light|The tales of the gods bring me comfort|Eygon has been my protector, but I worry for him"),
    ]))
    # Eygon of Carim — guards Irina (DS3: found outside near Irina, warns about the champion)
    entities.append(make_entity("Npc", 238 * 16, 136 * 16, [
        make_field("name", "String", "Eygon of Carim"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A3A2A"),
        make_field("dialogue", "String",
            "Keep your hands off the woman|I am Eygon of Carim, of the Morne bloodline|She is my responsibility, not yours|You would do well to remember that|I made a promise, and I intend to keep it|The blind woman is under my protection"),
    ]))

    # --- Items (DS3 Undead Settlement) ---

    # --- Chests (DS3 Undead Settlement) ---

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 22 * 16, 15 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 23 * 16, 21 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Alluring Skull")]))
    entities.append(make_entity("Item", 28 * 16, 25 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 90 * 16, 61 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Small Leather Shield")]))
    entities.append(make_entity("Item", 92 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Charcoal Pine Bundle")]))
    entities.append(make_entity("Item", 95 * 16, 71 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Loretta's Bone")]))
    entities.append(make_entity("Item", 87 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Repair Powder")]))
    entities.append(make_entity("Item", 90 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Charcoal Pine Bundle")]))
    entities.append(make_entity("Item", 90 * 16, 77 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 92 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember (behind blazing fire)")]))
    entities.append(make_entity("Item", 100 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 112 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Caduceus Round Shield")]))
    entities.append(make_entity("Item", 118 * 16, 77 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Plank Shield")]))
    entities.append(make_entity("Item", 127 * 16, 85 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Reinforced Club")]))
    entities.append(make_entity("Item", 131 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 145 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Hand Axe")]))
    entities.append(make_entity("Item", 148 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler")]))
    entities.append(make_entity("Item", 153 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Fire Clutch Ring")]))
    entities.append(make_entity("Item", 113 * 16, 97 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember (past sewers)")]))
    entities.append(make_entity("Item", 121 * 16, 96 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Bloodbite Ring")]))
    entities.append(make_entity("Item", 117 * 16, 96 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Caestus")]))
    entities.append(make_entity("Item", 127 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Loincloth")]))
    entities.append(make_entity("Item", 131 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Red Hilted Halberd")]))
    entities.append(make_entity("Item", 171 * 16, 128 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler")]))
    entities.append(make_entity("Item", 175 * 16, 135 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 178 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 181 * 16, 131 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Talisman"),
        make_field("name", "String", "Saint's Talisman")]))
    entities.append(make_entity("Item", 102 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard (house near Dilapidated Bridge)")]))
    entities.append(make_entity("Item", 96 * 16, 93 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Covenant"),
        make_field("name", "String", "Warriors of Sunlight Covenant")]))
    entities.append(make_entity("Item", 100 * 16, 96 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Charcoal Pine Resin")]))
    entities.append(make_entity("Item", 106 * 16, 83 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (lower house)")]))
    entities.append(make_entity("Item", 112 * 16, 95 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Whip")]))
    entities.append(make_entity("Item", 118 * 16, 96 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (ladder to bridge)")]))
    entities.append(make_entity("Item", 213 * 16, 96 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 211 * 16, 91 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Fading Soul")]))
    entities.append(make_entity("Item", 198 * 16, 81 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Red Bug Pellet")]))
    entities.append(make_entity("Item", 195 * 16, 87 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Large Club")]))
    entities.append(make_entity("Item", 206 * 16, 93 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Alluring Skull")]))
    entities.append(make_entity("Item", 210 * 16, 91 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Flynn's Ring")]))
    entities.append(make_entity("Item", 206 * 16, 77 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Chloranthy Ring")]))
    entities.append(make_entity("Item", 262 * 16, 158 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Irithyll Straight Sword (Boreal Knight drop)")]))
    entities.append(make_entity("Item", 228 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Fading Soul (giant spear area)")]))
    entities.append(make_entity("Item", 231 * 16, 105 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember (giant spear area)")]))
    entities.append(make_entity("Item", 225 * 16, 97 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 238 * 16, 102 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Mortician's Ashes")]))
    entities.append(make_entity("Item", 241 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Cleric Set")]))
    entities.append(make_entity("Item", 236 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 187 * 16, 200 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone (Pit of Hollows)")]))
    entities.append(make_entity("Item", 105 * 16, 86 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 98 * 16, 91 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (wall base)")]))
    entities.append(make_entity("Item", 150 * 16, 87 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Spell"),
        make_field("name", "String", "Pyromancy Flame")]))
    entities.append(make_entity("Item", 187 * 16, 207 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Rotted")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 207 * 16, 95 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    entities.append(make_entity("FogGate", 26 * 16, 16 * 16, [
        make_field("dest_area", "String", "RoadOfSacrifices"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 270 * 16, 156 * 16, [
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

    # ================================================================
    # SESSION 15 FIDELITY PASS — UndeadSettlement additional DS3 details
    # ================================================================
    # Burning tree square — scorched cobblestones (DS3: burning tree with hollows gathered)
    fill_tiles(chunk, TILE_WALL, 42, 46, 43, 47)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 38, 44, 39, 45)
    fill_tiles(chunk, TILE_WALL, 50, 50, 51, 51)
    # Giant tower — arrow-scarred masonry (DS3: Giant shoots arrows from tower)
    fill_tiles(chunk, TILE_WALL, 108, 78, 109, 80)
    fill_tiles(chunk, TILE_WALL, 112, 82, 113, 84)
    fill_tiles(chunk, TILE_WALL, 104, 80, 105, 82)
    fill_tiles(chunk, TILE_WALL, 116, 76, 117, 78)
    # Fire Demon plaza — scorched ground debris (DS3: Fire Demon battle area)
    fill_tiles(chunk, TILE_WALL, 86, 56, 87, 58)
    fill_tiles(chunk, TILE_WALL, 90, 60, 91, 62)
    fill_tiles(chunk, TILE_WALL, 82, 54, 83, 56)
    fill_tiles(chunk, TILE_WALL, 94, 58, 95, 60)
    # Dilapidated bridge — broken railing stones (DS3: wooden bridge with gaps)
    fill_tiles(chunk, TILE_WALL, 56, 66, 57, 68)
    fill_tiles(chunk, TILE_WALL, 62, 70, 63, 72)
    fill_tiles(chunk, TILE_WALL, 52, 68, 53, 70)
    fill_tiles(chunk, TILE_WALL, 68, 72, 69, 74)
    # Cliff underside — root-tangled debris (DS3: area beneath the settlement)
    fill_tiles(chunk, TILE_WALL, 22, 80, 23, 82)
    fill_tiles(chunk, TILE_WALL, 28, 84, 29, 86)
    fill_tiles(chunk, TILE_WALL, 34, 88, 35, 90)
    fill_tiles(chunk, TILE_WALL, 18, 86, 19, 88)

    # SESSION 18 FIDELITY PASS — UndeadSettlement DS3 village details
    # Tree sentinel area — hollow tree stumps (DS3: dead trees around settlement)
    fill_tiles(chunk, TILE_WALL, 40, 92, 41, 94)
    fill_tiles(chunk, TILE_WALL, 46, 96, 47, 98)
    fill_tiles(chunk, TILE_WALL, 52, 90, 53, 92)
    fill_tiles(chunk, TILE_WALL, 58, 94, 59, 96)
    # Pit area — rope net debris (DS3: pit with hollows and rats)
    fill_tiles(chunk, TILE_WALL, 64, 98, 65, 100)
    fill_tiles(chunk, TILE_WALL, 70, 102, 71, 104)
    fill_tiles(chunk, TILE_WALL, 76, 96, 77, 98)
    fill_tiles(chunk, TILE_WALL, 82, 100, 83, 102)
    # Mound maker cage — cage debris (DS3: cage elevator to giant)
    fill_tiles(chunk, TILE_WALL, 88, 104, 89, 106)
    fill_tiles(chunk, TILE_WALL, 94, 108, 95, 110)
    fill_tiles(chunk, TILE_WALL, 100, 102, 101, 104)
    fill_tiles(chunk, TILE_WALL, 106, 106, 107, 108)

    # ================================================================
    # SESSION 19 FIDELITY PASS — UndeadSettlement DS3 village depth
    # ================================================================
    # Sewer tunnel — slime-coated drain walls (DS3: rats and sewage beneath settlement)
    fill_tiles(chunk, TILE_WALL, 120, 92, 121, 94)
    fill_tiles(chunk, TILE_WALL, 126, 96, 127, 98)
    fill_tiles(chunk, TILE_WALL, 132, 90, 133, 92)
    fill_tiles(chunk, TILE_WALL, 138, 94, 139, 96)
    fill_tiles(chunk, TILE_WALL, 124, 100, 125, 102)
    # Cliff houses — wooden beam debris (DS3: houses hanging over cliff edge)
    fill_tiles(chunk, TILE_WALL, 14, 42, 15, 44)
    fill_tiles(chunk, TILE_WALL, 20, 46, 21, 48)
    fill_tiles(chunk, TILE_WALL, 8, 48, 9, 50)
    fill_tiles(chunk, TILE_WALL, 26, 50, 27, 52)
    # Evangelist square — paving cracks (DS3: open area where Evangelists patrol)
    fill_tiles(chunk, TILE_WALL, 36, 62, 37, 64)
    fill_tiles(chunk, TILE_WALL, 42, 66, 43, 68)
    fill_tiles(chunk, TILE_WALL, 48, 70, 49, 72)
    fill_tiles(chunk, TILE_WALL, 54, 74, 55, 76)
    fill_tiles(chunk, TILE_WALL, 60, 78, 61, 80)
    # Fire demon arena — scorch marks and debris (DS3: Siegward helps fight demon)
    fill_tiles(chunk, TILE_WALL, 96, 60, 97, 62)
    fill_tiles(chunk, TILE_WALL, 102, 64, 103, 66)
    fill_tiles(chunk, TILE_WALL, 108, 68, 109, 70)
    fill_tiles(chunk, TILE_WALL, 114, 72, 115, 74)
    fill_tiles(chunk, TILE_WALL, 100, 76, 101, 78)

    # ================================================================
    # SESSION 22 FIDELITY PASS — UndeadSettlement DS3 settlement details
    # ================================================================
    # Market stall debris (DS3: wooden stalls in the settlement square)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 33)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 40, 40, 41, 41)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 45)
    # Tree hollow positions (DS3: hollows hanging from trees)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 56, 65, 57)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 61)
    # Bridge support debris (DS3: broken bridge supports near settlement)
    fill_tiles(chunk, TILE_WALL, 22, 58, 23, 59)
    fill_tiles(chunk, TILE_WALL, 28, 62, 29, 63)
    fill_tiles(chunk, TILE_WALL, 34, 66, 35, 67)
    fill_tiles(chunk, TILE_WALL, 40, 70, 41, 71)

    # ================================================================
    # SESSION 24 FIDELITY PASS — UndeadSettlement DS3 settlement details
    # ================================================================
    # House foundation debris (DS3: collapsed house foundations)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    fill_tiles(chunk, TILE_WALL, 40, 48, 41, 49)
    # Wooden cart debris (DS3: broken carts along the settlement paths)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 52, 56, 53, 57)
    fill_tiles(chunk, TILE_WALL, 58, 60, 59, 61)
    fill_tiles(chunk, TILE_WALL, 64, 64, 65, 65)
    # Cliff edge stones (DS3: stones at the cliff edges of the settlement)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 77)
    fill_tiles(chunk, TILE_WALL, 88, 80, 89, 81)
    # Tree hollow positions (DS3: hollows hanging from settlement trees)
    fill_tiles(chunk, TILE_WALL, 94, 84, 95, 85)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 106, 92, 107, 93)
    fill_tiles(chunk, TILE_WALL, 112, 96, 113, 97)

    # ================================================================
    # SESSION 29 FIDELITY PASS — UndeadSettlement DS3 settlement details
    # ================================================================
    # Settlement market stalls (DS3: wooden market stalls in the square)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    # Wooden bridge supports (DS3: wooden bridge connecting settlement areas)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    # Giant's tree root debris (DS3: tree roots near the giant's tower)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    # Settlement cliff debris (DS3: debris at the cliff edges)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)
    fill_tiles(chunk, TILE_WALL, 114, 98, 115, 99)

    # ================================================================
    # SESSION 32 FIDELITY PASS — UndeadSettlement DS3 settlement details
    # ================================================================
    # Settlement gatehouse (DS3: stone gatehouse at settlement entrance)
    fill_tiles(chunk, TILE_WALL, 26, 38, 27, 39)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    fill_tiles(chunk, TILE_WALL, 38, 46, 39, 47)
    fill_tiles(chunk, TILE_WALL, 44, 50, 45, 51)
    # Tree hollow gallows (DS3: gallows where hollows hang from trees)
    fill_tiles(chunk, TILE_WALL, 50, 54, 51, 55)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 62, 62, 63, 63)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 67)
    # Evangelist's cathedral path (DS3: path to the cathedral area)
    fill_tiles(chunk, TILE_WALL, 74, 70, 75, 71)
    fill_tiles(chunk, TILE_WALL, 80, 74, 81, 75)
    fill_tiles(chunk, TILE_WALL, 86, 78, 87, 79)
    fill_tiles(chunk, TILE_WALL, 92, 82, 93, 83)
    # Giant arrow debris (DS3: giant arrows stuck in the ground)
    fill_tiles(chunk, TILE_WALL, 98, 86, 99, 87)
    fill_tiles(chunk, TILE_WALL, 104, 90, 105, 91)
    fill_tiles(chunk, TILE_WALL, 110, 94, 111, 95)
    fill_tiles(chunk, TILE_WALL, 116, 98, 117, 99)

    # SESSION 39 FIDELITY PASS — Undead Settlement DS3 details
    # DS3: Market stall frames, bridge stone supports, giant tree root clusters
    for tx in range(20, 55, 6):
        fill_tiles(chunk, TILE_WALL, tx, 30, tx+2, 32)             # Market stall frames
        fill_tiles(chunk, TILE_WALL, tx, 70, tx+2, 72)
    for tx in range(60, 100, 5):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+1, 36)             # Bridge stone supports
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+1, 76)
    for ty in range(40, 65, 8):
        fill_tiles(chunk, TILE_WALL, 35, ty, 36, ty+1)             # Tree root clusters
        fill_tiles(chunk, TILE_WALL, 85, ty, 86, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 50, 52, 52)                    # Giant tree base
    fill_tiles(chunk, TILE_WALL, 110, 45, 112, 47)                  # Cage elevator mechanism
    fill_tiles(chunk, TILE_WALL, 120, 60, 122, 62)                  # Cliff debris
    for tx in range(100, 135, 7):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+1, 51)             # Street cobblestones
    # --- SESSION 45 terrain (Undead Settlement) ---
    # DS3: Market stalls along the main street
    for tx in range(20, 28):
        chunk[25][tx] = TILE_WALLTOP  # stall canopy debris
    for tx in range(35, 42):
        chunk[30][tx] = TILE_WALLTOP  # wooden stall frame
    # Bridge support pillars (DS3: the main bridge over the cliff)
    for ty in range(40, 46):
        chunk[ty][50] = TILE_WALL  # bridge pillar
    for ty in range(42, 48):
        chunk[ty][60] = TILE_WALL  # bridge pillar
    # Giant's tree roots (DS3: massive roots near the giant's tower)
    for tx in range(70, 78):
        chunk[35][tx] = TILE_WALLTOP  # root debris
    # Wooden scaffolding around buildings (DS3: hollow construction)
    for ty in range(20, 26):
        chunk[ty][45] = TILE_WALLTOP  # scaffold plank
    # Hanging cage frames (DS3: cages hang from trees/buildings)
    chunk[32][55] = TILE_WALLTOP  # cage frame
    chunk[32][58] = TILE_WALLTOP  # cage frame
    # Hollow dwelling interior walls (DS3: makeshift homes)
    for tx in range(15, 20):
        chunk[50][tx] = TILE_WALLTOP  # debris pile

    # --- SESSION 50 terrain (Undead Settlement final) ---
    # DS3: Tree branch platforms (DS3: the giant's tree has walkable branches)
    for tx in range(72, 80):
        chunk[38][tx] = TILE_WALLTOP  # branch platform
    # Well structure in the main square
    chunk[42][35] = TILE_WALL  # well wall
    chunk[42][36] = TILE_WALL
    chunk[43][35] = TILE_WALLTOP  # well rim
    chunk[43][36] = TILE_WALLTOP
    # Hanging cage chains (DS3: cages hang from wooden frames)
    for tx, ty in [(50, 28), (58, 32)]:
        chunk[ty][tx] = TILE_WALLTOP  # cage debris
    # Wooden cart debris (DS3: scattered around the settlement)
    for tx in range(25, 30):
        chunk[55][tx] = TILE_WALLTOP  # cart pieces

    # --- SESSION 58 terrain (Undead Settlement) ---
    # DS3: Settlement bell tower base
    for ty in range(30, 36):
        chunk[ty][58] = TILE_WALL  # tower wall
    # Wooden bridge planks between buildings
    for tx in range(40, 50):
        chunk[38][tx] = TILE_WALLTOP  # bridge plank
    # Giant's chain anchors (DS3: chains that hold the giant)
    for tx, ty in [(72, 32), (76, 36)]:
        chunk[ty][tx] = TILE_WALL  # chain anchor
    # Settlement gate arch
    for ty in range(18, 24):
        chunk[ty][15] = TILE_WALL  # gate pillar
        chunk[ty][20] = TILE_WALL  # gate pillar

    # --- SESSION 86 DS3 terrain (Undead Settlement detail pass) ---
    # DS3: Giant's tower (tall structure with archer)
    for tx in range(50, 58):
        for ty in [10, 22]:
            chunk[tx][ty] = TILE_WALL
    for tx in [50, 58]:
        for ty in range(10, 23):
            chunk[tx][ty] = TILE_WALL
    for tx in range(50, 59):
        chunk[tx][9] = TILE_WALLTOP
    # DS3: Market stalls (wooden structures with hollows)
    for tx in [25, 28, 31]:
        for ty in range(35, 38):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    for tx in [35, 38, 41]:
        for ty in range(35, 38):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Bridge with cages hanging from it
    for tx in range(60, 75):
        chunk[tx][42] = TILE_WALL
        chunk[tx][41] = TILE_WALLTOP
    # DS3: Tree branch platforms (the descent path)
    for tx in [80, 82, 84, 86, 88]:
        for ty in [50, 52]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Pyre square central fire pit
    for tx in range(90, 96):
        for ty in range(55, 60):
            chunk[tx][ty] = TILE_GROUND

    # --- SESSION 90 DS3 terrain round 2 (Undead Settlement) ---
    # DS3: House structures along the street
    for tx in range(30, 38):
        for ty in [20, 26]:
            chunk[tx][ty] = TILE_WALL
    for tx in [30, 38]:
        for ty in range(20, 27):
            chunk[tx][ty] = TILE_WALL
    for tx in range(30, 39):
        chunk[tx][19] = TILE_WALLTOP
    # DS3: Scaffolding platforms (elevated walkways)
    for tx in [45, 47, 49, 51, 53]:
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][29] = TILE_WALLTOP
    # DS3: Hanging cages from the tree
    for tx in [68, 72, 76]:
        for ty in [35, 36]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Carts and wagons in the street
    for tx in range(55, 60):
        for ty in [42, 43]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Tree branches (the massive hollow tree)
    for tx in [80, 82, 84, 86, 88, 90]:
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Curse-rotted Greatwood arena debris
    for tx in range(95, 115):
        for ty in range(70, 82):
            chunk[tx][ty] = TILE_GROUND
    for tx in [95, 115]:
        for ty in range(70, 83):
            chunk[tx][ty] = TILE_WALL
    # DS3: Elevator shaft to Road of Sacrifices
    for tx in range(120, 128):
        for ty in [75, 80]:
            chunk[tx][ty] = TILE_WALL
    for tx in [120, 128]:
        for ty in range(75, 81):
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/UndeadSettlement.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("UndeadSettlement", chunk, entities, spawn_px, spawn_py)
