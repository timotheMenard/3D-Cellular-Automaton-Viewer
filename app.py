import os
from flask import Flask, jsonify, render_template, request
from grid import Grid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
    """API endpoint: save current grid state and colours to a text file."""
    data = request.json
    filename = data.get('filename', 'grid_state.txt')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")

    cellcolours = {}

    with open(filepath, 'w') as f:
        f.write(f"{grid.size} ")
        for x in grid.cells:
            for y in x:
                f.write("".join(str(cell.cell_type) for cell in y))

                for cell in y:
                    cellcolours[str(cell.cell_type)] = hex(cell.colour)

        f.write("".join(f' {cell_type} {colour}' for cell_type, colour in cellcolours.items()))

        f.write(f' {grid.predefined_update}')


    return jsonify({"message": "Grid saved successfully", "filename": filename + ".txt"})

@app.route('/load', methods=['POST'])
def load_grid():
    """API endpoint: load grid state from uploaded file and respond with its state."""
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    with open(file_path, 'r') as f:
        content = f.read().strip()

    # Get the size of the grid and the grid
    parts = content.split()
    size = int(parts[0])
    grid_data = parts[1]

    # Get the predefined_update
    predefined_update = int(parts[-1])
    
    # Get the colours
    colour_list = parts[2:-1]
    colour_dict = {0:0}
    for i in range(0, len(colour_list), 2):
        colour_dict[int(colour_list[i])] = int(colour_list[i+1], 16)

    initial_state = []
    index = 0
    for x in range(size):
        plane = []
        for y in range(size):
            row = [int(grid_data[index + z]) for z in range(size)]
            plane.append(row)
            index += size
        initial_state.append(plane)

    global grid
    grid = Grid(size, initial_state, colour_dict, predefined_update)
    new_state = [[[cell.celldict() for cell in z] for z in y] for y in grid.cells]
    return jsonify(new_state)

@app.route('/edit-rules', methods=['POST'])
def edit_rules():
    """API endpoint: update the automaton rules based on user input."""
    data = request.get_json()
    new_rules = data.get('rules')

    if new_rules:
        
        x, y, z = new_rules.split('/')
        stay_alive = list(map(int, x.split(',')))
        get_alive = list(map(int, y.split(',')))
        
        #global grid
        grid.edited_rules = [stay_alive, get_alive, z]

        return jsonify({"message": "Rules updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid rules format"}), 400


if __name__ == '__main__':
    app.run()
"""
# to test concurrency

if __name__ == '__main__':

    import time

    size = int(5)
    initial_state = [[[1 if (x + y + z) % 2 == 0 else 0 for z in range(size)] for y in range(size)] for x in range(size)]
    grid = Grid(size, initial_state, {0:0, 1:0xff0000})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'initial_state.txt')

    with open(file_path, 'r') as f:
        content = f.read().strip()

    # Get the size of the grid and the grid
    parts = content.split()
    size = int(parts[0])
    grid_data = parts[1]

    # Get the predefined_update
    predefined_update = int(parts[-1])

    # Get the colours
    colour_list = parts[2:-1]
    colour_dict = {0:0}
    for i in range(0, len(colour_list), 2):
        colour_dict[int(colour_list[i])] = int(colour_list[i+1], 16)

    initial_state = []
    index = 0
    for x in range(size):
        plane = []
        for y in range(size):
            row = [int(grid_data[index + z]) for z in range(size)]
            plane.append(row)
            index += size
        initial_state.append(plane)

    meanfull = []
    for y in range(10):
        grid = Grid(size, initial_state, colour_dict, predefined_update)

        meanel = []
        for x in range(10):
            start_time = time.time()
            grid.update()
            end_time = time.time()
            meanel.append(end_time - start_time)
        meanfull.append(meanel)
    
    meanfinal = []
    for x in meanfull:
        meanfinal.append(sum(x)/len(x))

    
    print(f"Update took {sum(meanfinal)/len(meanfinal):.4f} seconds")       
    """
