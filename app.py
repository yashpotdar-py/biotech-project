import json
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "biotech"


def load_docking_data():
    with open('db/docking_db.json', 'r') as f:
        return json.load(f)


def interpret_docking_score(score):
    if score < -9.0:
        return "✅ Strong binding affinity (likely good candidate for further study)", "success"
    elif -9.0 <= score <= -7.0:
        return "🟡 Moderate binding affinity (may need optimization)", "warning"
    elif -7.0 < score <= -5.0:
        return "⚠ Weak binding affinity (unlikely to be effective)", "secondary"
    else:
        return "❌ Poor binding affinity (not suitable for drug development)", "danger"


def get_docking_data(protein_id, ligand_name=None):
    try:
        data = load_docking_data()
        results = []

        for item in data['docking_results']:
            if item['protein_id'] == protein_id:
                if ligand_name is None or ligand_name.lower() in item['ligand_name'].lower():
                    score = item['docking_score']
                    interpretation, status = interpret_docking_score(score)
                    results.append({
                        'protein_id': item['protein_id'],
                        'ligand_id': item['ligand_id'],
                        'ligand_name': item['ligand_name'],
                        'docking_score': score,
                        'interpretation': interpretation,
                        'status': status,
                        'binding_site': item['binding_site'],
                        'rmsd': item['rmsd']
                    })

        return results
    except Exception as e:
        flash(f"Error loading docking data: {e}", "danger")
        return []


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/docking', methods=['GET', 'POST'])
def docking():
    return render_template('docking.html')


@app.route('/docking-results', methods=['POST'])
def results():
    protein_name = request.form.get('protein_name')
    ligand_name = request.form.get('ligand_name')

    if not protein_name:
        flash('Please enter a protein name', 'danger')
        return redirect(url_for('docking'))

    docking_results = get_docking_data(protein_name, ligand_name)

    if not docking_results:
        flash(
            f'No results found for protein {protein_name} and ligand {ligand_name}', 'warning')
        return redirect(url_for('docking'))

    return render_template('docking-results.html',
                           results=docking_results,
                           protein_name=protein_name,
                           ligand_name=ligand_name)


@app.route('/modelling', methods=['GET', 'POST'])
def modeling():
    # TODO: Implement modeling functionality
    return render_template('modeling.html')


@app.route('/modelling-results', methods=['POST'])
def modeling_results():
    # TODO: Implement modeling results functionality
    return render_template('modeling-results.html')


if __name__ == '__main__':
    app.run(debug=True)
