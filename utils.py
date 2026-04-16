import random
import math
import time
from datetime import datetime
from dataclasses import replace

from constants import Phases, Actions

def update(dataclass_, **kwargs):
    return replace(dataclass_, **kwargs)

def get_date():
    return datetime.now().strftime("%Y-%m-%d")
def get_time():
    return datetime.now().strftime("%H:%M:%S")

def init_rand(round, seed=None):

    if(seed == None):
        seed = math.floor(time.time()*1000000)

    random.seed(seed)

    round.log_action(phase=Phases.GAME_START, subject="Dealer", action=Actions.SHUFFLE, object=seed)

    return round

def shuffle(l):
    random.shuffle(l)
    return l


