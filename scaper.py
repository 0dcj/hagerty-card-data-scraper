from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.webdriver.chrome.options import Options

# Configure WebDriver options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Disable GPU for compatibility

# Initialize WebDriver
driver = webdriver.Chrome(options=options)
driver.get('https://www.hagerty.com/marketplace/search?forSale=false')

# Wait for elements to load
wait = WebDriverWait(driver, 10)

# Use a set to store unique car data
car_data = set()


def scrape():
    """Scrape car details from the current page."""
    try:
        # Wait for all car cards to load
        car_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.AuctionCard_auction-card__content__DBsKd'))
        )
        for card in car_cards:
            try:
                # Extract car details
                model = card.find_element(By.CLASS_NAME, 'AuctionCard_auction-card__title__IfwBE').text
                date = card.find_element(By.CLASS_NAME, 'AuctionCard_auction-card__end-date__xA1ux').text
                status = card.find_element(By.CLASS_NAME, 'AuctionBadge_auction-badge__title___jjEp').text

                # Add data to the set (removes duplicates automatically)
                car_data.add((model, date, status))
            except Exception as inner_error:
                print(f"Error extracting data from a card: {inner_error}")
    except Exception as e:
        print(f"Error during scraping: {e}")


def scroll_and_scrape():
    """Scroll through the page and scrape data."""
    while True:
        scrape()  # Extract data from the current page
        try:
            # Find and click the 'Load More' button
            scroll_button = driver.find_element(
                By.CSS_SELECTOR,
                "button[class='Button_button__0ZEtq Button_button--primary__WxAmE Button_button--outlined__rnUkt Button_button--large__Zx0HT MarketplaceSearch_marketplace-search__button__v2_xJ']"
            )
            driver.execute_script("arguments[0].click();", scroll_button)
            wait.until(EC.staleness_of(scroll_button))  # Wait for new content to load
        except Exception:
            print("No more 'Load More' button or an error occurred.")
            break


if __name__ == '__main__':
    scroll_and_scrape()

    # Save data to a CSV file
    with open('car_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Model', 'Date', 'Price/Status'])  # Write header
        writer.writerows(car_data)  # Write data rows

    print(f"Data extraction complete. Saved to 'car_data.csv'. Total cars processed: {len(car_data)}")

    driver.quit()
