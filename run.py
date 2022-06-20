#!/usr/bin/env python3

import os
import psutil
import subprocess

directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))
try:
    with open(f"{directory}/pid/{filename}.txt", "r") as file:
        pid = int(file.read())
    if psutil.pid_exists(pid):
        pid = psutil.Process(pid)
        pid.terminate()
        print("terminate")
except:
    pass

subprocess.Popen(["python", "bot.py"])
subprocess.Popen(["python", "cr.settings.py"])
subprocess.Popen(["python", "tl.add-to-group.py"])
