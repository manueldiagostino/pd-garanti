FROM ubuntu:latest

RUN apt update && apt upgrade -y

# Clingo
RUN apt install -y gringo
RUN useradd -ms /bin/bash clingo

# Workdir
ARG WORKDIR="/home/clingo/project"
RUN mkdir ${WORKDIR}
WORKDIR ${WORKDIR}

# RUN echo "umask 002" >> /etc/profile
# RUN chown -R clingo ${WORKDIR}
# RUN chmod -R 777 ${WORKDIR}
USER clingo
