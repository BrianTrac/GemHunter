from itertools import product
from utils import is_cnf_satisfied

def solver_bruteforce(cnf, variables):
    for values in product([True, False], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        if is_cnf_satisfied(cnf, assignment):
            return [v if assignment[v] else -v for v in variables]
    return None
