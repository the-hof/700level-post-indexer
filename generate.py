import sys
import argparse
from db import Db
from MarkovGenerator import MarkovGenerator


def args_are_valid(args):
    if args.user and args.project:
        return True
    else:
        return False

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="generate posts based on user")
    parser.add_argument("--project", help="use this project corpus")
    parser.add_argument("--depth", help="depth of markov chain to use")
    args = parser.parse_args()
    if args_are_valid(args):
        db = Db()
        if args.depth == None:
            depth = 2
        else:
            depth = int(args.depth)

        print MarkovGenerator(db).generate_sentence(args.user, args.project, depth)

if __name__ == "__main__":
    main(sys.argv)