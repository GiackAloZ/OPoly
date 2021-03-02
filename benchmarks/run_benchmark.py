import json
import subprocess
import re

def run_serial_benchmark():
    base_filename = "ser-gauss-seidel-"
    dims = ["1d", "2d", "3d"]

    src_dir = "src/"
    input_dir = "input/"
    input_dict = {
        "1d": "1d-10k-100k.txt",
        "2d": "2d-1k-1k-1k.txt",
        "3d": "3d-100-200-200-200.txt",
    }

    niters = 5

    benchs = []
    for d in dims:
        print(d, end="", flush=True)
        res_time = 0
        for _ in range(niters):
            print(".", end="", flush=True)
            run_res = subprocess.run("{}{}{} < {}{} > /dev/null ".format(
                src_dir, base_filename, d, input_dir, input_dict[d]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            res_string = run_res.stderr.decode("UTF-8").replace("\n", "")
            match = re.match(r".*done in (?P<time>\S*) seconds.*", res_string)
            exec_time = float(match.groupdict()["time"])
            res_time += exec_time
        res_time /= 5
        benchs.append({
            "dim": d,
            "type": "serial",
            "input": input_dict[d],
            "p": 1,
            "speedup": 1,
            "time": res_time
        })
    return benchs

def run_omp_benchmark():
    base_filename = "omp-gauss-seidel-"
    dims = ["1d", "2d", "3d"]

    src_dir = "src/"
    input_dir = "input/"
    input_dict = {
        "1d": "1d-10k-100k.txt",
        "2d": "2d-1k-1k-1k.txt",
        "3d": "3d-100-200-200-200.txt",
    }

    niters = 5

    benchs = []
    for d in dims:
        print(d, flush=True)
        p1time = 0
        for p in range(1, 13):
            print(p, end="", flush=True)
            res_time = 0
            for _ in range(niters):
                print(".", end="", flush=True)
                run_res = subprocess.run("OMP_NUM_THREADS={} {}{}{} < {}{} > /dev/null ".format(
                    p, src_dir, base_filename, d, input_dir, input_dict[d]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                res_string = run_res.stderr.decode("UTF-8").replace("\n", "")
                match = re.match(r".*done in (?P<time>\S*) seconds.*", res_string)
                exec_time = float(match.groupdict()["time"])
                res_time += exec_time
            res_time /= 5
            benchs.append({
                "dim": d,
                "type": "parallel",
                "input": input_dict[d],
                "p": p,
                "speedup": 1 if p == 1 else p1time / res_time,
                "time": res_time
            })
            if p == 1:
                p1time = res_time
        print("")
    return benchs


def run_benchmark():
    ser_benchs = run_serial_benchmark()
    omp_benchs = run_omp_benchmark()
    benchs = ser_benchs + omp_benchs
    with open("benchmark.json", "w") as f:
        json.dump(benchs, f, indent=4, sort_keys=True)

if __name__ == "__main__":
    run_benchmark()