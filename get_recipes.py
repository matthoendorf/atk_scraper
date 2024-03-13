#!/usr/bin/env python
import atkscrape as atk
import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="get_some",
        description = "scrape ATK recipes to images, mealie json, or both. ")
    parser.add_argument('-e', '--email', required=True, help="ATK email for login.")
    parser.add_argument('-p', '--password', required=True, help="SINGLE QUOTED ATK password for login. For example 'my_password!*'")
    parser.add_argument('-r', '--recipes', required=True, help="Text file containing a list of individual ATK recipes to grab. See recipes.txt for examples")
    parser.add_argument('-i', '--image', required=False, default=False, help="Get recipes as images (default False)")
    parser.add_argument('-j', '--json', required=False, default=True, help="Get recipes as json for mealie (default True)")
    parser.add_argument('-o', '--out_path', default='./recipes/', help="Location to save images/json (default './recipes/')")
    parser.add_argument('--driver', default='./chromedriver', help="Path to the chromedriver. (default './chromedriver')")
    parser.add_argument('--verbose', action='store_true', default=False, help="verbose output")
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()

    recipes = atk.read_pages(args.recipes)
    if not os.path.exists(args.out_path):
        os.mkdir(args.out_path)

    if args.verbose:
        print("Read " + str(len(recipes)) + " recipe pages to scrape from")

    driver = atk.create_driver(args.driver)
    try:
        atk.login(driver, args.email, args.password)
        for recipe in recipes:
            print("Working on "+recipe)
            atk.save_one_recipe(driver, recipe, args.image, args.json, args.out_path)
        if args.image:
            atk.format_images(args.out_path)        
    finally:
        # Close chrome
        driver.close()
