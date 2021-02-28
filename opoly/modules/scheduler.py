from abc import ABC
from datetime import timedelta

import numpy as np
import pymzn

from opoly.modules.minizinc import LAMPORT_SCHEDULER_PATH
from opoly.modules.minizinc.utils import solve_model


class LamportCPScheduler(ABC):

    def schedule(self, deps: np.ndarray) -> (np.ndarray, str):
        if len(deps.shape) != 2:
            return None, "Dependencies must be a matrix!"
        if not issubclass(deps.dtype.type, np.integer):
            return None, "Dependencies must be integers!"
        sol, err = solve_model(
            model=LAMPORT_SCHEDULER_PATH,
            data={
                "r": deps.shape[0],
                "n": deps.shape[1],
                "D": deps.tolist()
            }
        )
        if sol is None:
            return None, err
        return np.array(sol["tau"]), None
