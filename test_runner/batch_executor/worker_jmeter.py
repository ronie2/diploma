import sys
# import batch_executor
# from batch_executor import *

import os
#sys.path.append(os.path.abspath(__file__))
sys.path.append("/home/kali/DIPLOMA/diploma/test_runner")
from batch_executor import copy_file_to_folder
from rq import Connection, Worker

with Connection():
    qs = sys.argv[1:] or ['default']
    w = Worker(qs)
    w.work()

