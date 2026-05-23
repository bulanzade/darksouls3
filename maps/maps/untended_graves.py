from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_untended_graves():
    """Untended Graves -- DS3-faithful terrain.

    Dark mirror of Cemetery of Ash: player arrives via portal behind Oceiros,
    descends through dark coffin entry, dark cemetery path with tombstones,
    reaches Untended Graves bonfire, enters Champion Gundyr approach,
    fights Champion Gundyr in arena, continues past Black Knight courtyard,
    through Dark Firelink exterior into Dark Firelink Shrine itself.
    Perpetually dark, no sunlight.

    JSON doc is authoritative for entity positions.
    """
    chunk = new_chunk(320, 288)

    # ================================================================
    # 1. DARK CEMETERY ENTRY — coffin alcove (NW corner)
    # DS3: small dark stone chamber where player wakes in coffin
    # Section: x=480,y=480,w=760,h=560 -> tiles (30,30)-(77,65)
    # ================================================================
    # Coffin alcove walls (DS3: stone coffin in small enclosed room)
    fill_tiles(chunk, TILE_WALL, 30, 30, 32, 55)   # West wall
    fill_tiles(chunk, TILE_WALL, 75, 30, 77, 55)   # East wall
    fill_tiles(chunk, TILE_WALL, 30, 60, 77, 65)   # South wall
    fill_tiles(chunk, TILE_WALL, 30, 30, 42, 32)   # North wall left
    fill_tiles(chunk, TILE_WALL, 65, 30, 77, 32)   # North wall right
    # Coffin stone in alcove (DS3: stone coffin you wake in)
    fill_tiles(chunk, TILE_WALL, 45, 40, 48, 43)
    # Broken wall rubble (DS3: crumbling entry chamber)
    fill_tiles(chunk, TILE_WALL, 55, 45, 57, 48)

    # ================================================================
    # 2. DARK CEMETERY PATH — winding path through dark graves
    # DS3: narrow path with dense tombstones, ash-covered ground
    # Section: x=1040,y=900,w=900,h=640 -> tiles (65,56)-(121,96)
    # ================================================================
    # Path boundary walls (DS3: cliff faces and ruined cemetery walls)
    fill_tiles(chunk, TILE_WALL, 65, 56, 67, 72)   # NW boundary wall
    fill_tiles(chunk, TILE_WALL, 118, 56, 121, 72)  # NE boundary wall
    fill_tiles(chunk, TILE_WALL, 65, 88, 67, 96)    # SW boundary wall
    fill_tiles(chunk, TILE_WALL, 118, 88, 121, 96)  # SE boundary wall
    # Dense tombstone rows (DS3: dark cemetery packed with headstones)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 64)
    fill_tiles(chunk, TILE_WALL, 80, 66, 81, 68)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 64)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 72)
    fill_tiles(chunk, TILE_WALL, 104, 64, 105, 66)
    fill_tiles(chunk, TILE_WALL, 112, 70, 113, 72)
    fill_tiles(chunk, TILE_WALL, 76, 78, 77, 80)
    fill_tiles(chunk, TILE_WALL, 84, 82, 85, 84)
    fill_tiles(chunk, TILE_WALL, 92, 76, 93, 78)
    fill_tiles(chunk, TILE_WALL, 100, 84, 101, 86)
    fill_tiles(chunk, TILE_WALL, 108, 78, 109, 80)
    # Broken walls (DS3: crumbling cemetery structures)
    fill_tiles(chunk, TILE_WALL, 85, 58, 87, 60)
    fill_tiles(chunk, TILE_WALL, 106, 66, 108, 68)

    # ================================================================
    # 3. UNTENDED GRAVES BONFIRE — bonfire clearing
    # DS3: bonfire in small clearing amid dark graves
    # Section: x=1480,y=1420,w=860,h=620 -> tiles (92,88)-(146,127)
    # ================================================================
    # Clearing boundary walls (DS3: ruined walls around bonfire clearing)
    fill_tiles(chunk, TILE_WALL, 92, 88, 94, 105)   # NW wall
    fill_tiles(chunk, TILE_WALL, 143, 88, 146, 105)  # NE wall
    fill_tiles(chunk, TILE_WALL, 92, 118, 94, 127)   # SW wall
    fill_tiles(chunk, TILE_WALL, 143, 118, 146, 127)  # SE wall
    # Tombstones near clearing (DS3: graves surrounding bonfire)
    fill_tiles(chunk, TILE_WALL, 100, 94, 101, 96)
    fill_tiles(chunk, TILE_WALL, 115, 92, 116, 94)
    fill_tiles(chunk, TILE_WALL, 130, 96, 131, 98)
    fill_tiles(chunk, TILE_WALL, 105, 115, 106, 117)
    fill_tiles(chunk, TILE_WALL, 120, 118, 121, 120)
    fill_tiles(chunk, TILE_WALL, 135, 112, 136, 114)
    # Broken wall ruins (DS3: crumbling structures near bonfire)
    fill_tiles(chunk, TILE_WALL, 97, 92, 99, 95)
    fill_tiles(chunk, TILE_WALL, 137, 108, 139, 111)

    # ================================================================
    # 4. CHAMPION GUNDYR APPROACH — stone arch passage
    # DS3: dark version of Gundyr approach with twin torch pillars
    # Section: x=2020,y=1840,w=760,h=480 -> tiles (126,115)-(173,145)
    # ================================================================
    # Arch passage walls (DS3: narrow stone arch leading to arena)
    fill_tiles(chunk, TILE_WALL, 126, 115, 128, 130)  # Left arch wall
    fill_tiles(chunk, TILE_WALL, 170, 115, 173, 130)  # Right arch wall
    fill_tiles(chunk, TILE_WALL, 126, 115, 140, 117)  # North wall left
    fill_tiles(chunk, TILE_WALL, 160, 115, 173, 117)  # North wall right
    # Twin torch pillars (DS3: dark stone pillars flanking approach)
    fill_tiles(chunk, TILE_WALL, 136, 120, 138, 126)  # Left pillar
    fill_tiles(chunk, TILE_WALL, 162, 120, 164, 126)  # Right pillar
    # Approach tombstones (DS3: dark graves lining the path to arena)
    fill_tiles(chunk, TILE_WALL, 132, 132, 133, 134)
    fill_tiles(chunk, TILE_WALL, 142, 128, 143, 130)
    fill_tiles(chunk, TILE_WALL, 152, 136, 153, 138)
    fill_tiles(chunk, TILE_WALL, 162, 130, 163, 132)
    fill_tiles(chunk, TILE_WALL, 148, 140, 149, 142)
    fill_tiles(chunk, TILE_WALL, 168, 138, 169, 140)

    # ================================================================
    # 5. CHAMPION GUNDYR ARENA — large boss arena
    # DS3: dark version of Iudex Gundyr arena, open cemetery with ash
    # Section: x=2220,y=1980,w=900,h=700 -> tiles (138,123)-(194,166)
    # ================================================================
    # Arena perimeter walls (DS3: crumbling cemetery walls around arena)
    fill_tiles(chunk, TILE_WALL, 138, 123, 142, 127)  # NW wall
    fill_tiles(chunk, TILE_WALL, 188, 123, 194, 127)  # NE wall
    fill_tiles(chunk, TILE_WALL, 138, 160, 142, 166)  # SW wall
    fill_tiles(chunk, TILE_WALL, 188, 160, 194, 166)  # SE wall
    # Crumbling wall sections (DS3: partial walls around arena perimeter)
    fill_tiles(chunk, TILE_WALL, 150, 124, 153, 126)
    fill_tiles(chunk, TILE_WALL, 178, 124, 181, 126)
    fill_tiles(chunk, TILE_WALL, 140, 140, 142, 146)
    fill_tiles(chunk, TILE_WALL, 190, 140, 192, 146)
    fill_tiles(chunk, TILE_WALL, 150, 162, 153, 164)
    fill_tiles(chunk, TILE_WALL, 178, 162, 181, 164)
    # Arena tombstone clusters (DS3: dark graves scattered in arena)
    fill_tiles(chunk, TILE_WALL, 155, 130, 156, 132)
    fill_tiles(chunk, TILE_WALL, 175, 130, 176, 132)
    fill_tiles(chunk, TILE_WALL, 160, 155, 161, 157)
    fill_tiles(chunk, TILE_WALL, 172, 155, 173, 157)
    # Dark arena center — open fighting space (DS3: open area where Gundyr stands)
    fill_tiles(chunk, TILE_GROUND, 155, 135, 175, 155)

    # ================================================================
    # 6. BLACK KNIGHT COURTYARD — dark courtyard beyond arena
    # DS3: ash-covered courtyard patrolled by Black Knights
    # Section: x=2200,y=2600,w=600,h=500 -> tiles (137,162)-(175,193)
    # ================================================================
    # Courtyard boundary walls (DS3: dark stone walls enclosing courtyard)
    fill_tiles(chunk, TILE_WALL, 137, 162, 139, 178)  # NW wall
    fill_tiles(chunk, TILE_WALL, 172, 162, 175, 178)  # NE wall
    fill_tiles(chunk, TILE_WALL, 137, 188, 139, 193)  # SW wall
    fill_tiles(chunk, TILE_WALL, 172, 188, 175, 193)  # SE wall
    # Broken pillars (DS3: dark stone pillars in ruined courtyard)
    fill_tiles(chunk, TILE_WALL, 148, 170, 150, 174)  # Left broken pillar
    fill_tiles(chunk, TILE_WALL, 162, 170, 164, 174)  # Right broken pillar
    # Ash-covered debris (DS3: ash drifts and rubble)
    fill_tiles(chunk, TILE_WALL, 144, 180, 146, 183)
    fill_tiles(chunk, TILE_WALL, 165, 178, 167, 181)

    # ================================================================
    # 7. DARK FIRELINK EXTERIOR — path to dark shrine
    # DS3: dark stone path with dead trees, collapsing walls
    # Section: x=2600,y=2700,w=700,h=500 -> tiles (162,168)-(206,199)
    # ================================================================
    # Path boundary walls (DS3: cliff walls along approach to dark shrine)
    fill_tiles(chunk, TILE_WALL, 162, 168, 164, 182)  # NW wall
    fill_tiles(chunk, TILE_WALL, 203, 168, 206, 182)  # NE wall
    fill_tiles(chunk, TILE_WALL, 162, 194, 164, 199)  # SW wall
    fill_tiles(chunk, TILE_WALL, 203, 194, 206, 199)  # SE wall
    # Dead trees (DS3: withered trees in perpetual darkness)
    fill_tiles(chunk, TILE_WALL, 172, 176, 174, 180)  # Dead tree 1
    fill_tiles(chunk, TILE_WALL, 192, 178, 194, 182)  # Dead tree 2
    # Collapsing wall (DS3: ruined wall section)
    fill_tiles(chunk, TILE_WALL, 182, 172, 185, 175)

    # ================================================================
    # 8. DARK FIRELINK SHRINE — dark mirror of Firelink Shrine
    # DS3: exact dark copy of Firelink Shrine with empty thrones, no fire
    # Section: x=2500,y=2840,w=1080,h=760 -> tiles (156,177)-(223,224)
    # ================================================================
    # Shrine perimeter walls (DS3: stone walls of dark Firelink)
    fill_tiles(chunk, TILE_WALL, 156, 177, 158, 200)  # West outer wall
    fill_tiles(chunk, TILE_WALL, 220, 177, 223, 200)  # East outer wall
    fill_tiles(chunk, TILE_WALL, 156, 220, 158, 224)  # SW wall
    fill_tiles(chunk, TILE_WALL, 220, 220, 223, 224)  # SE wall
    fill_tiles(chunk, TILE_WALL, 156, 177, 175, 179)  # North wall left
    fill_tiles(chunk, TILE_WALL, 204, 177, 223, 179)  # North wall right
    # Shrine interior walls (DS3: dark version of Firelink interior)
    fill_tiles(chunk, TILE_WALL, 167, 185, 169, 191)  # Left shrine wall
    fill_tiles(chunk, TILE_WALL, 210, 185, 212, 191)  # Right shrine wall
    # Coiled sword stump (DS3: unlit coiled sword in dark Firelink)
    fill_tiles(chunk, TILE_WALL, 178, 192, 180, 194)
    # Throne alcove walls (DS3: 5 empty Lord of Cinder thrones, dark)
    fill_tiles(chunk, TILE_WALL, 162, 200, 164, 205)  # Throne 1
    fill_tiles(chunk, TILE_WALL, 170, 198, 172, 203)  # Throne 2
    fill_tiles(chunk, TILE_WALL, 186, 200, 188, 205)  # Throne 3
    fill_tiles(chunk, TILE_WALL, 194, 198, 196, 203)  # Throne 4
    fill_tiles(chunk, TILE_WALL, 202, 200, 204, 205)  # Throne 5
    # Dark shrine entrance pillars (DS3: stone pillars flanking entrance)
    fill_tiles(chunk, TILE_WALL, 176, 206, 178, 212)  # Left entrance pillar
    fill_tiles(chunk, TILE_WALL, 201, 206, 203, 212)  # Right entrance pillar
    # Shrine Handmaid alcove (DS3: dark corner where Handmaid works)
    fill_tiles(chunk, TILE_WALL, 192, 210, 194, 215)
    # Dark well (DS3: dark version of Firelink well)
    fill_tiles(chunk, TILE_WALL, 183, 215, 187, 218)

    # ================================================================
    # CONNECTION CORRIDORS — DS3 route paths
    # ================================================================
    # Dark Cemetery Entry -> Dark Cemetery Path (south-east)
    fill_tiles(chunk, TILE_GROUND, 55, 48, 75, 65)
    # Dark Cemetery Path -> Untended Graves Bonfire (south-east)
    fill_tiles(chunk, TILE_GROUND, 100, 80, 115, 100)
    # Untended Graves Bonfire -> Champion Gundyr Approach (south-east)
    fill_tiles(chunk, TILE_GROUND, 130, 110, 145, 125)
    # Champion Gundyr Approach -> Champion Gundyr Arena (south)
    fill_tiles(chunk, TILE_GROUND, 148, 130, 165, 140)
    # Champion Gundyr Arena -> Black Knight Courtyard (south)
    fill_tiles(chunk, TILE_GROUND, 150, 155, 168, 170)
    # Black Knight Courtyard -> Dark Firelink Exterior (south-east)
    fill_tiles(chunk, TILE_GROUND, 155, 180, 175, 185)
    # Dark Firelink Exterior -> Dark Firelink Shrine (south)
    fill_tiles(chunk, TILE_GROUND, 170, 190, 200, 200)
    # Entry shortcut corridor (north path)
    fill_tiles(chunk, TILE_GROUND, 40, 38, 60, 50)

    # ================================================================
    # FINALIZE
    # ================================================================
    spawn_px, spawn_py = 700, 720  # Untended Graves bonfire (JSON doc first bonfire)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("UntendedGraves"))

    return finalize_map("UntendedGraves", chunk, entities, spawn_px, spawn_py)
