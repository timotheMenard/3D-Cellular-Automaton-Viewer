// Switch to the cellular_automaton database
db = db.getSiblingDB('cellular_automaton');

// Create the grids collection if it doesn't exist
db.createCollection('grids');

// Load the trees.json file and insert it into the database
var treesData = cat('/docker-entrypoint-initdb.d/trees.json');
var trees = JSON.parse(treesData);

// Insert each tree configuration from the array
trees.forEach(function(tree) {
    // Converts everything to integers
    tree.size = NumberInt(tree.size);
    tree.predefined_update = NumberInt(tree.predefined_update);
    
    if (tree.cells) {
        for (var x = 0; x < tree.cells.length; x++) {
            for (var y = 0; y < tree.cells[x].length; y++) {
                for (var z = 0; z < tree.cells[x][y].length; z++) {
                    tree.cells[x][y][z] = NumberInt(tree.cells[x][y][z]);
                }
            }
        }
    }
    
    // Check if a document with this name already exists
    var existing = db.grids.findOne({ name: tree.name });
    
    if (!existing) {
        db.grids.insert(tree);
        print('Inserted tree configuration: ' + tree.name);
    } else {
        // Update existing document
        db.grids.replaceOne(
            { name: tree.name },
            tree
        );
        print('Updated tree configuration: ' + tree.name);
    }
});

print('MongoDB initialisation completed.');