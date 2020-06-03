import core_classes
import os.path
import json


def get_level(index):
    filename = f"{index}level.txt"
    if not os.path.isfile(filename):
        raise RuntimeError("Level do not exist")
    with open(filename, 'r') as f:
        data = f.readlines()
    level = core_classes.Level()
    for line in data:
        attr, str_value = line.split(":")
        attr = attr[1:-1]
        str_value = str_value[1:-2]
        value = json.loads(str_value)
        setattr(level, attr, value)
    level.end_creating_level()
    return level


def put_level(index, level):
    filename = f"{index}level.txt"
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, "a") as f:
        for attr in level.__dict__.keys():
            if not attr.startswith('_'):
                f.write(f'"{attr}": {json.dumps(getattr(level, attr))},\n')
