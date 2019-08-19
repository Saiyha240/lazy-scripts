FROM php:7.3.3-apache

WORKDIR /var/www/html

COPY app/ .

RUN mkdir -p /etc/service/apache
COPY apache.sh /etc/service/apache/run
RUN chmod +x /etc/service/apache/run

EXPOSE 80