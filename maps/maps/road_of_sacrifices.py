from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    apply_doc_terrain, finalize_map,
)

def make_road_of_sacrifices():
    """Road of Sacrifices - dark forest with Crucifixion Woods hub.
    Faithful DS3 layout: narrow entry woods -> Halfway Fortress -> wide woods
    -> Corvian forest -> Crystal Sage cave. Branches to Farron Keep and Cathedral.
    Design doc: 3200x2400, sections define the progression west-to-east.
    """
    chunk = new_chunk(288, 224)
    entities = []

    # ================================================================
    # SECTION 1: Entry dark woods (top-left) - doc: x=0,y=0,w=800,h=800
    # Narrow forest path with root obstacles, player enters from Undead Settlement
    # DS3: winding path through dark forest with multiple Corvian ambushes
    # ================================================================
    carve_ellipse(chunk, 18, 18, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 14, 16, 40, 28)
    # Tree root obstacles
    fill_tiles(chunk, TILE_WALL, 20, 20, 22, 22)
    fill_tiles(chunk, TILE_WALL, 32, 24, 34, 26)
    # Additional tree clusters (DS3: dense dark woods at entry)
    fill_tiles(chunk, TILE_WALL, 16, 16, 17, 18)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 24)
    fill_tiles(chunk, TILE_WALL, 36, 18, 37, 20)
    fill_tiles(chunk, TILE_WALL, 28, 26, 29, 28)

    # ================================================================
    # SECTION 2: Halfway Fortress - doc: x=1000,y=500,w=500,h=500
    # Ruined stone fortress with Anri and Horace, interior rooms
    # DS3: stone ruin with bonfire room, Anri and Horace sitting inside
    # ================================================================
    carve_ellipse(chunk, 52, 28, 12, 10)
    # Stone walls creating fortress rooms
    fill_tiles(chunk, TILE_WALL, 48, 24, 49, 30)
    fill_tiles(chunk, TILE_WALL, 56, 26, 57, 32)
    # Fortress doorway pillars (DS3: arched stone entry)
    fill_tiles(chunk, TILE_WALL, 46, 26, 47, 28)
    fill_tiles(chunk, TILE_WALL, 58, 28, 59, 30)
    # Interior wall divider (DS3: room partition)
    fill_tiles(chunk, TILE_WALL, 50, 30, 54, 31)
    # Corridor connecting entry to fortress
    fill_tiles(chunk, TILE_GROUND, 38, 22, 52, 30)

    # ================================================================
    # SECTION 3: Crucifixion Woods - doc: x=1700,y=300,w=600,h=500
    # Wide wetland forest with branching paths, large central hub
    # DS3: sprawling wetland with shallow water, fallen trees, ruin walls
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 50, 35, 110, 75)
    # Large tree root clusters as wall obstacles
    fill_tiles(chunk, TILE_WALL, 58, 42, 62, 46)
    fill_tiles(chunk, TILE_WALL, 78, 50, 82, 54)
    fill_tiles(chunk, TILE_WALL, 95, 40, 99, 44)
    fill_tiles(chunk, TILE_WALL, 68, 62, 72, 66)
    fill_tiles(chunk, TILE_WALL, 88, 65, 92, 69)
    # Additional forest detail (DS3: scattered ruins and fallen trees)
    fill_tiles(chunk, TILE_WALL, 52, 38, 54, 40)
    fill_tiles(chunk, TILE_WALL, 64, 50, 66, 52)
    fill_tiles(chunk, TILE_WALL, 85, 45, 87, 47)
    fill_tiles(chunk, TILE_WALL, 102, 55, 104, 57)
    fill_tiles(chunk, TILE_WALL, 74, 70, 76, 72)
    # Ruined stone wall (DS3: collapsed wall section in woods)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 58)
    fill_tiles(chunk, TILE_WALL, 92, 58, 94, 60)
    # Fallen tree trunks
    fill_tiles(chunk, TILE_WALL, 108, 48, 110, 50)
    fill_tiles(chunk, TILE_WALL, 62, 68, 64, 70)

    # ================================================================
    # SECTION 4: Corvian Forest - doc: x=2200,y=800,w=600,h=600
    # Dense forest toward Crystal Sage, Black Knight patrols here
    # DS3: path narrows through dense trees with Corvian ambushes
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 85, 75, 130, 110)
    # Dense tree clusters
    fill_tiles(chunk, TILE_WALL, 95, 82, 98, 85)
    fill_tiles(chunk, TILE_WALL, 115, 90, 118, 93)
    fill_tiles(chunk, TILE_WALL, 100, 100, 103, 103)
    fill_tiles(chunk, TILE_WALL, 120, 78, 123, 81)
    # Additional dense tree walls (DS3: very dense forest section)
    fill_tiles(chunk, TILE_WALL, 88, 76, 90, 78)
    fill_tiles(chunk, TILE_WALL, 105, 85, 107, 87)
    fill_tiles(chunk, TILE_WALL, 125, 95, 127, 97)
    fill_tiles(chunk, TILE_WALL, 92, 95, 94, 97)
    fill_tiles(chunk, TILE_WALL, 110, 105, 112, 107)

    # ================================================================
    # SECTION 5: Crystal Sage cave - doc: x=2300,y=1200,w=800,h=600
    # Boss arena: open rocky cave with crystal obstacles
    # DS3: open arena with crystal growths and ruined pillars
    # ================================================================
    carve_ellipse(chunk, 130, 120, 20, 18)
    # Crystal obstacles inside the cave
    fill_tiles(chunk, TILE_WALL, 122, 114, 124, 116)
    fill_tiles(chunk, TILE_WALL, 138, 126, 140, 128)
    fill_tiles(chunk, TILE_WALL, 125, 130, 127, 132)
    # Additional crystal growths (DS3: scattered crystal formations)
    fill_tiles(chunk, TILE_WALL, 130, 115, 132, 117)
    fill_tiles(chunk, TILE_WALL, 118, 122, 120, 124)
    fill_tiles(chunk, TILE_WALL, 142, 118, 144, 120)
    # Corridor from Corvian Forest to Crystal Sage
    fill_tiles(chunk, TILE_GROUND, 120, 108, 135, 118)

    # ================================================================
    # BRANCH: Path south to Farron Keep
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 62, 72, 74, 135)
    carve_ellipse(chunk, 68, 132, 10, 8)

    # ================================================================
    # BRANCH: Path east to Cathedral Deep
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 108, 60, 120, 70)
    carve_ellipse(chunk, 118, 65, 8, 6)

    # ================================================================
    # Connection corridors to ensure flow
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 42, 30, 55, 38)

    # ================================================================
    # ADDITIONAL DS3 ROAD OF SACRIFICES — forest depth, ruin details
    # ================================================================
    # Entry dark woods — more tree clusters (DS3: dense dark forest with Corvians)
    fill_tiles(chunk, TILE_WALL, 18, 22, 19, 24)
    fill_tiles(chunk, TILE_WALL, 30, 18, 31, 20)
    fill_tiles(chunk, TILE_WALL, 22, 26, 23, 28)
    fill_tiles(chunk, TILE_WALL, 34, 22, 35, 24)
    # Halfway Fortress — more interior walls (DS3: multi-room stone ruin)
    fill_tiles(chunk, TILE_WALL, 44, 28, 45, 32)
    fill_tiles(chunk, TILE_WALL, 60, 30, 61, 34)
    fill_tiles(chunk, TILE_WALL, 50, 34, 52, 36)
    fill_tiles(chunk, TILE_WALL, 55, 24, 56, 26)
    # Crucifixion Woods — more wetland detail (DS3: sprawling marsh with ruins)
    fill_tiles(chunk, TILE_WALL, 56, 42, 57, 44)
    fill_tiles(chunk, TILE_WALL, 70, 48, 71, 50)
    fill_tiles(chunk, TILE_WALL, 80, 55, 81, 57)
    fill_tiles(chunk, TILE_WALL, 98, 48, 99, 50)
    fill_tiles(chunk, TILE_WALL, 65, 56, 66, 58)
    fill_tiles(chunk, TILE_WALL, 90, 62, 91, 64)
    fill_tiles(chunk, TILE_WALL, 105, 60, 106, 62)
    fill_tiles(chunk, TILE_WALL, 75, 72, 76, 74)
    fill_tiles(chunk, TILE_WALL, 58, 65, 59, 67)
    # Corvian Forest — additional dense trees (DS3: very thick forest near Crystal Sage)
    fill_tiles(chunk, TILE_WALL, 90, 80, 91, 82)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 90)
    fill_tiles(chunk, TILE_WALL, 112, 95, 113, 97)
    fill_tiles(chunk, TILE_WALL, 118, 82, 119, 84)
    fill_tiles(chunk, TILE_WALL, 96, 98, 97, 100)
    fill_tiles(chunk, TILE_WALL, 108, 102, 109, 104)
    fill_tiles(chunk, TILE_WALL, 128, 88, 129, 90)
    # Crystal Sage cave — more crystal formations (DS3: crystal growths everywhere)
    fill_tiles(chunk, TILE_WALL, 126, 118, 127, 120)
    fill_tiles(chunk, TILE_WALL, 134, 124, 135, 126)
    fill_tiles(chunk, TILE_WALL, 140, 114, 141, 116)
    fill_tiles(chunk, TILE_WALL, 122, 128, 123, 130)
    fill_tiles(chunk, TILE_WALL, 136, 130, 137, 132)
    # Farron Keep branch — swamp approach ruins (DS3: crumbling path to poison swamp)
    fill_tiles(chunk, TILE_WALL, 64, 78, 65, 80)
    fill_tiles(chunk, TILE_WALL, 70, 85, 71, 87)
    fill_tiles(chunk, TILE_WALL, 66, 95, 67, 97)
    fill_tiles(chunk, TILE_WALL, 72, 105, 73, 107)
    fill_tiles(chunk, TILE_WALL, 68, 115, 69, 117)
    # Cathedral branch — stone gate approach (DS3: path to Cathedral of the Deep)
    fill_tiles(chunk, TILE_WALL, 110, 62, 111, 64)
    fill_tiles(chunk, TILE_WALL, 115, 66, 116, 68)

    # ================================================================
    # SESSION 9 FIDELITY PASS — RoadOfSacrifices architectural details
    # ================================================================
    # Entry forest path — mossy root clusters (DS3: forest with exposed roots)
    fill_tiles(chunk, TILE_WALL, 22, 18, 23, 19)
    fill_tiles(chunk, TILE_WALL, 26, 22, 27, 23)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 27)
    fill_tiles(chunk, TILE_WALL, 30, 16, 31, 17)
    # Halfway Fortress — collapsed stone arch (DS3: ruined fortress bridge)
    fill_tiles(chunk, TILE_WALL, 48, 28, 49, 29)
    fill_tiles(chunk, TILE_WALL, 52, 32, 53, 33)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 37)
    fill_tiles(chunk, TILE_WALL, 56, 26, 57, 27)
    fill_tiles(chunk, TILE_WALL, 50, 38, 51, 39)
    # Crucifixion Woods — crucified hollow posts (DS3: hollows crucified on trees)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 43)
    fill_tiles(chunk, TILE_WALL, 68, 46, 69, 47)
    fill_tiles(chunk, TILE_WALL, 60, 50, 61, 51)
    fill_tiles(chunk, TILE_WALL, 72, 40, 73, 41)
    fill_tiles(chunk, TILE_WALL, 66, 52, 67, 53)
    # Wetland shallows — submerged stone paths (DS3: flooded forest area)
    fill_tiles(chunk, TILE_WALL, 76, 56, 77, 57)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 72, 64, 73, 65)
    fill_tiles(chunk, TILE_WALL, 84, 54, 85, 55)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    # Black Knight ruins — ruined arch stones (DS3: Black Knight patrols ruins)
    fill_tiles(chunk, TILE_WALL, 88, 70, 89, 71)
    fill_tiles(chunk, TILE_WALL, 92, 74, 93, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    fill_tiles(chunk, TILE_WALL, 96, 68, 97, 69)
    # Corvian forest — fallen nest structures (DS3: Corvians in trees)
    fill_tiles(chunk, TILE_WALL, 100, 82, 101, 83)
    fill_tiles(chunk, TILE_WALL, 104, 86, 105, 87)
    fill_tiles(chunk, TILE_WALL, 96, 90, 97, 91)
    fill_tiles(chunk, TILE_WALL, 108, 80, 109, 81)
    fill_tiles(chunk, TILE_WALL, 102, 92, 103, 93)
    # Crystal Sage cave — crystal-encrusted pillars (DS3: crystal formations)
    fill_tiles(chunk, TILE_WALL, 112, 96, 113, 97)
    fill_tiles(chunk, TILE_WALL, 116, 100, 117, 101)
    fill_tiles(chunk, TILE_WALL, 108, 104, 109, 105)
    fill_tiles(chunk, TILE_WALL, 120, 94, 121, 95)
    fill_tiles(chunk, TILE_WALL, 114, 106, 115, 107)
    # Farron approach — mossy stone gate arch (DS3: stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 124, 110, 125, 111)
    fill_tiles(chunk, TILE_WALL, 128, 114, 129, 115)
    fill_tiles(chunk, TILE_WALL, 120, 118, 121, 119)
    fill_tiles(chunk, TILE_WALL, 132, 108, 133, 109)

    # ================================================================
    # DS3 STRUCTURAL WALLS — Road of Sacrifices forest and ruins
    # DS3: dense forest with Corvian ambush, ruined fortress, crystal caves
    # ================================================================
    # Corvian woods — tree obstacle walls (DS3: dense forest with Corvian enemies)
    fill_tiles(chunk, TILE_WALL, 30, 38, 34, 44)    # Tree cluster left
    fill_tiles(chunk, TILE_WALL, 46, 36, 50, 42)    # Tree cluster right
    fill_tiles(chunk, TILE_WALL, 38, 48, 42, 54)    # Tree cluster center
    # Halfway Fortress — ruined stone walls (DS3: stone fortress with Anri/Horace)
    fill_tiles(chunk, TILE_WALL, 54, 56, 58, 62)    # Fortress wall left
    fill_tiles(chunk, TILE_WALL, 66, 54, 70, 60)    # Fortress wall right
    fill_tiles(chunk, TILE_WALL, 60, 62, 64, 66)    # Fortress interior wall
    # Crucifixion woods — wetland tree clusters (DS3: wide wetland with Exiles)
    fill_tiles(chunk, TILE_WALL, 40, 68, 44, 74)    # Wetland tree cluster
    fill_tiles(chunk, TILE_WALL, 56, 72, 60, 78)    # Wetland tree cluster 2
    fill_tiles(chunk, TILE_WALL, 48, 82, 52, 88)    # Wetland tree cluster 3
    # Crystal Sage arena — crystal formations (DS3: crystal growths everywhere)
    fill_tiles(chunk, TILE_WALL, 120, 100, 124, 106) # Crystal wall left
    fill_tiles(chunk, TILE_WALL, 136, 96, 140, 102)  # Crystal wall right
    fill_tiles(chunk, TILE_WALL, 128, 108, 132, 114)  # Crystal wall center
    fill_tiles(chunk, TILE_WALL, 142, 108, 146, 114)  # Crystal wall far
    # Black Knight patrol area — stone ruins (DS3: Black Knight patrols forest)
    fill_tiles(chunk, TILE_WALL, 86, 68, 90, 74)    # Ruin wall left
    fill_tiles(chunk, TILE_WALL, 100, 72, 104, 78)   # Ruin wall right

        # --- ENTITIES ---
    spawn_px, spawn_py = 18 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 32 * 16, 32 * 16))    # Road of Sacrifices entry
    entities.append(make_entity("Bonfire", 91 * 16, 71 * 16))    # Halfway Fortress
    entities.append(make_entity("Bonfire", 157 * 16, 96 * 16))    # Crucifixion Woods
    entities.append(make_entity("Bonfire", 210 * 16, 148 * 16))  # Crystal Sage

    # Boss - Crystal Sage
    entities.append(make_entity("BossSpawn", 210 * 16, 148 * 16))

    # Enemies - DS3 faithful: Corvians (many throughout forest), Lycanthropes,
    # Corvian Storytellers, Black Knight, Exiles, Crabs, Crystal Lizards

    
    # --- DS3 faithful enemies (RoadOfSacrifices) ---
    # Corvian (21)
    for tx, ty in [(25, 20), (35, 24), (28, 22), (56, 35), (62, 40), (75, 52), (82, 58), (65, 45), (78, 48), (90, 50), (58, 55), (118, 88), (122, 92), (125, 96), (112, 82), (128, 85), (68, 80), (72, 85), (64, 82), (75, 84), (62, 92)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Corvian", "Corvian"))]))
    # LesserCrab (3 additional — DS3: small crabs near water/swampy forest floor)
    for tx, ty in [(42, 26), (48, 28), (45, 32)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LesserCrab", "Dog"))]))
    # Corvian (3 additional — DS3: corvian ambushes near Crucifixion Woods lower paths)
    for tx, ty in [(71, 101), (110, 95), (115, 100)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Corvian", "Corvian"))]))
    # DarkMage (4)
    entities.append(make_entity("Enemy", 70 * 16, 48 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 88 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 125 * 16, 115 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 135 * 16, 118 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    # LycanthropeHunter (2)
    entities.append(make_entity("Enemy", 72 * 16, 55 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LycanthropeHunter", "LycanthropeHunter"))]))
    entities.append(make_entity("Enemy", 85 * 16, 60 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LycanthropeHunter", "LycanthropeHunter"))]))
    # CrystalLizard (3)
    entities.append(make_entity("Enemy", 50 * 16, 26 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 96 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 112 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # PoisonhornBug (4)
    entities.append(make_entity("Enemy", 65 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PoisonhornBug", "PoisonhornBug"))]))
    entities.append(make_entity("Enemy", 70 * 16, 65 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PoisonhornBug", "PoisonhornBug"))]))
    entities.append(make_entity("Enemy", 62 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PoisonhornBug", "PoisonhornBug"))]))
    entities.append(make_entity("Enemy", 58 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PoisonhornBug", "PoisonhornBug"))]))
    # GreatCrab (1)
    entities.append(make_entity("Enemy", 76 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GreatCrab", "GreatCrab"))]))
    # LesserCrab (2)
    entities.append(make_entity("Enemy", 78 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LesserCrab", "LesserCrab"))]))
    entities.append(make_entity("Enemy", 80 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LesserCrab", "LesserCrab"))]))
    # Lycanthrope (5) — DS3: branch-wielding hollows in Crucifixion Woods
    for tx, ty in [(92, 78), (96, 82), (100, 86), (105, 80), (88, 85)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Lycanthrope", "PeasantHollow"))]))
    # Madwoman (1) — DS3: enemy NPC near beginning with Butcher Knife
    entities.append(make_entity("Enemy", 38 * 16, 30 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Madwoman", "PeasantHollow"))]))
    # BlackKnight (1) — DS3: patrols near Farron Coal room
    entities.append(make_entity("Enemy", 108 * 16, 85 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))
    # Basilisk (2)
    entities.append(make_entity("Enemy", 61 * 16, 87 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 53 * 16, 90 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    # ExileWarrior (2) — DS3: two NPCs guarding Farron Keep entrance (Great Club + Exile Greatsword)
    entities.append(make_entity("Enemy", 108 * 16, 100 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ExileWarrior", "Knight"))]))
    entities.append(make_entity("Enemy", 115 * 16, 105 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ExileWarrior", "Knight"))]))
    # MiniBoss (1) — Crystal Sage
    entities.append(make_entity("Enemy", 130 * 16, 112 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- Items (DS3 Road of Sacrifices) — accurate from wiki ---

    entities.append(make_entity("Npc", 87 * 16, 71 * 16, [make_field("name", "String", "Anri of Astora"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#C0C0C0"), make_field("dialogue", "String", "Oh, hello. We meet again|I am Anri of Astora, and this is Horace the Hushed|We journey to find the Lords of Cinder|Won't you join us?|I have no love for the smaller roads, they are treacherous|The Cathedral of the Deep lies ahead, tread carefully|Horace and I have been together for a long time now")]))
    entities.append(make_entity("Npc", 93 * 16, 71 * 16, [make_field("name", "String", "Horace the Hushed"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#606060"), make_field("dialogue", "String", "...|(nods silently)|(gestures toward Anri)|(adjusts helmet)")]))

    # Orbeck of Vinheim — sorcery teacher in the ruins (DS3: found in a side room of the Crucifixion Woods ruins)
    entities.append(make_entity("Npc", 157 * 16, 115 * 16, [make_field("name", "String", "Orbeck of Vinheim"), make_field("kind", "LocalEnum.NpcKind", "Merchant"), make_field("color", "Color", "#7090B0"), make_field("dialogue", "String", "Orbeck of Vinheim. A sorcerer, and an assassin|I wish to repay my debt to you|Bring me scrolls, and I shall decipher their sorceries|The Vinheim scholars would be proud|Sorcery requires dedication and talent|Show me you have both, and we shall prosper")]))

    # Fog Gate back to UndeadSettlement (entrance from settlement)
    entities.append(make_entity("FogGate", 32 * 16, 26 * 16, [
        make_field("dest_area", "String", "UndeadSettlement"),
        make_field("dest_x", "Float", 2368.0),
        make_field("dest_y", "Float", 880.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Fog Gate to FarronKeep
    entities.append(make_entity("FogGate", 145 * 16, 156 * 16, [
        make_field("dest_area", "String", "FarronKeep"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Fog Gate to CathedralDeep
    entities.append(make_entity("FogGate", 243 * 16, 93 * 16, [
        make_field("dest_area", "String", "CathedralDeep"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Lights
    entities.append(make_entity("Light", 18 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.4), make_field("g", "Float", 0.5), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 52 * 16, 30 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 80 * 16, 45 * 16, [make_field("radius", "Float", 200.0), make_field("r", "Float", 0.3), make_field("g", "Float", 0.5), make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 130 * 16, 112 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.4), make_field("b", "Float", 0.9), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — Road of Sacrifices DS3 fidelity ===
    # Entry dark woods — additional tree root clusters (DS3: dense forest entry)
    fill_tiles(chunk, TILE_WALL, 22, 25, 24, 28)
    fill_tiles(chunk, TILE_WALL, 38, 28, 40, 30)
    fill_tiles(chunk, TILE_WALL, 55, 22, 57, 24)
    fill_tiles(chunk, TILE_WALL, 30, 38, 32, 40)
    # Overturned coach debris (DS3: overturned carriage in entry path)
    fill_tiles(chunk, TILE_WALL, 26, 20, 28, 22)
    # Halfway Fortress — interior room partitions (DS3: stone ruin with multiple rooms)
    fill_tiles(chunk, TILE_WALL, 48, 42, 50, 44)
    fill_tiles(chunk, TILE_WALL, 65, 35, 67, 37)
    fill_tiles(chunk, TILE_WALL, 53, 28, 55, 30)
    fill_tiles(chunk, TILE_WALL, 46, 32, 48, 34)
    # Crucifixion Woods — wetland forest debris (DS3: sprawling wetland with ruins)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 57)
    fill_tiles(chunk, TILE_WALL, 52, 58, 54, 60)
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 50)
    fill_tiles(chunk, TILE_WALL, 42, 68, 44, 70)
    fill_tiles(chunk, TILE_WALL, 60, 72, 62, 74)
    fill_tiles(chunk, TILE_WALL, 80, 55, 82, 57)
    # Fallen trees across shallow water (DS3: horizontal logs in swamp)
    fill_tiles(chunk, TILE_WALL, 56, 64, 58, 66)
    fill_tiles(chunk, TILE_WALL, 84, 62, 86, 64)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    # Crucifixion crosses debris (DS3: crosses scattered throughout the woods)
    fill_tiles(chunk, TILE_WALL, 66, 42, 67, 44)
    fill_tiles(chunk, TILE_WALL, 78, 52, 79, 54)
    fill_tiles(chunk, TILE_WALL, 90, 46, 91, 48)
    # Ruined stone structure walls (DS3: Black Knight patrols these ruins)
    fill_tiles(chunk, TILE_WALL, 25, 78, 27, 80)
    fill_tiles(chunk, TILE_WALL, 90, 65, 92, 67)
    fill_tiles(chunk, TILE_WALL, 104, 78, 106, 82)
    fill_tiles(chunk, TILE_WALL, 112, 84, 114, 88)
    # Farron Keep gate fortress ruins (DS3: stone gate with Exile guards)
    fill_tiles(chunk, TILE_WALL, 66, 125, 70, 128)
    fill_tiles(chunk, TILE_WALL, 72, 130, 76, 133)
    fill_tiles(chunk, TILE_WALL, 64, 118, 66, 120)
    # Corvian forest dense trees (DS3: dense forest path narrows significantly)
    fill_tiles(chunk, TILE_WALL, 118, 102, 120, 104)
    fill_tiles(chunk, TILE_WALL, 135, 108, 137, 110)
    fill_tiles(chunk, TILE_WALL, 125, 115, 127, 118)
    fill_tiles(chunk, TILE_WALL, 96, 92, 98, 94)
    fill_tiles(chunk, TILE_WALL, 130, 95, 132, 98)
    fill_tiles(chunk, TILE_WALL, 116, 88, 118, 90)
    # Crystal Sage cave crystal formations (DS3: scattered crystal growths in boss arena)
    fill_tiles(chunk, TILE_WALL, 134, 120, 136, 122)
    fill_tiles(chunk, TILE_WALL, 122, 128, 124, 130)
    fill_tiles(chunk, TILE_WALL, 140, 114, 142, 116)
    # Cathedral road — dense tree walls (DS3: forest path to Cathedral of the Deep)
    fill_tiles(chunk, TILE_WALL, 114, 62, 116, 64)
    fill_tiles(chunk, TILE_WALL, 108, 68, 110, 70)
    # Orbeck's room interior (DS3: small side room in ruins with bookshelves)
    fill_tiles(chunk, TILE_WALL, 80, 58, 82, 60)
    fill_tiles(chunk, TILE_WALL, 84, 62, 86, 64)

    # === SESSION 8 FIDELITY PASS — Road of Sacrifices ===
    # Entry woods — mossy root clusters and fungus-covered stones (DS3: dark forest floor)
    fill_tiles(chunk, TILE_WALL, 14, 14, 15, 16)
    fill_tiles(chunk, TILE_WALL, 40, 16, 41, 18)
    fill_tiles(chunk, TILE_WALL, 26, 28, 27, 30)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 32)
    # Halfway Fortress — collapsed stone arch fragments (DS3: ruined stone tower)
    fill_tiles(chunk, TILE_WALL, 42, 26, 43, 28)
    fill_tiles(chunk, TILE_WALL, 62, 32, 63, 34)
    fill_tiles(chunk, TILE_WALL, 48, 36, 49, 38)
    # Crucifixion Woods — crucified hollow posts (DS3: multiple crucified corpses in woods)
    fill_tiles(chunk, TILE_WALL, 60, 38, 61, 40)
    fill_tiles(chunk, TILE_WALL, 84, 52, 85, 54)
    fill_tiles(chunk, TILE_WALL, 68, 54, 69, 56)
    fill_tiles(chunk, TILE_WALL, 92, 56, 93, 58)
    # Wetland shallows — submerged stone paths (DS3: shallow water with stepping stones)
    fill_tiles(chunk, TILE_WALL, 64, 66, 65, 68)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 70)
    fill_tiles(chunk, TILE_WALL, 70, 74, 71, 76)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 72)
    # Black Knight ruins — more ruined arch stones (DS3: stone ruin with Black Knight)
    fill_tiles(chunk, TILE_WALL, 106, 82, 107, 84)
    fill_tiles(chunk, TILE_WALL, 114, 86, 115, 88)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 92)
    # Corvian forest — fallen nest structures (DS3: Corvian nests in trees)
    fill_tiles(chunk, TILE_WALL, 122, 78, 123, 80)
    fill_tiles(chunk, TILE_WALL, 130, 92, 131, 94)
    fill_tiles(chunk, TILE_WALL, 114, 100, 115, 102)
    fill_tiles(chunk, TILE_WALL, 134, 102, 135, 104)
    # Crystal Sage cave — crystal-encrusted pillars (DS3: glowing crystal formations)
    fill_tiles(chunk, TILE_WALL, 132, 112, 133, 114)
    fill_tiles(chunk, TILE_WALL, 124, 134, 125, 136)
    fill_tiles(chunk, TILE_WALL, 138, 128, 139, 130)
    # Farron approach — mossy stone gate arch (DS3: stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 62, 122, 63, 124)
    fill_tiles(chunk, TILE_WALL, 74, 128, 75, 130)
    # SESSION 10 FIDELITY PASS — Road of Sacrifices
    # Additional DS3-faithful terrain: mossy root clusters, crucified hollow posts,
    # wetland submerged path edges, crystal pillar formations, ruin debris
    # Entry dark woods — root cluster debris (DS3: dark forest with exposed roots)
    fill_tiles(chunk, TILE_WALL, 20, 20, 21, 21)
    fill_tiles(chunk, TILE_WALL, 24, 24, 25, 25)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    fill_tiles(chunk, TILE_WALL, 16, 26, 17, 27)
    # Halfway Fortress — fortress wall debris (DS3: small fortress at midpoint)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 31)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)
    fill_tiles(chunk, TILE_WALL, 44, 32, 45, 33)
    # Crucifixion Woods — crucified hollow posts (DS3: crucified hollows on trees)
    fill_tiles(chunk, TILE_WALL, 52, 38, 53, 39)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 43)
    fill_tiles(chunk, TILE_WALL, 54, 44, 55, 45)
    fill_tiles(chunk, TILE_WALL, 60, 40, 61, 41)
    fill_tiles(chunk, TILE_WALL, 66, 38, 67, 39)
    # Wetland area — submerged path edges (DS3: flooded paths in woods)
    fill_tiles(chunk, TILE_WALL, 72, 46, 73, 47)
    fill_tiles(chunk, TILE_WALL, 78, 50, 79, 51)
    fill_tiles(chunk, TILE_WALL, 76, 52, 77, 53)
    fill_tiles(chunk, TILE_WALL, 82, 48, 83, 49)
    fill_tiles(chunk, TILE_WALL, 68, 54, 69, 55)
    # Crystal Sage area — crystal pillar formations (DS3: crystals near boss)
    fill_tiles(chunk, TILE_WALL, 108, 80, 109, 81)
    fill_tiles(chunk, TILE_WALL, 114, 84, 115, 85)
    fill_tiles(chunk, TILE_WALL, 120, 82, 121, 83)
    fill_tiles(chunk, TILE_WALL, 126, 86, 127, 87)
    fill_tiles(chunk, TILE_WALL, 110, 88, 111, 89)
    fill_tiles(chunk, TILE_WALL, 118, 90, 119, 91)
    # Corvian forest — fallen tree debris (DS3: dense forest with fallen trees)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)
    fill_tiles(chunk, TILE_WALL, 94, 66, 95, 67)
    fill_tiles(chunk, TILE_WALL, 100, 64, 101, 65)
    fill_tiles(chunk, TILE_WALL, 84, 68, 85, 69)
    fill_tiles(chunk, TILE_WALL, 92, 70, 93, 71)
    # Farron Keep gate — ruin wall debris (DS3: stone gate to Farron Keep)
    fill_tiles(chunk, TILE_WALL, 104, 96, 105, 97)
    fill_tiles(chunk, TILE_WALL, 110, 100, 111, 101)
    fill_tiles(chunk, TILE_WALL, 106, 102, 107, 103)
    fill_tiles(chunk, TILE_WALL, 116, 98, 117, 99)

    # ================================================================
    # SESSION 13 FIDELITY PASS — Road of Sacrifices DS3 architecture
    # ================================================================
    # Entry woods — fallen log bridges (DS3: paths through dense dark forest)
    fill_tiles(chunk, TILE_WALL, 28, 22, 29, 23)
    fill_tiles(chunk, TILE_WALL, 32, 26, 33, 27)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 31)
    fill_tiles(chunk, TILE_WALL, 40, 28, 41, 29)
    fill_tiles(chunk, TILE_WALL, 24, 34, 25, 35)
    # Halfway Fortress — stone battlement debris (DS3: ruined fortress with merchants)
    fill_tiles(chunk, TILE_WALL, 46, 30, 47, 31)
    fill_tiles(chunk, TILE_WALL, 50, 34, 51, 35)
    fill_tiles(chunk, TILE_WALL, 48, 26, 49, 27)
    fill_tiles(chunk, TILE_WALL, 44, 38, 45, 39)
    fill_tiles(chunk, TILE_WALL, 52, 28, 53, 29)
    # Crucifixion crosses — additional cross posts (DS3: many crucified hollows)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 45)
    fill_tiles(chunk, TILE_WALL, 70, 48, 71, 49)
    fill_tiles(chunk, TILE_WALL, 74, 42, 75, 43)
    fill_tiles(chunk, TILE_WALL, 80, 54, 81, 55)
    fill_tiles(chunk, TILE_WALL, 86, 50, 87, 51)
    fill_tiles(chunk, TILE_WALL, 62, 58, 63, 59)
    # Poison swamp — bog gas vents (DS3: toxic pools in lower woods)
    fill_tiles(chunk, TILE_WALL, 76, 60, 77, 61)
    fill_tiles(chunk, TILE_WALL, 82, 64, 83, 65)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)
    fill_tiles(chunk, TILE_WALL, 80, 72, 81, 73)
    # Corvian forest canopy — dense tree root clusters (DS3: thick forest)
    fill_tiles(chunk, TILE_WALL, 96, 74, 97, 75)
    fill_tiles(chunk, TILE_WALL, 102, 78, 103, 79)
    fill_tiles(chunk, TILE_WALL, 108, 76, 109, 77)
    fill_tiles(chunk, TILE_WALL, 114, 82, 115, 83)
    fill_tiles(chunk, TILE_WALL, 100, 86, 101, 87)
    fill_tiles(chunk, TILE_WALL, 120, 90, 121, 91)
    # Crystal Sage cave entrance — crystal formations (DS3: glowing crystals)
    fill_tiles(chunk, TILE_WALL, 130, 108, 131, 109)
    fill_tiles(chunk, TILE_WALL, 136, 112, 137, 113)
    fill_tiles(chunk, TILE_WALL, 124, 116, 125, 117)
    fill_tiles(chunk, TILE_WALL, 132, 120, 133, 121)
    fill_tiles(chunk, TILE_WALL, 128, 124, 129, 125)

    # ================================================================
    # SESSION 15 FIDELITY PASS — RoadOfSacrifices additional DS3 details
    # ================================================================
    # Crucifixion Woods — additional crucifixion posts (DS3: many crucified bodies)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 43)
    fill_tiles(chunk, TILE_WALL, 66, 50, 67, 51)
    fill_tiles(chunk, TILE_WALL, 72, 56, 73, 57)
    fill_tiles(chunk, TILE_WALL, 78, 48, 79, 49)
    # Farron Keep gate approach — ruined wall fragments (DS3: stone archway to swamp)
    fill_tiles(chunk, TILE_WALL, 108, 92, 109, 94)
    fill_tiles(chunk, TILE_WALL, 114, 96, 115, 98)
    fill_tiles(chunk, TILE_WALL, 120, 94, 121, 96)
    fill_tiles(chunk, TILE_WALL, 104, 100, 105, 102)
    # Cathedral Road — moss-covered stone path (DS3: path branching to Cathedral of the Deep)
    fill_tiles(chunk, TILE_WALL, 140, 108, 141, 110)
    fill_tiles(chunk, TILE_WALL, 146, 112, 147, 114)
    fill_tiles(chunk, TILE_WALL, 136, 116, 137, 118)
    fill_tiles(chunk, TILE_WALL, 142, 120, 143, 122)
    # Crystal Sage approach — crystal shard debris (DS3: magical crystal formations)
    fill_tiles(chunk, TILE_WALL, 122, 110, 123, 112)
    fill_tiles(chunk, TILE_WALL, 134, 114, 135, 116)
    fill_tiles(chunk, TILE_WALL, 118, 118, 119, 120)

    # ================================================================
    # SESSION 17 FIDELITY PASS — RoadOfSacrifices DS3 forest depth
    # ================================================================
    # Entry woods — moss-covered root tangles (DS3: dark forest with exposed roots)
    fill_tiles(chunk, TILE_WALL, 20, 14, 21, 16)
    fill_tiles(chunk, TILE_WALL, 26, 20, 27, 22)
    fill_tiles(chunk, TILE_WALL, 32, 16, 33, 18)
    fill_tiles(chunk, TILE_WALL, 38, 22, 39, 24)
    # Halfway Fortress — collapsed wall sections (DS3: ruined stone fortress)
    fill_tiles(chunk, TILE_WALL, 42, 30, 43, 32)
    fill_tiles(chunk, TILE_WALL, 62, 32, 63, 34)
    fill_tiles(chunk, TILE_WALL, 46, 34, 47, 36)
    fill_tiles(chunk, TILE_WALL, 58, 38, 59, 40)
    # Crucifixion Woods — more crucifixion posts and fallen trees (DS3: signature crucified hollows)
    fill_tiles(chunk, TILE_WALL, 54, 44, 55, 46)
    fill_tiles(chunk, TILE_WALL, 62, 48, 63, 50)
    fill_tiles(chunk, TILE_WALL, 70, 54, 71, 56)
    fill_tiles(chunk, TILE_WALL, 82, 60, 83, 62)
    fill_tiles(chunk, TILE_WALL, 94, 50, 95, 52)
    fill_tiles(chunk, TILE_WALL, 106, 46, 107, 48)
    # Corvian forest — dense canopy tree trunks (DS3: thick forest canopy)
    fill_tiles(chunk, TILE_WALL, 92, 86, 93, 88)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 94)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 90)
    fill_tiles(chunk, TILE_WALL, 128, 94, 129, 96)
    fill_tiles(chunk, TILE_WALL, 98, 102, 99, 104)
    fill_tiles(chunk, TILE_WALL, 110, 98, 111, 100)
    # Crystal Sage cave — additional crystal clusters (DS3: magical crystal growths)
    fill_tiles(chunk, TILE_WALL, 124, 122, 125, 124)
    fill_tiles(chunk, TILE_WALL, 132, 128, 133, 130)
    fill_tiles(chunk, TILE_WALL, 140, 122, 141, 124)
    fill_tiles(chunk, TILE_WALL, 116, 126, 117, 128)
    fill_tiles(chunk, TILE_WALL, 128, 134, 129, 136)

    # ================================================================
    # SESSION 19 FIDELITY PASS — RoadOfSacrifices DS3 forest depth
    # ================================================================
    # Corvian nesting trees — branch debris (DS3: Corvians nest in dead trees)
    fill_tiles(chunk, TILE_WALL, 44, 34, 45, 36)
    fill_tiles(chunk, TILE_WALL, 50, 38, 51, 40)
    fill_tiles(chunk, TILE_WALL, 56, 34, 57, 36)
    fill_tiles(chunk, TILE_WALL, 62, 40, 63, 42)
    fill_tiles(chunk, TILE_WALL, 48, 44, 49, 46)
    # Halfway Fortress interior — stone bench debris (DS3: ruined fortress interior)
    fill_tiles(chunk, TILE_WALL, 34, 26, 35, 28)
    fill_tiles(chunk, TILE_WALL, 40, 30, 41, 32)
    fill_tiles(chunk, TILE_WALL, 46, 28, 47, 30)
    fill_tiles(chunk, TILE_WALL, 52, 34, 53, 36)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 38)
    # Black Knight clearing — scorched earth (DS3: Black Knight patrols near keep entrance)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 82)
    fill_tiles(chunk, TILE_WALL, 106, 84, 107, 86)
    fill_tiles(chunk, TILE_WALL, 112, 82, 113, 84)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 88)
    fill_tiles(chunk, TILE_WALL, 118, 86, 119, 88)

    # ================================================================
    # SESSION 22 FIDELITY PASS — RoadOfSacrifices DS3 forest details
    # ================================================================
    # Fallen tree obstacles (DS3: fallen trees blocking forest paths)
    fill_tiles(chunk, TILE_WALL, 22, 36, 23, 37)
    fill_tiles(chunk, TILE_WALL, 28, 40, 29, 41)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    fill_tiles(chunk, TILE_WALL, 40, 48, 41, 49)
    # Corvian nest debris (DS3: corvian nests in the trees)
    fill_tiles(chunk, TILE_WALL, 46, 52, 47, 53)
    fill_tiles(chunk, TILE_WALL, 52, 56, 53, 57)
    fill_tiles(chunk, TILE_WALL, 58, 60, 59, 61)
    fill_tiles(chunk, TILE_WALL, 64, 64, 65, 65)
    # Swamp edge stones (DS3: stones along the poison swamp border)
    fill_tiles(chunk, TILE_WALL, 70, 68, 71, 69)
    fill_tiles(chunk, TILE_WALL, 76, 72, 77, 73)
    fill_tiles(chunk, TILE_WALL, 82, 76, 83, 77)
    fill_tiles(chunk, TILE_WALL, 88, 80, 89, 81)
    # Crucifixion Woods bridge debris (DS3: broken bridge supports)
    fill_tiles(chunk, TILE_WALL, 94, 84, 95, 85)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 106, 92, 107, 93)
    fill_tiles(chunk, TILE_WALL, 112, 96, 113, 97)

    # ================================================================
    # SESSION 26 FIDELITY PASS — RoadOfSacrifices DS3 forest details
    # ================================================================
    # Crucifixion Woods bridge supports (DS3: stone bridge over the river)
    fill_tiles(chunk, TILE_WALL, 20, 34, 21, 35)
    fill_tiles(chunk, TILE_WALL, 26, 38, 27, 39)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    fill_tiles(chunk, TILE_WALL, 38, 46, 39, 47)
    # Corvian settlement tree houses (DS3: elevated structures in trees)
    fill_tiles(chunk, TILE_WALL, 44, 50, 45, 51)
    fill_tiles(chunk, TILE_WALL, 50, 54, 51, 55)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 62, 62, 63, 63)
    # Farron Keep perimeter stones (DS3: boundary stones near Farron Keep)
    fill_tiles(chunk, TILE_WALL, 68, 66, 69, 67)
    fill_tiles(chunk, TILE_WALL, 74, 70, 75, 71)
    fill_tiles(chunk, TILE_WALL, 80, 74, 81, 75)
    fill_tiles(chunk, TILE_WALL, 86, 78, 87, 79)
    # Sage's Ruins debris (DS3: Crystal Sage's ruined study)
    fill_tiles(chunk, TILE_WALL, 92, 82, 93, 83)
    fill_tiles(chunk, TILE_WALL, 98, 86, 99, 87)
    fill_tiles(chunk, TILE_WALL, 104, 90, 105, 91)
    fill_tiles(chunk, TILE_WALL, 110, 94, 111, 95)

    # ================================================================
    # SESSION 30 FIDELITY PASS — RoadOfSacrifices DS3 forest details
    # ================================================================
    # Black Knight tomb debris (DS3: Black Knight tomb in the woods)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    # Estranged wife's grave (DS3: grave in the Crucifixion Woods)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    # Lycanthrope den debris (DS3: lycanthrope cave near the forest)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    # Halfway Fortress stones (DS3: stone ruins at the fortress bonfire)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)

    # SESSION 36 FIDELITY PASS — Road of Sacrifices DS3 details
    # DS3: Fallen trees, corvian nests, bridge supports, swamp edge stones
    for tx in range(25, 60, 7):
        fill_tiles(chunk, TILE_WALL, tx, 35, tx+2, 36)             # Fallen tree trunks
        fill_tiles(chunk, TILE_WALL, tx, 75, tx+2, 76)
    for tx in range(70, 110, 6):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 41)             # Corvian nest platforms
        fill_tiles(chunk, TILE_WALL, tx, 85, tx+1, 86)
    for ty in range(50, 80, 8):
        fill_tiles(chunk, TILE_WALL, 55, ty, 56, ty+1)             # Path edge stones
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)
    fill_tiles(chunk, TILE_WALL, 80, 60, 82, 62)                    # Bridge support debris
    fill_tiles(chunk, TILE_WALL, 40, 90, 42, 92)                    # Swamp edge marker
    fill_tiles(chunk, TILE_WALL, 120, 50, 122, 52)                  # Crucifixion woods entry
    for tx in range(30, 50, 5):
        fill_tiles(chunk, TILE_WALL, tx, 55, tx+1, 56)             # Moss-covered rocks
    # SESSION 40 FIDELITY PASS — Road of Sacrifices DS3 details
    for tx in range(30, 70, 5):
        fill_tiles(chunk, TILE_WALL, tx, 32, tx+1, 33)
        fill_tiles(chunk, TILE_WALL, tx, 72, tx+1, 73)
    for tx in range(75, 120, 5):
        fill_tiles(chunk, TILE_WALL, tx, 38, tx+1, 39)
        fill_tiles(chunk, TILE_WALL, tx, 78, tx+1, 79)
    for ty in range(40, 70, 7):
        fill_tiles(chunk, TILE_WALL, 35, ty, 36, ty+1)
        fill_tiles(chunk, TILE_WALL, 95, ty, 96, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)
    fill_tiles(chunk, TILE_WALL, 110, 55, 112, 57)
    fill_tiles(chunk, TILE_WALL, 70, 85, 72, 87)
    # --- SESSION 45 terrain (Road of Sacrifices) ---
    # DS3: Fallen trees blocking paths (the forest is full of them)
    for tx in range(20, 30):
        chunk[35][tx] = TILE_WALLTOP  # fallen log
    for tx in range(50, 60):
        chunk[40][tx] = TILE_WALLTOP  # fallen tree
    # Corvian nest platforms (DS3: corvians perch in trees)
    for tx, ty in [(35, 25), (55, 28), (75, 22)]:
        chunk[ty][tx] = TILE_WALLTOP  # nest debris
    # Moss-covered rock formations
    for tx, ty in [(40, 45), (60, 50), (80, 42)]:
        chunk[ty][tx] = TILE_WALL  # moss rock
    # Bridge support stonework (DS3: crucifixion woods bridge)
    for ty in range(55, 60):
        chunk[ty][70] = TILE_WALL  # bridge pillar
    # Marshy ground patches (DS3: swampy areas in the forest)
    for tx in range(30, 40):
        for ty in range(60, 65):
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON

    # --- SESSION 53 terrain (Road of Sacrifices final) ---
    # DS3: Crucifixion Woods swamp boundary stones
    for tx, ty in [(55, 60), (65, 62), (75, 58)]:
        chunk[ty][tx] = TILE_WALL  # boundary stone
    # Corvian perch platforms (DS3: wooden platforms in trees)
    for tx, ty in [(30, 28), (45, 25)]:
        chunk[ty][tx] = TILE_WALLTOP  # perch debris
    # Farron Keep perimeter wall (DS3: stone wall separating areas)
    for ty in range(50, 55):
        chunk[ty][90] = TILE_WALL  # perimeter wall
    # Abandoned campsite debris
    for tx in range(60, 68):
        chunk[38][tx] = TILE_WALLTOP  # camp debris
    # Mushroom patches (DS3: giant mushrooms in the forest)
    for tx, ty in [(35, 48), (50, 52)]:
        chunk[ty][tx] = TILE_WALLTOP  # mushroom debris

    # --- SESSION 58 terrain (Road of Sacrifices) ---
    # DS3: Farron Keep perimeter wall (DS3: the wall separating Road from Farron)
    for ty in range(62, 68):
        chunk[ty][88] = TILE_WALL  # perimeter wall
    # Crucifixion Woods bridge supports
    for ty in range(45, 50):
        chunk[ty][72] = TILE_WALL  # bridge support
    # Corvian village tree house platforms
    for tx in range(20, 28):
        chunk[32][tx] = TILE_WALLTOP  # platform debris
    # Witch's hut foundation (DS3: the witch in the woods)
    for tx in range(55, 62):
        chunk[42][tx] = TILE_WALLTOP  # hut foundation

    # --- SESSION 87 DS3 terrain (Road of Sacrifices detail pass) ---
    # DS3: Dense forest trees along the path edges
    for tx in [8, 12, 16, 20, 24, 28, 32, 36, 40]:
        for ty in [8, 10]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    for tx in [44, 48, 52, 56, 60, 64, 68, 72, 76, 80]:
        for ty in [108, 110]:
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty+1] = TILE_WALLTOP
    # DS3: Corvian nests in the treetops (elevated platforms)
    for tx in [35, 55, 75, 95]:
        for ty in [15, 16]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][14] = TILE_WALLTOP
    # DS3: Moss-covered ruins (the crumbling stone structures)
    for tx in range(50, 58):
        for ty in [40, 48]:
            chunk[tx][ty] = TILE_WALL
    for tx in [50, 58]:
        for ty in range(40, 49):
            chunk[tx][ty] = TILE_WALL
    # DS3: Swampy pools with crabs (dark ground patches)
    for tx in range(70, 80):
        for ty in range(85, 92):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Bridge supports over the ravine
    for tx in [60, 65, 70]:
        for ty in range(55, 65):
            chunk[tx][ty] = TILE_WALL
    for tx in range(58, 73):
        chunk[tx][55] = TILE_WALL
    # DS3: Crystal Sage arena (open clearing with crystal formations)
    for tx in range(100, 112):
        for ty in range(90, 100):
            chunk[tx][ty] = TILE_GROUND
    for tx in [100, 104, 108, 112]:
        for ty in [90, 100]:
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 91 DS3 terrain round 2 (Road of Sacrifices) ---
    # DS3: Fallen trees across the path (obstacles)
    for tx in range(35, 45):
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
    for tx in range(65, 72):
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Corvian nests in upper canopy
    for tx in [22, 32, 42, 52, 62]:
        for ty in [12, 13]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][11] = TILE_WALLTOP
    # DS3: Moss-covered stone ruins
    for tx in range(80, 90):
        for ty in [40, 46]:
            chunk[tx][ty] = TILE_WALL
    for tx in [80, 90]:
        for ty in range(40, 47):
            chunk[tx][ty] = TILE_WALL
    # DS3: Swampy water with crabs
    for tx in range(55, 75):
        for ty in range(70, 80):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Bridge supports (stone pillars under the bridge)
    for tx in [62, 67]:
        for ty in range(56, 65):
            chunk[tx][ty] = TILE_WALL
    # DS3: Crucifixion Woods camp (abandoned structures)
    for tx in range(90, 100):
        for ty in [60, 66]:
            chunk[tx][ty] = TILE_WALL
    for tx in [90, 100]:
        for ty in range(60, 67):
            chunk[tx][ty] = TILE_WALL
    for tx in range(90, 101):
        chunk[tx][59] = TILE_WALLTOP
    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 36 * 16, 31 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Shriving Stone")]))
    entities.append(make_entity("Item", 28 * 16, 30 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler")]))
    entities.append(make_entity("Item", 40 * 16, 36 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Brigand Axe")]))
    entities.append(make_entity("Item", 36 * 16, 40 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Brigand Set")]))
    entities.append(make_entity("Item", 36 * 16, 42 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Brigand Twindaggers")]))
    entities.append(make_entity("Item", 66 * 16, 63 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (cliff cavern)")]))
    entities.append(make_entity("Item", 78 * 16, 70 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Braille Divine Tome of Carim")]))
    entities.append(make_entity("Item", 78 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Morne's Ring")]))
    entities.append(make_entity("Item", 91 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember (near storyteller)")]))
    entities.append(make_entity("Item", 95 * 16, 71 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Covenant"),
        make_field("name", "String", "Blue Sentinels Covenant (from Horace)")]))
    entities.append(make_entity("Item", 126 * 16, 90 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (poison brumers)")]))
    entities.append(make_entity("Item", 133 * 16, 93 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (near crosses)")]))
    entities.append(make_entity("Item", 145 * 16, 101 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Fading Soul")]))
    entities.append(make_entity("Item", 96 * 16, 83 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard (ledge drop)")]))
    entities.append(make_entity("Item", 137 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember (blazing fire, crucified hollows)")]))
    entities.append(make_entity("Item", 97 * 16, 86 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of an Unknown Traveler (ledge drop)")]))
    entities.append(make_entity("Item", 170 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Heretic's Staff")]))
    entities.append(make_entity("Item", 155 * 16, 113 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Blue Bug Pellet (near Orbeck)")]))
    entities.append(make_entity("Item", 167 * 16, 112 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Blue Bug Pellet (ruins)")]))
    entities.append(make_entity("Item", 173 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Ring of Sacrifice (ledge drop)")]))
    entities.append(make_entity("Item", 178 * 16, 111 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Sage Ring")]))
    entities.append(make_entity("Item", 183 * 16, 107 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Crystal Gem")]))
    entities.append(make_entity("Item", 186 * 16, 112 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite (ruins 1)")]))
    entities.append(make_entity("Item", 186 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite (ruins 2)")]))
    entities.append(make_entity("Item", 151 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom (swamp edge 1)")]))
    entities.append(make_entity("Item", 160 * 16, 128 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom (swamp edge 2)")]))
    entities.append(make_entity("Item", 142 * 16, 138 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom (swamp 3)")]))
    entities.append(make_entity("Item", 166 * 16, 131 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom (swamp 4)")]))
    entities.append(make_entity("Item", 148 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Grass Crest Shield (before giant crab)")]))
    entities.append(make_entity("Item", 157 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Fallen Knight Set (in the swamp)")]))
    entities.append(make_entity("Item", 178 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (swamp area)")]))
    entities.append(make_entity("Item", 222 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Great Club (Exile drop)")]))
    entities.append(make_entity("Item", 227 * 16, 113 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Exile Greatsword (Exile drop)")]))
    entities.append(make_entity("Item", 225 * 16, 113 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone (Farron Keep castle 1)")]))
    entities.append(make_entity("Item", 228 * 16, 113 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone (Farron Keep castle 2)")]))
    entities.append(make_entity("Item", 224 * 16, 105 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Golden Falcon Shield (ledge drop)")]))
    entities.append(make_entity("Item", 171 * 16, 128 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Great Swamp Pyromancy Tome")]))
    entities.append(make_entity("Item", 235 * 16, 112 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Sellsword Set (ruins)")]))
    entities.append(make_entity("Item", 238 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Sellsword Twinblades (ruins drop)")]))
    entities.append(make_entity("Item", 210 * 16, 137 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Herald Set (past boss)")]))
    entities.append(make_entity("Item", 206 * 16, 143 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard (Crystal Sage area)")]))
    entities.append(make_entity("Item", 210 * 16, 150 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Crystal Sage")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout
    import json as _json
    with open("docs/maps/RoadOfSacrifices.json") as _f:
        _doc = _json.load(_f)
    apply_doc_terrain(chunk, _doc)
    return finalize_map("RoadOfSacrifices", chunk, entities, spawn_px, spawn_py)
