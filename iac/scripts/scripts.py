import os
import sys
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))

def manage():
    '''
    Runs Django management command.
    Passes arguments to bash script so that you can run Django management commands.
    '''
    args = sys.argv[1:]  # get command-line arguments
    subprocess.run(['bash', f'{dir_path}/manage.sh'] + args, check=True)  # pass arguments to bash script

def docker_reset():
    '''
    Stops, then turns off and removes all Docker containers and volumes for the application.
    Then rebuilds and re-runs the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-reset.sh'], check=True)
