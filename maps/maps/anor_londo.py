from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_anor_londo():
    """Anor Londo -- DS3-faithful terrain.

    Dark cathedral reached via Irithyll's rotating staircase.
    Route: rotating platform -> grand staircase -> silver knight battlements ->
    cathedral antechamber -> Gwyndolin hallway -> Aldrich depths -> Aldrich arena.
    Side path: prison tower (invisible bridge) -> Yorshka's Darkmoon chamber.
    Painting Guardian room off the main hall.

    JSON doc is authoritative for entity positions.
    """
    # 5120 / 16 = 320 tiles wide, 4096 / 16 = 256 tiles tall
    chunk = new_chunk(320, 256)

    # ================================================================
    # 1. ROTATING TOWER PLATFORM (entrance from Irithyll)
    # DS3: the iconic rotating staircase mechanism from DS1, now
    # leading into the darkened Anor Londo. Stone platform with
    # massive gear mechanism and surrounding pillars.
    # JSON section: x=720,y=620,w=700,h=520 -> tiles (45,38)-(88,70)
    # ================================================================
    # Platform perimeter walls (DS3: cathedral entrance chamber)
    fill_tiles(chunk, TILE_WALL, 45, 38, 48, 55)    # NW wall
    fill_tiles(chunk, TILE_WALL, 83, 38, 88, 55)    # NE wall
    fill_tiles(chunk, TILE_WALL, 45, 65, 48, 70)    # SW wall
    fill_tiles(chunk, TILE_WALL, 83, 65, 88, 70)    # SE wall
    fill_tiles(chunk, TILE_WALL, 45, 38, 65, 40)    # North wall left
    fill_tiles(chunk, TILE_WALL, 72, 38, 88, 40)    # North wall right
    # Rotating mechanism pillar (DS3: central gear column)
    fill_tiles(chunk, TILE_WALL, 63, 48, 67, 54)    # Central gear pillar
    # Entrance archway walls (DS3: arched cathedral doorway)
    fill_tiles(chunk, TILE_WALL, 55, 42, 57, 46)    # Left arch pillar
    fill_tiles(chunk, TILE_WALL, 73, 42, 75, 46)    # Right arch pillar

    # ================================================================
    # 2. ANOR LONDO GRAND STAIRCASE
    # DS3: the famous grand staircase from DS1, now dark and corrupted.
    # Wide stone steps flanked by knight statues, golden railings (tarnished).
    # JSON section: x=1180,y=840,w=820,h=680 -> tiles (73,52)-(124,94)
    # ================================================================
    # Staircase perimeter walls (DS3: cathedral walls flanking the steps)
    fill_tiles(chunk, TILE_WALL, 73, 52, 76, 65)    # NW wall
    fill_tiles(chunk, TILE_WALL, 120, 52, 124, 65)  # NE wall
    fill_tiles(chunk, TILE_WALL, 73, 88, 76, 94)    # SW wall
    fill_tiles(chunk, TILE_WALL, 120, 88, 124, 94)  # SE wall
    fill_tiles(chunk, TILE_WALL, 73, 52, 95, 54)    # North wall left
    fill_tiles(chunk, TILE_WALL, 105, 52, 124, 54)  # North wall right
    # Knight statue bases (DS3: statues line the grand staircase)
    fill_tiles(chunk, TILE_WALL, 79, 58, 81, 61)    # Left statue base 1
    fill_tiles(chunk, TILE_WALL, 79, 70, 81, 73)    # Left statue base 2
    fill_tiles(chunk, TILE_WALL, 79, 82, 81, 85)    # Left statue base 3
    fill_tiles(chunk, TILE_WALL, 116, 58, 118, 61)  # Right statue base 1
    fill_tiles(chunk, TILE_WALL, 116, 70, 118, 73)  # Right statue base 2
    fill_tiles(chunk, TILE_WALL, 116, 82, 118, 85)  # Right statue base 3
    # Grand railing pillars (DS3: golden railings now tarnished dark)
    fill_tiles(chunk, TILE_WALL, 90, 56, 92, 60)    # Railing pillar NW
    fill_tiles(chunk, TILE_WALL, 105, 56, 107, 60)  # Railing pillar NE

    # ================================================================
    # 3. PRISON TOWER (Yorshka's Darkmoon chamber)
    # DS3: reached via invisible bridge from the main hall. Contains
    # Company Captain Yorshka who leads the Darkmoon Blades.
    # Narrow tower with drop platforms and invisible bridge.
    # JSON section: x=300,y=1300,w=620,h=560 -> tiles (18,81)-(56,115)
    # ================================================================
    # Tower perimeter walls (DS3: narrow tower prison)
    fill_tiles(chunk, TILE_WALL, 18, 81, 21, 95)    # NW tower wall
    fill_tiles(chunk, TILE_WALL, 52, 81, 56, 95)    # NE tower wall
    fill_tiles(chunk, TILE_WALL, 18, 110, 21, 115)  # SW tower wall
    fill_tiles(chunk, TILE_WALL, 52, 110, 56, 115)  # SE tower wall
    fill_tiles(chunk, TILE_WALL, 18, 81, 35, 83)    # North wall left
    fill_tiles(chunk, TILE_WALL, 42, 81, 56, 83)    # North wall right
    # Tower interior: invisible bridge support pillars (DS3: beam structure)
    fill_tiles(chunk, TILE_WALL, 28, 88, 30, 92)    # Left beam support
    fill_tiles(chunk, TILE_WALL, 44, 88, 46, 92)    # Right beam support
    # Drop platforms (DS3: platforms you drop down to reach Yorshka)
    fill_tiles(chunk, TILE_WALL, 33, 100, 35, 103)  # Drop platform 1
    fill_tiles(chunk, TILE_WALL, 38, 106, 40, 109)  # Drop platform 2
    # Altar stones (DS3: Darkmoon altar in Yorshka's chamber)
    fill_tiles(chunk, TILE_WALL, 34, 112, 38, 114)  # Altar base

    # ================================================================
    # 4. PAINTING GUARDIAN ROOM
    # DS3: wooden-floored room containing the painted world painting.
    # Painting Guardians with curved swords patrol this area.
    # JSON section: x=1300,y=1100,w=600,h=400 -> tiles (81,68)-(118,92)
    # ================================================================
    # Room perimeter walls (DS3: wooden panel walls around painting)
    fill_tiles(chunk, TILE_WALL, 81, 68, 84, 80)    # NW wall
    fill_tiles(chunk, TILE_WALL, 114, 68, 118, 80)  # NE wall
    fill_tiles(chunk, TILE_WALL, 81, 88, 84, 92)    # SW wall
    fill_tiles(chunk, TILE_WALL, 114, 88, 118, 92)  # SE wall
    fill_tiles(chunk, TILE_WALL, 81, 68, 95, 70)    # North wall left
    fill_tiles(chunk, TILE_WALL, 104, 68, 118, 70)  # North wall right
    # Large painting frame (DS3: the painted world of Ariamis/Ariandel)
    fill_tiles(chunk, TILE_WALL, 93, 72, 96, 84)    # Painting frame left
    fill_tiles(chunk, TILE_WALL, 103, 72, 106, 84)  # Painting frame right
    fill_tiles(chunk, TILE_WALL, 93, 72, 106, 74)   # Painting frame top
    # Wooden floor support beams (DS3: wooden floor joists)
    fill_tiles(chunk, TILE_WALL, 86, 78, 88, 80)    # Floor beam 1
    fill_tiles(chunk, TILE_WALL, 110, 84, 112, 86)  # Floor beam 2

    # ================================================================
    # 5. SILVER KNIGHT ARCHER BATTLEMENTS
    # DS3: narrow walkway along castle battlements where Silver Knights
    # fire their greatbows with dragon arrows. Ledge path with high walls.
    # JSON section: x=1600,y=700,w=700,h=500 -> tiles (100,43)-(143,74)
    # ================================================================
    # Battlement perimeter walls (DS3: castle exterior walls)
    fill_tiles(chunk, TILE_WALL, 100, 43, 103, 55)  # NW wall
    fill_tiles(chunk, TILE_WALL, 139, 43, 143, 55)  # NE wall
    fill_tiles(chunk, TILE_WALL, 100, 68, 103, 74)  # SW wall
    fill_tiles(chunk, TILE_WALL, 139, 68, 143, 74)  # SE wall
    fill_tiles(chunk, TILE_WALL, 100, 43, 118, 45)  # North wall left
    fill_tiles(chunk, TILE_WALL, 126, 43, 143, 45)  # North wall right
    # Battlement merlons (DS3: crenellated castle walls)
    fill_tiles(chunk, TILE_WALL, 106, 46, 108, 48)  # Merlon 1
    fill_tiles(chunk, TILE_WALL, 114, 46, 116, 48)  # Merlon 2
    fill_tiles(chunk, TILE_WALL, 126, 46, 128, 48)  # Merlon 3
    fill_tiles(chunk, TILE_WALL, 134, 46, 136, 48)  # Merlon 4
    # Silver Knight arrow slit pillars (DS3: positions where knights stand)
    fill_tiles(chunk, TILE_WALL, 110, 55, 112, 60)  # Knight post 1
    fill_tiles(chunk, TILE_WALL, 130, 55, 132, 60)  # Knight post 2
    # Narrow ledge wall (DS3: the famous narrow ledge)
    fill_tiles(chunk, TILE_WALL, 118, 62, 122, 66)  # Ledge obstacle

    # ================================================================
    # 6. CATHEDRAL ANTECHAMBER
    # DS3: grand hall with massive stone pillars, Silver Knight patrols,
    # and Deacon/pyromancer enemies. Stone floor with hall pillars.
    # JSON section: x=1880,y=1320,w=780,h=520 -> tiles (117,82)-(165,113)
    # ================================================================
    # Antechamber perimeter walls (DS3: grand cathedral interior)
    fill_tiles(chunk, TILE_WALL, 117, 82, 120, 95)  # NW wall
    fill_tiles(chunk, TILE_WALL, 161, 82, 165, 95)  # NE wall
    fill_tiles(chunk, TILE_WALL, 117, 108, 120, 113) # SW wall
    fill_tiles(chunk, TILE_WALL, 161, 108, 165, 113) # SE wall
    fill_tiles(chunk, TILE_WALL, 117, 82, 135, 84)   # North wall left
    fill_tiles(chunk, TILE_WALL, 148, 82, 165, 84)   # North wall right
    # Massive cathedral pillars (DS3: grand hall with 2 rows of columns)
    fill_tiles(chunk, TILE_WALL, 126, 88, 129, 94)  # Pillar row 1, left
    fill_tiles(chunk, TILE_WALL, 138, 88, 141, 94)  # Pillar row 1, center
    fill_tiles(chunk, TILE_WALL, 150, 88, 153, 94)  # Pillar row 1, right
    fill_tiles(chunk, TILE_WALL, 126, 100, 129, 106) # Pillar row 2, left
    fill_tiles(chunk, TILE_WALL, 138, 100, 141, 106) # Pillar row 2, center
    fill_tiles(chunk, TILE_WALL, 150, 100, 153, 106) # Pillar row 2, right
    # Hall divider arch (DS3: stone arch dividing the antechamber)
    fill_tiles(chunk, TILE_WALL, 132, 95, 134, 98)   # Divider left pillar
    fill_tiles(chunk, TILE_WALL, 146, 95, 148, 98)   # Divider right pillar

    # ================================================================
    # 7. GWYNDOLIN HALLWAY
    # DS3: dark narrow corridor leading to Aldrich's domain. Stone
    # railings, narrow passage with dark atmosphere. Where Gwyndolin's
    # illusion once maintained the golden Anor Londo.
    # JSON section: x=2220,y=1680,w=820,h=480 -> tiles (138,105)-(189,134)
    # ================================================================
    # Hallway perimeter walls (DS3: narrow dark corridor)
    fill_tiles(chunk, TILE_WALL, 138, 105, 141, 115) # NW wall
    fill_tiles(chunk, TILE_WALL, 185, 105, 189, 115) # NE wall
    fill_tiles(chunk, TILE_WALL, 138, 130, 141, 134) # SW wall
    fill_tiles(chunk, TILE_WALL, 185, 130, 189, 134) # SE wall
    fill_tiles(chunk, TILE_WALL, 138, 105, 160, 107) # North wall left
    fill_tiles(chunk, TILE_WALL, 168, 105, 189, 107) # North wall right
    # Stone railing pillars (DS3: railings along the dark passage)
    fill_tiles(chunk, TILE_WALL, 148, 110, 150, 114) # Railing post 1
    fill_tiles(chunk, TILE_WALL, 160, 110, 162, 114) # Railing post 2
    fill_tiles(chunk, TILE_WALL, 172, 110, 174, 114) # Railing post 3
    fill_tiles(chunk, TILE_WALL, 148, 120, 150, 124) # Railing post 4
    fill_tiles(chunk, TILE_WALL, 160, 120, 162, 124) # Railing post 5
    fill_tiles(chunk, TILE_WALL, 172, 120, 174, 124) # Railing post 6
    # Dark alcove (DS3: side chamber in the hallway)
    fill_tiles(chunk, TILE_WALL, 180, 116, 183, 122) # Dark alcove wall

    # ================================================================
    # 8. ALDRICH DEPTHS
    # DS3: deep water and sludge floor area. Collapsed flooring with
    # Rotten Flesh of Aldrich enemies. Corrupted cathedral undercroft.
    # JSON section: x=2480,y=1500,w=800,h=400 -> tiles (155,93)-(204,117)
    # ================================================================
    # Depths perimeter walls (DS3: flooded cathedral undercroft)
    fill_tiles(chunk, TILE_WALL, 155, 93, 158, 103)  # NW wall
    fill_tiles(chunk, TILE_WALL, 200, 93, 204, 103)  # NE wall
    fill_tiles(chunk, TILE_WALL, 155, 113, 158, 117) # SW wall
    fill_tiles(chunk, TILE_WALL, 200, 113, 204, 117) # SE wall
    fill_tiles(chunk, TILE_WALL, 155, 93, 175, 95)   # North wall left
    fill_tiles(chunk, TILE_WALL, 185, 93, 204, 95)   # North wall right
    # Collapsed floor sections (DS3: broken flooring over deep water)
    fill_tiles(chunk, TILE_WALL, 165, 100, 168, 103) # Collapsed section 1
    fill_tiles(chunk, TILE_WALL, 180, 100, 183, 103) # Collapsed section 2
    fill_tiles(chunk, TILE_WALL, 192, 100, 195, 103) # Collapsed section 3
    # Sludge pool pillars (DS3: half-sunken columns in the muck)
    fill_tiles(chunk, TILE_WALL, 170, 108, 172, 112) # Sunken pillar 1
    fill_tiles(chunk, TILE_WALL, 188, 108, 190, 112) # Sunken pillar 2

    # ================================================================
    # 9. ALDRICH ARENA (boss room)
    # DS3: massive dark cathedral floor where Aldrich, Devourer of Gods
    # resides. Cathedral columns, debris, stone pillars. Gwyndolin's
    # throne room corrupted by the Abyss. Post-boss: Sun Princess Ring
    # in Gwynevere's chamber.
    # JSON section: x=2480,y=1940,w=760,h=620 -> tiles (155,121)-(202,159)
    # ================================================================
    # Arena perimeter walls (DS3: grand cathedral boss chamber)
    fill_tiles(chunk, TILE_WALL, 155, 121, 158, 135) # NW wall
    fill_tiles(chunk, TILE_WALL, 198, 121, 202, 135) # NE wall
    fill_tiles(chunk, TILE_WALL, 155, 155, 158, 159) # SW wall
    fill_tiles(chunk, TILE_WALL, 198, 155, 202, 159) # SE wall
    fill_tiles(chunk, TILE_WALL, 155, 121, 175, 123) # North wall left
    fill_tiles(chunk, TILE_WALL, 182, 121, 202, 123) # North wall right
    # Massive cathedral columns (DS3: 4 great columns in the arena)
    fill_tiles(chunk, TILE_WALL, 165, 130, 169, 137) # Column NW
    fill_tiles(chunk, TILE_WALL, 188, 130, 192, 137) # Column NE
    fill_tiles(chunk, TILE_WALL, 165, 145, 169, 152) # Column SW
    fill_tiles(chunk, TILE_WALL, 188, 145, 192, 152) # Column SE
    # Gwyndolin's throne debris (DS3: throne at far end, Aldrich emerges)
    fill_tiles(chunk, TILE_WALL, 175, 124, 181, 128) # Throne structure
    # Cathedral debris (DS3: scattered rubble from Aldrich's presence)
    fill_tiles(chunk, TILE_WALL, 160, 140, 163, 143) # Debris NW
    fill_tiles(chunk, TILE_WALL, 194, 140, 197, 143) # Debris NE

    # ================================================================
    # CONNECTION CORRIDORS -- DS3 route paths between sections
    # ================================================================
    # Rotating Tower -> Grand Staircase (east)
    fill_tiles(chunk, TILE_GROUND, 85, 50, 75, 62)
    # Grand Staircase -> Silver Knight Battlements (north-east)
    fill_tiles(chunk, TILE_GROUND, 100, 50, 110, 65)
    # Grand Staircase -> Painting Guardian Room (south)
    fill_tiles(chunk, TILE_GROUND, 90, 85, 95, 72)
    # Silver Knight Battlements -> Cathedral Antechamber (south-east)
    fill_tiles(chunk, TILE_GROUND, 130, 70, 140, 85)
    # Cathedral Antechamber -> Gwyndolin Hallway (south-east)
    fill_tiles(chunk, TILE_GROUND, 150, 100, 160, 110)
    # Gwyndolin Hallway -> Aldrich Depths (north-east)
    fill_tiles(chunk, TILE_GROUND, 160, 105, 170, 100)
    # Gwyndolin Hallway -> Aldrich Arena (south-east)
    fill_tiles(chunk, TILE_GROUND, 160, 130, 165, 125)
    # Grand Staircase -> Prison Tower (south-west, invisible bridge)
    fill_tiles(chunk, TILE_GROUND, 75, 80, 55, 95)
    # Aldrich Depths -> Aldrich Arena (south)
    fill_tiles(chunk, TILE_GROUND, 165, 112, 175, 125)

    # ================================================================
    # FINALIZE
    # ================================================================
    spawn_px, spawn_py = 980, 900  # Anor Londo bonfire (JSON doc first bonfire)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("AnorLondo"))

    return finalize_map("AnorLondo", chunk, entities, spawn_px, spawn_py)
