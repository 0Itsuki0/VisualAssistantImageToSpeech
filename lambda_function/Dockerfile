FROM --platform=linux/amd64 amazon/aws-lambda-python:latest

LABEL maintainer="Itsuki"

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./

CMD ["handler.handler"]