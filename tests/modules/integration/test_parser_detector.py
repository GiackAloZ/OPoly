from opoly.modules.parser import PseudocodeForLoopParser
from opoly.modules.checker import LamportForLoopChecker
from opoly.modules.detector import LamportLoopDependenciesDetector


class TestPseudocodeForLoopParserToLamportDetector():

    def test_1d_loop(self):
        code = "FOR i FROM 0 TO N { STM a[i]=a[i+1]; }"
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, _ = LamportForLoopChecker().check(loop)
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        assert sorted(map(lambda x: x.converted_values, deps)) == [(1,)]

    def test_2d_loop(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 2 TO M-1 { STM a[j] = (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, _ = LamportForLoopChecker().check(loop)
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        assert sorted(map(lambda x: x.converted_values, deps)) == [
            (0, 1), (1, -1), (1, 0), (1, 1)]

    def test_3d_loop(self):
        code = """
            FOR i FROM 1 TO N {
                FOR j FROM 1 TO M-2 {
                    FOR k FROM 1 TO L-2 {
                        STM u[j][k] = (u[j+1][k] + u[j][k+1] + u[j-1][k] + u[j][k-1]) * 0.25;
                    }
                }
            }
        """
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, _ = LamportForLoopChecker().check(loop)
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        assert sorted(map(lambda x: x.converted_values, deps)) == [
            (0, 0, 1), (0, 1, 0), (1, -1, 0), (1, 0, -1), (1, 0, 0), (1, 0, 1), (1, 1, 0)]
