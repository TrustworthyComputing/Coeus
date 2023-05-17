import os
import argparse
import heapq
import hashlib
import math
import numpy as np
from enum import Enum
from glob import glob
from colorama import Fore, Style

"""
Debug flag.
"""
DEBUG = False

"""
Verbose flag for various print messages.
"""
VERBOSE = False

"""
The maximum number of matches to return
"""
NUMBER_OF_MATCHES = 10

"""
Degree to which a fingerprint can be paired with its neighbors -- higher will cause more fingerprints, but potentially better accuracy.
"""
FAN_VALUE = 10

"""
The number of slices to split our shape to.
"""
NUM_OF_SLICES = 10

"""
The number of peaks to keep after filtering out.
"""
NUM_OF_PEAKS = 15

"""
The size of the grid that all shapes will scale to.
"""
GRID_SIZE = 1000

"""
Name of file
"""
ARRAY = None
NAME = None

"""
Interp flag.
"""
INTERP = False

"""
Flag to print accuracy including collisions.
"""
PRINT_NAIVE = False

"""
Flag to print accuracy using the neighborhoods approach.
"""
NEIGHBORHOODS = False

"""
Min number of signatures to match within a neighborhood.
"""
MIN_SIGNATURES_TO_MATCH = 2

"""
Number of bytes of the hash output
"""
HASH_DIGEST_SIZE = 20

"""
Export STL matches as PNGs and show them.
"""
EXPORT_PNGS = False
SHOW_PNGS = False



class Axis(Enum):
    """
    A class to represent the three axes.
    """
    X = 1
    Y = 2
    Z = 3


class Point:
    """
    A class to store points.
    """
    def __init__(self, token):
        self.x = float(token[1])
        self.y = float(token[2])
        self.z = float(token[3])

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.x == other.x and self.y == other.y and self.z == other.z

    def get_adjacent_axis_data(self, axis):
        if axis == Axis.X:
            return self.y, self.z
        elif axis == Axis.Y:
            return self.z, self.x
        elif axis == Axis.Z:
            return self.x, self.y
        else:
            error('get_adjacent_axis_data: no such axis')
            exit(-1)

    def get_star_rot_axis_data(self, axis):
        if axis == Axis.X:
            return self.x, self.y
        elif axis == Axis.Y:
            return self.y, self.z
        else:
            return self.z, self.x

    def print_point(self):
        print(str(self.x) + ' \t ' + str(self.y) + ' \t ' + str(self.z))



def log(s):
    """
    If DEBUG flag is specified, print log messages.
    """
    if DEBUG:
        print(Fore.YELLOW + str(s) + Style.RESET_ALL)


def error(s):
    """
    Print red the error messages.
    """
    print(Fore.RED + '> ' + str(s) + Style.RESET_ALL)


def file_or_dir_path(filepath):
    """
    Check if a path is a file or a directory
    """
    if os.path.isfile(filepath) or os.path.isdir(filepath):
        return filepath
    else:
        error(filepath + ' is not a file or directory')
        exit(-1)


def parseArgs():
    """
    Parse arguments and perform checks.
    """
    global DEBUG, VERBOSE, NUMBER_OF_MATCHES, FAN_VALUE, NUM_OF_SLICES, NUM_OF_PEAKS, GRID_SIZE, PRINT_NAIVE, NEIGHBORHOODS, MIN_SIGNATURES_TO_MATCH, EXPORT_PNGS, SHOW_PNGS, NAME, ARRAY
    parser = argparse.ArgumentParser(description='STL compression')
    parser.add_argument('--mode',               help='Learn or Search mode.', type=str.lower, choices=['learn', 'search'], required=True)
    parser.add_argument('--K',                  help='Max number of search results.', required=False)
    parser.add_argument('--fanout',             help='Degree to which a fingerprint can be paired with its neighbors.', required=False)
    parser.add_argument('--P',                  help='Number of peaks to keep after filtering.', required=False)
    parser.add_argument('--destroy_db',         help='Destroy the database.', action='store_true', required=False)
    parser.add_argument('--min_sig',            help='Min hashes to match in a neighborhood.', required=False)
    parser.add_argument('--grid_size', help='The 2D slice grid dimensions.', required=False)
    parser.add_argument('--neighborhoods',      help='Print matches using the neighborhood approach.', action='store_true', required=False)
    parser.add_argument('--print_fine_grained', help='Print matches using fine-grained approach.', action='store_true', required=False)
    parser.add_argument('--verbose',            help='Enable verbose mode.', action='store_true', required=False)
    parser.add_argument('--debug',              help='Enable debug mode.', action='store_true', required=False)
    parser.add_argument('--export_png',         help='Export PNG images for the matches.', action='store_true', required=False)
    parser.add_argument('--show_png',           help='Show the generated PNG images.', action='store_true', required=False)
    parser.add_argument('--array',              help='Path to arrray.', type=file_or_dir_path, nargs='+', required=True)
    parser.add_argument('--name',              help='Aearch name.', nargs='+', required=False)
    args = parser.parse_args()

    # Get list of files recursively
    array_inputs = []
    for filepath in args.array:
        # if it is a dir, get files recursively
        if os.path.isdir(filepath):
            array_inputs += [f for f in glob(filepath + '/**', recursive=True) if os.path.isfile(f)]
        # if it is a file, append it to the list of files
        else:
            array_inputs.append(filepath)
    # Check that all files end with .stl
    array_inputs = [filepath for filepath in array_inputs]
    DEBUG = args.debug
    VERBOSE = args.verbose
    EXPORT_PNGS = args.export_png
    SHOW_PNGS = args.show_png
    PRINT_NAIVE = args.print_fine_grained
    NEIGHBORHOODS = args.neighborhoods
    NAME = args.name
    if args.K is not None:
        NUMBER_OF_MATCHES = int(args.K)
    if args.fanout is not None:
        FAN_VALUE = int(args.fanout)
    if args.P is not None:
        NUM_OF_PEAKS = int(args.P)
    if args.grid_size is not None:
        GRID_SIZE = int(args.grid_size)
    if args.min_sig is not None:
        NEIGHBORHOODS = True
        MIN_SIGNATURES_TO_MATCH = int(args.min_sig)
    if not NEIGHBORHOODS:
        PRINT_NAIVE = True
    if args.array is not None:
        ARRAY = args.array
    return ARRAY, args.mode, args.destroy_db


def rot90(points_grid):
    """
    Rotate the grid clockwise by 90 degrees
    """
    return np.rot90(points_grid, 1, (0, 1))


def sort_by_axis(axis, points):
    """
    Sort the list for the given axis
    """
    if axis == Axis.X:
        return sorted(points, key=lambda point: point.x)
    elif axis == Axis.Y:
        return sorted(points, key=lambda point: point.y)
    elif axis == Axis.Z:
        return sorted(points, key=lambda point: point.z)
    else:
        print('No such axis.')

def find_max_min_range(points_array, axis):
    """
    Find min, max and range for the given axis
    """
    if axis == Axis.X:
        max_x = max(p.x for p in points_array)
        min_x = min(p.x for p in points_array)
        range_x = max_x - min_x
        return max_x, min_x, range_x
    elif axis == Axis.Y:
        max_y = max(p.y for p in points_array)
        min_y = min(p.y for p in points_array)
        range_y = max_y - min_y
        return max_y, min_y, range_y
    elif axis == Axis.Z:
        max_z = max(p.z for p in points_array)
        min_z = min(p.z for p in points_array)
        range_z = max_z - min_z
        return max_z, min_z, range_z


def sha1_hash(bytes):
    """
    Compute the SHA-1 hash of a byte stream.
    """
    sha = hashlib.sha1()
    sha.update(bytes)
    return sha.digest()


def sha1_hash_lst(byte_lst):
    """
    Compute the SHA-1 hash of a list with byte streams.
    """
    sha = hashlib.sha1()
    for l in byte_lst:
        sha.update(l)
    return sha.digest()


def nth_largest(n, lst):
    """
    Return the nth largest of a list
    """
    if len(lst) == 0:
        return None
    return heapq.nlargest(n, lst)[-1]


def quantizer(num, accuracy=0.02):
    factor = 1.0 / accuracy
    return round(num*factor)/factor


def print_lst_of_tuples(lst):
    if len(lst) == 0:
        print('0')
    else:
        print()
    for l in lst:
        match = l[0]
        accuracy = l[1]
        print('\t' + match + '\t(similarity = ' + str(round(accuracy, 3)) + ')')


def export_pngs(lst, show_png=False):
    if not os.path.exists('results'):
        os.makedirs('results')
    for i in range(len(lst)):
        file = lst[i]
        print('Exporting ./results/' + str(i+1) + '.png')
        os.system(
                'openscad -o ./results/' + str(i+1) + '.png -D \'model="' + file +
                '"; col=[0, 0.55, 0.81]\' --autocenter --viewall ' +
                '--colorscheme Nature --imgsize 3000,3000 ./open_stl.scad'
                )
        print()
        if show_png:
            os.system('eog ./results/' + str(i+1) + '.png &')


def normalize(lst):
    max_elem = max(lst,key=lambda item:item[1])[1]
    if max_elem <= 1:
        return
    # min_elem = min(lst,key=lambda item:item[1])[1]
    # delta = max_elem - min_elem
    for i in range(len(lst)):
        lst[i] = (lst[i][0], lst[i][1] / max_elem)
