# Dependencies
import pandas as pd
import requests
from pprint import pprint
import pymongo
from bs4 import BeautifulSoup as bs
from splinter import Browser
import lxml
import time

def scrape_info(): 
    results={}
    # Nasa's Mars News Site
    url = "https://mars.nasa.gov/news/"

    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

    # Set up MongoDB
    # conn='mongodb://localhost:27017'
    # client = pymongo.MongoClient(conn)

    # Define database
    # db = client.missions_to_mars
    # collection = db.mars_news

    # Retrieve page with the requests module
    browser.visit(url) 
    time.sleep(2) 
    html = browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html, 'html.parser')

    # Assign variables
    item_list=soup.find('ul', class_='item_list').find('li', class_='slide')

    news_title = item_list.find('div', class_='content_title').get_text()
    news_p = item_list.find('div', class_='article_teaser_body').get_text()

    # Splinter to featured image
    featured_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(featured_image_url)
    element = browser.find_by_id('full_image')
    element.click()
    browser.is_element_present_by_text('more info', wait_time = 1)
    more_info_element = browser.links.find_by_partial_text('more info')
    more_info_element.click()

    html = browser.html
    img = bs(html, 'html.parser')
    try:
        img_url = img.select_one('figure.lede a img').get('src')
    except AttributeError:
        img_url=""
    img_url = f"https://www.jpl.nasa.gov{img_url}"

    # Twitter - code from Vicky and Tracy, after a lot of troubleshootong!
    all_tweets = []
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    data = requests.get(twitter_url)
    html = bs(data.text, 'html.parser')
    timeline = html.select('#timeline li.stream-item')
    for tweet in timeline:
        tweet_id = tweet['data-item-id']
        tweet_text = tweet.select('p.tweet-text')[0].get_text()
        all_tweets.append({"id": tweet_id, "text": tweet_text})
        break

    # Mars Facts table
    facts_url = 'https://space-facts.com/mars/'
    mars_table = pd.read_html(facts_url)[0]
    mars_table.columns = ['description', 'value']
    html_table = mars_table.to_html()

    #Hemisphere images
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    links = browser.find_by_css('a.product-item h3')

    hemispheres = []

    for url_id in range(len(links)):
        hemisphere = {}
        browser.find_by_css('a.product-item h3')[url_id].click()
        sample = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = sample['href']
        hemisphere['title'] = browser.find_by_css('h2.title').text
        hemispheres.append(hemisphere)
        browser.back()

    browser.quit()
    results={"news_title": news_title,
        "news_p": news_p,
        "img_url": img_url,
        "tweet_text": tweet_text,
        "mars_table": html_table,
        "hemispheres": hemispheres
        }
    return results