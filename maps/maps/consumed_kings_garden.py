from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_consumed_kings_garden():
    """Consumed King's Garden - descending crystal garden with Oceiros boss.
    Faithful DS3 layout: entry (NW) -> crystal courtyard -> poison swamp ->
    serpent corridor -> Oceiros throne room (SE). Crystal growths throughout.
    """
    chunk = new_chunk(256, 224)
    entities = []

    # === Garden entry (NW) ===
    fill_tiles(chunk, TILE_GROUND, 8, 8, 38, 32)
    # Vines — overgrown garden walls
    fill_tiles(chunk, TILE_WALL, 15, 14, 17, 18)
    fill_tiles(chunk, TILE_WALL, 28, 20, 30, 24)

    # === Crystal courtyard ===
    fill_tiles(chunk, TILE_GROUND, 28, 28, 72, 58)
    carve_ellipse(chunk, 50, 42, 14, 10)
    # Crystal growth walls
    fill_tiles(chunk, TILE_WALL, 38, 34, 40, 38)
    fill_tiles(chunk, TILE_WALL, 58, 45, 60, 49)
    fill_tiles(chunk, TILE_WALL, 48, 50, 50, 53)

    # === Poison swamp (center-south) ===
    fill_tiles(chunk, TILE_POISON, 35, 62, 72, 88)
    # Safe paths through the swamp
    fill_tiles(chunk, TILE_GROUND, 40, 65, 68, 85)

    # === Serpent corridor ===
    fill_tiles(chunk, TILE_GROUND, 68, 48, 105, 72)
    # Lift mid-way ledge (wiki: roll off lift halfway to reach exterior ledge → Dragonscale Ring)
    fill_tiles(chunk, TILE_GROUND, 108, 55, 122, 64)
    # Corridor walls
    fill_tiles(chunk, TILE_WALL, 78, 52, 80, 56)
    fill_tiles(chunk, TILE_WALL, 92, 60, 94, 64)

    # === Oceiros throne room (SE) ===
    fill_tiles(chunk, TILE_GROUND, 95, 70, 145, 115)
    carve_ellipse(chunk, 120, 92, 22, 18)
    # Crystal walls in throne room
    fill_tiles(chunk, TILE_WALL, 102, 78, 104, 82)
    fill_tiles(chunk, TILE_WALL, 132, 95, 134, 100)
    fill_tiles(chunk, TILE_WALL, 115, 100, 117, 106)

    # === Connections ===
    # Entry -> Courtyard
    fill_tiles(chunk, TILE_GROUND, 28, 28, 35, 32)
    # Courtyard -> Poison
    fill_tiles(chunk, TILE_GROUND, 42, 56, 50, 65)
    # Courtyard -> Corridor
    fill_tiles(chunk, TILE_GROUND, 65, 48, 72, 55)
    # Corridor -> Arena
    fill_tiles(chunk, TILE_GROUND, 100, 65, 108, 75)
    # Lift mid-way ledge connection (serpent corridor → ledge → arena approach)
    fill_tiles(chunk, TILE_GROUND, 105, 55, 112, 64)

    # === ADDITIONAL INTERNAL STRUCTURES — crystal garden ===
    # Entry — overgrown stone pillars
    fill_tiles(chunk, TILE_WALL, 12, 10, 14, 12)
    fill_tiles(chunk, TILE_WALL, 25, 15, 27, 17)
    fill_tiles(chunk, TILE_WALL, 18, 24, 20, 26)
    # Crystal courtyard — crystal growth clusters
    fill_tiles(chunk, TILE_WALL, 32, 32, 34, 35)
    fill_tiles(chunk, TILE_WALL, 42, 38, 44, 40)
    fill_tiles(chunk, TILE_WALL, 55, 35, 57, 37)
    fill_tiles(chunk, TILE_WALL, 65, 42, 67, 44)
    fill_tiles(chunk, TILE_WALL, 38, 48, 40, 50)
    fill_tiles(chunk, TILE_WALL, 60, 52, 62, 54)
    # Poison swamp — dead tree stumps
    fill_tiles(chunk, TILE_WALL, 45, 68, 47, 70)
    fill_tiles(chunk, TILE_WALL, 58, 75, 60, 77)
    fill_tiles(chunk, TILE_WALL, 50, 82, 52, 84)
    fill_tiles(chunk, TILE_WALL, 62, 80, 64, 82)
    # Serpent corridor — serpent statues
    fill_tiles(chunk, TILE_WALL, 72, 52, 74, 55)
    fill_tiles(chunk, TILE_WALL, 82, 58, 84, 60)
    fill_tiles(chunk, TILE_WALL, 95, 65, 97, 68)
    fill_tiles(chunk, TILE_WALL, 88, 70, 90, 72)
    # Throne room — crystal pillars and throne debris
    fill_tiles(chunk, TILE_WALL, 100, 75, 102, 78)
    fill_tiles(chunk, TILE_WALL, 112, 82, 114, 84)
    fill_tiles(chunk, TILE_WALL, 125, 78, 127, 80)
    fill_tiles(chunk, TILE_WALL, 138, 88, 140, 90)
    fill_tiles(chunk, TILE_WALL, 108, 92, 110, 95)
    fill_tiles(chunk, TILE_WALL, 130, 100, 132, 102)
    fill_tiles(chunk, TILE_WALL, 140, 108, 142, 110)

    # === ADDITIONAL CRYSTAL GARDEN DETAILS — DS3 fidelity ===
    # Entry staircase — stone steps with crystal encrustation (DS3: crystal-covered descent)
    fill_tiles(chunk, TILE_WALL, 10, 8, 12, 10)
    fill_tiles(chunk, TILE_WALL, 22, 12, 24, 14)
    fill_tiles(chunk, TILE_WALL, 32, 18, 34, 20)
    fill_tiles(chunk, TILE_WALL, 16, 20, 18, 22)
    # Crystal courtyard — large crystal clusters (DS3: courtyard full of crystal growths)
    fill_tiles(chunk, TILE_WALL, 30, 36, 32, 38)
    fill_tiles(chunk, TILE_WALL, 36, 42, 38, 44)
    fill_tiles(chunk, TILE_WALL, 45, 36, 47, 38)
    fill_tiles(chunk, TILE_WALL, 52, 40, 54, 42)
    fill_tiles(chunk, TILE_WALL, 62, 48, 64, 50)
    fill_tiles(chunk, TILE_WALL, 68, 38, 70, 40)
    fill_tiles(chunk, TILE_WALL, 56, 55, 58, 57)
    # Poison swamp — more dead trees and rotten logs (DS3: toxic garden with dead foliage)
    fill_tiles(chunk, TILE_WALL, 42, 72, 44, 74)
    fill_tiles(chunk, TILE_WALL, 55, 70, 57, 72)
    fill_tiles(chunk, TILE_WALL, 48, 80, 50, 82)
    fill_tiles(chunk, TILE_WALL, 62, 85, 64, 87)
    fill_tiles(chunk, TILE_WALL, 38, 84, 40, 86)
    fill_tiles(chunk, TILE_WALL, 66, 78, 68, 80)
    # Serpent corridor — more serpent statue pillars (DS3: man-serpent guards line the path)
    fill_tiles(chunk, TILE_WALL, 76, 54, 78, 56)
    fill_tiles(chunk, TILE_WALL, 85, 62, 87, 64)
    fill_tiles(chunk, TILE_WALL, 98, 68, 100, 70)
    fill_tiles(chunk, TILE_WALL, 108, 58, 110, 60)
    # Oceiros throne room — throne structure and baby crib area
    # DS3: Oceiros guards a crib, throne room has crystal throne
    fill_tiles(chunk, TILE_WALL, 118, 85, 122, 87)
    fill_tiles(chunk, TILE_WALL, 128, 88, 130, 90)
    fill_tiles(chunk, TILE_WALL, 135, 95, 137, 97)
    fill_tiles(chunk, TILE_WALL, 105, 88, 107, 90)
    fill_tiles(chunk, TILE_WALL, 142, 102, 144, 104)
    fill_tiles(chunk, TILE_WALL, 120, 105, 122, 107)
    # Lift mid-way ledge — crystal outcroppings (DS3: exterior ledge with crystals)
    fill_tiles(chunk, TILE_WALL, 110, 56, 112, 58)
    fill_tiles(chunk, TILE_WALL, 118, 60, 120, 62)
    # Additional Consumed King's Garden DS3 details
    # Entry passage — crystal-encrusted walls (DS3: crystals grow on the stonework)
    fill_tiles(chunk, TILE_WALL, 14, 14, 15, 16)
    fill_tiles(chunk, TILE_WALL, 28, 10, 29, 12)
    # Crystal courtyard — scattered crystal shards (DS3: broken crystal debris)
    fill_tiles(chunk, TILE_WALL, 40, 30, 41, 32)
    fill_tiles(chunk, TILE_WALL, 58, 46, 59, 48)
    fill_tiles(chunk, TILE_WALL, 48, 44, 49, 46)
    # Poison swamp edge — reeds and toxic plants (DS3: toxic garden overgrowth)
    fill_tiles(chunk, TILE_WALL, 35, 76, 36, 78)
    fill_tiles(chunk, TILE_WALL, 70, 82, 71, 84)
    fill_tiles(chunk, TILE_WALL, 52, 88, 53, 90)
    # Serpent corridor — additional man-serpent alcoves (DS3: serpent warriors lurk in alcoves)
    fill_tiles(chunk, TILE_WALL, 80, 66, 82, 68)
    fill_tiles(chunk, TILE_WALL, 92, 72, 94, 74)
    fill_tiles(chunk, TILE_WALL, 115, 62, 117, 64)
    # Oceiros throne — baby crib stones (DS3: Oceiros cradles an invisible baby)
    fill_tiles(chunk, TILE_WALL, 125, 92, 127, 94)
    fill_tiles(chunk, TILE_WALL, 132, 98, 134, 100)
    fill_tiles(chunk, TILE_WALL, 115, 98, 117, 100)

    # ================================================================
    # ADDITIONAL DS3 CONSUMED KING'S GARDEN — descent details, crystal growths
    # ================================================================
    # Entry — crystal-encrusted stair walls (DS3: crystals grow on descent)
    fill_tiles(chunk, TILE_WALL, 8, 12, 10, 14)
    fill_tiles(chunk, TILE_WALL, 20, 18, 22, 20)
    fill_tiles(chunk, TILE_WALL, 14, 22, 16, 24)
    fill_tiles(chunk, TILE_WALL, 26, 14, 28, 16)
    # Crystal courtyard — more crystal clusters (DS3: garden full of crystal growths)
    fill_tiles(chunk, TILE_WALL, 34, 40, 35, 42)
    fill_tiles(chunk, TILE_WALL, 44, 36, 45, 38)
    fill_tiles(chunk, TILE_WALL, 62, 44, 63, 46)
    fill_tiles(chunk, TILE_WALL, 54, 48, 55, 50)
    fill_tiles(chunk, TILE_WALL, 40, 54, 41, 56)
    fill_tiles(chunk, TILE_WALL, 68, 50, 69, 52)
    # Poison swamp — dead roots and fallen logs (DS3: toxic garden with dead foliage)
    fill_tiles(chunk, TILE_WALL, 46, 74, 47, 76)
    fill_tiles(chunk, TILE_WALL, 56, 80, 57, 82)
    fill_tiles(chunk, TILE_WALL, 64, 76, 65, 78)
    fill_tiles(chunk, TILE_WALL, 40, 86, 41, 88)
    fill_tiles(chunk, TILE_WALL, 60, 88, 61, 90)
    # Corridor — dragon statue pillars (DS3: path to Oceiros has dragon motifs)
    fill_tiles(chunk, TILE_WALL, 75, 56, 76, 58)
    fill_tiles(chunk, TILE_WALL, 88, 64, 89, 66)
    fill_tiles(chunk, TILE_WALL, 98, 68, 99, 70)
    fill_tiles(chunk, TILE_WALL, 104, 60, 105, 62)
    # Throne room — additional crystal throne debris (DS3: Oceiros guards his invisible child)
    fill_tiles(chunk, TILE_WALL, 110, 76, 111, 78)
    fill_tiles(chunk, TILE_WALL, 122, 80, 123, 82)
    fill_tiles(chunk, TILE_WALL, 135, 86, 136, 88)
    fill_tiles(chunk, TILE_WALL, 140, 92, 141, 94)
    fill_tiles(chunk, TILE_WALL, 128, 102, 129, 104)
    fill_tiles(chunk, TILE_WALL, 138, 106, 139, 108)
    # Lift mid-way ledge — crystal outcrops (DS3: hidden ledge with Dragonscale Ring)
    fill_tiles(chunk, TILE_WALL, 112, 54, 113, 56)
    fill_tiles(chunk, TILE_WALL, 120, 60, 121, 62)

    # ================================================================
    # DS3 CONSUMED KING'S GARDEN — final architectural fidelity pass
    # ================================================================
    # Entry descent — switchback stair walls (DS3: winding crystal stairs down)
    fill_tiles(chunk, TILE_WALL, 10, 18, 11, 20)
    fill_tiles(chunk, TILE_WALL, 24, 20, 25, 22)
    fill_tiles(chunk, TILE_WALL, 18, 14, 19, 16)
    # Crystal courtyard — central crystal fountain ruin (DS3: courtyard fountain with crystals)
    fill_tiles(chunk, TILE_WALL, 50, 42, 52, 45)
    fill_tiles(chunk, TILE_WALL, 46, 38, 48, 40)
    fill_tiles(chunk, TILE_WALL, 54, 46, 56, 48)
    # Lift shaft — elevator mechanism walls (DS3: lift descends between garden floors)
    fill_tiles(chunk, TILE_WALL, 100, 58, 102, 60)
    fill_tiles(chunk, TILE_WALL, 106, 64, 108, 66)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    # Poison swamp — collapsed bridge pilings (DS3: rotten wooden bridge remains in toxic pool)
    fill_tiles(chunk, TILE_WALL, 38, 78, 39, 80)
    fill_tiles(chunk, TILE_WALL, 64, 84, 65, 86)
    fill_tiles(chunk, TILE_WALL, 56, 72, 57, 74)
    fill_tiles(chunk, TILE_WALL, 44, 88, 45, 90)
    # Oceiros approach — crumbled stair edge walls (DS3: broken stairs lead to throne room)
    fill_tiles(chunk, TILE_WALL, 108, 66, 109, 68)
    fill_tiles(chunk, TILE_WALL, 114, 70, 115, 72)
    fill_tiles(chunk, TILE_WALL, 122, 74, 123, 76)
    fill_tiles(chunk, TILE_WALL, 128, 80, 129, 82)
    # Oceiros throne room — baby crib stone circle (DS3: Oceiros cradles invisible child)
    fill_tiles(chunk, TILE_WALL, 118, 88, 120, 90)
    fill_tiles(chunk, TILE_WALL, 124, 94, 126, 96)
    fill_tiles(chunk, TILE_WALL, 130, 102, 132, 104)
    fill_tiles(chunk, TILE_WALL, 136, 108, 138, 110)
    # Exterior ledge — Dragonscale Ring path walls (DS3: narrow ledge with crystal outcrops)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 58)
    fill_tiles(chunk, TILE_WALL, 120, 60, 121, 62)
    # Garden hedgerow — overgrown walls (DS3: wild garden consumed by crystal growth)
    fill_tiles(chunk, TILE_WALL, 36, 44, 37, 46)
    fill_tiles(chunk, TILE_WALL, 60, 50, 61, 52)
    fill_tiles(chunk, TILE_WALL, 68, 40, 69, 42)

    # ================================================================
    # SESSION 9 FIDELITY PASS — ConsumedKingsGarden architectural details
    # ================================================================
    # Crystal garden path — crystallized flower beds (DS3: crystal formations everywhere)
    fill_tiles(chunk, TILE_WALL, 18, 18, 19, 19)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 23)
    fill_tiles(chunk, TILE_WALL, 14, 26, 15, 27)
    fill_tiles(chunk, TILE_WALL, 28, 16, 29, 17)
    # Consumed King's throne — shattered throne stones (DS3: Oceiros's ruined throne room)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 84, 64, 85, 65)
    fill_tiles(chunk, TILE_WALL, 76, 68, 77, 69)
    fill_tiles(chunk, TILE_WALL, 88, 58, 89, 59)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    # Crystal cavern — glowing crystal pillars (DS3: crystal cave beneath garden)
    fill_tiles(chunk, TILE_WALL, 50, 80, 51, 81)
    fill_tiles(chunk, TILE_WALL, 54, 84, 55, 85)
    fill_tiles(chunk, TILE_WALL, 46, 88, 47, 89)
    fill_tiles(chunk, TILE_WALL, 58, 78, 59, 79)
    fill_tiles(chunk, TILE_WALL, 52, 90, 53, 91)
    # Oceiros arena — baby crib stones (DS3: Oceiros cradles invisible child)
    fill_tiles(chunk, TILE_WALL, 100, 40, 101, 41)
    fill_tiles(chunk, TILE_WALL, 104, 44, 105, 45)
    fill_tiles(chunk, TILE_WALL, 96, 48, 97, 49)
    fill_tiles(chunk, TILE_WALL, 108, 38, 109, 39)
    fill_tiles(chunk, TILE_WALL, 102, 50, 103, 51)
    # Overgrown hedge maze — twisted roots (DS3: wild garden with crystal-infused plants)
    fill_tiles(chunk, TILE_WALL, 32, 36, 33, 37)
    fill_tiles(chunk, TILE_WALL, 38, 40, 39, 41)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 45)
    fill_tiles(chunk, TILE_WALL, 40, 34, 41, 35)
    # Untended Graves passage — dark stone arch (DS3: hidden passage behind Oceiros)
    fill_tiles(chunk, TILE_WALL, 120, 56, 121, 57)
    fill_tiles(chunk, TILE_WALL, 124, 60, 125, 61)
    fill_tiles(chunk, TILE_WALL, 116, 64, 117, 65)

    # ================================================================
    # SESSION 13 FIDELITY PASS — ConsumedKingsGarden DS3 architecture
    # ================================================================
    # Crystal entrance — fractured stair walls (DS3: crystal-covered descent)
    fill_tiles(chunk, TILE_WALL, 6, 10, 7, 11)
    fill_tiles(chunk, TILE_WALL, 12, 16, 13, 17)
    fill_tiles(chunk, TILE_WALL, 20, 8, 21, 9)
    fill_tiles(chunk, TILE_WALL, 16, 24, 17, 25)
    fill_tiles(chunk, TILE_WALL, 22, 14, 23, 15)
    # Crystal garden — overgrown crystal clusters (DS3: wild crystal growth)
    fill_tiles(chunk, TILE_WALL, 30, 28, 31, 29)
    fill_tiles(chunk, TILE_WALL, 42, 34, 43, 35)
    fill_tiles(chunk, TILE_WALL, 58, 42, 59, 43)
    fill_tiles(chunk, TILE_WALL, 66, 36, 67, 37)
    fill_tiles(chunk, TILE_WALL, 48, 50, 49, 51)
    # Toxic swamp — bubbling pool edges (DS3: toxic pools with slugs)
    fill_tiles(chunk, TILE_WALL, 34, 82, 35, 83)
    fill_tiles(chunk, TILE_WALL, 62, 88, 63, 89)
    fill_tiles(chunk, TILE_WALL, 46, 86, 47, 87)
    fill_tiles(chunk, TILE_WALL, 68, 76, 69, 77)
    fill_tiles(chunk, TILE_WALL, 40, 72, 41, 73)
    # Serpent corridor — ruined arch columns (DS3: man-serpent path)
    fill_tiles(chunk, TILE_WALL, 78, 60, 79, 61)
    fill_tiles(chunk, TILE_WALL, 84, 56, 85, 57)
    fill_tiles(chunk, TILE_WALL, 90, 68, 91, 69)
    fill_tiles(chunk, TILE_WALL, 102, 72, 103, 73)
    fill_tiles(chunk, TILE_WALL, 96, 76, 97, 77)

    # --- Player spawn ---
    spawn_px, spawn_py = 15 * 16, 15 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))

    # --- Bonfires ---
    # DS3 Consumed King's Garden: 2 bonfires — entry (after lift down) and Oceiros boss
    entities.append(make_entity("Bonfire", 38 * 16, 38 * 16))    # Consumed King's Garden (entry)
    entities.append(make_entity("Bonfire", 191 * 16, 167 * 16))   # Oceiros the Consumed King (boss)

    # --- Boss ---
    entities.append(make_entity("BossSpawn", 195 * 16, 161 * 16))  # Oceiros

    # --- Enemies — DS3 Consumed King's Garden (wiki-accurate):
    # Cathedral Knights patrol the garden. Hollow Slaves ambush from dark corners.
    # Pus of Man on wyvern-like creatures. Rotten Slugs in toxic water.
    # No Serpent Men here (those are only in Archdragon Peak).

    # --- Items — DS3 Consumed King's Garden (complete per wiki) ---
    # Wiki items: Estus Shard, Titanite Chunk x3, Titanite Scale x3 (1 ground + 2 chests),
    # Dark Gem, Black Firebomb x2, Human Pine Resin, Claw weapon, Shadow Set,
    # Ring of Sacrifice, Dragonscale Ring, Path of the Dragon gesture
    items = [
        ("EstusShard", "Estus Shard", 50, 72, 0),
        # Dragonscale Ring — wiki: on exterior ledge accessed from lift mid-way roll-off
        ("RingDrop", "Dragonscale Ring", 115, 60, 0),
        # Path of the Dragon gesture — wiki: found in room AFTER defeating Oceiros, not in courtyard
        ("Consumable", "Path of the Dragon", 130, 100, 0),
        # Toxic swamp loot per walkthrough
        ("WeaponDrop", "Claw", 45, 74, 0),
        ("ArmorDrop", "Shadow Set", 52, 78, 0),
        ("Consumable", "Black Firebomb", 50, 74, 0),
        ("Consumable", "Black Firebomb", 56, 80, 0),
        ("Consumable", "Human Pine Resin", 50, 82, 0),
        ("RingDrop", "Ring of Sacrifice", 54, 70, 0),
        ("Consumable", "Dark Gem", 42, 68, 0),
        # Magic Stoneplate Ring (wiki: dropped by Cathedral Knight near courtyard)
        ("RingDrop", "Magic Stoneplate Ring", 52, 40, 0),
        # Tower area — from lift and staircase
        ("TitaniteShard", "Titanite Chunk", 40, 58, 0),
        ("TitaniteShard", "Titanite Chunk", 105, 72, 0),
        ("TitaniteShard", "Titanite Chunk", 92, 66, 0),
        # 4th Titanite Chunk (wiki comments: right side of courtyard near Hawkwood summon)
        ("TitaniteShard", "Titanite Chunk", 118, 85, 0),
        # Ground Titanite Scale (room before Oceiros)
        ("TitaniteShard", "Titanite Scale", 108, 75, 0),
    ]
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    # --- Chests — DS3 Consumed King's Garden ---

    
    # --- DS3 faithful enemies (ConsumedKingsGarden) ---
    # LothricKnight (12)
    for tx, ty in [(32, 30), (55, 40), (112, 82), (98, 68), (42, 38), (72, 48), (80, 55), (95, 72), (121, 83), (135, 92), (128, 101), (137, 104)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("LothricKnight", "LothricKnight"))]))
    # Thrall (12)
    for tx, ty in [(35, 35), (88, 62), (22, 22), (60, 32), (90, 58), (100, 64), (108, 70), (118, 78), (125, 86), (136, 89), (135, 98), (112, 113)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("Thrall", "Thrall"))]))
    # PusOfMan (3)
    entities.append(make_entity("Enemy", 52 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    entities.append(make_entity("Enemy", 48 * 16, 76 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    entities.append(make_entity("Enemy", 58 * 16, 84 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("PusOfMan", "PusOfMan"))]))
    # RottenSlug (5) — DS3: slugs in the garden swamp
    for tx, ty in [(45, 70), (50, 75), (55, 78), (42, 78), (60, 82)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("RottenSlug", "RottenSlug"))]))
    # HollowSoldier (4) — DS3: hollow soldiers on the garden paths
    for tx, ty in [(48, 72), (56, 68), (44, 82), (52, 84)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowSoldier", "HollowSoldier"))]))
    # CrystalLizard (1)
    entities.append(make_entity("Enemy", 68 * 16, 42 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))
    # MiniBoss (1)
    entities.append(make_entity("Enemy", 120 * 16, 88 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))

# --- NPCs ---
    # Hawkwood — summon sign before Oceiros (DS3: he can be summoned for Oceiros)
    entities.append(make_entity("Npc", 185 * 16, 142 * 16, [
        make_field("name", "String", "Hawkwood"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#7F8C8D"),
        make_field("dialogue", "String",
            "I came to see Oceiros, the Consumed King|He holds the secret of the Path of the Dragon|But it seems I am too late|The dragon stones may still be of use"),
    ]))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 35 * 16, 33 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 45 * 16, 37 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 67 * 16, 83 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "EstusShard"),
        make_field("name", "String", "Estus Shard")]))
    entities.append(make_entity("Item", 81 * 16, 92 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 95 * 16, 100 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TitaniteShard"),
        make_field("name", "String", "Titanite Shard")]))
    entities.append(make_entity("Item", 107 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 71 * 16, 98 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss Clump")]))
    entities.append(make_entity("Item", 85 * 16, 106 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss Clump")]))
    entities.append(make_entity("Item", 98 * 16, 111 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Dung Pie")]))
    entities.append(make_entity("Item", 112 * 16, 116 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 126 * 16, 71 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Large Soul of a Nameless Soldier")]))
    entities.append(make_entity("Item", 141 * 16, 76 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 152 * 16, 87 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Weapon"),
        make_field("name", "String", "Lothric Knight Greatsword")]))
    entities.append(make_entity("Item", 131 * 16, 78 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Green Blossom")]))
    entities.append(make_entity("Item", 157 * 16, 82 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "HomewardBone"),
        make_field("name", "String", "Homeward Bone")]))
    entities.append(make_entity("Item", 153 * 16, 118 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "SoulOrb"),
        make_field("name", "String", "Soul of a Weary Warrior")]))
    entities.append(make_entity("Item", 165 * 16, 123 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "LargeTitaniteShard"),
        make_field("name", "String", "Large Titanite Shard")]))
    entities.append(make_entity("Item", 178 * 16, 130 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Ember"),
        make_field("name", "String", "Ember")]))
    entities.append(make_entity("Item", 157 * 16, 127 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Consumable"),
        make_field("name", "String", "Purple Moss Clump")]))
    entities.append(make_entity("Item", 165 * 16, 128 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 191 * 16, 168 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of Oceiros, the Consumed King")]))
    entities.append(make_entity("Item", 211 * 16, 142 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "Gesture"),
        make_field("name", "String", "Dragon Head Stone")]))
    entities.append(make_entity("Item", 218 * 16, 146 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    entities.append(make_entity("Item", 222 * 16, 150 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "TwinklingTitanite"),
        make_field("name", "String", "Twinkling Titanite")]))
    # --- DS3 faithful chests ---
    entities.append(make_entity("Chest", 117 * 16, 115 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 181 * 16, 133 * 16, [
        make_field("name", "String", "Unknown")]))
    entities.append(make_entity("Chest", 215 * 16, 147 * 16, [
        make_field("name", "String", "Unknown")]))
# --- Fog Gates ---
    # Back to Lothric Castle (NW)
    entities.append(make_entity("FogGate", 38 * 16, 32 * 16, [
        make_field("dest_area", "String", "LothricCastle"),
        make_field("dest_x", "Float", 1000.0),
        make_field("dest_y", "Float", 900.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))
    # To Untended Graves (E)
    entities.append(make_entity("FogGate", 212 * 16, 141 * 16, [
        make_field("dest_area", "String", "UntendedGraves"),
        make_field("dest_x", "Float", 300.0),
        make_field("dest_y", "Float", 400.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # Fog Gate back to Lothric Wall (DS3: return path from Consumed King's Garden)
    entities.append(make_entity("FogGate", 10 * 16, 90 * 16, [
        make_field("dest_area", "String", "LothricWall"),
        make_field("dest_x", "Float", 2200.0), make_field("dest_y", "Float", 2300.0),
        make_field("width", "Float", 64.0), make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 38 * 16, 38 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.8),
        make_field("b", "Float", 0.5), make_field("intensity", "Float", 0.4)]))
    entities.append(make_entity("Light", 32 * 16, 32 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 75 * 16, 93 * 16, [
        make_field("radius", "Float", 200.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 93 * 16, 102 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 62 * 16, 81 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.25)]))
    entities.append(make_entity("Light", 112 * 16, 110 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.2), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 136 * 16, 75 * 16, [
        make_field("radius", "Float", 180.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 153 * 16, 81 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.6), make_field("g", "Float", 0.7),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 161 * 16, 120 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.35)]))
    entities.append(make_entity("Light", 176 * 16, 128 * 16, [
        make_field("radius", "Float", 120.0),
        make_field("r", "Float", 0.5), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.6), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 191 * 16, 167 * 16, [
        make_field("radius", "Float", 260.0),
        make_field("r", "Float", 0.3), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.7), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 183 * 16, 160 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 198 * 16, 175 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.4), make_field("g", "Float", 0.5),
        make_field("b", "Float", 0.8), make_field("intensity", "Float", 0.3)]))
    entities.append(make_entity("Light", 212 * 16, 143 * 16, [
        make_field("radius", "Float", 100.0),
        make_field("r", "Float", 0.2), make_field("g", "Float", 0.2),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.4)]))
    # Poison swamp — sickly green
    # Oceiros arena — dark crystal
    # SESSION 10 FIDELITY PASS — Consumed King's Garden
    # Additional DS3-faithful terrain: crystal shard debris, consumed throne stones,
    # garden pool edges, crystal growth formations, consumed knight patrol debris
    # Crystal formations near entrance (DS3: crystal growths everywhere)
    fill_tiles(chunk, TILE_WALL, 48, 52, 49, 53)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 56, 54, 57, 55)
    # Garden pool edge stones (DS3: stagnant water pools with crystal growths)
    fill_tiles(chunk, TILE_WALL, 60, 58, 61, 59)
    fill_tiles(chunk, TILE_WALL, 66, 62, 67, 63)
    fill_tiles(chunk, TILE_WALL, 72, 60, 73, 61)
    # Consumed throne area — throne debris (DS3: Oceiros throne room with crystal growths)
    fill_tiles(chunk, TILE_WALL, 108, 82, 109, 83)
    fill_tiles(chunk, TILE_WALL, 114, 84, 115, 85)
    fill_tiles(chunk, TILE_WALL, 102, 78, 103, 79)
    fill_tiles(chunk, TILE_WALL, 118, 80, 119, 81)
    # Crystal cavern stalactites (DS3: crystal cave area behind Oceiros)
    fill_tiles(chunk, TILE_WALL, 128, 72, 129, 73)
    fill_tiles(chunk, TILE_WALL, 134, 68, 135, 69)
    fill_tiles(chunk, TILE_WALL, 138, 74, 139, 75)
    fill_tiles(chunk, TILE_WALL, 130, 78, 131, 79)
    fill_tiles(chunk, TILE_WALL, 136, 82, 137, 83)
    fill_tiles(chunk, TILE_WALL, 142, 70, 143, 71)
    # Knight patrol path debris (DS3: Cathedral Knights patrol garden paths)
    fill_tiles(chunk, TILE_WALL, 82, 64, 83, 65)
    fill_tiles(chunk, TILE_WALL, 88, 60, 89, 61)
    fill_tiles(chunk, TILE_WALL, 94, 66, 95, 67)
    fill_tiles(chunk, TILE_WALL, 78, 70, 79, 71)
    fill_tiles(chunk, TILE_WALL, 90, 72, 91, 73)
    # Crystal growth clusters (DS3: large crystal formations in garden)
    fill_tiles(chunk, TILE_WALL, 44, 68, 45, 69)
    fill_tiles(chunk, TILE_WALL, 50, 74, 51, 75)
    fill_tiles(chunk, TILE_WALL, 64, 70, 65, 71)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    # Lower garden — Thrall ambush debris (DS3: Thralls hide among crystal debris)
    fill_tiles(chunk, TILE_WALL, 86, 76, 87, 77)
    fill_tiles(chunk, TILE_WALL, 96, 78, 97, 79)
    fill_tiles(chunk, TILE_WALL, 100, 74, 101, 75)

    # SESSION 10 FIDELITY PASS B — Consumed King's Garden
    # Additional DS3-faithful terrain: crystal growth clusters, Oceiros throne room,
    # consumed knight path debris, garden bridge stones, crystal cavern details
    # Entrance garden — crystal growth clusters (DS3: crystals grow wild in garden)
    fill_tiles(chunk, TILE_WALL, 44, 54, 45, 55)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 56, 58, 57, 59)
    fill_tiles(chunk, TILE_WALL, 40, 60, 41, 61)
    fill_tiles(chunk, TILE_WALL, 46, 62, 47, 63)
    # Garden bridge — stone bridge debris (DS3: stone bridge over garden)
    fill_tiles(chunk, TILE_WALL, 70, 56, 71, 57)
    fill_tiles(chunk, TILE_WALL, 76, 58, 77, 59)
    fill_tiles(chunk, TILE_WALL, 82, 56, 83, 57)
    fill_tiles(chunk, TILE_WALL, 74, 60, 75, 61)
    # Oceiros throne room — throne debris (DS3: Oceiros guards his throne)
    fill_tiles(chunk, TILE_WALL, 104, 76, 105, 77)
    fill_tiles(chunk, TILE_WALL, 110, 78, 111, 79)
    fill_tiles(chunk, TILE_WALL, 116, 76, 117, 77)
    fill_tiles(chunk, TILE_WALL, 120, 80, 121, 81)
    fill_tiles(chunk, TILE_WALL, 106, 82, 107, 83)
    fill_tiles(chunk, TILE_WALL, 112, 84, 113, 85)
    # Crystal cavern — deep crystal formations (DS3: crystal cave behind throne)
    fill_tiles(chunk, TILE_WALL, 126, 70, 127, 71)
    fill_tiles(chunk, TILE_WALL, 132, 74, 133, 75)
    fill_tiles(chunk, TILE_WALL, 138, 72, 139, 73)
    fill_tiles(chunk, TILE_WALL, 144, 76, 145, 77)
    fill_tiles(chunk, TILE_WALL, 130, 78, 131, 79)
    fill_tiles(chunk, TILE_WALL, 140, 80, 141, 81)
    # Consumed knight patrol — path debris (DS3: Cathedral Knights patrol garden)
    fill_tiles(chunk, TILE_WALL, 62, 66, 63, 67)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 78, 70, 79, 71)
    fill_tiles(chunk, TILE_WALL, 84, 72, 85, 73)
    fill_tiles(chunk, TILE_WALL, 92, 74, 93, 75)
    fill_tiles(chunk, TILE_WALL, 98, 72, 99, 73)
    # Pus of Man area — consumed growth debris (DS3: Pus of Man creatures)
    fill_tiles(chunk, TILE_WALL, 52, 72, 53, 73)
    fill_tiles(chunk, TILE_WALL, 58, 76, 59, 77)
    fill_tiles(chunk, TILE_WALL, 64, 74, 65, 75)
    # Lower garden — Thrall ambush stones (DS3: Thralls hide among debris)
    fill_tiles(chunk, TILE_WALL, 88, 80, 89, 81)
    fill_tiles(chunk, TILE_WALL, 94, 82, 95, 83)
    fill_tiles(chunk, TILE_WALL, 100, 78, 101, 79)
    fill_tiles(chunk, TILE_WALL, 96, 84, 97, 85)

    # ================================================================
    # SESSION 14 FIDELITY PASS — ConsumedKingsGarden DS3 terrain details
    # ================================================================
    # Crystal entrance — fractured crystal shards (DS3: crystal growths at entrance)
    fill_tiles(chunk, TILE_WALL, 18, 10, 19, 11)
    fill_tiles(chunk, TILE_WALL, 24, 14, 25, 15)
    fill_tiles(chunk, TILE_WALL, 30, 12, 31, 13)
    fill_tiles(chunk, TILE_WALL, 36, 16, 37, 17)
    # Overgrown garden — toxic vine clusters (DS3: consumed by crystal growth)
    fill_tiles(chunk, TILE_WALL, 42, 20, 43, 21)
    fill_tiles(chunk, TILE_WALL, 48, 24, 49, 25)
    fill_tiles(chunk, TILE_WALL, 54, 22, 55, 23)
    fill_tiles(chunk, TILE_WALL, 60, 26, 61, 27)
    # Oceiros throne room — royal debris (DS3: consumed king's throne room)
    fill_tiles(chunk, TILE_WALL, 110, 85, 111, 86)
    fill_tiles(chunk, TILE_WALL, 116, 88, 117, 89)
    fill_tiles(chunk, TILE_WALL, 122, 82, 123, 83)
    fill_tiles(chunk, TILE_WALL, 128, 86, 129, 87)
    # Crystal garden — crystal formation bases (DS3: crystal clusters everywhere)
    fill_tiles(chunk, TILE_WALL, 40, 34, 41, 35)
    fill_tiles(chunk, TILE_WALL, 46, 38, 47, 39)
    fill_tiles(chunk, TILE_WALL, 52, 36, 53, 37)
    fill_tiles(chunk, TILE_WALL, 58, 40, 59, 41)
    # Toxic swamp — corroded stone edges (DS3: toxic pools in lower garden)
    fill_tiles(chunk, TILE_WALL, 72, 60, 73, 61)
    fill_tiles(chunk, TILE_WALL, 78, 64, 79, 65)
    fill_tiles(chunk, TILE_WALL, 84, 62, 85, 63)
    fill_tiles(chunk, TILE_WALL, 90, 66, 91, 67)
    # Serpent corridor — ruined arch columns (DS3: passage with Cathedral Knights)
    fill_tiles(chunk, TILE_WALL, 20, 30, 21, 31)
    fill_tiles(chunk, TILE_WALL, 26, 34, 27, 35)
    fill_tiles(chunk, TILE_WALL, 32, 32, 33, 33)
    fill_tiles(chunk, TILE_WALL, 38, 36, 39, 37)

    # ================================================================
    # SESSION 17 FIDELITY PASS — ConsumedKingsGarden DS3 overgrown ruins
    # ================================================================
    # Castle garden — overgrown wall sections (DS3: consumed by Oceiros's magic)
    fill_tiles(chunk, TILE_WALL, 44, 40, 45, 42)
    fill_tiles(chunk, TILE_WALL, 52, 44, 53, 46)
    fill_tiles(chunk, TILE_WALL, 60, 38, 61, 40)
    fill_tiles(chunk, TILE_WALL, 68, 42, 69, 44)
    # Cathedral Knight barracks — weapon rack alcoves (DS3: knights guard the garden)
    fill_tiles(chunk, TILE_WALL, 76, 46, 77, 48)
    fill_tiles(chunk, TILE_WALL, 84, 50, 85, 52)
    fill_tiles(chunk, TILE_WALL, 92, 44, 93, 46)
    fill_tiles(chunk, TILE_WALL, 100, 48, 101, 50)
    # Toxic pools — corroded stone edges (DS3: toxic water from consumed garden)
    fill_tiles(chunk, TILE_WALL, 108, 52, 109, 54)
    fill_tiles(chunk, TILE_WALL, 116, 56, 117, 58)
    fill_tiles(chunk, TILE_WALL, 124, 50, 125, 52)
    # Oceiros throne room — crystal debris (DS3: Oceiros's throne room with crystals)
    fill_tiles(chunk, TILE_WALL, 132, 54, 133, 56)
    fill_tiles(chunk, TILE_WALL, 140, 58, 141, 60)
    fill_tiles(chunk, TILE_WALL, 148, 52, 149, 54)
    fill_tiles(chunk, TILE_WALL, 136, 62, 137, 64)
    # Thrall ambush alcoves — dark corners (DS3: Thralls hide in dark corners)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 40)
    fill_tiles(chunk, TILE_WALL, 36, 42, 37, 44)
    fill_tiles(chunk, TILE_WALL, 48, 36, 49, 38)
    fill_tiles(chunk, TILE_WALL, 56, 40, 57, 42)

    # ================================================================
    # SESSION 19 FIDELITY PASS — ConsumedKingsGarden DS3 garden depth
    # ================================================================
    # Castle garden steps — moss-covered stones (DS3: overgrown stone stairs)
    fill_tiles(chunk, TILE_WALL, 22, 46, 23, 48)
    fill_tiles(chunk, TILE_WALL, 30, 50, 31, 52)
    fill_tiles(chunk, TILE_WALL, 38, 54, 39, 56)
    fill_tiles(chunk, TILE_WALL, 46, 58, 47, 60)
    fill_tiles(chunk, TILE_WALL, 54, 62, 55, 64)
    # Crystal growth — crystal spike bases (DS3: Oceiros's crystal magic)
    fill_tiles(chunk, TILE_WALL, 62, 66, 63, 68)
    fill_tiles(chunk, TILE_WALL, 70, 70, 71, 72)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 76)
    fill_tiles(chunk, TILE_WALL, 86, 78, 87, 80)
    fill_tiles(chunk, TILE_WALL, 94, 82, 95, 84)
    # Untended Graves path — dark stone debris (DS3: illusory wall to dark shrine)
    fill_tiles(chunk, TILE_WALL, 102, 86, 103, 88)
    fill_tiles(chunk, TILE_WALL, 110, 90, 111, 92)
    fill_tiles(chunk, TILE_WALL, 118, 94, 119, 96)
    fill_tiles(chunk, TILE_WALL, 126, 98, 127, 100)
    fill_tiles(chunk, TILE_WALL, 134, 102, 135, 104)

    # ================================================================
    # SESSION 22 FIDELITY PASS — ConsumedKingsGarden DS3 garden details
    # ================================================================
    # Hedge maze walls (DS3: garden hedges forming maze paths)
    fill_tiles(chunk, TILE_WALL, 22, 30, 23, 31)
    fill_tiles(chunk, TILE_WALL, 28, 34, 29, 35)
    fill_tiles(chunk, TILE_WALL, 34, 38, 35, 39)
    fill_tiles(chunk, TILE_WALL, 40, 42, 41, 43)
    # Toxic pool edge stones (DS3: stone borders around poison pools)
    fill_tiles(chunk, TILE_WALL, 46, 46, 47, 47)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 58, 54, 59, 55)
    fill_tiles(chunk, TILE_WALL, 64, 58, 65, 59)
    # Oceiros throne debris (DS3: shattered throne near Oceiros arena)
    fill_tiles(chunk, TILE_WALL, 70, 62, 71, 63)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    fill_tiles(chunk, TILE_WALL, 88, 74, 89, 75)
    # Wyvern skeleton debris (DS3: dragon remains in the garden)
    fill_tiles(chunk, TILE_WALL, 94, 78, 95, 79)
    fill_tiles(chunk, TILE_WALL, 100, 82, 101, 83)
    fill_tiles(chunk, TILE_WALL, 106, 86, 107, 87)
    fill_tiles(chunk, TILE_WALL, 112, 90, 113, 91)

    # ================================================================
    # SESSION 26 FIDELITY PASS — ConsumedKingsGarden DS3 garden details
    # ================================================================
    # Garden hedge walls (DS3: overgrown hedges forming maze paths)
    fill_tiles(chunk, TILE_WALL, 18, 34, 19, 35)
    fill_tiles(chunk, TILE_WALL, 24, 38, 25, 39)
    fill_tiles(chunk, TILE_WALL, 30, 42, 31, 43)
    fill_tiles(chunk, TILE_WALL, 36, 46, 37, 47)
    # Poison mist debris (DS3: toxic mist lingering around pools)
    fill_tiles(chunk, TILE_WALL, 42, 50, 43, 51)
    fill_tiles(chunk, TILE_WALL, 48, 54, 49, 55)
    fill_tiles(chunk, TILE_WALL, 54, 58, 55, 59)
    fill_tiles(chunk, TILE_WALL, 60, 62, 61, 63)
    # Oceiros crystal formations (DS3: crystal growth near Oceiros arena)
    fill_tiles(chunk, TILE_WALL, 66, 66, 67, 67)
    fill_tiles(chunk, TILE_WALL, 72, 70, 73, 71)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 75)
    fill_tiles(chunk, TILE_WALL, 84, 78, 85, 79)
    # Wyvern skeleton debris (DS3: dragon remains in the garden)
    fill_tiles(chunk, TILE_WALL, 90, 82, 91, 83)
    fill_tiles(chunk, TILE_WALL, 96, 86, 97, 87)
    fill_tiles(chunk, TILE_WALL, 102, 90, 103, 91)
    fill_tiles(chunk, TILE_WALL, 108, 94, 109, 95)

    # ================================================================
    # SESSION 29 FIDELITY PASS — ConsumedKingsGarden DS3 garden details
    # ================================================================
    # Garden path cobblestones (DS3: broken cobblestone paths)
    fill_tiles(chunk, TILE_WALL, 24, 40, 25, 41)
    fill_tiles(chunk, TILE_WALL, 30, 44, 31, 45)
    fill_tiles(chunk, TILE_WALL, 36, 48, 37, 49)
    fill_tiles(chunk, TILE_WALL, 42, 52, 43, 53)
    # Pus of Man wyrm remains (DS3: wyrm corpses infected by pus of man)
    fill_tiles(chunk, TILE_WALL, 48, 56, 49, 57)
    fill_tiles(chunk, TILE_WALL, 54, 60, 55, 61)
    fill_tiles(chunk, TILE_WALL, 60, 64, 61, 65)
    fill_tiles(chunk, TILE_WALL, 66, 68, 67, 69)
    # Oceiros crystal growth (DS3: crystal formations in Oceiros arena)
    fill_tiles(chunk, TILE_WALL, 72, 72, 73, 73)
    fill_tiles(chunk, TILE_WALL, 78, 76, 79, 77)
    fill_tiles(chunk, TILE_WALL, 84, 80, 85, 81)
    fill_tiles(chunk, TILE_WALL, 90, 84, 91, 85)
    # Toxic mist markers (DS3: toxic mist clouds in the lower garden)
    fill_tiles(chunk, TILE_WALL, 96, 88, 97, 89)
    fill_tiles(chunk, TILE_WALL, 102, 92, 103, 93)
    fill_tiles(chunk, TILE_WALL, 108, 96, 109, 97)
    fill_tiles(chunk, TILE_WALL, 114, 100, 115, 101)

    # SESSION 36 FIDELITY PASS — Consumed King's Garden DS3 details
    # DS3: Hedge maze walls, toxic pool edges, Oceiros crystal garden
    for tx in range(30, 70, 6):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)             # Hedge wall segments
        fill_tiles(chunk, TILE_WALL, tx, 85, tx+1, 86)
    for tx in range(80, 120, 6):
        fill_tiles(chunk, TILE_WALL, tx, 50, tx+1, 51)             # Crystal cluster bases
        fill_tiles(chunk, TILE_WALL, tx, 90, tx+1, 91)
    for ty in range(35, 70, 8):
        fill_tiles(chunk, TILE_WALL, 40, ty, 41, ty+1)             # Garden path stones
        fill_tiles(chunk, TILE_WALL, 90, ty, 91, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 65, 58, 68)                    # Toxic pool edge
    fill_tiles(chunk, TILE_WALL, 110, 75, 112, 77)                  # Crystal formation
    fill_tiles(chunk, TILE_WALL, 70, 100, 72, 102)                  # Wyrm bone scatter
    fill_tiles(chunk, TILE_WALL, 130, 55, 132, 57)                  # Oceiros arena debris
    # SESSION 40 FIDELITY PASS — Consumed King's Garden DS3 details
    for tx in range(35, 75, 5):
        fill_tiles(chunk, TILE_WALL, tx, 40, tx+1, 41)
        fill_tiles(chunk, TILE_WALL, tx, 80, tx+1, 81)
    for tx in range(80, 120, 5):
        fill_tiles(chunk, TILE_WALL, tx, 45, tx+1, 46)
        fill_tiles(chunk, TILE_WALL, tx, 85, tx+1, 86)
    for ty in range(35, 75, 7):
        fill_tiles(chunk, TILE_WALL, 30, ty, 31, ty+1)
        fill_tiles(chunk, TILE_WALL, 130, ty, 131, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)
    fill_tiles(chunk, TILE_WALL, 100, 70, 102, 72)
    fill_tiles(chunk, TILE_WALL, 75, 90, 77, 92)
    # --- SESSION 45 terrain (Consumed King's Garden) ---
    # DS3: Overgrown hedge walls forming maze-like paths
    for tx in range(15, 25):
        chunk[30][tx] = TILE_WALLTOP  # hedge debris
    for tx in range(40, 50):
        chunk[25][tx] = TILE_WALLTOP  # overgrown hedge
    # Crystal formations from Oceiros's magic
    for tx, ty in [(55, 35), (60, 38), (65, 32)]:
        chunk[ty][tx] = TILE_WALL  # crystal growth
    # Toxic pool stones (DS3: poison swamp in the garden)
    for tx in range(70, 80):
        for ty in range(40, 44):
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON
    # Oceiros throne room crystal pillars (DS3: crystals everywhere in boss room)
    for ty in range(50, 56):
        chunk[ty][85] = TILE_WALL  # crystal pillar
    for ty in range(48, 54):
        chunk[ty][90] = TILE_WALL  # crystal pillar
    # Garden pathway stones
    for tx in range(30, 38):
        chunk[45][tx] = TILE_WALLTOP  # cracked paving

    # --- SESSION 52 terrain (Consumed King's Garden) ---
    # DS3: Consumed garden overgrown paths
    for tx in range(25, 35):
        chunk[55][tx] = TILE_WALLTOP  # overgrown debris
    # Oceiros crystal throne room floor
    for tx in range(80, 92):
        chunk[58][tx] = TILE_WALLTOP  # crystal floor debris
    # Consumed King's treasure pile
    for tx in range(60, 65):
        chunk[48][tx] = TILE_WALLTOP  # treasure debris
    # Toxic fountain (DS3: the poisoned garden fountain)
    chunk[42][45] = TILE_WALL  # fountain edge
    chunk[42][46] = TILE_WALL
    for tx in range(46, 50):
        for ty in [42, 43]:
            if chunk[ty][tx] == TILE_GROUND:
                chunk[ty][tx] = TILE_POISON

    # --- SESSION 89 DS3 terrain (Consumed King's Garden detail pass) ---
    # DS3: Hedge walls (overgrown garden paths)
    for tx in [20, 25, 30, 35, 40, 45, 50, 55, 60]:
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][19] = TILE_WALLTOP
    # DS3: Crystal formations growing from walls
    for tx in [35, 45, 55, 65, 75]:
        for ty in [28, 29, 30]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Toxic pools in the lower garden
    for tx in range(30, 50):
        for ty in range(40, 50):
            chunk[tx][ty] = TILE_POISON
    for tx in range(60, 80):
        for ty in range(55, 65):
            chunk[tx][ty] = TILE_POISON
    # DS3: Crystal pillars (large growths)
    for tx in [25, 40, 55, 70, 85]:
        for ty in range(35, 42):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Pathway stones (garden path)
    for tx in range(15, 90):
        for ty in [32, 33]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Oceiros arena (open chamber with crystal growths)
    for tx in range(80, 110):
        for ty in range(70, 90):
            chunk[tx][ty] = TILE_GROUND
    for tx in [80, 110]:
        for ty in range(70, 91):
            chunk[tx][ty] = TILE_WALL
    for tx in [85, 90, 95, 100, 105]:
        for ty in [75, 80, 85]:
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 93 DS3 terrain round 2 (Consumed King's Garden) ---
    # DS3: Crystal growth along the walls
    for tx in [20, 28, 36, 44, 52, 60, 68, 76]:
        for ty in [32, 33, 34]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Consumed King's chamber (Oceiros arena)
    for tx in range(80, 100):
        for ty in range(60, 78):
            chunk[tx][ty] = TILE_GROUND
    for tx in [80, 100]:
        for ty in range(60, 79):
            chunk[tx][ty] = TILE_WALL
    for tx in range(80, 101):
        for ty in [60, 78]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Crystal waterfall (wall of crystal growths)
    for tx in range(85, 95):
        for ty in [50, 51, 52]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Garden path stones (winding path)
    for tx in range(25, 80):
        for ty in [38, 39]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Hidden wall (illusionary wall to Oceiros)
    for tx in range(75, 82):
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Toxic water pools
    for tx in range(35, 50):
        for ty in range(45, 52):
            chunk[tx][ty] = TILE_POISON
    for tx in range(60, 75):
        for ty in range(65, 72):
            chunk[tx][ty] = TILE_POISON
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/ConsumedKingsGarden.json") as _f:

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
    fill_tiles(chunk, TILE_GROUND, 26, 26, 73, 58)   # Lower Dancer Lift
    fill_tiles(chunk, TILE_GROUND, 56, 73, 131, 125)  # Poison Garden
    fill_tiles(chunk, TILE_GROUND, 117, 61, 168, 101)  # Lothric Knight Platform
    fill_tiles(chunk, TILE_GROUND, 172, 148, 223, 188) # Oceiros Arena
    fill_tiles(chunk, TILE_GROUND, 203, 135, 236, 161) # Untended Graves Illusory Wall
    fill_tiles(chunk, TILE_GROUND, 180, 137, 190, 147) # Supplement area
    # Corridors connecting sections
    fill_tiles(chunk, TILE_GROUND, 48, 40, 95, 101)
    fill_tiles(chunk, TILE_GROUND, 91, 79, 145, 101)
    fill_tiles(chunk, TILE_GROUND, 141, 79, 200, 170)
    fill_tiles(chunk, TILE_GROUND, 196, 146, 222, 170)
    fill_tiles(chunk, TILE_GROUND, 183, 140, 222, 150)

    snap_entities_to_walkable(chunk, entities)

    populate_entity_def_uids(entities)
    entity_positions = [(e["px"][0], e["px"][1]) for e in entities]
    coverage = ensure_connected(chunk, spawn_px, spawn_py, entity_positions)
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0]))
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100
    # print(f"  ConsumedKingsGarden (faithful DS3 layout) "
    # f"ground={pct:.1f}% connectivity={coverage}%")
    return "ConsumedKingsGarden", chunk, entities
