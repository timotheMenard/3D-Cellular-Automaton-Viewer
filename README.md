## 3D Cellular Automaton Viewer

This project was completed as part of a university course.

This project is a browser-based 3D cellular automaton visualiser built with Flask for the backend and Three.js for the frontend. It allows users to configure and visualise the evolution of cellular automata on a three-dimensional grid, with support for custom rules, simple tree growth simulations, and save/load functionality. The entire application can be containerised using Docker for easy deployment and consistent environment setup.

### Features

- **3D Rendering**: Uses Three.js to render a cube grid in 3D, with camera rotation around the scene.
- **Configurable Grid**: Select grid size at startup and adjust simulation speed.
- **Custom Rules**: Edit Conway's Game of Life rules (stay alive and get alive counts, Moore or Von Neumann neighborhood).
- **Tree Growth Simulation**: Predefined update rules simulate simple tree growth patterns (trunk, branches, leaves).
- **Save & Load**: Save grid state to file and load from saved files.
- **Parallel Updates**: Uses multi-threading for grid updates in larger simulations.
- **Automated Tests**: Unit tests for core `Cell` and `Grid` logic using Python's `unittest` framework.
- **MongoDB Integration**: Persistent storage of grid states with MongoDB.
- **Docker Support**: Fully containerised application with Docker Compose.

### Directory Structure

```
├── docker/
│   ├── docker-compose.yml   # Docker Compose configuration
│   ├── init-mongo.js        # MongoDB initialisation script
│   └── Dockerfile           # Docker image configuration
├── static/
│   ├── css/styles.css       # Stylesheet for the simulation interface
│   └── js/script.js         # Frontend logic using Three.js and UI controls
├── templates/               # HTML templates
│   └── index.html           # Main HTML page
├── app.py                   # Flask application handling routes and API
├── grid.py                  # Grid class managing cell states and updates
├── cell.py                  # Cell class defining cell behaviour and rules
├── trees.json               # Predefined tree growth configuration
├── requirements.txt         # Python dependencies
├── Project_Demo.mp4         # Small demo
└── README.md                # Project documentation
```

## Installation & Setup

### Prerequisites

- Docker and Docker Compose installed on your system
- Port 5000 (Flask app), 27017 (MongoDB), and 8081 (Mongo Express) available

### Running with Docker

1. **Clone the repository and start the application**:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build -d
   ```

2. **Access the application**:
   - Main application: `http://localhost:5000`
   - MongoDB Express (database viewer): `http://localhost:8081`

3. **Stop the application**:
   ```bash
   docker-compose -f docker/docker-compose.yml down -v
   ```

## Usage

1. **Initialise Grid**:
   - Enter the desired grid size and click "Initialise Grid"
   - The default creates a checkerboard pattern

2. **Control Simulation**:
   - **Next**: Advance one generation
   - **Play/Stop**: Start or pause automatic progression
   - **Speed Slider**: Adjust the interval between generations (0.25s - 2s)

3. **Edit Rules**:
   - Click "Edit" to customise cellular automaton rules
   - Format: `X/Y/Z` where:
     - X = numbers to stay alive (e.g., "2,3")
     - Y = numbers to get alive (e.g., "3")
     - Z = neighborhood type (M = Moore, N = Von Neumann)
   - Example: `2,3/3/M` (Conway's Game of Life in 3D)

4. **Save/Load States**:
   - **Save**: Save current grid state with a custom name
   - **Load**: Load a previously saved state (try "trees" for the pre-loaded tree simulation)

5. **Tree Growth Simulation**:
   - Load the "trees" configuration to see predefined tree growth patterns
   - Features realistic growth with trunk, branches, and leaves
   - Uses special cell types with brown (trunk) and green (leaves) colouring

## API Endpoints

- `GET /` - Main application page
- `POST /initial_state` - Generate initial grid state
- `POST /next` - Advance to next generation
- `POST /save` - Save current grid state
- `POST /load` - Load saved grid state
- `POST /edit-rules` - Update automaton rules
- `GET /test-db` - Test MongoDB connection

## Demo

A video demonstration (`Project_Demo.mp4`) is included showing the growth of 3 trees using the cellular automaton rules. You can try this yourself when the application is running by clicking "Load" and entering "trees" as the filename.

## Testing

Run unit tests:
```bash
python -m unittest cell.py
python -m unittest grid.py
```

## Issues

- Large grid sizes (>30) experience performance degradation

