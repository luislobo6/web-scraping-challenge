import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import re
import time
from flask import Markup

## Step 1 - Scraping

def scrape():

    # Create dictionary to return at the end
    mars = {}

    print(f"""--------------------
    Start Scraping...""")
    ### Nasa Mars News Scraping
    print("Nasa Mars News Scraping...")
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    response = requests.get(url)
    soup = bs(response.text, "html.parser")
    news_title = soup.find("div", class_="content_title").a.text.strip('\n')
    news_p = soup.find('div', class_='rollover_description_inner').text.strip('\n')

    # add this variables to our dictionary
    mars["news_title"] = news_title
    mars["news_p"] = news_p

    ### JPL Mars Space Images - Featured Image
    print("JPL Mars Space Images - Featured Image scraping... ")
    # Using splinter to create Browser
    executable_path = {"executable_path": ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars")
    html = browser.html
    soup = bs(html, "html.parser")
    base_url = "https://www.jpl.nasa.gov"
    image_url = soup.find("article", class_="carousel_item")["style"]
    image_url = image_url.lstrip("background-image: url('")
    image_url = image_url.rstrip("');")
    featured_image_url = base_url + image_url
    
    # add this variable to our dictionary
    mars["featured_image_url"] = featured_image_url

    ### Mars Weather
    print("Mars Weather scraping...")
    # go to the page
    browser.visit("https://twitter.com/marswxreport?lang=en")
    # Download more twitts
    (time.sleep(1))
    browser.execute_script("window.scrollTo(2, document.body.scrollHeight);")
    # Get the html
    html = browser.html
    soup = bs(html, "html.parser")
    mars_weather = ""
    list_tweets = soup.find_all("div", class_="css-901oao")
    for tweet in list_tweets:
        if "InSight" in tweet.text:
            mars_weather = tweet.text
            break
    
    # add this variable to our dictionary
    mars["mars_weather"] = mars_weather

    ### Mars Facts
    print("Mars Facts scraping...")
    # Read with pandas
    url = "https://space-facts.com/mars/"
    tables = pd.read_html(url)
    # copy to make some changes in the header and index
    html_table = tables[0].copy()
    html_table = html_table.rename(columns={0:"Description", 1:"Value"})
    html_table = html_table.set_index("Description")
    # change it to Markup so it can be displayed as html
    pd_table_html = Markup(html_table.to_html())

    # add this variable to our dictionary
    mars["pd_table_html"] = pd_table_html


    ### Mars Hemispheres
    print("Mars Hemispheres scraping...")
    # Visit with the browser the main page
    browser.visit("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars")
    # Parse into html and make a soup object
    html = browser.html
    soup = bs(html, "html.parser")
    # url type: https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/cerberus_enhanced.tif/full.jpg
    # Base URL to get the full image url 
    base_url= "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/"

    # Get the div class="description" where the link to each hemisphere is
    list_items = soup.find_all("div", class_="description")

    hemisphere_image_urls = []

    # For each link we get the href to get the full image and the description
    for item in list_items:
        aux_str = item.a['href'].split("/")[5]
        hemisphere_image_urls.append(
            {
                "title": item.a.text.rstrip(" Enhanced"),
                "img_url": f"{base_url}{aux_str}.tif/full.jpg"
            }
        )

     # add this variable to our dictionary
    mars["hemisphere_image_urls"] = hemisphere_image_urls

    # Close browser
    browser.quit()

    print(f"""...Finish Scraping
    --------------------""")

    # RETURN the dictionary
    return mars
