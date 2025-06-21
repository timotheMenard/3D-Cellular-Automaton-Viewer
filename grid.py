from cell import Cell
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor,  as_completed
import unittest


class TestGrid(unittest.TestCase):
    
    def setUp(self):
        self.size = 4  # Small grid size for testing
        self.initial_state = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        self.colours = {0: 0x000000, 1: 0xFFFFFF}  # Two colours for alive and dead cells
        self.grid = Grid(size=self.size, initial_state=self.initial_state, colours=self.colours)

    # Test the initialization of the grid
    def test_grid_initialization(self):
        self.assertEqual(len(self.grid.cells), self.size)
        self.assertEqual(len(self.grid.cells[0]), self.size)
        self.assertEqual(len(self.grid.cells[0][0]), self.size)
        self.assertEqual(self.grid.cells[0][0][0].cell_type, 0)  # All cells should be initialized as dead

    # Test get_neighbours function with Moore neighborhood
    def test_get_neighbours_moore(self):
        neighbours = self.grid.get_neighbours(1, 1, 1, radius=1, neighbourhood_type='M')
        # In a 4x4x4 grid, a Moore neighborhood with radius 1 at position (1,1,1) should have 26 neighbors
        self.assertEqual(len(neighbours), 26)

    # Test get_neighbours function with Von Neumann neighborhood
    def test_get_neighbours_von_neumann(self):
        neighbours = self.grid.get_neighbours(1, 1, 1, radius=1, neighbourhood_type='N')
        # In a Von Neumann neighborhood with radius 1, there should be fewer neighbours than Moore, typically 6
        self.assertEqual(len(neighbours), 6)


class Grid:
    def __init__(self, size, initial_state, colours, predefined_update=0):
        # Save the edited rules if the user edits them
        self.edited_rules = [[], [], 'M']
        self.size = size
        self.colours = colours
        self.predefined_update = predefined_update

        # Creates the grids of cells
        self.cells = [[[Cell(initial_state[x][y][z], 
                             [x,y,z], 
                             self.colours[initial_state[x][y][z]],
                             self.predefined_update) for z in range(size)] for y in range(size)] for x in range(size)]
    
    # Returns all cells give a neighbourhood  
    def get_neighbours(self, x, y, z, radius=1, neighbourhood_type='M'):
        neighbours = []
        if neighbourhood_type == 'M':  # Moore neighbourhood
            for i in range(max(0, x-radius), min(self.size, x+radius+1)):
                for j in range(max(0, y-radius), min(self.size, y+radius+1)):
                    for k in range(max(0, z-radius), min(self.size, z+radius+1)):
                        if (i, j, k) != (x, y, z):
                            neighbours.append(self.cells[i][j][k])
        elif neighbourhood_type == 'N':  # Von Neumann neighbourhood
            for i in range(max(0, x-radius), min(self.size, x+radius+1)):
                for j in range(max(0, y-radius), min(self.size, y+radius+1)):
                    for k in range(max(0, z-radius), min(self.size, z+radius+1)):
                        if (i, j, k) != (x, y, z) and (abs(i-x) + abs(j-y) + abs(k-z) <= radius):
                            neighbours.append(self.cells[i][j][k])
        return neighbours

    # Sequential update function
    """def update(self):
        new_cells = [[[Cell(self.cells[x][y][z].cell_type, 
                            self.cells[x][y][z].position,
                            self.cells[x][y][z].colour,
                            self.cells[x][y][z].predefined_update) for z in range(self.size)] for y in range(self.size)] for x in range(self.size)]
        
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    neighbours = self.get_neighbours(x, y, z, neighbourhood_type=self.edited_rules[2])
                    new_cells[x][y][z].update(neighbours, self.edited_rules[0], self.edited_rules[1])

        self.cells = new_cells"""
    
    def batch_update(self, start_x, end_x):
        #Update a slice of the grid from start_x to end_x (exclusive)
        new_cells_slice = [[[None for _ in range(self.size)] for _ in range(self.size)] for _ in range(start_x, end_x)]
        
        for x in range(start_x, end_x):
            for y in range(self.size):
                for z in range(self.size):
                    neighbours = self.get_neighbours(x, y, z, neighbourhood_type=self.edited_rules[2])
                    new_cell = Cell(self.cells[x][y][z].cell_type,
                                    self.cells[x][y][z].position,
                                    self.cells[x][y][z].colour,
                                    self.cells[x][y][z].predefined_update)
                    new_cell.update(neighbours, self.edited_rules[0], self.edited_rules[1])
                    new_cells_slice[x - start_x][y][z] = new_cell
                    
        return new_cells_slice

    # Concurrent update function
    def update(self):

        new_cells = [[[None for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        
        # Number of chunks to split the grid into for parallelisation
        num_chunks = os.cpu_count() 
        chunk_size = self.size // num_chunks
        
        # ThreadPoolExecutor to parallelise updates
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(num_chunks):
                start_x = i * chunk_size
                end_x = (i + 1) * chunk_size if i != num_chunks - 1 else self.size
                futures.append(executor.submit(self.batch_update, start_x, end_x))

            # Collect results
            for i, future in enumerate(as_completed(futures)):
                new_cells_slice = future.result()
                start_x = i * chunk_size
                for x in range(len(new_cells_slice)):
                    new_cells[start_x + x] = new_cells_slice[x]
        
        self.cells = new_cells

    
if __name__ == '__main__':
    unittest.main()
