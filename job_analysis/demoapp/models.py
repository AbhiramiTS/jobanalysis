# models.py
from django.db import models


class Company(models.Model):
    company_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)  # Adjust max_length as needed based on your data
    description = models.TextField()
    company_size = models.IntegerField()
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    url = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.company_id})"
    
    
class Job(models.Model):
    job_id = models.BigAutoField(primary_key=True)  # Change to BigAutoField for larger range
    company_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()  # Use TextField for long descriptions
    pay_period = models.CharField(max_length=50)  # Adjust max_length based on your needs
    location = models.CharField(max_length=255)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)  # Foreign key to the Company model
    views = models.IntegerField()
    formatted_work_type = models.CharField(max_length=50)
    applies = models.IntegerField()
    original_listed_time = models.DateTimeField()  # Assuming this is a datetime
    remote_allowed = models.BooleanField()
    job_posting_url = models.URLField()  # Use URLField for URLs
    expiry = models.DateTimeField()  # Assuming this is a datetime
    listed_time = models.DateTimeField()  # Assuming this is a datetime
    work_type = models.CharField(max_length=50)
    normalized_salary = models.FloatField()
    zip_code = models.CharField(max_length=10)  # Adjust max_length as necessary
    fips = models.IntegerField()

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    
class CompanyIndustry(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)  # Foreign key to the Company model
    industry = models.CharField(max_length=255)

    def __str__(self):
        return f"Company ID: {self.company.company_id} - Industry: {self.industry}"
    

class CompanySpeciality(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)  # Foreign key to the Company model
    speciality = models.CharField(max_length=255)

    def __str__(self):
        return f"Company ID: {self.company.company_id} - Speciality: {self.speciality}"
    

# Employee Count
class CompanyMetrics(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)  # Foreign key to Company model
    employee_count = models.IntegerField()
    follower_count = models.IntegerField()
    time_recorded = models.DateTimeField()  # Assuming time_recorded represents a date and time

    def __str__(self):
        return f"Company ID: {self.company.company_id} - Recorded on: {self.time_recorded}"


class Salary(models.Model):
    salary_id = models.AutoField(primary_key=True)  # Automatically incrementing primary key
    job = models.ForeignKey('Job', on_delete=models.CASCADE)  # Foreign key to Job model
    max_salary = models.FloatField()
    med_salary = models.FloatField()
    min_salary = models.FloatField()
    pay_period = models.CharField(max_length=50)  # Adjust max_length based on possible values
    currency = models.CharField(max_length=10)  # Adjust max_length based on currency codes
    compensation_type = models.CharField(max_length=50)  # Adjust based on expected values

    def __str__(self):
        return f"Salary ID: {self.salary_id} - Job ID: {self.job.job_id} - Max Salary: {self.max_salary} {self.currency}"
    
    
class JobSkill(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)  # Foreign key to Job model
    skill_abr = models.CharField(max_length=50)  # Adjust max_length based on expected values

    def __str__(self):
        return f"Job ID: {self.job.job_id} - Skill: {self.skill_abr}"
    
    
class JobIndustry(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)          # Foreign key to the Job model
    industry = models.ForeignKey('Industry', on_delete=models.CASCADE)  # Foreign key to the Industry model

    def __str__(self):
        return f"Job ID: {self.job.job_id} - Industry ID: {self.industry.industry_id}"
    
    
class Skill(models.Model):
    skill_abr = models.CharField(max_length=50)  # Abbreviation of the skill, must be unique
    skill_name = models.CharField(max_length=255)             # Full name of the skill

    def __str__(self):
        return f"{self.skill_abr} - {self.skill_name}"
    

class Benefits(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)  # Foreign key to Job model
    inferred = models.IntegerField()                           # Field for inferred value
    type = models.CharField(max_length=100)                   # Field for type description

    def __str__(self):
        return f"Job ID: {self.job.job_id} - Inferred: {self.inferred} - Type: {self.type}"


class Industry(models.Model):
    industry_id = models.AutoField(primary_key=True)  # Automatically incrementing primary key
    industry_name = models.CharField(max_length=255)  # Name of the industry, must be unique

    def __str__(self):
        return self.industry_name