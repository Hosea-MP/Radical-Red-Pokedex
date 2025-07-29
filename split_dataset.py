import ast
import os
import json
import argparse


def remove_sprites(obj):
    """Recursively remove 'sprites' keys from dictionaries."""
    if isinstance(obj, dict):
        return {k: remove_sprites(v) for k, v in obj.items() if k != 'sprites'}
    if isinstance(obj, list):
        return [remove_sprites(v) for v in obj]
    return obj


def build_lookup_tables(data):
    move_map = {int(mid): m.get('name', mid) for mid, m in data.get('moves', {}).items()}
    ability_map = {}
    for aid, info in data.get('abilities', {}).items():
        if isinstance(info, dict):
            name = info.get('name') or (info.get('names') or [aid])[0]
        else:
            name = info
        ability_map[int(aid)] = name
    egg_map = {int(eid): name for eid, name in data.get('eggGroups', {}).items()}
    tm_lookup = data.get('tmMoves', {})
    tutor_lookup = data.get('tutorMoves', {})
    species_map = {int(sid): mon.get('name', sid) for sid, mon in data.get('species', {}).items()}
    return move_map, ability_map, egg_map, tm_lookup, tutor_lookup, species_map


def replace_ids(data):
    move_map, ability_map, egg_map, tm_lookup, tutor_lookup, species_map = build_lookup_tables(data)
    for mon in data.get('species', {}).values():
        if 'eggMoves' in mon:
            mon['eggMoves'] = [move_map.get(mid, mid) for mid in mon['eggMoves']]
        if 'tutorMoves' in mon:
            ids = [tutor_lookup.get(idx, 0) for idx in mon['tutorMoves']]
            mon['tutorMoves'] = [move_map.get(mid, mid) for mid in ids if mid in move_map]
        if 'tmMoves' in mon:
            ids = [tm_lookup.get(idx, 0) for idx in mon['tmMoves']]
            mon['tmMoves'] = [move_map.get(mid, mid) for mid in ids if mid in move_map]
        if 'levelupMoves' in mon:
            mon['levelupMoves'] = [[move_map.get(mid, mid), lvl] for mid, lvl in mon['levelupMoves']]
        if 'abilities' in mon:
            mon['abilities'] = [[ability_map.get(aid, aid), slot] for aid, slot in mon['abilities']]
        if 'eggGroup' in mon:
            mon['eggGroup'] = [egg_map.get(eid, eid) for eid in mon['eggGroup']]
        if 'evolutions' in mon:
            converted = []
            for evo in mon['evolutions']:
                if len(evo) >= 3:
                    evo = list(evo)
                    evo[2] = species_map.get(evo[2], evo[2])
                converted.append(evo)
            mon['evolutions'] = converted
    for trainer in data.get('trainers', {}).values():
        for mode in ('normal', 'hardcore'):
            if mode in trainer:
                for poke in trainer[mode]:
                    if 'ability' in poke:
                        poke['ability'] = ability_map.get(poke['ability'], poke['ability'])


def write_js(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(repr(obj))


def main():
    parser = argparse.ArgumentParser(description='Normalize and split dataset')
    parser.add_argument('input', nargs='?', default='parsed_data.js', help='Input dataset (default parsed_data.js)')
    parser.add_argument('-o', '--outdir', default='split_data', help='Output directory')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = ast.literal_eval(f.read())

    # remove sprites then replace id references
    data = remove_sprites(data)
    replace_ids(data)

    os.makedirs(args.outdir, exist_ok=True)

    pieces = ['species', 'moves', 'abilities', 'eggGroups', 'trainers', 'tmMoves', 'tutorMoves']
    index = {}
    for key in pieces:
        if key in data:
            path = os.path.join(args.outdir, f'{key}.js')
            write_js(path, data[key])
            index[key] = path

    with open(os.path.join(args.outdir, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)


if __name__ == '__main__':
    main()
