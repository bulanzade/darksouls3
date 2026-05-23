from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_ellipse, carve_corridor,
    make_entity, make_field, apply_doc_terrain, finalize_map,
    load_doc,
)



def make_cathedral_deep():
    """Cathedral of the Deep -- DS3-faithful terrain.

    Real DS3 progression from speedrun/walkthrough data:
    1. Cathedral Approach Graveyard -- rain-soaked cemetery with Devout Hollows
    2. Cleansing Chapel -- small chapel interior with bonfire, Cathedral Knights
    3. Exterior Cemetery -- open graveyard, giant shoots arrows, Grave Wardens
    4. Cathedral Main Hall -- grand nave with stone pillars, evangelists, thralls
    5. Rooftops and Buttresses -- flying buttress walkways, gargoyles
    6. Rosaria Route -- slug corridor with Man Grubs, Rosaria's bedchamber
    7. Patches Bridge and Well -- stone bridge trap, Siegward in well
    8. Deacons Altar -- boss arena: dark altar hall with deacon swarm
    9. Deep Accursed Chamber -- ceiling drop ambush room
    10. Interior Rafter Walkways -- narrow beams above nave, thrall ambushes

    Design doc reference: docs/maps/CathedralDeep.json (4608x4096)
    Grid: 288x256 tiles, progression NW to SE then back west for boss.
    """
    chunk = new_chunk(288, 256)

    # ================================================================
    # SECTION 1: Cathedral Approach Graveyard (NW corner)
    # Doc: x=360,y=420,w=1040,h=740 -> tiles 22,26 to 87,72
    # DS3: Rain-soaked graveyard with tombstones, hollow soldiers, cathedral knights
    # ================================================================
    # Main graveyard ground area
    fill_tiles(chunk, TILE_GROUND, 24, 28, 85, 70)
    # Outer wall border (cemetery boundary)
    fill_tiles(chunk, TILE_WALL, 23, 26, 23, 72)
    fill_tiles(chunk, TILE_WALL, 87, 26, 87, 72)
    fill_tiles(chunk, TILE_WALL, 23, 26, 87, 26)
    fill_tiles(chunk, TILE_WALL, 23, 72, 87, 72)
    # Tombstone rows (DS3: rows of gravestones in rain)
    for tx in range(28, 84, 6):
        fill_tiles(chunk, TILE_WALL, tx, 32, tx + 1, 34)
        fill_tiles(chunk, TILE_WALL, tx + 3, 40, tx + 4, 42)
        fill_tiles(chunk, TILE_WALL, tx, 48, tx + 1, 50)
        fill_tiles(chunk, TILE_WALL, tx + 3, 56, tx + 4, 58)
    # Central path through cemetery (DS3: main walk through gravestones)
    fill_tiles(chunk, TILE_GROUND, 50, 28, 60, 72)
    # Side paths (DS3: narrow trails between tombstone clusters)
    fill_tiles(chunk, TILE_GROUND, 30, 44, 82, 46)
    fill_tiles(chunk, TILE_GROUND, 30, 60, 82, 62)

    # ================================================================
    # SECTION 2: Cleansing Chapel (west of center)
    # Doc: x=1260,y=1280,w=680,h=560 -> tiles 78,80 to 120,115
    # DS3: Small church interior with bonfire, cleansing water basin
    # ================================================================
    # Chapel exterior ground
    fill_tiles(chunk, TILE_GROUND, 80, 82, 119, 114)
    # Chapel building walls (DS3: stone chapel with thick walls)
    fill_tiles(chunk, TILE_WALL, 80, 82, 119, 82)      # North wall
    fill_tiles(chunk, TILE_WALL, 80, 114, 119, 114)     # South wall
    fill_tiles(chunk, TILE_WALL, 80, 82, 80, 114)       # West wall
    fill_tiles(chunk, TILE_WALL, 119, 82, 119, 114)     # East wall
    # Chapel interior (hollow out the walls)
    fill_tiles(chunk, TILE_GROUND, 82, 84, 117, 112)
    # Chapel interior pillars (DS3: stone columns flanking the aisle)
    fill_tiles(chunk, TILE_WALL, 88, 88, 90, 108)
    fill_tiles(chunk, TILE_WALL, 109, 88, 111, 108)
    # Altar alcove at north end (DS3: stone basin of cleansing water)
    fill_tiles(chunk, TILE_WALL, 95, 83, 104, 85)
    # Chapel doorways (DS3: entrances on south and east)
    fill_tiles(chunk, TILE_GROUND, 95, 113, 104, 115)   # South entrance
    fill_tiles(chunk, TILE_GROUND, 118, 95, 120, 101)   # East entrance

    # ================================================================
    # SECTION 3: Exterior Cemetery (center-south)
    # Doc: x=1840,y=1780,w=920,h=760 -> tiles 115,111 to 172,158
    # DS3: Open graveyard where giant shoots arrows, grave wardens patrol
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 117, 113, 170, 157)
    # Boundary walls (cemetery edges)
    fill_tiles(chunk, TILE_WALL, 115, 111, 172, 111)
    fill_tiles(chunk, TILE_WALL, 115, 159, 172, 159)
    fill_tiles(chunk, TILE_WALL, 115, 111, 115, 159)
    fill_tiles(chunk, TILE_WALL, 172, 111, 172, 159)
    # Tombstone clusters (DS3: disturbed graves with Infested Corpses)
    for tx in range(120, 168, 8):
        fill_tiles(chunk, TILE_WALL, tx, 118, tx + 2, 120)
        fill_tiles(chunk, TILE_WALL, tx + 4, 130, tx + 6, 132)
        fill_tiles(chunk, TILE_WALL, tx, 142, tx + 2, 144)
    # Cover pillars from giant arrows (DS3: stone cover to hide behind)
    fill_tiles(chunk, TILE_WALL, 130, 124, 133, 126)
    fill_tiles(chunk, TILE_WALL, 150, 136, 153, 138)
    fill_tiles(chunk, TILE_WALL, 125, 148, 128, 150)
    # Central open path (DS3: main route through exterior)
    fill_tiles(chunk, TILE_GROUND, 135, 113, 155, 159)

    # ================================================================
    # SECTION 4: Cathedral Main Hall (center-east)
    # Doc: x=2460,y=1320,w=980,h=760 -> tiles 153,82 to 214,129
    # DS3: Grand cathedral nave with massive stone pillars, evangelists
    # ================================================================
    # Cathedral exterior walls (DS3: massive gothic cathedral walls)
    fill_tiles(chunk, TILE_WALL, 154, 83, 214, 83)      # North wall
    fill_tiles(chunk, TILE_WALL, 154, 129, 214, 129)     # South wall
    fill_tiles(chunk, TILE_WALL, 154, 83, 154, 129)      # West wall
    fill_tiles(chunk, TILE_WALL, 214, 83, 214, 129)      # East wall
    # Cathedral nave interior
    fill_tiles(chunk, TILE_GROUND, 156, 85, 212, 127)
    # Nave pillars -- two rows flanking the central aisle (DS3: grand stone columns)
    for ty in range(88, 126, 8):
        fill_tiles(chunk, TILE_WALL, 165, ty, 168, ty + 3)    # Left pillar row
        fill_tiles(chunk, TILE_WALL, 200, ty, 203, ty + 3)    # Right pillar row
    # Central nave aisle (DS3: long central walk between pillars)
    fill_tiles(chunk, TILE_GROUND, 170, 85, 198, 127)
    # Side aisles along walls (DS3: narrow passages on each side)
    fill_tiles(chunk, TILE_GROUND, 157, 88, 163, 126)
    fill_tiles(chunk, TILE_GROUND, 206, 88, 212, 126)
    # Cathedral entrance doorway (west side, connecting to exterior cemetery)
    fill_tiles(chunk, TILE_GROUND, 154, 100, 156, 110)
    # Cathedral eastern door (connecting to rafter area)
    fill_tiles(chunk, TILE_GROUND, 212, 95, 214, 105)
    # Altar platform at north end (DS3: raised altar area with evangelist)
    fill_tiles(chunk, TILE_WALL, 175, 84, 193, 86)
    fill_tiles(chunk, TILE_WALLTOP, 175, 83, 193, 83)
    fill_tiles(chunk, TILE_GROUND, 177, 87, 191, 90)

    # ================================================================
    # SECTION 5: Rooftops and Buttresses (NE area)
    # Doc: x=3100,y=560,w=980,h=660 -> tiles 193,35 to 254,76
    # DS3: Rooftop walkways with flying buttresses, gargoyle encounter
    # ================================================================
    # Rooftop platform ground (DS3: stone rooftops in rain)
    fill_tiles(chunk, TILE_GROUND, 195, 37, 252, 75)
    # Buttress walls (DS3: flying buttress supports create corridors)
    fill_tiles(chunk, TILE_WALL, 200, 40, 202, 50)
    fill_tiles(chunk, TILE_WALL, 215, 45, 217, 55)
    fill_tiles(chunk, TILE_WALL, 230, 40, 232, 50)
    fill_tiles(chunk, TILE_WALL, 242, 50, 244, 60)
    # Rooftop boundary walls
    fill_tiles(chunk, TILE_WALL, 194, 35, 253, 35)      # North
    fill_tiles(chunk, TILE_WALL, 194, 76, 253, 76)       # South
    # Gargoyle perch (DS3: gargoyle ambush point on rooftop)
    fill_tiles(chunk, TILE_WALL, 220, 37, 226, 39)
    # Path through rooftops (DS3: walkway connecting nave to rafters)
    fill_tiles(chunk, TILE_GROUND, 205, 37, 245, 40)
    fill_tiles(chunk, TILE_GROUND, 205, 72, 245, 75)

    # ================================================================
    # SECTION 6: Rosaria Route (far east)
    # Doc: x=3820,y=1080,w=780,h=620 -> tiles 238,67 to 286,107
    # DS3: Slug corridor with Man Grubs leading to Rosaria's bedchamber
    # ================================================================
    # Slug corridor ground
    fill_tiles(chunk, TILE_GROUND, 240, 69, 284, 106)
    # Corridor walls (DS3: narrow passage with slime on walls)
    fill_tiles(chunk, TILE_WALL, 239, 67, 285, 67)      # North wall
    fill_tiles(chunk, TILE_WALL, 239, 108, 285, 108)     # South wall
    # Man Grub alcoves (DS3: side chambers where grubs gather)
    fill_tiles(chunk, TILE_WALL, 250, 70, 252, 74)
    fill_tiles(chunk, TILE_WALL, 265, 75, 267, 79)
    fill_tiles(chunk, TILE_WALL, 248, 90, 250, 94)
    fill_tiles(chunk, TILE_WALL, 270, 95, 272, 99)
    # Rosaria's bedchamber (DS3: candlelit chamber with pale tongue offering)
    fill_tiles(chunk, TILE_GROUND, 270, 78, 283, 104)
    # Bedchamber walls
    fill_tiles(chunk, TILE_WALL, 269, 77, 284, 77)
    fill_tiles(chunk, TILE_WALL, 269, 105, 284, 105)
    fill_tiles(chunk, TILE_WALL, 269, 77, 269, 105)
    fill_tiles(chunk, TILE_WALL, 284, 77, 284, 105)
    fill_tiles(chunk, TILE_GROUND, 271, 79, 282, 103)
    # Bedchamber entrance (DS3: doorway into Rosaria's room)
    fill_tiles(chunk, TILE_GROUND, 269, 88, 271, 94)

    # ================================================================
    # SECTION 7: Patches Bridge and Well (southwest)
    # Doc: x=1180,y=2060,w=880,h=520 -> tiles 73,128 to 128,160
    # DS3: Stone bridge where Patches kicks you, Siegward stuck in well
    # ================================================================
    # Bridge and well area ground
    fill_tiles(chunk, TILE_GROUND, 75, 130, 126, 158)
    # Area boundary walls
    fill_tiles(chunk, TILE_WALL, 74, 128, 127, 128)
    fill_tiles(chunk, TILE_WALL, 74, 159, 127, 159)
    fill_tiles(chunk, TILE_WALL, 74, 128, 74, 159)
    fill_tiles(chunk, TILE_WALL, 127, 128, 127, 159)
    # Stone bridge (DS3: narrow bridge where Patches traps you)
    fill_tiles(chunk, TILE_WALL, 80, 132, 120, 133)
    fill_tiles(chunk, TILE_WALLTOP, 80, 131, 120, 131)
    fill_tiles(chunk, TILE_GROUND, 82, 134, 118, 155)
    # Well (DS3: Siegward trapped in well, circular stone well)
    carve_ellipse(chunk, 100, 148, 5, 4)
    fill_tiles(chunk, TILE_WALL, 95, 144, 105, 152)
    fill_tiles(chunk, TILE_GROUND, 97, 146, 103, 150)
    # Bridge supports (DS3: stone pillars supporting the bridge)
    fill_tiles(chunk, TILE_WALL, 82, 140, 84, 155)
    fill_tiles(chunk, TILE_WALL, 116, 140, 118, 155)
    # Entrance from cemetery (north)
    fill_tiles(chunk, TILE_GROUND, 90, 128, 110, 130)

    # ================================================================
    # SECTION 8: Deacons Altar (south-center)
    # Doc: x=2600,y=3120,w=1020,h=720 -> tiles 162,195 to 225,240
    # DS3: Boss arena -- dark hall with deep fire, deacon swarm
    # ================================================================
    # Boss arena ground
    fill_tiles(chunk, TILE_GROUND, 164, 197, 223, 238)
    # Arena walls (DS3: enclosed dark cathedral hall)
    fill_tiles(chunk, TILE_WALL, 163, 195, 224, 195)    # North wall
    fill_tiles(chunk, TILE_WALL, 163, 239, 224, 239)    # South wall
    fill_tiles(chunk, TILE_WALL, 163, 195, 163, 239)    # West wall
    fill_tiles(chunk, TILE_WALL, 224, 195, 224, 239)    # East wall
    # Arena interior
    fill_tiles(chunk, TILE_GROUND, 165, 197, 222, 237)
    # Altar platform at north end (DS3: raised altar where archdeacon stands)
    fill_tiles(chunk, TILE_WALL, 180, 196, 207, 199)
    fill_tiles(chunk, TILE_WALLTOP, 180, 195, 207, 195)
    fill_tiles(chunk, TILE_GROUND, 182, 200, 205, 203)
    # Altar pillars (DS3: stone columns flanking the altar)
    fill_tiles(chunk, TILE_WALL, 172, 205, 175, 220)
    fill_tiles(chunk, TILE_WALL, 212, 205, 215, 220)
    # Side chapel alcoves (DS3: recessed areas where deacons gather)
    fill_tiles(chunk, TILE_WALL, 166, 210, 170, 230)
    fill_tiles(chunk, TILE_GROUND, 167, 211, 169, 229)
    fill_tiles(chunk, TILE_WALL, 217, 210, 221, 230)
    fill_tiles(chunk, TILE_GROUND, 218, 211, 220, 229)
    # Arena entrance (west side)
    fill_tiles(chunk, TILE_GROUND, 163, 210, 165, 225)

    # ================================================================
    # SECTION 9: Deep Accursed Chamber (between Main Hall and Rafter)
    # Doc: x=2200,y=900,w=600,h=400 -> tiles 137,56 to 174,81
    # DS3: Ceiling drop ambush, curse pools, stone chamber
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 139, 58, 172, 79)
    # Chamber walls
    fill_tiles(chunk, TILE_WALL, 138, 56, 173, 56)
    fill_tiles(chunk, TILE_WALL, 138, 80, 173, 80)
    fill_tiles(chunk, TILE_WALL, 138, 56, 138, 80)
    fill_tiles(chunk, TILE_WALL, 173, 56, 173, 80)
    # Interior pillars (DS3: stone columns in the ambush room)
    fill_tiles(chunk, TILE_WALL, 148, 62, 150, 66)
    fill_tiles(chunk, TILE_WALL, 160, 62, 162, 66)
    fill_tiles(chunk, TILE_WALL, 148, 72, 150, 76)
    fill_tiles(chunk, TILE_WALL, 160, 72, 162, 76)
    # Central passage (DS3: path through the chamber)
    fill_tiles(chunk, TILE_GROUND, 140, 65, 172, 68)
    # Entrance from nave area (south)
    fill_tiles(chunk, TILE_GROUND, 155, 78, 158, 82)

    # ================================================================
    # SECTION 10: Interior Rafter Walkways (NE, above Main Hall)
    # Doc: x=3300,y=660,w=700,h=440 -> tiles 206,41 to 249,68
    # DS3: Narrow wooden beams high above nave, thrall ambush points
    # ================================================================
    # Rafter walkway ground (DS3: narrow wooden beams)
    fill_tiles(chunk, TILE_GROUND, 208, 43, 247, 67)
    # Rafter boundary walls
    fill_tiles(chunk, TILE_WALL, 207, 41, 248, 41)
    fill_tiles(chunk, TILE_WALL, 207, 68, 248, 68)
    # Wooden beam supports (DS3: cross-beams creating narrow walkways)
    fill_tiles(chunk, TILE_WALL, 210, 46, 212, 50)
    fill_tiles(chunk, TILE_WALL, 220, 50, 222, 54)
    fill_tiles(chunk, TILE_WALL, 230, 46, 232, 50)
    fill_tiles(chunk, TILE_WALL, 240, 50, 242, 54)
    # Thrall ambush ledges (DS3: ceiling positions where thralls drop)
    fill_tiles(chunk, TILE_WALL, 215, 42, 218, 44)
    fill_tiles(chunk, TILE_WALL, 235, 42, 238, 44)
    fill_tiles(chunk, TILE_WALL, 225, 65, 228, 67)
    # Central walkway (DS3: main beam path through rafters)
    fill_tiles(chunk, TILE_GROUND, 210, 55, 245, 58)
    # Connection down to main hall (south)
    fill_tiles(chunk, TILE_GROUND, 215, 68, 220, 82)

    # ================================================================
    # CONNECTIONS BETWEEN SECTIONS
    # DS3: Cathedral is interconnected via corridors, shortcuts, and lifts
    # ================================================================

    # Cemetery -> Cleansing Chapel (DS3: descend from graveyard into chapel)
    fill_tiles(chunk, TILE_GROUND, 60, 70, 90, 84)
    carve_corridor(chunk, 75, 72, 95, 90, width=5)

    # Cleansing Chapel -> Exterior Cemetery (DS3: exit chapel into exterior)
    fill_tiles(chunk, TILE_GROUND, 110, 110, 130, 115)
    carve_corridor(chunk, 108, 108, 135, 120, width=5)

    # Cleansing Chapel -> Cathedral Main Hall (DS3: enter cathedral from side)
    fill_tiles(chunk, TILE_GROUND, 118, 95, 158, 100)
    carve_corridor(chunk, 119, 97, 155, 102, width=5)

    # Exterior Cemetery -> Patches Bridge (DS3: cemetery leads to bridge trap)
    fill_tiles(chunk, TILE_GROUND, 115, 155, 100, 160)
    carve_corridor(chunk, 130, 155, 100, 145, width=5)

    # Cathedral Main Hall -> Deep Accursed Chamber (DS3: side passage to ambush room)
    fill_tiles(chunk, TILE_GROUND, 155, 82, 155, 62)
    carve_corridor(chunk, 160, 85, 155, 62, width=5)

    # Deep Accursed Chamber -> Rafter Walkways (DS3: climb up to rafters)
    carve_corridor(chunk, 165, 62, 210, 50, width=5)

    # Rafter Walkways -> Rooftops (DS3: rafters connect to rooftop area)
    fill_tiles(chunk, TILE_GROUND, 210, 50, 210, 42)
    carve_corridor(chunk, 210, 50, 210, 40, width=5)

    # Cathedral Main Hall -> Deacons Altar (DS3: descend to boss arena)
    fill_tiles(chunk, TILE_GROUND, 155, 127, 180, 198)
    carve_corridor(chunk, 165, 127, 170, 197, width=5)

    # Rooftops -> Rosaria Route (DS3: cross rooftops to reach slug corridor)
    fill_tiles(chunk, TILE_GROUND, 248, 72, 248, 80)
    carve_corridor(chunk, 248, 72, 245, 80, width=5)
    fill_tiles(chunk, TILE_GROUND, 240, 76, 250, 80)

    # Deacons Altar -> Cleansing Chapel shortcut (DS3: lift shortcut back)
    carve_corridor(chunk, 170, 197, 100, 115, width=3)

    # Cemetery entry from Road of Sacrifices (DS3: fog gate from previous area)
    fill_tiles(chunk, TILE_GROUND, 22, 38, 26, 42)

    # ================================================================
    # ARCHITECTURAL DETAILS
    # ================================================================

    # Cathedral Approach -- entry path from fog gate (DS3: rain-soaked entry)
    fill_tiles(chunk, TILE_GROUND, 26, 30, 50, 40)
    # Entry archway stones (DS3: stone arch marking cemetery entrance)
    fill_tiles(chunk, TILE_WALL, 26, 28, 27, 32)
    fill_tiles(chunk, TILE_WALL, 49, 28, 50, 32)

    # Cathedral nave -- side chapel alcoves (DS3: recessed side rooms off the nave)
    fill_tiles(chunk, TILE_GROUND, 156, 95, 162, 100)
    fill_tiles(chunk, TILE_GROUND, 207, 95, 212, 100)
    fill_tiles(chunk, TILE_GROUND, 156, 115, 162, 120)
    fill_tiles(chunk, TILE_GROUND, 207, 115, 212, 120)

    # Giant's tower base in exterior cemetery (DS3: tower where giant shoots arrows)
    fill_tiles(chunk, TILE_WALL, 155, 120, 162, 130)
    fill_tiles(chunk, TILE_GROUND, 157, 122, 160, 128)

    # Cemetery entrance path (DS3: path from fog gate into graveyard)
    fill_tiles(chunk, TILE_GROUND, 24, 32, 30, 36)

    # ================================================================
    # ENTITIES -- only PlayerSpawn needed; doc provides all others
    # ================================================================
    entities = []

    spawn_px, spawn_py = 560, 620
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # Fill terrain from JSON doc sections (authoritative for entity positions)
    apply_doc_terrain(chunk, load_doc("CathedralDeep"))
    return finalize_map("CathedralDeep", chunk, entities, spawn_px, spawn_py)
