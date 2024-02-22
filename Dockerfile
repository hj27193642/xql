FROM python:slim

# environment settings 
ENV WORK="/work"
ENV HOME="/root"
ENV TZ=Asia/Seoul

RUN echo "*** ADDUSER ***" && \
    adduser --disabled-password --gecos "" homeuser && \
    mkdir $WORK && \
    chown -R homeuser:homeuser $WORK

RUN echo "*** UPDATE && UPGRADE && ***" && \
    apt update && \
    apt dist-upgrade -y --no-install-recommends && \
    apt autoremove -y

RUN apt install --no-install-recommends -y \
    tzdata \
    sudo \
    curl \
    build-essential

# # LANG UTF-8 setting
RUN \
	apt install -y locales && \
	localedef -i ko_KR -c -f UTF-8 -A /usr/share/locale/locale.alias ko_KR.UTF-8

ENV LANG ko_KR.utf8

# EXPOSE 8080
WORKDIR $WORK
RUN mkdir $WORK/src
COPY ./src/ ./src/
COPY poetry.lock pyproject.toml README.md .env ./
RUN chown -R homeuser:homeuser $WORK


USER homeuser
ENV HOME="/home/homeuser"

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# export
ENV PATH /home/homeuser/.local/bin:$PATH

RUN poetry update


CMD ["poetry", "run", "python", "src/main.py"]

