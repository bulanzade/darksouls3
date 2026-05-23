from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_corridor, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)


# Map size: 4608x4096 px = 288x256 tiles


def make_catacombs_of_carthus():
    """Catacombs of Carthus -- DS3-faithful terrain.

    Underground catacombs with narrow bone-lined corridors, skeleton enemies,
    rolling skeleton ball traps, rope bridge over abyss, and High Lord Wolnir
    boss chamber.  JSON doc is authoritative for entity positions.

    Route: Entry Stairs -> First Skeleton Ball -> Upper Catacombs ->
           Second Skeleton Ball -> Rope Bridge -> Wolnir Tomb (boss).
    Side: Underground Passage, Lower Catacombs, Tsorig Corridor,
          Bridge Ladder Descent (to Smouldering Lake), Carthus Pyromancy Tomb.
    """
    chunk = new_chunk(288, 256)

    # ================================================================
    # 1. ENTRY STAIRS  (doc: x=360,y=420,w=900,h=660)
    #    tiles: (22,26)-(78,67)
    #    DS3: stone stairs descending into the catacombs, torch-lit,
    #    skeletons line the walls, Horace found here
    # ================================================================
    # Boundary walls -- stone catacomb walls
    fill_tiles(chunk, TILE_WALL, 22, 26, 24, 55)    # West wall
    fill_tiles(chunk, TILE_WALL, 76, 26, 78, 55)    # East wall
    fill_tiles(chunk, TILE_WALL, 22, 26, 50, 28)    # North wall left
    fill_tiles(chunk, TILE_WALL, 60, 26, 78, 28)    # North wall right
    fill_tiles(chunk, TILE_WALL, 22, 65, 78, 67)    # South wall
    # Stone pillars flanking the entrance (DS3: entrance archway)
    fill_tiles(chunk, TILE_WALL, 30, 30, 32, 40)    # Left pillar
    fill_tiles(chunk, TILE_WALL, 68, 30, 70, 40)    # Right pillar
    # Sarcophagi along walls (DS3: stone coffins line entry hall)
    fill_tiles(chunk, TILE_WALL, 26, 35, 28, 37)
    fill_tiles(chunk, TILE_WALL, 26, 45, 28, 47)
    fill_tiles(chunk, TILE_WALL, 72, 35, 74, 37)
    fill_tiles(chunk, TILE_WALL, 72, 45, 74, 47)
    # Stair step platforms (DS3: descending steps)
    fill_tiles(chunk, TILE_WALL, 35, 40, 65, 41)
    fill_tiles(chunk, TILE_WALL, 38, 50, 62, 51)
    # Torch alcoves (DS3: torch sconces on walls)
    fill_tiles(chunk, TILE_WALL, 25, 55, 26, 56)
    fill_tiles(chunk, TILE_WALL, 74, 55, 75, 56)

    # ================================================================
    # 2. FIRST SKELETON BALL CORRIDOR  (doc: x=1080,y=760,w=820,h=520)
    #    tiles: (67,47)-(118,79)
    #    DS3: long narrow corridor where a giant skeleton ball rolls
    #    down. Side alcoves for dodging. Skeleton ambushes.
    # ================================================================
    # Corridor walls (DS3: narrow corridor with high stone walls)
    fill_tiles(chunk, TILE_WALL, 67, 47, 69, 70)    # West wall
    fill_tiles(chunk, TILE_WALL, 116, 47, 118, 70)  # East wall
    fill_tiles(chunk, TILE_WALL, 67, 47, 118, 49)   # North wall
    fill_tiles(chunk, TILE_WALL, 67, 77, 118, 79)   # South wall
    # Skeleton ball track -- central groove (DS3: worn track in floor)
    fill_tiles(chunk, TILE_WALLTOP, 72, 57, 113, 58)
    fill_tiles(chunk, TILE_WALLTOP, 72, 67, 113, 68)
    # Side dodge alcoves (DS3: recesses in wall to hide from ball)
    fill_tiles(chunk, TILE_WALL, 75, 50, 76, 55)    # Alcove NW pillar
    fill_tiles(chunk, TILE_WALL, 85, 50, 86, 55)    # Alcove pillar
    fill_tiles(chunk, TILE_WALL, 95, 50, 96, 55)    # Alcove pillar
    fill_tiles(chunk, TILE_WALL, 105, 50, 106, 55)  # Alcove pillar
    fill_tiles(chunk, TILE_WALL, 75, 71, 76, 76)    # Alcove SW pillar
    fill_tiles(chunk, TILE_WALL, 85, 71, 86, 76)    # Alcove pillar
    fill_tiles(chunk, TILE_WALL, 95, 71, 96, 76)    # Alcove pillar
    fill_tiles(chunk, TILE_WALL, 105, 71, 106, 76)  # Alcove pillar
    # Bone pile debris (DS3: bones scattered in corridor)
    fill_tiles(chunk, TILE_WALL, 78, 60, 79, 61)
    fill_tiles(chunk, TILE_WALL, 100, 64, 101, 65)

    # ================================================================
    # 3. UPPER CATACOMBS  (doc: x=1580,y=1180,w=980,h=780)
    #    tiles: (98,73)-(159,121)
    #    DS3: wider chamber with bone piles, reanimating skeletons,
    #    Carthus Worm mini-boss area, multiple interconnected rooms
    # ================================================================
    # Chamber boundary walls (DS3: catacomb room dividers)
    fill_tiles(chunk, TILE_WALL, 98, 73, 100, 110)   # West wall
    fill_tiles(chunk, TILE_WALL, 157, 73, 159, 110)  # East wall
    fill_tiles(chunk, TILE_WALL, 98, 73, 130, 75)    # North wall left
    fill_tiles(chunk, TILE_WALL, 140, 73, 159, 75)   # North wall right
    fill_tiles(chunk, TILE_WALL, 98, 119, 159, 121)  # South wall
    # Room divider walls (DS3: broken walls between sub-chambers)
    fill_tiles(chunk, TILE_WALL, 120, 80, 122, 95)   # Divider 1
    fill_tiles(chunk, TILE_WALL, 140, 90, 142, 110)  # Divider 2
    # Bone pile mounds (DS3: massive piles of bones, skeletons reanimate)
    fill_tiles(chunk, TILE_WALL, 105, 80, 107, 83)
    fill_tiles(chunk, TILE_WALL, 110, 95, 112, 98)
    fill_tiles(chunk, TILE_WALL, 130, 85, 132, 88)
    fill_tiles(chunk, TILE_WALL, 148, 100, 150, 103)
    fill_tiles(chunk, TILE_WALL, 125, 110, 127, 113)
    # Sarcophagus row (DS3: sealed tombs along walls)
    fill_tiles(chunk, TILE_WALL, 103, 105, 105, 108)
    fill_tiles(chunk, TILE_WALL, 103, 112, 105, 115)
    fill_tiles(chunk, TILE_WALL, 150, 82, 152, 85)
    fill_tiles(chunk, TILE_WALL, 150, 90, 152, 93)

    # ================================================================
    # 4. SECOND SKELETON BALL  (doc: x=2320,y=1860,w=760,h=620)
    #    tiles: (145,116)-(192,154)
    #    DS3: second rolling ball area, rat tunnels, ledge drops
    # ================================================================
    # Corridor walls (DS3: descending narrow passage)
    fill_tiles(chunk, TILE_WALL, 145, 116, 147, 145)   # West wall
    fill_tiles(chunk, TILE_WALL, 190, 116, 192, 145)   # East wall
    fill_tiles(chunk, TILE_WALL, 145, 116, 192, 118)   # North wall
    fill_tiles(chunk, TILE_WALL, 145, 152, 192, 154)   # South wall
    # Skeleton ball track (DS3: worn groove)
    fill_tiles(chunk, TILE_WALLTOP, 152, 130, 185, 131)
    fill_tiles(chunk, TILE_WALLTOP, 152, 140, 185, 141)
    # Ledge platforms (DS3: elevated side platforms)
    fill_tiles(chunk, TILE_WALL, 150, 120, 151, 128)   # Ledge wall NW
    fill_tiles(chunk, TILE_WALL, 186, 120, 187, 128)   # Ledge wall NE
    # Rat tunnel openings (DS3: dark side tunnels with rats)
    fill_tiles(chunk, TILE_WALL, 165, 145, 167, 150)   # Rat nest barrier
    fill_tiles(chunk, TILE_WALL, 175, 145, 177, 150)   # Rat nest barrier
    # Bone debris
    fill_tiles(chunk, TILE_WALL, 155, 125, 156, 126)
    fill_tiles(chunk, TILE_WALL, 180, 135, 181, 136)

    # ================================================================
    # 5. ROPE BRIDGE  (doc: x=2860,y=2360,w=860,h=560)
    #    tiles: (178,147)-(232,182)
    #    DS3: narrow rope bridge over a deep abyss, collapsible.
    #    Skeleton archers on far side. Can be cut for shortcut.
    # ================================================================
    # Bridge anchor walls (DS3: stone platforms at each end)
    fill_tiles(chunk, TILE_WALL, 178, 147, 180, 170)   # West anchor wall
    fill_tiles(chunk, TILE_WALL, 230, 147, 232, 170)   # East anchor wall
    fill_tiles(chunk, TILE_WALL, 178, 147, 200, 149)   # North wall left
    fill_tiles(chunk, TILE_WALL, 215, 147, 232, 149)   # North wall right
    fill_tiles(chunk, TILE_WALL, 178, 180, 232, 182)   # South wall
    # Bridge walkway -- narrow plank area (DS3: rope bridge slats)
    fill_tiles(chunk, TILE_WALLTOP, 195, 160, 215, 161)
    fill_tiles(chunk, TILE_WALLTOP, 195, 168, 215, 169)
    # Bridge side drops (DS3: abyss on both sides of bridge)
    fill_tiles(chunk, TILE_WALL, 185, 153, 186, 157)
    fill_tiles(chunk, TILE_WALL, 224, 153, 225, 157)
    fill_tiles(chunk, TILE_WALL, 185, 172, 186, 176)
    fill_tiles(chunk, TILE_WALL, 224, 172, 225, 176)
    # Archer positions (DS3: skeleton archers on far end)
    fill_tiles(chunk, TILE_WALL, 220, 155, 221, 156)
    fill_tiles(chunk, TILE_WALL, 220, 170, 221, 171)

    # ================================================================
    # 6. BRIDGE LADDER DESCENT  (doc: x=1540,y=2760,w=720,h=680)
    #    tiles: (96,172)-(141,214)
    #    DS3: ladder down from broken bridge, rats below,
    #    path toward Smouldering Lake
    # ================================================================
    # Chamber walls (DS3: small lower chamber)
    fill_tiles(chunk, TILE_WALL, 96, 172, 98, 200)     # West wall
    fill_tiles(chunk, TILE_WALL, 139, 172, 141, 200)   # East wall
    fill_tiles(chunk, TILE_WALL, 96, 172, 141, 174)    # North wall
    fill_tiles(chunk, TILE_WALL, 96, 212, 141, 214)    # South wall
    # Ladder shaft walls (DS3: ladder descent)
    fill_tiles(chunk, TILE_WALL, 113, 178, 114, 195)   # Ladder left
    fill_tiles(chunk, TILE_WALL, 123, 178, 124, 195)   # Ladder right
    # Rat nest debris (DS3: dark area with rats)
    fill_tiles(chunk, TILE_WALL, 102, 200, 103, 203)
    fill_tiles(chunk, TILE_WALL, 130, 198, 131, 201)
    fill_tiles(chunk, TILE_WALL, 108, 205, 109, 207)
    fill_tiles(chunk, TILE_WALL, 125, 205, 126, 207)

    # ================================================================
    # 7. WOLNIR TOMB -- BOSS ARENA  (doc: x=3240,y=2820,w=880,h=640)
    #    tiles: (202,176)-(257,215)
    #    DS3: vast dark chamber where High Lord Wolnir emerges from
    #    the abyss. Sandy floor, golden bracelets glow, skull mountain.
    # ================================================================
    # Arena perimeter walls (DS3: dark walls at edge of abyss)
    fill_tiles(chunk, TILE_WALL, 202, 176, 205, 200)   # NW wall
    fill_tiles(chunk, TILE_WALL, 253, 176, 257, 200)   # NE wall
    fill_tiles(chunk, TILE_WALL, 202, 212, 205, 215)   # SW wall
    fill_tiles(chunk, TILE_WALL, 253, 212, 257, 215)   # SE wall
    fill_tiles(chunk, TILE_WALL, 202, 176, 230, 178)   # North wall left
    fill_tiles(chunk, TILE_WALL, 240, 176, 257, 178)   # North wall right
    fill_tiles(chunk, TILE_WALL, 202, 213, 257, 215)   # South wall
    # Abyss edge markers (DS3: dark void edge around arena)
    fill_tiles(chunk, TILE_WALL, 210, 183, 212, 184)
    fill_tiles(chunk, TILE_WALL, 245, 183, 247, 184)
    fill_tiles(chunk, TILE_WALL, 210, 207, 212, 208)
    fill_tiles(chunk, TILE_WALL, 245, 207, 247, 208)
    # Ancient pillars in arena (DS3: crumbling stone columns)
    fill_tiles(chunk, TILE_WALL, 220, 190, 222, 193)   # Pillar NW
    fill_tiles(chunk, TILE_WALL, 240, 190, 242, 193)   # Pillar NE
    fill_tiles(chunk, TILE_WALL, 220, 200, 222, 203)   # Pillar SW
    fill_tiles(chunk, TILE_WALL, 240, 200, 242, 203)   # Pillar SE
    # Skull mound (DS3: Wolnir emerges from pile of skulls)
    fill_tiles(chunk, TILE_WALL, 226, 195, 235, 198)
    # Golden bracelet markers (DS3: Wolnir's bracelets are weak points)
    fill_tiles(chunk, TILE_WALL, 215, 188, 216, 189)
    fill_tiles(chunk, TILE_WALL, 248, 188, 249, 189)
    fill_tiles(chunk, TILE_WALL, 215, 205, 216, 206)
    fill_tiles(chunk, TILE_WALL, 248, 205, 249, 206)

    # ================================================================
    # 8. UNDERGROUND PASSAGE  (doc: x=208,y=1168,w=432,h=480)
    #    tiles: (13,73)-(40,102)
    #    DS3: narrow tunnel off the main path, skeleton ambush, bone piles
    # ================================================================
    # Tunnel walls (DS3: tight underground passage)
    fill_tiles(chunk, TILE_WALL, 13, 73, 15, 95)      # West wall
    fill_tiles(chunk, TILE_WALL, 38, 73, 40, 95)      # East wall
    fill_tiles(chunk, TILE_WALL, 13, 73, 40, 75)      # North wall
    fill_tiles(chunk, TILE_WALL, 13, 100, 40, 102)    # South wall
    # Tunnel obstacles (DS3: bone piles blocking path)
    fill_tiles(chunk, TILE_WALL, 20, 80, 21, 82)
    fill_tiles(chunk, TILE_WALL, 30, 88, 31, 90)
    fill_tiles(chunk, TILE_WALL, 24, 95, 25, 97)
    # Skeleton ambush alcoves (DS3: hidden enemies in wall recesses)
    fill_tiles(chunk, TILE_WALL, 16, 78, 17, 79)
    fill_tiles(chunk, TILE_WALL, 35, 85, 36, 86)

    # ================================================================
    # 9. LOWER CATACOMBS  (doc: x=700,y=2400,w=800,h=600)
    #    tiles: (43,150)-(93,187)
    #    DS3: ceiling slimes, skeleton wheels, dark corridors,
    #    shortcut lever connecting back to earlier areas
    # ================================================================
    # Chamber walls (DS3: underground tomb rooms)
    fill_tiles(chunk, TILE_WALL, 43, 150, 45, 178)    # West wall
    fill_tiles(chunk, TILE_WALL, 91, 150, 93, 178)    # East wall
    fill_tiles(chunk, TILE_WALL, 43, 150, 93, 152)    # North wall
    fill_tiles(chunk, TILE_WALL, 43, 185, 93, 187)    # South wall
    # Room dividers (DS3: walls between sub-chambers)
    fill_tiles(chunk, TILE_WALL, 60, 155, 62, 170)    # Divider 1
    fill_tiles(chunk, TILE_WALL, 78, 160, 80, 180)    # Divider 2
    # Slime drip pillars (DS3: ceiling slimes hang from above)
    fill_tiles(chunk, TILE_WALL, 50, 158, 51, 160)
    fill_tiles(chunk, TILE_WALL, 70, 165, 71, 167)
    fill_tiles(chunk, TILE_WALL, 85, 170, 86, 172)
    # Skeleton wheel obstacles (DS3: skeletal remains in corridors)
    fill_tiles(chunk, TILE_WALL, 48, 175, 49, 177)
    fill_tiles(chunk, TILE_WALL, 65, 180, 66, 182)
    fill_tiles(chunk, TILE_WALL, 82, 175, 83, 177)

    # ================================================================
    # 10. TSORIG CORRIDOR  (doc: x=1600,y=2000,w=700,h=500)
    #     tiles: (100,125)-(143,156)
    #     DS3: narrow bridge with lava floor below, Tsorig invades here
    # ================================================================
    # Corridor walls (DS3: narrow elevated bridge)
    fill_tiles(chunk, TILE_WALL, 100, 125, 102, 148)  # West wall
    fill_tiles(chunk, TILE_WALL, 141, 125, 143, 148)  # East wall
    fill_tiles(chunk, TILE_WALL, 100, 125, 143, 127)  # North wall
    fill_tiles(chunk, TILE_WALL, 100, 154, 143, 156)  # South wall
    # Bridge supports (DS3: stone pillars under the bridge)
    fill_tiles(chunk, TILE_WALL, 110, 135, 111, 137)
    fill_tiles(chunk, TILE_WALL, 130, 140, 131, 142)
    # Lava floor visible below (DS3: lava under the bridge)
    fill_tiles(chunk, TILE_POISON, 105, 148, 138, 152)
    # Tsorig invasion point cover (DS3: alcoves where Tsorig lurks)
    fill_tiles(chunk, TILE_WALL, 118, 130, 119, 133)
    fill_tiles(chunk, TILE_WALL, 125, 130, 126, 133)

    # ================================================================
    # 11. CARTHUS PYROMANCY TOMB  (doc: x=200,y=1800,w=600,h=400)
    #     tiles: (12,112)-(37,137)
    #     DS3: illusory wall entrance, drop-down platforms, bone trap floor
    # ================================================================
    # Chamber walls (DS3: hidden tomb behind illusory wall)
    fill_tiles(chunk, TILE_WALL, 12, 112, 14, 130)    # West wall
    fill_tiles(chunk, TILE_WALL, 35, 112, 37, 130)    # East wall
    fill_tiles(chunk, TILE_WALL, 12, 112, 37, 114)    # North wall
    fill_tiles(chunk, TILE_WALL, 12, 135, 37, 137)    # South wall
    # Drop-down platforms (DS3: platforms you drop between)
    fill_tiles(chunk, TILE_WALL, 18, 118, 20, 120)    # Platform 1
    fill_tiles(chunk, TILE_WALL, 28, 118, 30, 120)    # Platform 2
    fill_tiles(chunk, TILE_WALL, 22, 126, 26, 128)    # Platform 3 (lower)
    # Bone trap floor debris (DS3: breakable bone floor)
    fill_tiles(chunk, TILE_WALL, 16, 130, 17, 132)
    fill_tiles(chunk, TILE_WALL, 32, 130, 33, 132)
    # Illusory wall alcove (DS3: hidden entrance)
    fill_tiles(chunk, TILE_WALL, 14, 115, 15, 117)

    # ================================================================
    # CONNECTION CORRIDORS -- DS3 route paths between sections
    # ================================================================
    # Entry Stairs -> First Skeleton Ball (east-southeast)
    fill_tiles(chunk, TILE_GROUND, 70, 55, 80, 60)
    carve_corridor(chunk, 50, 45, 90, 60, width=5)

    # First Skeleton Ball -> Upper Catacombs (east-southeast)
    fill_tiles(chunk, TILE_GROUND, 110, 70, 120, 75)
    carve_corridor(chunk, 110, 65, 120, 95, width=5)

    # Upper Catacombs -> Second Skeleton Ball (southeast)
    fill_tiles(chunk, TILE_GROUND, 150, 110, 160, 120)
    carve_corridor(chunk, 130, 110, 165, 130, width=5)

    # Second Skeleton Ball -> Rope Bridge (southeast)
    fill_tiles(chunk, TILE_GROUND, 185, 145, 195, 155)
    carve_corridor(chunk, 170, 140, 195, 160, width=5)

    # Rope Bridge -> Wolnir Tomb (east)
    fill_tiles(chunk, TILE_GROUND, 225, 165, 235, 180)
    carve_corridor(chunk, 210, 165, 230, 195, width=5)

    # Upper Catacombs -> Tsorig Corridor (south)
    carve_corridor(chunk, 130, 115, 120, 135, width=5)

    # Tsorig Corridor -> Second Skeleton Ball (east-north)
    carve_corridor(chunk, 140, 135, 160, 130, width=5)

    # Upper Catacombs -> Underground Passage (west)
    carve_corridor(chunk, 100, 95, 30, 88, width=5)

    # Entry Stairs -> Underground Passage (south-west)
    carve_corridor(chunk, 40, 60, 25, 80, width=5)

    # Entry Stairs -> Lower Catacombs (south)
    carve_corridor(chunk, 50, 65, 65, 155, width=5)

    # Lower Catacombs -> Bridge Ladder Descent (east)
    carve_corridor(chunk, 90, 170, 105, 190, width=5)

    # Bridge Ladder Descent -> Smouldering Lake exit (south)
    carve_corridor(chunk, 115, 205, 100, 210, width=5)

    # Lower Catacombs -> Carthus Pyromancy Tomb (north-west)
    carve_corridor(chunk, 50, 155, 25, 125, width=5)

    # Wolnir Tomb -> Irithyll exit (east)
    fill_tiles(chunk, TILE_GROUND, 250, 195, 265, 200)

    # ================================================================
    # PLAYER SPAWN & FINALIZE
    # ================================================================
    spawn_px, spawn_py = 520, 620  # Catacombs of Carthus bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("CatacombsOfCarthus"))

    return finalize_map("CatacombsOfCarthus", chunk, entities, spawn_px, spawn_py)
