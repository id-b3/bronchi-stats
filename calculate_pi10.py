#!/usr/bin/env python3

from pathlib import Path
import argparse
import multiprocessing as mp
from math import pi

import pandas as pd

from bronchipy.io import load_pickle_tree
from bronchipy.calc import calc_pi10


def get_pi10(folder):
    # Calculate summary bronchial parameters
    for file in folder.iterdir():
        if "airway_tree.pickle" in file.name:
            df = load_pickle_tree(str(file))
            pi10_5_tree = df[(df.inner_radius * 2 * pi) >= 6]
            pi10_6_tree = df[(df.generation <= 5)]
            pi10_2_tree = df[(df.generation > 0) & (df.generation <= 5)]
            pi10_5 = calc_pi10(
                pi10_5_tree["wall_global_area"],
                pi10_5_tree["inner_radius"],
                plot=False,
            )
            pi10_6 = calc_pi10(
                pi10_6_tree["wall_global_area"],
                pi10_6_tree["inner_radius"],
                plot=False,
            )
            pi10_2 = calc_pi10(
                pi10_2_tree["wall_global_area"],
                pi10_2_tree["inner_radius"],
                plot=False,
            )
            return folder.stem, pi10_5, pi10_6, pi10_2


def main(args):
    dirs = Path(args.indir)
    dir_list = [d for d in dirs.iterdir() if d.is_dir()]
    dir_list.sort()
    p = mp.Pool(8)
    results = p.map(get_pi10, dir_list)
    p.close()
    p.join()

    pi10_df = pd.DataFrame(results)
    pi10_df.to_csv(args.outpath, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", type=str, help="Input dir to summarise.")
    parser.add_argument("outpath", type=str, help="Ouptut summary file.")
    args = parser.parse_args()

    main(args)
