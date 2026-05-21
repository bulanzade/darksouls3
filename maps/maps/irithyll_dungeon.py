from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_irithyll_dungeon():
    """Irithyll Dungeon - dark prison with jailers, Siegward's cell, Karla's cell.
    No boss. Tight corridors with cell walls creating a maze-like layout.
    Design doc: 3200x2800, spiral prison descending underground.
    """
    chunk = new_chunk(256, 288)
    entities = []

    # ================================================================
    # SECTION 1: Underground passage entry - doc: x=0,y=0,w=600,h=600
    # Damp stone corridor from Irithyll, two jailers patrol
    # ================================================================
    carve_ellipse(chunk, 15, 15, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 10, 30, 28)

    # ================================================================
    # SECTION 2: Upper cell block - wide corridor with cells
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 15, 25, 65, 45)
    # Cell walls creating prison cells
    fill_tiles(chunk, TILE_WALL, 25, 28, 27, 35)
    fill_tiles(chunk, TILE_WALL, 40, 28, 42, 35)
    fill_tiles(chunk, TILE_WALL, 55, 28, 57, 35)

    # ================================================================
    # SECTION 3: Central cell block - main hub with tight passages
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 25, 45, 80, 72)
    carve_ellipse(chunk, 52, 58, 14, 12)
    # More cell walls
    fill_tiles(chunk, TILE_WALL, 35, 50, 37, 57)
    fill_tiles(chunk, TILE_WALL, 50, 50, 52, 57)
    fill_tiles(chunk, TILE_WALL, 65, 50, 67, 57)

    # ================================================================
    # SECTION 4: Siegward's cell (east side)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 80, 50, 105, 68)
    carve_ellipse(chunk, 92, 58, 8, 6)
    fill_tiles(chunk, TILE_WALL, 85, 54, 87, 58)

    # ================================================================
    # SECTION 5: Lower drain / rat tunnels
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 72, 70, 95)
    fill_tiles(chunk, TILE_WALL, 30, 78, 32, 82)
    fill_tiles(chunk, TILE_WALL, 50, 85, 52, 89)

    # ================================================================
    # SECTION 6: Karla's cell (deep southeast)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 75, 78, 105, 95)
    carve_ellipse(chunk, 90, 86, 8, 6)
    fill_tiles(chunk, TILE_WALL, 82, 82, 84, 86)

    # ================================================================
    # SECTION 7: Exit corridor to Profaned Capital (upper right)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 105, 25, 145, 42)
    carve_ellipse(chunk, 135, 32, 8, 8)
    fill_tiles(chunk, TILE_WALL, 118, 28, 120, 35)

    # ================================================================
    # SECTION 8: Gargoyle tower (connection upper to exit)
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 35, 110, 48)

    # Connection corridors (widened for DS3 route connectivity)
    fill_tiles(chunk, TILE_GROUND, 40, 40, 58, 50)    # Upper to central (wide)
    fill_tiles(chunk, TILE_GROUND, 48, 65, 70, 80)    # Central to lower (wide)
    fill_tiles(chunk, TILE_GROUND, 65, 70, 85, 82)    # Lower to Karla (wide)
    fill_tiles(chunk, TILE_GROUND, 95, 42, 115, 52)   # Siegward to tower (wide)
    fill_tiles(chunk, TILE_GROUND, 100, 32, 120, 42)  # Tower to exit (wide)
    # Additional Irithyll connections for full route connectivity
    fill_tiles(chunk, TILE_GROUND, 20, 25, 40, 48)    # Entry to upper cells
    fill_tiles(chunk, TILE_GROUND, 60, 80, 75, 95)    # Central to lower sewers
    fill_tiles(chunk, TILE_GROUND, 30, 95, 50, 105)   # Lower sewers to dark room

    # ================================================================
    # ADDITIONAL DS3 IRITHYLL DUNGEON — cell walls, prison architecture
    # ================================================================
    # Entry passage — dripping water and broken masonry (DS3: damp stone corridor)
    fill_tiles(chunk, TILE_WALL, 10, 12, 12, 14)
    fill_tiles(chunk, TILE_WALL, 22, 16, 24, 18)
    fill_tiles(chunk, TILE_WALL, 16, 22, 18, 24)
    fill_tiles(chunk, TILE_WALL, 28, 20, 30, 22)
    # Upper cell block — additional cell dividers (DS3: many small cells with jailers)
    fill_tiles(chunk, TILE_WALL, 20, 30, 22, 34)
    fill_tiles(chunk, TILE_WALL, 32, 32, 34, 36)
    fill_tiles(chunk, TILE_WALL, 45, 30, 47, 34)
    fill_tiles(chunk, TILE_WALL, 58, 32, 60, 36)
    fill_tiles(chunk, TILE_WALL, 62, 38, 64, 42)
    # Central cell block — watchtower supports and cell partitions (DS3: multi-level prison)
    fill_tiles(chunk, TILE_WALL, 30, 48, 32, 52)
    fill_tiles(chunk, TILE_WALL, 42, 52, 44, 56)
    fill_tiles(chunk, TILE_WALL, 58, 55, 60, 58)
    fill_tiles(chunk, TILE_WALL, 70, 52, 72, 55)
    fill_tiles(chunk, TILE_WALL, 48, 62, 50, 65)
    fill_tiles(chunk, TILE_WALL, 62, 65, 64, 68)
    fill_tiles(chunk, TILE_WALL, 75, 58, 77, 62)
    # Siegward's cell — cell bars and chain hooks (DS3: Siegward trapped behind bars)
    fill_tiles(chunk, TILE_WALL, 88, 52, 90, 55)
    fill_tiles(chunk, TILE_WALL, 95, 62, 97, 65)
    fill_tiles(chunk, TILE_WALL, 82, 58, 84, 60)
    # Lower drain — tunnel walls and grates (DS3: flooded drain tunnels with rats)
    fill_tiles(chunk, TILE_WALL, 25, 75, 27, 78)
    fill_tiles(chunk, TILE_WALL, 40, 80, 42, 82)
    fill_tiles(chunk, TILE_WALL, 55, 88, 57, 90)
    fill_tiles(chunk, TILE_WALL, 35, 90, 37, 92)
    fill_tiles(chunk, TILE_WALL, 60, 75, 62, 78)
    fill_tiles(chunk, TILE_WALL, 48, 92, 50, 94)
    # Karla's cell — dark alcove walls (DS3: Karla imprisoned behind illusory wall)
    fill_tiles(chunk, TILE_WALL, 78, 80, 80, 84)
    fill_tiles(chunk, TILE_WALL, 88, 88, 90, 92)
    fill_tiles(chunk, TILE_WALL, 95, 82, 97, 85)
    # Exit corridor — stone arch supports (DS3: path to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 110, 28, 112, 32)
    fill_tiles(chunk, TILE_WALL, 125, 30, 127, 34)
    fill_tiles(chunk, TILE_WALL, 135, 36, 137, 40)
    fill_tiles(chunk, TILE_WALL, 140, 32, 142, 36)

    # ================================================================
    # SESSION 9 FIDELITY PASS — IrithyllDungeon architectural details
    # ================================================================
    # Entry cell corridor — iron bar debris (DS3: prison cell corridors)
    fill_tiles(chunk, TILE_WALL, 18, 16, 19, 17)
    fill_tiles(chunk, TILE_WALL, 24, 20, 25, 21)
    fill_tiles(chunk, TILE_WALL, 14, 24, 15, 25)
    fill_tiles(chunk, TILE_WALL, 28, 14, 29, 15)
    fill_tiles(chunk, TILE_WALL, 20, 28, 21, 29)
    # Jailer patrol corridor — hanging cage stones (DS3: cages hanging from ceiling)
    fill_tiles(chunk, TILE_WALL, 34, 36, 35, 37)
    fill_tiles(chunk, TILE_WALL, 38, 40, 39, 41)
    fill_tiles(chunk, TILE_WALL, 30, 44, 31, 45)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    # Giant rat cellar — slime-coated stones (DS3: wet dungeon basement)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 42, 60, 43, 61)
    fill_tiles(chunk, TILE_WALL, 54, 50, 55, 51)
    fill_tiles(chunk, TILE_WALL, 48, 64, 49, 65)
    # Siegward cell block — iron door frame stones (DS3: Siegward locked in cell)
    fill_tiles(chunk, TILE_WALL, 58, 44, 59, 45)
    fill_tiles(chunk, TILE_WALL, 62, 48, 63, 49)
    fill_tiles(chunk, TILE_WALL, 54, 52, 55, 53)
    fill_tiles(chunk, TILE_WALL, 66, 42, 67, 43)
    # Karla cell area — abyss-tinged stones (DS3: Karla imprisoned in deepest cell)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 68, 76, 69, 77)
    fill_tiles(chunk, TILE_WALL, 80, 66, 81, 67)
    fill_tiles(chunk, TILE_WALL, 74, 78, 75, 79)
    # Profaned Capital exit — dragon-crest stones (DS3: passage to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 90, 30, 91, 31)
    fill_tiles(chunk, TILE_WALL, 95, 34, 96, 35)
    fill_tiles(chunk, TILE_WALL, 86, 38, 87, 39)
    fill_tiles(chunk, TILE_WALL, 100, 28, 101, 29)

    # ================================================================
    # SESSION 12 FIDELITY PASS — IrithyllDungeon fine architectural details
    # ================================================================
    # Entry corridor — damp stone fragments (DS3: wet stone passage from Irithyll)
    fill_tiles(chunk, TILE_WALL, 8, 8, 9, 9)
    fill_tiles(chunk, TILE_WALL, 12, 10, 13, 11)
    fill_tiles(chunk, TILE_WALL, 20, 14, 21, 15)
    fill_tiles(chunk, TILE_WALL, 26, 18, 27, 19)
    fill_tiles(chunk, TILE_WALL, 16, 26, 17, 27)
    # Upper cell block — rusted bar debris (DS3: rusted prison cell bars)
    fill_tiles(chunk, TILE_WALL, 30, 26, 31, 27)
    fill_tiles(chunk, TILE_WALL, 38, 30, 39, 31)
    fill_tiles(chunk, TILE_WALL, 48, 28, 49, 29)
    fill_tiles(chunk, TILE_WALL, 56, 34, 57, 35)
    fill_tiles(chunk, TILE_WALL, 44, 38, 45, 39)
    fill_tiles(chunk, TILE_WALL, 60, 40, 61, 41)
    # Central block — watchtower stone supports (DS3: central prison hub)
    fill_tiles(chunk, TILE_WALL, 28, 46, 29, 47)
    fill_tiles(chunk, TILE_WALL, 38, 54, 39, 55)
    fill_tiles(chunk, TILE_WALL, 48, 58, 49, 59)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 68, 56, 69, 57)
    fill_tiles(chunk, TILE_WALL, 52, 66, 53, 67)
    fill_tiles(chunk, TILE_WALL, 64, 62, 65, 63)
    fill_tiles(chunk, TILE_WALL, 72, 60, 73, 61)
    # Siegward cell — chain anchor debris (DS3: Siegward's imprisonment cell)
    fill_tiles(chunk, TILE_WALL, 84, 50, 85, 51)
    fill_tiles(chunk, TILE_WALL, 90, 56, 91, 57)
    fill_tiles(chunk, TILE_WALL, 96, 60, 97, 61)
    fill_tiles(chunk, TILE_WALL, 82, 64, 83, 65)
    fill_tiles(chunk, TILE_WALL, 92, 54, 93, 55)
    # Lower drains — sewage grate debris (DS3: flooded drain tunnels)
    fill_tiles(chunk, TILE_WALL, 22, 74, 23, 75)
    fill_tiles(chunk, TILE_WALL, 32, 78, 33, 79)
    fill_tiles(chunk, TILE_WALL, 42, 82, 43, 83)
    fill_tiles(chunk, TILE_WALL, 52, 86, 53, 87)
    fill_tiles(chunk, TILE_WALL, 62, 80, 63, 81)
    fill_tiles(chunk, TILE_WALL, 38, 88, 39, 89)
    fill_tiles(chunk, TILE_WALL, 56, 92, 57, 93)
    fill_tiles(chunk, TILE_WALL, 44, 94, 45, 95)
    # Karla's cell — abyss-touched stones (DS3: deepest prison cell)
    fill_tiles(chunk, TILE_WALL, 76, 82, 77, 83)
    fill_tiles(chunk, TILE_WALL, 84, 86, 85, 87)
    fill_tiles(chunk, TILE_WALL, 92, 90, 93, 91)
    fill_tiles(chunk, TILE_WALL, 80, 90, 81, 91)
    fill_tiles(chunk, TILE_WALL, 88, 84, 89, 85)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    # Exit to Profaned Capital — stone arch fragments (DS3: passage to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 108, 26, 109, 27)
    fill_tiles(chunk, TILE_WALL, 120, 32, 121, 33)
    fill_tiles(chunk, TILE_WALL, 130, 34, 131, 35)
    fill_tiles(chunk, TILE_WALL, 138, 30, 139, 31)
    fill_tiles(chunk, TILE_WALL, 115, 38, 116, 39)
    fill_tiles(chunk, TILE_WALL, 128, 38, 129, 39)
    # Gargoyle tower — perch stones (DS3: gargoyles guard the tower)
    fill_tiles(chunk, TILE_WALL, 88, 38, 89, 39)
    fill_tiles(chunk, TILE_WALL, 96, 42, 97, 43)
    fill_tiles(chunk, TILE_WALL, 104, 40, 105, 41)
    fill_tiles(chunk, TILE_WALL, 92, 46, 93, 47)
    fill_tiles(chunk, TILE_WALL, 100, 44, 101, 45)


    # ================================================================
    # DS3 STRUCTURAL WALLS — Irithyll Dungeon jail cells and corridors
    # DS3: dark prison with iron bars, cell dividers, chains, drainage
    # ================================================================
    # Main cell block — large cell divider walls (DS3: prison cells with jailers)
    fill_tiles(chunk, TILE_WALL, 40, 30, 44, 36)    # Cell divider 1
    fill_tiles(chunk, TILE_WALL, 56, 28, 60, 34)    # Cell divider 2
    fill_tiles(chunk, TILE_WALL, 72, 30, 76, 36)    # Cell divider 3
    fill_tiles(chunk, TILE_WALL, 88, 28, 92, 34)    # Cell divider 4
    # Corridor walls — narrow passage walls (DS3: dark corridors with rats)
    fill_tiles(chunk, TILE_WALL, 32, 42, 36, 48)    # Corridor wall left
    fill_tiles(chunk, TILE_WALL, 60, 44, 64, 50)    # Corridor wall mid
    fill_tiles(chunk, TILE_WALL, 84, 42, 88, 48)    # Corridor wall right
    # Lower dungeon — cell rows (DS3: multiple cells with jailer patrols)
    fill_tiles(chunk, TILE_WALL, 36, 56, 40, 62)    # Lower cell wall 1
    fill_tiles(chunk, TILE_WALL, 52, 58, 56, 64)    # Lower cell wall 2
    fill_tiles(chunk, TILE_WALL, 68, 56, 72, 62)    # Lower cell wall 3
    fill_tiles(chunk, TILE_WALL, 84, 58, 88, 64)    # Lower cell wall 4
    # Dragon statue alcove — large wall block (DS3: dragon stone in dungeon)
    fill_tiles(chunk, TILE_WALL, 96, 50, 102, 56)   # Dragon statue alcove
    # Jailer patrol corridor — iron bar walls (DS3: jailers with branding irons)
    fill_tiles(chunk, TILE_WALL, 44, 68, 48, 74)    # Jailer room wall
    fill_tiles(chunk, TILE_WALL, 64, 70, 68, 76)    # Jailer room wall 2
    # Siegward cell area — reinforced walls (DS3: Siegward trapped in cell)
    fill_tiles(chunk, TILE_WALL, 24, 66, 28, 72)    # Siegward cell wall
    spawn_px, spawn_py = 15 * 16, 12 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires — DS3: only Irithyll Dungeon bonfire
    entities.append(make_entity("Bonfire", 32 * 16, 32 * 16))     # Irithyll Dungeon

    # Enemies — DS3 Irithyll Dungeon (wiki-verified walkthrough):
    # Jailers (branding iron wardens — many throughout), Reanimated Corpses in cells,
    # Wretches (screaming enemies), Rats (swarms in drains), Basilisks (curse spawners),
    # Infested Corpses (corpse-grubs), Lycanthropes (Dog), Monstrosity of Sin (MonstrosityOfSin),
    # Sewer Centipedes (ManGrub), Gargoyles (tower guard), Crystal Lizards, Mimics
    # Items — DS3 Irithyll Dungeon (verified against wiki)
    for kind, name, tx, ty, val in [
        # Upper prison cells
        ("Consumable", "Rusted Coin", 20, 16, 0),            # First cell near bonfire (wiki walkthrough)
        ("Consumable", "Fading Soul", 18, 22, 0),
        ("TitaniteShard", "Large Titanite Shard", 28, 32, 0),
        ("TitaniteShard", "Large Titanite Shard", 48, 40, 0),
        ("Consumable", "Pale Pine Resin", 38, 35, 0),
        ("Consumable", "Pale Pine Resin", 40, 36, 0),
        ("ArmorDrop", "Old Sorcerer Hat", 35, 42, 0),
        ("ArmorDrop", "Old Sorcerer Coat", 36, 43, 0),
        ("ArmorDrop", "Old Sorcerer Gauntlets", 37, 44, 0),
        ("ArmorDrop", "Old Sorcerer Boots", 38, 45, 0),
        ("Consumable", "Great Magic Shield", 42, 38, 0),
        # Central cell block
        ("Consumable", "Rusted Gold Coin", 52, 56, 0),
        ("TitaniteShard", "Large Titanite Shard", 62, 58, 0),
        ("RingDrop", "Bellowing Dragoncrest Ring", 55, 62, 0),
        ("Consumable", "Jailbreaker's Key", 58, 58, 0),
        # Siegward area
        ("Consumable", "Simple Gem", 82, 60, 0),
        ("Consumable", "Profaned Coal", 75, 58, 0),
        ("TitaniteShard", "Large Titanite Shard", 78, 62, 0),
        # Lower sewers
        ("SoulOrb", "Large Soul of a Nameless Soldier", 30, 80, 800),
        ("Consumable", "Dung Pie", 34, 82, 0),
        ("Consumable", "Dung Pie", 36, 84, 0),
        ("Consumable", "Dung Pie", 38, 86, 0),
        ("Consumable", "Dung Pie", 42, 86, 0),
        ("TitaniteShard", "Large Titanite Shard", 45, 85, 0),
        ("HomewardBone", "Homeward Bone", 55, 75, 0),
        ("HomewardBone", "Homeward Bone", 57, 77, 0),
        # Old Cell Key is in the chest at (58,78), not a ground pickup
        # Dragon Stone area
        ("Consumable", "Dragon Torso Stone", 105, 38, 0),
        ("SoulOrb", "Large Soul of a Nameless Soldier", 110, 35, 800),
        ("Consumable", "Lightning Blade", 108, 32, 0),
        # Karla area
        ("Consumable", "Xanthous Ashes", 82, 88, 0),
        ("RingDrop", "Dusk Crown Ring", 84, 90, 0),
        ("Ember", "Ember", 88, 85, 0),
        ("Ember", "Ember", 92, 88, 0),
        ("SoulOrb", "Soul of a Weary Warrior", 95, 92, 2000),
        # Exit area
        ("WeaponDrop", "Pickaxe", 115, 32, 0),
        ("SoulOrb", "Large Soul of a Weary Warrior", 130, 28, 2000),
        ("UndeadBoneShard", "Undead Bone Shard", 135, 30, 0),
    ]:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind), make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    entities.append(make_entity("Npc", 112 * 16, 101 * 16, [make_field("name", "String", "Siegward"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#D4A520"), make_field("dialogue", "String", "Oh! You have my thanks, my deepest thanks|I seem to have gotten myself locked in this cell|A brave warrior like yourself, I knew you would come|Let us share a drink, to celebrate your bravery|I am Siegward of Catarina, at your service")]))
    entities.append(make_entity("Npc", 111 * 16, 160 * 16, [make_field("name", "String", "Karla"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#4A0080"), make_field("dialogue", "String", "Hmm. A visitor? I'm a prisoner, same as you|I can teach you dark sorceries, if you bring me tomes|But nothing that could harm the Fire Keeper, understand|The pygmy is not to be trifled with")]))

    # Fog Gate back to Irithyll (DS3: return from dungeon entrance)
    entities.append(make_entity("FogGate", 32 * 16, 26 * 16, [
        make_field("dest_area", "String", "Irithyll"),
        make_field("dest_x", "Float", 2500.0), make_field("dest_y", "Float", 500.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    entities.append(make_entity("FogGate", 201 * 16, 250 * 16, [
        make_field("dest_area", "String", "ProfanedCapital"),
        make_field("dest_x", "Float", 100.0), make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))
    # To Archdragon Peak (dragon gesture path)
    entities.append(make_entity("FogGate", 191 * 16, 87 * 16, [
        make_field("dest_area", "String", "ArchdragonPeak"),
        make_field("dest_x", "Float", 280.0),
        make_field("dest_y", "Float", 2160.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights - dim cold prison lighting
    entities.append(make_entity("Light", 15 * 16, 15 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.7), make_field("g", "Float", 0.7), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 52 * 16, 58 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.6), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 135 * 16, 32 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 0.7), make_field("g", "Float", 0.7), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))

    # === ADDITIONAL INTERNAL STRUCTURES — dungeon ===
    # Entry cells — cell bars and walls
    fill_tiles(chunk, TILE_WALL, 12, 18, 14, 20)
    fill_tiles(chunk, TILE_WALL, 22, 22, 24, 24)
    fill_tiles(chunk, TILE_WALL, 30, 18, 32, 20)
    # Main prison hall — support pillars
    fill_tiles(chunk, TILE_WALL, 40, 38, 42, 40)
    fill_tiles(chunk, TILE_WALL, 52, 42, 54, 44)
    fill_tiles(chunk, TILE_WALL, 62, 48, 64, 50)
    fill_tiles(chunk, TILE_WALL, 45, 55, 47, 57)
    fill_tiles(chunk, TILE_WALL, 58, 58, 60, 60)
    # Jailer corridors — cell dividers
    fill_tiles(chunk, TILE_WALL, 75, 55, 77, 57)
    fill_tiles(chunk, TILE_WALL, 85, 52, 87, 54)
    fill_tiles(chunk, TILE_WALL, 95, 58, 97, 60)
    fill_tiles(chunk, TILE_WALL, 105, 55, 107, 57)
    fill_tiles(chunk, TILE_WALL, 80, 65, 82, 67)
    fill_tiles(chunk, TILE_WALL, 90, 68, 92, 70)
    # Dungeon depths — cages and torture equipment
    fill_tiles(chunk, TILE_WALL, 108, 22, 110, 24)
    fill_tiles(chunk, TILE_WALL, 118, 28, 120, 30)
    fill_tiles(chunk, TILE_WALL, 128, 25, 130, 27)
    fill_tiles(chunk, TILE_WALL, 115, 35, 117, 37)
    fill_tiles(chunk, TILE_WALL, 138, 30, 140, 32)

    # === ADDITIONAL DUNGEON DETAILS — DS3 fidelity ===
    # Upper cell block — additional cell bars (DS3: cramped cells with iron bars)
    fill_tiles(chunk, TILE_WALL, 18, 28, 20, 30)
    fill_tiles(chunk, TILE_WALL, 28, 32, 30, 34)
    fill_tiles(chunk, TILE_WALL, 35, 26, 37, 28)
    fill_tiles(chunk, TILE_WALL, 48, 30, 50, 32)
    fill_tiles(chunk, TILE_WALL, 60, 36, 62, 38)
    # Central cell block — more prison cell dividers
    # DS3: large room with many cells, jailers patrol between them
    fill_tiles(chunk, TILE_WALL, 30, 54, 32, 56)
    fill_tiles(chunk, TILE_WALL, 42, 60, 44, 62)
    fill_tiles(chunk, TILE_WALL, 55, 64, 57, 66)
    fill_tiles(chunk, TILE_WALL, 68, 55, 70, 57)
    fill_tiles(chunk, TILE_WALL, 72, 62, 74, 64)
    fill_tiles(chunk, TILE_WALL, 38, 66, 40, 68)
    # Siegward's cell area — cell interior walls (DS3: Siegward locked in a cell)
    fill_tiles(chunk, TILE_WALL, 82, 56, 84, 58)
    fill_tiles(chunk, TILE_WALL, 88, 60, 90, 62)
    fill_tiles(chunk, TILE_WALL, 95, 64, 97, 66)
    fill_tiles(chunk, TILE_WALL, 100, 58, 102, 60)
    # Lower drains — sewage pipes and grates (DS3: rat-infested sewer tunnels)
    fill_tiles(chunk, TILE_WALL, 25, 75, 27, 77)
    fill_tiles(chunk, TILE_WALL, 35, 80, 37, 82)
    fill_tiles(chunk, TILE_WALL, 45, 88, 47, 90)
    fill_tiles(chunk, TILE_WALL, 55, 82, 57, 84)
    fill_tiles(chunk, TILE_WALL, 62, 90, 64, 92)
    fill_tiles(chunk, TILE_WALL, 30, 88, 32, 90)
    # Karla's cell — deep prison walls (DS3: Karla locked in deepest cell)
    fill_tiles(chunk, TILE_WALL, 78, 82, 80, 84)
    fill_tiles(chunk, TILE_WALL, 85, 88, 87, 90)
    fill_tiles(chunk, TILE_WALL, 92, 84, 94, 86)
    fill_tiles(chunk, TILE_WALL, 98, 90, 100, 92)
    # Gargoyle tower — stone platforms (DS3: gargoyles on tower roof)
    fill_tiles(chunk, TILE_WALL, 88, 38, 90, 40)
    fill_tiles(chunk, TILE_WALL, 95, 42, 97, 44)
    fill_tiles(chunk, TILE_WALL, 102, 40, 104, 42)
    # Exit corridor — stone arches (DS3: long corridor to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 112, 30, 114, 32)
    fill_tiles(chunk, TILE_WALL, 125, 28, 127, 30)
    fill_tiles(chunk, TILE_WALL, 132, 32, 134, 34)
    fill_tiles(chunk, TILE_WALL, 142, 28, 144, 30)
    # Additional Irithyll Dungeon DS3 details
    # Entry guard room walls (DS3: wretches attack from cells on entry)
    fill_tiles(chunk, TILE_WALL, 10, 14, 12, 16)
    fill_tiles(chunk, TILE_WALL, 16, 16, 18, 18)
    # Main hall watchtower supports (DS3: tall dark corridor with Jailers carrying lanterns)
    fill_tiles(chunk, TILE_WALL, 36, 42, 38, 44)
    fill_tiles(chunk, TILE_WALL, 50, 46, 52, 48)
    fill_tiles(chunk, TILE_WALL, 65, 52, 67, 54)
    # Jailer patrol obstacles (DS3: jailers carry branding irons, patrol between cells)
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 62)
    fill_tiles(chunk, TILE_WALL, 100, 62, 102, 64)
    fill_tiles(chunk, TILE_WALL, 110, 56, 112, 58)
    # Deep drain tunnel walls (DS3: narrow tunnels beneath the prison)
    fill_tiles(chunk, TILE_WALL, 20, 82, 22, 84)
    fill_tiles(chunk, TILE_WALL, 40, 86, 42, 88)
    fill_tiles(chunk, TILE_WALL, 50, 78, 52, 80)
    fill_tiles(chunk, TILE_WALL, 65, 86, 67, 88)
    # Profaned Capital exit ramp stones (DS3: stone ramp leading out of dungeon)
    fill_tiles(chunk, TILE_WALL, 120, 34, 122, 36)
    fill_tiles(chunk, TILE_WALL, 135, 26, 137, 28)

    # ================================================================
    # DS3 IRITHYLL DUNGEON — final architectural fidelity pass
    # ================================================================
    # Entry passage — dripping water stalactites (DS3: damp stone entry from Irithyll)
    fill_tiles(chunk, TILE_WALL, 12, 10, 13, 12)
    fill_tiles(chunk, TILE_WALL, 20, 14, 21, 16)
    fill_tiles(chunk, TILE_WALL, 26, 18, 27, 20)
    # Upper cell block — iron bar dividers (DS3: rows of cramped cells with iron bars)
    fill_tiles(chunk, TILE_WALL, 30, 26, 31, 28)
    fill_tiles(chunk, TILE_WALL, 38, 34, 39, 36)
    fill_tiles(chunk, TILE_WALL, 52, 36, 53, 38)
    fill_tiles(chunk, TILE_WALL, 60, 28, 61, 30)
    # Central prison hall — additional support columns (DS3: dark hall with tall pillars)
    fill_tiles(chunk, TILE_WALL, 40, 48, 41, 50)
    fill_tiles(chunk, TILE_WALL, 55, 52, 56, 54)
    fill_tiles(chunk, TILE_WALL, 68, 58, 69, 60)
    fill_tiles(chunk, TILE_WALL, 45, 64, 46, 66)
    # Siegward cell — broken bars and chain rings (DS3: Siegward's cell with Old Cell Key)
    fill_tiles(chunk, TILE_WALL, 85, 56, 86, 58)
    fill_tiles(chunk, TILE_WALL, 92, 60, 93, 62)
    fill_tiles(chunk, TILE_WALL, 98, 56, 99, 58)
    # Lower drain — slime-coated tunnel walls (DS3: toxic water in drain tunnels)
    fill_tiles(chunk, TILE_WALL, 28, 84, 29, 86)
    fill_tiles(chunk, TILE_WALL, 38, 78, 39, 80)
    fill_tiles(chunk, TILE_WALL, 58, 82, 59, 84)
    fill_tiles(chunk, TILE_WALL, 48, 92, 49, 94)
    # Karla's cell — deep prison stone walls (DS3: illusory wall conceals Karla)
    fill_tiles(chunk, TILE_WALL, 82, 86, 83, 88)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 84)
    fill_tiles(chunk, TILE_WALL, 96, 88, 97, 90)
    # Gargoyle tower ledge — narrow parapet walls (DS3: exterior ledge with gargoyles)
    fill_tiles(chunk, TILE_WALL, 90, 36, 91, 38)
    fill_tiles(chunk, TILE_WALL, 98, 44, 99, 46)
    # Exit corridor — dungeon gate stones (DS3: long stone corridor to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 118, 32, 119, 34)
    fill_tiles(chunk, TILE_WALL, 128, 26, 129, 28)
    fill_tiles(chunk, TILE_WALL, 140, 30, 141, 32)
    # SESSION 10 FIDELITY PASS — Irithyll Dungeon
    # Additional DS3-faithful terrain: iron bar debris, hanging cage stones,
    # Siegward cell block, Karla abyss stones, jailer corridor debris
    # Entry stairs — stone step debris (DS3: crumbling dungeon stairs)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 22, 22, 23, 23)
    fill_tiles(chunk, TILE_WALL, 26, 20, 27, 21)
    # Jailer corridor — iron bar debris (DS3: iron bars and prison cells)
    fill_tiles(chunk, TILE_WALL, 32, 28, 33, 29)
    fill_tiles(chunk, TILE_WALL, 38, 32, 39, 33)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 37)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 35)
    fill_tiles(chunk, TILE_WALL, 56, 38, 57, 39)
    # Hanging cage area — cage support stones (DS3: cages hanging from ceiling)
    fill_tiles(chunk, TILE_WALL, 62, 42, 63, 43)
    fill_tiles(chunk, TILE_WALL, 68, 46, 69, 47)
    fill_tiles(chunk, TILE_WALL, 72, 44, 73, 45)
    fill_tiles(chunk, TILE_WALL, 66, 48, 67, 49)
    # Siegward cell block — cell wall debris (DS3: Siegward's prison cell)
    fill_tiles(chunk, TILE_WALL, 78, 52, 79, 53)
    fill_tiles(chunk, TILE_WALL, 82, 56, 83, 57)
    fill_tiles(chunk, TILE_WALL, 76, 54, 77, 55)
    # Karla's cell — abyss stones (DS3: Karla's cell in the abyss area)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)
    fill_tiles(chunk, TILE_WALL, 92, 66, 93, 67)
    fill_tiles(chunk, TILE_WALL, 86, 64, 87, 65)
    fill_tiles(chunk, TILE_WALL, 94, 68, 95, 69)
    # Main cell block — prison door debris (DS3: rows of prison cells)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    fill_tiles(chunk, TILE_WALL, 40, 46, 41, 47)
    fill_tiles(chunk, TILE_WALL, 46, 44, 47, 45)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 46, 59, 47)
    # Basilisk pit — wet stone debris (DS3: curse frog pit)
    fill_tiles(chunk, TILE_WALL, 98, 72, 99, 73)
    fill_tiles(chunk, TILE_WALL, 102, 76, 103, 77)
    fill_tiles(chunk, TILE_WALL, 96, 74, 97, 75)
    fill_tiles(chunk, TILE_WALL, 106, 78, 107, 79)
    # Profaned Capital exit — corridor stones (DS3: path to Profaned Capital)
    fill_tiles(chunk, TILE_WALL, 110, 82, 111, 83)
    fill_tiles(chunk, TILE_WALL, 114, 86, 115, 87)

    # ================================================================
    # SESSION 15 FIDELITY PASS — IrithyllDungeon additional DS3 details
    # ================================================================
    # Jailer torch alcoves along corridors (DS3: jailers carry lanterns, alcoves line halls)
    fill_tiles(chunk, TILE_WALL, 8, 22, 9, 23)
    fill_tiles(chunk, TILE_WALL, 14, 26, 15, 27)
    fill_tiles(chunk, TILE_WALL, 24, 30, 25, 31)
    fill_tiles(chunk, TILE_WALL, 36, 38, 37, 39)
    fill_tiles(chunk, TILE_WALL, 48, 40, 49, 41)
    # Giant's cell — chain anchor stones (DS3: massive giant held in cell by chains)
    fill_tiles(chunk, TILE_WALL, 102, 40, 103, 42)
    fill_tiles(chunk, TILE_WALL, 108, 44, 109, 46)
    fill_tiles(chunk, TILE_WALL, 112, 48, 113, 50)
    fill_tiles(chunk, TILE_WALL, 106, 52, 107, 54)
    # Drain grate debris (DS3: water drains with grates, rats lurk below)
    fill_tiles(chunk, TILE_WALL, 22, 86, 23, 87)
    fill_tiles(chunk, TILE_WALL, 32, 90, 33, 91)
    fill_tiles(chunk, TILE_WALL, 42, 94, 43, 95)
    fill_tiles(chunk, TILE_WALL, 52, 88, 53, 89)
    # Dragon gesture room — meditation alcove stones (DS3: Path of the Dragon gesture room)
    fill_tiles(chunk, TILE_WALL, 122, 18, 123, 20)
    fill_tiles(chunk, TILE_WALL, 128, 22, 129, 24)
    fill_tiles(chunk, TILE_WALL, 134, 16, 135, 18)
    # Spiral staircase stones (DS3: tight spiral stair connecting levels)
    fill_tiles(chunk, TILE_WALL, 72, 68, 73, 70)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 74)
    fill_tiles(chunk, TILE_WALL, 84, 76, 85, 78)
    fill_tiles(chunk, TILE_WALL, 76, 80, 77, 82)
    fill_tiles(chunk, TILE_WALL, 118, 84, 119, 85)

    # SESSION 18 FIDELITY PASS — IrithyllDungeon DS3 prison details
    # Entry corridor — rusted gate debris (DS3: entry from Irithyll through sewers)
    fill_tiles(chunk, TILE_WALL, 14, 28, 15, 30)
    fill_tiles(chunk, TILE_WALL, 20, 32, 21, 34)
    fill_tiles(chunk, TILE_WALL, 26, 30, 27, 32)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 36)
    # Jailer patrol corridor — lantern hook stones (DS3: Jailers patrol with lanterns)
    fill_tiles(chunk, TILE_WALL, 38, 38, 39, 40)
    fill_tiles(chunk, TILE_WALL, 44, 42, 45, 44)
    fill_tiles(chunk, TILE_WALL, 50, 36, 51, 38)
    fill_tiles(chunk, TILE_WALL, 56, 40, 57, 42)
    # Prison cells — iron bar debris (DS3: cells with Wretches inside)
    fill_tiles(chunk, TILE_WALL, 62, 44, 63, 46)
    fill_tiles(chunk, TILE_WALL, 68, 48, 69, 50)
    fill_tiles(chunk, TILE_WALL, 74, 42, 75, 44)
    fill_tiles(chunk, TILE_WALL, 80, 46, 81, 48)
    # Giant's room — chain anchor stones (DS3: giant chained in dungeon)
    fill_tiles(chunk, TILE_WALL, 86, 50, 87, 52)
    fill_tiles(chunk, TILE_WALL, 92, 54, 93, 56)
    fill_tiles(chunk, TILE_WALL, 98, 48, 99, 50)
    fill_tiles(chunk, TILE_WALL, 104, 52, 105, 54)
    # Karla's cell — hidden room debris (DS3: locked cell behind illusory wall)
    fill_tiles(chunk, TILE_WALL, 88, 82, 89, 84)
    fill_tiles(chunk, TILE_WALL, 94, 86, 95, 88)
    fill_tiles(chunk, TILE_WALL, 82, 86, 83, 88)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 82)

    # ================================================================
    # SESSION 21 FIDELITY PASS — IrithyllDungeon DS3 prison details
    # ================================================================
    # Jailer lantern bracket posts (DS3: wall-mounted brackets for jailer lanterns)
    fill_tiles(chunk, TILE_WALL, 15, 34, 17, 36)
    fill_tiles(chunk, TILE_WALL, 21, 38, 23, 40)
    fill_tiles(chunk, TILE_WALL, 27, 36, 29, 38)
    fill_tiles(chunk, TILE_WALL, 33, 42, 35, 44)
    # Iron cell door frames (DS3: rusted iron door frames on cells)
    fill_tiles(chunk, TILE_WALL, 41, 46, 43, 48)
    fill_tiles(chunk, TILE_WALL, 47, 50, 49, 52)
    fill_tiles(chunk, TILE_WALL, 53, 48, 55, 50)
    fill_tiles(chunk, TILE_WALL, 59, 52, 61, 54)
    # Torture rack debris (DS3: broken torture implements in lower cells)
    fill_tiles(chunk, TILE_WALL, 23, 78, 25, 80)
    fill_tiles(chunk, TILE_WALL, 29, 82, 31, 84)
    fill_tiles(chunk, TILE_WALL, 37, 86, 39, 88)
    fill_tiles(chunk, TILE_WALL, 43, 90, 45, 92)
    # Dungeon pipe fragments (DS3: rusted pipes along dungeon ceiling)
    fill_tiles(chunk, TILE_WALL, 65, 60, 67, 62)
    fill_tiles(chunk, TILE_WALL, 71, 64, 73, 66)
    fill_tiles(chunk, TILE_WALL, 77, 68, 79, 70)
    fill_tiles(chunk, TILE_WALL, 83, 72, 85, 74)
    # Profaned Capital elevator shaft debris (DS3: broken mechanism near exit)
    fill_tiles(chunk, TILE_WALL, 122, 36, 124, 38)
    fill_tiles(chunk, TILE_WALL, 130, 40, 132, 42)
    fill_tiles(chunk, TILE_WALL, 138, 44, 140, 46)
    fill_tiles(chunk, TILE_WALL, 146, 42, 148, 44)

    # ================================================================
    # SESSION 23 FIDELITY PASS — IrithyllDungeon DS3 prison details
    # ================================================================
    # Cell door iron frames (DS3: heavy iron door frames on cells)
    fill_tiles(chunk, TILE_WALL, 110, 36, 111, 37)
    fill_tiles(chunk, TILE_WALL, 116, 40, 117, 41)
    fill_tiles(chunk, TILE_WALL, 122, 44, 123, 45)
    fill_tiles(chunk, TILE_WALL, 128, 48, 129, 49)
    # Giant prisoner chain anchors (DS3: chains hanging from ceiling)
    fill_tiles(chunk, TILE_WALL, 134, 52, 135, 53)
    fill_tiles(chunk, TILE_WALL, 140, 56, 141, 57)
    fill_tiles(chunk, TILE_WALL, 146, 60, 147, 61)
    fill_tiles(chunk, TILE_WALL, 148, 64, 149, 65)
    # Drainage pipe debris (DS3: rusted pipes in the sewer section)
    fill_tiles(chunk, TILE_WALL, 20, 95, 21, 96)
    fill_tiles(chunk, TILE_WALL, 26, 99, 27, 100)
    fill_tiles(chunk, TILE_WALL, 32, 103, 33, 104)
    fill_tiles(chunk, TILE_WALL, 38, 107, 39, 108)

    # ================================================================
    # SESSION 27 FIDELITY PASS — IrithyllDungeon DS3 prison details
    # ================================================================
    # Oubliette pit debris (DS3: debris at the bottom of dungeon pits)
    fill_tiles(chunk, TILE_WALL, 44, 80, 45, 81)
    fill_tiles(chunk, TILE_WALL, 50, 84, 51, 85)
    fill_tiles(chunk, TILE_WALL, 56, 88, 57, 89)
    fill_tiles(chunk, TILE_WALL, 62, 92, 63, 93)
    # Dungeon ceiling supports (DS3: iron bars supporting the ceiling)
    fill_tiles(chunk, TILE_WALL, 68, 96, 69, 97)
    fill_tiles(chunk, TILE_WALL, 74, 100, 75, 101)
    fill_tiles(chunk, TILE_WALL, 80, 104, 81, 105)
    fill_tiles(chunk, TILE_WALL, 86, 108, 87, 109)
    # Karla's cell debris (DS3: debris outside Karla's locked cell)
    fill_tiles(chunk, TILE_WALL, 92, 112, 93, 113)
    fill_tiles(chunk, TILE_WALL, 98, 116, 99, 117)
    fill_tiles(chunk, TILE_WALL, 104, 120, 105, 121)
    fill_tiles(chunk, TILE_WALL, 110, 124, 111, 125)
    # Profaned Capital elevator mechanism (DS3: broken elevator near exit)
    fill_tiles(chunk, TILE_WALL, 116, 128, 117, 129)
    fill_tiles(chunk, TILE_WALL, 122, 132, 123, 133)
    fill_tiles(chunk, TILE_WALL, 128, 136, 129, 137)
    fill_tiles(chunk, TILE_WALL, 134, 140, 135, 141)

    # ================================================================
    # SESSION 31 FIDELITY PASS — IrithyllDungeon DS3 prison details
    # ================================================================
    # Jailer torture chamber debris (DS3: torture implements in jailer rooms)
    fill_tiles(chunk, TILE_WALL, 14, 32, 15, 33)
    fill_tiles(chunk, TILE_WALL, 20, 36, 21, 37)
    fill_tiles(chunk, TILE_WALL, 26, 40, 27, 41)
    fill_tiles(chunk, TILE_WALL, 32, 44, 33, 45)
    # Prison cell iron bars (DS3: rusted iron bars on cell doors)
    fill_tiles(chunk, TILE_WALL, 38, 48, 39, 49)
    fill_tiles(chunk, TILE_WALL, 44, 52, 45, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    # Siegward's cell debris (DS3: debris in Siegward's imprisonment cell)
    fill_tiles(chunk, TILE_WALL, 62, 64, 63, 65)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 74, 72, 75, 73)
    fill_tiles(chunk, TILE_WALL, 80, 76, 81, 77)
    # Profaned Capital exit corridor (DS3: long corridor to the capital)
    fill_tiles(chunk, TILE_WALL, 120, 40, 121, 41)
    fill_tiles(chunk, TILE_WALL, 126, 44, 127, 45)
    fill_tiles(chunk, TILE_WALL, 132, 48, 133, 49)
    fill_tiles(chunk, TILE_WALL, 138, 52, 139, 53)

    # SESSION 38 FIDELITY PASS — Irithyll Dungeon DS3 details
    # DS3: Cell door frames, torture rack debris, sewer pipe fragments
    for tx in range(20, 60, 6):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+1, 36)             # Cell door frames
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+1, 76)
    for tx in range(65, 110, 6):
        fill_tiles(chunk, TILE_WALL, tx, 30, tx+2, 31)             # Torture rack debris
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+2, 81)
    for ty in range(40, 70, 8):
        fill_tiles(chunk, TILE_WALL, 30, ty, 31, ty+1)             # Pipe fragments
        fill_tiles(chunk, TILE_WALL, 80, ty, 81, ty+1)
    fill_tiles(chunk, TILE_WALL, 45, 50, 47, 52)                    # Elevator mechanism
    fill_tiles(chunk, TILE_WALL, 100, 60, 102, 62)                  # Jailor key rack
    for tx in range(110, 140, 5):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)             # Sewer grates
    # SESSION 42 FIDELITY PASS — Irithyll Dungeon DS3 details
    # DS3: Cell blocks, sewer channels, jailor key racks, Sleight messaging
    for tx in range(20, 55, 5):
        fill_tiles(chunk, TILE_WALL, tx, 32, tx+1, 33)             # Cell block walls
        fill_tiles(chunk, TILE_WALL, tx, 72, tx+1, 73)
    for tx in range(60, 95, 5):
        fill_tiles(chunk, TILE_WALL, tx, 37, tx+1, 38)             # Sewer channel markers
        fill_tiles(chunk, TILE_WALL, tx, 77, tx+1, 78)
    for ty in range(35, 65, 7):
        fill_tiles(chunk, TILE_WALL, 35, ty, 36, ty+1)             # Pipe fragments
        fill_tiles(chunk, TILE_WALL, 90, ty, 91, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 52, 52, 54)                    # Jailor key rack
    fill_tiles(chunk, TILE_WALL, 100, 48, 102, 50)                  # Cell door cluster
    fill_tiles(chunk, TILE_WALL, 75, 85, 77, 87)                    # Prison grate
    for tx in range(105, 135, 6):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+1, 43)             # Dark corridor stones
    # --- SESSION 48 terrain (Irithyll Dungeon) ---
    # DS3: Cell door frames along the corridors
    for ty in range(22, 28):
        chunk[ty][28] = TILE_WALL  # cell frame
        chunk[ty][42] = TILE_WALL  # cell frame
    # Torture rack debris in the interrogation rooms
    for tx, ty in [(35, 32), (50, 35)]:
        chunk[ty][tx] = TILE_WALLTOP  # rack debris
    # Pipe fragments along the ceiling (DS3: pipes carry toxic liquid)
    for tx in range(55, 65):
        chunk[18][tx] = TILE_WALLTOP  # pipe segment
    # Sewer grate openings (DS3: the flooded basement)
    for tx in range(20, 28):
        chunk[48][tx] = TILE_WALLTOP  # grate debris
    # Jailer key rack frames (DS3: jailers carry brand-keys)
    for tx, ty in [(60, 25), (75, 30)]:
        chunk[ty][tx] = TILE_WALLTOP  # key rack

    # --- SESSION 54 terrain (Irithyll Dungeon final) ---
    # DS3: Dungeon iron maiden frames (the iron maiden torture devices)
    for tx, ty in [(22, 28), (38, 32)]:
        chunk[ty][tx] = TILE_WALL  # iron maiden frame
    # Prison cell bars (DS3: cells line the corridors)
    for ty in range(30, 36):
        chunk[ty][48] = TILE_WALL  # cell bars
    # Profaned Capital view window (DS3: you can see the capital from the dungeon)
    for ty in range(20, 25):
        chunk[ty][85] = TILE_WALLTOP  # window frame
    # Jailer brand rack (DS3: jailers carry glowing branding irons)
    chunk[35][55] = TILE_WALLTOP  # brand rack debris
    chunk[35][56] = TILE_WALLTOP

    # --- SESSION 88 DS3 terrain (Irithyll Dungeon detail pass) ---
    # DS3: Cell frames along the corridors
    for tx in [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99]:
        for ty in [15, 16]:
            chunk[tx][ty] = TILE_WALL
        for ty in [22, 23]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Main corridor (long hallway)
    for tx in range(10, 110):
        for ty in [18, 19]:
            chunk[tx][ty] = TILE_GROUND
    for tx in range(10, 110):
        chunk[tx][17] = TILE_WALL
        chunk[tx][20] = TILE_WALL
    # DS3: Torture racks in side rooms
    for tx in [20, 35, 50, 65, 80, 95]:
        for ty in [25, 26]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Pipe fragments along the ceiling
    for tx in range(15, 100):
        chunk[tx][10] = TILE_WALL
        chunk[tx][9] = TILE_WALLTOP
    # DS3: Lower sewer section
    for tx in range(20, 80):
        for ty in range(55, 65):
            chunk[tx][ty] = TILE_GROUND
    for tx in [20, 80]:
        for ty in range(55, 66):
            chunk[tx][ty] = TILE_WALL
    # DS3: Key rack alcoves
    for tx in [30, 45, 60, 75]:
        for ty in [12, 13, 14]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Giant's room (the hidden chamber)
    for tx in range(90, 110):
        for ty in [40, 55]:
            chunk[tx][ty] = TILE_WALL
    for tx in [90, 110]:
        for ty in range(40, 56):
            chunk[tx][ty] = TILE_WALL
    # DS3: Profaned Capital entrance staircase
    for tx in range(100, 115):
        for ty in range(60, 75):
            chunk[tx][ty] = TILE_GROUND
    for tx in [100, 115]:
        for ty in range(60, 76):
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 92 DS3 terrain round 2 (Irithyll Dungeon) ---
    # DS3: Cell block walls (individual cells)
    for tx in [18, 25, 32, 39, 46, 53, 60, 67, 74, 81, 88, 95]:
        for ty in range(12, 25):
            chunk[tx][ty] = TILE_WALL
    # DS3: Lower prison cells
    for tx in [22, 30, 38, 46, 54, 62, 70]:
        for ty in range(28, 40):
            chunk[tx][ty] = TILE_WALL
    # DS3: Sewer grate passages
    for tx in range(15, 50):
        for ty in [50, 51]:
            chunk[tx][ty] = TILE_GROUND
    for tx in range(15, 50):
        chunk[tx][49] = TILE_WALL
        chunk[tx][52] = TILE_WALL
    # DS3: Dragon Slayer Armour approach
    for tx in range(85, 105):
        for ty in range(65, 80):
            chunk[tx][ty] = TILE_GROUND
    for tx in [85, 105]:
        for ty in range(65, 81):
            chunk[tx][ty] = TILE_WALL
    
    # CRITICAL: Cell block connections (must be last terrain operations)
    # Connect upper cell blocks to main corridor
    fill_tiles(chunk, TILE_GROUND, 15, 8, 25, 25)      # Upper entry cells
    fill_tiles(chunk, TILE_GROUND, 15, 28, 28, 40)      # Upper cells row 2
    fill_tiles(chunk, TILE_GROUND, 15, 38, 28, 50)      # Upper cells row 3
    fill_tiles(chunk, TILE_GROUND, 15, 48, 28, 60)      # Upper cells row 4
    fill_tiles(chunk, TILE_GROUND, 15, 58, 28, 70)      # Upper cells row 5
    fill_tiles(chunk, TILE_GROUND, 15, 68, 30, 80)      # Upper cells row 6
    fill_tiles(chunk, TILE_GROUND, 15, 78, 28, 90)      # Lower cells row 7
    fill_tiles(chunk, TILE_GROUND, 15, 88, 28, 98)      # Lower cells row 8
    # Connect disconnected cell blocks to main corridors
    fill_tiles(chunk, TILE_GROUND, 140, 90, 175, 115)   # Upper right block to main
    fill_tiles(chunk, TILE_GROUND, 152, 180, 190, 220)   # Lower right block to main
    fill_tiles(chunk, TILE_GROUND, 19, 10, 30, 15)      # Entry cells to corridor
    fill_tiles(chunk, TILE_GROUND, 19, 25, 30, 35)      # Cell block link
    fill_tiles(chunk, TILE_GROUND, 19, 45, 30, 55)      # Cell block link
    fill_tiles(chunk, TILE_GROUND, 19, 65, 30, 75)      # Cell block link

    # --- DS3 faithful enemies (IrithyllDungeon) ---
    # Jailer (20)
    for tx, ty in [(22, 20), (35, 30), (48, 38), (25, 25), (32, 32), (42, 28), (58, 42), (55, 55), (60, 60), (68, 52), (48, 58), (62, 65), (70, 58), (58, 70), (65, 68), (88, 55), (95, 62), (85, 85), (95, 90), (82, 90)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Jailer", "Jailer"))]))
    # Wretch (10) — DS3: naked prisoners in cells
    for tx, ty in [(20, 30), (28, 35), (38, 28), (45, 34), (50, 50), (62, 55), (78, 60), (92, 58), (38, 80), (88, 88)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Wretch", "Wretch"))]))
    # Wretch (8 additional — DS3: Irithyllian Slaves in cells throughout dungeon)
    for tx, ty in [(55, 42), (65, 48), (45, 86), (25, 48), (35, 55), (48, 62), (85, 62), (32, 72)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Wretch", "Wretch"))]))
    # JailerHandmaid (4 — DS3: stronger jailer variant with pyromancy, patrols lower cells)
    for tx, ty in [(72, 52), (82, 58), (95, 42), (60, 75)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("JailerHandmaid", "Jailer"))]))
    # Jailer (4 additional — DS3: more jailers patrolling deeper prison levels)
    for tx, ty in [(42, 75), (50, 78), (52, 82), (92, 82)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Jailer", "Jailer"))]))
    # HoundRat (3 additional — DS3: Big Irithyllian Rats in flooded lower passages)
    for tx, ty in [(40, 76), (82, 65), (125, 30)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HoundRat", "Rat"))]))
    # Basilisk (2 additional — DS3: in dark lower cells)
    for tx, ty in [(85, 85), (40, 72)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    # GiantSlave (2) — DS3: giant in the large room, and one through shortcut
    for tx, ty in [(78, 82), (120, 90)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GiantSlave", "GiantSlave"))]))
    # CrystalLizard (1)
    entities.append(make_entity("Enemy", 52 * 16, 52 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # HoundRat (4) — DS3: rats in the sewer passage
    for tx, ty in [(28, 78), (35, 82), (42, 88), (32, 85)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HoundRat", "Rat"))]))
    # Basilisk (6)
    entities.append(make_entity("Enemy", 55 * 16, 80 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 62 * 16, 85 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 40 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 65 * 16, 78 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    # Mimic (1 additional â DS3: mimic in lower cell, total 4 mimics in dungeon)
    entities.append(make_entity("Enemy", 55 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Mimic", "Mimic"))]))
    # MiniBoss (1)
    entities.append(make_entity("Enemy", 78 * 16, 82 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    # Mimic (3)
    entities.append(make_entity("Enemy", 118 * 16, 32 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Mimic", "Mimic"))]))
    entities.append(make_entity("Enemy", 45 * 16, 82 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Mimic", "Mimic"))]))
    entities.append(make_entity("Enemy", 62 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Mimic", "Mimic"))]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 30 * 16, 23 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Coin")]))
    entities.append(make_entity("Item", 28 * 16, 28 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Fading Soul")]))
    entities.append(make_entity("Item", 35 * 16, 35 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 45 * 16, 41 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 41 * 16, 38 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Pale Pine Resin")]))
    entities.append(make_entity("Item", 38 * 16, 46 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Old Sorcerer Hat")]))
    entities.append(make_entity("Item", 39 * 16, 47 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Old Sorcerer Coat")]))
    entities.append(make_entity("Item", 40 * 16, 48 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Old Sorcerer Gauntlets")]))
    entities.append(make_entity("Item", 40 * 16, 50 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Old Sorcerer Boots")]))
    entities.append(make_entity("Item", 43 * 16, 42 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Great Magic Shield")]))
    entities.append(make_entity("Item", 68 * 16, 53 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Rusted Gold Coin")]))
    entities.append(make_entity("Item", 71 * 16, 58 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 70 * 16, 60 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Bellowing Dragoncrest Ring")]))
    entities.append(make_entity("Item", 68 * 16, 55 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Jailbreaker's Key")]))
    entities.append(make_entity("Item", 107 * 16, 105 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Simple Gem")]))
    entities.append(make_entity("Item", 105 * 16, 103 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Profaned Coal")]))
    entities.append(make_entity("Item", 85 * 16, 162 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 87 * 16, 165 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 96 * 16, 160 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 97 * 16, 162 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 176 * 16, 91 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gesture"),
        make_field("name", "String", "Dragon Torso Stone")]))
    entities.append(make_entity("Item", 178 * 16, 88 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 177 * 16, 86 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Lightning Blade")]))
    entities.append(make_entity("Item", 141 * 16, 161 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Xanthous Ashes")]))
    entities.append(make_entity("Item", 142 * 16, 165 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Dusk Crown Ring")]))
    entities.append(make_entity("Item", 145 * 16, 160 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 147 * 16, 162 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 148 * 16, 166 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 126 * 16, 97 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Pickaxe")]))
    entities.append(make_entity("Item", 191 * 16, 223 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 193 * 16, 225 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 73 * 16, 50 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 100 * 16, 167 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 112 * 16, 158 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 107 * 16, 162 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 97 * 16, 165 * 16, [
        make_field("name", "String", "Unknown")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/IrithyllDungeon.json") as _f:

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
    # print(f"  IrithyllDungeon (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "IrithyllDungeon", chunk, entities
