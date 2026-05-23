from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_road_of_sacrifices():
    """Road of Sacrifices — DS3-faithful terrain.

    Dark forest with winding paths through dense woods. Features ruined stone
    walls, dense forest, cliff edges, crucifixion area with hanging bodies,
    and a split path to Farron Keep or Cathedral of the Deep.

    Layout: Corvian Woods entry -> Halfway Fortress -> Crucifixion Woods ->
    Farron Keep Gate (south branch) + Crystal Sage Ruins (east) ->
    Cathedral Road (far east).

    JSON doc is authoritative for entity positions; apply_doc_terrain() fills
    section interiors and carves corridors between them.
    """
    chunk = new_chunk(288, 224)

    # ================================================================
    # 1. CORVIAN WOODS — entry dark forest
    # DS3: narrow winding path through dark forest, Corvian ambush points,
    # overturned coach, tree root obstacles, Lycanthropes in undergrowth
    # Section: x=300,y=300 -> tiles (18,18)-(77,62)
    # ================================================================
    # Forest boundary walls (DS3: dense trees form natural walls)
    fill_tiles(chunk, TILE_WALL, 18, 18, 20, 45)     # West tree line
    fill_tiles(chunk, TILE_WALL, 72, 18, 77, 45)     # East tree line
    fill_tiles(chunk, TILE_WALL, 18, 18, 60, 20)     # North tree canopy
    # Overturned coach debris (DS3: carriage on its side in the forest)
    fill_tiles(chunk, TILE_WALL, 30, 28, 34, 31)
    # Tree root obstacles (DS3: massive exposed roots block the path)
    fill_tiles(chunk, TILE_WALL, 38, 22, 40, 25)
    fill_tiles(chunk, TILE_WALL, 50, 30, 52, 33)
    fill_tiles(chunk, TILE_WALL, 44, 38, 46, 41)
    fill_tiles(chunk, TILE_WALL, 55, 24, 57, 27)
    # Corvian ambush trees (DS3: Corvians perch in dense canopy)
    fill_tiles(chunk, TILE_WALL, 24, 24, 25, 26)
    fill_tiles(chunk, TILE_WALL, 62, 32, 63, 34)
    fill_tiles(chunk, TILE_WALL, 35, 42, 36, 44)
    fill_tiles(chunk, TILE_WALL, 68, 40, 69, 42)
    # Hollow tree stump cluster (DS3: dead tree stumps)
    fill_tiles(chunk, TILE_WALL, 28, 35, 29, 37)
    fill_tiles(chunk, TILE_WALL, 58, 36, 59, 38)
    # Cliff edge stones (DS3: path runs along cliff)
    fill_tiles(chunk, TILE_WALL, 22, 50, 25, 55)
    fill_tiles(chunk, TILE_WALL, 60, 50, 63, 55)

    # ================================================================
    # 2. HALFWAY FORTRESS — ruined stone fortress
    # DS3: stone ruin with bonfire room, Anri and Horace sitting inside,
    # multi-room interior with collapsed walls
    # Section: x=1220,y=900 -> tiles (76,56)-(121,88)
    # ================================================================
    # Fortress exterior walls (DS3: stone fortress ruins)
    fill_tiles(chunk, TILE_WALL, 76, 56, 78, 85)     # West wall
    fill_tiles(chunk, TILE_WALL, 118, 56, 121, 85)   # East wall
    fill_tiles(chunk, TILE_WALL, 76, 56, 95, 58)     # North wall left
    fill_tiles(chunk, TILE_WALL, 105, 56, 121, 58)   # North wall right
    fill_tiles(chunk, TILE_WALL, 76, 85, 95, 88)     # South wall left
    fill_tiles(chunk, TILE_WALL, 105, 85, 121, 88)   # South wall right
    # Interior room divider (DS3: wall separating bonfire room from entry)
    fill_tiles(chunk, TILE_WALL, 92, 62, 94, 78)
    # Stone archway pillars (DS3: arched stone entry to bonfire room)
    fill_tiles(chunk, TILE_WALL, 85, 60, 87, 65)
    fill_tiles(chunk, TILE_WALL, 108, 60, 110, 65)
    # Collapsed wall section (DS3: partially collapsed stone wall)
    fill_tiles(chunk, TILE_WALL, 100, 72, 105, 74)
    # Fortress doorway rubble (DS3: debris in doorway)
    fill_tiles(chunk, TILE_WALL, 115, 68, 117, 70)
    # Bench stones (DS3: Anri and Horace sit on stone bench)
    fill_tiles(chunk, TILE_WALL, 80, 76, 82, 78)

    # ================================================================
    # 3. CRUCIFIXION WOODS — wide wetland forest
    # DS3: sprawling wetland with shallow water, ruined structures,
    # crucified hollows on trees, crabs in water, Exile guards
    # Section: x=1880,y=1280 -> tiles (117,80)-(197,133)
    # ================================================================
    # Forest edge walls (DS3: dense trees border the wetland)
    fill_tiles(chunk, TILE_WALL, 117, 80, 120, 100)  # NW tree line
    fill_tiles(chunk, TILE_WALL, 117, 115, 120, 133) # SW tree line
    fill_tiles(chunk, TILE_WALL, 190, 80, 197, 100)  # NE tree line
    fill_tiles(chunk, TILE_WALL, 190, 115, 197, 133) # SE tree line
    # Ruined stone structure (DS3: collapsed building in the swamp)
    fill_tiles(chunk, TILE_WALL, 130, 88, 132, 105)  # Left wall
    fill_tiles(chunk, TILE_WALL, 145, 88, 147, 105)  # Right wall
    fill_tiles(chunk, TILE_WALL, 130, 88, 140, 90)   # North wall
    fill_tiles(chunk, TILE_WALL, 130, 103, 140, 105) # South wall
    # Crucifixion crosses (DS3: hollows crucified on wooden crosses)
    fill_tiles(chunk, TILE_WALL, 125, 95, 126, 97)
    fill_tiles(chunk, TILE_WALL, 135, 110, 136, 112)
    fill_tiles(chunk, TILE_WALL, 155, 92, 156, 94)
    fill_tiles(chunk, TILE_WALL, 170, 105, 171, 107)
    fill_tiles(chunk, TILE_WALL, 160, 118, 161, 120)
    # Fallen tree trunks (DS3: horizontal logs across swamp)
    fill_tiles(chunk, TILE_WALL, 140, 115, 155, 116)
    fill_tiles(chunk, TILE_WALL, 165, 95, 178, 96)
    # Swamp rock clusters (DS3: rocks poking out of shallow water)
    fill_tiles(chunk, TILE_WALL, 150, 100, 152, 102)
    fill_tiles(chunk, TILE_WALL, 175, 110, 177, 112)
    fill_tiles(chunk, TILE_WALL, 122, 108, 124, 110)
    # Wetland shallow water patches (DS3: flooded forest floor)
    fill_tiles(chunk, TILE_POISON, 135, 95, 142, 100)
    fill_tiles(chunk, TILE_POISON, 160, 108, 172, 118)
    fill_tiles(chunk, TILE_POISON, 148, 120, 158, 128)

    # ================================================================
    # 4. FARRON KEEP GATE — stone gate descending to swamp
    # DS3: stone gate with Exile guards, path descending to Farron Keep,
    # fortress ruins with Black Knight patrol nearby
    # Section: x=1960,y=2220 -> tiles (122,138)-(169,176)
    # ================================================================
    # Gate fortress walls (DS3: stone gate structure)
    fill_tiles(chunk, TILE_WALL, 122, 138, 125, 170) # West wall
    fill_tiles(chunk, TILE_WALL, 165, 138, 169, 170) # East wall
    fill_tiles(chunk, TILE_WALL, 122, 138, 145, 140) # North wall left
    fill_tiles(chunk, TILE_WALL, 155, 138, 169, 140) # North wall right
    fill_tiles(chunk, TILE_WALL, 122, 173, 145, 176) # South wall left
    fill_tiles(chunk, TILE_WALL, 155, 173, 169, 176) # South wall right
    # Stone gate pillars (DS3: massive stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 130, 145, 133, 155)
    fill_tiles(chunk, TILE_WALL, 158, 145, 161, 155)
    # Descending path ruins (DS3: crumbling steps to swamp)
    fill_tiles(chunk, TILE_WALL, 138, 160, 140, 165)
    fill_tiles(chunk, TILE_WALL, 152, 160, 154, 165)
    # Exile guard posts (DS3: two Exiles guard the entrance)
    fill_tiles(chunk, TILE_WALL, 135, 148, 136, 150)
    fill_tiles(chunk, TILE_WALL, 155, 148, 156, 150)
    # Ruined wall fragments (DS3: partial walls from old fortress)
    fill_tiles(chunk, TILE_WALL, 140, 142, 142, 144)
    fill_tiles(chunk, TILE_WALL, 150, 168, 152, 170)

    # ================================================================
    # 5. CRYSTAL SAGE RUINS — rocky cave with crystal formations
    # DS3: open rocky cave with crystal growths, hollow sorcerers,
    # boss arena with crystal obstacles, magical crystal pillars
    # Section: x=3080,y=2040 -> tiles (192,127)-(245,172)
    # ================================================================
    # Cave boundary walls (DS3: rocky cave walls)
    fill_tiles(chunk, TILE_WALL, 192, 127, 195, 165) # West wall
    fill_tiles(chunk, TILE_WALL, 240, 127, 245, 165) # East wall
    fill_tiles(chunk, TILE_WALL, 192, 127, 220, 130) # North wall left
    fill_tiles(chunk, TILE_WALL, 230, 127, 245, 130) # North wall right
    fill_tiles(chunk, TILE_WALL, 192, 168, 220, 172) # South wall left
    fill_tiles(chunk, TILE_WALL, 230, 168, 245, 172) # South wall right
    # Crystal formations (DS3: glowing crystal growths throughout cave)
    fill_tiles(chunk, TILE_WALL, 200, 135, 203, 138) # Crystal cluster 1
    fill_tiles(chunk, TILE_WALL, 225, 140, 228, 143) # Crystal cluster 2
    fill_tiles(chunk, TILE_WALL, 210, 155, 213, 158) # Crystal cluster 3
    fill_tiles(chunk, TILE_WALL, 235, 150, 238, 153) # Crystal cluster 4
    # Rocky pillars (DS3: natural stone pillars in cave)
    fill_tiles(chunk, TILE_WALL, 205, 145, 207, 150)
    fill_tiles(chunk, TILE_WALL, 220, 160, 222, 165)
    # Crystal shard debris (DS3: scattered crystal fragments)
    fill_tiles(chunk, TILE_WALL, 215, 133, 216, 135)
    fill_tiles(chunk, TILE_WALL, 230, 158, 231, 160)
    fill_tiles(chunk, TILE_WALL, 198, 162, 199, 164)

    # ================================================================
    # 6. CATHEDRAL ROAD — forest path to Cathedral of the Deep
    # DS3: dense forest path branching east, ruined archway,
    # dense trees with hollow ambush
    # Section: x=3560,y=1280 -> tiles (222,80)-(264,115)
    # ================================================================
    # Dense tree walls (DS3: forest path bordered by thick trees)
    fill_tiles(chunk, TILE_WALL, 222, 80, 224, 105)  # West tree line
    fill_tiles(chunk, TILE_WALL, 260, 80, 264, 105)  # East tree line
    fill_tiles(chunk, TILE_WALL, 222, 80, 250, 82)   # North canopy
    fill_tiles(chunk, TILE_WALL, 222, 110, 250, 115) # South undergrowth
    fill_tiles(chunk, TILE_WALL, 258, 110, 264, 115) # SE trees
    # Ruined archway (DS3: stone arch marking path to Cathedral)
    fill_tiles(chunk, TILE_WALL, 232, 85, 234, 100)  # Left arch pillar
    fill_tiles(chunk, TILE_WALL, 248, 85, 250, 100)  # Right arch pillar
    fill_tiles(chunk, TILE_WALL, 232, 85, 243, 87)   # Arch top left
    fill_tiles(chunk, TILE_WALL, 243, 85, 250, 87)   # Arch top right
    # Fallen tree obstacles (DS3: trees blocking the path)
    fill_tiles(chunk, TILE_WALL, 226, 92, 228, 94)
    fill_tiles(chunk, TILE_WALL, 254, 95, 256, 97)
    # Dense undergrowth (DS3: thick bushes)
    fill_tiles(chunk, TILE_WALL, 238, 103, 240, 105)
    fill_tiles(chunk, TILE_WALL, 252, 108, 254, 110)

    # ================================================================
    # CONNECTION CORRIDORS — DS3 route paths
    # ================================================================
    # Corvian Woods -> Halfway Fortress (east)
    fill_tiles(chunk, TILE_GROUND, 60, 35, 95, 60)
    # Halfway Fortress -> Crucifixion Woods (east)
    fill_tiles(chunk, TILE_GROUND, 100, 70, 135, 90)
    # Crucifixion Woods -> Farron Keep Gate (south)
    fill_tiles(chunk, TILE_GROUND, 140, 115, 155, 145)
    # Crucifixion Woods -> Crystal Sage Ruins (east)
    fill_tiles(chunk, TILE_GROUND, 175, 100, 210, 135)
    # Crystal Sage Ruins -> Cathedral Road (north-east)
    fill_tiles(chunk, TILE_GROUND, 230, 120, 245, 100)
    # Farron Keep Gate -> Crystal Sage approach (east)
    fill_tiles(chunk, TILE_GROUND, 160, 155, 200, 140)

    # ================================================================
    # FINALIZE
    # ================================================================
    spawn_px, spawn_py = 520, 520  # Road of Sacrifices bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("RoadOfSacrifices"))
    return finalize_map("RoadOfSacrifices", chunk, entities, spawn_px, spawn_py)
