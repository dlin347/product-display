FROM jenkins/jenkins:lts
USER root
RUN apt-get update && apt-get install -y docker.io docker-compose
RUN usermod -aG docker jenkins
#RUN chmod 666 /var/run/docker.sock
USER jenkins
