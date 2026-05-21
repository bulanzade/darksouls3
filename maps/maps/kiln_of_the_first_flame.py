from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    ENEMY_KIND_MAP,
    new_chunk, fill_tiles, carve_ellipse, cw,
    carve_corridor, make_entity, make_field,
    ensure_connected, poison_tile,
    populate_entity_def_uids, snap_entities_to_walkable,
)

def make_kiln_of_the_first_flame():
    """Kiln of the First Flame - ash wasteland with Soul of Cinder boss.
    Faithful DS3 layout: Flameless Shrine entry (south) -> winding ash path through
    collapsed ruins -> twisted girder hall (middle) -> First Flame arena (north).
    No regular enemies. The end of all things.
    """
    chunk = new_chunk(192, 192)
    entities = []

    # ================================================================
    # TERRAIN — DS3 Kiln is a linear descent through ash and ruin
    # ================================================================

    # === 1. FLAMELESS SHRINE (south) — entry area from Grand Archives ===
    # Wide ash platform with ruined walls framing the entry
    fill_tiles(chunk, TILE_GROUND, 62, 140, 98, 158)
    # Collapsed entry arch — remnants of the kiln door
    fill_tiles(chunk, TILE_WALL, 64, 140, 68, 146)
    fill_tiles(chunk, TILE_WALL, 92, 140, 96, 146)
    # Ash dunes around the entry (elevated terrain framing the path)
    fill_tiles(chunk, TILE_WALL, 58, 142, 62, 152)
    fill_tiles(chunk, TILE_WALL, 98, 142, 102, 152)
    # Rubble pile near shrine bonfire
    fill_tiles(chunk, TILE_WALL, 78, 144, 82, 148)

    # === 2. ASH CORRIDOR — winding path through collapsed kiln walls ===
    # DS3: narrow path flanked by towering ash dunes and twisted metal
    fill_tiles(chunk, TILE_GROUND, 66, 128, 94, 142)
    # Left ash dune wall (tall, forces player through narrow gap)
    fill_tiles(chunk, TILE_WALL, 56, 118, 70, 130)
    fill_tiles(chunk, TILE_WALL, 72, 122, 76, 128)
    # Right ash dune wall
    fill_tiles(chunk, TILE_WALL, 84, 122, 88, 128)
    fill_tiles(chunk, TILE_WALL, 90, 118, 104, 130)
    # Twisted girder remnant across the path
    fill_tiles(chunk, TILE_WALL, 74, 126, 78, 128)
    # Rubble at corridor edges
    fill_tiles(chunk, TILE_WALL, 66, 130, 68, 134)
    fill_tiles(chunk, TILE_WALL, 92, 130, 94, 134)

    # === 3. COLLAPSED CHAMBER — first open area with ruined structures ===
    fill_tiles(chunk, TILE_GROUND, 52, 104, 108, 120)
    carve_ellipse(chunk, 80, 112, 18, 6)
    # Fallen pillar remnants (DS3: huge stone pillars collapsed across the hall)
    fill_tiles(chunk, TILE_WALL, 58, 106, 62, 114)
    fill_tiles(chunk, TILE_WALL, 98, 106, 102, 114)
    # Crossed girders on the ground
    fill_tiles(chunk, TILE_WALL, 68, 108, 72, 110)
    fill_tiles(chunk, TILE_WALL, 88, 110, 92, 112)
    # Ash drifts along walls
    fill_tiles(chunk, TILE_WALL, 54, 108, 56, 116)
    fill_tiles(chunk, TILE_WALL, 104, 108, 106, 116)
    # Scattered rubble
    fill_tiles(chunk, TILE_WALL, 76, 114, 78, 116)
    fill_tiles(chunk, TILE_WALL, 82, 114, 84, 116)

    # === 4. TWISTED GIRDER HALL — dense collapsed metal structure ===
    # DS3: the most iconic section — massive twisted iron beams everywhere
    fill_tiles(chunk, TILE_GROUND, 48, 78, 112, 106)
    carve_ellipse(chunk, 80, 92, 20, 10)
    # Main girder structures — diagonal collapsed beams
    fill_tiles(chunk, TILE_WALL, 52, 82, 56, 96)
    fill_tiles(chunk, TILE_WALL, 108, 82, 112, 96)
    # Cross-beams (DS3: massive iron beams crossing the corridor)
    fill_tiles(chunk, TILE_WALL, 60, 86, 64, 88)
    fill_tiles(chunk, TILE_WALL, 96, 86, 100, 88)
    fill_tiles(chunk, TILE_WALL, 66, 92, 68, 94)
    fill_tiles(chunk, TILE_WALL, 92, 92, 94, 94)
    # Fallen wall sections creating choke points
    fill_tiles(chunk, TILE_WALL, 58, 78, 66, 82)
    fill_tiles(chunk, TILE_WALL, 94, 78, 102, 82)
    # Twisted metal debris
    fill_tiles(chunk, TILE_WALL, 72, 96, 74, 98)
    fill_tiles(chunk, TILE_WALL, 86, 96, 88, 98)
    fill_tiles(chunk, TILE_WALL, 76, 100, 78, 102)
    fill_tiles(chunk, TILE_WALL, 82, 100, 84, 102)
    # Ash pile against north wall of hall
    fill_tiles(chunk, TILE_WALL, 60, 78, 62, 80)
    fill_tiles(chunk, TILE_WALL, 98, 78, 100, 80)
    # Elevated ash platform (left)
    fill_tiles(chunk, TILE_WALL, 48, 80, 52, 90)
    # Elevated ash platform (right)
    fill_tiles(chunk, TILE_WALL, 108, 80, 112, 90)

    # === 5. SECOND ASH CORRIDOR — narrowing approach to arena ===
    fill_tiles(chunk, TILE_GROUND, 58, 60, 102, 80)
    # Funnel walls — ash dunes pushing player toward arena
    fill_tiles(chunk, TILE_WALL, 50, 62, 60, 78)
    fill_tiles(chunk, TILE_WALL, 100, 62, 110, 78)
    # Girder fragments in corridor
    fill_tiles(chunk, TILE_WALL, 64, 68, 66, 72)
    fill_tiles(chunk, TILE_WALL, 94, 68, 96, 72)
    fill_tiles(chunk, TILE_WALL, 76, 72, 78, 76)
    fill_tiles(chunk, TILE_WALL, 82, 72, 84, 76)
    # Rubble
    fill_tiles(chunk, TILE_WALL, 68, 64, 70, 66)
    fill_tiles(chunk, TILE_WALL, 90, 64, 92, 66)

    # === 6. FIRST FLAME ARENA (north) — circular boss arena ===
    fill_tiles(chunk, TILE_GROUND, 46, 6, 114, 62)
    carve_ellipse(chunk, 80, 34, 28, 22)
    # Arena perimeter — collapsed arches framing the arena
    fill_tiles(chunk, TILE_WALL, 48, 8, 54, 20)
    fill_tiles(chunk, TILE_WALL, 106, 8, 112, 20)
    fill_tiles(chunk, TILE_WALL, 48, 48, 54, 58)
    fill_tiles(chunk, TILE_WALL, 106, 48, 112, 58)
    # Broken pillars around arena edge (DS3: stone column stumps)
    fill_tiles(chunk, TILE_WALL, 56, 14, 58, 18)
    fill_tiles(chunk, TILE_WALL, 102, 14, 104, 18)
    fill_tiles(chunk, TILE_WALL, 52, 36, 54, 40)
    fill_tiles(chunk, TILE_WALL, 106, 36, 108, 40)
    fill_tiles(chunk, TILE_WALL, 56, 48, 58, 52)
    fill_tiles(chunk, TILE_WALL, 102, 48, 104, 52)
    # Ember pit at center edge (DS3: glowing coals at arena center)
    fill_tiles(chunk, TILE_WALL, 78, 30, 82, 36)
    # Ash dunes at arena corners
    fill_tiles(chunk, TILE_WALL, 46, 6, 50, 12)
    fill_tiles(chunk, TILE_WALL, 110, 6, 114, 12)
    fill_tiles(chunk, TILE_WALL, 46, 54, 50, 60)
    fill_tiles(chunk, TILE_WALL, 110, 54, 114, 60)

    # === 7. Connecting corridors between sections ===
    # Entry to ash corridor
    fill_tiles(chunk, TILE_GROUND, 72, 134, 88, 142)
    # Ash corridor to collapsed chamber
    fill_tiles(chunk, TILE_GROUND, 70, 118, 90, 128)
    # Collapsed chamber to girder hall
    fill_tiles(chunk, TILE_GROUND, 66, 102, 94, 108)
    # Girder hall to second corridor
    fill_tiles(chunk, TILE_GROUND, 64, 76, 96, 82)
    # Second corridor to arena
    fill_tiles(chunk, TILE_GROUND, 64, 58, 96, 64)

    # ================================================================
    # SESSION 9 FIDELITY PASS — KilnOfTheFirstFlame architectural details
    # ================================================================
    # Ashen path — ember fragment debris (DS3: scorched earth fragments)
    fill_tiles(chunk, TILE_WALL, 74, 148, 75, 149)
    fill_tiles(chunk, TILE_WALL, 82, 146, 83, 147)
    fill_tiles(chunk, TILE_WALL, 78, 152, 79, 153)
    fill_tiles(chunk, TILE_WALL, 86, 144, 87, 145)
    # First collapsed corridor — iron girder debris (DS3: twisted metal structures)
    fill_tiles(chunk, TILE_WALL, 68, 128, 69, 129)
    fill_tiles(chunk, TILE_WALL, 76, 124, 77, 125)
    fill_tiles(chunk, TILE_WALL, 72, 132, 73, 133)
    fill_tiles(chunk, TILE_WALL, 80, 120, 81, 121)
    fill_tiles(chunk, TILE_WALL, 84, 130, 85, 131)
    # Ash field — scattered coiled sword fragments (DS3: remains of past kilns)
    fill_tiles(chunk, TILE_WALL, 70, 108, 71, 109)
    fill_tiles(chunk, TILE_WALL, 78, 104, 79, 105)
    fill_tiles(chunk, TILE_WALL, 74, 112, 75, 113)
    fill_tiles(chunk, TILE_WALL, 82, 100, 83, 101)
    fill_tiles(chunk, TILE_WALL, 66, 116, 67, 117)
    # Second corridor — burnt stone pillars (DS3: smoldering architecture)
    fill_tiles(chunk, TILE_WALL, 68, 90, 69, 91)
    fill_tiles(chunk, TILE_WALL, 76, 86, 77, 87)
    fill_tiles(chunk, TILE_WALL, 72, 94, 73, 95)
    fill_tiles(chunk, TILE_WALL, 80, 82, 81, 83)
    fill_tiles(chunk, TILE_WALL, 84, 92, 85, 93)
    # Girder hall — twisted iron beams (DS3: industrial hellscape)
    fill_tiles(chunk, TILE_WALL, 66, 76, 67, 77)
    fill_tiles(chunk, TILE_WALL, 74, 78, 75, 79)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    fill_tiles(chunk, TILE_WALL, 70, 80, 71, 81)
    fill_tiles(chunk, TILE_WALL, 78, 72, 79, 73)
    # Soul of Cinder arena — scorched throne remnants (DS3: final arena)
    fill_tiles(chunk, TILE_WALL, 64, 58, 65, 59)
    fill_tiles(chunk, TILE_WALL, 92, 58, 93, 59)
    fill_tiles(chunk, TILE_WALL, 72, 54, 73, 55)
    fill_tiles(chunk, TILE_WALL, 86, 54, 87, 55)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 88, 62, 89, 63)

    # ================================================================
    # SESSION 11 FIDELITY PASS — KilnOfTheFirstFlame fine architectural details
    # ================================================================
    # Flameless Shrine — scorched doorway debris (DS3: burnt entry arch)
    fill_tiles(chunk, TILE_WALL, 66, 150, 67, 151)
    fill_tiles(chunk, TILE_WALL, 90, 150, 91, 151)
    fill_tiles(chunk, TILE_WALL, 70, 154, 71, 155)
    fill_tiles(chunk, TILE_WALL, 86, 154, 87, 155)
    fill_tiles(chunk, TILE_WALL, 74, 142, 75, 143)
    fill_tiles(chunk, TILE_WALL, 84, 142, 85, 143)
    # Ash corridor — slag mound debris (DS3: molten metal slag along path)
    fill_tiles(chunk, TILE_WALL, 58, 124, 59, 125)
    fill_tiles(chunk, TILE_WALL, 100, 124, 101, 125)
    fill_tiles(chunk, TILE_WALL, 62, 126, 63, 127)
    fill_tiles(chunk, TILE_WALL, 96, 126, 97, 127)
    fill_tiles(chunk, TILE_WALL, 70, 130, 71, 131)
    fill_tiles(chunk, TILE_WALL, 88, 130, 89, 131)
    # Collapsed chamber — crumbled arch stones (DS3: massive fallen architecture)
    fill_tiles(chunk, TILE_WALL, 56, 110, 57, 111)
    fill_tiles(chunk, TILE_WALL, 102, 110, 103, 111)
    fill_tiles(chunk, TILE_WALL, 62, 118, 63, 119)
    fill_tiles(chunk, TILE_WALL, 96, 118, 97, 119)
    fill_tiles(chunk, TILE_WALL, 72, 106, 73, 107)
    fill_tiles(chunk, TILE_WALL, 86, 106, 87, 107)
    fill_tiles(chunk, TILE_WALL, 80, 118, 81, 119)
    # Girder hall — twisted rebar fragments (DS3: industrial hellscape with rebar)
    fill_tiles(chunk, TILE_WALL, 54, 84, 55, 85)
    fill_tiles(chunk, TILE_WALL, 106, 84, 107, 85)
    fill_tiles(chunk, TILE_WALL, 58, 88, 59, 89)
    fill_tiles(chunk, TILE_WALL, 100, 88, 101, 89)
    fill_tiles(chunk, TILE_WALL, 64, 96, 65, 97)
    fill_tiles(chunk, TILE_WALL, 94, 96, 95, 97)
    fill_tiles(chunk, TILE_WALL, 68, 102, 69, 103)
    fill_tiles(chunk, TILE_WALL, 90, 102, 91, 103)
    fill_tiles(chunk, TILE_WALL, 74, 90, 75, 91)
    fill_tiles(chunk, TILE_WALL, 84, 90, 85, 91)
    # Second corridor — collapsed ceiling fragments (DS3: debris from above)
    fill_tiles(chunk, TILE_WALL, 54, 66, 55, 67)
    fill_tiles(chunk, TILE_WALL, 104, 66, 105, 67)
    fill_tiles(chunk, TILE_WALL, 60, 70, 61, 71)
    fill_tiles(chunk, TILE_WALL, 98, 70, 99, 71)
    fill_tiles(chunk, TILE_WALL, 72, 74, 73, 75)
    fill_tiles(chunk, TILE_WALL, 86, 74, 87, 75)
    fill_tiles(chunk, TILE_WALL, 78, 66, 79, 67)
    fill_tiles(chunk, TILE_WALL, 80, 78, 81, 79)
    # Arena — scorched stone debris (DS3: final arena with burnt offerings)
    fill_tiles(chunk, TILE_WALL, 50, 10, 51, 12)
    fill_tiles(chunk, TILE_WALL, 108, 10, 109, 12)
    fill_tiles(chunk, TILE_WALL, 52, 42, 53, 44)
    fill_tiles(chunk, TILE_WALL, 106, 42, 107, 44)
    fill_tiles(chunk, TILE_WALL, 58, 22, 59, 24)
    fill_tiles(chunk, TILE_WALL, 100, 22, 101, 24)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 58)
    fill_tiles(chunk, TILE_WALL, 84, 56, 85, 58)
    fill_tiles(chunk, TILE_WALL, 66, 48, 67, 50)
    fill_tiles(chunk, TILE_WALL, 92, 48, 93, 50)


    # ================================================================
    # ENTITIES
    # ================================================================

    # --- Player spawn at Flameless Shrine ---
    spawn_px, spawn_py = 80 * 16, 150 * 16
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py, [make_field("heal", "Bool", True)]))
    entities.append(make_entity("BossSpawn", 97 * 16, 73 * 16, [make_field("name", "String", "Soul of Cinder")]))

    # --- Bonfires ---
    entities.append(make_entity("Bonfire", 38 * 16, 137 * 16))   # Flameless Shrine
    entities.append(make_entity("Bonfire", 97 * 16, 73 * 16))    # Kiln boss bonfire

    # --- Boss ---

    # --- Enemies — DS3 Kiln of the First Flame ---

    
    # --- DS3 faithful enemies (KilnOfTheFirstFlame) ---
    # HollowSoldier (22)
    for tx, ty in [(50, 140), (60, 138), (70, 142), (80, 136), (90, 140), (100, 138), (110, 142), (55, 134), (65, 130), (75, 132), (50, 80), (60, 84), (70, 78), (80, 82), (90, 86), (100, 80), (110, 84), (72, 20), (66, 26), (73, 37), (74, 50), (62, 68)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("HollowSoldier", "HollowSoldier"))]))
    # BlackKnight (10)
    for tx, ty in [(40, 120), (60, 118), (80, 122), (100, 116), (120, 120), (113, 20), (105, 26), (93, 38), (87, 44), (105, 50)]:
        entities.append(make_entity("Enemy", tx * 16, ty * 16,
            [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("BlackKnight", "BlackKnight"))]))
    # MiniBoss (1)
    entities.append(make_entity("Enemy", 80 * 16, 26 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("MiniBoss", "MiniBoss"))]))
    # CrystalLizard (1)
    entities.append(make_entity("Enemy", 120 * 16, 90 * 16,
        [make_field("kind", "LocalEnum.EnemyKind", ENEMY_KIND_MAP.get("CrystalLizard", "CrystalLizard"))]))

# --- NPCs ---
    # Fire Keeper — appears at Kiln for the final scene (DS3: summons Fire Keeper for ending)
    entities.append(make_entity("Npc", 78 * 16, 28 * 16, [
        make_field("name", "String", "Fire Keeper"),
        make_field("kind", "LocalEnum.NpcKind", "Dialogue"),
        make_field("color", "Color", "#E0E0F0"),
        make_field("dialogue", "String",
            "Ashen One, thou hast come to the end|I will remain beside thee|May the fire find thee worthy|Farewell, my Ashen One"),
    ]))

    # --- Items ---
    # DS3 Kiln has no item pickups — only the Soul of Cinder boss fight and endings
    items = []
    for kind, name, tx, ty, val in items:
        fields = [make_field("kind", "LocalEnum.ItemKind", kind),
                  make_field("name", "String", name)]
        if kind == "SoulOrb":
            fields.append(make_field("value", "Int", val))

    
    # --- DS3 faithful items ---
    entities.append(make_entity("Item", 97 * 16, 73 * 16, [
        make_field("kind", "LocalEnum.ItemKind", "BossSoul"),
        make_field("name", "String", "Soul of the Lords")]))
# --- Fog Gate back to Grand Archives (south) ---
    entities.append(make_entity("FogGate", 38 * 16, 143 * 16, [
        make_field("dest_area", "String", "GrandArchives"),
        make_field("dest_x", "Float", 300.0),
        make_field("dest_y", "Float", 2500.0),
        make_field("width", "Float", 48.0),
        make_field("height", "Float", 80.0),
    ]))

    # --- Lights ---
    # --- Lights (DS3 faithful positions from JSON) ---
    entities.append(make_entity("Light", 38 * 16, 137 * 16, [
        make_field("radius", "Float", 160.0),
        make_field("r", "Float", 0.9), make_field("g", "Float", 0.6),
        make_field("b", "Float", 0.3), make_field("intensity", "Float", 0.5)]))
    entities.append(make_entity("Light", 97 * 16, 73 * 16, [
        make_field("radius", "Float", 240.0),
        make_field("r", "Float", 1.0), make_field("g", "Float", 0.85),
        make_field("b", "Float", 0.4), make_field("intensity", "Float", 0.8)]))
    entities.append(make_entity("Light", 87 * 16, 105 * 16, [
        make_field("radius", "Float", 140.0),
        make_field("r", "Float", 0.8), make_field("g", "Float", 0.4),
        make_field("b", "Float", 0.15), make_field("intensity", "Float", 0.3)]))
    # Flickering embers in collapsed chamber

    # === ADDITIONAL INTERNAL STRUCTURES — Kiln DS3 fidelity ===
    # Flameless Shrine — ash dune detail and ruined pillar fragments
    fill_tiles(chunk, TILE_WALL, 70, 148, 72, 150)
    fill_tiles(chunk, TILE_WALL, 88, 148, 90, 150)
    fill_tiles(chunk, TILE_WALL, 74, 142, 75, 144)
    fill_tiles(chunk, TILE_WALL, 85, 142, 86, 144)
    # Ash corridor — additional twisted metal and ash drifts
    fill_tiles(chunk, TILE_WALL, 70, 124, 71, 126)
    fill_tiles(chunk, TILE_WALL, 88, 124, 89, 126)
    fill_tiles(chunk, TILE_WALL, 76, 130, 77, 132)
    fill_tiles(chunk, TILE_WALL, 82, 130, 83, 132)
    # Collapsed chamber — more fallen pillar sections and rubble
    fill_tiles(chunk, TILE_WALL, 64, 112, 66, 114)
    fill_tiles(chunk, TILE_WALL, 94, 112, 96, 114)
    fill_tiles(chunk, TILE_WALL, 74, 108, 76, 110)
    fill_tiles(chunk, TILE_WALL, 84, 108, 86, 110)
    # Girder hall — additional twisted iron beams (DS3: iconic metal forest)
    fill_tiles(chunk, TILE_WALL, 68, 84, 70, 86)
    fill_tiles(chunk, TILE_WALL, 90, 84, 92, 86)
    fill_tiles(chunk, TILE_WALL, 64, 90, 65, 92)
    fill_tiles(chunk, TILE_WALL, 95, 90, 96, 92)
    fill_tiles(chunk, TILE_WALL, 78, 94, 80, 96)
    fill_tiles(chunk, TILE_WALL, 82, 98, 84, 100)
    # Second ash corridor — narrowing rubble (DS3: funnel toward final arena)
    fill_tiles(chunk, TILE_WALL, 72, 66, 73, 68)
    fill_tiles(chunk, TILE_WALL, 88, 66, 89, 68)
    fill_tiles(chunk, TILE_WALL, 78, 74, 79, 76)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 76)
    # First Flame arena — additional broken column stumps and ash piles
    fill_tiles(chunk, TILE_WALL, 60, 24, 62, 26)
    fill_tiles(chunk, TILE_WALL, 98, 24, 100, 26)
    fill_tiles(chunk, TILE_WALL, 68, 42, 70, 44)
    fill_tiles(chunk, TILE_WALL, 90, 42, 92, 44)
    fill_tiles(chunk, TILE_WALL, 74, 18, 76, 20)
    fill_tiles(chunk, TILE_WALL, 84, 18, 86, 20)
    fill_tiles(chunk, TILE_WALL, 64, 52, 66, 54)
    fill_tiles(chunk, TILE_WALL, 94, 52, 96, 54)

    # === SESSION 6 FIDELITY PASS — Kiln of the First Flame ===
    # Flameless Shrine — more ash dune ridges (DS3: desolate ash wasteland)
    fill_tiles(chunk, TILE_WALL, 66, 144, 68, 146)
    fill_tiles(chunk, TILE_WALL, 92, 144, 94, 146)
    fill_tiles(chunk, TILE_WALL, 76, 146, 78, 148)
    fill_tiles(chunk, TILE_WALL, 82, 146, 84, 148)
    fill_tiles(chunk, TILE_WALL, 60, 148, 62, 150)
    fill_tiles(chunk, TILE_WALL, 98, 148, 100, 150)
    # Ash corridor — more twisted metal debris (DS3: collapsed iron structures)
    fill_tiles(chunk, TILE_WALL, 68, 120, 69, 122)
    fill_tiles(chunk, TILE_WALL, 90, 120, 91, 122)
    fill_tiles(chunk, TILE_WALL, 78, 128, 80, 130)
    fill_tiles(chunk, TILE_WALL, 80, 132, 82, 134)
    fill_tiles(chunk, TILE_WALL, 72, 136, 74, 138)
    fill_tiles(chunk, TILE_WALL, 86, 136, 88, 138)
    # Collapsed chamber — more fallen masonry (DS3: ruined cathedral-like hall)
    fill_tiles(chunk, TILE_WALL, 56, 104, 58, 106)
    fill_tiles(chunk, TILE_WALL, 102, 104, 104, 106)
    fill_tiles(chunk, TILE_WALL, 70, 116, 72, 118)
    fill_tiles(chunk, TILE_WALL, 88, 116, 90, 118)
    fill_tiles(chunk, TILE_WALL, 60, 118, 62, 120)
    fill_tiles(chunk, TILE_WALL, 98, 118, 100, 120)
    # Girder hall — more twisted iron forest (DS3: dense collapsed beams)
    fill_tiles(chunk, TILE_WALL, 54, 84, 56, 86)
    fill_tiles(chunk, TILE_WALL, 104, 84, 106, 86)
    fill_tiles(chunk, TILE_WALL, 72, 88, 74, 90)
    fill_tiles(chunk, TILE_WALL, 86, 88, 88, 90)
    fill_tiles(chunk, TILE_WALL, 66, 96, 68, 98)
    fill_tiles(chunk, TILE_WALL, 92, 96, 94, 98)
    fill_tiles(chunk, TILE_WALL, 76, 102, 78, 104)
    fill_tiles(chunk, TILE_WALL, 82, 102, 84, 104)
    # Second corridor — narrowing funnel walls (DS3: claustrophobic approach)
    fill_tiles(chunk, TILE_WALL, 62, 62, 64, 64)
    fill_tiles(chunk, TILE_WALL, 96, 62, 98, 64)
    fill_tiles(chunk, TILE_WALL, 68, 70, 70, 72)
    fill_tiles(chunk, TILE_WALL, 90, 70, 92, 72)
    fill_tiles(chunk, TILE_WALL, 74, 76, 76, 78)
    fill_tiles(chunk, TILE_WALL, 84, 76, 86, 78)
    # First Flame arena — more broken columns (DS3: ancient ruined circular arena)
    fill_tiles(chunk, TILE_WALL, 52, 28, 54, 30)
    fill_tiles(chunk, TILE_WALL, 106, 28, 108, 30)
    fill_tiles(chunk, TILE_WALL, 58, 44, 60, 46)
    fill_tiles(chunk, TILE_WALL, 100, 44, 102, 46)
    fill_tiles(chunk, TILE_WALL, 66, 10, 68, 12)
    fill_tiles(chunk, TILE_WALL, 92, 10, 94, 12)
    fill_tiles(chunk, TILE_WALL, 70, 56, 72, 58)
    fill_tiles(chunk, TILE_WALL, 88, 56, 90, 58)
    fill_tiles(chunk, TILE_WALL, 62, 14, 64, 16)
    fill_tiles(chunk, TILE_WALL, 96, 14, 98, 16)
    # SESSION 10 FIDELITY PASS — Kiln of the First Flame
    # Additional DS3-faithful terrain: ember fragment debris, iron girder remnants,
    # scorched throne stones, ash dune ridges, coiled sword base debris
    # Ash dunes — ridges and debris (DS3: ash-covered landscape)
    fill_tiles(chunk, TILE_WALL, 52, 48, 53, 49)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 53)
    fill_tiles(chunk, TILE_WALL, 64, 50, 65, 51)
    fill_tiles(chunk, TILE_WALL, 70, 54, 71, 55)
    fill_tiles(chunk, TILE_WALL, 76, 48, 77, 49)
    fill_tiles(chunk, TILE_WALL, 82, 52, 83, 53)
    # Iron girder remnants (DS3: twisted metal structures from ruined kiln)
    fill_tiles(chunk, TILE_WALL, 88, 56, 89, 57)
    fill_tiles(chunk, TILE_WALL, 94, 52, 95, 53)
    fill_tiles(chunk, TILE_WALL, 100, 58, 101, 59)
    fill_tiles(chunk, TILE_WALL, 106, 54, 107, 55)
    # Ember fragments — glowing debris (DS3: ember fragments scattered)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    fill_tiles(chunk, TILE_WALL, 68, 62, 69, 63)
    fill_tiles(chunk, TILE_WALL, 80, 60, 81, 61)
    fill_tiles(chunk, TILE_WALL, 92, 64, 93, 65)
    fill_tiles(chunk, TILE_WALL, 104, 62, 105, 63)
    # Scorched throne area — throne debris (DS3: ruined throne at kiln center)
    fill_tiles(chunk, TILE_WALL, 112, 68, 113, 69)
    fill_tiles(chunk, TILE_WALL, 118, 72, 119, 73)
    fill_tiles(chunk, TILE_WALL, 124, 70, 125, 71)
    fill_tiles(chunk, TILE_WALL, 116, 76, 117, 77)
    fill_tiles(chunk, TILE_WALL, 122, 74, 123, 75)
    # Coiled sword base — remnant stones (DS3: coiled sword at kiln center)
    fill_tiles(chunk, TILE_WALL, 128, 78, 129, 79)
    fill_tiles(chunk, TILE_WALL, 134, 82, 135, 83)
    fill_tiles(chunk, TILE_WALL, 130, 86, 131, 87)
    fill_tiles(chunk, TILE_WALL, 136, 80, 137, 81)
    # Path edges — ash ridge stones (DS3: ash ridges along path)
    fill_tiles(chunk, TILE_WALL, 48, 56, 49, 57)
    fill_tiles(chunk, TILE_WALL, 62, 58, 63, 59)
    fill_tiles(chunk, TILE_WALL, 74, 56, 75, 57)
    fill_tiles(chunk, TILE_WALL, 86, 62, 87, 63)
    fill_tiles(chunk, TILE_WALL, 98, 60, 99, 61)

    # ================================================================
    # SESSION 13 FIDELITY PASS — KilnOfTheFirstFlame DS3 architecture
    # ================================================================
    # Ashen entry path — ember deposits (DS3: glowing embers in ash)
    fill_tiles(chunk, TILE_WALL, 78, 148, 79, 149)
    fill_tiles(chunk, TILE_WALL, 82, 146, 83, 147)
    fill_tiles(chunk, TILE_WALL, 76, 144, 77, 145)
    fill_tiles(chunk, TILE_WALL, 84, 150, 85, 151)
    fill_tiles(chunk, TILE_WALL, 80, 142, 81, 143)
    # Flameless Shrine — collapsed shrine walls (DS3: dark ruined shrine)
    fill_tiles(chunk, TILE_WALL, 72, 152, 73, 153)
    fill_tiles(chunk, TILE_WALL, 88, 154, 89, 155)
    fill_tiles(chunk, TILE_WALL, 76, 156, 77, 157)
    fill_tiles(chunk, TILE_WALL, 84, 148, 85, 149)
    fill_tiles(chunk, TILE_WALL, 68, 148, 69, 149)
    # Kiln ascent — molten cinder walls (DS3: path through burning ash)
    fill_tiles(chunk, TILE_WALL, 32, 38, 33, 39)
    fill_tiles(chunk, TILE_WALL, 40, 42, 41, 43)
    fill_tiles(chunk, TILE_WALL, 48, 40, 49, 41)
    fill_tiles(chunk, TILE_WALL, 56, 44, 57, 45)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 43)
    fill_tiles(chunk, TILE_WALL, 72, 46, 73, 47)
    # Soul of Cinder arena — ash drifts (DS3: vast ash arena for final boss)
    fill_tiles(chunk, TILE_WALL, 52, 18, 53, 19)
    fill_tiles(chunk, TILE_WALL, 68, 22, 69, 23)
    fill_tiles(chunk, TILE_WALL, 84, 20, 85, 21)
    fill_tiles(chunk, TILE_WALL, 100, 24, 101, 25)
    fill_tiles(chunk, TILE_WALL, 116, 22, 117, 23)
    fill_tiles(chunk, TILE_WALL, 108, 28, 109, 29)
    fill_tiles(chunk, TILE_WALL, 60, 26, 61, 27)
    fill_tiles(chunk, TILE_WALL, 92, 30, 93, 31)

    # ================================================================
    # SESSION 17 FIDELITY PASS — KilnOfTheFirstFlame DS3 ash wasteland
    # ================================================================
    # Flameless Shrine — collapsing shrine walls (DS3: dark mirror of Firelink in ash)
    fill_tiles(chunk, TILE_WALL, 16, 18, 17, 20)
    fill_tiles(chunk, TILE_WALL, 24, 22, 25, 24)
    fill_tiles(chunk, TILE_WALL, 32, 26, 33, 28)
    fill_tiles(chunk, TILE_WALL, 40, 30, 41, 32)
    fill_tiles(chunk, TILE_WALL, 48, 34, 49, 36)
    # Ashen Wasteland — iron girder debris (DS3: twisted metal structures in ash)
    fill_tiles(chunk, TILE_WALL, 56, 38, 57, 40)
    fill_tiles(chunk, TILE_WALL, 64, 42, 65, 44)
    fill_tiles(chunk, TILE_WALL, 72, 36, 73, 38)
    fill_tiles(chunk, TILE_WALL, 80, 40, 81, 42)
    fill_tiles(chunk, TILE_WALL, 88, 34, 89, 36)
    # First Flame arena — ash mound debris (DS3: ash piles around the bonfire)
    fill_tiles(chunk, TILE_WALL, 44, 14, 45, 16)
    fill_tiles(chunk, TILE_WALL, 56, 16, 57, 18)
    fill_tiles(chunk, TILE_WALL, 76, 12, 77, 14)
    fill_tiles(chunk, TILE_WALL, 96, 18, 97, 20)
    fill_tiles(chunk, TILE_WALL, 112, 14, 113, 16)
    # Collapsed wall sections (DS3: ruined architecture throughout the kiln)
    fill_tiles(chunk, TILE_WALL, 28, 32, 29, 34)
    fill_tiles(chunk, TILE_WALL, 36, 28, 37, 30)
    fill_tiles(chunk, TILE_WALL, 48, 24, 49, 26)
    fill_tiles(chunk, TILE_WALL, 64, 28, 65, 30)
    fill_tiles(chunk, TILE_WALL, 80, 32, 81, 34)

    # ================================================================
    # SESSION 19 FIDELITY PASS — KilnOfTheFirstFlame DS3 ash depth
    # ================================================================
    # Flameless Shrine interior — crumbling stone benches (DS3: dark Firelink mirror)
    fill_tiles(chunk, TILE_WALL, 22, 40, 23, 42)
    fill_tiles(chunk, TILE_WALL, 34, 44, 35, 46)
    fill_tiles(chunk, TILE_WALL, 46, 48, 47, 50)
    fill_tiles(chunk, TILE_WALL, 58, 52, 59, 54)
    fill_tiles(chunk, TILE_WALL, 14, 36, 15, 38)
    # Ashen Wasteland — collapsed roof tiles (DS3: buried structures in deep ash)
    fill_tiles(chunk, TILE_WALL, 68, 48, 69, 50)
    fill_tiles(chunk, TILE_WALL, 84, 52, 85, 54)
    fill_tiles(chunk, TILE_WALL, 100, 48, 101, 50)
    fill_tiles(chunk, TILE_WALL, 116, 52, 117, 54)
    fill_tiles(chunk, TILE_WALL, 132, 48, 133, 50)
    # Soul of Cinder arena — ancient column bases (DS3: vast ruined arena)
    fill_tiles(chunk, TILE_WALL, 40, 8, 41, 10)
    fill_tiles(chunk, TILE_WALL, 64, 10, 65, 12)
    fill_tiles(chunk, TILE_WALL, 88, 8, 89, 10)
    fill_tiles(chunk, TILE_WALL, 108, 12, 109, 14)
    fill_tiles(chunk, TILE_WALL, 128, 10, 129, 12)
    # Ashen corridor — ember crust deposits (DS3: glowing crusts on path)
    fill_tiles(chunk, TILE_WALL, 18, 130, 19, 132)
    fill_tiles(chunk, TILE_WALL, 26, 134, 27, 136)
    fill_tiles(chunk, TILE_WALL, 34, 138, 35, 140)
    fill_tiles(chunk, TILE_WALL, 42, 142, 43, 144)
    fill_tiles(chunk, TILE_WALL, 50, 146, 51, 148)

    # ================================================================
    # SESSION 22 FIDELITY PASS — KilnOfTheFirstFlame DS3 ash ruins details
    # ================================================================
    # Ember debris piles (DS3: smoldering ash and ember piles)
    fill_tiles(chunk, TILE_WALL, 22, 30, 23, 31)
    fill_tiles(chunk, TILE_WALL, 28, 34, 29, 35)
    fill_tiles(chunk, TILE_WALL, 34, 38, 35, 39)
    fill_tiles(chunk, TILE_WALL, 40, 42, 41, 43)
    # Collapsed ruin walls (DS3: ruined walls along the ash path)
    fill_tiles(chunk, TILE_WALL, 46, 46, 47, 47)
    fill_tiles(chunk, TILE_WALL, 52, 50, 53, 51)
    fill_tiles(chunk, TILE_WALL, 58, 54, 59, 55)
    fill_tiles(chunk, TILE_WALL, 64, 58, 65, 59)
    # Black Knight monument (DS3: knight monuments along the path)
    fill_tiles(chunk, TILE_WALL, 70, 62, 71, 63)
    fill_tiles(chunk, TILE_WALL, 76, 66, 77, 67)
    fill_tiles(chunk, TILE_WALL, 82, 70, 83, 71)
    fill_tiles(chunk, TILE_WALL, 88, 74, 89, 75)
    # First Flame crater debris (DS3: scorch marks near the flame)
    fill_tiles(chunk, TILE_WALL, 94, 78, 95, 79)
    fill_tiles(chunk, TILE_WALL, 100, 82, 101, 83)
    fill_tiles(chunk, TILE_WALL, 106, 86, 107, 87)
    fill_tiles(chunk, TILE_WALL, 112, 90, 113, 91)

    # ================================================================
    # SESSION 28 FIDELITY PASS — KilnOfTheFirstFlame DS3 ash ruins details
    # ================================================================
    # Collapsed ruin walls (DS3: destroyed walls along the ash path)
    fill_tiles(chunk, TILE_WALL, 14, 32, 15, 33)
    fill_tiles(chunk, TILE_WALL, 20, 36, 21, 37)
    fill_tiles(chunk, TILE_WALL, 26, 40, 27, 41)
    fill_tiles(chunk, TILE_WALL, 32, 44, 33, 45)
    # Ember pile mounds (DS3: smoldering embers scattered around)
    fill_tiles(chunk, TILE_WALL, 38, 48, 39, 49)
    fill_tiles(chunk, TILE_WALL, 44, 52, 45, 53)
    fill_tiles(chunk, TILE_WALL, 50, 56, 51, 57)
    fill_tiles(chunk, TILE_WALL, 56, 60, 57, 61)
    # Soul of Cinder arena stones (DS3: stones near the First Flame)
    fill_tiles(chunk, TILE_WALL, 62, 64, 63, 65)
    fill_tiles(chunk, TILE_WALL, 68, 68, 69, 69)
    fill_tiles(chunk, TILE_WALL, 74, 72, 75, 73)
    fill_tiles(chunk, TILE_WALL, 80, 76, 81, 77)
    # Bonfire shrine debris (DS3: debris near the Kiln bonfire)
    fill_tiles(chunk, TILE_WALL, 86, 80, 87, 81)
    fill_tiles(chunk, TILE_WALL, 92, 84, 93, 85)
    fill_tiles(chunk, TILE_WALL, 98, 88, 99, 89)
    fill_tiles(chunk, TILE_WALL, 104, 92, 105, 93)

    # ================================================================
    # SESSION 32 FIDELITY PASS — KilnOfTheFirstFlame DS3 ash ruins details
    # ================================================================
    # Collapsed building debris (DS3: ruined buildings along the ash path)
    fill_tiles(chunk, TILE_WALL, 22, 34, 23, 35)
    fill_tiles(chunk, TILE_WALL, 28, 38, 29, 39)
    fill_tiles(chunk, TILE_WALL, 34, 42, 35, 43)
    fill_tiles(chunk, TILE_WALL, 40, 46, 41, 47)
    # Smoldering ember piles (DS3: glowing embers in the ruins)
    fill_tiles(chunk, TILE_WALL, 46, 50, 47, 51)
    fill_tiles(chunk, TILE_WALL, 52, 54, 53, 55)
    fill_tiles(chunk, TILE_WALL, 58, 58, 59, 59)
    fill_tiles(chunk, TILE_WALL, 64, 62, 65, 63)
    # First Flame crater edge (DS3: crater edge near the First Flame)
    fill_tiles(chunk, TILE_WALL, 70, 66, 71, 67)
    fill_tiles(chunk, TILE_WALL, 76, 70, 77, 71)
    fill_tiles(chunk, TILE_WALL, 82, 74, 83, 75)
    fill_tiles(chunk, TILE_WALL, 88, 78, 89, 79)
    # Ash dune debris (DS3: ash dunes throughout the kiln)
    fill_tiles(chunk, TILE_WALL, 94, 82, 95, 83)
    fill_tiles(chunk, TILE_WALL, 100, 86, 101, 87)
    fill_tiles(chunk, TILE_WALL, 106, 90, 107, 91)
    fill_tiles(chunk, TILE_WALL, 112, 94, 113, 95)

    # SESSION 41 FIDELITY PASS — Kiln of the First Flame DS3 details
    # DS3: Ember piles, collapsed architecture, Black Knight monuments, flame crater
    for tx in range(20, 55, 5):
        fill_tiles(chunk, TILE_WALL, tx, 38, tx+1, 39)             # Ember pile markers
        fill_tiles(chunk, TILE_WALL, tx, 78, tx+1, 79)
    for tx in range(60, 95, 5):
        fill_tiles(chunk, TILE_WALL, tx, 42, tx+2, 44)             # Collapsed wall segments
        fill_tiles(chunk, TILE_WALL, tx, 82, tx+2, 84)
    for ty in range(35, 70, 7):
        fill_tiles(chunk, TILE_WALL, 40, ty, 41, ty+1)             # Black Knight monuments
        fill_tiles(chunk, TILE_WALL, 100, ty, 101, ty+1)
    fill_tiles(chunk, TILE_WALL, 55, 55, 57, 57)                    # Flame crater rim
    fill_tiles(chunk, TILE_WALL, 120, 50, 122, 52)                  # Ash pile
    fill_tiles(chunk, TILE_WALL, 75, 90, 77, 92)                    # Collapsed archway
    # --- SESSION 46 terrain (Kiln of the First Flame) ---
    # DS3: Collapsed ceiling debris in the ruined corridors
    for tx in range(20, 30):
        chunk[25][tx] = TILE_WALLTOP  # ceiling rubble
    # Ember glow patches (DS3: coals and embers everywhere)
    for tx, ty in [(40, 30), (50, 35), (60, 28)]:
        chunk[ty][tx] = TILE_WALLTOP  # ember mound
    # Black Knight monument stones (DS3: the path is lined with them)
    for ty in range(40, 48):
        chunk[ty][55] = TILE_WALL  # monument stone
    # Collapsed wall sections
    for tx in range(70, 80):
        chunk[32][tx] = TILE_WALLTOP  # wall debris
    # Ash drifts near the final flame
    for tx in range(85, 95):
        chunk[38][tx] = TILE_WALLTOP  # ash pile

    # --- SESSION 51 terrain (Kiln of the First Flame) ---
    # DS3: Collapsed archways (the ruined Lordran architecture)
    for ty in range(18, 24):
        chunk[ty][45] = TILE_WALL  # broken arch
        chunk[ty][55] = TILE_WALL  # broken arch
    # Ember glow craters (DS3: fire pits dot the landscape)
    for tx, ty in [(30, 28), (48, 32), (65, 30)]:
        chunk[ty][tx] = TILE_WALLTOP  # ember crater
    # Black Knight monument columns (DS3: solemn stone markers)
    for ty in range(35, 42):
        chunk[ty][70] = TILE_WALL  # monument
    # Collapsed staircase (DS3: the ruined stairway to the final boss)
    for ty in range(45, 52):
        chunk[ty][80] = TILE_WALLTOP  # stair debris
    # First Flame altar stones (DS3: the stone ring around the flame)
    for tx in range(85, 92):
        chunk[55][tx] = TILE_WALLTOP  # altar stone

    # --- SESSION 58 terrain (Kiln of the First Flame) ---
    # DS3: Lord of Cinder thrones (DS3: the thrones of the Lords of Cinder)
    for tx in range(30, 36):
        chunk[60][tx] = TILE_WALLTOP  # throne base
    for tx in range(50, 56):
        chunk[62][tx] = TILE_WALLTOP  # throne base
    # Firelink Shrine ruins (DS3: the ruined shrine in the Kiln)
    for ty in range(40, 46):
        chunk[ty][35] = TILE_WALL  # shrine wall
    # Collapsed Lordran archway
    for ty in range(28, 34):
        chunk[ty][65] = TILE_WALL  # archway pillar

    # --- SESSION 89 DS3 terrain (Kiln of the First Flame detail pass) ---
    # DS3: Ceiling rubble (collapsed stone blocks)
    for tx in [15, 25, 35, 45, 55, 65, 75, 85]:
        for ty in [8, 9]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][7] = TILE_WALLTOP
    # DS3: Ember mounds (glowing ash piles)
    for tx in range(20, 35):
        for ty in range(25, 32):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(50, 65):
        for ty in range(35, 42):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Monument stones (ancient pillars)
    for tx in [30, 45, 60, 75]:
        for ty in range(15, 25):
            chunk[tx][ty] = TILE_WALL
            chunk[tx][ty-1] = TILE_WALLTOP
    # DS3: Wall debris along the path
    for tx in [18, 22, 28, 32, 38, 42, 48, 52, 58, 62, 68, 72]:
        for ty in [18, 19]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Ash drifts (soft ground patches)
    for tx in range(30, 50):
        for ty in range(40, 50):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(60, 80):
        for ty in range(28, 38):
            chunk[tx][ty] = TILE_GROUND
    # DS3: Final boss arena (open circular chamber)
    for tx in range(40, 70):
        for ty in range(50, 70):
            chunk[tx][ty] = TILE_GROUND
    for tx in [40, 70]:
        for ty in range(50, 71):
            chunk[tx][ty] = TILE_WALL
    for tx in range(40, 71):
        for ty in [50, 70]:
            chunk[tx][ty] = TILE_WALL

    # --- SESSION 93 DS3 terrain round 2 (Kiln of the First Flame) ---
    # DS3: Collapsed archways along the path
    for tx in [20, 30, 40, 50, 60, 70]:
        for ty in [10, 11, 12]:
            chunk[tx][ty] = TILE_WALL
        chunk[tx][9] = TILE_WALLTOP
    # DS3: Ember glows on the ground (bright patches)
    for tx in range(25, 35):
        for ty in range(30, 38):
            chunk[tx][ty] = TILE_GROUND
    for tx in range(55, 65):
        for ty in range(40, 48):
            chunk[tx][ty] = TILE_GROUND
    # DS3: SoC arena debris (scattered stone blocks)
    for tx in [45, 50, 55, 60]:
        for ty in [55, 56]:
            chunk[tx][ty] = TILE_WALL
    # DS3: Ash drifts along the path edges
    for tx in range(15, 80):
        for ty in [20, 21]:
            chunk[tx][ty] = TILE_GROUND
    # DS3: Firelink Shrine door at the end
    for tx in range(40, 48):
        for ty in [58, 59]:
            chunk[tx][ty] = TILE_WALL
    for tx in [40, 48]:
        for ty in range(55, 60):
            chunk[tx][ty] = TILE_WALL
    # DS3: Soul of Cinder arena (final boss chamber)
    for tx in range(42, 68):
        for ty in range(60, 78):
            chunk[tx][ty] = TILE_GROUND
    for tx in [42, 68]:
        for ty in range(60, 79):
            chunk[tx][ty] = TILE_WALL
    for tx in range(42, 69):
        for ty in [60, 78]:
            chunk[tx][ty] = TILE_WALL
    # Fill terrain from JSON doc sections for areas beyond hardcoded layout

    import json as _json

    with open("docs/maps/KilnOfTheFirstFlame.json") as _f:

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
    ground_count = sum(1 for y in range(len(chunk)) for x in range(len(chunk[0]))
                       if chunk[y][x] in (TILE_GROUND, TILE_POISON))
    pct = ground_count / (len(chunk) * len(chunk[0])) * 100
    # print(f"  KilnOfTheFirstFlame (faithful DS3 layout) "
    # f"ground={pct:.1f}% connectivity={coverage}%")
    return "KilnOfTheFirstFlame", chunk, entities
