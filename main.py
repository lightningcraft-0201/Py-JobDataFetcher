import requests
import os
import dotenv
import gspread
import datetime
import time
import tkinter as tk
from tkinter import ttk
from oauth2client.service_account import ServiceAccountCredentials

dotenv.load_dotenv()

# Load Google Sheets credentials from environment variable
google_credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
if not google_credentials_path:
    raise ValueError("The Google Sheets credentials path is not set in the environment variables")

# Set the scope and credentials for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentials_path, scope)
client = gspread.authorize(creds)

# Open the Google Spreadsheet by URL
sheet_url = "GOOGLE_SPREAD_SHEET_PUBLIC_URL"
spreadsheet = client.open_by_url(sheet_url)

# Get or create the first worksheet
try:
    worksheet = spreadsheet.get_worksheet(0)
except IndexError:
    worksheet = spreadsheet.add_worksheet(title="Sheet1", rows="100", cols="20")

# Ensure the header is set in the worksheet
header_names = ["Title", "Employer", "Employer Website", "Employer Type", "Job Publisher", "Employment Type", "Is Remote", "Posted Date", "Expiration Date", "Location", "Salary Info", "Salary Period", "Required Skills", "URL"]
if not worksheet.row_values(1):
    worksheet.append_row(header_names)

url = "https://jsearch.p.rapidapi.com/search"

def fetch_and_process_jobs():
    query = entry_query.get()
    date_posted = date_posted_var.get()
    is_remote = remote_var.get()
    start_page = entry_start_page.get()
    num_pages = entry_num_pages.get()
    min_salary = float(entry_min_salary.get()) if entry_min_salary.get() and enable_salary_filter_var.get() else 0
    max_salary = float(entry_max_salary.get()) if entry_max_salary.get() and enable_salary_filter_var.get() else float('inf')
    salary_period = salary_period_var.get()

    # Prepare the querystring for the API request based on user inputs
    querystring = {
        "query": query,
        "page": start_page,
        "num_pages": num_pages,
        "date_posted": date_posted,
        "remote_jobs_only": "true" if is_remote else "false",
    }

    headers = {
        "x-rapidapi-key": os.getenv('RAPID_API_TOKEN'),
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    jobs = []
    if data['status'] == "OK" and isinstance(data.get('data'), list):
        jobs.extend(data['data'])
    else:
        print("Data format is not as expected.")

    jobs_filtered = filter_jobs(jobs, min_salary, max_salary, salary_period, include_expired_var.get(), enable_salary_filter_var.get())
    append_jobs_to_sheet(jobs_filtered)
    print("Data loaded successfully to the spreadsheet.")

def safe_float(value, default=0.0):
    """Safely converts a value to float. Returns default if conversion fails."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def filter_jobs(job_list, min_salary, max_salary, salary_period, include_expired, enable_salary_filter):
    valid_jobs = []
    current_time = datetime.datetime.utcnow()

    for job in job_list:
        job_id = job.get('job_id', 'Unknown ID')
        expiration_date = job.get('job_offer_expiration_datetime_utc')
        job_salary_period = job.get('job_salary_period', '') or ''  # Ensure we handle None values properly
        job_salary_period = job_salary_period.upper() if job_salary_period else ''

        # Check if the salary period matches
        if salary_period.upper() != job_salary_period and job_salary_period:
            continue

        # Safely get salary values, defaulting to 0.0 if None or invalid
        job_min_salary = safe_float(job.get('job_min_salary'), 0.0)
        job_max_salary = safe_float(job.get('job_max_salary'), 0.0)

        # Check if the job has an expiration date and if it's valid
        if expiration_date:
            parsed_expiration_date = datetime.datetime.fromisoformat(expiration_date.rstrip('Z'))
            # Exclude expired jobs only if include_expired is False
            if not include_expired and parsed_expiration_date < current_time:
                continue

        # Check salary range if salary filtering is enabled
        if enable_salary_filter and not (min_salary <= job_min_salary and job_max_salary <= max_salary):
            continue

        valid_jobs.append(job)

    return valid_jobs

def append_jobs_to_sheet(job_list):
    for job in job_list:
        
        # Extract job details
        title = job.get('job_title', '')
        description = job.get('job_description', '')
        employer = job.get('employer_name', '')
        employer_website = job.get('employer_website', '')
        employment_type = job.get('job_employment_type', '')
        employer_company_type = job.get('employer_company_type', '')
        job_publisher = job.get('job_publisher', '')
        is_remote = job.get('job_is_remote', '')
        required_skills_list = job.get('job_required_skills', [])
        required_skills = ', '.join(required_skills_list) if required_skills_list else 'Not specified'

        # Handle dates
        posted_date_str = job.get('job_posted_at_datetime_utc', '')
        expiration_date_str = job.get('job_offer_expiration_datetime_utc', '')
        
        # Convert ISO format strings to datetime objects
        if posted_date_str:
            posted_date = datetime.datetime.fromisoformat(posted_date_str.rstrip('Z'))
            posted_date_formatted = posted_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            posted_date_formatted = 'Not provided'
        
        if expiration_date_str:
            expiration_date = datetime.datetime.fromisoformat(expiration_date_str.rstrip('Z'))
            expiration_date_formatted = expiration_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            expiration_date_formatted = 'Not provided'

        location = f"{job.get('job_city', '')}, {job.get('job_state', '')}"
        salary_info = f"{job.get('job_min_salary', 'N/A')} - {job.get('job_max_salary', 'N/A')}"
        salary_period = job.get('job_salary_period', '')
        url = job.get('job_apply_link', '')
        worksheet.append_row([title, employer, employer_website, employer_company_type, job_publisher, employment_type, is_remote, posted_date_formatted, expiration_date_formatted, location, salary_info, salary_period, required_skills, url])
        time.sleep(0.5)

def toggle_salary_fields():
    """Enable or disable salary fields based on the checkbox state."""
    if enable_salary_filter_var.get():
        entry_min_salary.config(state='normal')
        entry_max_salary.config(state='normal')
        salary_period_combobox.config(state='readonly')  # Enable dropdown for selection
    else:
        entry_min_salary.config(state='disabled')
        entry_max_salary.config(state='disabled')
        salary_period_combobox.config(state='disabled')  # Disable dropdown
        
# Initialize the main window
root = tk.Tk()
root.title("Job Data Fetching Tool")

# Variables for user inputs
date_posted_var = tk.StringVar()
remote_var = tk.BooleanVar()
include_expired_var = tk.BooleanVar()
enable_salary_filter_var = tk.BooleanVar()
salary_period_var = tk.StringVar()

# Search query input
tk.Label(root, text="Search Query:").grid(row=0, column=0)
entry_query = tk.Entry(root)
entry_query.grid(row=0, column=1)

# Date posted dropdown
tk.Label(root, text="Date Posted:").grid(row=1, column=0)
date_posted_combobox = ttk.Combobox(root, textvariable=date_posted_var, values=["all", "month", "week", "3days", "today"], state="readonly")
date_posted_combobox.grid(row=1, column=1)
date_posted_combobox.current(0)

# Remote jobs checkbox
tk.Checkbutton(root, text="Remote Jobs Only", variable=remote_var).grid(row=2, column=1)

# Include expired jobs checkbox
tk.Checkbutton(root, text="Include Expired Jobs", variable=include_expired_var).grid(row=3, column=1)

# Enable salary filter checkbox
tk.Checkbutton(root, text="Enable Salary Filter", variable=enable_salary_filter_var, command=toggle_salary_fields).grid(row=4, column=1)

# Start page input
tk.Label(root, text="Start Page:").grid(row=5, column=0)
entry_start_page = tk.Entry(root)
entry_start_page.grid(row=5, column=1)

# Page count input
tk.Label(root, text="Page Count:").grid(row=6, column=0)
entry_num_pages = tk.Entry(root)
entry_num_pages.grid(row=6, column=1)

# Minimum salary input
tk.Label(root, text="Min Salary:").grid(row=7, column=0)
entry_min_salary = tk.Entry(root, state='disabled')  # Initially disabled
entry_min_salary.grid(row=7, column=1)

# Maximum salary input
tk.Label(root, text="Max Salary:").grid(row=8, column=0)
entry_max_salary = tk.Entry(root, state='disabled')  # Initially disabled
entry_max_salary.grid(row=8, column=1)

# Salary period dropdown
tk.Label(root, text="Salary Period:").grid(row=9, column=0)
salary_period_combobox = ttk.Combobox(root, textvariable=salary_period_var, values=["HOUR", "YEAR"], state='disabled')  # Initially disabled
salary_period_combobox.grid(row=9, column=1)
salary_period_combobox.current(1)

# Submit button
submit_button = tk.Button(root, text="Submit", command=fetch_and_process_jobs)
submit_button.grid(row=10, column=1)

root.mainloop()
