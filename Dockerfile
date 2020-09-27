# docker build -t ubuntu1604py36
FROM ubuntu:16.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    python3.4 \
    python3-pip \
	wget

# install pip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install websocket-client boto3 numpy pandas

# add java repo
RUN add-apt-repository -y ppa:webupd8team/java

# install java silently
RUN apt-get install -y default-jre
RUN apt-get install -y default-jdk
RUN export JAVA_HOME=/usr/lib/jvm/java-8-oracle

# install zookeeper
RUN apt-get install zookeeperd -y

# install kafka
RUN wget https://mirrors.whoishostingthis.com/apache/kafka/2.6.0/kafka_2.13-2.6.0.tgz
RUN mkdir /opt/Kafka
RUN tar -xvf kafka_2.13-2.6.0.tgz -C /opt/Kafka/
RUN nohup /opt/Kafka/kafka_2.13-2.6.0.tgz/bin/kafka-server-start.sh /opt/Kafka/kafka_2.13-2.6.0.tgz/config/server.properties &

# install spark
RUN wget https://mirrors.whoishostingthis.com/apache/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz
RUN mkdir /opt/Spark
RUN tar xvf spark-2.4.7-bin-hadoop2.7.tgz -C /opt/Spark/
RUN export SPARK_HOME=/opt/Spark
RUN export PYSPARK_PYTHON=/usr/bin/python3
RUN export PATH=$SPARK_HOME/bin:$PATH
RUN export PATH=$JAVA_HOME/bin:$PATH
RUN export PATH=$PYSPARK_PYTHON/bin:$PATH


# start kafka producer
RUN nohup python meetup_producer.py &

# run spark code
RUN spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.1 meetup_analysis.py
