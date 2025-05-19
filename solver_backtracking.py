from utils import is_cnf_satisfied, is_partial_cnf_valid

def solver_backtracking(cnf, variables):
    def backtrack(index, assignment):
        if index == len(variables):
            if is_cnf_satisfied(cnf, assignment):
                return assignment
            return None

        var = variables[index]

        assignment[var] = True
        if is_partial_cnf_valid(cnf, assignment):
            result = backtrack(index + 1, assignment)
            if result: return result

        assignment[var] = False
        if is_partial_cnf_valid(cnf, assignment):
            result = backtrack(index + 1, assignment)
            if result: return result

        del assignment[var]
        return None

    assignment = {}
    result = backtrack(0, assignment)
    return [v if result[v] else -v for v in variables] if result else None
