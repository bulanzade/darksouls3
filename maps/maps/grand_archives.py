from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_ellipse, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)



def make_grand_archives():
    """Grand Archives -- DS3-faithful terrain.

    Towering library ascent through bookshelf mazes, wax pool halls,
    scholar galleries, gargoyle rooftops, and Twin Princes chamber.
    Entry at the south from Lothric Castle, exit north to Kiln.

    Map: 192x192 tiles (3072x3072 px).
    JSON doc sections (pixel -> tile = pixel // 16):
      1. Grand Archives Entry:       (0,171)-(54,191)   -- entrance hall from castle
      2. Wax Pool First Floor:       (30,146)-(96,173)  -- wax-coated library floor
      3. Second Floor Gallery:       (57,113)-(122,139)  -- bookshelf maze, desks, scholars
      4. Rooftop Gargoyles:          (86,79)-(159,104)   -- open rooftop with gargoyles
      5. Golden Winged Knight Roof:  (103,49)-(169,70)   -- high rooftop, winged knights
      6. Princes Stair:             (125,28)-(185,45)    -- stairway to Lothric's chamber
      7. Twin Princes Chamber:      (135,9)-(191,29)     -- Lorian & Lothric boss arena
    """
    chunk = new_chunk(192, 192)

    # ================================================================
    # 1. GRAND ARCHIVES ENTRY -- entrance hall from Lothric Castle
    # DS3: large stone entry hall with bookshelves, Gotthard's corpse at door
    # Section: x=0,y=2750,w=878,h=322 -> tiles (0,171)-(54,191)
    # ================================================================
    # Perimeter walls
    fill_tiles(chunk, TILE_WALL, 0, 171, 2, 191)       # West wall
    fill_tiles(chunk, TILE_WALL, 52, 171, 54, 191)     # East wall
    fill_tiles(chunk, TILE_WALL, 0, 171, 54, 173)      # North wall
    fill_tiles(chunk, TILE_WALL, 0, 189, 20, 191)      # South wall left
    fill_tiles(chunk, TILE_WALL, 35, 189, 54, 191)     # South wall right
    # Bookshelf rows along walls (DS3: towering bookshelves line entry hall)
    fill_tiles(chunk, TILE_WALL, 5, 175, 6, 183)       # Left bookshelf
    fill_tiles(chunk, TILE_WALL, 12, 177, 13, 185)     # Left-center bookshelf
    fill_tiles(chunk, TILE_WALL, 38, 176, 39, 184)     # Right-center bookshelf
    fill_tiles(chunk, TILE_WALL, 46, 178, 47, 186)     # Right bookshelf
    # Reading desk (DS3: scholars study at desks near entrance)
    fill_tiles(chunk, TILE_WALL, 22, 180, 24, 182)     # Center desk
    # Entry archway pillars (DS3: stone arch frames the entrance)
    fill_tiles(chunk, TILE_WALL, 20, 173, 22, 175)     # Left arch pillar
    fill_tiles(chunk, TILE_WALL, 33, 173, 35, 175)     # Right arch pillar

    # ================================================================
    # 2. WAX POOL FIRST FLOOR -- wax-coated library with pool
    # DS3: large hall with central wax pool, scholars wading through wax,
    # narrow bookshelf corridors, Crystal Sage arena nearby
    # Section: x=481,y=2342,w=1066,h=430 -> tiles (30,146)-(96,173)
    # ================================================================
    # Perimeter walls
    fill_tiles(chunk, TILE_WALL, 30, 146, 32, 173)     # West wall
    fill_tiles(chunk, TILE_WALL, 94, 146, 96, 173)     # East wall
    fill_tiles(chunk, TILE_WALL, 30, 146, 96, 148)     # North wall
    fill_tiles(chunk, TILE_WALL, 30, 171, 96, 173)     # South wall
    # Central wax pool (DS3: molten wax pool -- slows movement, non-toxic)
    # Kept as TILE_GROUND (wax slows but is non-toxic in DS3)
    fill_tiles(chunk, TILE_GROUND, 38, 149, 70, 159)   # Wax pool floor
    # Bookshelf walls around pool (DS3: bookshelves border the wax pool)
    fill_tiles(chunk, TILE_WALL, 43, 148, 44, 151)     # NW pool bookshelf
    fill_tiles(chunk, TILE_WALL, 56, 154, 57, 157)     # Center pool bookshelf
    fill_tiles(chunk, TILE_WALL, 66, 149, 67, 153)     # NE pool bookshelf
    # Long bookshelf rows creating narrow corridors (DS3: maze-like library)
    fill_tiles(chunk, TILE_WALL, 33, 162, 34, 168)     # West corridor shelf
    fill_tiles(chunk, TILE_WALL, 45, 160, 46, 167)     # Center-left shelf
    fill_tiles(chunk, TILE_WALL, 58, 163, 59, 169)     # Center-right shelf
    fill_tiles(chunk, TILE_WALL, 72, 161, 73, 168)     # East corridor shelf
    fill_tiles(chunk, TILE_WALL, 85, 160, 86, 166)     # Far east shelf
    # Scholar desks (DS3: study desks between bookshelves)
    fill_tiles(chunk, TILE_WALL, 40, 155, 42, 156)     # Desk near pool
    fill_tiles(chunk, TILE_WALL, 78, 155, 80, 157)     # East desk
    fill_tiles(chunk, TILE_WALL, 50, 168, 52, 169)     # South desk

    # ================================================================
    # 3. SECOND FLOOR GALLERY -- bookshelf maze, desks, scholars
    # DS3: dense library floor with towering bookshelf rows, reading alcoves,
    # Grand Archives Scholars patrol between shelves
    # Section: x=920,y=1815,w=1045,h=408 -> tiles (57,113)-(122,139)
    # ================================================================
    # Perimeter walls
    fill_tiles(chunk, TILE_WALL, 57, 113, 59, 139)     # West wall
    fill_tiles(chunk, TILE_WALL, 120, 113, 122, 139)   # East wall
    fill_tiles(chunk, TILE_WALL, 57, 113, 122, 115)    # North wall
    fill_tiles(chunk, TILE_WALL, 57, 137, 122, 139)    # South wall
    # Dense bookshelf rows (DS3: labyrinthine bookshelf corridors)
    fill_tiles(chunk, TILE_WALL, 63, 118, 64, 125)     # Bookshelf row 1
    fill_tiles(chunk, TILE_WALL, 72, 116, 73, 123)     # Bookshelf row 2
    fill_tiles(chunk, TILE_WALL, 82, 119, 83, 126)     # Bookshelf row 3
    fill_tiles(chunk, TILE_WALL, 92, 117, 93, 124)     # Bookshelf row 4
    fill_tiles(chunk, TILE_WALL, 103, 118, 104, 126)   # Bookshelf row 5
    fill_tiles(chunk, TILE_WALL, 113, 117, 114, 124)   # Bookshelf row 6
    # Cross-shelves creating maze (DS3: perpendicular shelves block sightlines)
    fill_tiles(chunk, TILE_WALL, 66, 127, 76, 128)     # Cross-shelf 1
    fill_tiles(chunk, TILE_WALL, 86, 129, 97, 130)     # Cross-shelf 2
    fill_tiles(chunk, TILE_WALL, 105, 126, 116, 127)   # Cross-shelf 3
    # Reading desks between shelves (DS3: scholars at desks throughout)
    fill_tiles(chunk, TILE_WALL, 67, 115, 69, 116)     # Desk near row 1
    fill_tiles(chunk, TILE_WALL, 77, 124, 79, 125)     # Desk between rows
    fill_tiles(chunk, TILE_WALL, 95, 115, 97, 116)     # Desk near row 4
    fill_tiles(chunk, TILE_WALL, 107, 131, 109, 132)   # Desk south area
    # Pillars (DS3: stone pillars support the vaulted ceiling)
    fill_tiles(chunk, TILE_WALL, 75, 132, 76, 133)     # SW pillar
    fill_tiles(chunk, TILE_WALL, 99, 134, 100, 135)    # SE pillar

    # ================================================================
    # 4. ROOFTOP GARGOLES -- open rooftop with gargoyle encounters
    # DS3: wide rooftop area with chimneys, roof structures, barricades,
    # gargoyles swoop down, Ascended Winged Knights patrol
    # Section: x=1379,y=1267,w=1170,h=408 -> tiles (86,79)-(159,104)
    # ================================================================
    # Perimeter walls (DS3: castle parapet walls around rooftop)
    fill_tiles(chunk, TILE_WALL, 86, 79, 88, 104)      # West parapet
    fill_tiles(chunk, TILE_WALL, 157, 79, 159, 104)    # East parapet
    fill_tiles(chunk, TILE_WALL, 86, 79, 159, 81)      # North parapet
    fill_tiles(chunk, TILE_WALL, 86, 102, 159, 104)    # South parapet
    # Chimney stacks (DS3: stone chimneys on rooftop)
    fill_tiles(chunk, TILE_WALL, 94, 83, 96, 88)       # Chimney 1
    fill_tiles(chunk, TILE_WALL, 103, 84, 105, 87)     # Chimney 2
    fill_tiles(chunk, TILE_WALL, 113, 81, 115, 85)     # Chimney 3
    fill_tiles(chunk, TILE_WALL, 124, 83, 126, 87)     # Chimney 4
    # Roof structures (DS3: peaked roof sections)
    fill_tiles(chunk, TILE_WALL, 134, 85, 136, 89)     # Roof structure 1
    fill_tiles(chunk, TILE_WALL, 145, 83, 147, 87)     # Roof structure 2
    # Barricades (DS3: wooden barricades on rooftop)
    fill_tiles(chunk, TILE_WALL, 98, 80, 98, 84)       # Barricade 1
    fill_tiles(chunk, TILE_WALL, 106, 84, 106, 88)     # Barricade 2
    fill_tiles(chunk, TILE_WALL, 118, 80, 118, 84)     # Barricade 3
    fill_tiles(chunk, TILE_WALL, 140, 80, 140, 83)     # Barricade 4

    # ================================================================
    # 5. GOLDEN WINGED KNIGHT ROOFTOP -- high rooftop with winged knights
    # DS3: upper rooftop where three Ascended Winged Knights patrol,
    # Titanite Slab reward for defeating all three
    # Section: x=1651,y=795,w=1066,h=333 -> tiles (103,49)-(169,70)
    # ================================================================
    # Perimeter walls (DS3: high castle battlements)
    fill_tiles(chunk, TILE_WALL, 103, 49, 105, 70)     # West battlement
    fill_tiles(chunk, TILE_WALL, 167, 49, 169, 70)     # East battlement
    fill_tiles(chunk, TILE_WALL, 103, 49, 169, 51)     # North battlement
    fill_tiles(chunk, TILE_WALL, 103, 68, 169, 70)     # South battlement
    # Armor displays (DS3: suits of armor displayed on rooftop)
    fill_tiles(chunk, TILE_WALL, 110, 52, 112, 54)     # Armor display 1
    fill_tiles(chunk, TILE_WALL, 123, 54, 125, 56)     # Armor display 2
    fill_tiles(chunk, TILE_WALL, 136, 52, 138, 54)     # Armor display 3
    # Pillars (DS3: stone pillars supporting higher structures)
    fill_tiles(chunk, TILE_WALL, 148, 52, 149, 53)     # Center pillar
    fill_tiles(chunk, TILE_WALL, 160, 55, 161, 56)     # East pillar

    # ================================================================
    # 6. PRINCES STAIR -- stairway to Lothric's chamber
    # DS3: grand staircase with throne pillars leading to boss fog gate
    # Section: x=2006,y=451,w=961,h=279 -> tiles (125,28)-(185,45)
    # ================================================================
    # Perimeter walls
    fill_tiles(chunk, TILE_WALL, 125, 28, 127, 45)     # West wall
    fill_tiles(chunk, TILE_WALL, 183, 28, 185, 45)     # East wall
    fill_tiles(chunk, TILE_WALL, 125, 28, 185, 30)     # North wall
    fill_tiles(chunk, TILE_WALL, 125, 43, 185, 45)     # South wall
    # Throne pillars along stair (DS3: pillars line the approach to Lothric)
    fill_tiles(chunk, TILE_WALL, 130, 31, 131, 32)     # Pillar 1
    fill_tiles(chunk, TILE_WALL, 146, 32, 147, 33)     # Pillar 2
    fill_tiles(chunk, TILE_WALL, 155, 31, 156, 32)     # Pillar 3
    fill_tiles(chunk, TILE_WALL, 170, 33, 171, 34)     # Pillar 4
    fill_tiles(chunk, TILE_WALL, 178, 31, 179, 32)     # Pillar 5

    # ================================================================
    # 7. TWIN PRINCES CHAMBER -- Lorian & Lothric boss arena
    # DS3: grand throne room at the top of the archives, Lothric's chamber,
    # throne pillars, sunset light, fog gate to Kiln
    # Section: x=2173,y=150,w=899,h=333 -> tiles (135,9)-(191,29)
    # ================================================================
    # Perimeter walls
    fill_tiles(chunk, TILE_WALL, 135, 9, 137, 29)      # West wall
    fill_tiles(chunk, TILE_WALL, 189, 9, 191, 29)      # East wall
    fill_tiles(chunk, TILE_WALL, 135, 9, 191, 11)      # North wall
    fill_tiles(chunk, TILE_WALL, 135, 27, 191, 29)     # South wall
    # Throne pillars (DS3: pillars around Lothric's throne)
    fill_tiles(chunk, TILE_WALL, 142, 12, 143, 13)     # NW throne pillar
    fill_tiles(chunk, TILE_WALL, 158, 13, 159, 14)     # N throne pillar
    fill_tiles(chunk, TILE_WALL, 168, 12, 169, 13)     # NE throne pillar
    fill_tiles(chunk, TILE_WALL, 150, 19, 151, 20)     # SW throne pillar
    fill_tiles(chunk, TILE_WALL, 163, 20, 164, 21)     # SE throne pillar
    # Central throne area (DS3: Lothric's throne, keep clear for boss fight)
    carve_ellipse(chunk, 162, 18, 12, 8)

    # ================================================================
    # CONNECTION CORRIDORS -- DS3 vertical library ascent
    # ================================================================
    # Entry -> Wax Pool (north through bookshelves)
    fill_tiles(chunk, TILE_GROUND, 25, 168, 42, 175)
    # Wax Pool -> Second Floor Gallery (north-east climb)
    fill_tiles(chunk, TILE_GROUND, 55, 142, 70, 150)
    # Second Floor Gallery -> Rooftop Gargoyles (north-east)
    fill_tiles(chunk, TILE_GROUND, 80, 108, 100, 116)
    # Rooftop Gargoyles -> Winged Knight Rooftop (north climb)
    fill_tiles(chunk, TILE_GROUND, 100, 68, 115, 82)
    # Winged Knight Rooftop -> Princes Stair (north-east)
    fill_tiles(chunk, TILE_GROUND, 125, 45, 140, 52)
    # Princes Stair -> Twin Princes Chamber (north)
    fill_tiles(chunk, TILE_GROUND, 145, 26, 165, 30)

    # ================================================================
    # ADDITIONAL DS3 TERRAIN -- wax side passages, crystal alcoves
    # ================================================================
    # Crystal Sage alcove off Wax Pool (DS3: Crystal Sage fight area)
    fill_tiles(chunk, TILE_GROUND, 30, 160, 38, 166)
    # Winged Knight side passage (DS3: narrow corridor to knight ambush)
    fill_tiles(chunk, TILE_GROUND, 110, 60, 130, 68)
    # Gertrude's cage area (DS3: elevated chamber, Divine Pillars of Light)
    fill_tiles(chunk, TILE_GROUND, 90, 90, 100, 100)

    # ================================================================
    # FINALIZE -- load doc, apply terrain, return
    # ================================================================
    spawn_px, spawn_py = 209, 2900  # Grand Archives bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("GrandArchives"))
    return finalize_map("GrandArchives", chunk, entities, spawn_px, spawn_py)
