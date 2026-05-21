from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_farron_keep():
    """Farron Keep - sprawling poison swamp with three torches.
    Faithful DS3 layout: entry highland -> poison swamp with torch platforms ->
    Keep Ruins center -> Old Wolf tower -> Abyss Watchers grand hall.
    Design doc: 4000x3600, swamp dominates center with torch islands.
    """
    chunk = new_chunk(320, 288)

    # ================================================================
    # SECTION 1: Keep entry highland (top-left) - doc: x=0,y=0,w=600,h=600
    # Stone steps leading down into the swamp
    # DS3: narrow stone path descending from Road of Sacrifices into the poison swamp
    # ================================================================
    carve_ellipse(chunk, 15, 18, 8, 6)
    fill_tiles(chunk, TILE_GROUND, 8, 20, 25, 35)
    # Broken stone wall at entry
    fill_tiles(chunk, TILE_WALL, 10, 14, 12, 16)
    # Entry path stones (DS3: stone steps down into swamp)
    fill_tiles(chunk, TILE_WALL, 16, 22, 18, 24)
    fill_tiles(chunk, TILE_WALL, 20, 28, 22, 30)

    # ================================================================
    # SECTION 2: Outer poison swamp - vast POISON area
    # Three torch platforms scattered across the swamp
    # DS3: massive poison swamp with three stone platforms holding flame altars
    # ================================================================
    carve_ellipse(chunk, 70, 70, 52, 48)
    # Convert much of the center to POISON tiles
    fill_tiles(chunk, TILE_POISON, 25, 35, 120, 110)

    # Left torch platform (NW) - doc: x=600,y=400,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 30, 30, 45, 42)
    fill_tiles(chunk, TILE_WALL, 34, 34, 36, 36)
    # Torch altar wall (DS3: stone platform with flame)
    fill_tiles(chunk, TILE_WALL, 36, 36, 38, 38)
    # Rubble on platform edge
    fill_tiles(chunk, TILE_WALL, 30, 38, 32, 40)

    # Center torch platform (N) - doc: x=1600,y=800,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 60, 42, 78, 55)
    fill_tiles(chunk, TILE_WALL, 66, 46, 68, 48)
    # Torch altar stone
    fill_tiles(chunk, TILE_WALL, 70, 48, 72, 50)
    # Rubble edges
    fill_tiles(chunk, TILE_WALL, 60, 50, 62, 52)
    fill_tiles(chunk, TILE_WALL, 75, 44, 77, 46)

    # Right torch platform (NE) - doc: x=2400,y=600,w=500,h=500
    fill_tiles(chunk, TILE_GROUND, 88, 35, 105, 48)
    fill_tiles(chunk, TILE_WALL, 94, 38, 96, 40)
    # Torch altar
    fill_tiles(chunk, TILE_WALL, 100, 42, 102, 44)
    # Rubble edges
    fill_tiles(chunk, TILE_WALL, 88, 44, 90, 46)
    fill_tiles(chunk, TILE_WALL, 103, 36, 105, 38)

    # Path from entry into swamp (poison corridor)
    fill_tiles(chunk, TILE_POISON, 22, 30, 35, 45)
    # Scattered rubble in swamp (DS3: sunken ruins visible in poison water)
    fill_tiles(chunk, TILE_WALL, 48, 40, 49, 42)
    fill_tiles(chunk, TILE_WALL, 55, 48, 56, 50)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 54)
    fill_tiles(chunk, TILE_WALL, 42, 55, 43, 57)
    fill_tiles(chunk, TILE_WALL, 75, 38, 76, 40)

    # ================================================================
    # SECTION 3: Keep Ruins (center) - doc: x=1800,y=1600,w=500,h=400
    # Solid ground island with ruined walls, central bonfire hub
    # DS3: stone ruin island with crumbling walls, bonfire inside
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 60, 60, 85, 80)
    fill_tiles(chunk, TILE_WALL, 65, 65, 68, 68)
    fill_tiles(chunk, TILE_WALL, 78, 72, 81, 75)
    fill_tiles(chunk, TILE_WALL, 70, 74, 72, 76)
    # Additional ruin walls (DS3: Keep Ruins has multiple broken walls)
    fill_tiles(chunk, TILE_WALL, 62, 70, 64, 73)
    fill_tiles(chunk, TILE_WALL, 80, 62, 82, 65)
    fill_tiles(chunk, TILE_WALL, 74, 78, 76, 80)
    fill_tiles(chunk, TILE_WALL, 83, 68, 85, 70)

    # ================================================================
    # SECTION 4: Old Wolf tower (south) - doc: x=1000,y=2200,w=400,h=500
    # High tower ruin accessed via ladder, covenant area
    # DS3: tall stone tower with the Old Wolf of Farron covenant
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 35, 95, 55, 115)
    carve_ellipse(chunk, 45, 105, 8, 7)
    # Tower walls
    fill_tiles(chunk, TILE_WALL, 38, 100, 40, 102)
    fill_tiles(chunk, TILE_WALL, 50, 108, 52, 110)
    # Tower base detail (DS3: stone tower with ladder access)
    fill_tiles(chunk, TILE_WALL, 36, 108, 38, 112)
    fill_tiles(chunk, TILE_WALL, 52, 96, 54, 100)

    # ================================================================
    # SECTION 5: Basilisk curse cave (west) - doc: x=400,y=1600,w=400,h=400
    # Dark cave with basilisks, hidden treasure
    # DS3: enclosed cave with multiple basilisks that cause curse
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 20, 65, 38, 82)
    carve_ellipse(chunk, 28, 72, 7, 6)
    # Cave stalagmites (DS3: dark cave with stone formations)
    fill_tiles(chunk, TILE_WALL, 22, 68, 24, 70)
    fill_tiles(chunk, TILE_WALL, 34, 76, 36, 78)
    fill_tiles(chunk, TILE_WALL, 26, 78, 28, 80)

    # ================================================================
    # SECTION 6: Darkwraith patrol zone (SE) - doc: x=2200,y=2000,w=600,h=600
    # Abyss knights patrol between swamp and boss arena approach
    # DS3: Darkwraiths emerge from the swamp water and fight Ghrus
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 95, 80, 120, 105)
    fill_tiles(chunk, TILE_POISON, 98, 85, 115, 100)
    # Ruined stone structures in Darkwraith zone
    fill_tiles(chunk, TILE_WALL, 100, 88, 102, 92)
    fill_tiles(chunk, TILE_WALL, 110, 95, 112, 98)
    fill_tiles(chunk, TILE_WALL, 95, 98, 97, 102)

    # ================================================================
    # SECTION 7: Grand stone gate corridor - doc: x=2800,y=2400,w=300,h=400
    # Long corridor lined with Abyss Watcher armor
    # DS3: grand stone hallway with wolf-crested walls
    # ================================================================
    fill_tiles(chunk, TILE_GROUND, 120, 80, 135, 105)
    # Corridor walls (DS3: stone walls with Abyss Watcher insignia)
    fill_tiles(chunk, TILE_WALL, 120, 85, 122, 90)
    fill_tiles(chunk, TILE_WALL, 132, 95, 134, 100)
    fill_tiles(chunk, TILE_WALL, 125, 88, 127, 92)

    # ================================================================
    # SECTION 8: Abyss Watchers grand hall (far right) - doc: x=3000,y=2600,w=800,h=800
    # Large boss arena - grand stone hall with wolf crest
    # DS3: massive stone hall where Abyss Watchers fight among themselves
    # ================================================================
    carve_ellipse(chunk, 140, 115, 18, 16)
    fill_tiles(chunk, TILE_GROUND, 128, 105, 155, 130)
    # Arena pillars (DS3: grand stone columns in the hall)
    fill_tiles(chunk, TILE_WALL, 132, 110, 134, 114)
    fill_tiles(chunk, TILE_WALL, 145, 118, 147, 122)
    fill_tiles(chunk, TILE_WALL, 138, 108, 140, 110)
    fill_tiles(chunk, TILE_WALL, 150, 112, 152, 115)
    # Arena wall sections (DS3: stone walls framing the boss room)
    fill_tiles(chunk, TILE_WALL, 128, 120, 130, 124)
    fill_tiles(chunk, TILE_WALL, 152, 108, 154, 112)

    # Connection corridors
    fill_tiles(chunk, TILE_GROUND, 55, 80, 65, 95)   # Ruins to Old Wolf
    fill_tiles(chunk, TILE_GROUND, 82, 75, 100, 85)   # Ruins to Darkwraith zone
    fill_tiles(chunk, TILE_GROUND, 115, 100, 128, 112) # Gate to arena

    # ================================================================
    # ADDITIONAL DS3 FARRON KEEP — swamp details, ruin depth
    # ================================================================
    # Entry path — more stone steps (DS3: descent into poison swamp)
    fill_tiles(chunk, TILE_WALL, 12, 18, 13, 20)
    fill_tiles(chunk, TILE_WALL, 18, 26, 19, 28)
    fill_tiles(chunk, TILE_WALL, 14, 30, 15, 32)
    # Left torch platform — additional rubble (DS3: stone ruin with flame altar)
    fill_tiles(chunk, TILE_WALL, 32, 32, 33, 34)
    fill_tiles(chunk, TILE_WALL, 40, 38, 41, 40)
    fill_tiles(chunk, TILE_WALL, 36, 30, 37, 32)
    # Center torch platform — more altar stones (DS3: stone platform with Ghru)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 46)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 52)
    fill_tiles(chunk, TILE_WALL, 68, 52, 69, 54)
    # Right torch platform — debris (DS3: Ghru-infested torch platform)
    fill_tiles(chunk, TILE_WALL, 92, 40, 93, 42)
    fill_tiles(chunk, TILE_WALL, 98, 36, 99, 38)
    fill_tiles(chunk, TILE_WALL, 102, 44, 103, 46)
    # Poison swamp — sunken ruins (DS3: crumbled structures visible in swamp)
    fill_tiles(chunk, TILE_WALL, 46, 45, 47, 47)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 54)
    fill_tiles(chunk, TILE_WALL, 85, 48, 86, 50)
    fill_tiles(chunk, TILE_WALL, 52, 58, 53, 60)
    fill_tiles(chunk, TILE_WALL, 68, 56, 69, 58)
    fill_tiles(chunk, TILE_WALL, 78, 44, 79, 46)
    fill_tiles(chunk, TILE_WALL, 90, 56, 91, 58)
    # Keep Ruins — more crumbled walls (DS3: central ruin island)
    fill_tiles(chunk, TILE_WALL, 66, 62, 67, 64)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 68)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 76)
    fill_tiles(chunk, TILE_WALL, 64, 76, 65, 78)
    # Old Wolf tower — tower stones (DS3: tall tower with covenant)
    fill_tiles(chunk, TILE_WALL, 40, 96, 41, 98)
    fill_tiles(chunk, TILE_WALL, 48, 102, 49, 104)
    fill_tiles(chunk, TILE_WALL, 42, 110, 43, 112)
    fill_tiles(chunk, TILE_WALL, 54, 98, 55, 100)
    # Basilisk cave — more stalagmites (DS3: dark curse cave)
    fill_tiles(chunk, TILE_WALL, 24, 72, 25, 74)
    fill_tiles(chunk, TILE_WALL, 32, 78, 33, 80)
    fill_tiles(chunk, TILE_WALL, 30, 66, 31, 68)
    # Darkwraith zone — more abyss ruins (DS3: dark knights emerge from swamp)
    fill_tiles(chunk, TILE_WALL, 98, 92, 99, 94)
    fill_tiles(chunk, TILE_WALL, 106, 90, 107, 92)
    fill_tiles(chunk, TILE_WALL, 112, 98, 113, 100)
    fill_tiles(chunk, TILE_WALL, 96, 102, 97, 104)
    # Grand gate corridor — wolf crest walls (DS3: Abyss Watcher hall)
    fill_tiles(chunk, TILE_WALL, 122, 82, 123, 84)
    fill_tiles(chunk, TILE_WALL, 130, 90, 131, 92)
    fill_tiles(chunk, TILE_WALL, 128, 98, 129, 100)
    fill_tiles(chunk, TILE_WALL, 134, 102, 135, 104)
    # Abyss Watchers arena — more grand columns (DS3: massive boss hall)
    fill_tiles(chunk, TILE_WALL, 136, 112, 137, 114)
    fill_tiles(chunk, TILE_WALL, 148, 114, 149, 116)
    fill_tiles(chunk, TILE_WALL, 130, 116, 131, 118)
    fill_tiles(chunk, TILE_WALL, 154, 118, 155, 120)

    # ================================================================
    # SESSION 9 FIDELITY PASS — FarronKeep architectural details
    # ================================================================
    # Swamp edge — rotting wooden posts (DS3: decayed fence posts along swamp)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 23)
    fill_tiles(chunk, TILE_WALL, 30, 16, 31, 17)
    # Ghru camp — bonfire stone ring (DS3: Ghru encampment with fire pit)
    fill_tiles(chunk, TILE_WALL, 36, 28, 37, 29)
    fill_tiles(chunk, TILE_WALL, 40, 32, 41, 33)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 35)
    # Great沼 swamp — submerged ruins (DS3: ruins visible above swamp water)
    fill_tiles(chunk, TILE_WALL, 60, 40, 61, 41)
    fill_tiles(chunk, TILE_WALL, 64, 44, 65, 45)
    fill_tiles(chunk, TILE_WALL, 56, 48, 57, 49)
    fill_tiles(chunk, TILE_WALL, 68, 36, 69, 37)
    fill_tiles(chunk, TILE_WALL, 72, 50, 73, 51)
    # Old Wolf of Farron tower — crumbling stairs (DS3: tower with wolf inside)
    fill_tiles(chunk, TILE_WALL, 90, 30, 91, 31)
    fill_tiles(chunk, TILE_WALL, 94, 34, 95, 35)
    fill_tiles(chunk, TILE_WALL, 86, 36, 87, 37)
    fill_tiles(chunk, TILE_WALL, 98, 28, 99, 29)
    # Abyss Watchers arena — broken greatswords (DS3: swords embedded in ground)
    fill_tiles(chunk, TILE_WALL, 120, 60, 121, 61)
    fill_tiles(chunk, TILE_WALL, 126, 64, 127, 65)
    fill_tiles(chunk, TILE_WALL, 132, 58, 133, 59)
    fill_tiles(chunk, TILE_WALL, 138, 62, 139, 63)
    fill_tiles(chunk, TILE_WALL, 116, 68, 117, 69)
    fill_tiles(chunk, TILE_WALL, 144, 66, 145, 67)
    # Grass-covered ruin arches (DS3: mossy stone arches throughout keep)
    fill_tiles(chunk, TILE_WALL, 42, 56, 43, 57)
    fill_tiles(chunk, TILE_WALL, 50, 60, 51, 61)
    fill_tiles(chunk, TILE_WALL, 46, 64, 47, 65)
    fill_tiles(chunk, TILE_WALL, 54, 52, 55, 53)
    # Strangleroot clusters (DS3: dangerous root tendrils in swamp)
    fill_tiles(chunk, TILE_WALL, 66, 72, 67, 73)
    fill_tiles(chunk, TILE_WALL, 74, 68, 75, 69)
    fill_tiles(chunk, TILE_WALL, 70, 76, 71, 77)
    fill_tiles(chunk, TILE_WALL, 62, 80, 63, 81)
    # Keep perimeter — crumbling wall foundations (DS3: ruined fort walls)
    fill_tiles(chunk, TILE_WALL, 100, 80, 101, 81)
    fill_tiles(chunk, TILE_WALL, 108, 84, 109, 85)
    fill_tiles(chunk, TILE_WALL, 104, 88, 105, 89)
    fill_tiles(chunk, TILE_WALL, 112, 76, 113, 77)
    # Farron Keep perimeter — darksign-tinged stones (DS3: abyss corruption visible)
    fill_tiles(chunk, TILE_WALL, 130, 100, 131, 101)
    fill_tiles(chunk, TILE_WALL, 136, 104, 137, 105)
    fill_tiles(chunk, TILE_WALL, 142, 96, 143, 97)
    fill_tiles(chunk, TILE_WALL, 148, 108, 149, 109)

    # ================================================================
    # SESSION 12 FIDELITY PASS — FarronKeep DS3 architectural details
    # ================================================================
    # Decayed Ghru totem poles (DS3: wooden Ghru effigies throughout swamp)
    fill_tiles(chunk, TILE_WALL, 20, 42, 21, 44)
    fill_tiles(chunk, TILE_WALL, 38, 38, 39, 40)
    fill_tiles(chunk, TILE_WALL, 52, 42, 53, 44)
    fill_tiles(chunk, TILE_WALL, 68, 46, 69, 48)
    # Sunken wolf-crested grave markers (DS3: Abyss Watcher memorial stones)
    fill_tiles(chunk, TILE_WALL, 44, 60, 45, 62)
    fill_tiles(chunk, TILE_WALL, 58, 64, 59, 66)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 64)
    fill_tiles(chunk, TILE_WALL, 86, 58, 87, 60)
    # Collapsed stone bridge fragments (DS3: crumbling bridge over deep swamp)
    fill_tiles(chunk, TILE_WALL, 50, 70, 52, 71)
    fill_tiles(chunk, TILE_WALL, 56, 72, 58, 73)
    fill_tiles(chunk, TILE_WALL, 62, 74, 64, 75)
    fill_tiles(chunk, TILE_WALL, 46, 76, 48, 77)
    # Poison-lily cluster bases (DS3: white flowers dotting the swamp surface)
    fill_tiles(chunk, TILE_WALL, 34, 82, 35, 83)
    fill_tiles(chunk, TILE_WALL, 48, 86, 49, 87)
    fill_tiles(chunk, TILE_WALL, 62, 84, 63, 85)
    fill_tiles(chunk, TILE_WALL, 76, 88, 77, 89)
    # Rotting wooden walkway planks (DS3: decayed boardwalks over poison)
    fill_tiles(chunk, TILE_WALL, 26, 90, 27, 92)
    fill_tiles(chunk, TILE_WALL, 32, 94, 33, 96)
    fill_tiles(chunk, TILE_WALL, 38, 88, 39, 90)
    fill_tiles(chunk, TILE_WALL, 44, 92, 45, 94)
    # Broken Abyss Watcher sword shrines (DS3: broken greatswords stuck in ground)
    fill_tiles(chunk, TILE_WALL, 118, 96, 119, 98)
    fill_tiles(chunk, TILE_WALL, 124, 100, 125, 102)
    fill_tiles(chunk, TILE_WALL, 130, 94, 131, 96)
    fill_tiles(chunk, TILE_WALL, 136, 98, 137, 100)
    # Swamp gas vent stones (DS3: bubbling poison pools throughout swamp)
    fill_tiles(chunk, TILE_WALL, 40, 96, 41, 97)
    fill_tiles(chunk, TILE_WALL, 56, 92, 57, 93)
    fill_tiles(chunk, TILE_WALL, 70, 96, 71, 97)
    fill_tiles(chunk, TILE_WALL, 84, 94, 85, 95)
    # Crumbling fortification pillars (DS3: ruined fort walls along perimeter)
    fill_tiles(chunk, TILE_WALL, 94, 78, 95, 80)
    fill_tiles(chunk, TILE_WALL, 106, 82, 107, 84)
    fill_tiles(chunk, TILE_WALL, 118, 86, 119, 88)
    fill_tiles(chunk, TILE_WALL, 142, 82, 143, 84)
    # Abyss-tainted water pool edges (DS3: dark water pools near Darkwraith area)
    fill_tiles(chunk, TILE_WALL, 96, 90, 98, 91)
    fill_tiles(chunk, TILE_WALL, 102, 94, 104, 95)
    fill_tiles(chunk, TILE_WALL, 110, 88, 112, 89)
    fill_tiles(chunk, TILE_WALL, 116, 92, 118, 93)
    # Old Wolf stairwell — mossy steps (DS3: stone steps up to Old Wolf tower)
    fill_tiles(chunk, TILE_WALL, 40, 100, 41, 102)
    fill_tiles(chunk, TILE_WALL, 44, 104, 45, 106)
    fill_tiles(chunk, TILE_WALL, 48, 108, 49, 110)
    fill_tiles(chunk, TILE_WALL, 52, 106, 53, 108)

    # ================================================================
    # DS3 POISON TERRAIN — Farron Keep expanded poison swamp
    # DS3: vast poison swamp dominates the center, only torch platforms are safe
    # ================================================================
    # Expanded central poison swamp (DS3: the entire low area is toxic water)
    fill_tiles(chunk, TILE_POISON, 35, 50, 55, 70)
    fill_tiles(chunk, TILE_POISON, 45, 60, 65, 80)
    fill_tiles(chunk, TILE_POISON, 55, 45, 75, 65)
    fill_tiles(chunk, TILE_POISON, 70, 55, 90, 75)
    fill_tiles(chunk, TILE_POISON, 40, 70, 60, 90)
    fill_tiles(chunk, TILE_POISON, 60, 70, 80, 85)
    fill_tiles(chunk, TILE_POISON, 80, 65, 100, 80)
    # Poison channels connecting swamp sections
    fill_tiles(chunk, TILE_POISON, 30, 45, 40, 55)
    fill_tiles(chunk, TILE_POISON, 85, 50, 95, 60)

    entities = []

    spawn_px, spawn_py = 15 * 16, 16 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # Bonfires
    entities.append(make_entity("Bonfire", 38 * 16, 47 * 16))     # Keep entry
    entities.append(make_entity("Bonfire", 150 * 16, 133 * 16))     # Keep Ruins
    entities.append(make_entity("Bonfire", 241 * 16, 170 * 16))    # Keep Perimeter
    entities.append(make_entity("Bonfire", 105 * 16, 73 * 16))    # Old Wolf
    entities.append(make_entity("Bonfire", 275 * 16, 215 * 16))   # Abyss Watchers

    # Boss - Abyss Watchers
    entities.append(make_entity("BossSpawn", 275 * 16, 215 * 16))

    # Enemies - DS3 faithful: Ghru (swarm the swamp), Elder Ghru (elite horned beasts),
    # Darkwraiths (abyss knights), Basilisks (curse cave), Rotten Slugs (leeches everywhere),
    # Great Crabs, Corvians + Storyteller, Crystal Lizards (5-6 total), Ravenous Crystal Lizard

    
    # --- DS3 faithful enemies (FarronKeep) ---
    # Ghru (21)
    for tx, ty in [(35, 45), (40, 48), (48, 50), (33, 50), (42, 55), (46, 58), (68, 48), (72, 52), (75, 55), (64, 55), (70, 58), (95, 42), (100, 45), (92, 48), (98, 52), (105, 50), (65, 72), (72, 76), (78, 70), (68, 68), (74, 65)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Ghru", "Ghru"))]))
    # DarkMage (2)
    entities.append(make_entity("Enemy", 70 * 16, 74 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    entities.append(make_entity("Enemy", 118 * 16, 98 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("DarkMage", "DarkMage"))]))
    # Darkwraith (5)
    entities.append(make_entity("Enemy", 100 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Darkwraith", "Darkwraith"))]))
    entities.append(make_entity("Enemy", 108 * 16, 95 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Darkwraith", "Darkwraith"))]))
    entities.append(make_entity("Enemy", 125 * 16, 108 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Darkwraith", "Darkwraith"))]))
    entities.append(make_entity("Enemy", 88 * 16, 75 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Darkwraith", "Darkwraith"))]))
    entities.append(make_entity("Enemy", 115 * 16, 90 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Darkwraith", "Darkwraith"))]))
    # Basilisk (5)
    entities.append(make_entity("Enemy", 24 * 16, 70 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 30 * 16, 75 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 32 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 28 * 16, 78 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    entities.append(make_entity("Enemy", 34 * 16, 72 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Basilisk", "Basilisk"))]))
    # RottenSlug (13)
    for tx, ty in [(42, 82), (45, 85), (50, 88), (48, 105), (52, 110), (38, 60), (44, 65), (55, 70), (62, 75), (70, 80), (85, 75), (40, 90), (56, 95)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("RottenSlug", "RottenSlug"))]))
    # ElderGhru (3 — DS3: elite horned Ghru with staff/hammer near torch platforms)
    entities.append(make_entity("Enemy", 55 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ElderGhru", "Ghru"))]))
    entities.append(make_entity("Enemy", 60 * 16, 68 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ElderGhru", "Ghru"))]))
    entities.append(make_entity("Enemy", 58 * 16, 75 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("ElderGhru", "Ghru"))]))
    # Ghru (3 additional — DS3: more regular Ghrus patrolling deeper swamp)
    for tx, ty in [(110, 100), (82, 60), (90, 55)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Ghru", "Ghru"))]))
    # GreatCrab (1)
    entities.append(make_entity("Enemy", 65 * 16, 62 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("GreatCrab", "GreatCrab"))]))
    # Corvian (2)
    entities.append(make_entity("Enemy", 115 * 16, 95 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Corvian", "Corvian"))]))
    entities.append(make_entity("Enemy", 120 * 16, 100 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Corvian", "Corvian"))]))
    # CrystalLizard (5)
    entities.append(make_entity("Enemy", 85 * 16, 82 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 48 * 16, 112 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 122 * 16, 95 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 128 * 16, 98 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    entities.append(make_entity("Enemy", 56 * 16, 65 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # MiniBoss (2)
    entities.append(make_entity("Enemy", 108 * 16, 85 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    entities.append(make_entity("Enemy", 120 * 16, 98 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- Items (DS3 Farron Keep) — accurate from wiki ---

    # NPC - Old Wolf of Farron
    entities.append(make_entity("Npc", 108 * 16, 154 * 16, [make_field("name", "String", "Old Wolf of Farron"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#8899AA"), make_field("dialogue", "String", "(The wolf gazes silently|Its eyes reflect distant flames)|(The old wolf acknowledges your presence)|(It carries the scent of the Abyss Watchers)")]))

    # NPC - Hawkwood (event: he meditates at Farron Keep, relating to Abyss Watchers)
    entities.append(make_entity("Npc", 137 * 16, 115 * 16, [make_field("name", "String", "Hawkwood"), make_field("kind", "LocalEnum.NpcKind", "Dialogue"), make_field("color", "Color", "#8B7355"), make_field("dialogue", "String", "The Undead Legion used to be around here|They were a fierce bunch|They linked the fire long ago|The wolf blood runs through their veins|They kept watch over the Abyss, and its abominations|If you seek them, you must first prove your worth")]))

    # Fog Gate to CatacombsOfCarthus
    entities.append(make_entity("FogGate", 275 * 16, 231 * 16, [
        make_field("dest_area", "String", "CatacombsOfCarthus"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # Fog Gate to RoadOfSacrifices (DS3: entrance from Road of Sacrifices)
    entities.append(make_entity("FogGate", 38 * 16, 38 * 16, [
        make_field("dest_area", "String", "RoadOfSacrifices"),
        make_field("dest_x", "Float", 100.0),
        make_field("dest_y", "Float", 100.0),
        make_field("width", "Float", 64.0),
        make_field("height", "Float", 80.0),
    ]))

    # No chests in Farron Keep per DS3 wiki — all items are ground pickups

    # Lights - torch fires and bonfire glow
    entities.append(make_entity("Light", 15 * 16, 18 * 16, [make_field("radius", "Float", 140.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 37 * 16, 36 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 69 * 16, 48 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 96 * 16, 40 * 16, [make_field("radius", "Float", 120.0), make_field("r", "Float", 1.0), make_field("g", "Float", 0.6), make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 72 * 16, 68 * 16, [make_field("radius", "Float", 180.0), make_field("r", "Float", 0.8), make_field("g", "Float", 0.7), make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 45 * 16, 105 * 16, [make_field("radius", "Float", 160.0), make_field("r", "Float", 0.6), make_field("g", "Float", 0.7), make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 140 * 16, 112 * 16, [make_field("radius", "Float", 220.0), make_field("r", "Float", 0.5), make_field("g", "Float", 0.5), make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.4)]))

    # === ADDITIONAL INTERNAL STRUCTURES — Farron Keep DS3 fidelity ===
    # Torch platform rubble (DS3: three stone platforms with flame altars)
    fill_tiles(chunk, TILE_WALL, 25, 35, 27, 38)
    fill_tiles(chunk, TILE_WALL, 40, 42, 42, 44)
    fill_tiles(chunk, TILE_WALL, 55, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 70, 42, 72, 44)
    # Sunken ruin walls in swamp (DS3: visible stone walls poking through poison)
    fill_tiles(chunk, TILE_WALL, 35, 55, 37, 58)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)
    fill_tiles(chunk, TILE_WALL, 65, 55, 67, 57)
    fill_tiles(chunk, TILE_WALL, 80, 50, 82, 52)
    # Deep swamp debris (DS3: scattered rocks and sunken stonework)
    fill_tiles(chunk, TILE_WALL, 45, 72, 47, 74)
    fill_tiles(chunk, TILE_WALL, 60, 75, 62, 77)
    fill_tiles(chunk, TILE_WALL, 75, 68, 77, 70)
    fill_tiles(chunk, TILE_WALL, 90, 60, 92, 62)
    # Darkwraith zone rubble (DS3: ruins where Darkwraiths emerge)
    fill_tiles(chunk, TILE_WALL, 100, 68, 102, 70)
    fill_tiles(chunk, TILE_WALL, 110, 75, 112, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 122, 82)
    fill_tiles(chunk, TILE_WALL, 130, 85, 132, 88)
    # Entry path stone steps (DS3: narrow stone steps down into swamp)
    fill_tiles(chunk, TILE_WALL, 12, 20, 14, 22)
    fill_tiles(chunk, TILE_WALL, 20, 24, 22, 26)
    # Basilisk cave stalagmites (DS3: dark cave with stone formations)
    fill_tiles(chunk, TILE_WALL, 24, 66, 26, 68)
    fill_tiles(chunk, TILE_WALL, 32, 74, 34, 76)
    fill_tiles(chunk, TILE_WALL, 20, 78, 22, 80)
    # Old Wolf tower base stones (DS3: tall stone tower accessed by ladder)
    fill_tiles(chunk, TILE_WALL, 42, 98, 44, 100)
    fill_tiles(chunk, TILE_WALL, 48, 110, 50, 112)
    # Grand gate corridor walls (DS3: stone hallway with wolf-crested walls)
    fill_tiles(chunk, TILE_WALL, 118, 82, 120, 85)
    fill_tiles(chunk, TILE_WALL, 128, 90, 130, 93)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 98)
    # Abyss Watchers arena perimeter (DS3: grand stone hall columns)
    fill_tiles(chunk, TILE_WALL, 135, 110, 137, 112)
    fill_tiles(chunk, TILE_WALL, 145, 120, 147, 122)
    fill_tiles(chunk, TILE_WALL, 130, 118, 132, 120)
    # Poison swamp islands (DS3: safe ground patches in the poison)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 50)
    fill_tiles(chunk, TILE_WALL, 85, 55, 86, 57)
    fill_tiles(chunk, TILE_WALL, 58, 68, 59, 70)
    # SESSION 10 FIDELITY PASS — Farron Keep
    # Additional DS3-faithful terrain: rotting post debris, Ghru camp stones,
    # submerged ruin walls, Abyss Watchers sword fragments, swamp edge details
    # Left torch area — rotting post debris (DS3: rotting wooden posts everywhere)
    fill_tiles(chunk, TILE_WALL, 32, 42, 33, 43)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    fill_tiles(chunk, TILE_WALL, 40, 52, 41, 53)
    fill_tiles(chunk, TILE_WALL, 28, 54, 29, 55)
    # Center torch — stone platform details (DS3: stone platform with fire)
    fill_tiles(chunk, TILE_WALL, 66, 46, 67, 47)
    fill_tiles(chunk, TILE_WALL, 70, 50, 71, 51)
    fill_tiles(chunk, TILE_WALL, 64, 52, 65, 53)
    fill_tiles(chunk, TILE_WALL, 72, 54, 73, 55)
    # Right torch — debris stones (DS3: crumbling stone platform)
    fill_tiles(chunk, TILE_WALL, 94, 40, 95, 41)
    fill_tiles(chunk, TILE_WALL, 98, 44, 99, 45)
    fill_tiles(chunk, TILE_WALL, 102, 48, 103, 49)
    fill_tiles(chunk, TILE_WALL, 92, 46, 93, 47)
    # Ghru camp — bonfire ring stones (DS3: Ghru encampment with fire pit)
    fill_tiles(chunk, TILE_WALL, 62, 70, 63, 71)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 66, 74, 67, 75)
    fill_tiles(chunk, TILE_WALL, 72, 72, 73, 73)
    # Keep Ruins — submerged ruin walls (DS3: flooded ruins of the keep)
    fill_tiles(chunk, TILE_WALL, 76, 64, 77, 65)
    fill_tiles(chunk, TILE_WALL, 82, 68, 83, 69)
    fill_tiles(chunk, TILE_WALL, 86, 72, 87, 73)
    fill_tiles(chunk, TILE_WALL, 80, 76, 81, 77)
    # Darkwraith zone — abyss stone debris (DS3: dark knights emerge from abyss)
    fill_tiles(chunk, TILE_WALL, 96, 82, 97, 83)
    fill_tiles(chunk, TILE_WALL, 102, 86, 103, 87)
    fill_tiles(chunk, TILE_WALL, 108, 90, 109, 91)
    fill_tiles(chunk, TILE_WALL, 114, 94, 115, 95)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    # Abyss Watchers arena approach — broken sword fragments (DS3: scattered swords)
    fill_tiles(chunk, TILE_WALL, 120, 98, 121, 99)
    fill_tiles(chunk, TILE_WALL, 126, 102, 127, 103)
    fill_tiles(chunk, TILE_WALL, 122, 106, 123, 107)
    # Swamp water edges — submerged debris (DS3: debris visible in swamp water)
    fill_tiles(chunk, TILE_WALL, 38, 58, 39, 59)
    fill_tiles(chunk, TILE_WALL, 44, 64, 45, 65)
    fill_tiles(chunk, TILE_WALL, 50, 70, 51, 71)
    fill_tiles(chunk, TILE_WALL, 56, 76, 57, 77)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    fill_tiles(chunk, TILE_WALL, 94, 84, 95, 85)
    # Basilisk cave — stone formations (DS3: curse cave with stone formations)
    fill_tiles(chunk, TILE_WALL, 40, 88, 41, 89)
    fill_tiles(chunk, TILE_WALL, 46, 92, 47, 93)
    fill_tiles(chunk, TILE_WALL, 52, 96, 53, 97)

    # ================================================================
    # SESSION 14 FIDELITY PASS — FarronKeep DS3 terrain details
    # ================================================================
    # Swamp edge — sunken wagon debris (DS3: abandoned wagons in swamp)
    fill_tiles(chunk, TILE_WALL, 28, 46, 29, 47)
    fill_tiles(chunk, TILE_WALL, 34, 50, 35, 51)
    fill_tiles(chunk, TILE_WALL, 44, 48, 45, 49)
    fill_tiles(chunk, TILE_WALL, 54, 52, 55, 53)
    # Ghru camp — ritual bone piles (DS3: Ghru gather around bone fires)
    fill_tiles(chunk, TILE_WALL, 62, 42, 63, 43)
    fill_tiles(chunk, TILE_WALL, 70, 48, 71, 49)
    fill_tiles(chunk, TILE_WALL, 82, 44, 83, 45)
    fill_tiles(chunk, TILE_WALL, 92, 50, 93, 51)
    # Darkwraith emergence pools (DS3: dark wraiths rise from black pools)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 93)
    fill_tiles(chunk, TILE_WALL, 112, 96, 113, 97)
    fill_tiles(chunk, TILE_WALL, 120, 90, 121, 91)
    # Abyss Watcher memorial stones (DS3: swords embedded in ground near arena)
    fill_tiles(chunk, TILE_WALL, 124, 106, 125, 107)
    fill_tiles(chunk, TILE_WALL, 132, 110, 133, 111)
    fill_tiles(chunk, TILE_WALL, 140, 104, 141, 105)
    fill_tiles(chunk, TILE_WALL, 148, 112, 149, 113)
    # Wolf-crested grave markers (DS3: wolf insignia gravestones)
    fill_tiles(chunk, TILE_WALL, 38, 62, 39, 63)
    fill_tiles(chunk, TILE_WALL, 48, 66, 49, 67)
    fill_tiles(chunk, TILE_WALL, 58, 70, 59, 71)
    fill_tiles(chunk, TILE_WALL, 68, 74, 69, 75)

    # ================================================================
    # SESSION 17 FIDELITY PASS — FarronKeep DS3 swamp details
    # ================================================================
    # Poison swamp — more murky island debris (DS3: swamp with scattered stone islands)
    fill_tiles(chunk, TILE_WALL, 22, 28, 23, 30)
    fill_tiles(chunk, TILE_WALL, 32, 34, 33, 36)
    fill_tiles(chunk, TILE_WALL, 42, 38, 43, 40)
    fill_tiles(chunk, TILE_WALL, 52, 42, 53, 44)
    fill_tiles(chunk, TILE_WALL, 28, 44, 29, 46)
    # Torch platform stones — fire pit debris around the three torches (DS3: three flames to light)
    fill_tiles(chunk, TILE_WALL, 34, 52, 35, 54)
    fill_tiles(chunk, TILE_WALL, 44, 56, 45, 58)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 50)
    fill_tiles(chunk, TILE_WALL, 24, 58, 25, 60)
    fill_tiles(chunk, TILE_WALL, 64, 54, 65, 56)
    # Old Wolf tower — stone bridge debris (DS3: tower where Old Wolf of Farron sits)
    fill_tiles(chunk, TILE_WALL, 72, 62, 73, 64)
    fill_tiles(chunk, TILE_WALL, 80, 58, 81, 60)
    fill_tiles(chunk, TILE_WALL, 88, 66, 89, 68)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 70)
    # Abyss Watchers approach — broken sword debris (DS3: swords embedded in ground)
    fill_tiles(chunk, TILE_WALL, 96, 72, 97, 74)
    fill_tiles(chunk, TILE_WALL, 104, 78, 105, 80)
    fill_tiles(chunk, TILE_WALL, 112, 74, 113, 76)
    fill_tiles(chunk, TILE_WALL, 120, 82, 121, 84)
    fill_tiles(chunk, TILE_WALL, 128, 78, 129, 80)
    # Keep Ruins — collapsed stone walls (DS3: ruins in the center of the swamp)
    fill_tiles(chunk, TILE_WALL, 132, 86, 133, 88)
    fill_tiles(chunk, TILE_WALL, 140, 92, 141, 94)
    fill_tiles(chunk, TILE_WALL, 136, 98, 137, 100)
    fill_tiles(chunk, TILE_WALL, 144, 88, 145, 90)
    # Ghrus territory — slug-ridden swamp debris (DS3: Ghrus swarm near the torches)
    fill_tiles(chunk, TILE_WALL, 16, 34, 17, 36)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 46)
    fill_tiles(chunk, TILE_WALL, 48, 50, 49, 52)
    fill_tiles(chunk, TILE_WALL, 60, 46, 61, 48)

    # ================================================================
    # SESSION 21 FIDELITY PASS — FarronKeep DS3 swamp details
    # ================================================================
    # Ruined knight corpse mounds (DS3: fallen knight bodies in swamp water)
    fill_tiles(chunk, TILE_WALL, 30, 50, 32, 52)
    fill_tiles(chunk, TILE_WALL, 36, 54, 38, 56)
    fill_tiles(chunk, TILE_WALL, 42, 58, 44, 60)
    fill_tiles(chunk, TILE_WALL, 24, 56, 26, 58)
    # Collapsed stone bridge fragments (DS3: broken bridge to Old Wolf tower)
    fill_tiles(chunk, TILE_WALL, 34, 80, 36, 82)
    fill_tiles(chunk, TILE_WALL, 40, 84, 42, 86)
    fill_tiles(chunk, TILE_WALL, 46, 88, 48, 90)
    fill_tiles(chunk, TILE_WALL, 52, 92, 54, 94)
    # Ghru totem pole bases (DS3: wooden ghru markers near torch platforms)
    fill_tiles(chunk, TILE_WALL, 60, 48, 62, 50)
    fill_tiles(chunk, TILE_WALL, 66, 52, 68, 54)
    fill_tiles(chunk, TILE_WALL, 72, 56, 74, 58)
    fill_tiles(chunk, TILE_WALL, 78, 60, 80, 62)
    # Swamp root cluster obstacles (DS3: thick swamp vegetation clusters)
    fill_tiles(chunk, TILE_WALL, 18, 36, 20, 38)
    fill_tiles(chunk, TILE_WALL, 24, 40, 26, 42)
    fill_tiles(chunk, TILE_WALL, 48, 44, 50, 46)
    fill_tiles(chunk, TILE_WALL, 56, 50, 58, 52)
    # Abyss Watcher statue debris (DS3: broken watcher statues near grand hall)
    fill_tiles(chunk, TILE_WALL, 134, 104, 136, 106)
    fill_tiles(chunk, TILE_WALL, 140, 108, 142, 110)
    fill_tiles(chunk, TILE_WALL, 146, 114, 148, 116)
    fill_tiles(chunk, TILE_WALL, 152, 118, 154, 120)

    # ================================================================
    # SESSION 23 FIDELITY PASS — FarronKeep DS3 swamp details
    # ================================================================
    # Abyss Watcher monument stones (DS3: stone monument near grand hall)
    fill_tiles(chunk, TILE_WALL, 140, 108, 141, 109)
    fill_tiles(chunk, TILE_WALL, 146, 112, 147, 113)
    fill_tiles(chunk, TILE_WALL, 148, 116, 149, 117)
    fill_tiles(chunk, TILE_WALL, 142, 120, 143, 121)
    # Poison swamp tree roots (DS3: thick roots rising from swamp)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 89)
    fill_tiles(chunk, TILE_WALL, 50, 92, 51, 93)
    fill_tiles(chunk, TILE_WALL, 56, 96, 57, 97)
    fill_tiles(chunk, TILE_WALL, 62, 100, 63, 101)
    # Old Wolf tower stairs (DS3: spiral staircase in the tower)
    fill_tiles(chunk, TILE_WALL, 28, 96, 29, 97)
    fill_tiles(chunk, TILE_WALL, 34, 100, 35, 101)
    fill_tiles(chunk, TILE_WALL, 40, 104, 41, 105)
    fill_tiles(chunk, TILE_WALL, 46, 108, 47, 109)

    # ================================================================
    # SESSION 27 FIDELITY PASS — FarronKeep DS3 swamp details
    # ================================================================
    # Torch platform stone circles (DS3: stone circles around torch altars)
    fill_tiles(chunk, TILE_WALL, 16, 42, 17, 43)
    fill_tiles(chunk, TILE_WALL, 22, 46, 23, 47)
    fill_tiles(chunk, TILE_WALL, 28, 50, 29, 51)
    fill_tiles(chunk, TILE_WALL, 34, 54, 35, 55)
    # Ghru camp debris (DS3: ghru encampment near swamp edge)
    fill_tiles(chunk, TILE_WALL, 40, 58, 41, 59)
    fill_tiles(chunk, TILE_WALL, 46, 62, 47, 63)
    fill_tiles(chunk, TILE_WALL, 52, 66, 53, 67)
    fill_tiles(chunk, TILE_WALL, 58, 70, 59, 71)
    # Abyss Watcher memorial stones (DS3: memorial stones near the grand hall)
    fill_tiles(chunk, TILE_WALL, 64, 74, 65, 75)
    fill_tiles(chunk, TILE_WALL, 70, 78, 71, 79)
    fill_tiles(chunk, TILE_WALL, 76, 82, 77, 83)
    fill_tiles(chunk, TILE_WALL, 82, 86, 83, 87)
    # Darkwraith patrol markers (DS3: darkwraith patrol route markers)
    fill_tiles(chunk, TILE_WALL, 88, 90, 89, 91)
    fill_tiles(chunk, TILE_WALL, 94, 94, 95, 95)
    fill_tiles(chunk, TILE_WALL, 100, 98, 101, 99)
    fill_tiles(chunk, TILE_WALL, 106, 102, 107, 103)

    # ================================================================
    # SESSION 31 FIDELITY PASS — FarronKeep DS3 swamp details
    # ================================================================
    # Old Wolf tower steps (DS3: spiral steps in the Old Wolf's tower)
    fill_tiles(chunk, TILE_WALL, 38, 95, 39, 96)
    fill_tiles(chunk, TILE_WALL, 44, 99, 45, 100)
    fill_tiles(chunk, TILE_WALL, 50, 103, 51, 104)
    fill_tiles(chunk, TILE_WALL, 56, 107, 57, 108)
    # Abyss Watcher throne debris (DS3: watcher thrones in the grand hall)
    fill_tiles(chunk, TILE_WALL, 62, 111, 63, 112)
    fill_tiles(chunk, TILE_WALL, 68, 115, 69, 116)
    fill_tiles(chunk, TILE_WALL, 74, 119, 75, 120)
    fill_tiles(chunk, TILE_WALL, 80, 123, 81, 124)
    # Darkwraith ambush stones (DS3: stones where Darkwraiths emerge)
    fill_tiles(chunk, TILE_WALL, 100, 85, 101, 86)
    fill_tiles(chunk, TILE_WALL, 106, 89, 107, 90)
    fill_tiles(chunk, TILE_WALL, 112, 93, 113, 94)
    fill_tiles(chunk, TILE_WALL, 118, 97, 119, 98)
    # Swamp crossing stones (DS3: stepping stones through the poison swamp)
    fill_tiles(chunk, TILE_WALL, 86, 102, 87, 103)
    fill_tiles(chunk, TILE_WALL, 92, 106, 93, 107)
    fill_tiles(chunk, TILE_WALL, 98, 110, 99, 111)
    fill_tiles(chunk, TILE_WALL, 104, 114, 105, 115)

    # SESSION 38 FIDELITY PASS — Farron Keep DS3 details
    # DS3: Torch platforms, ghru camp remains, Abyss Watcher memorials, darkwraith markers
    for tx in range(20, 60, 7):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)             # Torch platforms
        fill_tiles(chunk, TILE_WALL, tx, 85, tx+1, 86)
    for tx in range(65, 110, 6):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+2, 52)             # Ghru camp remains
        fill_tiles(chunk, TILE_WALL, tx, 90, tx+2, 92)
    for ty in range(40, 80, 10):
        fill_tiles(chunk, TILE_WALL, 35, ty, 37, ty+1)             # Abyss Watcher memorial stones
        fill_tiles(chunk, TILE_WALL, 85, ty, 87, ty+1)
    fill_tiles(chunk, TILE_WALL, 50, 60, 52, 62)                    # Darkwraith marker
    fill_tiles(chunk, TILE_WALL, 110, 70, 112, 72)                  # Fallen knight debris
    fill_tiles(chunk, TILE_WALL, 70, 95, 72, 97)                    # Swamp edge ruin
    for tx in range(115, 140, 6):
        fill_tiles(chunk, TILE_WALL, tx, 55, tx+1, 56)             # Rotting wood piles
    # --- SESSION 43 terrain (Farron Keep) ---
    # DS3: Swamp mud islands (higher ground in the poison swamp)
    for tx in range(30, 40):
        chunk[50][tx] = TILE_GROUND
    for tx in range(60, 70):
        chunk[45][tx] = TILE_GROUND
    # Fallen tree bridge debris
    for tx in range(80, 90):
        chunk[40][tx] = TILE_WALLTOP
    # Ghru camp fire pits
    for tx, ty in [(35, 35), (55, 40), (75, 38)]:
        chunk[ty][tx] = TILE_WALLTOP
        chunk[ty][tx+1] = TILE_WALLTOP
    # Abyss Watcher memorial stones near the boss arena
    for tx in range(90, 96):
        chunk[60][tx] = TILE_WALLTOP
    # Darkwraith emergence holes
    for tx, ty in [(50, 55), (65, 50), (80, 52)]:
        chunk[ty][tx] = TILE_WALLTOP
    # Poison swamp deep patches
    for tx in range(20, 30):
        for ty in range(55, 60):
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON
    for tx in range(70, 80):
        for ty in range(50, 55):
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON

    # --- SESSION 51 terrain (Farron Keep) ---
    # DS3: Broken sword grave markers (DS3: swords stuck in the swamp)
    for tx, ty in [(25, 30), (40, 35), (55, 32)]:
        chunk[ty][tx] = TILE_WALLTOP  # sword marker
    # Abyss Watcher tomb stones (DS3: the Watchers' graves in the keep)
    for tx in range(80, 88):
        chunk[45][tx] = TILE_WALLTOP  # tomb stone
    # Collapsed bridge supports (DS3: the bridge to the boss)
    for ty in range(55, 60):
        chunk[ty][95] = TILE_WALL  # bridge pillar
    # Swamp gas vent (DS3: gas erupts from the swamp)
    for tx in range(45, 52):
        chunk[65][tx] = TILE_WALLTOP  # vent debris
    # Ghru totem poles (DS3: ghru-built structures)
    for tx, ty in [(60, 38), (75, 42)]:
        chunk[ty][tx] = TILE_WALL  # totem pole

    # --- SESSION 55 terrain (Farron Keep final) ---
    # DS3: Abyss Watcher grave stone rows (the Watchers' cemetery)
    for tx in range(15, 25):
        chunk[25][tx] = TILE_WALLTOP  # grave marker
    # Old Wolf of Farron tower base (DS3: the wolf sits atop a tower)
    for ty in range(30, 36):
        chunk[ty][85] = TILE_WALL  # tower base
    # Swamp water channels (DS3: narrow waterways through the swamp)
    for tx in range(40, 50):
        for ty in [38, 39]:
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON
    # Ghru bonfire ring stones (DS3: ritual circles in ghru camps)
    for tx, ty in [(60, 32), (75, 35)]:
        chunk[ty][tx] = TILE_WALLTOP  # fire ring stone
        chunk[ty][tx+1] = TILE_WALLTOP

    # --- SESSION 87 DS3 terrain (Farron Keep detail pass) ---
    # DS3: Poison swamp islands (elevated ground in the swamp)
    for tx in range(15, 25):
        for ty in range(30, 38):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(40, 52):
        for ty in range(55, 65):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(65, 78):
        for ty in range(80, 90):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(90, 102):
        for ty in range(60, 70):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Ghru camp fires on the islands (small wall clusters as camps)
    for tx in [18, 20, 22]:
        for ty in [32, 34]:
            chunk[tx][ty] = TILE_WALL
    for tx in [45, 47, 49]:
        for ty in [57, 59]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Old Wolf tower (stone structure)
    for tx in range(55, 62):
        for ty in [20, 30]:
            chunk[tx][ty] = TILE_WALL
    for tx in [55, 62]:
        for ty in range(20, 31):
            chunk[tx][ty] = TILE_WALL
    for tx in range(55, 63):
        chunk[tx][19] = TILE_WALLTOP
    # DS3: Abyss Watchers mausoleum entrance
    for tx in range(110, 125):
        for ty in [95, 105]:
            chunk[tx][ty] = TILE_WALL
    for tx in [110, 125]:
        for ty in range(95, 106):
            chunk[tx][ty] = TILE_WALL
    # DS3: Three fire basin pedestals
    for tx in [25, 55, 85]:
        for ty in [45, 46, 47]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][44] = TILE_WALLTOP
    # DS3: Darkwraith holes (dark passages)
    for tx in range(35, 40):
        for ty in range(70, 75):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Broken bridge to the keep
    for tx in range(100, 115):
        chunk[tx][50] = TILE_WALL
        chunk[tx][49] = TILE_WALLTOP

    # --- SESSION 90 DS3 terrain round 2 (Farron Keep) ---
    # DS3: More swamp islands connected by tree bridges
    for tx in range(55, 65):
        for ty in range(40, 48):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(110, 120):
        for ty in range(50, 58):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Tree bridges between islands (log walkways)
    for tx in range(30, 40):
        for ty in [52, 53]:
            chunk[tx][ty] = TILE_WALL
    for tx in range(70, 80):
        for ty in [62, 63]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Memorial stones (ancient gravestones in the swamp)
    for tx in [28, 32, 38]:
        for ty in [68, 69]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Ghru camp fire rings
    for tx in range(45, 50):
        for ty in [70, 71]:
            chunk[tx][ty] = TILE_WALL
    for tx in [45, 50]:
        for ty in range(70, 72):
            chunk[tx][ty] = TILE_WALL
    # DS3: Abyss Watchers mausoleum interior
    for tx in range(112, 122):
        for ty in range(98, 106):
            chunk[tx][ty] = TILE_GROUND
    for tx in [112, 122]:
        for ty in range(98, 107):
            chunk[tx][ty] = TILE_WALL
    # DS3: Farron perimeter legion sign (stone markers)
    for tx in [12, 14, 16]:
        for ty in [30, 31]:
            chunk[tx][ty] = TILE_WALL
    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 45 * 16, 71 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Spell"),
        make_field("name", "String", "Iron Flesh (pyromancy)")]))
    entities.append(make_entity("Item", 72 * 16, 82 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Golden Scroll")]))
    entities.append(make_entity("Item", 78 * 16, 83 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Sage's Coal")]))
    entities.append(make_entity("Item", 73 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Coal"),
        make_field("name", "String", "Farron Coal (illusory wall near Old Wolf)")]))
    entities.append(make_entity("Item", 107 * 16, 150 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ashes"),
        make_field("name", "String", "Dreamchaser's Ashes")]))
    entities.append(make_entity("Item", 218 * 16, 140 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Lightning Spear (miracle)")]))
    entities.append(make_entity("Item", 113 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Scroll"),
        make_field("name", "String", "Sage's Scroll")]))
    entities.append(make_entity("Item", 122 * 16, 123 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Poison Gem")]))
    entities.append(make_entity("Item", 146 * 16, 97 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Spell"),
        make_field("name", "String", "Great Magic Weapon (sorcery)")]))
    entities.append(make_entity("Item", 174 * 16, 78 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Spell"),
        make_field("name", "String", "Atonement (miracle)")]))
    entities.append(make_entity("Item", 106 * 16, 153 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Covenant"),
        make_field("name", "String", "Wolf's Blood Swordgrass (covenant item)")]))
    entities.append(make_entity("Item", 106 * 16, 133 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BoneShard"),
        make_field("name", "String", "Undead Bone Shard")]))
    entities.append(make_entity("Item", 145 * 16, 111 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 106 * 16, 155 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 111 * 16, 151 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 168 * 16, 131 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 143 * 16, 166 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 106 * 16, 151 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 117 * 16, 103 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Heavy Gem")]))
    entities.append(make_entity("Item", 126 * 16, 115 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gem"),
        make_field("name", "String", "Hollow Gem")]))
    entities.append(make_entity("Item", 136 * 16, 123 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Shriving Stone")]))
    entities.append(make_entity("Item", 178 * 16, 78 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Greatsword")]))
    entities.append(make_entity("Item", 141 * 16, 165 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Greataxe")]))
    entities.append(make_entity("Item", 140 * 16, 98 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Talisman"),
        make_field("name", "String", "Sunlight Talisman")]))
    entities.append(make_entity("Item", 78 * 16, 79 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Black Bow of Pharis")]))
    entities.append(make_entity("Item", 80 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Stone Parma")]))
    entities.append(make_entity("Item", 211 * 16, 88 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Dragon Crest Shield")]))
    entities.append(make_entity("Item", 76 * 16, 85 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ring"),
        make_field("name", "String", "Lingering Dragoncrest Ring")]))
    entities.append(make_entity("Item", 87 * 16, 84 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Ragged Mask")]))
    entities.append(make_entity("Item", 74 * 16, 81 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Armor"),
        make_field("name", "String", "Pharis's Hat")]))
    entities.append(make_entity("Item", 211 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 77 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss Clump (swamp 1)")]))
    entities.append(make_entity("Item", 77 * 16, 86 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss Clump (swamp 2)")]))
    entities.append(make_entity("Item", 75 * 16, 82 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss Clump (swamp 3)")]))
    entities.append(make_entity("Item", 107 * 16, 155 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 108 * 16, 152 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Item"),
        make_field("name", "String", "Young White Branch")]))
    entities.append(make_entity("Item", 131 * 16, 105 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 174 * 16, 80 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 258 * 16, 178 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of a Stray Demon")]))
    entities.append(make_entity("Item", 200 * 16, 162 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Key"),
        make_field("name", "String", "Wolf's Blood (key to Abyss Watchers)")]))
    entities.append(make_entity("Item", 275 * 16, 216 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Blood of the Wolf")]))
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/FarronKeep.json") as _f:

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
    # Farron Keep: poison swamp with flame towers and Abyss Watchers mausoleum
    fill_tiles(chunk, TILE_GROUND, 22, 32, 73, 71)   # Farron Keep Entry
    fill_tiles(chunk, TILE_GROUND, 72, 53, 111, 86)   # First Flame Tower
    fill_tiles(chunk, TILE_GROUND, 93, 26, 135, 73)   # Old Wolf Tower
    fill_tiles(chunk, TILE_POISON, 106, 96, 188, 156)  # Central Swamp (poison)
    fill_tiles(chunk, TILE_GROUND, 172, 76, 217, 111)  # Second Flame Tower
    fill_tiles(chunk, TILE_GROUND, 196, 128, 243, 167) # Third Flame Tower
    fill_tiles(chunk, TILE_GROUND, 141, 133, 188, 168) # Keep Ruins
    fill_tiles(chunk, TILE_GROUND, 208, 40, 256, 73)   # Black Knight Side Path
    fill_tiles(chunk, TILE_GROUND, 223, 157, 271, 190) # Keep Perimeter
    fill_tiles(chunk, TILE_GROUND, 255, 198, 306, 237) # Abyss Watchers Mausoleum
    # Corridors connecting sections
    fill_tiles(chunk, TILE_GROUND, 46, 49, 93, 72)
    fill_tiles(chunk, TILE_GROUND, 89, 48, 116, 72)
    fill_tiles(chunk, TILE_GROUND, 112, 48, 149, 128)
    fill_tiles(chunk, TILE_GROUND, 145, 91, 197, 128)
    fill_tiles(chunk, TILE_GROUND, 193, 91, 222, 150)
    fill_tiles(chunk, TILE_GROUND, 163, 146, 222, 153)
    fill_tiles(chunk, TILE_GROUND, 163, 54, 234, 153)
    fill_tiles(chunk, TILE_GROUND, 230, 54, 249, 175)
    fill_tiles(chunk, TILE_GROUND, 245, 171, 282, 220)

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0])) if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100

    # print(f"  FarronKeep (faithful DS3 layout) ground={pct:.1f}% connectivity={coverage}%")
    return "FarronKeep", chunk, entities
