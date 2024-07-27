import csv
from django.core.management.base import BaseCommand, CommandError
from pubs.models import Pub

class Command(BaseCommand):
    help = 'Import pubs data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be imported')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        try:
            with open(csv_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        Pub.objects.update_or_create(
                            fas_id=row['fas_id'],
                            defaults={
                                'name': row['name'],
                                'address': row['address'],
                                'postcode': row['postcode'],
                                'easting': row['easting'],
                                'northing': row['northing'],
                                'latitude': row['latitude'],
                                'longitude': row['longitude'],
                                'local_authority': row['local_authority']
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated pub {row["name"]}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error importing pub {row["name"]}: {e}'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file}" does not exist')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')

        self.stdout.write(self.style.SUCCESS('Successfully imported all pubs'))

