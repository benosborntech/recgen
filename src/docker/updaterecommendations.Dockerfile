FROM python:3.11

WORKDIR /app/src

COPY updaterecommendations/requirements.txt .
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

COPY ./ ./

WORKDIR /app

CMD ["python3", "-m", "src.updaterecommendations.main"]