import os
import subprocess

def reset():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subprocess.run(["bash", f"{dir_path}/docker-reset.sh"], check=True)
