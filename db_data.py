import os
import django

# Set the environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_analysis.settings')  # Replace 'yourproject' with the name of your Django project

# Setup Django
django.setup()

# In the Django shell
from demoapp.models import Job

# Fetch all records
# all_records = CompanyMetrics.objects.all()
# for record in all_records:
#     print(record.id, record.employee_count)  # Replace `id` and `name` with relevant fields

row_count = Job.objects.count()
print(row_count)
