import pytest

import numpy as np

from opoly.modules.parser import PseudocodeForLoopParser
from opoly.modules.checker import LamportForLoopChecker
from opoly.modules.detector import LamportLoopDependenciesDetector
from opoly.modules.scheduler import LamportCPScheduler
from opoly.modules.allocator import LamportCPAllocator
from opoly.modules.scanner import FourierMotzkinScanner
from opoly.modules.generator import PseudoCodeGenerator, CCodeGenerator


class TestPseudocodeForLoopParserToPseudoCodeGenerator():

    def _pipeline_parser_scheduler(self, code: str) -> np.ndarray:
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        _, _ = LamportForLoopChecker().check(loop)
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        deps_np = np.array(list(list(d.converted_values) for d in deps))
        schedule, _ = LamportCPScheduler().schedule(deps_np)
        allocation, _ = LamportCPAllocator().allocate(schedule)
        reindexed_loop = FourierMotzkinScanner().reindex(loop, allocation)
        parallel_code = PseudoCodeGenerator().generate(reindexed_loop)
        return parallel_code

    def test_1d_loop(self):
        code = "FOR i FROM 0 TO N { STM a[i]=a[i+1]; }"
        parallel_code = self._pipeline_parser_scheduler(code)
        assert parallel_code == """FOR new_i FROM 0 TO N STEP 1 {
    VAR i = new_i;
    STM a[i] = a[i + 1];
}"""

    def test_2d_loop_example1(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 1 TO M-1 { STM a[i][j] = (a[i-1][j] + a[i][j] + a[i][j-1]) / 3.0; } }"
        parallel_code = self._pipeline_parser_scheduler(code)
        print(parallel_code)
        assert parallel_code == """FOR new_i FROM 2 TO M + N - 2 STEP 1 {
    FOR CONC new_j FROM fmax(1, -N + new_i + 1) TO fmin(M - 1, new_i - 1) STEP 1 {
        VAR i = new_i - new_j;
        VAR j = new_j;
        STM a[i][j] = (a[i - 1][j] + a[i][j] + a[i][j - 1]) / 3.0;
    }
}"""

    def test_2d_loop_example2(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 1 TO M-1 { STM a[j] = (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        parallel_code = self._pipeline_parser_scheduler(code)
        print(parallel_code)
        assert parallel_code == """FOR new_i FROM 3 TO M + 2 * N - 3 STEP 1 {
    FOR CONC new_j FROM ceil(fmax(1, (1.0 / 2.0) * (-M + new_i + 1))) TO floor(fmin(N - 1, (1.0 / 2.0) * (new_i - 1))) STEP 1 {
        VAR i = new_j;
        VAR j = new_i - 2 * new_j;
        STM a[j] = (a[j - 1] + a[j] + a[j + 1]) / 3.0;
    }
}"""

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
        parallel_code = self._pipeline_parser_scheduler(code)
        assert parallel_code == """FOR new_i FROM 4 TO L + M + 2 * N - 6 STEP 1 {
    FOR CONC new_j FROM ceil(fmax(1, (1.0 / 2.0) * (-L - M + new_i + 4))) TO floor(fmin(N - 1, (1.0 / 2.0) * (new_i - 2))) STEP 1 {
        FOR new_k FROM fmax(1, -M + new_i - 2 * new_j + 2) TO fmin(L - 2, new_i - 2 * new_j - 1) STEP 1 {
            VAR i = new_j;
            VAR j = new_i - 2 * new_j - new_k;
            VAR k = new_k;
            STM u[j][k] = (u[j + 1][k] + u[j][k + 1] + u[j - 1][k] + u[j][k - 1]) * 0.25;
        }
    }
}"""

# @pytest.mark.skip(reason="too slow to test every time")
class TestPseudocodeForLoopParserToCCodeGenerator():

    def _pipeline_parser_scheduler(self, code: str) -> np.ndarray:
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        _, _ = LamportForLoopChecker().check(loop)
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        deps_np = np.array(list(list(d.converted_values) for d in deps))
        schedule, _ = LamportCPScheduler().schedule(deps_np)
        allocation, _ = LamportCPAllocator().allocate(schedule)
        reindexed_loop = FourierMotzkinScanner().reindex(loop, allocation)
        parallel_code = CCodeGenerator().generate(reindexed_loop)
        return parallel_code

    def test_1d_loop(self):
        code = "FOR i FROM 0 TO N { STM a[i]=a[i+1]; }"
        parallel_code = self._pipeline_parser_scheduler(code)
        print(parallel_code)
        assert parallel_code == """for(int new_i = 0; new_i <= N; new_i++) {
    int i = new_i;
    a[i] = a[i + 1];
}"""

    def test_2d_loop_example1(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 1 TO M-1 { STM a[i][j] = (a[i-1][j] + a[i][j] + a[i][j-1]) / 3.0; } }"
        parallel_code = self._pipeline_parser_scheduler(code)
        print(parallel_code)
        assert parallel_code == """for(int new_i = 2; new_i <= M + N - 2; new_i++) {
    #pragma omp parallel for
    for(int new_j = fmax(1, -N + new_i + 1); new_j <= fmin(M - 1, new_i - 1); new_j++) {
        int i = new_i - new_j;
        int j = new_j;
        a[i][j] = (a[i - 1][j] + a[i][j] + a[i][j - 1]) / 3.0;
    }
}"""

    def test_2d_loop_example2(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 1 TO M-1 { STM a[j] = (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        parallel_code = self._pipeline_parser_scheduler(code)
        print(parallel_code)
        assert parallel_code == """for(int new_i = 3; new_i <= M + 2 * N - 3; new_i++) {
    #pragma omp parallel for
    for(int new_j = ceil(fmax(1, (1.0 / 2.0) * (-M + new_i + 1))); new_j <= floor(fmin(N - 1, (1.0 / 2.0) * (new_i - 1))); new_j++) {
        int i = new_j;
        int j = new_i - 2 * new_j;
        a[j] = (a[j - 1] + a[j] + a[j + 1]) / 3.0;
    }
}"""

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
        parallel_code = self._pipeline_parser_scheduler(code)
        print(parallel_code)
        assert parallel_code == """for(int new_i = 4; new_i <= L + M + 2 * N - 6; new_i++) {
    #pragma omp parallel for
    for(int new_j = ceil(fmax(1, (1.0 / 2.0) * (-L - M + new_i + 4))); new_j <= floor(fmin(N - 1, (1.0 / 2.0) * (new_i - 2))); new_j++) {
        for(int new_k = fmax(1, -M + new_i - 2 * new_j + 2); new_k <= fmin(L - 2, new_i - 2 * new_j - 1); new_k++) {
            int i = new_j;
            int j = new_i - 2 * new_j - new_k;
            int k = new_k;
            u[j][k] = (u[j + 1][k] + u[j][k + 1] + u[j - 1][k] + u[j][k - 1]) * 0.25;
        }
    }
}"""

    def test_3d_loop_lamport(self):
        code = """
            FOR i FROM 1 TO L {
                FOR j FROM 2 TO M {
                    FOR k FROM 2 TO N {
                        STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
                    }
                }
            }
            """
        parallel_code = self._pipeline_parser_scheduler(code)
        assert parallel_code == """for(int new_i = 6; new_i <= 2 * L + M + N; new_i++) {
    #pragma omp parallel for
    for(int new_j = ceil(fmax(1, (1.0 / 2.0) * (-M - N + new_i))); new_j <= floor(fmin(L, (1.0 / 2.0) * (new_i - 4))); new_j++) {
        for(int new_k = fmax(2, -M + new_i - 2 * new_j); new_k <= fmin(N, new_i - 2 * new_j - 2); new_k++) {
            int i = new_j;
            int j = new_i - 2 * new_j - new_k;
            int k = new_k;
            u[j][k] = (u[j + 1][k] + u[j][k + 1] + u[j - 1][k] + u[j][k - 1]) * 0.25;
        }
    }
}"""

#     def test_separate_bounds(self):
#         code = """
#             FOR i FROM 1 TO L {
#                 FOR j FROM 2 TO M {
#                     FOR k FROM 2 TO N {
#                         STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
#                     }
#                 }
#             }
#             """
#         parallel_code = self._pipeline_parser_scheduler(code)
#         assert parallel_code == """for(int new_i = 6; new_i <= 2 * L + M + N; new_i++) {
#     int new_j_lb = ceil(fmax(1, (1.0 / 2.0) * (-M - N + new_i)));
#     int new_j_ub = floor(fmin(L, (1.0 / 2.0) * (new_i - 4)));
#     #pragma omp parallel for
#     for(int new_j = new_j_lb; new_j <= new_j_ub; new_j++) {
#         for(int new_k = fmax(2, -M + new_i - 2 * new_j); new_k <= fmin(N, new_i - 2 * new_j - 2); new_k++) {
#             int i = new_j;
#             int j = new_i - 2 * new_j - new_k;
#             int k = new_k;
#             u[j][k] = (u[j + 1][k] + u[j][k + 1] + u[j - 1][k] + u[j][k - 1]) * 0.25;
#         }
#     }
# }"""

