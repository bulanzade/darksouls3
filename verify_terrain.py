"""Verify all enemies land on walkable ground tiles in every area."""
import sys, os, importlib.util

spec = importlib.util.spec_from_file_location("generate_maps", "maps/generate_maps.py")
mod = importlib.util.module_from_spec(spec)

# Remove __main__ block from source
original_source = open("maps/generate_maps.py").read()
lines = original_source.split("\n")
filtered = []
skip = False
for line in lines:
    if '__name__' in line and '__main__' in line:
        skip = True
        continue
    if skip and line and not line[0].isspace() and not line.startswith('#'):
        skip = False
    if not skip:
        filtered.append(line)

exec("\n".join(filtered), mod.__dict__)

TILE_GROUND = 1
TILE_POISON = 4

area_funcs = [
    ("CemeteryOfAsh", mod.make_cemetery_of_ash),
    ("FirelinkShrine", mod.make_firelink_shrine),
    ("LothricWall", mod.make_lothric_wall),
    ("UndeadSettlement", mod.make_undead_settlement),
    ("RoadOfSacrifices", mod.make_road_of_sacrifices),
    ("FarronKeep", mod.make_farron_keep),
    ("CathedralDeep", mod.make_cathedral_deep),
    ("CatacombsOfCarthus", mod.make_catacombs_of_carthus),
    ("SmoulderingLake", mod.make_smouldering_lake),
    ("Irithyll", mod.make_irithyll),
    ("IrithyllDungeon", mod.make_irithyll_dungeon),
    ("ProfanedCapital", mod.make_profaned_capital),
    ("AnorLondo", mod.make_anor_londo),
    ("LothricCastle", mod.make_lothric_castle),
    ("GrandArchives", mod.make_grand_archives),
    ("KilnOfTheFirstFlame", mod.make_kiln_of_the_first_flame),
    ("ConsumedKingsGarden", mod.make_consumed_kings_garden),
    ("UntendedGraves", mod.make_untended_graves),
    ("ArchdragonPeak", mod.make_archdragon_peak),
]

total_enemies = 0
total_on_ground = 0
total_on_wall = 0
total_on_oob = 0

for name, func in area_funcs:
    area_name, chunk, entities = func()
    h = len(chunk)
    w = len(chunk[0]) if h > 0 else 0

    enemies_on_wall = 0
    enemies_on_ground = 0
    enemies_oob = 0

    for ent in entities:
        ident = ent.get("__identifier", "")
        if ident == "Enemy":
            total_enemies += 1
            grid = ent.get("__grid", [0, 0])
            tx, ty = grid[0], grid[1]
            if 0 <= ty < h and 0 <= tx < w:
                tile = chunk[ty][tx]
                if tile in (TILE_GROUND, TILE_POISON):
                    enemies_on_ground += 1
                    total_on_ground += 1
                else:
                    enemies_on_wall += 1
                    total_on_wall += 1
                    # Find the enemy kind
                    kind = "?"
                    for f in ent.get("fieldInstances", []):
                        if f.get("__identifier") == "kind":
                            kind = f.get("__value", "?")
                            break
                    print(f"  {name}: Enemy '{kind}' at tile ({tx},{ty}) on tile={tile} (WALL)")
            else:
                enemies_oob += 1
                total_on_oob += 1
                print(f"  {name}: Enemy at tile ({tx},{ty}) OOB (map {w}x{h})")

    enemy_count = enemies_on_ground + enemies_on_wall + enemies_oob
    status = "OK" if enemies_on_wall == 0 and enemies_oob == 0 else "ISSUES"
    print(f"{name}: {enemy_count} enemies, {enemies_on_ground} on ground, {enemies_on_wall} on wall, {enemies_oob} OOB [{status}]")

print(f"\n=== TOTAL: {total_enemies} enemies, {total_on_ground} on ground, {total_on_wall} on wall, {total_on_oob} OOB ===")
