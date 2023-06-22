import os
import sys
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))

def manage():
    '''
    Runs Django management command.
    Passes arguments to bash script so that you can run Django manage.py commands.
    '''
    args = sys.argv[1:]  # get command-line arguments
    subprocess.run(['bash', f'{dir_path}/manage.sh'] + args, check=True)  # pass arguments to bash script

def start_app():
    args = sys.argv[1:]  # get command-line arguments
    subprocess.run(['bash', f'{dir_path}/start-app.sh'] + args, check=True)

def docker_reset():
    '''
    Stops, then turns off and removes all Docker containers, images and volumes for the application.
    Then rebuilds and re-runs the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-reset.sh'], check=True)

def docker_down():
    '''
    Stops, then turns off and removes all Docker containers and volumes for the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-down.sh'], check=True)

def docker_up():
    '''
    Builds and runs the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-up.sh'], check=True)

def docker_logs():
    '''
    Shows logs for the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-logs.sh'], check=True)

def docker_web():
    '''
    Runs a bash shell in the web (Django) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-web.sh'], check=True)
