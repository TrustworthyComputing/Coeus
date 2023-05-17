#!/usr/bin/env python3
import helper as _hp
import database as _db
import fingerprint as _fp
import sys
from tqdm import tqdm
import os

def main():
    # parse arguments
    arrays, mode, destroyDB = _hp.parseArgs()

    # Delete database if the flag is set
    if destroyDB:
        _db.destroy_db('./avocado_db')
        if mode == 'search':
            sys.exit(0)

    # Open (or create) database
    db = _db.Database('./avocado_db')

    if _hp.VERBOSE:
        print('Generating fingerprint of', arrays, 'with:',
        '\n\tNumber of matches to return :', str(_hp.NUMBER_OF_MATCHES),
        '\n\tFan value :', str(_hp.FAN_VALUE),
        '\n\tNumber of slices :', str(_hp.NUM_OF_SLICES),
        '\n\tNumber of peaks :', str(_hp.NUM_OF_PEAKS),
        '\n\tGrid size :', str(_hp.GRID_SIZE),
        '\n\tRotate flag :', str(_hp.ROTATE),
        '\n\tStar rotate :', str(_hp.STAR_ROTATE),
        '\n\tInterpolation flag :', str(_hp.INTERP),
        '\n\tMin number of signatures to match within a neighborhood :', str(_hp.MIN_SIGNATURES_TO_MATCH),
        '\n')

    # Disable progress bar if only one
    disable_tqdm = False
    if len(arrays) < 2:
        disable_tqdm = True

    if mode == 'learn':
        #print('Enrolling fingerprint(s) to the database...')
        pass

    # For each file
    neighborhoods = None
    if True:
        # generate fingerprint of the file
        if neighborhoods is None:
            neighborhoods = _fp.fingerprint(arrays, _hp.NUM_OF_PEAKS, _hp.FAN_VALUE)
        else:
            neighborhoods.append(_fp.fingerprint(arrays, _hp.NUM_OF_PEAKS, _hp.FAN_VALUE))
        search_name = _hp.NAME
        #print(search_name)
        if _hp.NAME == None:
            search_name = _fp.array_name(arrays[0])
        
        # Add fingerprint to database
        if isinstance(search_name, list):
            for name in search_name:
                if mode == 'learn':
                    db.add_signatures(neighborhoods, name)
                # Search in database for potential matches
                else: # mode == 'search':
                    anchor_matches, signatures_matches = db.search_signatures(neighborhoods)
                    matches = None
                    if _hp.PRINT_NAIVE:
                        print('\nFiles matched with ' + search_name + ' using the number of signatures : ')
                        matches = signatures_matches
                        _hp.print_lst_of_tuples(matches)
                        print()

                    if _hp.NEIGHBORHOODS:
                        print('\nFiles matched with ' + search_name + ' using the number of neighborhoods : ')
                        matches = anchor_matches
                        _hp.print_lst_of_tuples(matches)
                        print()

                    if _hp.EXPORT_PNGS or _hp.SHOW_PNGS:
                        _hp.export_pngs([i[0] for i in matches], _hp.SHOW_PNGS)



        else:
            if mode == 'learn':
                db.add_signatures(neighborhoods, search_name)
            # Search in database for potential matches
            else: # mode == 'search':
                anchor_matches, signatures_matches = db.search_signatures(neighborhoods)
                matches = None
                if _hp.PRINT_NAIVE:
                    print('\nFiles matched with ' + search_name + ' using the number of signatures : ')
                    matches = signatures_matches
                    _hp.print_lst_of_tuples(matches)
                    print()

                if _hp.NEIGHBORHOODS:
                    print('\nFiles matched with ' + search_name + ' using the number of neighborhoods : ')
                    matches = anchor_matches
                    _hp.print_lst_of_tuples(matches)
                    print()

                if _hp.EXPORT_PNGS or _hp.SHOW_PNGS:
                    _hp.export_pngs([i[0] for i in matches], _hp.SHOW_PNGS)

    # Close the database
    db.close_db()

if __name__ == "__main__":
    main()
