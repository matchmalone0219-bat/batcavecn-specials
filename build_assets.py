"""Copy only assets whose bytes differ; source timestamps are not trusted."""
import shutil


def copy_asset(source, destination):
    if destination.is_file() and source.stat().st_size == destination.stat().st_size:
        with source.open("rb") as original, destination.open("rb") as copied:
            while True:
                chunk = original.read(1024 * 1024)
                if chunk != copied.read(1024 * 1024):
                    break
                if not chunk:
                    return False
    shutil.copyfile(source, destination)
    return True
