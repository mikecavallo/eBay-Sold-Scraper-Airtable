import requests
from lxml import html
from openai import OpenAI
import random
from pyairtable import Api
from os import environ
api_key = environ.get('OPENAI_API_KEY')
client = OpenAI(api_key)

class Listing:
    def __init__(self, category, title, price, date):
        self.category = category
        self.title = title
        self.price = price
        self.date = date
        
    def __repr__(self):
        return f"Listing(category='{self.category}, title='{self.title}', price='{self.price}', date='{self.date}')"
    
search_queries = []

category_list = [
    # Collectibles & Art
    "Antiques",
    "Art",
    "Coins & Paper Money",
    "Collectibles",
    "Entertainment Memorabilia",
    "Pottery & Glass",
    "Stamps",
    "Trading Cards",

    # Electronics
    "Audio",
    "Cameras & Photo",
    "Cell Phones & Accessories",
    "Computers/Tablets & Networking",
    "Home Audio & Theater",
    "Major Appliances",
    "Small Appliances",
    "TV, Video & Home Audio",
    "Video Games & Consoles",

    # Home & Garden
    "Appliances",
    "Bedding & Bath",
    "Furniture",
    "Home Décor",
    "Home Improvement",
    "Kitchen & Dining",
    "Patio, Lawn & Garden",
    "Tools",
    "TVs & Home Theater",

    # Clothing, Shoes & Accessories
    "Accessories",
    "Clothing",
    "Shoes",
    "Jewelry & Watches",

    # Toys & Hobbies
    "Action Figures & Collectibles",
    "Baby & Toddler Toys",
    "Dolls & Bears",
    "Educational Toys",
    "Games & Puzzles",
    "Hobbies & Crafts",
    "Model Kits & Vehicles",
    "Outdoor Toys & Structures",
    "Radio Control Toys",
    "Sports & Outdoor Recreation",
    "Stuffed Animals & Plush Toys",

    # Sporting Goods
    "Exercise & Fitness",
    "Golf",
    "Hunting",
    "Outdoor Sports",
    "Sports Apparel & Collectibles",
    "Tennis & Racquet Sports",
    "Team Sports",

    # Books, Movies & Music
    "Books",
    "DVDs & Movies",
    "Music",
    'Childrens Chapter Books',
    'Kids Book Lots',
    'Childrens Chapter Book Lot',
    'Kids Book Lot',

    # Other categories
    "Business & Industrial",
    "Health & Beauty",
    "Pet Supplies",
    "Sports Mem, Cards & Fan Shop",
]

categories = random.sample(category_list, 3)
urls = []
listings = []

def generate_random_search_via_category(category):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful eBay assistant who provides 2 random descriptive ebay searches when given a category by the user. List them one per line only the query on each line. Do not prepend query with any numbers or symbols. Each query should be no longer than 75 characters"},
                {"role": "user", "content": category}
            ]
        )
    except Exception as e:
        print(f"Error generating random search via category: {e}")

    queries = completion.choices[0].message.content.strip().split('\n')
    # Append queries to the list along with the category
    for query in queries:
        if query:  # Check if the query is not empty
            search_queries.append(f'{category}: {query}')
        

def generate_sold_listings_url(query, new=False):
    """
    Generates the URL for sold listings on eBay based on the search keywords and condition of the item.
    
    Args:
        search_keywords (str): The keywords to search for.
        new (bool, optional): Whether the item is new. Defaults to False.
        Returns:
        str: The URL for sold listings on eBay.
    """""
    print("Generating sold listings URL...")
    query_string = query.split(":")
    base_url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw="
    sold_listings_params = "&_sacat=0&LH_TitleDesc=1&LH_Complete=1&LH_Sold=1&_ipg=240"
    new_condition_param = "&LH_ItemCondition=1000"
    url_query = query_string[1].strip().replace(' ', '+')
    sold_url = base_url + url_query + sold_listings_params
    if new:
        sold_url += new_condition_param
    
    fetch_data(query_string[0], sold_url) 


def fetch_data(category, url):

    # Fetch the HTML content
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content
    doc = html.fromstring(html_content)

    for li in doc.xpath('//ul/li'):
        # Extract the date
        date_text = li.xpath('.//span[@class="POSITIVE"]/text()')
        if not date_text:
            continue
        date = date_text[0].replace('Sold', '').strip()

        # Extract the title
        title = li.xpath('.//div[@class="s-item__title"]/span/text()')
        if not title:
            continue
        title = title[0]

        # Extract the price
        price_elements = li.xpath('.//span[@class="s-item__price"]/span/text()')
        if not price_elements:
            continue
        price = price_elements[0]

        # All conditions met, create and add the Listing object
        listing = Listing(category, title, price, date)
        listings.append(listing)

    # Print or process the listings
    for listing in listings:
        print(listing)

for query in search_queries:
    generate_sold_listings_url(query)
    
base_id = 'appDSg5XdN5KywBSW'
table_name = 'Solds'
airtable_api_key = environ.get('AIRTABLE_API_KEY')
# Initialize an Airtable object
api = Api(airtable_api_key)
table = api.table(base_id, table_name)

# Function to add a listing to the 'Solds' table
def add_listing_to_table(listing):

    # Create a record with the listing details
    records = [{
            'fields': {
            'Title': listing.title,
            'Price': listing.price,
            'Sold Date': listing.date,
            'Category': listing.category,
            }
    }]

    # Add the record to the Airtable
    try:    
        table.batch_upsert(records, key_fields=['Title', 'Price', 'Sold Date'], typecast=True)
    except Exception as e:
        print(f"Error adding listing to table: {e}")

# Main execution
if __name__ == "__main__":
    while True:
        # Generate 3 random searches for each category
        for category in categories:
            generate_random_search_via_category(category)
        
        # Generate the sold listings URLs for each search query
        for query in search_queries:
            generate_sold_listings_url(query)
        
        # Iterate over your listings and add them to the table
        for listing in listings:
            add_listing_to_table(listing)   

        # Iterate over your listings and add them to the table
        # Note: This seems to be a duplicate of the previous loop and may not be necessary
        for listing in listings:
            add_listing_to_table(listing)

