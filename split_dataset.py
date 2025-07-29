"""Normalize and split the dataset into individual files.

This script removes sprite data and converts numeric ID references to
human-readable forms. Species IDs are replaced with their key value
where available so trainers and areas reference Pokémon by key.
Trainer and item references in areas are also replaced with their
corresponding names. Raid dens use names for their Pokémon and reward
items as well.
Each top-level section of the input file is then written to its own
JavaScript file.
An index.json mapping keys to file paths is generated for convenience.
"""

import ast
import os
import json
import argparse
import re


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
    species_map = {
        int(sid): mon.get('key') or mon.get('name', sid)
        for sid, mon in data.get('species', {}).items()
    }
    trainer_map = {
        int(tid): t.get('name', tid)
        for tid, t in data.get('trainers', {}).items()
    }
    type_map = {int(tid): t.get('name', tid) for tid, t in data.get('types', {}).items()}
    item_map = {int(iid): item.get('name', iid) for iid, item in data.get('items', {}).items()}
    nature_map = {int(nid): name for nid, name in data.get('natures', {}).items()}
    return (
        move_map,
        ability_map,
        egg_map,
        tm_lookup,
        tutor_lookup,
        species_map,
        trainer_map,
        type_map,
        item_map,
        nature_map,
    )


def replace_ids(data):
    (
        move_map,
        ability_map,
        egg_map,
        tm_lookup,
        tutor_lookup,
        species_map,
        trainer_map,
        type_map,
        item_map,
        nature_map,
    ) = build_lookup_tables(data)
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
        if 'type' in mon:
            mon['type'] = [type_map.get(t, t) for t in mon['type']]
        if 'items' in mon:
            mon['items'] = [item_map.get(i, i) for i in mon['items']]
        if 'ancestor' in mon and mon['ancestor']:
            mon['ancestor'] = species_map.get(mon['ancestor'], mon['ancestor'])
        if 'evolutions' in mon:
            converted = []
            for evo in mon['evolutions']:
                evo = list(evo)
                if len(evo) >= 3:
                    evo[2] = species_map.get(evo[2], evo[2])
                method = evo[0]
                if method == 7:
                    evo[1] = item_map.get(evo[1], evo[1])
                elif method == 17:
                    evo[1] = type_map.get(evo[1], evo[1])
                elif method == 18 and len(evo) > 3:
                    evo[3] = type_map.get(evo[3], evo[3])
                elif method == 26:
                    evo[1] = move_map.get(evo[1], evo[1])
                elif method == 27:
                    evo[1] = species_map.get(evo[1], evo[1])
                elif method == 254:
                    if len(evo) > 3 and evo[3] == 2:
                        evo[1] = move_map.get(evo[1], evo[1])
                    else:
                        evo[1] = item_map.get(evo[1], evo[1])
                converted.append(evo)
            mon['evolutions'] = converted

    for move in data.get('moves', {}).values():
        if 'type' in move:
            move['type'] = type_map.get(move['type'], move['type'])
    for trainer in data.get('trainers', {}).values():
        for mode in ('normal', 'hardcore'):
            if mode in trainer:
                for poke in trainer[mode]:
                    if 'ability' in poke:
                        poke['ability'] = ability_map.get(poke['ability'], poke['ability'])
                    if 'species' in poke:
                        poke['species'] = species_map.get(poke['species'], poke['species'])
                    if 'nature' in poke:
                        poke['nature'] = nature_map.get(poke['nature'], poke['nature'])
                    if 'moves' in poke:
                        poke['moves'] = [move_map.get(mid, mid) for mid in poke['moves']]

    for area in data.get('areas', []):
        for field in (
            'wild-day',
            'wild-night',
            'wild-surf',
            'wild-oldRod',
            'wild-goodRod',
            'wild-superRod',
            'wild-smash',
        ):
            if field in area:
                for slot, encounters in area[field].items():
                    for entry in encounters:
                        if entry:
                            entry[0] = species_map.get(entry[0], entry[0])

        for fixed in (
            'fixed-gift',
            'fixed-overworld',
            'fixed-roaming',
            'fixed-trade',
        ):
            if fixed in area:
                for slot, mons in area[fixed].items():
                    area[fixed][slot] = [species_map.get(mid, mid) for mid in mons]

        if 'trainers' in area:
            for slot, ids in area['trainers'].items():
                area['trainers'][slot] = [trainer_map.get(tid, tid) for tid in ids]

        for key in list(area.keys()):
            if key.startswith('item-'):
                for slot, items in area[key].items():
                    area[key][slot] = [item_map.get(iid, iid) for iid in items]
            elif re.fullmatch(r"raid\d+", key):
                for slot, entries in area[key].items():
                    converted = []
                    for mon_id, rewards in entries:
                        mon_name = species_map.get(mon_id, mon_id)
                        reward_names = [item_map.get(rid, rid) for rid in rewards]
                        converted.append([mon_name, reward_names])
                    area[key][slot] = converted

    dawn_name = item_map.get(101, 'Dawn Stone')
    for mid, template in data.get('evolutions', {}).items():
        template = template.replace("items[evo[1]].name", "evo[1]")
        template = template.replace("moves[evo[1]].name", "evo[1]")
        template = template.replace("types[evo[1]].name", "evo[1]")
        template = template.replace("types[evo[3]].name", "evo[3]")
        template = template.replace("species[evo[1]].name", "evo[1]")
        template = template.replace("'move ' + moves[evo[1]].name", "'move ' + evo[1]")
        template = template.replace("evo[1] !== 101", f"evo[1] !== '{dawn_name}'")
        data['evolutions'][mid] = template


def write_js(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(repr(obj))


def main():
    parser = argparse.ArgumentParser(description='Normalize and split dataset')
    parser.add_argument('input', nargs='?', default='data.js', help='Input dataset (default data.js)')
    parser.add_argument('-o', '--outdir', default='split_data', help='Output directory')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = ast.literal_eval(f.read())

    # remove sprites then replace id references
    data = remove_sprites(data)
    replace_ids(data)

    os.makedirs(args.outdir, exist_ok=True)

    # gather all top level keys so we emit every section
    pieces = sorted(data.keys())
    index = {}
    for key in pieces:
        path = os.path.join(args.outdir, f'{key}.js')
        write_js(path, data[key])
        index[key] = path

    with open(os.path.join(args.outdir, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)


if __name__ == '__main__':
    main()