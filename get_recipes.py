from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import os
from os.path import basename
from os.path import splitext
import time
import json
import glob
from PIL import Image, ImageChops, ImageOps
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="atk_scraper",
        description = "scrape ATK recipes to images, mealie json, or both")
    parser.add_argument('-e', '--email', required=True, help="ATK email for login.")
    parser.add_argument('-p', '--password', required=True, help="SINGLE QUOTED ATK password for login. For example 'my_password!*'")
    parser.add_argument('-r', '--recipes', required=True, help="Text file containing a list of ATK pages to grab recipes from. See recipes.txt for an example")
    parser.add_argument('-i', '--image', required=False, default=True, help="Get recipes as images (default True)")
    parser.add_argument('-j', '--json', required=False, default=True, help="Get recipes as json for mealie (default True)")
    parser.add_argument('-o', '--out_path', default='./recipes/', help="Location to save images/json (default './recipes/')")
    parser.add_argument('--driver', default='./chromedriver', help="Path to the chromedriver. (default './chromedriver')")
    parser.add_argument('--verbose', action='store_true', default=False, help="verbose output")
    
    args = parser.parse_args()
    return args

def read_pages(filename):
    pages = []
    with open(filename,'r') as f:
        for line in f:
            if line[0] == "#":
                continue
            pages.append(line.rstrip())
    return pages

def create_driver(path):
    print('Starting...')
    try:
        # Launch chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(path, options=chrome_options)
        return driver
    except Exception as e:
        print("Couldn't create chrome driver")
        print(e)
        exit()

def login(driver, email, password):
    try:
        # Load login page
        driver.get("https://www.americastestkitchen.com/sign_in")
        # Enter email address
        e = driver.find_element(By.ID, "email")
        e.send_keys(email)
        # Enter password
        e = driver.find_element(By.NAME, "password")
        e.send_keys(password)
        # Click submit button
        e = driver.find_element(
            By.XPATH, r"//*[@id='app-content']/main/section/section/article[1]/form/fieldset/div[2]/button")
        e.click()
        time.sleep(10)
        # Load recipes page
        return driver
    except Exception as e:
        print("Couldn't log in")
        print(e)
        exit()

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
    images = glob.glob(path+'/'+'*.png')
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
            im.save(path+'/'+newname)
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

def load_full_page(driver):
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
        
    return(driver)

def make_image(driver, slug, savepath):
    """
    Returns image containing screenshot of the page, ready for writing
    """
    try:
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
        screenshot = driver.save_screenshot(savepath+"/"+slug+".png") # FIXME
    except Exception as e:
        print(e)

def make_json(driver):
    """
    Returns dictionary of recipe in mealie-formatting, ready for json conversion
    """
    try:
        d = driver.find_element(By.XPATH, '//*[@id="why-this-works"]/p/button')
        d.click()
    except:
        pass # this is fine, since it just means that the full text is already visible, so let's keep chrome from killing everything
    
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    #TITLE
    title = soup.find('div', attrs={'class': "detail-page-main"})
    title = title['data-document-title']

    # DESCRIPTION
    try:
        description =  soup.find('div', attrs={'id': 'why-this-works'})
        description = description.get_text(" ", strip=True)[:-9] # remove last 9 characters = "Read Less"
        description = re.sub(r'\n', ' ', description) # remove internal linebreaks
    except:
        description = ""

    # IMAGE
    img =  soup.find('img', attrs={'class': 'img recipe-detail-header__image'})
    img_handle = None
    if img != None:
        if "http" in img.get('src'):
            lnk = img.get('src')
            img_handle = requests.get(lnk).content
            #with open(savepath+slug+".jp2", "wb") as f:
                #f.write(requests.get(lnk).content)

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
    recipe["totalTime"] = totaltime
    recipe["recipeYield"] = recipeyield
    recipe["recipeIngredient"] = [{"note":ingredient} for ingredient in ingredients]
    recipe["recipeInstructions"] = [{"text":step} for step in steps]
    recipe["org_url"]  = driver.current_url
    recipe["settings"] = {
        "public": True,
        "showNutrition": False,
        "showAssets": True,
        "landscapeView": True,
        "disableComments": False,
        "disableAmount": False
    }
    return (recipe, img_handle)

def save_recipes(driver, page, do_image, do_json, savepath):
    driver.get(page)
    # Refresh to prevent loading errors
    driver.refresh()
    time.sleep(15)
    
    driver = load_full_page(driver)
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

        # Load the recipe
        print('{0} / {1} | https://www.americastestkitchen.com{2}'.format(
            str(curr).zfill(digits), length, link))
        if link == '/recipes/24-easy-caramel-sauce':
            link = '/recipes/10610-all-purpose-caramel-sauce'
            driver.get("https://www.cooksillustrated.com/recipes/10610-all-purpose-caramel-sauce")
        else:
            driver.get("https://www.americastestkitchen.com{0}".format(link))
        
        time.sleep(1)
        
        if do_image:
            if os.path.exists(savepath+"/"+slug+".png"):
                print("Already fetched image for " + slug)
            else:
                make_image(driver, slug, savepath)

        if do_json:
            if os.path.exists(savepath+"/"+slug+".json"):
                print("Already fetched json for " + slug)
            else:
                recipe, img = make_json(driver)
                with open(savepath+"/"+slug+".json", "w") as write_file:
                    json.dump(recipe, write_file, indent=4)
                if img != None:
                    with open(savepath+"/"+slug+".jp2", "wb") as f:
                        f.write(img)
                
        curr += 1

if __name__ == "__main__":
    args = parse_arguments()

    pages = read_pages(args.recipes)
    if not os.path.exists(args.out_path):
        os.mkdir(args.out_path)

    if args.verbose:
        print("Read " + str(len(pages)) + " recipe pages to scrape from")

    driver = create_driver(args.driver)
    driver = login(driver, args.email, args.password)
    for page in pages:
        save_recipes(driver, page, args.image, args.json, args.out_path)
    
    # Close chrome
    driver.close()
    if args.image:
        format_images(save_path)
