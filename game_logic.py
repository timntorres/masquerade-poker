
from game_structs import HoldemRound, Action

from rand_manager import init_rand, shuffle

import random
import math
import time
from datetime import datetime

from constants import Phases, Actions

def log_action(round: HoldemRound, phase: str, subject: str, action: str, object: str) -> HoldemRound:
    action_list = round.actions
    new_action = Action(phase, subject, -1, action, object, datetime.now())
    action_list.append(new_action)
    print(new_action)


def init_rand(round, seed=None):
    if(seed == None):
        seed = math.floor(time.time()*1000000)
    random.seed(seed)
    log_action(round, phase=Phases.GAME_START, subject="Dealer", action=Actions.SHUFFLE, object=f"seed {seed}")
    return round

def shuffle(l):
    random.shuffle(l)
    return l



def play_round(round: HoldemRound) -> HoldemRound:
    round = init_rand(round)

    print('test')

