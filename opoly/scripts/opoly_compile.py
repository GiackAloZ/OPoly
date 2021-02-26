import argparse
import pathlib
import logging
import re

import numpy as np

from opoly.modules.parser import PseudocodeForLoopParser
from opoly.modules.checker import LamportForLoopChecker
from opoly.modules.detector import LamportLoopDependenciesDetector
from opoly.modules.scheduler import LamportCPScheduler
from opoly.modules.allocator import LamportCPAllocator
from opoly.modules.scanner import FourierMotzkinScanner
from opoly.modules.generator import CCodeGenerator, PseudoCodeGenerator


def opoly_compile(
    input_file: pathlib.Path,
    output_file: pathlib.Path = None,
    out_format: str = "CCODE",
    verbose: bool = False
):
    logger = logging.getLogger("logger_opoly")
    sh = logging.StreamHandler()
    sh_formatter = logging.Formatter("%(levelname)s - %(message)s")
    sh.setFormatter(sh_formatter)
    logger.addHandler(sh)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    try:
        logger.debug("Reading input file")
        with open(input_file, "r") as file:
            input_code = file.read()

        logger.debug("Scanning input file")
        omp_poly_dir_regex = re.compile(
            r"#pragma\s+omp\s+parallel\s+poly(?P<code>(.|\s)*?)#pragma\s+end")
        last_pos = 0
        code_list = []
        matches = []
        while True:
            match = omp_poly_dir_regex.search(input_code, pos=last_pos)
            if match is None:
                break
            code_list.append(match.group("code"))
            logger.info(
                f"Found code #{len(code_list)}: " + match.group("code"))
            matches.append(match)
            last_pos = match.end()+1

        if len(matches) == 0:
            logging.warning("No code found. Aborting")
            return

        new_loops = []
        for i, code in enumerate(code_list):
            logger.info(f"Processing code #{i+1}")
            logger.debug("Parsing code")
            loop, err = PseudocodeForLoopParser().parse_for_loop(code)
            if loop is None:
                logger.error(f"Error while parsing code #{i+1}: " + err)
                return
            logger.debug("Checking code")
            ok, err = LamportForLoopChecker().check(loop)
            if not ok:
                logger.error(f"Error while checking code #{i+1}: " + err)
                return
            logger.debug("Detecting dependencies")
            deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
            if len(deps) == 0:
                logger.warning(
                    f"No dependecies found for code #{i+1}. Skipping optimization")
            else:
                deps_np = np.array(list(list(d.converted_values)
                                        for d in deps))
                logger.debug("Scheduling loop")
                schedule, err = LamportCPScheduler().schedule(deps_np)
                if schedule is None:
                    logger.error(f"Error while scheduling loop #{i+1}: " + err)
                    return
                logger.debug("Allocating loop")
                allocation, err = LamportCPAllocator().allocate(schedule)
                if allocation is None:
                    logger.error(f"Error while allocating loop #{i+1}: " + err)
                    return
                logger.debug("Reindexing loop")
                loop = FourierMotzkinScanner().reindex(loop, allocation)
            logger.debug("Generating code")
            generator = CCodeGenerator() if out_format == "CCODE" else PseudoCodeGenerator()
            new_loop_code = generator.generate(loop)
            new_loops.append(new_loop_code)
            logger.debug(f"Loop #{i+1} done")

        # TODO replace old code with new code

    except Exception as ex:
        logger.error(f"An unexpected error as occourred: {ex}")


def main():
    argument_parser = argparse.ArgumentParser(
        description="A simple OpenMP polyhedral compiler for C programs"
    )
    argument_parser.add_argument(
        "file",
        type=pathlib.Path,
        help="the source file containing opoly loops"
    )
    argument_parser.add_argument(
        "-o", "--output",
        type=pathlib.Path,
        metavar="<file>",
        help="place the output into <file>"
    )
    argument_parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["CCODE", "PSEUDO"],
        default="CCODE",
        help="the output format, default CCODE"
    )
    argument_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="make output verbose"
    )
    args = argument_parser.parse_args()
    opoly_compile(
        args.file,
        args.output,
        args.format,
        args.verbose
    )


if __name__ == "__main__":
    main()
