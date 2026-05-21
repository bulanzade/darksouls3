from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_archdragon_peak():
    """Archdragon Peak - mountain peak with Nameless King boss.
    Faithful DS3 layout: mountain entry (NW) -> serpent barracks -> wyvern arena ->
    Dragon-Kin Mausoleum -> storm path -> Great Belfry -> Nameless King arena (SE).
    Lightning storms and dragon ruins throughout.
    """
    chunk = new_chunk(320, 288)
    entities = []

    # === Mountain entry (NW) ===
    fill_tiles(chunk, TILE_GROUND, 6, 108, 35, 145)
    carve_ellipse(chunk, 20, 126, 12, 10)

    # === Serpent barracks ===
    fill_tiles(chunk, TILE_GROUND, 25, 85, 70, 120)
    carve_ellipse(chunk, 48, 102, 14, 10)
    # Barracks walls
    fill_tiles(chunk, TILE_WALL, 32, 90, 34, 95)
    fill_tiles(chunk, TILE_WALL, 58, 105, 60, 110)

    # === Wyvern arena (center) ===
    fill_tiles(chunk, TILE_GROUND, 30, 48, 80, 85)
    carve_ellipse(chunk, 55, 66, 18, 14)
    # Dragon ruin walls
    fill_tiles(chunk, TILE_WALL, 40, 55, 44, 60)
    fill_tiles(chunk, TILE_WALL, 65, 70, 68, 75)

    # === Dragon-Kin Mausoleum (center-right) ===
    fill_tiles(chunk, TILE_GROUND, 62, 38, 98, 62)
    carve_ellipse(chunk, 80, 50, 12, 8)

    # === Storm path (ascending ridge) ===
    fill_tiles(chunk, TILE_GROUND, 88, 28, 125, 55)
    # Ridge walls
    fill_tiles(chunk, TILE_WALL, 95, 32, 97, 36)
    fill_tiles(chunk, TILE_WALL, 112, 42, 114, 46)

    # === Great Belfry (upper) ===
    fill_tiles(chunk, TILE_GROUND, 105, 12, 140, 35)
    carve_ellipse(chunk, 122, 22, 14, 10)
    # Bell tower walls
    fill_tiles(chunk, TILE_WALL, 112, 16, 114, 20)
    fill_tiles(chunk, TILE_WALL, 130, 25, 132, 30)

    # === Nameless King arena (SE) ===
    fill_tiles(chunk, TILE_GROUND, 100, 62, 155, 118)
    carve_ellipse(chunk, 128, 90, 24, 22)
    # Storm walls
    fill_tiles(chunk, TILE_WALL, 108, 70, 110, 75)
    fill_tiles(chunk, TILE_WALL, 145, 95, 147, 100)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 108)

    # === Connections ===
    # Entry -> Barracks
    fill_tiles(chunk, TILE_GROUND, 25, 108, 35, 115)
    # Barracks -> Wyvern
    fill_tiles(chunk, TILE_GROUND, 38, 80, 48, 90)
    # Wyvern -> Mausoleum
    fill_tiles(chunk, TILE_GROUND, 62, 48, 72, 58)
    # Mausoleum -> Storm path
    fill_tiles(chunk, TILE_GROUND, 88, 38, 98, 48)
    # Storm path -> Belfry
    fill_tiles(chunk, TILE_GROUND, 115, 28, 125, 35)
    # Belfry -> Nameless arena
    fill_tiles(chunk, TILE_GROUND, 125, 35, 135, 62)

    # === ADDITIONAL INTERNAL STRUCTURES — dense DS3 mountain terrain ===
    # Serpent barracks — training dummies and serpent statues
    fill_tiles(chunk, TILE_WALL, 35, 92, 37, 95)
    fill_tiles(chunk, TILE_WALL, 42, 98, 44, 100)
    fill_tiles(chunk, TILE_WALL, 52, 108, 54, 110)
    fill_tiles(chunk, TILE_WALL, 60, 95, 62, 97)
    fill_tiles(chunk, TILE_WALL, 38, 105, 40, 107)
    fill_tiles(chunk, TILE_WALL, 48, 92, 50, 94)
    # Wyvern arena — dragon bone walls
    fill_tiles(chunk, TILE_WALL, 45, 52, 47, 55)
    fill_tiles(chunk, TILE_WALL, 58, 60, 60, 63)
    fill_tiles(chunk, TILE_WALL, 50, 72, 52, 75)
    fill_tiles(chunk, TILE_WALL, 68, 65, 70, 68)
    fill_tiles(chunk, TILE_WALL, 35, 68, 37, 70)
    fill_tiles(chunk, TILE_WALL, 72, 78, 74, 80)
    # Mausoleum — dragon altar walls
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 45)
    fill_tiles(chunk, TILE_WALL, 85, 48, 87, 50)
    fill_tiles(chunk, TILE_WALL, 78, 55, 80, 57)
    fill_tiles(chunk, TILE_WALL, 90, 40, 92, 42)
    # Storm path — cliff edges and wind-swept rocks
    fill_tiles(chunk, TILE_WALL, 95, 35, 97, 38)
    fill_tiles(chunk, TILE_WALL, 105, 40, 107, 42)
    fill_tiles(chunk, TILE_WALL, 118, 32, 120, 34)
    fill_tiles(chunk, TILE_WALL, 100, 48, 102, 50)
    fill_tiles(chunk, TILE_WALL, 112, 38, 114, 40)
    # Belfry — bell tower columns and arches
    fill_tiles(chunk, TILE_WALL, 108, 18, 110, 22)
    fill_tiles(chunk, TILE_WALL, 118, 20, 120, 24)
    fill_tiles(chunk, TILE_WALL, 128, 18, 130, 22)
    fill_tiles(chunk, TILE_WALL, 115, 28, 117, 30)
    fill_tiles(chunk, TILE_WALL, 135, 22, 137, 26)
    # Nameless arena — storm debris and lightning-scorched rocks
    fill_tiles(chunk, TILE_WALL, 112, 75, 114, 78)
    fill_tiles(chunk, TILE_WALL, 135, 82, 137, 85)
    fill_tiles(chunk, TILE_WALL, 120, 95, 122, 98)
    fill_tiles(chunk, TILE_WALL, 140, 90, 142, 93)
    fill_tiles(chunk, TILE_WALL, 115, 105, 117, 108)
    fill_tiles(chunk, TILE_WALL, 150, 100, 152, 103)

    # === MORE ARCHDRAGON PEAK DETAILS — DS3 fidelity ===
    # Mountain entry — stone steps and cliff walls (DS3: path winds up the mountain)
    fill_tiles(chunk, TILE_WALL, 10, 115, 12, 118)
    fill_tiles(chunk, TILE_WALL, 22, 128, 24, 130)
    fill_tiles(chunk, TILE_WALL, 30, 135, 32, 138)
    fill_tiles(chunk, TILE_WALL, 16, 140, 18, 142)
    fill_tiles(chunk, TILE_WALL, 28, 142, 30, 145)
    # Serpent barracks — more training grounds walls
    # DS3: outdoor training area with serpent-man warriors
    fill_tiles(chunk, TILE_WALL, 30, 88, 32, 90)
    fill_tiles(chunk, TILE_WALL, 45, 95, 47, 97)
    fill_tiles(chunk, TILE_WALL, 55, 98, 57, 100)
    fill_tiles(chunk, TILE_WALL, 40, 108, 42, 110)
    fill_tiles(chunk, TILE_WALL, 62, 108, 64, 110)
    fill_tiles(chunk, TILE_WALL, 35, 115, 37, 118)
    fill_tiles(chunk, TILE_WALL, 50, 112, 52, 114)
    # Wyvern arena — more dragon skeleton debris (DS3: massive dead dragon bones)
    fill_tiles(chunk, TILE_WALL, 38, 58, 40, 60)
    fill_tiles(chunk, TILE_WALL, 48, 65, 50, 67)
    fill_tiles(chunk, TILE_WALL, 60, 58, 62, 60)
    fill_tiles(chunk, TILE_WALL, 70, 72, 72, 74)
    fill_tiles(chunk, TILE_WALL, 42, 78, 44, 80)
    fill_tiles(chunk, TILE_WALL, 75, 82, 77, 84)
    # Dragon-Kin Mausoleum — altar and dragon statue walls
    # DS3: interior with dragon altar, serpent-man summoners
    fill_tiles(chunk, TILE_WALL, 65, 40, 67, 42)
    fill_tiles(chunk, TILE_WALL, 75, 45, 77, 47)
    fill_tiles(chunk, TILE_WALL, 82, 52, 84, 54)
    fill_tiles(chunk, TILE_WALL, 92, 45, 94, 47)
    fill_tiles(chunk, TILE_WALL, 88, 55, 90, 57)
    # Storm path — wind-sculpted rocks and ruins (DS3: ascending path with lightning)
    fill_tiles(chunk, TILE_WALL, 92, 30, 94, 32)
    fill_tiles(chunk, TILE_WALL, 102, 35, 104, 37)
    fill_tiles(chunk, TILE_WALL, 110, 45, 112, 47)
    fill_tiles(chunk, TILE_WALL, 120, 38, 122, 40)
    fill_tiles(chunk, TILE_WALL, 98, 50, 100, 52)
    # Great Belfry — bell tower architecture (DS3: massive bell structure)
    fill_tiles(chunk, TILE_WALL, 110, 14, 112, 16)
    fill_tiles(chunk, TILE_WALL, 125, 15, 127, 18)
    fill_tiles(chunk, TILE_WALL, 135, 18, 137, 20)
    fill_tiles(chunk, TILE_WALL, 120, 30, 122, 32)
    fill_tiles(chunk, TILE_WALL, 132, 28, 134, 30)
    # Nameless arena — more storm debris (DS3: lightning-scorched mountaintop)
    fill_tiles(chunk, TILE_WALL, 105, 78, 107, 80)
    fill_tiles(chunk, TILE_WALL, 118, 82, 120, 84)
    fill_tiles(chunk, TILE_WALL, 138, 85, 140, 88)
    fill_tiles(chunk, TILE_WALL, 125, 98, 127, 100)
    fill_tiles(chunk, TILE_WALL, 145, 105, 147, 108)
    fill_tiles(chunk, TILE_WALL, 132, 108, 134, 110)
    fill_tiles(chunk, TILE_WALL, 148, 95, 150, 98)

    # === SESSION 6 FIDELITY PASS — Archdragon Peak ===
    # Mountain entry — rocky cliff faces (DS3: steep mountain path with stone steps)
    fill_tiles(chunk, TILE_WALL, 8, 112, 10, 114)
    fill_tiles(chunk, TILE_WALL, 14, 125, 16, 127)
    fill_tiles(chunk, TILE_WALL, 24, 132, 26, 134)
    fill_tiles(chunk, TILE_WALL, 32, 140, 34, 142)
    fill_tiles(chunk, TILE_WALL, 12, 138, 14, 140)
    # Serpent barracks — weapon racks and pillars (DS3: outdoor arena with stone pillars)
    fill_tiles(chunk, TILE_WALL, 28, 92, 30, 94)
    fill_tiles(chunk, TILE_WALL, 44, 100, 46, 102)
    fill_tiles(chunk, TILE_WALL, 56, 102, 58, 104)
    fill_tiles(chunk, TILE_WALL, 64, 112, 66, 114)
    fill_tiles(chunk, TILE_WALL, 42, 112, 44, 114)
    fill_tiles(chunk, TILE_WALL, 54, 115, 56, 117)
    # Wyvern arena — massive dragon ribs (DS3: huge dragon skeleton on bridge)
    fill_tiles(chunk, TILE_WALL, 36, 52, 38, 54)
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 64)
    fill_tiles(chunk, TILE_WALL, 74, 76, 76, 78)
    fill_tiles(chunk, TILE_WALL, 46, 76, 48, 78)
    fill_tiles(chunk, TILE_WALL, 56, 80, 58, 82)
    # Mausoleum — dragon stone altar details (DS3: dragon-kin meditation chamber)
    fill_tiles(chunk, TILE_WALL, 68, 44, 70, 46)
    fill_tiles(chunk, TILE_WALL, 76, 50, 78, 52)
    fill_tiles(chunk, TILE_WALL, 84, 46, 86, 48)
    fill_tiles(chunk, TILE_WALL, 94, 42, 96, 44)
    fill_tiles(chunk, TILE_WALL, 66, 56, 68, 58)
    # Storm path — lightning-charred rocks (DS3: storm-swept mountain ridge)
    fill_tiles(chunk, TILE_WALL, 90, 34, 92, 36)
    fill_tiles(chunk, TILE_WALL, 108, 38, 110, 40)
    fill_tiles(chunk, TILE_WALL, 116, 40, 118, 42)
    fill_tiles(chunk, TILE_WALL, 96, 44, 98, 46)
    fill_tiles(chunk, TILE_WALL, 124, 35, 126, 37)
    # Belfry — tower arch buttresses (DS3: massive bell tower with stone arches)
    fill_tiles(chunk, TILE_WALL, 106, 12, 108, 14)
    fill_tiles(chunk, TILE_WALL, 122, 12, 124, 14)
    fill_tiles(chunk, TILE_WALL, 138, 20, 140, 22)
    fill_tiles(chunk, TILE_WALL, 116, 32, 118, 34)
    fill_tiles(chunk, TILE_WALL, 130, 30, 132, 32)
    # Nameless arena — storm-battered summit (DS3: open sky arena on peak)
    fill_tiles(chunk, TILE_WALL, 102, 72, 104, 74)
    fill_tiles(chunk, TILE_WALL, 130, 78, 132, 80)
    fill_tiles(chunk, TILE_WALL, 142, 88, 144, 90)
    fill_tiles(chunk, TILE_WALL, 136, 98, 138, 100)
    fill_tiles(chunk, TILE_WALL, 148, 102, 150, 104)
    fill_tiles(chunk, TILE_WALL, 122, 112, 124, 114)

    # ================================================================
    # SESSION 9 FIDELITY PASS — ArchdragonPeak architectural details
    # ================================================================
    # Entry path — dragon-crest pillars (DS3: ornate pillars with dragon motifs)
    fill_tiles(chunk, TILE_WALL, 16, 128, 17, 129)
    fill_tiles(chunk, TILE_WALL, 22, 130, 23, 131)
    fill_tiles(chunk, TILE_WALL, 12, 134, 13, 135)
    fill_tiles(chunk, TILE_WALL, 26, 126, 27, 127)
    # Ancient dragon ruins — petrified dragon bones (DS3: massive skeletal remains)
    fill_tiles(chunk, TILE_WALL, 34, 118, 35, 119)
    fill_tiles(chunk, TILE_WALL, 38, 122, 39, 123)
    fill_tiles(chunk, TILE_WALL, 30, 124, 31, 125)
    fill_tiles(chunk, TILE_WALL, 42, 116, 43, 117)
    fill_tiles(chunk, TILE_WALL, 36, 126, 37, 127)
    # Serpent-Man temple — carved stone serpents (DS3: serpent imagery everywhere)
    fill_tiles(chunk, TILE_WALL, 52, 108, 53, 109)
    fill_tiles(chunk, TILE_WALL, 56, 112, 57, 113)
    fill_tiles(chunk, TILE_WALL, 48, 114, 49, 115)
    fill_tiles(chunk, TILE_WALL, 60, 106, 61, 107)
    # Belfry — giant bell stone supports (DS3: massive bell structure)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    fill_tiles(chunk, TILE_WALL, 72, 100, 73, 101)
    fill_tiles(chunk, TILE_WALL, 64, 102, 65, 103)
    fill_tiles(chunk, TILE_WALL, 76, 94, 77, 95)
    fill_tiles(chunk, TILE_WALL, 70, 104, 71, 105)
    # Dragon-Kin Mausoleum — ritual altar stones (DS3: meditation area)
    fill_tiles(chunk, TILE_WALL, 80, 86, 81, 87)
    fill_tiles(chunk, TILE_WALL, 84, 90, 85, 91)
    fill_tiles(chunk, TILE_WALL, 76, 92, 77, 93)
    fill_tiles(chunk, TILE_WALL, 88, 84, 89, 85)
    # Nameless King arena — storm-worn pillars (DS3: arena atop the peak)
    fill_tiles(chunk, TILE_WALL, 120, 72, 121, 73)
    fill_tiles(chunk, TILE_WALL, 126, 76, 127, 77)
    fill_tiles(chunk, TILE_WALL, 132, 70, 133, 71)
    fill_tiles(chunk, TILE_WALL, 138, 74, 139, 75)
    fill_tiles(chunk, TILE_WALL, 116, 80, 117, 81)
    fill_tiles(chunk, TILE_WALL, 144, 78, 145, 79)
    # Twisted stone formations (DS3: wind-sculpted rock on the peak)
    fill_tiles(chunk, TILE_WALL, 100, 92, 101, 93)
    fill_tiles(chunk, TILE_WALL, 108, 88, 109, 89)
    fill_tiles(chunk, TILE_WALL, 104, 96, 105, 97)
    fill_tiles(chunk, TILE_WALL, 112, 84, 113, 85)


    # ================================================================
    # DS3 STRUCTURAL WALLS — Archdragon Peak mountain architecture
    # DS3: mountain peak with serpent-man camp, dragon bones, wyvern arena,
    # ancient mausoleum, and Nameless King boss at the summit
    # ================================================================
    # Serpent-man camp — barracks walls (DS3: serpent-men train at camp)
    fill_tiles(chunk, TILE_WALL, 60, 160, 64, 166)  # Barracks wall 1
    fill_tiles(chunk, TILE_WALL, 76, 158, 80, 164)  # Barracks wall 2
    fill_tiles(chunk, TILE_WALL, 68, 168, 72, 174)  # Barracks wall 3
    fill_tiles(chunk, TILE_WALL, 84, 166, 88, 172)  # Training area wall
    # Ancient Wyvern arena — dragon bone obstacles (DS3: massive dragon skeleton)
    fill_tiles(chunk, TILE_WALL, 108, 150, 112, 158) # Dragon bone NW
    fill_tiles(chunk, TILE_WALL, 124, 148, 128, 156) # Dragon bone NE
    fill_tiles(chunk, TILE_WALL, 116, 162, 120, 170) # Dragon bone SW
    fill_tiles(chunk, TILE_WALL, 132, 160, 136, 168) # Dragon bone SE
    # Dragon-Kin Mausoleum — altar walls (DS3: dragon meditation altar)
    fill_tiles(chunk, TILE_WALL, 100, 120, 104, 126) # Altar wall left
    fill_tiles(chunk, TILE_WALL, 116, 118, 120, 124) # Altar wall right
    fill_tiles(chunk, TILE_WALL, 108, 128, 112, 134) # Altar center wall
    # Havel knight area — stone cliff walls (DS3: Havel Knight ambush)
    fill_tiles(chunk, TILE_WALL, 140, 140, 144, 146) # Cliff wall 1
    fill_tiles(chunk, TILE_WALL, 148, 136, 152, 142) # Cliff wall 2
    # Nameless King arena — peak summit walls (DS3: open sky arena)
    fill_tiles(chunk, TILE_WALL, 80, 40, 84, 46)    # Summit wall NW
    fill_tiles(chunk, TILE_WALL, 96, 38, 100, 44)   # Summit wall NE
    fill_tiles(chunk, TILE_WALL, 84, 50, 88, 56)    # Summit wall SW
    fill_tiles(chunk, TILE_WALL, 92, 48, 96, 54)    # Summit wall SE
    # Path corridors — mountain passage walls (DS3: narrow paths between areas)
    fill_tiles(chunk, TILE_WALL, 44, 142, 48, 148)  # Passage wall left
    fill_tiles(chunk, TILE_WALL, 56, 140, 60, 146)  # Passage wall right

    # ================================================================
    # DS3 MOUNTAIN CLIFF WALLS — Archdragon Peak terrain depth
    # DS3: mountain peak with steep cliffs, narrow paths, wind-blasted
    # ruins, and serpent-man structures carved into the rock
    # ================================================================
    # Entry cliff — steep cliff face walls (DS3: narrow mountain path entry)
    fill_tiles(chunk, TILE_WALL, 10, 180, 16, 200)  # Cliff face left
    fill_tiles(chunk, TILE_WALL, 28, 178, 34, 198)  # Cliff face right
    fill_tiles(chunk, TILE_WALL, 18, 190, 26, 210)  # Cliff center wall
    # Serpent camp — barracks interior walls (DS3: serpent-men barracks)
    fill_tiles(chunk, TILE_WALL, 48, 155, 54, 175)  # Barracks interior left
    fill_tiles(chunk, TILE_WALL, 68, 150, 74, 170)  # Barracks interior right
    fill_tiles(chunk, TILE_WALL, 56, 165, 64, 180)  # Barracks center divider
    fill_tiles(chunk, TILE_WALL, 76, 160, 82, 178)  # Training yard wall
    # Wyvern arena — cliff edge walls (DS3: arena on cliff edge)
    fill_tiles(chunk, TILE_WALL, 100, 140, 106, 158) # Cliff edge NW
    fill_tiles(chunk, TILE_WALL, 120, 138, 126, 156) # Cliff edge NE
    fill_tiles(chunk, TILE_WALL, 108, 158, 116, 175) # Cliff edge SW
    fill_tiles(chunk, TILE_WALL, 124, 155, 130, 172) # Cliff edge SE
    # Mausoleum — ancient stone walls (DS3: dragon meditation chamber)
    fill_tiles(chunk, TILE_WALL, 92, 112, 98, 128)  # Mausoleum wall left
    fill_tiles(chunk, TILE_WALL, 112, 110, 118, 126) # Mausoleum wall right
    fill_tiles(chunk, TILE_WALL, 100, 120, 108, 135) # Mausoleum center wall
    # Havel area — rock formation walls (DS3: rocky outcrops)
    fill_tiles(chunk, TILE_WALL, 132, 128, 138, 145) # Rock formation 1
    fill_tiles(chunk, TILE_WALL, 142, 122, 148, 140) # Rock formation 2
    # Path between areas — narrow passage walls (DS3: winding mountain paths)
    fill_tiles(chunk, TILE_WALL, 36, 135, 42, 150)  # Passage wall
    fill_tiles(chunk, TILE_WALL, 86, 130, 92, 145)  # Mid passage wall
    # Nameless King peak — summit cliff walls (DS3: open sky summit)
    fill_tiles(chunk, TILE_WALL, 70, 42, 76, 55)    # Summit cliff NW
    fill_tiles(chunk, TILE_WALL, 100, 40, 106, 53)  # Summit cliff NE
    fill_tiles(chunk, TILE_WALL, 80, 55, 86, 68)    # Summit cliff SW
    fill_tiles(chunk, TILE_WALL, 92, 53, 98, 66)    # Summit cliff SE
        # --- Player spawn ---
    spawn_px, spawn_py = 18 * 16, 132 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 38 * 16, 225 * 16))    # Entry: Archdragon Peak
    entities.append(make_entity("Bonfire", 137 * 16, 143 * 16))     # Dragonkin Mausoleum
    entities.append(make_entity("Bonfire", 210 * 16, 78 * 16))    # Great Belfry
    entities.append(make_entity("Bonfire", 262 * 16, 56 * 16))    # Nameless King

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 262 * 16, 56 * 16))  # Nameless King

    # --- Enemies (DS3 Archdragon Peak: dense Serpent-Men, Summoners, Drakeblood Knights,
    # Havel Knight, Rock Lizards, Wyvern) ---

    # --- Items — DS3 Archdragon Peak (complete per wiki walkthrough) ---
    items = [
        # Mountain entry area
        ("SoulOrb", "Soul of a Weary Warrior", 22, 135, 2000),
        ("Consumable", "Lightning Gem", 35, 112, 0),                # Entry path
        ("HomewardBone", "Homeward Bone", 42, 118, 0),                # Path to barracks
        ("TitaniteShard", "Titanite Chunk", 55, 68, 0),             # Near bonfire
        ("Ember", "Ember", 28, 125, 0),                             # Near entry bonfire
        # Barracks area
        ("SoulOrb", "Soul of a Nameless Soldier", 50, 98, 1000),
        ("TitaniteShard", "Titanite Chunk", 52, 95, 0),             # Stairs landing
        ("WeaponDrop", "Ancient Dragon Greatshield", 62, 102, 0),   # Near overhang
        ("TitaniteShard", "Titanite Chunk", 47, 106, 0),            # Left stairs
        ("TitaniteShard", "Large Titanite Shard", 38, 115, 0),      # Hop down short stairs
        # Wyvern arena
        ("Ember", "Ember", 55, 62, 0),                              # Wyvern arena
        ("Ember", "Ember", 65, 78, 0),                              # Wyvern arena
        ("Consumable", "Stalk Dung Pie", 58, 70, 0),
        ("Consumable", "Stalk Dung Pie", 60, 72, 0),
        ("Consumable", "Stalk Dung Pie", 62, 74, 0),
        ("Consumable", "Stalk Dung Pie", 64, 68, 0),
        ("Consumable", "Stalk Dung Pie", 66, 70, 0),
        ("Consumable", "Stalk Dung Pie", 68, 72, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 70, 82, 2000),       # Wyvern arena
        ("RingDrop", "Ring of Steel Protection", 52, 60, 0),        # Right side steps
        ("Consumable", "Lightning Urn", 74, 76, 0),                 # Up stairs left
        ("TitaniteShard", "Titanite Chunk", 77, 53, 0),             # Building interior
        ("TitaniteShard", "Twinkling Titanite", 78, 48, 0),         # Ladder top
        ("TitaniteShard", "Twinkling Titanite", 80, 45, 0),         # Ladder top x2
        # Upper wyvern path — plank ledges
        ("TitaniteShard", "Titanite Chunk", 85, 40, 0),
        ("TitaniteShard", "Titanite Chunk", 88, 38, 0),
        ("Consumable", "Lightning Bolt", 90, 35, 0),                # 12x Lightning Bolt
        # Dragon-Kin Mausoleum
        ("Consumable", "Dragon Head Stone", 42, 100, 0),            # After Wyvern defeat
        ("TitaniteShard", "Titanite Scale", 75, 45, 0),             # Corpse over railing
        ("TitaniteShard", "Titanite Scale", 78, 42, 0),             # Left side
        ("TitaniteShard", "Titanite Scale", 82, 48, 0),             # Room leading out
        ("SoulOrb", "Soul of a Crestfallen Knight", 87, 48, 1500),  # Corner corpse
        ("RingDrop", "Calamity Ring", 80, 52, 0),                  # Altar dragon gesture
        # Storm path / Great Belfry
        ("RingDrop", "Thunder Stoneplate Ring", 98, 32, 0),         # Ladder top
        ("Ember", "Ember", 118, 28, 0),                             # Ruins doorway
        ("SoulOrb", "Soul of a Weary Warrior", 132, 27, 2000),      # After wyvern area
        # Belfry area — Havel area
        ("Consumable", "Great Magic Barrier", 138, 82, 0),          # Drop down from Havel area
        ("TitaniteShard", "Titanite Slab", 132, 78, 0),             # Next to wyvern claw
        ("SoulOrb", "Large Soul of a Crestfallen Knight", 125, 85, 2500),
        # Path to altar
        ("Consumable", "Dragon Chaser's Ashes", 110, 40, 0),        # Behind Rock Lizard
        ("Consumable", "Twinkling Dragon Torso Stone", 120, 55, 0),  # Altar at top of stairs
        # Nameless King arena — post-boss
        ("TitaniteShard", "Titanite Slab", 128, 95, 0),             # After Nameless King
        ("ArmorDrop", "Dragonslayer Set", 125, 100, 0),             # After Nameless King
        # Weapons from drops/transposition
        ("WeaponDrop", "Dragonslayer Spear", 128, 92, 0),           # Gate before Nameless King
        ("WeaponDrop", "Dragon Tooth", 132, 80, 0),                 # Havel NPC drop
        ("WeaponDrop", "Havel's Greatshield", 135, 82, 0),          # Havel NPC drop
        ("RingDrop", "Lightning Clutch Ring", 50, 62, 0),           # Left of wyvern gate
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    # --- Chests — DS3 Archdragon Peak ---

    
    # --- DS3 faithful enemies (ArchdragonPeak) ---
    # SerpentMan (38)
    for tx, ty in [(22, 115), (28, 120), (38, 98), (45, 108), (42, 102), (48, 95), (55, 100), (52, 88), (58, 92), (55, 75), (62, 80), (48, 68), (65, 72), (72, 78), (68, 58), (80, 48), (75, 55), (85, 50), (90, 45), (92, 48), (95, 35), (100, 42), (105, 38), (108, 28), (118, 25), (115, 30), (120, 75), (135, 28), (125, 72), (130, 35), (132, 40), (146, 83), (144, 87), (137, 91), (132, 95), (149, 99), (142, 111), (122, 115)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SerpentMan", "SerpentMan"))]))
    # SerpentManSummoner (4 â DS3: casts spells from elevated positions in mausoleum/belfry)
    entities.append(make_entity("Enemy", 72 * 16, 52 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SerpentManSummoner", "DarkMage"))]))
    entities.append(make_entity("Enemy", 85 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SerpentManSummoner", "DarkMage"))]))
    entities.append(make_entity("Enemy", 98 * 16, 45 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SerpentManSummoner", "DarkMage"))]))
    entities.append(make_entity("Enemy", 153 * 16, 107 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SerpentManSummoner", "DarkMage"))]))
    # RockLizard (7)
    for tx, ty in [(35, 110), (42, 95), (118, 20), (130, 25), (142, 85), (112, 72), (148, 95)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("RockLizard", "RockLizard"))]))
    # CrystalLizard (2)
    entities.append(make_entity("Enemy", 50 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 28 * 16, 118 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # DrakebloodKnight (3)
    entities.append(make_entity("Enemy", 110 * 16, 30 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DrakebloodKnight", "DrakebloodKnight"))]))
    entities.append(make_entity("Enemy", 142 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DrakebloodKnight", "DrakebloodKnight"))]))
    entities.append(make_entity("Enemy", 78 * 16, 52 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DrakebloodKnight", "DrakebloodKnight"))]))
    # HavelKnight (1)
    entities.append(make_entity("Enemy", 128 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HavelKnight", "HavelKnight"))]))
    # MiniBoss (2)
    entities.append(make_entity("Enemy", 55 * 16, 66 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    entities.append(make_entity("Enemy", 62 * 16, 76 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- NPCs ---
    # Hawkwood — can be summoned for Nameless King (DS3: summon sign at Great Belfry)
    entities.append(make_entity("Npc", 210 * 16, 78 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String",
            "The Nameless King awaits atop this peak|He is the firstborn of Gwyn, Lord of Cinder|I have come this far to face him|The dragons and their secrets end here"),
    ]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 33 * 16, 231 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 67 * 16, 217 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Lightning Gem")]))
    entities.append(make_entity("Item", 81 * 16, 228 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 121 * 16, 163 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 46 * 16, 236 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 96 * 16, 186 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 98 * 16, 180 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 113 * 16, 191 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Ancient Dragon Greatshield")]))
    entities.append(make_entity("Item", 86 * 16, 202 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 72 * 16, 217 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 130 * 16, 158 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 136 * 16, 168 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Stalk Dung Pie")]))
    entities.append(make_entity("Item", 153 * 16, 185 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 126 * 16, 160 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Ring of Steel Protection")]))
    entities.append(make_entity("Item", 150 * 16, 178 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Lightning Urn")]))
    entities.append(make_entity("Item", 147 * 16, 136 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 150 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 168 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Bolt"),
        make_field("name", "String", "Lightning Bolt")]))
    entities.append(make_entity("Item", 141 * 16, 136 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 146 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 153 * 16, 141 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 157 * 16, 143 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 150 * 16, 146 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Calamity Ring")]))
    entities.append(make_entity("Item", 181 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Thunder Stoneplate Ring")]))
    entities.append(make_entity("Item", 246 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 276 * 16, 57 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Great Magic Barrier")]))
    entities.append(make_entity("Item", 251 * 16, 53 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteSlab"),
        make_field("name", "String", "Titanite Slab")]))
    entities.append(make_entity("Item", 245 * 16, 57 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 210 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Dragon Chaser's Ashes")]))
    entities.append(make_entity("Item", 228 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gesture"),
        make_field("name", "String", "Twinkling Dragon Torso Stone")]))
    entities.append(make_entity("Item", 251 * 16, 67 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Dragonslayer Set")]))
    entities.append(make_entity("Item", 257 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Dragonslayer Swordspear")]))
    entities.append(make_entity("Item", 263 * 16, 52 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Dragon Tooth")]))
    entities.append(make_entity("Item", 270 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Havel's Greatshield")]))
    entities.append(make_entity("Item", 126 * 16, 157 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Lightning Clutch Ring")]))
    entities.append(make_entity("Item", 262 * 16, 57 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Nameless King")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 207 * 16, 71 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 226 * 16, 78 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gate ---
    # Back to Irithyll Dungeon (NW)
    entities.append(make_entity("FogGate", 38 * 16, 231 * 16, [
        make_field("dest_area", "String", "IrithyllDungeon"),
        make_field("dest_x", "Float", 2160.0),
        make_field("dest_y", "Float", 128.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Mountain entry — golden sunlight
    entities.append(make_entity("Light", 18 * 16, 132 * 16, [
        make_field("radius", "Float", 150.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    # Barracks — orange torch glow
    entities.append(make_entity("Light", 48 * 16, 102 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.35)]))
    # Wyvern arena — pale daylight
    entities.append(make_entity("Light", 55 * 16, 66 * 16, [
        make_field("radius", "Float", 170.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.3)]))
    # Belfry — blue lightning
    entities.append(make_entity("Light", 122 * 16, 22 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.7),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.45)]))
    # Nameless King arena — storm blue/white
    entities.append(make_entity("Light", 128 * 16, 85 * 16, [
        make_field("radius", "Float", 220.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.75),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.5)]))
    # SESSION 10 FIDELITY PASS — Archdragon Peak
    # Additional DS3-faithful terrain: dragon-crest altar stones, serpent temple
    # pillars, belfry step stones, wyvern perch debris, summoner altar stones
    # Dragon-crest altar stones (DS3: dragon crest medallion at entrance)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 33)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    # Serpent temple pillars (DS3: serpentine architecture throughout)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 49)
    fill_tiles(chunk, TILE_WALL, 46, 56, 47, 57)
    # Ancient dragon head stones (DS3: petrified dragon heads line the path)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 41)
    fill_tiles(chunk, TILE_WALL, 68, 44, 69, 45)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    # Belfry area — step stones and bell debris (DS3: great belfry with bell)
    fill_tiles(chunk, TILE_WALL, 122, 64, 123, 65)
    fill_tiles(chunk, TILE_WALL, 126, 68, 127, 69)
    fill_tiles(chunk, TILE_WALL, 130, 72, 131, 73)
    fill_tiles(chunk, TILE_WALL, 118, 70, 119, 71)
    fill_tiles(chunk, TILE_WALL, 134, 66, 135, 67)
    # Wyvern perch — cliff debris (DS3: wyvern perches on cliff edge)
    fill_tiles(chunk, TILE_WALL, 78, 38, 79, 39)
    fill_tiles(chunk, TILE_WALL, 84, 42, 85, 43)
    fill_tiles(chunk, TILE_WALL, 90, 38, 91, 39)
    # Summoner altar stones (DS3: Serpent-Man Summoners at altars)
    fill_tiles(chunk, TILE_WALL, 106, 28, 107, 29)
    fill_tiles(chunk, TILE_WALL, 112, 32, 113, 33)
    fill_tiles(chunk, TILE_WALL, 140, 84, 141, 85)
    fill_tiles(chunk, TILE_WALL, 146, 88, 147, 89)
    # Path edge stones (DS3: stone-lined mountain paths)
    fill_tiles(chunk, TILE_WALL, 38, 42, 39, 43)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 59)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 51)
    fill_tiles(chunk, TILE_WALL, 98, 44, 99, 45)
    # Nameless King gate — ancient stones (DS3: gate to boss arena)
    fill_tiles(chunk, TILE_WALL, 124, 88, 125, 89)
    fill_tiles(chunk, TILE_WALL, 130, 92, 131, 93)
    fill_tiles(chunk, TILE_WALL, 136, 86, 137, 87)

    # SESSION 10 PASS B — ArchdragonPeak
    # Additional DS3 terrain: dragon-crest steps, serpent altar stones, wyvern bridge debris
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 51)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 59)
    fill_tiles(chunk, TILE_WALL, 92, 52, 93, 53)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 61)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 57)
    fill_tiles(chunk, TILE_WALL, 128, 64, 129, 65)
    fill_tiles(chunk, TILE_WALL, 140, 58, 141, 59)
    fill_tiles(chunk, TILE_WALL, 136, 72, 137, 73)
    fill_tiles(chunk, TILE_WALL, 120, 68, 121, 69)
    fill_tiles(chunk, TILE_WALL, 108, 74, 109, 75)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 84, 66, 85, 67)

    # ================================================================
    # SESSION 12 FIDELITY PASS — ArchdragonPeak DS3 architectural details
    # ================================================================
    # Dragon stone scale fragments (DS3: petrified dragon scales along paths)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 28)
    fill_tiles(chunk, TILE_WALL, 26, 30, 27, 32)
    fill_tiles(chunk, TILE_WALL, 34, 26, 35, 28)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 36)
    # Serpent-man altar pedestals (DS3: stone altars where serpent-men pray)
    fill_tiles(chunk, TILE_WALL, 56, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 44)
    fill_tiles(chunk, TILE_WALL, 72, 36, 73, 38)
    fill_tiles(chunk, TILE_WALL, 80, 40, 81, 42)
    # Havel's rock formation (DS3: Havel knight ambush area with boulders)
    fill_tiles(chunk, TILE_WALL, 88, 48, 89, 50)
    fill_tiles(chunk, TILE_WALL, 94, 44, 95, 46)
    fill_tiles(chunk, TILE_WALL, 100, 50, 101, 52)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 54)
    # Petrified dragon egg clusters (DS3: dragon eggs in nest area)
    fill_tiles(chunk, TILE_WALL, 40, 60, 41, 62)
    fill_tiles(chunk, TILE_WALL, 48, 64, 49, 66)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 60)
    fill_tiles(chunk, TILE_WALL, 64, 62, 65, 64)
    # Ancient dragon tooth debris (DS3: massive dragon teeth along cliffs)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 58)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 62)
    fill_tiles(chunk, TILE_WALL, 88, 54, 89, 56)
    fill_tiles(chunk, TILE_WALL, 96, 58, 97, 60)
    # Storm ritual stone circles (DS3: Nameless King storm ritual stones)
    fill_tiles(chunk, TILE_WALL, 108, 52, 109, 54)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 58)
    fill_tiles(chunk, TILE_WALL, 124, 50, 125, 52)
    fill_tiles(chunk, TILE_WALL, 132, 54, 133, 56)
    # Nameless King lightning scars (DS3: scorched ground from lightning strikes)
    fill_tiles(chunk, TILE_WALL, 138, 60, 139, 62)
    fill_tiles(chunk, TILE_WALL, 144, 56, 145, 58)
    fill_tiles(chunk, TILE_WALL, 134, 64, 135, 66)
    fill_tiles(chunk, TILE_WALL, 142, 68, 143, 70)
    # Belfry bell rope anchors (DS3: rope anchors for the great bell)
    fill_tiles(chunk, TILE_WALL, 118, 78, 119, 80)
    fill_tiles(chunk, TILE_WALL, 126, 74, 127, 76)
    fill_tiles(chunk, TILE_WALL, 122, 82, 123, 84)
    fill_tiles(chunk, TILE_WALL, 130, 80, 131, 82)
    # Twisted gargoyle base stones (DS3: gargoyle perches on temple walls)
    fill_tiles(chunk, TILE_WALL, 100, 74, 101, 76)
    fill_tiles(chunk, TILE_WALL, 106, 78, 107, 80)
    fill_tiles(chunk, TILE_WALL, 112, 72, 113, 74)
    fill_tiles(chunk, TILE_WALL, 94, 76, 95, 78)
    # Dragon-king path monuments (DS3: ancient dragon-king path markers)
    fill_tiles(chunk, TILE_WALL, 24, 44, 25, 46)
    fill_tiles(chunk, TILE_WALL, 32, 48, 33, 50)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 54)
    fill_tiles(chunk, TILE_WALL, 60, 46, 61, 48)

    # ================================================================
    # SESSION 14 FIDELITY PASS — ArchdragonPeak DS3 terrain details
    # ================================================================
    # Serpent-Man statue pedestals (DS3: serpent imagery carved into walls)
    fill_tiles(chunk, TILE_WALL, 40, 92, 41, 93)
    fill_tiles(chunk, TILE_WALL, 50, 96, 51, 97)
    fill_tiles(chunk, TILE_WALL, 60, 100, 61, 101)
    fill_tiles(chunk, TILE_WALL, 44, 104, 45, 105)
    # Wyvern perch — petrified dragon claw stones (DS3: dead wyvern on bridge)
    fill_tiles(chunk, TILE_WALL, 42, 56, 43, 57)
    fill_tiles(chunk, TILE_WALL, 54, 62, 55, 63)
    fill_tiles(chunk, TILE_WALL, 66, 68, 67, 69)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    # Storm ridge — wind-eroded rock formations (DS3: storm-swept ridge path)
    fill_tiles(chunk, TILE_WALL, 100, 34, 101, 35)
    fill_tiles(chunk, TILE_WALL, 108, 42, 109, 43)
    fill_tiles(chunk, TILE_WALL, 116, 36, 117, 37)
    fill_tiles(chunk, TILE_WALL, 124, 44, 125, 45)
    # Nameless King arena — lightning-scorched stone circles (DS3: ritual stones)
    fill_tiles(chunk, TILE_WALL, 132, 80, 133, 81)
    fill_tiles(chunk, TILE_WALL, 140, 84, 141, 85)
    fill_tiles(chunk, TILE_WALL, 136, 92, 137, 93)
    fill_tiles(chunk, TILE_WALL, 144, 96, 145, 97)
    # Dragon-Kin Mausoleum — meditation alcove stones (DS3: dragon-kin meditate here)
    fill_tiles(chunk, TILE_WALL, 70, 44, 71, 45)
    fill_tiles(chunk, TILE_WALL, 78, 48, 79, 49)
    fill_tiles(chunk, TILE_WALL, 86, 44, 87, 45)
    fill_tiles(chunk, TILE_WALL, 94, 50, 95, 51)

    # ================================================================
    # SESSION 17 FIDELITY PASS — ArchdragonPeak DS3 mountain details
    # ================================================================
    # Mountain entry — wind-eroded stone steps (DS3: steep mountain ascent)
    fill_tiles(chunk, TILE_WALL, 14, 110, 15, 112)
    fill_tiles(chunk, TILE_WALL, 20, 116, 21, 118)
    fill_tiles(chunk, TILE_WALL, 26, 122, 27, 124)
    fill_tiles(chunk, TILE_WALL, 32, 128, 33, 130)
    fill_tiles(chunk, TILE_WALL, 38, 134, 39, 136)
    # Serpent barracks — training ground debris (DS3: serpent-man training area)
    fill_tiles(chunk, TILE_WALL, 44, 96, 45, 98)
    fill_tiles(chunk, TILE_WALL, 50, 102, 51, 104)
    fill_tiles(chunk, TILE_WALL, 56, 96, 57, 98)
    fill_tiles(chunk, TILE_WALL, 62, 100, 63, 102)
    # Wyvern arena — dragon bone cluster (DS3: massive dragon skeleton)
    fill_tiles(chunk, TILE_WALL, 48, 64, 49, 66)
    fill_tiles(chunk, TILE_WALL, 56, 68, 57, 70)
    fill_tiles(chunk, TILE_WALL, 64, 72, 65, 74)
    fill_tiles(chunk, TILE_WALL, 72, 76, 73, 78)
    # Storm path — lightning-blasted rocks (DS3: storm-swept ridge)
    fill_tiles(chunk, TILE_WALL, 96, 40, 97, 42)
    fill_tiles(chunk, TILE_WALL, 104, 44, 105, 46)
    fill_tiles(chunk, TILE_WALL, 112, 38, 113, 40)
    fill_tiles(chunk, TILE_WALL, 120, 42, 121, 44)
    # Great Belfry — bell tower buttresses (DS3: massive bell tower)
    fill_tiles(chunk, TILE_WALL, 108, 20, 109, 22)
    fill_tiles(chunk, TILE_WALL, 116, 24, 117, 26)
    fill_tiles(chunk, TILE_WALL, 124, 20, 125, 22)
    fill_tiles(chunk, TILE_WALL, 132, 24, 133, 26)
    # Nameless King arena — storm altar debris (DS3: peak-top arena with storm)
    fill_tiles(chunk, TILE_WALL, 140, 96, 141, 98)
    fill_tiles(chunk, TILE_WALL, 148, 100, 149, 102)
    fill_tiles(chunk, TILE_WALL, 136, 104, 137, 106)
    fill_tiles(chunk, TILE_WALL, 144, 108, 145, 110)

    # ================================================================
    # SESSION 19 FIDELITY PASS — ArchdragonPeak DS3 mountain depth
    # ================================================================
    # Serpent Man temple — stone altar debris (DS3: ancient dragon temple)
    fill_tiles(chunk, TILE_WALL, 28, 44, 29, 46)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 50)
    fill_tiles(chunk, TILE_WALL, 44, 44, 45, 46)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 54)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 50)
    # Dragonkin Mausoleum — dragon skeleton debris (DS3: dragon remains in mausoleum)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 58)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 62)
    fill_tiles(chunk, TILE_WALL, 88, 58, 89, 60)
    fill_tiles(chunk, TILE_WALL, 96, 64, 97, 66)
    fill_tiles(chunk, TILE_WALL, 104, 62, 105, 64)
    # Nameless King peak — storm-worn pillars (DS3: wind-battered peak arena)
    fill_tiles(chunk, TILE_WALL, 142, 112, 143, 114)
    fill_tiles(chunk, TILE_WALL, 150, 116, 151, 118)
    fill_tiles(chunk, TILE_WALL, 138, 118, 139, 120)
    fill_tiles(chunk, TILE_WALL, 146, 122, 147, 124)
    fill_tiles(chunk, TILE_WALL, 154, 120, 155, 122)

    # ================================================================
    # SESSION 22 FIDELITY PASS — ArchdragonPeak DS3 dragon ruins details
    # ================================================================
    # Dragon skeleton debris (DS3: massive dragon bones scattered around peak)
    fill_tiles(chunk, TILE_WALL, 22, 34, 23, 35)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 39)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    fill_tiles(chunk, TILE_WALL, 40, 46, 41, 47)
    # Serpent Man totem bases (DS3: stone serpent totems)
    fill_tiles(chunk, TILE_WALL, 46, 50, 47, 51)
    fill_tiles(chunk, TILE_WALL, 52, 54, 53, 55)
    fill_tiles(chunk, TILE_WALL, 58, 58, 59, 59)
    fill_tiles(chunk, TILE_WALL, 64, 62, 65, 63)
    # Ancient dragon altar stones (DS3: dragon stones for meditation)
    fill_tiles(chunk, TILE_WALL, 70, 66, 71, 67)
    fill_tiles(chunk, TILE_WALL, 76, 70, 77, 71)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    # Nameless King perch debris (DS3: storm cloud debris near boss arena)
    fill_tiles(chunk, TILE_WALL, 94, 82, 95, 83)
    fill_tiles(chunk, TILE_WALL, 100, 86, 101, 87)
    fill_tiles(chunk, TILE_WALL, 106, 90, 107, 91)
    fill_tiles(chunk, TILE_WALL, 112, 94, 113, 95)

    # ================================================================
    # SESSION 25 FIDELITY PASS — ArchdragonPeak DS3 dragon peak details
    # ================================================================
    # Dragon stone meditation circles (DS3: stone circles for Path of the Dragon gesture)
    fill_tiles(chunk, TILE_WALL, 16, 28, 17, 29)
    fill_tiles(chunk, TILE_WALL, 22, 32, 23, 33)
    fill_tiles(chunk, TILE_WALL, 28, 36, 29, 37)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 41)
    # Serpent Man shrine stones (DS3: serpent-man worship stones)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 57)
    # Havel's armor debris (DS3: Havel's equipment on the peak)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    fill_tiles(chunk, TILE_WALL, 70, 64, 71, 65)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 69)
    fill_tiles(chunk, TILE_WALL, 82, 72, 83, 73)
    # Nameless King storm debris (DS3: storm debris near the arena)
    fill_tiles(chunk, TILE_WALL, 88, 76, 89, 77)
    fill_tiles(chunk, TILE_WALL, 94, 80, 95, 81)
    fill_tiles(chunk, TILE_WALL, 100, 84, 101, 85)
    fill_tiles(chunk, TILE_WALL, 106, 88, 107, 89)

    # ================================================================
    # SESSION 29 FIDELITY PASS — ArchdragonPeak DS3 dragon peak details
    # ================================================================
    # Dragon stone circle (DS3: petrified dragon in meditation pose)
    fill_tiles(chunk, TILE_WALL, 20, 36, 21, 37)
    fill_tiles(chunk, TILE_WALL, 26, 40, 27, 41)
    fill_tiles(chunk, TILE_WALL, 32, 44, 33, 45)
    fill_tiles(chunk, TILE_WALL, 38, 48, 39, 49)
    # Serpent Man altar stones (DS3: altar stones for dragon transformation)
    fill_tiles(chunk, TILE_WALL, 44, 52, 45, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    fill_tiles(chunk, TILE_WALL, 62, 64, 63, 65)
    # Twinkling Dragon torso stones (DS3: dragon torso stone location)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 74, 72, 75, 73)
    fill_tiles(chunk, TILE_WALL, 80, 76, 81, 77)
    fill_tiles(chunk, TILE_WALL, 86, 80, 87, 81)
    # Nameless King storm altar (DS3: storm altar at the peak summit)
    fill_tiles(chunk, TILE_WALL, 92, 84, 93, 85)
    fill_tiles(chunk, TILE_WALL, 98, 88, 99, 89)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 93)
    fill_tiles(chunk, TILE_WALL, 110, 96, 111, 97)

    # SESSION 36 FIDELITY PASS — Archdragon Peak DS3 details
    # DS3: Serpent totem poles, dragon bone piles, stone meditation circles
    for tx in range(50, 90, 8):
        fill_tiles(chunk, TILE_WALL, tx, 60, tx+2, 62)             # Serpent totem poles
        fill_tiles(chunk, TILE_WALL, tx, 100, tx+2, 102)
    for tx in range(100, 140, 8):
        fill_tiles(chunk, TILE_WALL, tx, 55, tx+1, 56)             # Stone dragon teeth
        fill_tiles(chunk, TILE_WALL, tx, 105, tx+1, 106)
    fill_tiles(chunk, TILE_WALL, 40, 80, 43, 83)                    # Dragon skeleton skull
    fill_tiles(chunk, TILE_WALL, 130, 70, 132, 72)                  # Ancient wyvern bones
    fill_tiles(chunk, TILE_WALL, 60, 115, 62, 117)                  # Meditation platform
    for ty in range(30, 60, 10):
        fill_tiles(chunk, TILE_WALL, 75, ty, 76, ty+1)              # Cliff face detail
    fill_tiles(chunk, TILE_WALL, 115, 90, 117, 92)                  # Storm damaged pillar
    # SESSION 39 FIDELITY PASS — Archdragon Peak DS3 details
    # DS3: Dragon skeleton archways, serpent statues, meditation stones, storm markers
    for tx in range(30, 70, 8):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+3, 37)             # Dragon rib archways
        fill_tiles(chunk, TILE_WALL, tx, 95, tx+3, 97)
    for tx in range(80, 130, 8):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 42)             # Serpent statue bases
        fill_tiles(chunk, TILE_WALL, tx, 100, tx+1, 102)
    for ty in range(30, 80, 10):
        fill_tiles(chunk, TILE_WALL, 50, ty, 51, ty+1)             # Stone path markers
        fill_tiles(chunk, TILE_WALL, 110, ty, 111, ty+1)
    fill_tiles(chunk, TILE_WALL, 60, 80, 62, 82)                    # Meditation stone circle
    fill_tiles(chunk, TILE_WALL, 130, 60, 132, 62)                  # Ancient dragon skull
    fill_tiles(chunk, TILE_WALL, 90, 110, 92, 112)                  # Storm debris pile
    # --- SESSION 47 terrain (Archdragon Peak) ---
    # DS3: Dragon skeleton skull
    for tx in range(80, 90):
        chunk[30][tx] = TILE_WALLTOP
    # Serpent totem pillars
    for tx, ty in [(35, 25), (50, 30), (65, 28)]:
        chunk[ty][tx] = TILE_WALL
    # Meditation circle stones
    for tx in range(20, 28):
        chunk[45][tx] = TILE_WALLTOP
    # Ancient dragon bone fragments
    for tx, ty in [(70, 40), (85, 45), (100, 38)]:
        chunk[ty][tx] = TILE_WALLTOP
    # Stone staircase to Nameless King arena
    for ty in range(50, 58):
        chunk[ty][110] = TILE_WALL

    # --- SESSION 52 terrain (Archdragon Peak) ---
    # DS3: Ancient Wyvern skeleton in the courtyard
    for tx in range(40, 52):
        chunk[60][tx] = TILE_WALLTOP  # rib bones
    # Serpent statue altar (DS3: snake worship altar)
    for tx in range(55, 60):
        chunk[65][tx] = TILE_WALLTOP  # altar stone
    chunk[66][57] = TILE_WALL  # altar pillar
    # Dragon egg nests (DS3: eggs in the peak)
    for tx, ty in [(70, 50), (82, 55)]:
        chunk[ty][tx] = TILE_WALLTOP  # egg nest
    # Bell tower structure (DS3: the great bell)
    for ty in range(35, 42):
        chunk[ty][95] = TILE_WALL  # tower wall

    # --- SESSION 58 terrain (Archdragon Peak) ---
    # DS3: Nameless King arena storm clouds (stone markers for the arena)
    for tx in range(100, 112):
        if tx % 2 == 0:
            chunk[68][tx] = TILE_WALLTOP  # storm marker
    # Ancient dragon bone ridge
    for tx in range(30, 40):
        chunk[55][tx] = TILE_WALLTOP  # bone ridge
    # Serpent man altar
    for ty in range(40, 45):
        chunk[ty][20] = TILE_WALL  # altar wall
    # Dragon egg cluster
    for tx, ty in [(60, 48), (68, 52)]:
        chunk[ty][tx] = TILE_WALL  # egg stone

    # --- SESSION 89 DS3 terrain (Archdragon Peak detail pass) ---
    # DS3: Dragon bones (massive skeletal structures)
    for tx in [20, 25, 30, 35, 40, 45]:
        for ty in [18, 19]:
            chunk[tx][ty] = TILE_WALL
    for tx in [50, 55, 60, 65, 70]:
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Serpent totems (stone pillars with serpent carvings)
    for tx in [25, 40, 55, 70, 85]:
        for ty in range(15, 22):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Meditation circles (stone rings for path of the dragon)
    for tx in range(45, 55):
        for ty in [40, 48]:
            chunk[tx][ty] = TILE_WALL
    for tx in [45, 55]:
        for ty in range(40, 49):
            chunk[tx][ty] = TILE_WALL
    for tx in range(46, 55):
        for ty in range(41, 48):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Bone fragments scattered across the peak
    for tx in [15, 22, 30, 38, 45, 52, 60, 68, 75, 82, 90]:
        for ty in [25, 28]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Grand staircase to the peak
    for tx in range(60, 80):
        for ty in range(50, 70):
            chunk[tx][ty] = TILE_GROUND
    for tx in [60, 80]:
        for ty in range(50, 71):
            chunk[tx][ty] = TILE_WALL
    # DS3: Nameless King's arena (open peak platform)
    for tx in range(80, 110):
        for ty in range(30, 50):
            chunk[tx][ty] = TILE_GROUND
    for tx in [80, 110]:
        for ty in range(30, 51):
            chunk[tx][ty] = TILE_WALL
    for tx in range(80, 111):
        for ty in [30, 50]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Havel's tower (stone structure)
    for tx in range(100, 112):
        for ty in [55, 65]:
            chunk[tx][ty] = TILE_WALL
    for tx in [100, 112]:
        for ty in range(55, 66):
            chunk[tx][ty] = TILE_WALL
    for tx in range(100, 113):
        chunk[tx][54] = TILE_WALLTOP

    # --- SESSION 93 DS3 terrain round 2 (Archdragon Peak) ---
    # DS3: Ancient dragon skeleton (massive bone structure)
    for tx in range(30, 50):
        for ty in [22, 23]:
            chunk[tx][ty] = TILE_WALL
    for tx in [30, 35, 40, 45, 50]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Serpent man ritual circle
    for tx in range(55, 65):
        for ty in range(35, 42):
            chunk[tx][ty] = TILE_GROUND
    for tx in [55, 65]:
        for ty in range(35, 43):
            chunk[tx][ty] = TILE_WALL
    for tx in range(55, 66):
        for ty in [35, 42]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Path of the Dragon meditation spot
    for tx in range(45, 52):
        for ty in range(43, 48):
            chunk[tx][ty] = TILE_GROUND
    for tx in [45, 52]:
        for ty in range(43, 49):
            chunk[tx][ty] = TILE_WALL
    # DS3: Drakeblood Knight altar
    for tx in range(70, 78):
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    for tx in [70, 78]:
        for ty in range(55, 57):
            chunk[tx][ty] = TILE_WALL
    for tx in range(70, 79):
        chunk[tx][54] = TILE_WALLTOP
    # DS3: Nameless King arena detail (storm clouds = wall top)
    for tx in range(82, 108):
        chunk[tx][25] = TILE_WALL
        chunk[tx][24] = TILE_WALLTOP
    for tx in range(82, 108):
        chunk[tx][48] = TILE_WALL
    # DS3: Twisted dragon head stone
    for tx in [90, 91, 92]:
        for ty in [55, 56, 57]:
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/ArchdragonPeak.json") as _f:

        _doc = _json.load(_f)

    # Wider connectivity corridors between sections
    fill_tiles(chunk, TILE_GROUND, 25, 95, 50, 115)   # Entry to barracks
    fill_tiles(chunk, TILE_GROUND, 40, 70, 65, 90)    # Barracks to wyvern
    fill_tiles(chunk, TILE_GROUND, 65, 40, 95, 60)    # Wyvern to mausoleum
    fill_tiles(chunk, TILE_GROUND, 90, 25, 130, 50)   # Storm path to belfry
    fill_tiles(chunk, TILE_GROUND, 110, 35, 140, 70)  # Belfry to Nameless arena
    fill_tiles(chunk, TILE_GROUND, 80, 55, 120, 80)   # Mausoleum to Nameless arena

    for _sec in _doc.get("map_layout", {}).get("sections", []):

        _sx, _sy = _sec["x"] // 16, _sec["y"] // 16

        _sw, _sh = _sec["w"] // 16, _sec["h"] // 16

        _features = " ".join(f for f in _sec.get("terrain_features", []) if isinstance(f, str))

        _tile = poison_tile(_features)

        fill_tiles(chunk, _tile, _sx + 1, _sy + 1, _sx + _sw - 2, _sy + _sh - 2)

    # Connect sections with corridors

    _centers = []

    for _sec in _doc.get("map_layout", {}).get("sections", []):

        _cx = (_sec["x"] + _sec["w"] // 2) // 16

        _cy = (_sec["y"] + _sec["h"] // 2) // 16

        _centers.append((_cx, _cy))

    for _i in range(len(_centers) - 1):

        _cx1, _cy1 = _centers[_i]

        _cx2, _cy2 = _centers[_i + 1]

        carve_corridor(chunk, _cx1, _cy1, _cx2, _cy2, width=5)

    # Ensure bonfire/boss positions have ground

    for _bf in _doc.get("bonfires", []):

        _bx, _by = _bf["x"] // 16, _bf["y"] // 16

        fill_tiles(chunk, TILE_GROUND, _bx - 3, _by - 3, _bx + 3, _by + 3)

    _boss = _doc.get("boss")

    if _boss:

        for _b in (_boss if isinstance(_boss, list) else [_boss]):

            _bx, _by = _b.get("x", 0) // 16, _b.get("y", 0) // 16

            fill_tiles(chunk, TILE_GROUND, _bx - 5, _by - 5, _bx + 5, _by + 5)

    for _fg in _doc.get("fog_gates", []):

        _fx, _fy = _fg["x"] // 16, _fg["y"] // 16

        fill_tiles(chunk, TILE_GROUND, _fx - 3, _fy - 3, _fx + 3, _fy + 3)
    # Add terrain feature obstacles (walls) from JSON doc
    for _sec in _doc.get("map_layout", {}).get("sections", []):
        for _feat in _sec.get("terrain_features", []):
            if not isinstance(_feat, dict):
                continue
            _fk = _feat.get("kind", "")
            if _fk in ("tombstone", "bookshelf_wall", "pillar", "throne_pillar",
                        "barracks_wall", "bell_tower_column", "shrine_wall", "broken_wall",
                        "barricade", "collapsed_wall", "desk_cluster",
                        "roof_structure", "chimney", "armor_display", "iron_girder",
                        "coffin", "dragon_altar", "serpent_statue",
                        "arena_ruin", "ruined_pillar"):
                _fx2 = _feat["x"] // 16
                _fy2 = _feat["y"] // 16
                _fw = max(1, _feat["w"] // 16)
                _fh = max(1, _feat["h"] // 16)
                fill_tiles(chunk, TILE_WALL, _fx2, _fy2, _fx2 + _fw - 1, _fy2 + _fh - 1)

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0]))
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100
    # print(f"  ArchdragonPeak (faithful DS3 layout) "
    # f"ground={pct:.1f}% connectivity={coverage}%")
    return "ArchdragonPeak", chunk, entities
