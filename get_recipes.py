from bs4 import BeautifulSoup
import urllib.request
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import os
from PIL import Image, ImageChops, ImageOps
import time

YOUR_ATK_EMAIL = 'test@test.com'
YOUR_ATK_PASSWORD = 'test_password'


def trim(im):
    # trims empty around image (based on color of upper left pixel)
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def format_images(index):
    # trims images and adds equal border around each, saves to new folder
    images = os.listdir('recipes/{0}'.format(index))
    length = len(images)
    digits = len(str(length))
    curr = 1

    print('Trimming...')

    for image in images:
        print('{0} / {1} | https://www.americastestkitchen.com/recipes/{2}'.format(
            str(curr).zfill(digits), length, image.replace('.png', '')))
        im = Image.open('./recipes/' + str(index) + '/' + image)

        border = (315, 209, 315, 0)  # left, up, right, bottom
        try:
            im = ImageOps.crop(im, border)
            color = im.getpixel((0, 0))
            im = trim(im)
            im = ImageOps.expand(im, 50, color)
            im.save('./recipes_trimmed/' + str(index) + '/' + image)
        except:
            print('failed')
        curr += 1


def save_recipes(page, index):

    driver = None

    # Create a new folder for specific page's recipes based on index (1, 2, 3, etc.)
    os.mkdir('./recipes/'+str(index))
    os.mkdir('./recipes_trimmed/'+str(index))

    def check_exists_by_class(class_name):
        # Check if a page element exists based on class name (return bool)
        try:
            driver.find_element(By.CLASS_NAME, class_name)
        except NoSuchElementException:
            return False
        return True

    print('Starting...')
    try:
        # Launch chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        cpath = "./chromedriver.exe"
        driver = webdriver.Chrome(cpath, options=chrome_options)

        # Load login page
        driver.get("https://www.americastestkitchen.com/sign_in")
        # Enter email address
        e = driver.find_element(By.ID, "email")
        e.send_keys(YOUR_ATK_EMAIL)
        # Enter password
        e = driver.find_element(By.NAME, "password")
        e.send_keys(YOUR_ATK_PASSWORD)
        # Click submit button
        e = driver.find_element(
            By.XPATH, r"//*[@id='app-content']/main/section/section/article[1]/form/fieldset/div[2]/button")
        e.click()
        time.sleep(10)
        # Load recipes page
        driver.get(page)
        # Refresh to prevent loading errors
        driver.refresh()
        time.sleep(15)
    except:
        print('fail')
        exit()

    # Check for "Load More Recipes" button and click it until all are loaded
    while check_exists_by_class('browse-load-more') == True:
        e = driver.find_element(By.CLASS_NAME, 'browse-load-more')
        try:
            e.click()
        except:
            # Sometimes a pop-up covers the screen, so we close that
            try:
                d = driver.find_element(By.CLASS_NAME, 'bx-button')
                d.click()
            except:
                # This is another pop-up that covers the screen, so we close that too
                try:
                    f = driver.find_element(By.CLASS_NAME, 'bx-close-link')
                    f.click()
                except:
                    # Other exceptions can be added here (additional pop-ups)
                    print('well shit')
        time.sleep(2)

    # Pass page source to beautiful soup so we can extract recipe links
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Build list of recipe links
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile("^\/recipes\/[0-9]")}):
        links.append(link.get('href'))

    # Variables for monitoring progress
    links = sorted(set(links))
    length = len(links)
    digits = len(str(length))
    curr = 1

    # Iterate over each recipe link
    for link in links:

        # Load the recipe
        print('{0} / {1} | https://www.americastestkitchen.com{2}'.format(
            str(curr).zfill(digits), length, link))
        if link == '/recipes/24-easy-caramel-sauce':
            link = '/recipes/10610-all-purpose-caramel-sauce'
            driver.get("https://www.cooksillustrated.com/recipes/10610-all-purpose-caramel-sauce")
        else:
            driver.get("https://www.americastestkitchen.com{0}".format(link))
        time.sleep(2)

        # Get the pixel height of page content for screenshot
        ele1 = driver.find_element(
            "xpath", '//*[@id="document-detail"]/div[1]')
        ele2 = driver.find_element(
            "xpath", '//*[@id="document-detail"]/div[2]/div[1]')
        ele3 = driver.find_element(
            "xpath", '//*[@id="document-detail"]/div[2]/div[2]')
        ele4 = driver.find_element(
            "xpath", '//*[@id="document-detail"]/div[2]/div[3]')
        total_height = ele1.size["height"]+ele2.size["height"] + \
            ele3.size["height"]+ele4.size["height"]+250

        # Set chrome window to 1920 x content height
        driver.set_window_size(1920, total_height)  # the trick
        time.sleep(2)

        # Save screenshot
        driver.save_screenshot(
            "./recipes/{0}/{1}.png".format(index, link.replace('/recipes/', '')))
        curr += 1

    # Close chrome
    if driver is not None:
        driver.close()

    format_images(index)


if __name__ == "__main__":
    pages = [
        # Cook It In Cast Iron
        'https://www.americastestkitchen.com/books/cook-it-in-cast-iron?q=&fR[search_browse_slugs][0]=cook-it-in-cast-iron&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Holiday
        'https://www.americastestkitchen.com/recipes/browse/holiday?q=&fR[search_browse_slugs][0]=holiday&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Perfect Cookie Cookbook
        'https://www.americastestkitchen.com/books/the-perfect-cookie?q=&fR[search_browse_slugs][0]=the-perfect-cookie&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Complete Vegetarian Cookbook
        'https://www.americastestkitchen.com/books/the-complete-vegetarian?q=&fR[search_browse_slugs][0]=the-complete-vegetarian&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Complete Slow Cooker Cookbook
        'https://www.americastestkitchen.com/books/the-complete-slow-cooker?q=&fR[search_browse_slugs][0]=the-complete-slow-cooker&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Grilling & BBQ
        'https://www.americastestkitchen.com/recipes/browse/grilling?q=&fR[search_browse_slugs][0]=grilling&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Desserts & Baked Goods
        'https://www.americastestkitchen.com/recipes/browse/desserts?q=&fR[search_browse_slugs][0]=desserts&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Bread, Sandwiches, & Pizza
        'https://www.americastestkitchen.com/recipes/browse/breads_sandwiches_pizza?q=&fR[search_browse_slugs][0]=breads_sandwiches_pizza&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Poultry
        'https://www.americastestkitchen.com/recipes/browse/poultry?q=&fR[search_browse_slugs][0]=poultry&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Meat
        'https://www.americastestkitchen.com/recipes/browse/meat?q=&fR[search_browse_slugs][0]=meat&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Soups & Stews
        'https://www.americastestkitchen.com/recipes/browse/soups?q=&fR[search_browse_slugs][0]=soups&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Fish & Seafood
        'https://www.americastestkitchen.com/recipes/browse/seafood?q=&fR[search_browse_slugs][0]=seafood&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Eggs & Breakfast
        'https://www.americastestkitchen.com/recipes/browse/breakfast?q=&fR[search_browse_slugs][0]=breakfast&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Marinades & Sauces
        'https://www.americastestkitchen.com/recipes/browse/sauces?q=&fR[search_browse_slugs][0]=sauces&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Beans & Grains
        'https://www.americastestkitchen.com/recipes/browse/beans_and_grains?q=&fR[search_browse_slugs][0]=beans_and_grains&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Pasta
        'https://www.americastestkitchen.com/recipes/browse/pasta?q=&fR[search_browse_slugs][0]=pasta&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Salads
        'https://www.americastestkitchen.com/recipes/browse/salads?q=&fR[search_browse_slugs][0]=salads&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Vegetables
        'https://www.americastestkitchen.com/recipes/browse/salads?q=&fR[search_browse_slugs][0]=salads&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk'
    ]

    index = 1
    for page in pages:
        save_recipes(page, index)
        index += 1
