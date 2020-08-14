# Spark_and_ALS_Movie_Recommender
Uses Apache Spark and Pyspark ML to implement the Spark ALS factorization algorithm to generate movie recommendations based on movie input. Trained on movielens 25 million movie rating dataset. 
Hardware: 4 cores, 4gb spark driver memory, parallel computing
Benchmarks: average time to calculate: 4.5 mins, average root mean square error: 0.78

Images for the movie recommendations are then scraped from google images using a headless selenium chrome driver and displayed on a flask web app. 
