import ast
import os
from flask import Flask, render_template, abort

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

# Mapping from species name to its dex ID for quick lookups
NAME_TO_ID = {s['name']: s.get('dexID', s.get('ID')) for s in species.values()}

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

@app.route('/pokedex')
def pokedex():
    mons = sorted(species.values(), key=lambda m: m['dexID'])
    return render_template('pokedex.html', mons=mons)

@app.route('/pokemon/<int:dex_id>')
def pokemon(dex_id):
    mon = next((m for m in species.values() if m['dexID'] == dex_id), None)
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
        dex = NAME_TO_ID.get(mon.get('species'))
        party.append({**mon, 'dexID': dex})
    return render_template('trainer.html', trainer=t, party=party)

if __name__ == '__main__':
    app.run(debug=True)
