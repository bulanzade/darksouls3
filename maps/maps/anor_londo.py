from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_anor_londo():
    """Anor Londo - grand cathedral with Aldrich, Devourer of Gods boss.
    Faithful DS3 layout: entrance hall (rotating staircase) -> royal avenue ->
    Silver Knight hall (with Deep Accursed) -> staircase corridor ->
    Darkmoon Temple (Aldrich arena with abyss swamp). Side path to Yorshka's
    church via invisible platforms. DS1 nostalgia with faded golden grandeur.
    """
    chunk = new_chunk(224, 192)
    entities = []

    # === Cathedral entrance hall (west, from Irithyll rotating staircase) ===
    fill_tiles(chunk, TILE_GROUND, 6, 26, 40, 55)
    # High stone pillars (decorative wall obstacles)
    fill_tiles(chunk, TILE_WALL, 14, 32, 16, 38)
    fill_tiles(chunk, TILE_WALL, 26, 34, 28, 40)
    fill_tiles(chunk, TILE_WALL, 20, 46, 22, 50)

    # === Royal avenue (wide golden corridor east) ===
    fill_tiles(chunk, TILE_GROUND, 36, 30, 82, 58)
    # Knight statue pillars along the avenue
    fill_tiles(chunk, TILE_WALL, 48, 35, 50, 40)
    fill_tiles(chunk, TILE_WALL, 62, 42, 64, 47)
    fill_tiles(chunk, TILE_WALL, 74, 36, 76, 41)

    # === Yorshka side path (south from royal avenue) ===
    fill_tiles(chunk, TILE_GROUND, 52, 56, 68, 82)
    # Narrow invisible-platform-style path
    fill_tiles(chunk, TILE_GROUND, 56, 80, 72, 100)
    # Yorshka's church (hidden prayer room)
    carve_ellipse(chunk, 62, 92, 10, 8)
    fill_tiles(chunk, TILE_GROUND, 50, 82, 76, 104)

    # === Silver Knight hall (large council chamber) ===
    fill_tiles(chunk, TILE_GROUND, 78, 26, 118, 56)
    carve_ellipse(chunk, 98, 40, 14, 10)
    # Hall pillars
    fill_tiles(chunk, TILE_WALL, 86, 30, 88, 36)
    fill_tiles(chunk, TILE_WALL, 106, 38, 108, 44)

    # === Staircase corridor (Silver Knight gauntlet to boss) ===
    fill_tiles(chunk, TILE_GROUND, 114, 32, 142, 58)
    # Corridor walls creating narrow passage
    fill_tiles(chunk, TILE_WALL, 120, 34, 122, 38)
    fill_tiles(chunk, TILE_WALL, 132, 42, 134, 46)

    # === Darkmoon Temple / Aldrich arena (SE) ===
    fill_tiles(chunk, TILE_GROUND, 100, 55, 155, 110)
    carve_ellipse(chunk, 128, 82, 24, 20)
    # Dark stone floor in center of arena (DS3: no poison/swamp in Anor Londo)
    fill_tiles(chunk, TILE_GROUND, 116, 70, 140, 94)
    # Arena stone pillars
    fill_tiles(chunk, TILE_WALL, 108, 62, 110, 68)
    fill_tiles(chunk, TILE_WALL, 146, 88, 148, 94)
    fill_tiles(chunk, TILE_WALL, 122, 98, 124, 103)

    # === Connections ===
    # Entrance hall to Royal avenue (already adjacent at x=36-40)
    # Royal avenue to Silver Knight hall
    fill_tiles(chunk, TILE_GROUND, 78, 36, 82, 52)
    # Silver Knight hall to Staircase corridor
    fill_tiles(chunk, TILE_GROUND, 114, 38, 118, 52)
    # Staircase corridor down to Aldrich arena
    fill_tiles(chunk, TILE_GROUND, 136, 55, 144, 62)
    # Royal avenue south to Yorshka path
    fill_tiles(chunk, TILE_GROUND, 56, 55, 62, 62)

    # ================================================================
    # ADDITIONAL DS3 ANOR LONDO — cathedral grandeur, golden architecture
    # ================================================================
    # Cathedral entrance — more grand pillars (DS3: massive stone pillars in entry hall)
    fill_tiles(chunk, TILE_WALL, 10, 30, 12, 34)
    fill_tiles(chunk, TILE_WALL, 18, 42, 20, 46)
    fill_tiles(chunk, TILE_WALL, 30, 48, 32, 52)
    fill_tiles(chunk, TILE_WALL, 8, 40, 10, 44)
    fill_tiles(chunk, TILE_WALL, 34, 38, 36, 42)
    # Royal avenue — knight statue bases (DS3: statues line the golden corridor)
    fill_tiles(chunk, TILE_WALL, 42, 32, 44, 36)
    fill_tiles(chunk, TILE_WALL, 56, 44, 58, 48)
    fill_tiles(chunk, TILE_WALL, 68, 38, 70, 42)
    fill_tiles(chunk, TILE_WALL, 78, 46, 80, 50)
    fill_tiles(chunk, TILE_WALL, 54, 50, 56, 54)
    fill_tiles(chunk, TILE_WALL, 66, 52, 68, 56)
    # Yorshka side path — invisible platform debris (DS3: drop down to invisible bridge)
    fill_tiles(chunk, TILE_WALL, 54, 60, 56, 64)
    fill_tiles(chunk, TILE_WALL, 62, 76, 64, 80)
    fill_tiles(chunk, TILE_WALL, 58, 88, 60, 92)
    fill_tiles(chunk, TILE_WALL, 66, 96, 68, 100)
    # Silver Knight hall — display alcove walls (DS3: ornate chamber with paintings)
    fill_tiles(chunk, TILE_WALL, 82, 28, 84, 32)
    fill_tiles(chunk, TILE_WALL, 94, 34, 96, 38)
    fill_tiles(chunk, TILE_WALL, 102, 42, 104, 46)
    fill_tiles(chunk, TILE_WALL, 112, 32, 114, 36)
    fill_tiles(chunk, TILE_WALL, 90, 48, 92, 52)
    fill_tiles(chunk, TILE_WALL, 110, 44, 112, 48)
    # Staircase corridor — wall sconces and debris (DS3: Silver Knight gauntlet)
    fill_tiles(chunk, TILE_WALL, 116, 36, 118, 40)
    fill_tiles(chunk, TILE_WALL, 126, 38, 128, 42)
    fill_tiles(chunk, TILE_WALL, 136, 44, 138, 48)
    fill_tiles(chunk, TILE_WALL, 140, 52, 142, 56)
    # Aldrich arena — throne room pillars (DS3: Gwyndolin's chamber with abyss)
    fill_tiles(chunk, TILE_WALL, 104, 58, 106, 62)
    fill_tiles(chunk, TILE_WALL, 114, 66, 116, 70)
    fill_tiles(chunk, TILE_WALL, 136, 62, 138, 66)
    fill_tiles(chunk, TILE_WALL, 142, 78, 144, 82)
    fill_tiles(chunk, TILE_WALL, 128, 96, 130, 100)
    fill_tiles(chunk, TILE_WALL, 148, 92, 150, 96)
    fill_tiles(chunk, TILE_WALL, 120, 102, 122, 106)
    # Deep Accursed corner — web-covered debris (DS3: spider ambush in side room)
    fill_tiles(chunk, TILE_WALL, 96, 36, 98, 40)
    fill_tiles(chunk, TILE_WALL, 100, 44, 102, 48)

    # ================================================================
    # SESSION 9 FIDELITY PASS — AnorLondo architectural details
    # ================================================================
    # Main cathedral entrance — grand staircase debris (DS3: iconic Anor Londo steps)
    fill_tiles(chunk, TILE_WALL, 14, 40, 15, 41)
    fill_tiles(chunk, TILE_WALL, 18, 44, 19, 45)
    fill_tiles(chunk, TILE_WALL, 10, 48, 11, 49)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    fill_tiles(chunk, TILE_WALL, 16, 50, 17, 51)
    # Silver Knight hall — ornate pillar bases (DS3: massive pillars in great hall)
    fill_tiles(chunk, TILE_WALL, 28, 54, 29, 55)
    fill_tiles(chunk, TILE_WALL, 32, 58, 33, 59)
    fill_tiles(chunk, TILE_WALL, 24, 62, 25, 63)
    fill_tiles(chunk, TILE_WALL, 36, 52, 37, 53)
    fill_tiles(chunk, TILE_WALL, 30, 64, 31, 65)
    # Deacon corridor — burned banner stones (DS3: path to Aldrich with paintings)
    fill_tiles(chunk, TILE_WALL, 40, 68, 41, 69)
    fill_tiles(chunk, TILE_WALL, 44, 72, 45, 73)
    fill_tiles(chunk, TILE_WALL, 36, 76, 37, 77)
    fill_tiles(chunk, TILE_WALL, 48, 66, 49, 67)
    fill_tiles(chunk, TILE_WALL, 42, 78, 43, 79)
    # Gwyndolin chamber — illusion mirror fragments (DS3: Gwyndolin's chamber)
    fill_tiles(chunk, TILE_WALL, 52, 82, 53, 83)
    fill_tiles(chunk, TILE_WALL, 56, 86, 57, 87)
    fill_tiles(chunk, TILE_WALL, 48, 90, 49, 91)
    fill_tiles(chunk, TILE_WALL, 60, 80, 61, 81)
    fill_tiles(chunk, TILE_WALL, 54, 92, 55, 93)
    # Darkmoon Tomb — candle alcoves (DS3: Darkmoon covenant area)
    fill_tiles(chunk, TILE_WALL, 64, 96, 65, 97)
    fill_tiles(chunk, TILE_WALL, 68, 100, 69, 101)
    fill_tiles(chunk, TILE_WALL, 60, 104, 61, 105)
    fill_tiles(chunk, TILE_WALL, 72, 94, 73, 95)
    # Aldrich arena — consumed throne room debris (DS3: Gwyndolin consumed by Aldrich)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 126, 84, 127, 85)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 130, 78, 131, 79)
    fill_tiles(chunk, TILE_WALL, 122, 90, 123, 91)
    # Man Grub corridors — slime-coated wall stones (DS3: Man Grubs roam the halls)
    fill_tiles(chunk, TILE_WALL, 76, 60, 77, 61)
    fill_tiles(chunk, TILE_WALL, 80, 64, 81, 65)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 84, 58, 85, 59)
    fill_tiles(chunk, TILE_WALL, 78, 70, 79, 71)

    # ================================================================
    # SESSION 13 FIDELITY PASS — AnorLondo DS3 architecture
    # ================================================================
    # Rotating staircase mechanism — gear stones (DS3: mechanical staircase at entrance)
    fill_tiles(chunk, TILE_WALL, 8, 34, 9, 35)
    fill_tiles(chunk, TILE_WALL, 12, 36, 13, 37)
    fill_tiles(chunk, TILE_WALL, 6, 44, 7, 45)
    fill_tiles(chunk, TILE_WALL, 16, 38, 17, 39)
    fill_tiles(chunk, TILE_WALL, 24, 40, 25, 41)
    fill_tiles(chunk, TILE_WALL, 4, 48, 5, 49)
    # Silver Knight hall — banquet table remnants (DS3: long hall with knight statues)
    fill_tiles(chunk, TILE_WALL, 84, 40, 85, 41)
    fill_tiles(chunk, TILE_WALL, 88, 44, 89, 45)
    fill_tiles(chunk, TILE_WALL, 92, 38, 93, 39)
    fill_tiles(chunk, TILE_WALL, 96, 46, 97, 47)
    fill_tiles(chunk, TILE_WALL, 100, 36, 101, 37)
    fill_tiles(chunk, TILE_WALL, 108, 40, 109, 41)
    # Aldrich arena — half-sunken pillars (DS3: Gwyndolin's chamber sinking into abyss)
    fill_tiles(chunk, TILE_WALL, 110, 72, 111, 73)
    fill_tiles(chunk, TILE_WALL, 118, 76, 119, 77)
    fill_tiles(chunk, TILE_WALL, 124, 80, 125, 81)
    fill_tiles(chunk, TILE_WALL, 132, 74, 133, 75)
    fill_tiles(chunk, TILE_WALL, 138, 82, 139, 83)
    fill_tiles(chunk, TILE_WALL, 134, 90, 135, 91)
    fill_tiles(chunk, TILE_WALL, 140, 86, 141, 87)
    fill_tiles(chunk, TILE_WALL, 146, 80, 147, 81)
    # Yorshka's tower — bell tower stones (DS3: Darkmoon Tomb bell tower)
    fill_tiles(chunk, TILE_WALL, 58, 84, 59, 85)
    fill_tiles(chunk, TILE_WALL, 62, 88, 63, 89)
    fill_tiles(chunk, TILE_WALL, 66, 92, 67, 93)
    fill_tiles(chunk, TILE_WALL, 60, 96, 61, 97)
    fill_tiles(chunk, TILE_WALL, 64, 100, 65, 101)
    fill_tiles(chunk, TILE_WALL, 56, 98, 57, 99)
    # Deacon procession path — melted candle wax (DS3: Deacons of the Deep)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 63)
    fill_tiles(chunk, TILE_WALL, 90, 58, 91, 59)
    fill_tiles(chunk, TILE_WALL, 98, 64, 99, 65)
    fill_tiles(chunk, TILE_WALL, 106, 60, 107, 61)
    fill_tiles(chunk, TILE_WALL, 114, 66, 115, 67)
    # Prison tower — cage bars and chains (DS3: prison tower bonfire area)
    fill_tiles(chunk, TILE_WALL, 52, 70, 53, 71)
    fill_tiles(chunk, TILE_WALL, 56, 74, 57, 75)
    fill_tiles(chunk, TILE_WALL, 48, 78, 49, 79)
    fill_tiles(chunk, TILE_WALL, 64, 72, 65, 73)


    # ================================================================
    # DS3 STRUCTURAL WALLS — Anor Londo cathedral architecture
    # DS3: dark cathedral with grand staircase, silver knight halls,
    # invisible bridge, and Aldrich devourer arena
    # ================================================================
    # Grand staircase — wide stone steps (DS3: iconic Anor Londo staircase)
    fill_tiles(chunk, TILE_WALL, 48, 48, 52, 52)    # Staircase landing wall
    fill_tiles(chunk, TILE_WALL, 62, 52, 66, 56)    # Mid-staircase wall
    fill_tiles(chunk, TILE_WALL, 56, 56, 60, 60)    # Staircase pillar
    # Cathedral nave — massive column rows (DS3: dark cathedral with columns)
    fill_tiles(chunk, TILE_WALL, 80, 80, 84, 88)    # Nave pillar NW
    fill_tiles(chunk, TILE_WALL, 100, 80, 104, 88)  # Nave pillar NE
    fill_tiles(chunk, TILE_WALL, 80, 100, 84, 108)  # Nave pillar SW
    fill_tiles(chunk, TILE_WALL, 100, 100, 104, 108) # Nave pillar SE
    fill_tiles(chunk, TILE_WALL, 90, 90, 94, 98)    # Central nave column
    # Cathedral antechamber — hall divider walls (DS3: silver knight guard hall)
    fill_tiles(chunk, TILE_WALL, 120, 80, 124, 86)  # Hall divider left
    fill_tiles(chunk, TILE_WALL, 136, 80, 140, 86)  # Hall divider right
    fill_tiles(chunk, TILE_WALL, 128, 88, 132, 94)  # Central pillar
    # Gwyndolin hallway — narrow passage walls (DS3: dark corridor to Aldrich)
    fill_tiles(chunk, TILE_WALL, 140, 100, 144, 108) # Corridor wall left
    fill_tiles(chunk, TILE_WALL, 156, 100, 160, 108) # Corridor wall right
    fill_tiles(chunk, TILE_WALL, 148, 96, 152, 100)  # Corridor pillar
    # Aldrich arena — dark cathedral columns (DS3: massive dark boss arena)
    fill_tiles(chunk, TILE_WALL, 168, 110, 172, 118) # Arena pillar NW
    fill_tiles(chunk, TILE_WALL, 188, 110, 192, 118) # Arena pillar NE
    fill_tiles(chunk, TILE_WALL, 168, 130, 172, 138) # Arena pillar SW
    fill_tiles(chunk, TILE_WALL, 188, 130, 192, 138) # Arena pillar SE
    fill_tiles(chunk, TILE_WALL, 178, 120, 182, 128) # Arena center column
    # Prison tower — invisible bridge area walls (DS3: narrow beams over darkness)
    fill_tiles(chunk, TILE_WALL, 30, 90, 34, 96)    # Tower wall
    fill_tiles(chunk, TILE_WALL, 42, 94, 46, 100)   # Tower pillar
    # Rotating platform area — stone pillars (DS3: mechanism to reach Anor Londo)
    fill_tiles(chunk, TILE_WALL, 28, 42, 32, 48)    # Platform support wall
    fill_tiles(chunk, TILE_WALL, 40, 38, 44, 44)    # Platform pillar
        # --- Spawn from Irithyll rotating staircase ---
    spawn_px, spawn_py = 10 * 16, 38 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires --- DS3: Anor Londo, Prison Tower, Aldrich Devourer of Gods
    entities.append(make_entity("Bonfire", 61 * 16, 56 * 16))
    entities.append(make_entity("Bonfire", 33 * 16, 97 * 16))   # Prison Tower (invisible bridge area)
    entities.append(make_entity("Bonfire", 168 * 16, 131 * 16))  # Aldrich boss bonfire

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 168 * 16, 131 * 16))

    # --- Enemies — DS3 Anor Londo: Silver Knights, Giant Slave (archer),
    # Deep Accursed, Deacons (pyromancers + 3 before fog), Rotten Flesh of Aldrich (slimes)

    # --- Items — DS3 Anor Londo (wiki-verified) ---
    items = [
        # Top of stairs — left side (DS3: after climbing stairs past Silver Knights)
        ("SoulOrb", "Large Soul of a Weary Warrior", 18, 40, 1000),
        # Right side — red-eyed Silver Knight corpse (DS3: loot corpse)
        ("SoulOrb", "Soul of a Crestfallen Knight", 22, 42, 1000),
        # Dead giant blacksmith room (DS3: Giant's Coal in his hand)
        ("Consumable", "Giant's Coal", 26, 48, 0),
        # Main chamber — near pyromancers (DS3: corpse near fireball casters)
        ("Consumable", "Proof of a Concord Kept", 96, 48, 0),
        # Opposite staircase (DS3: corpse with Moonlight Arrow x5)
        ("Consumable", "Moonlight Arrow", 120, 60, 0),
        ("Consumable", "Moonlight Arrow", 121, 61, 0),
        ("Consumable", "Moonlight Arrow", 122, 60, 0),
        ("Consumable", "Moonlight Arrow", 120, 62, 0),
        ("Consumable", "Moonlight Arrow", 122, 62, 0),
        # Deep Accursed area near revolving platform (DS3: ring drop)
        ("RingDrop", "Aldrich's Ruby", 100, 50, 0),
        # Yorshka tower beam (DS3: drop down from invisible bridge)
        ("WeaponDrop", "Painting Guardian's Curved Sword", 58, 88, 0),
        # Below beam in tower (DS3: further drop)
        ("ArmorDrop", "Painting Guardian Set", 60, 94, 0),
        # Post-boss elevator — Gwynevere's chamber (DS3: after defeating Aldrich)
        ("RingDrop", "Sun Princess Ring", 130, 90, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    # --- Chests — DS3 Anor Londo (wiki-verified) ---

    
    # --- DS3 faithful enemies (AnorLondo) ---
    # SilverKnight (20)
    for tx, ty in [(20, 35), (34, 42), (42, 38), (52, 42), (64, 48), (48, 50), (70, 44), (82, 38), (90, 42), (108, 34), (118, 36), (55, 45), (68, 40), (70, 46), (125, 38), (135, 44), (138, 50), (28, 48), (58, 54), (65, 55)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SilverKnight", "SilverKnight"))]))
    # GiantSlave (1)
    entities.append(make_entity("Enemy", 38 * 16, 52 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))
    # ManGrub (18)
    for tx, ty in [(72, 52), (76, 48), (142, 75), (148, 82), (136, 68), (124, 88), (132, 92), (130, 65), (115, 72), (140, 95), (112, 80), (55, 85), (64, 91), (69, 93), (61, 101), (78, 52), (82, 58), (145, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ManGrub", "ManGrub"))]))
    # PaintingGuardian (3) — DS3: guardians near the painting room
    for tx, ty in [(88, 36), (92, 40), (96, 38)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Assassin", "Assassin"))]))
    # DeepAccursed (1)
    entities.append(make_entity("Enemy", 100 * 16, 40 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DeepAccursed", "DeepAccursed"))]))
    # CrystalLizard (1)
    entities.append(make_entity("Enemy", 56 * 16, 84 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # MiniBoss (1)
    entities.append(make_entity("Enemy", 128 * 16, 78 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- NPCs ---
    # Anri of Astora — summon sign near main doors (wiki: "purple sign on the floor")
    entities.append(make_entity("Npc", 171 * 16, 127 * 16, [
        make_field("name", "String", "Anri of Astora"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#d0d0ff"),
        make_field("dialogue", "String",
            "We meet at last, in this grand cathedral|Aldrich, Devourer of Gods, lies ahead|Will you help me defeat him, together?|I cannot do this alone"),
    ]))
    # Company Captain Yorshka — Darkmoon Tomb, reached from Prison Tower bonfire
    entities.append(make_entity("Npc", 36 * 16, 97 * 16, [
        make_field("name", "String", "Company Captain Yorshka"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#E0E8F0"),
        make_field("dialogue", "String",
            "I am Yorshka, Captain of the Darkmoon Knights|The Darkmoon remains true to its duty, even now|Will you swear the oath of the Darkmoon?|Then let us join hands, and take the oath"),
    ]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 52 * 16, 53 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 56 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Crestfallen Knight")]))
    entities.append(make_entity("Item", 60 * 16, 61 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Giant's Coal")]))
    entities.append(make_entity("Item", 135 * 16, 91 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Proof of a Concord Kept")]))
    entities.append(make_entity("Item", 161 * 16, 105 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Arrow"),
        make_field("name", "String", "Moonlight Arrow")]))
    entities.append(make_entity("Item", 163 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Arrow"),
        make_field("name", "String", "Moonlight Arrow")]))
    entities.append(make_entity("Item", 136 * 16, 95 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Aldrich's Ruby")]))
    entities.append(make_entity("Item", 86 * 16, 72 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Painting Guardian's Curved Sword")]))
    entities.append(make_entity("Item", 87 * 16, 77 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Painting Guardian Set")]))
    entities.append(make_entity("Item", 173 * 16, 137 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Sun Princess Ring")]))
    entities.append(make_entity("Item", 168 * 16, 132 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of Aldrich")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 165 * 16, 101 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    # Back to Irithyll (rotating staircase, west)
    entities.append(make_entity("FogGate", 61 * 16, 50 * 16, [
        make_field("dest_area", "String", "Irithyll"),
        make_field("dest_x", "Float", 2400.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # Cathedral entrance — faded golden
    entities.append(make_entity("Light", 10 * 16, 38 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.5)]))
    # Royal avenue — false sunlight
    entities.append(make_entity("Light", 60 * 16, 44 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.9),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    # Yorshka church — darkmoon blue
    entities.append(make_entity("Light", 62 * 16, 90 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.6),
        make_field("b", "Float", 1.0), make_field("intensity", "Float", 0.5)]))
    # Silver Knight hall — dim gold
    entities.append(make_entity("Light", 98 * 16, 40 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.9),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.35)]))
    # Deep Accursed lair — abyss purple
    entities.append(make_entity("Light", 100 * 16, 40 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.1),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.5)]))
    # Aldrich arena — dark abyss glow
    entities.append(make_entity("Light", 128 * 16, 82 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.6)]))

    # === ADDITIONAL INTERNAL STRUCTURES — AnorLondo cathedral ===
    # Cathedral entrance pillars
    fill_tiles(chunk, TILE_WALL, 18, 32, 20, 36)
    fill_tiles(chunk, TILE_WALL, 28, 28, 30, 32)
    # Royal avenue — stone pillars and silver knight positions
    fill_tiles(chunk, TILE_WALL, 42, 38, 44, 42)
    fill_tiles(chunk, TILE_WALL, 55, 35, 57, 39)
    fill_tiles(chunk, TILE_WALL, 68, 40, 70, 44)
    fill_tiles(chunk, TILE_WALL, 48, 48, 50, 52)
    fill_tiles(chunk, TILE_WALL, 62, 46, 64, 50)
    # Yorshka side path — church pews and altar stones
    fill_tiles(chunk, TILE_WALL, 58, 80, 60, 84)
    fill_tiles(chunk, TILE_WALL, 68, 85, 70, 88)
    fill_tiles(chunk, TILE_WALL, 52, 88, 54, 92)
    # Silver Knight hall — hall pillars
    fill_tiles(chunk, TILE_WALL, 92, 35, 94, 38)
    fill_tiles(chunk, TILE_WALL, 100, 38, 102, 42)
    fill_tiles(chunk, TILE_WALL, 108, 35, 110, 38)
    fill_tiles(chunk, TILE_WALL, 96, 44, 98, 48)
    # Staircase corridor — stone railings
    fill_tiles(chunk, TILE_WALL, 112, 52, 114, 55)
    fill_tiles(chunk, TILE_WALL, 118, 58, 120, 62)
    fill_tiles(chunk, TILE_WALL, 125, 65, 127, 68)
    # Aldrich arena — cathedral columns and debris
    fill_tiles(chunk, TILE_WALL, 118, 78, 120, 82)
    fill_tiles(chunk, TILE_WALL, 138, 82, 140, 86)
    fill_tiles(chunk, TILE_WALL, 128, 92, 130, 96)
    fill_tiles(chunk, TILE_WALL, 142, 88, 144, 92)
    fill_tiles(chunk, TILE_WALL, 132, 76, 134, 79)

    # === MORE ANOR LONDO DETAILS — DS3 fidelity ===
    # Cathedral entrance — grand archway stones (DS3: massive cathedral doors)
    fill_tiles(chunk, TILE_WALL, 8, 28, 10, 32)
    fill_tiles(chunk, TILE_WALL, 32, 42, 34, 46)
    fill_tiles(chunk, TILE_WALL, 24, 50, 26, 54)
    fill_tiles(chunk, TILE_WALL, 36, 48, 38, 52)
    # Royal avenue — more decorative pillars (DS3: avenue lined with columns)
    fill_tiles(chunk, TILE_WALL, 44, 34, 46, 37)
    fill_tiles(chunk, TILE_WALL, 58, 38, 60, 41)
    fill_tiles(chunk, TILE_WALL, 70, 35, 72, 38)
    fill_tiles(chunk, TILE_WALL, 52, 52, 54, 55)
    fill_tiles(chunk, TILE_WALL, 66, 50, 68, 53)
    fill_tiles(chunk, TILE_WALL, 76, 45, 78, 48)
    # Silver Knight hall — council chamber details (DS3: large hall with paintings)
    fill_tiles(chunk, TILE_WALL, 82, 32, 84, 35)
    fill_tiles(chunk, TILE_WALL, 90, 45, 92, 48)
    fill_tiles(chunk, TILE_WALL, 104, 42, 106, 45)
    fill_tiles(chunk, TILE_WALL, 112, 38, 114, 41)
    fill_tiles(chunk, TILE_WALL, 95, 48, 97, 51)
    # Staircase corridor — more railing sections (DS3: narrow staircase with Silver Knights)
    fill_tiles(chunk, TILE_WALL, 116, 35, 118, 38)
    fill_tiles(chunk, TILE_WALL, 124, 40, 126, 43)
    fill_tiles(chunk, TILE_WALL, 130, 45, 132, 48)
    fill_tiles(chunk, TILE_WALL, 136, 50, 138, 53)
    # Aldrich arena — more cathedral columns (DS3: Gwynevere's chamber, massive pillars)
    fill_tiles(chunk, TILE_WALL, 105, 70, 107, 74)
    fill_tiles(chunk, TILE_WALL, 115, 65, 117, 68)
    fill_tiles(chunk, TILE_WALL, 145, 75, 147, 78)
    fill_tiles(chunk, TILE_WALL, 150, 85, 152, 88)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 98)
    fill_tiles(chunk, TILE_WALL, 120, 85, 122, 88)
    # Yorshka path — more invisible platform stones (DS3: narrow drop-down path)
    fill_tiles(chunk, TILE_WALL, 54, 78, 56, 80)
    fill_tiles(chunk, TILE_WALL, 64, 82, 66, 84)
    fill_tiles(chunk, TILE_WALL, 60, 92, 62, 94)
    fill_tiles(chunk, TILE_WALL, 70, 90, 72, 92)
    # Additional Anor Londo DS3 details
    # Cathedral entrance — more grand archway stones (DS3: massive doors to Anor Londo)
    fill_tiles(chunk, TILE_WALL, 14, 36, 16, 39)
    fill_tiles(chunk, TILE_WALL, 22, 42, 24, 45)
    # Deacon corridor walls (DS3: deacons line the path to the cathedral)
    fill_tiles(chunk, TILE_WALL, 38, 55, 40, 58)
    fill_tiles(chunk, TILE_WALL, 46, 60, 48, 63)
    # Royal avenue — stone bench debris (DS3: ruined avenue with Silver Knight patrols)
    fill_tiles(chunk, TILE_WALL, 50, 44, 52, 46)
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 54)
    # Silver Knight hall — display alcoves (DS3: paintings and armor displays)
    fill_tiles(chunk, TILE_WALL, 86, 48, 88, 50)
    fill_tiles(chunk, TILE_WALL, 102, 36, 104, 38)
    # Deep Accursed corner — web-covered debris (DS3: spider-like enemy lurks in corner)
    fill_tiles(chunk, TILE_WALL, 96, 42, 98, 44)
    fill_tiles(chunk, TILE_WALL, 108, 44, 110, 46)
    # Aldrich arena — more throne room pillars (DS3: Gwyndolin's chamber with massive columns)
    fill_tiles(chunk, TILE_WALL, 122, 80, 124, 83)
    fill_tiles(chunk, TILE_WALL, 148, 90, 150, 93)
    fill_tiles(chunk, TILE_WALL, 140, 78, 142, 80)
    fill_tiles(chunk, TILE_WALL, 115, 90, 117, 92)
    # Yorshka's church — altar and nave walls (DS3: Darkmoon Tomb)
    fill_tiles(chunk, TILE_WALL, 48, 84, 50, 86)
    fill_tiles(chunk, TILE_WALL, 66, 88, 68, 90)
    fill_tiles(chunk, TILE_WALL, 56, 94, 58, 96)

    # === SESSION 8 FIDELITY PASS — Anor Londo ===
    # Cathedral entrance — grand staircase debris (DS3: massive steps to cathedral doors)
    fill_tiles(chunk, TILE_WALL, 10, 38, 11, 40)
    fill_tiles(chunk, TILE_WALL, 18, 40, 19, 42)
    fill_tiles(chunk, TILE_WALL, 8, 32, 9, 34)
    # Deacon corridor — burned banners and ash (DS3: corrupted passage to Aldrich)
    fill_tiles(chunk, TILE_WALL, 34, 52, 35, 54)
    fill_tiles(chunk, TILE_WALL, 42, 58, 43, 60)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 58)
    fill_tiles(chunk, TILE_WALL, 30, 60, 31, 62)
    # Royal avenue — collapsed archway stones (DS3: grand avenue with Silver Knights)
    fill_tiles(chunk, TILE_WALL, 56, 40, 57, 42)
    fill_tiles(chunk, TILE_WALL, 68, 48, 69, 50)
    fill_tiles(chunk, TILE_WALL, 62, 50, 63, 52)
    fill_tiles(chunk, TILE_WALL, 76, 44, 77, 46)
    # Silver Knight hall — ornate pillar bases (DS3: grand hall with mounted banners)
    fill_tiles(chunk, TILE_WALL, 82, 50, 83, 52)
    fill_tiles(chunk, TILE_WALL, 94, 46, 95, 48)
    fill_tiles(chunk, TILE_WALL, 88, 54, 89, 56)
    fill_tiles(chunk, TILE_WALL, 100, 40, 101, 42)
    # Gwyndolin chamber — illusion-shattered mirror fragments (DS3: Aldrich's lair)
    fill_tiles(chunk, TILE_WALL, 118, 84, 119, 86)
    fill_tiles(chunk, TILE_WALL, 144, 86, 145, 88)
    fill_tiles(chunk, TILE_WALL, 130, 92, 131, 94)
    fill_tiles(chunk, TILE_WALL, 138, 76, 139, 78)
    # Darkmoon Tomb — candle alcoves and prayer stones (DS3: hidden covenant area)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 90)
    fill_tiles(chunk, TILE_WALL, 62, 82, 63, 84)
    fill_tiles(chunk, TILE_WALL, 52, 90, 53, 92)
    fill_tiles(chunk, TILE_WALL, 70, 92, 71, 94)
    # SESSION 10 FIDELITY PASS — Anor Londo
    # Additional DS3-faithful terrain: grand staircase debris, silver knight hall
    # pillars, Gwyndolin mirror fragments, Darkmoon candle clusters, Aldrich arena
    # Grand staircase — step debris (DS3: iconic grand staircase with broken steps)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 29)
    fill_tiles(chunk, TILE_WALL, 38, 32, 39, 33)
    fill_tiles(chunk, TILE_WALL, 44, 30, 45, 31)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 35)
    fill_tiles(chunk, TILE_WALL, 56, 32, 57, 33)
    # Silver Knight hall — pillar bases (DS3: pillars in great hall)
    fill_tiles(chunk, TILE_WALL, 62, 38, 63, 39)
    fill_tiles(chunk, TILE_WALL, 68, 42, 69, 43)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 45)
    fill_tiles(chunk, TILE_WALL, 70, 40, 71, 41)
    fill_tiles(chunk, TILE_WALL, 66, 36, 67, 37)
    # Gwyndolin chamber — mirror fragments (DS3: Dark Sun Gwyndolin's chamber)
    fill_tiles(chunk, TILE_WALL, 76, 48, 77, 49)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 53)
    fill_tiles(chunk, TILE_WALL, 78, 54, 79, 55)
    fill_tiles(chunk, TILE_WALL, 84, 50, 85, 51)
    # Darkmoon chamber — candle clusters (DS3: Darkmoon chamber with candles)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    fill_tiles(chunk, TILE_WALL, 94, 60, 95, 61)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 63)
    fill_tiles(chunk, TILE_WALL, 96, 58, 97, 59)
    # Aldrich arena — cathedral debris (DS3: Aldrich's cathedral arena)
    fill_tiles(chunk, TILE_WALL, 100, 66, 101, 67)
    fill_tiles(chunk, TILE_WALL, 106, 70, 107, 71)
    fill_tiles(chunk, TILE_WALL, 102, 72, 103, 73)
    fill_tiles(chunk, TILE_WALL, 108, 68, 109, 69)
    fill_tiles(chunk, TILE_WALL, 104, 64, 105, 65)
    fill_tiles(chunk, TILE_WALL, 110, 72, 111, 73)
    # Deacon corridor — cathedral stones (DS3: Deacons patrol corridors)
    fill_tiles(chunk, TILE_WALL, 114, 76, 115, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 118, 78, 119, 79)
    fill_tiles(chunk, TILE_WALL, 124, 82, 125, 83)
    # Man Grub area — ooze debris (DS3: Man Grubs in cathedral corridors)
    fill_tiles(chunk, TILE_WALL, 36, 36, 37, 37)
    fill_tiles(chunk, TILE_WALL, 42, 40, 43, 41)
    fill_tiles(chunk, TILE_WALL, 48, 38, 49, 39)
    fill_tiles(chunk, TILE_WALL, 54, 42, 55, 43)
    # Exterior — silver knight roof debris (DS3: knights patrol rooftops)
    fill_tiles(chunk, TILE_WALL, 128, 84, 129, 85)
    fill_tiles(chunk, TILE_WALL, 134, 88, 135, 89)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 87)

    # ================================================================
    # SESSION 15 FIDELITY PASS — AnorLondo additional DS3 details
    # ================================================================
    # Cathedral main hall — golden throne pillars (DS3: grand golden cathedral)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 16, 38, 17, 39)
    fill_tiles(chunk, TILE_WALL, 34, 34, 35, 35)
    # Silver Knight gauntlet — hall pillar bases (DS3: ornate hall with knights)
    fill_tiles(chunk, TILE_WALL, 86, 30, 87, 31)
    fill_tiles(chunk, TILE_WALL, 92, 34, 93, 35)
    fill_tiles(chunk, TILE_WALL, 80, 32, 81, 33)
    fill_tiles(chunk, TILE_WALL, 98, 28, 99, 29)
    # Yorshka tower — invisible bridge supports (DS3: invisible bridge to tower)
    fill_tiles(chunk, TILE_WALL, 50, 66, 51, 67)
    fill_tiles(chunk, TILE_WALL, 56, 70, 57, 71)
    fill_tiles(chunk, TILE_WALL, 44, 68, 45, 69)
    # Darkmoon Tomb — candle alcove stones (DS3: covenant area below cathedral)
    fill_tiles(chunk, TILE_WALL, 62, 78, 63, 79)
    fill_tiles(chunk, TILE_WALL, 68, 82, 69, 83)
    fill_tiles(chunk, TILE_WALL, 58, 80, 59, 81)
    # Aldrich arena approach — Gwyndolin's throne debris (DS3: throne room of Anor Londo)
    fill_tiles(chunk, TILE_WALL, 132, 74, 133, 75)
    fill_tiles(chunk, TILE_WALL, 138, 78, 139, 79)
    fill_tiles(chunk, TILE_WALL, 126, 76, 127, 77)

    # ================================================================
    # SESSION 17 FIDELITY PASS — AnorLondo DS3 cathedral details
    # ================================================================
    # Main cathedral hall — gothic column bases (DS3: grand cathedral with massive columns)
    fill_tiles(chunk, TILE_WALL, 28, 42, 29, 44)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 50)
    fill_tiles(chunk, TILE_WALL, 44, 44, 45, 46)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 52)
    fill_tiles(chunk, TILE_WALL, 60, 46, 61, 48)
    # Silver Knight gallery — weapon rack alcoves (DS3: knights patrol the gallery)
    fill_tiles(chunk, TILE_WALL, 68, 54, 69, 56)
    fill_tiles(chunk, TILE_WALL, 76, 58, 77, 60)
    fill_tiles(chunk, TILE_WALL, 84, 52, 85, 54)
    fill_tiles(chunk, TILE_WALL, 92, 56, 93, 58)
    # Man Grub chambers — slime puddle debris (DS3: slimes throughout the cathedral)
    fill_tiles(chunk, TILE_WALL, 100, 60, 101, 62)
    fill_tiles(chunk, TILE_WALL, 108, 64, 109, 66)
    fill_tiles(chunk, TILE_WALL, 116, 58, 117, 60)
    fill_tiles(chunk, TILE_WALL, 124, 62, 125, 64)
    # Yorshka's tower — invisible bridge supports (DS3: invisible bridge to tower)
    fill_tiles(chunk, TILE_WALL, 48, 82, 49, 84)
    fill_tiles(chunk, TILE_WALL, 56, 88, 57, 90)
    fill_tiles(chunk, TILE_WALL, 42, 90, 43, 92)
    # Aldrich cathedral — stained glass debris (DS3: broken stained glass windows)
    fill_tiles(chunk, TILE_WALL, 132, 70, 133, 72)
    fill_tiles(chunk, TILE_WALL, 140, 74, 141, 76)
    fill_tiles(chunk, TILE_WALL, 148, 70, 149, 72)
    fill_tiles(chunk, TILE_WALL, 144, 80, 145, 82)

    # ================================================================
    # SESSION 19 FIDELITY PASS — AnorLondo DS3 cathedral depth
    # ================================================================
    # Main hall — additional column debris (DS3: massive gothic cathedral interior)
    fill_tiles(chunk, TILE_WALL, 32, 56, 33, 58)
    fill_tiles(chunk, TILE_WALL, 40, 62, 41, 64)
    fill_tiles(chunk, TILE_WALL, 48, 58, 49, 60)
    fill_tiles(chunk, TILE_WALL, 56, 64, 57, 66)
    fill_tiles(chunk, TILE_WALL, 64, 60, 65, 62)
    # Silver Knight archer posts — parapet stones (DS3: archers on cathedral ledges)
    fill_tiles(chunk, TILE_WALL, 108, 48, 109, 50)
    fill_tiles(chunk, TILE_WALL, 116, 52, 117, 54)
    fill_tiles(chunk, TILE_WALL, 124, 48, 125, 50)
    fill_tiles(chunk, TILE_WALL, 132, 54, 133, 56)
    fill_tiles(chunk, TILE_WALL, 140, 50, 141, 52)
    # Giant's chamber — chain and anchor debris (DS3: giants in the cathedral)
    fill_tiles(chunk, TILE_WALL, 72, 66, 73, 68)
    fill_tiles(chunk, TILE_WALL, 80, 70, 81, 72)
    fill_tiles(chunk, TILE_WALL, 88, 66, 89, 68)
    fill_tiles(chunk, TILE_WALL, 96, 72, 97, 74)
    fill_tiles(chunk, TILE_WALL, 104, 68, 105, 70)

    # ================================================================
    # SESSION 22 FIDELITY PASS — AnorLondo DS3 cathedral details
    # ================================================================
    # Silver Knight statue bases (DS3: ornate statues lining the cathedral hall)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 29)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 33)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 40, 40, 41, 41)
    # Painting frame debris (DS3: paintings along the cathedral walls)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 45)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 56, 65, 57)
    # Aldrich cathedral debris (DS3: debris from Aldrich's chamber)
    fill_tiles(chunk, TILE_WALL, 70, 60, 71, 61)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    fill_tiles(chunk, TILE_WALL, 82, 68, 83, 69)
    fill_tiles(chunk, TILE_WALL, 88, 72, 89, 73)
    # Man Grub slime pools (DS3: grub trails on the cathedral floor)
    fill_tiles(chunk, TILE_WALL, 30, 68, 31, 69)
    fill_tiles(chunk, TILE_WALL, 36, 72, 37, 73)
    fill_tiles(chunk, TILE_WALL, 42, 76, 43, 77)
    fill_tiles(chunk, TILE_WALL, 48, 80, 49, 81)

    # ================================================================
    # SESSION 25 FIDELITY PASS — AnorLondo DS3 cathedral details
    # ================================================================
    # Ornstein's armor display (DS3: Ornstein's empty armor on display)
    fill_tiles(chunk, TILE_WALL, 118, 78, 119, 79)
    fill_tiles(chunk, TILE_WALL, 124, 82, 125, 83)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 87)
    fill_tiles(chunk, TILE_WALL, 136, 90, 137, 91)
    # Cathedral window frame debris (DS3: broken stained glass windows)
    fill_tiles(chunk, TILE_WALL, 142, 94, 143, 95)
    fill_tiles(chunk, TILE_WALL, 148, 98, 149, 99)
    fill_tiles(chunk, TILE_WALL, 140, 102, 141, 103)
    fill_tiles(chunk, TILE_WALL, 134, 106, 135, 107)
    # Aldrich's slime trails (DS3: Aldrich's slug trails on the floor)
    fill_tiles(chunk, TILE_WALL, 128, 110, 129, 111)
    fill_tiles(chunk, TILE_WALL, 122, 114, 123, 115)
    fill_tiles(chunk, TILE_WALL, 116, 118, 117, 119)
    fill_tiles(chunk, TILE_WALL, 110, 122, 111, 123)

    # ================================================================
    # SESSION 30 FIDELITY PASS — AnorLondo DS3 cathedral details
    # ================================================================
    # Cathedral stained glass debris (DS3: broken stained glass windows)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    # Silver Knight barracks (DS3: knight quarters along the corridors)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    # Aldrich's cathedral throne debris (DS3: Gwyndolin's throne room)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    # Painting room frame (DS3: frame for the painted world painting)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)

    # ================================================================
    # SESSION 33 FIDELITY PASS — AnorLondo DS3 cathedral details
    # ================================================================
    # Cathedral nave arch stones (DS3: stone arches in the main nave)
    fill_tiles(chunk, TILE_WALL, 16, 34, 17, 35)
    fill_tiles(chunk, TILE_WALL, 22, 38, 23, 39)
    fill_tiles(chunk, TILE_WALL, 28, 42, 29, 43)
    fill_tiles(chunk, TILE_WALL, 34, 46, 35, 47)
    # Silver Knight statue pedestals (DS3: pedestals for knight statues)
    fill_tiles(chunk, TILE_WALL, 40, 50, 41, 51)
    fill_tiles(chunk, TILE_WALL, 46, 54, 47, 55)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 59)
    fill_tiles(chunk, TILE_WALL, 58, 62, 59, 63)
    # Gwyndolin's throne room (DS3: throne room where Aldrich resides)
    fill_tiles(chunk, TILE_WALL, 64, 66, 65, 67)
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 71)
    fill_tiles(chunk, TILE_WALL, 76, 74, 77, 75)
    fill_tiles(chunk, TILE_WALL, 82, 78, 83, 79)
    # Painting guardian area (DS3: area near the painted world painting)
    fill_tiles(chunk, TILE_WALL, 88, 82, 89, 83)
    fill_tiles(chunk, TILE_WALL, 94, 86, 95, 87)
    fill_tiles(chunk, TILE_WALL, 100, 90, 101, 91)
    fill_tiles(chunk, TILE_WALL, 106, 94, 107, 95)

    # SESSION 41 FIDELITY PASS — Anor Londo DS3 details
    # DS3: Grand hall columns, painting room frame, Aldrich chamber debris
    for tx in range(20, 55, 5):
        fill_tiles(chunk, TILE_WALL, tx, 38, tx+2, 40)             # Grand hall columns
        fill_tiles(chunk, TILE_WALL, tx, 78, tx+2, 80)
    for tx in range(60, 95, 5):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+1, 43)             # Corridor arch stones
        fill_tiles(chunk, TILE_WALL, tx, 82, tx+1, 83)
    for ty in range(30, 65, 7):
        fill_tiles(chunk, TILE_WALL, 35, ty, 36, ty+1)             # Interior buttresses
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)                    # Painting room frame
    fill_tiles(chunk, TILE_WALL, 115, 55, 117, 57)                  # Aldrich chamber debris
    fill_tiles(chunk, TILE_WALL, 75, 90, 77, 92)                    # Silver Knight post
    for tx in range(120, 145, 6):
        fill_tiles(chunk, TILE_WALL, tx, 48, tx+1, 49)             # Cathedral exterior
    # --- SESSION 48 terrain (Anor Londo) ---
    # DS3: Silver Knight statues flanking the main hall
    for ty in range(20, 28):
        chunk[ty][30] = TILE_WALL  # statue base
        chunk[ty][50] = TILE_WALL  # statue base
    # Painting frames on the walls (DS3: the painted world painting)
    for ty in range(35, 42):
        chunk[ty][65] = TILE_WALL  # painting frame
    # Great Hall interior columns (DS3: the massive hall has stone columns)
    for ty in range(25, 35):
        chunk[ty][40] = TILE_WALL  # column
        chunk[ty][55] = TILE_WALL  # column
    # Balcony railing along the second floor
    for tx in range(70, 82):
        chunk[22][tx] = TILE_WALLTOP  # railing stone
    # Gwyndolin's fog corridor pillars (DS3: the corridor to the boss)
    for ty in range(45, 52):
        chunk[ty][80] = TILE_WALL  # corridor pillar

    # --- SESSION 53 terrain (Anor Londo final) ---
    # DS3: Ornstein's throne alcove (DS3: empty throne where Ornstein sat)
    for ty in range(55, 60):
        chunk[ty][85] = TILE_WALL  # throne alcove wall
    # Great Hall chandelier debris (DS3: fallen chandeliers)
    for tx in range(35, 42):
        chunk[30][tx] = TILE_WALLTOP  # chandelier debris
    # Man Grub slime trails (DS3: trails near Rosaria's chamber)
    for tx in range(58, 65):
        chunk[42][tx] = TILE_WALLTOP  # slime trail
    # Silver Knight training dummy (DS3: dummies in the practice hall)
    chunk[48][60] = TILE_WALLTOP  # training debris
    chunk[48][62] = TILE_WALLTOP  # training debris

    # --- SESSION 88 DS3 terrain (Anor Londo detail pass) ---
    # DS3: Grand hall columns (massive stone pillars)
    for tx in [20, 30, 40, 50, 60, 70, 80]:
        for ty in range(15, 30):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Knight statues lining the hall
    for tx in [22, 28, 32, 38, 42, 48, 52, 58, 62, 68, 72, 78]:
        for ty in [12, 13]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Painting frame (the iconic painting of Ariamis)
    for tx in range(35, 45):
        for ty in [8, 14]:
            chunk[tx][ty] = TILE_WALL
    for tx in [35, 45]:
        for ty in range(8, 15):
            chunk[tx][ty] = TILE_WALL
    for tx in range(35, 46):
        chunk[tx][7] = TILE_WALLTOP
    # DS3: Balcony railing along the upper level
    for tx in range(15, 85):
        chunk[tx][32] = TILE_WALL
        chunk[tx][31] = TILE_WALLTOP
    # DS3: Darkmoon tomb (hidden room)
    for tx in range(60, 75):
        for ty in [38, 48]:
            chunk[tx][ty] = TILE_WALL
    for tx in [60, 75]:
        for ty in range(38, 49):
            chunk[tx][ty] = TILE_WALL
    for tx in range(60, 76):
        chunk[tx][37] = TILE_WALLTOP
    # DS3: Fog corridor pillars
    for tx in [90, 95, 100, 105, 110]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][19] = TILE_WALLTOP
    # DS3: Main hall floor (open area)
    for tx in range(18, 82):
        for ty in range(33, 38):
            chunk[tx][ty] = TILE_GROUND

    # --- SESSION 92 DS3 terrain round 2 (Anor Londo) ---
    # DS3: Grand staircase entrance
    for tx in range(15, 30):
        for ty in range(35, 42):
            chunk[tx][ty] = TILE_GROUND
    for tx in [15, 30]:
        for ty in range(35, 43):
            chunk[tx][ty] = TILE_WALL
    # DS3: Silver Knight patrol alcoves
    for tx in [22, 32, 42, 52, 62]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Man-Grub chambers (side rooms)
    for tx in range(35, 45):
        for ty in [42, 48]:
            chunk[tx][ty] = TILE_WALL
    for tx in [35, 45]:
        for ty in range(42, 49):
            chunk[tx][ty] = TILE_WALL
    for tx in range(35, 46):
        chunk[tx][41] = TILE_WALLTOP
    # DS3: Giant Slave archer platform
    for tx in range(75, 85):
        for ty in [10, 15]:
            chunk[tx][ty] = TILE_WALL
    for tx in [75, 85]:
        for ty in range(10, 16):
            chunk[tx][ty] = TILE_WALL
    for tx in range(75, 86):
        chunk[tx][9] = TILE_WALLTOP
    # DS3: Aldrich's chamber (cathedral interior)
    for tx in range(50, 70):
        for ty in [50, 58]:
            chunk[tx][ty] = TILE_WALL
    for tx in [50, 70]:
        for ty in range(50, 59):
            chunk[tx][ty] = TILE_WALL
    for tx in range(50, 71):
        chunk[tx][49] = TILE_WALLTOP
    # DS3: Painting guardian room (above the painting)
    for tx in range(80, 95):
        for ty in [25, 30]:
            chunk[tx][ty] = TILE_WALL
    for tx in [80, 95]:
        for ty in range(25, 31):
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/AnorLondo.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("AnorLondo", chunk, entities, spawn_px, spawn_py)
