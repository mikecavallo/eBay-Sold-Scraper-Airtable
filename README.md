# Sold Scraper Airtable

This Python script is used to scrape sold listings from a website and store them in an Airtable. It generates random searches based on categories, generates URLs for sold listings, and then adds each listing to an Airtable.

## How to Run

1. Ensure you have Python installed on your machine.
2. Install the necessary Python packages by running `pip install -r requirements.txt` in your terminal.
3. Run the script with `python sold_scraper_airtable.py`.

## Code Overview

The script consists of several functions that perform the following tasks:

- `generate_random_search_via_category(category)`: Generates random searches based on the provided category.
- `generate_sold_listings_url(query)`: Generates URLs for sold listings based on the provided query.
- `add_listing_to_table(listing)`: Adds a listing to the Airtable.

The script runs in an infinite loop, continuously generating searches, URLs, and adding listings to the Airtable.