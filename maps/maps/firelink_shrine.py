from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_firelink_shrine():
    """Firelink Shrine - central hub area.
    DS3 Faithful layout: stone shrine with central bonfire chamber,
    throne room (5 Lord of Cinder thrones), Andre's forge alcove,
    Tower (locked door, Fire Keeper Soul at top), exterior graveyard
    with Sword Master, Shrine Handmaiden at back corner.
    """
    chunk = new_chunk(160, 128)
    entities = []

    # ================================================================
    # TERRAIN — DS3 Firelink Shrine interior and exterior
    # ================================================================

    # === 1. CENTRAL SHRINE CHAMBER — main circular room with bonfire ===
    # DS3: large circular stone chamber, bonfire at center
    carve_ellipse(chunk, 80, 80, 22, 20)
    # Shrine interior walls — stone pillars flanking the bonfire
    fill_tiles(chunk, TILE_WALL, 64, 68, 66, 76)
    fill_tiles(chunk, TILE_WALL, 94, 68, 96, 76)
    fill_tiles(chunk, TILE_WALL, 64, 84, 66, 92)
    fill_tiles(chunk, TILE_WALL, 94, 84, 96, 92)
    # Interior stone column near bonfire (DS3: central structural pillar)
    fill_tiles(chunk, TILE_WALL, 78, 76, 82, 80)

    # === 2. THRONE ROOM (north) — 5 Lord of Cinder thrones ===
    # DS3: semicircular alcove behind the bonfire with empty thrones
    fill_tiles(chunk, TILE_GROUND, 68, 54, 92, 66)
    carve_ellipse(chunk, 80, 58, 14, 6)
    # Throne alcove walls
    fill_tiles(chunk, TILE_WALL, 68, 54, 70, 58)
    fill_tiles(chunk, TILE_WALL, 90, 54, 92, 58)
    # Throne bases (DS3: 5 thrones arranged in a semicircle)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    fill_tiles(chunk, TILE_WALL, 76, 55, 78, 57)
    fill_tiles(chunk, TILE_WALL, 82, 55, 84, 57)
    fill_tiles(chunk, TILE_WALL, 86, 56, 88, 58)

    # === 3. ANDRE'S FORGE (west) — blacksmith alcove ===
    # DS3: Andre sits at his anvil in an alcove to the left of the entrance
    fill_tiles(chunk, TILE_GROUND, 42, 72, 62, 90)
    carve_ellipse(chunk, 44, 80, 8, 7)
    # Forge anvil block
    fill_tiles(chunk, TILE_WALL, 46, 78, 48, 82)
    # Forge walls creating a workshop feel
    fill_tiles(chunk, TILE_WALL, 42, 72, 44, 80)
    fill_tiles(chunk, TILE_WALL, 42, 84, 44, 90)

    # === 4. EAST WING — Hawkwood's resting area ===
    # DS3: Hawkwood sits on the floor near the right side of the shrine
    fill_tiles(chunk, TILE_GROUND, 98, 72, 118, 90)
    carve_ellipse(chunk, 120, 80, 7, 6)
    # Interior divider wall
    fill_tiles(chunk, TILE_WALL, 98, 72, 100, 80)
    fill_tiles(chunk, TILE_WALL, 98, 84, 100, 90)

    # === 5. SHRINE HANDMAIDEN ALCOVE (NW corner) ===
    # DS3: Handmaiden stands in the back-left corner of the shrine
    fill_tiles(chunk, TILE_GROUND, 62, 62, 72, 72)
    # Wall divider between handmaiden and throne room
    fill_tiles(chunk, TILE_WALL, 68, 64, 70, 68)

    # === 6. TOWER PATH (upper west) — locked tower with Fire Keeper Soul ===
    # DS3: Tower Key required to open, bridge leads across to tower
    fill_tiles(chunk, TILE_GROUND, 34, 56, 48, 72)
    carve_ellipse(chunk, 32, 60, 6, 5)
    # Tower bridge (DS3: narrow stone bridge to the tower)
    fill_tiles(chunk, TILE_GROUND, 42, 64, 48, 68)
    # Tower interior
    fill_tiles(chunk, TILE_GROUND, 26, 56, 36, 64)
    # Tower top — Fire Keeper Soul location (DS3: elevator to top)
    carve_ellipse(chunk, 28, 58, 4, 3)

    # === 7. TOWER PATH (upper east) — rafter area ===
    # DS3: Rafters accessible by dropping from tower bridge
    fill_tiles(chunk, TILE_GROUND, 112, 56, 128, 68)
    carve_ellipse(chunk, 124, 60, 7, 5)
    # Rafter supports
    fill_tiles(chunk, TILE_WALL, 116, 58, 118, 62)
    fill_tiles(chunk, TILE_WALL, 122, 58, 124, 62)

    # === 8. ENTRANCE HALL (south) — main shrine doorway ===
    # DS3: wide entrance arch leading into the shrine
    fill_tiles(chunk, TILE_GROUND, 72, 92, 88, 100)
    # Entrance pillars (DS3: stone pillars framing the door)
    fill_tiles(chunk, TILE_WALL, 72, 92, 74, 96)
    fill_tiles(chunk, TILE_WALL, 86, 92, 88, 96)

    # === 9. EXTERIOR GRAVEYARD (south) — tombstones leading to Cemetery of Ash ===
    # DS3: open graveyard with many tombstones, Sword Master patrols here
    fill_tiles(chunk, TILE_GROUND, 68, 100, 92, 118)
    # Graveyard expansion — wider area with tombstones
    fill_tiles(chunk, TILE_GROUND, 62, 108, 100, 126)
    carve_ellipse(chunk, 80, 112, 14, 8)
    # Tombstone walls (DS3: rows of gravestones)
    fill_tiles(chunk, TILE_WALL, 72, 104, 74, 106)
    fill_tiles(chunk, TILE_WALL, 78, 106, 80, 108)
    fill_tiles(chunk, TILE_WALL, 84, 104, 86, 106)
    fill_tiles(chunk, TILE_WALL, 76, 110, 78, 112)
    fill_tiles(chunk, TILE_WALL, 82, 110, 84, 112)
    # Gravestone rows in lower graveyard
    fill_tiles(chunk, TILE_WALL, 68, 116, 70, 118)
    fill_tiles(chunk, TILE_WALL, 74, 118, 76, 120)
    fill_tiles(chunk, TILE_WALL, 80, 116, 82, 118)
    fill_tiles(chunk, TILE_WALL, 86, 118, 88, 120)

    # === 10. ENTRANCE PATH (far south) — path from Cemetery of Ash ===
    fill_tiles(chunk, TILE_GROUND, 74, 126, 86, 142)
    # Walls framing the path
    fill_tiles(chunk, TILE_WALL, 70, 128, 74, 136)
    fill_tiles(chunk, TILE_WALL, 86, 128, 90, 136)

    # === 11. SWORD MASTER AREA (SW exterior) ===
    # DS3: Sword Master patrols the left side stairs outside the shrine
    fill_tiles(chunk, TILE_GROUND, 58, 128, 76, 142)
    # Stair wall divider
    fill_tiles(chunk, TILE_WALL, 62, 132, 64, 138)

    # === 12. RIGHT SIDE EXTERIOR (SE) ===
    # DS3: ember pickup area to the right of the shrine
    fill_tiles(chunk, TILE_GROUND, 86, 128, 104, 140)
    # Tree/rock obstacles
    fill_tiles(chunk, TILE_WALL, 92, 132, 94, 136)
    fill_tiles(chunk, TILE_WALL, 98, 130, 100, 134)

    # === 13. CONNECTION CORRIDORS ===
    # Central chamber to throne room
    fill_tiles(chunk, TILE_GROUND, 74, 64, 86, 70)
    # Central chamber to Andre's forge
    fill_tiles(chunk, TILE_GROUND, 60, 76, 70, 84)
    # Central chamber to east wing
    fill_tiles(chunk, TILE_GROUND, 90, 76, 100, 84)
    # Central chamber to entrance hall
    fill_tiles(chunk, TILE_GROUND, 76, 88, 84, 94)
    # Entrance hall to graveyard
    fill_tiles(chunk, TILE_GROUND, 76, 98, 84, 102)
    # Forge to tower path
    fill_tiles(chunk, TILE_GROUND, 48, 66, 56, 74)
    # East wing to rafter area
    fill_tiles(chunk, TILE_GROUND, 108, 66, 114, 74)
    # Handmaiden alcove connection
    fill_tiles(chunk, TILE_GROUND, 66, 68, 72, 74)
    # Forge to handmaiden path
    fill_tiles(chunk, TILE_GROUND, 56, 64, 64, 70)

    # ================================================================
    # SESSION 9 FIDELITY PASS — FirelinkShrine architectural details
    # ================================================================
    # Main hall — stone pillar bases (DS3: thick stone pillars support the roof)
    fill_tiles(chunk, TILE_WALL, 78, 90, 79, 91)
    fill_tiles(chunk, TILE_WALL, 84, 90, 85, 91)
    fill_tiles(chunk, TILE_WALL, 90, 90, 91, 91)
    fill_tiles(chunk, TILE_WALL, 78, 96, 79, 97)
    fill_tiles(chunk, TILE_WALL, 84, 96, 85, 97)
    fill_tiles(chunk, TILE_WALL, 90, 96, 91, 97)
    # Fireplace alcove — charred stone surround (DS3: bonfire in stone hearth)
    fill_tiles(chunk, TILE_WALL, 80, 84, 81, 85)
    fill_tiles(chunk, TILE_WALL, 88, 84, 89, 85)
    fill_tiles(chunk, TILE_WALL, 82, 82, 87, 83)
    # Throne room — coiled sword base stones (DS3: fire keeper throne area)
    fill_tiles(chunk, TILE_WALL, 76, 76, 77, 77)
    fill_tiles(chunk, TILE_WALL, 92, 76, 93, 77)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    fill_tiles(chunk, TILE_WALL, 86, 74, 87, 75)
    # Courtyard — crumbled wall debris (DS3: ruined walls around courtyard)
    fill_tiles(chunk, TILE_WALL, 68, 100, 69, 101)
    fill_tiles(chunk, TILE_WALL, 96, 100, 97, 101)
    fill_tiles(chunk, TILE_WALL, 72, 108, 73, 109)
    fill_tiles(chunk, TILE_WALL, 92, 108, 93, 109)
    # Andre's forge — anvil stones (DS3: Andre works at a stone forge)
    fill_tiles(chunk, TILE_WALL, 50, 70, 51, 71)
    fill_tiles(chunk, TILE_WALL, 54, 68, 55, 69)
    fill_tiles(chunk, TILE_WALL, 48, 74, 49, 75)
    # Handmaiden area — shelf stones (DS3: Handmaiden near stone shelves)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 70, 72, 71, 73)
    # Entry stairs — worn stone steps (DS3: worn stairs leading up to shrine)
    fill_tiles(chunk, TILE_WALL, 76, 114, 77, 115)
    fill_tiles(chunk, TILE_WALL, 84, 116, 85, 117)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Tree root cluster (DS3: massive tree roots visible inside Firelink)
    fill_tiles(chunk, TILE_WALL, 74, 86, 75, 87)
    fill_tiles(chunk, TILE_WALL, 94, 86, 95, 87)
    fill_tiles(chunk, TILE_WALL, 76, 80, 77, 81)
    fill_tiles(chunk, TILE_WALL, 92, 80, 93, 81)

    # ================================================================
    # SESSION 12 FIDELITY PASS — FirelinkShrine fine architectural details
    # ================================================================
    # Central shrine — coiled sword base stones (DS3: bonfire at center of shrine)
    fill_tiles(chunk, TILE_WALL, 76, 82, 77, 83)
    fill_tiles(chunk, TILE_WALL, 84, 82, 85, 83)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    fill_tiles(chunk, TILE_WALL, 80, 86, 81, 87)
    # Throne room — Lord of Cinder throne bases (DS3: 5 thrones in semicircle)
    fill_tiles(chunk, TILE_WALL, 74, 60, 75, 61)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 59)
    fill_tiles(chunk, TILE_WALL, 86, 60, 87, 61)
    fill_tiles(chunk, TILE_WALL, 70, 62, 71, 63)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 63)
    # Andre's forge — slag and anvil debris (DS3: Andre's workshop alcove)
    fill_tiles(chunk, TILE_WALL, 44, 76, 45, 77)
    fill_tiles(chunk, TILE_WALL, 48, 74, 49, 75)
    fill_tiles(chunk, TILE_WALL, 52, 78, 53, 79)
    fill_tiles(chunk, TILE_WALL, 46, 82, 47, 83)
    fill_tiles(chunk, TILE_WALL, 50, 86, 51, 87)
    # East wing — rafter support stones (DS3: Hawkwood's resting area)
    fill_tiles(chunk, TILE_WALL, 100, 74, 101, 75)
    fill_tiles(chunk, TILE_WALL, 106, 78, 107, 79)
    fill_tiles(chunk, TILE_WALL, 112, 76, 113, 77)
    fill_tiles(chunk, TILE_WALL, 104, 84, 105, 85)
    fill_tiles(chunk, TILE_WALL, 110, 82, 111, 83)
    # Tower path — bridge railing stones (DS3: bridge to locked tower)
    fill_tiles(chunk, TILE_WALL, 36, 58, 37, 59)
    fill_tiles(chunk, TILE_WALL, 40, 62, 41, 63)
    fill_tiles(chunk, TILE_WALL, 44, 66, 45, 67)
    fill_tiles(chunk, TILE_WALL, 38, 70, 39, 71)
    # Tower interior — spiral stair fragments (DS3: elevator tower)
    fill_tiles(chunk, TILE_WALL, 28, 60, 29, 61)
    fill_tiles(chunk, TILE_WALL, 32, 56, 33, 57)
    fill_tiles(chunk, TILE_WALL, 24, 62, 25, 63)
    fill_tiles(chunk, TILE_WALL, 30, 64, 31, 65)
    # Rafters — wooden beam fragments (DS3: rafters accessible from tower)
    fill_tiles(chunk, TILE_WALL, 114, 58, 115, 59)
    fill_tiles(chunk, TILE_WALL, 120, 62, 121, 63)
    fill_tiles(chunk, TILE_WALL, 118, 56, 119, 57)
    fill_tiles(chunk, TILE_WALL, 126, 60, 127, 61)
    # Handmaiden alcove — shelf debris (DS3: shrine handmaiden's corner)
    fill_tiles(chunk, TILE_WALL, 64, 70, 65, 71)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 67)
    fill_tiles(chunk, TILE_WALL, 70, 74, 71, 75)
    # Entrance hall — arch stones (DS3: main entrance arch)
    fill_tiles(chunk, TILE_WALL, 74, 94, 75, 95)
    fill_tiles(chunk, TILE_WALL, 86, 94, 87, 95)
    fill_tiles(chunk, TILE_WALL, 78, 98, 79, 99)
    fill_tiles(chunk, TILE_WALL, 82, 98, 83, 99)
    # Graveyard — tilted cross stones (DS3: many gravestones outside shrine)
    fill_tiles(chunk, TILE_WALL, 70, 102, 71, 103)
    fill_tiles(chunk, TILE_WALL, 80, 104, 81, 105)
    fill_tiles(chunk, TILE_WALL, 90, 102, 91, 103)
    fill_tiles(chunk, TILE_WALL, 76, 108, 77, 109)
    fill_tiles(chunk, TILE_WALL, 84, 112, 85, 113)
    fill_tiles(chunk, TILE_WALL, 72, 116, 73, 117)
    fill_tiles(chunk, TILE_WALL, 88, 118, 89, 119)
    fill_tiles(chunk, TILE_WALL, 66, 120, 67, 121)
    fill_tiles(chunk, TILE_WALL, 92, 122, 93, 123)
    # Entry path — stone border debris (DS3: path from Cemetery of Ash)
    fill_tiles(chunk, TILE_WALL, 76, 130, 77, 131)
    fill_tiles(chunk, TILE_WALL, 82, 134, 83, 135)
    fill_tiles(chunk, TILE_WALL, 78, 138, 79, 139)
    fill_tiles(chunk, TILE_WALL, 84, 140, 85, 141)
    # Sword Master area — broken stair stones (DS3: sword master outside stairs)
    fill_tiles(chunk, TILE_WALL, 60, 130, 61, 131)
    fill_tiles(chunk, TILE_WALL, 64, 136, 65, 137)
    fill_tiles(chunk, TILE_WALL, 68, 140, 69, 141)
    # Right exterior — tree root debris (DS3: trees near shrine)
    fill_tiles(chunk, TILE_WALL, 90, 130, 91, 131)
    fill_tiles(chunk, TILE_WALL, 96, 134, 97, 135)
    fill_tiles(chunk, TILE_WALL, 100, 138, 101, 139)

    # ================================================================
    # ENTITIES
    # ================================================================

    # --- Player spawn at entrance from south ---
    spawn_px, spawn_py = 80 * 16, 118 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfire in center ---
    entities.append(make_entity("Bonfire", 80 * 16, 64 * 16))

    # --- Enemies (DS3 Firelink Shrine exterior) ---
    # Sword Master — down the left stairs from shrine, wields Uchigatana

    
    # --- DS3 faithful enemies (FirelinkShrine) ---
    # DS3 wiki enemies: Crystal Lizard, Grave Warden, Starved Hound, Sword Master
    # Walkthrough: "undead dog" near right side, "two hollows" on stairs (Grave Wardens)
    # Drops: Cleric's Sacred Chime, Fading Soul (from Grave Wardens)
    # SwordMaster (1) — DS3: hostile NPC patrolling exterior stairs near grave area
    entities.append(make_entity("Enemy", 68 * 16, 110 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("SwordMaster", "Assassin"))]))
    # GraveWarden (2) — DS3: two hollows on stairs right of exterior
    for tx, ty in [(82, 102), (90, 98)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GraveWarden", "CathedralGraveWarden"))]))
    # StarvedHound (1) — DS3: undead dog near right exterior path, guards Ember pickup
    entities.append(make_entity("Enemy", 112 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("StarvedHound", "StarvedHound"))]))
    # CrystalLizard (1) — DS3: on tower rafter area, drops Twinkling Titanite
    entities.append(make_entity("Enemy", 122 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))

# --- NPCs (DS3 Firelink Shrine inhabitants) ---
    # Fire Keeper (level up) — stands near bonfire, south side
    entities.append(make_entity("Npc", 77 * 16, 60 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "LevelUp"),
        make_field("color", "Color", "#FFFFFF"),
        make_field("dialogue", "String", "Welcome to Firelink Shrine, Ashen One|I am a Fire Keeper. I tend the flame, and tend to thee|May the flames guide thee|Touch the darkness within me, and take in the excess souls|Speak thy mind, Ashen One|Ashen One, my thanks for the eyes of a Fire Keeper"),
    ]))

    # Ludleth of Courland (dialogue) — sits on throne behind bonfire
    entities.append(make_entity("Npc", 82 * 16, 64 * 16, [
        make_field("name", "String", "Ludleth of Courland"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#DAA520"),
        make_field("dialogue", "String", "Peace. I am Ludleth of Courland|Let me ask you this: is it not the nature of a Lord to sacrifice himself for his people?|Ah, it singeth, to the bone|Ahh, it singeth, to the very bone|I will not be moved. Not by you, not by anyone|The five Lords sit their thrones, and link the fire"),
    ]))

    # Blacksmith Andre — forge alcove, west wing
    entities.append(make_entity("Npc", 36 * 16, 67 * 16, [
        make_field("name", "String", "Andre of Astora"),
        make_field("kind", "LocalEnum.NpcKind", "Blacksmith"),
        make_field("color", "Color", "#C0C0C0"),
        make_field("dialogue", "String", "What do you need? Speak freely|I can reinforce your weapons with titanite|Undead, we are one and the same, we must persist|The weapons of old are a wonder, are they not?|Keep your wits about you, Undead|This forge has been here since the beginning"),
    ]))

    # Shrine Handmaiden (merchant) — back-left corner of shrine
    entities.append(make_entity("Npc", 122 * 16, 67 * 16, [
        make_field("name", "String", "Shrine Handmaiden"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B7355"),
        make_field("dialogue", "String", "What is it? Buy something|Or be on your way|I shall tend the flame|And tend to thee"),
    ]))

    # Hawkwood (dialogue) — sitting on floor in east wing
    entities.append(make_entity("Npc", 87 * 16, 68 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String", "Oh, another Unkindled|The Legion of Farron is in the Keep below|They were Lords, once... but now they are Unkindled|Do you know what an Unkindled is? We are not Lords, we are nameless, sodden souls|When the Lords abandoned their thrones, we rose from our coffins to link the fire|The Abyss Watchers took the blood of the wolf, and with it, their duty"),
    ]))

    # Yuria of Londor — appears after Yoel dies (DS3: stands near east entrance)
    entities.append(make_entity("Npc", 114 * 16, 76 * 16, [
        make_field("name", "String", "Yuria of Londor"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#2A1A3A"),
        make_field("dialogue", "String",
            "Very well. I am Yuria of Londor, a servant of the Lord of Hollows|Thou art the Lord of Hollows, the fire has bent to thy will|Let us embrace the age of hollows, together|Our battle must go on, for as long as we persist|The fire is linked by the Lord of Hollows|A world without fire, or a world with fire, the choice is thine|Hollows are the true stewards of this age"),
    ]))

    # Ringfinger Leonhard — gives Cracked Red Eye Orb (DS3: near lower stairway)
    entities.append(make_entity("Npc", 92 * 16, 94 * 16, [
        make_field("name", "String", "Ringfinger Leonhard"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#8B0000"),
        make_field("dialogue", "String",
            "Fingers crossed, you have a good look|I am Leonhard, a Ringfinger. I have a proposition for you|Take this Cracked Red Eye Orb, invade and pillage the souls of others|That is what we do, after all|You have a good head for this work|No need to be shy, we are both of the same ilk|Rosaria is the mother of rebirth, she will welcome you"),
    ]))

    # Yoel of Londor — after recruitment (DS3: stands near lower shrine, eventually dies)
    entities.append(make_entity("Npc", 56 * 16, 88 * 16, [
        make_field("name", "String", "Yoel of Londor"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#3A3A4A"),
        make_field("dialogue", "String",
            "Ahh, you're a kind soul. I am Yoel of Londor|I can draw out your true strength, the power that sleeps within thee|Accept this draw of true power|Come back when you need more|Death is a temporary affliction, nothing more|Ahh, the Abyss... I can feel it swelling within thee"),
    ]))

    # Greirat — after rescue from Lothric Wall (DS3: thief merchant near lower shrine)
    entities.append(make_entity("Npc", 52 * 16, 92 * 16, [
        make_field("name", "String", "Greirat"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#5A5A5A"),
        make_field("dialogue", "String",
            "You saved me from that cell, I owe you everything|I am Greirat of the Undead Settlement|I can steal items for you, if you like|Just leave it to old Greirat|Loretta, are you well? I brought you this bauble|I will go on a pillage, don't try to stop me"),
    ]))

    # Cornyx — after rescue from Undead Settlement (DS3: pyromancy teacher, sits near bonfire)
    entities.append(make_entity("Npc", 74 * 16, 80 * 16, [
        make_field("name", "String", "Cornyx"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#8B6914"),
        make_field("dialogue", "String",
            "You freed me from my cage. I am Cornyx, pyromancer of the Great Swamp|Bring me pyromancy tomes, and I shall teach you their arts|The flame is a wondrous thing, isn't it|Let it serve you well|A pyromancer's flame is a fragment of the ancient fire|I wonder what the Great Swamp is like these days"),
    ]))

    # Orbeck of Vinheim — after recruitment (DS3: sorcery teacher, near upper shrine)
    entities.append(make_entity("Npc", 86 * 16, 74 * 16, [
        make_field("name", "String", "Orbeck of Vinheim"),
        make_field("kind", "LocalEnum.NpcKind", "Merchant"),
        make_field("color", "Color", "#7090B0"),
        make_field("dialogue", "String",
            "Orbeck of Vinheim. A sorcerer, and an assassin|I shall teach you sorceries, as promised|Bring me scrolls, and I shall decipher them|But if you prove talentless, our arrangement ends|The Vinheim Dragon School produced many fine sorcerers|Sorcery is the art of the gods, wielded by mortal hands"),
    ]))

    # Sirris of the Sunless Realms — after oath (DS3: swears knighthood near shrine)
    entities.append(make_entity("Npc", 98 * 16, 88 * 16, [
        make_field("name", "String", "Sirris of the Sunless Realms"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#A0B0C0"),
        make_field("dialogue", "String",
            "I am Sirris of the Sunless Realms|I have sworn a knightly oath to serve you|I shall come to your aid whenever you need|Thank you, for accepting my knightly vows|My grandfather was Holy Knight Hodrick|I wish only to fulfill my duty, as a knight|The Sunless Realms are my home, and my burden"),
    ]))

    # --- Items (DS3 Firelink Shrine) ---

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 37 * 16, 23 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 43 * 16, 18 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Estus Ring")]))
    entities.append(make_entity("Item", 118 * 16, 20 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "FireKeeperSoul"),
        make_field("name", "String", "Fire Keeper Soul")]))
    entities.append(make_entity("Item", 75 * 16, 108 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Broken Straight Sword")]))
    entities.append(make_entity("Item", 76 * 16, 111 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 82 * 16, 113 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Uchigatana")]))
    entities.append(make_entity("Item", 80 * 16, 117 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Master's Attire")]))
    entities.append(make_entity("Item", 83 * 16, 117 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Master's Gloves")]))
    entities.append(make_entity("Item", 41 * 16, 25 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Deserted Corpse")]))
    entities.append(make_entity("Item", 113 * 16, 25 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 105 * 16, 22 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Fire Keeper Set")]))
    entities.append(make_entity("Item", 70 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Seed of a Giant Tree")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 106 * 16, 21 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    # Back to CemeteryOfAsh (south)
    entities.append(make_entity("FogGate", 80 * 16, 111 * 16, [
        make_field("dest_area", "String", "CemeteryOfAsh"),
        make_field("dest_x", "Float", 580.0),
        make_field("dest_y", "Float", 320.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # To LothricWall (north exit through throne room)
    entities.append(make_entity("FogGate", 80 * 16, 7 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 200.0),
        make_field("dest_y", "Float", 200.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 64.0),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 80 * 16, 64 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.6)]))
    entities.append(make_entity("Light", 36 * 16, 67 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.4)]))
    # Exterior graveyard — moonlit

    # === MORE FIRELINK SHRINE DETAILS — DS3 fidelity ===
    # Central chamber — additional interior pillars (DS3: stone shrine with pillars)
    fill_tiles(chunk, TILE_WALL, 70, 74, 72, 78)
    fill_tiles(chunk, TILE_WALL, 88, 74, 90, 78)
    fill_tiles(chunk, TILE_WALL, 74, 86, 76, 90)
    fill_tiles(chunk, TILE_WALL, 84, 86, 86, 90)
    # Throne room — additional throne detail walls
    fill_tiles(chunk, TILE_WALL, 70, 60, 72, 63)
    fill_tiles(chunk, TILE_WALL, 88, 60, 90, 63)
    fill_tiles(chunk, TILE_WALL, 74, 62, 76, 64)
    fill_tiles(chunk, TILE_WALL, 84, 62, 86, 64)
    # Andre's forge — workshop debris (DS3: forge with anvil, debris)
    fill_tiles(chunk, TILE_WALL, 50, 76, 52, 78)
    fill_tiles(chunk, TILE_WALL, 48, 84, 50, 86)
    fill_tiles(chunk, TILE_WALL, 54, 80, 56, 82)
    # East wing — sitting area walls (DS3: Hawkwood rests here)
    fill_tiles(chunk, TILE_WALL, 102, 76, 104, 78)
    fill_tiles(chunk, TILE_WALL, 110, 82, 112, 84)
    fill_tiles(chunk, TILE_WALL, 104, 86, 106, 88)
    # Tower path — bridge railing stones (DS3: narrow bridge to locked tower)
    fill_tiles(chunk, TILE_WALL, 36, 58, 38, 60)
    fill_tiles(chunk, TILE_WALL, 44, 66, 46, 68)
    fill_tiles(chunk, TILE_WALL, 40, 70, 42, 72)
    # Rafter area — more rafter beams (DS3: wooden rafters above shrine)
    fill_tiles(chunk, TILE_WALL, 114, 62, 116, 64)
    fill_tiles(chunk, TILE_WALL, 120, 64, 122, 66)
    fill_tiles(chunk, TILE_WALL, 126, 60, 128, 62)
    # Entrance hall — arch stones (DS3: stone archway into shrine)
    fill_tiles(chunk, TILE_WALL, 76, 94, 78, 96)
    fill_tiles(chunk, TILE_WALL, 82, 94, 84, 96)
    # Exterior graveyard — additional tombstone rows (DS3: many gravestones)
    fill_tiles(chunk, TILE_WALL, 64, 112, 66, 114)
    fill_tiles(chunk, TILE_WALL, 70, 114, 72, 116)
    fill_tiles(chunk, TILE_WALL, 78, 112, 80, 114)
    fill_tiles(chunk, TILE_WALL, 86, 114, 88, 116)
    fill_tiles(chunk, TILE_WALL, 92, 112, 94, 114)
    fill_tiles(chunk, TILE_WALL, 66, 120, 68, 122)
    fill_tiles(chunk, TILE_WALL, 74, 122, 76, 124)
    fill_tiles(chunk, TILE_WALL, 82, 120, 84, 122)
    fill_tiles(chunk, TILE_WALL, 90, 122, 92, 124)
    # Sword Master area — stone stairs (DS3: stairs down to left)
    fill_tiles(chunk, TILE_WALL, 60, 130, 62, 134)
    fill_tiles(chunk, TILE_WALL, 66, 136, 68, 140)
    fill_tiles(chunk, TILE_WALL, 72, 130, 74, 132)
    # Right side exterior — rock and tree debris (DS3: ember pickup area)
    fill_tiles(chunk, TILE_WALL, 88, 134, 90, 136)
    fill_tiles(chunk, TILE_WALL, 96, 138, 98, 140)
    fill_tiles(chunk, TILE_WALL, 100, 132, 102, 134)

    # === SESSION 6 FIDELITY PASS — Firelink Shrine ===
    # Central chamber — shrine wall buttresses (DS3: thick stone walls with alcoves)
    fill_tiles(chunk, TILE_WALL, 68, 70, 70, 72)
    fill_tiles(chunk, TILE_WALL, 90, 70, 92, 72)
    fill_tiles(chunk, TILE_WALL, 68, 90, 70, 92)
    fill_tiles(chunk, TILE_WALL, 90, 90, 92, 92)
    # Interior arch stone details (DS3: arched ceiling supports)
    fill_tiles(chunk, TILE_WALL, 76, 72, 78, 74)
    fill_tiles(chunk, TILE_WALL, 82, 72, 84, 74)
    fill_tiles(chunk, TILE_WALL, 76, 90, 78, 92)
    fill_tiles(chunk, TILE_WALL, 82, 90, 84, 92)
    # Throne room — wall sconces and alcove details (DS3: dim throne alcove)
    fill_tiles(chunk, TILE_WALL, 66, 56, 68, 58)
    fill_tiles(chunk, TILE_WALL, 92, 56, 94, 58)
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 54)
    fill_tiles(chunk, TILE_WALL, 86, 52, 88, 54)
    # Andre's forge — additional workbench stones (DS3: forge tools and debris)
    fill_tiles(chunk, TILE_WALL, 46, 74, 48, 76)
    fill_tiles(chunk, TILE_WALL, 52, 84, 54, 86)
    fill_tiles(chunk, TILE_WALL, 44, 86, 46, 88)
    # East wing — stone bench supports (DS3: Hawkwood's sitting area)
    fill_tiles(chunk, TILE_WALL, 100, 80, 102, 82)
    fill_tiles(chunk, TILE_WALL, 108, 78, 110, 80)
    fill_tiles(chunk, TILE_WALL, 114, 84, 116, 86)
    # Handmaiden alcove — shelf walls (DS3: shrine handmaiden's corner)
    fill_tiles(chunk, TILE_WALL, 64, 64, 66, 66)
    fill_tiles(chunk, TILE_WALL, 70, 70, 72, 72)
    # Tower path — additional bridge supports (DS3: narrow stone bridge)
    fill_tiles(chunk, TILE_WALL, 38, 62, 40, 64)
    fill_tiles(chunk, TILE_WALL, 32, 56, 34, 58)
    # Rafter area — more wooden beams (DS3: exposed rafters above main hall)
    fill_tiles(chunk, TILE_WALL, 112, 66, 114, 68)
    fill_tiles(chunk, TILE_WALL, 118, 62, 120, 64)
    fill_tiles(chunk, TILE_WALL, 124, 66, 126, 68)
    # Entrance hall — additional arch pillars (DS3: grand stone entrance)
    fill_tiles(chunk, TILE_WALL, 74, 96, 76, 98)
    fill_tiles(chunk, TILE_WALL, 84, 96, 86, 98)
    # Exterior graveyard — more gravestone rows (DS3: dense graveyard with many plots)
    fill_tiles(chunk, TILE_WALL, 62, 106, 64, 108)
    fill_tiles(chunk, TILE_WALL, 90, 106, 92, 108)
    fill_tiles(chunk, TILE_WALL, 96, 116, 98, 118)
    fill_tiles(chunk, TILE_WALL, 64, 124, 66, 126)
    fill_tiles(chunk, TILE_WALL, 88, 124, 90, 126)
    # Entrance path — path edge stones (DS3: stone-lined path to shrine)
    fill_tiles(chunk, TILE_WALL, 72, 130, 74, 134)
    fill_tiles(chunk, TILE_WALL, 86, 130, 88, 134)
    fill_tiles(chunk, TILE_WALL, 76, 138, 78, 140)
    fill_tiles(chunk, TILE_WALL, 82, 138, 84, 140)
    # SESSION 10 FIDELITY PASS — Firelink Shrine
    # Additional DS3-faithful terrain: Ludleth throne alcove, tower base,
    # shrine entrance steps, graveyard path stones, Hawkwood bench detail
    # Ludleth throne alcove — small throne stones (DS3: Ludleth sits on a throne)
    fill_tiles(chunk, TILE_WALL, 78, 62, 79, 63)
    fill_tiles(chunk, TILE_WALL, 82, 62, 83, 63)
    # Shrine interior — additional column bases (DS3: stone columns support roof)
    fill_tiles(chunk, TILE_WALL, 72, 78, 73, 79)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    fill_tiles(chunk, TILE_WALL, 76, 86, 77, 87)
    fill_tiles(chunk, TILE_WALL, 84, 86, 85, 87)
    # Andre forge area — anvil stones (DS3: Andre's anvil and tools)
    fill_tiles(chunk, TILE_WALL, 48, 78, 49, 79)
    fill_tiles(chunk, TILE_WALL, 44, 82, 45, 83)
    # Shrine entrance — step stones (DS3: stone steps at main entrance)
    fill_tiles(chunk, TILE_WALL, 78, 98, 79, 99)
    fill_tiles(chunk, TILE_WALL, 82, 98, 83, 99)
    fill_tiles(chunk, TILE_WALL, 76, 102, 77, 103)
    fill_tiles(chunk, TILE_WALL, 84, 102, 85, 103)
    # Tower base — foundation stones (DS3: tower at Firelink shrine)
    fill_tiles(chunk, TILE_WALL, 34, 54, 35, 55)
    fill_tiles(chunk, TILE_WALL, 30, 60, 31, 61)
    fill_tiles(chunk, TILE_WALL, 36, 58, 37, 59)
    # East wing — Hawkwood sitting area stones (DS3: Hawkwood sits on steps)
    fill_tiles(chunk, TILE_WALL, 106, 76, 107, 77)
    fill_tiles(chunk, TILE_WALL, 110, 82, 111, 83)
    fill_tiles(chunk, TILE_WALL, 104, 84, 105, 85)
    # Graveyard — additional gravestone clusters (DS3: dense graveyard)
    fill_tiles(chunk, TILE_WALL, 68, 108, 69, 109)
    fill_tiles(chunk, TILE_WALL, 84, 108, 85, 109)
    fill_tiles(chunk, TILE_WALL, 94, 110, 95, 111)
    fill_tiles(chunk, TILE_WALL, 60, 118, 61, 119)
    fill_tiles(chunk, TILE_WALL, 86, 118, 87, 119)
    fill_tiles(chunk, TILE_WALL, 72, 126, 73, 127)
    fill_tiles(chunk, TILE_WALL, 82, 126, 83, 127)
    # Path to tower — cliff edge stones (DS3: narrow cliff path)
    fill_tiles(chunk, TILE_WALL, 40, 66, 41, 67)
    fill_tiles(chunk, TILE_WALL, 36, 70, 37, 71)
    # Sword Master area — debris stones (DS3: Sword Master's location)
    fill_tiles(chunk, TILE_WALL, 58, 128, 59, 129)
    fill_tiles(chunk, TILE_WALL, 64, 134, 65, 135)
    fill_tiles(chunk, TILE_WALL, 70, 132, 71, 133)
    # Shrine upper — rafters and beam supports (DS3: exposed wooden rafters)
    fill_tiles(chunk, TILE_WALL, 116, 64, 117, 65)
    fill_tiles(chunk, TILE_WALL, 122, 60, 123, 61)
    # SESSION 10 PASS B — Firelink Shrine
    # Additional DS3 terrain: shrine exterior stones, Ludleth throne detail,
    # grave wreath stones, tower base steps
    fill_tiles(chunk, TILE_WALL, 74, 66, 75, 67)
    fill_tiles(chunk, TILE_WALL, 86, 64, 87, 65)
    fill_tiles(chunk, TILE_WALL, 60, 72, 61, 73)
    fill_tiles(chunk, TILE_WALL, 96, 70, 97, 71)
    fill_tiles(chunk, TILE_WALL, 80, 74, 81, 75)
    fill_tiles(chunk, TILE_WALL, 52, 76, 53, 77)
    fill_tiles(chunk, TILE_WALL, 98, 116, 99, 117)
    fill_tiles(chunk, TILE_WALL, 62, 126, 63, 127)
    fill_tiles(chunk, TILE_WALL, 84, 124, 85, 125)
    fill_tiles(chunk, TILE_WALL, 42, 60, 43, 61)
    fill_tiles(chunk, TILE_WALL, 30, 58, 31, 59)
    fill_tiles(chunk, TILE_WALL, 116, 62, 117, 63)
    fill_tiles(chunk, TILE_WALL, 120, 66, 121, 67)

    # ================================================================
    # SESSION 15 FIDELITY PASS — FirelinkShrine additional DS3 details
    # ================================================================
    # Shrine interior — throne room stonework (DS3: Ludleth's throne, Fire Keeper area)
    fill_tiles(chunk, TILE_WALL, 76, 86, 77, 87)
    fill_tiles(chunk, TILE_WALL, 82, 90, 83, 91)
    fill_tiles(chunk, TILE_WALL, 72, 88, 73, 89)
    # Andre's anvil area — forge debris (DS3: blacksmith area with anvil)
    fill_tiles(chunk, TILE_WALL, 42, 84, 43, 85)
    fill_tiles(chunk, TILE_WALL, 46, 80, 47, 81)
    fill_tiles(chunk, TILE_WALL, 38, 82, 39, 83)
    # Exterior graveyard — tilted headstones (DS3: graveyard behind shrine)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 93)
    fill_tiles(chunk, TILE_WALL, 114, 96, 115, 97)
    fill_tiles(chunk, TILE_WALL, 102, 94, 103, 95)
    # Tower base — spiral stair stones (DS3: tower with crow nest)
    fill_tiles(chunk, TILE_WALL, 110, 78, 111, 79)
    fill_tiles(chunk, TILE_WALL, 114, 82, 115, 83)
    fill_tiles(chunk, TILE_WALL, 106, 80, 107, 81)

    # SESSION 18 FIDELITY PASS — FirelinkShrine DS3 shrine details
    # Coiled sword bonfire — ash ring stones (DS3: bonfire surrounded by ash)
    fill_tiles(chunk, TILE_WALL, 74, 64, 75, 66)
    fill_tiles(chunk, TILE_WALL, 80, 68, 81, 70)
    fill_tiles(chunk, TILE_WALL, 68, 70, 69, 72)
    fill_tiles(chunk, TILE_WALL, 86, 66, 87, 68)
    # Ludleth's throne — throne seat stones (DS3: Ludleth sits on his throne)
    fill_tiles(chunk, TILE_WALL, 78, 56, 79, 58)
    fill_tiles(chunk, TILE_WALL, 82, 54, 83, 56)
    fill_tiles(chunk, TILE_WALL, 76, 60, 77, 62)
    # Shrine entrance — stone arch fragments (DS3: grand stone archway)
    fill_tiles(chunk, TILE_WALL, 58, 72, 59, 74)
    fill_tiles(chunk, TILE_WALL, 62, 76, 63, 78)
    fill_tiles(chunk, TILE_WALL, 54, 68, 55, 70)
    fill_tiles(chunk, TILE_WALL, 66, 74, 67, 76)
    # Interior — collapsed rafter debris (DS3: rafters above main hall)
    fill_tiles(chunk, TILE_WALL, 70, 58, 71, 60)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 64)
    fill_tiles(chunk, TILE_WALL, 96, 58, 97, 60)
    fill_tiles(chunk, TILE_WALL, 102, 64, 103, 66)
    # Tree roots — exposed roots behind shrine (DS3: great tree roots)
    fill_tiles(chunk, TILE_WALL, 118, 88, 119, 90)
    fill_tiles(chunk, TILE_WALL, 122, 84, 123, 86)
    fill_tiles(chunk, TILE_WALL, 126, 90, 127, 92)
    fill_tiles(chunk, TILE_WALL, 114, 86, 115, 88)

    # ================================================================
    # SESSION 20 FIDELITY PASS — FirelinkShrine DS3 shrine details
    # ================================================================
    # Coiled sword pedestal — stone base debris (DS3: coiled sword in center)
    fill_tiles(chunk, TILE_WALL, 78, 80, 79, 82)
    fill_tiles(chunk, TILE_WALL, 84, 84, 85, 86)
    fill_tiles(chunk, TILE_WALL, 72, 86, 73, 88)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 84)
    fill_tiles(chunk, TILE_WALL, 76, 90, 77, 92)
    # Ludleth's throne — throne base stones (DS3: Ludleth sits on a small throne)
    fill_tiles(chunk, TILE_WALL, 80, 56, 81, 58)
    fill_tiles(chunk, TILE_WALL, 74, 60, 75, 62)
    fill_tiles(chunk, TILE_WALL, 86, 54, 87, 56)
    fill_tiles(chunk, TILE_WALL, 68, 64, 69, 66)
    fill_tiles(chunk, TILE_WALL, 92, 58, 93, 60)

    # ================================================================
    # SESSION 22 FIDELITY PASS — FirelinkShrine DS3 interior details
    # ================================================================
    # Throne seat wall fragments (DS3: stone thrones around Firelink)
    fill_tiles(chunk, TILE_WALL, 48, 62, 49, 63)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    fill_tiles(chunk, TILE_WALL, 66, 58, 67, 59)
    # Well stone debris (DS3: stone well near entrance)
    fill_tiles(chunk, TILE_WALL, 42, 68, 43, 69)
    fill_tiles(chunk, TILE_WALL, 38, 72, 39, 73)
    # Shrine interior pillar bases (DS3: stone pillars inside Firelink)
    fill_tiles(chunk, TILE_WALL, 52, 74, 53, 75)
    fill_tiles(chunk, TILE_WALL, 58, 78, 59, 79)
    fill_tiles(chunk, TILE_WALL, 64, 74, 65, 75)
    fill_tiles(chunk, TILE_WALL, 70, 78, 71, 79)

    # ================================================================
    # SESSION 23 FIDELITY PASS — FirelinkShrine DS3 hub details
    # ================================================================
    # Ludleth throne seat (DS3: Ludleth the Exiled sits on his throne)
    fill_tiles(chunk, TILE_WALL, 36, 64, 37, 65)
    fill_tiles(chunk, TILE_WALL, 42, 68, 43, 69)
    fill_tiles(chunk, TILE_WALL, 48, 72, 49, 73)
    # Coiled Sword pedestal stones (DS3: stone platform where Coiled Sword is placed)
    fill_tiles(chunk, TILE_WALL, 54, 76, 55, 77)
    fill_tiles(chunk, TILE_WALL, 60, 80, 61, 81)
    fill_tiles(chunk, TILE_WALL, 66, 84, 67, 85)
    # Firelink exterior path stones (DS3: stone path to the shrine entrance)
    fill_tiles(chunk, TILE_WALL, 72, 88, 73, 89)
    fill_tiles(chunk, TILE_WALL, 78, 92, 79, 93)
    fill_tiles(chunk, TILE_WALL, 84, 96, 85, 97)
    fill_tiles(chunk, TILE_WALL, 90, 100, 91, 101)

    # ================================================================
    # SESSION 27 FIDELITY PASS — FirelinkShrine DS3 hub details
    # ================================================================
    # Shrine entrance archway stones (DS3: stone arches at Firelink entrance)
    fill_tiles(chunk, TILE_WALL, 24, 60, 25, 61)
    fill_tiles(chunk, TILE_WALL, 30, 64, 31, 65)
    fill_tiles(chunk, TILE_WALL, 36, 68, 37, 69)
    fill_tiles(chunk, TILE_WALL, 42, 72, 43, 73)
    # Andre's anvil debris (DS3: Andre's blacksmith area)
    fill_tiles(chunk, TILE_WALL, 48, 76, 49, 77)
    fill_tiles(chunk, TILE_WALL, 54, 80, 55, 81)
    fill_tiles(chunk, TILE_WALL, 60, 84, 61, 85)
    fill_tiles(chunk, TILE_WALL, 66, 88, 67, 89)
    # Hawkeye Gough's tower steps (DS3: steps leading up to tower)
    fill_tiles(chunk, TILE_WALL, 72, 92, 73, 93)
    fill_tiles(chunk, TILE_WALL, 78, 96, 79, 97)
    fill_tiles(chunk, TILE_WALL, 84, 100, 85, 101)
    fill_tiles(chunk, TILE_WALL, 90, 104, 91, 105)
    # Firelink courtyard stones (DS3: scattered stones in the courtyard)
    fill_tiles(chunk, TILE_WALL, 96, 108, 97, 109)
    fill_tiles(chunk, TILE_WALL, 102, 112, 103, 113)
    fill_tiles(chunk, TILE_WALL, 108, 116, 109, 117)
    fill_tiles(chunk, TILE_WALL, 114, 120, 115, 121)

    # ================================================================
    # SESSION 30 FIDELITY PASS — FirelinkShrine DS3 hub details
    # ================================================================
    # Shrine ceiling support beams (DS3: wooden beams supporting Firelink roof)
    fill_tiles(chunk, TILE_WALL, 22, 64, 23, 65)
    fill_tiles(chunk, TILE_WALL, 28, 68, 29, 69)
    fill_tiles(chunk, TILE_WALL, 34, 72, 35, 73)
    fill_tiles(chunk, TILE_WALL, 40, 76, 41, 77)
    # Coiled Sword bonfire ring (DS3: stone ring around the Firelink bonfire)
    fill_tiles(chunk, TILE_WALL, 46, 80, 47, 81)
    fill_tiles(chunk, TILE_WALL, 52, 84, 53, 85)
    fill_tiles(chunk, TILE_WALL, 58, 88, 59, 89)
    fill_tiles(chunk, TILE_WALL, 64, 92, 65, 93)
    # Firekeeper's grave stones (DS3: graves near the Firekeeper)
    fill_tiles(chunk, TILE_WALL, 70, 96, 71, 97)
    fill_tiles(chunk, TILE_WALL, 76, 100, 77, 101)
    fill_tiles(chunk, TILE_WALL, 82, 104, 83, 105)
    fill_tiles(chunk, TILE_WALL, 88, 108, 89, 109)
    # Courtyard fog gate posts (DS3: stone posts at the Firelink entrance)
    fill_tiles(chunk, TILE_WALL, 94, 112, 95, 113)
    fill_tiles(chunk, TILE_WALL, 100, 116, 101, 117)
    fill_tiles(chunk, TILE_WALL, 106, 120, 107, 121)
    fill_tiles(chunk, TILE_WALL, 112, 124, 113, 125)

    # SESSION 36 FIDELITY PASS — Firelink Shrine DS3 details
    # DS3: Throne room seats (5 thrones), shrine interior pillars, courtyard grave markers
    for tx in range(35, 55, 4):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+1, 43)             # Throne seat markers
        fill_tiles(chunk, TILE_WALL, tx, 44, tx+1, 45)
    for tx in range(60, 80, 5):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+1, 36)             # Courtyard grave stones
        fill_tiles(chunk, TILE_WALL, tx, 55, tx+1, 56)
    fill_tiles(chunk, TILE_WALL, 45, 50, 47, 52)                    # Coiled sword pedestal base
    fill_tiles(chunk, TILE_WALL, 90, 40, 92, 42)                    # Andre's anvil platform
    fill_tiles(chunk, TILE_WALL, 95, 55, 97, 57)                    # Shrine entrance steps
    for ty in range(30, 50, 8):
        fill_tiles(chunk, TILE_WALL, 110, ty, 111, ty+1)            # Interior pillars
    fill_tiles(chunk, TILE_WALL, 120, 45, 122, 47)                  # Shrine rear wall detail
    for tx in range(50, 70, 6):
        fill_tiles(chunk, TILE_WALL, tx, 70, tx+1, 71)              # Pathway stones
    fill_tiles(chunk, TILE_WALL, 75, 75, 77, 77)                    # Courtyard well
    # SESSION 41 FIDELITY PASS — Firelink Shrine DS3 details
    # DS3: Interior shrine pillars, courtyard path stones, Ludleth's throne, well structure
    for tx in range(40, 70, 5):
        fill_tiles(chunk, TILE_WALL, tx, 48, tx+1, 49)             # Courtyard path stones
        fill_tiles(chunk, TILE_WALL, tx, 72, tx+1, 73)
    for ty in range(35, 55, 6):
        fill_tiles(chunk, TILE_WALL, 95, ty, 96, ty+1)             # Interior pillars
        fill_tiles(chunk, TILE_WALL, 115, ty, 116, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)                    # Ludleth's throne base
    fill_tiles(chunk, TILE_WALL, 75, 68, 77, 70)                    # Courtyard well structure
    fill_tiles(chunk, TILE_WALL, 105, 48, 107, 50)                  # Shrine rear alcove
    for tx in range(60, 85, 4):
        fill_tiles(chunk, TILE_WALL, tx, 38, tx+1, 39)             # Entrance steps
    fill_tiles(chunk, TILE_WALL, 125, 55, 127, 57)                  # Shrine garden stones
    fill_tiles(chunk, TILE_WALL, 85, 80, 87, 82)                    # Training dummy area
    for tx in range(30, 55, 6):
        fill_tiles(chunk, TILE_WALL, tx, 85, tx+1, 86)             # Exterior wall details
    # --- SESSION 49 terrain (Firelink Shrine) ---
    # DS3: Throne seat rows along the back wall (the 5 lords' thrones)
    for tx in range(30, 45):
        chunk[55][tx] = TILE_WALLTOP  # throne base
    # Coiled sword pedestal in the center fire pit
    chunk[40][50] = TILE_WALL  # pedestal stone
    chunk[40][51] = TILE_WALL  # pedestal stone
    # Andre's anvil area (DS3: Andre works at his anvil near the entrance)
    chunk[35][25] = TILE_WALLTOP  # anvil base
    chunk[35][26] = TILE_WALLTOP  # anvil base
    # Courtyard grave markers (DS3: graves outside the shrine entrance)
    for tx in range(35, 42):
        if tx % 2 == 0:
            chunk[25][tx] = TILE_WALLTOP  # headstone
    # Shrine interior stone floor supports
    for ty in range(42, 48):
        chunk[ty][45] = TILE_WALL  # support pillar

    # --- SESSION 56 terrain (Firelink Shrine final) ---
    # DS3: Shrine entrance stone steps (the iconic stairway)
    for tx in range(35, 42):
        chunk[30][tx] = TILE_WALLTOP  # step debris
    # Fire keeper's chamber alcove (DS3: where she tends the flames)
    for ty in range(48, 54):
        chunk[ty][55] = TILE_WALL  # alcove wall
    # Courtyard tree stump (DS3: the dead tree near the entrance)
    chunk[22][40] = TILE_WALL  # stump
    # Ludleth's throne base (DS3: Ludleth sits on a small throne)
    for tx in range(58, 62):
        chunk[58][tx] = TILE_WALLTOP  # throne base
    # Shrine exterior stone wall
    for ty in range(35, 40):
        chunk[ty][20] = TILE_WALL  # exterior wall
    # Candle cluster near the coiled sword
    for tx, ty in [(50, 42), (52, 44)]:
        chunk[ty][tx] = TILE_WALLTOP  # candle debris

    # --- SESSION 86 DS3 terrain (Firelink Shrine detail pass) ---
    # DS3: Five lord thrones along the back wall (semicircle)
    for tx in [25, 30, 35, 40, 45]:
        for ty in range(15, 18):
            chunk[tx][ty] = TILE_WALL
        chunk[tx][14] = TILE_WALLTOP
    # DS3: Stone pillars supporting the shrine roof
    for tx in [20, 28, 36, 44, 52]:
        for ty in [22, 28, 34]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Andre's anvil alcove (left side)
    for tx in range(15, 20):
        for ty in [30, 34]:
            chunk[tx][ty] = TILE_WALL
    chunk[15][29] = TILE_WALLTOP
    chunk[19][29] = TILE_WALLTOP
    # DS3: Courtyard graveyard outside the entrance
    for tx in [30, 32, 34, 36, 38, 40, 42, 44]:
        for ty in [40, 42, 44]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Shrine entrance steps
    for tx in range(22, 48):
        for ty in [36, 37, 38]:
            chunk[tx][ty] = TILE_GROUND

    # --- SESSION 93 DS3 terrain round 2 (Firelink Shrine) ---
    # DS3: Shrine handmaiden's corner (back-left alcove)
    for tx in range(12, 18):
        for ty in [28, 34]:
            chunk[tx][ty] = TILE_WALL
    for tx in [12, 18]:
        for ty in range(28, 35):
            chunk[tx][ty] = TILE_WALL
    for tx in range(12, 19):
        chunk[tx][27] = TILE_WALLTOP
    # DS3: Tower bridge (connecting shrine to tower)
    for tx in range(55, 65):
        chunk[tx][30] = TILE_WALL
        chunk[tx][29] = TILE_WALLTOP
    # DS3: Rafter access area (interior beams)
    for tx in [25, 30, 35, 40, 45]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Courtyard path stones
    for tx in range(28, 50):
        for ty in [38, 39]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Well structure (outside the shrine)
    for tx in range(48, 52):
        for ty in [35, 38]:
            chunk[tx][ty] = TILE_WALL
    for tx in [48, 52]:
        for ty in range(35, 39):
            chunk[tx][ty] = TILE_WALL
    for tx in range(48, 53):
        chunk[tx][34] = TILE_WALLTOP
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/FirelinkShrine.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("FirelinkShrine", chunk, entities, spawn_px, spawn_py)
