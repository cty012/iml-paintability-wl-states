#!/usr/bin/env python3

"""
Converts between old and new board file formats.
"""

import argparse
import copy
from enum import Enum


# Default separator used in the input/output files
DEFAULT_SEPARATOR = "---"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Board format conversion tool. Converts between old and new board file formats.")

    # Input file argument
    parser.add_argument(
        "-i", "--in", type=str, required=True,
        help="Path to the input file")

    # Output file argument
    parser.add_argument(
        "-o", "--out", type=str, required=True,
        help="Path to the output file")

    # Output format argument
    parser.add_argument(
        "-d", "--direction", type=str, required=True,
        help="Direction of the conversion (\"old-to-new\", \"new2old\")")

    # Goal argument
    parser.add_argument(
        "-g", "--goal", type=str,
        help="When converting from new to old, the goal of the boards must be specified")

    # Separator argument (default: ---)
    parser.add_argument(
        "--isep", type=str, default="---",
        help="Separator used in the input file")

    # Separator argument
    parser.add_argument(
        "--osep", type=str, default="---",
        help="Separator used in the output file")

    # Parse the arguments
    args = parser.parse_args()

    # Check if --direction is valid
    if args.direction not in ["old-to-new", "new-to-old"]:
        parser.error("--direction must be either \"old-to-new\" or \"new-to-old\"")

    # Check if --goal is required and if it has been provided
    if args.direction == "new-to-old" and not args.goal:
        parser.error("--goal is required when --direction is \"new-to-old\"")

    return args


class DataType(Enum):
    OLD = 0
    NEW = 1


class Board:
    def __init__(self, n, k, chips, goal=0):
        self.n = n
        self.k = k
        self.chips_asc = copy.deepcopy(chips)
        self.chips_desc = copy.deepcopy(chips)
        self.goal = goal

        # Sort the chips in ascending/descending order
        for column in self.chips_asc:
            column.sort()
        for column in self.chips_desc:
            column.sort(reverse=True)

    def calc_max_row(self):
        return max(column[0] for column in self.chips_desc)

    def calc_num_chips(self):
        return sum(len(list(filter(lambda r: (r >= 0), column))) for column in self.chips_asc)

    @staticmethod
    def fromString(datatype, lines):
        if datatype == DataType.OLD:
            n, k, goal, max_row, num_chips = map(int, lines[0].split(","))
            chips = [[int(r.split(":")[0]) for r in column.split(" ")] for column in lines[1:]]
            return Board(n, k, chips, goal)
        elif datatype == DataType.NEW:
            n, k, num_chips = map(lambda x: int(x.split("=")[1]), lines[0].split(","))
            chips = [list(map(int, column.split(" "))) for column in lines[1:]]
            return Board(n, k, chips)
        else:
            raise ValueError("Invalid type")

    def toString(self, datatype):
        if datatype == DataType.OLD:
            head = f"{self.n},{self.k},{self.goal},{self.calc_max_row()},{self.calc_num_chips()}"
            body = "\n".join([
                " ".join([f"{r}:0" for r in column]) for column in self.chips_asc
            ])
            return f"{head}\n{body}"
        elif datatype == DataType.NEW:
            head = f"n={self.n},k={self.k},n_chips={self.calc_num_chips()}"
            body = "\n".join([" ".join(map(str, column)) for column in self.chips_desc])
            return f"{head}\n{body}"
        else:
            raise ValueError("Invalid type")


def file_to_boards(args):
    # Parse values from the arguments
    in_filename = getattr(args, "in")
    in_separator = getattr(args, "isep")
    datatype = DataType.OLD if getattr(args, "direction") == "old-to-new" else DataType.NEW
    if in_separator is None:
        in_separator = DEFAULT_SEPARATOR

    boards = []

    # Read the input file and convert it to the Board
    with open(in_filename, "r") as file:
        buffer = []

        # Read line by line
        for line in file:
            # Remove newline character
            line = line.strip()

            if line != in_separator:
                # Add line to buffer
                buffer.append(line)
            else:
                # Parse the contents received so far
                boards.append(Board.fromString(datatype, buffer))
                buffer = []

        # Add the last board (if any)
        if len(buffer) > 0:
            boards.append(Board.fromString(datatype, buffer))

    return boards


def boards_to_file(boards, args):
    # Parse values from the arguments
    out_filename = getattr(args, "out")
    out_separator = getattr(args, "osep")
    datatype = DataType.NEW if getattr(args, "direction") == "old-to-new" else DataType.OLD
    if out_separator is None:
        out_separator = DEFAULT_SEPARATOR

    # Write the Board to the output file
    with open(out_filename, "w") as file:
        for board in boards:
            if datatype == DataType.OLD:
                board.goal = int(getattr(args, "goal"))
            file.write(board.toString(datatype))
            file.write("\n")
            file.write(out_separator)
            file.write("\n")


if __name__ == "__main__":
    args = parse_args()
    boards = file_to_boards(args)
    boards_to_file(boards, args)
