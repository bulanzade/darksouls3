from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_smouldering_lake():
    """Smouldering Lake - DS3-faithful terrain.

    Underground area below Catacombs of Carthus. Features a massive subterranean
    lake with ballista firing giant arrows, demon ruins with lava channels, and
    the Old Demon King boss at the deepest point.

    Map: 320x256 tiles (5120x4096 px).
    JSON doc sections (pixel -> tile = pixel // 16):
      1. Abandoned Tomb Entry:       (26,26)-(77,61)   — dark cave from Catacombs
      2. Smouldering Lake Shore:     (65,56)-(176,122)  — vast lava lake with ballista
      3. Ballista Tower:             (157,18)-(214,66)  — giant ballista platform
      4. Demon Ruins Entry:          (115,131)-(170,171) — demon architecture, basilisks
      5. Old King's Antechamber:     (157,115)-(218,162) — stone hall, demon carvings
      6. Old Demon King Arena:       (206,156)-(262,197) — lava arena, boss fight
      7. Lava Cave:                  (10,80)-(35,103)   — side cave with hound rats
    """
    chunk = new_chunk(320, 256)

    # ================================================================
    # 1. ABANDONED TOMB ENTRY — dark cave from Catacombs
    # DS3: player drops down from Catacombs rope bridge into small tomb
    # Section: x=420,y=420,w=820,h=560 -> tiles (26,26)-(77,61)
    # ================================================================
    # Cave walls — outer boundary
    fill_tiles(chunk, TILE_WALL, 26, 26, 28, 61)       # West wall
    fill_tiles(chunk, TILE_WALL, 75, 26, 77, 61)       # East wall
    fill_tiles(chunk, TILE_WALL, 26, 26, 77, 28)       # North wall
    fill_tiles(chunk, TILE_WALL, 26, 59, 55, 61)       # South wall left
    fill_tiles(chunk, TILE_WALL, 65, 59, 77, 61)       # South wall right
    # Stone tomb interior walls (DS3: burial niches carved into cave)
    fill_tiles(chunk, TILE_WALL, 34, 32, 36, 36)       # Tomb niche left
    fill_tiles(chunk, TILE_WALL, 55, 30, 57, 34)       # Tomb niche right
    # Rope bridge support columns (DS3: wooden supports at entrance)
    fill_tiles(chunk, TILE_WALL, 40, 28, 42, 31)       # Left column
    fill_tiles(chunk, TILE_WALL, 62, 28, 64, 31)       # Right column
    # Stalactites (DS3: rocky cave ceiling)
    fill_tiles(chunk, TILE_WALL, 48, 33, 50, 35)       # Center stalactite
    fill_tiles(chunk, TILE_WALL, 70, 38, 71, 40)       # Side stalactite

    # ================================================================
    # 2. SMOULDERING LAKE SHORE — vast underground lava lake
    # DS3: enormous cavern, lava covers most of the floor, ballista bolts rain down
    # Section: x=1040,y=900,w=1780,h=1060 -> tiles (65,56)-(176,122)
    # ================================================================
    # Lake cavern boundary walls (DS3: massive cavern walls)
    fill_tiles(chunk, TILE_WALL, 65, 56, 67, 88)       # NW wall
    fill_tiles(chunk, TILE_WALL, 65, 108, 67, 122)     # SW wall
    fill_tiles(chunk, TILE_WALL, 173, 56, 176, 90)     # NE wall
    fill_tiles(chunk, TILE_WALL, 173, 112, 176, 122)   # SE wall
    # Northern cliff wall (DS3: high cliff face, ballista visible above)
    fill_tiles(chunk, TILE_WALL, 75, 56, 165, 58)
    # Southern shore wall (DS3: rocky shore where lake ends)
    fill_tiles(chunk, TILE_WALL, 70, 118, 130, 122)
    fill_tiles(chunk, TILE_WALL, 150, 116, 170, 122)
    # Lava pools across the lake (DS3: magma covers most of the lake floor)
    fill_tiles(chunk, TILE_POISON, 80, 68, 110, 85)    # NW lava pool
    fill_tiles(chunk, TILE_POISON, 120, 75, 155, 95)   # Central-east lava pool
    fill_tiles(chunk, TILE_POISON, 90, 95, 130, 112)   # SW lava pool
    fill_tiles(chunk, TILE_POISON, 140, 100, 165, 115)  # SE lava pool
    # Stone islands / cover points (DS3: rock formations to dodge ballista bolts)
    fill_tiles(chunk, TILE_GROUND, 95, 78, 105, 85)    # NW island
    fill_tiles(chunk, TILE_GROUND, 125, 86, 135, 93)   # Center island
    fill_tiles(chunk, TILE_GROUND, 105, 100, 118, 108)  # South island
    fill_tiles(chunk, TILE_GROUND, 150, 92, 158, 98)   # East island
    # Demon statues along shore (DS3: petrified demon corpses)
    fill_tiles(chunk, TILE_WALL, 72, 65, 74, 67)       # NW shore statue
    fill_tiles(chunk, TILE_WALL, 112, 62, 114, 64)     # N shore statue
    fill_tiles(chunk, TILE_WALL, 155, 68, 157, 70)     # NE shore statue
    fill_tiles(chunk, TILE_WALL, 168, 95, 170, 97)     # E shore statue
    # Rocky outcrops (DS3: volcanic rock formations jutting from lava)
    fill_tiles(chunk, TILE_WALL, 82, 90, 84, 93)       # W outcrop
    fill_tiles(chunk, TILE_WALL, 145, 80, 147, 83)     # E outcrop
    # Ballista bolt impact craters (DS3: giant bolts embedded in ground)
    fill_tiles(chunk, TILE_WALL, 100, 70, 101, 71)     # Bolt crater 1
    fill_tiles(chunk, TILE_WALL, 130, 82, 131, 83)     # Bolt crater 2
    fill_tiles(chunk, TILE_WALL, 115, 98, 116, 99)     # Bolt crater 3

    # ================================================================
    # 3. BALLISTA TOWER — giant ballista on the cliff
    # DS3: massive ballista fires across the lake, override lever inside
    # Section: x=2520,y=300,w=920,h=780 -> tiles (157,18)-(214,66)
    # ================================================================
    # Tower walls (DS3: stone tower housing the ballista)
    fill_tiles(chunk, TILE_WALL, 160, 20, 162, 62)     # West tower wall
    fill_tiles(chunk, TILE_WALL, 211, 20, 214, 62)     # East tower wall
    fill_tiles(chunk, TILE_WALL, 160, 20, 185, 22)     # North wall left
    fill_tiles(chunk, TILE_WALL, 195, 20, 214, 22)     # North wall right
    fill_tiles(chunk, TILE_WALL, 160, 60, 180, 62)     # South wall left
    fill_tiles(chunk, TILE_WALL, 195, 60, 214, 62)     # South wall right
    # Ballista mechanism platform (DS3: central ballista platform)
    fill_tiles(chunk, TILE_WALL, 175, 35, 200, 37)     # Ballista base
    fill_tiles(chunk, TILE_WALL, 175, 30, 177, 42)     # Left support
    fill_tiles(chunk, TILE_WALL, 198, 30, 200, 42)     # Right support
    # Override lever alcove (DS3: lever to disable ballista)
    fill_tiles(chunk, TILE_WALL, 163, 48, 165, 55)     # Lever room left wall
    fill_tiles(chunk, TILE_WALL, 172, 48, 174, 55)     # Lever room right wall
    # Skeleton defenders positions (DS3: skeletons guard the ballista)
    fill_tiles(chunk, TILE_WALL, 185, 25, 187, 28)     # N guard post
    fill_tiles(chunk, TILE_WALL, 205, 45, 207, 48)     # SE guard post
    fill_tiles(chunk, TILE_WALL, 190, 52, 192, 55)     # S barrier

    # ================================================================
    # 4. DEMON RUINS ENTRY — lava-floored demon architecture
    # DS3: large hall with demon carvings, basilisks, fire everywhere
    # Section: x=1840,y=2100,w=880,h=640 -> tiles (115,131)-(170,171)
    # ================================================================
    # Ruins boundary walls (DS3: Izalith-style demon stone architecture)
    fill_tiles(chunk, TILE_WALL, 115, 131, 117, 165)   # West wall
    fill_tiles(chunk, TILE_WALL, 167, 131, 170, 165)   # East wall
    fill_tiles(chunk, TILE_WALL, 115, 131, 150, 133)   # North wall left
    fill_tiles(chunk, TILE_WALL, 158, 131, 170, 133)   # North wall right
    fill_tiles(chunk, TILE_WALL, 115, 168, 140, 171)   # South wall left
    fill_tiles(chunk, TILE_WALL, 150, 168, 170, 171)   # South wall right
    # Collapsed pillars (DS3: massive stone columns, partially destroyed)
    fill_tiles(chunk, TILE_WALL, 125, 138, 127, 142)   # NW pillar stump
    fill_tiles(chunk, TILE_WALL, 145, 136, 147, 140)   # N pillar
    fill_tiles(chunk, TILE_WALL, 158, 140, 160, 144)   # NE pillar
    fill_tiles(chunk, TILE_WALL, 130, 155, 132, 159)   # SW pillar
    fill_tiles(chunk, TILE_WALL, 152, 158, 154, 162)   # SE pillar
    # Lava floor patches (DS3: lava pools in demon ruins)
    fill_tiles(chunk, TILE_POISON, 120, 143, 135, 152)  # W lava pool
    fill_tiles(chunk, TILE_POISON, 155, 150, 165, 162)  # E lava pool
    # Demon archway (DS3: carved stone archway entrance)
    fill_tiles(chunk, TILE_WALL, 130, 131, 132, 135)   # Left arch
    fill_tiles(chunk, TILE_WALL, 155, 131, 157, 135)   # Right arch
    # Ritual stone (DS3: demon worship altar)
    fill_tiles(chunk, TILE_WALL, 140, 148, 145, 152)   # Central altar

    # ================================================================
    # 5. OLD KING'S ANTECHAMBER — stone hall with demon carvings
    # DS3: grand hall with lava fissures, fog gate to boss
    # Section: x=2520,y=1840,w=980,h=760 -> tiles (157,115)-(218,162)
    # ================================================================
    # Hall boundary walls (DS3: grand demon stone hall)
    fill_tiles(chunk, TILE_WALL, 157, 115, 159, 155)   # West wall
    fill_tiles(chunk, TILE_WALL, 215, 115, 218, 155)   # East wall
    fill_tiles(chunk, TILE_WALL, 157, 115, 195, 117)   # North wall left
    fill_tiles(chunk, TILE_WALL, 205, 115, 218, 117)   # North wall right
    fill_tiles(chunk, TILE_WALL, 157, 158, 185, 162)   # South wall left
    fill_tiles(chunk, TILE_WALL, 200, 158, 218, 162)   # South wall right
    # Lava fissure channels (DS3: glowing cracks in floor)
    fill_tiles(chunk, TILE_POISON, 165, 125, 175, 128)  # NW fissure
    fill_tiles(chunk, TILE_POISON, 195, 148, 210, 152)  # SE fissure
    fill_tiles(chunk, TILE_POISON, 175, 140, 180, 155)  # Center fissure
    # Demon carving pillars (DS3: pillars with demon reliefs)
    fill_tiles(chunk, TILE_WALL, 168, 120, 170, 128)   # NW carved pillar
    fill_tiles(chunk, TILE_WALL, 190, 120, 192, 128)   # NE carved pillar
    fill_tiles(chunk, TILE_WALL, 175, 135, 178, 140)   # Center pillar
    fill_tiles(chunk, TILE_WALL, 200, 138, 203, 143)   # East pillar
    # Fog gate frame (DS3: fog gate to Old Demon King)
    fill_tiles(chunk, TILE_WALL, 208, 150, 210, 158)   # Fog gate left
    fill_tiles(chunk, TILE_WALL, 214, 150, 216, 158)   # Fog gate right
    # Throne remnants (DS3: broken demon throne)
    fill_tiles(chunk, TILE_WALL, 162, 145, 165, 150)   # Throne fragment

    # ================================================================
    # 6. OLD DEMON KING ARENA — lava arena boss fight
    # DS3: large circular arena with lava at edges, demon throne at center
    # Section: x=3300,y=2500,w=900,h=660 -> tiles (206,156)-(262,197)
    # ================================================================
    # Arena perimeter walls (DS3: massive circular chamber)
    fill_tiles(chunk, TILE_WALL, 206, 156, 208, 190)   # West wall
    fill_tiles(chunk, TILE_WALL, 259, 156, 262, 190)   # East wall
    fill_tiles(chunk, TILE_WALL, 206, 156, 240, 158)   # North wall left
    fill_tiles(chunk, TILE_WALL, 250, 156, 262, 158)   # North wall right
    fill_tiles(chunk, TILE_WALL, 206, 194, 240, 197)   # South wall left
    fill_tiles(chunk, TILE_WALL, 250, 194, 262, 197)   # South wall right
    # Lava pools at arena edges (DS3: lava rings the arena floor)
    fill_tiles(chunk, TILE_POISON, 210, 160, 225, 168)  # NW lava pool
    fill_tiles(chunk, TILE_POISON, 245, 160, 258, 168)  # NE lava pool
    fill_tiles(chunk, TILE_POISON, 210, 188, 225, 195)  # SW lava pool
    fill_tiles(chunk, TILE_POISON, 245, 188, 258, 195)  # SE lava pool
    # Central broken altar/throne (DS3: Old Demon King's destroyed throne)
    fill_tiles(chunk, TILE_WALL, 228, 172, 238, 180)   # Throne base
    # Arena pillars (DS3: massive stone columns)
    fill_tiles(chunk, TILE_WALL, 215, 165, 217, 170)   # NW pillar
    fill_tiles(chunk, TILE_WALL, 252, 165, 254, 170)   # NE pillar
    fill_tiles(chunk, TILE_WALL, 215, 188, 217, 193)   # SW pillar
    fill_tiles(chunk, TILE_WALL, 252, 188, 254, 193)   # SE pillar
    # Boss fight open floor (ensure clear center)
    fill_tiles(chunk, TILE_GROUND, 220, 170, 250, 190)  # Central arena floor

    # ================================================================
    # 7. LAVA CAVE — side cave with hound rats and demon remains
    # DS3: hidden lava cave beneath the lake shore, Tsorig's domain
    # Section: x=160,y=1280,w=400,h=368 -> tiles (10,80)-(35,103)
    # ================================================================
    # Cave walls (DS3: narrow lava cave)
    fill_tiles(chunk, TILE_WALL, 10, 80, 12, 100)      # West wall
    fill_tiles(chunk, TILE_WALL, 33, 80, 35, 100)      # East wall
    fill_tiles(chunk, TILE_WALL, 10, 80, 30, 82)       # North wall left
    fill_tiles(chunk, TILE_WALL, 10, 100, 25, 103)     # South wall left
    fill_tiles(chunk, TILE_WALL, 30, 100, 35, 103)     # South wall right
    # Lava pool (DS3: lava pool in the cave center)
    fill_tiles(chunk, TILE_POISON, 16, 88, 28, 96)     # Central lava pool
    # Rocky outcroppings (DS3: stone platforms over lava)
    fill_tiles(chunk, TILE_GROUND, 13, 85, 16, 92)     # W platform
    fill_tiles(chunk, TILE_GROUND, 28, 86, 32, 93)     # E platform
    # Demon remains (DS3: demon skeleton in the cave)
    fill_tiles(chunk, TILE_WALL, 20, 84, 22, 86)       # Skeleton debris
    fill_tiles(chunk, TILE_WALL, 26, 96, 28, 98)       # Bone pile

    # ================================================================
    # CONNECTION CORRIDORS — key DS3 route paths
    # ================================================================
    # Abandoned Tomb -> Lake Shore (south-east descent)
    fill_tiles(chunk, TILE_GROUND, 55, 48, 80, 70)
    # Lake Shore -> Ballista Tower (north-east climb)
    fill_tiles(chunk, TILE_GROUND, 155, 55, 170, 65)
    # Lake Shore -> Demon Ruins Entry (south-east descent)
    fill_tiles(chunk, TILE_GROUND, 120, 115, 135, 140)
    # Demon Ruins Entry -> Old King's Antechamber (east)
    fill_tiles(chunk, TILE_GROUND, 160, 140, 175, 155)
    # Old King's Antechamber -> Old Demon King Arena (east)
    fill_tiles(chunk, TILE_GROUND, 210, 150, 220, 165)
    # Lake Shore -> Lava Cave (west, hidden path)
    fill_tiles(chunk, TILE_GROUND, 25, 70, 65, 90)
    # Ballista Tower -> Lake Shore (south drop)
    fill_tiles(chunk, TILE_GROUND, 165, 60, 175, 75)
    # Lake Shore -> Old King's Antechamber (south-east)
    fill_tiles(chunk, TILE_GROUND, 160, 110, 180, 130)

    # ================================================================
    # ADDITIONAL DS3 TERRAIN — lava channels, shore features
    # ================================================================
    # Lava channel from Lake Shore to Demon Ruins (DS3: lava flows down to ruins)
    fill_tiles(chunk, TILE_POISON, 110, 110, 125, 125)
    # Tsorig invasion corridor (DS3: Knight Slayer Tsorig invades near lava)
    fill_tiles(chunk, TILE_GROUND, 50, 95, 70, 110)
    # Carthus Sandworm area — open ground in lake (DS3: sandworm emerges here)
    fill_tiles(chunk, TILE_GROUND, 90, 90, 115, 105)

    # ================================================================
    # FINALIZE — load doc, apply terrain, return
    # ================================================================
    spawn_px, spawn_py = 620, 640  # Abandoned Tomb bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("SmoulderingLake"))
    return finalize_map("SmoulderingLake", chunk, entities, spawn_px, spawn_py)
