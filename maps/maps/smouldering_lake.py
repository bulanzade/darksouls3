from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_smouldering_lake():
    """Smouldering Lake - lava cavern beneath Carthus catacombs.
    Faithful DS3 layout: underground cave -> smouldering lake shore with lava ->
    demon ruins outer hall -> demon cleric corridors -> Old Demon King arena.
    DS3: vast underground cavern with ballista firing across the lake, demon ruins
    below, and the Old Demon King boss at the deepest point.
    """
    chunk = new_chunk(288, 256)
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
    # CONNECTIVITY CORRIDORS — wider paths between sections
    # ================================================================
    # Wide corridor: lake shore to demon ruins (east)
    fill_tiles(chunk, TILE_GROUND, 40, 40, 60, 55)
    # Wide corridor: demon ruins to cleric corridors (east)
    fill_tiles(chunk, TILE_GROUND, 82, 55, 100, 65)
    # Wide corridor: cleric corridors to arena (east)
    fill_tiles(chunk, TILE_GROUND, 105, 70, 120, 90)
    # Wide corridor: entry cave to lake (south)
    fill_tiles(chunk, TILE_GROUND, 12, 18, 28, 35)
    # Wide corridor: ballista to lake center
    fill_tiles(chunk, TILE_GROUND, 20, 70, 40, 82)

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

    # ================================================================
    # SESSION 13 FIDELITY PASS — SmoulderingLake DS3 architecture
    # ================================================================
    # Ballista platform — bolt rack debris (DS3: giant ballista fires at you)
    fill_tiles(chunk, TILE_WALL, 16, 82, 17, 83)
    fill_tiles(chunk, TILE_WALL, 22, 86, 23, 87)
    fill_tiles(chunk, TILE_WALL, 12, 90, 13, 91)
    fill_tiles(chunk, TILE_WALL, 28, 84, 29, 85)
    # Demon ruins — molten stone pillars (DS3: fire demon temple)
    fill_tiles(chunk, TILE_WALL, 62, 58, 63, 59)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 80, 64, 81, 65)
    # Underground lake — volcanic rock formations (DS3: lava lake with rock islands)
    fill_tiles(chunk, TILE_WALL, 42, 68, 43, 69)
    fill_tiles(chunk, TILE_WALL, 50, 72, 51, 73)
    fill_tiles(chunk, TILE_WALL, 58, 70, 59, 71)
    fill_tiles(chunk, TILE_WALL, 66, 74, 67, 75)
    fill_tiles(chunk, TILE_WALL, 46, 76, 47, 77)
    # Tsorig area — magma pool edges (DS3: Knight Slayer Tsorig invades near lava)
    fill_tiles(chunk, TILE_WALL, 30, 88, 31, 89)
    fill_tiles(chunk, TILE_WALL, 36, 92, 37, 93)
    fill_tiles(chunk, TILE_WALL, 24, 94, 25, 95)
    fill_tiles(chunk, TILE_WALL, 34, 96, 35, 97)
    fill_tiles(chunk, TILE_WALL, 26, 90, 27, 91)
    # Demon King arena — scorched throne debris (DS3: Old Demon King arena)
    fill_tiles(chunk, TILE_WALL, 130, 102, 131, 103)
    fill_tiles(chunk, TILE_WALL, 138, 108, 139, 109)
    fill_tiles(chunk, TILE_WALL, 126, 108, 127, 109)
    fill_tiles(chunk, TILE_WALL, 142, 104, 143, 105)

    # ================================================================
    # DS3 POISON TERRAIN — Smouldering Lake expanded lava coverage
    # DS3: vast underground lava lake with demon ruins
    # ================================================================
    # Expanded lava coverage across the lake (DS3: magma covers most of the floor)
    fill_tiles(chunk, TILE_POISON, 25, 35, 45, 48)
    fill_tiles(chunk, TILE_POISON, 50, 45, 65, 58)
    fill_tiles(chunk, TILE_POISON, 35, 55, 50, 70)
    fill_tiles(chunk, TILE_POISON, 60, 60, 75, 72)
    fill_tiles(chunk, TILE_POISON, 70, 50, 85, 62)
    # Demon ruins lava pools (DS3: lava pools in demon architecture)
    fill_tiles(chunk, TILE_POISON, 90, 68, 105, 78)
    fill_tiles(chunk, TILE_POISON, 95, 62, 110, 72)
    # Old Demon King arena edge lava expansion (DS3: lava surrounds the throne)
    fill_tiles(chunk, TILE_POISON, 115, 95, 125, 102)
    fill_tiles(chunk, TILE_POISON, 140, 115, 150, 125)

    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 38 * 16, 40 * 16))     # Abandoned Tomb
    entities.append(make_entity("Bonfire", 145 * 16, 155 * 16))     # Old King's Antechamber
    entities.append(make_entity("Bonfire", 172 * 16, 126 * 16))    # Demon Ruins
    entities.append(make_entity("Bonfire", 228 * 16, 173 * 16))   # Old Demon King

    # Boss - Old Demon King
    entities.append(make_entity("BossSpawn", 228 * 16, 173 * 16))

    # Enemies — DS3 Smouldering Lake: Demon Clerics, Demon Statues, Basilisks,
    # Smouldering Rotten Flesh, Great Crab, Carthus Sandworm,
    # Skeleton Swordsmen, Skeleton Wheels, Knight Slayer Tsorig NPC
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
        ("EstusShard", "Estus Shard", 20, 86, 0),               # Ballista caves
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

    entities.append(make_entity("FogGate", 38 * 16, 33 * 16, [
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

    # ================================================================
    # SESSION 12 FIDELITY PASS — SmoulderingLake DS3 architectural details
    # ================================================================
    # Ballista bolt impact craters (DS3: massive bolts embedded in ground from ballista)
    fill_tiles(chunk, TILE_WALL, 16, 28, 17, 30)
    fill_tiles(chunk, TILE_WALL, 24, 32, 25, 34)
    fill_tiles(chunk, TILE_WALL, 20, 36, 21, 38)
    fill_tiles(chunk, TILE_WALL, 30, 26, 31, 28)
    # Lava crust formations (DS3: cooled lava crust with glowing cracks)
    fill_tiles(chunk, TILE_WALL, 44, 62, 45, 64)
    fill_tiles(chunk, TILE_WALL, 52, 66, 53, 68)
    fill_tiles(chunk, TILE_WALL, 60, 60, 61, 62)
    fill_tiles(chunk, TILE_WALL, 66, 68, 67, 70)
    # Demon bone furnace debris (DS3: demon skeletons near demon ruins)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 78)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 82)
    fill_tiles(chunk, TILE_WALL, 76, 84, 77, 86)
    fill_tiles(chunk, TILE_WALL, 98, 78, 99, 80)
    # Scorched pillar bases (DS3: burned stone columns in demon ruins)
    fill_tiles(chunk, TILE_WALL, 38, 70, 39, 72)
    fill_tiles(chunk, TILE_WALL, 46, 74, 47, 76)
    fill_tiles(chunk, TILE_WALL, 54, 72, 55, 74)
    fill_tiles(chunk, TILE_WALL, 70, 76, 71, 78)
    # Ember vein stone clusters (DS3: glowing ember deposits in rock walls)
    fill_tiles(chunk, TILE_WALL, 100, 68, 101, 70)
    fill_tiles(chunk, TILE_WALL, 106, 72, 107, 74)
    fill_tiles(chunk, TILE_WALL, 114, 66, 115, 68)
    fill_tiles(chunk, TILE_WALL, 122, 70, 123, 72)
    # Old Demon King altar fragments (DS3: demon ritual stones near arena)
    fill_tiles(chunk, TILE_WALL, 126, 80, 127, 82)
    fill_tiles(chunk, TILE_WALL, 132, 84, 133, 86)
    fill_tiles(chunk, TILE_WALL, 138, 78, 139, 80)
    fill_tiles(chunk, TILE_WALL, 144, 82, 145, 84)
    # Charred wood bridge remnants (DS3: burned bridges over lava channels)
    fill_tiles(chunk, TILE_WALL, 34, 78, 36, 79)
    fill_tiles(chunk, TILE_WALL, 42, 82, 44, 83)
    fill_tiles(chunk, TILE_WALL, 58, 80, 60, 81)
    fill_tiles(chunk, TILE_WALL, 64, 84, 66, 85)
    # Smoke vent fissures (DS3: steam vents and smoke holes in cave floor)
    fill_tiles(chunk, TILE_WALL, 86, 64, 87, 65)
    fill_tiles(chunk, TILE_WALL, 94, 68, 95, 69)
    fill_tiles(chunk, TILE_WALL, 102, 62, 103, 63)
    fill_tiles(chunk, TILE_WALL, 110, 66, 111, 67)
    # Tsorig tunnel — worn stone arch (DS3: worn archway where Tsorig invades)
    fill_tiles(chunk, TILE_WALL, 22, 48, 23, 50)
    fill_tiles(chunk, TILE_WALL, 28, 52, 29, 54)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 48)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 52)

    # ================================================================
    # SESSION 17 FIDELITY PASS — SmoulderingLake DS3 lava cavern details
    # ================================================================
    # Lava channel rock walls — narrow stone channels guide lava flow (DS3: lava rivers)
    fill_tiles(chunk, TILE_WALL, 24, 34, 25, 36)
    fill_tiles(chunk, TILE_WALL, 32, 38, 33, 40)
    fill_tiles(chunk, TILE_WALL, 40, 36, 41, 38)
    fill_tiles(chunk, TILE_WALL, 48, 42, 49, 44)
    fill_tiles(chunk, TILE_WALL, 56, 46, 57, 48)
    # Demon bone pile debris — massive demon skeletons in ruins (DS3: dead demons everywhere)
    fill_tiles(chunk, TILE_WALL, 60, 56, 62, 57)
    fill_tiles(chunk, TILE_WALL, 72, 62, 74, 63)
    fill_tiles(chunk, TILE_WALL, 84, 68, 86, 69)
    fill_tiles(chunk, TILE_WALL, 96, 64, 98, 65)
    fill_tiles(chunk, TILE_WALL, 108, 70, 110, 71)
    # Volcanic vent stones — steam vent rock formations (DS3: volcanic activity)
    fill_tiles(chunk, TILE_WALL, 14, 40, 16, 41)
    fill_tiles(chunk, TILE_WALL, 26, 48, 28, 49)
    fill_tiles(chunk, TILE_WALL, 38, 56, 40, 57)
    fill_tiles(chunk, TILE_WALL, 50, 62, 52, 63)
    fill_tiles(chunk, TILE_WALL, 62, 66, 64, 67)
    # Demon cleric altar pedestals — ritual stones in corridors (DS3: demon worship)
    fill_tiles(chunk, TILE_WALL, 92, 74, 93, 76)
    fill_tiles(chunk, TILE_WALL, 100, 78, 101, 80)
    fill_tiles(chunk, TILE_WALL, 108, 76, 109, 78)
    fill_tiles(chunk, TILE_WALL, 116, 72, 117, 74)
    # Old Demon King arena — throne room pillars (DS3: massive demon throne room)
    fill_tiles(chunk, TILE_WALL, 120, 96, 121, 98)
    fill_tiles(chunk, TILE_WALL, 134, 100, 135, 102)
    fill_tiles(chunk, TILE_WALL, 148, 96, 149, 98)
    fill_tiles(chunk, TILE_WALL, 126, 116, 127, 118)
    fill_tiles(chunk, TILE_WALL, 140, 112, 141, 114)
    fill_tiles(chunk, TILE_WALL, 152, 108, 153, 110)
    # Ballista tunnel — cave ceiling debris (DS3: stalactites in ballista cave)
    fill_tiles(chunk, TILE_WALL, 10, 84, 11, 86)
    fill_tiles(chunk, TILE_WALL, 18, 88, 19, 90)
    fill_tiles(chunk, TILE_WALL, 26, 82, 27, 84)
    fill_tiles(chunk, TILE_WALL, 32, 90, 33, 92)
    fill_tiles(chunk, TILE_WALL, 14, 96, 15, 98)

    # ================================================================
    # SESSION 21 FIDELITY PASS — SmoulderingLake DS3 lava cavern details
    # ================================================================
    # Demon bone pile debris (DS3: ancient demon skeletons scattered around)
    fill_tiles(chunk, TILE_WALL, 22, 40, 24, 42)
    fill_tiles(chunk, TILE_WALL, 28, 44, 30, 46)
    fill_tiles(chunk, TILE_WALL, 34, 48, 36, 50)
    fill_tiles(chunk, TILE_WALL, 18, 52, 20, 54)
    # Lava rock formations (DS3: cooled lava crust forming walkable obstacles)
    fill_tiles(chunk, TILE_WALL, 40, 56, 42, 58)
    fill_tiles(chunk, TILE_WALL, 46, 60, 48, 62)
    fill_tiles(chunk, TILE_WALL, 52, 64, 54, 66)
    fill_tiles(chunk, TILE_WALL, 58, 68, 60, 70)
    # Ballista debris (DS3: giant ballista firing into the lake from above)
    fill_tiles(chunk, TILE_WALL, 66, 74, 68, 76)
    fill_tiles(chunk, TILE_WALL, 72, 78, 74, 80)
    fill_tiles(chunk, TILE_WALL, 78, 82, 80, 84)
    fill_tiles(chunk, TILE_WALL, 84, 86, 86, 88)
    # Basilisk eye alcove walls (DS3: curse-fog alcoves with basilisk nests)
    fill_tiles(chunk, TILE_WALL, 16, 76, 18, 78)
    fill_tiles(chunk, TILE_WALL, 22, 80, 24, 82)
    fill_tiles(chunk, TILE_WALL, 28, 84, 30, 86)
    fill_tiles(chunk, TILE_WALL, 34, 88, 36, 90)
    # Old Demon King throne debris (DS3: shattered throne in boss arena)
    fill_tiles(chunk, TILE_WALL, 136, 110, 138, 112)
    fill_tiles(chunk, TILE_WALL, 142, 114, 144, 116)
    fill_tiles(chunk, TILE_WALL, 148, 118, 150, 120)
    fill_tiles(chunk, TILE_WALL, 132, 116, 134, 118)

    # ================================================================
    # SESSION 25 FIDELITY PASS — SmoulderingLake DS3 lava cavern details
    # ================================================================
    # Lava crust formations (DS3: cooled lava forming walkable surfaces)
    fill_tiles(chunk, TILE_WALL, 14, 28, 15, 29)
    fill_tiles(chunk, TILE_WALL, 20, 32, 21, 33)
    fill_tiles(chunk, TILE_WALL, 26, 36, 27, 37)
    fill_tiles(chunk, TILE_WALL, 32, 40, 33, 41)
    # Ballista bolt debris (DS3: giant ballista bolts embedded in ground)
    fill_tiles(chunk, TILE_WALL, 38, 44, 39, 45)
    fill_tiles(chunk, TILE_WALL, 44, 48, 45, 49)
    fill_tiles(chunk, TILE_WALL, 50, 52, 51, 53)
    fill_tiles(chunk, TILE_WALL, 56, 56, 57, 57)
    # Demon skeleton fragments (DS3: ancient demon bones in the lake)
    fill_tiles(chunk, TILE_WALL, 62, 60, 63, 61)
    fill_tiles(chunk, TILE_WALL, 68, 64, 69, 65)
    fill_tiles(chunk, TILE_WALL, 74, 68, 75, 69)
    fill_tiles(chunk, TILE_WALL, 80, 72, 81, 73)
    # Old Demon King arena pillars (DS3: stone pillars in the boss arena)
    fill_tiles(chunk, TILE_WALL, 120, 100, 121, 101)
    fill_tiles(chunk, TILE_WALL, 126, 104, 127, 105)
    fill_tiles(chunk, TILE_WALL, 132, 108, 133, 109)
    fill_tiles(chunk, TILE_WALL, 138, 112, 139, 113)
    # Hidden path debris (DS3: hidden path under the lake)
    fill_tiles(chunk, TILE_WALL, 10, 80, 11, 81)
    fill_tiles(chunk, TILE_WALL, 16, 84, 17, 85)
    fill_tiles(chunk, TILE_WALL, 22, 88, 23, 89)
    fill_tiles(chunk, TILE_WALL, 28, 92, 29, 93)

    # ================================================================
    # SESSION 29 FIDELITY PASS — SmoulderingLake DS3 lava cavern details
    # ================================================================
    # Lava flow debris (DS3: cooled lava flow formations)
    fill_tiles(chunk, TILE_WALL, 16, 32, 17, 33)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    # Demon ruin columns (DS3: broken columns in the demon ruins)
    fill_tiles(chunk, TILE_WALL, 40, 48, 41, 49)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 52, 56, 53, 57)
    fill_tiles(chunk, TILE_WALL, 58, 60, 59, 61)
    # Ballista platform (DS3: giant ballista platform above the lake)
    fill_tiles(chunk, TILE_WALL, 64, 64, 65, 65)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 77)
    # Chaos flame debris (DS3: chaos flame remnants near the altar)
    fill_tiles(chunk, TILE_WALL, 88, 80, 89, 81)
    fill_tiles(chunk, TILE_WALL, 94, 84, 95, 85)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 106, 92, 107, 93)

    # ================================================================
    # SESSION 33 FIDELITY PASS — SmoulderingLake DS3 lava cavern details
    # ================================================================
    # Demon ruin arches (DS3: stone arches in the demon ruins)
    fill_tiles(chunk, TILE_WALL, 14, 30, 15, 31)
    fill_tiles(chunk, TILE_WALL, 20, 34, 21, 35)
    fill_tiles(chunk, TILE_WALL, 26, 38, 27, 39)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    # Lava flow edge stones (DS3: stones at the edge of lava flows)
    fill_tiles(chunk, TILE_WALL, 38, 46, 39, 47)
    fill_tiles(chunk, TILE_WALL, 44, 50, 45, 51)
    fill_tiles(chunk, TILE_WALL, 50, 54, 51, 55)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    # Carthus Sandworm burrow (DS3: sandworm tunnel entrance)
    fill_tiles(chunk, TILE_WALL, 62, 62, 63, 63)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 67)
    fill_tiles(chunk, TILE_WALL, 74, 70, 75, 71)
    fill_tiles(chunk, TILE_WALL, 80, 74, 81, 75)
    # Hidden path debris (DS3: hidden path under the ballista area)
    fill_tiles(chunk, TILE_WALL, 86, 78, 87, 79)
    fill_tiles(chunk, TILE_WALL, 92, 82, 93, 83)
    fill_tiles(chunk, TILE_WALL, 98, 86, 99, 87)
    fill_tiles(chunk, TILE_WALL, 104, 90, 105, 91)

    # --- SESSION 43 terrain (Smouldering Lake) ---
    # DS3: Lava crust formations (solidified lava flows)
    for tx in range(20, 30):
        for ty in [50, 51]:
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON
    for tx in range(40, 50):
        for ty in [45, 46]:
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON
    # Ballista bolt impact craters (DS3: giant ballista shoots the lake)
    for tx, ty in [(35, 35), (55, 40), (70, 38), (85, 42)]:
        chunk[ty][tx] = TILE_WALLTOP
        chunk[ty+1][tx] = TILE_WALLTOP
    # Demon skeleton ribcages
    for tx in range(60, 68):
        chunk[55][tx] = TILE_WALLTOP
    # Scorched earth patches
    for tx in range(80, 90):
        for ty in range(50, 54):
            chunk[ty][tx] = TILE_WALLTOP

    # --- SESSION 48 terrain (Smouldering Lake) ---
    # DS3: Demon ruins stone archways
    for ty in range(30, 36):
        chunk[ty][40] = TILE_WALL  # demon arch
    for ty in range(35, 42):
        chunk[ty][65] = TILE_WALL  # demon arch
    # Ballista platform structure (DS3: the giant ballista on the cliff)
    for tx in range(15, 22):
        chunk[20][tx] = TILE_WALLTOP  # platform debris
    # Underground lake shore stones (DS3: the hidden lake beneath)
    for tx in range(80, 90):
        chunk[55][tx] = TILE_WALLTOP  # shore rocks
    # Demon bone piles (DS3: remnants of the Chaos flame demons)
    for tx, ty in [(45, 40), (55, 45), (70, 42)]:
        chunk[ty][tx] = TILE_WALLTOP  # demon bone

    # --- SESSION 52 terrain (Smouldering Lake) ---
    # DS3: Demon ruins pillar fragments
    for ty in range(25, 32):
        chunk[ty][35] = TILE_WALL  # pillar stump
    # Lava flow channels (DS3: rivers of lava through the ruins)
    for tx in range(55, 65):
        for ty in [58, 59]:
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON
    # Carthus skeleton debris on the lake bed
    for tx, ty in [(30, 48), (45, 52)]:
        chunk[ty][tx] = TILE_WALLTOP  # bone scatter
    # Ballista bolt embedded in ground
    chunk[42][75] = TILE_WALL  # bolt shaft
    chunk[43][75] = TILE_WALLTOP  # impact crater

    # --- SESSION 56 terrain (Smouldering Lake final) ---
    # DS3: Carthus catacombs entrance arch (DS3: the entrance from Catacombs)
    for ty in range(15, 22):
        chunk[ty][10] = TILE_WALL  # entrance arch
        chunk[ty][14] = TILE_WALL  # entrance arch
    # Underground lake rock formations (DS3: the hidden lake cavern)
    for tx, ty in [(75, 60), (82, 58), (90, 62)]:
        chunk[ty][tx] = TILE_WALL  # rock formation
    # Lava channel banks (DS3: lava flows in channels between ruins)
    for tx in range(35, 45):
        chunk[55][tx] = TILE_WALLTOP  # lava bank

    # --- SESSION 88 DS3 terrain (Smouldering Lake detail pass) ---
    # DS3: Lava crust formations (hardened lava flow patterns)
    for tx in range(40, 60):
        for ty in range(30, 45):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(80, 100):
        for ty in range(40, 55):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Ballista tower (stone structure on the hill)
    for tx in range(110, 120):
        for ty in [20, 30]:
            chunk[tx][ty] = TILE_WALL
    for tx in [110, 120]:
        for ty in range(20, 31):
            chunk[tx][ty] = TILE_WALL
    for tx in range(110, 121):
        chunk[tx][19] = TILE_WALLTOP
    # DS3: Demon bones scattered across the lake
    for tx in [25, 35, 50, 65, 80, 95, 110, 125]:
        for ty in [50, 55]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Scorched earth patches
    for tx in range(20, 40):
        for ty in range(60, 70):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Underground lake (large cavern)
    for tx in range(30, 80):
        for ty in range(80, 100):
            chunk[tx][ty] = TILE_GROUND
    for tx in [30, 80]:
        for ty in range(80, 101):
            chunk[tx][ty] = TILE_WALL
    for tx in range(30, 81):
        for ty in [80, 100]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Demon arches (stone archways in the ruins)
    for tx in [45, 55, 65]:
        for ty in range(35, 42):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Old Demon King arena (large open chamber)
    for tx in range(60, 90):
        for ty in range(90, 110):
            chunk[tx][ty] = TILE_GROUND
    for tx in [60, 90]:
        for ty in range(90, 111):
            chunk[tx][ty] = TILE_WALL
    for tx in range(60, 91):
        for ty in [90, 110]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Connecting tunnel to Catacombs
    for tx in range(10, 25):
        for ty in range(65, 70):
            chunk[tx][ty] = TILE_GROUND

    # --- SESSION 91 DS3 terrain round 2 (Smouldering Lake) ---
    # DS3: Demon ruins entrance (arched stone gateway)
    for tx in range(45, 55):
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    for tx in [45, 55]:
        for ty in range(53, 57):
            chunk[tx][ty] = TILE_WALL
    for tx in range(45, 56):
        chunk[tx][52] = TILE_WALLTOP
    # DS3: Ballista craters (impact holes)
    for tx in [30, 45, 60, 75, 90]:
        for ty in range(42, 46):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Lava flow channels
    for tx in range(35, 55):
        for ty in [35, 36]:
            chunk[tx][ty] = TILE_GROUND
    for tx in range(65, 85):
        for ty in [45, 46]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Underground lake shore
    for tx in range(25, 50):
        for ty in range(85, 95):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Titanite slab chamber (hidden room)
    for tx in range(110, 120):
        for ty in [80, 88]:
            chunk[tx][ty] = TILE_WALL
    for tx in [110, 120]:
        for ty in range(80, 89):
            chunk[tx][ty] = TILE_WALL
    for tx in range(110, 121):
        chunk[tx][79] = TILE_WALLTOP
    
    # --- DS3 faithful enemies (SmoulderingLake) ---
    # DS3 wiki enemies: Demon Statue, Demon Cleric, Smoldering Ghru, Basilisk, Black Knight,
    # Crystal Lizard, Great Crab, Hound-Rat, Skeleton Swordsman, Skeleton Wheel,
    # Smoldering Rotten Flesh, Carthus Sandworm, Stray Demon (boss)
    # DemonStatue (18) — DS3: stone demon statues scattered around lava lake
    for tx, ty in [(18, 18), (22, 22), (28, 42), (50, 60), (65, 50), (18, 32), (35, 40), (62, 58), (68, 62), (72, 55), (42, 48), (55, 52), (95, 62), (100, 60), (112, 82), (130, 108), (140, 98), (105, 90)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DemonStatue", "DemonStatue"))]))
    # DemonCleric (3) — DS3: demon clerics casting fire spells near lava
    for tx, ty in [(58, 62), (98, 65), (125, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DemonCleric", "DemonCleric"))]))
    # SmolderingGhru (5) — DS3: goat-demons adapted to lava environment
    for tx, ty in [(48, 55), (65, 60), (100, 85), (115, 100), (148, 112)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SmolderingGhru", "SmolderingGhru"))]))
    # SmolderingRottenFlesh (3) — DS3: charred fleshy creatures near lava pools
    for tx, ty in [(72, 62), (120, 120), (142, 105)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SmolderingRottenFlesh", "SmolderingRottenFlesh"))]))
    # Basilisk (5)
    entities.append(make_entity("Enemy", 52 * 16, 65 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 58 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 55 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 115 * 16, 110 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 130 * 16, 118 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    # GreatCrab (1)
    entities.append(make_entity("Enemy", 38 * 16, 45 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GreatCrab", "GreatCrab"))]))
    # FireDemon (6)
    entities.append(make_entity("Enemy", 58 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))
    entities.append(make_entity("Enemy", 95 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))
    entities.append(make_entity("Enemy", 100 * 16, 75 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))
    entities.append(make_entity("Enemy", 118 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))
    entities.append(make_entity("Enemy", 125 * 16, 95 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))
    entities.append(make_entity("Enemy", 135 * 16, 102 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("FireDemon", "FireDemon"))]))
    # BlackKnight (3)
    entities.append(make_entity("Enemy", 78 * 16, 58 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))
    entities.append(make_entity("Enemy", 108 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))
    entities.append(make_entity("Enemy", 140 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))
    # SkeletonSwordman (3) — DS3: skeleton swordsmen in tunnels connecting to Catacombs
    for tx, ty in [(82, 52), (88, 60), (25, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SkeletonSwordman", "SkeletonSwordman"))]))
    # SkeletonBall (2) — DS3: rolling skeleton balls in tunnels
    for tx, ty in [(30, 90), (18, 92)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SkeletonBall", "SkeletonBall"))]))
    # MiniBoss (3)
    entities.append(make_entity("Enemy", 75 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    entities.append(make_entity("Enemy", 22 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    entities.append(make_entity("Enemy", 28 * 16, 92 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    # HoundRat (4) — DS3: hound-rats in dark tunnels
    for tx, ty in [(15, 85), (25, 95), (40, 58), (62, 68)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HoundRat", "HoundRat"))]))
    # LargeHoundRat (2) — DS3: larger hound-rats in deeper tunnels
    for tx, ty in [(20, 90), (48, 64)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LargeHoundRat", "LargeHoundRat"))]))
    # CarthusSandworm (1)
    entities.append(make_entity("Enemy", 45 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CarthusSandworm", "CarthusSandworm"))]))
    # CrystalLizard (3)
    entities.append(make_entity("Enemy", 82 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 112 * 16, 78 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 22 * 16, 98 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))

        # Horace the Hushed — hostile NPC in Smouldering Lake cave (DS3: found after Catacombs)
    entities.append(make_entity("Npc", 81 * 16, 75 * 16, [
        make_field("name", "String", "Horace the Hushed"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#4A4A4A"),
        make_field("dialogue", "String", "...|...(groans)|...(shrieks)"),
    ]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 81 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 106 * 16, 81 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 226 * 16, 171 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Demon's Greataxe (drop)")]))
    entities.append(make_entity("Item", 162 * 16, 125 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Speckled Stoneplate Ring")]))
    entities.append(make_entity("Item", 131 * 16, 146 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 156 * 16, 137 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of a Stray Demon")]))
    entities.append(make_entity("Item", 143 * 16, 156 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Iron Flesh")]))
    entities.append(make_entity("Item", 168 * 16, 143 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Fire Surge")]))
    entities.append(make_entity("Item", 181 * 16, 131 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 212 * 16, 168 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Dragon's Greataxe")]))
    entities.append(make_entity("Item", 228 * 16, 175 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Old Demon King")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/SmoulderingLake.json") as _f:

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

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0])) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100

    # print(f"  SmoulderingLake (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "SmoulderingLake", chunk, entities
