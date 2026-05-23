from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_kiln_of_the_first_flame():
    """Kiln of the First Flame -- DS3-faithful terrain.

    Linear descent through ash and ruin. No regular enemies.
    Route: Flameless Shrine (south) -> Ashen Ruins -> Ashen Wasteland ->
    First Flame Arena (north, Soul of Cinder boss).

    JSON doc is authoritative for entity positions. apply_doc_terrain() fills
    section interiors, carves corridors, clears bonfire/boss/fog positions,
    and places wall features (iron_girder, collapsed_wall, ruined_pillar).

    Section layout (tiles, map is 256x224):
      Flameless Shrine: (26,122)-(82,160)   center (54,141)
      Ashen Ruins:      (85,133)-(115,147)  center (100,140)
      Ashen Wasteland:  (67,90)-(124,125)   center (96,107)
      First Flame Arena:(73,47)-(134,92)    center (104,70)
    """
    chunk = new_chunk(256, 224)

    # ================================================================
    # 1. FLAMELESS SHRINE (south) -- dark mirror of Firelink Shrine
    # DS3: identical layout to Firelink but buried in ash, dim lighting,
    #      only the Fire Keeper stands here. Entry from Grand Archives.
    # Section: tiles (26,122)-(82,160)
    # ================================================================
    # Perimeter walls (DS3: ash-buried shrine walls)
    fill_tiles(chunk, TILE_WALL, 26, 122, 30, 152)    # West wall
    fill_tiles(chunk, TILE_WALL, 78, 122, 82, 152)    # East wall
    fill_tiles(chunk, TILE_WALL, 26, 122, 82, 125)    # North wall
    fill_tiles(chunk, TILE_WALL, 26, 155, 82, 160)    # South wall
    # Interior shrine columns (DS3: stone pillars supporting shrine roof)
    fill_tiles(chunk, TILE_WALL, 36, 128, 38, 148)    # Left column row
    fill_tiles(chunk, TILE_WALL, 70, 128, 72, 148)    # Right column row
    # Shrine alcove walls (DS3: small rooms along shrine sides)
    fill_tiles(chunk, TILE_WALL, 30, 130, 34, 134)    # NW alcove
    fill_tiles(chunk, TILE_WALL, 74, 130, 78, 134)    # NE alcove
    fill_tiles(chunk, TILE_WALL, 30, 142, 34, 146)    # SW alcove
    fill_tiles(chunk, TILE_WALL, 74, 142, 78, 146)    # SE alcove
    # Ash dunes inside shrine (DS3: deep ash covering the floor)
    fill_tiles(chunk, TILE_WALL, 40, 132, 42, 134)
    fill_tiles(chunk, TILE_WALL, 66, 132, 68, 134)
    fill_tiles(chunk, TILE_WALL, 40, 144, 42, 146)
    fill_tiles(chunk, TILE_WALL, 66, 144, 68, 146)
    # Broken stone bench (DS3: ruined throne-like structure)
    fill_tiles(chunk, TILE_WALL, 50, 150, 58, 152)
    # Entry arch pillars (DS3: archway from fog gate)
    fill_tiles(chunk, TILE_WALL, 34, 155, 38, 158)
    fill_tiles(chunk, TILE_WALL, 70, 155, 74, 158)

    # ================================================================
    # 2. ASHEN RUINS -- transition between shrine and wasteland
    # DS3: scattered burned pillars and ash dunes. A small side area
    #      near the Kiln bonfire with ember debris.
    # Section: tiles (85,133)-(115,147)
    # ================================================================
    # Boundary walls (DS3: ruined walls flanking the ash dunes)
    fill_tiles(chunk, TILE_WALL, 85, 133, 88, 145)    # West wall
    fill_tiles(chunk, TILE_WALL, 112, 133, 115, 145)  # East wall
    fill_tiles(chunk, TILE_WALL, 85, 133, 115, 135)   # North wall
    fill_tiles(chunk, TILE_WALL, 85, 145, 115, 147)   # South wall
    # Burned pillars (DS3: charred column stumps in the ash)
    fill_tiles(chunk, TILE_WALL, 92, 137, 93, 139)
    fill_tiles(chunk, TILE_WALL, 107, 137, 108, 139)
    fill_tiles(chunk, TILE_WALL, 99, 141, 100, 143)
    # Ember debris (DS3: glowing coals and cinders scattered in ash)
    fill_tiles(chunk, TILE_WALL, 90, 134, 91, 135)
    fill_tiles(chunk, TILE_WALL, 109, 134, 110, 135)
    fill_tiles(chunk, TILE_WALL, 96, 144, 97, 145)
    fill_tiles(chunk, TILE_WALL, 103, 144, 104, 145)

    # ================================================================
    # 3. ASHEN WASTELAND -- wide ash field with collapsed iron structures
    # DS3: vast open ash field, twisted iron girders sticking out of the
    #      ground like a metal forest. Collapsed walls and slag everywhere.
    # Section: tiles (67,90)-(124,125)
    # ================================================================
    # Perimeter walls (DS3: ash dunes forming natural boundaries)
    fill_tiles(chunk, TILE_WALL, 67, 90, 70, 122)     # West wall
    fill_tiles(chunk, TILE_WALL, 121, 90, 124, 122)   # East wall
    fill_tiles(chunk, TILE_WALL, 67, 90, 124, 93)     # North wall
    fill_tiles(chunk, TILE_WALL, 67, 122, 124, 125)   # South wall
    # Collapsed wall sections (DS3: ruined masonry half-buried in ash)
    fill_tiles(chunk, TILE_WALL, 75, 95, 78, 98)      # NW rubble
    fill_tiles(chunk, TILE_WALL, 113, 95, 116, 98)    # NE rubble
    fill_tiles(chunk, TILE_WALL, 75, 117, 78, 120)    # SW rubble
    fill_tiles(chunk, TILE_WALL, 113, 117, 116, 120)  # SE rubble
    # Slag mounds (DS3: solidified molten metal deposits)
    fill_tiles(chunk, TILE_WALL, 82, 100, 84, 102)
    fill_tiles(chunk, TILE_WALL, 107, 100, 109, 102)
    fill_tiles(chunk, TILE_WALL, 92, 115, 94, 117)
    fill_tiles(chunk, TILE_WALL, 99, 115, 101, 117)
    # Note: iron_girder and collapsed_wall features from JSON doc are placed
    # by apply_doc_terrain automatically (they are in WALL_FEATURE_KINDS)

    # ================================================================
    # 4. FIRST FLAME ARENA (north) -- circular boss arena with altar
    # DS3: large circular arena, ash-covered ground, the First Flame
    #      altar at center where Soul of Cinder awaits. Surrounded by
    #      ruined arches and broken thrones of past Lords of Cinder.
    # Section: tiles (73,47)-(134,92)
    # ================================================================
    # Arena perimeter walls (DS3: circular ruined wall ring)
    fill_tiles(chunk, TILE_WALL, 73, 47, 78, 55)      # NW wall
    fill_tiles(chunk, TILE_WALL, 129, 47, 134, 55)    # NE wall
    fill_tiles(chunk, TILE_WALL, 73, 84, 78, 92)      # SW wall
    fill_tiles(chunk, TILE_WALL, 129, 84, 134, 92)    # SE wall
    fill_tiles(chunk, TILE_WALL, 73, 47, 134, 50)     # North wall
    fill_tiles(chunk, TILE_WALL, 73, 89, 134, 92)     # South wall
    # Broken throne remnants (DS3: thrones of the Lords of Cinder around arena)
    fill_tiles(chunk, TILE_WALL, 80, 52, 82, 55)      # Throne 1
    fill_tiles(chunk, TILE_WALL, 88, 50, 90, 53)      # Throne 2
    fill_tiles(chunk, TILE_WALL, 117, 50, 119, 53)    # Throne 3
    fill_tiles(chunk, TILE_WALL, 125, 52, 127, 55)    # Throne 4
    fill_tiles(chunk, TILE_WALL, 80, 84, 82, 87)      # Throne 5
    fill_tiles(chunk, TILE_WALL, 125, 84, 127, 87)    # Throne 6
    # Broken column stumps (DS3: stone pillars ringing the arena)
    fill_tiles(chunk, TILE_WALL, 76, 60, 77, 63)
    fill_tiles(chunk, TILE_WALL, 130, 60, 131, 63)
    fill_tiles(chunk, TILE_WALL, 76, 74, 77, 77)
    fill_tiles(chunk, TILE_WALL, 130, 74, 131, 77)
    fill_tiles(chunk, TILE_WALL, 84, 51, 85, 53)
    fill_tiles(chunk, TILE_WALL, 122, 51, 123, 53)
    fill_tiles(chunk, TILE_WALL, 84, 86, 85, 88)
    fill_tiles(chunk, TILE_WALL, 122, 86, 123, 88)
    # Ash mound clusters (DS3: ash piles around the arena floor)
    fill_tiles(chunk, TILE_WALL, 92, 56, 94, 58)
    fill_tiles(chunk, TILE_WALL, 113, 56, 115, 58)
    fill_tiles(chunk, TILE_WALL, 92, 80, 94, 82)
    fill_tiles(chunk, TILE_WALL, 113, 80, 115, 82)
    # First Flame altar ring (DS3: stone ring around the flame altar)
    # Center is at tile (99,75) approximately
    fill_tiles(chunk, TILE_WALL, 93, 68, 95, 72)      # Altar NW
    fill_tiles(chunk, TILE_WALL, 112, 68, 114, 72)    # Altar NE
    fill_tiles(chunk, TILE_WALL, 93, 78, 95, 82)      # Altar SW
    fill_tiles(chunk, TILE_WALL, 112, 78, 114, 82)    # Altar SE

    # ================================================================
    # 5. CONNECTION CORRIDORS -- carved paths between sections
    # DS3: the Kiln is a linear descent; each area connects to the next
    #      via narrow ash corridors with twisted metal debris.
    # ================================================================
    # Flameless Shrine -> Ashen Ruins (east-northeast)
    fill_tiles(chunk, TILE_GROUND, 50, 132, 100, 142)
    # Ashen Ruins -> Ashen Wasteland (north)
    fill_tiles(chunk, TILE_GROUND, 90, 125, 110, 135)
    # Ashen Wasteland -> First Flame Arena (north)
    fill_tiles(chunk, TILE_GROUND, 90, 90, 115, 95)

    # ================================================================
    # 6. ENTRY CORRIDOR -- narrow ash path from fog gate to shrine
    # DS3: the player enters through fog into a narrow ash-covered passage
    #      leading to the Flameless Shrine interior.
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 34, 143, 50, 152)

    # ================================================================
    # FINALIZE -- apply doc terrain and return
    # ================================================================
    spawn_px, spawn_py = 620, 2200  # Flameless Shrine bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("KilnOfTheFirstFlame"))

    return finalize_map("KilnOfTheFirstFlame", chunk, entities, spawn_px, spawn_py)
