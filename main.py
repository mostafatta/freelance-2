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
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging

class NoonScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("جمع بيانات منتجات نون")
        self.root.geometry("500x400")
        
        # Variables
        self.product_name = tk.StringVar()
        self.max_sellers = tk.IntVar(value=5)
        self.scraping = False
        self.progress_value = tk.IntVar(value=0)
        
        # GUI Elements
        self.create_widgets()
        
        # Scraper variables
        self.driver = None
        self.all_products = []
        self.seller_names = set()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product name
        ttk.Label(main_frame, text="اسم المنتج:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        product_entry = ttk.Entry(main_frame, textvariable=self.product_name, width=40)
        product_entry.grid(row=0, column=1, sticky=tk.EW, pady=(0, 5))
        
        # Number of sellers
        ttk.Label(main_frame, text="عدد البائعين:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        sellers_spin = ttk.Spinbox(main_frame, from_=1, to=50, textvariable=self.max_sellers, width=5)
        sellers_spin.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Start button
        start_btn = ttk.Button(main_frame, text="بدء الجمع", command=self.start_scraping_thread)
        start_btn.grid(row=2, column=0, columnspan=2, pady=(10, 20))
        
        # Progress bar
        ttk.Label(main_frame, text="التقدم:").grid(row=3, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, 
                                           length=300, mode='determinate',
                                           variable=self.progress_value)
        self.progress_bar.grid(row=3, column=1, sticky=tk.EW, pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="جاهز للبدء", foreground="gray")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def start_scraping_thread(self):
        if not self.scraping:
            if not self.product_name.get():
                messagebox.showerror("خطأ", "الرجاء إدخال اسم المنتج")
                return
                
            self.scraping = True
            self.all_products = []
            self.seller_names = set()
            self.progress_value.set(0)
            self.status_label.config(text="جاري البدء...", foreground="black")
            
            # Start scraping in a separate thread
            threading.Thread(target=self.scrape_noon, daemon=True).start()
        else:
            messagebox.showinfo("معلومة", "جاري جمع البيانات بالفعل")
    
    def update_progress(self, value, max_value):
        self.progress_value.set(value)
        self.progress_bar['maximum'] = max_value
        self.status_label.config(text=f"تم العثور على {value} من {max_value} بائعين")
        
    def setup_driver(self):
        options = Options()
        
        # Headless configuration
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Make headless browser appear more like a regular user
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Disable extensions and enable JavaScript
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        
        # Additional options to prevent detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images to make scraping faster (optional)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.javascript": 1
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Additional JavaScript evasions
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return WebDriverWait(self.driver, 20)  # Increased timeout
        except Exception as e:
            print(f"Error initializing driver: {e}")
            raise
    
    def get_product_seller(self, url, product_name):
        try:
            # Open product page in new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(url)
            time.sleep(2)  # Added delay for page load
            
            divs = self.driver.find_elements(By.CLASS_NAME, "Nudges_nudgeText__cWC9q.Nudges_isPdp__uEFfk")
            
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
                wait = WebDriverWait(self.driver, 15)
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

                if seller_name not in self.seller_names:
                    # Open the seller page
                    a_tag = self.driver.find_element(By.CSS_SELECTOR, 'a.PartnerRatings_partnerRatingsCtr__ofBys')
                    href = a_tag.get_attribute('href')
                    seller_url = href if href else None

                    if seller_url:
                        self.driver.execute_script("window.open('');")
                        self.driver.switch_to.window(self.driver.window_handles[2])
                        self.driver.get(seller_url)
                        time.sleep(3)

                        # Scrape the seller page
                        seller_page_soup = BeautifulSoup(self.driver.page_source, 'html.parser')

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
                        self.all_products.append({
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

                        self.seller_names.add(seller_name)
                        
                        # Update progress in GUI
                        self.root.after(0, self.update_progress, len(self.seller_names), self.max_sellers.get())

                        # Close seller tab and switch back
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        
                        # Check if we've reached the desired number of sellers
                        if len(self.seller_names) >= self.max_sellers.get():
                            return True
                    else:
                        print("❌ No seller URL found")
                else:
                    print(f"✅ Already visited seller: {seller_name}")

            except Exception as e:
                print(f"❌ Error finding seller name: {e}")

            # Close product tab and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return False

        except Exception as e:
            print(f"❌ Error extracting seller data: {e}")
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return False

    def scrape_noon(self):
        product_name = self.product_name.get()
        max_sellers = self.max_sellers.get()
        
        try:
            self.root.after(0, self.status_label.config, {"text": "جاري إعداد المتصفح...", "foreground": "black"})
            wait = self.setup_driver()
            
            search_url = f"https://www.noon.com/saudi-ar/search/?q={product_name.replace(' ', '%20')}"
            
            try:
                self.driver.get(search_url)
                # Wait for either the content or a potential error page
                WebDriverWait(self.driver, 20).until(
                    lambda d: d.find_elements(By.CLASS_NAME, "ProductBoxLinkHandler_linkWrapper__b0qZ9") or 
                             d.find_elements(By.XPATH, "//*[contains(text(), 'Access Denied')]")
                )
                
                # Check if we got an access denied message
                if self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Access Denied')]"):
                    raise Exception("تم حظر الوصول إلى الموقع (Access Denied)")
                    
            except Exception as e:
                # Take screenshot for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.driver.save_screenshot(f"error_{timestamp}.png")
                raise Exception(f"فشل تحميل الصفحة: {str(e)}")
            
            current_page = 1
            while len(self.seller_names) < max_sellers:
                print(f"🔄 Processing page {current_page}... (Found {len(self.seller_names)}/{max_sellers} sellers)")
                self.root.after(0, self.status_label.config, 
                               {"text": f"جاري معالجة الصفحة {current_page}... تم العثور على {len(self.seller_names)}/{max_sellers} بائعين", 
                                "foreground": "black"})
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                product_cards = soup.find_all('div', class_="ProductBoxLinkHandler_linkWrapper__b0qZ9")

                if not product_cards:
                    self.root.after(0, self.status_label.config, 
                                  {"text": "لا توجد منتجات في هذه الصفحة", "foreground": "red"})
                    print("❌ No products found on this page.")
                    break

                for card in product_cards:
                    if len(self.seller_names) >= max_sellers:
                        break
                        
                    product_name_element = card.find('h2', {"data-qa": "product-name"})
                    current_product_name = product_name_element.text.strip() if product_name_element else "Unknown Product"
                    link = card.find('a', class_='ProductBoxLinkHandler_productBoxLink__FPhjp')
                    href = link.get('href') if link else None
                    product_url = f"https://www.noon.com{href}" if href else None

                    if product_url:
                        if self.get_product_seller(product_url, current_product_name):
                            break  # Reached desired number of sellers

                # Navigate to next page if needed
                if len(self.seller_names) < max_sellers:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        next_button.click()
                        current_page += 1
                        time.sleep(3)
                    except Exception as e:
                        self.root.after(0, self.status_label.config, 
                                        {"text": "لا توجد صفحات أخرى متاحة", "foreground": "red"})
                        print(f"❌ Next button not found or can't be clicked: {e}")
                        break

        except Exception as e:
            self.root.after(0, self.status_label.config, 
                           {"text": f"خطأ: {str(e)}", "foreground": "red"})
            print(f"Error loading page: {e}")

        finally:
            # Save data
            if self.all_products:
                df = pd.DataFrame(self.all_products)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_name = f'noon_{product_name}_sellers_data_{timestamp}.xlsx'
                
                with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                success_msg = f"تم جمع بيانات {len(self.seller_names)} بائع بنجاح. تم الحفظ في ملف {file_name}"
                self.root.after(0, self.status_label.config, 
                              {"text": success_msg, "foreground": "green"})
                print(f"✅ {success_msg}")
                messagebox.showinfo("نجاح", success_msg)
            else:
                self.root.after(0, self.status_label.config, 
                              {"text": "لم يتم جمع أي بيانات", "foreground": "red"})
                print("❌ No data collected to save")

            self.scraping = False
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NoonScraperGUI(root)
    root.mainloop()