import random

def pick_solution():
    with open("./helpers/arcdle.txt") as f:
        lines = f.readlines()
        return random.choice(lines)