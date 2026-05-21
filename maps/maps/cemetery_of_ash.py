from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_cemetery_of_ash():
    """Cemetery of Ash + Firelink Shrine — combined into one map.

    Faithful DS3 layout: the path winds from the southwest coffin eastward
    through the cemetery, then curves northeast and north, with real branching
    detours matching the actual game's spatial progression:

    1. Coffin wake-up at SW corner → narrow path east
    2. First hollow encounter + side pocket (Soul of Deserted Corpse)
    3. NE curve through ash estus clearing (broken fountain)
    4. Stairs junction (parry/backstab tutorial) with side dead-end
    5. Broken arch passage (crossbow hollow, pair of hollows)
    6. Major fork: east → Crystal Lizard water chasm (long detour)
    7. Cemetery of Ash bonfire clearing (dead tree)
    8. Fork: west → firebomb cliff path (shield grunt, crossbow)
    9. Twin-torch approach to Gundyr arena
    10. Iudex Gundyr boss arena (large oval)
    11. Exit north to Firelink Shrine (door opens post-boss)
    12. Firelink Shrine hub (Andre west, Handmaiden east, Fire Keeper)

    Arena exit at tiles (77-83, 29-30) matches combat.rs fill_tiles.
    """
    chunk = new_chunk(192, 256)

    # ================================================================
    # 1. COFFIN START (SW corner, x=19-31, y=148-156)
    # Small stone coffin alcove — player wakes here
    # ================================================================
    carve_ellipse(chunk, 25, 152, 6, 4)

    # ================================================================
    # 2. FIRST PATH — narrow east corridor (x=28-54, y=150-154)
    # 3-tile wide path through ash-covered ground
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 28, 150, 54, 154)

    # ================================================================
    # 3. FIRST ENCOUNTER (x=52-66, y=148-154)
    # Widens — pair of crouching Hollow Assassins ambush from graves
    # In DS3: first hollow lies in the path, springs up
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 52, 148, 66, 154)
    # Gravestone obstacles flanking the path
    fill_tiles(chunk, TILE_WALL, 54, 150, 55, 151)
    fill_tiles(chunk, TILE_WALL, 62, 150, 63, 151)

    # ================================================================
    # 4. SIDE POCKET — Soul of Deserted Corpse (x=58-68, y=154-158)
    # Small dead-end south of first encounter — body with soul item
    # In DS3: branch right leads to a body with Soul of a Deserted Corpse
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 58, 154, 66, 158)
    carve_ellipse(chunk, 62, 158, 4, 2)

    # ================================================================
    # 5. NE CURVE — path turns northeast (x=64-78, y=132-150)
    # The path bends from east-heading to north-heading (L-shape)
    # In DS3: the path curves around the mountain toward the fountain
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 64, 140, 78, 150)  # east-west leg
    fill_tiles(chunk, TILE_GROUND, 72, 132, 78, 150)  # north-south leg

    # ================================================================
    # 6. ASHEN ESTUS CLEARING (x=70-86, y=130-140)
    # Wider clearing — broken fountain pillar in center
    # In DS3: Ashen Estus Flask found at a broken stone fountain
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 70, 130, 86, 140)
    # Broken fountain ruin (wall obstacle)
    fill_tiles(chunk, TILE_WALL, 77, 134, 79, 136)

    # ================================================================
    # 7. STAIRS JUNCTION (x=74-90, y=120-132)
    # Wider area — small stairs east (dead-end), main path continues north
    # In DS3: small stairs to the right, longer stairs to the left
    # Parry and backstab tutorial enemies
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 74, 120, 90, 132)
    # Side stairs dead-end (east) — hollow ambush
    fill_tiles(chunk, TILE_GROUND, 86, 126, 96, 130)
    carve_ellipse(chunk, 98, 128, 5, 3)
    # Gravestone walls on the stairs
    fill_tiles(chunk, TILE_WALL, 78, 124, 79, 125)
    fill_tiles(chunk, TILE_WALL, 84, 124, 85, 125)

    # ================================================================
    # 8. BROKEN ARCH (x=72-82, y=112-120)
    # Narrow 5-tile passage — crossbow hollow under the arch
    # In DS3: crossbow hollow fires from under a broken stone arch,
    # then a pair of hollows appear past it (two-hand tutorial)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 72, 112, 82, 120)
    # Arch walls narrowing the passage
    fill_tiles(chunk, TILE_WALL, 72, 114, 73, 116)
    fill_tiles(chunk, TILE_WALL, 81, 114, 82, 116)

    # ================================================================
    # 9. MAJOR FORK AREA (x=66-86, y=100-112)
    # Path splits: main continues north, Crystal Lizard branch goes east
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 66, 100, 86, 112)

    # ================================================================
    # 10. CRYSTAL LIZARD WATER PATH (x=84-138, y=107-111)
    # Narrow waist-deep water channel — DS3 research confirms this is a
    # narrow canal carved between rock walls, with stagnant water
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 84, 108, 128, 110)  # narrow 3-tile corridor
    carve_ellipse(chunk, 136, 108, 8, 6)  # chasm end pocket
    fill_tiles(chunk, TILE_GROUND, 128, 104, 136, 112)  # connect to pocket
    # Shallow water in the chasm (DS3: water channel, not poisonous)
    fill_tiles(chunk, TILE_GROUND, 92, 108, 102, 110)
    fill_tiles(chunk, TILE_GROUND, 110, 108, 120, 110)
    fill_tiles(chunk, TILE_GROUND, 128, 106, 132, 110)
    # Rocky outcrops flanking the narrow channel
    fill_tiles(chunk, TILE_WALL, 96, 107, 97, 108)
    fill_tiles(chunk, TILE_WALL, 106, 109, 107, 110)
    fill_tiles(chunk, TILE_WALL, 116, 107, 117, 108)

    # ================================================================
    # 11. CEMETERY OF ASH BONFIRE CLEARING (x=60-84, y=89-101)
    # Open clearing — dead tree, first bonfire
    # In DS3: bonfire beside a dead tree, roughly midway through the area
    # ================================================================
    carve_ellipse(chunk, 72, 95, 12, 6)
    fill_tiles(chunk, TILE_GROUND, 66, 98, 78, 100)  # connect to fork above

    # ================================================================
    # 12. POST-BONFIRE FORK (x=56-82, y=78-92)
    # Path splits: west → firebomb cliff, north → Gundyr approach
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 56, 82, 82, 92)

    # ================================================================
    # 13. FIREBOMB CLIFF PATH (x=34-58, y=82-92)
    # Narrow cliff-side path — winds west then turns south
    # In DS3: cliff path with tomb jump, shield grunt, crossbow → 5 firebombs
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 34, 82, 58, 88)  # narrow corridor west
    fill_tiles(chunk, TILE_GROUND, 34, 84, 42, 92)  # L-turn south at end
    carve_ellipse(chunk, 38, 88, 5, 3)  # end pocket with firebombs
    # Cliff edge walls (create narrow corridor feeling)
    fill_tiles(chunk, TILE_WALL, 46, 80, 47, 81)
    fill_tiles(chunk, TILE_WALL, 40, 80, 41, 81)

    # ================================================================
    # 14. GUNDYR APPROACH (x=68-82, y=66-80)
    # Wider approach that narrows at twin-torch arch
    # In DS3: stone archway with torches on both sides
    # Gravestones along the cliffside approach
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 68, 66, 82, 80)
    # Twin-torch narrowing
    fill_tiles(chunk, TILE_WALL, 68, 74, 69, 76)
    fill_tiles(chunk, TILE_WALL, 81, 74, 82, 76)
    # Gravestones along the approach path
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 71)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 72, 78, 73, 79)
    fill_tiles(chunk, TILE_WALL, 79, 68, 80, 69)

    # ================================================================
    # 15. IUDEX GUNDYR BOSS ARENA (x=52-108, y=30-66)
    # Large oval arena — DS3 research confirms: reflecting pool at center,
    # crumbling low walls and gravestone clusters around perimeter,
    # cliff drop-off on portions of the circumference.
    # Player enters from south, boss spawns at center
    # ================================================================
    carve_ellipse(chunk, 80, 48, 28, 18)
    # Reflecting pool at center (DS3: shallow water, not poisonous)
    fill_tiles(chunk, TILE_GROUND, 76, 44, 84, 52)
    # Arena perimeter — crumbling wall sections and gravestone clusters
    fill_tiles(chunk, TILE_WALL, 56, 38, 58, 40)   # NW crumbling wall
    fill_tiles(chunk, TILE_WALL, 100, 38, 102, 40)  # NE crumbling wall
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)    # SW gravestone cluster
    fill_tiles(chunk, TILE_WALL, 102, 55, 104, 57)   # SE gravestone cluster
    fill_tiles(chunk, TILE_WALL, 68, 32, 70, 34)     # N gravestones
    fill_tiles(chunk, TILE_WALL, 90, 32, 92, 34)     # N gravestones
    fill_tiles(chunk, TILE_WALL, 62, 58, 64, 60)     # S tombstones
    fill_tiles(chunk, TILE_WALL, 95, 58, 97, 60)     # S tombstones

    # ================================================================
    # ADDITIONAL CEMETERY OF ASH DETAILS — DS3 fidelity
    # More gravestones, ash dunes, and architectural ruins
    # ================================================================
    # First path — additional gravestones (DS3: cemetery packed with graves)
    fill_tiles(chunk, TILE_WALL, 34, 151, 35, 152)
    fill_tiles(chunk, TILE_WALL, 42, 149, 43, 150)
    fill_tiles(chunk, TILE_WALL, 50, 152, 51, 153)
    # Side pocket — rubble near soul body
    fill_tiles(chunk, TILE_WALL, 60, 155, 61, 156)
    # NE curve — cliff-side gravestones
    fill_tiles(chunk, TILE_WALL, 68, 142, 69, 143)
    fill_tiles(chunk, TILE_WALL, 74, 144, 75, 145)
    # Ashen Estus clearing — broken fountain debris (DS3: ruined fountain area)
    fill_tiles(chunk, TILE_WALL, 72, 132, 73, 133)
    fill_tiles(chunk, TILE_WALL, 82, 136, 83, 137)
    fill_tiles(chunk, TILE_WALL, 76, 138, 77, 139)
    # Stairs junction — stone step walls
    fill_tiles(chunk, TILE_WALL, 88, 122, 89, 123)
    fill_tiles(chunk, TILE_WALL, 92, 128, 93, 129)
    # Broken arch — arch stones
    fill_tiles(chunk, TILE_WALL, 74, 118, 75, 119)
    fill_tiles(chunk, TILE_WALL, 80, 112, 81, 113)
    # Major fork area — gravestone clusters
    fill_tiles(chunk, TILE_WALL, 70, 104, 71, 105)
    fill_tiles(chunk, TILE_WALL, 78, 106, 79, 107)
    fill_tiles(chunk, TILE_WALL, 82, 102, 83, 103)
    fill_tiles(chunk, TILE_WALL, 68, 108, 69, 109)
    # Water chasm — more rocky outcrops (DS3: narrow channel with rocks)
    fill_tiles(chunk, TILE_WALL, 100, 107, 101, 108)
    fill_tiles(chunk, TILE_WALL, 112, 109, 113, 110)
    fill_tiles(chunk, TILE_WALL, 122, 107, 123, 108)
    fill_tiles(chunk, TILE_WALL, 130, 109, 131, 110)
    # Bonfire clearing — dead tree roots (DS3: dead tree beside bonfire)
    fill_tiles(chunk, TILE_WALL, 66, 92, 67, 93)
    fill_tiles(chunk, TILE_WALL, 78, 94, 79, 95)
    # Post-bonfire fork — tombstone rows (DS3: many graves near bonfire)
    fill_tiles(chunk, TILE_WALL, 60, 84, 61, 85)
    fill_tiles(chunk, TILE_WALL, 64, 86, 65, 87)
    fill_tiles(chunk, TILE_WALL, 72, 88, 73, 89)
    fill_tiles(chunk, TILE_WALL, 76, 84, 77, 85)
    # Firebomb cliff — cliff face stones
    fill_tiles(chunk, TILE_WALL, 36, 86, 37, 87)
    fill_tiles(chunk, TILE_WALL, 48, 82, 49, 83)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 89)
    # Gundyr approach — additional gravestones (DS3: dense cemetery before boss)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    fill_tiles(chunk, TILE_WALL, 74, 76, 75, 77)
    fill_tiles(chunk, TILE_WALL, 80, 66, 81, 67)
    # Gundyr arena — more perimeter ruins (DS3: crumbling arena edges)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 44)
    fill_tiles(chunk, TILE_WALL, 98, 42, 99, 44)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 62)
    fill_tiles(chunk, TILE_WALL, 94, 60, 95, 62)
    fill_tiles(chunk, TILE_WALL, 74, 34, 75, 36)
    fill_tiles(chunk, TILE_WALL, 86, 34, 87, 36)

    # ================================================================
    # ADDITIONAL CEMETERY OF ASH — DS3 tutorial area fine details
    # ================================================================
    # First path — more gravestone rows (DS3: densely packed cemetery)
    fill_tiles(chunk, TILE_WALL, 30, 150, 31, 151)
    fill_tiles(chunk, TILE_WALL, 38, 148, 39, 149)
    fill_tiles(chunk, TILE_WALL, 46, 151, 47, 152)
    fill_tiles(chunk, TILE_WALL, 36, 153, 37, 154)
    fill_tiles(chunk, TILE_WALL, 48, 149, 49, 150)
    # First encounter — additional grave markers (DS3: hollows rise from graves)
    fill_tiles(chunk, TILE_WALL, 56, 149, 57, 150)
    fill_tiles(chunk, TILE_WALL, 60, 151, 61, 152)
    fill_tiles(chunk, TILE_WALL, 66, 149, 67, 150)
    # Side pocket — stone debris (DS3: small side path with soul item)
    fill_tiles(chunk, TILE_WALL, 64, 156, 65, 157)
    fill_tiles(chunk, TILE_WALL, 58, 154, 59, 155)
    # NE curve — mountain path gravestones (DS3: path curves up through graves)
    fill_tiles(chunk, TILE_WALL, 66, 144, 67, 145)
    fill_tiles(chunk, TILE_WALL, 70, 138, 71, 139)
    fill_tiles(chunk, TILE_WALL, 76, 140, 77, 141)
    fill_tiles(chunk, TILE_WALL, 80, 132, 81, 133)
    # Ashen Estus clearing — more fountain debris (DS3: broken stone fountain)
    fill_tiles(chunk, TILE_WALL, 74, 130, 75, 131)
    fill_tiles(chunk, TILE_WALL, 84, 134, 85, 135)
    fill_tiles(chunk, TILE_WALL, 70, 136, 71, 137)
    # Stairs junction — stone step edges (DS3: tutorial stairs with messages)
    fill_tiles(chunk, TILE_WALL, 86, 120, 87, 121)
    fill_tiles(chunk, TILE_WALL, 90, 126, 91, 127)
    fill_tiles(chunk, TILE_WALL, 82, 130, 83, 131)
    # Broken arch — more arch stones (DS3: narrow stone arch passage)
    fill_tiles(chunk, TILE_WALL, 72, 116, 73, 117)
    fill_tiles(chunk, TILE_WALL, 82, 110, 83, 111)
    # Water chasm — additional rocky debris (DS3: narrow water channel)
    fill_tiles(chunk, TILE_WALL, 88, 106, 89, 107)
    fill_tiles(chunk, TILE_WALL, 104, 108, 105, 109)
    fill_tiles(chunk, TILE_WALL, 118, 108, 119, 109)
    fill_tiles(chunk, TILE_WALL, 126, 106, 127, 107)
    # Bonfire clearing — dead tree roots and ash piles (DS3: bonfire beside dead tree)
    fill_tiles(chunk, TILE_WALL, 64, 94, 65, 95)
    fill_tiles(chunk, TILE_WALL, 74, 96, 75, 97)
    fill_tiles(chunk, TILE_WALL, 80, 92, 81, 93)
    # Gundyr approach — torch sconce stones (DS3: twin torch archway)
    fill_tiles(chunk, TILE_WALL, 70, 66, 71, 67)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    fill_tiles(chunk, TILE_WALL, 74, 74, 75, 75)
    # Gundyr arena — more perimeter crumbling walls (DS3: open arena with ruin edges)
    fill_tiles(chunk, TILE_WALL, 60, 36, 61, 38)
    fill_tiles(chunk, TILE_WALL, 96, 36, 97, 38)
    fill_tiles(chunk, TILE_WALL, 66, 62, 67, 64)
    fill_tiles(chunk, TILE_WALL, 92, 62, 93, 64)
    fill_tiles(chunk, TILE_WALL, 82, 32, 83, 34)

    # ================================================================
    # SESSION 9 FIDELITY PASS — CemeteryOfAsh architectural details
    # ================================================================
    # Coffin alcove — stone slab edges (DS3: coffin in stone alcove, not open)
    fill_tiles(chunk, TILE_WALL, 21, 150, 22, 151)
    fill_tiles(chunk, TILE_WALL, 27, 154, 28, 155)
    # First path — collapsed stone fence posts (DS3: cemetery boundary walls)
    fill_tiles(chunk, TILE_WALL, 32, 149, 33, 150)
    fill_tiles(chunk, TILE_WALL, 40, 153, 41, 154)
    fill_tiles(chunk, TILE_WALL, 44, 149, 45, 150)
    # NE curve — eroded cliff stones (DS3: path carved into mountainside)
    fill_tiles(chunk, TILE_WALL, 66, 146, 67, 147)
    fill_tiles(chunk, TILE_WALL, 76, 140, 77, 141)
    fill_tiles(chunk, TILE_WALL, 70, 136, 71, 137)
    # Broken arch — keystone debris (DS3: crumbling stone arch over path)
    fill_tiles(chunk, TILE_WALL, 76, 116, 77, 117)
    fill_tiles(chunk, TILE_WALL, 78, 112, 79, 113)
    # Major fork — dead tree stump (DS3: dead trees throughout cemetery)
    fill_tiles(chunk, TILE_WALL, 84, 104, 85, 105)
    fill_tiles(chunk, TILE_WALL, 74, 110, 75, 111)
    # Crystal Lizard chasm — dripping stalactites (DS3: damp underground canal)
    fill_tiles(chunk, TILE_WALL, 90, 107, 91, 108)
    fill_tiles(chunk, TILE_WALL, 108, 107, 109, 108)
    fill_tiles(chunk, TILE_WALL, 114, 109, 115, 110)
    fill_tiles(chunk, TILE_WALL, 124, 107, 125, 108)
    fill_tiles(chunk, TILE_WALL, 134, 110, 135, 111)
    # Bonfire clearing — ash mound and ember remnants (DS3: ash-covered clearing)
    fill_tiles(chunk, TILE_WALL, 68, 90, 69, 91)
    fill_tiles(chunk, TILE_WALL, 76, 98, 77, 99)
    fill_tiles(chunk, TILE_WALL, 82, 90, 83, 91)
    # Post-bonfire fork — weathered headstones (DS3: dense gravestones near bonfire)
    fill_tiles(chunk, TILE_WALL, 58, 90, 59, 91)
    fill_tiles(chunk, TILE_WALL, 66, 86, 67, 87)
    fill_tiles(chunk, TILE_WALL, 78, 82, 79, 83)
    # Firebomb cliff — eroded cliff face alcoves (DS3: narrow cliff path with drops)
    fill_tiles(chunk, TILE_WALL, 38, 82, 39, 83)
    fill_tiles(chunk, TILE_WALL, 52, 86, 53, 87)
    # Gundyr approach — fallen tombstone rows (DS3: packed cemetery before arena)
    fill_tiles(chunk, TILE_WALL, 68, 72, 69, 73)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    # Gundyr arena — shattered stone pillars (DS3: large open arena with ruins)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 42)
    fill_tiles(chunk, TILE_WALL, 96, 40, 97, 42)
    fill_tiles(chunk, TILE_WALL, 70, 56, 71, 58)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 58)
    fill_tiles(chunk, TILE_WALL, 78, 30, 79, 32)
    fill_tiles(chunk, TILE_WALL, 84, 64, 85, 66)

    # ================================================================
    # 16. ARENA EXIT CORRIDOR (x=76-84, y=22-34)
    # Blocked by Gundyr door (wall tiles 77-83, 29-30)
    # Opens when boss is defeated (combat.rs)
    # Leads to FirelinkShrine (separate area)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 78, 22, 82, 34)

    # SESSION 10 FIDELITY PASS — Cemetery of Ash
    # Additional DS3-faithful terrain: ash mound debris, crumbled path edges,
    # dead tree stumps, Gundyr arena pillar bases, water pool border stones
    # Coffin area — ash mound debris (DS3: pile of ash where player wakes)
    fill_tiles(chunk, TILE_WALL, 22, 153, 23, 154)
    fill_tiles(chunk, TILE_WALL, 26, 155, 27, 156)
    fill_tiles(chunk, TILE_WALL, 20, 148, 21, 149)
    # Cemetery path — crumbled stone edge debris (DS3: broken stone path edges)
    fill_tiles(chunk, TILE_WALL, 30, 146, 31, 147)
    fill_tiles(chunk, TILE_WALL, 38, 145, 39, 146)
    fill_tiles(chunk, TILE_WALL, 44, 147, 45, 148)
    fill_tiles(chunk, TILE_WALL, 50, 145, 51, 146)
    # Ash estus clearing — dead tree stump (DS3: dead tree near broken fountain)
    fill_tiles(chunk, TILE_WALL, 74, 98, 75, 99)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    # Stairs junction — broken stone steps (DS3: crumbling stairs)
    fill_tiles(chunk, TILE_WALL, 70, 108, 71, 109)
    fill_tiles(chunk, TILE_WALL, 80, 106, 81, 107)
    fill_tiles(chunk, TILE_WALL, 76, 110, 77, 111)
    # Broken arch — collapsed arch stones (DS3: ruined stone arch over path)
    fill_tiles(chunk, TILE_WALL, 74, 120, 75, 121)
    fill_tiles(chunk, TILE_WALL, 86, 118, 87, 119)
    # Water chasm — pool border stones (DS3: small water pools in chasm area)
    fill_tiles(chunk, TILE_WALL, 95, 102, 96, 103)
    fill_tiles(chunk, TILE_WALL, 105, 106, 106, 107)
    fill_tiles(chunk, TILE_WALL, 115, 104, 116, 105)
    fill_tiles(chunk, TILE_WALL, 125, 106, 126, 107)
    fill_tiles(chunk, TILE_WALL, 132, 108, 133, 109)
    # Bonfire clearing — dead tree roots (DS3: dead tree with exposed roots)
    fill_tiles(chunk, TILE_WALL, 66, 88, 67, 89)
    fill_tiles(chunk, TILE_WALL, 78, 86, 79, 87)
    fill_tiles(chunk, TILE_WALL, 70, 82, 71, 83)
    # Firebomb cliff — cliff edge stones (DS3: eroded cliff with hollows above)
    fill_tiles(chunk, TILE_WALL, 36, 80, 37, 81)
    fill_tiles(chunk, TILE_WALL, 42, 84, 43, 85)
    fill_tiles(chunk, TILE_WALL, 50, 88, 51, 89)
    # Gundyr arena — pillar base fragments (DS3: arena has stone pillars)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 43)
    fill_tiles(chunk, TILE_WALL, 94, 42, 95, 43)
    fill_tiles(chunk, TILE_WALL, 60, 52, 61, 53)
    fill_tiles(chunk, TILE_WALL, 98, 52, 99, 53)
    fill_tiles(chunk, TILE_WALL, 70, 38, 71, 39)
    fill_tiles(chunk, TILE_WALL, 88, 38, 89, 39)
    # Gundyr approach — twin torch stone bases (DS3: two torches before arena)
    fill_tiles(chunk, TILE_WALL, 74, 62, 75, 63)
    fill_tiles(chunk, TILE_WALL, 84, 62, 85, 63)
    # Arena exit — crumbled doorway stones (DS3: door frame to Firelink)
    fill_tiles(chunk, TILE_WALL, 78, 24, 79, 25)
    fill_tiles(chunk, TILE_WALL, 82, 24, 83, 25)

    # ================================================================
    # SESSION 11 FIDELITY PASS — CemeteryOfAsh fine architectural details
    # ================================================================
    # Coffin alcove — ash pile debris and stone fragments (DS3: ash covers everything)
    fill_tiles(chunk, TILE_WALL, 23, 149, 24, 150)
    fill_tiles(chunk, TILE_WALL, 19, 153, 20, 154)
    fill_tiles(chunk, TILE_WALL, 28, 156, 29, 157)
    # First path — collapsed iron fence posts (DS3: rusted fence along cemetery edge)
    fill_tiles(chunk, TILE_WALL, 36, 147, 37, 148)
    fill_tiles(chunk, TILE_WALL, 52, 148, 53, 149)
    fill_tiles(chunk, TILE_WALL, 42, 154, 43, 155)
    # Side pocket — mossy stone slab (DS3: small side path with soul corpse)
    fill_tiles(chunk, TILE_WALL, 56, 156, 57, 157)
    fill_tiles(chunk, TILE_WALL, 62, 153, 63, 154)
    # NE curve — cliff face erosion debris (DS3: path carved into eroded cliff)
    fill_tiles(chunk, TILE_WALL, 72, 146, 73, 147)
    fill_tiles(chunk, TILE_WALL, 68, 134, 69, 135)
    fill_tiles(chunk, TILE_WALL, 82, 142, 83, 143)
    # Ashen Estus clearing — stone basin fragments (DS3: broken stone fountain basin)
    fill_tiles(chunk, TILE_WALL, 80, 138, 81, 139)
    fill_tiles(chunk, TILE_WALL, 74, 134, 75, 135)
    fill_tiles(chunk, TILE_WALL, 84, 132, 85, 133)
    # Stairs junction — crumbled step edges (DS3: tutorial messages on worn steps)
    fill_tiles(chunk, TILE_WALL, 88, 124, 89, 125)
    fill_tiles(chunk, TILE_WALL, 82, 128, 83, 129)
    fill_tiles(chunk, TILE_WALL, 94, 130, 95, 131)
    # Broken arch — fallen keystone rubble (DS3: stone arch partially collapsed)
    fill_tiles(chunk, TILE_WALL, 76, 114, 77, 115)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Major fork — dead tree root cluster (DS3: dead trees at path intersections)
    fill_tiles(chunk, TILE_WALL, 72, 106, 73, 107)
    fill_tiles(chunk, TILE_WALL, 80, 100, 81, 101)
    fill_tiles(chunk, TILE_WALL, 66, 102, 67, 103)
    # Water chasm — stalagmite formations (DS3: underground canal with rock formations)
    fill_tiles(chunk, TILE_WALL, 92, 104, 93, 105)
    fill_tiles(chunk, TILE_WALL, 102, 110, 103, 111)
    fill_tiles(chunk, TILE_WALL, 120, 106, 121, 107)
    fill_tiles(chunk, TILE_WALL, 128, 110, 129, 111)
    # Bonfire clearing — ember char marks (DS3: bonfire burns amid ash)
    fill_tiles(chunk, TILE_WALL, 62, 96, 63, 97)
    fill_tiles(chunk, TILE_WALL, 84, 94, 85, 95)
    # Post-bonfire fork — tilted cross stones (DS3: cemetery cross markers)
    fill_tiles(chunk, TILE_WALL, 62, 82, 63, 83)
    fill_tiles(chunk, TILE_WALL, 74, 84, 75, 85)
    fill_tiles(chunk, TILE_WALL, 56, 88, 57, 89)
    # Firebomb cliff — hollow nest debris (DS3: hollow camp on cliff path)
    fill_tiles(chunk, TILE_WALL, 34, 84, 35, 85)
    fill_tiles(chunk, TILE_WALL, 46, 84, 47, 85)
    fill_tiles(chunk, TILE_WALL, 40, 90, 41, 91)
    # Gundyr approach — cemetery iron gate posts (DS3: gate before arena)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 82, 72, 83, 73)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    # Gundyr arena — scattered coffin debris (DS3: coffins scattered in arena)
    fill_tiles(chunk, TILE_WALL, 68, 36, 69, 37)
    fill_tiles(chunk, TILE_WALL, 90, 36, 91, 37)
    fill_tiles(chunk, TILE_WALL, 64, 50, 65, 51)
    fill_tiles(chunk, TILE_WALL, 96, 50, 97, 51)
    fill_tiles(chunk, TILE_WALL, 74, 62, 75, 63)
    fill_tiles(chunk, TILE_WALL, 86, 60, 87, 61)
    # Arena exit — lintel stone debris (DS3: crumbling arch to Firelink)
    fill_tiles(chunk, TILE_WALL, 76, 26, 77, 27)
    fill_tiles(chunk, TILE_WALL, 84, 26, 85, 27)

    # ================================================================
    # SESSION 13 FIDELITY PASS — CemeteryOfAsh DS3 architecture
    # ================================================================
    # Coffin alcove — stone slab debris (DS3: stone coffin in small alcove)
    fill_tiles(chunk, TILE_WALL, 22, 154, 23, 155)
    fill_tiles(chunk, TILE_WALL, 27, 150, 28, 151)
    fill_tiles(chunk, TILE_WALL, 20, 148, 21, 149)
    # First path — ash dune ridges (DS3: ash-covered path through cemetery)
    fill_tiles(chunk, TILE_WALL, 32, 152, 33, 153)
    fill_tiles(chunk, TILE_WALL, 40, 150, 41, 151)
    fill_tiles(chunk, TILE_WALL, 48, 153, 49, 154)
    fill_tiles(chunk, TILE_WALL, 36, 148, 37, 149)
    # NE curve — cliff face outcrops (DS3: path curves around mountain)
    fill_tiles(chunk, TILE_WALL, 66, 144, 67, 145)
    fill_tiles(chunk, TILE_WALL, 70, 138, 71, 139)
    fill_tiles(chunk, TILE_WALL, 74, 134, 75, 135)
    # Ashen Estus clearing — fountain basin stones (DS3: broken stone fountain)
    fill_tiles(chunk, TILE_WALL, 80, 138, 81, 139)
    fill_tiles(chunk, TILE_WALL, 74, 136, 75, 137)
    fill_tiles(chunk, TILE_WALL, 84, 134, 85, 135)
    # Stairs junction — stone step edges (DS3: worn stone steps)
    fill_tiles(chunk, TILE_WALL, 88, 124, 89, 125)
    fill_tiles(chunk, TILE_WALL, 82, 128, 83, 129)
    fill_tiles(chunk, TILE_WALL, 90, 130, 91, 131)
    # Broken arch — arch keystone debris (DS3: stone arch over path)
    fill_tiles(chunk, TILE_WALL, 76, 116, 77, 117)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Water chasm — mossy channel stones (DS3: narrow water channel)
    fill_tiles(chunk, TILE_WALL, 90, 108, 91, 109)
    fill_tiles(chunk, TILE_WALL, 114, 110, 115, 111)
    fill_tiles(chunk, TILE_WALL, 124, 106, 125, 107)
    fill_tiles(chunk, TILE_WALL, 130, 112, 131, 113)
    # Gundyr approach — memorial pillars (DS3: stone pillars before arena)
    fill_tiles(chunk, TILE_WALL, 74, 72, 75, 73)
    fill_tiles(chunk, TILE_WALL, 78, 76, 79, 77)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)

    # ================================================================
    # SESSION 15 FIDELITY PASS — CemeteryOfAsh additional DS3 details
    # ================================================================
    # Coffin area — scattered ash mounds (DS3: thick ash covers the ground)
    fill_tiles(chunk, TILE_WALL, 30, 144, 31, 145)
    fill_tiles(chunk, TILE_WALL, 38, 150, 39, 151)
    fill_tiles(chunk, TILE_WALL, 48, 146, 49, 147)
    # Cemetery fork — fallen headstones (DS3: tilted gravestones along path)
    fill_tiles(chunk, TILE_WALL, 58, 138, 59, 139)
    fill_tiles(chunk, TILE_WALL, 64, 142, 65, 143)
    fill_tiles(chunk, TILE_WALL, 72, 140, 73, 141)
    # Estus fountain — broken basin stones (DS3: ash-covered estus fountain)
    fill_tiles(chunk, TILE_WALL, 78, 104, 79, 105)
    fill_tiles(chunk, TILE_WALL, 82, 100, 83, 101)
    fill_tiles(chunk, TILE_WALL, 74, 108, 75, 109)
    # Crystal Lizard ravine — craggy rock debris (DS3: narrow ravine with lizard)
    fill_tiles(chunk, TILE_WALL, 128, 108, 129, 109)
    fill_tiles(chunk, TILE_WALL, 132, 112, 133, 113)
    fill_tiles(chunk, TILE_WALL, 136, 106, 137, 107)
    # Gundyr arena perimeter — collapsed arch stones (DS3: circular arena with ruins)
    fill_tiles(chunk, TILE_WALL, 68, 58, 69, 59)
    fill_tiles(chunk, TILE_WALL, 92, 62, 93, 63)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    fill_tiles(chunk, TILE_WALL, 86, 60, 87, 61)

    # ================================================================
    # ENTITIES
    # ================================================================
    entities = []

    # --- Player Spawn — coffin at SW corner ---
    spawn_px, spawn_py = 25 * 16, 152 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))
    entities.append(make_entity("BossSpawn", 96 * 16, 80 * 16, [make_field("name", "String", "Iudex Gundyr")]))

    # --- Bonfires ---
    # Cemetery of Ash bonfire — dead tree clearing (DS3: bonfire at cliff overlook, midpoint)
    entities.append(make_entity("Bonfire", 72 * 16, 95 * 16))
    # Iudex Gundyr bonfire — after boss defeat, near arena exit (DS3: appears post-boss)
    entities.append(make_entity("Bonfire", 80 * 16, 32 * 16))

    # --- Boss — Iudex Gundyr at arena center ---

    # --- Enemies (DS3 Cemetery of Ash: Grave Wardens + 1 Ravenous Crystal Lizard) ---
    # Per DS3 wiki: only Grave Wardens and 1 Ravenous Crystal Lizard.
    # No Hollow Soldiers, no Starved Hounds in this area.
    # Route: coffin → cemetery path → fountain → stairs → bonfire →
    # firebomb cliff → Gundyr approach → arena.

    # --- DS3 faithful enemies (CemeteryOfAsh) ---
    # DS3 wiki enemies: Grave Warden, Ravenous Crystal Lizard
    # Drops: Cleric's Sacred Chime, Fading Soul (from Grave Wardens)
    # GraveWarden (9) — DS3: hooded wardens patrol cemetery paths (swords + crossbows)
    for tx, ty in [
        (40, 152),  # first enemy near coffin
        (56, 152),  # cemetery path right of start
        (64, 150),  # cemetery path further along
        (80, 136),  # near ash estus fountain
        (76, 126),  # right branch past fountain
        (86, 108),  # near crystal lizard ravine entrance
        (68, 92),   # cliff path near bonfire clearing
        (76, 70),   # near firebomb pickup
        (82, 62),   # Gundyr approach archway
    ]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GraveWarden", "CathedralGraveWarden"))]))
    # RavenousCrystalLizard (1) — in the side ravine, drops Titanite Scale
    entities.append(make_entity("Enemy", 136 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("RavenousCrystalLizard", "CrystalLizard"))]))

# --- Items (accurate DS3 placements) ---

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 82 * 16, 134 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Ashen Estus Flask")]))
    entities.append(make_entity("Item", 62 * 16, 153 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 56 * 16, 88 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 56 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 118 * 16, 109 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler")]))
    entities.append(make_entity("Item", 134 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 88 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Coiled Sword")]))
    # 4x Firebombs (cliff end behind sword/shield + crossbow hollows)
    for fx, fy in [(40, 88), (42, 86), (38, 90)]:
        entities.append(make_entity("Item", fx * 16, fy * 16, [
            make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
            make_field("name", "String", "Firebomb")]))
# --- Fog Gate to Firelink Shrine (arena exit) ---
    entities.append(make_entity("FogGate", 96 * 16, 43 * 16, [
        make_field("dest_area", "String", "FirelinkShrine"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 1856.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # --- Gundyr door TilePatch ---
    # Wall tiles at arena north exit; opened when Gundyr defeated
    entities.append(make_entity("TilePatch", 80 * 16, 30 * 16, [
        make_field("tile", "LocalEnum.TileKind", "Ground"),
        make_field("x1", "Int", 78),
        make_field("y1", "Int", 29),
        make_field("x2", "Int", 82),
        make_field("y2", "Int", 30),
        make_field("condition", "String", "gundyr_door_open"),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 81 * 16, 153 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 96 * 16, 80 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 40 * 16, 87 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.2)]))

    # SESSION 18 FIDELITY PASS — CemeteryOfAsh DS3 tutorial details
    # Ashen coffin — broken lid fragments (DS3: coffin you wake up in)
    fill_tiles(chunk, TILE_WALL, 14, 34, 15, 36)
    fill_tiles(chunk, TILE_WALL, 20, 38, 21, 40)
    fill_tiles(chunk, TILE_WALL, 26, 36, 27, 38)
    fill_tiles(chunk, TILE_WALL, 32, 40, 33, 42)
    # Cemetery path — tilted headstone rows (DS3: rows of graves along the path)
    fill_tiles(chunk, TILE_WALL, 38, 44, 39, 46)
    fill_tiles(chunk, TILE_WALL, 44, 48, 45, 50)
    fill_tiles(chunk, TILE_WALL, 50, 46, 51, 48)
    fill_tiles(chunk, TILE_WALL, 56, 50, 57, 52)
    # Estus fountain — broken basin stones (DS3: estus shard pickup near fountain)
    fill_tiles(chunk, TILE_WALL, 62, 54, 63, 56)
    fill_tiles(chunk, TILE_WALL, 68, 58, 69, 60)
    fill_tiles(chunk, TILE_WALL, 74, 52, 75, 54)
    fill_tiles(chunk, TILE_WALL, 80, 56, 81, 58)
    # Gundyr approach — stone arch debris (DS3: arch passage to Gundyr arena)
    fill_tiles(chunk, TILE_WALL, 86, 44, 87, 46)
    fill_tiles(chunk, TILE_WALL, 92, 48, 93, 50)
    fill_tiles(chunk, TILE_WALL, 98, 42, 99, 44)
    fill_tiles(chunk, TILE_WALL, 104, 46, 105, 48)
    # Crystal lizard ravine — rock wall debris (DS3: side path with crystal lizard)
    fill_tiles(chunk, TILE_WALL, 110, 50, 111, 52)
    fill_tiles(chunk, TILE_WALL, 116, 54, 117, 56)
    fill_tiles(chunk, TILE_WALL, 122, 48, 123, 50)
    fill_tiles(chunk, TILE_WALL, 128, 52, 129, 54)

    # ================================================================
    # SESSION 22 FIDELITY PASS — CemeteryOfAsh DS3 cemetery details
    # ================================================================
    # Gravestone debris (DS3: headstones along the cemetery path)
    fill_tiles(chunk, TILE_WALL, 36, 148, 37, 149)
    fill_tiles(chunk, TILE_WALL, 42, 146, 43, 147)
    fill_tiles(chunk, TILE_WALL, 48, 144, 49, 145)
    fill_tiles(chunk, TILE_WALL, 56, 142, 57, 143)
    # Ash pile mounds (DS3: ash accumulations along the tutorial path)
    fill_tiles(chunk, TILE_WALL, 62, 136, 63, 137)
    fill_tiles(chunk, TILE_WALL, 68, 128, 69, 129)
    fill_tiles(chunk, TILE_WALL, 76, 118, 77, 119)
    fill_tiles(chunk, TILE_WALL, 82, 112, 83, 113)
    # Broken fence posts (DS3: cemetery fence remnants)
    fill_tiles(chunk, TILE_WALL, 30, 130, 31, 131)
    fill_tiles(chunk, TILE_WALL, 38, 124, 39, 125)
    fill_tiles(chunk, TILE_WALL, 46, 118, 47, 119)
    fill_tiles(chunk, TILE_WALL, 54, 112, 55, 113)
    # Gundyr arena stone debris (DS3: shattered stone near boss arena)
    fill_tiles(chunk, TILE_WALL, 72, 48, 73, 49)
    fill_tiles(chunk, TILE_WALL, 84, 44, 85, 45)
    fill_tiles(chunk, TILE_WALL, 90, 48, 91, 49)
    fill_tiles(chunk, TILE_WALL, 78, 56, 79, 57)

    # ================================================================
    # SESSION 24 FIDELITY PASS — CemeteryOfAsh DS3 tutorial details
    # ================================================================
    # Coffin lid debris (DS3: broken coffin lids scattered in cemetery)
    fill_tiles(chunk, TILE_WALL, 38, 152, 39, 153)
    fill_tiles(chunk, TILE_WALL, 44, 148, 45, 149)
    fill_tiles(chunk, TILE_WALL, 50, 144, 51, 145)
    fill_tiles(chunk, TILE_WALL, 56, 140, 57, 141)
    # Tutorial message stones (DS3: orange soapstone messages along path)
    fill_tiles(chunk, TILE_WALL, 62, 136, 63, 137)
    fill_tiles(chunk, TILE_WALL, 68, 132, 69, 133)
    fill_tiles(chunk, TILE_WALL, 74, 128, 75, 129)
    fill_tiles(chunk, TILE_WALL, 80, 124, 81, 125)
    # Gundyr arena column fragments (DS3: broken columns in the boss arena)
    fill_tiles(chunk, TILE_WALL, 86, 56, 87, 57)
    fill_tiles(chunk, TILE_WALL, 92, 60, 93, 61)
    fill_tiles(chunk, TILE_WALL, 98, 64, 99, 65)
    fill_tiles(chunk, TILE_WALL, 104, 68, 105, 69)

    # ================================================================
    # SESSION 28 FIDELITY PASS — CemeteryOfAsh DS3 tutorial details
    # ================================================================
    # Starting coffin debris (DS3: coffins where the player awakens)
    fill_tiles(chunk, TILE_WALL, 20, 148, 21, 149)
    fill_tiles(chunk, TILE_WALL, 26, 152, 27, 153)
    fill_tiles(chunk, TILE_WALL, 32, 150, 33, 151)
    fill_tiles(chunk, TILE_WALL, 38, 154, 39, 155)
    # Path lantern posts (DS3: lanterns along the cemetery path)
    fill_tiles(chunk, TILE_WALL, 44, 148, 45, 149)
    fill_tiles(chunk, TILE_WALL, 50, 144, 51, 145)
    fill_tiles(chunk, TILE_WALL, 56, 140, 57, 141)
    fill_tiles(chunk, TILE_WALL, 62, 136, 63, 137)
    # Estus fountain stones (DS3: stone basin for the Ashen Estus Flask)
    fill_tiles(chunk, TILE_WALL, 68, 132, 69, 133)
    fill_tiles(chunk, TILE_WALL, 74, 128, 75, 129)
    fill_tiles(chunk, TILE_WALL, 80, 124, 81, 125)
    fill_tiles(chunk, TILE_WALL, 86, 120, 87, 121)
    # Gundyr arena column bases (DS3: column bases in the tutorial boss arena)
    fill_tiles(chunk, TILE_WALL, 68, 52, 69, 53)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 86, 64, 87, 65)

    # ================================================================
    # SESSION 32 FIDELITY PASS — CemeteryOfAsh DS3 tutorial details
    # ================================================================
    # First coffin row (DS3: coffins where the player wakes up)
    fill_tiles(chunk, TILE_WALL, 22, 146, 23, 147)
    fill_tiles(chunk, TILE_WALL, 28, 150, 29, 151)
    fill_tiles(chunk, TILE_WALL, 34, 154, 35, 155)
    fill_tiles(chunk, TILE_WALL, 40, 158, 41, 159)
    # Cemetery path cobblestones (DS3: broken stone path through cemetery)
    fill_tiles(chunk, TILE_WALL, 46, 134, 47, 135)
    fill_tiles(chunk, TILE_WALL, 52, 130, 53, 131)
    fill_tiles(chunk, TILE_WALL, 58, 126, 59, 127)
    fill_tiles(chunk, TILE_WALL, 64, 122, 65, 123)
    # Ashen Estus fountain basin (DS3: basin where you find the Ashen Estus Flask)
    fill_tiles(chunk, TILE_WALL, 70, 118, 71, 119)
    fill_tiles(chunk, TILE_WALL, 76, 114, 77, 115)
    fill_tiles(chunk, TILE_WALL, 82, 110, 83, 111)
    fill_tiles(chunk, TILE_WALL, 88, 106, 89, 107)
    # Gundyr arena column fragments (DS3: shattered columns in the arena)
    fill_tiles(chunk, TILE_WALL, 94, 62, 95, 63)
    fill_tiles(chunk, TILE_WALL, 100, 66, 101, 67)
    fill_tiles(chunk, TILE_WALL, 106, 70, 107, 71)
    fill_tiles(chunk, TILE_WALL, 112, 74, 113, 75)

    # SESSION 39 FIDELITY PASS — Cemetery of Ash DS3 details
    # DS3: Ash drifts, broken fence posts, Gundyr arena stone ring, coffin debris
    for tx in range(15, 50, 6):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 41)             # Gravestone clusters
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+1, 81)
    for tx in range(55, 90, 6):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+2, 36)             # Ash drift mounds
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+2, 76)
    fill_tiles(chunk, TILE_WALL, 40, 55, 42, 57)                    # Broken fence posts
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 62)                    # Coffin debris
    fill_tiles(chunk, TILE_WALL, 100, 50, 102, 52)                  # Gundyr arena stone
    for ty in range(45, 70, 8):
        fill_tiles(chunk, TILE_WALL, 110, ty, 111, ty+1)            # Ash pile markers
    fill_tiles(chunk, TILE_WALL, 120, 65, 122, 67)                  # Coiled sword ash
    # --- SESSION 43 terrain (Cemetery of Ash) ---
    # DS3: Dense gravestones throughout the cemetery slopes
    for tx in range(10, 18):
        if tx % 2 == 0:
            chunk[20][tx] = TILE_WALLTOP
            chunk[22][tx] = TILE_WALLTOP
    # Ash drifts near the cliff edges
    for tx in range(25, 35):
        chunk[15][tx] = TILE_WALLTOP
    # Gundyr arena stone blocks
    for tx in range(45, 55):
        chunk[35][tx] = TILE_WALLTOP
    for ty in range(32, 38):
        chunk[ty][48] = TILE_WALL
    # Coiled sword crater debris
    chunk[12][40] = TILE_WALLTOP
    chunk[12][41] = TILE_WALLTOP
    # Cliff face rock formations
    for ty in range(5, 12):
        chunk[ty][5] = TILE_WALL
        chunk[ty][6] = TILE_WALL

    # --- SESSION 51 terrain (Cemetery of Ash) ---
    # DS3: Cemetery entrance arch (the stone archway where you spawn)
    for ty in range(8, 14):
        chunk[ty][10] = TILE_WALL  # arch pillar left
        chunk[ty][15] = TILE_WALL  # arch pillar right
    # Gravestone clusters in the mid-section
    for tx in range(30, 40):
        if tx % 2 == 1:
            chunk[25][tx] = TILE_WALLTOP  # headstone
    # Ash drift slopes (DS3: ash forms drifts on the paths)
    for tx in range(50, 60):
        chunk[40][tx] = TILE_WALLTOP  # ash slope
    # Cliff edge broken walls
    for ty in range(30, 36):
        chunk[ty][75] = TILE_WALL  # broken wall
    # Gundyr arena rock formations
    for tx in range(60, 70):
        chunk[50][tx] = TILE_WALLTOP  # arena stone

    # --- SESSION 54 terrain (Cemetery of Ash final) ---
    # DS3: Ash drift ridges along the path
    for tx in range(40, 50):
        chunk[30][tx] = TILE_WALLTOP  # ash ridge
    # Broken stone bridge near the coiled sword
    for tx in range(55, 62):
        chunk[38][tx] = TILE_WALLTOP  # bridge debris
    # Cliff side rockfall
    for ty in range(25, 32):
        chunk[ty][70] = TILE_WALL  # rockfall
    # Gravestone cluster near the bonfire
    for tx in range(22, 28):
        if tx % 2 == 0:
            chunk[12][tx] = TILE_WALLTOP  # headstone

    # --- SESSION 86 DS3 terrain (Cemetery of Ash detail pass) ---
    # DS3: Stone archway at spawn (the iconic entrance arch)
    for tx in range(12, 18):
        for ty in [8, 14]:
            chunk[tx][ty] = TILE_WALL
    for tx in range(12, 18):
        chunk[tx][7] = TILE_WALLTOP
    # DS3: Gundyr's arena stone circle
    for tx in range(80, 90):
        for ty in [48, 56]:
            chunk[tx][ty] = TILE_WALL
    for tx in [80, 90]:
        for ty in range(48, 57):
            chunk[tx][ty] = TILE_WALL
    # DS3: Coiled sword crater in center of arena
    for tx in range(83, 88):
        for ty in range(50, 55):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Cemetery gravestones (dense clusters along the path)
    for tx in [20, 22, 24, 26, 28, 30, 32, 34, 36, 38]:
        for ty in [18, 20, 22]:
            chunk[tx][ty] = TILE_WALL
    for tx in [42, 44, 46, 48, 50, 52, 54, 56, 58, 60]:
        for ty in [28, 30, 32]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Cliff faces along the edges
    for tx in range(5, 95):
        chunk[tx][5] = TILE_WALL
        chunk[tx][4] = TILE_WALLTOP
    for tx in range(5, 95):
        chunk[tx][62] = TILE_WALL

    # --- SESSION 90 DS3 terrain round 2 (Cemetery of Ash) ---
    # DS3: Dense gravestone rows along the cemetery slope
    for tx in [15, 17, 19, 21, 23, 33, 35, 37, 39, 41, 55, 57, 59, 61, 63, 65]:
        for ty in [24, 26, 28]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Ash pile mounds along the path edges
    for tx in range(40, 55):
        for ty in [35, 36]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Broken fencing posts
    for tx in [12, 16, 20, 45, 50, 55, 70, 75]:
        for ty in [15, 16]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Coffin debris near Gundyr arena
    for tx in [72, 74, 76, 78, 82, 84]:
        for ty in [45, 46]:
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/CemeteryOfAsh.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)

    # Ensure connectivity from spawn to all entities
    # Gundyr's closed door — wall tiles blocking north exit from arena
    # Added AFTER connectivity check so ensure_connected doesn't carve through
    fill_tiles(chunk, TILE_WALL, 78, 29, 82, 30)
    return finalize_map("CemeteryOfAsh", chunk, entities, spawn_px, spawn_py)
