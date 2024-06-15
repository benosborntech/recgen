FROM python:alpine

WORKDIR /build

COPY updaterecommendations/requirements.txt .
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

COPY ./ ./

CMD ["python3 updaterecommendations/main.py"]