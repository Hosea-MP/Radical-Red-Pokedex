import ast
import os
from flask import Flask, render_template, abort, jsonify, request

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

# Mapping from species key to its unique species ID for quick lookups
# This lets us resolve forms such as "Pikachu-Surfing" correctly.
NAME_TO_ID = {s.get('key', s['name']): s['ID'] for s in species.values()}

# Serve image assets from the graphics directory so templates can reference
# sprites directly via ``/graphics/...`` URLs.
app = Flask(
    __name__,
    static_url_path='/graphics',
    static_folder=os.path.join(BASE_DIR, 'graphics')
)

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

<<<<<<< HEAD
@app.route('/pokemon/<int:dex_id>')
def pokemon(dex_id):
    mon = next((m for m in species.values() if m['dexID'] == dex_id), None)
=======
@app.route('/pokemon/<int:species_id>')
def pokemon(species_id):
    """Display details for a single species/form by its unique ID."""
    mon = species.get(species_id)
>>>>>>> 2m0rit-codex/create-pokedex-viewer-web-application
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
        return [trainers.get(tid, {'name': tid}) for tid in ids]
    trainer_groups = {slot: resolve_trainers(ids) for slot, ids in area.get('trainers', {}).items()}
    return render_template('area.html', area=area, trainers=trainer_groups)

@app.route('/trainer/<int:tid>')
def trainer_detail(tid):
    t = trainers.get(tid)
    if not t:
        abort(404)
    party = []
    for mon in t.get('normal', []):
<<<<<<< HEAD
        dex = NAME_TO_ID.get(mon.get('species'))
        party.append({**mon, 'dexID': dex})
=======
        sid = NAME_TO_ID.get(mon.get('species'))
        party.append({**mon, 'ID': sid})
>>>>>>> 2m0rit-codex/create-pokedex-viewer-web-application
    return render_template('trainer.html', trainer=t, party=party)

if __name__ == '__main__':
    app.run(debug=True)
