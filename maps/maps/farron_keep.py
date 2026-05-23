from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_corridor, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)


# Map: 5120x4608 px = 320x288 tiles

# Bonfire positions (pixels)
BF_FARRON_KEEP = (620, 760)
BF_KEEP_RUINS = (2400, 2140)
BF_KEEP_PERIMETER = (3860, 2720)
BF_OLD_WOLF = (1680, 1180)
BF_ABYSS_WATCHERS = (4400, 3440)

# Player spawn at first bonfire
SPAWN_PX, SPAWN_PY = BF_FARRON_KEEP


def make_farron_keep():
    """Farron Keep - sprawling poison swamp with three flame altars.
    DS3 layout: entry highland -> vast poison swamp with torch islands ->
    Keep Ruins center -> Old Wolf tower -> Abyss Watchers grand hall.
    Map size: 5120x4608 (320x288 tiles).
    """

    chunk = new_chunk(320, 288)

    # ================================================================
    # STEP 1: Fill the large central swamp area with POISON
    # DS3: The vast majority of Farron Keep is waist-deep poison swamp.
    #      Only raised stone islands, ruins, and torch platforms are safe.
    # ================================================================

    # Main poison swamp basin - covers the center and south of the map
    fill_tiles(chunk, TILE_POISON, 50, 55, 280, 200)

    # Extend poison channels toward entry area (shallow poison at edges)
    fill_tiles(chunk, TILE_POISON, 30, 70, 55, 110)
    fill_tiles(chunk, TILE_POISON, 55, 85, 80, 130)

    # Southeast poison extension (toward Keep Perimeter)
    fill_tiles(chunk, TILE_POISON, 200, 140, 270, 190)

    # South poison pool (deep swamp near Old Wolf area)
    fill_tiles(chunk, TILE_POISON, 85, 150, 200, 210)

    # ================================================================
    # STEP 2: Farron Keep Entry (doc: x=360,y=520 -> tx=22,ty=32)
    # DS3: Stone steps descending from Road of Sacrifices into the swamp.
    #      A narrow stone causeway with broken walls, first bonfire here.
    #      High ground above the poison swamp, Ghru and slugs nearby.
    # ================================================================

    # Entry highland - solid ground platform
    fill_tiles(chunk, TILE_GROUND, 18, 30, 52, 60)

    # Stone steps descending into the swamp (narrow walkway going south)
    fill_tiles(chunk, TILE_GROUND, 32, 55, 42, 75)

    # Broken stone walls at entry (DS3: ruined wall fragments)
    fill_tiles(chunk, TILE_WALL, 20, 33, 26, 38)
    fill_tiles(chunk, TILE_WALL, 42, 35, 48, 39)
    fill_tiles(chunk, TILE_WALL, 28, 48, 30, 54)

    # Entry stone step obstacles
    fill_tiles(chunk, TILE_WALL, 34, 40, 36, 43)
    fill_tiles(chunk, TILE_WALL, 38, 50, 40, 53)

    # ================================================================
    # STEP 3: First Flame Tower (doc: x=1160,y=860 -> tx=72,ty=53)
    # DS3: One of three stone platforms with a flame altar that must be lit.
    #      Surrounded by poison, accessed by wading through toxic water.
    #      Ghru swarm on and around this platform.
    # ================================================================

    # Platform island - raised ground above the poison
    fill_tiles(chunk, TILE_GROUND, 68, 50, 105, 80)

    # Stone walls forming the ruined tower base
    fill_tiles(chunk, TILE_WALL, 70, 52, 73, 56)
    fill_tiles(chunk, TILE_WALL, 98, 72, 102, 76)
    fill_tiles(chunk, TILE_WALL, 68, 50, 70, 52)
    fill_tiles(chunk, TILE_WALL, 102, 50, 105, 53)

    # Flame altar structure in center (DS3: fire basin on stone pedestal)
    fill_tiles(chunk, TILE_WALL, 82, 62, 86, 66)

    # Rubble around the platform edge
    fill_tiles(chunk, TILE_WALL, 90, 55, 93, 58)
    fill_tiles(chunk, TILE_WALL, 74, 72, 77, 75)

    # Shallow poison path from entry to this island
    fill_tiles(chunk, TILE_POISON, 42, 60, 70, 70)

    # ================================================================
    # STEP 4: Old Wolf Tower (doc: x=1500,y=420 -> tx=93,ty=26)
    # DS3: Tall tower ruin in the north area, accessed via ladder.
    #      Covenant area (Watchdogs of Farron), Old Wolf statue inside.
    #      Connected by a narrow ridge above the swamp.
    # ================================================================

    # Tower ground platform (raised above swamp)
    fill_tiles(chunk, TILE_GROUND, 88, 22, 130, 65)

    # Tower walls - thick stone structure (DS3: massive tower)
    fill_tiles(chunk, TILE_WALL, 90, 24, 93, 28)
    fill_tiles(chunk, TILE_WALL, 124, 58, 128, 63)
    fill_tiles(chunk, TILE_WALL, 88, 22, 92, 26)
    fill_tiles(chunk, TILE_WALL, 126, 22, 130, 26)

    # Interior wall dividers (DS3: multi-level tower interior)
    fill_tiles(chunk, TILE_WALL, 100, 35, 104, 40)
    fill_tiles(chunk, TILE_WALL, 112, 48, 116, 54)

    # Ladder access structure (narrow wall gap)
    fill_tiles(chunk, TILE_WALL, 95, 30, 98, 32)
    fill_tiles(chunk, TILE_WALL, 118, 30, 121, 33)

    # Connection corridor from entry to Old Wolf area
    fill_tiles(chunk, TILE_GROUND, 50, 35, 90, 50)

    # ================================================================
    # STEP 5: Central Swamp (doc: x=1700,y=1540 -> tx=106,ty=96)
    # DS3: The vast open poison swamp. Deep toxic water with Ghru hordes
    #      wading through, Elder Ghru on islands, scattered ruin fragments.
    #      This is the core traversal area connecting all sections.
    # ================================================================

    # Central swamp is already POISON from step 1.
    # Add scattered safe-ground islands within the swamp (DS3: small raised patches)
    fill_tiles(chunk, TILE_GROUND, 110, 90, 130, 105)
    fill_tiles(chunk, TILE_GROUND, 135, 100, 155, 118)
    fill_tiles(chunk, TILE_GROUND, 160, 90, 175, 108)

    # Sunken ruin walls poking through the swamp (DS3: crumbled structures)
    fill_tiles(chunk, TILE_WALL, 115, 95, 118, 98)
    fill_tiles(chunk, TILE_WALL, 140, 105, 143, 108)
    fill_tiles(chunk, TILE_WALL, 165, 95, 168, 99)

    # Submerged debris (DS3: scattered stones visible in poison water)
    fill_tiles(chunk, TILE_WALL, 120, 100, 121, 102)
    fill_tiles(chunk, TILE_WALL, 148, 112, 150, 114)
    fill_tiles(chunk, TILE_WALL, 170, 100, 172, 102)

    # ================================================================
    # STEP 6: Second Flame Tower (doc: x=2760,y=1220 -> tx=172,ty=76)
    # DS3: Another torch platform in the northeast of the swamp.
    #      Stone ramp leads up, Elder Ghru guards, Ghru patrol around.
    # ================================================================

    # Platform island
    fill_tiles(chunk, TILE_GROUND, 168, 72, 215, 105)

    # Stone ramp and walls (DS3: ramp leading up to flame altar)
    fill_tiles(chunk, TILE_WALL, 170, 74, 174, 78)
    fill_tiles(chunk, TILE_WALL, 208, 98, 213, 103)

    # Flame altar structure
    fill_tiles(chunk, TILE_WALL, 186, 86, 192, 92)

    # Rubble and ruin walls
    fill_tiles(chunk, TILE_WALL, 176, 82, 179, 85)
    fill_tiles(chunk, TILE_WALL, 198, 90, 201, 94)
    fill_tiles(chunk, TILE_WALL, 180, 96, 183, 100)

    # Connection from Central Swamp to Second Flame Tower
    fill_tiles(chunk, TILE_GROUND, 155, 85, 170, 95)

    # ================================================================
    # STEP 7: Third Flame Tower (doc: x=3140,y=2060 -> tx=196,ty=128)
    # DS3: The last torch platform, furthest into the swamp.
    #      Ruined structure with Darkwraith patrol zone nearby.
    # ================================================================

    # Platform island
    fill_tiles(chunk, TILE_GROUND, 192, 124, 240, 160)

    # Ruined structure walls (DS3: crumbling stone building)
    fill_tiles(chunk, TILE_WALL, 194, 126, 198, 130)
    fill_tiles(chunk, TILE_WALL, 232, 152, 237, 158)
    fill_tiles(chunk, TILE_WALL, 192, 124, 196, 128)

    # Flame altar
    fill_tiles(chunk, TILE_WALL, 210, 140, 216, 146)

    # Debris and broken walls
    fill_tiles(chunk, TILE_WALL, 200, 135, 203, 138)
    fill_tiles(chunk, TILE_WALL, 224, 148, 227, 152)
    fill_tiles(chunk, TILE_WALL, 205, 150, 208, 154)

    # Connection from Central Swamp to Third Flame Tower
    fill_tiles(chunk, TILE_GROUND, 155, 110, 195, 135)

    # ================================================================
    # STEP 8: Keep Ruins (doc: x=2260,y=2140 -> tx=141,ty=133)
    # DS3: Solid ground island with ruined walls, central bonfire hub.
    #      Large stone ruin with multiple crumbling wall sections.
    #      Nameless Knight Set, items scattered in the ruins.
    # ================================================================

    # Main ground island - largest safe area in the swamp
    fill_tiles(chunk, TILE_GROUND, 136, 128, 185, 165)

    # Ruined walls forming the keep structure (DS3: multi-room stone ruin)
    fill_tiles(chunk, TILE_WALL, 138, 130, 142, 135)
    fill_tiles(chunk, TILE_WALL, 178, 155, 183, 162)
    fill_tiles(chunk, TILE_WALL, 136, 128, 140, 132)
    fill_tiles(chunk, TILE_WALL, 180, 128, 184, 133)

    # Interior room dividers (DS3: walls dividing the ruin into sections)
    fill_tiles(chunk, TILE_WALL, 150, 138, 154, 145)
    fill_tiles(chunk, TILE_WALL, 165, 145, 170, 152)
    fill_tiles(chunk, TILE_WALL, 155, 155, 160, 162)

    # Additional ruin fragments
    fill_tiles(chunk, TILE_WALL, 144, 148, 147, 152)
    fill_tiles(chunk, TILE_WALL, 172, 135, 176, 140)

    # Connection corridor from Central Swamp to Keep Ruins
    fill_tiles(chunk, TILE_GROUND, 130, 110, 145, 130)
    fill_tiles(chunk, TILE_GROUND, 155, 118, 165, 130)

    # ================================================================
    # STEP 9: Black Knight Side Path (doc: x=3340,y=640 -> tx=208,ty=40)
    # DS3: Optional area with overgrown path, Crystal Lizards, dragon corpse.
    #      Black Knight patrols here. Off the main path to the northeast.
    # ================================================================

    # Ground area for side path
    fill_tiles(chunk, TILE_GROUND, 205, 36, 252, 68)

    # Overgrown path walls (DS3: ruined walls overgrown with vegetation)
    fill_tiles(chunk, TILE_WALL, 207, 38, 210, 42)
    fill_tiles(chunk, TILE_WALL, 244, 60, 248, 66)
    fill_tiles(chunk, TILE_WALL, 205, 36, 208, 40)

    # Scattered ruin obstacles
    fill_tiles(chunk, TILE_WALL, 220, 48, 224, 52)
    fill_tiles(chunk, TILE_WALL, 235, 42, 238, 46)
    fill_tiles(chunk, TILE_WALL, 228, 56, 232, 60)

    # Connection from Second Flame Tower to Black Knight Side Path
    fill_tiles(chunk, TILE_GROUND, 210, 68, 218, 76)

    # ================================================================
    # STEP 10: Keep Perimeter (doc: x=3580,y=2520 -> tx=223,ty=157)
    # DS3: Stone perimeter wall with Stray Demon pit, Darkwraith patrol.
    #      Ravenous Crystal Lizard here. Transition zone toward boss arena.
    # ================================================================

    # Ground area for perimeter
    fill_tiles(chunk, TILE_GROUND, 218, 153, 268, 187)

    # Stone perimeter wall (DS3: large fortification wall)
    fill_tiles(chunk, TILE_WALL, 220, 155, 225, 162)
    fill_tiles(chunk, TILE_WALL, 260, 178, 266, 185)
    fill_tiles(chunk, TILE_WALL, 218, 153, 222, 158)
    fill_tiles(chunk, TILE_WALL, 263, 153, 268, 158)

    # Stray Demon pit area - open ground within walls
    fill_tiles(chunk, TILE_WALL, 235, 165, 240, 170)
    fill_tiles(chunk, TILE_WALL, 248, 170, 253, 176)

    # Connection from Third Flame Tower to Keep Perimeter
    fill_tiles(chunk, TILE_GROUND, 236, 155, 245, 165)
    fill_tiles(chunk, TILE_GROUND, 235, 148, 225, 160)

    # ================================================================
    # STEP 11: Abyss Watchers Mausoleum (doc: x=4080,y=3180 -> tx=255,ty=198)
    # DS3: Grand stone hall with wolf crest banners.
    #      Long corridor lined with Abyss Watcher armor.
    #      Massive boss arena where the Watchers fight among themselves.
    # ================================================================

    # Grand hall ground - large boss arena
    fill_tiles(chunk, TILE_GROUND, 250, 192, 310, 240)

    # Mausoleum walls - thick stone enclosure (DS3: grand stone hall)
    fill_tiles(chunk, TILE_WALL, 252, 194, 257, 200)
    fill_tiles(chunk, TILE_WALL, 303, 232, 308, 238)
    fill_tiles(chunk, TILE_WALL, 250, 192, 255, 198)
    fill_tiles(chunk, TILE_WALL, 305, 192, 310, 198)
    fill_tiles(chunk, TILE_WALL, 250, 234, 256, 240)
    fill_tiles(chunk, TILE_WALL, 304, 234, 310, 240)

    # Grand hall pillars (DS3: massive stone columns in the boss room)
    fill_tiles(chunk, TILE_WALL, 265, 205, 268, 210)
    fill_tiles(chunk, TILE_WALL, 280, 205, 283, 210)
    fill_tiles(chunk, TILE_WALL, 295, 205, 298, 210)
    fill_tiles(chunk, TILE_WALL, 265, 222, 268, 227)
    fill_tiles(chunk, TILE_WALL, 280, 222, 283, 227)
    fill_tiles(chunk, TILE_WALL, 295, 222, 298, 227)

    # Approach corridor from Keep Perimeter (DS3: grand stone hallway)
    fill_tiles(chunk, TILE_GROUND, 240, 170, 260, 198)
    # Corridor walls (DS3: wolf-crested stone walls)
    fill_tiles(chunk, TILE_WALL, 242, 172, 246, 180)
    fill_tiles(chunk, TILE_WALL, 254, 185, 258, 195)

    # Additional corridor walls lining the approach
    fill_tiles(chunk, TILE_WALL, 238, 175, 240, 190)
    fill_tiles(chunk, TILE_WALL, 260, 180, 262, 195)

    # ================================================================
    # STEP 12: Connection corridors between major sections
    # DS3: Wading through poison between islands on narrow raised paths
    # ================================================================

    # Entry -> First Flame Tower (through shallow poison)
    fill_tiles(chunk, TILE_GROUND, 45, 55, 72, 65)

    # First Flame Tower -> Old Wolf Tower (ridge above swamp)
    fill_tiles(chunk, TILE_GROUND, 100, 50, 115, 60)

    # Old Wolf Tower -> Central Swamp (descent into poison)
    fill_tiles(chunk, TILE_GROUND, 105, 60, 120, 90)

    # Central Swamp -> Second Flame Tower
    carve_corridor(chunk, 120, 100, 185, 88, width=5)

    # Second Flame Tower -> Third Flame Tower
    carve_corridor(chunk, 200, 100, 215, 135, width=5)

    # Third Flame Tower -> Keep Ruins
    carve_corridor(chunk, 200, 145, 160, 140, width=5)

    # Keep Ruins -> Keep Perimeter
    carve_corridor(chunk, 180, 155, 230, 170, width=5)

    # Keep Perimeter -> Abyss Watchers Mausoleum
    carve_corridor(chunk, 250, 175, 275, 200, width=6)

    # ================================================================
    # STEP 13: Additional terrain detail for DS3 fidelity
    # Small island patches, scattered ruin fragments in the swamp
    # ================================================================

    # Small safe islands in the poison swamp (DS3: raised patches of ground)
    fill_tiles(chunk, TILE_GROUND, 60, 100, 68, 108)
    fill_tiles(chunk, TILE_GROUND, 85, 115, 92, 122)
    fill_tiles(chunk, TILE_GROUND, 125, 80, 132, 88)
    fill_tiles(chunk, TILE_GROUND, 180, 115, 188, 122)
    fill_tiles(chunk, TILE_GROUND, 145, 145, 152, 152)

    # Scattered ruin walls in the swamp (DS3: crumbled structures)
    fill_tiles(chunk, TILE_WALL, 63, 103, 65, 106)
    fill_tiles(chunk, TILE_WALL, 88, 118, 90, 121)
    fill_tiles(chunk, TILE_WALL, 128, 83, 130, 86)
    fill_tiles(chunk, TILE_WALL, 183, 118, 185, 121)
    fill_tiles(chunk, TILE_WALL, 148, 148, 150, 151)

    # Basilisk cave area (small enclosed area near entry, south side)
    fill_tiles(chunk, TILE_GROUND, 35, 65, 55, 85)
    fill_tiles(chunk, TILE_WALL, 37, 67, 40, 72)
    fill_tiles(chunk, TILE_WALL, 50, 78, 53, 83)

    # Darkwraith emergence zone (between Central Swamp and Keep Ruins)
    fill_tiles(chunk, TILE_POISON, 100, 120, 140, 140)
    fill_tiles(chunk, TILE_WALL, 108, 125, 111, 128)
    fill_tiles(chunk, TILE_WALL, 125, 130, 128, 134)

    # ================================================================
    # STEP 14: Player spawn and entity creation
    # ================================================================

    entities = []

    spawn_px, spawn_py = SPAWN_PX, SPAWN_PY
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # ================================================================
    # STEP 15: Apply JSON doc terrain and finalize
    # ================================================================

    apply_doc_terrain(chunk, load_doc("FarronKeep"))
    return finalize_map("FarronKeep", chunk, entities, spawn_px, spawn_py)
