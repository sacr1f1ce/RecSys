from thefuzz import fuzz
from thefuzz import process

from load import name2id

names = name2id.keys()

def search(name):
    return name2id[process.extract(name, names, limit=1)[0][0]]