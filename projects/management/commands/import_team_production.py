from django.core.management.base import BaseCommand
import pandas as pd
from projects.models import Project
from resources.models import Resource

class Command(BaseCommand):
    help = 'Import projects and resources from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        self.stdout.write(self.style.NOTICE(f'Reading Excel file: {excel_path}'))
        df = pd.read_excel(excel_path)
        for idx, row in df.iterrows():
            # Adjust these field names to match your Excel columns
            resource, _ = Resource.objects.get_or_create(resource_name=row['resource_name'])
            project, created = Project.objects.get_or_create(
                project_name=row['project_name'],
                year=row['year'],
                month=row['month'],
                defaults={
                    'billable_days': row.get('billable_days', 0),
                    'non_billable_days': row.get('non_billable_days', 0),
                }
            )
            project.resources.add(resource)
            project.save()
            self.stdout.write(self.style.SUCCESS(f"Imported project: {project.project_name} (row {idx+1})"))
        self.stdout.write(self.style.SUCCESS('Import complete!'))
