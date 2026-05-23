from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_corridor, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)


# Map size: 3584x3072 px = 224x192 tiles


def make_profaned_capital():
    """Profaned Capital -- DS3-faithful terrain.

    Ruined capital consumed by the Profaned Flame. Features a tower with
    Gilligan's body, collapsed city ruins, a flooded prison, fire-scorched
    palace, and Yhorm the Giant's throne room with the Storm Ruler.

    Route (DS3):
      1. Enter from Irithyll Dungeon via stone bridge (Sewer Entrance)
      2. Tower bonfire room (Gilligan's body, Stretch Out gesture)
      3. EXPLORE PATH (south): descent -> Collapsed Exterior -> Flooded Cells
         (Monstrosities, Sewer Centipedes) -> Palace Ruins (Siegward's cell,
         Court Sorcerer roof, Jailer Handmaids, treasure rooms)
      4. BOSS PATH (southeast): Yhorm Bridge (Jailers, Gargoyles)
         -> Yhorm Throne Room (boss arena with Storm Ruler pedestal)

    JSON doc sections (pixel -> tile = pixel // 16):
      1. Sewer Entrance:          (5,6)-(15,16)     -- drain pipe from Irithyll Dungeon
      2. Profaned Capital Tower:  (41,35)-(84,73)   -- bonfire room, Gilligan's ladder
      3. Collapsed Exterior:      (67,76)-(128,123) -- broken walls, ruined houses
      4. Palace Ruins:            (118,73)-(169,116)-- fire ruins, Siegward's cell, roof
      5. Flooded Cells:           (53,145)-(119,189)-- stagnant water, Sewer Centipedes
      6. Yhorm Bridge:            (143,141)-(194,173)-- stone bridge, Jailer rooms
      7. Yhorm Throne Room:       (165,182)-(221,225)-- boss arena, Storm Ruler, throne
    """
    chunk = new_chunk(224, 192)

    # ================================================================
    # 1. SEWER ENTRANCE  (doc: x=80,y=96,w=160,h=160)
    #    tiles: (5,6)-(15,16)
    #    DS3: narrow drain pipe from Irithyll Dungeon, stone arch
    # ================================================================
    # Sewer pipe walls (DS3: cramped stone tunnel entrance)
    fill_tiles(chunk, TILE_WALL, 5, 6, 7, 16)         # West wall
    fill_tiles(chunk, TILE_WALL, 13, 6, 15, 16)        # East wall
    fill_tiles(chunk, TILE_WALL, 5, 6, 15, 8)          # North wall
    fill_tiles(chunk, TILE_WALL, 5, 14, 15, 16)        # South wall
    # Drain grate pillars (DS3: stone supports in sewer)
    fill_tiles(chunk, TILE_WALL, 8, 9, 9, 11)          # Left grate
    fill_tiles(chunk, TILE_WALL, 11, 9, 12, 11)        # Right grate

    # ================================================================
    # 2. PROFANED CAPITAL TOWER  (doc: x=660,y=560,w=700,h=620)
    #    tiles: (41,35)-(84,73)
    #    DS3: bonfire room, Gilligan's broken ladder, tower staircase
    # ================================================================
    # Tower boundary walls (DS3: cylindrical stone tower interior)
    fill_tiles(chunk, TILE_WALL, 41, 35, 43, 71)       # West wall
    fill_tiles(chunk, TILE_WALL, 82, 35, 84, 71)       # East wall
    fill_tiles(chunk, TILE_WALL, 41, 35, 82, 37)       # North wall
    fill_tiles(chunk, TILE_WALL, 41, 71, 60, 73)       # South wall left
    fill_tiles(chunk, TILE_WALL, 68, 71, 84, 73)       # South wall right
    # Gilligan's ladder alcove (DS3: Gilligan's body at top of broken ladder)
    fill_tiles(chunk, TILE_WALL, 45, 40, 47, 44)       # Ladder alcove wall
    fill_tiles(chunk, TILE_WALL, 50, 39, 51, 42)       # Ladder support
    # Tower spiral staircase supports (DS3: curved stone stairs)
    fill_tiles(chunk, TILE_WALL, 55, 42, 57, 45)       # Stair segment 1
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 51)       # Stair segment 2
    fill_tiles(chunk, TILE_WALL, 58, 55, 60, 58)       # Stair segment 3
    # Bonfire alcove walls (DS3: bonfire set in stone alcove)
    fill_tiles(chunk, TILE_WALL, 48, 50, 50, 52)       # Left alcove
    fill_tiles(chunk, TILE_WALL, 54, 50, 56, 52)       # Right alcove
    # Window embrasure (DS3: tower window overlooking capital)
    fill_tiles(chunk, TILE_WALL, 78, 42, 80, 44)
    # Crumbling wall debris (DS3: age-damaged tower interior)
    fill_tiles(chunk, TILE_WALL, 44, 62, 46, 64)
    fill_tiles(chunk, TILE_WALL, 74, 65, 76, 67)

    # ================================================================
    # 3. COLLAPSED EXTERIOR  (doc: x=1080,y=1220,w=980,h=760)
    #    tiles: (67,76)-(128,123)
    #    DS3: broken walls, ruined houses, upper ruins descent
    # ================================================================
    # Exterior boundary walls (DS3: collapsed city walls)
    fill_tiles(chunk, TILE_WALL, 67, 76, 69, 121)      # West wall
    fill_tiles(chunk, TILE_WALL, 126, 76, 128, 121)    # East wall
    fill_tiles(chunk, TILE_WALL, 67, 76, 125, 78)      # North wall
    fill_tiles(chunk, TILE_WALL, 67, 121, 95, 123)     # South wall left
    fill_tiles(chunk, TILE_WALL, 105, 121, 128, 123)   # South wall right
    # Ruined house walls (DS3: collapsed buildings line the streets)
    fill_tiles(chunk, TILE_WALL, 75, 83, 78, 88)       # House 1 wall
    fill_tiles(chunk, TILE_WALL, 85, 82, 87, 90)       # House 2 wall
    fill_tiles(chunk, TILE_WALL, 95, 85, 98, 92)       # House 3 wall
    fill_tiles(chunk, TILE_WALL, 108, 83, 111, 90)     # House 4 wall
    fill_tiles(chunk, TILE_WALL, 118, 86, 120, 93)     # House 5 wall
    # Broken archways (DS3: stone arches between ruined buildings)
    fill_tiles(chunk, TILE_WALL, 80, 95, 82, 100)      # Arch debris
    fill_tiles(chunk, TILE_WALL, 100, 96, 102, 102)    # Arch debris 2
    # Rubble piles (DS3: destroyed masonry)
    fill_tiles(chunk, TILE_WALL, 72, 108, 74, 112)     # Rubble NW
    fill_tiles(chunk, TILE_WALL, 90, 110, 92, 114)     # Rubble center
    fill_tiles(chunk, TILE_WALL, 115, 108, 117, 113)   # Rubble SE
    # Crumbled fountain (DS3: ruined city square)
    fill_tiles(chunk, TILE_WALL, 82, 105, 86, 108)
    # Collapsed stairs descent (DS3: stairs leading down to lower capital)
    fill_tiles(chunk, TILE_WALL, 70, 115, 72, 118)     # Stair wall
    fill_tiles(chunk, TILE_WALL, 76, 117, 78, 120)     # Stair wall 2

    # ================================================================
    # 4. PALACE RUINS  (doc: x=1900,y=1180,w=820,h=700)
    #    tiles: (118,73)-(169,116)
    #    DS3: fire-scorched palace, Siegward's cell, Court Sorcerer roof,
    #    roof obstacles, treasure rooms, Jailer Handmaids
    # ================================================================
    # Palace boundary walls (DS3: burned palace structure)
    fill_tiles(chunk, TILE_WALL, 118, 73, 120, 114)    # West wall
    fill_tiles(chunk, TILE_WALL, 167, 73, 169, 114)    # East wall
    fill_tiles(chunk, TILE_WALL, 118, 73, 167, 75)     # North wall
    fill_tiles(chunk, TILE_WALL, 118, 114, 140, 116)   # South wall left
    fill_tiles(chunk, TILE_WALL, 150, 114, 169, 116)   # South wall right
    # Siegward's cell (DS3: iron-barred cell holding Siegward of Catarina)
    fill_tiles(chunk, TILE_WALL, 122, 80, 124, 88)     # Cell west wall
    fill_tiles(chunk, TILE_WALL, 130, 80, 132, 88)     # Cell east wall
    fill_tiles(chunk, TILE_WALL, 122, 80, 132, 82)     # Cell north wall
    fill_tiles(chunk, TILE_WALL, 126, 86, 128, 88)     # Cell bars
    # Court Sorcerer roof area (DS3: rooftop above palace, loot area)
    fill_tiles(chunk, TILE_WALL, 140, 78, 142, 84)     # Roof wall west
    fill_tiles(chunk, TILE_WALL, 155, 78, 157, 84)     # Roof wall east
    fill_tiles(chunk, TILE_WALL, 142, 78, 155, 80)     # Roof north wall
    fill_tiles(chunk, TILE_WALL, 145, 84, 148, 87)     # Roof obstacle
    # Fire-scorched masonry (DS3: profaned flame damage)
    fill_tiles(chunk, TILE_WALL, 135, 90, 137, 95)     # Scorched wall 1
    fill_tiles(chunk, TILE_WALL, 150, 92, 152, 97)     # Scorched wall 2
    fill_tiles(chunk, TILE_WALL, 160, 88, 162, 93)     # Scorched wall 3
    # Palace pillars (DS3: grand stone columns, partially melted)
    fill_tiles(chunk, TILE_WALL, 125, 95, 127, 100)    # Pillar SW
    fill_tiles(chunk, TILE_WALL, 140, 98, 142, 103)    # Pillar center
    fill_tiles(chunk, TILE_WALL, 158, 100, 160, 105)   # Pillar SE
    # Treasure room walls (DS3: side room with jailer handmaids)
    fill_tiles(chunk, TILE_WALL, 134, 105, 136, 112)   # Treasure wall 1
    fill_tiles(chunk, TILE_WALL, 148, 106, 150, 112)   # Treasure wall 2
    # Profaned flame scorch on floor (DS3: burned patches)
    fill_tiles(chunk, TILE_WALL, 120, 108, 122, 110)
    fill_tiles(chunk, TILE_WALL, 163, 107, 165, 110)

    # ================================================================
    # 5. FLOODED CELLS  (doc: x=860,y=2320,w=1060,h=720)
    #    tiles: (53,145)-(119,189)
    #    DS3: stagnant water, flooded prison cells, stone platforms,
    #    Monstrosities of Sin, Sewer Centipedes
    # ================================================================
    # Cell boundary walls (DS3: waterlogged prison structure)
    fill_tiles(chunk, TILE_WALL, 53, 145, 55, 187)     # West wall
    fill_tiles(chunk, TILE_WALL, 117, 145, 119, 187)   # East wall
    fill_tiles(chunk, TILE_WALL, 53, 145, 117, 147)    # North wall
    fill_tiles(chunk, TILE_WALL, 53, 187, 85, 189)     # South wall left
    fill_tiles(chunk, TILE_WALL, 95, 187, 119, 189)    # South wall right
    # Stagnant water pools (DS3: flooded cell floors)
    fill_tiles(chunk, TILE_POISON, 60, 155, 80, 165)   # NW pool
    fill_tiles(chunk, TILE_POISON, 90, 160, 110, 175)  # SE pool
    fill_tiles(chunk, TILE_POISON, 65, 172, 95, 183)   # South pool
    # Stone platforms above water (DS3: raised stone walkways)
    fill_tiles(chunk, TILE_GROUND, 58, 150, 68, 155)   # NW platform
    fill_tiles(chunk, TILE_GROUND, 100, 150, 115, 160)  # NE platform
    fill_tiles(chunk, TILE_GROUND, 70, 167, 88, 172)   # Center platform
    fill_tiles(chunk, TILE_GROUND, 95, 178, 112, 185)  # SE platform
    # Cell dividers (DS3: prison cell partition walls)
    fill_tiles(chunk, TILE_WALL, 72, 150, 74, 158)     # Divider 1
    fill_tiles(chunk, TILE_WALL, 85, 155, 87, 165)     # Divider 2
    fill_tiles(chunk, TILE_WALL, 100, 168, 102, 178)   # Divider 3
    # Rusty gate debris (DS3: corroded iron bars)
    fill_tiles(chunk, TILE_WALL, 58, 165, 60, 168)
    fill_tiles(chunk, TILE_WALL, 108, 180, 110, 183)

    # ================================================================
    # 6. YHORM BRIDGE  (doc: x=2300,y=2260,w=820,h=520)
    #    tiles: (143,141)-(194,173)
    #    DS3: stone bridge with Jailer rooms, fire vessels, Gargoyle perch
    # ================================================================
    # Bridge boundary walls (DS3: stone bridge walls with fire sconces)
    fill_tiles(chunk, TILE_WALL, 143, 141, 145, 171)   # West wall
    fill_tiles(chunk, TILE_WALL, 192, 141, 194, 171)   # East wall
    fill_tiles(chunk, TILE_WALL, 143, 141, 192, 143)   # North wall
    fill_tiles(chunk, TILE_WALL, 143, 171, 165, 173)   # South wall left
    fill_tiles(chunk, TILE_WALL, 175, 171, 194, 173)   # South wall right
    # First jailer room (DS3: room with 4+ jailers and branding irons)
    fill_tiles(chunk, TILE_WALL, 148, 146, 150, 155)   # Jailer room wall W
    fill_tiles(chunk, TILE_WALL, 162, 146, 164, 155)   # Jailer room wall E
    fill_tiles(chunk, TILE_WALL, 150, 146, 162, 148)   # Jailer room wall N
    # Jailer cell partitions (DS3: prison cells along bridge)
    fill_tiles(chunk, TILE_WALL, 152, 152, 154, 156)   # Cell bar 1
    fill_tiles(chunk, TILE_WALL, 158, 152, 160, 156)   # Cell bar 2
    # Second jailer room (DS3: mimics and real chest, jailer guards)
    fill_tiles(chunk, TILE_WALL, 170, 148, 172, 158)   # Jailer room 2 wall W
    fill_tiles(chunk, TILE_WALL, 185, 148, 187, 158)   # Jailer room 2 wall E
    fill_tiles(chunk, TILE_WALL, 172, 148, 185, 150)   # Jailer room 2 wall N
    # Pillar in second jailer room (DS3: stone column)
    fill_tiles(chunk, TILE_WALL, 177, 153, 179, 156)
    # Fire vessel pedestals (DS3: fire containers along bridge)
    fill_tiles(chunk, TILE_WALL, 148, 160, 150, 162)   # Fire vessel 1
    fill_tiles(chunk, TILE_WALL, 165, 162, 167, 164)   # Fire vessel 2
    fill_tiles(chunk, TILE_WALL, 180, 160, 182, 162)   # Fire vessel 3
    # Bridge support buttresses (DS3: stone supports under bridge)
    fill_tiles(chunk, TILE_WALL, 155, 165, 157, 168)
    fill_tiles(chunk, TILE_WALL, 172, 166, 174, 169)

    # ================================================================
    # 7. YHORM THRONE ROOM  (doc: x=2640,y=2920,w=900,h=700)
    #    tiles: (165,182)-(221,225)
    #    DS3: grand throne room, fire hall, boss arena, Storm Ruler pedestal
    # ================================================================
    # Throne room boundary walls (DS3: massive stone hall)
    fill_tiles(chunk, TILE_WALL, 165, 182, 167, 223)   # West wall
    fill_tiles(chunk, TILE_WALL, 219, 182, 221, 223)   # East wall
    fill_tiles(chunk, TILE_WALL, 165, 182, 218, 184)   # North wall
    fill_tiles(chunk, TILE_WALL, 165, 223, 221, 225)   # South wall
    # Throne pillars (DS3: massive columns flanking Yhorm's throne)
    fill_tiles(chunk, TILE_WALL, 172, 188, 174, 195)   # NW pillar
    fill_tiles(chunk, TILE_WALL, 190, 188, 192, 195)   # NE pillar
    fill_tiles(chunk, TILE_WALL, 172, 212, 174, 219)   # SW pillar
    fill_tiles(chunk, TILE_WALL, 190, 212, 192, 219)   # SE pillar
    # Central pillars (DS3: row of columns down the hall center)
    fill_tiles(chunk, TILE_WALL, 180, 198, 182, 202)   # Center pillar N
    fill_tiles(chunk, TILE_WALL, 205, 198, 207, 202)   # Center pillar S
    # Storm Ruler pedestal (DS3: sword embedded in stone at arena entrance)
    fill_tiles(chunk, TILE_WALL, 170, 200, 173, 204)   # Pedestal base
    # Yhorm's throne (DS3: giant stone throne at far end)
    fill_tiles(chunk, TILE_WALL, 200, 215, 215, 220)   # Throne
    fill_tiles(chunk, TILE_WALLTOP, 201, 214, 214, 215) # Throne top
    # Fire pool edges (DS3: profaned flame pools around arena)
    fill_tiles(chunk, TILE_WALL, 178, 190, 179, 192)   # Fire pool NW
    fill_tiles(chunk, TILE_WALL, 210, 208, 212, 210)   # Fire pool SE
    # Fallen column debris (DS3: destroyed columns from Yhorm's rage)
    fill_tiles(chunk, TILE_WALL, 195, 192, 197, 194)
    fill_tiles(chunk, TILE_WALL, 208, 195, 210, 197)
    # Boss arena open floor (DS3: wide open area for Yhorm fight)
    fill_tiles(chunk, TILE_GROUND, 175, 195, 215, 215)

    # ================================================================
    # CONNECTION CORRIDORS -- DS3 route paths between sections
    # ================================================================
    # Sewer Entrance -> Tower (southeast climb up from dungeon)
    carve_corridor(chunk, 12, 12, 55, 45, width=5)

    # Tower -> Collapsed Exterior (south descent into ruins)
    carve_corridor(chunk, 60, 70, 95, 85, width=5)

    # Tower -> Palace Ruins (east across rooftops)
    carve_corridor(chunk, 80, 55, 130, 80, width=5)

    # Collapsed Exterior -> Flooded Cells (south descent to prison)
    carve_corridor(chunk, 90, 120, 80, 150, width=5)

    # Collapsed Exterior -> Palace Ruins (east into palace)
    carve_corridor(chunk, 120, 95, 135, 95, width=5)

    # Palace Ruins -> Flooded Cells (south descent)
    carve_corridor(chunk, 140, 112, 100, 148, width=5)

    # Palace Ruins -> Yhorm Bridge (southeast)
    carve_corridor(chunk, 165, 100, 160, 145, width=5)

    # Flooded Cells -> Yhorm Bridge (east along prison level)
    carve_corridor(chunk, 115, 165, 150, 155, width=5)

    # Yhorm Bridge -> Yhorm Throne Room (south to boss)
    carve_corridor(chunk, 175, 170, 190, 185, width=5)

    # Flooded Cells -> Tower (northwest shortcut back)
    carve_corridor(chunk, 60, 148, 55, 72, width=5)

    # ================================================================
    # PLAYER SPAWN
    # ================================================================
    spawn_px, spawn_py = 900, 820  # Profaned Capital bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # ================================================================
    # FINALIZE -- load doc, apply terrain, return
    # ================================================================
    apply_doc_terrain(chunk, load_doc("ProfanedCapital"))

    return finalize_map("ProfanedCapital", chunk, entities, spawn_px, spawn_py)
