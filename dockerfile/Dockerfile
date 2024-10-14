# Ubuntu 22.04 base image
FROM ubuntu:22.04

# Set the environment variable for non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    wget \
    curl \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    git \
    ca-certificates \
    tzdata

# Set the timezone
RUN ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Install python3.9
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3.9 python3.9-dev python3.9-distutils

# Install latest pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py

# Set the python3.9 as default python
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# Git clone the repository
RUN git clone https://github.com/kupl/erc-group2-framework.git

# Set the working directory
WORKDIR /erc-group2-framework

# Install the requirements
RUN pip install -r requirements.txt
RUN pip install --use-pep517 -e pyannotate

# Set the entrypoint
CMD ["bash"]