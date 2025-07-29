import ast
import sys

INPUT = sys.argv[1] if len(sys.argv) > 1 else 'parsed_data.js'
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else INPUT

with open(INPUT, 'r', encoding='utf-8') as f:
    data = ast.literal_eval(f.read())

# Map of move ID -> move name
move_map = {int(mid): m.get('name', mid) for mid, m in data.get('moves', {}).items()}

# Maps for abilities and egg groups
ability_map = {}
for aid, info in data.get('abilities', {}).items():
    if isinstance(info, dict):
        name = info.get('name') or (info.get('names') or [aid])[0]
    else:
        name = info
    ability_map[int(aid)] = name

egg_map = {int(eid): name for eid, name in data.get('eggGroups', {}).items()}

# Lookup tables for tutor and TM move indices to actual move IDs
tutor_lookup = data.get('tutorMoves', {})
tm_lookup = data.get('tmMoves', {})

for mon in data.get('species', {}).values():
    if 'eggMoves' in mon:
        mon['eggMoves'] = [move_map.get(mid, mid) for mid in mon['eggMoves']]

    if 'tutorMoves' in mon:
        ids = [tutor_lookup.get(idx, 0) for idx in mon['tutorMoves']]
        mon['tutorMoves'] = [move_map[mid] for mid in ids if mid in move_map]

    if 'tmMoves' in mon:
        ids = [tm_lookup.get(idx, 0) for idx in mon['tmMoves']]
        mon['tmMoves'] = [move_map[mid] for mid in ids if mid in move_map]

    if 'levelupMoves' in mon:
        mon['levelupMoves'] = [[move_map.get(mid, mid), lvl] for mid, lvl in mon['levelupMoves']]

    if 'abilities' in mon:
        mon['abilities'] = [[ability_map.get(aid, aid), slot] for aid, slot in mon['abilities']]

    if 'eggGroup' in mon:
        mon['eggGroup'] = [egg_map.get(eid, eid) for eid in mon['eggGroup']]

# Update trainer Pokemon abilities
for trainer in data.get('trainers', {}).values():
    for mode in ('normal', 'hardcore'):
        if mode in trainer:
            for poke in trainer[mode]:
                if 'ability' in poke:
                    poke['ability'] = ability_map.get(poke['ability'], poke['ability'])

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(repr(data))
