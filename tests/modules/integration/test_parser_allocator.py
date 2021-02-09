import numpy as np

from opoly.modules.parser import PseudocodeForLoopParser
from opoly.modules.checker import LamportForLoopChecker
from opoly.modules.detector import LamportLoopDependenciesDetector
from opoly.modules.scheduler import LamportCPScheduler
from opoly.modules.allocator import LamportCPAllocator


class TestPseudocodeForLoopParserToLamportCPAllocator():

    def _pipeline_parser_allocator(self, code: str) -> np.ndarray:
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        _, _ = LamportForLoopChecker().check(loop)
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        deps_np = np.array(list(list(d.converted_values) for d in deps))
        schedule, _ = LamportCPScheduler().schedule(deps_np)
        allocation, _ = LamportCPAllocator().allocate(schedule)
        return allocation

    def test_1d_loop(self):
        code = "FOR i FROM 0 TO N { STM a[i]=a[i+1]; }"
        allocation = self._pipeline_parser_allocator(code)
        assert allocation.tolist() == [[1]]

    def test_2d_loop_example1(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 2 TO M-1 { STM a[i][j] = (a[i-1][j] + a[i][j] + a[i][j-1]) / 3.0; } }"
        allocation = self._pipeline_parser_allocator(code)
        assert allocation.tolist() == [[1, 1], [0, 1]]

    def test_2d_loop_example2(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 2 TO M-1 { STM a[j] = (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        allocation = self._pipeline_parser_allocator(code)
        assert allocation.tolist() == [[2, 1], [1, 0]]

    def test_3d_loop_example5(self):
        code = """
        FOR i FROM 1 TO N-1 {
            FOR j FROM 1 TO M-2 {
                FOR k FROM 1 TO L-2 {
                    STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
                }
            }
        }
        """
        allocation = self._pipeline_parser_allocator(code)
        assert allocation.tolist() == [[2, 1, 1], [1, 0, 0], [0, 0, 1]]
