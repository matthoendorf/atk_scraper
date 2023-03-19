"""
class="ingredient__title"
class="ingredient__quantity"
class="sc-f0bc663c-0 fcUPyI recipe-instructions main"
"""

from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from os.path  import basename
import os
import time
import json
from os.path import exists
import glob
from os.path import splitext
from PIL import Image, ImageChops, ImageOps

YOUR_ATK_EMAIL = 'test@test.com'
YOUR_ATK_PASSWORD = 'test_password'

def login():
    print('Starting...')
    try:
        driver = None
        # Launch chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        cpath = "./chromedriver"
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
        return driver
    except Exception as e:
        print(e)
        return driver

def trim(im):
    # trims empty around image (based on color of upper left pixel)
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        return im


def format_images(path):
    # trims images and adds equal border around each, saves to new folder
    images = glob.glob(path+'*.png')
    curr = 1

    print('Trimming...')

    for image in images:
        base = basename(image)
        newname = splitext(base)[0]+'.trimmed.png'
        print(base+" -> "+newname)
        im = Image.open(image)
        border = (315, 209, 315, 0)  # left, up, right, bottom
        try:
            im = ImageOps.crop(im, border)
            color = im.getpixel((0, 0))
            im = trim(im)
            im = ImageOps.expand(im, 50, color)
            im.save(path + '/trimmed/'+newname)
        except Exception as e:
            print(e)
        curr += 1


def check_exists_by_class(class_name):
    # Check if a page element exists based on class name (return bool)
    try:
        driver.find_element(By.CLASS_NAME, class_name)
    except NoSuchElementException:
        return False
    return True

def save_recipes(driver, page, savepath):

    driver.get(page)
    # Refresh to prevent loading errors
    driver.refresh()
    time.sleep(15)

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
                except Exception as e:
                    # Other exceptions can be added here (additional pop-ups)
                    print(e)
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

        slug = basename(link)
        if exists(savepath+slug+".json") and exists(savepath+slug+".png"):
            print("Already fetched " + slug)
            continue

        # Load the recipe
        print('{0} / {1} | https://www.americastestkitchen.com{2}'.format(
            str(curr).zfill(digits), length, link))
        if link == '/recipes/24-easy-caramel-sauce':
            link = '/recipes/10610-all-purpose-caramel-sauce'
            driver.get("https://www.cooksillustrated.com/recipes/10610-all-purpose-caramel-sauce")
        else:
            driver.get("https://www.americastestkitchen.com{0}".format(link))
        
        time.sleep(1)
        
        if not exists(savepath+slug+".png"):
            # Get the pixel height of page content for screenshot
            try:
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
                driver.save_screenshot(savepath+slug+".png")
            except:
                pass

        if not exists(savepath+slug+".json"):
            try:
                d = driver.find_element(By.XPATH, '//*[@id="why-this-works"]/p/button')
                d.click()
            except:
                pass # this is fine, since it just means that the full text is already visible, so let's keep chrome from killing everything
            
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            title = soup.find('div', attrs={'class': "detail-page-main"})
            title = title['data-document-title']

            # DESCRIPTION
            try:
                description =  soup.find('div', attrs={'id': 'why-this-works'})
                description = description.get_text(" ", strip=True)[:-9] # remove last 9 characters = "Read Less"
            except:
                description = ""

            # IMAGE
            img =  soup.find('img', attrs={'class': 'img recipe-detail-header__image'})
            if img != None:
                if "http" in img.get('src'):
                    lnk = img.get('src')
                    with open(savepath+slug+".jp2", "wb") as f:
                        f.write(requests.get(lnk).content)

            # EXTRAS
            servestime = []
            extras = soup.find_all('p', attrs={'class': re.compile('recipe-detail-page__meta$')})
            for extra in extras:
                try:
                    e = extra.get_text(" ")
                except:
                    e = ""
                servestime.append(e)
                for x in servestime:
                    match = re.search('^(TIME )(.*)', x)
                    try:
                        totaltime = match.group(2)
                    except:
                        totaltime = ""
                    match = re.search('^(SERVES )(.*)', x)
                    try:
                        recipeyield = match.group(2)
                    except:
                        recipeyield = ""


            # INGREDIENTS
            ingredients = []
            for ingredient in soup.find_all('span', attrs={'class': 'ingredient__title'}):
                try:
                    i = ingredient.get_text(" ", strip=True)
                except:
                    i = ""
                ingredients.append(i)
            
            # STEPS
            steps = []
            r = re.compile('^(1 INSTRUCTIONS | \d )(.*)')
            steps = soup.find('div', attrs={'class': 'recipe-instructions__list'})
            try:
                s = steps.get_text(" ")
            except:
                s = ""
            steps = s.split('\n')
            steps = [x for x in steps if x != ''] # remove any empty steps
            for i,x in enumerate(steps):
                try: 
                    steps[i] = r.match(x).group(2)
                except:
                    steps[i] = x

            recipe = {}
            recipe["name"] = title
            recipe["description"] = description
            recipe["image"] = slug+".jp2"

            recipe["totalTime"] = totaltime
            recipe["recipeYield"] = recipeyield
            
            recipe["recipeIngredient"] = [{"note":ingredient} for ingredient in ingredients]
            recipe["recipeInstructions"] = [{"text":step} for step in steps]
            recipe["slug"] = slug
            recipe["org_url"]  = "https://www.americastestkitchen.com"+link
            recipe["settings"] = {
                "public": True,
                "showNutrition": False,
                "showAssets": True,
                "landscapeView": True,
                "disableComments": False,
                "disableAmount": False
            }
            with open(savepath+slug+".json", "w") as write_file:
                json.dump(recipe, write_file, indent=4)

        curr += 1


if __name__ == "__main__":
    pages = [
        # Cook It In Cast Iron
        'https://www.americastestkitchen.com/books/cook-it-in-cast-iron?q=&fR[search_browse_slugs][0]=cook-it-in-cast-iron&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Perfect Cookie Cookbook
        'https://www.americastestkitchen.com/books/the-perfect-cookie?q=&fR[search_browse_slugs][0]=the-perfect-cookie&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Complete Vegetarian Cookbook
        'https://www.americastestkitchen.com/books/the-complete-vegetarian?q=&fR[search_browse_slugs][0]=the-complete-vegetarian&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Complete Slow Cooker Cookbook
        'https://www.americastestkitchen.com/books/the-complete-slow-cooker?q=&fR[search_browse_slugs][0]=the-complete-slow-cooker&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Complete Plant-Based Cookbook
        'https://www.americastestkitchen.com/books/the-complete-plant-based-cookbook?q=&fR[search_browse_slugs][0]=the-complete-plant-based-cookbook&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Complete Salad Cookbook
        'https://www.americastestkitchen.com/books/the-complete-salad-cookbook?q=&fR[search_browse_slugs][0]=the-complete-salad-cookbook&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Vegetables Illustrated
        'https://www.americastestkitchen.com/books/vegetables-illustrated?q=&fR[search_browse_slugs][0]=vegetables-illustrated&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Complete SUmmer Cookbook
        'https://www.americastestkitchen.com/books/the-complete-summer-cookbook?q=&fR[search_browse_slugs][0]=the-complete-summer-cookbook&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Foolproof Fish
        'https://www.americastestkitchen.com/books/foolproof-fish?q=&fR[search_browse_slugs][0]=foolproof-fish&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Cook it in your Dutch Oven
        'https://www.americastestkitchen.com/books/cook-it-in-your-dutch-oven?q=&fR[search_browse_slugs][0]=cook-it-in-your-dutch-oven&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Spiced
        'https://www.americastestkitchen.com/books/spiced?q=&fR[search_browse_slugs][0]=spiced&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # How to Cocktail
        'https://www.americastestkitchen.com/books/how-to-cocktail?q=&fR[search_browse_slugs][0]=how-to-cocktail&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',        
        # one pan wonders
        'https://www.americastestkitchen.com/books/one-pan-wonders?q=&fR[search_browse_slugs][0]=one-pan-wonders&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # foolproof preserving
        'https://www.americastestkitchen.com/books/foolproof-preserving?q=&fR[search_browse_slugs][0]=foolproof-preserving&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Vegan for Everybody
        'https://www.americastestkitchen.com/books/vegan-for-everybody?q=&fR[search_browse_slugs][0]=vegan-for-everybody&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Nutritious Delicious
        'https://www.americastestkitchen.com/books/nutritious-delicious?q=&fR[search_browse_slugs][0]=nutritious-delicious&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The complete Slow Cooker
        'https://www.americastestkitchen.com/books/the-complete-slow-cooker?q=&fR[search_browse_slugs][0]=the-complete-slow-cooker&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Complete Vegetarian
        'https://www.americastestkitchen.com/books/the-complete-vegetarian?q=&fR[search_browse_slugs][0]=the-complete-vegetarian&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # The Perfect Cake
        'https://www.americastestkitchen.com/books/the-perfect-cake?q=&fR[search_browse_slugs][0]=the-perfect-cake&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Light
        'https://www.americastestkitchen.com/recipes/browse?refinementList%5Bsearch_recipe_type_list%5D%5B0%5D=Light&refinementList%5Bsearch_document_klass%5D%5B0%5D=recipe',
        # Grilling & BBQ
        'https://www.americastestkitchen.com/recipes/browse/grilling?q=&fR[search_browse_slugs][0]=grilling&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Desserts & Baked Goods
        'https://www.americastestkitchen.com/recipes/browse/desserts?q=&fR[search_browse_slugs][0]=desserts&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Soups & Stews
        'https://www.americastestkitchen.com/recipes/browse/soups?q=&fR[search_browse_slugs][0]=soups&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Fish & Seafood
        'https://www.americastestkitchen.com/recipes/browse/seafood?q=&fR[search_browse_slugs][0]=seafood&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Eggs & Breakfast
        'https://www.americastestkitchen.com/recipes/browse/breakfast?q=&fR[search_browse_slugs][0]=breakfast&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Marinades & Sauces
        'https://www.americastestkitchen.com/recipes/browse/sauces?q=&fR[search_browse_slugs][0]=sauces&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Vegetarian
        'https://www.americastestkitchen.com/recipes/browse?refinementList%5Bsearch_recipe_type_list%5D%5B0%5D=Vegetarian&refinementList%5Bsearch_document_klass%5D%5B0%5D=recipe,'
        # Beans & Grains
        'https://www.americastestkitchen.com/recipes/browse/beans_and_grains?q=&fR[search_browse_slugs][0]=beans_and_grains&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Weeknight
        'https://www.americastestkitchen.com/recipes/browse?refinementList%5Bsearch_recipe_type_list%5D%5B0%5D=Weeknight&refinementList%5Bsearch_document_klass%5D%5B0%5D=recipe',
        # Salads
        'https://www.americastestkitchen.com/recipes/browse/salads?q=&fR[search_browse_slugs][0]=salads&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
        # Vegetables
        'https://www.americastestkitchen.com/recipes/browse?refinementList%5Bsearch_main_ingredient_list%5D%5B0%5D=Vegetables&refinementList%5Bsearch_document_klass%5D%5B0%5D=recipe'
    ]

    save_path = './recipes/'
    driver = login()
    for page in pages:
        save_recipes(driver, page, save_path)
    
    # Close chrome
    if driver is not None:
        driver.close()
    format_images(save_path)
