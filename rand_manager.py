import random
import math
import time

from constants import Phases, Actions

def init_rand(round, seed=None):

    if(seed == None):
        seed = math.floor(time.time()*1000000)

    random.seed(seed)

    round.log_action(phase=Phases.GAME_START, subject="Dealer", action=Actions.SHUFFLE, object=seed)

    return round

def shuffle(l):
    random.shuffle(l)
    return l

