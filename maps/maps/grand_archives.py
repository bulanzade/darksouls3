from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_grand_archives():
    """Grand Archives — vertical library climb with Twin Princes boss.

    Faithful DS3 layout: the Grand Archives is a towering library ascent.
    Entry at the south from Lothric Castle, climbing through bookshelf mazes,
    a wax-pool hall, the scholar tower, winged knight corridors, gargoyle
    rooftops, and finally the Twin Princes chamber at the summit. Exit north
    to the Kiln of the First Flame.

    Vertical progression (y decreases = higher):
      1. Entry hall (south) — arrive from Lothric Castle
      2. First floor corridors — bookshelf maze
      3. Wax pool hall — slow wading through molten wax
      4. Scholar tower — crystal sage arena
      5. Winged Knight corridor — gauntlet to rooftop
      6. Gargoyle rooftop — open-air encounter
      7. Twin Princes chamber (north) — Lorian & Lothric boss fight
    """
    chunk = new_chunk(256, 384)
    entities = []

    # ================================================================
    # TERRAIN — carved from wall, south (high y) to north (low y)
    # ================================================================

    # 1. Entry hall (south, x=15-60, y=125-152)
    fill_tiles(chunk, TILE_GROUND, 15, 125, 60, 152)
    # Bookshelf walls
    fill_tiles(chunk, TILE_WALL, 25, 130, 27, 138)
    fill_tiles(chunk, TILE_WALL, 48, 134, 50, 140)

    # 2. First floor corridors — bookshelf maze (x=40-98, y=85-128)
    fill_tiles(chunk, TILE_GROUND, 40, 85, 98, 128)
    carve_ellipse(chunk, 68, 105, 16, 12)
    # Bookshelf walls
    fill_tiles(chunk, TILE_WALL, 52, 90, 54, 96)
    fill_tiles(chunk, TILE_WALL, 78, 100, 80, 106)
    fill_tiles(chunk, TILE_WALL, 60, 112, 62, 118)

    # 3. Wax pool hall (x=30-85, y=55-88)
    fill_tiles(chunk, TILE_GROUND, 30, 55, 85, 88)
    # Wax pool — slows movement but does NOT cause poison in DS3
    # Keep as TILE_GROUND (wax slows but is non-toxic)
    fill_tiles(chunk, TILE_GROUND, 42, 62, 72, 80)
    # Walls around pool
    fill_tiles(chunk, TILE_WALL, 55, 60, 57, 65)
    fill_tiles(chunk, TILE_WALL, 68, 72, 70, 76)

    # 4. Scholar tower (x=65-108, y=30-58)
    fill_tiles(chunk, TILE_GROUND, 65, 30, 108, 58)
    carve_ellipse(chunk, 86, 44, 14, 10)
    # Tower walls
    fill_tiles(chunk, TILE_WALL, 74, 35, 76, 40)
    fill_tiles(chunk, TILE_WALL, 96, 42, 98, 47)

    # 5. Winged Knight corridor (x=50-100, y=18-35)
    fill_tiles(chunk, TILE_GROUND, 50, 18, 100, 35)
    # Corridor walls
    fill_tiles(chunk, TILE_WALL, 62, 22, 64, 26)
    fill_tiles(chunk, TILE_WALL, 85, 26, 87, 30)

    # 6. Gargoyle rooftop (x=58-108, y=5-22)
    fill_tiles(chunk, TILE_GROUND, 58, 5, 108, 22)
    # Rooftop walls
    fill_tiles(chunk, TILE_WALL, 70, 8, 72, 12)
    fill_tiles(chunk, TILE_WALL, 92, 14, 94, 18)

    # 7. Twin Princes chamber (x=80-140, y=5-35)
    fill_tiles(chunk, TILE_GROUND, 80, 5, 140, 35)
    carve_ellipse(chunk, 110, 18, 22, 14)

    # 8. Lift shortcut alcove — Lothric Castle shortcut off the Bridge of Glory
    fill_tiles(chunk, TILE_GROUND, 128, 28, 148, 38)
    # Hidden lift platform alcove (Titanite Slab from lift trick)
    fill_tiles(chunk, TILE_GROUND, 132, 36, 142, 46)

    # ================================================================
    # CONNECTIONS — vertical staircases between levels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 38, 120, 48, 130)    # Entry hall → First floor
    fill_tiles(chunk, TILE_GROUND, 55, 82, 65, 88)      # First floor → Wax pool
    fill_tiles(chunk, TILE_GROUND, 72, 52, 82, 58)      # Wax pool → Scholar tower
    fill_tiles(chunk, TILE_GROUND, 85, 30, 95, 35)      # Scholar tower → WK corridor
    fill_tiles(chunk, TILE_GROUND, 75, 15, 85, 22)      # WK corridor → Rooftop
    fill_tiles(chunk, TILE_GROUND, 98, 10, 105, 18)     # Rooftop → Princes chamber
    fill_tiles(chunk, TILE_GROUND, 128, 22, 135, 30)    # Bridge → Lift shortcut alcove

    # ================================================================
    # CONNECTIVITY CORRIDORS — ensure all levels are walkable
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 40, 122, 52, 130)    # Entry → First floor (wide)
    fill_tiles(chunk, TILE_GROUND, 48, 82, 70, 90)      # First floor → Wax pool (wide)
    fill_tiles(chunk, TILE_GROUND, 65, 52, 90, 60)      # Wax pool → Scholar tower (wide)
    fill_tiles(chunk, TILE_GROUND, 68, 28, 100, 36)     # Scholar tower → WK corridor (wide)
    fill_tiles(chunk, TILE_GROUND, 62, 14, 90, 24)      # WK corridor → Rooftop (wide)
    fill_tiles(chunk, TILE_GROUND, 90, 8, 120, 22)      # Rooftop → Princes chamber (wide)
    fill_tiles(chunk, TILE_GROUND, 128, 24, 142, 38)    # Bridge → Lift shortcut (wide)
    fill_tiles(chunk, TILE_GROUND, 40, 150, 52, 175)    # Entry hall → lower archives
    fill_tiles(chunk, TILE_GROUND, 60, 170, 120, 180)   # Lower archives horizontal link
    fill_tiles(chunk, TILE_GROUND, 115, 170, 125, 195)  # Link to vertical tower shaft
    fill_tiles(chunk, TILE_GROUND, 135, 175, 145, 195)  # Link to right side lower archives

    # ================================================================
    # SESSION 9 FIDELITY PASS — GrandArchives architectural details
    # ================================================================
    # Main hall — bookshelf alcove walls (DS3: towering bookshelves)
    fill_tiles(chunk, TILE_WALL, 28, 130, 29, 131)
    fill_tiles(chunk, TILE_WALL, 34, 134, 35, 135)
    fill_tiles(chunk, TILE_WALL, 22, 138, 23, 139)
    fill_tiles(chunk, TILE_WALL, 40, 126, 41, 127)
    fill_tiles(chunk, TILE_WALL, 30, 142, 31, 143)
    # Wax pool room — candle cluster stones (DS3: wax-scholar pool area)
    fill_tiles(chunk, TILE_WALL, 48, 118, 49, 119)
    fill_tiles(chunk, TILE_WALL, 54, 122, 55, 123)
    fill_tiles(chunk, TILE_WALL, 44, 126, 45, 127)
    fill_tiles(chunk, TILE_WALL, 56, 114, 57, 115)
    # Crystal sages room — crystal formation debris (DS3: crystal growths in archives)
    fill_tiles(chunk, TILE_WALL, 62, 100, 63, 101)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    fill_tiles(chunk, TILE_WALL, 58, 104, 59, 105)
    fill_tiles(chunk, TILE_WALL, 72, 92, 73, 93)
    # Twin Princes chamber — throne debris (DS3: Lothric's chamber with throne)
    fill_tiles(chunk, TILE_WALL, 100, 12, 101, 13)
    fill_tiles(chunk, TILE_WALL, 104, 16, 105, 17)
    fill_tiles(chunk, TILE_WALL, 96, 18, 97, 19)
    fill_tiles(chunk, TILE_WALL, 108, 10, 109, 11)
    # Winged Knight corridor — armor stand stones (DS3: suits of armor in halls)
    fill_tiles(chunk, TILE_WALL, 78, 28, 79, 29)
    fill_tiles(chunk, TILE_WALL, 82, 32, 83, 33)
    fill_tiles(chunk, TILE_WALL, 74, 36, 75, 37)
    fill_tiles(chunk, TILE_WALL, 86, 24, 87, 25)
    # Rooftop — gargoyle perch stones (DS3: gargoyles patrol the rooftops)
    fill_tiles(chunk, TILE_WALL, 90, 14, 91, 15)
    fill_tiles(chunk, TILE_WALL, 94, 18, 95, 19)
    fill_tiles(chunk, TILE_WALL, 88, 22, 89, 23)
    # Bridge shortcut — broken railing stones (DS3: lift bridge connects areas)
    fill_tiles(chunk, TILE_WALL, 130, 24, 131, 25)
    fill_tiles(chunk, TILE_WALL, 134, 28, 135, 29)
    fill_tiles(chunk, TILE_WALL, 126, 30, 127, 31)


    # ================================================================
    # DS3 BOOKSHELF MAZE — Grand Archives narrow library corridors
    # DS3: towering bookshelves create a maze-like library with narrow
    # passages, reading alcoves, and dead-end stacks
    # ================================================================
    # Entry hall — full bookshelf rows (DS3: tall bookshelves line entry hall)
    fill_tiles(chunk, TILE_WALL, 18, 126, 22, 140)  # Left bookshelf row
    fill_tiles(chunk, TILE_WALL, 38, 128, 42, 142)  # Right bookshelf row
    fill_tiles(chunk, TILE_WALL, 28, 132, 34, 138)  # Center bookshelf divider
    # First floor — long bookshelf rows creating maze corridors (DS3: labyrinthine library)
    fill_tiles(chunk, TILE_WALL, 44, 86, 48, 100)   # Bookshelf row NW
    fill_tiles(chunk, TILE_WALL, 56, 92, 60, 108)   # Bookshelf row N
    fill_tiles(chunk, TILE_WALL, 68, 88, 72, 102)   # Bookshelf row NE
    fill_tiles(chunk, TILE_WALL, 80, 94, 84, 110)   # Bookshelf row E
    fill_tiles(chunk, TILE_WALL, 44, 108, 48, 120)  # Bookshelf row SW
    fill_tiles(chunk, TILE_WALL, 64, 112, 68, 124)  # Bookshelf row S
    fill_tiles(chunk, TILE_WALL, 82, 106, 86, 118)  # Bookshelf row SE
    fill_tiles(chunk, TILE_WALL, 90, 90, 94, 104)   # Bookshelf row far E
    # Wax pool hall — perimeter bookshelf walls (DS3: wax pool surrounded by shelves)
    fill_tiles(chunk, TILE_WALL, 32, 58, 36, 72)    # Left bookshelf
    fill_tiles(chunk, TILE_WALL, 72, 60, 76, 74)    # Right bookshelf
    fill_tiles(chunk, TILE_WALL, 44, 82, 68, 86)    # South bookshelf row
    fill_tiles(chunk, TILE_WALL, 44, 54, 68, 58)    # North bookshelf row
    # Scholar tower — desk and book clusters (DS3: crystal sage study area)
    fill_tiles(chunk, TILE_WALL, 68, 32, 72, 44)    # Tower bookshelf left
    fill_tiles(chunk, TILE_WALL, 88, 34, 92, 46)    # Tower bookshelf right
    fill_tiles(chunk, TILE_WALL, 78, 38, 84, 42)    # Tower center desk row
    fill_tiles(chunk, TILE_WALL, 98, 38, 104, 44)   # Tower far bookshelf
    # Winged Knight corridor — armor display walls (DS3: narrow hall with knights)
    fill_tiles(chunk, TILE_WALL, 52, 20, 56, 32)    # Corridor wall left
    fill_tiles(chunk, TILE_WALL, 68, 22, 72, 34)    # Corridor wall center
    fill_tiles(chunk, TILE_WALL, 84, 20, 88, 32)    # Corridor wall right
    # Gargoyle rooftop — chimney clusters (DS3: rooftop with chimney stacks)
    fill_tiles(chunk, TILE_WALL, 62, 8, 66, 18)     # Chimney stack 1
    fill_tiles(chunk, TILE_WALL, 78, 10, 82, 20)    # Chimney stack 2
    fill_tiles(chunk, TILE_WALL, 94, 6, 98, 16)     # Chimney stack 3
    fill_tiles(chunk, TILE_WALL, 106, 12, 110, 22)  # Chimney stack 4
    # Twin Princes chamber — throne room pillars (DS3: grand throne room)
    fill_tiles(chunk, TILE_WALL, 92, 8, 96, 18)     # Throne pillar left
    fill_tiles(chunk, TILE_WALL, 108, 12, 112, 22)  # Throne pillar center
    fill_tiles(chunk, TILE_WALL, 124, 8, 128, 18)   # Throne pillar right
    fill_tiles(chunk, TILE_WALL, 136, 14, 140, 24)  # Throne pillar far right
    # ================================================================
    spawn_px, spawn_py = 25 * 16, 142 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    entities.append(make_entity("Bonfire", 45 * 16, 342 * 16))     # Entry bonfire
    entities.append(make_entity("Bonfire", 181 * 16, 38 * 16))     # Twin Princes bonfire

    # ================================================================
    # BOSS SPAWN — Twin Princes (Lorian & Lothric)
    # ================================================================
    entities.append(make_entity("BossSpawn", 181 * 16, 38 * 16))

    # ================================================================
    # ENEMIES — DS3 Grand Archives (wiki-complete)
    # ================================================================

    # ================================================================
    # ITEMS — DS3 Grand Archives (wiki-complete)
    # ================================================================
    items = [
        # Spells
        ("Consumable", "Power Within", 55, 80, 0),
        ("Consumable", "Soul Stream", 60, 70, 0),
        ("Consumable", "Divine Pillars of Light", 88, 32, 0),
        # Consumables — souls
        ("SoulOrb", "Soul of a Crestfallen Knight", 32, 138, 600),
        ("SoulOrb", "Soul of a Crestfallen Knight", 78, 35, 600),
        ("SoulOrb", "Soul of a Nameless Soldier", 52, 78, 1000),
        ("SoulOrb", "Soul of a Weary Warrior", 72, 15, 1000),
        ("SoulOrb", "Large Soul of a Crestfallen Knight", 82, 30, 1500),
        # Consumables
        ("HomewardBone", "Homeward Bone", 60, 108, 0),
        ("HomewardBone", "Homeward Bone", 65, 88, 0),
        ("HomewardBone", "Homeward Bone", 72, 92, 0),
        ("Ember", "Ember", 57, 96, 0),
        # Weapons
        ("WeaponDrop", "Avelyn", 68, 85, 0),
        ("WeaponDrop", "Golden Wing Crest Shield", 80, 32, 0),
        ("WeaponDrop", "Sage's Crystal Staff", 82, 28, 0),
        ("WeaponDrop", "Onikiri and Ubadachi", 84, 30, 0),
        ("WeaponDrop", "Crystal Chime", 70, 60, 0),
        # Scrolls
        ("Consumable", "Crystal Scroll", 48, 125, 0),
        # Armor
        ("ArmorDrop", "Outrider Knight Armor Set", 60, 70, 0),
        # Upgrade materials — Titanite Chunks (8x)
        ("TitaniteShard", "Titanite Chunk", 42, 90, 0),
        ("TitaniteShard", "Titanite Chunk", 55, 95, 0),
        ("TitaniteShard", "Titanite Chunk", 65, 60, 0),
        ("TitaniteShard", "Titanite Chunk", 75, 42, 0),
        ("TitaniteShard", "Titanite Chunk", 88, 18, 0),
        ("TitaniteShard", "Titanite Chunk", 95, 22, 0),
        ("TitaniteShard", "Titanite Chunk", 70, 125, 0),
        ("TitaniteShard", "Titanite Chunk", 62, 75, 0),
        # Titanite Scales (5x ground pickups)
        ("TitaniteShard", "Titanite Scale", 58, 95, 0),
        ("TitaniteShard", "Titanite Scale", 52, 72, 0),
        ("TitaniteShard", "Titanite Scale", 68, 68, 0),
        ("TitaniteShard", "Titanite Scale", 77, 53, 0),
        ("TitaniteShard", "Titanite Scale", 65, 50, 0),
        # Titanite Slabs (3x — elevator secret + Winged Knights trio + lift trick)
        ("TitaniteShard", "Titanite Slab", 108, 15, 0),
        ("TitaniteShard", "Titanite Slab", 95, 35, 0),
        # Titanite Slab from lift trick (activate lift, roll off, ride second platform down)
        ("TitaniteShard", "Titanite Slab", 137, 42, 0),
        # Greirat's Ashes (adjacent rooftop — only obtainable by jumping)
        ("Consumable", "Greirat's Ashes", 92, 8, 0),
        # Third Soul of a Crestfallen Knight (near Winged Knights / rooftops)
        ("SoulOrb", "Soul of a Crestfallen Knight", 85, 8, 600),
        # Other upgrade materials
        ("Consumable", "Shriving Stone", 82, 45, 0),
        ("Consumable", "Hollow Gem", 100, 15, 0),
        ("Consumable", "Blessed Gem", 90, 30, 0),
        ("UndeadBoneShard", "Undead Bone Shard", 55, 100, 0),
        ("EstusShard", "Estus Shard", 82, 20, 0),
        # Rings
        ("RingDrop", "Fleshbite Ring", 90, 22, 0),
        ("RingDrop", "Hunter's Ring", 88, 18, 0),
        ("RingDrop", "Scholar Ring", 68, 72, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    # ================================================================
    # CHESTS — DS3 Grand Archives (5 chests, 0 mimics)
    # ================================================================

    # ================================================================
    # NPC — DS3 Grand Archives
    # ================================================================
    # Black Hand Gotthard (dead body at Grand Archives entrance — drops Grand Archives Key)
    # DS3: Gotthard's corpse is at the doors of Grand Archives, not deep inside
    entities.append(make_entity("Npc", 40 * 16, 347 * 16, [
        make_field("name", "String", "Black Hand Gotthard"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#606060"),
        make_field("dialogue", "String",
            "A corpse with the Grand Archives Key|"
            "Black Hand Gotthard's journey ends here|He was one of the King's Black Hands|"
            "The Black Hands serve the kingdom's darkest secrets|"
            "Gotthard must have come seeking the Prince"),
    ]))
    # NOTE: Siegward does NOT appear in Grand Archives in DS3.
    # His locations: Undead Settlement, Cathedral well, Irithyll kitchen, Irithyll Dungeon cell, Profaned Capital cell.
    # Grand Archives has no Siegward NPC dialogue encounter.

    # ================================================================
    # FOG GATES — area transitions
    # ================================================================
    # South: back to Lothric Castle
    entities.append(make_entity("FogGate", 45 * 16, 348 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 2400.0), make_field("dest_y", "Float", 1500.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # North: to Kiln of the First Flame
    entities.append(make_entity("FogGate", 181 * 16, 32 * 16, [
        make_field("dest_area", "String", "KilnOfTheFirstFlame"),
        make_field("dest_x", "Float", 1280.0), make_field("dest_y", "Float", 2320.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))

    # ================================================================
    # LIGHTS — candlelight, wax glow, golden sunlight
    # ================================================================
    # Entry hall — warm candlelight
    entities.append(make_entity("Light", 25 * 16, 142 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.9), make_field("g", "Float", 0.7), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    # Wax pool hall — orange molten-wax glow
    entities.append(make_entity("Light", 57 * 16, 72 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.5), make_field("b", "Float", 0.1), make_field("intensity", "Float", 0.35)]))
    # Scholar tower — cool candlelight
    entities.append(make_entity("Light", 86 * 16, 44 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.4), make_field("g", "Float", 0.5), make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.35)]))
    # Twin Princes chamber — golden sunlight from above
    entities.append(make_entity("Light", 110 * 16, 12 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.95), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.5)]))

    # ================================================================
    # ADDITIONAL INTERNAL STRUCTURES — bookshelf maze, desks, pillars
    # ================================================================
    # Entry hall — bookshelf walls
    fill_tiles(chunk, TILE_WALL, 20, 135, 22, 138)
    fill_tiles(chunk, TILE_WALL, 30, 138, 32, 142)
    fill_tiles(chunk, TILE_WALL, 25, 128, 27, 130)
    fill_tiles(chunk, TILE_WALL, 38, 130, 40, 132)
    # Wax pool hall — wax pillars and bookshelves
    fill_tiles(chunk, TILE_WALL, 45, 65, 47, 68)
    fill_tiles(chunk, TILE_WALL, 55, 70, 57, 72)
    fill_tiles(chunk, TILE_WALL, 62, 78, 64, 80)
    fill_tiles(chunk, TILE_WALL, 50, 80, 52, 82)
    fill_tiles(chunk, TILE_WALL, 40, 72, 42, 74)
    fill_tiles(chunk, TILE_WALL, 68, 68, 70, 70)
    # Scholar tower — desk and shelf clusters
    fill_tiles(chunk, TILE_WALL, 78, 35, 80, 38)
    fill_tiles(chunk, TILE_WALL, 85, 40, 87, 42)
    fill_tiles(chunk, TILE_WALL, 92, 36, 94, 38)
    fill_tiles(chunk, TILE_WALL, 80, 48, 82, 50)
    fill_tiles(chunk, TILE_WALL, 90, 50, 92, 52)
    fill_tiles(chunk, TILE_WALL, 98, 42, 100, 44)
    # Winged Knight corridors — suit of armor displays
    fill_tiles(chunk, TILE_WALL, 38, 55, 40, 58)
    fill_tiles(chunk, TILE_WALL, 50, 52, 52, 55)
    fill_tiles(chunk, TILE_WALL, 60, 55, 62, 58)
    fill_tiles(chunk, TILE_WALL, 42, 45, 44, 48)
    # Gargoyle rooftops — chimney and roof structures
    fill_tiles(chunk, TILE_WALL, 65, 18, 67, 22)
    fill_tiles(chunk, TILE_WALL, 75, 22, 77, 26)
    fill_tiles(chunk, TILE_WALL, 85, 18, 87, 22)
    fill_tiles(chunk, TILE_WALL, 95, 20, 97, 24)
    fill_tiles(chunk, TILE_WALL, 70, 28, 72, 30)
    fill_tiles(chunk, TILE_WALL, 80, 30, 82, 32)
    # Twin Princes chamber — throne room pillars
    fill_tiles(chunk, TILE_WALL, 100, 8, 102, 10)
    fill_tiles(chunk, TILE_WALL, 115, 10, 117, 12)
    fill_tiles(chunk, TILE_WALL, 125, 8, 127, 10)
    fill_tiles(chunk, TILE_WALL, 105, 20, 107, 22)
    fill_tiles(chunk, TILE_WALL, 118, 22, 120, 24)
    # Bridge of Glory — barricade walls (zigzag gauntlet before Twin Princes)
    # Wiki: "series of blockades with many hollows behind them, then knights"
    fill_tiles(chunk, TILE_WALL, 110, 5, 112, 11)     # Barricade 1 (north gap)
    fill_tiles(chunk, TILE_WALL, 116, 13, 118, 20)    # Barricade 2 (south gap)
    fill_tiles(chunk, TILE_WALL, 122, 5, 124, 12)     # Barricade 3 (north gap)
    # Lift shortcut alcove walls
    fill_tiles(chunk, TILE_WALL, 130, 30, 132, 34)
    fill_tiles(chunk, TILE_WALL, 144, 30, 146, 36)

    # === MORE GRAND ARCHIVES DETAILS — DS3 fidelity ===
    # Entry hall — more bookshelf rows (DS3: towering bookshelves)
    fill_tiles(chunk, TILE_WALL, 35, 125, 37, 127)
    fill_tiles(chunk, TILE_WALL, 45, 128, 47, 130)
    fill_tiles(chunk, TILE_WALL, 52, 132, 54, 134)
    fill_tiles(chunk, TILE_WALL, 42, 140, 44, 142)
    fill_tiles(chunk, TILE_WALL, 55, 138, 57, 140)
    fill_tiles(chunk, TILE_WALL, 32, 132, 34, 134)
    # First floor corridors — dense bookshelf maze (DS3: labyrinthine library)
    fill_tiles(chunk, TILE_WALL, 45, 88, 47, 90)
    fill_tiles(chunk, TILE_WALL, 58, 95, 60, 97)
    fill_tiles(chunk, TILE_WALL, 68, 90, 70, 92)
    fill_tiles(chunk, TILE_WALL, 82, 95, 84, 97)
    fill_tiles(chunk, TILE_WALL, 48, 100, 50, 102)
    fill_tiles(chunk, TILE_WALL, 65, 105, 67, 107)
    fill_tiles(chunk, TILE_WALL, 75, 110, 77, 112)
    fill_tiles(chunk, TILE_WALL, 90, 108, 92, 110)
    fill_tiles(chunk, TILE_WALL, 55, 115, 57, 117)
    fill_tiles(chunk, TILE_WALL, 72, 120, 74, 122)
    fill_tiles(chunk, TILE_WALL, 85, 118, 87, 120)
    fill_tiles(chunk, TILE_WALL, 95, 112, 97, 114)
    # Wax pool hall — more wax features (DS3: central wax pool)
    fill_tiles(chunk, TILE_WALL, 35, 58, 37, 60)
    fill_tiles(chunk, TILE_WALL, 48, 56, 50, 58)
    fill_tiles(chunk, TILE_WALL, 60, 58, 62, 60)
    fill_tiles(chunk, TILE_WALL, 75, 62, 77, 64)
    fill_tiles(chunk, TILE_WALL, 38, 82, 40, 84)
    fill_tiles(chunk, TILE_WALL, 72, 82, 74, 84)
    fill_tiles(chunk, TILE_WALL, 58, 85, 60, 87)
    # Scholar tower — crystal formations and book stacks (DS3: Crystal Sage arena)
    fill_tiles(chunk, TILE_WALL, 70, 32, 72, 34)
    fill_tiles(chunk, TILE_WALL, 82, 32, 84, 34)
    fill_tiles(chunk, TILE_WALL, 88, 48, 90, 50)
    fill_tiles(chunk, TILE_WALL, 100, 38, 102, 40)
    fill_tiles(chunk, TILE_WALL, 72, 45, 74, 47)
    fill_tiles(chunk, TILE_WALL, 95, 50, 97, 52)
    fill_tiles(chunk, TILE_WALL, 104, 44, 106, 46)
    # Winged Knight corridor — armor displays (DS3: golden Winged Knights)
    fill_tiles(chunk, TILE_WALL, 55, 22, 57, 24)
    fill_tiles(chunk, TILE_WALL, 68, 20, 70, 22)
    fill_tiles(chunk, TILE_WALL, 78, 25, 80, 27)
    fill_tiles(chunk, TILE_WALL, 90, 22, 92, 24)
    fill_tiles(chunk, TILE_WALL, 58, 30, 60, 32)
    fill_tiles(chunk, TILE_WALL, 82, 30, 84, 32)
    # Gargoyle rooftop — more roof structures (DS3: open rooftop with gargoyles)
    fill_tiles(chunk, TILE_WALL, 62, 10, 64, 12)
    fill_tiles(chunk, TILE_WALL, 78, 12, 80, 14)
    fill_tiles(chunk, TILE_WALL, 88, 8, 90, 10)
    fill_tiles(chunk, TILE_WALL, 100, 12, 102, 14)
    fill_tiles(chunk, TILE_WALL, 74, 16, 76, 18)
    fill_tiles(chunk, TILE_WALL, 92, 16, 94, 18)
    # Twin Princes chamber — throne room pillars (DS3: grand throne room)
    fill_tiles(chunk, TILE_WALL, 92, 15, 94, 18)
    fill_tiles(chunk, TILE_WALL, 108, 22, 110, 25)
    fill_tiles(chunk, TILE_WALL, 122, 18, 124, 20)
    fill_tiles(chunk, TILE_WALL, 130, 12, 132, 14)
    fill_tiles(chunk, TILE_WALL, 135, 20, 137, 22)
    fill_tiles(chunk, TILE_WALL, 98, 28, 100, 30)

    # ================================================================
    # DS3 GRAND ARCHIVES — final architectural fidelity pass
    # ================================================================
    # Grand staircase — landing walls between floors (DS3: main spiral staircase)
    fill_tiles(chunk, TILE_WALL, 48, 122, 50, 124)
    fill_tiles(chunk, TILE_WALL, 52, 118, 54, 120)
    fill_tiles(chunk, TILE_WALL, 58, 108, 60, 110)
    # Reading alcoves — desk and chair clusters (DS3: scholars study at desks)
    fill_tiles(chunk, TILE_WALL, 42, 92, 44, 94)
    fill_tiles(chunk, TILE_WALL, 56, 98, 58, 100)
    fill_tiles(chunk, TILE_WALL, 70, 102, 72, 104)
    fill_tiles(chunk, TILE_WALL, 88, 96, 90, 98)
    # Balcony railings overlooking lower floors (DS3: library has open balconies)
    fill_tiles(chunk, TILE_WALL, 62, 82, 64, 84)
    fill_tiles(chunk, TILE_WALL, 70, 78, 72, 80)
    fill_tiles(chunk, TILE_WALL, 48, 68, 50, 70)
    # Archive storage rooms — locked rooms with scrolls (DS3: side rooms full of scrolls)
    fill_tiles(chunk, TILE_WALL, 32, 62, 34, 64)
    fill_tiles(chunk, TILE_WALL, 78, 60, 80, 62)
    fill_tiles(chunk, TILE_WALL, 38, 75, 40, 77)
    # Crystal Sage crystal formations (DS3: crystal sage arena has crystal clusters)
    fill_tiles(chunk, TILE_WALL, 68, 38, 70, 40)
    fill_tiles(chunk, TILE_WALL, 84, 46, 86, 48)
    fill_tiles(chunk, TILE_WALL, 76, 42, 78, 44)
    # Candle-lined corridor sconces (DS3: candles everywhere, scholars carry them)
    fill_tiles(chunk, TILE_WALL, 36, 135, 38, 136)
    fill_tiles(chunk, TILE_WALL, 48, 142, 50, 143)
    fill_tiles(chunk, TILE_WALL, 28, 128, 30, 129)
    fill_tiles(chunk, TILE_WALL, 55, 125, 57, 126)
    # Wax pool edge — more wax formations (DS3: molten wax drips from ceiling)
    fill_tiles(chunk, TILE_WALL, 42, 58, 44, 59)
    fill_tiles(chunk, TILE_WALL, 64, 84, 66, 85)
    fill_tiles(chunk, TILE_WALL, 52, 88, 54, 89)
    # Lift mechanism walls (DS3: hidden lift for Titanite Slab)
    fill_tiles(chunk, TILE_WALL, 134, 34, 136, 36)
    fill_tiles(chunk, TILE_WALL, 140, 38, 142, 40)
    fill_tiles(chunk, TILE_WALL, 130, 40, 132, 42)

    # ================================================================
    # FINALIZE — connectivity check
    # SESSION 10 FIDELITY PASS — Grand Archives
    # Additional DS3-faithful terrain: bookshelf alcove walls, scholar desk debris,
    # crystal formation clusters, Twin Princes tower stones, wax pool edge details
    # Entrance hall — bookshelf alcove walls (DS3: massive bookshelves line halls)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 50, 65, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    # Scholar desks — study area debris (DS3: scholars at desks throughout)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 57)
    fill_tiles(chunk, TILE_WALL, 78, 60, 79, 61)
    fill_tiles(chunk, TILE_WALL, 66, 58, 67, 59)
    fill_tiles(chunk, TILE_WALL, 84, 54, 85, 55)
    # Crystal formations — crystal sage area (DS3: crystals near Crystal Sage)
    fill_tiles(chunk, TILE_WALL, 92, 62, 93, 63)
    fill_tiles(chunk, TILE_WALL, 98, 66, 99, 67)
    fill_tiles(chunk, TILE_WALL, 88, 68, 89, 69)
    fill_tiles(chunk, TILE_WALL, 102, 64, 103, 65)
    # Wax pool edges — candle cluster stones (DS3: wax pools with candles)
    fill_tiles(chunk, TILE_WALL, 108, 72, 109, 73)
    fill_tiles(chunk, TILE_WALL, 114, 68, 115, 69)
    fill_tiles(chunk, TILE_WALL, 104, 76, 105, 77)
    # Twin Princes tower — tower base stones (DS3: Lothric's tower at top)
    fill_tiles(chunk, TILE_WALL, 118, 82, 119, 83)
    fill_tiles(chunk, TILE_WALL, 124, 78, 125, 79)
    fill_tiles(chunk, TILE_WALL, 130, 84, 131, 85)
    fill_tiles(chunk, TILE_WALL, 122, 86, 123, 87)
    fill_tiles(chunk, TILE_WALL, 128, 80, 129, 81)
    # Dragon head — bridge debris (DS3: dragon head on bridge)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 62, 46, 63, 47)
    # Upper archive — more book clusters (DS3: books everywhere)
    fill_tiles(chunk, TILE_WALL, 136, 88, 137, 89)
    fill_tiles(chunk, TILE_WALL, 142, 84, 143, 85)
    fill_tiles(chunk, TILE_WALL, 132, 92, 133, 93)
    fill_tiles(chunk, TILE_WALL, 138, 90, 139, 91)
    # Gargoyle perch — roof stones (DS3: gargoyles on archive roof)
    fill_tiles(chunk, TILE_WALL, 146, 78, 147, 79)
    fill_tiles(chunk, TILE_WALL, 140, 76, 141, 77)

    # SESSION 10 PASS B — GrandArchives
    # Additional DS3 terrain: scholar desk debris, crystal sage formations, Twin Princes tower stones
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
    # SESSION 12 FIDELITY PASS — GrandArchives DS3 architectural details
    # ================================================================
    # Wax-dripping chandelier debris (DS3: wax-covered chandeliers hang from ceilings)
    fill_tiles(chunk, TILE_WALL, 26, 32, 27, 34)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 38)
    fill_tiles(chunk, TILE_WALL, 42, 30, 43, 32)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 36)
    # Book avalanche clusters (DS3: toppled book piles throughout archives)
    fill_tiles(chunk, TILE_WALL, 58, 40, 59, 42)
    fill_tiles(chunk, TILE_WALL, 66, 44, 67, 46)
    fill_tiles(chunk, TILE_WALL, 74, 38, 75, 40)
    fill_tiles(chunk, TILE_WALL, 82, 42, 83, 44)
    # Crystal Sage ritual circles (DS3: crystal formations near sage arena)
    fill_tiles(chunk, TILE_WALL, 46, 80, 48, 82)
    fill_tiles(chunk, TILE_WALL, 54, 84, 56, 86)
    fill_tiles(chunk, TILE_WALL, 62, 78, 64, 80)
    fill_tiles(chunk, TILE_WALL, 70, 82, 72, 84)
    # Gertrude's cage debris (DS3: cage where Divine Pillar of Light is found)
    fill_tiles(chunk, TILE_WALL, 38, 88, 39, 90)
    fill_tiles(chunk, TILE_WALL, 44, 92, 45, 94)
    fill_tiles(chunk, TILE_WALL, 32, 94, 33, 96)
    fill_tiles(chunk, TILE_WALL, 50, 86, 51, 88)
    # Manuscript scroll fragments (DS3: scattered scrolls and tomes)
    fill_tiles(chunk, TILE_WALL, 60, 90, 61, 92)
    fill_tiles(chunk, TILE_WALL, 68, 94, 69, 96)
    fill_tiles(chunk, TILE_WALL, 76, 88, 77, 90)
    fill_tiles(chunk, TILE_WALL, 84, 92, 85, 94)
    # Candelabra base stones (DS3: ornate candelabras throughout library)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 82)
    fill_tiles(chunk, TILE_WALL, 96, 84, 97, 86)
    fill_tiles(chunk, TILE_WALL, 102, 78, 103, 80)
    fill_tiles(chunk, TILE_WALL, 108, 82, 109, 84)
    # Broken lectern fragments (DS3: shattered reading stands in study alcoves)
    fill_tiles(chunk, TILE_WALL, 114, 76, 115, 78)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 82)
    fill_tiles(chunk, TILE_WALL, 126, 74, 127, 76)
    fill_tiles(chunk, TILE_WALL, 132, 78, 133, 80)
    # Golden feather debris (DS3: angelic feathers near Gertrude's area)
    fill_tiles(chunk, TILE_WALL, 36, 100, 37, 102)
    fill_tiles(chunk, TILE_WALL, 42, 104, 43, 106)
    fill_tiles(chunk, TILE_WALL, 48, 98, 49, 100)
    fill_tiles(chunk, TILE_WALL, 54, 102, 55, 104)
    # Twin Princes elevator shaft stones (DS3: elevator to Lothric's chamber)
    fill_tiles(chunk, TILE_WALL, 138, 86, 139, 88)
    fill_tiles(chunk, TILE_WALL, 144, 82, 145, 84)
    fill_tiles(chunk, TILE_WALL, 134, 90, 135, 92)
    fill_tiles(chunk, TILE_WALL, 142, 94, 143, 96)

    # ================================================================
    # SESSION 13 FIDELITY PASS — GrandArchives DS3 architecture
    # ================================================================
    # Library entrance — wax candle debris (DS3: wax pools at archive entrance)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 29)
    fill_tiles(chunk, TILE_WALL, 28, 34, 29, 35)
    fill_tiles(chunk, TILE_WALL, 16, 32, 17, 33)
    # Main library — bookshelf alcove walls (DS3: towering bookshelves)
    fill_tiles(chunk, TILE_WALL, 40, 36, 41, 37)
    fill_tiles(chunk, TILE_WALL, 46, 42, 47, 43)
    fill_tiles(chunk, TILE_WALL, 52, 38, 53, 39)
    fill_tiles(chunk, TILE_WALL, 58, 44, 59, 45)
    fill_tiles(chunk, TILE_WALL, 64, 40, 65, 41)
    # Crystal sage room — crystal growth clusters (DS3: Crystal Sage fight area)
    fill_tiles(chunk, TILE_WALL, 36, 52, 37, 53)
    fill_tiles(chunk, TILE_WALL, 42, 56, 43, 57)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    # Archive roof — crystal-encrusted railings (DS3: crystal-covered rooftops)
    fill_tiles(chunk, TILE_WALL, 18, 20, 19, 21)
    fill_tiles(chunk, TILE_WALL, 24, 24, 25, 25)
    fill_tiles(chunk, TILE_WALL, 30, 22, 31, 23)
    fill_tiles(chunk, TILE_WALL, 12, 26, 13, 27)
    # Gertrude's cage area — bird cage debris (DS3: Divine Pillars of Light location)
    fill_tiles(chunk, TILE_WALL, 72, 28, 73, 29)
    fill_tiles(chunk, TILE_WALL, 78, 32, 79, 33)
    fill_tiles(chunk, TILE_WALL, 84, 30, 85, 31)

    # ================================================================
    # SESSION 16 FIDELITY PASS — GrandArchives DS3 architectural details
    # ================================================================
    # Main library — bookshelf alcove walls (DS3: towering bookshelves in library halls)
    fill_tiles(chunk, TILE_WALL, 22, 62, 23, 64)
    fill_tiles(chunk, TILE_WALL, 32, 66, 33, 68)
    fill_tiles(chunk, TILE_WALL, 42, 70, 43, 72)
    fill_tiles(chunk, TILE_WALL, 52, 74, 53, 76)
    fill_tiles(chunk, TILE_WALL, 62, 78, 63, 80)
    # Wax puddle debris (DS3: wax-covered scholars leave puddles everywhere)
    fill_tiles(chunk, TILE_WALL, 26, 68, 27, 69)
    fill_tiles(chunk, TILE_WALL, 36, 72, 37, 73)
    fill_tiles(chunk, TILE_WALL, 46, 76, 47, 77)
    fill_tiles(chunk, TILE_WALL, 56, 80, 57, 81)
    # Candle sconce pillars (DS3: candles line the archive corridors)
    fill_tiles(chunk, TILE_WALL, 18, 66, 19, 67)
    fill_tiles(chunk, TILE_WALL, 28, 70, 29, 71)
    fill_tiles(chunk, TILE_WALL, 38, 74, 39, 75)
    fill_tiles(chunk, TILE_WALL, 48, 78, 49, 79)
    fill_tiles(chunk, TILE_WALL, 58, 82, 59, 83)
    # Bridge railings — iron balustrade (DS3: ornate bridges between archive wings)
    fill_tiles(chunk, TILE_WALL, 102, 40, 103, 41)
    fill_tiles(chunk, TILE_WALL, 108, 44, 109, 45)
    fill_tiles(chunk, TILE_WALL, 114, 48, 115, 49)
    fill_tiles(chunk, TILE_WALL, 120, 52, 121, 53)
    fill_tiles(chunk, TILE_WALL, 126, 56, 127, 57)
    # Dragon corpse debris (DS3: dead wyvern on archive roof)
    fill_tiles(chunk, TILE_WALL, 14, 28, 15, 30)
    fill_tiles(chunk, TILE_WALL, 10, 32, 11, 34)
    fill_tiles(chunk, TILE_WALL, 16, 36, 17, 38)

    # ================================================================
    # SESSION 18 FIDELITY PASS — GrandArchives DS3 library and roof details
    # ================================================================
    # Twin Princes arena — battlement debris (DS3: Lothric's chamber at the very top)
    fill_tiles(chunk, TILE_WALL, 136, 18, 138, 20)
    fill_tiles(chunk, TILE_WALL, 140, 24, 142, 26)
    fill_tiles(chunk, TILE_WALL, 134, 28, 136, 30)
    fill_tiles(chunk, TILE_WALL, 144, 20, 146, 22)
    # Crystal Sage study — crystal formations (DS3: crystal sage's private study)
    fill_tiles(chunk, TILE_WALL, 66, 68, 68, 70)
    fill_tiles(chunk, TILE_WALL, 74, 72, 76, 74)
    fill_tiles(chunk, TILE_WALL, 70, 76, 72, 78)
    fill_tiles(chunk, TILE_WALL, 82, 70, 84, 72)
    # Lower archives — reading desk walls (DS3: desks and book piles in archive halls)
    fill_tiles(chunk, TILE_WALL, 20, 82, 22, 84)
    fill_tiles(chunk, TILE_WALL, 30, 86, 32, 88)
    fill_tiles(chunk, TILE_WALL, 40, 84, 42, 86)
    fill_tiles(chunk, TILE_WALL, 50, 88, 52, 90)
    fill_tiles(chunk, TILE_WALL, 60, 86, 62, 88)
    # Grand Archives roof — railing and wyvern bones (DS3: extensive roof area)
    fill_tiles(chunk, TILE_WALL, 130, 34, 132, 36)
    fill_tiles(chunk, TILE_WALL, 138, 38, 140, 40)
    fill_tiles(chunk, TILE_WALL, 126, 42, 128, 44)

    # ================================================================
    # ================================================================
    # SESSION 22 FIDELITY PASS — GrandArchives DS3 library details
    # ================================================================
    # Bookshelf debris (DS3: fallen bookshelves in the Archives)
    fill_tiles(chunk, TILE_WALL, 22, 32, 23, 33)
    fill_tiles(chunk, TILE_WALL, 28, 36, 29, 37)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 41)
    fill_tiles(chunk, TILE_WALL, 40, 44, 41, 45)
    # Candle cluster debris (DS3: wax clusters from the wax head mechanic)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 49)
    fill_tiles(chunk, TILE_WALL, 52, 52, 53, 53)
    fill_tiles(chunk, TILE_WALL, 58, 56, 59, 57)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 61)
    # Crystal Sage debris (DS3: crystal formations from the Sage fight)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    fill_tiles(chunk, TILE_WALL, 86, 82, 87, 83)
    fill_tiles(chunk, TILE_WALL, 92, 86, 93, 87)
    fill_tiles(chunk, TILE_WALL, 98, 90, 99, 91)

    # ================================================================
    # SESSION 23 FIDELITY PASS — GrandArchives DS3 library details
    # ================================================================
    # Crystal Sage crystal formations (DS3: crystal growths near Sage arena)
    fill_tiles(chunk, TILE_WALL, 48, 68, 49, 69)
    fill_tiles(chunk, TILE_WALL, 54, 72, 55, 73)
    fill_tiles(chunk, TILE_WALL, 60, 76, 61, 77)
    fill_tiles(chunk, TILE_WALL, 66, 80, 67, 81)
    # Hunter's Ring balcony (DS3: exterior balcony with items)
    fill_tiles(chunk, TILE_WALL, 72, 84, 73, 85)
    fill_tiles(chunk, TILE_WALL, 78, 88, 79, 89)
    fill_tiles(chunk, TILE_WALL, 84, 92, 85, 93)
    fill_tiles(chunk, TILE_WALL, 90, 96, 91, 97)
    # Twin Princes elevator shaft (DS3: elevator mechanism near boss)
    fill_tiles(chunk, TILE_WALL, 96, 100, 97, 101)
    fill_tiles(chunk, TILE_WALL, 102, 104, 103, 105)
    fill_tiles(chunk, TILE_WALL, 108, 108, 109, 109)
    fill_tiles(chunk, TILE_WALL, 114, 112, 115, 113)

    # ================================================================
    # SESSION 27 FIDELITY PASS — GrandArchives DS3 library details
    # ================================================================
    # Gertrude's cage debris (DS3: Gertrude's cage on the archives roof)
    fill_tiles(chunk, TILE_WALL, 20, 38, 21, 39)
    fill_tiles(chunk, TILE_WALL, 26, 42, 27, 43)
    fill_tiles(chunk, TILE_WALL, 32, 46, 33, 47)
    fill_tiles(chunk, TILE_WALL, 38, 50, 39, 51)
    # Wax head mechanic debris (DS3: wax pools from the candle wax mechanic)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 55)
    fill_tiles(chunk, TILE_WALL, 50, 58, 51, 59)
    fill_tiles(chunk, TILE_WALL, 56, 62, 57, 63)
    fill_tiles(chunk, TILE_WALL, 62, 66, 63, 67)
    # Twin Princes elevator shaft (DS3: elevator to Lothric's chamber)
    fill_tiles(chunk, TILE_WALL, 68, 70, 69, 71)
    fill_tiles(chunk, TILE_WALL, 74, 74, 75, 75)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    fill_tiles(chunk, TILE_WALL, 86, 82, 87, 83)
    # Archives balcony railings (DS3: stone railings on the archives balconies)
    fill_tiles(chunk, TILE_WALL, 92, 86, 93, 87)
    fill_tiles(chunk, TILE_WALL, 98, 90, 99, 91)
    fill_tiles(chunk, TILE_WALL, 104, 94, 105, 95)
    fill_tiles(chunk, TILE_WALL, 110, 98, 111, 99)

    # ================================================================
    # SESSION 31 FIDELITY PASS — GrandArchives DS3 library details
    # ================================================================
    # Archives main hall bookshelves (DS3: towering bookshelves in the main hall)
    fill_tiles(chunk, TILE_WALL, 18, 40, 19, 41)
    fill_tiles(chunk, TILE_WALL, 24, 44, 25, 45)
    fill_tiles(chunk, TILE_WALL, 30, 48, 31, 49)
    fill_tiles(chunk, TILE_WALL, 36, 52, 37, 53)
    # Crystal Sage crystal growth (DS3: crystal formations throughout archives)
    fill_tiles(chunk, TILE_WALL, 42, 56, 43, 57)
    fill_tiles(chunk, TILE_WALL, 48, 60, 49, 61)
    fill_tiles(chunk, TILE_WALL, 54, 64, 55, 65)
    fill_tiles(chunk, TILE_WALL, 60, 68, 61, 69)
    # Twin Princes elevator debris (DS3: elevator shaft to Lothric's chamber)
    fill_tiles(chunk, TILE_WALL, 66, 72, 67, 73)
    fill_tiles(chunk, TILE_WALL, 72, 76, 73, 77)
    fill_tiles(chunk, TILE_WALL, 78, 80, 79, 81)
    fill_tiles(chunk, TILE_WALL, 84, 84, 85, 85)
    # Archives roof debris (DS3: debris on the archives rooftop)
    fill_tiles(chunk, TILE_WALL, 90, 88, 91, 89)
    fill_tiles(chunk, TILE_WALL, 96, 92, 97, 93)
    fill_tiles(chunk, TILE_WALL, 102, 96, 103, 97)
    fill_tiles(chunk, TILE_WALL, 108, 100, 109, 101)

    # SESSION 38 FIDELITY PASS — Grand Archives DS3 details
    # DS3: Bookshelf debris, candle clusters, Crystal Sage crystals, wax pools
    for tx in range(30, 70, 5):
        fill_tiles(chunk, TILE_WALL, tx, 25, tx+1, 26)             # Bookshelf debris
        fill_tiles(chunk, TILE_WALL, tx, 65, tx+1, 66)
    for tx in range(75, 120, 5):
        fill_tiles(chunk, TILE_WALL, tx, 30, tx+1, 31)             # Candle clusters
        fill_tiles(chunk, TILE_WALL, tx, 70, tx+1, 71)
    for ty in range(35, 60, 8):
        fill_tiles(chunk, TILE_WALL, 50, ty, 52, ty+1)             # Book pile stacks
        fill_tiles(chunk, TILE_WALL, 100, ty, 102, ty+1)
    fill_tiles(chunk, TILE_WALL, 60, 50, 62, 52)                    # Crystal Sage crystal
    fill_tiles(chunk, TILE_WALL, 110, 55, 112, 57)                  # Wax head pool
    fill_tiles(chunk, TILE_WALL, 80, 80, 82, 82)                    # Broken bookshelf
    for tx in range(120, 145, 6):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 41)             # Scroll racks
    # --- SESSION 44 terrain (Grand Archives) ---
    # DS3: Bookshelf debris throughout the library
    for tx in range(15, 25):
        chunk[20][tx] = TILE_WALLTOP  # fallen books
    for tx in range(40, 50):
        chunk[30][tx] = TILE_WALLTOP  # scattered scrolls
    # Crystal Sage crystal formations (DS3: grow on walls and floors)
    for tx, ty in [(55, 35), (60, 38), (65, 35)]:
        chunk[ty][tx] = TILE_WALLTOP  # crystal growth
    # Wax pool patches (DS3: wax-covered scholars leave pools)
    for tx in range(70, 78):
        chunk[25][tx] = TILE_WALLTOP  # wax residue
    # Grand staircase railing supports
    for ty in range(40, 48):
        chunk[ty][45] = TILE_WALL  # banister post
    # Candle cluster pedestals (DS3: scholars carry candles everywhere)
    for tx, ty in [(20, 35), (35, 40), (50, 38), (65, 42)]:
        chunk[ty][tx] = TILE_WALLTOP  # candle stand

    # --- SESSION 46 terrain (Grand Archives) ---
    # DS3: Grand staircase with railing supports
    for ty in range(15, 22):
        chunk[ty][30] = TILE_WALL  # staircase pillar
    # More bookshelf debris in the upper library
    for tx in range(55, 65):
        chunk[18][tx] = TILE_WALLTOP  # fallen scrolls
    # Crystal growth patches (DS3: crystals invade the archives)
    for tx, ty in [(70, 25), (80, 28), (90, 22)]:
        chunk[ty][tx] = TILE_WALLTOP  # crystal shard
    # Candle wax pool accumulation (DS3: scholars drip wax)
    for tx in range(35, 42):
        chunk[40][tx] = TILE_WALLTOP  # wax pool
    # Scroll rack debris
    for tx, ty in [(48, 35), (58, 38)]:
        chunk[ty][tx] = TILE_WALL  # fallen rack

    # --- SESSION 50 terrain (Grand Archives final) ---
    # DS3: Grand balcony railing along the exterior
    for tx in range(20, 30):
        chunk[12][tx] = TILE_WALLTOP  # balcony stone
    # Crystal Sage crystal garden (DS3: crystals grow in the archive garden)
    for tx in range(60, 68):
        chunk[50][tx] = TILE_WALLTOP  # crystal patch
    # Wax fountain (DS3: the wax pooling in the central hall)
    chunk[42][40] = TILE_WALL  # fountain edge
    chunk[42][41] = TILE_WALLTOP
    # Scroll archive debris
    for tx, ty in [(30, 45), (45, 50)]:
        chunk[ty][tx] = TILE_WALL  # fallen shelf

    # --- SESSION 53 terrain (Grand Archives final) ---
    # DS3: Grand reading hall pillars (the massive circular library)
    for ty in range(25, 32):
        chunk[ty][25] = TILE_WALL  # pillar
        chunk[ty][40] = TILE_WALL  # pillar
    # Candle wax accumulation (DS3: wax drips from chandeliers)
    for tx in range(50, 58):
        chunk[55][tx] = TILE_WALLTOP  # wax pool
    # Crystal Sage's laboratory crystals
    for tx, ty in [(65, 45), (72, 48)]:
        chunk[ty][tx] = TILE_WALL  # crystal formation
    # Scroll archive broken shelf
    for tx in range(80, 88):
        chunk[35][tx] = TILE_WALLTOP  # shelf debris

    # --- SESSION 89 DS3 terrain (Grand Archives detail pass) ---
    # DS3: Bookshelf rows (tall wooden shelves lining the halls)
    for tx in [15, 18, 21, 25, 28, 31, 35, 38, 41, 45, 48, 51, 55, 58, 61]:
        for ty in [15, 16, 17]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][14] = TILE_WALLTOP
    # DS3: Crystal formations (blue crystals growing on surfaces)
    for tx in range(65, 80):
        for ty in range(20, 30):
            chunk[tx][ty] = TILE_GROUND
    for tx in [68, 72, 76]:
        for ty in [22, 26]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Wax pools on the floor
    for tx in range(20, 40):
        for ty in range(35, 42):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Scroll racks (reading stations)
    for tx in [22, 28, 34, 40, 46, 52]:
        for ty in [42, 43]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Balcony overlooking the main hall
    for tx in range(15, 55):
        chunk[tx][48] = TILE_WALL
        chunk[tx][47] = TILE_WALLTOP
    # DS3: Crystal garden (outdoor area with crystal trees)
    for tx in range(70, 90):
        for ty in range(45, 58):
            chunk[tx][ty] = TILE_GROUND
    for tx in [72, 76, 80, 84, 88]:
        for ty in [48, 52]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Outrider Knight ambush alcove
    for tx in range(50, 58):
        for ty in [55, 60]:
            chunk[tx][ty] = TILE_WALL
    for tx in [50, 58]:
        for ty in range(55, 61):
            chunk[tx][ty] = TILE_WALL
    for tx in range(50, 59):
        chunk[tx][54] = TILE_WALLTOP

    # --- SESSION 93 DS3 terrain round 2 (Grand Archives) ---
    # DS3: Main reading hall with long tables
    for tx in [20, 24, 28, 32, 36, 40, 44, 48]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Candle clusters on shelves
    for tx in [17, 23, 29, 35, 41, 47]:
        for ty in [25, 26]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Crystal Sage arena (open courtyard)
    for tx in range(50, 65):
        for ty in range(30, 42):
            chunk[tx][ty] = TILE_GROUND
    for tx in [50, 65]:
        for ty in range(30, 43):
            chunk[tx][ty] = TILE_WALL
    # DS3: Wax-coated corridors
    for tx in range(30, 50):
        for ty in [45, 46]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Winged Knight rooftop perch
    for tx in range(60, 70):
        for ty in [12, 18]:
            chunk[tx][ty] = TILE_WALL
    for tx in [60, 70]:
        for ty in range(12, 19):
            chunk[tx][ty] = TILE_WALL
    for tx in range(60, 71):
        chunk[tx][11] = TILE_WALLTOP
    # DS3: Gertrude's room (elevated chamber)
    for tx in range(70, 82):
        for ty in [50, 58]:
            chunk[tx][ty] = TILE_WALL
    for tx in [70, 82]:
        for ty in range(50, 59):
            chunk[tx][ty] = TILE_WALL
    for tx in range(70, 83):
        chunk[tx][49] = TILE_WALLTOP
    
    # ================================================================
    # LATE CONNECTIVITY — corridors carved AFTER all wall placement
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 40, 120, 55, 132)   # Entry → First floor
    fill_tiles(chunk, TILE_GROUND, 50, 82, 75, 90)     # First floor → Wax pool
    fill_tiles(chunk, TILE_GROUND, 62, 52, 92, 62)     # Wax pool → Scholar tower
    fill_tiles(chunk, TILE_GROUND, 66, 28, 102, 38)    # Scholar → WK corridor
    fill_tiles(chunk, TILE_GROUND, 60, 12, 100, 26)    # WK corridor → Rooftop
    fill_tiles(chunk, TILE_GROUND, 88, 5, 130, 22)     # Rooftop → Princes chamber
    fill_tiles(chunk, TILE_GROUND, 126, 20, 145, 40)   # Bridge → Lift shortcut

    # CRITICAL: Final connectivity corridors (must be last terrain operations)
    # These connect ALL clusters to the main playable area
    fill_tiles(chunk, TILE_GROUND, 115, 190, 125, 285)  # Entry hall south -> lower archives
    fill_tiles(chunk, TILE_GROUND, 135, 190, 150, 225)  # Mid-level -> lower library
    fill_tiles(chunk, TILE_GROUND, 38, 22, 55, 35)      # Upper tower alcove -> main
    fill_tiles(chunk, TILE_GROUND, 42, 28, 52, 38)      # Small upper alcove -> main
    fill_tiles(chunk, TILE_GROUND, 85, 85, 100, 92)     # Wax pool island -> main
    fill_tiles(chunk, TILE_GROUND, 68, 72, 78, 80)      # Small wax pool island -> main
    fill_tiles(chunk, TILE_GROUND, 145, 32, 185, 45)    # Twin Princes -> main cluster
    fill_tiles(chunk, TILE_GROUND, 100, 30, 150, 50)    # Scholar tower -> Princes path

    # --- DS3 faithful enemies (GrandArchives) ---
    # GrandArchivesScholar (10) — DS3: wax-headed scholars throughout archives
    for tx, ty in [(45, 130), (50, 100), (55, 75), (48, 85), (72, 55), (62, 112), (88, 95), (95, 108), (115, 100), (125, 115)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GrandArchivesScholar", "DarkMage"))]))
    # CrystalSage (1) — DS3: boss-like sage that teleports in the archives
    entities.append(make_entity("Enemy", 85 * 16, 40 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalSage", "DarkMage"))]))
    # DarkMage (3) — DS3: remaining spell casters in upper archives
    for tx, ty in [(75, 28), (105, 120), (62, 95)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    # HollowSlave (19)
    for tx, ty in [(44, 136), (55, 98), (68, 108), (75, 50), (62, 65), (40, 138), (52, 92), (58, 80), (112, 8), (114, 10), (119, 15), (121, 18), (125, 7), (127, 12), (85, 105), (92, 115), (100, 125), (110, 110), (120, 130)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowSlave", "HollowSlave"))]))
    # LothricKnight (7)
    for tx, ty in [(70, 92), (88, 45), (55, 65), (78, 48), (130, 10), (132, 15), (130, 120)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LothricKnight", "LothricKnight"))]))
    # AscendedWingedKnight (3)
    entities.append(make_entity("Enemy", 82 * 16, 38 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("AscendedWingedKnight", "AscendedWingedKnight"))]))
    entities.append(make_entity("Enemy", 92 * 16, 35 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("AscendedWingedKnight", "AscendedWingedKnight"))]))
    entities.append(make_entity("Enemy", 75 * 16, 32 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("AscendedWingedKnight", "AscendedWingedKnight"))]))
    # BorealOutriderKnight (1)
    entities.append(make_entity("Enemy", 58 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BorealOutriderKnight", "BorealOutriderKnight"))]))
    # Gargoyle (3)
    entities.append(make_entity("Enemy", 68 * 16, 12 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Gargoyle", "Gargoyle"))]))
    entities.append(make_entity("Enemy", 82 * 16, 15 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Gargoyle", "Gargoyle"))]))
    entities.append(make_entity("Enemy", 95 * 16, 10 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Gargoyle", "Gargoyle"))]))
    # CrystalLizard (5)
    entities.append(make_entity("Enemy", 52 * 16, 85 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 48 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 65 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 88 * 16, 22 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 145 * 16, 118 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # ClawedCurse (4) — DS3: curse hands that emerge from bookshelves
    for tx, ty in [(46, 88), (70, 58), (90, 98), (110, 115)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ClawedCurse", "Basilisk"))]))
    # ManGrub (3) — DS3: grub-like creatures on beams and rafters
    for tx, ty in [(78, 65), (100, 105), (120, 122)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    # Corvian (3) — DS3: crow-people on rooftops near storyteller
    for tx, ty in [(125, 5), (130, 12), (135, 8)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Corvian", "Assassin"))]))
    # CorvianStoryteller (1) — DS3: storyteller with corvian group on rooftop
    entities.append(make_entity("Enemy", 128 * 16, 10 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CorvianStoryteller", "DarkMage"))]))
    # HollowSoldier (4) — DS3: hollow soldiers in barricades near Twin Princes
    for tx, ty in [(55, 135), (60, 138), (65, 132), (70, 136)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowSoldier", "HollowSoldier"))]))
    # MiniBoss (2)
    entities.append(make_entity("Enemy", 60 * 16, 110 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    entities.append(make_entity("Enemy", 64 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 76 * 16, 281 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Power Within")]))
    entities.append(make_entity("Item", 80 * 16, 280 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Soul Stream")]))
    entities.append(make_entity("Item", 105 * 16, 217 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Divine Pillars of Light")]))
    entities.append(make_entity("Item", 39 * 16, 341 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 97 * 16, 225 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 65 * 16, 280 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 126 * 16, 160 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 102 * 16, 220 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 70 * 16, 295 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 81 * 16, 280 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 65 * 16, 291 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 86 * 16, 282 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Avelyn")]))
    entities.append(make_entity("Item", 100 * 16, 221 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Golden Wing Crest Shield")]))
    entities.append(make_entity("Item", 102 * 16, 216 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Sage's Crystal Staff")]))
    entities.append(make_entity("Item", 105 * 16, 218 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Onikiri and Ubadachi")]))
    entities.append(make_entity("Item", 90 * 16, 222 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Crystal Chime")]))
    entities.append(make_entity("Item", 62 * 16, 323 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Crystal Scroll")]))
    entities.append(make_entity("Item", 74 * 16, 280 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Outrider Knight Armor Set")]))
    entities.append(make_entity("Item", 63 * 16, 288 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 67 * 16, 291 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 92 * 16, 223 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteChunk"),
        make_field("name", "String", "Titanite Chunk")]))
    entities.append(make_entity("Item", 72 * 16, 290 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 66 * 16, 280 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteScale"),
        make_field("name", "String", "Titanite Scale")]))
    entities.append(make_entity("Item", 136 * 16, 157 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteSlab"),
        make_field("name", "String", "Titanite Slab")]))
    entities.append(make_entity("Item", 116 * 16, 152 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Greirat's Ashes")]))
    entities.append(make_entity("Item", 102 * 16, 223 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Shriving Stone")]))
    entities.append(make_entity("Item", 126 * 16, 157 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Hollow Gem")]))
    entities.append(make_entity("Item", 113 * 16, 218 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Blessed Gem")]))
    entities.append(make_entity("Item", 68 * 16, 292 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 100 * 16, 218 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 111 * 16, 216 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Fleshbite Ring")]))
    entities.append(make_entity("Item", 109 * 16, 218 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Hunter's Ring")]))
    entities.append(make_entity("Item", 87 * 16, 278 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Scholar Ring")]))
    entities.append(make_entity("Item", 181 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Twin Princes")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 67 * 16, 280 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 97 * 16, 218 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 75 * 16, 286 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 115 * 16, 216 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 118 * 16, 218 * 16, [
        make_field("name", "String", "Unknown")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/GrandArchives.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("GrandArchives", chunk, entities, spawn_px, spawn_py)
