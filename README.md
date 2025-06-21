## 3D Cellular Automaton Viewer

This project was completed as part of a university course.

This project is a browser-based 3D cellular automaton visualiser built with Flask for the backend and Three.js for the frontend. It allows users to configure and visualise the evolution of cellular automata on a three-dimensional grid, with support for custom rules, tree growth simulations, and save/load functionality.

### Features

- **3D Rendering**: Uses Three.js to render a cube grid in 3D, with camera rotation around the scene.
- **Configurable Grid**: Select grid size at startup and adjust simulation speed.
- **Custom Rules**: Edit Conway's Game of Life rules (stay alive and get alive counts, Moore or Von Neumann neighborhood).
- **Tree Growth Simulation**: Predefined update rules simulate simple tree growth patterns (trunk, branches, leaves).
- **Save & Load**: Save grid state to file and load from saved files.
- **Parallel Updates**: Uses multi-threading for grid updates in larger simulations.
- **Automated Tests**: Unit tests for core `Cell` and `Grid` logic using Python's `unittest` framework.

### Directory Structure

```
├── app.py               # Flask application handling routes and API
├── grid.py              # Grid class managing cell states and parallel updates
├── cell.py              # Cell class defining cell behaviour and update rules
├── Project_Demo.mp4     # Small demo
├── static/
│   ├── css/styles.css   # Stylesheet for the simulation interface
│   └── js/script.js     # Frontend logic using Three.js and UI controls
├── templates/           # HTML templates
│   └── index.html       # Main HTML page
├── uploads/             # Directory for saved grid files
└── README.md            # Project documentation
```

### Usage

1. **Start the Flask server**:

   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`.

3. **Configure the simulation**:
   - Enter the desired grid size and press `Enter` to initialise.
   - Use **Play/Stop** to start or pause the simulation.
   - Adjust the **Speed** slider to change the interval between generations.
   - Click **Save** to download the current grid state, or **Load** to upload a previously saved state.
   - Click **Edit Rules** to customise survival and birth conditions.

### Demo

There is also a small video demo showing the growth of 3 trees (`Project_Demo.mp4`).

