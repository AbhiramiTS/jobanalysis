import os
import django


# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_analysis.settings')  # Replace 'myproject' with your project name
django.setup()

import random
from faker import Faker
from demoapp.models import Job, Company  # Replace 'myapp' with your app name

def update_and_add_jobs():
    fake = Faker()
    total_new_jobs = 100  # Number of new job entries to add
    companies = Company.objects.all()[:50]  # Choose the top 50 companies
    job_entries_to_update = list(Job.objects.all()[:100])  # Get the first 100 job entries to update

    if len(job_entries_to_update) < 100:
        print('Not enough job entries to update. Ensure there are at least 100 entries.')
        return

    # Ensure there are enough companies to select from
    if not companies:
        print('No companies found. Please add companies before running this script.')
        return

    # Update existing 100 job entries
    for job in job_entries_to_update:
        company = random.choice(companies)
        job.company = company
        job.company_name = company.name
        job.title = fake.job()
        job.description = fake.text(max_nb_chars=500)
        job.pay_period = random.choice(['hourly', 'monthly', 'yearly'])
        job.location = fake.city()
        job.views = random.randint(100, 1000)
        job.formatted_work_type = random.choice(['Full-time', 'Part-time', 'Contract'])
        job.applies = random.randint(0, 100)
        job.original_listed_time = fake.date_time_this_year()
        job.remote_allowed = random.choice([True, False])
        job.job_posting_url = fake.url()
        job.expiry = fake.date_time_this_year()
        job.listed_time = fake.date_time_this_year()
        job.work_type = random.choice(['On-site', 'Remote', 'Hybrid'])
        job.normalized_salary = round(random.uniform(30000, 120000), 2)
        job.zip_code = fake.zipcode()
        job.fips = random.randint(10000, 99999)

    # Bulk update existing job entries
    Job.objects.bulk_update(
        job_entries_to_update,
        fields=[
            'company', 'company_name', 'title', 'description', 'pay_period', 'location',
            'views', 'formatted_work_type', 'applies', 'original_listed_time', 'remote_allowed',
            'job_posting_url', 'expiry', 'listed_time', 'work_type', 'normalized_salary',
            'zip_code', 'fips'
        ]
    )

    print('Updated 100 existing job entries successfully.')

    # Create 100 new job entries
    job_entries_new = []
    for _ in range(total_new_jobs):
        company = random.choice(companies)
        job_entries_new.append(Job(
            company_name=company.name,
            title=fake.job(),
            description=fake.text(max_nb_chars=500),
            pay_period=random.choice(['hourly', 'monthly', 'yearly']),
            location=fake.city(),
            company=company,
            views=random.randint(100, 1000),
            formatted_work_type=random.choice(['Full-time', 'Part-time', 'Contract']),
            applies=random.randint(0, 100),
            original_listed_time=fake.date_time_this_year(),
            remote_allowed=random.choice([True, False]),
            job_posting_url=fake.url(),
            expiry=fake.date_time_this_year(),
            listed_time=fake.date_time_this_year(),
            work_type=random.choice(['On-site', 'Remote', 'Hybrid']),
            normalized_salary=round(random.uniform(30000, 120000), 2),
            zip_code=fake.zipcode(),
            fips=random.randint(10000, 99999)
        ))

    # Bulk create new job entries
    Job.objects.bulk_create(job_entries_new)

    print(f'Added {total_new_jobs} new job entries successfully.')

if __name__ == "__main__":
    update_and_add_jobs()
