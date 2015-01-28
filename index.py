import sys
import os
import json
from MarkovParser import MarkovParser
from db import Db

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

def main(args):
    if (len(args)) > 2:
        directory_name = args[1]
        depth = int(args[2])
        files = list_files(directory_name)
        for file in files:
            post_list = read_json(directory_name, file)
            for post in post_list:
                author = post.get("author")
                #thread = post.get("thread")
                post_text = post.get("post")
                MarkovParser("700Level", Db()).parse(post_text, author, depth)


if __name__ == "__main__":
    main(sys.argv)
