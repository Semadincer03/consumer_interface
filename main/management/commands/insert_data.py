from django.core.management.base import BaseCommand, CommandError
import csv
from main.models import Hotel, Destination
from django.utils import translation


class Command(BaseCommand):
    help = 'Inserts the static data from specific file'

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('type', choices=['hotel', 'destination'])

    def handle(self, *args, **options):
        filename = options['filename']
        self.stdout.write("Reading from %s.." % filename)

        with open(filename, 'rb') as file:
            if options['type'] == 'hotel':
                model = Hotel
            else:
                model = Destination

            rows = csv.reader(file, delimiter=",", quotechar='"')
            for row in rows:
                try:
                    data = model(coral_code=row[0], name=row[1])
                    data.save()
                except:
                    self.stderr.write(str(row[0]) + " already exist\n",
                                      ending='')
