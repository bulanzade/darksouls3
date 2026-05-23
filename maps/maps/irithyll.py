from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_irithyll():
    """Irithyll of the Boreal Valley - frozen moonlit city with Pontiff Sulyvahn boss.
    Faithful DS3 layout: ice bridge -> Central Irithyll boulevard -> Church of Yorshka ->
    Graveyard/Dark Room -> Sewer Route -> Distant Manor -> Silver Knight Upper Street ->
    Pontiff Cathedral -> Post-Pontiff Courtyard -> Anor Londo exit.
    Design doc: 4096x4608, gothic city with icy blue moonlight.
    """
    chunk = new_chunk(258, 288)


    # ================================================================
    # SECTION 1: Central Irithyll Bridge (doc: x=360,y=460,w=1180,h=420)
    # DS3: Narrow stone bridge over a frozen valley. Sulyvahn's Beast
    # ambushes here. Ice crystal pillars line the railings.
    # ================================================================
    # Bridge deck — long narrow corridor
    fill_tiles(chunk, TILE_GROUND, 22, 28, 96, 56)
    # Bridge narrows at midpoint (DS3: the bridge has railings)
    fill_tiles(chunk, TILE_WALL, 22, 28, 22, 32)
    fill_tiles(chunk, TILE_WALL, 22, 52, 22, 56)
    fill_tiles(chunk, TILE_WALL, 96, 28, 96, 32)
    fill_tiles(chunk, TILE_WALL, 96, 52, 96, 56)
    # Railing pillars along bridge (DS3: stone railing posts)
    for bx in range(30, 92, 8):
        fill_tiles(chunk, TILE_WALL, bx, 28, bx + 1, 30)
        fill_tiles(chunk, TILE_WALL, bx, 54, bx + 1, 56)
    # Widen at center for beast ambush area
    fill_tiles(chunk, TILE_GROUND, 50, 25, 70, 58)

    # ================================================================
    # SECTION 2: Central Irithyll (doc: x=1240,y=780,w=1080,h=720)
    # DS3: Wide boulevard with lampposts, market stalls, buildings.
    # Pontiff Knights, Fire Witches, Irithyllian Slaves patrol.
    # Central fountain in the square.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 78, 48, 146, 96)
    # Building facades — left side of boulevard (DS3: gothic buildings)
    fill_tiles(chunk, TILE_WALL, 80, 50, 88, 58)
    fill_tiles(chunk, TILE_WALL, 80, 65, 86, 72)
    fill_tiles(chunk, TILE_WALL, 80, 80, 88, 88)
    # Building facades — right side of boulevard
    fill_tiles(chunk, TILE_WALL, 132, 50, 140, 60)
    fill_tiles(chunk, TILE_WALL, 135, 68, 142, 76)
    fill_tiles(chunk, TILE_WALL, 130, 82, 138, 90)
    # Central fountain (DS3: frozen fountain in town square)
    fill_tiles(chunk, TILE_WALL, 106, 68, 112, 74)
    # Street lamp bases (DS3: magical blue lampposts)
    for lx in [95, 108, 122, 136]:
        fill_tiles(chunk, TILE_WALL, lx, 62, lx + 1, 64)
        fill_tiles(chunk, TILE_WALL, lx, 78, lx + 1, 80)
    # Market stalls along the street
    fill_tiles(chunk, TILE_WALL, 96, 56, 98, 59)
    fill_tiles(chunk, TILE_WALL, 118, 56, 120, 59)
    fill_tiles(chunk, TILE_WALL, 126, 86, 128, 89)

    # ================================================================
    # SECTION 3: Church of Yorshka (doc: x=1780,y=1500,w=700,h=520)
    # DS3: Small stone church with bonfire, altar, pews, and stained
    # glass windows. Bonfire inside. Sirris can appear here.
    # ================================================================
    # Church building — walled rectangle with interior
    fill_tiles(chunk, TILE_GROUND, 111, 94, 156, 126)
    # Church outer walls (DS3: stone church exterior)
    fill_tiles(chunk, TILE_WALL, 111, 94, 156, 96)     # north wall
    fill_tiles(chunk, TILE_WALL, 111, 124, 156, 126)   # south wall
    fill_tiles(chunk, TILE_WALL, 111, 94, 113, 126)    # west wall
    fill_tiles(chunk, TILE_WALL, 154, 94, 156, 126)    # east wall
    # Church door openings (ground through walls)
    fill_tiles(chunk, TILE_GROUND, 130, 94, 136, 96)   # north entrance
    fill_tiles(chunk, TILE_GROUND, 111, 108, 113, 112)  # west entrance
    fill_tiles(chunk, TILE_GROUND, 154, 108, 156, 112)  # east exit
    # Interior pews (DS3: two rows of wooden pews)
    fill_tiles(chunk, TILE_WALL, 118, 100, 120, 104)
    fill_tiles(chunk, TILE_WALL, 124, 100, 126, 104)
    fill_tiles(chunk, TILE_WALL, 138, 100, 140, 104)
    fill_tiles(chunk, TILE_WALL, 144, 100, 146, 104)
    # Altar at far end (DS3: stone altar with bonfire)
    fill_tiles(chunk, TILE_WALL, 130, 118, 136, 120)
    # Altar side columns
    fill_tiles(chunk, TILE_WALL, 128, 110, 129, 116)
    fill_tiles(chunk, TILE_WALL, 137, 110, 138, 116)

    # ================================================================
    # SECTION 4: Graveyard and Dark Room (doc: x=1500,y=2060,w=900,h=640)
    # DS3: Frost-covered graveyard with headstones, dark alcoves where
    # invisible Irithyllian Slaves ambush. Stone staircase descends.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 94, 128, 150, 170)
    # Graveyard headstones (DS3: rows of frost-covered graves)
    for gx, gy in [(100, 134), (108, 134), (116, 134), (124, 134),
                    (100, 142), (108, 142), (116, 142), (124, 142),
                    (100, 150), (108, 150), (116, 150), (124, 150)]:
        fill_tiles(chunk, TILE_WALL, gx, gy, gx + 1, gy + 2)
    # Dark room entrance walls (DS3: enclosed dark room with hags)
    fill_tiles(chunk, TILE_WALL, 136, 130, 148, 132)
    fill_tiles(chunk, TILE_WALL, 136, 148, 148, 150)
    fill_tiles(chunk, TILE_WALL, 136, 130, 138, 150)
    # Dark room interior
    fill_tiles(chunk, TILE_GROUND, 138, 132, 148, 148)
    # Stone staircase along south edge (DS3: stairs leading down)
    fill_tiles(chunk, TILE_WALL, 94, 165, 150, 168)
    fill_tiles(chunk, TILE_GROUND, 94, 168, 150, 170)

    # ================================================================
    # SECTION 5: Sewer Route (doc: x=2340,y=2380,w=940,h=560)
    # DS3: Underground waterway with Sewer Centipedes, support pillars,
    # drainage channels. Greirat's ashes found here.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 146, 148, 206, 186)
    # Sewer tunnel walls (DS3: stone tunnel walls)
    fill_tiles(chunk, TILE_WALL, 146, 148, 148, 186)   # west wall
    fill_tiles(chunk, TILE_WALL, 204, 148, 206, 186)   # east wall
    fill_tiles(chunk, TILE_WALL, 146, 148, 206, 150)   # north wall
    fill_tiles(chunk, TILE_WALL, 146, 184, 206, 186)   # south wall
    # Sewer entrance openings
    fill_tiles(chunk, TILE_GROUND, 146, 156, 148, 162)  # west entrance
    fill_tiles(chunk, TILE_GROUND, 204, 160, 206, 170)  # east exit
    fill_tiles(chunk, TILE_GROUND, 170, 148, 180, 150)  # north entrance
    # Support pillars (DS3: stone pillars holding up the ceiling)
    for px, py in [(158, 158), (175, 158), (192, 158),
                    (158, 175), (175, 175), (192, 175)]:
        fill_tiles(chunk, TILE_WALL, px, py, px + 2, py + 2)
    # Drainage channel divider (DS3: water channels)
    fill_tiles(chunk, TILE_WALL, 155, 166, 198, 168)

    # ================================================================
    # SECTION 6: Distant Manor (doc: x=2960,y=2360,w=760,h=520)
    # DS3: Kitchen where Siegward cooks estus soup. Fireplace,
    # kitchen furniture, dining area. Siegward NPC here.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 185, 148, 232, 180)
    # Manor outer walls (DS3: stone manor building)
    fill_tiles(chunk, TILE_WALL, 185, 148, 232, 150)   # north wall
    fill_tiles(chunk, TILE_WALL, 185, 178, 232, 180)   # south wall
    fill_tiles(chunk, TILE_WALL, 185, 148, 187, 180)   # west wall
    fill_tiles(chunk, TILE_WALL, 230, 148, 232, 180)   # east wall
    # Manor entrance (west door)
    fill_tiles(chunk, TILE_GROUND, 185, 160, 187, 166)
    # Interior: kitchen counter (DS3: Siegward's cooking area)
    fill_tiles(chunk, TILE_WALL, 192, 155, 198, 160)
    # Fireplace (DS3: stone fireplace where Siegward cooks)
    fill_tiles(chunk, TILE_WALL, 220, 155, 226, 162)
    # Dining table and furniture
    fill_tiles(chunk, TILE_WALL, 200, 168, 210, 172)
    fill_tiles(chunk, TILE_WALL, 216, 168, 222, 172)

    # ================================================================
    # SECTION 7: Silver Knight Upper Street (doc: x=2880,y=1460,w=980,h=620)
    # DS3: Rooftop walkways and stone battlements where Silver Knights
    # patrol with greatbows. Archer positions overlook the city.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 180, 92, 242, 130)
    # Battlement walls (DS3: stone battlements with archer positions)
    fill_tiles(chunk, TILE_WALL, 182, 92, 240, 94)     # north battlement
    fill_tiles(chunk, TILE_WALL, 182, 128, 240, 130)   # south battlement
    fill_tiles(chunk, TILE_WALL, 182, 92, 184, 130)    # west wall
    # Rooftop platforms (DS3: multiple roof levels)
    fill_tiles(chunk, TILE_WALL, 195, 98, 210, 105)
    fill_tiles(chunk, TILE_WALL, 220, 98, 235, 105)
    fill_tiles(chunk, TILE_WALL, 195, 115, 210, 122)
    fill_tiles(chunk, TILE_WALL, 220, 115, 235, 122)
    # Archer positions (DS3: elevated positions for Silver Knight archers)
    fill_tiles(chunk, TILE_WALL, 242, 96, 245, 100)
    fill_tiles(chunk, TILE_WALL, 242, 108, 245, 112)
    fill_tiles(chunk, TILE_WALL, 242, 120, 245, 124)

    # ================================================================
    # SECTION 8: Pontiff Cathedral (doc: x=3600,y=1680,w=860,h=620)
    # DS3: Massive stone cathedral where Pontiff Sulyvahn is fought.
    # Grand cathedral pillars, boss arena floor.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 225, 105, 280, 146)
    # Cathedral walls (DS3: grand stone cathedral)
    fill_tiles(chunk, TILE_WALL, 225, 105, 280, 107)   # north wall
    fill_tiles(chunk, TILE_WALL, 225, 144, 280, 146)   # south wall
    fill_tiles(chunk, TILE_WALL, 225, 105, 227, 146)   # west wall
    fill_tiles(chunk, TILE_WALL, 278, 105, 280, 146)   # east wall
    # Cathedral entrance (west door, from Silver Knight area)
    fill_tiles(chunk, TILE_GROUND, 225, 120, 227, 128)
    # Grand cathedral pillars (DS3: four massive stone columns)
    for px, py in [(238, 114), (260, 114), (238, 136), (260, 136)]:
        fill_tiles(chunk, TILE_WALL, px, py, px + 3, py + 3)
    # Altar area at east end (DS3: desecrated altar)
    fill_tiles(chunk, TILE_WALL, 270, 110, 275, 118)
    fill_tiles(chunk, TILE_WALL, 270, 134, 275, 142)

    # ================================================================
    # SECTION 9: Post-Pontiff Courtyard (doc: x=3900,y=820,w=860,h=700)
    # DS3: Open courtyard after defeating Pontiff. Giant Slave patrols.
    # Revolving staircase mechanism leads to Anor Londo.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 244, 50, 256, 92)
    # Courtyard walls (DS3: walled open courtyard)
    fill_tiles(chunk, TILE_WALL, 244, 50, 256, 52)     # north wall
    fill_tiles(chunk, TILE_WALL, 244, 90, 256, 92)     # south wall
    fill_tiles(chunk, TILE_WALL, 244, 50, 246, 92)     # west wall
    fill_tiles(chunk, TILE_WALL, 254, 50, 256, 92)     # east wall
    # Courtyard entrance (south, from cathedral)
    fill_tiles(chunk, TILE_GROUND, 248, 90, 252, 92)
    # Giant platform (DS3: elevated platform where giant stands)
    fill_tiles(chunk, TILE_WALL, 248, 56, 252, 62)
    # Revolving staircase base (DS3: mechanism leading to Anor Londo)
    fill_tiles(chunk, TILE_WALL, 248, 74, 252, 80)

    # ================================================================
    # SECTION 10: Water Reserve (doc: x=3600,y=2400,w=700,h=520)
    # DS3: Flooded chamber beneath the city. Sewer Centipedes and
    # Sulyvahn's Beasts lurk in the water. Illusory wall entrance.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 225, 150, 268, 182)
    # Water reserve walls
    fill_tiles(chunk, TILE_WALL, 225, 150, 268, 152)   # north wall
    fill_tiles(chunk, TILE_WALL, 225, 180, 268, 182)   # south wall
    fill_tiles(chunk, TILE_WALL, 225, 150, 227, 182)   # west wall
    fill_tiles(chunk, TILE_WALL, 266, 150, 268, 182)   # east wall
    # Entrance from sewers (north)
    fill_tiles(chunk, TILE_GROUND, 244, 150, 250, 152)
    # Sludge pools (DS3: water pools where beasts lurk)
    fill_tiles(chunk, TILE_WALL, 235, 160, 240, 168)
    fill_tiles(chunk, TILE_WALL, 255, 160, 260, 168)

    # ================================================================
    # SECTION 11: Darkmoon Tomb (doc: x=400,y=2100,w=600,h=460)
    # DS3: Dark stone room with statue and illusory wall concealing
    # the Darkmoon covenant. Rotating platform mechanism.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 25, 130, 64, 160)
    # Tomb walls (DS3: dark enclosed room)
    fill_tiles(chunk, TILE_WALL, 25, 130, 64, 132)     # north wall
    fill_tiles(chunk, TILE_WALL, 25, 158, 64, 160)     # south wall
    fill_tiles(chunk, TILE_WALL, 25, 130, 27, 160)     # west wall
    fill_tiles(chunk, TILE_WALL, 62, 130, 64, 160)     # east wall
    # Entrance from graveyard (north)
    fill_tiles(chunk, TILE_GROUND, 38, 130, 50, 132)
    # Statue with illusory wall (DS3: Gwyndolin statue)
    fill_tiles(chunk, TILE_WALL, 38, 145, 42, 152)
    # Rotating platform mechanism (DS3: elevator platform)
    fill_tiles(chunk, TILE_WALL, 52, 148, 56, 155)

    # ================================================================
    # CONNECTION CORRIDORS — linking all sections
    # DS3: Irithyll is a linear but interconnected city
    # ================================================================
    # Bridge -> Central Irithyll boulevard
    fill_tiles(chunk, TILE_GROUND, 60, 52, 82, 58)
    # Central Irithyll -> Church of Yorshka
    fill_tiles(chunk, TILE_GROUND, 120, 90, 128, 98)
    # Central Irithyll -> Graveyard/Dark Room
    fill_tiles(chunk, TILE_GROUND, 110, 96, 118, 132)
    # Church of Yorshka -> Graveyard
    fill_tiles(chunk, TILE_GROUND, 120, 120, 128, 130)
    # Graveyard -> Sewer Route (stone staircase down)
    fill_tiles(chunk, TILE_GROUND, 140, 168, 156, 172)
    # Graveyard -> Darkmoon Tomb
    fill_tiles(chunk, TILE_GROUND, 64, 145, 94, 148)
    # Church of Yorshka -> Silver Knight Upper Street
    fill_tiles(chunk, TILE_GROUND, 152, 105, 182, 115)
    # Central Irithyll -> Silver Knight area
    fill_tiles(chunk, TILE_GROUND, 140, 88, 185, 96)
    # Silver Knight Upper Street -> Pontiff Cathedral
    fill_tiles(chunk, TILE_GROUND, 238, 120, 242, 124)
    # Pontiff Cathedral -> Post-Pontiff Courtyard
    fill_tiles(chunk, TILE_GROUND, 248, 105, 252, 120)
    # Sewer Route -> Distant Manor
    fill_tiles(chunk, TILE_GROUND, 204, 162, 210, 164)
    fill_tiles(chunk, TILE_GROUND, 210, 158, 220, 168)
    fill_tiles(chunk, TILE_GROUND, 220, 158, 232, 162)
    fill_tiles(chunk, TILE_GROUND, 232, 158, 240, 166)
    fill_tiles(chunk, TILE_GROUND, 240, 166, 248, 174)
    fill_tiles(chunk, TILE_GROUND, 248, 174, 256, 178)
    # Sewer Route -> Water Reserve
    fill_tiles(chunk, TILE_GROUND, 200, 180, 210, 185)
    fill_tiles(chunk, TILE_GROUND, 210, 182, 225, 186)
    fill_tiles(chunk, TILE_GROUND, 225, 182, 235, 178)
    # Post-Pontiff Courtyard -> Anor Londo exit (east edge)
    fill_tiles(chunk, TILE_GROUND, 252, 55, 256, 70)

    # ================================================================
    # WALLTOP decoration — icicles, frost ridges, roof edges
    # DS3: Irithyll is perpetually frozen; icicles hang from eaves
    # ================================================================
    # Bridge icicle ridge
    for tx in range(24, 94, 3):
        fill_tiles(chunk, TILE_WALLTOP, tx, 27, tx + 1, 28)
    # Boulevard rooftop edges
    for tx in range(80, 145, 2):
        fill_tiles(chunk, TILE_WALLTOP, tx, 48, tx + 1, 49)
        fill_tiles(chunk, TILE_WALLTOP, tx, 96, tx + 1, 97)
    # Church roof
    for tx in range(112, 155, 2):
        fill_tiles(chunk, TILE_WALLTOP, tx, 93, tx + 1, 94)
    # Cathedral roof
    for tx in range(226, 278, 2):
        fill_tiles(chunk, TILE_WALLTOP, tx, 104, tx + 1, 105)

    # ================================================================
    # TERRAIN FROM JSON DOC — fills remaining section interiors
    # and connects all areas with corridors
    # ================================================================
    apply_doc_terrain(chunk, load_doc("Irithyll"))

    # Spawn at first bonfire (Irithyll of the Boreal Valley, x=400, y=800)
    spawn_px, spawn_py = 400, 800
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
                                [make_field("heal", "Bool", True)]))

    return finalize_map("Irithyll", chunk, entities, spawn_px, spawn_py)
