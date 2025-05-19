

def is_clause_satisfied(clause, assignment):
    return any((lit > 0 and assignment.get(abs(lit), False)) or
               (lit < 0 and not assignment.get(abs(lit), False))
               for lit in clause)

def is_cnf_satisfied(cnf, assignment):
    return all(is_clause_satisfied(clause, assignment) for clause in cnf)

def is_partial_cnf_valid(cnf, assignment):
    for clause in cnf:
        satisfied = False
        undecided = False
        for lit in clause:
            var = abs(lit)
            if var in assignment:
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    satisfied = True
                    break
            else:
                undecided = True
        if not satisfied and not undecided:
            return False
    return True


# Get valid neighbor coordinates
def get_neighbors(i, j, rows, cols):
    neighbors = []
    for x in range(i-1, i+2):
        for y in range(j-1, j+2):
            if (x == i and y == j) or x < 0 or y < 0 or x >= rows or y >= cols:
                continue
            neighbors.append((x, y))
    return neighbors

# Read grid from file
def read_input_file(filepath):
    grid = []
    with open(filepath, 'r') as f:
        for line in f:
            row = [cell.strip() for cell in line.strip().split(',')]
            grid.append(row)
    return grid

# Generate variable mapping
def assign_variables(grid):
    variables = {}
    id_counter = 1
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            variables[(i, j)] = id_counter
            id_counter += 1
    return variables

def interpret_model(grid, variables, model):
    result = []
    model_set = set(model)
    for i in range(len(grid)):
        row = []
        for j in range(len(grid[0])):
            cell = grid[i][j]
            if cell.isdigit():
                row.append(cell)  # Keep numbers as they are
            else:
                var = variables[(i, j)]
                if var in model_set:
                    row.append('T')  # trap
                else:
                    row.append('G')  # gem
            
        result.append(row)
    return result

# Print and optionally write the output
def print_grid(grid):
    for row in grid:
        print(', '.join(row))

def write_output_file(output_path, grid):
    with open(output_path, 'w') as f:
        for row in grid:
            f.write(', '.join(row) + '\n')
