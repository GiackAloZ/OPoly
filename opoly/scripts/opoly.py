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


def opoly(
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
            code = file.read()

        logger.debug("Parsing code")
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        if loop is None:
            logger.error("Error while parsing code: " + err)
            return

        logger.debug("Checking code")
        ok, err = LamportForLoopChecker().check(loop)
        if not ok:
            logger.error("Error while checking code: " + err)
            return

        logger.debug("Detecting code dependencies")
        deps = LamportLoopDependenciesDetector().extract_dependencies(loop)
        if len(deps) == 0:
            logger.warning(
                "No dependecies found in code. Skipping optimization")
        else:
            deps_np = np.array(list(list(d.converted_values)
                                    for d in deps))

            logger.debug("Scheduling loop")
            schedule, err = LamportCPScheduler().schedule(deps_np)
            if schedule is None:
                logger.error("Error while scheduling loop: " + err)
                return

            logger.debug("Allocating loop")
            allocation, err = LamportCPAllocator().allocate(schedule)
            if allocation is None:
                logger.error("Error while allocating loop: " + err)
                return

            logger.debug("Reindexing loop")
            loop = FourierMotzkinScanner().reindex(loop, allocation, separate_bounds=out_format == "CCODE")
        logger.debug("Generating code")
        generator = CCodeGenerator() if out_format == "CCODE" else PseudoCodeGenerator()
        new_code = generator.generate(loop)

        if output_file is None:
            print(new_code)
        else:
            logger.debug("Writing output file")
            with open(output_file, "w") as file:
                file.write(new_code)

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
    opoly(
        args.file,
        args.output,
        args.format,
        args.verbose
    )


if __name__ == "__main__":
    main()
