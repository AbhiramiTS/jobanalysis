from django.urls import path
from . import views


urlpatterns = [

    path('', views.job_statistics_dashboard, name="job_statistics_dashboard"),
    path('top-companies/', views.top_companies_view, name='top_companies'),
    path('plot-top-companies/<int:num_companies>/', views.plot_top_companies, name='plot_top_companies'),
    path('top_industries_salary_chart/', views.top_industries_salary_chart, name='top_industries_salary_chart'),
    
    path('job_analysis/', views.job_analysis, name='job_analysis'),
    path('job_posting_efficacy/', views.job_posting_efficacy, name='job_posting_efficacy'),
    path('company-characteristics/', views.company_characteristics, name='company_characteristics'),
    path('job_statistics/', views.job_statistics, name='JobSalaryDashboard'),
    path('top-companies-dashboard/', views.top_companies_dashboard, name='top_companies_dashboard'),
    path('industry-pie-chart/', views.industry_pie_chart, name='industry_pie_chart'),
    path('about/', views.about, name='about'),







]