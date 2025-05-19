import sys
import os
from time import time

from cnf_generator import generate_cnf
from solver_pysat import solver_pysat
from solver_bruteforce import solver_bruteforce
from solver_backtracking import solver_backtracking
from utils import interpret_model, print_grid, write_output_file, read_input_file, assign_variables
from puzzle_generator import generate_input_file


def run_solver(name, solver_func, grid, variables, cnf):
    print(f"\n=== Running {name} Solver ===")
    start = time()
    model = solver_func(cnf, list(variables.values()))
    elapsed = time() - start

    if model is None:
        print(f"{name} solver: No solution found.")
        return None, elapsed
    else:
        output_grid = interpret_model(grid, variables, model)
        print_grid(output_grid)
        return output_grid, elapsed


def menu():
    print("Choose a mode:")
    print("1. PySAT Solver")
    print("2. Brute-force")
    print("3. Backtracking")
    print("4. PySAT vs Brute-force")
    print("5. Backtracking vs Brute-force")
    print("6. Backtracking vs PySAT")
    print("7. PySAT vs Brute-force vs Backtracking")
    print("8. Generate random input file")
    print("0. Exit")
    return input("Your choice: ").strip()


def main():
    os.makedirs("testcases", exist_ok=True)

    if len(sys.argv) == 3 and sys.argv[1] == "--gen":
        size = int(sys.argv[2])
        generate_input_file(size)
        return

    while True:
        choice = menu()

        if choice == "0":
            break

        if choice in {"1", "2", "3", "4", "5", "6", "7"}:
            try:
                file_num = input("Enter file number: ").strip()
                input_file = f"testcases/input_{file_num}.txt"
                output_file = f"testcases/output_{file_num}.txt"

                if not os.path.exists(input_file):
                    print(f"Error: File {input_file} does not exist.")
                    continue

                grid = read_input_file(input_file)
                variables = assign_variables(grid)
                cnf = generate_cnf(grid, variables)

                if choice == "1":
                    output, elapsed = run_solver("PySAT", solver_pysat, grid, variables, cnf)
                    if output:
                        write_output_file(output_file, output)
                    print(f"PySAT time: {elapsed:.4f} seconds")

                elif choice == "2":
                    output, elapsed = run_solver("Brute-force", solver_bruteforce, grid, variables, cnf)
                    if output:
                        write_output_file(output_file, output)
                    print(f"Brute-force time: {elapsed:.4f} seconds")

                elif choice == "3":
                    output, elapsed = run_solver("Backtracking", solver_backtracking, grid, variables, cnf)
                    if output:
                        write_output_file(output_file, output)
                    print(f"Backtracking time: {elapsed:.4f} seconds")

                elif choice == "4":
                    for name, solver in [("PySAT", solver_pysat), ("Brute-force", solver_bruteforce)]:
                        output, elapsed = run_solver(name, solver, grid, variables, cnf)
                        print(f"{name} time: {elapsed:.4f} seconds")
                        if output:
                            write_output_file(output_file, output)

                elif choice == "5":
                    for name, solver in [("Backtracking", solver_backtracking), ("Brute-force", solver_bruteforce)]:
                        output, elapsed = run_solver(name, solver, grid, variables, cnf)
                        print(f"{name} time: {elapsed:.4f} seconds")
                        if output:
                            write_output_file(output_file, output)

                elif choice == "6":
                    for name, solver in [("Backtracking", solver_backtracking), ("PySAT", solver_pysat)]:
                        output, elapsed = run_solver(name, solver, grid, variables, cnf)
                        print(f"{name} time: {elapsed:.4f} seconds")
                        if output:
                            write_output_file(output_file, output)

                elif choice == "7":
                    for name, solver in [
                        ("PySAT", solver_pysat),
                        ("Backtracking", solver_backtracking),
                        ("Brute-force", solver_bruteforce)
                    ]:
                        output, elapsed = run_solver(name, solver, grid, variables, cnf)
                        print(f"{name} time: {elapsed:.4f} seconds")

                        if output:
                            write_output_file(output_file, output)

            except ValueError:
                print("Invalid input. Try again.")
                continue

        elif choice == "8":
            try:
                # Get file number
                file_num_input = input("Enter file number to create or overwrite: ").strip()
                if file_num_input:
                    try:
                        file_num = int(file_num_input)
                        file_exists = os.path.exists(f"testcases/input_{file_num}.txt")
                        if file_exists:
                            confirm = input(f"File input_{file_num}.txt already exists. Overwrite? (y/n): ").strip().lower()
                            if confirm != 'y':
                                print("Operation cancelled.")
                                continue
                    except ValueError:
                        print("Invalid file number. Please enter a numeric value.")
                        continue
                else:
                    # If no file number provided, get the next available one
                    from puzzle_generator import get_next_file_number
                    file_num = get_next_file_number()
                
                # Get grid dimensions
                rows = int(input("Enter number of rows (e.g., 5): ").strip())
                cols_input = input("Enter number of columns (or press Enter to use same as rows): ").strip()
                cols = int(cols_input) if cols_input else rows
                
                missing_input = input("Enter number of numbers to hide (or press Enter for default): ").strip()
                num_missing = int(missing_input) if missing_input else None
                
                trap_prob_input = input("Enter trap probability (0.0-1.0, or press Enter for default 0.2): ").strip()
                trap_probability = float(trap_prob_input) if trap_prob_input else 0.2
                
                result_file_num = generate_input_file(rows, cols, num_missing, trap_probability, file_num)
                if result_file_num:
                    print(f"Generated testcases/input_{result_file_num}.txt with dimensions {rows}x{cols}")
                    print(f"Solution saved to testcases/solution_{result_file_num}.txt")
                else:
                    print("Failed to generate a solvable puzzle. Try different parameters.")
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                
        else:
            print("Invalid choice. Try again.")
    print("Exiting the program.")


if __name__ == "__main__":
    main()