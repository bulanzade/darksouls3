from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_catacombs_of_carthus():
    """Catacombs of Carthus - underground tunnels with skeleton ball traps.
    Faithful DS3 layout: entry stairs -> skeleton ball corridor -> rope bridge ->
    lower tombs -> abandoned tomb -> Wolnir arena. Side path to Smouldering Lake.
    Design doc: 3600x3200, tight underground corridors with multiple levels.
    """
    chunk = new_chunk(288, 256)
    entities = []

    # ================================================================
    # SECTION 1: Entry stairs - doc: x=0,y=0,w=600,h=700
    # Stone steps descending into the catacombs, skeletons line the walls
    # ================================================================
    carve_ellipse(chunk, 15, 15, 10, 8)
    fill_tiles(chunk, TILE_GROUND, 8, 10, 28, 25)
    # Sarcophagi lining the walls
    fill_tiles(chunk, TILE_WALL, 12, 14, 13, 16)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 20)

    # ================================================================
    # SECTION 2: Skeleton ball corridor - doc: x=400,y=600,w=1000,h=400
    # Long straight corridor where a rolling skeleton ball attacks
    # Niches on sides for躲避, skeleton ambushes
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 22, 55, 38)
    # Side alcoves for dodging
    fill_tiles(chunk, TILE_GROUND, 20, 20, 26, 22)
    fill_tiles(chunk, TILE_GROUND, 35, 20, 41, 22)
    fill_tiles(chunk, TILE_GROUND, 48, 20, 54, 22)
    # Corridor walls (barriers in middle creating narrow passages)
    fill_tiles(chunk, TILE_WALL, 28, 26, 30, 30)
    fill_tiles(chunk, TILE_WALL, 42, 28, 44, 32)

    # ================================================================
    # SECTION 3: Rope bridge over abyss - doc: x=1200,y=400,w=1000,h=600
    # Narrow bridge, can be cut to create shortcut
    # ================================================================
    carve_ellipse(chunk, 65, 28, 14, 10)
    fill_tiles(chunk, TILE_GROUND, 52, 25, 72, 35)
    # Bridge approach corridor
    fill_tiles(chunk, TILE_GROUND, 50, 30, 58, 38)

    # ================================================================
    # SECTION 4: Lower tomb chambers - doc: x=400,y=900,w=800,h=700
    # Connected stone rooms full of skeleton swordsmen
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 42, 50, 72)
    carve_ellipse(chunk, 32, 55, 14, 12)
    # Cell walls creating tomb chambers
    fill_tiles(chunk, TILE_WALL, 22, 46, 24, 50)
    fill_tiles(chunk, TILE_WALL, 38, 48, 40, 52)
    fill_tiles(chunk, TILE_WALL, 28, 60, 30, 64)
    # Corridor from skeleton ball area down to tombs
    fill_tiles(chunk, TILE_GROUND, 25, 36, 35, 44)

    # ================================================================
    # SECTION 5: Skeleton wheel area - connects to lower levels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 48, 55, 75, 72)
    # Obstacles
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 63)
    fill_tiles(chunk, TILE_WALL, 65, 65, 67, 68)

    # ================================================================
    # SECTION 6: Abandoned tomb / Smouldering Lake passage - doc: x=800,y=1500
    # Side path with Fire Demon guarding descent to Smouldering Lake
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 10, 72, 40, 100)
    carve_ellipse(chunk, 25, 85, 10, 8)
    # Tight tunnel toward Smouldering Lake
    fill_tiles(chunk, TILE_GROUND, 30, 90, 48, 105)
    fill_tiles(chunk, TILE_GROUND, 15, 100, 35, 112)
    carve_ellipse(chunk, 25, 108, 8, 6)

    # ================================================================
    # SECTION 7: Path to Wolnir - wide corridor approaching boss
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 70, 55, 100, 80)
    fill_tiles(chunk, TILE_GROUND, 85, 70, 115, 90)

    # ================================================================
    # SECTION 8: Wolnir arena - doc: x=2500,y=2300,w=1000,h=800
    # Dark arena where Wolnir emerges from the abyss
    # ================================================================
    carve_ellipse(chunk, 125, 105, 22, 20)
    fill_tiles(chunk, TILE_GROUND, 105, 88, 148, 125)
    # Dark wall barriers at arena edges
    fill_tiles(chunk, TILE_WALL, 108, 92, 110, 95)
    fill_tiles(chunk, TILE_WALL, 140, 98, 142, 101)

    # Exit corridor to Irithyll
    fill_tiles(chunk, TILE_GROUND, 135, 85, 150, 100)

    # Connection from lower tombs to Wolnir path
    fill_tiles(chunk, TILE_GROUND, 45, 68, 55, 75)
    # Connection from bridge area to Wolnir path
    fill_tiles(chunk, TILE_GROUND, 68, 40, 78, 55)

    # === ADDITIONAL INTERNAL STRUCTURES — catacombs ===
    # Skeleton ball corridor — skull piles and bone walls
    fill_tiles(chunk, TILE_WALL, 25, 18, 27, 20)
    fill_tiles(chunk, TILE_WALL, 40, 22, 42, 24)
    fill_tiles(chunk, TILE_WALL, 55, 18, 57, 20)
    fill_tiles(chunk, TILE_WALL, 35, 32, 37, 34)
    fill_tiles(chunk, TILE_WALL, 50, 35, 52, 37)
    # Rope bridge area — cliff edges
    fill_tiles(chunk, TILE_WALL, 62, 25, 64, 28)
    fill_tiles(chunk, TILE_WALL, 78, 30, 80, 32)
    fill_tiles(chunk, TILE_WALL, 88, 35, 90, 37)
    # Lower tombs — sarcophagus walls
    fill_tiles(chunk, TILE_WALL, 20, 55, 22, 58)
    fill_tiles(chunk, TILE_WALL, 32, 60, 34, 62)
    fill_tiles(chunk, TILE_WALL, 42, 55, 44, 57)
    fill_tiles(chunk, TILE_WALL, 55, 62, 57, 64)
    fill_tiles(chunk, TILE_WALL, 28, 72, 30, 74)
    fill_tiles(chunk, TILE_WALL, 48, 78, 50, 80)
    # Wolnir path — bone pillars
    fill_tiles(chunk, TILE_WALL, 75, 55, 77, 57)
    fill_tiles(chunk, TILE_WALL, 90, 62, 92, 64)
    fill_tiles(chunk, TILE_WALL, 105, 68, 107, 70)
    fill_tiles(chunk, TILE_WALL, 115, 75, 117, 77)
    # Wolnir arena — ancient pillars
    fill_tiles(chunk, TILE_WALL, 112, 95, 114, 98)
    fill_tiles(chunk, TILE_WALL, 130, 100, 132, 103)
    fill_tiles(chunk, TILE_WALL, 120, 112, 122, 115)
    fill_tiles(chunk, TILE_WALL, 138, 108, 140, 110)

    # === MORE CATACOMBS DETAILS — DS3 fidelity ===
    # Entry stairs — more sarcophagi (DS3: stone coffins line the entry)
    fill_tiles(chunk, TILE_WALL, 10, 12, 11, 14)
    fill_tiles(chunk, TILE_WALL, 18, 16, 19, 18)
    fill_tiles(chunk, TILE_WALL, 24, 12, 25, 14)
    # Skeleton ball corridor — more bone pile walls and alcove barriers
    # DS3: narrow corridor with side alcoves to dodge rolling balls
    fill_tiles(chunk, TILE_WALL, 32, 24, 34, 26)
    fill_tiles(chunk, TILE_WALL, 45, 26, 47, 28)
    fill_tiles(chunk, TILE_WALL, 52, 30, 54, 32)
    fill_tiles(chunk, TILE_WALL, 22, 34, 24, 36)
    fill_tiles(chunk, TILE_WALL, 46, 34, 48, 36)
    # Rope bridge area — bridge support pillars and cliff edges
    # DS3: narrow rope bridge over dark abyss
    fill_tiles(chunk, TILE_WALL, 58, 28, 60, 30)
    fill_tiles(chunk, TILE_WALL, 68, 26, 70, 28)
    fill_tiles(chunk, TILE_WALL, 72, 32, 74, 34)
    fill_tiles(chunk, TILE_WALL, 82, 28, 84, 30)
    # Lower tomb chambers — more sarcophagus and tomb walls
    # DS3: interconnected tomb rooms with skeleton ambushes
    fill_tiles(chunk, TILE_WALL, 16, 50, 18, 52)
    fill_tiles(chunk, TILE_WALL, 26, 56, 28, 58)
    fill_tiles(chunk, TILE_WALL, 36, 54, 38, 56)
    fill_tiles(chunk, TILE_WALL, 45, 58, 47, 60)
    fill_tiles(chunk, TILE_WALL, 22, 64, 24, 66)
    fill_tiles(chunk, TILE_WALL, 38, 66, 40, 68)
    fill_tiles(chunk, TILE_WALL, 50, 68, 52, 70)
    fill_tiles(chunk, TILE_WALL, 42, 72, 44, 74)
    # Skeleton wheel area — rubble obstacles (DS3: rolling skeleton wheels)
    fill_tiles(chunk, TILE_WALL, 58, 58, 60, 60)
    fill_tiles(chunk, TILE_WALL, 68, 64, 70, 66)
    fill_tiles(chunk, TILE_WALL, 62, 70, 64, 72)
    fill_tiles(chunk, TILE_WALL, 72, 68, 74, 70)
    # Abandoned tomb — tunnel walls (DS3: descent to Smouldering Lake)
    fill_tiles(chunk, TILE_WALL, 12, 78, 14, 80)
    fill_tiles(chunk, TILE_WALL, 22, 82, 24, 84)
    fill_tiles(chunk, TILE_WALL, 32, 88, 34, 90)
    fill_tiles(chunk, TILE_WALL, 18, 92, 20, 94)
    fill_tiles(chunk, TILE_WALL, 28, 98, 30, 100)
    fill_tiles(chunk, TILE_WALL, 20, 106, 22, 108)
    fill_tiles(chunk, TILE_WALL, 35, 95, 37, 97)
    # Wolnir path — more bone pillars and ancient walls
    # DS3: dark corridor approaching Wolnir's arena
    fill_tiles(chunk, TILE_WALL, 78, 60, 80, 62)
    fill_tiles(chunk, TILE_WALL, 85, 58, 87, 60)
    fill_tiles(chunk, TILE_WALL, 95, 65, 97, 67)
    fill_tiles(chunk, TILE_WALL, 110, 72, 112, 74)
    fill_tiles(chunk, TILE_WALL, 100, 78, 102, 80)
    # Wolnir arena — more ancient pillars and ruins
    # DS3: dark arena where Wolnir emerges from the abyss
    fill_tiles(chunk, TILE_WALL, 118, 90, 120, 93)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 98)
    fill_tiles(chunk, TILE_WALL, 125, 105, 127, 108)
    fill_tiles(chunk, TILE_WALL, 142, 102, 144, 105)
    fill_tiles(chunk, TILE_WALL, 115, 115, 117, 118)
    fill_tiles(chunk, TILE_WALL, 132, 112, 134, 115)

    # === SESSION 6 FIDELITY PASS — Catacombs of Carthus ===
    # Entry stairs — stone urn decorations (DS3: burial urns flanking entry path)
    fill_tiles(chunk, TILE_WALL, 8, 16, 9, 18)
    fill_tiles(chunk, TILE_WALL, 26, 14, 27, 16)
    fill_tiles(chunk, TILE_WALL, 14, 22, 15, 24)
    # Entry arch pillars (DS3: stone archway at catacomb entrance)
    fill_tiles(chunk, TILE_WALL, 10, 8, 12, 10)
    fill_tiles(chunk, TILE_WALL, 24, 8, 26, 10)
    # Skeleton ball corridor — more alcove barriers (DS3: niches to dodge boulder)
    fill_tiles(chunk, TILE_WALL, 17, 26, 19, 28)
    fill_tiles(chunk, TILE_WALL, 38, 20, 40, 22)
    fill_tiles(chunk, TILE_WALL, 53, 22, 55, 24)
    # Skull pile formations (DS3: bone piles throughout corridors)
    fill_tiles(chunk, TILE_WALL, 30, 30, 32, 32)
    fill_tiles(chunk, TILE_WALL, 48, 28, 50, 30)
    fill_tiles(chunk, TILE_WALL, 56, 36, 58, 38)
    # Rope bridge — bridge cable anchor points (DS3: rope bridge over deep abyss)
    fill_tiles(chunk, TILE_WALL, 60, 22, 62, 24)
    fill_tiles(chunk, TILE_WALL, 76, 28, 78, 30)
    fill_tiles(chunk, TILE_WALL, 85, 32, 87, 34)
    fill_tiles(chunk, TILE_WALL, 80, 36, 82, 38)
    # Lower tombs — additional tomb chamber dividers (DS3: interlinked stone rooms)
    fill_tiles(chunk, TILE_WALL, 14, 46, 16, 48)
    fill_tiles(chunk, TILE_WALL, 24, 48, 26, 50)
    fill_tiles(chunk, TILE_WALL, 40, 52, 42, 54)
    fill_tiles(chunk, TILE_WALL, 48, 56, 50, 58)
    fill_tiles(chunk, TILE_WALL, 16, 68, 18, 70)
    fill_tiles(chunk, TILE_WALL, 34, 70, 36, 72)
    # Skeleton wheel tracks (DS3: grooves in stone from rolling wheels)
    fill_tiles(chunk, TILE_WALL, 52, 64, 54, 66)
    fill_tiles(chunk, TILE_WALL, 66, 62, 68, 64)
    fill_tiles(chunk, TILE_WALL, 70, 70, 72, 72)
    # Abandoned tomb — stalactite formations (DS3: underground cave with rock formations)
    fill_tiles(chunk, TILE_WALL, 16, 76, 18, 78)
    fill_tiles(chunk, TILE_WALL, 26, 86, 28, 88)
    fill_tiles(chunk, TILE_WALL, 34, 92, 36, 94)
    fill_tiles(chunk, TILE_WALL, 24, 100, 26, 102)
    # Wolnir path — dark corridor ancient stonework (DS3: ancient carved passage)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    fill_tiles(chunk, TILE_WALL, 82, 64, 84, 66)
    fill_tiles(chunk, TILE_WALL, 98, 70, 100, 72)
    fill_tiles(chunk, TILE_WALL, 108, 76, 110, 78)
    # Wolnir arena — abyss edge pillars (DS3: dark arena with glowing bracelets)
    fill_tiles(chunk, TILE_WALL, 110, 88, 112, 90)
    fill_tiles(chunk, TILE_WALL, 128, 94, 130, 96)
    fill_tiles(chunk, TILE_WALL, 138, 106, 140, 108)
    fill_tiles(chunk, TILE_WALL, 122, 118, 124, 120)
    fill_tiles(chunk, TILE_WALL, 145, 110, 147, 112)
    fill_tiles(chunk, TILE_WALL, 130, 118, 132, 120)

    # ================================================================
    # SESSION 9 FIDELITY PASS — CatacombsOfCarthus architectural details
    # ================================================================
    # Entry stairs — bone pile debris (DS3: bones scattered on entry stairs)
    fill_tiles(chunk, TILE_WALL, 12, 10, 13, 11)
    fill_tiles(chunk, TILE_WALL, 18, 14, 19, 15)
    # Skeleton ball corridor — skull niches (DS3: wall-mounted skull alcoves)
    fill_tiles(chunk, TILE_WALL, 22, 20, 23, 21)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    fill_tiles(chunk, TILE_WALL, 34, 18, 35, 19)
    # Rope bridge approach — crumbling pillar bases (DS3: stone pillars supporting bridge)
    fill_tiles(chunk, TILE_WALL, 40, 32, 41, 33)
    fill_tiles(chunk, TILE_WALL, 44, 34, 45, 35)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    # Lower tombs — collapsed coffin lids (DS3: broken sarcophagi in lower chambers)
    fill_tiles(chunk, TILE_WALL, 20, 50, 21, 51)
    fill_tiles(chunk, TILE_WALL, 26, 52, 27, 53)
    fill_tiles(chunk, TILE_WALL, 14, 54, 15, 55)
    fill_tiles(chunk, TILE_WALL, 30, 56, 31, 57)
    # Skeleton horde room — bone wall formations (DS3: walls of stacked bones)
    fill_tiles(chunk, TILE_WALL, 48, 60, 49, 61)
    fill_tiles(chunk, TILE_WALL, 52, 64, 53, 65)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 44, 66, 45, 67)
    # Abandoned tomb alcove — ritual stones (DS3: dark ritual area)
    fill_tiles(chunk, TILE_WALL, 18, 80, 19, 81)
    fill_tiles(chunk, TILE_WALL, 22, 84, 23, 85)
    fill_tiles(chunk, TILE_WALL, 16, 88, 17, 89)
    # Wolnir arena approach — giant sword fragments (DS3: Wolnir's swords in sand)
    fill_tiles(chunk, TILE_WALL, 30, 94, 31, 95)
    fill_tiles(chunk, TILE_WALL, 36, 96, 37, 97)
    fill_tiles(chunk, TILE_WALL, 42, 92, 43, 93)
    # Wolnir arena — skeleton mound base (DS3: massive pile of skeletons)
    fill_tiles(chunk, TILE_WALL, 60, 98, 61, 99)
    fill_tiles(chunk, TILE_WALL, 64, 102, 65, 103)
    fill_tiles(chunk, TILE_WALL, 70, 96, 71, 97)
    fill_tiles(chunk, TILE_WALL, 56, 104, 57, 105)
    fill_tiles(chunk, TILE_WALL, 68, 106, 69, 107)
    # Smouldering Lake side path — volcanic rock (DS3: lava-adjacent tunnels)
    fill_tiles(chunk, TILE_WALL, 8, 108, 9, 109)
    fill_tiles(chunk, TILE_WALL, 14, 110, 15, 111)
    fill_tiles(chunk, TILE_WALL, 20, 106, 21, 107)
    # Irithyll exit — frost-touched stone (DS3: cold stone near Irithyll entrance)
    fill_tiles(chunk, TILE_WALL, 140, 88, 141, 89)
    fill_tiles(chunk, TILE_WALL, 148, 92, 149, 93)
    fill_tiles(chunk, TILE_WALL, 136, 96, 137, 97)

    # ================================================================
    # DS3 STRUCTURAL WALLS — Catacombs of Carthus catacomb architecture
    # DS3: underground catacombs with bone piles, narrow corridors,
    # rolling skeleton balls, rope bridge, and Wolnir tomb
    # ================================================================
    # Entry stairs — stone step walls (DS3: descent into catacombs)
    fill_tiles(chunk, TILE_WALL, 24, 22, 28, 28)    # Stair wall left
    fill_tiles(chunk, TILE_WALL, 36, 20, 40, 26)    # Stair wall right
    fill_tiles(chunk, TILE_WALL, 30, 30, 34, 34)    # Stair divider
    # First skeleton ball corridor — narrow passage walls (DS3: rolling ball trap)
    fill_tiles(chunk, TILE_WALL, 50, 40, 54, 46)    # Corridor wall left
    fill_tiles(chunk, TILE_WALL, 62, 38, 66, 44)    # Corridor wall right
    fill_tiles(chunk, TILE_WALL, 56, 46, 60, 50)    # Corridor center wall
    # Upper catacombs — bone pile walls (DS3: bone piles with reanimating skeletons)
    fill_tiles(chunk, TILE_WALL, 78, 54, 82, 60)    # Bone pile wall 1
    fill_tiles(chunk, TILE_WALL, 92, 52, 96, 58)    # Bone pile wall 2
    fill_tiles(chunk, TILE_WALL, 84, 62, 88, 68)    # Bone pile wall 3
    # Second skeleton ball area — narrow corridor walls (DS3: another rolling ball)
    fill_tiles(chunk, TILE_WALL, 100, 72, 104, 78)  # Corridor wall left
    fill_tiles(chunk, TILE_WALL, 116, 70, 120, 76)  # Corridor wall right
    fill_tiles(chunk, TILE_WALL, 108, 78, 112, 82)  # Corridor center wall
    # Rope bridge area — bridge anchor walls (DS3: wooden rope bridge)
    fill_tiles(chunk, TILE_WALL, 126, 84, 130, 90)  # Bridge anchor left
    fill_tiles(chunk, TILE_WALL, 140, 82, 144, 88)  # Bridge anchor right
    # Wolnir tomb — boss arena walls (DS3: dark abyss tomb with Wolnir)
    fill_tiles(chunk, TILE_WALL, 130, 100, 134, 106) # Tomb wall NW
    fill_tiles(chunk, TILE_WALL, 148, 98, 152, 104)  # Tomb wall NE
    fill_tiles(chunk, TILE_WALL, 134, 110, 138, 116) # Tomb wall SW
    fill_tiles(chunk, TILE_WALL, 146, 108, 150, 114) # Tomb wall SE

    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 32 * 16, 38 * 16))     # Entry
    entities.append(make_entity("Bonfire", 222 * 16, 187 * 16))     # Abandoned Tomb
    entities.append(make_entity("Bonfire", 102 * 16, 187 * 16))   # Wolnir

    # Boss - Wolnir
    entities.append(make_entity("BossSpawn", 222 * 16, 187 * 16))

    # Enemies — DS3 Catacombs of Carthus: Skeleton Swordsmen, Skeleton Wheels,
    # Hound-Rats, Writhing Rotten Flesh, Black Knight (Tsorig invasion), Crystal Lizard
    # Items — DS3 Catacombs of Carthus (verified against wiki)
    # 2x Sharp Gem, Dark Gem, Carthus Pyromancy Tome, Grave Warden Pyromancy Tome,
    # Grave Warden's Ashes, Witch's Ring, Carthus Bloodring, Carthus Milkring,
    # Carthus Rouge x2, Old Sage's Blindfold, Knight Slayer's Ring,
    # Undead Bone Shard, Titanite Shard x2, Large Titanite Shard x2, Twinkling Titanite,
    # Yellow Bug Pellet x3, Black Bug Pellet x2, Bloodred Moss Clump x3,
    # Ember x2, Soul of a Deserted Corpse x2, Soul of a Nameless Soldier x2,
    # Large Soul of an Unknown Traveler
    for kind, name, tx, ty, val in [
        # Upper Catacombs — entry area
        ("Consumable", "Sharp Gem", 18, 16, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 24, 18, 200),
        ("Consumable", "Carthus Rouge", 25, 22, 0),
        ("Consumable", "Yellow Bug Pellet", 30, 18, 0),
        ("Consumable", "Yellow Bug Pellet", 32, 19, 0),
        ("Consumable", "Yellow Bug Pellet", 34, 20, 0),
        ("Consumable", "Black Bug Pellet", 38, 20, 0),
        ("Consumable", "Black Bug Pellet", 38, 23, 0),
        ("Consumable", "Bloodred Moss Clump", 40, 19, 0),
        ("Consumable", "Bloodred Moss Clump", 42, 20, 0),
        ("Consumable", "Bloodred Moss Clump", 44, 21, 0),
        # Skeleton ball corridor area
        ("Consumable", "Carthus Pyromancy Tome", 40, 28, 0),
        ("TitaniteShard", "Titanite Shard", 48, 30, 0),
        ("Consumable", "Carthus Rouge", 50, 32, 0),
        ("Consumable", "Dark Gem", 52, 36, 0),
        ("SoulOrb", "Soul of a Deserted Corpse", 20, 30, 200),
        # Lower tomb chambers
        ("Consumable", "Grave Warden's Ashes", 28, 50, 0),
        ("Consumable", "Old Sage's Blindfold", 48, 48, 0),
        ("TitaniteShard", "Large Titanite Shard", 35, 55, 0),
        # Large Titanite Shard removed (extra — wiki says 1x for Catacombs)
        ("SoulOrb", "Soul of a Nameless Soldier", 32, 55, 800),
        # Deep tomb — Grave Warden area
        ("Consumable", "Grave Warden Pyromancy Tome", 40, 64, 0),
        ("RingDrop", "Carthus Milkring", 28, 62, 0),
        ("RingDrop", "Carthus Bloodring", 55, 58, 0),
        ("TitaniteShard", "Twinkling Titanite", 42, 66, 0),
        # Skeleton bridge area
        ("Consumable", "Sharp Gem", 58, 40, 0),
        ("TitaniteShard", "Titanite Shard", 62, 45, 0),
        ("Ember", "Ember", 65, 50, 0),
        # Ember removed (duplicate — wiki says 1x Ember for Catacombs of Carthus)
        ("SoulOrb", "Soul of a Nameless Soldier", 70, 52, 800),
        ("SoulOrb", "Large Soul of an Unknown Traveler", 72, 55, 800),
        # Knight Slayer Tsorig area
        ("RingDrop", "Knight Slayer's Ring", 45, 70, 0),
        # Abandoned Tomb / Wolnir approach
        ("RingDrop", "Witch's Ring", 25, 90, 0),
        ("UndeadBoneShard", "Undead Bone Shard", 30, 85, 0),
        # Titanite Shard removed (extra — wiki says 2x for Catacombs)
        # Titanite Shard removed (extra — wiki says 2x for Catacombs)
    ]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    entities.append(make_entity("Npc", 193 * 16, 156 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Oh, hello, we meet again|Have you seen Horace anywhere?|I have been separated from him|I am worried... Please tell me if you find him")]))
    entities.append(make_entity("Npc", 17 * 16, 19 * 16, [make_field("name", "String", "Horace the Hushed"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#606060"), make_field("dialogue", "String", "...|(nods slowly)|(points toward the deeper catacombs)|(holds shield tighter)")]))

    # Fog Gate back to Farron Keep (DS3: return path from Catacombs entrance)
    entities.append(make_entity("FogGate", 32 * 16, 32 * 16, [
        make_field("dest_area", "String", "FarronKeep"),
        make_field("dest_x", "Float", 4400.0), make_field("dest_y", "Float", 3440.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 102 * 16, 200 * 16, [
        make_field("dest_area", "String", "SmoulderingLake"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 237 * 16, 193 * 16, [
        make_field("dest_area", "String", "Irithyll"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))

    # Lights - warm torch light in dark catacombs
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 35 * 16, 30 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.5), make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 25 * 16, 85 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 125 * 16, 100 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.3), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.35)]))
    # SESSION 10 FIDELITY PASS — Catacombs of Carthus
    # Additional DS3-faithful terrain: bone pile debris, skull niche alcoves,
    # collapsed coffin lids, skeleton mound clusters, Wolnir approach bones
    # Entry stairs — skull niche alcoves (DS3: skulls embedded in walls)
    fill_tiles(chunk, TILE_WALL, 16, 16, 17, 17)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 19)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    # Skeleton ball corridor — bone pile debris (DS3: bone piles throughout corridor)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 29)
    fill_tiles(chunk, TILE_WALL, 38, 32, 39, 33)
    fill_tiles(chunk, TILE_WALL, 44, 26, 45, 27)
    fill_tiles(chunk, TILE_WALL, 28, 24, 29, 25)
    # Side alcoves — collapsed coffin lids (DS3: broken coffins in alcoves)
    fill_tiles(chunk, TILE_WALL, 48, 22, 49, 23)
    fill_tiles(chunk, TILE_WALL, 54, 28, 55, 29)
    fill_tiles(chunk, TILE_WALL, 42, 30, 43, 31)
    # Rope bridge area — cliff edge bones (DS3: bones on cliff edges near bridge)
    fill_tiles(chunk, TILE_WALL, 58, 28, 59, 29)
    fill_tiles(chunk, TILE_WALL, 62, 32, 63, 33)
    fill_tiles(chunk, TILE_WALL, 66, 34, 67, 35)
    # Lower tomb chambers — skeleton mound clusters (DS3: dense bone mounds)
    fill_tiles(chunk, TILE_WALL, 18, 46, 19, 47)
    fill_tiles(chunk, TILE_WALL, 24, 50, 25, 51)
    fill_tiles(chunk, TILE_WALL, 30, 54, 31, 55)
    fill_tiles(chunk, TILE_WALL, 36, 58, 37, 59)
    fill_tiles(chunk, TILE_WALL, 42, 62, 43, 63)
    fill_tiles(chunk, TILE_WALL, 22, 56, 23, 57)
    fill_tiles(chunk, TILE_WALL, 34, 60, 35, 61)
    # Carthus Wyvern area — bone and ash debris (DS3: smoldering remains)
    fill_tiles(chunk, TILE_WALL, 50, 68, 51, 69)
    fill_tiles(chunk, TILE_WALL, 56, 72, 57, 73)
    fill_tiles(chunk, TILE_WALL, 62, 70, 63, 71)
    # Wolnir approach — skull wall niches (DS3: giant skull wall before arena)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 81)
    fill_tiles(chunk, TILE_WALL, 108, 84, 109, 85)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 122, 92, 123, 93)
    fill_tiles(chunk, TILE_WALL, 112, 86, 113, 87)
    fill_tiles(chunk, TILE_WALL, 104, 82, 105, 83)

    # SESSION 10 PASS B — CatacombsOfCarthus
    # Additional DS3 terrain: bone pile clusters, Wolnir approach bones, skeleton alcove debris
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
    # SESSION 12 FIDELITY PASS — CatacombsOfCarthus DS3 architectural details
    # ================================================================
    # Bone throne fragments (DS3: Carthus ruler bone thrones in alcoves)
    fill_tiles(chunk, TILE_WALL, 16, 22, 17, 24)
    fill_tiles(chunk, TILE_WALL, 24, 26, 25, 28)
    fill_tiles(chunk, TILE_WALL, 32, 22, 33, 24)
    fill_tiles(chunk, TILE_WALL, 40, 28, 41, 30)
    # Skull candle alcoves (DS3: skull-shaped niches with candles on walls)
    fill_tiles(chunk, TILE_WALL, 48, 34, 49, 36)
    fill_tiles(chunk, TILE_WALL, 56, 30, 57, 32)
    fill_tiles(chunk, TILE_WALL, 64, 36, 65, 38)
    fill_tiles(chunk, TILE_WALL, 72, 32, 73, 34)
    # Rusted chain mechanism debris (DS3: chain-driven skeleton ball mechanisms)
    fill_tiles(chunk, TILE_WALL, 20, 40, 21, 42)
    fill_tiles(chunk, TILE_WALL, 28, 44, 29, 46)
    fill_tiles(chunk, TILE_WALL, 36, 38, 37, 40)
    fill_tiles(chunk, TILE_WALL, 44, 42, 45, 44)
    # Skeleton ball track grooves (DS3: worn grooves where skeleton balls roll)
    fill_tiles(chunk, TILE_WALL, 52, 48, 54, 49)
    fill_tiles(chunk, TILE_WALL, 60, 46, 62, 47)
    fill_tiles(chunk, TILE_WALL, 68, 50, 70, 51)
    fill_tiles(chunk, TILE_WALL, 76, 48, 78, 49)
    # Rope bridge anchor stones (DS3: stone anchors for the rope bridge)
    fill_tiles(chunk, TILE_WALL, 88, 38, 89, 40)
    fill_tiles(chunk, TILE_WALL, 96, 42, 97, 44)
    fill_tiles(chunk, TILE_WALL, 104, 36, 105, 38)
    fill_tiles(chunk, TILE_WALL, 112, 40, 113, 42)
    # Bronze urn debris (DS3: Carthus burial urns scattered in corridors)
    fill_tiles(chunk, TILE_WALL, 24, 56, 25, 58)
    fill_tiles(chunk, TILE_WALL, 36, 60, 37, 62)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 56)
    fill_tiles(chunk, TILE_WALL, 60, 58, 61, 60)
    # Sarcophagus lid fragments (DS3: broken stone coffin lids throughout)
    fill_tiles(chunk, TILE_WALL, 72, 54, 74, 55)
    fill_tiles(chunk, TILE_WALL, 84, 58, 86, 59)
    fill_tiles(chunk, TILE_WALL, 96, 52, 98, 53)
    fill_tiles(chunk, TILE_WALL, 108, 56, 110, 57)
    # Cobweb-covered arch stones (DS3: dusty archways between tomb sections)
    fill_tiles(chunk, TILE_WALL, 120, 48, 122, 49)
    fill_tiles(chunk, TILE_WALL, 132, 52, 134, 53)
    fill_tiles(chunk, TILE_WALL, 144, 46, 146, 47)
    fill_tiles(chunk, TILE_WALL, 136, 60, 138, 61)
    # Wolnir wall carving fragments (DS3: giant skull carvings before boss)
    fill_tiles(chunk, TILE_WALL, 100, 68, 102, 70)
    fill_tiles(chunk, TILE_WALL, 114, 72, 116, 74)
    fill_tiles(chunk, TILE_WALL, 128, 66, 130, 68)
    fill_tiles(chunk, TILE_WALL, 142, 70, 144, 72)

    # ================================================================
    # SESSION 13 FIDELITY PASS — CatacombsOfCarthus DS3 architecture
    # ================================================================
    # Entry stairs — skull-lined walls (DS3: skulls embedded in catacomb walls)
    fill_tiles(chunk, TILE_WALL, 8, 12, 9, 13)
    fill_tiles(chunk, TILE_WALL, 14, 16, 15, 17)
    fill_tiles(chunk, TILE_WALL, 10, 20, 11, 21)
    # Rolling ball corridor — alcove debris (DS3: skeleton ball trap corridor)
    fill_tiles(chunk, TILE_WALL, 18, 24, 19, 25)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 29)
    fill_tiles(chunk, TILE_WALL, 26, 26, 27, 27)
    # Upper catacombs — bone pile walls (DS3: reanimating skeletons in bone piles)
    fill_tiles(chunk, TILE_WALL, 30, 32, 31, 33)
    fill_tiles(chunk, TILE_WALL, 36, 36, 37, 37)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 48, 38, 49, 39)
    # Second ball corridor — narrow passage walls (DS3: second skeleton ball area)
    fill_tiles(chunk, TILE_WALL, 54, 42, 55, 43)
    fill_tiles(chunk, TILE_WALL, 58, 46, 59, 47)
    fill_tiles(chunk, TILE_WALL, 62, 44, 63, 45)
    # Rope bridge — frayed rope posts (DS3: collapsing rope bridge)
    fill_tiles(chunk, TILE_WALL, 66, 50, 67, 51)
    fill_tiles(chunk, TILE_WALL, 72, 54, 73, 55)
    fill_tiles(chunk, TILE_WALL, 78, 52, 79, 53)
    # Bridge descent — ladder rung stones (DS3: ladder down to Smouldering Lake)
    fill_tiles(chunk, TILE_WALL, 32, 58, 33, 59)
    fill_tiles(chunk, TILE_WALL, 28, 62, 29, 63)
    fill_tiles(chunk, TILE_WALL, 36, 66, 37, 67)

    # ================================================================
    # SESSION 15 FIDELITY PASS — CatacombsOfCarthus additional DS3 details
    # ================================================================
    # Skeleton ball tracks — groove debris (DS3: carved stone grooves for rolling balls)
    fill_tiles(chunk, TILE_WALL, 44, 46, 45, 47)
    fill_tiles(chunk, TILE_WALL, 50, 48, 51, 49)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 62, 50, 63, 51)
    # Wolnir tomb — golden bracelet debris (DS3: Wolnir's golden bracelets glow)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 61)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 63)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 67)
    # Carthus worm alcove — sand debris (DS3: Carthus Sandworm emerges from sand)
    fill_tiles(chunk, TILE_WALL, 84, 58, 85, 59)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 63)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    # Abandoned tomb — coffin lid debris (DS3: broken coffins near Smouldering Lake entrance)
    fill_tiles(chunk, TILE_WALL, 24, 68, 25, 69)
    fill_tiles(chunk, TILE_WALL, 20, 72, 21, 73)
    fill_tiles(chunk, TILE_WALL, 30, 70, 31, 71)

    # ================================================================
    # SESSION 18 FIDELITY PASS — CatacombsOfCarthus DS3 catacomb depth
    # ================================================================
    # Entry staircase — skull niche alcoves (DS3: skull-lined walls at entrance)
    fill_tiles(chunk, TILE_WALL, 12, 22, 13, 23)
    fill_tiles(chunk, TILE_WALL, 16, 26, 17, 27)
    fill_tiles(chunk, TILE_WALL, 10, 28, 11, 29)
    fill_tiles(chunk, TILE_WALL, 14, 30, 15, 31)
    # Skeleton ball corridor — track grooves (DS3: rolling skeleton ball mechanism)
    fill_tiles(chunk, TILE_WALL, 38, 34, 39, 35)
    fill_tiles(chunk, TILE_WALL, 42, 38, 43, 39)
    fill_tiles(chunk, TILE_WALL, 46, 42, 47, 43)
    fill_tiles(chunk, TILE_WALL, 52, 36, 53, 37)
    fill_tiles(chunk, TILE_WALL, 58, 40, 59, 41)
    # Lower tombs — sarcophagus lids (DS3: burial chambers with sealed tombs)
    fill_tiles(chunk, TILE_WALL, 96, 42, 97, 43)
    fill_tiles(chunk, TILE_WALL, 102, 48, 103, 49)
    fill_tiles(chunk, TILE_WALL, 108, 44, 109, 45)
    fill_tiles(chunk, TILE_WALL, 114, 50, 115, 51)
    # Smouldering Lake descent — ash-covered steps (DS3: path down to lava area)
    fill_tiles(chunk, TILE_WALL, 34, 74, 35, 75)
    fill_tiles(chunk, TILE_WALL, 28, 78, 29, 79)
    fill_tiles(chunk, TILE_WALL, 38, 82, 39, 83)
    fill_tiles(chunk, TILE_WALL, 26, 84, 27, 85)
    fill_tiles(chunk, TILE_WALL, 32, 86, 33, 87)

    # ================================================================
    # SESSION 21 FIDELITY PASS — CatacombsOfCarthus DS3 crypt details
    # ================================================================
    # Bone chariot track debris (DS3: skeleton chariot tracks through corridors)
    fill_tiles(chunk, TILE_WALL, 16, 22, 18, 24)
    fill_tiles(chunk, TILE_WALL, 22, 26, 24, 28)
    fill_tiles(chunk, TILE_WALL, 28, 30, 30, 32)
    fill_tiles(chunk, TILE_WALL, 34, 28, 36, 30)
    # Crypt pillar fragments (DS3: broken pillars in Wolnir's antechamber)
    fill_tiles(chunk, TILE_WALL, 46, 54, 48, 56)
    fill_tiles(chunk, TILE_WALL, 52, 58, 54, 60)
    fill_tiles(chunk, TILE_WALL, 40, 50, 42, 52)
    # Skull candle alcove walls (DS3: skull-lined alcoves with candles)
    fill_tiles(chunk, TILE_WALL, 58, 34, 60, 36)
    fill_tiles(chunk, TILE_WALL, 64, 38, 66, 40)
    fill_tiles(chunk, TILE_WALL, 70, 36, 72, 38)
    fill_tiles(chunk, TILE_WALL, 76, 42, 78, 44)
    # Broken sarcophagus fragments (DS3: destroyed coffins in lower tombs)
    fill_tiles(chunk, TILE_WALL, 20, 40, 22, 42)
    fill_tiles(chunk, TILE_WALL, 26, 44, 28, 46)
    fill_tiles(chunk, TILE_WALL, 34, 48, 36, 50)
    fill_tiles(chunk, TILE_WALL, 14, 52, 16, 54)
    # Rope bridge anchor stones (DS3: stone posts anchoring the rope bridge)
    fill_tiles(chunk, TILE_WALL, 48, 28, 50, 30)
    fill_tiles(chunk, TILE_WALL, 54, 32, 56, 34)
    fill_tiles(chunk, TILE_WALL, 60, 36, 62, 38)
    fill_tiles(chunk, TILE_WALL, 66, 40, 68, 42)

    # ================================================================
    # SESSION 24 FIDELITY PASS — CatacombsOfCarthus DS3 catacomb details
    # ================================================================
    # Chariot track groove debris (DS3: skeleton chariot groove marks)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    # Burial chamber pillars (DS3: stone pillars supporting catacomb ceiling)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    # Wolnir bracelet debris (DS3: Wolnir's golden bracelets scattered in arena)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    # Smouldering Lake descent steps (DS3: steps down to the lava area)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)

    # ================================================================
    # SESSION 29 FIDELITY PASS — CatacombsOfCarthus DS3 catacomb details
    # ================================================================
    # Skeleton ball mechanism debris (DS3: mechanical parts for rolling balls)
    fill_tiles(chunk, TILE_WALL, 20, 36, 21, 37)
    fill_tiles(chunk, TILE_WALL, 26, 40, 27, 41)
    fill_tiles(chunk, TILE_WALL, 32, 44, 33, 45)
    fill_tiles(chunk, TILE_WALL, 38, 48, 39, 49)
    # Rope bridge anchor posts (DS3: wooden posts holding the rope bridge)
    fill_tiles(chunk, TILE_WALL, 44, 52, 45, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    fill_tiles(chunk, TILE_WALL, 62, 64, 63, 65)
    # Wolnir's abyss edge (DS3: dark void at the edge of Wolnir's arena)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 74, 72, 75, 73)
    fill_tiles(chunk, TILE_WALL, 80, 76, 81, 77)
    fill_tiles(chunk, TILE_WALL, 86, 80, 87, 81)
    # Carthus Sandworm tunnel (DS3: sandworm burrow near Smouldering Lake)
    fill_tiles(chunk, TILE_WALL, 92, 84, 93, 85)
    fill_tiles(chunk, TILE_WALL, 98, 88, 99, 89)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 93)
    fill_tiles(chunk, TILE_WALL, 110, 96, 111, 97)

    # ================================================================
    # SESSION 32 FIDELITY PASS — CatacombsOfCarthus DS3 catacomb details
    # ================================================================
    # Skeleton ball groove marks (DS3: deep grooves from rolling balls)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    fill_tiles(chunk, TILE_WALL, 28, 42, 29, 43)
    fill_tiles(chunk, TILE_WALL, 34, 46, 35, 47)
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 51)
    # Burial chamber wall carvings (DS3: carved walls in the tombs)
    fill_tiles(chunk, TILE_WALL, 46, 54, 47, 55)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 59)
    fill_tiles(chunk, TILE_WALL, 58, 62, 59, 63)
    fill_tiles(chunk, TILE_WALL, 64, 66, 65, 67)
    # Wolnir's golden bracelet debris (DS3: Wolnir's bracelets in the arena)
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 71)
    fill_tiles(chunk, TILE_WALL, 76, 74, 77, 75)
    fill_tiles(chunk, TILE_WALL, 82, 78, 83, 79)
    fill_tiles(chunk, TILE_WALL, 88, 82, 89, 83)
    # Smouldering Lake descent (DS3: path down to the lava area)
    fill_tiles(chunk, TILE_WALL, 94, 86, 95, 87)
    fill_tiles(chunk, TILE_WALL, 100, 90, 101, 91)
    fill_tiles(chunk, TILE_WALL, 106, 94, 107, 95)
    fill_tiles(chunk, TILE_WALL, 112, 98, 113, 99)

    # SESSION 39 FIDELITY PASS — Catacombs of Carthus DS3 details
    # DS3: Chariot track grooves, burial niches, Wolnir bracelet pedestals, rope bridge anchors
    for tx in range(20, 60, 5):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+1, 36)             # Chariot track grooves
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+1, 76)
    for tx in range(65, 110, 5):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 41)             # Burial niche frames
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+1, 81)
    for ty in range(30, 70, 8):
        fill_tiles(chunk, TILE_WALL, 30, ty, 31, ty+1)             # Skeleton bone piles
        fill_tiles(chunk, TILE_WALL, 90, ty, 91, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 55, 52, 57)                    # Wolnir bracelet pedestal
    fill_tiles(chunk, TILE_WALL, 110, 50, 112, 52)                  # Rope bridge anchor
    fill_tiles(chunk, TILE_WALL, 70, 95, 72, 97)                    # Skeleton pile
    for tx in range(115, 140, 6):
        fill_tiles(chunk, TILE_WALL, tx, 60, tx+1, 61)             # Catacomb wall sconces
    # --- SESSION 44 terrain (Catacombs of Carthus) ---
    # DS3: Chariot wheel tracks carved into floor
    for tx in range(20, 40):
        chunk[30][tx] = TILE_WALLTOP  # rut track
        chunk[31][tx] = TILE_WALLTOP
    # Burial pillar fragments
    for tx, ty in [(50, 25), (60, 30), (70, 28)]:
        chunk[ty][tx] = TILE_WALL  # broken pillar
    # Skeleton bone piles (DS3: everywhere in the catacombs)
    for tx in range(35, 45):
        chunk[40][tx] = TILE_WALLTOP  # bone scatter
    # Wolnir's bracelet alcoves (DS3: in the boss arena walls)
    for ty in range(55, 60):
        chunk[ty][80] = TILE_WALL  # bracelet niche
    # Burial urn clusters
    for tx, ty in [(25, 50), (40, 55), (55, 52)]:
        chunk[ty][tx] = TILE_WALLTOP  # urn debris

    # --- SESSION 48 terrain (Catacombs of Carthus) ---
    # DS3: Bone pile accumulations in the side chambers
    for tx in range(55, 65):
        chunk[42][tx] = TILE_WALLTOP  # bone scatter
    # Skull lantern alcoves in the walls (DS3: skull-lit passages)
    for ty in range(35, 40):
        chunk[ty][42] = TILE_WALL  # skull niche
        chunk[ty][58] = TILE_WALL  # skull niche
    # Broken bridge section (DS3: the collapsing floor over the abyss)
    for tx in range(70, 78):
        chunk[48][tx] = TILE_WALLTOP  # broken planks
    # Carthus urn clusters (DS3: breakable pots with items)
    for tx, ty in [(22, 38), (35, 42), (48, 45)]:
        chunk[ty][tx] = TILE_WALLTOP  # urn debris
    # Wolnir's bracelet alcove (DS3: massive bracelets in the boss arena wall)
    for ty in range(60, 65):
        chunk[ty][88] = TILE_WALL  # bracelet mount

    # --- SESSION 54 terrain (Catacombs of Carthus final) ---
    # DS3: Wolnir's sword embedded in the arena wall
    for ty in range(62, 68):
        chunk[ty][92] = TILE_WALL  # sword embedding
    # Skeleton wheel track grooves (DS3: the rolling skeleton ball track)
    for tx in range(30, 45):
        chunk[55][tx] = TILE_WALLTOP  # track groove
    # Burial chamber alcove walls
    for ty in range(40, 48):
        chunk[ty][72] = TILE_WALL  # alcove wall
    # Torch sconce positions (DS3: torches light the catacombs)
    for tx, ty in [(20, 30), (50, 35), (80, 40)]:
        chunk[ty][tx] = TILE_WALLTOP  # sconce debris

    # --- SESSION 58 terrain (Catacombs of Carthus) ---
    # DS3: Abyss Watcher bridge arches (DS3: the bridge to Farron Keep)
    for ty in range(70, 76):
        chunk[ty][85] = TILE_WALL  # bridge arch
    # Carthus war banner alcoves
    for tx, ty in [(25, 52), (40, 58)]:
        chunk[ty][tx] = TILE_WALL  # banner alcove
    # Skeleton pile pyramids (DS3: massive bone piles)
    for tx in range(55, 62):
        chunk[48][tx] = TILE_WALLTOP  # bone pyramid
    # Wolnir's sword mount point
    chunk[65][90] = TILE_WALL  # sword mount

    # --- SESSION 87 DS3 terrain (Catacombs of Carthus detail pass) ---
    # DS3: Bone piles throughout the catacombs
    for tx in [15, 22, 30, 38, 45, 52, 60, 68, 75, 82, 90, 98, 105]:
        for ty in [20, 25, 30]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Skull alcoves in the walls
    for tx in [18, 28, 38, 48, 58, 68, 78, 88, 98, 108]:
        for ty in [12, 13]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Broken bridge (the iconic collapsing bridge)
    for tx in range(30, 50):
        chunk[tx][40] = TILE_WALL
        chunk[tx][39] = TILE_WALLTOP
    # DS3: Bridge gap (missing section)
    for tx in range(40, 45):
        chunk[tx][40] = TILE_GROUND
        chunk[tx][39] = TILE_GROUND
    # DS3: Chariot ruts in the corridor floor
    for tx in range(55, 85):
        for ty in [48, 49]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Urn clusters (breakable pots with loot)
    for tx in [60, 62, 64, 70, 72, 74, 80, 82]:
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Wolnir's arena (large chamber)
    for tx in range(90, 115):
        for ty in range(35, 55):
            chunk[tx][ty] = TILE_GROUND
    for tx in [90, 115]:
        for ty in range(35, 56):
            chunk[tx][ty] = TILE_WALL
    for tx in range(90, 116):
        for ty in [35, 55]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Smouldering Lake drop shaft
    for tx in range(100, 106):
        for ty in range(60, 68):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Black Knight alcove
    for tx in range(110, 116):
        for ty in [22, 28]:
            chunk[tx][ty] = TILE_WALL
    for tx in [110, 116]:
        for ty in range(22, 29):
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 91 DS3 terrain round 2 (Catacombs of Carthus) ---
    # DS3: Chariot corridor (long straight with ruts)
    for tx in range(20, 60):
        for ty in [42, 43]:
            chunk[tx][ty] = TILE_GROUND
    for tx in range(20, 60):
        chunk[tx][41] = TILE_WALL
        chunk[tx][44] = TILE_WALL
    # DS3: Skeleton ball alcove (hidden side passage)
    for tx in range(45, 52):
        for ty in [35, 40]:
            chunk[tx][ty] = TILE_WALL
    for tx in [45, 52]:
        for ty in range(35, 41):
            chunk[tx][ty] = TILE_WALL
    for tx in range(45, 53):
        chunk[tx][34] = TILE_WALLTOP
    # DS3: Black Knight ambush room
    for tx in range(100, 112):
        for ty in [18, 25]:
            chunk[tx][ty] = TILE_WALL
    for tx in [100, 112]:
        for ty in range(18, 26):
            chunk[tx][ty] = TILE_WALL
    # DS3: Havel Knight drop area
    for tx in range(80, 88):
        for ty in [50, 56]:
            chunk[tx][ty] = TILE_WALL
    for tx in [80, 88]:
        for ty in range(50, 57):
            chunk[tx][ty] = TILE_WALL
    # DS3: Carthus Worm arena
    for tx in range(60, 75):
        for ty in range(65, 78):
            chunk[tx][ty] = TILE_GROUND
    for tx in [60, 75]:
        for ty in range(65, 79):
            chunk[tx][ty] = TILE_WALL
    
    # --- DS3 faithful enemies (CatacombsOfCarthus) ---
    # DS3 wiki enemies: Skeleton, Skeleton Swordsman, Skeleton Wheel, Writhing Rotten Flesh,
    # Lesser Crab, Hound-Rat, Black Knight, Crystal Lizard, Carthus Sandworm
    # Skeleton (18) — basic skeleton warriors throughout catacombs
    for tx, ty in [(18, 18), (22, 20), (25, 28), (35, 30), (42, 26), (52, 34), (20, 48), (35, 56), (45, 65), (32, 58), (63, 70), (25, 82), (28, 95), (35, 98), (110, 85), (120, 95), (130, 92), (115, 90)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Skeleton", "Skeleton"))]))
    # SkeletonSwordman (10) — DS3: agile dual-wielding skeletons in corridors
    for tx, ty in [(16, 22), (36, 22), (50, 21), (64, 32), (24, 55), (32, 50), (18, 85), (22, 92), (22, 96), (95, 66)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SkeletonSwordman", "SkeletonSwordman"))]))
    # SkeletonBall (4) — DS3: rolling skeleton ball traps in narrow corridors
    for tx, ty in [(30, 24), (55, 38), (40, 52), (50, 56)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SkeletonBall", "SkeletonBall"))]))
    # WrithingRottenFlesh (4) — DS3: fleshy creatures in lower tomb chambers
    for tx, ty in [(48, 32), (40, 60), (30, 88), (90, 70)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("WrithingRottenFlesh", "WrithingRottenFlesh"))]))
    # HoundRat (4) — DS3: rats scurrying in dark catacomb passages
    for tx, ty in [(28, 52), (38, 62), (20, 78), (135, 98)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HoundRat", "HoundRat"))]))
    # LesserCrab (2) — DS3: small crabs near flooded sections toward Smouldering Lake
    for tx, ty in [(60, 30), (58, 66)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LesserCrab", "LesserCrab"))]))
    # Archer (2) — DS3: skeleton archers on elevated positions
    entities.append(make_entity("Enemy", 20 * 16, 21 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Archer", "Archer"))]))
    entities.append(make_entity("Enemy", 125 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Archer", "Archer"))]))
    # CarthusSandworm / MiniBoss (3) — DS3: Wolnir (boss), carthus worm mini-boss encounters
    entities.append(make_entity("Enemy", 55 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CarthusSandworm", "CarthusSandworm"))]))
    entities.append(make_entity("Enemy", 60 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    entities.append(make_entity("Enemy", 65 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    # CrystalLizard (1)
    entities.append(make_entity("Enemy", 48 * 16, 50 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # BlackKnight (1) — DS3: Black Knight guarding path to Wolnir
    entities.append(make_entity("Enemy", 80 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 31 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 43 * 16, 37 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 75 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Carthus Pyromancy Tome")]))
    entities.append(make_entity("Item", 112 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Carthus Bloodring")]))
    entities.append(make_entity("Item", 131 * 16, 93 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Carthus Curved Sword")]))
    entities.append(make_entity("Item", 156 * 16, 125 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Carthus Milkring")]))
    entities.append(make_entity("Item", 168 * 16, 131 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 193 * 16, 159 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 212 * 16, 184 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 222 * 16, 188 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of High Lord Wolnir")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/CatacombsOfCarthus.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("CatacombsOfCarthus", chunk, entities, spawn_px, spawn_py)
