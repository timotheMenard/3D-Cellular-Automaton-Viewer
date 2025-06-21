let intervalId;
let intervalTime = 1000; // Default interval time in milliseconds
let scene, camera, renderer;
let cubeGrid = [];
let gridSize;
let angle;
let radius;

// Initialise grid size, fetch initial state, and set up Three.js scene
function initialiseGrid() {
    gridSize = parseInt(document.getElementById('grid-size').value);
    fetchInitialState();
    initialiseThreeJS();
    radius = gridSize * 2; // Radius for the camera's circular path
    angle = 0; 
}

// Set up Three.js renderer, scene, and camera
function initialiseThreeJS() {
    const gridContainer = document.getElementById('grid-container');
    gridContainer.innerHTML = '';

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({antialias : true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    gridContainer.appendChild(renderer.domElement);
    
    camera.position.set(gridSize * 1.5, gridSize * 1.5, gridSize * 1.5);
    camera.lookAt(new THREE.Vector3(((gridSize-1) / 2), ((gridSize-1) / 2), ((gridSize-1) / 2)));
}

// Updates the camera position depending on the grid size
function updateCameraPosition() {
    camera.position.set(gridSize * 1.5, gridSize * 1.5, gridSize * 1.5);
    camera.lookAt(new THREE.Vector3(((gridSize-1) / 2), ((gridSize-1) / 2), ((gridSize-1) / 2)));
}

// Create cubes in 3D based on the cell state array
function createGrid(state) {

    cubeGrid = state.map((plane, x) => 
        plane.map((row, y) => 
            row.map((cell, z) => {
                if (cell.cell_type > 0) {
                    // Placing the cubes on the scene
                    const geometry = new THREE.BoxGeometry(1, 1, 1);
                    const material = new THREE.MeshBasicMaterial({ color: cell.colour });
                    const cube = new THREE.Mesh(geometry, material);
                    cube.position.set(x, y, z);
                    scene.add(cube);

                    // Adding borders to the cube
                    const edges = new THREE.EdgesGeometry(geometry);
                    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000 }));
                    line.position.set(x, y, z);
                    scene.add(line);

                    return cube;
                }
                return null;
            })
        )
    );


    animate();
}


// Renderes scene and camera and updates the camera's position
function animate() {

    // Update the camera's position in a circular path around the grid
    camera.position.x = radius * (gridSize*.15) * Math.cos(angle) + ((gridSize-1) / 2);
    camera.position.z = radius * (gridSize*.15) * Math.sin(angle) + ((gridSize-1) / 2);

    // Keep the camera's y position fixed
    camera.position.y = gridSize / 2;

    // Increment the angle to rotate the camera around the grid
    angle = 0.0001 * performance.now();

    // Ensure the camera is always looking at the center of the grid
    camera.lookAt(new THREE.Vector3(((gridSize-1) / 2),  ((gridSize-1) / 2), ((gridSize-1) / 2)));

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

// Fetch the initial grid state from the server via POST
async function fetchInitialState() {
    try {
        const response = await fetch('/initial_state', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ size: gridSize })
        });
        const initialState = await response.json();
        createGrid(initialState);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Advance the automaton by one generation
async function next() {
    try {
        const response = await fetch('/next', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ size: gridSize })
        });
        const newState = await response.json();
        scene.clear();
        createGrid(newState);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Play or stop the automatic progression
function togglePlay() {
    const playStopButton = document.getElementById('play-stop-button');
    if (playStopButton.textContent === 'Play') {
        playStopButton.textContent = 'Stop';
        intervalId = setInterval(next, intervalTime);
    } else {
        playStopButton.textContent = 'Play';
        clearInterval(intervalId);
    }
}

// Update simulation speed based on slider input
function updateSpeed(value) {
    value = 2.25 - value;
    intervalTime = value * 1000;
    document.getElementById('speed-value').textContent = value + 's';
    const playStopButton = document.getElementById('play-stop-button');
    if (intervalId && playStopButton.textContent === 'Stop') {
        clearInterval(intervalId);
        intervalId = setInterval(next, intervalTime);
    }
}

// Save current grid state via prompt and POST
async function saveGrid() {
    const filename = prompt("Enter the filename to save the grid state:", "grid_state");
    try {
        if (filename) {
            const response = await fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: filename })
            });
            const result = await response.json();
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Load grid state from uploaded file
async function loadGrid(event) {
    try {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/load', {
        method: 'POST',
        body: formData
    });
    const newState = await response.json();
    gridSize = newState.length;
    scene.clear();
    createGrid(newState);
    updateCameraPosition();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Prompt user to edit automaton rules and send to server
async function editRules() {
    try {
    const newrules = prompt(`Rule explanation X/Y/A where:
X - number of neighbours to stay alive
Y - number of neighbours to get alive
Z - neighbourhood type (N - Moore, M - Von Neumann)`, "3/3/M");

    const response = await fetch('/edit-rules', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rules: newrules })
    });
    } catch (error) {
        console.error('Error:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initialiseGrid();
});