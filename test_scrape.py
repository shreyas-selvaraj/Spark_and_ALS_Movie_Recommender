from flask import Flask
import json
from flask import request, jsonify, render_template
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


movies = ['Avengers', 'Real Steel','Inception','Toy Story','The Godfather']

urls = ""

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
browser = webdriver.Chrome(chrome_options=options)
#browser = webdriver.Chrome()

url = 'https://images.google.com'
browser.get(url)

name = 'q'
search_el = browser.find_element_by_name(name)
search_el.send_keys(movies[0])
submit_btn_el = browser.find_element_by_css_selector("button[type='submit']")
time.sleep(1)
submit_btn_el.click()
img_el = browser.find_elements_by_xpath("//img[@class ='rg_i Q4LuWd']")[0]
print(img_el)
img_src = img_el.get_attribute("src")
print(img_src)
urls = urls + img_src + "|"
browser.find_element_by_name(name).clear()

for i in range(1, len(movies)):
	search_el = browser.find_element_by_name(name)
	search_el.send_keys(movies[i])
	submit_btn_el = browser.find_elements_by_xpath("//button[@class ='KXJfe']")[0]
	time.sleep(1)
	submit_btn_el.click()
    #img_el = browser.find_element_by_css_selector("img")
	img_el = browser.find_elements_by_xpath("//img[@class ='rg_i Q4LuWd']")[0]
	img_src = img_el.get_attribute("src")
	print(img_src)
	urls = urls + img_src + "|"
	browser.find_element_by_name(name).clear()


app = Flask(__name__)
@app.route("/")
def hello():
    return render_template("home.html", urls=urls)
    #return urls

if __name__ == "__main__":
    app.run()