"""Extract enemy type counts per area from the Python code."""
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

area_funcs = [
    mod.make_cemetery_of_ash, mod.make_firelink_shrine, mod.make_lothric_wall,
    mod.make_undead_settlement, mod.make_road_of_sacrifices, mod.make_farron_keep,
    mod.make_cathedral_deep, mod.make_catacombs_of_carthus, mod.make_smouldering_lake,
    mod.make_irithyll, mod.make_irithyll_dungeon, mod.make_profaned_capital,
    mod.make_anor_londo, mod.make_lothric_castle, mod.make_grand_archives,
    mod.make_kiln_of_the_first_flame, mod.make_consumed_kings_garden,
    mod.make_untended_graves, mod.make_archdragon_peak,
]

for func in area_funcs:
    area_name, chunk, entities = func()
    enemy_kinds = {}
    for ent in entities:
        if ent.get("__identifier") == "Enemy":
            kind = "?"
            for f in ent.get("fieldInstances", []):
                if f.get("__identifier") == "kind":
                    kind = f.get("__value", "?")
                    break
            enemy_kinds[kind] = enemy_kinds.get(kind, 0) + 1

    sorted_kinds = sorted(enemy_kinds.items(), key=lambda x: -x[1])
    kind_str = ", ".join(f"{k}({v})" for k, v in sorted_kinds)
    total = sum(enemy_kinds.values())
    print(f"{area_name}: {total} enemies — {kind_str}")
