import pymzn


def solve_model(
    model_path: str,
    data: dict,
    solver=pymzn.chuffed,
    timeout: int = 5
) -> (pymzn.Solutions, str):
    try:
        sols = pymzn.minizinc(
            mzn=model_path,
            data=data,
            solver=solver,
            timeout=timeout
        )
    except:
        return None, "An error occurred!"
    if sols.status in (pymzn.Status.UNKNOWN, pymzn.Status.INCOMPLETE):
        return None, "Solution not found in time!"
    if sols.status == pymzn.Status.UNSATISFIABLE:
        return None, "Unsatisfiable!"
    return sols[0], None
