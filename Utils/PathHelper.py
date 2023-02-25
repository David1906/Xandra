import os
import sys


class PathHelper:
    def get_root_path(self) -> str:
        return os.path.abspath(os.path.dirname(sys.argv[0]))
