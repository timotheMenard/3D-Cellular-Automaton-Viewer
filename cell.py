import random
import unittest


class TestCell(unittest.TestCase):
    
    def setUp(self):
        # Create a basic cell for testing
        self.cell = Cell(cell_type=0, position=[0, 0, 0], colour=0, predefined_update=0)
        self.neighbours = [
            Cell(cell_type=1, position=[-1, 0, 0]),
            Cell(cell_type=0, position=[1, 0, 0]),
            Cell(cell_type=1, position=[0, 1, 0]),
            Cell(cell_type=1, position=[0, -1, 0]),
        ]
        
    # Test default constructor values
    def test_default_constructor(self):
        cell = Cell(cell_type=0, position=[1, 1, 1])
        self.assertEqual(cell.cell_type, 0)
        self.assertEqual(cell.position, [1, 1, 1])
        self.assertEqual(cell.colour, 0)

    # Test celldict() method
    def test_celldict(self):
        self.cell.cell_type = 1
        self.cell.colour = 0x00FF00
        cell_dict = self.cell.celldict()
        self.assertEqual(cell_dict, {'cell_type': 1, 'colour': 0x00FF00})
    
    # Test update_default() method for underpopulation and overpopulation
    def test_update_default_underpopulation(self):
        # Set the cell as live (1) and ensure it has less than 2 live neighbours (underpopulation)
        self.cell.cell_type = 1
        neighbours = [Cell(cell_type=1, position=[-1, 0, 0])]
        self.cell.update_default(neighbours)
        self.assertEqual(self.cell.cell_type, 0)  # Should die due to underpopulation

    def test_update_default_survival(self):
        # Set the cell as live (1) and ensure it has 2-3 live neighbours (survival)
        self.cell.cell_type = 1
        self.cell.update_default(self.neighbours)
        self.assertEqual(self.cell.cell_type, 1)  # Should survive

    def test_update_default_overpopulation(self):
        # Set the cell as live (1) and ensure it has more than 3 live neighbours (overpopulation)
        neighbours = [Cell(cell_type=1, position=[i, 0, 0]) for i in range(4)]
        self.cell.cell_type = 1
        self.cell.update_default(neighbours)
        self.assertEqual(self.cell.cell_type, 0)  # Should die due to overpopulation

    def test_update_default_reproduction(self):
        # Set the cell as dead (0) and ensure it has exactly 3 live neighbours (reproduction)
        neighbours = [Cell(cell_type=1, position=[-1, 0, 0]),
                      Cell(cell_type=1, position=[1, 0, 0]),
                      Cell(cell_type=1, position=[0, 1, 0])]
        self.cell.cell_type = 0
        self.cell.update_default(neighbours)
        self.assertEqual(self.cell.cell_type, 1)  # Should come to life due to reproduction

    # Test update_edited_rules() with custom rules
    def test_update_edited_rules_custom(self):
        # Test with custom stay_alive and get_alive rules
        self.cell.cell_type = 1
        stay_alive = [2, 3]
        get_alive = [3]
        self.cell.update_edited_rules(self.neighbours, stay_alive, get_alive)
        self.assertEqual(self.cell.cell_type, 1)  # Should survive as there are 3 live neighbours

    def test_update_edited_rules_death(self):
        self.cell.cell_type = 1
        stay_alive = [4, 5]  
        get_alive = [3]
        self.cell.update_edited_rules(self.neighbours, stay_alive, get_alive)
        self.assertEqual(self.cell.cell_type, 0)  # Should die as live neighbours not in stay_alive

    def test_location(self):
        # Test location method to find a neighbour at a specific position
        result = self.cell.location(self.neighbours, [-1, 0, 0])
        self.assertEqual(result, (1, 0))  # Neighbour at [-1, 0, 0] should be cell_type 1 and height 0




class Cell:
    def __init__(self, cell_type, position, colour=0, predefined_update=0):
        self.cell_type = cell_type
        self.colour = colour #colour when alive, if dead it is not rendered
        self.position = position
        self.predefined_update = predefined_update

        # To limit the tree height (just to make sure)
        self.height = 0

        # Chooses which update function to use based on the file loaded
        if self.predefined_update == 0:
            self.update = self.update_edited_rules
        elif self.predefined_update == 1:
            self.update = self.tree1_update

    # Used to colour and cell type information for the scene
    def celldict(self):
        return {'cell_type': self.cell_type, 'colour':self.colour}

    # This is the default update method, 
    def update_default(self, neighbours):
        live_neighbours = sum(1 for n in neighbours if n.cell_type == 1)

        if self.cell_type == 1:
            if live_neighbours < 2 or live_neighbours > 3:
                self.cell_type = 0
        elif self.cell_type == 0:
            if live_neighbours == 3:
                self.cell_type = 1
    
    # This handles the rules if the user edits them
    def update_edited_rules(self, neighbours, stay_alive=[], get_alive=[]):
        red = 0xff0000
        if stay_alive == [] and get_alive == []:
            self.update_default(neighbours)
        else:
            live_neighbours = sum(1 for n in neighbours if n.cell_type == 1)

            if self.cell_type == 1:
                if live_neighbours not in stay_alive:
                    self.cell_type = 0
            elif self.cell_type == 0:
                if live_neighbours in get_alive:
                    self.cell_type = 1
                    self.colour = red

    # To find a certain cell at a certain location
    def location(self, neighbours, pos):
        npos = [self.position[0]+pos[0],
                self.position[1]+pos[1],
                self.position[2]+pos[2]]
        
        for cell in neighbours:
            if cell.position == npos:
                return cell.cell_type, cell.height
        return 0, 0

    def tree1_update(self, neighbours, stay_alive=[], get_alive=[]):
        brown = 0xdc7633
        green = 0x2ecc71

        if self.cell_type != 0: return

        # Check if there is wood under
        cell_under, height1 = self.location(neighbours, [0,-1,0])

        # Using Wolfram's strategy
        # For leaf x
        cell_xneg, height2x = self.location(neighbours, [-1,0,0])
        cell_xpos, height3x = self.location(neighbours, [1,0,0])
        cell_xbdownpos, _ = self.location(neighbours, [-1, 1, 0])
        cell_xbdownneg, _ = self.location(neighbours, [1, 1, 0])
        height = max([height1, height2x, height3x])
        heightbx = max([height2x, height3x])

        # For leaf z
        cell_zneg, height2z = self.location(neighbours, [0,0,-1])
        cell_zpos, height3z = self.location(neighbours, [0,0,1])
        cell_zbdownpos, _ = self.location(neighbours, [0, 1, -1])
        cell_zbdownneg, _ = self.location(neighbours, [0, 1, 1])
        heightbz = max([height2z, height3z])

        # Using Conway's strategy
        live_neighbours = sum(1 for n in neighbours if n.cell_type in [5, 6, 7, 8, 9, 10])

        # Trunk
        if cell_under == 2:
            # It stops
            if (height > 6 or random.random() > .8) and not height < 3:
                self.cell_type = 4
                self.colour = brown
            # It goes to the left
            elif random.random() < .2:
                self.cell_type = 3
                self.colour = brown
                self.height = height
            # It continues
            else:
                self.cell_type = 2
                self.colour = brown
                # Add height
                self.height = height + 1
        # first left wood
        elif cell_xneg == 3:
            self.cell_type = 2
            self.colour = brown
            # Add height
            self.height = height + 1
        
        # Leaf on x 
        elif cell_xneg in [4, 5, 8] or cell_xpos in [4, 5, 8]:
            # It stops on 6 coninues on 5
            if random.random() < .3 or heightbx > 2:
                self.cell_type = 6
                self.colour = green
            else:
                self.cell_type = 5
                self.colour = green
                self.height = heightbx + 1
        # Leaf down on x
        elif cell_xbdownpos in [9, 6] or cell_xbdownneg in [9, 6]:
            if random.random() > .91:
                self.cell_type = 6
                self.colour = green
            else:
                self.cell_type = 7
                self.colour = green
            self.height = heightbx + 1

        # Leaf on z
        elif cell_zneg in [4, 8, 5] or cell_zpos in [4, 8, 5]:
            # It stops on 9 coninues on 8
            if random.random() < .3 or heightbz > 2:
                self.cell_type = 9
                self.colour = green
            else:
                self.cell_type = 8
                self.colour = green
                self.height = heightbz + 1
        # Leaf down on z (this is where gravity is simulated using probabilities)
        elif cell_zbdownpos in [9, 6] or cell_zbdownneg in [9, 6]:
            if random.random() > .91:
                self.cell_type = 9
                self.colour = green
            else:
                self.cell_type = 10
                self.colour = green
            self.height = heightbz + 1

        # Top of tree
        elif cell_under == 4:
            self.cell_type = 11

        # Top of tree
        elif cell_xneg == 11 or cell_xpos == 11 or cell_zneg == 11 or cell_zpos == 11 and cell_under != 0:
            if random.random() > .8:
                self.cell_type = 11
                self.colour = green
            else:
                self.cell_type = 12
                self.colour = green

        # Makes it look like a tree
        elif live_neighbours > 5:
            self.colour = green
            self.cell_type = 12

            

    def __str__(self):
        return str(self.cell_type)
    


if __name__ == '__main__':
    unittest.main()
