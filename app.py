from flask import Flask, request, render_template_string, send_file
import requests
from bs4 import BeautifulSoup
import csv
from io import BytesIO, StringIO

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
                    <th>Image</th>
                    <th>Reviews</th>
                </tr>
                {% for result in results %}
                <tr>
                    <td>{{ result['position'] }}</td>
                    <td>{{ result['url'] }}</td>
                    <td>{{ result['title'] }}</td>
                    <td>{{ result['description'] }}</td>
                    <td>{% if result['image'] %}<img src="{{ result['image'] }}" alt="Image" width="100">{% else %}None{% endif %}</td>
                    <td>{{ result['reviews'] }}</td>
                </tr>
                {% endfor %}
            </table>
            <h2>Local Pack/Map Pack</h2>
            <table border="1">
                <tr>
                    <th>Business Name</th>
                    <th>URL</th>
                    <th>Address</th>
                    <th>Phone Number</th>
                    <th>Reviews</th>
                    <th>Opening Hours</th>
                </tr>
                {% for business in local_pack %}
                <tr>
                    <td>{{ business['name'] }}</td>
                    <td>{% if business['url'] != 'No URL' %}<a href="{{ business['url'] }}">{{ business['url'] }}</a>{% else %}No URL{% endif %}</td>
                    <td>{{ business['address'] }}</td>
                    <td>{{ business['phone'] }}</td>
                    <td>{{ business['reviews'] }}</td>
                    <td>{{ business['hours'] }}</td>
                </tr>
                {% endfor %}
            </table>
            <form method="POST" action="/export">
                <input type="hidden" name="keyword" value="{{ keyword }}">
                <input type="hidden" name="location" value="{{ location }}">
                <input type="hidden" name="ignore_location" value="{{ ignore_location }}">
                <button type="submit">Export to CSV</button>
            </form>
        {% endif %}
    </body>
</html>
'''

# Route for handling the home page and form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []  # Initialize results list
    local_pack = []  # Initialize local pack list
    keyword, location, ignore_location = None, None, None  # Ensure variables are always defined
    if request.method == 'POST':  # Check if the form is submitted via POST
        keyword = request.form.get('keyword')  # Get the keyword from the form
        location = request.form.get('location')  # Get the location from the form
        ignore_location = request.form.get('ignore_location')  # Check if the ignore location checkbox is checked
        if keyword:  # Check if keyword is provided
            if ignore_location:  # If ignore location is checked
                results, local_pack = scrape_google_results(keyword)  # Call scrape function without location
            else:
                results, local_pack = scrape_google_results(keyword, location)  # Call scrape function with location
        else:
            # Display message if keyword is not provided
            results = [{'position': 'N/A', 'url': 'N/A', 'title': 'N/A', 'description': 'Please fill out the keyword field.'}]
    # Render the HTML template with the results
    return render_template_string(HTML_TEMPLATE, results=results, local_pack=local_pack, keyword=keyword, location=location, ignore_location=ignore_location)

# Route for exporting results to CSV
@app.route('/export', methods=['POST'])
def export():
    keyword = request.form.get('keyword')
    location = request.form.get('location')
    ignore_location = request.form.get('ignore_location')
    if keyword:
        if ignore_location:
            results, local_pack = scrape_google_results(keyword)
        else:
            results, local_pack = scrape_google_results(keyword, location)
        
        # Create CSV data
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Position', 'URL', 'Meta Title', 'Meta Description', 'Image', 'Reviews'])
        for result in results:
            cw.writerow([result['position'], result['url'], result['title'], result['description'], result['image'], result['reviews']])
        
        cw.writerow([])  # Blank line before local pack data
        cw.writerow(['Business Name', 'URL', 'Address', 'Phone Number', 'Reviews', 'Opening Hours'])
        for business in local_pack:
            cw.writerow([business['name'], business['url'], business['address'], business['phone'], business['reviews'], business['hours']])
        
        # Get CSV content as string
        output = si.getvalue()
        si.close()
        
        # Convert string to bytes and write to BytesIO
        bio = BytesIO()
        bio.write(output.encode('utf-8'))
        bio.seek(0)
        
        # Send the CSV file as a response
        return send_file(
            bio,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'results_{keyword}.csv'
        )
    return "No keyword provided", 400

# Function to scrape Google search results
def scrape_google_results(keyword, location=None):
    # Construct the search query
    query = f'{keyword}' if location is None else f'{keyword} {location}'
    url = f'https://www.google.com/search?q={query}&num=100'  # URL for Google search with 30 results
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)  # Send the request to Google
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the response with BeautifulSoup
    
    results = []  # Initialize results list
    local_pack = []  # Initialize local pack list
    
    # Iterate over search results and extract information
    for i, result in enumerate(soup.select('.tF2Cxc'), start=1):
        title = result.select_one('.DKV0Md').get_text() if result.select_one('.DKV0Md') else 'No title'  # Extract title
        description = result.select_one('.IsZvec').get_text() if result.select_one('.IsZvec') else 'No description'  # Extract description
        url = result.select_one('.yuRUbf a')['href'] if result.select_one('.yuRUbf a') else 'No URL'  # Extract URL
        image = result.select_one('img')['src'] if result.select_one('img') else 'No image'  # Extract image URL
        reviews = result.select_one('.aCOpRe .f').get_text() if result.select_one('.aCOpRe .f') else 'No reviews'  # Extract reviews
        
        # Append the extracted data to results list
        results.append({
            'position': i,
            'url': url,
            'title': title,
            'description': description,
            'image': image,
            'reviews': reviews
        })
    
    # Extract Local Pack/Map Pack information
    for business in soup.select('.VkpGBb'):
        name = business.select_one('.dbg0pd').get_text() if business.select_one('.dbg0pd') else 'No name'
        url_elem = business.select_one('a')
        url = url_elem['href'] if url_elem and url_elem.has_attr('href') else 'No URL'
        address = business.select_one('.rllt__details div').get_text() if business.select_one('.rllt__details div') else 'No address'
        phone = business.select_one('.rllt__wrapped').get_text() if business.select_one('.rllt__wrapped') else 'No phone number'
        reviews = business.select_one('.rllt__wrapped .BTtC6e').get_text() if business.select_one('.rllt__wrapped .BTtC6e') else 'No reviews'
        hours = business.select_one('.rllt__details div:nth-of-type(3)').get_text() if business.select_one('.rllt__details div:nth-of-type(3)') else 'No hours'
        
        local_pack.append({
            'name': name,
            'url': url,
            'address': address,
            'phone': phone,
            'reviews': reviews,
            'hours': hours
        })
    
    return results, local_pack  # Return the results list and local pack list

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
