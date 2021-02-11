from pkg_resources import resource_filename

import opoly.modules.minizinc as minizinc
import pymzn


def solve_model(
    model: str,
    data: dict,
    solver=pymzn.chuffed,
    timeout: int = 5
) -> (pymzn.Solutions, str):
    try:
        sols = pymzn.minizinc(
            mzn=model,
            data=data,
            solver=solver,
            timeout=timeout
        )
    except Exception as ex:
        return None, f"An error occurred!\n{ex}"
    if sols.status in (pymzn.Status.UNKNOWN, pymzn.Status.INCOMPLETE):
        return None, "Solution not found in time!"
    if sols.status == pymzn.Status.UNSATISFIABLE:
        return None, "Unsatisfiable!"
    return sols[0], None
