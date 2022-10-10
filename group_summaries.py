#!/usr/bin/env python3

from pathlib import Path
import argparse

import pandas as pd


def main(args):
    dirs = Path(args.indir)
    dir_list = [d for d in dirs.iterdir() if d.is_dir()]
    dir_list.sort()

    summary_list = []

    for folder in dir_list:
        for file in folder.iterdir():
            if "bp_summary_redcap.csv" in file.name:
                pass
            if "bp_summary_redcap.json" in file.name:
                df = pd.read_json(str(file), typ='series')
                df["id"] = folder.stem
                summary_list.append(df)

    summary_df = pd.DataFrame(summary_list)
    summary_df.to_csv(args.outpath, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", type=str, help="Input dir to summarise.")
    parser.add_argument("outpath", type=str, help="Ouptut summary file.")
    args = parser.parse_args()

    main(args)
