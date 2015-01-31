import sys
import os
import json
import argparse
from MarkovParser import MarkovParser
from db import Db

from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)
    def get_data(self):
        return ''.join(self.fed)


def html_to_text(html):
    s = MLStripper()
    if html is None:
        return None
    else:
        s.feed(html)
        return s.get_data()

def list_files(path):
    # returns a list of names (with extension, without full path) of all files
    # in folder path
    files = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            files.append(name)
    return files

def read_json(path, name):
    #reads json from a file
    #returns dict
    full_path = os.path.join(path, name)
    if os.path.isfile(full_path):
        json_data=open(full_path)
        data = json.load(json_data)
        json_data.close()
        return data

def args_are_valid(args):
    if args.input and args.project:
        return True
    else:
        return False

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="directory of input files")
    parser.add_argument("--project", help="use this project corpus")
    parser.add_argument("--depth", help="depth of markov chain to use")
    args = parser.parse_args()

    if args.depth == None:
        depth = 2
    else:
        depth = int(args.depth)

    directory_name = args.input
    db = Db()
    db.init_project(args.project, depth)
    files = list_files(directory_name)
    for file in files:
        post_list = read_json(directory_name, file)
        post_count = len(post_list)
        i = 0
        for post in post_list:
            i = i + 1
            author = post.get("author")
            # thread = post.get("thread")
            post_text = html_to_text(post.get("post"))
            print file + ": " + str(i) + " out of " + str(post_count)
            if post_text is not None:
                MarkovParser("700Level", db).parse(post_text, author, depth)


if __name__ == "__main__":
    main(sys.argv)
