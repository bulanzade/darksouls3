#!/usr/bin/env python3
"""Verify generated LDtk terrain files against docs/maps metadata.

The game now supports per-map dimensions, so this verifier reads the generated
.ldtkl files directly instead of assuming a fixed 160x160 grid.
"""
import json
import os
from collections import deque

TILE_GROUND = 1
TILE_POISON = 4
TILE_SIZE = 16

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(PROJECT_DIR, "docs", "maps")
LEVELS_DIR = os.path.join(SCRIPT_DIR, "ds2d")


def canonical_map_id(raw):
    return {"IrithyllOfTheBorealValley": "Irithyll"}.get(raw, raw)


def load_docs():
    docs = {}
    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(DOCS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        docs[canonical_map_id(doc.get("id", ""))] = doc
    return docs


def layer(level, identifier):
    for item in level.get("layerInstances", []):
        if item.get("__identifier") == identifier:
            return item
    raise ValueError(f"missing layer {identifier}")


def terrain_grid(terrain):
    width = terrain["__cWid"]
    height = terrain["__cHei"]
    values = terrain.get("intGridCsv", [])
    if len(values) != width * height:
        raise ValueError(f"terrain CSV length {len(values)} != {width * height}")
    return width, height, [values[y * width:(y + 1) * width] for y in range(height)]


def walkable(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] in (TILE_GROUND, TILE_POISON)


def find_walkable_nearby(grid, px, py, radius=8):
    tx, ty = int(px) // TILE_SIZE, int(py) // TILE_SIZE
    for r in range(radius + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, y = tx + dx, ty + dy
                if walkable(grid, x, y):
                    return x, y
    return None


def reachable_from(grid, start):
    if start is None:
        return set()
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in seen and walkable(grid, nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))
    return seen


def entity_pos(entity):
    px = entity.get("px", [0, 0])
    return px[0], px[1]


def verify_level(path, docs):
    with open(path, encoding="utf-8") as f:
        level = json.load(f)
    map_id = level["identifier"]
    doc = docs.get(map_id)
    issues = []

    terrain = layer(level, "Terrain")
    entities_layer = layer(level, "Entities")
    width, height, grid = terrain_grid(terrain)

    if doc:
        expected_w = int(round(doc.get("map_size", {}).get("width", width * TILE_SIZE) / TILE_SIZE))
        expected_h = int(round(doc.get("map_size", {}).get("height", height * TILE_SIZE) / TILE_SIZE))
        if (width, height) != (expected_w, expected_h):
            issues.append(f"size {width}x{height} tiles != docs {expected_w}x{expected_h}")

    entities = entities_layer.get("entityInstances", [])
    spawn = next((entity_pos(e) for e in entities if e.get("__identifier") == "PlayerSpawn"), None)
    spawn_tile = find_walkable_nearby(grid, *spawn) if spawn else None
    if not spawn_tile:
        issues.append("PlayerSpawn is not near walkable terrain")
    reachable = reachable_from(grid, spawn_tile)

    checked_types = {"Bonfire", "BossSpawn", "FogGate", "Enemy", "Item", "Chest", "Npc"}
    checked = 0
    reachable_count = 0
    for entity in entities:
        if entity.get("__identifier") not in checked_types:
            continue
        checked += 1
        px, py = entity_pos(entity)
        if not (0 <= px <= level["pxWid"] and 0 <= py <= level["pxHei"]):
            issues.append(f"{entity['__identifier']} out of bounds at {px},{py}")
            continue
        tile = find_walkable_nearby(grid, px, py)
        if not tile:
            issues.append(f"{entity['__identifier']} at {px},{py} is not near walkable terrain")
        elif tile in reachable:
            reachable_count += 1
        else:
            issues.append(f"{entity['__identifier']} at {px},{py} is not reachable from spawn")

    ground = sum(1 for row in grid for tile in row if tile in (TILE_GROUND, TILE_POISON))
    pct = ground / (width * height) * 100
    print(f"{map_id:24s} {width:4d}x{height:<4d} walkable={pct:5.1f}% entities={reachable_count}/{checked}")
    for issue in issues:
        print(f"  - {issue}")
    return len(issues)


def main():
    docs = load_docs()
    total = 0
    for filename in sorted(os.listdir(LEVELS_DIR)):
        if not filename.endswith(".ldtkl"):
            continue
        total += verify_level(os.path.join(LEVELS_DIR, filename), docs)
    print(f"TOTAL ISSUES: {total}")
    raise SystemExit(1 if total else 0)


if __name__ == "__main__":
    main()
