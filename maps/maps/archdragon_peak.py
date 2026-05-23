from maps.generate_maps import (
    TILE_GROUND, TILE_WALL, TILE_WALLTOP, TILE_POISON,
    new_chunk, fill_tiles, carve_corridor, make_entity,
    make_field, apply_doc_terrain, finalize_map, load_doc,
)



def make_archdragon_peak():
    """Archdragon Peak - DS3-faithful terrain.

    Mountain peak area reached via Irithyll Dungeon gesture or Grand Archives
    bridge. Features serpent-man camps, ancient wyvern arena, dragon-kin
    mausoleum, great belfry, and the Nameless King boss at the storm summit.

    Map: 320x288 tiles (5120x4608 px).
    JSON doc sections (pixel -> tile = pixel // 16):
      1. Archdragon Entry Cliff:     (26,207)-(82,246)  - narrow mountain path entry
      2. Man-Serpent Camp:           (67,173)-(128,218)  - serpent-man barracks & training
      3. Ancient Wyvern Arena:       (118,157)-(180,202) - open wyvern arena with dragon bones
      4. Dragonkin Mausoleum:        (123,127)-(175,162) - dragon altar, summoners, Drakeblood
      5. Lightning Clutch Side-Path: (75,146)-(106,171)  - narrow cliff ledge
      6. Second Wyvern Path:         (165,96)-(226,137)  - ascending storm ridge
      7. Great Belfry:               (197,67)-(245,102)  - bell tower, Havel knight
      8. Serpent-Man Summoner Bldg:  (175,111)-(212,136) - summoner interior room
      9. Bell Lever Chamber:         (212,48)-(243,73)   - bell mechanism room
     10. Havel Rooftop Arena:        (231,87)-(268,118)  - rooftop with fallen wyvern
     11. Man-Serpent Gauntlet:       (243,112)-(281,143) - ruined courtyard gauntlet
     12. Path of the Dragon Altar:   (225,98)-(256,117)  - stone altar overlook
     13. Storm Cloud Bridge:         (225,25)-(262,50)   - floating storm bridge
     14. Nameless King Storm Arena:  (242,37)-(298,81)   - open storm boss arena
    """
    chunk = new_chunk(320, 288)

    # ================================================================
    # 1. ARCHDRAGON ENTRY CLIFF — narrow mountain path
    # DS3: player arrives via Path of the Dragon gesture, steep cliff path
    # Section: x=420,y=3320,w=900,h=620 -> tiles (26,207)-(82,246)
    # ================================================================
    # Cliff boundary walls (DS3: steep mountain cliffs on both sides)
    fill_tiles(chunk, TILE_WALL, 26, 207, 28, 246)       # West cliff wall
    fill_tiles(chunk, TILE_WALL, 80, 207, 82, 230)       # East cliff wall upper
    fill_tiles(chunk, TILE_WALL, 80, 238, 82, 246)       # East cliff wall lower
    fill_tiles(chunk, TILE_WALL, 26, 207, 55, 209)       # North wall left
    fill_tiles(chunk, TILE_WALL, 65, 207, 82, 209)       # North wall right
    fill_tiles(chunk, TILE_WALL, 26, 244, 60, 246)       # South wall left
    fill_tiles(chunk, TILE_WALL, 70, 244, 82, 246)       # South wall right
    # Serpent statue (DS3: serpent statue along the path)
    fill_tiles(chunk, TILE_WALL, 38, 217, 40, 220)
    # Cliff edge stones (DS3: rocky outcrops along narrow path)
    fill_tiles(chunk, TILE_WALL, 48, 221, 50, 222)
    fill_tiles(chunk, TILE_WALL, 62, 226, 64, 227)
    fill_tiles(chunk, TILE_WALL, 30, 234, 32, 236)
    fill_tiles(chunk, TILE_WALL, 70, 231, 72, 232)

    # ================================================================
    # 2. MAN-SERPENT CAMP — outdoor barracks and training grounds
    # DS3: serpent-men train at dummies, camp with statues and walls
    # Section: x=1080,y=2780,w=980,h=720 -> tiles (67,173)-(128,218)
    # ================================================================
    # Camp boundary walls (DS3: stone walls surrounding serpent-man camp)
    fill_tiles(chunk, TILE_WALL, 67, 173, 69, 200)       # West wall upper
    fill_tiles(chunk, TILE_WALL, 67, 210, 69, 218)       # West wall lower
    fill_tiles(chunk, TILE_WALL, 126, 173, 128, 195)     # East wall upper
    fill_tiles(chunk, TILE_WALL, 126, 205, 128, 218)     # East wall lower
    fill_tiles(chunk, TILE_WALL, 67, 173, 95, 175)       # North wall left
    fill_tiles(chunk, TILE_WALL, 110, 173, 128, 175)     # North wall right
    fill_tiles(chunk, TILE_WALL, 67, 216, 100, 218)      # South wall left
    fill_tiles(chunk, TILE_WALL, 110, 216, 128, 218)     # South wall right
    # Training dummy posts (DS3: wooden training dummies)
    fill_tiles(chunk, TILE_WALL, 72, 178, 74, 181)       # Training dummy NW
    fill_tiles(chunk, TILE_WALL, 87, 193, 89, 195)       # Training dummy SE
    # Barracks walls (DS3: stone walls dividing camp sections)
    fill_tiles(chunk, TILE_WALL, 93, 192, 96, 195)       # Barracks wall 1
    fill_tiles(chunk, TILE_WALL, 107, 180, 110, 183)     # Barracks wall 2
    # Serpent statues (DS3: carved serpent imagery)
    fill_tiles(chunk, TILE_WALL, 80, 183, 82, 186)       # Serpent statue NW
    fill_tiles(chunk, TILE_WALL, 102, 182, 104, 185)     # Serpent statue NE
    fill_tiles(chunk, TILE_WALL, 78, 205, 80, 208)       # Serpent statue SW
    # Campfire pit (DS3: central fire pit)
    fill_tiles(chunk, TILE_WALL, 95, 192, 99, 196)

    # ================================================================
    # 3. ANCIENT WYVERN ARENA — open arena with massive dragon bones
    # DS3: Ancient Wyvern boss fight, huge dragon skeleton scattered around
    # Section: x=1900,y=2520,w=980,h=720 -> tiles (118,157)-(180,202)
    # ================================================================
    # Arena boundary walls (DS3: open cliff-side arena)
    fill_tiles(chunk, TILE_WALL, 118, 157, 120, 188)     # West wall upper
    fill_tiles(chunk, TILE_WALL, 118, 198, 120, 202)     # West wall lower
    fill_tiles(chunk, TILE_WALL, 178, 157, 180, 185)     # East wall upper
    fill_tiles(chunk, TILE_WALL, 178, 195, 180, 202)     # East wall lower
    fill_tiles(chunk, TILE_WALL, 118, 157, 150, 159)     # North wall left
    fill_tiles(chunk, TILE_WALL, 160, 157, 180, 159)     # North wall right
    fill_tiles(chunk, TILE_WALL, 118, 200, 145, 202)     # South wall left
    fill_tiles(chunk, TILE_WALL, 155, 200, 180, 202)     # South wall right
    # Massive dragon bone structures (DS3: enormous skeletal remains)
    fill_tiles(chunk, TILE_WALL, 126, 162, 129, 166)     # Dragon rib NW
    fill_tiles(chunk, TILE_WALL, 138, 170, 141, 173)     # Dragon rib center
    fill_tiles(chunk, TILE_WALL, 132, 180, 135, 183)     # Dragon rib SW
    fill_tiles(chunk, TILE_WALL, 151, 165, 154, 168)     # Dragon bone NE
    fill_tiles(chunk, TILE_WALL, 122, 175, 124, 177)     # Dragon fragment W
    fill_tiles(chunk, TILE_WALL, 160, 181, 163, 184)     # Dragon bone SE
    # Wyvern perch (DS3: wyvern stands atop bones)
    fill_tiles(chunk, TILE_WALL, 145, 173, 149, 177)     # Perch platform
    # Cliff edge debris (DS3: debris at arena edge)
    fill_tiles(chunk, TILE_WALL, 170, 190, 172, 193)
    fill_tiles(chunk, TILE_WALL, 125, 195, 127, 197)

    # ================================================================
    # 4. DRAGONKIN MAUSOLEUM — dragon altar chamber with summoners
    # DS3: interior room with dragon altar, Serpent-Man Summoners, Drakeblood Knights
    # Section: x=1980,y=2040,w=820,h=560 -> tiles (123,127)-(175,162)
    # ================================================================
    # Mausoleum boundary walls (DS3: ancient stone temple walls)
    fill_tiles(chunk, TILE_WALL, 123, 127, 125, 155)     # West wall
    fill_tiles(chunk, TILE_WALL, 173, 127, 175, 150)     # East wall upper
    fill_tiles(chunk, TILE_WALL, 173, 158, 175, 162)     # East wall lower
    fill_tiles(chunk, TILE_WALL, 123, 127, 148, 129)     # North wall left
    fill_tiles(chunk, TILE_WALL, 158, 127, 175, 129)     # North wall right
    fill_tiles(chunk, TILE_WALL, 123, 160, 148, 162)     # South wall left
    fill_tiles(chunk, TILE_WALL, 158, 160, 175, 162)     # South wall right
    # Dragon altar (DS3: stone altar with dragon-crest medallion)
    fill_tiles(chunk, TILE_WALL, 140, 140, 145, 145)     # Central altar
    # Altar alcove walls (DS3: recessed alcoves with dragon imagery)
    fill_tiles(chunk, TILE_WALL, 128, 131, 130, 135)     # NW alcove wall
    fill_tiles(chunk, TILE_WALL, 142, 131, 144, 134)     # N alcove wall
    fill_tiles(chunk, TILE_WALL, 165, 135, 168, 138)     # NE alcove wall
    fill_tiles(chunk, TILE_WALL, 155, 152, 158, 156)     # SE alcove wall
    # Stone pillars (DS3: temple interior pillars)
    fill_tiles(chunk, TILE_WALL, 135, 148, 137, 152)     # SW pillar
    fill_tiles(chunk, TILE_WALL, 160, 145, 162, 149)     # E pillar

    # ================================================================
    # 5. LIGHTNING CLUTCH SIDE-PATH — narrow cliff ledge
    # DS3: optional narrow ledge with Lightning Clutch Ring
    # Section: x=1200,y=2340,w=500,h=400 -> tiles (75,146)-(106,171)
    # ================================================================
    # Ledge walls (DS3: narrow path with cliff drop on one side)
    fill_tiles(chunk, TILE_WALL, 75, 146, 77, 165)       # West wall
    fill_tiles(chunk, TILE_WALL, 104, 146, 106, 160)     # East wall upper
    fill_tiles(chunk, TILE_WALL, 104, 166, 106, 171)     # East wall lower
    fill_tiles(chunk, TILE_WALL, 75, 146, 95, 148)       # North wall
    fill_tiles(chunk, TILE_WALL, 75, 169, 106, 171)      # South cliff edge
    # Cliff overlook rocks (DS3: wind-blasted stones)
    fill_tiles(chunk, TILE_WALL, 82, 155, 84, 157)
    fill_tiles(chunk, TILE_WALL, 95, 162, 97, 164)

    # ================================================================
    # 6. SECOND WYVERN PATH — ascending storm ridge
    # DS3: winding mountain path with cliff edges and wind-swept rocks
    # Section: x=2640,y=1540,w=980,h=660 -> tiles (165,96)-(226,137)
    # ================================================================
    # Ridge boundary walls (DS3: narrow ridge with cliffs on both sides)
    fill_tiles(chunk, TILE_WALL, 165, 96, 167, 120)      # West wall upper
    fill_tiles(chunk, TILE_WALL, 165, 130, 167, 137)     # West wall lower
    fill_tiles(chunk, TILE_WALL, 224, 96, 226, 115)      # East wall upper
    fill_tiles(chunk, TILE_WALL, 224, 125, 226, 137)     # East wall lower
    fill_tiles(chunk, TILE_WALL, 165, 96, 195, 98)       # North wall left
    fill_tiles(chunk, TILE_WALL, 210, 96, 226, 98)       # North wall right
    fill_tiles(chunk, TILE_WALL, 165, 135, 195, 137)     # South wall left
    fill_tiles(chunk, TILE_WALL, 205, 135, 226, 137)     # South wall right
    # Cliff edge stones (DS3: perilous drops along the ridge)
    fill_tiles(chunk, TILE_WALL, 171, 101, 173, 103)     # Cliff edge NW
    fill_tiles(chunk, TILE_WALL, 182, 106, 184, 108)     # Cliff edge center
    fill_tiles(chunk, TILE_WALL, 198, 100, 200, 102)     # Wind rock NE
    fill_tiles(chunk, TILE_WALL, 177, 113, 179, 115)     # Cliff edge mid
    fill_tiles(chunk, TILE_WALL, 193, 108, 195, 110)     # Wind rock center
    fill_tiles(chunk, TILE_WALL, 210, 115, 212, 117)     # Cliff edge E
    fill_tiles(chunk, TILE_WALL, 190, 125, 192, 127)     # South rock

    # ================================================================
    # 7. GREAT BELFRY — massive bell tower structure
    # DS3: great bell atop the tower, Havel Knight ambush, summoner
    # Section: x=3160,y=1080,w=760,h=560 -> tiles (197,67)-(245,102)
    # ================================================================
    # Tower boundary walls (DS3: massive stone bell tower)
    fill_tiles(chunk, TILE_WALL, 197, 67, 199, 95)       # West wall
    fill_tiles(chunk, TILE_WALL, 243, 67, 245, 90)       # East wall upper
    fill_tiles(chunk, TILE_WALL, 243, 97, 245, 102)      # East wall lower
    fill_tiles(chunk, TILE_WALL, 197, 67, 220, 69)       # North wall left
    fill_tiles(chunk, TILE_WALL, 230, 67, 245, 69)       # North wall right
    fill_tiles(chunk, TILE_WALL, 197, 100, 220, 102)     # South wall left
    fill_tiles(chunk, TILE_WALL, 230, 100, 245, 102)     # South wall right
    # Bell tower columns (DS3: stone columns supporting the bell)
    fill_tiles(chunk, TILE_WALL, 202, 71, 204, 75)       # NW column
    fill_tiles(chunk, TILE_WALL, 212, 73, 214, 77)       # N column
    fill_tiles(chunk, TILE_WALL, 223, 71, 225, 75)       # NE column
    fill_tiles(chunk, TILE_WALL, 207, 82, 209, 86)       # SW column
    fill_tiles(chunk, TILE_WALL, 233, 75, 235, 79)       # E column
    # Bell platform (DS3: raised platform with the great bell)
    fill_tiles(chunk, TILE_WALL, 215, 86, 230, 88)       # Bell support beam
    # Entrance arch pillars (DS3: stone arch at tower entrance)
    fill_tiles(chunk, TILE_WALL, 205, 93, 207, 97)       # SW arch pillar
    fill_tiles(chunk, TILE_WALL, 235, 93, 237, 97)       # SE arch pillar

    # ================================================================
    # 8. SERPENT-MAN SUMMONER BUILDING — interior summoner room
    # DS3: building with Serpent-Man Summoner casting spells
    # Section: x=2800,y=1780,w=600,h=400 -> tiles (175,111)-(212,136)
    # ================================================================
    # Building walls (DS3: stone interior room)
    fill_tiles(chunk, TILE_WALL, 175, 111, 177, 130)     # West wall
    fill_tiles(chunk, TILE_WALL, 210, 111, 212, 128)     # East wall upper
    fill_tiles(chunk, TILE_WALL, 210, 133, 212, 136)     # East wall lower
    fill_tiles(chunk, TILE_WALL, 175, 111, 195, 113)     # North wall left
    fill_tiles(chunk, TILE_WALL, 202, 111, 212, 113)     # North wall right
    fill_tiles(chunk, TILE_WALL, 175, 134, 195, 136)     # South wall left
    fill_tiles(chunk, TILE_WALL, 202, 134, 212, 136)     # South wall right
    # Summon circle (DS3: glowing summon circle on floor)
    fill_tiles(chunk, TILE_WALL, 190, 120, 195, 124)     # Summon altar
    # Stone pillars (DS3: interior support pillars)
    fill_tiles(chunk, TILE_WALL, 182, 117, 184, 120)     # NW pillar
    fill_tiles(chunk, TILE_WALL, 200, 117, 202, 120)     # NE pillar
    fill_tiles(chunk, TILE_WALL, 186, 128, 188, 131)     # SW pillar
    fill_tiles(chunk, TILE_WALL, 204, 128, 206, 131)     # SE pillar

    # ================================================================
    # 9. BELL LEVER CHAMBER — mechanism room to ring the bell
    # DS3: lever that rings the great bell, opens path to Nameless King
    # Section: x=3400,y=780,w=500,h=400 -> tiles (212,48)-(243,73)
    # ================================================================
    # Chamber walls (DS3: interior tower room)
    fill_tiles(chunk, TILE_WALL, 212, 48, 214, 68)       # West wall
    fill_tiles(chunk, TILE_WALL, 241, 48, 243, 68)       # East wall
    fill_tiles(chunk, TILE_WALL, 212, 48, 230, 50)       # North wall left
    fill_tiles(chunk, TILE_WALL, 235, 48, 243, 50)       # North wall right
    fill_tiles(chunk, TILE_WALL, 212, 71, 230, 73)       # South wall left
    fill_tiles(chunk, TILE_WALL, 235, 71, 243, 73)       # South wall right
    # Bell mechanism (DS3: stone lever and gears)
    fill_tiles(chunk, TILE_WALL, 225, 55, 229, 59)       # Lever mechanism
    fill_tiles(chunk, TILE_WALL, 232, 62, 234, 65)       # Gear housing
    # Tower interior supports (DS3: stone ceiling supports)
    fill_tiles(chunk, TILE_WALL, 218, 51, 220, 54)       # NW support
    fill_tiles(chunk, TILE_WALL, 237, 51, 239, 54)       # NE support
    fill_tiles(chunk, TILE_WALL, 220, 66, 222, 69)       # SW support

    # ================================================================
    # 10. HAVEL ROOFTOP ARENA — rooftop with fallen wyvern debris
    # DS3: Havel Knight on rooftop near fallen wyvern
    # Section: x=3700,y=1400,w=600,h=500 -> tiles (231,87)-(268,118)
    # ================================================================
    # Rooftop walls (DS3: parapet walls around rooftop)
    fill_tiles(chunk, TILE_WALL, 231, 87, 233, 110)      # West wall
    fill_tiles(chunk, TILE_WALL, 266, 87, 268, 108)      # East wall
    fill_tiles(chunk, TILE_WALL, 231, 87, 250, 89)       # North wall left
    fill_tiles(chunk, TILE_WALL, 258, 87, 268, 89)       # North wall right
    fill_tiles(chunk, TILE_WALL, 231, 116, 250, 118)     # South wall left
    fill_tiles(chunk, TILE_WALL, 258, 116, 268, 118)     # South wall right
    # Fallen wyvern debris (DS3: dead wyvern on rooftop)
    fill_tiles(chunk, TILE_WALL, 240, 95, 248, 100)      # Wyvern body
    fill_tiles(chunk, TILE_WALL, 250, 98, 254, 102)      # Wyvern wing
    # Stone parapets (DS3: crenellated rooftop walls)
    fill_tiles(chunk, TILE_WALL, 235, 90, 237, 92)       # NW parapet
    fill_tiles(chunk, TILE_WALL, 260, 92, 262, 94)       # NE parapet
    fill_tiles(chunk, TILE_WALL, 236, 112, 238, 114)     # SW parapet
    fill_tiles(chunk, TILE_WALL, 258, 110, 260, 112)     # SE parapet

    # ================================================================
    # 11. MAN-SERPENT GAUNTLET COURTYARD — ruined courtyard
    # DS3: open courtyard with serpent-man gauntlet and large statues
    # Section: x=3900,y=1800,w=600,h=500 -> tiles (243,112)-(281,143)
    # ================================================================
    # Courtyard walls (DS3: ruined courtyard walls)
    fill_tiles(chunk, TILE_WALL, 243, 112, 245, 135)     # West wall
    fill_tiles(chunk, TILE_WALL, 279, 112, 281, 133)     # East wall
    fill_tiles(chunk, TILE_WALL, 243, 112, 262, 114)     # North wall left
    fill_tiles(chunk, TILE_WALL, 270, 112, 281, 114)     # North wall right
    fill_tiles(chunk, TILE_WALL, 243, 141, 262, 143)     # South wall left
    fill_tiles(chunk, TILE_WALL, 270, 141, 281, 143)     # South wall right
    # Large serpent statues (DS3: massive stone serpent statues)
    fill_tiles(chunk, TILE_WALL, 250, 118, 254, 123)     # NW serpent statue
    fill_tiles(chunk, TILE_WALL, 268, 125, 272, 130)     # SE serpent statue
    # Stone debris (DS3: ruined masonry scattered around)
    fill_tiles(chunk, TILE_WALL, 258, 135, 261, 138)     # S debris pile
    fill_tiles(chunk, TILE_WALL, 248, 128, 250, 130)     # W debris

    # ================================================================
    # 12. PATH OF THE DRAGON ALTAR — stone altar at summit overlook
    # DS3: dragon stone altar where player uses Path of the Dragon gesture
    # Section: x=3600,y=1580,w=500,h=300 -> tiles (225,98)-(256,117)
    # ================================================================
    # Altar boundary walls (DS3: small plateau with stone altar)
    fill_tiles(chunk, TILE_WALL, 225, 98, 227, 112)      # West wall
    fill_tiles(chunk, TILE_WALL, 254, 98, 256, 112)      # East wall
    fill_tiles(chunk, TILE_WALL, 225, 98, 240, 100)      # North wall left
    fill_tiles(chunk, TILE_WALL, 246, 98, 256, 100)      # North wall right
    fill_tiles(chunk, TILE_WALL, 225, 115, 240, 117)     # South wall left
    fill_tiles(chunk, TILE_WALL, 246, 115, 256, 117)     # South wall right
    # Stone altar (DS3: dragon-crest stone altar)
    fill_tiles(chunk, TILE_WALL, 237, 105, 243, 110)     # Altar stone
    # Dragon skeleton (DS3: petrified dragon remains)
    fill_tiles(chunk, TILE_WALL, 230, 102, 232, 104)     # Dragon skull
    fill_tiles(chunk, TILE_WALL, 248, 110, 250, 112)     # Dragon tail fragment

    # ================================================================
    # 13. STORM CLOUD BRIDGE — floating bridge to Nameless King
    # DS3: storm-wreathed bridge connecting belfry to boss arena
    # Section: x=3600,y=400,w=600,h=400 -> tiles (225,25)-(262,50)
    # ================================================================
    # Bridge walls (DS3: narrow storm bridge with floating debris)
    fill_tiles(chunk, TILE_WALL, 225, 25, 227, 42)       # West wall
    fill_tiles(chunk, TILE_WALL, 260, 25, 262, 40)       # East wall upper
    fill_tiles(chunk, TILE_WALL, 260, 46, 262, 50)       # East wall lower
    fill_tiles(chunk, TILE_WALL, 225, 25, 245, 27)       # North wall left
    fill_tiles(chunk, TILE_WALL, 252, 25, 262, 27)       # North wall right
    fill_tiles(chunk, TILE_WALL, 225, 48, 245, 50)       # South wall left
    fill_tiles(chunk, TILE_WALL, 252, 48, 262, 50)       # South wall right
    # Floating debris (DS3: broken stone fragments floating in storm)
    fill_tiles(chunk, TILE_WALL, 232, 30, 234, 32)       # NW debris
    fill_tiles(chunk, TILE_WALL, 245, 35, 247, 37)       # Center debris
    fill_tiles(chunk, TILE_WALL, 255, 42, 257, 44)       # SE debris
    # Lightning strike marks (DS3: scorched stone from lightning)
    fill_tiles(chunk, TILE_WALL, 238, 40, 240, 42)
    fill_tiles(chunk, TILE_WALL, 250, 28, 252, 30)

    # ================================================================
    # 14. NAMELESS KING STORM ARENA — open peak boss arena
    # DS3: vast open arena on storm-wrapped peak, King rides storm drake
    # Section: x=3880,y=600,w=900,h=700 -> tiles (242,37)-(298,81)
    # ================================================================
    # Arena perimeter walls (DS3: open sky arena bounded by storm clouds)
    fill_tiles(chunk, TILE_WALL, 242, 37, 244, 70)       # West wall
    fill_tiles(chunk, TILE_WALL, 296, 37, 298, 65)       # East wall upper
    fill_tiles(chunk, TILE_WALL, 296, 75, 298, 81)       # East wall lower
    fill_tiles(chunk, TILE_WALL, 242, 37, 270, 39)       # North wall left
    fill_tiles(chunk, TILE_WALL, 280, 37, 298, 39)       # North wall right
    fill_tiles(chunk, TILE_WALL, 242, 79, 270, 81)       # South wall left
    fill_tiles(chunk, TILE_WALL, 280, 79, 298, 81)       # South wall right
    # Storm debris (DS3: wind-blasted stone fragments)
    fill_tiles(chunk, TILE_WALL, 251, 45, 253, 48)       # NW debris
    fill_tiles(chunk, TILE_WALL, 275, 53, 277, 56)       # Center debris
    fill_tiles(chunk, TILE_WALL, 258, 62, 260, 65)       # SW debris
    fill_tiles(chunk, TILE_WALL, 285, 52, 287, 55)       # NE debris
    fill_tiles(chunk, TILE_WALL, 255, 67, 257, 70)       # S debris
    fill_tiles(chunk, TILE_WALL, 295, 63, 297, 66)       # E debris
    # Boss arena open center (DS3: large open fighting area)
    fill_tiles(chunk, TILE_GROUND, 258, 45, 290, 72)     # Central arena floor

    # ================================================================
    # CONNECTION CORRIDORS — DS3 route paths connecting sections
    # ================================================================
    # Entry Cliff -> Man-Serpent Camp (north ascent)
    fill_tiles(chunk, TILE_GROUND, 50, 200, 90, 215)
    # Man-Serpent Camp -> Ancient Wyvern Arena (east)
    fill_tiles(chunk, TILE_GROUND, 110, 185, 140, 175)
    # Man-Serpent Camp -> Lightning Clutch Side-Path (west branch)
    fill_tiles(chunk, TILE_GROUND, 80, 165, 100, 158)
    # Ancient Wyvern Arena -> Dragonkin Mausoleum (north)
    fill_tiles(chunk, TILE_GROUND, 135, 150, 155, 165)
    # Dragonkin Mausoleum -> Serpent-Man Summoner Building (east)
    fill_tiles(chunk, TILE_GROUND, 165, 130, 185, 120)
    # Dragonkin Mausoleum -> Second Wyvern Path (east ascent)
    fill_tiles(chunk, TILE_GROUND, 165, 130, 180, 115)
    # Second Wyvern Path -> Serpent-Man Summoner Building (south)
    fill_tiles(chunk, TILE_GROUND, 180, 125, 200, 120)
    # Second Wyvern Path -> Great Belfry (north ascent)
    fill_tiles(chunk, TILE_GROUND, 210, 95, 225, 85)
    # Great Belfry -> Bell Lever Chamber (north climb)
    fill_tiles(chunk, TILE_GROUND, 220, 65, 235, 55)
    # Great Belfry -> Havel Rooftop Arena (east)
    fill_tiles(chunk, TILE_GROUND, 240, 85, 255, 95)
    # Great Belfry -> Path of the Dragon Altar (east)
    fill_tiles(chunk, TILE_GROUND, 240, 95, 250, 105)
    # Havel Rooftop -> Man-Serpent Gauntlet Courtyard (south)
    fill_tiles(chunk, TILE_GROUND, 250, 110, 265, 120)
    # Man-Serpent Gauntlet -> Path of the Dragon Altar (west)
    fill_tiles(chunk, TILE_GROUND, 245, 115, 255, 110)
    # Bell Lever Chamber -> Storm Cloud Bridge (west)
    fill_tiles(chunk, TILE_GROUND, 230, 45, 240, 40)
    # Storm Cloud Bridge -> Nameless King Storm Arena (east)
    fill_tiles(chunk, TILE_GROUND, 255, 35, 265, 45)
    # Ancient Wyvern boss area -> Dragonkin Mausoleum (DS3: wyvern boss area connects to mausoleum)
    carve_corridor(chunk, 112, 87, 145, 145, width=7)
    # GrandArchives fog gate (NW corner) -> Entry Cliff (DS3: path back to Grand Archives)
    carve_corridor(chunk, 31, 37, 54, 207, width=5)

    # ================================================================
    # FINALIZE — spawn, doc terrain, return
    # ================================================================
    spawn_px, spawn_py = 620, 3600  # Archdragon Peak bonfire (JSON doc)
    entities = []
    entities.append(make_entity("PlayerSpawn", spawn_px, spawn_py,
        [make_field("heal", "Bool", True)]))

    apply_doc_terrain(chunk, load_doc("ArchdragonPeak"))

    return finalize_map("ArchdragonPeak", chunk, entities, spawn_px, spawn_py)
