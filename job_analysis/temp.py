import os
import django

# Set the environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_analysis.settings')  # Replace 'yourproject' with the name of your Django project

# Setup Django
django.setup()

import random
from faker import Faker
from django.utils import timezone
from demoapp.models import Company, Job, CompanyIndustry, CompanySpeciality, CompanyMetrics, Salary, JobSkill, JobIndustry, Skill, Benefits, Industry


# Initialize Faker instance
fake = Faker()

# Function to create dummy data
def populate_data():
    # Create 100 Company instances
    for _ in range(100):
        company = Company.objects.create(
            company_id=fake.unique.random_int(min=1, max=1000),
            name=fake.company(),
            description=fake.text(),
            company_size=fake.random_int(min=50, max=5000),
            state=fake.state(),
            country=fake.country(),
            city=fake.city(),
            zip_code=fake.zipcode(),
            address=fake.address(),
            url=fake.url()
        )
        
        # Create associated CompanyIndustry and CompanySpeciality entries
        for _ in range(3):  # Create up to 3 industries per company
            CompanyIndustry.objects.create(
                company=company,
                industry=fake.bs()
            )
        
        for _ in range(2):  # Create up to 2 specialities per company
            CompanySpeciality.objects.create(
                company=company,
                speciality=fake.job()
            )
        
        # Create CompanyMetrics
        CompanyMetrics.objects.create(
            company=company,
            employee_count=fake.random_int(min=50, max=5000),
            follower_count=fake.random_int(min=100, max=10000),
            time_recorded=timezone.now()
        )
        
    # Create 100 Job instances and associated data
    for _ in range(100):
        job = Job.objects.create(
            company_name=fake.company(),
            title=fake.job(),
            description=fake.paragraph(nb_sentences=5),
            pay_period=random.choice(['Monthly', 'Yearly', 'Weekly']),
            location=f"{fake.city()}, {fake.state()}",
            company=Company.objects.order_by('?').first(),
            views=fake.random_int(min=0, max=5000),
            formatted_work_type=random.choice(['Full-Time', 'Part-Time', 'Contract']),
            applies=fake.random_int(min=0, max=100),
            original_listed_time=timezone.now(),
            remote_allowed=fake.boolean(),
            job_posting_url=fake.url(),
            expiry=timezone.now() + timezone.timedelta(days=fake.random_int(min=30, max=365)),
            listed_time=timezone.now(),
            work_type=random.choice(['On-Site', 'Remote', 'Hybrid']),
            normalized_salary=fake.random_int(min=50000, max=200000),
            zip_code=fake.zipcode(),
            fips=fake.random_int(min=1000, max=9999)
        )
        
        # Create associated JobSkill, Salary, and Benefits
        for _ in range(3):  # Create up to 3 skills per job
            JobSkill.objects.create(
                job=job,
                skill_abr=fake.word()
            )
        
        Salary.objects.create(
            job=job,
            max_salary=fake.random_int(min=100000, max=300000),
            med_salary=fake.random_int(min=70000, max=150000),
            min_salary=fake.random_int(min=50000, max=100000),
            pay_period=random.choice(['Monthly', 'Yearly', 'Weekly']),
            currency='USD',
            compensation_type=random.choice(['Base', 'Bonus', 'Stock'])
        )
        
        Benefits.objects.create(
            job=job,
            inferred=fake.random_int(min=0, max=1),
            type=random.choice(['Health Insurance', 'Paid Time Off', 'Retirement Plan'])
        )
    
    # Create 100 Industry instances
    for _ in range(100):
        Industry.objects.create(
            industry_name=fake.unique.job()
        )
    
    print("Data population completed!")

# Call the function to populate the database
populate_data()
