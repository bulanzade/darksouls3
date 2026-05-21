from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_untended_graves():
    """Untended Graves - dark mirror of Cemetery of Ash with Champion Gundyr boss.
    Faithful DS3 layout: dark coffin entry (NW) -> dark cemetery path ->
    dark courtyard -> Black Knight cemetery -> Champion Gundyr arena ->
    Dark Firelink Shrine (SE). Extremely dim lighting throughout.
    """
    chunk = new_chunk(256, 256)
    entities = []

    # === Dark coffin entry (NW) ===
    fill_tiles(chunk, TILE_GROUND, 8, 8, 35, 30)

    # === Dark cemetery path ===
    fill_tiles(chunk, TILE_GROUND, 25, 22, 75, 52)
    # Tombstone walls
    fill_tiles(chunk, TILE_WALL, 32, 28, 34, 31)
    fill_tiles(chunk, TILE_WALL, 48, 35, 50, 38)
    fill_tiles(chunk, TILE_WALL, 60, 40, 62, 43)
    fill_tiles(chunk, TILE_WALL, 40, 45, 42, 48)

    # === Dark courtyard ===
    fill_tiles(chunk, TILE_GROUND, 58, 40, 98, 68)
    carve_ellipse(chunk, 78, 54, 16, 10)
    # Courtyard walls
    fill_tiles(chunk, TILE_WALL, 68, 48, 70, 52)
    fill_tiles(chunk, TILE_WALL, 88, 55, 90, 59)

    # === Black Knight cemetery ===
    fill_tiles(chunk, TILE_GROUND, 38, 48, 75, 78)
    # Cemetery walls
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 58)
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 65)
    fill_tiles(chunk, TILE_WALL, 55, 70, 57, 73)

    # === Champion Gundyr arena ===
    fill_tiles(chunk, TILE_GROUND, 82, 65, 130, 100)
    carve_ellipse(chunk, 105, 82, 20, 15)
    # Arena edge ruins
    fill_tiles(chunk, TILE_WALL, 88, 70, 90, 73)
    fill_tiles(chunk, TILE_WALL, 118, 90, 120, 93)
    fill_tiles(chunk, TILE_WALL, 95, 95, 97, 98)

    # === ADDITIONAL TOMBSTONES (dense cemetery feel) ===
    # Dark cemetery path — many tombstones
    fill_tiles(chunk, TILE_WALL, 28, 25, 29, 27)
    fill_tiles(chunk, TILE_WALL, 35, 30, 36, 32)
    fill_tiles(chunk, TILE_WALL, 42, 28, 43, 30)
    fill_tiles(chunk, TILE_WALL, 55, 34, 56, 36)
    fill_tiles(chunk, TILE_WALL, 50, 42, 51, 44)
    fill_tiles(chunk, TILE_WALL, 65, 38, 66, 40)
    fill_tiles(chunk, TILE_WALL, 38, 38, 39, 40)
    # Dark courtyard — broken walls
    fill_tiles(chunk, TILE_WALL, 62, 44, 63, 46)
    fill_tiles(chunk, TILE_WALL, 75, 50, 76, 52)
    fill_tiles(chunk, TILE_WALL, 92, 58, 93, 60)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 64)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 62)
    # Black Knight cemetery — dense tombstones
    fill_tiles(chunk, TILE_WALL, 42, 52, 43, 54)
    fill_tiles(chunk, TILE_WALL, 50, 58, 51, 60)
    fill_tiles(chunk, TILE_WALL, 58, 55, 59, 57)
    fill_tiles(chunk, TILE_WALL, 65, 68, 66, 70)
    fill_tiles(chunk, TILE_WALL, 48, 65, 49, 67)
    fill_tiles(chunk, TILE_WALL, 70, 72, 71, 74)

    # === EVEN MORE TOMBSTONES — dense DS3 cemetery ===
    # Cemetery path — additional rows of graves (DS3: graveyard packed with headstones)
    fill_tiles(chunk, TILE_WALL, 30, 24, 31, 26)
    fill_tiles(chunk, TILE_WALL, 33, 32, 34, 34)
    fill_tiles(chunk, TILE_WALL, 46, 30, 47, 32)
    fill_tiles(chunk, TILE_WALL, 52, 38, 53, 40)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 44)
    fill_tiles(chunk, TILE_WALL, 63, 34, 64, 36)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 38)
    # Courtyard — broken walls and debris (DS3: ruined courtyard near Gundyr)
    fill_tiles(chunk, TILE_WALL, 72, 46, 73, 48)
    fill_tiles(chunk, TILE_WALL, 80, 54, 81, 56)
    fill_tiles(chunk, TILE_WALL, 85, 58, 86, 60)
    fill_tiles(chunk, TILE_WALL, 95, 62, 96, 64)
    fill_tiles(chunk, TILE_WALL, 78, 64, 79, 66)
    # Black Knight cemetery — dense tombstone rows
    fill_tiles(chunk, TILE_WALL, 44, 58, 45, 60)
    fill_tiles(chunk, TILE_WALL, 52, 62, 53, 64)
    fill_tiles(chunk, TILE_WALL, 60, 58, 61, 60)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 68)
    fill_tiles(chunk, TILE_WALL, 46, 72, 47, 74)
    fill_tiles(chunk, TILE_WALL, 56, 68, 57, 70)
    fill_tiles(chunk, TILE_WALL, 64, 74, 65, 76)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 72)

    # === Champion Gundyr arena — broken fountain and ruins ===
    # DS3: Gundyr fights in a dark version of the Cemetery of Ash arena
    # Broken fountain in center
    fill_tiles(chunk, TILE_WALL, 100, 78, 108, 80)
    fill_tiles(chunk, TILE_WALL, 103, 75, 105, 83)
    # Arena perimeter ruins
    fill_tiles(chunk, TILE_WALL, 85, 68, 87, 72)
    fill_tiles(chunk, TILE_WALL, 120, 85, 122, 88)
    fill_tiles(chunk, TILE_WALL, 110, 95, 112, 98)
    fill_tiles(chunk, TILE_WALL, 125, 92, 127, 95)
    fill_tiles(chunk, TILE_WALL, 90, 90, 92, 93)
    fill_tiles(chunk, TILE_WALL, 115, 98, 117, 100)
    # Scattered debris
    fill_tiles(chunk, TILE_WALL, 108, 88, 110, 90)
    fill_tiles(chunk, TILE_WALL, 98, 92, 100, 94)

    # === Dark coffin entry details ===
    # DS3: you wake up in a coffin, small enclosed stone chamber
    fill_tiles(chunk, TILE_WALL, 10, 12, 12, 14)
    fill_tiles(chunk, TILE_WALL, 18, 10, 20, 12)
    fill_tiles(chunk, TILE_WALL, 14, 18, 16, 20)

    # === Dark Firelink Shrine (SE) — dark mirror of Firelink ===
    fill_tiles(chunk, TILE_GROUND, 115, 95, 150, 130)
    carve_ellipse(chunk, 132, 112, 12, 10)
    # Shrine interior walls — dark coiled sword spot (DS3: no fire, just dark)
    fill_tiles(chunk, TILE_WALL, 128, 108, 132, 110)
    fill_tiles(chunk, TILE_WALL, 136, 108, 140, 110)
    # Throne room walls — 5 empty Lord of Cinder thrones (DS3: dark version)
    fill_tiles(chunk, TILE_WALL, 118, 98, 120, 102)
    fill_tiles(chunk, TILE_WALL, 125, 96, 127, 100)
    fill_tiles(chunk, TILE_WALL, 138, 96, 140, 100)
    fill_tiles(chunk, TILE_WALL, 145, 98, 147, 102)
    # Dark Handmaid alcove
    fill_tiles(chunk, TILE_WALL, 130, 118, 132, 122)
    # Shrine exterior walls
    fill_tiles(chunk, TILE_WALL, 122, 100, 124, 105)
    fill_tiles(chunk, TILE_WALL, 140, 115, 142, 120)
    # Dark shrine entrance pillars
    fill_tiles(chunk, TILE_WALL, 116, 104, 118, 108)
    fill_tiles(chunk, TILE_WALL, 146, 104, 148, 108)

    # === ADDITIONAL DS3 UNTENDED GRAVES — shrine architecture, cemetery depth ===
    # Dark Firelink Shrine — Andre's anvil alcove (DS3: dark Andre works silently)
    fill_tiles(chunk, TILE_WALL, 134, 110, 136, 114)
    fill_tiles(chunk, TILE_WALL, 130, 114, 132, 118)
    # Shrine — Ludleth's throne seat (DS3: Ludleth present in dark shrine)
    fill_tiles(chunk, TILE_WALL, 142, 106, 144, 109)
    # Shrine — Fire Keeper's enclosure (DS3: dark Fire Keeper stands in silence)
    fill_tiles(chunk, TILE_WALL, 136, 120, 138, 124)
    fill_tiles(chunk, TILE_WALL, 142, 122, 144, 126)
    # Shrine — shattered coiled sword debris (DS3: sword present but unlit)
    fill_tiles(chunk, TILE_WALL, 128, 114, 130, 116)
    fill_tiles(chunk, TILE_WALL, 134, 116, 136, 118)
    # Cemetery — collapsed grave walls (DS3: dark cemetery with fallen headstones)
    fill_tiles(chunk, TILE_WALL, 30, 32, 31, 34)
    fill_tiles(chunk, TILE_WALL, 36, 36, 37, 38)
    fill_tiles(chunk, TILE_WALL, 54, 40, 55, 42)
    fill_tiles(chunk, TILE_WALL, 48, 44, 49, 46)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 48)
    # Gundyr arena — collapsed arch stones (DS3: mirror of Cemetery of Ash arena)
    fill_tiles(chunk, TILE_WALL, 92, 74, 94, 76)
    fill_tiles(chunk, TILE_WALL, 112, 82, 114, 84)
    fill_tiles(chunk, TILE_WALL, 102, 90, 104, 92)
    fill_tiles(chunk, TILE_WALL, 122, 88, 124, 90)
    fill_tiles(chunk, TILE_WALL, 96, 86, 98, 88)
    # Dark path — dead tree stumps (DS3: withered trees in darkness)
    fill_tiles(chunk, TILE_WALL, 22, 18, 24, 20)
    fill_tiles(chunk, TILE_WALL, 68, 42, 70, 44)

    # === SESSION 6 FIDELITY PASS — Untended Graves ===
    # Dark coffin entry — stone lid debris (DS3: coffin you wake up in breaks open)
    fill_tiles(chunk, TILE_WALL, 12, 8, 14, 10)
    fill_tiles(chunk, TILE_WALL, 22, 14, 24, 16)
    fill_tiles(chunk, TILE_WALL, 8, 16, 10, 18)
    fill_tiles(chunk, TILE_WALL, 26, 10, 28, 12)
    # Dark cemetery path — more fallen headstones (DS3: destroyed graveyard)
    fill_tiles(chunk, TILE_WALL, 34, 26, 36, 28)
    fill_tiles(chunk, TILE_WALL, 40, 32, 42, 34)
    fill_tiles(chunk, TILE_WALL, 56, 36, 58, 38)
    fill_tiles(chunk, TILE_WALL, 50, 40, 52, 42)
    fill_tiles(chunk, TILE_WALL, 60, 44, 62, 46)
    fill_tiles(chunk, TILE_WALL, 44, 42, 46, 44)
    # Dark courtyard — more broken walls (DS3: ruined structure near Gundyr approach)
    fill_tiles(chunk, TILE_WALL, 64, 52, 66, 54)
    fill_tiles(chunk, TILE_WALL, 74, 56, 76, 58)
    fill_tiles(chunk, TILE_WALL, 84, 60, 86, 62)
    fill_tiles(chunk, TILE_WALL, 90, 64, 92, 66)
    fill_tiles(chunk, TILE_WALL, 78, 66, 80, 68)
    # Black Knight cemetery — more dense graves (DS3: dark mirror cemetery)
    fill_tiles(chunk, TILE_WALL, 40, 56, 42, 58)
    fill_tiles(chunk, TILE_WALL, 54, 60, 56, 62)
    fill_tiles(chunk, TILE_WALL, 62, 64, 64, 66)
    fill_tiles(chunk, TILE_WALL, 66, 72, 68, 74)
    fill_tiles(chunk, TILE_WALL, 52, 70, 54, 72)
    fill_tiles(chunk, TILE_WALL, 74, 68, 76, 70)
    # Gundyr arena — more collapsed arch stones (DS3: mirror of Cemetery of Ash arena)
    fill_tiles(chunk, TILE_WALL, 86, 72, 88, 74)
    fill_tiles(chunk, TILE_WALL, 116, 84, 118, 86)
    fill_tiles(chunk, TILE_WALL, 100, 88, 102, 90)
    fill_tiles(chunk, TILE_WALL, 120, 92, 122, 94)
    fill_tiles(chunk, TILE_WALL, 106, 94, 108, 96)
    # Dark Firelink — more shrine interior walls (DS3: exact dark mirror of Firelink)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 104)
    fill_tiles(chunk, TILE_WALL, 148, 102, 150, 104)
    fill_tiles(chunk, TILE_WALL, 124, 110, 126, 112)
    fill_tiles(chunk, TILE_WALL, 144, 110, 146, 112)
    fill_tiles(chunk, TILE_WALL, 132, 124, 134, 126)
    fill_tiles(chunk, TILE_WALL, 138, 126, 140, 128)
    # Dark path connections — more debris along route
    fill_tiles(chunk, TILE_WALL, 20, 22, 22, 24)
    fill_tiles(chunk, TILE_WALL, 72, 48, 74, 50)
    fill_tiles(chunk, TILE_WALL, 82, 70, 84, 72)

    # === Connections ===
    # Entry -> Cemetery path (already adjacent)
    # Cemetery -> Courtyard
    fill_tiles(chunk, TILE_GROUND, 58, 42, 65, 48)
    # Courtyard -> Arena
    fill_tiles(chunk, TILE_GROUND, 82, 55, 90, 68)
    # Cemetery -> Knight cemetery
    fill_tiles(chunk, TILE_GROUND, 42, 48, 50, 55)
    # Arena -> Dark Firelink
    fill_tiles(chunk, TILE_GROUND, 115, 88, 122, 98)

    # ================================================================
    # SESSION 9 FIDELITY PASS — UntendedGraves architectural details
    # ================================================================
    # Dark cemetery entry — collapsed coffin stones (DS3: broken coffins at entrance)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 23)
    fill_tiles(chunk, TILE_WALL, 14, 26, 15, 27)
    fill_tiles(chunk, TILE_WALL, 28, 16, 29, 17)
    # Dark cemetery path — tilted gravestones (DS3: dark version of Cemetery of Ash)
    fill_tiles(chunk, TILE_WALL, 34, 32, 35, 33)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    fill_tiles(chunk, TILE_WALL, 30, 40, 31, 41)
    fill_tiles(chunk, TILE_WALL, 40, 28, 41, 29)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 45)
    # Knight cemetery — black knight armor stands (DS3: suits of armor as decoration)
    fill_tiles(chunk, TILE_WALL, 46, 50, 47, 51)
    fill_tiles(chunk, TILE_WALL, 50, 54, 51, 55)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 59)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 49)
    fill_tiles(chunk, TILE_WALL, 48, 60, 49, 61)
    # Gundyr arena approach — eroded stone arches (DS3: same layout as Cemetery of Ash but darker)
    fill_tiles(chunk, TILE_WALL, 60, 66, 61, 67)
    fill_tiles(chunk, TILE_WALL, 64, 70, 65, 71)
    fill_tiles(chunk, TILE_WALL, 56, 74, 57, 75)
    fill_tiles(chunk, TILE_WALL, 68, 64, 69, 65)
    # Gundyr arena — darkened perimeter ruins (DS3: identical to Iudex arena but unlit)
    fill_tiles(chunk, TILE_WALL, 80, 72, 81, 73)
    fill_tiles(chunk, TILE_WALL, 84, 76, 85, 77)
    fill_tiles(chunk, TILE_WALL, 76, 80, 77, 81)
    fill_tiles(chunk, TILE_WALL, 88, 70, 89, 71)
    fill_tiles(chunk, TILE_WALL, 82, 82, 83, 83)
    # Dark Firelink Shrine — extinguished coiled sword stump (DS3: dark version of Firelink)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 93)
    fill_tiles(chunk, TILE_WALL, 96, 96, 97, 97)
    fill_tiles(chunk, TILE_WALL, 108, 86, 109, 87)
    fill_tiles(chunk, TILE_WALL, 102, 98, 103, 99)
    fill_tiles(chunk, TILE_WALL, 112, 94, 113, 95)
    # Shrine interior — darkened stone pillars (DS3: same layout but no fire)
    fill_tiles(chunk, TILE_WALL, 118, 90, 119, 91)
    fill_tiles(chunk, TILE_WALL, 124, 94, 125, 95)
    fill_tiles(chunk, TILE_WALL, 116, 98, 117, 99)

    # ================================================================
    # SESSION 11 FIDELITY PASS — UntendedGraves fine architectural details
    # ================================================================
    # Dark coffin entry — shattered lid fragments (DS3: coffin breaks open in darkness)
    fill_tiles(chunk, TILE_WALL, 9, 10, 10, 11)
    fill_tiles(chunk, TILE_WALL, 16, 12, 17, 13)
    fill_tiles(chunk, TILE_WALL, 12, 16, 13, 17)
    # Dark cemetery path — sunken grave pits (DS3: collapsed graves in dark soil)
    fill_tiles(chunk, TILE_WALL, 26, 30, 27, 31)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 35)
    fill_tiles(chunk, TILE_WALL, 38, 28, 39, 29)
    fill_tiles(chunk, TILE_WALL, 44, 34, 45, 35)
    fill_tiles(chunk, TILE_WALL, 48, 38, 49, 39)
    fill_tiles(chunk, TILE_WALL, 56, 32, 57, 33)
    # Dark courtyard — eroded stone floor debris (DS3: worn stone courtyard in darkness)
    fill_tiles(chunk, TILE_WALL, 66, 48, 67, 49)
    fill_tiles(chunk, TILE_WALL, 74, 52, 75, 53)
    fill_tiles(chunk, TILE_WALL, 82, 56, 83, 57)
    fill_tiles(chunk, TILE_WALL, 90, 60, 91, 61)
    fill_tiles(chunk, TILE_WALL, 78, 62, 79, 63)
    fill_tiles(chunk, TILE_WALL, 86, 66, 87, 67)
    # Black Knight cemetery — broken iron fence (DS3: rusted fence around graves)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 55)
    fill_tiles(chunk, TILE_WALL, 56, 56, 57, 57)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    fill_tiles(chunk, TILE_WALL, 48, 68, 49, 69)
    fill_tiles(chunk, TILE_WALL, 58, 72, 59, 73)
    fill_tiles(chunk, TILE_WALL, 68, 76, 69, 77)
    # Gundyr arena — darkened coffin debris (DS3: scattered coffins in dark arena)
    fill_tiles(chunk, TILE_WALL, 84, 74, 85, 75)
    fill_tiles(chunk, TILE_WALL, 92, 78, 93, 79)
    fill_tiles(chunk, TILE_WALL, 116, 86, 117, 87)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)
    fill_tiles(chunk, TILE_WALL, 126, 90, 127, 91)
    # Dark Firelink — extinguished bonfire ash pile (DS3: cold ash where bonfire should be)
    fill_tiles(chunk, TILE_WALL, 130, 112, 131, 113)
    fill_tiles(chunk, TILE_WALL, 126, 116, 127, 117)
    fill_tiles(chunk, TILE_WALL, 134, 120, 135, 121)
    fill_tiles(chunk, TILE_WALL, 140, 118, 141, 119)
    # Dark shrine — collapsed rafter debris (DS3: rafters in darkness)
    fill_tiles(chunk, TILE_WALL, 122, 106, 123, 107)
    fill_tiles(chunk, TILE_WALL, 146, 108, 147, 109)
    fill_tiles(chunk, TILE_WALL, 128, 122, 129, 123)
    fill_tiles(chunk, TILE_WALL, 142, 124, 143, 125)
    # Path connections — eroded stone path edges (DS3: crumbling path borders)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 64, 46, 65, 47)
    fill_tiles(chunk, TILE_WALL, 76, 50, 77, 51)
    fill_tiles(chunk, TILE_WALL, 84, 68, 85, 69)
    fill_tiles(chunk, TILE_WALL, 110, 90, 111, 91)

    # ================================================================
    # SESSION 13 FIDELITY PASS — UntendedGraves DS3 architecture
    # ================================================================
    # Dark coffin entry — stone splinter debris (DS3: coffin shatters in darkness)
    fill_tiles(chunk, TILE_WALL, 7, 8, 8, 9)
    fill_tiles(chunk, TILE_WALL, 11, 12, 12, 13)
    fill_tiles(chunk, TILE_WALL, 19, 14, 20, 15)
    fill_tiles(chunk, TILE_WALL, 15, 20, 16, 21)
    fill_tiles(chunk, TILE_WALL, 23, 8, 24, 9)
    # Dark cemetery — collapsed tomb clusters (DS3: dark mirror of Cemetery of Ash)
    fill_tiles(chunk, TILE_WALL, 28, 24, 29, 25)
    fill_tiles(chunk, TILE_WALL, 42, 28, 43, 29)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 35)
    fill_tiles(chunk, TILE_WALL, 36, 42, 37, 43)
    fill_tiles(chunk, TILE_WALL, 60, 38, 61, 39)
    fill_tiles(chunk, TILE_WALL, 46, 46, 47, 47)
    # Black Knight patrol route — rusted weapon racks (DS3: Black Knights guard the dark cemetery)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    fill_tiles(chunk, TILE_WALL, 70, 58, 71, 59)
    fill_tiles(chunk, TILE_WALL, 44, 66, 45, 67)
    fill_tiles(chunk, TILE_WALL, 62, 70, 63, 71)
    # Gundyr arena perimeter — dark reflection stones (DS3: same arena as Iudex but dark)
    fill_tiles(chunk, TILE_WALL, 88, 76, 89, 77)
    fill_tiles(chunk, TILE_WALL, 96, 80, 97, 81)
    fill_tiles(chunk, TILE_WALL, 114, 84, 115, 85)
    fill_tiles(chunk, TILE_WALL, 122, 88, 123, 89)
    fill_tiles(chunk, TILE_WALL, 104, 94, 105, 95)
    # Dark Firelink Shrine — throne room ash drifts (DS3: ash covers everything in dark shrine)
    fill_tiles(chunk, TILE_WALL, 118, 96, 119, 97)
    fill_tiles(chunk, TILE_WALL, 148, 100, 149, 101)
    fill_tiles(chunk, TILE_WALL, 124, 108, 125, 109)
    fill_tiles(chunk, TILE_WALL, 140, 112, 141, 113)
    fill_tiles(chunk, TILE_WALL, 148, 116, 149, 117)
    fill_tiles(chunk, TILE_WALL, 132, 120, 133, 121)
    # Starved Hound dens — hollowed tree trunks (DS3: hounds lurk near dead trees)
    fill_tiles(chunk, TILE_WALL, 34, 48, 35, 49)
    fill_tiles(chunk, TILE_WALL, 72, 54, 73, 55)

        # --- Player spawn ---
    spawn_px, spawn_py = 15 * 16, 15 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 43 * 16, 45 * 16))    # Entry
    entities.append(make_entity("Bonfire", 155 * 16, 133 * 16))   # Champion Gundyr

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 155 * 16, 133 * 16))  # Champion Gundyr

    # --- Enemies — DS3 Untended Graves (wiki-accurate):
    # Black Knights are the primary enemies — dark mirror of Cemetery of Ash.
    # No Grave Wardens, Corvians, or Pus of Man in this area (those belong elsewhere).
    # Champion Gundyr is the boss.

    # --- Items (DS3 Untended Graves) ---

    
    # --- DS3 faithful enemies (UntendedGraves) ---
    # DS3 wiki enemies: Pus of Man, Cathedral Grave Warden, Black Knight,
    # Grave Warden, Starved Hound, Corvian, Corvian Storyteller, Ravenous Crystal Lizard
    # BlackKnight (4) — DS3: guard Dark Firelink Shrine (greataxe, greatsword, stairs, Hornet Ring)
    for tx, ty in [(170, 185), (180, 190), (165, 195), (175, 200)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))
    # CathedralGraveWarden (2) — DS3: in the pool/water area of dark cemetery
    for tx, ty in [(95, 80), (100, 85)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CathedralGraveWarden", "CathedralGraveWarden"))]))
    # GraveWarden (2) — DS3: dark cemetery, one at archway, one to the left
    for tx, ty in [(50, 45), (55, 50)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GraveWarden", "CathedralGraveWarden"))]))
    # StarvedHound (6) — DS3: throughout area, pool area, near arena approach
    for tx, ty in [(60, 55), (65, 60), (85, 70), (90, 75), (110, 100), (130, 120)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    # Corvian (3) — DS3: group near bonfire guarding Ashen Estus Ring area
    for tx, ty in [(35, 35), (40, 38), (45, 42)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Corvian", "Assassin"))]))
    # CorvianStoryteller (1) — DS3: with the Corvian group
    entities.append(make_entity("Enemy", 42 * 16, 40 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CorvianStoryteller", "DarkMage"))]))
    # PusOfMan (1) — DS3: in the dark cemetery
    entities.append(make_entity("Enemy", 80 * 16, 65 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    # RavenousCrystalLizard (2) — DS3: right section where Cemetery of Ash had 1
    for tx, ty in [(105, 75), (110, 80)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("RavenousCrystalLizard", "CrystalLizard"))]))

# --- NPCs ---
    # Dark Shrine Handmaid in Dark Firelink Shrine (different from normal Firelink)
    entities.append(make_entity("Npc", 193 * 16, 201 * 16, [
        make_field("name", "String", "Shrine Handmaid"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#606060"),
        make_field("dialogue", "String",
            "What is it? There is only dark here|The fire has long been out|I will tend to the ash, as I always have|There is nothing else for it"),
    ]))
    # Daughter of Crystal Kriemhild — DS3: NPC invader on center path heading up the hill
    entities.append(make_entity("Npc", 115 * 16, 95 * 16, [
        make_field("name", "String", "Daughter of Crystal Kriemhild"),
        make_field("kind", "LocalEnum.NpcKind", "Invader"),
        make_field("color", "Color", "#4A6A8A"),
        make_field("dialogue", "String",
            "I am Kriemhild, daughter of crystal|The dark is not to be feared|It is merely the absence of fire"),
    ]))


    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 201 * 16, 211 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Hidden Blessing")]))
    entities.append(make_entity("Item", 191 * 16, 199 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Eyes of a Fire Keeper")]))
    entities.append(make_entity("Item", 191 * 16, 205 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "WeaponDrop"),
        make_field("name", "String", "Coiled Sword Fragment")]))
    entities.append(make_entity("Item", 80 * 16, 65 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Ashen Estus Ring")]))
    entities.append(make_entity("Item", 223 * 16, 185 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Hornet Ring")]))
    entities.append(make_entity("Item", 106 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Black Knight Glaive")]))
    entities.append(make_entity("Item", 120 * 16, 85 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Chaos Blade")]))
    entities.append(make_entity("Item", 181 * 16, 181 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Blacksmith Hammer")]))
    entities.append(make_entity("Item", 68 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 146 * 16, 120 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 95 * 16, 90 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 167 * 16, 137 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 155 * 16, 135 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of Champion Gundyr")]))
# --- Fog Gate ---
    # To Firelink Shrine (DS3: dark Firelink connects back to normal Firelink)
    entities.append(make_entity("FogGate", 43 * 16, 38 * 16, [
        make_field("dest_area", "String", "FirelinkShrine"),
        make_field("dest_x", "Float", 1280.0),
        make_field("dest_y", "Float", 1280.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))
    # Fog Gate back to Consumed King's Garden (DS3: return path)
    entities.append(make_entity("FogGate", 191 * 16, 191 * 16, [
        make_field("dest_area", "String", "ConsumedKingsGarden"),
        make_field("dest_x", "Float", 2200.0), make_field("dest_y", "Float", 1500.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))

    # --- Lights (extremely dim — this area is in total darkness) ---
    # Entry — barely visible
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [
        make_field("radius", "Float", 70.0),
        make_field("r", "Float", 0.25), make_field("g", "Float", 0.25),
        make_field("b", "Float", 0.25), make_field("intensity", "Float", 0.1)]))
    # Cemetery — faint glow
    entities.append(make_entity("Light", 50 * 16, 38 * 16, [
        make_field("radius", "Float", 80.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.25), make_field("intensity", "Float", 0.1)]))
    # Gundyr arena — slightly brighter
    entities.append(make_entity("Light", 105 * 16, 78 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.3),
        make_field("b", "Float", 0.25), make_field("intensity", "Float", 0.15)]))
    # Dark Firelink — minimal
    entities.append(make_entity("Light", 132 * 16, 112 * 16, [
        make_field("radius", "Float", 60.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.1)]))
    # SESSION 10 FIDELITY PASS — Untended Graves
    # Additional DS3-faithful terrain: collapsed coffin stones, tilted gravestones,
    # Dark Firelink pillar fragments, Gundyr arena debris, dark cemetery path edges
    # Dark cemetery path — tilted gravestones (DS3: tilted broken gravestones)
    fill_tiles(chunk, TILE_WALL, 52, 88, 53, 89)
    fill_tiles(chunk, TILE_WALL, 58, 92, 59, 93)
    fill_tiles(chunk, TILE_WALL, 64, 86, 65, 87)
    fill_tiles(chunk, TILE_WALL, 70, 90, 71, 91)
    fill_tiles(chunk, TILE_WALL, 76, 94, 77, 95)
    fill_tiles(chunk, TILE_WALL, 82, 88, 83, 89)
    # Cemetery approach — collapsed coffins (DS3: broken coffins along path)
    fill_tiles(chunk, TILE_WALL, 88, 96, 89, 97)
    fill_tiles(chunk, TILE_WALL, 94, 100, 95, 101)
    fill_tiles(chunk, TILE_WALL, 84, 104, 85, 105)
    fill_tiles(chunk, TILE_WALL, 90, 108, 91, 109)
    # Gundyr arena — arena debris (DS3: ruined arena with debris)
    fill_tiles(chunk, TILE_WALL, 108, 112, 109, 113)
    fill_tiles(chunk, TILE_WALL, 114, 116, 115, 117)
    fill_tiles(chunk, TILE_WALL, 118, 120, 119, 121)
    fill_tiles(chunk, TILE_WALL, 104, 118, 105, 119)
    fill_tiles(chunk, TILE_WALL, 122, 114, 123, 115)
    fill_tiles(chunk, TILE_WALL, 110, 124, 111, 125)
    # Gundyr approach — more tombstone clusters (DS3: dense dark cemetery)
    fill_tiles(chunk, TILE_WALL, 96, 104, 97, 105)
    fill_tiles(chunk, TILE_WALL, 102, 108, 103, 109)
    fill_tiles(chunk, TILE_WALL, 98, 112, 99, 113)
    fill_tiles(chunk, TILE_WALL, 106, 110, 107, 111)
    # Dark Firelink — collapsed pillar fragments (DS3: ruined version of Firelink)
    fill_tiles(chunk, TILE_WALL, 132, 128, 133, 129)
    fill_tiles(chunk, TILE_WALL, 138, 132, 139, 133)
    fill_tiles(chunk, TILE_WALL, 144, 128, 145, 129)
    fill_tiles(chunk, TILE_WALL, 136, 136, 137, 137)
    fill_tiles(chunk, TILE_WALL, 142, 140, 143, 141)
    fill_tiles(chunk, TILE_WALL, 148, 134, 149, 135)
    # Dark Firelink interior — shrine debris (DS3: dark version of Firelink interior)
    fill_tiles(chunk, TILE_WALL, 128, 140, 129, 141)
    fill_tiles(chunk, TILE_WALL, 134, 144, 135, 145)
    fill_tiles(chunk, TILE_WALL, 140, 138, 141, 139)
    fill_tiles(chunk, TILE_WALL, 146, 142, 147, 143)

    # ================================================================
    # SESSION 17 FIDELITY PASS — UntendedGraves DS3 dark cemetery depth
    # ================================================================
    # Dark cemetery — tilted headstone clusters (DS3: packed dark cemetery with fallen graves)
    fill_tiles(chunk, TILE_WALL, 28, 20, 29, 21)
    fill_tiles(chunk, TILE_WALL, 36, 24, 37, 25)
    fill_tiles(chunk, TILE_WALL, 44, 28, 45, 29)
    fill_tiles(chunk, TILE_WALL, 52, 32, 53, 33)
    fill_tiles(chunk, TILE_WALL, 60, 36, 61, 37)
    # Black Knight patrol path — broken stone path (DS3: dark stone path where Black Knights patrol)
    fill_tiles(chunk, TILE_WALL, 48, 48, 49, 50)
    fill_tiles(chunk, TILE_WALL, 56, 52, 57, 54)
    fill_tiles(chunk, TILE_WALL, 64, 56, 65, 58)
    fill_tiles(chunk, TILE_WALL, 72, 60, 73, 62)
    fill_tiles(chunk, TILE_WALL, 42, 64, 43, 66)
    # Gundyr arena perimeter — darkened arch fragments (DS3: mirror of Iudex arena)
    fill_tiles(chunk, TILE_WALL, 94, 80, 95, 82)
    fill_tiles(chunk, TILE_WALL, 102, 84, 103, 86)
    fill_tiles(chunk, TILE_WALL, 110, 80, 111, 82)
    fill_tiles(chunk, TILE_WALL, 118, 76, 119, 78)
    fill_tiles(chunk, TILE_WALL, 126, 82, 127, 84)
    fill_tiles(chunk, TILE_WALL, 114, 90, 115, 92)
    # Dark Firelink — throne alcove walls (DS3: 5 empty lord thrones in dark shrine)
    fill_tiles(chunk, TILE_WALL, 120, 108, 121, 110)
    fill_tiles(chunk, TILE_WALL, 136, 106, 137, 108)
    fill_tiles(chunk, TILE_WALL, 144, 112, 145, 114)
    fill_tiles(chunk, TILE_WALL, 132, 116, 133, 118)
    fill_tiles(chunk, TILE_WALL, 140, 120, 141, 122)
    # Dark path edges — collapsed stone borders (DS3: crumbling path in total darkness)
    fill_tiles(chunk, TILE_WALL, 20, 26, 21, 28)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 36)
    fill_tiles(chunk, TILE_WALL, 40, 40, 41, 42)
    fill_tiles(chunk, TILE_WALL, 66, 50, 67, 52)
    fill_tiles(chunk, TILE_WALL, 76, 58, 77, 60)
    # Dark well debris — broken well near Dark Firelink (DS3: dark version of Firelink well)
    fill_tiles(chunk, TILE_WALL, 124, 118, 126, 120)
    fill_tiles(chunk, TILE_WALL, 138, 114, 140, 116)

    # ================================================================
    # SESSION 19 FIDELITY PASS — UntendedGraves DS3 dark cemetery depth
    # ================================================================
    # Champion Gundyr arena — dark crater debris (DS3: dark arena with dead Fire Keeper)
    fill_tiles(chunk, TILE_WALL, 98, 78, 99, 80)
    fill_tiles(chunk, TILE_WALL, 106, 82, 107, 84)
    fill_tiles(chunk, TILE_WALL, 114, 86, 115, 88)
    fill_tiles(chunk, TILE_WALL, 122, 90, 123, 92)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 88)
    # Dark tombstones — additional graves (DS3: cemetery mirrors Cemetery of Ash)
    fill_tiles(chunk, TILE_WALL, 24, 30, 25, 32)
    fill_tiles(chunk, TILE_WALL, 36, 38, 37, 40)
    fill_tiles(chunk, TILE_WALL, 48, 44, 49, 46)
    fill_tiles(chunk, TILE_WALL, 60, 52, 61, 54)
    fill_tiles(chunk, TILE_WALL, 72, 60, 73, 62)
    # Dark Firelink interior — more shrine debris (DS3: completely dark Firelink copy)
    fill_tiles(chunk, TILE_WALL, 116, 122, 117, 124)
    fill_tiles(chunk, TILE_WALL, 128, 126, 129, 128)
    fill_tiles(chunk, TILE_WALL, 148, 124, 149, 126)
    fill_tiles(chunk, TILE_WALL, 152, 128, 153, 130)
    fill_tiles(chunk, TILE_WALL, 112, 130, 113, 132)

    # ================================================================
    # SESSION 22 FIDELITY PASS — UntendedGraves DS3 dark cemetery details
    # ================================================================
    # Dark gravestone debris (DS3: broken headstones in the dark graveyard)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 29)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 33)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 40, 40, 41, 41)
    # Dark Firelink rubble (DS3: debris around the dark Firelink Shrine)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 45)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 56, 65, 57)
    # Gundyr arena stone fragments (DS3: broken stones near Champion Gundyr)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 61)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    fill_tiles(chunk, TILE_WALL, 82, 68, 83, 69)
    fill_tiles(chunk, TILE_WALL, 88, 72, 89, 73)
    # Ash pile mounds (DS3: ash accumulations in the dark version)
    fill_tiles(chunk, TILE_WALL, 94, 76, 95, 77)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 81)
    fill_tiles(chunk, TILE_WALL, 106, 84, 107, 85)
    fill_tiles(chunk, TILE_WALL, 112, 88, 113, 89)

    # ================================================================
    # SESSION 28 FIDELITY PASS — UntendedGraves DS3 dark cemetery details
    # ================================================================
    # Dark tombstone rows (DS3: broken tombstones in the shadow version)
    fill_tiles(chunk, TILE_WALL, 16, 30, 17, 31)
    fill_tiles(chunk, TILE_WALL, 22, 34, 23, 35)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 39)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    # Dark Firelink shrine stones (DS3: shrine stones in shadow Firelink)
    fill_tiles(chunk, TILE_WALL, 40, 46, 41, 47)
    fill_tiles(chunk, TILE_WALL, 46, 50, 47, 51)
    fill_tiles(chunk, TILE_WALL, 52, 54, 53, 55)
    fill_tiles(chunk, TILE_WALL, 58, 58, 59, 59)
    # Gundyr arena ash mounds (DS3: ash mounds in Champion Gundyr's arena)
    fill_tiles(chunk, TILE_WALL, 64, 62, 65, 63)
    fill_tiles(chunk, TILE_WALL, 70, 66, 71, 67)
    fill_tiles(chunk, TILE_WALL, 76, 70, 77, 71)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    # Dark path debris (DS3: debris along the dark cemetery path)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    fill_tiles(chunk, TILE_WALL, 94, 82, 95, 83)
    fill_tiles(chunk, TILE_WALL, 100, 86, 101, 87)
    fill_tiles(chunk, TILE_WALL, 106, 90, 107, 91)

    # ================================================================
    # SESSION 31 FIDELITY PASS — UntendedGraves DS3 dark cemetery details
    # ================================================================
    # Dark cemetery entrance debris (DS3: debris at the dark cemetery entrance)
    fill_tiles(chunk, TILE_WALL, 12, 22, 13, 23)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 27)
    fill_tiles(chunk, TILE_WALL, 24, 30, 25, 31)
    fill_tiles(chunk, TILE_WALL, 30, 34, 31, 35)
    # Dark hollow burial mounds (DS3: burial mounds in the shadow version)
    fill_tiles(chunk, TILE_WALL, 36, 38, 37, 39)
    fill_tiles(chunk, TILE_WALL, 42, 42, 43, 43)
    fill_tiles(chunk, TILE_WALL, 48, 46, 49, 47)
    fill_tiles(chunk, TILE_WALL, 54, 50, 55, 51)
    # Champion Gundyr arena ash (DS3: thick ash in Gundyr's arena)
    fill_tiles(chunk, TILE_WALL, 60, 54, 61, 55)
    fill_tiles(chunk, TILE_WALL, 66, 58, 67, 59)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 63)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    # Dark Firelink shrine path (DS3: overgrown path to dark shrine)
    fill_tiles(chunk, TILE_WALL, 84, 70, 85, 71)
    fill_tiles(chunk, TILE_WALL, 90, 74, 91, 75)
    fill_tiles(chunk, TILE_WALL, 96, 78, 97, 79)
    fill_tiles(chunk, TILE_WALL, 102, 82, 103, 83)

    # SESSION 41 FIDELITY PASS — Untended Graves DS3 details
    # DS3: Dark tombstones, ash-covered paths, dark Firelink rubble, Gundyr arena
    for tx in range(20, 55, 5):
        fill_tiles(chunk, TILE_WALL, tx, 38, tx+1, 39)             # Dark tombstone clusters
        fill_tiles(chunk, TILE_WALL, tx, 78, tx+1, 79)
    for tx in range(60, 95, 5):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+1, 43)             # Ash-covered paths
        fill_tiles(chunk, TILE_WALL, tx, 82, tx+1, 83)
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 57)                    # Dark Firelink rubble
    fill_tiles(chunk, TILE_WALL, 80, 60, 82, 62)                    # Gundyr arena debris
    fill_tiles(chunk, TILE_WALL, 110, 50, 112, 52)                  # Champion's gravestone
    for ty in range(45, 70, 7):
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)            # Dark path markers
    fill_tiles(chunk, TILE_WALL, 70, 90, 72, 92)                    # Collapsed wall
    # --- SESSION 45 terrain (Untended Graves) ---
    # DS3: Dark tombstones (mirror of Cemetery of Ash but corrupted)
    for tx in range(10, 20):
        if tx % 2 == 0:
            chunk[20][tx] = TILE_WALLTOP  # dark headstone
            chunk[22][tx] = TILE_WALLTOP
    # Collapsed Firelink Shrine rubble (DS3: destroyed version)
    for tx in range(30, 42):
        chunk[35][tx] = TILE_WALLTOP  # building debris
    for ty in range(32, 38):
        chunk[ty][36] = TILE_WALL  # collapsed wall
    # Gundyr arena ash piles (DS3: Champion Gundyr's arena)
    for tx in range(80, 95):
        chunk[70][tx] = TILE_WALLTOP  # ash drift
    for tx in range(85, 92):
        chunk[75][tx] = TILE_WALLTOP  # deep ash
    # Dark version coiled sword crater
    chunk[15][40] = TILE_WALLTOP
    chunk[15][41] = TILE_WALLTOP
    # Dead tree stumps (DS3: barren version of cemetery trees)
    for tx, ty in [(25, 45), (45, 50), (60, 48)]:
        chunk[ty][tx] = TILE_WALL  # stump
    # Dark cliff face
    for ty in range(5, 15):
        chunk[ty][5] = TILE_WALL
        chunk[ty][6] = TILE_WALL

    # --- SESSION 55 terrain (Untended Graves final) ---
    # DS3: Dark Firelink Shrine collapsed ceiling
    for tx in range(30, 42):
        chunk[40][tx] = TILE_WALLTOP  # ceiling debris
    # Champion Gundyr arena stone circle
    for tx in range(80, 92):
        if tx % 3 == 0:
            chunk[75][tx] = TILE_WALL  # arena stone
    # Dark tree stump cluster
    for tx, ty in [(50, 55), (65, 58), (78, 52)]:
        chunk[ty][tx] = TILE_WALL  # stump
    # Ash drift over the dark bonfire area
    for tx in range(20, 28):
        chunk[45][tx] = TILE_WALLTOP  # ash pile
    # Broken fence line (DS3: the cemetery fence in ruins)
    for tx in range(55, 65):
        chunk[35][tx] = TILE_WALLTOP  # fence debris

    # --- SESSION 89 DS3 terrain (Untended Graves detail pass) ---
    # DS3: Dark tombstones (mirroring Firelink's courtyard but darker)
    for tx in [20, 22, 24, 26, 28, 30, 32, 34, 36, 38]:
        for ty in [20, 22, 24]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Firelink shrine rubble (collapsed interior)
    for tx in range(35, 55):
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
    for tx in [38, 42, 46, 50]:
        for ty in [28, 29]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Gundyr arena ash (darkened version)
    for tx in range(60, 80):
        for ty in range(40, 55):
            chunk[tx][ty] = TILE_GROUND
    for tx in [60, 80]:
        for ty in range(40, 56):
            chunk[tx][ty] = TILE_WALL
    # DS3: Dark crater (impact site)
    for tx in range(68, 75):
        for ty in range(45, 52):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Tree stumps along the path
    for tx in [15, 25, 45, 55, 75, 85]:
        for ty in [35, 36]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Cliff faces around the area
    for tx in range(10, 95):
        chunk[tx][10] = TILE_WALL
        chunk[tx][9] = TILE_WALLTOP
    # DS3: Champion Gundyr's arena stone ring
    for tx in [65, 66, 67, 73, 74, 75]:
        for ty in [42, 52]:
            chunk[tx][ty] = TILE_WALL
    for tx in [65, 75]:
        for ty in range(42, 53):
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 93 DS3 terrain round 2 (Untended Graves) ---
    # DS3: Dark Firelink interior (collapsed shrine)
    for tx in range(30, 55):
        for ty in [28, 29]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Collapsed throne area
    for tx in [35, 38, 41, 44, 47]:
        for ty in [25, 26]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Champion Gundyr's stone arena
    for tx in range(60, 80):
        for ty in range(38, 55):
            chunk[tx][ty] = TILE_GROUND
    for tx in [60, 80]:
        for ty in range(38, 56):
            chunk[tx][ty] = TILE_WALL
    # DS3: Dark tombstone clusters
    for tx in [12, 14, 16, 18, 20, 82, 84, 86, 88, 90]:
        for ty in [18, 20, 22]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Shrine Handmaid's spot
    for tx in range(32, 38):
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Coiled sword fragment crater
    for tx in range(42, 48):
        for ty in range(32, 36):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Dark cliff faces
    for tx in range(5, 95):
        chunk[tx][8] = TILE_WALL
        chunk[tx][7] = TILE_WALLTOP
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/UntendedGraves.json") as _f:

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
    # Cover all JSON doc sections with walkable ground
    fill_tiles(chunk, TILE_GROUND, 30, 30, 77, 65)   # Dark Cemetery Entry
    fill_tiles(chunk, TILE_GROUND, 65, 56, 121, 96)   # Dark Cemetery Path
    fill_tiles(chunk, TILE_GROUND, 92, 88, 146, 127)  # Untended Graves Bonfire
    fill_tiles(chunk, TILE_GROUND, 126, 115, 173, 145) # Champion Gundyr Approach
    fill_tiles(chunk, TILE_GROUND, 138, 123, 195, 167) # Champion Gundyr Arena
    fill_tiles(chunk, TILE_GROUND, 156, 177, 223, 225) # Dark Firelink Shrine
    # Corridors connecting sections
    fill_tiles(chunk, TILE_GROUND, 51, 45, 95, 78)
    fill_tiles(chunk, TILE_GROUND, 91, 74, 121, 110)
    fill_tiles(chunk, TILE_GROUND, 117, 106, 152, 132)
    fill_tiles(chunk, TILE_GROUND, 148, 128, 168, 147)
    fill_tiles(chunk, TILE_GROUND, 164, 143, 192, 203)

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0]))
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100
    # print(f"  UntendedGraves (faithful DS3 layout) "
    # f"ground={pct:.1f}% connectivity={coverage}%")
    return "UntendedGraves", chunk, entities
