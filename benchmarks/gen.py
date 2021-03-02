import argparse
import pathlib
import numpy as np

def gen(maxiter, dims, filename):
    with open(filename, "w") as f:
        f.write("%d " % maxiter)
        for d in dims:
            f.write("%d " % d)
        f.write("\n")
        f.write(" ".join([str(int(el)) for el in (np.random.rand(*dims) * 1000).flatten()]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=pathlib.Path)
    parser.add_argument("--maxiter", type=int)
    parser.add_argument("--dims", nargs="*", type=int)
    args = parser.parse_args()

    gen(args.maxiter, args.dims, args.filename)