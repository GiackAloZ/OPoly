import numpy as np

from opoly.modules.scheduler import LamportCPScheduler

class TestlamportCPScheduler():

    def test_2d_identity(self):
        deps = np.array([
            [1,0]
        ])
        sched, _ = LamportCPScheduler().schedule(deps)
        assert sched is not None
        assert sched.tolist() == [1,0]
    
    def test_2d_example1(self):
        deps = np.array([
            [1, 0],
            [0, 1]
        ])
        sched, _ = LamportCPScheduler().schedule(deps)
        assert sched is not None
        assert sched.tolist() == [1,1]
    
    def test_2d_example2(self):
        deps = np.array([
            [1,-1],
            [1, 1],
            [0, 1]
        ])
        sched, _ = LamportCPScheduler().schedule(deps)
        assert sched is not None
        assert sched.tolist() == [2,1]
    
    def test_3d_example4(self):
        deps = np.array([
            [1,0,0],
            [0,1,0],
            [0,0,1],
        ])
        sched, _ = LamportCPScheduler().schedule(deps)
        assert sched is not None
        assert sched.tolist() == [1,1,1]
    
    def test_3d_example5(self):
        deps = np.array([
            [1,0,0],
            [1,-1,0],
            [1,1,0],
            [0,1,0],
            [1,0,-1],
            [1,0,1],
            [0,0,1],
        ])
        sched, _ = LamportCPScheduler().schedule(deps)
        assert sched is not None
        assert sched.tolist() == [2,1,1]