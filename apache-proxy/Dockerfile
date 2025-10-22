FROM httpd:latest

COPY ./configuration-files/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./configuration-files/httpd-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf
COPY ./configuration-files/httpd-ssl.conf /usr/local/apache2/conf/extra/httpd-ssl.conf
COPY ./certificates /usr/local/apache2/conf/certificates