FROM python:3.12.3

# Update system packages and install libfbclient2
RUN apt update && apt install -y libfbclient2

# Change working directory
RUN mkdir "/app"
WORKDIR /app

# Copy and install Requirements
COPY ./requirements.txt .
RUN pip install -r requirements.txt


# Copy core
COPY ./core ./core
COPY main.py .