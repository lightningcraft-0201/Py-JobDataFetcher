# Job Data Fetching Tool

## Description

The Job Data Fetching Tool is a Python-based application that fetches job listings from a specified API (RapidAPI's JSearch) based on user-defined criteria and uploads the filtered job listings to a Google Sheets document. The tool provides a user-friendly interface using Tkinter for ease of use.

## Features

- Fetch job listings based on a search query.
- Filter jobs by date posted, remote availability, and expiration status.
- Optionally filter jobs based on salary range and period.
- Append job listings to a Google Sheets document.
- User-friendly interface for setting query parameters.

## Prerequisites

- Python 3.x
- `requests` library
- `python-dotenv` library
- `gspread` library
- `oauth2client` library
- `tkinter` library (usually included with Python installation)

## Installation

1. Clone the repository or download the source code.

2. Install the required Python libraries:
   ```bash
   pip install requests python-dotenv gspread oauth2client
   ```

3. Ensure you have a Google Cloud project with Google Sheets API enabled. Download the service account credentials JSON file and save it to your project directory.

4. Create a `.env` file in the project directory with the following content:
   ```dotenv
   GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/credentials.json
   RAPID_API_TOKEN=your_rapidapi_token
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. The Tkinter interface will appear. Fill in the fields with your desired search criteria:
   - **Search Query**: Enter the job search query.
   - **Date Posted**: Select the date range for job postings.
   - **Remote Jobs Only**: Check to filter only remote jobs.
   - **Include Expired Jobs**: Check to include jobs that have already expired.
   - **Enable Salary Filter**: Check to enable salary filtering.
   - **Start Page**: Enter the starting page for the job search.
   - **Page Count**: Enter the number of pages to fetch.
   - **Min Salary**: Enter the minimum salary (if salary filter is enabled).
   - **Max Salary**: Enter the maximum salary (if salary filter is enabled).
   - **Salary Period**: Select the salary period (if salary filter is enabled).

3. Click the **Submit** button to fetch and process the jobs. The results will be appended to the specified Google Sheets document.

## Code Overview

### Main Components

- **Google Sheets Authorization**: Loads Google Sheets credentials and authorizes the client to access the spreadsheet.
- **API Request**: Sends a GET request to the RapidAPI JSearch endpoint with the specified query parameters.
- **Data Filtering**: Filters the fetched job data based on salary range, expiration status, and salary period.
- **Data Upload**: Appends the filtered job data to the specified Google Sheets document.
- **Tkinter Interface**: Provides a user-friendly interface for setting query parameters and initiating the job fetch process.

### Functions

- `fetch_and_process_jobs()`: Fetches job listings based on user input, filters the results, and uploads them to Google Sheets.
- `safe_float(value, default=0.0)`: Safely converts a value to float, returning a default value if conversion fails.
- `filter_jobs(job_list, min_salary, max_salary, salary_period, include_expired, enable_salary_filter)`: Filters the job list based on salary range, expiration status, and salary period.
- `append_jobs_to_sheet(job_list)`: Appends job details to the Google Sheets document.
- `toggle_salary_fields()`: Enables or disables salary input fields based on the state of the salary filter checkbox.

### User Interface

- **Entry Fields**: Allow users to input search criteria.
- **Checkboxes**: Provide options to filter remote jobs, include expired jobs, and enable salary filtering.
- **Comboboxes**: Allow users to select date ranges and salary periods.
- **Submit Button**: Initiates the job fetching and processing.