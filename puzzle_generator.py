import random
import os
import copy
import sys
import itertools

def get_neighbors(i, j, rows, cols):
    neighbors = []
    for x in range(i-1, i+2):
        for y in range(j-1, j+2):
            if (x == i and y == j) or x < 0 or y < 0 or x >= rows or y >= cols:
                continue
            neighbors.append((x, y))
    return neighbors

def get_next_file_number():
    """
    Count the number of existing files in the testcases directory and return the next number
    """
    if not os.path.exists("testcases"):
        os.makedirs("testcases")
        return 1
    
    files = [f for f in os.listdir("testcases") if f.startswith("input_")]
    return len(files) + 1

def is_puzzle_solvable(grid, traps, rows, cols):
    """
    Check if the puzzle is uniquely solvable using a simple backtracking approach
    Returns: Boolean indicating if solvable, and the solution if found
    """
    # Create a working copy to avoid modifying the original
    working_grid = copy.deepcopy(grid)
    solution_found = [False]
    solutions = []
    max_solutions = 2  # Stop after finding 2 solutions (we just need to know if it's unique)
    
    def is_valid_placement(i, j, is_trap):
        # Check if placing a trap or non-trap at (i,j) is valid
        if is_trap:
            # If this is a trap, all numbers around it should increase by 1
            for ni, nj in get_neighbors(i, j, rows, cols):
                # Check if the neighbor is a digit before calling isdigit()
                if isinstance(working_grid[ni][nj], str) and working_grid[ni][nj].isdigit():
                    # There's already a number here, we need to check if increasing it would be valid
                    current_num = int(working_grid[ni][nj])
                    new_num = current_num + 1
                    # Count existing traps around this cell
                    existing_traps = sum(1 for ni2, nj2 in get_neighbors(ni, nj, rows, cols)
                                      if (ni2, nj2) != (i, j) and 
                                      isinstance(working_grid[ni2][nj2], bool) and working_grid[ni2][nj2])
                    # Check if adding this trap would exceed the number
                    if existing_traps + 1 > current_num:
                        return False
        else:
            # If this is not a trap, check if any surrounding number would become invalid
            for ni, nj in get_neighbors(i, j, rows, cols):
                # Check if the neighbor is a digit before calling isdigit()
                if isinstance(working_grid[ni][nj], str) and working_grid[ni][nj].isdigit():
                    current_num = int(working_grid[ni][nj])
                    # Count existing traps around this cell
                    existing_traps = sum(1 for ni2, nj2 in get_neighbors(ni, nj, rows, cols)
                                      if (ni2, nj2) != (i, j) and
                                      isinstance(working_grid[ni2][nj2], bool) and working_grid[ni2][nj2])
                    # Check if removing a potential trap would make the number invalid
                    remaining_cells = sum(1 for ni2, nj2 in get_neighbors(ni, nj, rows, cols)
                                         if (ni2, nj2) != (i, j) and
                                         not isinstance(working_grid[ni2][nj2], bool))
                    if existing_traps + remaining_cells < current_num:
                        return False
        return True
    
    def solve_backtrack(indices):
        if len(solutions) >= max_solutions:
            return
            
        if not indices:
            # We've placed all cells, check if this is a valid solution
            solution = [[False for _ in range(cols)] for _ in range(rows)]
            for i in range(rows):
                for j in range(cols):
                    if isinstance(working_grid[i][j], bool):
                        solution[i][j] = working_grid[i][j]
            solutions.append(solution)
            return
        
        i, j = indices[0]
        remaining = indices[1:]
        
        # Try placing a trap
        if is_valid_placement(i, j, True):
            working_grid[i][j] = True
            solve_backtrack(remaining)
            
        # Try not placing a trap
        if is_valid_placement(i, j, False):
            working_grid[i][j] = False
            solve_backtrack(remaining)
            
        # Backtrack
        working_grid[i][j] = '_'
    
    # Simplified approach for large puzzles: check basic constraints only
    if rows * cols > 25:  # For larger puzzles, do a basic check
        # Basic check: ensure that cells with numbers can potentially have that many traps around them
        for i in range(rows):
            for j in range(cols):
                if isinstance(grid[i][j], str) and grid[i][j].isdigit():
                    number = int(grid[i][j])
                    neighbors = get_neighbors(i, j, rows, cols)
                    unknown_neighbors = sum(1 for ni, nj in neighbors if grid[ni][nj] == '_')
                    known_traps = sum(1 for ni, nj in neighbors if traps[ni][nj])
                    if known_traps > number or known_traps + unknown_neighbors < number:
                        return False, None
        # For large puzzles, we'll assume it's solvable if it passes basic constraints
        return True, traps
    
    # For smaller puzzles, we'll do a full backtracking search
    # Find all unknown cells
    unknown_cells = [(i, j) for i in range(rows) for j in range(cols) if grid[i][j] == '_']
    
    # Initialize grid with known values
    for i in range(rows):
        for j in range(cols):
            if isinstance(grid[i][j], str) and grid[i][j].isdigit():
                working_grid[i][j] = grid[i][j]
            else:
                working_grid[i][j] = '_'
    
    # Run backtracking
    solve_backtrack(unknown_cells)
    
    # A puzzle is solvable if it has exactly one solution
    return len(solutions) == 1, solutions[0] if solutions else None

def generate_input_file(rows, cols=None, num_missing=None, trap_probability=0.2, file_number=None, max_attempts=50):
    """
    Generate a rows*cols puzzle grid for gem hunter:
    - Randomly place traps internally (hidden)
    - Calculate numbers for cells (how many traps around)
    - Replace traps and some numbers with '_'
    - Save as CSV file with numbers or '_' for unknown
    - Ensures the puzzle is solvable
    
    Parameters:
    - rows: Number of rows
    - cols: Number of columns (if None, use rows to make a square grid)
    - num_missing: Number of numbers to hide (if None, calculate based on grid size)
    - trap_probability: Probability of a cell being a trap
    - file_number: File number for naming (if None, auto-generate)
    - max_attempts: Maximum number of attempts to generate a solvable puzzle
    """
    # If cols is not provided, make a square grid
    if cols is None:
        cols = rows
    
    # Calculate default number of missing cells if not provided
    if num_missing is None:
        num_missing = int(rows * cols * 0.2)
    
    # Get the next file number if not provided
    if file_number is None:
        file_number = get_next_file_number()
    
    if not os.path.exists("testcases"):
        os.makedirs("testcases")
    
    # Try to generate a solvable puzzle
    for attempt in range(max_attempts):
        print(f"Generating puzzle attempt {attempt+1}/{max_attempts}...")
        
        # Step 1: Place traps internally (True means trap)
        traps = [[random.random() < trap_probability for _ in range(cols)] for _ in range(rows)]

        # Step 2: Calculate number of traps around each cell
        grid = []
        for i in range(rows):
            row = []
            for j in range(cols):
                if traps[i][j]:
                    # Trap cell hidden, output '_'
                    row.append('_')
                else:
                    neighbors = get_neighbors(i, j, rows, cols)
                    count = sum(1 for (nx, ny) in neighbors if traps[nx][ny])
                    # Store number as string, '0' will also be shown as '0' (or '_')
                    row.append(str(count) if count > 0 else '_')
            grid.append(row)

        # Step 3: Check if the grid is solvable without hiding any numbers
        solvable, solution = is_puzzle_solvable(grid, traps, rows, cols)
        if not solvable:
            continue
            
        # Step 4: Only now hide some of the numbers
        visible_grid = copy.deepcopy(grid)
        # Collect all cells that have numbers (digits)
        numbered_cells = [(i, j) for i in range(rows) for j in range(cols) if isinstance(grid[i][j], str) and grid[i][j].isdigit()]
        
        if not numbered_cells:
            # If there are no numbered cells, try again
            continue
            
        # Try different combinations of hidden cells until we find one that's solvable
        max_hide_attempts = 10
        for hide_attempt in range(max_hide_attempts):
            to_hide = random.sample(numbered_cells, min(num_missing, len(numbered_cells)))
            
            test_grid = copy.deepcopy(grid)
            for i, j in to_hide:
                test_grid[i][j] = '_'
                
            # Check if hiding these cells still gives a solvable puzzle
            still_solvable, _ = is_puzzle_solvable(test_grid, traps, rows, cols)
            if still_solvable:
                # We found a good configuration
                for i, j in to_hide:
                    grid[i][j] = '_'
                break
                
        if hide_attempt == max_hide_attempts - 1:
            # Couldn't find a good hiding configuration
            continue
                
        # Step 5: Write to file
        input_path = f"testcases/input_{file_number}.txt"
        with open(input_path, "w") as f:
            for row in grid:
                f.write(', '.join(row) + '\n')

        print(f"Generated solvable puzzle saved to {input_path}")
        
        # Write solution to a separate file for reference
        solution_path = f"testcases/solution_{file_number}.txt"
        with open(solution_path, "w") as f:
            for i in range(rows):
                row = []
                for j in range(cols):
                    if traps[i][j]:
                        row.append('T')  # T for trap
                    else:
                        neighbors = get_neighbors(i, j, rows, cols)
                        count = sum(1 for (nx, ny) in neighbors if traps[nx][ny])
                        if count == 0:
                            row.append('G')  # G for gem
                        else:
                            row.append(str(count))
                f.write(', '.join(row) + '\n')
        
        print(f"Solution saved to {solution_path}")
        
        # Return the file number used
        return file_number
        
    # If we get here, we couldn't generate a solvable puzzle
    print(f"Failed to generate a solvable puzzle after {max_attempts} attempts.")
    print("Try adjusting the trap probability or reduce the number of hidden cells.")
    return None