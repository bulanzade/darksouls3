from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_consumed_kings_garden():
    """Consumed King's Garden - DS3-faithful terrain.

    Small garden area accessed via ladder from Lothric Castle. Descends through
    stone stairway to a toxic swamp garden, then continues down through an upper
    interior platform and lower garden path to Oceiros's throne room arena.
    A hidden illusory wall leads to Untended Graves.

    Layout follows JSON doc sections (pixel // 16 = tile):
      1. Lower Dancer Lift        (26,26)-(73,58)   - entry lift, Cathedral Knight guards
      2. Garden Stone Stairway    (31,56)-(62,81)   - moss-covered descent
      3. Poison Garden            (56,73)-(131,124) - toxic swamp, Pus of Man, Rotten Slugs
      4. Upper Interior Platform  (117,61)-(168,101)- stone platform, Cathedral Knights
      5. Lower Garden Path        (112,112)-(162,143)- crumbling masonry, dead hedges
      6. Oceiros Approach         (150,131)-(187,156)- dark corridor to boss
      7. Oceiros Arena            (172,148)-(223,188)- boss room, Oceiros
      8. Untended Graves Wall     (203,135)-(235,161)- illusory wall exit
      9. Hidden Garden            (180,137)-(190,147)- small secret area

    JSON doc is authoritative for all entity positions.
    """
    chunk = new_chunk(256, 256)

    # ================================================================
    # 1. LOWER DANCER LIFT — entry from Lothric Castle
    # DS3: lift platform from Lothric Castle descends into the garden.
    #      Stone-walled lift shaft with iron gate, lantern sconces.
    #      Cathedral Knight and Lothric Priest guard the lift area.
    # Tiles: (26,26)-(73,58)
    # ================================================================
    # Lift shaft walls (DS3: enclosed stone elevator shaft)
    fill_tiles(chunk, TILE_WALL, 26, 26, 28, 58)     # West wall
    fill_tiles(chunk, TILE_WALL, 71, 26, 73, 58)     # East wall
    fill_tiles(chunk, TILE_WALL, 26, 26, 73, 28)     # North wall
    fill_tiles(chunk, TILE_WALL, 26, 56, 73, 58)     # South wall
    # Lift platform (DS3: central lift platform)
    fill_tiles(chunk, TILE_GROUND, 42, 32, 57, 44)
    # Entry corridor walls (DS3: short corridor from lift to garden)
    fill_tiles(chunk, TILE_WALL, 34, 36, 36, 50)     # Corridor west pillar
    fill_tiles(chunk, TILE_WALL, 63, 36, 65, 50)     # Corridor east pillar
    # Iron gate pillars (DS3: gate at lift exit)
    fill_tiles(chunk, TILE_WALL, 38, 46, 40, 50)     # Gate pillar left
    fill_tiles(chunk, TILE_WALL, 59, 46, 61, 50)     # Gate pillar right
    # Lantern sconces (DS3: wall-mounted lanterns in lift area)
    fill_tiles(chunk, TILE_WALL, 30, 34, 31, 36)
    fill_tiles(chunk, TILE_WALL, 68, 34, 69, 36)

    # ================================================================
    # 2. GARDEN STONE STAIRWAY — moss-covered descent
    # DS3: narrow stone stairway descending from lift area to the garden.
    #      Moss and water drip from the walls, iron railings.
    # Tiles: (31,56)-(62,81)
    # ================================================================
    # Stairway walls (DS3: enclosed stone staircase)
    fill_tiles(chunk, TILE_WALL, 31, 56, 33, 81)     # West wall
    fill_tiles(chunk, TILE_WALL, 60, 56, 62, 81)     # East wall
    fill_tiles(chunk, TILE_WALL, 31, 79, 62, 81)     # Bottom wall
    # Stair mid-point pillars (DS3: stone supports along stairs)
    fill_tiles(chunk, TILE_WALL, 40, 62, 42, 65)
    fill_tiles(chunk, TILE_WALL, 51, 62, 53, 65)
    fill_tiles(chunk, TILE_WALL, 36, 72, 38, 75)
    fill_tiles(chunk, TILE_WALL, 55, 72, 57, 75)
    # Railing posts (DS3: iron railings along descent)
    fill_tiles(chunk, TILE_WALL, 35, 68, 36, 69)
    fill_tiles(chunk, TILE_WALL, 57, 68, 58, 69)

    # ================================================================
    # 3. POISON GARDEN — toxic swamp with dead trees
    # DS3: large open toxic swamp garden. Pus of Man creatures in the water.
    #      Cathedral Knights patrol the edges. Rotten Slugs everywhere.
    #      Dead trees and stagnant toxic water throughout.
    # Tiles: (56,73)-(131,124)
    # ================================================================
    # Garden perimeter walls (DS3: high stone garden walls)
    fill_tiles(chunk, TILE_WALL, 56, 73, 58, 124)    # West wall
    fill_tiles(chunk, TILE_WALL, 129, 73, 131, 124)  # East wall
    fill_tiles(chunk, TILE_WALL, 56, 73, 131, 75)    # North wall
    fill_tiles(chunk, TILE_WALL, 56, 122, 131, 124)  # South wall
    # Poison swamp interior (DS3: toxic water fills most of the garden)
    fill_tiles(chunk, TILE_POISON, 62, 80, 123, 118)
    # Safe paths around edges (DS3: raised stone paths above swamp)
    fill_tiles(chunk, TILE_GROUND, 60, 76, 125, 79)  # North raised path
    fill_tiles(chunk, TILE_GROUND, 60, 119, 125, 121) # South raised path
    fill_tiles(chunk, TILE_GROUND, 59, 76, 62, 121)  # West raised path
    fill_tiles(chunk, TILE_GROUND, 123, 76, 126, 121) # East raised path
    # Central island (DS3: raised stone island in swamp center)
    fill_tiles(chunk, TILE_GROUND, 85, 92, 100, 106)
    fill_tiles(chunk, TILE_WALL, 86, 93, 88, 95)     # Island ruins NW
    fill_tiles(chunk, TILE_WALL, 97, 93, 99, 95)     # Island ruins NE
    fill_tiles(chunk, TILE_WALL, 86, 103, 88, 105)   # Island ruins SW
    fill_tiles(chunk, TILE_WALL, 97, 103, 99, 105)   # Island ruins SE
    # Dead trees in swamp (DS3: large dead trees rising from toxic water)
    fill_tiles(chunk, TILE_WALL, 70, 84, 72, 87)     # Dead tree NW
    fill_tiles(chunk, TILE_WALL, 115, 84, 117, 87)   # Dead tree NE
    fill_tiles(chunk, TILE_WALL, 70, 110, 72, 113)   # Dead tree SW
    fill_tiles(chunk, TILE_WALL, 115, 110, 117, 113) # Dead tree SE
    # Stepping stones (DS3: raised stones to cross swamp)
    fill_tiles(chunk, TILE_GROUND, 75, 90, 77, 92)
    fill_tiles(chunk, TILE_GROUND, 108, 90, 110, 92)
    fill_tiles(chunk, TILE_GROUND, 75, 108, 77, 110)
    fill_tiles(chunk, TILE_GROUND, 108, 108, 110, 110)
    # Garden archway ruins (DS3: crumbling stone arches)
    fill_tiles(chunk, TILE_WALL, 64, 96, 66, 100)    # Arch ruin west
    fill_tiles(chunk, TILE_WALL, 119, 96, 121, 100)  # Arch ruin east

    # ================================================================
    # 4. UPPER INTERIOR PLATFORM — stone platform above garden
    # DS3: upper stone platform overlooking the garden. Cathedral Knights
    #      and Lothric Priest guard this area. Crumbling battlements.
    # Tiles: (117,61)-(168,101)
    # ================================================================
    # Platform walls (DS3: stone platform with battlement walls)
    fill_tiles(chunk, TILE_WALL, 117, 61, 119, 101)  # West wall
    fill_tiles(chunk, TILE_WALL, 166, 61, 168, 101)  # East wall
    fill_tiles(chunk, TILE_WALL, 117, 61, 168, 63)   # North wall
    fill_tiles(chunk, TILE_WALL, 117, 99, 168, 101)  # South wall
    # Battlement merlons (DS3: crenellated stone battlements)
    for bx in range(122, 164, 6):
        fill_tiles(chunk, TILE_WALL, bx, 63, bx + 2, 65)
    for bx in range(122, 164, 6):
        fill_tiles(chunk, TILE_WALL, bx, 97, bx + 2, 99)
    # Interior stone pillars (DS3: stone columns supporting ceiling)
    fill_tiles(chunk, TILE_WALL, 130, 72, 132, 76)
    fill_tiles(chunk, TILE_WALL, 148, 72, 150, 76)
    fill_tiles(chunk, TILE_WALL, 130, 86, 132, 90)
    fill_tiles(chunk, TILE_WALL, 148, 86, 150, 90)
    # Overgrown masonry (DS3: moss-covered stone blocks)
    fill_tiles(chunk, TILE_WALL, 122, 80, 124, 82)
    fill_tiles(chunk, TILE_WALL, 160, 80, 162, 82)
    # Garden overlook balcony (DS3: balcony overlooking poison garden)
    fill_tiles(chunk, TILE_WALL, 138, 68, 142, 70)   # Balustrade left
    fill_tiles(chunk, TILE_WALL, 152, 68, 156, 70)   # Balustrade right

    # ================================================================
    # 5. LOWER GARDEN PATH — crumbling masonry path
    # DS3: lower path with crumbling masonry, overgrown arches,
    #      shallow poison puddles, dead hedges along the route.
    # Tiles: (112,112)-(162,143)
    # ================================================================
    # Path walls (DS3: crumbling garden walls)
    fill_tiles(chunk, TILE_WALL, 112, 112, 114, 143) # West wall
    fill_tiles(chunk, TILE_WALL, 160, 112, 162, 143) # East wall
    fill_tiles(chunk, TILE_WALL, 112, 112, 162, 114) # North wall
    fill_tiles(chunk, TILE_WALL, 112, 141, 162, 143) # South wall
    # Crumbling masonry (DS3: broken wall sections)
    fill_tiles(chunk, TILE_WALL, 120, 118, 122, 122)
    fill_tiles(chunk, TILE_WALL, 145, 118, 147, 122)
    fill_tiles(chunk, TILE_WALL, 130, 130, 132, 134)
    fill_tiles(chunk, TILE_WALL, 150, 130, 152, 134)
    # Overgrown arch (DS3: vine-covered stone arch spanning path)
    fill_tiles(chunk, TILE_WALL, 124, 124, 126, 128)
    fill_tiles(chunk, TILE_WALL, 140, 124, 142, 128)
    # Shallow poison puddles (DS3: small toxic pools on path)
    fill_tiles(chunk, TILE_POISON, 134, 120, 138, 122)
    fill_tiles(chunk, TILE_POISON, 136, 132, 140, 134)
    # Dead hedge walls (DS3: withered garden hedges)
    fill_tiles(chunk, TILE_WALL, 116, 136, 118, 138)
    fill_tiles(chunk, TILE_WALL, 155, 136, 157, 138)

    # ================================================================
    # 6. OCEIROS APPROACH — dark corridor to boss arena
    # DS3: dark corridor with moonlit archway, crumbling throne pillars,
    #      stone steps descending to Oceiros's throne room.
    # Tiles: (150,131)-(187,156)
    # ================================================================
    # Approach walls (DS3: dark stone corridor)
    fill_tiles(chunk, TILE_WALL, 150, 131, 152, 156) # West wall
    fill_tiles(chunk, TILE_WALL, 185, 131, 187, 156) # East wall
    fill_tiles(chunk, TILE_WALL, 150, 131, 187, 133) # North wall
    fill_tiles(chunk, TILE_WALL, 150, 154, 187, 156) # South wall
    # Throne pillars (DS3: crumbling pillars lining the approach)
    fill_tiles(chunk, TILE_WALL, 158, 136, 160, 140)
    fill_tiles(chunk, TILE_WALL, 170, 136, 172, 140)
    fill_tiles(chunk, TILE_WALL, 162, 146, 164, 150)
    fill_tiles(chunk, TILE_WALL, 176, 146, 178, 150)
    # Moonlit archway (DS3: arch with moonlight streaming through)
    fill_tiles(chunk, TILE_WALL, 154, 142, 156, 145)
    fill_tiles(chunk, TILE_WALL, 180, 142, 182, 145)
    # Stone steps (DS3: worn stone steps descending)
    fill_tiles(chunk, TILE_WALL, 166, 150, 168, 152)
    fill_tiles(chunk, TILE_WALL, 174, 150, 176, 152)

    # ================================================================
    # 7. OCEIROS ARENA — boss room
    # DS3: large crumbling throne room. Oceiros guards an invisible child.
    #      Moonlight shaft from above. Overgrown pillars throughout.
    # Tiles: (172,148)-(223,188)
    # ================================================================
    # Arena walls (DS3: crumbling throne room walls)
    fill_tiles(chunk, TILE_WALL, 172, 148, 174, 188) # West wall
    fill_tiles(chunk, TILE_WALL, 221, 148, 223, 188) # East wall
    fill_tiles(chunk, TILE_WALL, 172, 148, 223, 150) # North wall
    fill_tiles(chunk, TILE_WALL, 172, 186, 223, 188) # South wall
    # Throne platform (DS3: raised throne area where Oceiros starts)
    fill_tiles(chunk, TILE_WALL, 196, 160, 216, 162) # Throne dais back
    fill_tiles(chunk, TILE_WALL, 196, 164, 198, 172) # Throne left pillar
    fill_tiles(chunk, TILE_WALL, 214, 164, 216, 172) # Throne right pillar
    # Baby crib area (DS3: Oceiros cradles invisible child)
    fill_tiles(chunk, TILE_WALL, 202, 166, 210, 168)
    # Overgrown pillars (DS3: crystal-covered stone pillars)
    fill_tiles(chunk, TILE_WALL, 180, 158, 182, 164) # Pillar NW
    fill_tiles(chunk, TILE_WALL, 192, 158, 194, 164) # Pillar N
    fill_tiles(chunk, TILE_WALL, 180, 174, 182, 180) # Pillar W
    fill_tiles(chunk, TILE_WALL, 192, 174, 194, 180) # Pillar CW
    fill_tiles(chunk, TILE_WALL, 210, 174, 212, 180) # Pillar CE
    fill_tiles(chunk, TILE_WALL, 180, 178, 182, 184) # Pillar SW
    fill_tiles(chunk, TILE_WALL, 210, 178, 212, 184) # Pillar SE
    # Moonlight shaft (DS3: open ceiling with moonlight)
    fill_tiles(chunk, TILE_GROUND, 190, 166, 200, 174)
    # Crystal growths on walls (DS3: crystal formations everywhere)
    fill_tiles(chunk, TILE_WALL, 176, 155, 178, 158)
    fill_tiles(chunk, TILE_WALL, 218, 155, 220, 158)
    fill_tiles(chunk, TILE_WALL, 176, 182, 178, 185)
    fill_tiles(chunk, TILE_WALL, 218, 182, 220, 185)

    # ================================================================
    # 8. UNTENDED GRAVES ILLUSORY WALL — hidden passage
    # DS3: illusory wall behind Oceiros arena leads to dark chamber.
    #      Ash-covered floor, Serpent Man guards the hallway.
    # Tiles: (203,135)-(235,161)
    # ================================================================
    # Illusory wall chamber (DS3: hidden dark chamber)
    fill_tiles(chunk, TILE_WALL, 203, 135, 205, 161) # West wall
    fill_tiles(chunk, TILE_WALL, 233, 135, 235, 161) # East wall
    fill_tiles(chunk, TILE_WALL, 203, 135, 235, 137) # North wall
    fill_tiles(chunk, TILE_WALL, 203, 159, 235, 161) # South wall
    # Dark alcoves (DS3: shadowy corners)
    fill_tiles(chunk, TILE_WALL, 210, 142, 212, 146)
    fill_tiles(chunk, TILE_WALL, 226, 142, 228, 146)
    fill_tiles(chunk, TILE_WALL, 210, 152, 212, 156)
    fill_tiles(chunk, TILE_WALL, 226, 152, 228, 156)
    # Ash-covered stone blocks (DS3: ash piles on floor)
    fill_tiles(chunk, TILE_WALL, 218, 144, 220, 146)
    fill_tiles(chunk, TILE_WALL, 218, 150, 220, 152)

    # ================================================================
    # 9. HIDDEN GARDEN — small secret area
    # DS3: small hidden passage area between sections.
    # Tiles: (180,137)-(190,147)
    # ================================================================
    # Hidden garden walls (DS3: small enclosed secret garden)
    fill_tiles(chunk, TILE_WALL, 180, 137, 182, 147) # West wall
    fill_tiles(chunk, TILE_WALL, 188, 137, 190, 147) # East wall
    fill_tiles(chunk, TILE_WALL, 180, 137, 190, 139) # North wall
    fill_tiles(chunk, TILE_WALL, 180, 145, 190, 147) # South wall
    # Overgrown stone (DS3: moss-covered stones)
    fill_tiles(chunk, TILE_WALL, 184, 141, 186, 143)

    # ================================================================
    # CONNECTION CORRIDORS — DS3 route paths between sections
    # ================================================================
    # Lift area → Stone Stairway (south descent)
    fill_tiles(chunk, TILE_GROUND, 40, 50, 55, 62)
    # Stone Stairway → Poison Garden (south into swamp)
    fill_tiles(chunk, TILE_GROUND, 42, 72, 70, 78)
    # Poison Garden → Upper Interior Platform (east climb)
    fill_tiles(chunk, TILE_GROUND, 118, 76, 130, 82)
    # Upper Interior Platform → Lower Garden Path (south descent)
    fill_tiles(chunk, TILE_GROUND, 128, 95, 150, 116)
    # Poison Garden → Lower Garden Path (southeast)
    fill_tiles(chunk, TILE_GROUND, 110, 115, 130, 120)
    # Lower Garden Path → Oceiros Approach (east)
    fill_tiles(chunk, TILE_GROUND, 148, 132, 160, 142)
    # Oceiros Approach → Oceiros Arena (south into boss room)
    fill_tiles(chunk, TILE_GROUND, 160, 148, 185, 156)
    # Oceiros Arena → Untended Graves Wall (northeast hidden passage)
    fill_tiles(chunk, TILE_GROUND, 210, 148, 220, 158)
    # Upper Interior Platform → Hidden Garden (south)
    fill_tiles(chunk, TILE_GROUND, 170, 90, 188, 142)

    # ================================================================
    # FINALIZE — spawn and doc terrain
    # ================================================================
    spawn_px, spawn_py = 620, 520  # Fog gate entry from Lothric Castle (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("ConsumedKingsGarden"))
    return finalize_map("ConsumedKingsGarden", chunk, entities, spawn_px, spawn_py)
