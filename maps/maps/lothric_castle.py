from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_lothric_castle():
    """Lothric Castle - Dragonslayer Armour boss arena.

    Faithful DS3 layout (spatial progression on 160x160 grid):
    Entry from AnorLondo (west) -> castle gate -> outer corridor -> dragon barracks
    (open, with dragon wall obstacles) -> inner castle stairs -> wall bridge
    (Dragonslayer Armour arena, large open area) -> Grand Archives exit (NE).
    Side path south to ConsumedKingsGarden.
    """
    chunk = new_chunk(320, 256)
    entities = []

    # ================================================================
    # TERRAIN
    # ================================================================

    # 1. Castle gate (SW entry from AnorLondo)
    fill_tiles(chunk, TILE_GROUND, 6, 18, 35, 45)
    # Pillar walls flanking the gate
    fill_tiles(chunk, TILE_WALL, 12, 24, 14, 30)
    fill_tiles(chunk, TILE_WALL, 24, 28, 26, 34)

    # 2. Outer corridor (east from gate)
    fill_tiles(chunk, TILE_GROUND, 30, 22, 68, 48)
    # Statue walls along corridor
    fill_tiles(chunk, TILE_WALL, 42, 28, 44, 33)
    fill_tiles(chunk, TILE_WALL, 56, 35, 58, 40)

    # 3. Dragon barracks (open area NE)
    fill_tiles(chunk, TILE_GROUND, 58, 10, 102, 40)
    # Dragon skeleton wall obstacles
    fill_tiles(chunk, TILE_WALL, 68, 15, 72, 20)
    fill_tiles(chunk, TILE_WALL, 88, 28, 92, 33)

    # 4. Inner stairs (narrow passage NE)
    fill_tiles(chunk, TILE_GROUND, 95, 35, 118, 58)
    # Wall obstacles along stairs
    fill_tiles(chunk, TILE_WALL, 102, 40, 104, 44)
    fill_tiles(chunk, TILE_WALL, 110, 48, 112, 52)

    # 5. Wall bridge / Dragonslayer Armour arena (NE large)
    fill_tiles(chunk, TILE_GROUND, 108, 50, 155, 88)
    # Rounded arena shape
    carve_ellipse(chunk, 132, 68, 20, 16)
    # Arena pillars
    fill_tiles(chunk, TILE_WALL, 118, 58, 120, 63)
    fill_tiles(chunk, TILE_WALL, 145, 72, 147, 77)

    # 6. Garden side path (south)
    fill_tiles(chunk, TILE_GROUND, 35, 45, 55, 68)
    carve_ellipse(chunk, 45, 56, 8, 6)

    # 7. Grand Archives exit (far NE)
    fill_tiles(chunk, TILE_GROUND, 148, 55, 158, 72)

    # --- Connections between areas ---
    fill_tiles(chunk, TILE_GROUND, 58, 28, 62, 42)     # Corridor -> Dragon barracks
    fill_tiles(chunk, TILE_GROUND, 95, 25, 102, 38)    # Barracks -> Inner stairs
    fill_tiles(chunk, TILE_GROUND, 112, 52, 120, 58)   # Stairs -> Arena
    fill_tiles(chunk, TILE_GROUND, 42, 45, 48, 50)     # Corridor -> Garden side path

    # ================================================================
    # ADDITIONAL INTERNAL STRUCTURES — castle architecture
    # ================================================================
    # Castle gate battlements
    fill_tiles(chunk, TILE_WALL, 10, 20, 11, 24)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 26)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 38)
    # Corridor pillars
    fill_tiles(chunk, TILE_WALL, 38, 28, 39, 32)
    fill_tiles(chunk, TILE_WALL, 48, 34, 49, 38)
    fill_tiles(chunk, TILE_WALL, 62, 30, 63, 34)
    # Dragon barracks — more dragon bones and debris
    fill_tiles(chunk, TILE_WALL, 72, 12, 74, 15)
    fill_tiles(chunk, TILE_WALL, 82, 16, 84, 18)
    fill_tiles(chunk, TILE_WALL, 92, 22, 94, 25)
    fill_tiles(chunk, TILE_WALL, 76, 30, 78, 32)
    fill_tiles(chunk, TILE_WALL, 96, 34, 98, 37)
    fill_tiles(chunk, TILE_WALL, 65, 18, 67, 20)
    # Inner stairs — wall buttresses
    fill_tiles(chunk, TILE_WALL, 98, 38, 100, 40)
    fill_tiles(chunk, TILE_WALL, 105, 45, 107, 47)
    fill_tiles(chunk, TILE_WALL, 115, 52, 117, 55)
    # Arena — Dragonslayer Armour arena pillars
    fill_tiles(chunk, TILE_WALL, 122, 55, 124, 58)
    fill_tiles(chunk, TILE_WALL, 138, 60, 140, 63)
    fill_tiles(chunk, TILE_WALL, 152, 68, 154, 72)
    fill_tiles(chunk, TILE_WALL, 128, 78, 130, 82)
    fill_tiles(chunk, TILE_WALL, 142, 82, 144, 86)
    fill_tiles(chunk, TILE_WALL, 135, 72, 137, 75)
    # Garden side path — overgrown walls
    fill_tiles(chunk, TILE_WALL, 40, 52, 42, 55)
    fill_tiles(chunk, TILE_WALL, 50, 58, 52, 60)
    fill_tiles(chunk, TILE_WALL, 38, 62, 40, 65)

    # ================================================================
    # ADDITIONAL DS3 CASTLE ARCHITECTURE — Lothric Castle fidelity
    # ================================================================
    # Castle gate — entrance arch walls (DS3: grand stone archway from Anor Londo)
    fill_tiles(chunk, TILE_WALL, 8, 22, 10, 26)
    fill_tiles(chunk, TILE_WALL, 20, 32, 22, 36)
    fill_tiles(chunk, TILE_WALL, 16, 38, 18, 42)
    fill_tiles(chunk, TILE_WALL, 30, 40, 32, 44)
    # Outer corridor — stone arches and buttresses (DS3: vaulted corridor)
    fill_tiles(chunk, TILE_WALL, 34, 24, 36, 28)
    fill_tiles(chunk, TILE_WALL, 52, 28, 54, 32)
    fill_tiles(chunk, TILE_WALL, 60, 34, 62, 38)
    fill_tiles(chunk, TILE_WALL, 44, 40, 46, 44)
    fill_tiles(chunk, TILE_WALL, 55, 42, 57, 46)
    # Dragon barracks — dragon ribcage and skull debris (DS3: two dead wyverns)
    fill_tiles(chunk, TILE_WALL, 70, 22, 71, 24)
    fill_tiles(chunk, TILE_WALL, 74, 26, 75, 28)
    fill_tiles(chunk, TILE_WALL, 80, 20, 81, 22)
    fill_tiles(chunk, TILE_WALL, 86, 24, 87, 26)
    fill_tiles(chunk, TILE_WALL, 90, 18, 91, 20)
    fill_tiles(chunk, TILE_WALL, 94, 30, 95, 32)
    fill_tiles(chunk, TILE_WALL, 78, 32, 79, 34)
    fill_tiles(chunk, TILE_WALL, 84, 36, 85, 38)
    # Inner stairs — narrow passage walls (DS3: tight staircase with hollows)
    fill_tiles(chunk, TILE_WALL, 96, 36, 98, 38)
    fill_tiles(chunk, TILE_WALL, 100, 42, 102, 44)
    fill_tiles(chunk, TILE_WALL, 108, 46, 110, 48)
    fill_tiles(chunk, TILE_WALL, 114, 52, 116, 54)
    fill_tiles(chunk, TILE_WALL, 120, 56, 122, 58)
    # Arena perimeter — Dragonslayer Armour fights on castle wall (DS3: open parapet)
    fill_tiles(chunk, TILE_WALL, 112, 62, 114, 65)
    fill_tiles(chunk, TILE_WALL, 130, 55, 132, 58)
    fill_tiles(chunk, TILE_WALL, 148, 60, 150, 63)
    fill_tiles(chunk, TILE_WALL, 155, 72, 157, 75)
    fill_tiles(chunk, TILE_WALL, 148, 82, 150, 85)
    fill_tiles(chunk, TILE_WALL, 135, 85, 137, 88)
    fill_tiles(chunk, TILE_WALL, 120, 82, 122, 85)
    fill_tiles(chunk, TILE_WALL, 112, 78, 114, 80)
    # Garden side path — overgrown ruin walls (DS3: consumed garden area)
    fill_tiles(chunk, TILE_WALL, 36, 48, 38, 50)
    fill_tiles(chunk, TILE_WALL, 44, 56, 46, 58)
    fill_tiles(chunk, TILE_WALL, 52, 62, 54, 64)
    fill_tiles(chunk, TILE_WALL, 48, 66, 50, 68)
    # Grand Archives approach — bookshelves and stone arches
    fill_tiles(chunk, TILE_WALL, 150, 58, 152, 60)
    fill_tiles(chunk, TILE_WALL, 154, 64, 156, 66)

    # ================================================================
    # ADDITIONAL DS3 LOTHRIC CASTLE DETAILS — wyvern bones, church, parapets
    # ================================================================
    # Castle gate — fortified entry (DS3: grand stone archway with Lothric banners)
    fill_tiles(chunk, TILE_WALL, 6, 22, 8, 24)
    fill_tiles(chunk, TILE_WALL, 12, 26, 14, 28)
    fill_tiles(chunk, TILE_WALL, 22, 28, 24, 30)
    fill_tiles(chunk, TILE_WALL, 26, 36, 28, 38)
    fill_tiles(chunk, TILE_WALL, 15, 40, 17, 42)
    fill_tiles(chunk, TILE_WALL, 32, 42, 34, 44)
    # Dragon barracks — wyvern ribcage arches and burning debris (DS3: two dead wyverns, one with Pus of Man)
    fill_tiles(chunk, TILE_WALL, 60, 14, 62, 16)
    fill_tiles(chunk, TILE_WALL, 64, 20, 66, 22)
    fill_tiles(chunk, TILE_WALL, 84, 14, 86, 16)
    fill_tiles(chunk, TILE_WALL, 88, 20, 90, 22)
    fill_tiles(chunk, TILE_WALL, 96, 26, 98, 28)
    fill_tiles(chunk, TILE_WALL, 100, 30, 102, 32)
    fill_tiles(chunk, TILE_WALL, 78, 26, 80, 28)
    fill_tiles(chunk, TILE_WALL, 72, 34, 74, 36)
    fill_tiles(chunk, TILE_WALL, 68, 10, 70, 12)
    # Church interior — stone pews and altar walls (DS3: Emma's cathedral with Lothric banners)
    fill_tiles(chunk, TILE_WALL, 120, 60, 122, 62)
    fill_tiles(chunk, TILE_WALL, 126, 64, 128, 66)
    fill_tiles(chunk, TILE_WALL, 132, 70, 134, 72)
    fill_tiles(chunk, TILE_WALL, 136, 74, 138, 76)
    fill_tiles(chunk, TILE_WALL, 124, 68, 126, 70)
    fill_tiles(chunk, TILE_WALL, 130, 66, 132, 68)
    # Inner stairs — narrow castle passage (DS3: tight spiral staircase with hollows)
    fill_tiles(chunk, TILE_WALL, 106, 40, 108, 42)
    fill_tiles(chunk, TILE_WALL, 118, 50, 120, 52)
    # Arena perimeter — castle parapet walls (DS3: Dragonslayer Armour on open castle bridge)
    fill_tiles(chunk, TILE_WALL, 116, 70, 118, 72)
    fill_tiles(chunk, TILE_WALL, 140, 76, 142, 78)
    fill_tiles(chunk, TILE_WALL, 146, 80, 148, 82)
    fill_tiles(chunk, TILE_WALL, 125, 85, 127, 87)
    fill_tiles(chunk, TILE_WALL, 150, 74, 152, 76)
    # Grand Archives approach — stone staircase and fountain (DS3: grand fountain before Archives)
    fill_tiles(chunk, TILE_WALL, 144, 56, 146, 58)
    fill_tiles(chunk, TILE_WALL, 148, 62, 150, 64)
    fill_tiles(chunk, TILE_WALL, 152, 70, 154, 72)
    # Garden path — overgrown arches and crumbling walls (DS3: consumed garden ruins)
    fill_tiles(chunk, TILE_WALL, 34, 54, 36, 56)
    fill_tiles(chunk, TILE_WALL, 42, 60, 44, 62)
    fill_tiles(chunk, TILE_WALL, 54, 64, 56, 66)

    # === SESSION 6 FIDELITY PASS — Lothric Castle ===
    # Castle gate — more entry fortification (DS3: grand Lothric Castle gate)
    fill_tiles(chunk, TILE_WALL, 8, 18, 10, 20)
    fill_tiles(chunk, TILE_WALL, 22, 36, 24, 38)
    fill_tiles(chunk, TILE_WALL, 14, 42, 16, 44)
    fill_tiles(chunk, TILE_WALL, 28, 44, 30, 46)
    # Outer corridor — more stone arches (DS3: vaulted corridor with knight statues)
    fill_tiles(chunk, TILE_WALL, 36, 30, 38, 32)
    fill_tiles(chunk, TILE_WALL, 46, 36, 48, 38)
    fill_tiles(chunk, TILE_WALL, 58, 38, 60, 40)
    fill_tiles(chunk, TILE_WALL, 50, 44, 52, 46)
    fill_tiles(chunk, TILE_WALL, 40, 42, 42, 44)
    # Dragon barracks — more wyvern debris (DS3: massive dragon skeletons)
    fill_tiles(chunk, TILE_WALL, 62, 16, 64, 18)
    fill_tiles(chunk, TILE_WALL, 66, 22, 68, 24)
    fill_tiles(chunk, TILE_WALL, 82, 28, 84, 30)
    fill_tiles(chunk, TILE_WALL, 92, 20, 94, 22)
    fill_tiles(chunk, TILE_WALL, 98, 32, 100, 34)
    fill_tiles(chunk, TILE_WALL, 76, 34, 78, 36)
    # Inner stairs — more passage walls (DS3: tight castle staircase)
    fill_tiles(chunk, TILE_WALL, 104, 44, 106, 46)
    fill_tiles(chunk, TILE_WALL, 112, 48, 114, 50)
    fill_tiles(chunk, TILE_WALL, 116, 54, 118, 56)
    fill_tiles(chunk, TILE_WALL, 122, 58, 124, 60)
    # Arena — more parapet walls (DS3: open castle wall bridge)
    fill_tiles(chunk, TILE_WALL, 110, 66, 112, 68)
    fill_tiles(chunk, TILE_WALL, 126, 62, 128, 64)
    fill_tiles(chunk, TILE_WALL, 144, 66, 146, 68)
    fill_tiles(chunk, TILE_WALL, 152, 76, 154, 78)
    fill_tiles(chunk, TILE_WALL, 142, 84, 144, 86)
    fill_tiles(chunk, TILE_WALL, 118, 80, 120, 82)
    fill_tiles(chunk, TILE_WALL, 132, 88, 134, 90)
    fill_tiles(chunk, TILE_WALL, 150, 88, 152, 90)
    # Garden side path — more overgrown walls (DS3: consumed garden)
    fill_tiles(chunk, TILE_WALL, 38, 56, 40, 58)
    fill_tiles(chunk, TILE_WALL, 46, 64, 48, 66)
    fill_tiles(chunk, TILE_WALL, 56, 60, 58, 62)
    # Grand Archives approach — stone pillars (DS3: grand fountain courtyard)
    fill_tiles(chunk, TILE_WALL, 146, 60, 148, 62)
    fill_tiles(chunk, TILE_WALL, 156, 68, 158, 70)

    # ================================================================
    # SESSION 9 FIDELITY PASS — LothricCastle architectural details
    # ================================================================
    # Dragon courtyard — burnt stone debris (DS3: dragon breath scorches area)
    fill_tiles(chunk, TILE_WALL, 20, 34, 21, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 16, 42, 17, 43)
    fill_tiles(chunk, TILE_WALL, 28, 30, 29, 31)
    fill_tiles(chunk, TILE_WALL, 22, 46, 23, 47)
    # Lothric Knight barracks — weapon rack stones (DS3: knight garrison area)
    fill_tiles(chunk, TILE_WALL, 36, 50, 37, 51)
    fill_tiles(chunk, TILE_WALL, 40, 54, 41, 55)
    fill_tiles(chunk, TILE_WALL, 32, 58, 33, 59)
    fill_tiles(chunk, TILE_WALL, 44, 48, 45, 49)
    fill_tiles(chunk, TILE_WALL, 38, 62, 39, 63)
    # Wyvern perch — scorched tower stones (DS3: wyvern roosts on castle wall)
    fill_tiles(chunk, TILE_WALL, 50, 40, 51, 41)
    fill_tiles(chunk, TILE_WALL, 54, 44, 55, 45)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 58, 38, 59, 39)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    # Grand Archives fountain courtyard — ornate fountain stones
    fill_tiles(chunk, TILE_WALL, 142, 56, 143, 57)
    fill_tiles(chunk, TILE_WALL, 150, 64, 151, 65)
    fill_tiles(chunk, TILE_WALL, 138, 68, 139, 69)
    fill_tiles(chunk, TILE_WALL, 154, 60, 155, 61)
    # Dragonslayer Armour arena — shattered monument stones (DS3: storm-swept rooftop)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 126, 84, 127, 85)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 130, 76, 131, 77)
    fill_tiles(chunk, TILE_WALL, 122, 90, 123, 91)
    # Dancer's cathedral — stained glass debris (DS3: cathedral with stained glass)
    fill_tiles(chunk, TILE_WALL, 60, 28, 61, 29)
    fill_tiles(chunk, TILE_WALL, 66, 32, 67, 33)
    fill_tiles(chunk, TILE_WALL, 56, 36, 57, 37)
    fill_tiles(chunk, TILE_WALL, 70, 26, 71, 27)
    fill_tiles(chunk, TILE_WALL, 64, 38, 65, 39)

    # ================================================================
    # SESSION 12 FIDELITY PASS — LothricCastle fine architectural details
    # ================================================================
    # Dragon Barracks — scorched stone walls (DS3: dragon-scorched fortress)
    fill_tiles(chunk, TILE_WALL, 8, 28, 9, 29)
    fill_tiles(chunk, TILE_WALL, 14, 32, 15, 33)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 37)
    fill_tiles(chunk, TILE_WALL, 30, 34, 31, 35)
    fill_tiles(chunk, TILE_WALL, 38, 38, 39, 39)
    fill_tiles(chunk, TILE_WALL, 18, 40, 19, 41)
    fill_tiles(chunk, TILE_WALL, 26, 42, 27, 43)
    # Castle interior — tapestry alcoves (DS3: grand castle halls)
    fill_tiles(chunk, TILE_WALL, 46, 22, 47, 23)
    fill_tiles(chunk, TILE_WALL, 54, 28, 55, 29)
    fill_tiles(chunk, TILE_WALL, 62, 24, 63, 25)
    fill_tiles(chunk, TILE_WALL, 70, 30, 71, 31)
    fill_tiles(chunk, TILE_WALL, 78, 26, 79, 27)
    fill_tiles(chunk, TILE_WALL, 86, 32, 87, 33)
    fill_tiles(chunk, TILE_WALL, 94, 28, 95, 29)
    fill_tiles(chunk, TILE_WALL, 102, 34, 103, 35)
    # Winged Knight ramparts — battlement stones (DS3: castle ramparts)
    fill_tiles(chunk, TILE_WALL, 108, 36, 109, 37)
    fill_tiles(chunk, TILE_WALL, 116, 40, 117, 41)
    fill_tiles(chunk, TILE_WALL, 124, 44, 125, 45)
    fill_tiles(chunk, TILE_WALL, 132, 42, 133, 43)
    fill_tiles(chunk, TILE_WALL, 140, 46, 141, 47)
    fill_tiles(chunk, TILE_WALL, 148, 44, 149, 45)
    # Dragon perch — volcanic rock debris (DS3: wyvern roost)
    fill_tiles(chunk, TILE_WALL, 110, 50, 111, 51)
    fill_tiles(chunk, TILE_WALL, 118, 54, 119, 55)
    fill_tiles(chunk, TILE_WALL, 126, 52, 127, 53)
    fill_tiles(chunk, TILE_WALL, 134, 56, 135, 57)
    fill_tiles(chunk, TILE_WALL, 142, 54, 143, 55)
    fill_tiles(chunk, TILE_WALL, 150, 58, 151, 59)
    # Archives bridge — stone arch fragments (DS3: bridge to Grand Archives)
    fill_tiles(chunk, TILE_WALL, 130, 62, 131, 63)
    fill_tiles(chunk, TILE_WALL, 136, 66, 137, 67)
    fill_tiles(chunk, TILE_WALL, 142, 70, 143, 71)
    fill_tiles(chunk, TILE_WALL, 148, 74, 149, 75)
    fill_tiles(chunk, TILE_WALL, 152, 78, 153, 79)
    # Dragonslayer arena — storm-swept debris (DS3: rooftop boss arena)
    fill_tiles(chunk, TILE_WALL, 118, 78, 119, 79)
    fill_tiles(chunk, TILE_WALL, 124, 82, 125, 83)
    fill_tiles(chunk, TILE_WALL, 128, 86, 129, 87)
    fill_tiles(chunk, TILE_WALL, 132, 80, 133, 81)
    fill_tiles(chunk, TILE_WALL, 114, 84, 115, 85)
    fill_tiles(chunk, TILE_WALL, 134, 88, 135, 89)
    # Dancer cathedral — ornate column bases (DS3: gothic cathedral interior)
    fill_tiles(chunk, TILE_WALL, 52, 30, 53, 31)
    fill_tiles(chunk, TILE_WALL, 58, 34, 59, 35)
    fill_tiles(chunk, TILE_WALL, 68, 28, 69, 29)
    fill_tiles(chunk, TILE_WALL, 72, 36, 73, 37)
    fill_tiles(chunk, TILE_WALL, 76, 30, 77, 31)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 41)
    # Castle lower — sewer stones (DS3: underground passages)
    fill_tiles(chunk, TILE_WALL, 34, 46, 35, 47)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    fill_tiles(chunk, TILE_WALL, 50, 44, 51, 45)
    fill_tiles(chunk, TILE_WALL, 58, 50, 59, 51)
    fill_tiles(chunk, TILE_WALL, 66, 46, 67, 47)

    # ================================================================
    # DS3 STRUCTURAL WALLS — Lothric Castle interior architecture
    # DS3: castle with stone gates, dragon bridge, barracks, grand halls
    # ================================================================
    # Dancer hall — castle throne room walls (DS3: Dancer of the Boreal Valley)
    fill_tiles(chunk, TILE_WALL, 30, 36, 34, 42)    # Throne room wall left
    fill_tiles(chunk, TILE_WALL, 46, 38, 50, 44)    # Throne room wall right
    fill_tiles(chunk, TILE_WALL, 38, 32, 42, 36)    # Throne room divider
    # Castle gate — grand entrance arch (DS3: stone gate into Lothric Castle)
    fill_tiles(chunk, TILE_WALL, 56, 64, 60, 70)    # Gate pillar left
    fill_tiles(chunk, TILE_WALL, 72, 64, 76, 70)    # Gate pillar right
    fill_tiles(chunk, TILE_WALL, 64, 66, 68, 72)    # Gate center wall
    # Twin Dragon Bridge — bridge walls (DS3: dragon corpse on bridge)
    fill_tiles(chunk, TILE_WALL, 100, 48, 104, 54)  # Bridge parapet left
    fill_tiles(chunk, TILE_WALL, 120, 48, 124, 54)  # Bridge parapet mid
    fill_tiles(chunk, TILE_WALL, 140, 48, 144, 54)  # Bridge parapet right
    fill_tiles(chunk, TILE_WALL, 110, 42, 114, 46)  # Dragon corpse obstacle
    fill_tiles(chunk, TILE_WALL, 130, 52, 134, 56)  # Dragon corpse 2
    # Barracks interior — bunk walls and weapon racks (DS3: Lothric Knight barracks)
    fill_tiles(chunk, TILE_WALL, 106, 92, 110, 98)  # Barracks wall left
    fill_tiles(chunk, TILE_WALL, 120, 88, 124, 94)  # Barracks wall center
    fill_tiles(chunk, TILE_WALL, 134, 90, 138, 96)  # Barracks wall right
    fill_tiles(chunk, TILE_WALL, 112, 100, 116, 106) # Bunk partition
    fill_tiles(chunk, TILE_WALL, 128, 102, 132, 108) # Bunk partition 2
    # Dragonslayer bridge — wide bridge walls (DS3: bridge to Dragonslayer Armour)
    fill_tiles(chunk, TILE_WALL, 170, 120, 174, 126) # Bridge wall left
    fill_tiles(chunk, TILE_WALL, 186, 118, 190, 124) # Bridge wall right
    fill_tiles(chunk, TILE_WALL, 178, 126, 182, 132) # Bridge center pillar
    # Dragonslayer arena — boss arena walls (DS3: open bridge arena)
    fill_tiles(chunk, TILE_WALL, 196, 130, 200, 136) # Arena wall NW
    fill_tiles(chunk, TILE_WALL, 216, 128, 220, 134) # Arena wall NE
    fill_tiles(chunk, TILE_WALL, 200, 142, 204, 148) # Arena wall SW
    fill_tiles(chunk, TILE_WALL, 212, 140, 216, 146) # Arena wall SE

        # ================================================================
    # ENTITIES
    # ================================================================

    # --- Player Spawn ---
    spawn_px, spawn_py = 10 * 16, 30 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))
    entities.append(make_entity("BossSpawn", 257 * 16, 142 * 16, [make_field("name", "String", "Dragonslayer Armour")]))

    # --- Bonfires --- DS3: Dragon Barracks, Lothric Castle, Grand Archives, Dragonslayer Armour
    entities.append(make_entity("Bonfire", 38 * 16, 56 * 16))    # Dragon Barracks (entry)
    entities.append(make_entity("Bonfire", 78 * 16, 80 * 16))    # Lothric Castle
    entities.append(make_entity("Bonfire", 157 * 16, 68 * 16))   # Dragonslayer Armour (boss)
    entities.append(make_entity("Bonfire", 253 * 16, 148 * 16))    # Dragonslayer Armour
    # Grand Archives bonfire (DS3: after Dragonslayer Armour, entrance to Grand Archives)
    entities.append(make_entity("Bonfire", 292 * 16, 137 * 16, [
        make_field("name", "String", "Grand Archives"),
        make_field("kind", "LocalEnum.BonfireKind", "Bonfire"),
    ]))    # Grand Archives

    # --- Boss ---

    # --- Enemies ---
    # DS3 Lothric Castle enemies: Lothric Knights, Hollow Soldiers, Hollow Assassins,
    # Hollow Priests (DarkMage), Winged Knights, Pus of Man, Boreal Outrider Knight,
    # Mimic, Crystal Lizards, Lothric Wyverns
    enemy_positions = [
        # Castle gate area — Lothric Knight + Hollow Priest healing combo
        ("LothricKnight", 18, 28), ("DarkMage", 22, 30),              # Priest heals knight (DS3)
        ("HollowSoldier", 14, 34), ("HollowSoldier", 20, 40),        # Crossbow hollows at gate
        # Outer corridor — Lothric Knights, Hollow Assassins, Starved Hounds
        ("LothricKnight", 35, 32), ("HollowAssassin", 32, 38),
        ("HollowSoldier", 28, 36),                                    # Crossbow hollow
        ("StarvedHound", 30, 30), ("StarvedHound", 38, 36),         # DS3: dogs in corridors
        ("HollowSoldier", 40, 40), ("HollowAssassin", 44, 44),      # Hollow ambushes in corridor
        # Corridor -> barracks transition
        ("LothricKnight", 55, 38), ("WingedKnight", 50, 38),
        ("DarkMage", 48, 42),                                         # Priest healer
        ("LothricKnight", 58, 44), ("LothricKnight", 62, 34),       # Knight pair guards stairs
        # Dragon barracks — Wyvern area (Pus of Man on dragon corpses)
        ("HollowSoldier", 68, 18), ("PusOfMan", 78, 18),
        ("HollowSoldier", 75, 22), ("CrystalLizard", 82, 22),
        ("HollowSoldier", 85, 28), ("PusOfMan", 95, 32),             # Second Pus of Man
        ("HollowSoldier", 70, 25), ("HollowSoldier", 92, 28),       # More hollows in barracks
        ("LothricKnight", 88, 34),                                    # Knight patrolling barracks
        # Boreal Outrider Knight (DS3: in a room with chests, frost damage)
        ("BorealOutriderKnight", 45, 55),                             # DS3: frost knight in side room
        ("StarvedHound", 48, 60),                                     # DS3: dog in side path
        # Inner stairs — Winged Knight gauntlet
        ("WingedKnight", 108, 48), ("CrystalLizard", 115, 45),
        ("LothricKnight", 112, 52),                                   # Knight on stairs
        ("LothricKnight", 100, 42),                                   # Red-eyed Lothric Knight
        ("HollowAssassin", 105, 54), ("HollowAssassin", 118, 50),   # Assassin ambush on stairs
        # Arena approaches
        ("PusOfMan", 125, 55), ("LothricKnight", 132, 58),
        ("HollowSoldier", 128, 62), ("HollowAssassin", 135, 55),      # Hollow gauntlet to boss
        ("WingedKnight", 140, 60),                                    # Ascended Winged Knight near arena
        ("HollowSoldier", 138, 68), ("HollowSoldier", 142, 72),     # Hollows at arena entrance
        # Additional DS3 Lothric Castle enemies — more knights, dogs, hollows (DS3: dense with enemies)
        ("LothricKnight", 22, 32), ("LothricKnight", 42, 38),       # Knights at gate courtyard
        ("StarvedHound", 32, 34), ("StarvedHound", 46, 42), ("StarvedHound", 52, 48),  # DS3: hounds in castle corridors
        ("StarvedHound", 65, 30), ("StarvedHound", 72, 25), ("StarvedHound", 98, 38),  # DS3: 8 hounds total
        ("LothricKnight", 75, 30), ("LothricKnight", 82, 26),      # Knights patrolling wyvern area
        ("LothricKnight", 95, 36), ("LothricKnight", 108, 44),     # Knights on inner stairs
        ("HollowSoldier", 60, 36), ("HollowSoldier", 85, 32),      # More hollows in barracks
        ("LothricKnight", 128, 60), ("LothricKnight", 136, 68),    # Knights near arena approach
        ("DarkMage", 122, 60),                                        # Priest healing knights near arena
        # Q(1,1) lower arena / throne room — DS3: hollows and knight near Lothric's empty throne
        ("HollowSoldier", 130, 82), ("HollowSoldier", 138, 86),     # Hollows in lower arena
        ("LothricKnight", 142, 90),                                   # Knight patrolling throne room approach
        ("HollowSoldier", 118, 85), ("HollowSoldier", 125, 88),     # Hollows at arena south edge
        ("DarkMage", 135, 92),                                        # Priest in lower castle chambers
    ]

    # --- Items - DS3 Lothric Castle (wiki-verified) ---
    items = [
        # Souls
        ("SoulOrb", "Soul of a Crestfallen Knight", 25, 25, 600),      # Altar room
        ("SoulOrb", "Soul of a Crestfallen Knight", 126, 60, 600),     # After wyvern dead
        ("SoulOrb", "Soul of a Weary Warrior", 55, 36, 1000),          # Right of stairs
        ("SoulOrb", "Soul of a Weary Warrior", 90, 35, 2000),          # Lever room
        ("SoulOrb", "Large Soul of a Nameless Soldier", 75, 18, 1500), # Hanging corpse
        ("SoulOrb", "Large Soul of a Nameless Soldier", 98, 28, 1500), # Tower top
        ("SoulOrb", "Large Soul of a Nameless Soldier", 105, 40, 1500),# Over ledge
        ("SoulOrb", "Large Soul of a Weary Warrior", 88, 30, 2000),    # Lever room
        # Lightning Urn x7
        ("Consumable", "Lightning Urn", 72, 15, 0),
        ("Consumable", "Lightning Urn", 78, 12, 0),
        ("Consumable", "Lightning Urn", 74, 18, 0),
        ("Consumable", "Lightning Urn", 76, 14, 0),
        ("Consumable", "Lightning Urn", 80, 16, 0),
        ("Consumable", "Lightning Urn", 82, 18, 0),
        ("Consumable", "Lightning Urn", 84, 15, 0),
        # Other consumables
        ("Consumable", "Sniper Bolt", 88, 25, 11),                     # Near sniper crossbow (11x)
        ("Consumable", "Pale Pine Resin", 115, 55, 0),                 # Mimic room
        ("Consumable", "Black Firebomb", 125, 62, 0),                  # Lower ladder room
        ("Consumable", "Black Firebomb", 126, 63, 0),                  # Same pickup (3x total)
        ("Consumable", "Black Firebomb", 124, 64, 0),                  # Same pickup (3x total)
        ("Consumable", "Sunlight Medal", 140, 66, 0),                  # Corpse outside church
        ("Consumable", "Rusted Coin", 125, 70, 0),                     # Church room
        ("Consumable", "Rusted Coin", 128, 72, 0),                     # Church room
        ("UndeadBoneShard", "Undead Bone Shard", 70, 20, 0),                # Under wyvern bridge
        # Embers x5
        ("Ember", "Ember", 68, 22, 0),                                 # Dragon barracks
        ("Ember", "Ember", 62, 30, 0),                                 # Wyvern bridge
        ("Ember", "Ember", 132, 63, 0),                                # Corner corpse
        ("Ember", "Ember", 82, 20, 0),                                 # Wyvern area
        ("Ember", "Ember", 135, 58, 0),                                # Post-wyvern
        # Weapons
        ("WeaponDrop", "Greatlance", 62, 28, 0),                       # Red-eye knight guards
        ("WeaponDrop", "Sniper Crossbow", 87, 26, 0),                  # Tower top near WK
        ("WeaponDrop", "Irithyll Rapier", 43, 53, 0),                  # Boreal Knight area
        ("WeaponDrop", "Caitha's Chime", 128, 75, 0),                  # Church roof
        ("WeaponDrop", "Sacred Bloom Shield", 52, 42, 0),              # Illusory wall
        # Armor
        ("ArmorDrop", "Winged Knight Set", 55, 42, 0),                 # Illusory wall
        # Upgrade materials — Large Titanite Shard x2
        ("TitaniteShard", "Large Titanite Shard", 75, 16, 0),
        ("TitaniteShard", "Large Titanite Shard", 95, 30, 0),
        # Titanite Chunk x10
        ("TitaniteShard", "Titanite Chunk", 42, 40, 0),
        ("TitaniteShard", "Titanite Chunk", 92, 30, 0),
        ("TitaniteShard", "Titanite Chunk", 74, 23, 0),
        ("TitaniteShard", "Titanite Chunk", 115, 48, 0),
        ("TitaniteShard", "Titanite Chunk", 135, 60, 0),
        ("TitaniteShard", "Titanite Chunk", 65, 20, 0),
        ("TitaniteShard", "Titanite Chunk", 127, 53, 0),
        ("TitaniteShard", "Titanite Chunk", 132, 42, 0),
        ("TitaniteShard", "Titanite Chunk", 138, 58, 0),
        ("TitaniteShard", "Titanite Chunk", 50, 44, 0),
        # Twinkling Titanite (ground pickups)
        ("TitaniteShard", "Twinkling Titanite", 52, 38, 0),            # Winged Knight room corpse
        ("TitaniteShard", "Twinkling Titanite", 118, 55, 0),           # Wyvern bridge far side
        # Titanite Scale (ground pickup)
        ("TitaniteShard", "Titanite Scale", 116, 50, 0),               # Outside mimic room corpse
        ("TitaniteShard", "Titanite Scale", 130, 68, 0),               # Shortcut path
        ("TitaniteShard", "Titanite Scale", 142, 62, 0),               # Shortcut path near Archives
        # Titanite Slab (DS3: elevator shortcut going down from Prince fight)
        ("TitaniteShard", "Titanite Slab", 148, 68, 0),                # Near Grand Archives exit
        # Rings & key items
        ("RingDrop", "Red Tearstone Ring", 132, 75, 0),                # Church jump
        ("RingDrop", "Knight's Ring", 106, 46, 0),                     # Ladder room
        ("Consumable", "Braille Divine Tome of Lothric", 102, 32, 0),  # Up stairs from mimic
        # Gems
        ("Consumable", "Raw Gem", 82, 35, 0),                          # Side room
        ("Consumable", "Refined Gem", 78, 20, 0),                      # After wyvern kill
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    # --- Chests - DS3 Lothric Castle (wiki-verified, 9 chests: 7 regular + 2 mimics) ---

    
    # --- DS3 faithful enemies (LothricCastle) ---
    # LothricKnight (18)
    for tx, ty in [(18, 28), (35, 32), (55, 38), (58, 44), (62, 34), (88, 34), (112, 52), (100, 42), (132, 58), (22, 32), (42, 38), (75, 30), (82, 26), (95, 36), (108, 44), (128, 60), (136, 68), (142, 90)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LothricKnight", "LothricKnight"))]))
    # DarkMage (4)
    entities.append(make_entity("Enemy", 22 * 16, 30 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 48 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 122 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 135 * 16, 92 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    # HollowSoldier (18)
    for tx, ty in [(14, 34), (20, 40), (28, 36), (40, 40), (68, 18), (75, 22), (85, 28), (70, 25), (92, 28), (128, 62), (138, 68), (142, 72), (60, 36), (85, 32), (130, 82), (138, 86), (118, 85), (125, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowSoldier", "HollowSoldier"))]))
    # HollowAssassin (5)
    entities.append(make_entity("Enemy", 32 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 44 * 16, 44 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 105 * 16, 54 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 118 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    entities.append(make_entity("Enemy", 135 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowAssassin", "HollowAssassin"))]))
    # StarvedHound (3)
    entities.append(make_entity("Enemy", 30 * 16, 30 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 38 * 16, 36 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    entities.append(make_entity("Enemy", 48 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    # WingedKnight (3)
    entities.append(make_entity("Enemy", 50 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("WingedKnight", "WingedKnight"))]))
    entities.append(make_entity("Enemy", 108 * 16, 48 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("WingedKnight", "WingedKnight"))]))
    entities.append(make_entity("Enemy", 140 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("WingedKnight", "WingedKnight"))]))
    # PusOfMan (3)
    entities.append(make_entity("Enemy", 78 * 16, 18 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    entities.append(make_entity("Enemy", 95 * 16, 32 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    entities.append(make_entity("Enemy", 125 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    # CrystalLizard (2)
    entities.append(make_entity("Enemy", 82 * 16, 22 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 115 * 16, 45 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # BorealOutriderKnight (1)
    entities.append(make_entity("Enemy", 45 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BorealOutriderKnight", "BorealOutriderKnight"))]))
    # Dog (6)
    entities.append(make_entity("Enemy", 32 * 16, 34 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Dog", "Dog"))]))
    entities.append(make_entity("Enemy", 46 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Dog", "Dog"))]))
    entities.append(make_entity("Enemy", 52 * 16, 48 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Dog", "Dog"))]))
    entities.append(make_entity("Enemy", 65 * 16, 30 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Dog", "Dog"))]))
    entities.append(make_entity("Enemy", 72 * 16, 25 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Dog", "Dog"))]))
    entities.append(make_entity("Enemy", 98 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Dog", "Dog"))]))
    # MiniBoss (1)
    entities.append(make_entity("Enemy", 132 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- NPCs - DS3 Lothric Castle ---
    # NOTE: Emma is only at High Wall of Lothric (LothricWall) — she dies after giving Basin of Vows
    # NOTE: Eygon of Carim only appears near Irina (Undead Settlement) or Firelink Shrine, not here
    # Lothric Castle NPCs in DS3: summon signs only (no dialogue NPCs roam the castle interior)

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 30 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 47 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 67 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 82 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 97 * 16, 81 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Grand Archives Key")]))
    entities.append(make_entity("Item", 133 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 160 * 16, 65 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 171 * 16, 68 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 143 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 145 * 16, 61 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 181 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 156 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 146 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 176 * 16, 117 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Lothric Knight Greatshield")]))
    entities.append(make_entity("Item", 172 * 16, 122 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Lothric Knight Set")]))
    entities.append(make_entity("Item", 143 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    entities.append(make_entity("Item", 162 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Firebomb"),
        make_field("name", "String", "Firebomb")]))
    entities.append(make_entity("Item", 240 * 16, 147 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 218 * 16, 136 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 253 * 16, 150 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Dragonslayer Armour")]))
    entities.append(make_entity("Item", 288 * 16, 133 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 56 * 16, 113 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 102 * 16, 83 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 185 * 16, 77 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 152 * 16, 112 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 173 * 16, 120 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    # Back to LothricWall (return to High Wall, DS3: castle connects back to high wall)
    entities.append(make_entity("FogGate", 38 * 16, 50 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 1600.0),
        make_field("dest_y", "Float", 1600.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Grand Archives (NE exit)
    entities.append(make_entity("FogGate", 292 * 16, 137 * 16, [
        make_field("dest_area", "String", "GrandArchives"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 2300.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Consumed King's Garden (south side path)
    entities.append(make_entity("FogGate", 57 * 16, 110 * 16, [
        make_field("dest_area", "String", "ConsumedKingsGarden"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 38 * 16, 56 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.75),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.45)]))
    entities.append(make_entity("Light", 31 * 16, 46 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 78 * 16, 80 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.95), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 68 * 16, 75 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 93 * 16, 81 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 157 * 16, 68 * 16, [
        make_field("radius", "Float", 220.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 137 * 16, 56 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.75),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 178 * 16, 67 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 157 * 16, 106 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.75),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 171 * 16, 116 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 146 * 16, 113 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 225 * 16, 136 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 242 * 16, 145 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 253 * 16, 148 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 247 * 16, 142 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 260 * 16, 155 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.7), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 292 * 16, 137 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 285 * 16, 130 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.9),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 57 * 16, 112 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    # SESSION 10 FIDELITY PASS — Lothric Castle
    # Additional DS3-faithful terrain: dragon courtyard scorch debris, knight barracks,
    # wyvern perch stones, Dancer cathedral pillars, Grand Archives approach
    # Dragon courtyard — scorch debris (DS3: dragon burns the courtyard)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 56, 55, 57)
    fill_tiles(chunk, TILE_WALL, 60, 54, 61, 55)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 59)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    # Knight barracks — barrack walls (DS3: Lothric Knight barracks)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 74, 58, 75, 59)
    fill_tiles(chunk, TILE_WALL, 80, 64, 81, 65)
    fill_tiles(chunk, TILE_WALL, 72, 66, 73, 67)
    # Wyvern perch — cliff stones (DS3: wyvern perches on castle wall)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    fill_tiles(chunk, TILE_WALL, 94, 60, 95, 61)
    fill_tiles(chunk, TILE_WALL, 84, 62, 85, 63)
    fill_tiles(chunk, TILE_WALL, 90, 58, 91, 59)
    # Dancer cathedral — cathedral pillars (DS3: grand cathedral entrance)
    fill_tiles(chunk, TILE_WALL, 100, 68, 101, 69)
    fill_tiles(chunk, TILE_WALL, 106, 72, 107, 73)
    fill_tiles(chunk, TILE_WALL, 112, 70, 113, 71)
    fill_tiles(chunk, TILE_WALL, 104, 74, 105, 75)
    fill_tiles(chunk, TILE_WALL, 110, 76, 111, 77)
    # Grand Archives approach — book and crystal debris (DS3: path to archives)
    fill_tiles(chunk, TILE_WALL, 118, 80, 119, 81)
    fill_tiles(chunk, TILE_WALL, 124, 84, 125, 85)
    fill_tiles(chunk, TILE_WALL, 130, 82, 131, 83)
    fill_tiles(chunk, TILE_WALL, 122, 88, 123, 89)
    fill_tiles(chunk, TILE_WALL, 128, 86, 129, 87)
    # Castle ramparts — wall stones (DS3: castle battlements)
    fill_tiles(chunk, TILE_WALL, 36, 54, 37, 55)
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 51)
    fill_tiles(chunk, TILE_WALL, 56, 48, 57, 49)
    fill_tiles(chunk, TILE_WALL, 64, 52, 65, 53)
    # Lothric throne room — throne debris (DS3: Lothric's empty throne room)
    fill_tiles(chunk, TILE_WALL, 134, 90, 135, 91)
    fill_tiles(chunk, TILE_WALL, 140, 88, 141, 89)
    fill_tiles(chunk, TILE_WALL, 136, 94, 137, 95)
    fill_tiles(chunk, TILE_WALL, 132, 92, 133, 93)

    # ================================================================
    # SESSION 15 FIDELITY PASS — LothricCastle additional DS3 details
    # ================================================================
    # Dragonslayer Armour rooftop — storm-worn battlements (DS3: rooftop boss arena)
    fill_tiles(chunk, TILE_WALL, 124, 64, 125, 65)
    fill_tiles(chunk, TILE_WALL, 130, 68, 131, 69)
    fill_tiles(chunk, TILE_WALL, 118, 66, 119, 67)
    fill_tiles(chunk, TILE_WALL, 136, 72, 137, 73)
    # Twin Dragon bridge — dragon corpse debris (DS3: two dragon corpses on bridge)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 68, 70, 69, 71)
    # Winged Knight stairs — armor stand alcoves (DS3: Winged Knights descend stairs)
    fill_tiles(chunk, TILE_WALL, 96, 56, 97, 57)
    fill_tiles(chunk, TILE_WALL, 100, 60, 101, 61)
    fill_tiles(chunk, TILE_WALL, 92, 58, 93, 59)
    fill_tiles(chunk, TILE_WALL, 104, 54, 105, 55)
    # Boreal Outrider room — frost-cracked stones (DS3: frost knight in side room)
    fill_tiles(chunk, TILE_WALL, 44, 52, 45, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 38, 54, 39, 55)
    # Castle dungeon — sewer grate stones (DS3: underground passage beneath castle)
    fill_tiles(chunk, TILE_WALL, 28, 62, 29, 63)
    fill_tiles(chunk, TILE_WALL, 34, 66, 35, 67)
    fill_tiles(chunk, TILE_WALL, 22, 64, 23, 65)

    # ================================================================
    # SESSION 17 FIDELITY PASS — LothricCastle DS3 castle ramparts
    # ================================================================
    # Dragon barracks — scorched earth debris (DS3: dragon-scorched garrison)
    fill_tiles(chunk, TILE_WALL, 62, 12, 63, 14)
    fill_tiles(chunk, TILE_WALL, 70, 16, 71, 18)
    fill_tiles(chunk, TILE_WALL, 78, 14, 79, 16)
    fill_tiles(chunk, TILE_WALL, 86, 18, 87, 20)
    fill_tiles(chunk, TILE_WALL, 94, 14, 95, 16)
    # Inner stairs — narrow passage buttresses (DS3: tight spiral staircase)
    fill_tiles(chunk, TILE_WALL, 102, 38, 103, 40)
    fill_tiles(chunk, TILE_WALL, 108, 42, 109, 44)
    fill_tiles(chunk, TILE_WALL, 114, 46, 115, 48)
    fill_tiles(chunk, TILE_WALL, 120, 50, 121, 52)
    # Dragonslayer Armour arena — storm-worn parapet debris (DS3: rooftop arena with wind)
    fill_tiles(chunk, TILE_WALL, 128, 56, 129, 58)
    fill_tiles(chunk, TILE_WALL, 134, 60, 135, 62)
    fill_tiles(chunk, TILE_WALL, 140, 64, 141, 66)
    fill_tiles(chunk, TILE_WALL, 146, 58, 147, 60)
    # Castle gate courtyard — statue pedestals (DS3: knight statues at gate)
    fill_tiles(chunk, TILE_WALL, 14, 26, 15, 28)
    fill_tiles(chunk, TILE_WALL, 20, 30, 21, 32)
    fill_tiles(chunk, TILE_WALL, 26, 34, 27, 36)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 30)
    # Grand Archives approach — fountain basin stones (DS3: grand fountain before archives)
    fill_tiles(chunk, TILE_WALL, 148, 56, 149, 58)
    fill_tiles(chunk, TILE_WALL, 152, 62, 153, 64)
    fill_tiles(chunk, TILE_WALL, 156, 68, 157, 70)

    # ================================================================
    # SESSION 19 FIDELITY PASS — LothricCastle DS3 castle depth
    # ================================================================
    # Dragon barracks — burnt pillar bases (DS3: dragon-scorched barracks walls)
    fill_tiles(chunk, TILE_WALL, 66, 20, 67, 22)
    fill_tiles(chunk, TILE_WALL, 74, 22, 75, 24)
    fill_tiles(chunk, TILE_WALL, 82, 20, 83, 22)
    fill_tiles(chunk, TILE_WALL, 90, 24, 91, 26)
    fill_tiles(chunk, TILE_WALL, 98, 22, 99, 24)
    # Twin dragon bridge — ribcage debris (DS3: dragon skeletons on bridge)
    fill_tiles(chunk, TILE_WALL, 76, 74, 77, 76)
    fill_tiles(chunk, TILE_WALL, 82, 78, 83, 80)
    fill_tiles(chunk, TILE_WALL, 88, 76, 89, 78)
    fill_tiles(chunk, TILE_WALL, 94, 80, 95, 82)
    fill_tiles(chunk, TILE_WALL, 100, 78, 101, 80)
    # Lothric throne room — curtain rod pillars (DS3: ornate throne chamber)
    fill_tiles(chunk, TILE_WALL, 138, 94, 139, 96)
    fill_tiles(chunk, TILE_WALL, 144, 98, 145, 100)
    fill_tiles(chunk, TILE_WALL, 150, 96, 151, 98)
    fill_tiles(chunk, TILE_WALL, 142, 100, 143, 102)
    fill_tiles(chunk, TILE_WALL, 148, 102, 149, 104)
    # Castle lower passages — iron grate debris (DS3: passages beneath castle)
    fill_tiles(chunk, TILE_WALL, 18, 56, 19, 58)
    fill_tiles(chunk, TILE_WALL, 24, 60, 25, 62)
    fill_tiles(chunk, TILE_WALL, 30, 58, 31, 60)
    fill_tiles(chunk, TILE_WALL, 36, 62, 37, 64)
    fill_tiles(chunk, TILE_WALL, 42, 66, 43, 68)

    # ================================================================
    # SESSION 22 FIDELITY PASS — LothricCastle DS3 castle details
    # ================================================================
    # Castle rampart merlons (DS3: stone battlements on castle walls)
    fill_tiles(chunk, TILE_WALL, 22, 30, 23, 31)
    fill_tiles(chunk, TILE_WALL, 28, 34, 29, 35)
    fill_tiles(chunk, TILE_WALL, 34, 38, 35, 39)
    fill_tiles(chunk, TILE_WALL, 40, 42, 41, 43)
    # Dragon corpse debris (DS3: dragon remains on the castle wall)
    fill_tiles(chunk, TILE_WALL, 46, 46, 47, 47)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 58, 54, 59, 55)
    fill_tiles(chunk, TILE_WALL, 64, 58, 65, 59)
    # Lothric throne room debris (DS3: shattered throne in Lothric room)
    fill_tiles(chunk, TILE_WALL, 70, 62, 71, 63)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    fill_tiles(chunk, TILE_WALL, 88, 74, 89, 75)
    # Wyvern perch stones (DS3: stones where wyverns land)
    fill_tiles(chunk, TILE_WALL, 94, 78, 95, 79)
    fill_tiles(chunk, TILE_WALL, 100, 82, 101, 83)
    fill_tiles(chunk, TILE_WALL, 106, 86, 107, 87)
    fill_tiles(chunk, TILE_WALL, 112, 90, 113, 91)

    # ================================================================
    # SESSION 28 FIDELITY PASS — LothricCastle DS3 castle details
    # ================================================================
    # Castle great hall pillars (DS3: stone pillars in the great hall)
    fill_tiles(chunk, TILE_WALL, 18, 32, 19, 33)
    fill_tiles(chunk, TILE_WALL, 24, 36, 25, 37)
    fill_tiles(chunk, TILE_WALL, 30, 40, 31, 41)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 45)
    # Dragon perch debris (DS3: dragon perching spots on castle walls)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 56, 55, 57)
    fill_tiles(chunk, TILE_WALL, 60, 60, 61, 61)
    # Dancer arena debris (DS3: shattered floor in Dancer's arena)
    fill_tiles(chunk, TILE_WALL, 66, 64, 67, 65)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    fill_tiles(chunk, TILE_WALL, 84, 76, 85, 77)
    # Lothric throne room debris (DS3: debris in Lothric's chamber)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 81)
    fill_tiles(chunk, TILE_WALL, 96, 84, 97, 85)
    fill_tiles(chunk, TILE_WALL, 102, 88, 103, 89)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)

    # ================================================================
    # SESSION 32 FIDELITY PASS — LothricCastle DS3 castle details
    # ================================================================
    # Castle battlement merlons (DS3: stone battlements on the walls)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    fill_tiles(chunk, TILE_WALL, 40, 48, 41, 49)
    # Dragon perch stones (DS3: stones where dragons roost)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 52, 56, 53, 57)
    fill_tiles(chunk, TILE_WALL, 58, 60, 59, 61)
    fill_tiles(chunk, TILE_WALL, 64, 64, 65, 65)
    # Dancer of the Boreal Valley arena (DS3: shattered floor tiles)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 77)
    fill_tiles(chunk, TILE_WALL, 88, 80, 89, 81)
    # Lothric's study debris (DS3: debris in Prince Lothric's chamber)
    fill_tiles(chunk, TILE_WALL, 94, 84, 95, 85)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 106, 92, 107, 93)
    fill_tiles(chunk, TILE_WALL, 112, 96, 113, 97)

    # SESSION 38 FIDELITY PASS — Lothric Castle DS3 details
    # DS3: Great hall pillars, dragon perches, throne room debris, Dancer arena
    for tx in range(25, 65, 6):
        fill_tiles(chunk, TILE_WALL, tx, 30, tx+2, 32)             # Great hall pillars
        fill_tiles(chunk, TILE_WALL, tx, 70, tx+2, 72)
    for tx in range(75, 120, 6):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+1, 36)             # Dragon perch debris
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+1, 76)
    for ty in range(40, 65, 8):
        fill_tiles(chunk, TILE_WALL, 40, ty, 41, ty+1)             # Castle interior columns
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 50, 57, 52)                    # Throne room debris
    fill_tiles(chunk, TILE_WALL, 110, 60, 112, 62)                  # Dancer arena debris
    fill_tiles(chunk, TILE_WALL, 80, 85, 82, 87)                    # Dragon skeleton
    for tx in range(120, 145, 5):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)             # Rooftop debris
    # SESSION 41 FIDELITY PASS — Lothric Castle DS3 details
    # DS3: Castle great hall, Dragon Slayer Armor arena, Lothric throne room
    for tx in range(25, 60, 5):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)             # Castle corridor tiles
        fill_tiles(chunk, TILE_WALL, tx, 85, tx+1, 86)
    for tx in range(65, 100, 5):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+1, 51)             # Dragon arena stones
        fill_tiles(chunk, TILE_WALL, tx, 90, tx+1, 91)
    for ty in range(40, 75, 7):
        fill_tiles(chunk, TILE_WALL, 45, ty, 46, ty+1)             # Castle interior columns
        fill_tiles(chunk, TILE_WALL, 105, ty, 106, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 65, 57, 67)                    # Dragon Slayer Armor arena
    fill_tiles(chunk, TILE_WALL, 120, 55, 122, 57)                  # Throne room approach
    fill_tiles(chunk, TILE_WALL, 80, 95, 82, 97)                    # Lothric prince chamber
    # --- SESSION 49 terrain (Lothric Castle) ---
    # DS3: Great hall pillars supporting the massive ceiling
    for ty in range(30, 38):
        chunk[ty][35] = TILE_WALL  # hall pillar
        chunk[ty][50] = TILE_WALL  # hall pillar
    # Dragon perch stones (DS3: where the dragon rests on the roof)
    for tx in range(95, 102):
        chunk[28][tx] = TILE_WALLTOP  # perch debris
    # Dancer arena columns (DS3: the circular arena has pillars)
    for ty in range(60, 68):
        chunk[ty][72] = TILE_WALL  # arena column
        chunk[ty][82] = TILE_WALL  # arena column
    # Throne room debris (DS3: Lothric's throne room is in ruins)
    for tx in range(100, 108):
        chunk[42][tx] = TILE_WALLTOP  # throne debris

    # --- SESSION 54 terrain (Lothric Castle final) ---
    # DS3: Castle gatehouse stonework
    for ty in range(15, 22):
        chunk[ty][8] = TILE_WALL  # gatehouse wall
        chunk[ty][12] = TILE_WALL  # gatehouse pillar
    # Consumed King's Garden approach archway
    for ty in range(68, 74):
        chunk[ty][18] = TILE_WALL  # archway pillar
    # Grand Archives bridge supports
    for ty in range(42, 48):
        chunk[ty][145] = TILE_WALL  # bridge support
    # Castle courtyard fountain
    chunk[48][65] = TILE_WALL  # fountain base
    chunk[48][66] = TILE_WALLTOP  # fountain rim

    # --- SESSION 89 DS3 terrain (Lothric Castle detail pass) ---
    # DS3: Great hall pillars (massive columns in the throne room)
    for tx in [20, 30, 40, 50, 60, 70, 80, 90]:
        for ty in range(12, 28):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Dragon perch (the dead wyvern platform)
    for tx in range(45, 58):
        for ty in range(5, 10):
            chunk[tx][ty] = TILE_WALL
    for tx in range(45, 59):
        chunk[tx][4] = TILE_WALLTOP
    # DS3: Dancer arena columns (circular chamber)
    for tx in [15, 25, 35, 45, 55]:
        for ty in [40, 41]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Throne debris (scattered stone blocks)
    for tx in [65, 68, 72, 75, 78]:
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Castle ramparts with battlements
    for tx in range(10, 100):
        chunk[tx][8] = TILE_WALL
        chunk[tx][7] = TILE_WALLTOP
    # DS3: Grand Archives entrance staircase
    for tx in range(85, 100):
        for ty in range(50, 65):
            chunk[tx][ty] = TILE_GROUND
    for tx in [85, 100]:
        for ty in range(50, 66):
            chunk[tx][ty] = TILE_WALL
    # DS3: Castle kennel (enclosed area with dogs)
    for tx in range(20, 30):
        for ty in [55, 62]:
            chunk[tx][ty] = TILE_WALL
    for tx in [20, 30]:
        for ty in range(55, 63):
            chunk[tx][ty] = TILE_WALL
    for tx in range(20, 31):
        chunk[tx][54] = TILE_WALLTOP

    # --- SESSION 92 DS3 terrain round 2 (Lothric Castle) ---
    # DS3: Consumed King's Garden entrance
    for tx in range(10, 20):
        for ty in [60, 66]:
            chunk[tx][ty] = TILE_WALL
    for tx in [10, 20]:
        for ty in range(60, 67):
            chunk[tx][ty] = TILE_WALL
    for tx in range(10, 21):
        chunk[tx][59] = TILE_WALLTOP
    # DS3: Lothric Wyvern perch (high tower)
    for tx in range(50, 60):
        for ty in [5, 10]:
            chunk[tx][ty] = TILE_WALL
    for tx in [50, 60]:
        for ty in range(5, 11):
            chunk[tx][ty] = TILE_WALL
    for tx in range(50, 61):
        chunk[tx][4] = TILE_WALLTOP
    # DS3: Castle courtyard fountain
    for tx in range(35, 45):
        for ty in [45, 46]:
            chunk[tx][ty] = TILE_WALL
    for tx in [35, 45]:
        for ty in [45, 46]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Dark Mage study room
    for tx in range(75, 85):
        for ty in [55, 60]:
            chunk[tx][ty] = TILE_WALL
    for tx in [75, 85]:
        for ty in range(55, 61):
            chunk[tx][ty] = TILE_WALL
    for tx in range(75, 86):
        chunk[tx][54] = TILE_WALLTOP
    # DS3: Twin Princes tower staircase
    for tx in range(85, 95):
        for ty in range(20, 35):
            chunk[tx][ty] = TILE_GROUND
    for tx in [85, 95]:
        for ty in range(20, 36):
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/LothricCastle.json") as _f:

        _doc = _json.load(_f)

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

    # === SECTION-BASED GROUND EXPANSION (DS3 fidelity) ===
    # Lothric Castle is the largest DS3 area — many rooms, wyvern bridge, boss arena
    fill_tiles(chunk, TILE_GROUND, 26, 40, 73, 80)   # Dancer Ladder Hall
    fill_tiles(chunk, TILE_GROUND, 62, 67, 110, 102)  # Lothric Castle Entry
    fill_tiles(chunk, TILE_GROUND, 128, 48, 195, 92)  # Twin Dragon Bridge
    fill_tiles(chunk, TILE_GROUND, 136, 93, 193, 133)  # Barracks Interior
    fill_tiles(chunk, TILE_GROUND, 206, 123, 257, 158) # Dragonslayer Bridge
    fill_tiles(chunk, TILE_GROUND, 241, 136, 288, 175) # Dragonslayer Armour Arena
    fill_tiles(chunk, TILE_GROUND, 280, 126, 310, 155) # Grand Archives Door
    fill_tiles(chunk, TILE_GROUND, 47, 100, 86, 132)   # Consumed King Garden Branch
    # Corridors connecting sections
    fill_tiles(chunk, TILE_GROUND, 48, 58, 88, 87)
    fill_tiles(chunk, TILE_GROUND, 84, 68, 163, 87)
    fill_tiles(chunk, TILE_GROUND, 159, 68, 167, 115)
    fill_tiles(chunk, TILE_GROUND, 163, 111, 233, 143)
    fill_tiles(chunk, TILE_GROUND, 229, 139, 267, 157)
    fill_tiles(chunk, TILE_GROUND, 263, 138, 297, 157)
    fill_tiles(chunk, TILE_GROUND, 64, 114, 297, 142)

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)

    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0]))
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100
    # print(f"  LothricCastle (faithful DS3 layout) "
    # f"ground={pct:.1f}% connectivity={coverage}%")
    return "LothricCastle", chunk, entities
