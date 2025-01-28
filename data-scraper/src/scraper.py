import os
import time
import schedule
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class DataScraper:
    def __init__(self):
        # MongoDB connection
        mongodb_uri = os.getenv('MONGODB_URI')
        self.client = MongoClient(mongodb_uri)
        self.db = self.client['scantether']
        self.collection = self.db['scraped_data']

    def scrape_data(self):
        try:
            # Example: Scraping a simple webpage
            url = "https://www.google.com"  # Replace with your target URL
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example data extraction
            data = {
                'title': soup.title.string if soup.title else None,
                'timestamp': datetime.utcnow(),
                # Add more fields as needed
            }
            
            # Store in MongoDB
            self.collection.insert_one(data)
            print(f"Data scraped successfully at {datetime.utcnow()}")
            
        except Exception as e:
            print(f"Error scraping data: {str(e)}")

    def run(self):
        # Schedule the scraping job to run every hour
        schedule.every(1).hours.do(self.scrape_data)
        
        # Run immediately on startup
        self.scrape_data()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scraper = DataScraper()
    scraper.run()
