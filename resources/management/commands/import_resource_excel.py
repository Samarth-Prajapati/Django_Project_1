from django.core.management.base import BaseCommand
import pandas as pd
from resources.models import Resource

class Command(BaseCommand):
    help = 'Import resource data from Excel for May 2025 (auto-calculate present_hours)'

    def add_arguments(self, parser):
        parser.add_argument('excel_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        df = pd.read_excel(excel_path)
        
        # Clean the data
        df = df.dropna(how='all')
        
        for idx, row in df.iterrows():
            present_day = row.get('Present Days', 0)
            resource, created = Resource.objects.update_or_create(
                resource_name=row['Unnamed: 0'],
                year=2025,
                month=5,
                defaults={
                    'working_days': row.get('Total No. Of working Days', 0),
                    'present_day': present_day,
                    # present_hours will be auto-calculated by model save()
                }
            )
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} resource: {resource.resource_name} (May 2025)"
            ))
        self.stdout.write(self.style.SUCCESS('Resource import complete!'))
