from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_ellipse, carve_corridor,
    make_entity, make_field, apply_doc_terrain, finalize_map,
    load_doc,
)



def make_lothric_castle():
    """Lothric Castle - Dragonslayer Armour boss arena.

    DS3-faithful layout (256x384 tiles, 4096x6144 pixels):
    Progression: Entry from LothricWall (west) -> Dancer ladder hall -> castle
    entry hall -> Winged Knight tower side -> castle stairs -> Twin Dragon Bridge
    (dragon corpses, Pus of Man) -> dark room below -> barracks interior ->
    Boreal Outrider vault -> Pus of Man room -> castle chapel -> elevator tower ->
    Dragonslayer Bridge -> Sunlight Altar rooftop -> Dragonslayer Armour arena ->
    Grand Archives Door (NE exit). Side path south to ConsumedKingsGarden.

    Sections from JSON doc (pixel // 16 = tile):
      0  Dancer Ladder Hall       (26,40)-(73,80)    stone staircase, ladder shaft
      1  Lothric Castle Entry      (62,67)-(110,102)  castle gate, grand archway
      2  Winged Knight Tower       (37,62)-(68,87)    spiral staircase, drop hole
      3  Castle Stairs             (106,43)-(143,68)  winding stairs, crossbow hollows
      4  Twin Dragon Bridge        (128,48)-(195,92)  dragon corpses, fire hazard
      5  Dark Room under Wyverns   (162,81)-(200,106) dark interior, firebarrels
      6  Barracks Interior         (136,93)-(193,133) barracks bunks, weapon racks
      7  Boreal Outrider Vault     (131,112)-(162,137) lower room, four chests
      8  Pus of Man Room           (181,106)-(212,131) wyvern claw, shortcut
      9  Castle Chapel             (200,93)-(237,125) chapel, red tearstone altar
     10  Elevator Shortcut Tower   (225,100)-(250,125) elevator shaft, iron gate
     11  Dragonslayer Bridge       (206,123)-(257,158) wide stone bridge, storms
     12  Sunlight Altar Rooftop    (237,112)-(268,137) sunlight altar, knight ring
     13  Dragonslayer Armour Arena (241,136)-(288,175) boss arena, battlements
     14  Grand Archives Door       (280,126)-(310,155) grand doorway, candles
     15  Consumed King Garden Br.  (47,100)-(86,132)  overgrown stone, moss walls

    JSON doc (docs/maps/LothricCastle.json) is authoritative for entity positions.
    """
    chunk = new_chunk(320, 384)

    # ================================================================
    # 0. DANCER LADDER HALL
    # DS3: Stone staircase rising from Dancer's arena below. Dark walls with
    #      torch sconces. Lothric Knights and Hollow Soldiers patrol the steps.
    #      Ladder shaft leads up. Tight, atmospheric vertical passage.
    # Tiles: (26,40)-(73,80)
    # ================================================================
    # Hall perimeter walls (DS3: dark stone walls enclosing the staircase)
    fill_tiles(chunk, TILE_WALL, 26, 40, 28, 80)      # West wall
    fill_tiles(chunk, TILE_WALL, 71, 40, 73, 80)      # East wall
    fill_tiles(chunk, TILE_WALL, 26, 40, 73, 42)      # North wall
    fill_tiles(chunk, TILE_WALL, 26, 78, 73, 80)      # South wall
    # Ladder shaft (DS3: ladder climbing up from lower level)
    fill_tiles(chunk, TILE_WALL, 30, 44, 32, 48)      # Shaft west wall
    fill_tiles(chunk, TILE_WALL, 38, 44, 40, 48)      # Shaft east wall
    fill_tiles(chunk, TILE_WALL, 30, 44, 40, 45)      # Shaft top wall
    # Staircase buttresses (DS3: stone supports along the staircase walls)
    fill_tiles(chunk, TILE_WALL, 42, 50, 44, 55)      # Mid stair pillar left
    fill_tiles(chunk, TILE_WALL, 55, 50, 57, 55)      # Mid stair pillar right
    fill_tiles(chunk, TILE_WALL, 48, 62, 50, 67)      # Lower stair pillar
    fill_tiles(chunk, TILE_WALL, 60, 62, 62, 67)      # Lower stair pillar
    # Torch sconce alcoves (DS3: wall-mounted torches)
    fill_tiles(chunk, TILE_WALL, 29, 55, 30, 57)      # West sconce alcove
    fill_tiles(chunk, TILE_WALL, 69, 55, 70, 57)      # East sconce alcove
    fill_tiles(chunk, TILE_WALL, 29, 70, 30, 72)      # Lower west sconce
    fill_tiles(chunk, TILE_WALL, 69, 70, 70, 72)      # Lower east sconce
    # Dark corner pillars (DS3: pillars in corners of the staircase hall)
    fill_tiles(chunk, TILE_WALL, 33, 74, 35, 76)
    fill_tiles(chunk, TILE_WALL, 64, 74, 66, 76)

    # ================================================================
    # 1. LOTHRIC CASTLE ENTRY
    # DS3: Grand castle gate with stone floor, banners hung on walls, a great
    #      archway entrance. Red-eyed Lothric Knight, Hollow Soldiers, Priests,
    #      a Mimic chest. The main bonfire "Lothric Castle" is here.
    # Tiles: (62,67)-(110,102)
    # ================================================================
    # Entry hall perimeter walls (DS3: grand stone gate walls)
    fill_tiles(chunk, TILE_WALL, 62, 67, 64, 102)     # West wall
    fill_tiles(chunk, TILE_WALL, 108, 67, 110, 102)   # East wall
    fill_tiles(chunk, TILE_WALL, 62, 67, 110, 69)     # North wall
    fill_tiles(chunk, TILE_WALL, 62, 100, 110, 102)   # South wall
    # Grand archway pillars (DS3: massive stone pillars at the gate)
    fill_tiles(chunk, TILE_WALL, 68, 72, 71, 80)      # Left gate pillar
    fill_tiles(chunk, TILE_WALL, 101, 72, 104, 80)    # Right gate pillar
    fill_tiles(chunk, TILE_WALL, 68, 90, 71, 97)      # Left inner pillar
    fill_tiles(chunk, TILE_WALL, 101, 90, 104, 97)    # Right inner pillar
    # Banner alcoves (DS3: Lothric banners on walls)
    fill_tiles(chunk, TILE_WALL, 66, 82, 67, 85)      # West banner alcove
    fill_tiles(chunk, TILE_WALL, 105, 82, 106, 85)    # East banner alcove
    # Central stone columns (DS3: pillars supporting vaulted ceiling)
    fill_tiles(chunk, TILE_WALL, 80, 76, 82, 79)
    fill_tiles(chunk, TILE_WALL, 90, 76, 92, 79)
    fill_tiles(chunk, TILE_WALL, 85, 88, 87, 91)
    # Entry vestibule walls (DS3: small vestibule before main hall)
    fill_tiles(chunk, TILE_WALL, 75, 95, 77, 98)
    fill_tiles(chunk, TILE_WALL, 95, 95, 97, 98)

    # ================================================================
    # 2. WINGED KNIGHT TOWER
    # DS3: Spiral staircase tower. A Winged Knight drops from a hole above.
    #      Hidden wall conceals a secret room. Upper room with item.
    # Tiles: (37,62)-(68,87)
    # ================================================================
    # Tower perimeter (DS3: round stone tower walls)
    fill_tiles(chunk, TILE_WALL, 37, 62, 39, 87)      # West wall
    fill_tiles(chunk, TILE_WALL, 66, 62, 68, 87)      # East wall
    fill_tiles(chunk, TILE_WALL, 37, 62, 68, 64)      # North wall
    fill_tiles(chunk, TILE_WALL, 37, 85, 68, 87)      # South wall
    # Spiral staircase center column (DS3: central pillar of spiral stairs)
    fill_tiles(chunk, TILE_WALL, 48, 70, 56, 78)
    carve_ellipse(chunk, 52, 74, 3, 3)                 # Hollow center
    # Dropping knight hole (DS3: hole in ceiling where Winged Knight drops)
    fill_tiles(chunk, TILE_WALL, 42, 66, 44, 68)      # Hole frame left
    fill_tiles(chunk, TILE_WALL, 60, 66, 62, 68)      # Hole frame right
    # Hidden wall alcove (DS3: illusory wall concealing secret)
    fill_tiles(chunk, TILE_WALL, 41, 80, 43, 83)
    # Upper room partition (DS3: upper room accessed via ladder)
    fill_tiles(chunk, TILE_WALL, 58, 72, 60, 75)

    # ================================================================
    # 3. CASTLE STAIRS
    # DS3: Long winding stone staircase. Crossbow hollows fire from above.
    #      Tower top at the end with a Crystal Lizard. Stone railings.
    # Tiles: (106,43)-(143,68)
    # ================================================================
    # Stair walls (DS3: stone walls along winding staircase)
    fill_tiles(chunk, TILE_WALL, 106, 43, 108, 68)    # West wall
    fill_tiles(chunk, TILE_WALL, 141, 43, 143, 68)    # East wall
    fill_tiles(chunk, TILE_WALL, 106, 43, 143, 45)    # North wall (tower top)
    fill_tiles(chunk, TILE_WALL, 106, 66, 143, 68)    # South wall
    # Stair landing buttresses (DS3: stone supports at each turn)
    fill_tiles(chunk, TILE_WALL, 114, 48, 116, 51)
    fill_tiles(chunk, TILE_WALL, 130, 48, 132, 51)
    fill_tiles(chunk, TILE_WALL, 118, 55, 120, 58)
    fill_tiles(chunk, TILE_WALL, 126, 55, 128, 58)
    # Stone railing posts (DS3: stone balusters along stairs)
    fill_tiles(chunk, TILE_WALL, 110, 50, 111, 51)
    fill_tiles(chunk, TILE_WALL, 138, 50, 139, 51)
    fill_tiles(chunk, TILE_WALL, 112, 60, 113, 61)
    fill_tiles(chunk, TILE_WALL, 136, 60, 137, 61)
    # Crossbow hollow perches (DS3: elevated positions for hollow crossbowmen)
    fill_tiles(chunk, TILE_WALL, 122, 46, 124, 48)

    # ================================================================
    # 4. TWIN DRAGON BRIDGE
    # DS3: Massive stone bridge with two dragon corpses. Fire breath hazard
    #      sweeps across. Barricades provide cover. Pus of Man on dragon corpses.
    #      Lothric Wyverns are the main hazard. Crystal Lizards at edges.
    # Tiles: (128,48)-(195,92)
    # ================================================================
    # Bridge perimeter walls (DS3: high stone bridge parapets)
    fill_tiles(chunk, TILE_WALL, 128, 48, 130, 92)    # West wall
    fill_tiles(chunk, TILE_WALL, 193, 48, 195, 92)    # East wall
    fill_tiles(chunk, TILE_WALL, 128, 48, 195, 50)    # North parapet
    fill_tiles(chunk, TILE_WALL, 128, 90, 195, 92)    # South parapet
    # Dragon corpse 1 - western wyvern (DS3: massive dragon skeleton blocking bridge)
    fill_tiles(chunk, TILE_WALL, 138, 55, 155, 60)    # Wyvern body
    fill_tiles(chunk, TILE_WALL, 135, 53, 140, 55)    # Wyvern head
    fill_tiles(chunk, TILE_WALL, 150, 57, 158, 62)    # Wyvern tail
    # Dragon corpse 2 - eastern wyvern (DS3: second dragon corpse)
    fill_tiles(chunk, TILE_WALL, 170, 65, 187, 70)    # Wyvern body
    fill_tiles(chunk, TILE_WALL, 167, 63, 172, 65)    # Wyvern head
    fill_tiles(chunk, TILE_WALL, 182, 67, 190, 72)    # Wyvern tail
    # Barricades (DS3: wooden/stone barricades providing cover from fire)
    fill_tiles(chunk, TILE_WALL, 145, 62, 148, 64)    # Barricade near wyvern 1
    fill_tiles(chunk, TILE_WALL, 160, 55, 163, 57)    # Barricade mid-bridge
    fill_tiles(chunk, TILE_WALL, 178, 72, 181, 74)    # Barricade near wyvern 2
    # Fire scorched debris (DS3: scorched stone from dragon breath)
    fill_tiles(chunk, TILE_WALL, 155, 80, 157, 82)
    fill_tiles(chunk, TILE_WALL, 175, 82, 177, 84)
    # Bridge arch supports (DS3: massive stone arches beneath bridge)
    fill_tiles(chunk, TILE_WALL, 132, 85, 134, 88)
    fill_tiles(chunk, TILE_WALL, 155, 85, 157, 88)
    fill_tiles(chunk, TILE_WALL, 178, 85, 180, 88)

    # ================================================================
    # 5. DARK ROOM UNDER WYVERNS
    # DS3: Dark interior room beneath the dragon bridge. Firebarrel hollows
    #      hide here. Stone stairs lead down to barracks level.
    # Tiles: (162,81)-(200,106)
    # ================================================================
    # Room perimeter (DS3: dark stone walls)
    fill_tiles(chunk, TILE_WALL, 162, 81, 164, 106)   # West wall
    fill_tiles(chunk, TILE_WALL, 198, 81, 200, 106)   # East wall
    fill_tiles(chunk, TILE_WALL, 162, 81, 200, 83)    # North wall
    fill_tiles(chunk, TILE_WALL, 162, 104, 200, 106)  # South wall
    # Stone stairs down (DS3: stairs leading to barracks)
    fill_tiles(chunk, TILE_WALL, 186, 96, 188, 103)   # Stair wall left
    fill_tiles(chunk, TILE_WALL, 194, 96, 196, 103)   # Stair wall right
    # Firebarrel positions (DS3: explosive barrels hollows use)
    fill_tiles(chunk, TILE_WALL, 170, 88, 172, 90)
    fill_tiles(chunk, TILE_WALL, 178, 92, 180, 94)
    # Dark corner debris
    fill_tiles(chunk, TILE_WALL, 166, 98, 168, 100)
    fill_tiles(chunk, TILE_WALL, 190, 86, 192, 88)

    # ================================================================
    # 6. BARRACKS INTERIOR
    # DS3: Lothric Knight barracks with bunks, weapon racks, iron grates.
    #      Winged Knights, a Boreal Outrider Knight. Dense enemy area.
    #      Estus Shard and other loot in chests.
    # Tiles: (136,93)-(193,133)
    # ================================================================
    # Barracks perimeter walls (DS3: stone barrack walls)
    fill_tiles(chunk, TILE_WALL, 136, 93, 138, 133)   # West wall
    fill_tiles(chunk, TILE_WALL, 191, 93, 193, 133)   # East wall
    fill_tiles(chunk, TILE_WALL, 136, 93, 193, 95)    # North wall
    fill_tiles(chunk, TILE_WALL, 136, 131, 193, 133)  # South wall
    # Bunk partitions (DS3: stone walls dividing sleeping quarters)
    fill_tiles(chunk, TILE_WALL, 148, 98, 150, 108)   # Bunk wall left
    fill_tiles(chunk, TILE_WALL, 165, 98, 167, 108)   # Bunk wall center
    fill_tiles(chunk, TILE_WALL, 180, 98, 182, 108)   # Bunk wall right
    # Weapon rack alcoves (DS3: weapon racks along walls)
    fill_tiles(chunk, TILE_WALL, 140, 100, 142, 104)  # West weapon rack
    fill_tiles(chunk, TILE_WALL, 140, 112, 142, 116)  # West lower rack
    fill_tiles(chunk, TILE_WALL, 187, 100, 189, 104)  # East weapon rack
    fill_tiles(chunk, TILE_WALL, 187, 112, 189, 116)  # East lower rack
    # Iron grate supports (DS3: iron grates between rooms)
    fill_tiles(chunk, TILE_WALL, 155, 115, 158, 118)  # Grate mid
    fill_tiles(chunk, TILE_WALL, 172, 115, 175, 118)  # Grate east
    # Boreal Outrider alcove (DS3: frost knight room)
    fill_tiles(chunk, TILE_WALL, 138, 120, 140, 128)  # Frost room west
    fill_tiles(chunk, TILE_WALL, 148, 120, 150, 128)  # Frost room east
    fill_tiles(chunk, TILE_WALL, 138, 126, 150, 128)  # Frost room south
    # Barracks central column (DS3: support column in middle of barracks)
    fill_tiles(chunk, TILE_WALL, 158, 122, 160, 125)

    # ================================================================
    # 7. BOREAL OUTRIDER KNIGHT VAULT
    # DS3: Lower room with iron door. Four chests inside, guarded by the
    #      Boreal Outrider Knight who deals frost damage.
    # Tiles: (131,112)-(162,137)
    # ================================================================
    # Vault perimeter (DS3: stone vault walls)
    fill_tiles(chunk, TILE_WALL, 131, 112, 133, 137)  # West wall
    fill_tiles(chunk, TILE_WALL, 160, 112, 162, 137)  # East wall
    fill_tiles(chunk, TILE_WALL, 131, 112, 162, 114)  # North wall
    fill_tiles(chunk, TILE_WALL, 131, 135, 162, 137)  # South wall
    # Iron door frame (DS3: heavy iron door entrance)
    fill_tiles(chunk, TILE_WALL, 143, 112, 145, 116)  # Door frame left
    fill_tiles(chunk, TILE_WALL, 150, 112, 152, 116)  # Door frame right
    # Chest alcove walls (DS3: chest niches in vault walls)
    fill_tiles(chunk, TILE_WALL, 136, 118, 138, 122)  # NW chest alcove
    fill_tiles(chunk, TILE_WALL, 155, 118, 157, 122)  # NE chest alcove
    fill_tiles(chunk, TILE_WALL, 136, 128, 138, 132)  # SW chest alcove
    fill_tiles(chunk, TILE_WALL, 155, 128, 157, 132)  # SE chest alcove
    # Frost-cracked pillar (DS3: frost damage on stone)
    fill_tiles(chunk, TILE_WALL, 145, 124, 148, 127)

    # ================================================================
    # 8. PUS OF MAN ROOM
    # DS3: Interior room with wyvern claw reaching in. Pus of Man weak point
    #      is here. Castle gate lever and shortcut mechanism inside.
    # Tiles: (181,106)-(212,131)
    # ================================================================
    # Room perimeter (DS3: stone walls)
    fill_tiles(chunk, TILE_WALL, 181, 106, 183, 131)  # West wall
    fill_tiles(chunk, TILE_WALL, 210, 106, 212, 131)  # East wall
    fill_tiles(chunk, TILE_WALL, 181, 106, 212, 108)  # North wall
    fill_tiles(chunk, TILE_WALL, 181, 129, 212, 131)  # South wall
    # Wyvern claw alcove (DS3: dragon claw reaching through wall)
    fill_tiles(chunk, TILE_WALL, 185, 110, 190, 114)  # Claw debris NW
    fill_tiles(chunk, TILE_WALL, 195, 110, 200, 114)  # Claw debris NE
    # Shortcut mechanism (DS3: lever and gate mechanism)
    fill_tiles(chunk, TILE_WALL, 204, 118, 208, 122)  # Mechanism housing
    # Gate lever (DS3: iron lever)
    fill_tiles(chunk, TILE_WALL, 186, 122, 188, 126)
    # Interior debris (DS3: scattered stones)
    fill_tiles(chunk, TILE_WALL, 193, 120, 195, 123)
    fill_tiles(chunk, TILE_WALL, 200, 126, 202, 128)

    # ================================================================
    # 9. CASTLE CHAPEL
    # DS3: Small chapel interior with red tearstone altar. Eygon summon spot.
    #      Rusted coins near the altar. Sacred and solemn atmosphere.
    # Tiles: (200,93)-(237,125)
    # ================================================================
    # Chapel perimeter (DS3: chapel stone walls)
    fill_tiles(chunk, TILE_WALL, 200, 93, 202, 125)   # West wall
    fill_tiles(chunk, TILE_WALL, 235, 93, 237, 125)   # East wall
    fill_tiles(chunk, TILE_WALL, 200, 93, 237, 95)    # North wall
    fill_tiles(chunk, TILE_WALL, 200, 123, 237, 125)  # South wall
    # Altar (DS3: stone altar with red tearstone ring)
    fill_tiles(chunk, TILE_WALL, 214, 98, 224, 103)   # Altar platform
    fill_tiles(chunk, TILE_WALL, 216, 96, 222, 98)    # Altar back wall
    # Chapel columns (DS3: stone columns flanking the nave)
    fill_tiles(chunk, TILE_WALL, 206, 100, 208, 104)  # Left column front
    fill_tiles(chunk, TILE_WALL, 230, 100, 232, 104)  # Right column front
    fill_tiles(chunk, TILE_WALL, 206, 112, 208, 116)  # Left column rear
    fill_tiles(chunk, TILE_WALL, 230, 112, 232, 116)  # Right column rear
    # Pews (DS3: stone pews in chapel)
    fill_tiles(chunk, TILE_WALL, 210, 106, 212, 109)  # Pew row 1 left
    fill_tiles(chunk, TILE_WALL, 226, 106, 228, 109)  # Pew row 1 right
    fill_tiles(chunk, TILE_WALL, 210, 113, 212, 116)  # Pew row 2 left
    fill_tiles(chunk, TILE_WALL, 226, 113, 228, 116)  # Pew row 2 right

    # ================================================================
    # 10. ELEVATOR SHORTCUT TOWER
    # DS3: Stone tower with elevator shaft. Iron gate at top and bottom.
    #      Provides shortcut between Dragonslayer Bridge and lower castle.
    # Tiles: (225,100)-(250,125)
    # ================================================================
    # Tower perimeter (DS3: cylindrical stone tower)
    fill_tiles(chunk, TILE_WALL, 225, 100, 227, 125)  # West wall
    fill_tiles(chunk, TILE_WALL, 248, 100, 250, 125)  # East wall
    fill_tiles(chunk, TILE_WALL, 225, 100, 250, 102)  # North wall
    fill_tiles(chunk, TILE_WALL, 225, 123, 250, 125)  # South wall
    # Elevator shaft (DS3: central elevator mechanism)
    fill_tiles(chunk, TILE_WALL, 233, 105, 243, 120)  # Shaft walls
    fill_tiles(chunk, TILE_GROUND, 234, 106, 242, 119) # Shaft interior
    # Iron gate frame at top (DS3: iron gate)
    fill_tiles(chunk, TILE_WALL, 230, 100, 232, 104)  # Gate pillar left
    fill_tiles(chunk, TILE_WALL, 244, 100, 246, 104)  # Gate pillar right
    # Iron gate frame at bottom (DS3: iron gate)
    fill_tiles(chunk, TILE_WALL, 230, 121, 232, 125)  # Gate pillar left
    fill_tiles(chunk, TILE_WALL, 244, 121, 246, 125)  # Gate pillar right
    # Tower stone steps (DS3: narrow steps alongside elevator)
    fill_tiles(chunk, TILE_WALL, 228, 108, 230, 110)
    fill_tiles(chunk, TILE_WALL, 228, 116, 230, 118)

    # ================================================================
    # 11. DRAGONSLAYER BRIDGE
    # DS3: Wide stone bridge leading to Dragonslayer Armour. Dragon sculptures
    #      on the parapets. Storm clouds overhead, wind-blasted atmosphere.
    #      Lothric Knights patrol the bridge.
    # Tiles: (206,123)-(257,158)
    # ================================================================
    # Bridge perimeter (DS3: wide stone bridge with parapets)
    fill_tiles(chunk, TILE_WALL, 206, 123, 208, 158)  # West wall
    fill_tiles(chunk, TILE_WALL, 255, 123, 257, 158)  # East wall
    fill_tiles(chunk, TILE_WALL, 206, 123, 257, 125)  # North parapet
    fill_tiles(chunk, TILE_WALL, 206, 156, 257, 158)  # South parapet
    # Dragon sculptures (DS3: stone dragon statues on parapets)
    fill_tiles(chunk, TILE_WALL, 215, 124, 219, 127)  # Dragon sculpture 1
    fill_tiles(chunk, TILE_WALL, 240, 124, 244, 127)  # Dragon sculpture 2
    fill_tiles(chunk, TILE_WALL, 215, 154, 219, 157)  # Dragon sculpture 3
    fill_tiles(chunk, TILE_WALL, 240, 154, 244, 157)  # Dragon sculpture 4
    # Bridge arch supports (DS3: massive arches supporting the bridge)
    fill_tiles(chunk, TILE_WALL, 212, 138, 214, 148)  # Arch support 1
    fill_tiles(chunk, TILE_WALL, 230, 138, 232, 148)  # Arch support 2
    fill_tiles(chunk, TILE_WALL, 248, 138, 250, 148)  # Arch support 3
    # Storm debris (DS3: wind-blown stone fragments)
    fill_tiles(chunk, TILE_WALL, 222, 132, 224, 134)
    fill_tiles(chunk, TILE_WALL, 236, 148, 238, 150)

    # ================================================================
    # 12. SUNLIGHT ALTAR ROFTOP
    # DS3: Rooftop with Sunlight Altar (covenant). Knight's Ring in tower.
    #      Covered bridge connects to castle. Lothric Knights patrol.
    # Tiles: (237,112)-(268,137)
    # ================================================================
    # Rooftop perimeter (DS3: castle rooftop walls)
    fill_tiles(chunk, TILE_WALL, 237, 112, 239, 137)  # West wall
    fill_tiles(chunk, TILE_WALL, 266, 112, 268, 137)  # East wall
    fill_tiles(chunk, TILE_WALL, 237, 112, 268, 114)  # North wall
    fill_tiles(chunk, TILE_WALL, 237, 135, 268, 137)  # South wall
    # Sunlight Altar (DS3: covenant altar, stone platform)
    fill_tiles(chunk, TILE_WALL, 248, 118, 257, 124)  # Altar platform
    fill_tiles(chunk, TILE_WALL, 250, 116, 255, 118)  # Altar back
    # Knight's Ring tower (DS3: small tower with the ring)
    fill_tiles(chunk, TILE_WALL, 260, 120, 264, 130)  # Tower walls
    fill_tiles(chunk, TILE_GROUND, 261, 121, 263, 129) # Tower interior
    # Covered bridge entrance (DS3: covered walkway to castle)
    fill_tiles(chunk, TILE_WALL, 240, 128, 242, 132)  # Bridge wall left
    fill_tiles(chunk, TILE_WALL, 246, 128, 248, 132)  # Bridge wall right

    # ================================================================
    # 13. DRAGONSLAYER ARMOUR ARENA
    # DS3: Large boss arena on a widened castle bridge. Battlement walls
    #      overlook the castle below. Storm-swept atmosphere. The boss
    #      Dragonslayer Armour fights here with a greatshield and greataxe.
    # Tiles: (241,136)-(288,175)
    # ================================================================
    # Arena perimeter (DS3: high battlement walls)
    fill_tiles(chunk, TILE_WALL, 241, 136, 243, 175)  # West wall
    fill_tiles(chunk, TILE_WALL, 286, 136, 288, 175)  # East wall
    fill_tiles(chunk, TILE_WALL, 241, 136, 288, 138)  # North wall
    fill_tiles(chunk, TILE_WALL, 241, 173, 288, 175)  # South wall
    # Battlement merlons (DS3: crenellated stone battlements)
    fill_tiles(chunk, TILE_WALL, 250, 137, 252, 139)
    fill_tiles(chunk, TILE_WALL, 262, 137, 264, 139)
    fill_tiles(chunk, TILE_WALL, 274, 137, 276, 139)
    fill_tiles(chunk, TILE_WALL, 250, 174, 252, 176)
    fill_tiles(chunk, TILE_WALL, 262, 174, 264, 176)
    fill_tiles(chunk, TILE_WALL, 274, 174, 276, 176)
    # Arena columns (DS3: stone columns at arena edges)
    fill_tiles(chunk, TILE_WALL, 248, 145, 250, 152)  # NW column
    fill_tiles(chunk, TILE_WALL, 280, 145, 282, 152)  # NE column
    fill_tiles(chunk, TILE_WALL, 248, 160, 250, 167)  # SW column
    fill_tiles(chunk, TILE_WALL, 280, 160, 282, 167)  # SE column
    # Bridge widening markers (DS3: bridge widens into arena)
    fill_tiles(chunk, TILE_WALL, 255, 143, 257, 145)
    fill_tiles(chunk, TILE_WALL, 273, 143, 275, 145)
    fill_tiles(chunk, TILE_WALL, 255, 168, 257, 170)
    fill_tiles(chunk, TILE_WALL, 273, 168, 275, 170)
    # Overlooking castle parapet (DS3: view of castle below)
    fill_tiles(chunk, TILE_WALL, 260, 150, 270, 155)

    # ================================================================
    # 14. GRAND ARCHIVES DOOR
    # DS3: Grand doorway to the Grand Archives. Candle sconces on walls.
    #      Stone steps lead up. Wax accumulations from candles. Crystal Lizards.
    # Tiles: (280,126)-(310,155)
    # ================================================================
    # Doorway perimeter (DS3: grand stone doorway)
    fill_tiles(chunk, TILE_WALL, 280, 126, 282, 155)  # West wall
    fill_tiles(chunk, TILE_WALL, 308, 126, 310, 155)  # East wall
    fill_tiles(chunk, TILE_WALL, 280, 126, 310, 128)  # North wall
    fill_tiles(chunk, TILE_WALL, 280, 153, 310, 155)  # South wall
    # Grand door frame (DS3: massive double door frame)
    fill_tiles(chunk, TILE_WALL, 288, 130, 291, 142)  # Left door pillar
    fill_tiles(chunk, TILE_WALL, 299, 130, 302, 142)  # Right door pillar
    fill_tiles(chunk, TILE_WALL, 288, 130, 302, 132)  # Door lintel
    # Stone steps (DS3: steps leading up to archives)
    fill_tiles(chunk, TILE_WALL, 292, 140, 294, 145)  # Step wall left
    fill_tiles(chunk, TILE_WALL, 297, 140, 299, 145)  # Step wall right
    # Candle sconces (DS3: wall-mounted candles)
    fill_tiles(chunk, TILE_WALL, 284, 135, 285, 137)  # West sconce
    fill_tiles(chunk, TILE_WALL, 305, 135, 306, 137)  # East sconce
    fill_tiles(chunk, TILE_WALL, 284, 145, 285, 147)  # Lower west sconce
    fill_tiles(chunk, TILE_WALL, 305, 145, 306, 147)  # Lower east sconce
    # Wax accumulation (DS3: wax dripping from candles)
    fill_tiles(chunk, TILE_WALL, 303, 142, 305, 144)

    # ================================================================
    # 15. CONSUMED KING GARDEN BRANCH
    # DS3: Overgrown stone path branching south from the castle. Moss-covered
    #      walls, crumbling stairs, vine-choked arches lead down to the garden.
    # Tiles: (47,100)-(86,132)
    # ================================================================
    # Path perimeter (DS3: crumbling overgrown walls)
    fill_tiles(chunk, TILE_WALL, 47, 100, 49, 132)    # West wall
    fill_tiles(chunk, TILE_WALL, 84, 100, 86, 132)    # East wall
    fill_tiles(chunk, TILE_WALL, 47, 100, 86, 102)    # North wall
    fill_tiles(chunk, TILE_WALL, 47, 130, 86, 132)    # South wall
    # Crumbling stairs (DS3: broken stone steps descending)
    fill_tiles(chunk, TILE_WALL, 58, 106, 60, 110)    # Step debris 1
    fill_tiles(chunk, TILE_WALL, 70, 112, 72, 116)    # Step debris 2
    fill_tiles(chunk, TILE_WALL, 58, 120, 60, 124)    # Step debris 3
    # Vine-choked arch (DS3: overgrown stone arch)
    fill_tiles(chunk, TILE_WALL, 52, 115, 54, 122)    # Arch pillar left
    fill_tiles(chunk, TILE_WALL, 78, 115, 80, 122)    # Arch pillar right
    fill_tiles(chunk, TILE_WALL, 55, 113, 77, 115)    # Arch top
    # Moss-covered walls (DS3: vegetation on stone)
    fill_tiles(chunk, TILE_WALL, 63, 125, 66, 128)    # Moss wall 1
    fill_tiles(chunk, TILE_WALL, 73, 118, 76, 121)    # Moss wall 2

    # ================================================================
    # CORRIDOR CONNECTIONS — ensure section adjacency is walkable
    # Additional corridors beyond what apply_doc_terrain provides
    # ================================================================
    # Dancer Hall -> Castle Entry (DS3: stairs from dancer hall into castle)
    carve_corridor(chunk, 49, 70, 72, 78, width=5)
    # Castle Entry -> Winged Knight Tower (DS3: side path to tower)
    carve_corridor(chunk, 72, 85, 52, 74, width=5)
    # Castle Entry -> Castle Stairs (DS3: main path up into castle)
    carve_corridor(chunk, 100, 75, 115, 55, width=5)
    # Castle Stairs -> Twin Dragon Bridge (DS3: stairs emerge onto bridge)
    carve_corridor(chunk, 130, 55, 145, 60, width=5)
    # Twin Dragon Bridge -> Dark Room (DS3: stairs down under bridge)
    carve_corridor(chunk, 170, 85, 175, 90, width=5)
    # Dark Room -> Barracks (DS3: continues down into barracks)
    carve_corridor(chunk, 178, 100, 165, 110, width=5)
    # Barracks -> Boreal Vault (DS3: side room in barracks)
    carve_corridor(chunk, 148, 120, 146, 125, width=5)
    # Barracks -> Pus of Man Room (DS3: passage to wyvern interior)
    carve_corridor(chunk, 190, 115, 195, 118, width=5)
    # Barracks -> Castle Chapel (DS3: path from barracks to chapel)
    carve_corridor(chunk, 180, 105, 210, 110, width=5)
    # Castle Chapel -> Elevator Tower (DS3: chapel connects to shortcut)
    carve_corridor(chunk, 230, 110, 237, 112, width=5)
    # Elevator Tower -> Dragonslayer Bridge (DS3: elevator emerges at bridge)
    carve_corridor(chunk, 237, 115, 220, 135, width=5)
    # Dragonslayer Bridge -> Sunlight Altar (DS3: bridge side to rooftop)
    carve_corridor(chunk, 240, 130, 250, 125, width=5)
    # Dragonslayer Bridge -> Dragonslayer Arena (DS3: bridge leads to arena)
    carve_corridor(chunk, 245, 150, 255, 150, width=5)
    # Sunlight Altar -> Dragonslayer Arena (DS3: rooftop to arena)
    carve_corridor(chunk, 255, 130, 258, 140, width=5)
    # Dragonslayer Arena -> Grand Archives Door (DS3: after boss, to archives)
    carve_corridor(chunk, 280, 150, 290, 140, width=5)
    # Castle Entry -> Consumed King Garden (DS3: side path to garden)
    carve_corridor(chunk, 75, 95, 65, 115, width=5)

    # ================================================================
    # PLAYER SPAWN
    # DS3: Player enters from LothricWall (fog gate at west of Dancer Hall).
    #      Spawn near the fog gate entry point.
    # Fog gate at doc: x=620,y=800 -> tile (38,50)
    # ================================================================
    spawn_px, spawn_py = 38 * 16, 50 * 16

    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    # ================================================================
    # BOSS SPAWN
    # DS3: Dragonslayer Armour at the center of the arena
    # ================================================================
    entities.append(make_entity("BossSpawn", 257 * 16, 148 * 16,
        [make_field("name", "String", "Dragonslayer Armour")]))

    # ================================================================
    # APPLY DOC TERRAIN — fills section interiors with ground,
    # connects section centers via corridors, clears bonfire/boss/fog
    # positions, and adds wall features from terrain_features dicts.
    # ================================================================
    apply_doc_terrain(chunk, load_doc("LothricCastle"))

    return finalize_map("LothricCastle", chunk, entities, spawn_px, spawn_py)
