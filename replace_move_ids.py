import ast
import sys

INPUT = sys.argv[1] if len(sys.argv) > 1 else 'parsed_data.js'
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else INPUT

with open(INPUT, 'r', encoding='utf-8') as f:
    data = ast.literal_eval(f.read())

# Map of move ID -> move name
move_map = {int(mid): m.get('name', mid) for mid, m in data.get('moves', {}).items()}

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

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(repr(data))
