import os
import sys

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

if __name__ == "__main__":
    with open(sys.argv[2], "a+") as f:
        f.write(str(get_size(sys.argv[1])/1024.0))
        f.write("\n")

