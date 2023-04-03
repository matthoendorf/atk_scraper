# America's Test Kitchen Recipe Scraper 

Scrapes America's Test Kitchen website for recipes and saves PNG screenshots and/or JSON for import to a recipe manager (e.g. https://mealie.io).

## Pre-requisites 

* [Chrome v111](https://www.techspot.com/downloads/4718-google-chrome-for-windows.html). If you have a different version of Chrome, replace with the corresponding driver found [here](https://chromedriver.chromium.org/).

* Python 3.6 with an environment built off of ```requirements.txt```.

* America's Test Kitchen/Cook's Country/Cook's Illustrated web subscription (or [trial](https://www.cooksillustrated.com/trial)).
  
## Apps
### ```get_recipes.py```: Grab individual recipes from a list
* ```-h, --help``` : show this help message and exit
* ```-e EMAIL, --email EMAIL``` : ATK email for login.
* ```-p PASSWORD, --password PASSWORD``` : **Single quoted** password for login. For example ```'my_password!*'```
* ```-r RECIPES, --recipes RECIPES``` : Text file containing a list of **individual recipes** to grab.
* ```-j JSON, --json JSON``` : Get recipes as json for mealie (default **True**)
* ```-i IMAGE, --image IMAGE``` : Get recipes as images (default **False**)
* ```-o OUT_PATH, --out_path OUT_PATH``` : Location to save images/json (default './recipes/')
* ```--driver DRIVER ``` : Path to the chromedriver. (default './chromedriver')
* ```--verbose``` : verbose output

### ```get_searches.py```: Traverse search results and grab all recipes within
* ```-h, --help``` : show this help message and exit
* ```-e EMAIL, --email EMAIL``` : ATK email for login.
* ```-p PASSWORD, --password PASSWORD``` : **Single quoted** ATK password for login. For example ```'my_password!*'```
* ```-r RECIPES, --recipes RECIPES``` : Text file containing a list of **search result pages** to recursively descend and grab all recipes from. See recipes.txt for an example. Using "[All Recipes](https://www.americastestkitchen.com/recipes/browse)" page will not work as the site stops loading recipes after 900 are reached. It will not load "All Recipes" as the name implies. This is why you need to separate into smaller search sets
* ```-j JSON, --json JSON``` : Get recipes as json for mealie (default **True**)
* ```-i IMAGE, --image IMAGE``` : Get recipes as images (default **False**)
* ```-o OUT_PATH, --out_path OUT_PATH``` : Location to save images/json (default ``./recipes/``)
* ```--driver DRIVER ``` : Path to the chromedriver. (default ``./chromedriver``)
* ```--verbose``` : verbose output

## Process
1. Selenium opens Chrome driver in headless mode.
2. Logs into ATK using credentials provided.
3. Iterates through the list of pages, whether individual recipes or full search pages.
5. Each page source is passed to BeautifulSoup, which extracts all recipe links.
6. Each recipe link is loaded with Selenium. Page dimensions are determined using page divs. 
7. If ```-i``` is specified, a screenshot is saved. The Chrome window is resized to fit these dimensions and a screenshot is saved to the specified path. Screenshots are cleaned using Pillow and saved as ```<image>.trimmed.png```
8. If ```-j``` is specified, recipe information is smartly scraped and loaded into JSON for later import to a recipe manager (e.g. mealie). The highlight image is also saved as a ```.jp2``` image (this is the format used by ATK)
9. The program will load the next page and repeat.

## Disclaimer

This project is for educational, read-only purposes.

The use of this project is done at your own discretion and risk. 

You are solely responsible for liability and consequences.


