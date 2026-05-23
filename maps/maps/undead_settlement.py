from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, make_entity, make_field,
    apply_doc_terrain, finalize_map, load_doc,
)



def make_undead_settlement():
    """Undead Settlement — DS3-faithful terrain.

    Creates real DS3 structures: portcullis entry, narrow village streets between
    wooden houses, multi-story building shortcut, blazing tree square, circular
    Giant Tower with lift, Fire Demon plaza, broken Dilapidated Bridge over
    graveyard, underground sewers, Irina's locked cell, and Greatwood boss arena.

    JSON doc is authoritative for entity positions; apply_doc_terrain() fills
    section interiors and carves corridors between them.
    """
    chunk = new_chunk(320, 256)

    # ================================================================
    # 1. FOOT OF THE HIGH WALL — entry from Lothric Wall
    # DS3: walled courtyard, portcullis gate, 3 hounds, pilgrims
    # Section: x=200,y=180 → tiles (12,11)-(59,37)
    # ================================================================
    fill_tiles(chunk, TILE_WALL, 12, 11, 14, 37)     # West wall
    fill_tiles(chunk, TILE_WALL, 55, 11, 59, 37)     # East wall
    fill_tiles(chunk, TILE_WALL, 12, 11, 59, 13)     # North wall
    # Portcullis gate pillars (DS3: iron gate, hounds released)
    fill_tiles(chunk, TILE_WALL, 24, 14, 26, 20)
    fill_tiles(chunk, TILE_WALL, 42, 14, 44, 20)
    # Graveyard tombstones
    fill_tiles(chunk, TILE_WALL, 30, 16, 31, 17)
    fill_tiles(chunk, TILE_WALL, 36, 20, 37, 21)
    fill_tiles(chunk, TILE_WALL, 32, 25, 33, 26)
    fill_tiles(chunk, TILE_WALL, 48, 18, 49, 19)
    fill_tiles(chunk, TILE_WALL, 44, 30, 45, 31)
    # Overturned cart (DS3: cart near hounds)
    fill_tiles(chunk, TILE_WALL, 38, 28, 41, 30)
    # Pilgrim stones (DS3: Yoel among pilgrims)
    fill_tiles(chunk, TILE_WALL, 16, 32, 17, 34)
    fill_tiles(chunk, TILE_WALL, 22, 34, 23, 35)

    # ================================================================
    # 2. SETTLEMENT ENTRY STREET — winding path through village
    # DS3: narrow street, wooden houses both sides, hanging corpses
    # Section: x=760,y=700 → tiles (47,43)-(94,79)
    # ================================================================
    # House walls lining street (DS3: densely packed wooden houses)
    fill_tiles(chunk, TILE_WALL, 47, 43, 49, 52)
    fill_tiles(chunk, TILE_WALL, 47, 58, 49, 65)
    fill_tiles(chunk, TILE_WALL, 90, 43, 94, 52)
    fill_tiles(chunk, TILE_WALL, 90, 58, 94, 65)
    # Interior rooms (DS3: multi-room dwellings)
    fill_tiles(chunk, TILE_WALL, 55, 46, 60, 48)
    fill_tiles(chunk, TILE_WALL, 65, 50, 70, 52)
    fill_tiles(chunk, TILE_WALL, 75, 46, 80, 48)
    fill_tiles(chunk, TILE_WALL, 58, 56, 63, 58)
    fill_tiles(chunk, TILE_WALL, 72, 60, 77, 62)
    fill_tiles(chunk, TILE_WALL, 82, 56, 87, 58)
    # Hanging corpse frames (DS3: bodies hang from wooden frames)
    fill_tiles(chunk, TILE_WALL, 52, 54, 53, 55)
    fill_tiles(chunk, TILE_WALL, 85, 54, 86, 55)
    # Bonfire room walls (DS3: small room inside house)
    fill_tiles(chunk, TILE_WALL, 52, 68, 54, 72)
    fill_tiles(chunk, TILE_WALL, 62, 70, 64, 74)
    fill_tiles(chunk, TILE_WALL, 74, 68, 76, 72)

    # ================================================================
    # 3. HOUSE SHORTCUT — multi-story building
    # DS3: ramshackle house, thrall ambush, Small Leather Shield
    # Section: x=1380,y=960 → tiles (86,60)-(137,98)
    # ================================================================
    # Building exterior (DS3: large multi-story dwelling)
    fill_tiles(chunk, TILE_WALL, 86, 60, 88, 78)
    fill_tiles(chunk, TILE_WALL, 134, 60, 137, 78)
    fill_tiles(chunk, TILE_WALL, 86, 60, 120, 62)
    fill_tiles(chunk, TILE_WALL, 128, 60, 137, 62)
    fill_tiles(chunk, TILE_WALL, 86, 93, 110, 96)
    fill_tiles(chunk, TILE_WALL, 118, 93, 137, 96)
    # Interior partitions (DS3: rooms inside house)
    fill_tiles(chunk, TILE_WALL, 100, 62, 102, 75)
    fill_tiles(chunk, TILE_WALL, 118, 62, 120, 75)
    fill_tiles(chunk, TILE_WALL, 108, 78, 114, 80)
    # Thrall ambush beams (DS3: drop from ceiling)
    fill_tiles(chunk, TILE_WALL, 92, 64, 93, 65)
    fill_tiles(chunk, TILE_WALL, 108, 66, 109, 67)
    fill_tiles(chunk, TILE_WALL, 126, 64, 127, 65)
    # Rooftop walkway (DS3: path to Cornyx cage)
    fill_tiles(chunk, TILE_GROUND, 90, 58, 135, 60)

    # ================================================================
    # 4. BURNING TREE SQUARE — open area with blazing tree
    # DS3: Evangelist praying, massive fire, Estus Shard
    # Section: x=1980,y=1180 → tiles (123,73)-(170,108)
    # ================================================================
    # Perimeter buildings (DS3: houses surround square)
    fill_tiles(chunk, TILE_WALL, 123, 73, 130, 76)
    fill_tiles(chunk, TILE_WALL, 140, 73, 148, 76)
    fill_tiles(chunk, TILE_WALL, 160, 73, 170, 76)
    fill_tiles(chunk, TILE_WALL, 123, 105, 132, 108)
    fill_tiles(chunk, TILE_WALL, 160, 105, 170, 108)
    fill_tiles(chunk, TILE_WALL, 123, 88, 126, 95)
    fill_tiles(chunk, TILE_WALL, 166, 88, 170, 95)
    # Blazing tree trunk (DS3: massive burning tree)
    fill_tiles(chunk, TILE_WALL, 143, 87, 149, 93)
    # Market stalls (DS3: wooden stalls)
    fill_tiles(chunk, TILE_WALL, 132, 80, 134, 82)
    fill_tiles(chunk, TILE_WALL, 156, 80, 158, 82)
    fill_tiles(chunk, TILE_WALL, 132, 98, 134, 100)
    fill_tiles(chunk, TILE_WALL, 156, 98, 158, 100)

    # ================================================================
    # 5. TREE-SHADED PATH — connector with dead trees
    # DS3: short path with dead trees
    # Section: x=2160,y=688 → tiles (135,43)-(151,59)
    # ================================================================
    fill_tiles(chunk, TILE_WALL, 136, 45, 138, 48)
    fill_tiles(chunk, TILE_WALL, 145, 50, 147, 53)
    fill_tiles(chunk, TILE_WALL, 140, 54, 142, 57)

    # ================================================================
    # 6. GIANT TOWER — circular stone tower
    # DS3: Giant Slave at top with greatbow, Hawk Ring, lift down
    # Section: x=2920,y=820 → tiles (182,51)-(221,107)
    # ================================================================
    # Tower walls (DS3: circular stone tower, approximated)
    fill_tiles(chunk, TILE_WALL, 186, 55, 188, 100)
    fill_tiles(chunk, TILE_WALL, 215, 55, 217, 100)
    fill_tiles(chunk, TILE_WALL, 186, 55, 200, 57)
    fill_tiles(chunk, TILE_WALL, 208, 55, 217, 57)
    fill_tiles(chunk, TILE_WALL, 186, 98, 200, 100)
    fill_tiles(chunk, TILE_WALL, 208, 98, 217, 100)
    # Giant platform (DS3: Giant at top of tower)
    fill_tiles(chunk, TILE_WALL, 194, 58, 196, 62)
    fill_tiles(chunk, TILE_WALL, 210, 58, 212, 62)
    # Interior walls (DS3: ladder and lift)
    fill_tiles(chunk, TILE_WALL, 198, 62, 200, 80)
    fill_tiles(chunk, TILE_WALL, 206, 62, 208, 80)
    # Lift shaft (DS3: elevator down to Fire Demon area)
    fill_tiles(chunk, TILE_WALL, 200, 90, 202, 107)
    fill_tiles(chunk, TILE_WALL, 212, 90, 214, 107)
    fill_tiles(chunk, TILE_GROUND, 202, 95, 212, 107)

    # ================================================================
    # 7. FIRE DEMON PLAZA — Siegward encounter
    # DS3: open plaza, Fire Demon + Siegward
    # Section: x=3420,y=1420 → tiles (213,88)-(258,121)
    # ================================================================
    # Plaza perimeter ruins
    fill_tiles(chunk, TILE_WALL, 213, 88, 218, 92)
    fill_tiles(chunk, TILE_WALL, 250, 88, 258, 92)
    fill_tiles(chunk, TILE_WALL, 213, 117, 218, 121)
    fill_tiles(chunk, TILE_WALL, 250, 117, 258, 121)
    # Burnt buildings (DS3: structures destroyed by demon)
    fill_tiles(chunk, TILE_WALL, 220, 94, 226, 98)
    fill_tiles(chunk, TILE_WALL, 244, 94, 250, 98)
    fill_tiles(chunk, TILE_WALL, 232, 112, 240, 116)
    # Siegward's cooking spot
    fill_tiles(chunk, TILE_WALL, 228, 104, 230, 108)
    # Tower drop path (DS3: Chloranthy Ring drop)
    fill_tiles(chunk, TILE_GROUND, 255, 115, 270, 130)

    # ================================================================
    # 8. DILAPIDATED BRIDGE GRAVEYARD — broken bridge over graves
    # DS3: wooden bridge, graveyard, sewer entrance, Hodrick invasion
    # Section: x=2300,y=1640 → tiles (143,102)-(212,146)
    # ================================================================
    # Bridge pillars (DS3: broken wooden bridge)
    fill_tiles(chunk, TILE_WALL, 150, 104, 152, 108)
    fill_tiles(chunk, TILE_WALL, 170, 104, 172, 108)
    fill_tiles(chunk, TILE_WALL, 190, 104, 192, 108)
    # Broken railing (DS3: wooden railings with gaps)
    fill_tiles(chunk, TILE_WALL, 148, 103, 165, 104)
    fill_tiles(chunk, TILE_WALL, 178, 103, 195, 104)
    # Graveyard tombstone rows (DS3: dense rows)
    for tx in range(148, 205, 6):
        fill_tiles(chunk, TILE_WALL, tx, 112, tx + 1, 114)
    for tx in range(152, 200, 6):
        fill_tiles(chunk, TILE_WALL, tx, 120, tx + 1, 122)
    # Sewer entrance (DS3: underground sewer)
    fill_tiles(chunk, TILE_WALL, 162, 126, 164, 132)
    fill_tiles(chunk, TILE_WALL, 192, 126, 194, 132)
    # Hodrick invasion debris
    fill_tiles(chunk, TILE_WALL, 178, 134, 182, 136)

    # ================================================================
    # 9. CLIFF UNDERSIDE — underground passages
    # DS3: sewers with rats, locked cell, Irina, Eygon
    # Section: x=3120,y=2080 → tiles (195,130)-(252,168)
    # ================================================================
    # Underground passage walls
    fill_tiles(chunk, TILE_WALL, 195, 130, 198, 135)
    fill_tiles(chunk, TILE_WALL, 248, 130, 252, 135)
    fill_tiles(chunk, TILE_WALL, 195, 164, 198, 168)
    fill_tiles(chunk, TILE_WALL, 248, 164, 252, 168)
    # Sewer tunnel walls (DS3: narrow tunnels with rats)
    fill_tiles(chunk, TILE_WALL, 206, 138, 208, 148)
    fill_tiles(chunk, TILE_WALL, 232, 138, 234, 148)
    fill_tiles(chunk, TILE_WALL, 216, 152, 224, 154)
    # Irina's cell (DS3: locked room behind Grave Key door)
    fill_tiles(chunk, TILE_WALL, 238, 140, 240, 152)
    fill_tiles(chunk, TILE_WALL, 248, 140, 250, 152)
    fill_tiles(chunk, TILE_WALL, 238, 140, 250, 142)
    # Skeleton stones outside cell (DS3: Root Skeletons)
    fill_tiles(chunk, TILE_WALL, 242, 158, 244, 160)
    fill_tiles(chunk, TILE_WALL, 236, 162, 238, 164)
    fill_tiles(chunk, TILE_WALL, 248, 162, 250, 164)

    # ================================================================
    # 10. GREATWOOD COURTYARD — boss arena
    # DS3: open courtyard, praying hollows, Curse-rotted Greatwood
    # Section: x=2460,y=2860 → tiles (153,178)-(223,220)
    # ================================================================
    # Arena perimeter walls
    fill_tiles(chunk, TILE_WALL, 153, 178, 160, 181)
    fill_tiles(chunk, TILE_WALL, 216, 178, 223, 181)
    fill_tiles(chunk, TILE_WALL, 153, 217, 160, 220)
    fill_tiles(chunk, TILE_WALL, 216, 217, 223, 220)
    # Hollow prayer spots (DS3: hollows praying at flowers)
    fill_tiles(chunk, TILE_WALL, 166, 188, 168, 190)
    fill_tiles(chunk, TILE_WALL, 180, 188, 182, 190)
    fill_tiles(chunk, TILE_WALL, 194, 188, 196, 190)
    fill_tiles(chunk, TILE_WALL, 208, 188, 210, 190)
    # Greatwood tree base (DS3: massive twisted tree)
    fill_tiles(chunk, TILE_WALL, 178, 200, 182, 204)
    fill_tiles(chunk, TILE_WALL, 198, 200, 202, 204)
    # Pit of Hollows drop (DS3: after boss, drop to lower level)
    fill_tiles(chunk, TILE_GROUND, 175, 215, 205, 230)
    fill_tiles(chunk, TILE_GROUND, 182, 230, 198, 245)

    # ================================================================
    # 11. ROAD OF SACRIFICES LIFT — exit to next area
    # DS3: stone elevator guarded by Boreal Outrider Knight
    # Section: x=4040,y=2260 → tiles (252,141)-(288,180)
    # ================================================================
    # Lift shaft walls
    fill_tiles(chunk, TILE_WALL, 254, 143, 256, 155)
    fill_tiles(chunk, TILE_WALL, 282, 143, 286, 155)
    fill_tiles(chunk, TILE_WALL, 254, 168, 256, 178)
    fill_tiles(chunk, TILE_WALL, 282, 168, 286, 178)
    # Lift platform
    fill_tiles(chunk, TILE_WALL, 262, 158, 264, 162)
    fill_tiles(chunk, TILE_WALL, 276, 158, 278, 162)
    # Exit gate
    fill_tiles(chunk, TILE_WALL, 260, 172, 280, 174)

    # ================================================================
    # CONNECTION CORRIDORS — key DS3 route paths
    # ================================================================
    # Entry → Settlement Entry Street (south-east)
    fill_tiles(chunk, TILE_GROUND, 30, 35, 70, 50)
    # Settlement Entry Street → House Shortcut (east)
    fill_tiles(chunk, TILE_GROUND, 75, 65, 105, 78)
    # House Shortcut → Burning Tree Square (east)
    fill_tiles(chunk, TILE_GROUND, 120, 70, 140, 85)
    # Burning Tree → Giant Tower (east, cage elevator route)
    fill_tiles(chunk, TILE_GROUND, 165, 78, 195, 90)
    # Giant Tower → Fire Demon Plaza (south-east)
    fill_tiles(chunk, TILE_GROUND, 215, 95, 230, 105)
    # Fire Demon Plaza → Road of Sacrifices Lift
    fill_tiles(chunk, TILE_GROUND, 250, 115, 270, 150)
    # Burning Tree → Dilapidated Bridge (south)
    fill_tiles(chunk, TILE_GROUND, 148, 105, 175, 125)
    # Dilapidated Bridge → Cliff Underside (south-east)
    fill_tiles(chunk, TILE_GROUND, 190, 130, 215, 145)
    # Cliff Underside → Greatwood Courtyard (south)
    fill_tiles(chunk, TILE_GROUND, 200, 160, 195, 185)
    # House Shortcut → Tree-shaded Path (east)
    fill_tiles(chunk, TILE_GROUND, 130, 55, 140, 65)
    # Tree-shaded Path → Giant Tower (east)
    fill_tiles(chunk, TILE_GROUND, 148, 50, 185, 70)

    # ================================================================
    # FINALIZE — load doc, apply terrain, return
    # ================================================================
    spawn_px, spawn_py = 300, 400  # Foot of the High Wall bonfire
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("UndeadSettlement"))
    return finalize_map("UndeadSettlement", chunk, entities, spawn_px, spawn_py)
