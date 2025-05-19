from utils import get_neighbors
import itertools
from pysat.formula import CNF

def generate_cnf(grid, variables):
    """
    Generate CNF clauses for the Gem Hunter game.
    
    Args:
        grid: 2D grid where each cell contains a digit, '_', or '*'
        variables: Dictionary mapping cell coordinates to variable IDs
    
    Returns:
        CNF object containing all constraints
    """
    cnf = CNF()
    rows, cols = len(grid), len(grid[0])
    
    # CRITICAL FIX: Add constraints for cells that MUST be numbers
    # These are FIXED cells and not part of the solution variables
    for i in range(rows):
        for j in range(cols):
            if grid[i][j].isdigit():
                # This cell must remain a number - force its variable to be False
                # (not a trap, which would be True)
                cnf.append([-variables[(i, j)]])
    
    # For each cell with a number, add constraints for its neighbors
    for i in range(rows):
        for j in range(cols):
            if grid[i][j].isdigit():
                k = int(grid[i][j])
                neighbors = get_neighbors(i, j, rows, cols)
                neighbor_vars = [variables[(x, y)] for x, y in neighbors]
                
                # Generate constraints for "exactly k neighbors are traps"
                add_exactly_k_constraints(cnf, neighbor_vars, k)
    
    return cnf

def add_exactly_k_constraints(cnf, variables, k):
    """
    Add CNF clauses that enforce exactly k variables are True.
    
    Args:
        cnf: The CNF formula to add clauses to
        variables: List of variables
        k: The exact number of variables that should be True
    """
    n = len(variables)
    
    # Check if k is valid
    if k < 0 or k > n:
        raise ValueError(f"Invalid k value: {k}. Must be between 0 and {n}.")
    
    # Special cases for efficiency
    if k == 0:
        # All variables must be False
        for var in variables:
            cnf.append([-var])
        return
    
    if k == n:
        # All variables must be True
        for var in variables:
            cnf.append([var])
        return
    
    # "At least k" constraint:
    # We can't have more than n-k variables be False
    # So for any selection of n-k+1 variables, at least one must be True
    for combo in itertools.combinations(variables, n-k+1):
        cnf.append(list(combo))  # Creates an OR clause of positive literals
    
    # "At most k" constraint:
    # We can't have more than k variables be True
    # So for any selection of k+1 variables, at least one must be False
    for combo in itertools.combinations(variables, k+1):
        cnf.append([-var for var in combo])  # Creates an OR clause of negative literals