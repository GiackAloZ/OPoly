from pkg_resources import resource_filename

import pymzn

import opoly.modules.minizinc as minizinc


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
            timeout=timeout,
            include=minizinc.INCLUDE_FOLDER_PATH
        )
    except Exception as ex:
        return None, f"An error occurred!\n{ex}"
    if sols.status in (pymzn.Status.UNKNOWN, pymzn.Status.INCOMPLETE):
        return None, "Solution not found in time!"
    if sols.status == pymzn.Status.UNSATISFIABLE:
        return None, "Unsatisfiable!"
    return sols[0], None
