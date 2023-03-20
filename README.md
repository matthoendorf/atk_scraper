# America's Test Kitchen Recipe Scraper 

Scrapes America's Test Kitchen website for recipes and saves PNG screenshots and/or JSON for import to a recipe manager (e.g. https://mealie.io).

### Pre-requisites 

* [Chrome v111](https://www.techspot.com/downloads/4718-google-chrome-for-windows.html).
  * If you have a different version of Chrome, replace ```chromedriver.exe``` with the corresponding driver found [here](https://chromedriver.chromium.org/).

* Python 3.6 with an environment built off of ```requirements.txt```.

* America's Test Kitchen/Cook's Country/Cook's Illustrated web subscription (or [trial](https://www.cooksillustrated.com/trial)).
  
### Options
Several options control get_recipes.py:
* ```-h, --help``` : show this help message and exit
* ```-e EMAIL, --email EMAIL``` : ATK email for login.
* ```-p PASSWORD, --password PASSWORD``` : SINGLE QUOTED ATK password for login. For example * ```'my_password!*'```
* ```-r RECIPES, --recipes RECIPES``` : Text file containing a list of ATK pages to grab recipes from. See recipes.txt for an example. Using "[All Recipes](https://www.americastestkitchen.com/recipes/browse)" page will not work as the site stops loading recipes after 900 are reached. It will not load "All Recipes" as the name implies. This is why I separate by category.
* ```-i IMAGE, --image IMAGE``` : Get recipes as images (default True)
* ```-j JSON, --json JSON``` : Get recipes as json for mealie (default True)
* ```-o OUT_PATH, --out_path OUT_PATH``` : Location to save images/json (default './recipes/')
* ```--driver DRIVER ``` : Path to the chromedriver. (default './chromedriver')
* ```--verbose``` : verbose output
  
### Process

1. Selenium opens Chrome driver in headless mode.
2. Logs into ATK using credentials provided.
3. Iterates through the list of pages.
4. For each page, it clicks "Load More Recipes" until all recipes are displayed.
5. The page source is passed to BeautifulSoup, which extracts all recipe links.
6. Each recipe link is loaded with Selenium. Page dimensions are determined using page divs. 
7. If ```-i``` is specified, a screenshot is saved. The Chrome window is resized to fit these dimensions and a screenshot is saved to the specified path. Screenshots are cleaned using Pillow and saved as ```<image>.trimmed.png```
8. If ```-j``` is specified, recipe information is smartly scraped and loaded into JSON for later import to a recipe manager. The highlight image is also saved as a ```.jp2``` image (this is the format used by ATK)
9. The program will load the next page and repeat.

### Improvements

Visit the "Issues" page for proposed improvements.

### Happy Cooking!

### Disclaimer

This project is for educational, read-only purposes.

The use of this project is done at your own discretion and risk. 

You are solely responsible for liability and consequences.


