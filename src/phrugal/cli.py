import argparse
import os
from pathlib import Path

import phrugal


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phrugal")
    parser.add_argument("-c", "--config", help="Path to custom JSON config")
    parser.add_argument(
        "-i",
        "--input-dir",
        help="Path where the tool will recursively look for images to process.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Path to folder where to locate the output. If omitted, will default to current dir. "
        "The tool will attempt to create a directory if its not yet existing.",
    )
    parser.add_argument(
        "--create-default-config",
        help="If given, create default configuration at given path (or in current directory if omitted) and exit.",
        nargs="?",
        const="",  # the value of no path is given
        default=None,
    )
    parser.add_argument(
        "--version", action="version", version=f"{parser.prog} {phrugal.__version__}"
    )
    return parser


def _phrugal_main(args: argparse.Namespace):
    if args.create_default_config is not None:
        _create_default_config(args.create_default_config)


def _create_default_config(provided_path: str):
    if provided_path == "":
        current_dir = os.getcwd()
        target_file = Path(current_dir) / "phrugal-default.json"
    else:
        target_file = Path(provided_path)
    pc = phrugal.DecorationConfig()
    pc.write_default_config(target_file)


def run_cli():
    parser = _get_parser()
    parsed_args = parser.parse_args()

    _phrugal_main(parsed_args)


if __name__ == "__main__":
    run_cli()
