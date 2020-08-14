from pyspark.sql import SparkSession

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
import csv
from flask import Flask
import json
from flask import request, jsonify, render_template
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def loadMovieNames():
    movieID_to_name = {}
    with open("ml-25m/movies.csv", newline='', encoding='ISO-8859-1') as csvfile:
        movieReader = csv.reader(csvfile)
        next(movieReader)  #Skip header line
        for row in movieReader:
            movieID = int(row[0])
            movieName = row[1]
            movieID_to_name[movieID] = movieName
    return movieID_to_name

spark = SparkSession\
    .builder\
    .appName("ALSExample")\
    .config("spark.executor.cores", '4')\
    .config("spark.memory.offHeap.enabled",True)\
    .config("spark.memory.offHeap.size","16g") \
    .config("spark.driver.memory", "4g")\
    .getOrCreate()
    

lines = spark.read.option("header", "true").csv("ml-25m/ratings.csv").rdd

ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), movieId=int(p[1]),
                                     rating=float(p[2]), timestamp=int(p[3])))

ratings = spark.createDataFrame(ratingsRDD)

(training, test) = ratings.randomSplit([0.8, 0.2])

als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating",
          coldStartStrategy="drop")
model = als.fit(training)

predictions = model.transform(test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print("Root-mean-square error = " + str(rmse))

userRecs = model.recommendForAllUsers(5) #get 5 results

usersRecs = userRecs.filter(userRecs['userId'] == 75).collect()

spark.stop()

movieID_to_name = loadMovieNames()
movies = []
movieids = []
output = ""
    
for row in usersRecs:
    for rec in row.recommendations:
        if rec.movieId in movieID_to_name:
            print(movieID_to_name[rec.movieId])
            movieids.append(rec.movieId)
            movies.append(movieID_to_name[rec.movieId])

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

'''
SETUP PYSPARK
https://stackoverflow.com/questions/38936150/spark-exception-python-in-worker-has-different-version-3-4-than-that-in-driver
https://stackoverflow.com/questions/21964709/how-to-set-or-change-the-default-java-jdk-version-on-os-x
https://stackoverflow.com/questions/52196261/pyspark-will-not-start-python-no-such-file-or-directory
https://superuser.com/questions/1436855/port-binding-error-in-pyspark
'''