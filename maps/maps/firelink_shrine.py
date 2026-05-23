from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_firelink_shrine():
    """Firelink Shrine -- DS3-faithful terrain.

    Central hub: raised stone shrine building with bonfire chamber, flanked
    by Andre's forge alcove (west) and Handmaid's shop alcove (east).
    Lord Thrones run along the north wall. Roof rafters and tower bridge
    span above. Exterior graveyard to the south holds hostile enemies.
    Fog gates: south to Cemetery of Ash, north to Lothric Wall.

    JSON doc is authoritative for entity positions. apply_doc_terrain() fills
    section interiors, carves corridors, clears bonfire/boss/fog positions.

    Section layout (tiles, map is 160x128):
      Exterior Graves:    (65,105)-(97,122)  center (81,113)
      Central Shrine Hall:(47,46)-(112,93)   center (80,70)
      Andre Alcove:       (26,56)-(48,78)    center (37,67)
      Handmaid Alcove:    (111,56)-(133,78)  center (122,67)
      Lord Thrones:       (51,26)-(108,44)   center (80,36)
      Roof and Tower:     (22,11)-(137,33)   center (80,22)
      High Wall Warp:     (72,3)-(87,13)     center (80,8)
    """
    chunk = new_chunk(160, 128)

    # ================================================================
    # 1. CENTRAL SHRINE HALL -- large stone chamber with bonfire
    # DS3: the main circular room, bonfire at center, coiled sword,
    #      Fire Keeper tends the flame. Stone walls, arched ceiling.
    # Section: tiles (47,46)-(112,93)
    # ================================================================
    # Perimeter walls (DS3: thick stone shrine walls)
    fill_tiles(chunk, TILE_WALL, 47, 46, 50, 90)     # West wall
    fill_tiles(chunk, TILE_WALL, 109, 46, 112, 90)   # East wall
    fill_tiles(chunk, TILE_WALL, 47, 46, 112, 49)    # North wall
    fill_tiles(chunk, TILE_WALL, 47, 90, 112, 93)    # South wall
    # Grand entrance archway (DS3: wide stone arch opening south)
    fill_tiles(chunk, TILE_GROUND, 74, 90, 86, 93)
    # Entrance arch pillars (DS3: stone pillars flanking the doorway)
    fill_tiles(chunk, TILE_WALL, 72, 88, 74, 93)     # Left arch pillar
    fill_tiles(chunk, TILE_WALL, 86, 88, 88, 93)     # Right arch pillar
    # Interior stone pillars (DS3: thick columns supporting the roof)
    fill_tiles(chunk, TILE_WALL, 56, 54, 58, 62)     # NW pillar
    fill_tiles(chunk, TILE_WALL, 101, 54, 103, 62)   # NE pillar
    fill_tiles(chunk, TILE_WALL, 56, 78, 58, 86)     # SW pillar
    fill_tiles(chunk, TILE_WALL, 101, 78, 103, 86)   # SE pillar
    # Coiled sword bonfire ring (DS3: stone ring around the bonfire)
    fill_tiles(chunk, TILE_WALL, 77, 66, 79, 68)     # NW ring stone
    fill_tiles(chunk, TILE_WALL, 81, 66, 83, 68)     # NE ring stone
    fill_tiles(chunk, TILE_WALL, 77, 73, 79, 75)     # SW ring stone
    fill_tiles(chunk, TILE_WALL, 81, 73, 83, 75)     # SE ring stone

    # ================================================================
    # 2. LORD THRONES -- semicircular throne alcove north of bonfire
    # DS3: five Lord of Cinder thrones along the north wall, Ludleth
    #      sits on his. Coiled sword fragment marks the center.
    # Section: tiles (51,26)-(108,44)
    # ================================================================
    # Perimeter walls (DS3: throne room stone walls)
    fill_tiles(chunk, TILE_WALL, 51, 26, 54, 42)     # West wall
    fill_tiles(chunk, TILE_WALL, 105, 26, 108, 42)   # East wall
    fill_tiles(chunk, TILE_WALL, 51, 26, 108, 28)    # North wall
    # Throne bases (DS3: five stone thrones in a row)
    fill_tiles(chunk, TILE_WALL, 57, 30, 60, 33)     # Throne 1 (Abyss Watchers)
    fill_tiles(chunk, TILE_WALL, 65, 29, 68, 32)     # Throne 2 (Yhorm)
    fill_tiles(chunk, TILE_WALL, 77, 28, 80, 31)     # Throne 3 (Ludleth - center)
    fill_tiles(chunk, TILE_WALL, 89, 29, 92, 32)     # Throne 4 (Aldrich)
    fill_tiles(chunk, TILE_WALL, 97, 30, 100, 33)    # Throne 5 (Lothric)
    # Throne room divider walls (DS3: short walls separating throne room)
    fill_tiles(chunk, TILE_WALL, 62, 36, 64, 40)
    fill_tiles(chunk, TILE_WALL, 95, 36, 97, 40)

    # ================================================================
    # 3. ANDRE'S FORGE ALCOVE (west) -- blacksmith workshop
    # DS3: Andre works at his anvil in a stone alcove off the main hall.
    #      Forge, anvil, titanite supplies. Connected by short corridor.
    # Section: tiles (26,56)-(48,78)
    # ================================================================
    # Perimeter walls (DS3: stone workshop walls)
    fill_tiles(chunk, TILE_WALL, 26, 56, 29, 76)     # West wall
    fill_tiles(chunk, TILE_WALL, 45, 56, 48, 76)     # East wall
    fill_tiles(chunk, TILE_WALL, 26, 56, 48, 58)     # North wall
    fill_tiles(chunk, TILE_WALL, 26, 74, 48, 78)     # South wall
    # Forge anvil (DS3: large stone anvil where Andre works)
    fill_tiles(chunk, TILE_WALL, 34, 64, 37, 68)     # Anvil block
    # Forge workbench (DS3: workbench with titanite and tools)
    fill_tiles(chunk, TILE_WALL, 30, 60, 32, 63)     # NW workbench
    fill_tiles(chunk, TILE_WALL, 40, 70, 43, 73)     # SE debris pile
    # Entry arch (DS3: archway connecting forge to main hall)
    fill_tiles(chunk, TILE_GROUND, 45, 64, 48, 72)

    # ================================================================
    # 4. HANDMAID ALCOVE (east) -- Shrine Handmaiden's shop
    # DS3: Handmaiden stands behind stone shelves of goods in an alcove
    #      on the east side. Shelves with weapons, armor, trinkets.
    # Section: tiles (111,56)-(133,78)
    # ================================================================
    # Perimeter walls (DS3: stone shop walls)
    fill_tiles(chunk, TILE_WALL, 111, 56, 114, 76)   # West wall
    fill_tiles(chunk, TILE_WALL, 130, 56, 133, 76)   # East wall
    fill_tiles(chunk, TILE_WALL, 111, 56, 133, 58)   # North wall
    fill_tiles(chunk, TILE_WALL, 111, 74, 133, 78)   # South wall
    # Stone shelves (DS3: Handmaiden's merchandise shelves)
    fill_tiles(chunk, TILE_WALL, 116, 60, 118, 64)   # NW shelf
    fill_tiles(chunk, TILE_WALL, 125, 60, 127, 64)   # NE shelf
    fill_tiles(chunk, TILE_WALL, 120, 70, 123, 73)   # Central table
    # Entry arch (DS3: archway from main hall to shop)
    fill_tiles(chunk, TILE_GROUND, 112, 64, 114, 72)

    # ================================================================
    # 5. ROOF AND TOWER -- rafter area above shrine, tower bridge
    # DS3: wooden rafters accessible by dropping from tower bridge.
    #      Tower connects via narrow bridge on the west side.
    #      Contains chest with Covetous Silver Serpent Ring, Estus Shard,
    #      Estus Ring, Fire Keeper Soul, Fire Keeper Set.
    # Section: tiles (22,11)-(137,33)
    # ================================================================
    # Outer boundary walls (DS3: tower and rafter boundary)
    fill_tiles(chunk, TILE_WALL, 22, 11, 25, 31)     # West wall
    fill_tiles(chunk, TILE_WALL, 134, 11, 137, 31)   # East wall
    fill_tiles(chunk, TILE_WALL, 22, 11, 137, 13)    # North wall
    fill_tiles(chunk, TILE_WALL, 22, 30, 137, 33)    # South wall
    # Tower structure (DS3: locked tower on the west, accessible with Tower Key)
    fill_tiles(chunk, TILE_WALL, 26, 14, 28, 20)     # Tower west wall
    fill_tiles(chunk, TILE_WALL, 34, 14, 36, 20)     # Tower east wall
    fill_tiles(chunk, TILE_WALL, 26, 14, 36, 15)     # Tower north wall
    # Tower bridge (DS3: narrow stone bridge connecting tower to shrine roof)
    fill_tiles(chunk, TILE_WALL, 38, 18, 42, 20)     # Bridge railing left
    fill_tiles(chunk, TILE_WALL, 48, 18, 52, 20)     # Bridge railing right
    # Rafter beams (DS3: exposed wooden rafters spanning the ceiling)
    fill_tiles(chunk, TILE_WALL, 60, 16, 62, 22)     # Rafter beam 1
    fill_tiles(chunk, TILE_WALL, 75, 14, 77, 20)     # Rafter beam 2
    fill_tiles(chunk, TILE_WALL, 90, 16, 92, 22)     # Rafter beam 3
    fill_tiles(chunk, TILE_WALL, 105, 14, 107, 20)   # Rafter beam 4
    fill_tiles(chunk, TILE_WALL, 120, 16, 122, 22)   # Rafter beam 5
    # Rafter cross-beams (DS3: perpendicular support beams)
    fill_tiles(chunk, TILE_WALL, 65, 24, 95, 26)
    fill_tiles(chunk, TILE_WALL, 100, 24, 130, 26)

    # ================================================================
    # 6. HIGH WALL WARP -- north exit to Lothric Wall
    # DS3: coiled sword fragment serves as warp point to High Wall.
    #      Small alcove at the very top of the map.
    # Section: tiles (72,3)-(87,13)
    # ================================================================
    # Perimeter walls (DS3: stone alcove with warp shrine)
    fill_tiles(chunk, TILE_WALL, 72, 3, 75, 11)      # West wall
    fill_tiles(chunk, TILE_WALL, 84, 3, 87, 11)      # East wall
    fill_tiles(chunk, TILE_WALL, 72, 3, 87, 5)       # North wall
    # Warp altar (DS3: stone platform with coiled sword fragment)
    fill_tiles(chunk, TILE_WALL, 77, 5, 79, 7)
    fill_tiles(chunk, TILE_WALL, 83, 5, 85, 7)

    # ================================================================
    # 7. EXTERIOR GRAVEYARD -- tombstones and hostile enemies
    # DS3: open graveyard south of the shrine. Grave Wardens, Starved
    #      Hounds, Sword Master patrols here. Dense tombstone rows,
    #      dead trees, stone path to Cemetery of Ash.
    # Section: tiles (65,105)-(97,122)
    # ================================================================
    # Boundary walls (DS3: cliff faces and cemetery walls)
    fill_tiles(chunk, TILE_WALL, 65, 105, 68, 120)   # West wall
    fill_tiles(chunk, TILE_WALL, 94, 105, 97, 120)   # East wall
    fill_tiles(chunk, TILE_WALL, 65, 105, 97, 107)   # North wall
    fill_tiles(chunk, TILE_WALL, 65, 120, 97, 122)   # South wall
    # Entry from shrine (DS3: stone steps down from shrine entrance)
    fill_tiles(chunk, TILE_GROUND, 74, 93, 86, 107)
    # Tombstone rows (DS3: densely packed gravestones)
    fill_tiles(chunk, TILE_WALL, 70, 110, 71, 112)   # Row 1
    fill_tiles(chunk, TILE_WALL, 76, 108, 77, 110)
    fill_tiles(chunk, TILE_WALL, 82, 110, 83, 112)
    fill_tiles(chunk, TILE_WALL, 88, 108, 89, 110)
    fill_tiles(chunk, TILE_WALL, 73, 114, 74, 116)   # Row 2
    fill_tiles(chunk, TILE_WALL, 79, 116, 80, 118)
    fill_tiles(chunk, TILE_WALL, 85, 114, 86, 116)
    fill_tiles(chunk, TILE_WALL, 91, 116, 92, 118)
    # Dead tree stumps (DS3: gnarled dead trees in the graveyard)
    fill_tiles(chunk, TILE_WALL, 68, 112, 69, 114)
    fill_tiles(chunk, TILE_WALL, 94, 112, 95, 114)
    # Exit path south (DS3: path continues to Cemetery of Ash)
    fill_tiles(chunk, TILE_GROUND, 76, 118, 84, 122)

    # ================================================================
    # CONNECTION CORRIDORS -- carved paths between sections
    # ================================================================
    # Central Hall -> Lord Thrones (north)
    fill_tiles(chunk, TILE_GROUND, 74, 44, 86, 50)
    # Central Hall -> Andre's Forge (west)
    fill_tiles(chunk, TILE_GROUND, 47, 64, 56, 76)
    # Central Hall -> Handmaid Alcove (east)
    fill_tiles(chunk, TILE_GROUND, 104, 64, 114, 76)
    # Lord Thrones -> Roof and Tower (north)
    fill_tiles(chunk, TILE_GROUND, 74, 28, 86, 33)
    # Roof and Tower -> High Wall Warp (north)
    fill_tiles(chunk, TILE_GROUND, 76, 13, 84, 26)
    # Central Hall -> Exterior Graves (south)
    fill_tiles(chunk, TILE_GROUND, 74, 90, 86, 107)
    # Tower bridge connecting to rafter area
    fill_tiles(chunk, TILE_GROUND, 28, 18, 60, 22)
    # Rafter area to east rafter access
    fill_tiles(chunk, TILE_GROUND, 95, 18, 130, 22)

    # ================================================================
    # FINALIZE -- spawn, doc terrain, return
    # ================================================================
    spawn_px, spawn_py = 1280, 1024  # Firelink Shrine bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("FirelinkShrine"))

    return finalize_map("FirelinkShrine", chunk, entities, spawn_px, spawn_py)
