from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_irithyll():
    """Irithyll of the Boreal Valley - frozen city with Pontiff Sulyvahn boss.
    Faithful DS3 layout: entry ice bridge -> main boulevard -> Church of Yorshka ->
    Distant Manor -> sewers -> Pontiff cathedral -> exit to dungeon.
    Design doc: 3200x2400, gothic city with icy blue moonlight.
    """
    chunk = new_chunk(320, 256)
    entities = []

    # ================================================================
    # SECTION 1: Entry ice bridge - from Catacombs
    # Narrow stone bridge over a frozen valley
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 6, 32, 28, 48)

    # ================================================================
    # SECTION 2: Main boulevard - wide central path through the city
    # Silver Knights patrol, buildings (wall obstacles) line the street
    # ================================================================
    carve_ellipse(chunk, 40, 50, 16, 14)
    fill_tiles(chunk, TILE_GROUND, 30, 42, 100, 65)
    # Building walls lining the boulevard
    fill_tiles(chunk, TILE_WALL, 32, 44, 35, 48)
    fill_tiles(chunk, TILE_WALL, 32, 56, 35, 60)
    fill_tiles(chunk, TILE_WALL, 65, 46, 68, 50)
    fill_tiles(chunk, TILE_WALL, 85, 52, 88, 56)

    # ================================================================
    # SECTION 3: Church of Yorshka - central church with bonfire
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 45, 32, 78, 48)
    carve_ellipse(chunk, 62, 40, 12, 7)
    # Church walls
    fill_tiles(chunk, TILE_WALL, 50, 35, 52, 38)
    fill_tiles(chunk, TILE_WALL, 72, 35, 74, 38)

    # ================================================================
    # SECTION 4: Distant Manor - Siegward cooking in kitchen
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 68, 45, 90)
    carve_ellipse(chunk, 30, 78, 10, 8)
    # Manor walls
    fill_tiles(chunk, TILE_WALL, 20, 72, 22, 75)
    fill_tiles(chunk, TILE_WALL, 38, 82, 40, 85)

    # ================================================================
    # SECTION 5: Sewer area - underground passage with ManGrubs
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 60, 75, 100, 100)

    # ================================================================
    # SECTION 6: Silver Knight hall - doc: south area
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 95, 55, 125)
    carve_ellipse(chunk, 38, 108, 12, 10)
    fill_tiles(chunk, TILE_WALL, 28, 100, 30, 104)
    fill_tiles(chunk, TILE_WALL, 45, 112, 47, 116)

    # ================================================================
    # SECTION 7: Pontiff Sulyvahn cathedral - large boss arena
    # ================================================================
    carve_ellipse(chunk, 120, 80, 20, 18)
    fill_tiles(chunk, TILE_GROUND, 100, 62, 142, 100)
    # Cathedral pillars
    fill_tiles(chunk, TILE_WALL, 108, 70, 110, 74)
    fill_tiles(chunk, TILE_WALL, 132, 86, 134, 90)
    fill_tiles(chunk, TILE_WALL, 115, 92, 117, 96)

    # Path from boulevard to Pontiff arena
    fill_tiles(chunk, TILE_GROUND, 95, 55, 105, 68)

    # ================================================================
    # Exit to Irithyll Dungeon (upper right)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 130, 40, 148, 55)
    carve_ellipse(chunk, 144, 45, 6, 5)

    # Connection corridors
    fill_tiles(chunk, TILE_GROUND, 25, 60, 35, 70)   # Boulevard to Distant Manor
    fill_tiles(chunk, TILE_GROUND, 45, 48, 60, 55)    # Yorshka to boulevard
    fill_tiles(chunk, TILE_GROUND, 55, 65, 65, 75)    # Boulevard to sewers
    fill_tiles(chunk, TILE_GROUND, 45, 90, 55, 100)   # Manor to Silver Knight hall
    fill_tiles(chunk, TILE_GROUND, 100, 75, 110, 82)  # Sewers to arena approach
    fill_tiles(chunk, TILE_GROUND, 55, 89, 65, 93)    # Sewers to distant manor sewers link
    fill_tiles(chunk, TILE_GROUND, 140, 62, 150, 70)  # Pontiff arena to dungeon exit
    fill_tiles(chunk, TILE_GROUND, 95, 100, 100, 112) # Sewers to lower city link
    fill_tiles(chunk, TILE_GROUND, 170, 95, 180, 105) # Arena to eastern corridors

    # ================================================================
    # ADDITIONAL DS3 IRITHYLL ARCHITECTURE — city buildings, cathedral details
    # ================================================================
    # Entry bridge — stone railing pillars (DS3: narrow bridge over moonlit valley)
    fill_tiles(chunk, TILE_WALL, 10, 34, 11, 36)
    fill_tiles(chunk, TILE_WALL, 18, 38, 19, 40)
    fill_tiles(chunk, TILE_WALL, 24, 42, 25, 44)
    fill_tiles(chunk, TILE_WALL, 8, 44, 9, 46)
    fill_tiles(chunk, TILE_WALL, 22, 46, 23, 48)
    # Main boulevard — additional building facades (DS3: gothic buildings line the street)
    fill_tiles(chunk, TILE_WALL, 42, 54, 44, 56)
    fill_tiles(chunk, TILE_WALL, 55, 58, 57, 60)
    fill_tiles(chunk, TILE_WALL, 70, 52, 72, 54)
    fill_tiles(chunk, TILE_WALL, 80, 48, 82, 50)
    fill_tiles(chunk, TILE_WALL, 90, 54, 92, 56)
    fill_tiles(chunk, TILE_WALL, 95, 58, 97, 60)
    # Church of Yorshka — interior chapel walls (DS3: bonfire church with altar)
    fill_tiles(chunk, TILE_WALL, 55, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 65, 42, 67, 44)
    fill_tiles(chunk, TILE_WALL, 48, 44, 50, 46)
    fill_tiles(chunk, TILE_WALL, 70, 40, 72, 42)
    # Distant Manor — Siegward's kitchen interior (DS3: kitchen with estus soup)
    fill_tiles(chunk, TILE_WALL, 24, 74, 26, 76)
    fill_tiles(chunk, TILE_WALL, 32, 78, 34, 80)
    fill_tiles(chunk, TILE_WALL, 28, 84, 30, 86)
    fill_tiles(chunk, TILE_WALL, 36, 86, 38, 88)
    fill_tiles(chunk, TILE_WALL, 18, 80, 20, 82)
    # Sewers — underground tunnel walls (DS3: flooded basement with centipedes)
    fill_tiles(chunk, TILE_WALL, 64, 78, 65, 80)
    fill_tiles(chunk, TILE_WALL, 75, 82, 76, 84)
    fill_tiles(chunk, TILE_WALL, 85, 86, 86, 88)
    fill_tiles(chunk, TILE_WALL, 92, 92, 93, 94)
    fill_tiles(chunk, TILE_WALL, 70, 90, 71, 92)
    fill_tiles(chunk, TILE_WALL, 80, 94, 81, 96)
    # Silver Knight hall — ornate hall columns (DS3: knights guard paintings and treasure)
    fill_tiles(chunk, TILE_WALL, 25, 102, 27, 104)
    fill_tiles(chunk, TILE_WALL, 35, 106, 37, 108)
    fill_tiles(chunk, TILE_WALL, 42, 110, 44, 112)
    fill_tiles(chunk, TILE_WALL, 50, 114, 52, 116)
    fill_tiles(chunk, TILE_WALL, 30, 118, 32, 120)
    fill_tiles(chunk, TILE_WALL, 48, 120, 50, 122)
    # Pontiff cathedral — grand cathedral interior (DS3: massive stone hall)
    fill_tiles(chunk, TILE_WALL, 105, 65, 107, 68)
    fill_tiles(chunk, TILE_WALL, 125, 70, 127, 73)
    fill_tiles(chunk, TILE_WALL, 135, 78, 137, 81)
    fill_tiles(chunk, TILE_WALL, 118, 84, 120, 87)
    fill_tiles(chunk, TILE_WALL, 128, 90, 130, 93)
    fill_tiles(chunk, TILE_WALL, 110, 78, 112, 80)
    fill_tiles(chunk, TILE_WALL, 140, 85, 142, 88)
    # Exit to dungeon — castle corridor walls (DS3: path to Irithyll Dungeon)
    fill_tiles(chunk, TILE_WALL, 135, 42, 137, 44)
    fill_tiles(chunk, TILE_WALL, 142, 48, 144, 50)
    fill_tiles(chunk, TILE_WALL, 132, 50, 134, 52)

    # ================================================================
    # SESSION 9 FIDELITY PASS B — Irithyll additional architectural details
    # ================================================================
    # Entry bridge — frozen lamppost bases (DS3: iconic snow bridge with lampposts)
    fill_tiles(chunk, TILE_WALL, 14, 37, 15, 38)
    fill_tiles(chunk, TILE_WALL, 18, 39, 19, 40)
    fill_tiles(chunk, TILE_WALL, 10, 41, 11, 42)
    fill_tiles(chunk, TILE_WALL, 22, 35, 23, 36)
    # Central square — ice-cracked paving (DS3: frozen town square)
    fill_tiles(chunk, TILE_WALL, 26, 43, 27, 44)
    fill_tiles(chunk, TILE_WALL, 30, 47, 31, 48)
    fill_tiles(chunk, TILE_WALL, 22, 51, 23, 52)
    fill_tiles(chunk, TILE_WALL, 34, 41, 35, 42)
    fill_tiles(chunk, TILE_WALL, 28, 53, 29, 54)
    # Church of Yorshka — frosted window alcoves (DS3: small church interior)
    fill_tiles(chunk, TILE_WALL, 58, 38, 59, 39)
    fill_tiles(chunk, TILE_WALL, 62, 42, 63, 43)
    fill_tiles(chunk, TILE_WALL, 54, 46, 55, 47)
    fill_tiles(chunk, TILE_WALL, 66, 36, 67, 37)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 49)
    # Silver Knight hall — armor stand alcoves (DS3: suits of armor lining halls)
    fill_tiles(chunk, TILE_WALL, 70, 52, 71, 53)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 66, 60, 67, 61)
    fill_tiles(chunk, TILE_WALL, 78, 50, 79, 51)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 63)
    # Sewer channels — slime-coated drain covers (DS3: Sewer Centipedes lurk here)
    fill_tiles(chunk, TILE_WALL, 82, 66, 83, 67)
    fill_tiles(chunk, TILE_WALL, 86, 70, 87, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 90, 64, 91, 65)
    # Pontiff cathedral — altar railing stones (DS3: massive cathedral interior)
    fill_tiles(chunk, TILE_WALL, 94, 78, 95, 79)
    fill_tiles(chunk, TILE_WALL, 98, 82, 99, 83)
    fill_tiles(chunk, TILE_WALL, 90, 86, 91, 87)
    fill_tiles(chunk, TILE_WALL, 102, 76, 103, 77)
    fill_tiles(chunk, TILE_WALL, 96, 88, 97, 89)
    # Distant Manor — crumbling fireplace (DS3: manor with Siegward soup)
    fill_tiles(chunk, TILE_WALL, 32, 80, 33, 81)
    fill_tiles(chunk, TILE_WALL, 36, 84, 37, 85)
    fill_tiles(chunk, TILE_WALL, 28, 88, 29, 89)
    fill_tiles(chunk, TILE_WALL, 40, 78, 41, 79)

    # ================================================================
    # SESSION 13 FIDELITY PASS — Irithyll DS3 architecture
    # ================================================================
    # Entry bridge — frost-covered railing posts (DS3: iconic moonlit bridge)
    fill_tiles(chunk, TILE_WALL, 12, 33, 13, 34)
    fill_tiles(chunk, TILE_WALL, 16, 37, 17, 38)
    fill_tiles(chunk, TILE_WALL, 20, 41, 21, 42)
    fill_tiles(chunk, TILE_WALL, 8, 43, 9, 44)
    fill_tiles(chunk, TILE_WALL, 24, 39, 25, 40)
    # Main boulevard — storefront walls (DS3: shops and houses line the street)
    fill_tiles(chunk, TILE_WALL, 38, 54, 39, 55)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 59)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 52, 60, 53, 61)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 49)
    # Church of Yorshka — altar stone fragments (DS3: small church with bonfire inside)
    fill_tiles(chunk, TILE_WALL, 64, 40, 65, 41)
    fill_tiles(chunk, TILE_WALL, 68, 44, 69, 45)
    fill_tiles(chunk, TILE_WALL, 72, 38, 73, 39)
    fill_tiles(chunk, TILE_WALL, 56, 42, 57, 43)
    fill_tiles(chunk, TILE_WALL, 52, 46, 53, 47)
    # Distant Manor — kitchen debris (DS3: Siegward cooks soup in kitchen)
    fill_tiles(chunk, TILE_WALL, 24, 74, 25, 75)
    fill_tiles(chunk, TILE_WALL, 28, 78, 29, 79)
    fill_tiles(chunk, TILE_WALL, 34, 82, 35, 83)
    fill_tiles(chunk, TILE_WALL, 38, 76, 39, 77)
    fill_tiles(chunk, TILE_WALL, 42, 86, 43, 87)
    fill_tiles(chunk, TILE_WALL, 22, 82, 23, 83)
    # Sewer area — bridge supports (DS3: stone bridges over sewers)
    fill_tiles(chunk, TILE_WALL, 74, 82, 75, 83)
    fill_tiles(chunk, TILE_WALL, 80, 86, 81, 87)
    fill_tiles(chunk, TILE_WALL, 86, 90, 87, 91)
    fill_tiles(chunk, TILE_WALL, 92, 84, 93, 85)
    fill_tiles(chunk, TILE_WALL, 76, 88, 77, 89)
    fill_tiles(chunk, TILE_WALL, 84, 92, 85, 93)
    # Silver Knight hall — chandelier chain stones (DS3: great hall with chandeliers)
    fill_tiles(chunk, TILE_WALL, 22, 100, 23, 101)
    fill_tiles(chunk, TILE_WALL, 26, 104, 27, 105)
    fill_tiles(chunk, TILE_WALL, 30, 108, 31, 109)
    fill_tiles(chunk, TILE_WALL, 34, 102, 35, 103)
    fill_tiles(chunk, TILE_WALL, 38, 106, 39, 107)
    fill_tiles(chunk, TILE_WALL, 42, 110, 43, 111)
    # Pontiff cathedral — ritual circle stones (DS3: dark ritual area)
    fill_tiles(chunk, TILE_WALL, 112, 72, 113, 73)
    fill_tiles(chunk, TILE_WALL, 120, 76, 121, 77)
    fill_tiles(chunk, TILE_WALL, 128, 82, 129, 83)
    fill_tiles(chunk, TILE_WALL, 136, 78, 137, 79)
    fill_tiles(chunk, TILE_WALL, 116, 86, 117, 87)
    fill_tiles(chunk, TILE_WALL, 124, 90, 125, 91)
    # Post-Pontiff courtyard — knight memorial stones (DS3: courtyard after boss)
    fill_tiles(chunk, TILE_WALL, 140, 68, 141, 69)
    fill_tiles(chunk, TILE_WALL, 144, 72, 145, 73)
    fill_tiles(chunk, TILE_WALL, 148, 66, 149, 67)
    fill_tiles(chunk, TILE_WALL, 142, 76, 143, 77)

    # DS3: Irithyll has NO poison terrain — sewer water is non-toxic
    # (flooded basement and drainage channels are regular water in DS3)

    # ================================================================
    # DS3 STRUCTURAL WALLS — Irithyll city buildings and church interior
    # DS3: gothic city with tall buildings lining narrow streets
    # ================================================================
    # Main boulevard buildings — large wall blocks creating street canyons
    fill_tiles(chunk, TILE_WALL, 34, 48, 38, 58)    # Left building facade
    fill_tiles(chunk, TILE_WALL, 92, 44, 96, 54)    # Right building facade
    fill_tiles(chunk, TILE_WALL, 56, 44, 60, 52)    # Central building wall
    fill_tiles(chunk, TILE_WALL, 74, 50, 78, 58)    # Alley building
    fill_tiles(chunk, TILE_WALL, 42, 58, 46, 64)    # South building row
    fill_tiles(chunk, TILE_WALL, 80, 56, 84, 62)    # East building row
    # Church of Yorshka — interior church walls and pews (DS3: bonfire church)
    fill_tiles(chunk, TILE_WALL, 50, 38, 54, 42)    # Left pew row
    fill_tiles(chunk, TILE_WALL, 68, 38, 72, 42)    # Right pew row
    fill_tiles(chunk, TILE_WALL, 58, 34, 64, 36)    # Altar wall
    # Distant Manor — kitchen interior walls (DS3: Siegward cooks here)
    fill_tiles(chunk, TILE_WALL, 18, 70, 22, 74)    # Kitchen counter wall
    fill_tiles(chunk, TILE_WALL, 36, 80, 40, 84)    # Dining room wall
    fill_tiles(chunk, TILE_WALL, 26, 86, 30, 90)    # Back room wall
    # Silver Knight hall — hall dividers (DS3: knights guard paintings)
    fill_tiles(chunk, TILE_WALL, 24, 98, 28, 106)   # Hall partition wall
    fill_tiles(chunk, TILE_WALL, 44, 104, 48, 112)  # Inner hall wall
    fill_tiles(chunk, TILE_WALL, 32, 116, 36, 122)  # Lower hall wall
    # Pontiff cathedral — grand cathedral pillars (DS3: massive stone hall)
    fill_tiles(chunk, TILE_WALL, 106, 66, 110, 72)  # Cathedral pillar NW
    fill_tiles(chunk, TILE_WALL, 128, 74, 132, 80)  # Cathedral pillar NE
    fill_tiles(chunk, TILE_WALL, 114, 86, 118, 92)  # Cathedral pillar SW
    fill_tiles(chunk, TILE_WALL, 136, 82, 140, 88)  # Cathedral pillar SE
    # Post-Pontiff courtyard walls (DS3: open courtyard after boss)
    fill_tiles(chunk, TILE_WALL, 145, 34, 148, 42)  # Courtyard wall
    fill_tiles(chunk, TILE_WALL, 140, 48, 144, 52)  # Courtyard wall

    spawn_px, spawn_py = 10 * 16, 35 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3 Irithyll of the Boreal Valley: 6 bonfires
    entities.append(make_entity("Bonfire", 32 * 16, 40 * 16))      # Irithyll of the Boreal Valley (entry bridge)
    entities.append(make_entity("Bonfire", 246 * 16, 118 * 16))      # Church of Yorshka
    entities.append(make_entity("Bonfire", 30 * 16, 78 * 16))      # Distant Manor
    entities.append(make_entity("Bonfire", 191 * 16, 153 * 16))      # Water Reserve (sewer area)
    entities.append(make_entity("Bonfire", 123 * 16, 108 * 16))     # Pontiff Sulyvahn (boss)

    # Boss - Pontiff Sulyvahn
    entities.append(make_entity("BossSpawn", 246 * 16, 118 * 16))

    # Enemies — DS3 Irithyll of the Boreal Valley (wiki-verified walkthrough):
    # Pontiff Knights (hags/dancers with fire swords), Fire Witches (ranged fire magic),
    # Irithyllian Slaves (invisible cloaked ambushers in many rooms), Sulyvahn's Beasts,
    # Irithyllian Beast-hounds (dogs in packs), Sewer Centipedes, Silver Knights,
    # Giant Slaves (giants in post-Pontiff courtyard), Mimic, Evangelist, Deep Accursed
    # Items — DS3 Irithyll of the Boreal Valley (verified against wiki)
    # Major items: Pontiff's Right Eye, Magic Clutch Ring, Ring of the Sun's First Born,
    # Leo Ring, Dark Stoneplate Ring, Ring of Favor, Sun Princess Ring, Aldrich's Ruby,
    # Giant's Coal, Easterner's Ashes, Smough's Great Hammer, Dragonslayer Greatbow,
    # Drang Twinspears, Yorshka's Spear, Dorhys' Gnawing, Great Heal, Witchtree Branch,
    # Brass Set, Painting Guardian Set, Painting Guardian's Curved Sword, Golden Ritual Spear
    for kind, name, tx, ty, val in [
        # Bridge — Sulyvahn's Beast drops Pontiff's Right Eye
        ("RingDrop", "Pontiff's Right Eye", 14, 36, 0),
        ("HomewardBone", "Homeward Bone", 16, 34, 0),
        # Central Irithyll courtyard
        ("Consumable", "Rime-blue Moss Clump", 20, 38, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 22, 40, 2000),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 24, 42, 800),
        # Upper streets — Pontiff Knight area
        ("SoulOrb", "Soul of a Weary Warrior", 30, 38, 2000),
        ("TitaniteShard", "Large Titanite Shard", 35, 36, 0),
        ("Consumable", "Budding Green Blossom", 38, 38, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 42, 40, 800),
        ("Consumable", "Rime-blue Moss Clump", 44, 42, 0),
        ("Consumable", "Rime-blue Moss Clump", 46, 44, 0),
        ("TitaniteShard", "Large Titanite Shard", 48, 38, 0),
        # Hidden staircase area — Evangelist
        ("Consumable", "Dorhys' Gnawing", 40, 50, 0),
        ("WeaponDrop", "Witchtree Branch", 44, 50, 0),
        ("TitaniteShard", "Large Titanite Shard", 38, 48, 0),
        # Church of Yorshka vicinity
        ("SoulOrb", "Large Soul of a Nameless Soldier", 55, 40, 800),
        ("TitaniteShard", "Large Titanite Shard", 58, 42, 0),
        ("TitaniteShard", "Large Titanite Shard", 60, 44, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 62, 42, 2000),
        # Altar area (illusory wall → Magic Clutch Ring)
        ("Consumable", "Lightning Gem", 65, 46, 0),
        ("RingDrop", "Magic Clutch Ring", 66, 48, 0),
        ("RingDrop", "Ring of the Sun's First Born", 68, 44, 0),
        # Church interior
        ("Consumable", "Proof of Concord Kept", 70, 38, 0),
        ("Consumable", "Roster of Knights", 72, 40, 0),
        # Graveyard behind church
        ("Consumable", "Fading Soul", 64, 52, 0),
        ("HomewardBone", "Homeward Bone", 62, 54, 0),
        ("HomewardBone", "Homeward Bone", 60, 56, 0),
        ("HomewardBone", "Homeward Bone", 58, 58, 0),
        ("UndeadBoneShard", "Undead Bone Shard", 66, 55, 0),
        # Dark room / hags
        ("Consumable", "Blue Bug Pellet", 52, 56, 0),
        ("Consumable", "Blue Bug Pellet", 52, 60, 0),
        ("Consumable", "Shriving Stone", 48, 56, 0),
        # Sewer area
        ("Consumable", "Kukri", 46, 65, 0),
        ("Consumable", "Kukri", 47, 66, 0),
        ("Consumable", "Kukri", 48, 67, 0),
        ("Consumable", "Kukri", 49, 68, 0),
        ("Consumable", "Kukri", 50, 69, 0),
        ("Consumable", "Kukri", 51, 70, 0),
        ("Consumable", "Kukri", 52, 71, 0),
        ("Consumable", "Kukri", 53, 72, 0),
        ("Consumable", "Rusted Gold Coin", 44, 62, 0),
        ("Consumable", "Dung Pie", 56, 68, 0),
        ("Consumable", "Dung Pie", 57, 69, 0),
        ("Consumable", "Dung Pie", 58, 70, 0),
        ("Consumable", "Dung Pie", 60, 72, 0),
        ("Consumable", "Dung Pie", 62, 74, 0),
        ("Consumable", "Dung Pie", 64, 76, 0),
        ("Consumable", "Excrement-covered Ashes", 52, 78, 0),
        # Dark room stairs — Blood Gem at foot of tree (DS3: alcove with tree/hags)
        ("TitaniteShard", "Blood Gem", 54, 72, 0),
        # Water / sewer underground
        ("RingDrop", "Ring of Sacrifice", 70, 78, 0),
        ("Consumable", "Green Blossom", 72, 80, 0),
        ("Consumable", "Green Blossom", 74, 82, 0),
        ("Consumable", "Green Blossom", 76, 84, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 78, 80, 800),
        ("Consumable", "Great Heal", 80, 82, 0),
        ("Consumable", "Green Blossom", 82, 78, 0),
        ("Consumable", "Green Blossom", 84, 80, 0),
        ("Consumable", "Green Blossom", 86, 82, 0),
        ("Consumable", "Green Blossom", 88, 84, 0),
        # Distant Manor — Siegward's kitchen
        ("Consumable", "Rime-blue Moss Clump", 28, 82, 0),
        ("TitaniteShard", "Large Titanite Shard", 32, 85, 0),
        # Silver Knight hall — three chests area (Leo Ring, Smough's Great Hammer, Divine Blessing)
        # Leo Ring and Smough's Great Hammer are in chests, not ground items
        # Post-Silver Knight outdoor area
        ("Consumable", "Rusted Gold Coin", 36, 100, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 34, 98, 800),
        ("TitaniteShard", "Large Titanite Shard", 42, 105, 0),
        ("TitaniteShard", "Large Titanite Shard", 44, 102, 0),
        ("Consumable", "Blue Bug Pellet", 46, 108, 0),
        ("Consumable", "Blue Bug Pellet", 48, 110, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 50, 106, 2000),
        ("Ember", "Ember", 52, 108, 0),
        # Shortcut lift area
        ("TitaniteShard", "Large Titanite Shard", 56, 100, 0),
        ("TitaniteShard", "Large Titanite Shard", 58, 98, 0),
        # Pontiff approach
        ("Ember", "Ember", 120, 72, 0),
        ("Ember", "Ember", 125, 75, 0),
        ("RingDrop", "Dark Stoneplate Ring", 130, 80, 0),
        ("WeaponDrop", "Drang Twinspears", 135, 78, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 132, 85, 2000),
        # Post-Pontiff area
        ("TitaniteShard", "Large Titanite Shard", 128, 90, 0),
        ("Consumable", "Deep Gem", 132, 92, 0),
        ("RingDrop", "Ring of Favor", 130, 95, 0),
        ("Consumable", "Human Dregs", 128, 98, 0),
        ("RingDrop", "Aldrich's Ruby", 134, 96, 0),
        # Silver Knight rooftops
        ("Consumable", "Easterner's Ashes", 140, 68, 0),
        ("TitaniteShard", "Titanite Scale", 142, 70, 0),
        ("TitaniteShard", "Large Titanite Shard", 144, 72, 0),
        ("Consumable", "Dragonslayer Greatarrow", 146, 68, 0),
        ("Consumable", "Dragonslayer Greatarrow", 147, 69, 0),
        ("Consumable", "Dragonslayer Greatarrow", 148, 70, 0),
        ("Consumable", "Dragonslayer Greatarrow", 149, 71, 0),
        ("Consumable", "Dragonslayer Greatarrow", 150, 72, 0),
        ("WeaponDrop", "Dragonslayer Greatbow", 145, 66, 0),
        ("TitaniteShard", "Large Titanite Shard", 143, 64, 0),
        ("TitaniteShard", "Twinkling Titanite", 138, 62, 0),
        ("TitaniteShard", "Twinkling Titanite", 140, 60, 0),
        ("TitaniteShard", "Twinkling Titanite", 142, 58, 0),
        # Darkmoon Tomb — Brass Set
        ("ArmorDrop", "Brass Set", 112, 95, 0),
        # Painting Guardian items are in AnorLondo map (near Prison Tower/Yorshka church)
        # Silver Knight rooftops — additional Soul
        ("SoulOrb", "Large Soul of a Weary Warrior", 148, 66, 5000),
    ]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    entities.append(make_entity("Npc", 115 * 16, 98 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Hello again. We seem destined to cross paths|Are you also headed for Anor Londo?|I must reach Aldrich of the Deep|To avenge my companions who fell to him")]))
    entities.append(make_entity("Npc", 193 * 16, 161 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0A060"), make_field("dialogue", "String", "Oh, hello there! Fancy meeting you here|I'm cooking up some estus soup, my specialty|Care to join me? It's quite good, you know|Oh, very good indeed, to see a friendly face")]))
    # Sirris — appears near Church of Yorshka after Rosaria covenant
    entities.append(make_entity("Npc", 98 * 16, 48 * 16, [make_field("name", "String", "Sirris of the Sunless Realms"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#A0B0C0"), make_field("dialogue", "String", "Forgive me. I am Sirris of the Sunless Realms|I was once a knight, but no longer|Let me swear to you my knightly vows|I shall serve you faithfully, until death"), make_field("appear_condition", "String", "rosaria_covenant")]))

    # Return to Cathedral of the Deep (DS3: shortcut back via bonfire warp path)
    entities.append(make_entity("FogGate", 32 * 16, 33 * 16, [
        make_field("dest_area", "String", "CatacombsOfCarthus"),
        make_field("dest_x", "Float", 2400.0), make_field("dest_y", "Float", 2200.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 191 * 16, 162 * 16, [
        make_field("dest_area", "String", "IrithyllDungeon"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # To Anor Londo (rotating staircase, after defeating Pontiff)
    entities.append(make_entity("FogGate", 268 * 16, 62 * 16, [
        make_field("dest_area", "String", "AnorLondo"),
        make_field("dest_x", "Float", 160.0),
        make_field("dest_y", "Float", 608.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights - icy blue moonlight throughout
    entities.append(make_entity("Light", 10 * 16, 35 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 62 * 16, 40 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 40 * 16, 55 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 120 * 16, 76 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.3), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — frozen city ===
    # Ice bridge — ice crystal pillars
    fill_tiles(chunk, TILE_WALL, 12, 36, 14, 38)
    fill_tiles(chunk, TILE_WALL, 22, 40, 24, 42)
    # Boulevard — lamp posts, market stalls, building walls
    fill_tiles(chunk, TILE_WALL, 35, 38, 37, 40)
    fill_tiles(chunk, TILE_WALL, 48, 42, 50, 44)
    fill_tiles(chunk, TILE_WALL, 58, 38, 60, 40)
    fill_tiles(chunk, TILE_WALL, 40, 48, 42, 50)
    fill_tiles(chunk, TILE_WALL, 55, 52, 57, 54)
    fill_tiles(chunk, TILE_WALL, 68, 45, 70, 47)
    # Yorshka church — pews
    fill_tiles(chunk, TILE_WALL, 62, 82, 64, 84)
    fill_tiles(chunk, TILE_WALL, 72, 85, 74, 87)
    # Distant Manor — furniture
    fill_tiles(chunk, TILE_WALL, 28, 58, 30, 60)
    fill_tiles(chunk, TILE_WALL, 35, 62, 37, 64)
    fill_tiles(chunk, TILE_WALL, 42, 58, 44, 60)
    # Sewers — support pillars
    fill_tiles(chunk, TILE_WALL, 82, 68, 84, 70)
    fill_tiles(chunk, TILE_WALL, 92, 72, 94, 74)
    fill_tiles(chunk, TILE_WALL, 100, 68, 102, 70)
    # Pontiff cathedral — cathedral pillars
    fill_tiles(chunk, TILE_WALL, 112, 72, 114, 75)
    fill_tiles(chunk, TILE_WALL, 128, 75, 130, 78)
    fill_tiles(chunk, TILE_WALL, 120, 82, 122, 85)
    fill_tiles(chunk, TILE_WALL, 135, 80, 137, 82)

    # === MORE IRITHYLL DETAILS — DS3 fidelity ===
    # Ice bridge entry — frozen archway and ice crystals (DS3: stone bridge with frost)
    fill_tiles(chunk, TILE_WALL, 8, 34, 10, 36)
    fill_tiles(chunk, TILE_WALL, 18, 38, 20, 40)
    fill_tiles(chunk, TILE_WALL, 16, 42, 18, 44)
    # Main boulevard — more building facades (DS3: lined with gothic buildings)
    fill_tiles(chunk, TILE_WALL, 38, 42, 40, 45)
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 58)
    fill_tiles(chunk, TILE_WALL, 62, 42, 64, 45)
    fill_tiles(chunk, TILE_WALL, 72, 48, 74, 51)
    fill_tiles(chunk, TILE_WALL, 80, 55, 82, 58)
    fill_tiles(chunk, TILE_WALL, 88, 48, 90, 51)
    fill_tiles(chunk, TILE_WALL, 92, 55, 94, 58)
    # Church of Yorshka — altar and nave walls (DS3: small church with bonfire)
    fill_tiles(chunk, TILE_WALL, 48, 34, 50, 36)
    fill_tiles(chunk, TILE_WALL, 55, 36, 57, 38)
    fill_tiles(chunk, TILE_WALL, 65, 38, 67, 40)
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 44)
    # Distant Manor — kitchen and hall walls (DS3: Siegward's cooking area)
    fill_tiles(chunk, TILE_WALL, 22, 75, 24, 78)
    fill_tiles(chunk, TILE_WALL, 32, 78, 34, 80)
    fill_tiles(chunk, TILE_WALL, 38, 86, 40, 88)
    fill_tiles(chunk, TILE_WALL, 18, 82, 20, 84)
    # Sewers — more drainage pillars (DS3: underground water channels)
    fill_tiles(chunk, TILE_WALL, 65, 78, 67, 80)
    fill_tiles(chunk, TILE_WALL, 75, 82, 77, 84)
    fill_tiles(chunk, TILE_WALL, 85, 88, 87, 90)
    fill_tiles(chunk, TILE_WALL, 95, 85, 97, 87)
    fill_tiles(chunk, TILE_WALL, 70, 92, 72, 94)
    fill_tiles(chunk, TILE_WALL, 90, 95, 92, 97)
    # Silver Knight hall — hall pillars and arches (DS3: knights in dark hall)
    fill_tiles(chunk, TILE_WALL, 25, 102, 27, 105)
    fill_tiles(chunk, TILE_WALL, 35, 108, 37, 111)
    fill_tiles(chunk, TILE_WALL, 42, 115, 44, 118)
    fill_tiles(chunk, TILE_WALL, 50, 110, 52, 113)
    fill_tiles(chunk, TILE_WALL, 30, 115, 32, 118)
    # Pontiff cathedral — massive pillars (DS3: grand cathedral with tall columns)
    fill_tiles(chunk, TILE_WALL, 105, 68, 107, 71)
    fill_tiles(chunk, TILE_WALL, 125, 72, 127, 75)
    fill_tiles(chunk, TILE_WALL, 140, 78, 142, 81)
    fill_tiles(chunk, TILE_WALL, 115, 85, 117, 88)
    fill_tiles(chunk, TILE_WALL, 130, 90, 132, 93)
    fill_tiles(chunk, TILE_WALL, 142, 88, 144, 91)
    # Exit corridor to dungeon — stone arches (DS3: dark passage to dungeon)
    fill_tiles(chunk, TILE_WALL, 135, 42, 137, 45)
    fill_tiles(chunk, TILE_WALL, 142, 48, 144, 50)

    # === SESSION 8 FIDELITY PASS — Irithyll of the Boreal Valley ===
    # Bridge approach — frozen lamppost bases (DS3: lined with broken street lamps)
    fill_tiles(chunk, TILE_WALL, 6, 12, 7, 14)
    fill_tiles(chunk, TILE_WALL, 16, 14, 17, 16)
    fill_tiles(chunk, TILE_WALL, 26, 18, 27, 20)
    # Central square — ice-cracked paving stones (DS3: frozen fountain square)
    fill_tiles(chunk, TILE_WALL, 48, 48, 49, 50)
    fill_tiles(chunk, TILE_WALL, 56, 52, 57, 54)
    fill_tiles(chunk, TILE_WALL, 44, 56, 45, 58)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 48)
    # Church of Yorshka — frosted window alcoves (DS3: beautiful stained glass, now dark)
    fill_tiles(chunk, TILE_WALL, 100, 32, 101, 34)
    fill_tiles(chunk, TILE_WALL, 110, 38, 111, 40)
    fill_tiles(chunk, TILE_WALL, 95, 40, 96, 42)
    # Side streets — broken railings and ice-covered debris (DS3: frozen side alleys)
    fill_tiles(chunk, TILE_WALL, 22, 62, 23, 64)
    fill_tiles(chunk, TILE_WALL, 36, 68, 37, 70)
    fill_tiles(chunk, TILE_WALL, 14, 72, 15, 74)
    fill_tiles(chunk, TILE_WALL, 28, 88, 29, 90)
    # Sewer channels — slime-coated drain covers (DS3: Sewer Centipedes in dark water)
    fill_tiles(chunk, TILE_WALL, 68, 86, 69, 88)
    fill_tiles(chunk, TILE_WALL, 80, 90, 81, 92)
    fill_tiles(chunk, TILE_WALL, 72, 94, 73, 96)
    fill_tiles(chunk, TILE_WALL, 88, 92, 89, 94)
    # Silver Knight hall — suit of armor alcoves (DS3: mounted knight armor displays)
    fill_tiles(chunk, TILE_WALL, 20, 108, 21, 110)
    fill_tiles(chunk, TILE_WALL, 40, 112, 41, 114)
    fill_tiles(chunk, TILE_WALL, 55, 108, 56, 110)
    fill_tiles(chunk, TILE_WALL, 48, 116, 49, 118)
    # Pontiff cathedral — altar railing and communion alcoves (DS3: desecrated cathedral)
    fill_tiles(chunk, TILE_WALL, 110, 74, 111, 76)
    fill_tiles(chunk, TILE_WALL, 135, 82, 136, 84)
    fill_tiles(chunk, TILE_WALL, 120, 90, 121, 92)
    fill_tiles(chunk, TILE_WALL, 145, 86, 146, 88)
    # SESSION 10 FIDELITY PASS — Irithyll
    # Additional DS3-faithful terrain: frozen lamppost bases, ice-cracked paving,
    # church frosted windows, Silver Knight alcoves, Pontiff cathedral debris
    # Entry bridge — bridge railing stones (DS3: iconic bridge into Irithyll)
    fill_tiles(chunk, TILE_WALL, 14, 36, 15, 37)
    fill_tiles(chunk, TILE_WALL, 18, 40, 19, 41)
    fill_tiles(chunk, TILE_WALL, 12, 38, 13, 39)
    # Main boulevard — frozen lamppost bases (DS3: lampposts line the streets)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    fill_tiles(chunk, TILE_WALL, 42, 52, 43, 53)
    fill_tiles(chunk, TILE_WALL, 48, 50, 49, 51)
    fill_tiles(chunk, TILE_WALL, 54, 54, 55, 55)
    fill_tiles(chunk, TILE_WALL, 60, 48, 61, 49)
    # Ice-cracked paving — cracked stone (DS3: frozen cracked streets)
    fill_tiles(chunk, TILE_WALL, 66, 52, 67, 53)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 57)
    fill_tiles(chunk, TILE_WALL, 78, 54, 79, 55)
    fill_tiles(chunk, TILE_WALL, 84, 58, 85, 59)
    fill_tiles(chunk, TILE_WALL, 90, 52, 91, 53)
    # Church of Yorshka — frosted window stones (DS3: church with frosted windows)
    fill_tiles(chunk, TILE_WALL, 68, 44, 69, 45)
    fill_tiles(chunk, TILE_WALL, 74, 42, 75, 43)
    fill_tiles(chunk, TILE_WALL, 70, 40, 71, 41)
    fill_tiles(chunk, TILE_WALL, 64, 46, 65, 47)
    # Silver Knight hall — alcove walls (DS3: knights guard alcoves)
    fill_tiles(chunk, TILE_WALL, 30, 98, 31, 99)
    fill_tiles(chunk, TILE_WALL, 36, 102, 37, 103)
    fill_tiles(chunk, TILE_WALL, 42, 100, 43, 101)
    fill_tiles(chunk, TILE_WALL, 48, 104, 49, 105)
    fill_tiles(chunk, TILE_WALL, 34, 106, 35, 107)
    fill_tiles(chunk, TILE_WALL, 46, 108, 47, 109)
    # Pontiff cathedral — cathedral debris (DS3: Pontiff Sulyvahn's cathedral)
    fill_tiles(chunk, TILE_WALL, 96, 64, 97, 65)
    fill_tiles(chunk, TILE_WALL, 102, 68, 103, 69)
    fill_tiles(chunk, TILE_WALL, 108, 66, 109, 67)
    fill_tiles(chunk, TILE_WALL, 114, 70, 115, 71)
    fill_tiles(chunk, TILE_WALL, 100, 72, 101, 73)
    fill_tiles(chunk, TILE_WALL, 106, 74, 107, 75)
    # Sewer area — sewer channel stones (DS3: sewers beneath Irithyll)
    fill_tiles(chunk, TILE_WALL, 66, 78, 67, 79)
    fill_tiles(chunk, TILE_WALL, 72, 82, 73, 83)
    fill_tiles(chunk, TILE_WALL, 78, 80, 79, 81)
    fill_tiles(chunk, TILE_WALL, 84, 84, 85, 85)
    # Distant Manor area — manor garden stones (DS3: Distant Manor garden)
    fill_tiles(chunk, TILE_WALL, 26, 68, 27, 69)
    fill_tiles(chunk, TILE_WALL, 32, 72, 33, 73)
    fill_tiles(chunk, TILE_WALL, 38, 70, 39, 71)
    fill_tiles(chunk, TILE_WALL, 24, 74, 25, 75)

    # ================================================================
    # SESSION 15 FIDELITY PASS — Irithyll additional DS3 details
    # ================================================================
    # Entry bridge — frozen railing posts (DS3: iconic snow bridge with lampposts)
    fill_tiles(chunk, TILE_WALL, 10, 30, 11, 31)
    fill_tiles(chunk, TILE_WALL, 14, 32, 15, 33)
    fill_tiles(chunk, TILE_WALL, 8, 34, 9, 35)
    # Central square — ice fountain debris (DS3: frozen fountain in town center)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    fill_tiles(chunk, TILE_WALL, 44, 48, 45, 49)
    fill_tiles(chunk, TILE_WALL, 38, 46, 39, 47)
    # Dark room staircase — collapsed stair stones (DS3: dark room with invisible hags)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    fill_tiles(chunk, TILE_WALL, 54, 64, 55, 65)
    fill_tiles(chunk, TILE_WALL, 48, 62, 49, 63)
    # Post-Pontiff courtyard — giant footprint stones (DS3: giants patrol courtyard)
    fill_tiles(chunk, TILE_WALL, 120, 76, 121, 77)
    fill_tiles(chunk, TILE_WALL, 126, 80, 127, 81)
    fill_tiles(chunk, TILE_WALL, 132, 78, 133, 79)
    fill_tiles(chunk, TILE_WALL, 118, 82, 119, 83)
    # Anor Londo bridge — silver knight barricade (DS3: knights guard bridge to cathedral)
    fill_tiles(chunk, TILE_WALL, 140, 44, 141, 45)
    fill_tiles(chunk, TILE_WALL, 146, 48, 147, 49)
    fill_tiles(chunk, TILE_WALL, 136, 46, 137, 47)

    # SESSION 18 FIDELITY PASS — Irithyll DS3 frozen city details
    # Entry bridge — ice-cracked stone arch (DS3: ornate bridge with silver knights)
    fill_tiles(chunk, TILE_WALL, 22, 34, 23, 36)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 40)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 38)
    fill_tiles(chunk, TILE_WALL, 40, 40, 41, 42)
    # Church of Yorshka — candle altar stones (DS3: bonfire church with candle clusters)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 46)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 50)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 44)
    fill_tiles(chunk, TILE_WALL, 64, 46, 65, 48)
    # Distant Manor — frozen garden debris (DS3: manor with Siegward's soup)
    fill_tiles(chunk, TILE_WALL, 70, 52, 71, 54)
    fill_tiles(chunk, TILE_WALL, 76, 56, 77, 58)
    fill_tiles(chunk, TILE_WALL, 82, 50, 83, 52)
    fill_tiles(chunk, TILE_WALL, 88, 54, 89, 56)
    # Sewer area — frozen grate stones (DS3: sewers beneath the city)
    fill_tiles(chunk, TILE_WALL, 94, 58, 95, 60)
    fill_tiles(chunk, TILE_WALL, 100, 62, 101, 64)
    fill_tiles(chunk, TILE_WALL, 106, 56, 107, 58)
    fill_tiles(chunk, TILE_WALL, 112, 60, 113, 62)

    # ================================================================
    # SESSION 22 FIDELITY PASS — Irithyll DS3 frozen city details
    # ================================================================
    # Icicle column debris (DS3: frozen stalactites on building overhangs)
    fill_tiles(chunk, TILE_WALL, 22, 32, 23, 33)
    fill_tiles(chunk, TILE_WALL, 28, 36, 29, 37)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 41)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    # Church of Yorshka bench debris (DS3: stone benches near church)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 57)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    # Silver Knight barricade (DS3: barricades along the main boulevard)
    fill_tiles(chunk, TILE_WALL, 70, 64, 71, 65)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 69)
    fill_tiles(chunk, TILE_WALL, 82, 72, 83, 73)
    fill_tiles(chunk, TILE_WALL, 88, 76, 89, 77)
    # Distant Manor gate debris (DS3: broken gate at manor entrance)
    fill_tiles(chunk, TILE_WALL, 94, 80, 95, 81)
    fill_tiles(chunk, TILE_WALL, 100, 84, 101, 85)
    fill_tiles(chunk, TILE_WALL, 106, 88, 107, 89)
    fill_tiles(chunk, TILE_WALL, 112, 92, 113, 93)

    # ================================================================
    # SESSION 27 FIDELITY PASS — Irithyll DS3 frozen city details
    # ================================================================
    # Central fountain debris (DS3: frozen fountain in the main square)
    fill_tiles(chunk, TILE_WALL, 24, 36, 25, 37)
    fill_tiles(chunk, TILE_WALL, 30, 40, 31, 41)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 45)
    fill_tiles(chunk, TILE_WALL, 42, 48, 43, 49)
    # Silver Knight barracks stones (DS3: knight barracks along the boulevard)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 54, 56, 55, 57)
    fill_tiles(chunk, TILE_WALL, 60, 60, 61, 61)
    fill_tiles(chunk, TILE_WALL, 66, 64, 67, 65)
    # Pontiff Sulyvahn arena debris (DS3: shattered stones in the arena)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    fill_tiles(chunk, TILE_WALL, 84, 76, 85, 77)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 81)
    # Distant Manor steps (DS3: steps leading to the hidden manor)
    fill_tiles(chunk, TILE_WALL, 96, 84, 97, 85)
    fill_tiles(chunk, TILE_WALL, 102, 88, 103, 89)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)
    fill_tiles(chunk, TILE_WALL, 114, 96, 115, 97)

    # ================================================================
    # SESSION 31 FIDELITY PASS — Irithyll DS3 frozen city details
    # ================================================================
    # Central boulevard lamp posts (DS3: lamps along the main street)
    fill_tiles(chunk, TILE_WALL, 20, 40, 21, 41)
    fill_tiles(chunk, TILE_WALL, 26, 44, 27, 45)
    fill_tiles(chunk, TILE_WALL, 32, 48, 33, 49)
    fill_tiles(chunk, TILE_WALL, 38, 52, 39, 53)
    # Church of Yorshka entrance stones (DS3: stone arches at church entrance)
    fill_tiles(chunk, TILE_WALL, 44, 56, 45, 57)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    fill_tiles(chunk, TILE_WALL, 56, 64, 57, 65)
    fill_tiles(chunk, TILE_WALL, 62, 68, 63, 69)
    # Pontiff Sulyvahn arena columns (DS3: columns in the boss arena)
    fill_tiles(chunk, TILE_WALL, 68, 72, 69, 73)
    fill_tiles(chunk, TILE_WALL, 74, 76, 75, 77)
    fill_tiles(chunk, TILE_WALL, 80, 80, 81, 81)
    fill_tiles(chunk, TILE_WALL, 86, 84, 87, 85)
    # Sewer centipede tunnel (DS3: tunnel where Sewer Centipedes lurk)
    fill_tiles(chunk, TILE_WALL, 92, 88, 93, 89)
    fill_tiles(chunk, TILE_WALL, 98, 92, 99, 93)
    fill_tiles(chunk, TILE_WALL, 104, 96, 105, 97)
    fill_tiles(chunk, TILE_WALL, 110, 100, 111, 101)

    # SESSION 38 FIDELITY PASS — Irithyll of the Boreal Valley DS3 details
    # DS3: Icicle columns, fountain debris, Silver Knight barricades, distant manor steps
    for tx in range(25, 60, 6):
        fill_tiles(chunk, TILE_WALL, tx, 30, tx+1, 31)             # Icicle columns
        fill_tiles(chunk, TILE_WALL, tx, 70, tx+1, 71)
    for tx in range(65, 100, 5):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+2, 36)             # Fountain debris
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+2, 76)
    for ty in range(25, 65, 8):
        fill_tiles(chunk, TILE_WALL, 40, ty, 41, ty+1)             # Street lantern bases
        fill_tiles(chunk, TILE_WALL, 90, ty, 91, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)                    # Central fountain
    fill_tiles(chunk, TILE_WALL, 110, 40, 112, 42)                  # Silver Knight barricade
    fill_tiles(chunk, TILE_WALL, 120, 65, 122, 67)                  # Distant Manor steps
    for tx in range(100, 130, 7):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+1, 51)             # Snow-covered rubble
    # --- SESSION 44 terrain (Irithyll of the Boreal Valley) ---
    # DS3: Icicle formations on buildings and streets
    for tx in range(20, 30):
        chunk[18][tx] = TILE_WALLTOP  # icicle ridge
    for tx in range(45, 55):
        chunk[25][tx] = TILE_WALLTOP  # icicle columns
    # Frozen fountain debris (DS3: central square fountain)
    for tx in range(35, 42):
        chunk[35][tx] = TILE_WALLTOP
    chunk[36][38] = TILE_WALL  # fountain center
    # Silver Knight barricades (DS3: near Anor Londo entrance)
    for ty in range(50, 55):
        chunk[ty][60] = TILE_WALL
    # Street lantern bases (DS3: magical streetlights)
    for tx, ty in [(22, 22), (38, 28), (55, 24), (70, 30)]:
        chunk[ty][tx] = TILE_WALLTOP
    # Boreal frost patches
    for tx in range(65, 75):
        chunk[40][tx] = TILE_WALLTOP  # frost debris
    # Church of Yorshka approach columns
    for ty in range(30, 38):
        chunk[ty][48] = TILE_WALL

    # --- SESSION 47 terrain (Irithyll additions) ---
    # DS3: Distant Manor architecture
    for ty in range(15, 22):
        chunk[ty][80] = TILE_WALL
    # Sewer channel under the bridge
    for tx in range(45, 60):
        chunk[72][tx] = TILE_WALLTOP
    # Church of Yorshka window frame
    for ty in range(40, 46):
        chunk[ty][38] = TILE_WALL
    # Boreal valley ice formations
    for tx, ty in [(72, 18), (85, 22), (92, 16)]:
        chunk[ty][tx] = TILE_WALLTOP
    # Bridge railing near Pontiff area
    for tx in range(25, 35):
        chunk[28][tx] = TILE_WALLTOP

    # --- SESSION 53 terrain (Irithyll final) ---
    # DS3: Pontiff Sulyvahn's cathedral exterior pillars
    for ty in range(10, 18):
        chunk[ty][65] = TILE_WALL  # cathedral pillar
        chunk[ty][70] = TILE_WALL  # cathedral pillar
    # Frozen waterfall (DS3: ice formation near the distant manor)
    for ty in range(30, 36):
        chunk[ty][85] = TILE_WALL  # ice cliff
    # Sewer grate openings along the canal
    for tx in range(40, 55):
        if tx % 3 == 0:
            chunk[68][tx] = TILE_WALLTOP  # grate debris
    # Silver Knight memorial arch (DS3: memorial near Anor Londo approach)
    for ty in range(50, 56):
        chunk[ty][75] = TILE_WALL  # memorial pillar
    # Boreal frost heave (DS3: ground pushed up by frost)
    for tx, ty in [(30, 45), (45, 48), (58, 45)]:
        chunk[ty][tx] = TILE_WALLTOP  # frost heave

    # --- SESSION 56 terrain (Irithyll final) ---
    # DS3: Central square fountain basin (DS3: the main square has a frozen fountain)
    for tx in range(38, 44):
        chunk[42][tx] = TILE_WALLTOP  # fountain rim
    # Siegward's kitchen debris (DS3: distant manor kitchen where Siegward cooks)
    for tx in range(25, 32):
        chunk[78][tx] = TILE_WALLTOP  # kitchen debris
    # Irithyllian street lamp row (DS3: magical blue lamps line the streets)
    for tx, ty in [(32, 32), (48, 35), (62, 38)]:
        chunk[ty][tx] = TILE_WALL  # lamp post base
    # Church of Yorshka bell tower base
    for ty in range(32, 38):
        chunk[ty][50] = TILE_WALL  # bell tower base

    # --- SESSION 88 DS3 terrain (Irithyll detail pass) ---
    # DS3: Main avenue (wide boulevard through the city)
    for tx in range(15, 60):
        for ty in range(20, 28):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Buildings along the avenue (wall clusters)
    for tx in [15, 25, 35, 45]:
        for ty in [15, 16, 17]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][14] = TILE_WALLTOP
    for tx in [20, 30, 40, 50]:
        for ty in [30, 31, 32]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][33] = TILE_WALLTOP
    # DS3: Church of Yorshka (stone building)
    for tx in range(45, 58):
        for ty in [35, 48]:
            chunk[tx][ty] = TILE_WALL
    for tx in [45, 58]:
        for ty in range(35, 49):
            chunk[tx][ty] = TILE_WALL
    for tx in range(45, 59):
        chunk[tx][34] = TILE_WALLTOP
    # DS3: Church interior columns
    for tx in [48, 52, 56]:
        for ty in [38, 42, 46]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Icicles hanging from eaves
    for tx in [18, 22, 28, 32, 38, 42, 48, 55]:
        for ty in [18, 19]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Central fountain with debris
    for tx in range(55, 62):
        for ty in range(22, 28):
            chunk[tx][ty] = TILE_WALL
        chunk[tx][21] = TILE_WALLTOP
    # DS3: Sewer canal (underground waterway)
    for tx in range(30, 65):
        for ty in range(70, 76):
            chunk[tx][ty] = TILE_GROUND
    for tx in [30, 65]:
        for ty in range(70, 77):
            chunk[tx][ty] = TILE_WALL
    # DS3: Pontiff Sulyvahn's cathedral
    for tx in range(80, 100):
        for ty in [50, 65]:
            chunk[tx][ty] = TILE_WALL
    for tx in [80, 100]:
        for ty in range(50, 66):
            chunk[tx][ty] = TILE_WALL
    for tx in range(80, 101):
        chunk[tx][49] = TILE_WALLTOP
    # DS3: Frost patches on the ground
    for tx in range(20, 50):
        for ty in [25, 26]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Distant manor (Anor Londo approach)
    for tx in range(100, 115):
        for ty in [30, 42]:
            chunk[tx][ty] = TILE_WALL
    for tx in [100, 115]:
        for ty in range(30, 43):
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 92 DS3 terrain round 2 (Irithyll) ---
    # DS3: Central canal (water channel through the city)
    for tx in range(20, 50):
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_GROUND
    for tx in range(20, 50):
        chunk[tx][29] = TILE_WALL
        chunk[tx][32] = TILE_WALL
    # DS3: Barricades across side streets
    for tx in [35, 50, 65]:
        for ty in [24, 25, 26]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Street lanterns (stone posts)
    for tx in [18, 25, 32, 40, 48, 56, 64]:
        for ty in [28, 29]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Manor interior (Siegward's prison)
    for tx in range(70, 82):
        for ty in [55, 62]:
            chunk[tx][ty] = TILE_WALL
    for tx in [70, 82]:
        for ty in range(55, 63):
            chunk[tx][ty] = TILE_WALL
    for tx in range(70, 83):
        chunk[tx][54] = TILE_WALLTOP
    # DS3: Sewer entrance (grated opening)
    for tx in range(55, 65):
        for ty in [68, 69]:
            chunk[tx][ty] = TILE_WALL
    for tx in [55, 65]:
        for ty in range(66, 70):
            chunk[tx][ty] = TILE_WALL
    # DS3: Pontiff's arena pillars (large stone columns)
    for tx in [85, 92, 99]:
        for ty in [55, 60]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    
    # ================================================================
    # LATE CONNECTIVITY — corridors carved AFTER all wall placement
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 10, 20, 35, 45)     # Entry → Upper cells
    fill_tiles(chunk, TILE_GROUND, 38, 38, 58, 50)     # Upper → Central
    fill_tiles(chunk, TILE_GROUND, 50, 60, 75, 78)     # Central → Lower
    fill_tiles(chunk, TILE_GROUND, 68, 70, 90, 85)     # Lower → Waterways
    fill_tiles(chunk, TILE_GROUND, 90, 40, 120, 55)    # Tower → Exit corridor
    fill_tiles(chunk, TILE_GROUND, 20, 90, 50, 105)    # Sewers → Dark room
    # Boss-to-main-cluster corridor
    fill_tiles(chunk, TILE_GROUND, 220, 110, 255, 155) # Pontiff → main cluster
    fill_tiles(chunk, TILE_GROUND, 200, 100, 240, 120) # Silver Knight area → boss

    # --- DS3 faithful enemies (Irithyll) ---
    # SulyvahnsBeast (3)
    entities.append(make_entity("Enemy", 12 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SulyvahnsBeast", "SulyvahnsBeast"))]))
    entities.append(make_entity("Enemy", 72 * 16, 90 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SulyvahnsBeast", "SulyvahnsBeast"))]))
    entities.append(make_entity("Enemy", 78 * 16, 94 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SulyvahnsBeast", "SulyvahnsBeast"))]))
    # PontiffKnight (13) — DS3: Sulyvahn's elite knights patrolling Irithyll
    for tx, ty in [(18, 42), (38, 50), (55, 55), (75, 60), (90, 58), (32, 72), (40, 82), (70, 45), (72, 42), (105, 65), (100, 62), (108, 68), (132, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PontiffKnight", "PontiffKnight"))]))
    # IrithyllianSlave (18)
    for tx, ty in [(42, 48), (60, 52), (78, 56), (36, 44), (46, 46), (52, 50), (56, 48), (62, 56), (82, 52), (28, 70), (35, 75), (22, 68), (64, 44), (45, 55), (48, 54), (58, 60), (50, 58), (56, 60)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("IrithyllianSlave", "IrithyllianSlave"))]))
    # BurningStakeWitch (4) — DS3: witches with burning stakes patrolling Irithyll streets
    for tx, ty in [(42, 52), (95, 62), (68, 58), (110, 70)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BurningStakeWitch", "BurningStakeWitch"))]))
    # IrithyllianBeasthound (8) — DS3: ice beasts patrolling with Irithyllian slaves
    for tx, ty in [(50, 48), (80, 55), (65, 54), (48, 60), (52, 62), (76, 58), (38, 65), (42, 68)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("IrithyllianBeasthound", "IrithyllianBeasthound"))]))
    # CrystalLizard (4)
    entities.append(make_entity("Enemy", 65 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 128 * 16, 75 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 135 * 16, 80 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 140 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # IrithyllianSlave (5 additional — DS3: slaves feigning death in waterway district)
    for tx, ty in [(68, 80), (78, 85), (88, 90), (72, 88), (82, 82)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("IrithyllianSlave", "IrithyllianSlave"))]))
    # SilverKnight (13)
    for tx, ty in [(30, 100), (42, 110), (48, 118), (36, 108), (44, 105), (32, 104), (138, 64), (146, 64), (140, 50), (142, 48), (144, 52), (146, 54), (148, 56)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SilverKnight", "SilverKnight"))]))
    # GiantSlave (2)
    entities.append(make_entity("Enemy", 126 * 16, 78 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))
    entities.append(make_entity("Enemy", 134 * 16, 82 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))
    # PontiffKnight (2 additional — DS3: Sulyvahn's knights patrolling near church)
    for tx, ty in [(46, 50), (88, 60)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PontiffKnight", "PontiffKnight"))]))
    # IrithyllianSlave (3 additional — DS3: slaves feigning death in Irithyll streets)
    for tx, ty in [(22, 45), (30, 48), (58, 52)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("IrithyllianSlave", "IrithyllianSlave"))]))
    # IrithyllianBeasthound (3 additional — DS3: ice beasts patrolling waterway areas)
    for tx, ty in [(75, 85), (85, 90), (92, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("IrithyllianBeasthound", "IrithyllianBeasthound"))]))
    # DeepAccursed (1) — DS3: deep accursed in church basement
    entities.append(make_entity("Enemy", 38 * 16, 100 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DeepAccursed", "DeepAccursed"))]))
    # Mimic (1)
    entities.append(make_entity("Enemy", 58 * 16, 56 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Mimic", "Mimic"))]))
    # MiniBoss (1) — DS3: Pontiff Sulyvahn (boss)
    entities.append(make_entity("Enemy", 120 * 16, 76 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 32 * 16, 31 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Pontiff's Right Eye")]))
    entities.append(make_entity("Item", 33 * 16, 32 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 37 * 16, 33 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rime-blue Moss Clump")]))
    entities.append(make_entity("Item", 40 * 16, 35 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 42 * 16, 36 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 80 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 83 * 16, 49 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 86 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Budding Green Blossom")]))
    entities.append(make_entity("Item", 88 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 91 * 16, 51 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rime-blue Moss Clump")]))
    entities.append(make_entity("Item", 93 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 87 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Dorhys' Gnawing")]))
    entities.append(make_entity("Item", 90 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Witchtree Branch")]))
    entities.append(make_entity("Item", 85 * 16, 53 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 106 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Lightning Gem")]))
    entities.append(make_entity("Item", 107 * 16, 51 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Magic Clutch Ring")]))
    entities.append(make_entity("Item", 108 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Ring of the Sun's First Born")]))
    entities.append(make_entity("Item", 111 * 16, 51 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Proof of Concord Kept")]))
    entities.append(make_entity("Item", 112 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Roster of Knights")]))
    entities.append(make_entity("Item", 105 * 16, 54 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Fading Soul")]))
    entities.append(make_entity("Item", 103 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 106 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 96 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Blue Bug Pellet")]))
    entities.append(make_entity("Item", 100 * 16, 61 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Blue Bug Pellet")]))
    entities.append(make_entity("Item", 95 * 16, 56 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Shriving Stone")]))
    entities.append(make_entity("Item", 92 * 16, 67 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Kukri")]))
    entities.append(make_entity("Item", 91 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Gold Coin")]))
    entities.append(make_entity("Item", 98 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 97 * 16, 81 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Excrement-covered Ashes")]))
    entities.append(make_entity("Item", 148 * 16, 158 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Ring of Sacrifice")]))
    entities.append(make_entity("Item", 150 * 16, 161 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    entities.append(make_entity("Item", 160 * 16, 165 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Great Heal")]))
    entities.append(make_entity("Item", 190 * 16, 165 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 185 * 16, 102 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Gold Coin")]))
    entities.append(make_entity("Item", 203 * 16, 110 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 246 * 16, 77 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 246 * 16, 86 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Dark Stoneplate Ring")]))
    entities.append(make_entity("Item", 243 * 16, 83 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Drang Twinspears")]))
    entities.append(make_entity("Item", 242 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Deep Gem")]))
    entities.append(make_entity("Item", 241 * 16, 101 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Ring of Favor")]))
    entities.append(make_entity("Item", 240 * 16, 103 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Human Dregs")]))
    entities.append(make_entity("Item", 286 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Easterner's Ashes")]))
    entities.append(make_entity("Item", 288 * 16, 75 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 293 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Arrow"),
        make_field("name", "String", "Dragonslayer Greatarrow")]))
    entities.append(make_entity("Item", 292 * 16, 71 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Dragonslayer Greatbow")]))
    entities.append(make_entity("Item", 282 * 16, 67 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 285 * 16, 66 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 233 * 16, 101 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Brass Set")]))
    entities.append(make_entity("Item", 295 * 16, 71 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 246 * 16, 120 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of Pontiff Sulyvahn")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 187 * 16, 111 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 192 * 16, 111 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 273 * 16, 95 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 235 * 16, 102 * 16, [
        make_field("name", "String", "Unknown")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/Irithyll.json") as _f:

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

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0])) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100

    # print(f"  Irithyll (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "Irithyll", chunk, entities
