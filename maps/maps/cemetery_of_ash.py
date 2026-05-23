from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_cemetery_of_ash():
    """Cemetery of Ash — DS3-faithful terrain.

    Tutorial area: player wakes in coffin at bottom, fights through ash-covered
    cemetery with dense tombstones, finds Ashen Estus at broken fountain,
    reaches bonfire clearing, descends through Gundyr approach arch into
    the boss arena, then exits north to Firelink Shrine.

    JSON doc is authoritative for entity positions.
    """
    chunk = new_chunk(192, 256)

    # ================================================================
    # 1. ASHEN COFFIN — player start (bottom of map)
    # DS3: stone coffin in small alcove, player wakes here
    # Section: x=360,y=3540 → tiles (22,221)-(54,243)
    # ================================================================
    # Coffin alcove walls
    fill_tiles(chunk, TILE_WALL, 22, 221, 24, 243)   # Left wall
    fill_tiles(chunk, TILE_WALL, 52, 221, 54, 243)   # Right wall
    fill_tiles(chunk, TILE_WALL, 22, 241, 54, 243)   # South wall
    fill_tiles(chunk, TILE_WALL, 22, 221, 30, 223)   # North wall left
    fill_tiles(chunk, TILE_WALL, 46, 221, 54, 223)   # North wall right

    # ================================================================
    # 2. CEMETERY PATH — narrow path through graves
    # DS3: winding path with dense tombstones, first hollow ambush
    # Section: x=780,y=3300 → tiles (48,206)-(95,232)
    # ================================================================
    # Path boundary walls (DS3: cliff faces and cemetery walls)
    fill_tiles(chunk, TILE_WALL, 48, 206, 50, 220)   # NW wall
    fill_tiles(chunk, TILE_WALL, 48, 228, 50, 232)   # SW wall
    fill_tiles(chunk, TILE_WALL, 91, 206, 95, 215)   # NE wall
    fill_tiles(chunk, TILE_WALL, 91, 225, 95, 232)   # SE wall
    # Tombstone rows (DS3: densely packed graves)
    fill_tiles(chunk, TILE_WALL, 55, 210, 56, 212)
    fill_tiles(chunk, TILE_WALL, 62, 214, 63, 216)
    fill_tiles(chunk, TILE_WALL, 70, 210, 71, 212)
    fill_tiles(chunk, TILE_WALL, 78, 216, 79, 218)
    fill_tiles(chunk, TILE_WALL, 58, 224, 59, 226)
    fill_tiles(chunk, TILE_WALL, 68, 222, 69, 224)
    fill_tiles(chunk, TILE_WALL, 80, 224, 81, 226)
    # Hollow ambush stones (DS3: hollows hide behind graves)
    fill_tiles(chunk, TILE_WALL, 52, 218, 53, 219)
    fill_tiles(chunk, TILE_WALL, 85, 218, 86, 219)

    # ================================================================
    # 3. ASHEN ESTUS FOUNTAIN — broken fountain clearing
    # DS3: Ashen Estus Flask at broken stone fountain
    # Section: x=1280,y=2920 → tiles (80,182)-(118,211)
    # ================================================================
    # Clearing boundary walls (DS3: ruined walls around fountain)
    fill_tiles(chunk, TILE_WALL, 80, 182, 82, 195)   # NW wall
    fill_tiles(chunk, TILE_WALL, 114, 182, 118, 195)  # NE wall
    fill_tiles(chunk, TILE_WALL, 80, 200, 82, 211)   # SW wall
    fill_tiles(chunk, TILE_WALL, 114, 200, 118, 211)  # SE wall
    # Broken fountain (DS3: stone fountain with estus)
    fill_tiles(chunk, TILE_WALL, 96, 193, 100, 197)   # Fountain base
    # Stair stones (DS3: crumbling stairs)
    fill_tiles(chunk, TILE_WALL, 88, 186, 89, 188)
    fill_tiles(chunk, TILE_WALL, 108, 186, 109, 188)
    fill_tiles(chunk, TILE_WALL, 92, 204, 93, 206)
    fill_tiles(chunk, TILE_WALL, 104, 204, 105, 206)

    # ================================================================
    # 4. CRYSTAL LIZARD RAVINE — side path
    # DS3: narrow water channel with Crystal Lizard
    # Section: x=1740,y=2600 → tiles (108,162)-(166,184)
    # ================================================================
    # Ravine walls (DS3: narrow channel between rock walls)
    fill_tiles(chunk, TILE_WALL, 108, 162, 110, 175)  # NW wall
    fill_tiles(chunk, TILE_WALL, 162, 162, 166, 175)  # NE wall
    fill_tiles(chunk, TILE_WALL, 108, 180, 110, 184)  # SW wall
    fill_tiles(chunk, TILE_WALL, 162, 180, 166, 184)  # SE wall
    # Rock outcrops in channel (DS3: rocks in the water)
    fill_tiles(chunk, TILE_WALL, 120, 170, 121, 172)
    fill_tiles(chunk, TILE_WALL, 138, 168, 139, 170)
    fill_tiles(chunk, TILE_WALL, 150, 172, 151, 174)

    # ================================================================
    # 5. BONFIRE CLEARING — Cemetery of Ash bonfire
    # DS3: bonfire beside dead tree, clearing midway through area
    # Section: x=1120,y=2300 → tiles (70,143)-(117,175)
    # ================================================================
    # Clearing walls (DS3: open area bounded by cliffs)
    fill_tiles(chunk, TILE_WALL, 70, 143, 72, 155)   # NW wall
    fill_tiles(chunk, TILE_WALL, 113, 143, 117, 155)  # NE wall
    fill_tiles(chunk, TILE_WALL, 70, 170, 72, 175)   # SW wall
    fill_tiles(chunk, TILE_WALL, 113, 170, 117, 175)  # SE wall
    # Dead tree (DS3: dead tree beside bonfire)
    fill_tiles(chunk, TILE_WALL, 88, 155, 90, 160)   # Tree trunk
    # Tombstones near clearing
    fill_tiles(chunk, TILE_WALL, 76, 148, 77, 150)
    fill_tiles(chunk, TILE_WALL, 84, 165, 85, 167)
    fill_tiles(chunk, TILE_WALL, 106, 150, 107, 152)
    fill_tiles(chunk, TILE_WALL, 100, 168, 101, 170)

    # ================================================================
    # 6. FIREBOMB CLIFF — side path with cliff edge
    # DS3: narrow cliff path, shield hollow, crossbow hollow, 5 firebombs
    # Section: x=640,y=2140 → tiles (40,133)-(88,155)
    # ================================================================
    # Cliff walls (DS3: narrow path along cliff edge)
    fill_tiles(chunk, TILE_WALL, 40, 133, 42, 145)   # NW cliff wall
    fill_tiles(chunk, TILE_WALL, 84, 133, 88, 145)   # NE cliff wall
    fill_tiles(chunk, TILE_WALL, 40, 150, 42, 155)   # SW wall
    fill_tiles(chunk, TILE_WALL, 84, 150, 88, 155)   # SE wall
    # Cliff edge stones (DS3: sheer drop on one side)
    fill_tiles(chunk, TILE_WALL, 52, 135, 53, 136)
    fill_tiles(chunk, TILE_WALL, 66, 135, 67, 136)
    fill_tiles(chunk, TILE_WALL, 56, 150, 57, 152)
    fill_tiles(chunk, TILE_WALL, 70, 148, 71, 150)

    # ================================================================
    # 7. GUNDYR APPROACH — stone arch passage
    # DS3: twin-torch archway leading to boss arena
    # Section: x=1280,y=1840 → tiles (80,115)-(112,141)
    # ================================================================
    # Arch passage walls (DS3: narrow stone arch)
    fill_tiles(chunk, TILE_WALL, 80, 115, 82, 125)   # Left arch wall
    fill_tiles(chunk, TILE_WALL, 108, 115, 112, 125)  # Right arch wall
    fill_tiles(chunk, TILE_WALL, 80, 115, 95, 117)   # North wall left
    fill_tiles(chunk, TILE_WALL, 100, 115, 112, 117)  # North wall right
    # Twin torch pillars (DS3: two torch sconces)
    fill_tiles(chunk, TILE_WALL, 88, 120, 90, 125)   # Left torch pillar
    fill_tiles(chunk, TILE_WALL, 104, 120, 106, 125)  # Right torch pillar
    # Approach tombstones (DS3: graves line the approach)
    fill_tiles(chunk, TILE_WALL, 84, 130, 85, 132)
    fill_tiles(chunk, TILE_WALL, 92, 128, 93, 130)
    fill_tiles(chunk, TILE_WALL, 100, 132, 101, 134)
    fill_tiles(chunk, TILE_WALL, 108, 128, 109, 130)

    # ================================================================
    # 8. IUDEX GUNDYR ARENA — large boss arena
    # DS3: open cemetery arena with reflecting pool, coiled sword
    # Section: x=860,y=980 → tiles (53,61)-(137,109)
    # ================================================================
    # Arena perimeter walls (DS3: crumbling cemetery walls around arena)
    fill_tiles(chunk, TILE_WALL, 53, 61, 58, 65)     # NW wall
    fill_tiles(chunk, TILE_WALL, 130, 61, 137, 65)   # NE wall
    fill_tiles(chunk, TILE_WALL, 53, 105, 58, 109)   # SW wall
    fill_tiles(chunk, TILE_WALL, 130, 105, 137, 109)  # SE wall
    # Crumbling wall sections (DS3: partial walls around arena)
    fill_tiles(chunk, TILE_WALL, 65, 62, 68, 64)
    fill_tiles(chunk, TILE_WALL, 120, 62, 123, 64)
    fill_tiles(chunk, TILE_WALL, 56, 80, 58, 85)
    fill_tiles(chunk, TILE_WALL, 132, 80, 134, 85)
    fill_tiles(chunk, TILE_WALL, 65, 106, 68, 108)
    fill_tiles(chunk, TILE_WALL, 120, 106, 123, 108)
    # Tombstone clusters in arena (DS3: graves scattered in arena)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 70)
    fill_tiles(chunk, TILE_WALL, 115, 68, 116, 70)
    fill_tiles(chunk, TILE_WALL, 75, 100, 76, 102)
    fill_tiles(chunk, TILE_WALL, 110, 100, 111, 102)
    # Coiled sword crater (DS3: sword in center of arena)
    fill_tiles(chunk, TILE_GROUND, 90, 82, 98, 90)

    # ================================================================
    # 9. PATH TO FIRELINK SHRINE — exit north
    # DS3: door opens post-boss, path to Firelink
    # Section: x=1380,y=520 → tiles (86,32)-(118,67)
    # ================================================================
    # Exit passage walls (DS3: narrow mountain path)
    fill_tiles(chunk, TILE_WALL, 86, 32, 88, 50)
    fill_tiles(chunk, TILE_WALL, 114, 32, 118, 50)
    fill_tiles(chunk, TILE_WALL, 86, 32, 100, 34)
    fill_tiles(chunk, TILE_WALL, 108, 32, 118, 34)
    # Mountain cliff walls (DS3: narrow path along cliff)
    fill_tiles(chunk, TILE_WALL, 92, 42, 93, 44)
    fill_tiles(chunk, TILE_WALL, 110, 42, 111, 44)

    # ================================================================
    # CONNECTION CORRIDORS — DS3 route paths
    # ================================================================
    # Coffin → Cemetery Path (north-east)
    fill_tiles(chunk, TILE_GROUND, 38, 220, 65, 235)
    # Cemetery Path → Ashen Estus Fountain (north-east)
    fill_tiles(chunk, TILE_GROUND, 70, 205, 95, 195)
    # Ashen Estus → Crystal Lizard Ravine (east)
    fill_tiles(chunk, TILE_GROUND, 108, 190, 125, 175)
    # Ashen Estus → Bonfire Clearing (north)
    fill_tiles(chunk, TILE_GROUND, 85, 180, 100, 160)
    # Bonfire Clearing → Firebomb Cliff (west)
    fill_tiles(chunk, TILE_GROUND, 60, 145, 80, 155)
    # Bonfire Clearing → Gundyr Approach (north)
    fill_tiles(chunk, TILE_GROUND, 85, 145, 100, 130)
    # Gundyr Approach → Gundyr Arena (north)
    fill_tiles(chunk, TILE_GROUND, 85, 110, 100, 95)
    # Gundyr Arena → Firelink Path (north)
    fill_tiles(chunk, TILE_GROUND, 88, 65, 110, 55)

    # ================================================================
    # FINALIZE
    # ================================================================
    spawn_px, spawn_py = 360, 3540  # Ashen Coffin (JSON doc first bonfire)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("CemeteryOfAsh"))

    # Gundyr's closed door — wall blocking north arena exit
    fill_tiles(chunk, TILE_WALL, 94, 62, 110, 63)

    return finalize_map("CemeteryOfAsh", chunk, entities, spawn_px, spawn_py)
