from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_corridor, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)


# Map size: 4096x4096 px = 256x256 tiles


def make_irithyll_dungeon():
    """Irithyll Dungeon -- DS3-faithful terrain.

    Dark underground prison beneath Irithyll. Tight cell corridors patrolled by
    Jailers with branding irons, Siegward locked in a cell, a Giant prisoner,
    flooded sewer tunnels with rats and basilisks, Karla imprisoned behind an
    illusory wall, and the dragon gesture path to Archdragon Peak. Ends at the
    stone bridge exit to Profaned Capital. No boss in this map.

    Layout follows JSON doc sections (pixel // 16 = tile):
      1. Dungeon Entrance Cells   (22,20)-(73,58)   - entry cells, jailers, damp corridors
      2. Upper Cell Blocks        (61,45)-(117,92)   - cell dividers, support pillars, iron bars
      3. Giant Cell              (101,95)-(148,146)  - large cell, chains, Siegward
      4. Lower Sewer             (73,153)-(130,191)  - sewer water, drainage, rats, basilisks
      5. Jailer Hall            (133,142)-(189,185)  - torture equipment, cages, Karla
      6. Dragon Side Room       (167,75)-(214,113)   - stone altar, dragon statue, meditation
      7. Bridge to Profaned Cap  (178,212)-(225,250)  - stone bridge, iron railings, exit
      8. Torture Chamber         (113,25)-(129,36)   - iron maidens, torture devices

    JSON doc is authoritative for all entity positions.
    """
    chunk = new_chunk(256, 256)

    # ================================================================
    # 1. DUNGEON ENTRANCE CELLS  (doc: x=360,y=320,w=820,h=620)
    #    tiles: (22,20)-(73,58)
    #    DS3: damp stone corridors with prison cells on both sides,
    #    jailers patrol carrying branding irons and lanterns.
    #    Entry from Irithyll through a dark staircase.
    # ================================================================
    # Outer walls -- stone dungeon walls
    fill_tiles(chunk, TILE_WALL, 22, 20, 24, 56)    # West wall
    fill_tiles(chunk, TILE_WALL, 71, 20, 73, 56)    # East wall
    fill_tiles(chunk, TILE_WALL, 22, 20, 72, 22)    # North wall
    fill_tiles(chunk, TILE_WALL, 22, 56, 72, 58)    # South wall
    # Central corridor -- main patrol route (DS3: long dark corridor)
    fill_tiles(chunk, TILE_GROUND, 26, 34, 68, 44)
    # Cell blocks -- north side cells (DS3: rows of iron-bar cells)
    fill_tiles(chunk, TILE_GROUND, 26, 24, 38, 32)    # Cell 1
    fill_tiles(chunk, TILE_GROUND, 42, 24, 54, 32)    # Cell 2
    fill_tiles(chunk, TILE_GROUND, 58, 24, 68, 32)    # Cell 3
    # Cell block walls -- iron bar dividers between cells
    fill_tiles(chunk, TILE_WALL, 38, 24, 40, 32)      # Bar divider 1-2
    fill_tiles(chunk, TILE_WALL, 54, 24, 56, 32)      # Bar divider 2-3
    # Cell blocks -- south side cells
    fill_tiles(chunk, TILE_GROUND, 26, 46, 38, 54)    # Cell 4
    fill_tiles(chunk, TILE_GROUND, 42, 46, 54, 54)    # Cell 5
    fill_tiles(chunk, TILE_GROUND, 58, 46, 68, 54)    # Cell 6
    # South cell bar dividers
    fill_tiles(chunk, TILE_WALL, 38, 46, 40, 54)      # Bar divider 4-5
    fill_tiles(chunk, TILE_WALL, 54, 46, 56, 54)      # Bar divider 5-6
    # Pillars flanking corridor (DS3: stone support pillars)
    fill_tiles(chunk, TILE_WALL, 32, 33, 34, 35)      # NW pillar
    fill_tiles(chunk, TILE_WALL, 48, 33, 50, 35)      # N-mid pillar
    fill_tiles(chunk, TILE_WALL, 62, 33, 64, 35)      # NE pillar
    fill_tiles(chunk, TILE_WALL, 32, 43, 34, 45)      # SW pillar
    fill_tiles(chunk, TILE_WALL, 48, 43, 50, 45)      # S-mid pillar
    fill_tiles(chunk, TILE_WALL, 62, 43, 64, 45)      # SE pillar
    # Dripping water debris (DS3: damp, water drips from ceiling)
    fill_tiles(chunk, TILE_WALL, 28, 28, 29, 29)
    fill_tiles(chunk, TILE_WALL, 44, 28, 45, 29)
    fill_tiles(chunk, TILE_WALL, 60, 28, 61, 29)

    # ================================================================
    # 2. UPPER CELL BLOCKS  (doc: x=980,y=720,w=900,h=760)
    #    tiles: (61,45)-(117,92)
    #    DS3: large room with many cell dividers, support pillars,
    #    iron bars. Jailers patrol carrying lanterns through dark halls.
    #    Multiple levels of cells with narrow passages between them.
    # ================================================================
    # Outer walls
    fill_tiles(chunk, TILE_WALL, 61, 45, 63, 90)    # West wall
    fill_tiles(chunk, TILE_WALL, 115, 45, 117, 90)  # East wall
    fill_tiles(chunk, TILE_WALL, 61, 45, 117, 47)   # North wall
    fill_tiles(chunk, TILE_WALL, 61, 90, 117, 92)   # South wall
    # Main hall floor
    fill_tiles(chunk, TILE_GROUND, 65, 49, 113, 88)
    # Cell divider walls -- rows of cells (DS3: prison cells with iron bars)
    # North row cells
    fill_tiles(chunk, TILE_WALL, 65, 55, 67, 70)    # Divider A
    fill_tiles(chunk, TILE_WALL, 77, 55, 79, 70)    # Divider B
    fill_tiles(chunk, TILE_WALL, 89, 55, 91, 70)    # Divider C
    fill_tiles(chunk, TILE_WALL, 101, 55, 103, 70)  # Divider D
    # South row cells
    fill_tiles(chunk, TILE_WALL, 65, 72, 67, 87)    # Divider E
    fill_tiles(chunk, TILE_WALL, 77, 72, 79, 87)    # Divider F
    fill_tiles(chunk, TILE_WALL, 89, 72, 91, 87)    # Divider G
    fill_tiles(chunk, TILE_WALL, 101, 72, 103, 87)  # Divider H
    # Support pillars in corridor (DS3: tall stone pillars in central hall)
    fill_tiles(chunk, TILE_WALL, 72, 64, 74, 66)    # Pillar NW
    fill_tiles(chunk, TILE_WALL, 85, 64, 87, 66)    # Pillar NE
    fill_tiles(chunk, TILE_WALL, 72, 78, 74, 80)    # Pillar SW
    fill_tiles(chunk, TILE_WALL, 85, 78, 87, 80)    # Pillar SE
    # Iron bar debris (DS3: broken iron bars on cell doors)
    fill_tiles(chunk, TILE_WALL, 70, 50, 71, 51)
    fill_tiles(chunk, TILE_WALL, 82, 50, 83, 51)
    fill_tiles(chunk, TILE_WALL, 94, 50, 95, 51)
    fill_tiles(chunk, TILE_WALL, 106, 50, 107, 51)

    # ================================================================
    # 3. GIANT CELL  (doc: x=1620,y=1520,w=760,h=820)
    #    tiles: (101,95)-(148,146)
    #    DS3: massive chamber where a Giant is held prisoner by chains.
    #    Siegward is found locked in a cell here. Stone platform,
    #    large iron door, chain anchors on walls.
    # ================================================================
    # Outer walls -- massive stone walls
    fill_tiles(chunk, TILE_WALL, 101, 95, 103, 144)   # West wall
    fill_tiles(chunk, TILE_WALL, 146, 95, 148, 144)   # East wall
    fill_tiles(chunk, TILE_WALL, 101, 95, 148, 97)    # North wall
    fill_tiles(chunk, TILE_WALL, 101, 144, 148, 146)  # South wall
    # Chamber floor
    fill_tiles(chunk, TILE_GROUND, 105, 99, 144, 142)
    # Stone platform in center (DS3: raised stone platform where giant stands)
    fill_tiles(chunk, TILE_WALL, 115, 110, 135, 118)  # Central platform
    # Chain anchors on walls (DS3: heavy chains bolted to walls)
    fill_tiles(chunk, TILE_WALL, 105, 102, 107, 104)  # NW chain
    fill_tiles(chunk, TILE_WALL, 142, 102, 144, 104)  # NE chain
    fill_tiles(chunk, TILE_WALL, 105, 138, 107, 140)  # SW chain
    fill_tiles(chunk, TILE_WALL, 142, 138, 144, 140)  # SE chain
    # Siegward's cell alcove (DS3: Siegward locked behind iron bars)
    fill_tiles(chunk, TILE_GROUND, 136, 120, 143, 130)  # Siegward cell floor
    fill_tiles(chunk, TILE_WALL, 134, 120, 136, 130)    # Cell bars (west)
    # Iron door frame (DS3: heavy iron door)
    fill_tiles(chunk, TILE_WALL, 109, 105, 111, 108)  # Door frame NW

    # ================================================================
    # 4. LOWER SEWER  (doc: x=1180,y=2460,w=920,h=620)
    #    tiles: (73,153)-(130,191)
    #    DS3: flooded sewer tunnels beneath the dungeon. Shallow water,
    #    drainage channels, rat nests. Wretches, Basilisks, and
    #    Sewer Centipedes lurk in the water. Dark and toxic.
    # ================================================================
    # Outer walls
    fill_tiles(chunk, TILE_WALL, 73, 153, 75, 189)   # West wall
    fill_tiles(chunk, TILE_WALL, 128, 153, 130, 189)  # East wall
    fill_tiles(chunk, TILE_WALL, 73, 153, 130, 155)   # North wall
    fill_tiles(chunk, TILE_WALL, 73, 189, 130, 191)   # South wall
    # Sewer water floor (poison tiles for the flooded area)
    fill_tiles(chunk, TILE_POISON, 77, 157, 126, 187)
    # Drainage channel walls (DS3: raised walkways above water)
    fill_tiles(chunk, TILE_WALL, 85, 160, 87, 175)    # Channel divider 1
    fill_tiles(chunk, TILE_WALL, 100, 158, 102, 178)  # Channel divider 2
    fill_tiles(chunk, TILE_WALL, 115, 162, 117, 180)  # Channel divider 3
    # Stone walkways along edges (DS3: narrow stone paths above water)
    fill_tiles(chunk, TILE_GROUND, 77, 157, 84, 162)   # NW walkway
    fill_tiles(chunk, TILE_GROUND, 120, 157, 126, 162)  # NE walkway
    fill_tiles(chunk, TILE_GROUND, 77, 183, 84, 187)   # SW walkway
    fill_tiles(chunk, TILE_GROUND, 120, 183, 126, 187)  # SE walkway
    # Grate debris (DS3: rusted grates over drains)
    fill_tiles(chunk, TILE_WALL, 90, 165, 91, 166)
    fill_tiles(chunk, TILE_WALL, 108, 170, 109, 171)

    # ================================================================
    # 5. JAILER HALL  (doc: x=2140,y=2280,w=900,h=700)
    #    tiles: (133,142)-(189,185)
    #    DS3: large hall with torture equipment, cages, and lantern hooks.
    #    Jailers patrol here. Karla is imprisoned behind an illusory wall
    #    in the deeper part of this area. Monstrosities of Sin guard items.
    # ================================================================
    # Outer walls
    fill_tiles(chunk, TILE_WALL, 133, 142, 135, 183)  # West wall
    fill_tiles(chunk, TILE_WALL, 187, 142, 189, 183)  # East wall
    fill_tiles(chunk, TILE_WALL, 133, 142, 189, 144)  # North wall
    fill_tiles(chunk, TILE_WALL, 133, 183, 189, 185)  # South wall
    # Hall floor
    fill_tiles(chunk, TILE_GROUND, 137, 146, 185, 181)
    # Torture equipment -- cages against walls (DS3: iron cages)
    fill_tiles(chunk, TILE_WALL, 138, 148, 142, 152)  # Cage NW
    fill_tiles(chunk, TILE_WALL, 138, 175, 142, 179)  # Cage SW
    fill_tiles(chunk, TILE_WALL, 180, 148, 184, 152)  # Cage NE
    fill_tiles(chunk, TILE_WALL, 180, 175, 184, 179)  # Cage SE
    # Iron maiden frames (DS3: iron maiden torture devices)
    fill_tiles(chunk, TILE_WALL, 150, 148, 152, 150)
    fill_tiles(chunk, TILE_WALL, 170, 148, 172, 150)
    # Central torture rack (DS3: wooden rack in center of room)
    fill_tiles(chunk, TILE_WALL, 155, 158, 175, 160)
    # Lantern hook pillars (DS3: jailers hang lanterns on wall hooks)
    fill_tiles(chunk, TILE_WALL, 145, 155, 147, 157)
    fill_tiles(chunk, TILE_WALL, 178, 155, 180, 157)
    fill_tiles(chunk, TILE_WALL, 145, 170, 147, 172)
    fill_tiles(chunk, TILE_WALL, 178, 170, 180, 172)
    # Karla's hidden cell alcove (DS3: illusory wall conceals Karla)
    fill_tiles(chunk, TILE_GROUND, 163, 174, 175, 180)  # Karla cell floor
    fill_tiles(chunk, TILE_WALL, 161, 174, 163, 180)    # Illusory wall (west side)

    # ================================================================
    # 6. PATH OF THE DRAGON SIDE ROOM  (doc: x=2680,y=1200,w=760,h=620)
    #    tiles: (167,75)-(214,113)
    #    DS3: hidden room with stone altar, dragon statue, and meditation
    #    mat. Requires "Path of the Dragon" gesture to reach Archdragon Peak.
    #    Reached via a narrow passage from the upper dungeon.
    # ================================================================
    # Outer walls
    fill_tiles(chunk, TILE_WALL, 167, 75, 169, 111)   # West wall
    fill_tiles(chunk, TILE_WALL, 212, 75, 214, 111)   # East wall
    fill_tiles(chunk, TILE_WALL, 167, 75, 214, 77)    # North wall
    fill_tiles(chunk, TILE_WALL, 167, 111, 214, 113)  # South wall
    # Room floor
    fill_tiles(chunk, TILE_GROUND, 171, 79, 210, 109)
    # Dragon statue pedestal (DS3: large dragon stone on pedestal)
    fill_tiles(chunk, TILE_WALL, 185, 85, 198, 92)    # Dragon statue base
    # Stone altar (DS3: stone altar in front of dragon statue)
    fill_tiles(chunk, TILE_WALL, 188, 95, 195, 99)    # Altar
    # Meditation mat area (DS3: woven mat where you perform the gesture)
    fill_tiles(chunk, TILE_WALL, 188, 102, 192, 104)  # Mat marker
    # Side alcove pillars (DS3: pillars flanking the altar)
    fill_tiles(chunk, TILE_WALL, 175, 88, 177, 95)    # Left pillar
    fill_tiles(chunk, TILE_WALL, 206, 88, 208, 95)    # Right pillar

    # ================================================================
    # 7. BRIDGE TO PROFANED CAPITAL  (doc: x=2860,y=3400,w=760,h=620)
    #    tiles: (178,212)-(225,250)
    #    DS3: stone bridge with iron railings leading out of the dungeon.
    #    Wind gusts across. Profaned Capital bonfire at the far end.
    #    Exit fog gate to Profaned Capital here.
    # ================================================================
    # Outer walls -- bridge railings (DS3: stone bridge with iron railings)
    fill_tiles(chunk, TILE_WALL, 178, 212, 180, 248)  # West railing
    fill_tiles(chunk, TILE_WALL, 223, 212, 225, 248)  # East railing
    fill_tiles(chunk, TILE_WALL, 178, 212, 225, 214)  # North wall
    fill_tiles(chunk, TILE_WALL, 178, 248, 225, 250)  # South wall
    # Bridge floor
    fill_tiles(chunk, TILE_GROUND, 182, 216, 221, 246)
    # Railing supports (DS3: iron railing posts along bridge)
    fill_tiles(chunk, TILE_WALL, 185, 218, 186, 219)
    fill_tiles(chunk, TILE_WALL, 195, 218, 196, 219)
    fill_tiles(chunk, TILE_WALL, 205, 218, 206, 219)
    fill_tiles(chunk, TILE_WALL, 215, 218, 216, 219)
    fill_tiles(chunk, TILE_WALL, 185, 243, 186, 244)
    fill_tiles(chunk, TILE_WALL, 195, 243, 196, 244)
    fill_tiles(chunk, TILE_WALL, 205, 243, 206, 244)
    fill_tiles(chunk, TILE_WALL, 215, 243, 216, 244)
    # Wind gust debris (DS3: broken stone from wind erosion)
    fill_tiles(chunk, TILE_WALL, 190, 230, 191, 231)
    fill_tiles(chunk, TILE_WALL, 210, 235, 211, 236)

    # ================================================================
    # 8. TORTURE CHAMBER  (doc: x=1808,y=400,w=272,h=192)
    #    tiles: (113,25)-(129,36)
    #    DS3: small room off the upper dungeon corridor with iron
    #    maidens, torture devices, and narrow cells. Optional side area.
    # ================================================================
    # Outer walls
    fill_tiles(chunk, TILE_WALL, 113, 25, 115, 34)   # West wall
    fill_tiles(chunk, TILE_WALL, 127, 25, 129, 34)   # East wall
    fill_tiles(chunk, TILE_WALL, 113, 25, 129, 27)   # North wall
    fill_tiles(chunk, TILE_WALL, 113, 34, 129, 36)   # South wall
    # Room floor
    fill_tiles(chunk, TILE_GROUND, 116, 28, 126, 33)
    # Iron maiden devices (DS3: standing iron maidens)
    fill_tiles(chunk, TILE_WALL, 117, 29, 119, 31)    # Iron maiden 1
    fill_tiles(chunk, TILE_WALL, 123, 29, 125, 31)    # Iron maiden 2
    # Torture rack (DS3: wooden rack)
    fill_tiles(chunk, TILE_WALL, 120, 32, 122, 33)    # Rack debris

    # ================================================================
    # CONNECTION CORRIDORS -- DS3 route paths between sections
    # ================================================================

    # Entry Cells -> Upper Cell Blocks (east)
    # DS3: descending stone corridor from entry to main cell block
    carve_corridor(chunk, 48, 38, 80, 68, width=5)
    fill_tiles(chunk, TILE_GROUND, 68, 55, 80, 68)    # Overlap ground

    # Upper Cell Blocks -> Giant Cell (southeast)
    # DS3: narrow passage descending to giant's chamber
    carve_corridor(chunk, 100, 88, 125, 120, width=5)
    fill_tiles(chunk, TILE_GROUND, 100, 90, 125, 120)  # Overlap ground

    # Upper Cell Blocks -> Torture Chamber (north-east)
    # DS3: side passage from upper cells to torture room
    carve_corridor(chunk, 90, 50, 120, 30, width=4)

    # Upper Cell Blocks -> Dragon Side Room (east)
    # DS3: hidden passage requiring exploration to dragon altar room
    carve_corridor(chunk, 112, 80, 170, 95, width=4)
    fill_tiles(chunk, TILE_GROUND, 112, 85, 170, 100)

    # Giant Cell -> Lower Sewer (south-west)
    # DS3: passage descending from giant's cell to flooded sewer
    carve_corridor(chunk, 110, 142, 100, 160, width=5)
    fill_tiles(chunk, TILE_GROUND, 100, 150, 115, 165)

    # Giant Cell -> Jailer Hall (south-east)
    # DS3: corridor from giant cell area to jailer torture hall
    carve_corridor(chunk, 145, 140, 160, 155, width=5)
    fill_tiles(chunk, TILE_GROUND, 145, 145, 165, 160)

    # Lower Sewer -> Jailer Hall (east)
    # DS3: flooded passage connecting sewer to jailer area
    carve_corridor(chunk, 125, 170, 145, 165, width=5)
    fill_tiles(chunk, TILE_GROUND, 125, 162, 150, 175)

    # Jailer Hall -> Bridge to Profaned Capital (south-east)
    # DS3: ascending stone path to the bridge exit
    carve_corridor(chunk, 165, 180, 200, 220, width=5)
    fill_tiles(chunk, TILE_GROUND, 170, 190, 210, 225)

    # Lower Sewer -> Bridge to Profaned Capital (south-east shortcut)
    # DS3: alternative path from sewer area toward exit
    carve_corridor(chunk, 120, 185, 185, 220, width=4)

    # ================================================================
    # PLAYER SPAWN & BONFIRE
    # ================================================================
    spawn_px, spawn_py = 600, 600   # Irithyll Dungeon bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # ================================================================
    # APPLY DOC TERRAIN -- fills sections, connects corridors, clears
    # bonfire/fog positions from JSON. Must come before finalize.
    # ================================================================
    apply_doc_terrain(chunk, load_doc("IrithyllDungeon"))

    return finalize_map("IrithyllDungeon", chunk, entities, spawn_px, spawn_py)
