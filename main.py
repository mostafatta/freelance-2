from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time

# Get user inputs
product_name = input("Enter the product name to search for: ")
max_sellers = int(input("Enter the number of unique sellers you want to scrape: "))

# Setup Chrome options
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
all_products = []  # To store all products and their seller info
seller_names = set()  # To avoid duplicate seller data
wait = WebDriverWait(driver, 15)

def get_product_seller(url, product_name):
    try:
        # Open product page in new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)
        divs = driver.find_elements(By.CLASS_NAME, "Nudges_nudgeText__cWC9q.Nudges_isPdp__uEFfk")
        
        target_div = None

        for div in divs:
            try:
                if "مؤخرًا" in div.text:
                    target_div = div
                    break
            except Exception as e:
                print(f"Error while processing div: {e}")
                continue

        amount_sold = "Not found"
        if target_div:
            amount_sold = target_div.text.strip()
            print(amount_sold)
        else:
            print("Target div not found.")
        
        # Price and other details extraction
        try:
            price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".PriceOffer_priceNowText__08sYH")))
            price = price.text.strip() if price else "Not found"
        except Exception as e:
            price = "Not found"
            print(f"Error finding price: {e}")

        try:
            rating = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".RatingPreviewStar_text__ZO_T7")))
            rating = rating.text.strip() if rating else "Not found"
        except Exception as e:
            rating = "Not found"
            print(f"Error finding rating: {e}")

        try:
            rating_count = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".RatingPreviewStar_countText__MdxCQ")))
            rating_count = rating_count.text.strip() if rating_count else "Not found"
        except Exception as e:
            rating_count = "Not found"
            print(f"Error finding rating count: {e}")
        
        product_url = url
        
        # Collect seller information
        try:
            seller_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".PartnerRatings_allOffers__bjHvU")))
            seller_name = seller_name_element.text.strip()
            print(f"🛒 Found seller: {seller_name}")

            if seller_name not in seller_names:
                # Open the seller page
                a_tag = driver.find_element(By.CSS_SELECTOR, 'a.PartnerRatings_partnerRatingsCtr__ofBys')
                href = a_tag.get_attribute('href')
                seller_url = href if href else None

                if seller_url:
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[2])
                    driver.get(seller_url)
                    time.sleep(3)

                    # Scrape the seller page
                    seller_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Collect seller details
                    geo = seller_page_soup.find('div', class_='SellerDetails_profileAddress__F8cju')
                    geolocation = geo.find('a').text.strip() if geo and geo.find('a') else "Not found"
                    google_map_link = geo.find('a')['href'] if geo and geo.find('a') else "Not found"
                    
                    phone_div = seller_page_soup.find('div', class_='SellerDetails_profileCall__kQnQg')
                    phone_number = phone_div.find('a').text.strip() if phone_div and phone_div.find('a') else "Not found"
                    
                    email_div = seller_page_soup.find('div', class_='SellerDetails_profileEmail__H3znZ')
                    email = email_div.find('a').text.strip() if email_div and email_div.find('a') else "Not found"
                    
                    spans = seller_page_soup.find_all('span', class_='Skeleton_skeletonWrapper__QaWR9 Skeleton_wrapper__dQPwT')
                    seller_rating = spans[0].text.strip() if len(spans) > 0 else "Not found"
                    number_of_ratings = spans[1].text.strip() if len(spans) > 1 else "Not found"
                    
                    number_of_clients_div = seller_page_soup.find('div', class_='SellerCustomersCard_customerValue__1pC30')
                    number_of_clients = number_of_clients_div.text.strip() if number_of_clients_div else "Not found"

                    # Append product and seller details
                    all_products.append({
                        'اسم المنتج': product_name,
                        'سعر المنتج': price,
                        'عدد مبيعات المنتج مؤخرا': amount_sold,
                        "تقييم المنتج": rating,
                        "عدد تقييمات المنتج": rating_count,
                        "رابط المنتج": product_url,
                        'اسم البائع': seller_name,
                        'رابط البائع': seller_url,
                        'الموقع الجغرافي': geolocation,
                        'رابط الموقع الجغرافي': google_map_link,
                        'رقم الهاتف': phone_number,
                        'البريد الإلكتروني': email,
                        'تقييم البائع': seller_rating,
                        'عدد تقييمات البائع': number_of_ratings,
                        'عدد عملاء البائع': number_of_clients,
                    })

                    seller_names.add(seller_name)

                    # Close seller tab and switch back
                    driver.close()
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Check if we've reached the desired number of sellers
                    if len(seller_names) >= max_sellers:
                        return True
                else:
                    print("❌ No seller URL found")
            else:
                print(f"✅ Already visited seller: {seller_name}")

        except Exception as e:
            print(f"❌ Error finding seller name: {e}")

        # Close product tab and switch back
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return False

    except Exception as e:
        print(f"❌ Error extracting seller data: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False

# Function to repeatedly click the 'Check availability' and 'OK' buttons
def repeatedly_click_buttons():
    try:
        start_time = time.time()
        while time.time() - start_time < 300:  # 5 minutes
            try:
                # Find and click 'Check availability' button
                check_availability_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Check availability')]")))
                check_availability_button.click()
                print("Clicked 'Check availability' button.")

                # Wait for the 'OK' button to become clickable and then click it
                ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
                ok_button.click()
                print("Clicked 'OK' button.")
                
                time.sleep(2)  # Wait 2 seconds before repeating

            except Exception as e:
                print(f"❌ Error while clicking buttons: {e}")
                break

    except Exception as e:
        print(f"❌ Error in the repeating click function: {e}")

# Main scraping function
def scrape_noon(product_name, max_sellers):
    try:
        search_url = f"https://www.noon.com/saudi-ar/search/?q={product_name.replace(' ', '%20')}"
        driver.get(search_url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ProductBoxLinkHandler_linkWrapper__b0qZ9")))
        
        current_page = 1
        while len(seller_names) < max_sellers:
            print(f"🔄 Processing page {current_page}... (Found {len(seller_names)}/{max_sellers} sellers)")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_cards = soup.find_all('div', class_="ProductBoxLinkHandler_linkWrapper__b0qZ9")

            if not product_cards:
                print("❌ No products found on this page.")
                break

            for card in product_cards:
                if len(seller_names) >= max_sellers:
                    break
                    
                product_name_element = card.find('h2', {"data-qa": "product-name"})
                current_product_name = product_name_element.text.strip() if product_name_element else "Unknown Product"
                link = card.find('a', class_='ProductBoxLinkHandler_productBoxLink__FPhjp')
                href = link.get('href') if link else None
                product_url = f"https://www.noon.com{href}" if href else None

                if product_url:
                    if get_product_seller(product_url, current_product_name):
                        break  # Reached desired number of sellers

            # Navigate to next page if needed
            if len(seller_names) < max_sellers:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    next_button.click()
                    current_page += 1
                    time.sleep(3)
                except Exception as e:
                    print(f"❌ Next button not found or can't be clicked: {e}")
                    break

    except Exception as e:
        print(f"Error loading page: {e}")

    finally:
        # Save data
        if all_products:
            df = pd.DataFrame(all_products)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f'noon_{product_name}_sellers_data_{timestamp}.xlsx'  # Fixed the issue here
            
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            print(f"✅ Successfully collected {len(seller_names)} sellers. Data saved to {file_name}")
        else:
            print("❌ No data collected to save")

        driver.quit()

# Start scraping
print(f"🚀 Starting Noon scraper for: '{product_name}' (Target: {max_sellers} sellers)")
scrape_noon(product_name, max_sellers)
