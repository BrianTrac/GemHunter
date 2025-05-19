from pysat.solvers import Solver

def solver_pysat(cnf, variables):
    with Solver(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            return solver.get_model()
        return None
