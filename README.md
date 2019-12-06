# atk_scraper - America's Test Kitchen Scraper

Scrapes America's Test Kitchen website for recipes and saves as PNGs.

### Pre-requisites 

* [Chrome v78](https://www.techspot.com/downloads/4718-google-chrome-for-windows.html).
  * If you have a different version of Chrome, replace ```chromedriver.exe``` with the corresponding driver found [here](https://chromedriver.chromium.org/).

* Python 3.6 with an environment built off of ```requirements.txt```.

* America's Test Kitchen/Cook's Country/Cook's Illustrated web subscription (or [trial](https://www.cooksillustrated.com/trial)).
  
  Update the following lines with your login information:

  ```
  YOUR_ATK_EMAIL = 'test@test.com'
  YOUR_ATK_PASSWORD = 'test_password'
  ```

* A list of page URLs that contain recipe links (e.g. category pages). 
  * Example:
  ```
  pages = [
  'https://www.americastestkitchen.com/books/cook-it-in-cast-iron?q=&fR[search_browse_slugs][0]=cook-it-in-cast-iron&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
  'https://www.americastestkitchen.com/recipes/browse/holiday?q=&fR[search_browse_slugs][0]=holiday&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk',
  'https://www.americastestkitchen.com/books/the-perfect-cookie?q=&fR[search_browse_slugs][0]=the-perfect-cookie&fR[search_document_klass][0]=recipe&fR[search_site_list][0]=atk'
  ]
  ```
  * **NOTE: using "[All Recipes](https://www.americastestkitchen.com/recipes/browse)" page will not work as the site stops loading recipes after a finite amount. It will not load "All Recipes" as the name implies. This is why I separate by category.**
  
### Process

1. Selenium opens Chrome driver in headless mode.
2. Logs into ATK using credentials provided.
3. Iterates through the list of pages.
4. For each page, it clicks "Load More Recipes" until all recipes are displayed.
5. The page source is passed to BeautifulSoup, which extracts all recipe links.
6. Each recipe link is loaded with Selenium. Page dimensions are determined using page divs. 
7. The Chrome window is resized to fit these dimensions and a screenshot is saved to ```./recipes```.
8. Screenshots are cleaned using Pillow and saved to ```./recipes_trimmed```.
9. The program will load the next page and repeat.

### Improvements

Visit the "Issues" page for proposed improvements.
