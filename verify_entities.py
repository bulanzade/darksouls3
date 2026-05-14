"""Verify all NPCs and items land on walkable ground tiles in every area."""
import sys, os, importlib.util

spec = importlib.util.spec_from_file_location("generate_maps", "maps/generate_maps.py")
mod = importlib.util.module_from_spec(spec)

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
    mod.make_cemetery_of_ash, mod.make_firelink_shrine, mod.make_lothric_wall,
    mod.make_undead_settlement, mod.make_road_of_sacrifices, mod.make_farron_keep,
    mod.make_cathedral_deep, mod.make_catacombs_of_carthus, mod.make_smouldering_lake,
    mod.make_irithyll, mod.make_irithyll_dungeon, mod.make_profaned_capital,
    mod.make_anor_londo, mod.make_lothric_castle, mod.make_grand_archives,
    mod.make_kiln_of_the_first_flame, mod.make_consumed_kings_garden,
    mod.make_untended_graves, mod.make_archdragon_peak,
]

total_issues = 0

for func in area_funcs:
    area_name, chunk, entities = func()
    h = len(chunk)
    w = len(chunk[0]) if h > 0 else 0

    npcs_on_wall = []
    items_on_wall = []

    for ent in entities:
        ident = ent.get("__identifier", "")
        if ident in ("NPC", "Npc", "Item", "Chest", "Bonfire", "BossSpawn", "FogGate"):
            grid = ent.get("__grid", [0, 0])
            tx, ty = grid[0], grid[1]
            if not (0 <= ty < h and 0 <= tx < w):
                print(f"  {area_name}: {ident} at ({tx},{ty}) OOB (map {w}x{h})")
                total_issues += 1
            elif chunk[ty][tx] not in (TILE_GROUND, TILE_POISON):
                label = ""
                for f in ent.get("fieldInstances", []):
                    if f.get("__identifier") in ("kind", "name", "name_en"):
                        label = f.get("__value", "")
                        break
                if ident in ("NPC", "Npc"):
                    npcs_on_wall.append((tx, ty, label))
                elif ident == "Item":
                    items_on_wall.append((tx, ty, label))

    if npcs_on_wall:
        print(f"{area_name}: {len(npcs_on_wall)} NPCs on WALL tiles:")
        for tx, ty, label in npcs_on_wall:
            print(f"  NPC '{label}' at ({tx},{ty}) tile={chunk[ty][tx]}")
        total_issues += len(npcs_on_wall)
    if items_on_wall:
        print(f"{area_name}: {len(items_on_wall)} Items on WALL tiles:")
        for tx, ty, label in items_on_wall[:10]:
            print(f"  Item '{label}' at ({tx},{ty}) tile={chunk[ty][tx]}")
        if len(items_on_wall) > 10:
            print(f"  ... and {len(items_on_wall)-10} more")
        total_issues += len(items_on_wall)

    # Count entity types
    counts = {}
    for ent in entities:
        ident = ent.get("__identifier", "")
        counts[ident] = counts.get(ident, 0) + 1
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"{area_name}: {summary}")

print(f"\n=== Total issues: {total_issues} ===")
