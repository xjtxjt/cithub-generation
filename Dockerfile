FROM centos:7

WORKDIR /app
VOLUME /tmp

# java
RUN yum install -y java-1.8.0-openjdk

# python
RUN yum install -y python3
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

CMD [ "python3", "/app/app.py" ]
