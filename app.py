import ast
import os
import io
import numpy as np
import imageio.v2 as iio
from flask import Flask, render_template, abort, jsonify, request, send_file
from functools import lru_cache

# Load data
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'split_data')

def load_data(name):
    path = os.path.join(DATA_DIR, f'{name}.js')
    with open(path, 'r', encoding='utf-8') as f:
        return ast.literal_eval(f.read())

species = load_data('species')
areas = load_data('areas')
trainers = load_data('trainers')
items = load_data('items')

# Helper mapping from trainer name to ID for resolving trainers listed by name
TRAINER_NAME_TO_ID = {t['name']: t['ID'] for t in trainers.values()}

# Mapping from species key to its unique species ID for quick lookups
# This lets us resolve forms such as "Pikachu-Surfing" correctly.
NAME_TO_ID = {s.get('key', s['name']): s['ID'] for s in species.values()}

# Images live in the ``graphics`` directory but are processed on the fly. The
# ``/sprites`` route serves them with transparency applied.
app = Flask(
    __name__,
    static_url_path='/graphics',
    static_folder=os.path.join(BASE_DIR, 'graphics')
)


@lru_cache(maxsize=None)
def load_sprite(path: str) -> bytes:
    """Return PNG data for *path* with background color made transparent."""
    img = iio.imread(path)
    if img.ndim == 2:  # grayscale
        img = np.dstack([img, img, img, np.full_like(img, 255)])
    elif img.shape[2] == 3:
        img = np.dstack([img, np.full(img.shape[:2], 255, dtype=img.dtype)])
    bg = img[0, 0, :3]
    # Allow small variation in background color to account for GIF artifacts
    mask = np.all(np.abs(img[:, :, :3] - bg) <= 1, axis=-1)
    img[mask, 3] = 0
    buf = io.BytesIO()
    iio.imwrite(buf, img, format='png')
    return buf.getvalue()


@app.route('/sprites/<path:filename>')
def sprites(filename):
    path = os.path.join(BASE_DIR, 'graphics', filename)
    if not os.path.isfile(path):
        abort(404)
    return send_file(io.BytesIO(load_sprite(path)), mimetype='image/png')

@app.route('/')
def index():
    return render_template('index.html')

# Precompute a sorted list for pagination
MON_LIST = sorted(species.values(), key=lambda m: m['dexID'])

@app.route('/pokedex')
def pokedex():
    return render_template('pokedex.html')

@app.route('/api/pokemon')
def api_pokemon():
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 50))
    except ValueError:
        abort(400)
    slice_ = MON_LIST[offset:offset + limit]
    return jsonify(slice_)

@app.route('/pokemon/<int:species_id>')
def pokemon(species_id):
    """Display details for a single species/form by its unique ID."""
    mon = species.get(species_id)
    if not mon:
        abort(404)
    return render_template('pokemon.html', mon=mon)

@app.route('/areas')
def area_list():
    return render_template('areas.html', areas=areas)

@app.route('/areas/<int:idx>')
def area_detail(idx):
    if idx < 0 or idx >= len(areas):
        abort(404)
    area = areas[idx]
    def resolve_trainers(ids):
        resolved = []
        for tid in ids:
            trainer = None
            if isinstance(tid, int):
                trainer = trainers.get(tid)
            else:
                t_id = TRAINER_NAME_TO_ID.get(tid)
                if t_id is not None:
                    trainer = trainers.get(t_id)
            if not trainer:
                trainer = {'name': tid}
            resolved.append(trainer)
        return resolved
    trainer_groups = {slot: resolve_trainers(ids) for slot, ids in area.get('trainers', {}).items()}

    processed = {}
    for key, value in area.items():
        if key.startswith('wild-'):
            new_slots = {}
            for slot, entries in value.items():
                new_entries = []
                for entry in entries:
                    sid = NAME_TO_ID.get(entry[0])
                    new_entries.append({'name': entry[0], 'min': entry[1], 'max': entry[2], 'ID': sid})
                new_slots[slot] = new_entries
            processed[key] = new_slots
        else:
            processed[key] = value

    return render_template('area.html', area=processed, trainers=trainer_groups)

@app.route('/trainer/<int:tid>')
def trainer_detail(tid):
    t = trainers.get(tid)
    if not t:
        abort(404)
    party = []
    for mon in t.get('normal', []):
        sid = NAME_TO_ID.get(mon.get('species'))
        party.append({**mon, 'ID': sid})
    return render_template('trainer.html', trainer=t, party=party)

if __name__ == '__main__':
    app.run(debug=True)
