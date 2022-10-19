from pathlib import Path
import argparse
import subprocess
from tqdm import tqdm

def main(args):
    main_dir = Path(args.indir)
    list_dirs = [d for d in main_dir.iterdir() if d.is_dir()]
    list_dirs.sort()

    for folder in tqdm(list_dirs):
        try:
            lung_vol = str(next(folder.glob("lung_volume.txt")))
            air_vol = str(next(folder.glob("airway_volume.txt")))
            pickle = str(next(folder.glob("airway_tree.pickle")))
            summary = str(next(folder.glob("bp_summary_redcap.json")))

            command = [
                    "python3",
                    "./flag_potential_seg_errors.py",
                    lung_vol,
                    air_vol,
                    summary,
                    pickle
                    ]

            subprocess.run(command)
        except(StopIteration) as e:
            print(f"Error with finding file {e}")


if __name__ == "__main__":
    print("*********************************************")
    print("Correcting the airway and volume measurements.")
    print("*********************************************")
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", type=str, help="Main path to files.")
    args = parser.parse_args()

    main(args)
