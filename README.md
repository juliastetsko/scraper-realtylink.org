# Apartment Spider

This Scrapy spider is designed to scrape apartment listings from realtylink.org.
It navigates through the listings using pagination, fetching details of each apartment.

## Installation

Make sure you have Python and Scrapy installed. You can install requirements using pip:

`pip install -r requirements.txt`


## Usage

To run the spider, navigate to the directory containing the spider code and run the following command:

`scrapy crawl apartment -o apartments.json`

This command will start the spider, scrape apartment data, and save it to a file named "apartments.json".