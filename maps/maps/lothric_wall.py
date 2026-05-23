from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_ellipse, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)



def make_lothric_wall():
    """High Wall of Lothric — DS3-faithful terrain.

    Real DS3 structures from the High Wall area:
    1. High Wall Entry — stone ramparts, winding stairs from Cemetery of Ash
    2. Tower on the Wall — spiral staircase tower, Winged Knight room
    3. Wyvern Fire Bridge — scorched stone bridge with dragon corpse
    4. Lower Knight Plaza — open courtyard with Lothric Knights, fountain
    5. Greirat Cell Route — dark prison corridors, locked iron gate
    6. Winged Knight Courtyard — rooftop plaza with high battlements
    7. Emma Chapel — cathedral interior with stained glass, Basin of Vows
    8. Vordt Stairs — stone descent into cold mist, frost-covered
    9. Post-Dancer Lift — elevator shaft up to Lothric Castle
    10. Vordt Arena — open boss platform at base of wall

    JSON doc (docs/maps/LothricWall.json) is authoritative for entity data.
    apply_doc_terrain() fills section interiors and carves corridors.
    """
    chunk = new_chunk(256, 256)

    # ================================================================
    # 1. HIGH WALL ENTRY — NW area, arrive from Cemetery of Ash
    # DS3: stone ramparts, battlement walkway, winding stairs, rubble
    # Section: x=260,y=180 → tiles (16,11)-(63,43)
    # ================================================================
    # Perimeter castle walls (DS3: high stone ramparts)
    fill_tiles(chunk, TILE_WALL, 16, 11, 18, 43)      # West wall
    fill_tiles(chunk, TILE_WALL, 59, 11, 63, 43)      # East wall
    fill_tiles(chunk, TILE_WALL, 16, 11, 63, 13)      # North wall
    fill_tiles(chunk, TILE_WALL, 16, 41, 63, 43)      # South wall
    # Battlement crenellations (DS3: merlons along the wall top)
    for tx in range(20, 60, 4):
        fill_tiles(chunk, TILE_WALLTOP, tx, 10, tx + 1, 10)
    # Interior: winding entry stairs (DS3: curved stone staircase)
    fill_tiles(chunk, TILE_GROUND, 20, 15, 60, 39)
    # Stone stairway (DS3: steps leading down from rampart)
    fill_tiles(chunk, TILE_WALL, 28, 16, 30, 18)      # Stair wall A
    fill_tiles(chunk, TILE_WALL, 38, 20, 40, 22)      # Stair wall B
    fill_tiles(chunk, TILE_WALL, 48, 24, 50, 26)      # Stair wall C
    # Rubble piles (DS3: loose stone debris from crumbling wall)
    fill_tiles(chunk, TILE_WALL, 24, 30, 25, 31)
    fill_tiles(chunk, TILE_WALL, 34, 34, 35, 35)
    fill_tiles(chunk, TILE_WALL, 44, 28, 45, 29)
    # Hollow soldier alcove (DS3: hollows hide behind pillars)
    fill_tiles(chunk, TILE_WALL, 52, 32, 54, 34)

    # ================================================================
    # 2. TOWER ON THE WALL — central stone tower
    # DS3: spiral staircase, stone archway, narrow windows
    # Section: x=1180,y=650 → tiles (73,40)-(112,75)
    # ================================================================
    # Tower exterior walls (DS3: circular stone tower, approximated)
    fill_tiles(chunk, TILE_WALL, 73, 40, 76, 75)      # West wall
    fill_tiles(chunk, TILE_WALL, 109, 40, 112, 75)    # East wall
    fill_tiles(chunk, TILE_WALL, 73, 40, 112, 43)     # North wall
    fill_tiles(chunk, TILE_WALL, 73, 72, 112, 75)     # South wall
    # Tower interior (DS3: hollow interior with spiral staircase)
    fill_tiles(chunk, TILE_GROUND, 78, 45, 107, 70)
    # Spiral staircase center column (DS3: central stone pillar)
    fill_tiles(chunk, TILE_WALL, 90, 52, 96, 58)
    # Stone archway (DS3: arched entrance to tower)
    fill_tiles(chunk, TILE_WALL, 82, 65, 84, 70)
    fill_tiles(chunk, TILE_WALL, 100, 65, 102, 70)
    # Narrow window alcoves (DS3: arrow slits in tower walls)
    fill_tiles(chunk, TILE_WALL, 80, 46, 81, 48)
    fill_tiles(chunk, TILE_WALL, 104, 46, 105, 48)
    # Upper landing (DS3: platform at top of spiral stairs)
    fill_tiles(chunk, TILE_GROUND, 85, 44, 100, 46)

    # ================================================================
    # 3. WYVERN FIRE BRIDGE — scorched stone bridge
    # DS3: dragon corpse, charred corpses, fire breath zone
    # Section: x=1680,y=520 → tiles (105,32)-(164,64)
    # ================================================================
    # Bridge perimeter (DS3: long stone bridge with railings)
    fill_tiles(chunk, TILE_WALL, 105, 32, 107, 64)    # West abutment
    fill_tiles(chunk, TILE_WALL, 161, 32, 164, 64)    # East abutment
    # Bridge interior (DS3: wide walkable stone bridge)
    fill_tiles(chunk, TILE_GROUND, 108, 34, 159, 62)
    # Stone bridge railings (DS3: low stone walls on both sides)
    fill_tiles(chunk, TILE_WALLTOP, 108, 33, 159, 33)  # North railing
    fill_tiles(chunk, TILE_WALLTOP, 108, 63, 159, 63)  # South railing
    # Dragon corpse obstruction (DS3: massive wyvern body on bridge)
    fill_tiles(chunk, TILE_WALL, 120, 38, 124, 44)    # Wyvern body segment 1
    fill_tiles(chunk, TILE_WALL, 134, 48, 138, 54)    # Wyvern body segment 2
    fill_tiles(chunk, TILE_WALL, 148, 40, 152, 46)    # Wyvern body segment 3
    # Charred corpses / scorch marks (DS3: burned bodies along bridge)
    fill_tiles(chunk, TILE_WALL, 112, 40, 113, 41)
    fill_tiles(chunk, TILE_WALL, 128, 50, 129, 51)
    fill_tiles(chunk, TILE_WALL, 142, 42, 143, 43)
    fill_tiles(chunk, TILE_WALL, 155, 56, 156, 57)
    # Fire breath cover pillars (DS3: stone pillars to hide behind)
    fill_tiles(chunk, TILE_WALL, 116, 36, 117, 38)
    fill_tiles(chunk, TILE_WALL, 144, 52, 145, 54)

    # ================================================================
    # 4. LOWER KNIGHT PLAZA — open courtyard
    # DS3: stone fountain, knight statues, barricades
    # Section: x=920,y=1320 → tiles (57,82)-(118,124)
    # ================================================================
    # Courtyard perimeter (DS3: walled courtyard)
    fill_tiles(chunk, TILE_WALL, 57, 82, 60, 124)     # West wall
    fill_tiles(chunk, TILE_WALL, 115, 82, 118, 124)   # East wall
    fill_tiles(chunk, TILE_WALL, 57, 82, 118, 85)     # North wall
    fill_tiles(chunk, TILE_WALL, 57, 121, 118, 124)   # South wall
    # Courtyard interior (DS3: open stone-paved area)
    fill_tiles(chunk, TILE_GROUND, 62, 87, 113, 119)
    # Stone fountain at center (DS3: ornate stone fountain)
    fill_tiles(chunk, TILE_WALL, 82, 98, 92, 106)
    carve_ellipse(chunk, 87, 102, 3, 3)               # Fountain basin
    # Knight statue plinths (DS3: statues of Lothric knights)
    fill_tiles(chunk, TILE_WALL, 66, 90, 68, 93)
    fill_tiles(chunk, TILE_WALL, 108, 90, 110, 93)
    # Barricades (DS3: wooden barricades blocking paths)
    fill_tiles(chunk, TILE_WALL, 70, 115, 74, 117)
    fill_tiles(chunk, TILE_WALL, 100, 115, 104, 117)
    # Sewer grate passage (DS3: lower passage out of courtyard)
    fill_tiles(chunk, TILE_GROUND, 108, 112, 113, 118)

    # ================================================================
    # 5. GREIRAT CELL ROUTE — dark prison corridors
    # DS3: locked iron gate, dark cell corridor, narrow passages
    # Section: x=1740,y=1320 → tiles (108,82)-(156,129)
    # ================================================================
    # Cell block perimeter (DS3: underground prison area)
    fill_tiles(chunk, TILE_WALL, 108, 82, 112, 129)   # West wall
    fill_tiles(chunk, TILE_WALL, 152, 82, 156, 129)   # East wall
    fill_tiles(chunk, TILE_WALL, 108, 82, 156, 85)    # North wall
    fill_tiles(chunk, TILE_WALL, 108, 126, 156, 129)  # South wall
    # Prison corridor (DS3: long dark corridor)
    fill_tiles(chunk, TILE_GROUND, 114, 87, 150, 122)
    # Locked iron gate (DS3: gate requiring Cell Key)
    fill_tiles(chunk, TILE_WALL, 130, 90, 132, 100)
    fill_tiles(chunk, TILE_WALL, 130, 108, 132, 118)
    # Cell partitions (DS3: individual cells along corridor)
    fill_tiles(chunk, TILE_WALL, 118, 95, 120, 100)
    fill_tiles(chunk, TILE_WALL, 118, 108, 120, 113)
    fill_tiles(chunk, TILE_WALL, 140, 95, 142, 100)
    fill_tiles(chunk, TILE_WALL, 140, 108, 142, 113)
    # Darkwraith alcove (DS3: Darkwraith behind locked door)
    fill_tiles(chunk, TILE_GROUND, 144, 96, 150, 112)

    # ================================================================
    # 6. WINGED KNIGHT COURTYARD — rooftop plaza
    # DS3: rooftop plaza, high battlements, patrolling knight
    # Section: x=2260,y=2080 → tiles (141,130)-(188,168)
    # ================================================================
    # Rooftop perimeter (DS3: high stone walls on rooftop)
    fill_tiles(chunk, TILE_WALL, 141, 130, 144, 168)  # West wall
    fill_tiles(chunk, TILE_WALL, 184, 130, 188, 168)  # East wall
    fill_tiles(chunk, TILE_WALL, 141, 130, 188, 133)  # North wall
    fill_tiles(chunk, TILE_WALL, 141, 165, 188, 168)  # South wall
    # Rooftop interior (DS3: paved stone rooftop)
    fill_tiles(chunk, TILE_GROUND, 146, 135, 182, 162)
    # High battlement merlons (DS3: crenellated parapets)
    for tx in range(146, 182, 5):
        fill_tiles(chunk, TILE_WALLTOP, tx, 134, tx + 2, 134)
    # Stone pavement obstacles (DS3: raised stone platforms)
    fill_tiles(chunk, TILE_WALL, 155, 142, 158, 145)
    fill_tiles(chunk, TILE_WALL, 168, 150, 171, 153)
    # Drop-down ledge (DS3: path down from rooftop)
    fill_tiles(chunk, TILE_GROUND, 145, 158, 150, 162)

    # ================================================================
    # 7. EMMA CHAPEL — cathedral interior
    # DS3: chapel interior, stained glass, cathedral pews, candle altar
    # Section: x=2440,y=2500 → tiles (152,156)-(195,188)
    # ================================================================
    # Chapel perimeter (DS3: gothic stone walls)
    fill_tiles(chunk, TILE_WALL, 152, 156, 156, 188)  # West wall
    fill_tiles(chunk, TILE_WALL, 191, 156, 195, 188)  # East wall
    fill_tiles(chunk, TILE_WALL, 152, 156, 195, 159)  # North wall
    fill_tiles(chunk, TILE_WALL, 152, 185, 195, 188)  # South wall
    # Chapel interior (DS3: nave with stone floor)
    fill_tiles(chunk, TILE_GROUND, 158, 161, 189, 183)
    # Cathedral columns (DS3: gothic stone pillars)
    fill_tiles(chunk, TILE_WALL, 164, 165, 166, 169)
    fill_tiles(chunk, TILE_WALL, 164, 176, 166, 180)
    fill_tiles(chunk, TILE_WALL, 179, 165, 181, 169)
    fill_tiles(chunk, TILE_WALL, 179, 176, 181, 180)
    # Altar (DS3: stone altar with Basin of Vows)
    fill_tiles(chunk, TILE_WALL, 170, 162, 175, 164)
    # Cathedral pews (DS3: wooden bench rows)
    fill_tiles(chunk, TILE_WALL, 163, 170, 165, 175)
    fill_tiles(chunk, TILE_WALL, 180, 170, 182, 175)
    # Candle alcove (DS3: candle-lit side chapel)
    fill_tiles(chunk, TILE_WALL, 158, 170, 160, 173)

    # ================================================================
    # 8. VORDT STAIRS — cold descent
    # DS3: stone stairs descending into frost, cold mist, ashen stone
    # Section: x=2820,y=3120 → tiles (176,195)-(220,233)
    # ================================================================
    # Stair walls (DS3: stone walls flanking the descent)
    fill_tiles(chunk, TILE_WALL, 176, 195, 179, 233)  # West wall
    fill_tiles(chunk, TILE_WALL, 217, 195, 220, 233)  # East wall
    fill_tiles(chunk, TILE_WALL, 176, 195, 220, 198)  # Top wall
    # Stair interior (DS3: wide stone steps)
    fill_tiles(chunk, TILE_GROUND, 181, 199, 215, 230)
    # Stone landing platforms (DS3: wider landings at intervals)
    fill_tiles(chunk, TILE_GROUND, 178, 208, 218, 212)
    fill_tiles(chunk, TILE_GROUND, 178, 220, 218, 224)
    # Frost-covered stones (DS3: icy patches on stairs)
    fill_tiles(chunk, TILE_WALL, 190, 200, 191, 201)
    fill_tiles(chunk, TILE_WALL, 200, 206, 201, 207)
    fill_tiles(chunk, TILE_WALL, 185, 214, 186, 215)
    fill_tiles(chunk, TILE_WALL, 210, 218, 211, 219)
    fill_tiles(chunk, TILE_WALL, 195, 226, 196, 227)

    # ================================================================
    # 9. POST-DANCER LIFT — elevator to Lothric Castle
    # DS3: elevator shaft, stone landing, locked door
    # Section: x=2920,y=2140 → tiles (182,133)-(214,158)
    # ================================================================
    # Lift shaft walls (DS3: narrow elevator shaft)
    fill_tiles(chunk, TILE_WALL, 182, 133, 185, 158)  # West shaft wall
    fill_tiles(chunk, TILE_WALL, 211, 133, 214, 158)  # East shaft wall
    fill_tiles(chunk, TILE_WALL, 182, 133, 214, 136)  # Top wall
    fill_tiles(chunk, TILE_WALL, 182, 155, 214, 158)  # Bottom wall
    # Lift interior (DS3: stone elevator platform)
    fill_tiles(chunk, TILE_GROUND, 187, 138, 209, 152)
    # Lift mechanism (DS3: central pillar)
    fill_tiles(chunk, TILE_WALL, 196, 142, 200, 148)
    # Stone landing at top (DS3: small room at lift top)
    fill_tiles(chunk, TILE_GROUND, 186, 134, 210, 136)

    # ================================================================
    # 10. VORDT ARENA — open boss platform
    # DS3: wide open arena at base of wall, icy ground
    # Boss: x=3160,y=3540 → tiles (197,221)
    # ================================================================
    # Arena perimeter (DS3: open area with distant walls)
    fill_tiles(chunk, TILE_WALL, 175, 230, 178, 250)  # West
    fill_tiles(chunk, TILE_WALL, 218, 230, 220, 250)  # East
    fill_tiles(chunk, TILE_WALL, 175, 247, 220, 250)  # South wall
    # Arena interior (DS3: wide open boss platform)
    fill_tiles(chunk, TILE_GROUND, 180, 231, 216, 245)
    # Wider arena oval (DS3: circular-ish arena)
    carve_ellipse(chunk, 198, 238, 16, 10)
    # Arena entry gate arch (DS3: stone arch from stairs)
    fill_tiles(chunk, TILE_WALL, 190, 228, 194, 230)
    fill_tiles(chunk, TILE_WALL, 202, 228, 206, 230)
    # Perimeter ice pillars (DS3: frozen stone columns)
    fill_tiles(chunk, TILE_WALL, 183, 233, 184, 235)
    fill_tiles(chunk, TILE_WALL, 212, 233, 213, 235)
    fill_tiles(chunk, TILE_WALL, 183, 242, 184, 244)
    fill_tiles(chunk, TILE_WALL, 212, 242, 213, 244)
    # Ashen stone debris (DS3: crumbled masonry)
    fill_tiles(chunk, TILE_WALL, 192, 236, 193, 237)
    fill_tiles(chunk, TILE_WALL, 204, 240, 205, 241)

    # ================================================================
    # CONNECTION CORRIDORS — DS3 route paths between areas
    # ================================================================
    # Entry → Tower on the Wall (east descent)
    fill_tiles(chunk, TILE_GROUND, 55, 35, 78, 50)
    # Entry → Wyvern Bridge (east from entry)
    fill_tiles(chunk, TILE_GROUND, 60, 32, 110, 42)
    # Tower → Wyvern Bridge (north connection)
    fill_tiles(chunk, TILE_GROUND, 100, 42, 115, 50)
    # Wyvern Bridge → Lower Knight Plaza (south descent)
    fill_tiles(chunk, TILE_GROUND, 100, 60, 120, 85)
    # Tower → Greirat Cell Route (east from tower)
    fill_tiles(chunk, TILE_GROUND, 108, 55, 130, 85)
    # Tower → Lower Knight Plaza (south from tower)
    fill_tiles(chunk, TILE_GROUND, 80, 70, 95, 85)
    # Lower Knight Plaza → Greirat Cell Route (east)
    fill_tiles(chunk, TILE_GROUND, 112, 95, 140, 105)
    # Greirat Cell → Winged Knight Courtyard (south)
    fill_tiles(chunk, TILE_GROUND, 130, 122, 150, 135)
    # Lower Knight Plaza → Winged Knight Courtyard (east)
    fill_tiles(chunk, TILE_GROUND, 110, 115, 148, 135)
    # Winged Knight Courtyard → Emma Chapel (south)
    fill_tiles(chunk, TILE_GROUND, 150, 160, 160, 170)
    # Emma Chapel → Vordt Stairs (south descent)
    fill_tiles(chunk, TILE_GROUND, 160, 180, 185, 200)
    # Emma Chapel → Post-Dancer Lift (north-east)
    fill_tiles(chunk, TILE_GROUND, 185, 158, 195, 165)
    # Vordt Stairs → Vordt Arena (south into arena)
    fill_tiles(chunk, TILE_GROUND, 185, 228, 210, 235)
    # Post-Dancer Lift → Winged Knight Courtyard (west)
    fill_tiles(chunk, TILE_GROUND, 170, 140, 185, 150)

    # ================================================================
    # FINALIZE — spawn point, load doc, apply terrain, return
    # ================================================================
    spawn_px, spawn_py = 560, 360  # High Wall of Lothric bonfire
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("LothricWall"))
    return finalize_map("LothricWall", chunk, entities, spawn_px, spawn_py)
