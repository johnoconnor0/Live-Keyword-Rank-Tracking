# Search Result Scraper

A simple web application built with Flask to scrape and display the top 30 Google search results based on a keyword and an optional location.

## Features

- Input a keyword and an optional location to search.
- Option to ignore the location in the search.
- Displays the position, URL, meta title, and meta description of the top 30 search results.

## Requirements

- Python 3.x
- Flask
- Requests
- BeautifulSoup4

## Installation

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Install the required Python packages:**
    ```bash
    pip install flask beautifulsoup4 requests
    ```

## Usage

1. **Run the Flask application:**
    ```bash
    python app.py
    ```

2. **Open your web browser and go to:**
    ```
    http://127.0.0.1:5000/
    ```

3. **Enter the keyword and optional location:**
    - **Keyword**: The main search term.
    - **Location**: The location to include in the search (optional).
    - **Ignore Location**: Check this box if you do not want to include the location in the search.

4. **Click the "Search" button to see the results:**
    - The top 30 search results will be displayed in a table with their position, URL, meta title, and meta description.

## Code Overview

### app.py

The main Flask application file that handles the web server, form submissions, and scraping logic.

- **Imports:**
    - `Flask`, `request`, `render_template_string` from `flask`
    - `requests`
    - `BeautifulSoup` from `bs4`

- **HTML_TEMPLATE:**
    - A string containing the HTML template for the form and displaying the results.

- **index function:**
    - Handles the root URL (`/`) and both GET and POST requests.
    - Retrieves form data and calls the `scrape_google_results` function based on the form inputs.
    - Renders the HTML template with the results.

- **scrape_google_results function:**
    - Constructs the search query based on the keyword and optional location.
    - Sends a request to Google and parses the HTML response using BeautifulSoup.
    - Extracts the position, URL, meta title, and meta description for each result.
    - Returns the extracted results.

- **Main block:**
    - Runs the Flask application in debug mode if the script is executed directly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This app uses Flask for the web framework, Requests for making HTTP requests, and BeautifulSoup4 for parsing HTML.
