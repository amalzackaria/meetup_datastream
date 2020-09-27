#!/usr/bin/env python3
from __future__ import print_function
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row, SparkSession
from pyspark.sql.functions import *
import json


def getSparkSessionInstance(sparkConf):
    """Initialise Spark Instance
    """
    if ('sparkSessionSingletonInstance' not in globals()):
        globals()['sparkSessionSingletonInstance'] = SparkSession\
            .builder\
            .config(conf=sparkConf)\
            .getOrCreate()
    return globals()['sparkSessionSingletonInstance']


def extract_event_count(pair):
    """extract event_id, event_name, country,City  and response from rsvp
    INPUT: json
    """
    try:
        rsvp = json.loads(pair[1])
        rsvp = json.loads(rsvp)
        event = rsvp.get('event', {})
        event_id = event.get('event_id', None)
        event_name = event.get('event_name', None)
        group = rsvp.get('group', {})
        country = group.get('group_country', None)
        city = group.get('group_city', None)
        response = 1 if rsvp.get('response', None) == 'yes' else 0
        return event_id, event_name, country, city, response
    except ValueError:
        return None


def process(time, rdd):
    """Process stream data
    INPUT: Stream input event_id, event_name, country,City  and response
    """
    print("========= %s =========" % str(time))

    try:
        # Get the singleton instance of SparkSession
        spark = getSparkSessionInstance(rdd.context.getConf())

        # Convert RDD[String] to RDD[Row] to DataFrame
        eventDataFrame = spark.createDataFrame(rdd)

        # Creates a temporary view using the DataFrame.
        eventDataFrame.createOrReplaceTempView("events")

         # Count the number of yes responses per event per minute and return top 5 responses
        eventsdetailDataFrame = \
            spark.sql("select _2 as Event_Name,_3 as Country,_4 as City,sum(_5) as Tot_Subsription from events group by _1,_2,_3,_4 order by sum(_5) desc limit 5")
        eventsdetailDataFrame.show()

    except:
        pass

sc = SparkContext(appName="readmeetupdata")
ssc = StreamingContext(sc, 60)
ssc.checkpoint("C:/SparkCourse/rsvps_checkpoint_dir")

directKafkaStream = KafkaUtils.createDirectStream(ssc, ["meetup-topic"], {"metadata.broker.list": "localhost:9092"})
event = directKafkaStream.map(extract_event_count).filter(lambda line: line is not None)
event.foreachRDD(process)
ssc.start()
ssc.awaitTermination()
