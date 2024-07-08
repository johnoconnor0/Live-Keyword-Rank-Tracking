from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

# Initialize the Flask application
app = Flask(__name__)

# HTML template for rendering the form and displaying results
HTML_TEMPLATE = '''
<!doctype html>
<html>
    <head>
        <title>Search Result Scraper</title>
    </head>
    <body>
        <h1>Search Result Scraper</h1>
        <form method="POST">
            <label for="keyword">Keyword:</label>
            <input type="text" id="keyword" name="keyword" required><br><br>
            <label for="location">Location:</label>
            <input type="text" id="location" name="location"><br><br>
            <input type="checkbox" id="ignore_location" name="ignore_location">
            <label for="ignore_location">Ignore Location</label><br><br>
            <button type="submit">Search</button>
        </form>
        {% if results %}
            <h2>Results</h2>
            <table border="1">
                <tr>
                    <th>Position</th>
                    <th>URL</th>
                    <th>Meta Title</th>
                    <th>Meta Description</th>
                </tr>
                {% for result in results %}
                <tr>
                    <td>{{ result['position'] }}</td>
                    <td>{{ result['url'] }}</td>
                    <td>{{ result['title'] }}</td>
                    <td>{{ result['description'] }}</td>
                </tr>
                {% endfor %}
            </table>
        {% endif %}
    </body>
</html>
'''

# Route for handling the home page and form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []  # Initialize results list
    if request.method == 'POST':  # Check if the form is submitted via POST
        keyword = request.form.get('keyword')  # Get the keyword from the form
        location = request.form.get('location')  # Get the location from the form
        ignore_location = request.form.get('ignore_location')  # Check if the ignore location checkbox is checked
        if keyword:  # Check if keyword is provided
            if ignore_location:  # If ignore location is checked
                results = scrape_google_results(keyword)  # Call scrape function without location
            else:
                results = scrape_google_results(keyword, location)  # Call scrape function with location
        else:
            # Display message if keyword is not provided
            results = [{'position': 'N/A', 'url': 'N/A', 'title': 'N/A', 'description': 'Please fill out the keyword field.'}]
    # Render the HTML template with the results
    return render_template_string(HTML_TEMPLATE, results=results)

# Function to scrape Google search results
def scrape_google_results(keyword, location=None):
    # Construct the search query
    query = f'{keyword}' if location is None else f'{keyword} {location}'
    url = f'https://www.google.com/search?q={query}&num=30'  # URL for Google search with 30 results
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)  # Send the request to Google
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the response with BeautifulSoup
    
    results = []  # Initialize results list
    # Iterate over search results and extract information
    for i, result in enumerate(soup.select('.tF2Cxc'), start=1):
        title = result.select_one('.DKV0Md').get_text() if result.select_one('.DKV0Md') else 'No title'  # Extract title
        description = result.select_one('.IsZvec').get_text() if result.select_one('.IsZvec') else 'No description'  # Extract description
        url = result.select_one('.yuRUbf a')['href'] if result.select_one('.yuRUbf a') else 'No URL'  # Extract URL
        # Append the extracted data to results list
        results.append({
            'position': i,
            'url': url,
            'title': title,
            'description': description
        })
    return results  # Return the results list

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
