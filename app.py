import os
from flask import Flask, jsonify, render_template, request
from grid import Grid
from pymongo import MongoClient

app = Flask(__name__)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/')
client = MongoClient(mongo_uri)
db = client['cellular_automaton']
grid_collection = db['grids']

n = 5
grid = None

# Helper to initialise a new Grid with a checkerboard pattern
def initialise_grid(sizestr):
    size = int(sizestr)
    global grid
    initial_state = [[[1 if (x + y + z) % 2 == 0 else 0 for z in range(size)] for y in range(size)] for x in range(size)]
    grid = Grid(size, initial_state, {0:0, 1:0xff0000})
    return [[[cell.celldict() for cell in z] for z in y] for y in grid.cells]


@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html')


@app.route('/initial_state', methods=['POST'])
def get_initial_state():
    """API endpoint: generate and return the initial grid state."""
    size = request.json.get('size', n)
    initial_state = initialise_grid(size)
    return jsonify(initial_state)


@app.route('/next', methods=['POST'])
def next_step():
    """API endpoint: advance grid to next generation and return updated state."""
    grid.update()
    new_state = [[[cell.celldict() for cell in z] for z in y] for y in grid.cells]
    return jsonify(new_state)


@app.route('/save', methods=['POST'])
def save_grid():
    """API endpoint: saves the current grid state into the MongoDB collection, inserting a new document
    or replacing an existing one by name."""
    data = request.get_json()
    filename = data.get('filename', 'grid_state')

    # Build a document
    doc = {
        'name': filename,
        'size': grid.size,
        'cells': [[[cell.cell_type for cell in z] for z in y] for y in grid.cells],
        'colours': {str(ct): hex(col) for ct, col in grid.colours.items()},
        'predefined_update': grid.predefined_update
    }

    # Upsert by name
    result = grid_collection.replace_one(
        {'name': filename},
        doc,
        upsert=True
    )

    return jsonify({"message": f"Grid '{filename}' saved.", "id": str(result.upserted_id or filename)})


@app.route('/load', methods=['POST'])
def load_grid():
    """API endpoint: load a saved grid state from MongoDB and reinitialise the global Grid object."""
    try:

        filename = request.get_json().get('filename')

        if not filename:
            return jsonify({"error": "No filename provided."}), 400

        doc = grid_collection.find_one({'name': filename})
        if not doc:
            return jsonify({"error": f"No saved grid found with name: {filename}"}), 404

         # Makes sure size is an integer
        size = int(doc['size'])
        
        # Convert state from floats to integers
        state = []
        for x_plane in doc['cells']:
            plane = []
            for y_row in x_plane:
                row = []
                for z_val in y_row:
                    # Convert float to int
                    row.append(int(z_val))
                plane.append(row)
            state.append(plane)
        
        # Handle colours - makes them integers
        colours = {}
        for k, v in doc['colours'].items():
            colours[int(k)] = int(v, 16) if v else 0
        
        # Makes sure that there is a colour for the empty cell
        if 0 not in colours:
            colours[0] = 0
        
        # Makes sure that predefined_update is an integer
        predefined_update = int(doc.get('predefined_update', 0))

        # Reinitialise the Grid object
        global grid
        grid = Grid(size, state, colours, predefined_update)

        new_state = [[[cell.celldict() for cell in z] for z in y] for y in grid.cells]
        return jsonify(new_state)
    
    except Exception as e:
        print(f"Error in load_grid: {str(e)}")
        return jsonify({"error": f"Failed to load grid: {str(e)}"}), 500


@app.route('/edit-rules', methods=['POST'])
def edit_rules():
    """API endpoint: update the automaton rules based on user input."""
    data = request.get_json()
    new_rules = data.get('rules')

    if new_rules:
        
        # Updates the rules
        x, y, z = new_rules.split('/')
        stay_alive = list(map(int, x.split(',')))
        get_alive = list(map(int, y.split(',')))
        
        #global grid
        grid.edited_rules = [stay_alive, get_alive, z]

        return jsonify({"message": "Rules updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid rules format"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)