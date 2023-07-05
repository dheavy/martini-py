import os
import shutil
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Removes all files from the /static/ directory, except .gitkeep and /uploads/'

    def handle(self, *args, **options):
        path = 'static/'
        for root, dirs, files in os.walk(path):
            for f in files:
                full_path = os.path.join(root, f)
                if full_path != os.path.join(path, '.gitkeep'):
                    os.remove(full_path)

            for d in dirs:
                full_path = os.path.join(root, d)
                if full_path != os.path.join(path, 'uploads'):
                    shutil.rmtree(full_path)

        self.stdout.write('Successfully removed all files in /static except .gitkeep and /uploads/')
