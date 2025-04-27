# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# import datetime

# # Setup Chrome options
# options = Options()
# options.add_experimental_option("detach", True)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# all_products = []  # To store all products and their seller info
# seller_names = set()  # To avoid duplicate seller data
# wait = WebDriverWait(driver, 15)

# def get_product_seller(url, product_name):
#     try:
#         driver.execute_script("window.open('');")
#         driver.switch_to.window(driver.window_handles[1])
#         driver.get(url)
        
#         # Collect seller information
#         try:
#             seller_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".PartnerRatings_allOffers__bjHvU")))
#             seller_name = seller_name_element.text.strip()
#             print(f"🛒 Found seller: {seller_name}")

#             if seller_name not in seller_names:
#                 # Open the seller page
#                 a_tag = driver.find_element(By.CSS_SELECTOR, 'a.PartnerRatings_partnerRatingsCtr__ofBys')
#                 href = a_tag.get_attribute('href')
#                 seller_url = href if href else None

#                 driver.execute_script("window.open('');")
#                 driver.switch_to.window(driver.window_handles[2])
#                 driver.get(seller_url)
#                 time.sleep(3)

#                 # Scrape the seller page for additional details
#                 seller_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

#                 # Collect geolocation
#                 geo = seller_page_soup.find('div', class_='SellerDetails_profileAddress__F8cju')
#                 geolocation = geo.find('a').text.strip() if geo else "Not found"
                
#                 # Collect phone number
#                 phone_div = seller_page_soup.find('div', class_='SellerDetails_profileCall__kQnQg')
#                 phone_number = phone_div.find('a').text.strip() if phone_div else "Not found"
                
#                 # Collect email
#                 email_div = seller_page_soup.find('div', class_='SellerDetails_profileEmail__H3znZ')
#                 email = email_div.find('a').text.strip() if email_div else "Not found"
                
#                 # Collect rating
#                 rating_span = seller_page_soup.find('span', class_='Skeleton_skeletonWrapper__QaWR9Skeleton_wrapper__dQPwT')
#                 rating = rating_span.text.strip() if rating_span else "Not found"
                
#                 # Collect number of ratings
#                 number_of_ratings_span = seller_page_soup.find('span', class_='Skeleton_skeletonWrapper__QaWR9 Skeleton_wrapper__dQPwT')
#                 number_of_ratings = number_of_ratings_span.text.strip() if number_of_ratings_span else "Not found"
                
#                 # Collect number of clients
#                 number_of_clients_div = seller_page_soup.find('div', class_='SellerCustomersCard_customerValue__1pC30')
#                 number_of_clients = number_of_clients_div.text.strip() if number_of_clients_div else "Not found"

#                 # Append product and seller details to the list
#                 all_products.append({
#                     'اسم المنتج': product_name,
#                     'اسم البائع': seller_name,
#                     'رابط البائع': seller_url,
#                     'الموقع الجغرافي': geolocation,
#                     'رقم الهاتف': phone_number,
#                     'البريد الإلكتروني': email,
#                     'التقييم': rating,
#                     'عدد التقييمات': number_of_ratings,
#                     'عدد العملاء': number_of_clients,
#                 })

#                 seller_names.add(seller_name)

#                 driver.close()
#                 driver.switch_to.window(driver.window_handles[1])

#             else:
#                 print(f"✅ Already visited seller: {seller_name}")

#         except Exception as e:
#             print(f"❌ Error finding seller name: {e}")
#             return None

#     except Exception as e:
#         print(f"❌ Error extracting seller data: {e}")
#         return None

# # Main scraping loop
# try:
#     driver.get("https://www.noon.com/saudi-ar/search/?q=افالو فارما")
#     wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ProductBoxLinkHandler_linkWrapper__b0qZ9")))
    
#     current_page = 1
#     max_page = 3  # Max pages to scrape
#     while current_page <= max_page:
#         print(f"🔄 Processing page {current_page}...")
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)

#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         product_cards = soup.find_all('div', class_="ProductBoxLinkHandler_linkWrapper__b0qZ9")

#         if not product_cards:
#             print("❌ No products found on this page.")
#             break

#         for card in product_cards:
#             product_name = card.find('h2', {"data-qa": "product-name"}).text.strip()
#             link = card.find('a', class_='ProductBoxLinkHandler_productBoxLink__FPhjp')
#             href = link.get('href') if link else None
#             product_url = f"https://www.noon.com{href}" if href else None

#             if product_url:
#                 get_product_seller(product_url, product_name)

#         # Navigate to the next page
#         try:
#             next_button = driver.find_element(By.CSS_SELECTOR, ".pagination-next")
#             if next_button.is_enabled():
#                 next_button.click()
#                 time.sleep(3)
#             else:
#                 print("⚠️ No next page available.")
#                 break
#         except Exception as e:
#             print(f"❌ Couldn't find next button: {e}")
#             break

#         current_page += 1

# except Exception as e:
#     print(f"Error loading page: {e}")
#     driver.quit()
#     exit(1)

# # Save data to Excel file
# df = pd.DataFrame(all_products)
# df.to_excel('product_sellers_data.xlsx', index=False, encoding='utf-8-sig')
# print("✅ All data saved to product_sellers_data.xlsx")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime

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
        #Nudges_nudgeText__cWC9q Nudges_isPdp__uEFfk
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)
        amount_sold = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".Nudges_nudgeText__cWC9q.Nudges_isPdp__uEFfk")))
        amount_sold = amount_sold.text.strip() if amount_sold else "Not found"
        #PriceOffer_priceNowText__08sYH
        price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".PriceOffer_priceNowText__08sYH")))
        price = price.text.strip() if price else "Not found"
        #RatingPreviewStar_text__ZO_T7
        rating = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".RatingPreviewStar_text__ZO_T7")))
        rating = rating.text.strip() if rating else "Not found"
        #RatingPreviewStar_countText__MdxCQ
        rating_count = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".RatingPreviewStar_countText__MdxCQ")))
        rating_count = rating_count.text.strip() if rating_count else "Not found"
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

                if seller_url:  # Only open seller page if URL exists
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[2])
                    driver.get(seller_url)
                    time.sleep(3)

                    # Scrape the seller page for additional details
                    seller_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Collect geolocation
                    geo = seller_page_soup.find('div', class_='SellerDetails_profileAddress__F8cju')
                    geolocation = geo.find('a').text.strip() if geo and geo.find('a') else "Not found"
                    google_map_link = geo.find('a')['href'] if geo and geo.find('a') else "Not found"
                    
                    # Collect phone number
                    phone_div = seller_page_soup.find('div', class_='SellerDetails_profileCall__kQnQg')
                    phone_number = phone_div.find('a').text.strip() if phone_div and phone_div.find('a') else "Not found"
                    
                    # Collect email
                    email_div = seller_page_soup.find('div', class_='SellerDetails_profileEmail__H3znZ')
                    email = email_div.find('a').text.strip() if email_div and email_div.find('a') else "Not found"
                    
                    # Collect rating
                    # rating_span = seller_page_soup.find('span', class_='Skeleton_skeletonWrapper__QaWR9Skeleton_wrapper__dQPwT')
                    # rating = rating_span.text.strip() if rating_span else "Not found"
                    
                    # # Collect number of ratings
                    # number_of_ratings_span = seller_page_soup.find('span', class_='Skeleton_skeletonWrapper__QaWR9 Skeleton_wrapper__dQPwT')
                    # number_of_ratings = number_of_ratings_span.text.strip() if number_of_ratings_span else "Not found"
                    spans = seller_page_soup.find_all('span', class_='Skeleton_skeletonWrapper__QaWR9 Skeleton_wrapper__dQPwT')
                    rating = spans[0].text.strip() if len(spans) > 0 else "Not found"
                    number_of_ratings = spans[1].text.strip() if len(spans) > 1 else "Not found"
                    
                    # Collect number of clients
                    number_of_clients_div = seller_page_soup.find('div', class_='SellerCustomersCard_customerValue__1pC30')
                    number_of_clients = number_of_clients_div.text.strip() if number_of_clients_div else "Not found"

                    # Append product and seller details to the list
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
                        'التقييم': rating,
                        'عدد التقييمات': number_of_ratings,
                        'عدد العملاء': number_of_clients,
                    })

                    seller_names.add(seller_name)

                    # Close seller tab and switch back to product tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[1])
                else:
                    print("❌ No seller URL found")
            else:
                print(f"✅ Already visited seller: {seller_name}")

        except Exception as e:
            print(f"❌ Error finding seller name: {e}")

        # Close product tab and switch back to main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"❌ Error extracting seller data: {e}")
        # Ensure we don't leave stray tabs open
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

# Main scraping loop
try:
    driver.get("https://www.noon.com/saudi-ar/search/?q=افالو فارما")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ProductBoxLinkHandler_linkWrapper__b0qZ9")))
    
    current_page = 1
    max_page = 7  # Max pages to scrape
    while current_page <= max_page:
        print(f"🔄 Processing page {current_page}...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_cards = soup.find_all('div', class_="ProductBoxLinkHandler_linkWrapper__b0qZ9")

        if not product_cards:
            print("❌ No products found on this page.")
            break

        for card in product_cards:
            product_name_element = card.find('h2', {"data-qa": "product-name"})
            product_name = product_name_element.text.strip() if product_name_element else "Unknown Product"
            link = card.find('a', class_='ProductBoxLinkHandler_productBoxLink__FPhjp')
            href = link.get('href') if link else None
            product_url = f"https://www.noon.com{href}" if href else None

            if product_url:
                get_product_seller(product_url, product_name)

        # Navigate to the next page
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            current_page += 1
            time.sleep(3)  # Wait for page to load
        except Exception as e:
            print(f"❌ Next button not found or can't be clicked: {e}")
            break

except Exception as e:
    print(f"Error loading page: {e}")

finally:
    # Save data to Excel file
    if all_products:
        df = pd.DataFrame(all_products)
        # For Arabic text in Excel, we'll use utf-8-sig encoding when saving
        with pd.ExcelWriter('product_sellers_data.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        print("✅ All data saved to product_sellers_data.xlsx")
    else:
        print("❌ No data collected to save")
    
    driver.quit()