from opoly.modules.parser import PseudocodeForLoopParser
from opoly.modules.checker import LamportForLoopChecker


class TestPseudocodeForLoopParserAndLamportChecker():

    def test_1d_loop(self):
        code = "FOR i FROM 0 TO N { VAR a[i]=a[i+1]; }"
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, _ = LamportForLoopChecker().check(loop)
        assert res

    def test_2d_loop(self):
        code = "FOR i FROM 1 TO N-1 { FOR j FROM 2 TO M-1 { VAR a[j] = (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, _ = LamportForLoopChecker().check(loop)
        assert res

    def test_3d_loop(self):
        code = """
            FOR i FROM 1 TO N {
                FOR j FROM 2 TO M-2 {
                    FOR k FROM 2 TO L-2 {
                        VAR a[j][k] = (a[j-1][k-1] + a[j][k] + a[j+1][k+1]) / 3.0;
                        VAR a[j+2][k+2] = a[j][k];
                    }
                }
            }
        """
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, _ = LamportForLoopChecker().check(loop)
        assert res

    def test_not_perfectly_nested_loop(self):
        code = """
        FOR i FROM 0 TO N {
            VAR a[i][0] = 0;
            FOR j FROM 1 TO M-1 {
                VAR a[i][j] = a[i][j-1] + a[i][j+1];
                VAR a[j][j] = 0;
            }
            VAR a[N][M] = a[0][0];
        }
        """
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, err = LamportForLoopChecker().check(loop)
        assert not res
        assert err == "Not perfectly nested loop!"

    def test_not_plain_loop(self):
        code = """
        FOR i FROM 0 TO N {
            FOR j FROM i TO M {
                VAR a = b;
            }
        }
        """
        loop, _ = PseudocodeForLoopParser().parse_for_loop(code)
        res, err = LamportForLoopChecker().check(loop)
        assert not res
        assert err == "Not plain loop!"
