from abc import ABC
from datetime import timedelta

import numpy as np
import pymzn

from opoly.modules.minizinc import LAMPORT_ALLOCATOR_PATH
from opoly.modules.minizinc.utils import solve_model


class LamportCPAllocator(ABC):

    def allocate(self, schedule: np.ndarray) -> (np.ndarray, str):
        if len(schedule.shape) != 1:
            return None, "Schedule must be a one-dimensional vector!"
        sol, err = solve_model(
            model=LAMPORT_ALLOCATOR_PATH,
            data={
                "n": schedule.shape[0],
                "tau": schedule.tolist()
            }
        )
        if sol is None:
            return None, err
        return np.array(sol["T"]), None
