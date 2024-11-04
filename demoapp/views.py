from django.shortcuts import render
from django.db.models import Count, Max, Avg
from django.db.models.functions import Round
from .models import Job, CompanyMetrics, JobIndustry, Industry
import plotly.express as px
from plotly.graph_objs import Figure
from plotly.offline import plot
import pandas as pd
import plotly.graph_objects as go
from django.http import JsonResponse, HttpResponse
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
from django.conf import settings
import os
import seaborn as sns
from io import BytesIO
from django.db.models import OuterRef, Subquery, Count


# def home(request):
# 	context = {'form':"form"}
# 	return render(request, 'job_analysis/dashboard.html', context)


def get_top_locations():
    # Annotate job count and maximum salary for each location
    salary_job_stats_by_location = (
        Job.objects
        .values('location')
        .annotate(
            job_count=Count('job_id'),
            max_salary=Round(Max('normalized_salary'), 2)
        )
        .order_by('-job_count')  # Sort by job count for descending order
    )
    # Get the top 10 by max salary and job count
    top_10_salary = sorted(salary_job_stats_by_location, key=lambda x: x['max_salary'], reverse=True)[:10]
    top_10_job_count = salary_job_stats_by_location[:10]  # Already sorted by job count
    return top_10_salary, top_10_job_count


def salary_job_plot():
    # Get the data
    top_10_salary, top_10_job_count = get_top_locations()

    # Define hover templates
    hover_template_salary = '<b>Location</b>: %{y}<br><b>Max Salary</b>: $%{x:.2f}<extra></extra>'
    hover_template_job_count = '<b>Location</b>: %{y}<br><b>Job Count</b>: %{x}<extra></extra>'

    # Plot salary chart
    fig = px.bar(
        x=[item['max_salary'] for item in top_10_salary],
        y=[item['location'] for item in top_10_salary],
        orientation='h',
        labels={'x': 'Max Salary', 'y': 'Location'},
        title="Top 10 Locations by Max Salary"
    )

    # Apply hover template for the initial salary view
    fig.update_traces(hovertemplate=hover_template_salary)

    # Dropdown to toggle between 'Max Salary' and 'Job Count'
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        args=[{
                            'x': [[item['max_salary'] for item in top_10_salary]],
                            'y': [[item['location'] for item in top_10_salary]],
                            'hovertemplate': hover_template_salary
                        }],
                        label="Max Salary",
                        method="update"
                    ),
                    dict(
                        args=[{
                            'x': [[item['job_count'] for item in top_10_job_count]],
                            'y': [[item['location'] for item in top_10_job_count]],
                            'hovertemplate': hover_template_job_count
                        }],
                        label="Job Count",
                        method="update"
                    )
                ],
                direction="down",
                pad={"r": 10, "t": 20},
                showactive=True,
                x=0.17,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )
    
    fig.update_layout(
        xaxis_title="Values",
        yaxis_title="Location",
        title="Top 10 Locations by Max Salary or Job Count",
        yaxis=dict(categoryorder='total ascending'),
        autosize=False,
        width=900,
        height=700,
    )
    
    return fig



def job_statistics_dashboard(request):
    fig = salary_job_plot()
    plot_div = plot(fig, output_type='div')  # Convert the Plotly figure to an HTML div

    return render(request, 'demoapp/dashboard.html', {'plot_div': plot_div})

    

def get_top_companies(num_companies=50):
    # Load data from Django ORM
    postings = pd.DataFrame.from_records(
        Job.objects.all().values('company_id', 'company_name', 'original_listed_time')
    )
    employee_counts = pd.DataFrame.from_records(
        CompanyMetrics.objects.all().values('company_id', 'employee_count')
    )

    # Process Data
    postings['month_year'] = pd.to_datetime(postings['original_listed_time']).dt.to_period('M')
    monthly_postings = postings.groupby('month_year').size().reset_index(name='job_posting_count')

    company_postings = postings.groupby(['company_id', 'company_name']).size().reset_index(name='job_posting_count')
    top_companies = company_postings.sort_values(by='job_posting_count', ascending=False).head(num_companies)
    
    top_companies = top_companies.merge(employee_counts[['company_id', 'employee_count']], on='company_id', how='left')
    top_companies_cleaned = top_companies.drop_duplicates(subset=['company_id', 'company_name', 'job_posting_count'])

    return top_companies_cleaned

def plot_top_companies(request, num_companies=50):
    top_companies = get_top_companies(num_companies)

    # Create plot with Plotly
    fig = px.line(
        top_companies,
        x='company_name',
        y='job_posting_count',
        title=f'Top {num_companies} Companies with Highest Job Openings',
        markers=True,
        hover_data={'employee_count': True, 'job_posting_count': True}
    )
    fig.update_layout(xaxis_title='Company Name', yaxis_title='Job Posting Count', xaxis_tickangle=-45)

    # Convert plot to JSON for Plotly rendering in template
    graph_json = fig.to_json()

    return JsonResponse(graph_json, safe=False)

def top_companies_view(request):
    # Render the initial template with the default number of companies
    return render(request, 'demoapp/top_companies.html')


matplotlib.use('Agg')  # Use the non-GUI Agg backend for rendering images
def top_industries_salary_chart(request):
    # Filter jobs with positive salary
    jobs_with_salary = Job.objects.filter(normalized_salary__gt=0)
    
    # Calculate average salary per industry
    industry_salary = (
        jobs_with_salary
        .values('jobindustry__industry__industry_name')  # Access industry name through related fields
        .annotate(average_salary=Avg('normalized_salary'))
        .order_by('-average_salary')
    )

    # Get the top 10 industries by salary
    top_10_industries = list(industry_salary[:10])
    
    # Filter out any entries with a None or empty industry name
    top_10_industries = [
        item for item in top_10_industries 
        if item['jobindustry__industry__industry_name']
    ]
    
    # Extract industry names and salaries for plotting
    industry_names = [item['jobindustry__industry__industry_name'] for item in top_10_industries]
    salaries = [item['average_salary'] for item in top_10_industries]

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(salaries, labels=industry_names, autopct='%1.1f%%', startangle=140)
    ax.set_title('Top 10 Highest Paying Industries by Average Salary')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    # Save the image to the images directory
    images_dir = os.path.join(settings.BASE_DIR, 'images')  # Make sure the 'images' folder exists
    os.makedirs(images_dir, exist_ok=True)  # Create the folder if it doesn't exist

    image_path = os.path.join(images_dir, 'top_industries_salary_chart.png')
    with open(image_path, 'wb') as f:
        f.write(buf.getvalue())

    # Convert the plot to a PNG image and encode it as a base64 string for the template
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Pass the image to the template
    return render(request, 'demoapp/top_industries_salary_chart.html', {'chart_image': image_base64})



def job_analysis(request):
    # Step 1: Retrieve job postings
    postings = Job.objects.all().values()

    # Convert to DataFrame
    df = pd.DataFrame(list(postings))

    # ### Analysis 1: Job Description Length and Applications
    # Step 2: Calculate the length of each job description
    df['description_length'] = df['description'].apply(len)

    # Step 3: Calculate the correlation between description length and applications received
    correlation = df['description_length'].corr(df['applies'])

    # Step 4: Categorize description lengths with appropriate bins based on your data
    bins = [0, 350, 400, 450, 500]  # Updated bin edges based on your data range
    labels = ['Very Short', 'Short', 'Medium', 'Long']  # Updated labels matching the bins

    df['length_category'] = pd.cut(df['description_length'], bins=bins, labels=labels)

    # Step 5: Create the boxplot for description lengths
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='length_category', y='applies', data=df)
    plt.title("Applications by Job Description Length Category")
    plt.xlabel("Description Length Category")
    plt.ylabel("Number of Applications")

    # Save the plot to a BytesIO object
    buffer_desc_length = BytesIO()
    plt.savefig(buffer_desc_length, format='png')
    plt.close()
    buffer_desc_length.seek(0)
    plot_desc_length_url = base64.b64encode(buffer_desc_length.getvalue()).decode()

    # ### Analysis 2: Job Type Distribution
    # Step 6: Count job types
    job_type_counts = df['work_type'].value_counts()

    # Step 7: Create the bar plot for job types
    plt.figure(figsize=(10, 6))
    sns.barplot(x=job_type_counts.index, y=job_type_counts.values, palette="viridis")
    plt.title("Distribution of Job Types in the Market")
    plt.xlabel("Job Type")
    plt.ylabel("Number of Job Postings")

    # Save the plot to a BytesIO object
    buffer_job_type = BytesIO()
    plt.savefig(buffer_job_type, format='png')
    plt.close()
    buffer_job_type.seek(0)
    plot_job_type_url = base64.b64encode(buffer_job_type.getvalue()).decode()

    return render(request, 'demoapp/job_analysis.html', {
        'correlation': correlation,
        'plot_desc_length_url': plot_desc_length_url,
        'job_type_counts': job_type_counts,
        'plot_job_type_url': plot_job_type_url,
    })

    

def job_posting_efficacy(request):
    # Fetch data from the database
    postings = pd.DataFrame(list(Job.objects.all().values()))
    
    # Calculate conversion rates
    postings['conversion_rate'] = postings['applies'] / postings['views']
    
    # Get top job postings by conversion rate
    top_conversions = postings.sort_values(by='conversion_rate', ascending=False).head(10)

    # Create an interactive bar chart for conversion rates
    conversion_fig = px.bar(
        top_conversions,
        x='conversion_rate',
        y='title',
        title='Top Job Postings by Conversion Rate',
        labels={'conversion_rate': 'Conversion Rate (Applications / Views)', 'title': 'Job Title'},
        color='conversion_rate',
        color_continuous_scale=px.colors.sequential.Viridis,
    )
    conversion_graph = conversion_fig.to_html(full_html=False)

    # Analyze expiry and time until filled
    postings['expiry'] = pd.to_datetime(postings['expiry'])
    postings['original_listed_time'] = pd.to_datetime(postings['original_listed_time'])
    postings['time_until_expiry'] = (postings['expiry'] - postings['original_listed_time']).dt.days
    avg_time_to_fill_by_title = postings.groupby('title')['time_until_expiry'].mean().reset_index()

    # Create an interactive bar chart for average time until expiry
    time_fig = px.bar(
        avg_time_to_fill_by_title.head(20),
        x='time_until_expiry',
        y='title',
        title='Average Time Until Expiry by Job Role',
        labels={'time_until_expiry': 'Average Time Until Expiry (days)', 'title': 'Job Title'},
        color='time_until_expiry',
        color_continuous_scale=px.colors.sequential.Plasma,
    )
    time_graph = time_fig.to_html(full_html=False)

    return render(request, 'demoapp/job_posting_efficacy.html', {
        'conversion_graph': conversion_graph,
        'time_graph': time_graph,
    })
    
    


def company_characteristics(request):
    # Step 1: Fetch job postings and aggregate counts
    job_postings = (
        Job.objects
        .values('company_id', 'company_name')  # Group by company_id and company_name
        .annotate(job_posting_count=Count('job_id'))  # Count the job postings
    )

    # Fetch the latest employee counts based on company_id using a subquery
    latest_employee_counts = CompanyMetrics.objects.filter(
        company_id=OuterRef('company_id')
    ).order_by('-time_recorded')

    employee_counts = (
        CompanyMetrics.objects
        .values('company_id')
        .annotate(
            employee_count=Subquery(latest_employee_counts.values('employee_count')[:1]),
            follower_count=Subquery(latest_employee_counts.values('follower_count')[:1])
        )
    )

    # Convert to DataFrame for processing
    postings_df = pd.DataFrame(list(job_postings))
    employee_counts_df = pd.DataFrame(list(employee_counts))

    # Step 2: Merge the DataFrames
    merged_df = postings_df.merge(
        employee_counts_df[['company_id', 'employee_count', 'follower_count']],
        on='company_id', how='left'
    )

    # Check the merged DataFrame for debugging
    print(merged_df)

    # Step 3: Create visualizations
    # Job Postings vs Employee Count
    fig1 = px.scatter(
        merged_df,
        x="employee_count",
        y="job_posting_count",
        size="employee_count",
        hover_name="company_name",
        title="Job Postings vs Employee Count",
        labels={"employee_count": "Employee Count", "job_posting_count": "Job Posting Count"},
        size_max=50
    )
    fig1_html = fig1.to_html(full_html=False)

    # Follower Count vs Job Posting Count
    plt.figure(figsize=(10, 6))
    sns.regplot(
        x='follower_count',
        y='job_posting_count',
        data=merged_df,
        scatter_kws={'alpha': 0.5},
        line_kws={'color': 'red'}
    )
    plt.title('Follower Count vs. Job Posting Count')
    plt.xlabel('Follower Count')
    plt.ylabel('Job Posting Count')

    # Save plot to a PNG image and encode it for rendering in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_png = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plot_url = f"data:image/png;base64,{image_png}"

    context = {
        'scatter_plot': fig1_html,
        'regression_plot': plot_url,
    }

    return render(request, 'demoapp/company_characteristics.html', context)



# Top 10 Locations by Max Salary or Job Count
def job_statistics(request):
    fig = salary_job_plot()
    plot_div = plot(fig, output_type='div')  # Convert the Plotly figure to an HTML div

    return render(request, 'demoapp/job_statistics_dashboard.html', {'plot_div': plot_div})

def top_companies_dashboard(request):
    # Render the initial template with the default number of companies
    return render(request, 'demoapp/top_companies_dashboard.html')

def industry_pie_chart(request):
    return render(request, 'demoapp/industry_pie_chart.html')

def about(request):
    return render(request, 'demoapp/about.html')



