import os
import sys


class PathHelper:
    def get_root_path(self) -> str:
        return os.path.abspath(os.path.dirname(sys.argv[0]))

    def join_root_path(self, path):
        return self.get_root_path() + path

    def make_executable(self, path):
        mode = os.stat(path).st_mode
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        os.chmod(path, mode)
