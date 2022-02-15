# syntax=docker/dockerfile:1
#
# docker build -t mbijakowski/hr-calendar .
# docker run -it mbijakowski/hr-calendar

# Specify main image to import
FROM python:3-slim-buster

# Specify virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Specify work directory
WORKDIR /usr/app

# Copy requirements.txt into the containter
COPY ./requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy other (all) files into the containter
COPY ./ ./

# Run app :
#CMD [ "python", "./works_localy.py" ]
CMD [ "python", "./docker_test.py" ]
