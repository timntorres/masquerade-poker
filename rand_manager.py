import random
import math
import time

def init_rand(seed=None, silent=False):
    if(seed == None):
        seed = math.floor(time.time()*1000000)
    if(not silent):
        print(f"Shuffling with seed {seed}")
    random.seed(seed)
    return f"\n(Shuffling with seed {seed})\n"

def shuffle(l):
    random.shuffle(l)
    return l

