import argparse
import shutil

from config import CHROMA_DB_PATH
from ingestion.indexer import index_project

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="wipe the existing index first")
    args = parser.parse_args()

    if args.rebuild:
        shutil.rmtree(CHROMA_DB_PATH, ignore_errors=True)

    print(index_project())
