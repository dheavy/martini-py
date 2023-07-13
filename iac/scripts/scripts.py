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
    subprocess.run([
        'bash',
        f'{dir_path}/manage.sh'] + args, # pass arguments to bash script
        check=True,
    )

def startapp():
    '''
    Beware of the naming here. This does not start the application.
    It just proxies a script wrapping "manage.py startapp" command (creates a new Django app)
    to create apps in the "apps" directory instead of the root directory.
    '''
    args = sys.argv[1:]  # get command-line arguments
    subprocess.run(['bash', f'{dir_path}/startapp.sh'] + args, check=True)

def docker_prod():
    '''
    Builds and runs the application in production mode.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-prod.sh'], check=True)

def docker_clean():
    '''
    Stop, then turn off and remove all Docker containers, images and volumes for the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-clean.sh'], check=True)

def docker_reset():
    '''
    Stop, then turn off and remove all Docker containers, images and volumes for the application.
    Then rebuilds and re-runs the application.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-reset.sh'], check=True)

def docker_down():
    '''
    Shutdown containers.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-down.sh'], check=True)

def docker_up():
    '''
    Build and start containers in development mode.
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

def docker_web_nginx():
    '''
    Runs a bash shell in the web_nginx (nginx reverse proxy for Django) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-web_nginx.sh'], check=True)

def docker_celery_beat():
    '''
    Runs a bash shell in the celery_beat (Celery scheduler) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-celery_beat.sh'], check=True)

def docker_celery_worker():
    '''
    Runs a bash shell in the celery_worker (Celery worker looking tasks to perform) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-celery_worker.sh'], check=True)

def docker_celery_flower():
    '''
    Runs a bash shell in the celery_flower (Celery cluster management and monitoring web UI) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-celery_flower.sh'], check=True)

def docker_postgres():
    '''
    Runs a bash shell in the postgres (Django's SQL DB) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-postgres.sh'], check=True)

def docker_qdrant():
    '''
    Runs a bash shell in the qdrant (vector database) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-qdrant.sh'], check=True)

def docker_redis():
    '''
    Runs a bash shell in the redis (queue for Celery tasks) container.
    '''
    subprocess.run(['bash', f'{dir_path}/docker-redis.sh'], check=True)
