FROM golang:alpine AS build

WORKDIR /build

COPY go.mod .
COPY go.sum .
RUN go mod download

COPY ./ ./

RUN go build -o main updaterecommendations/main.go

FROM alpine:latest as run

WORKDIR /app

COPY --from=build /build/main /build/data.json ./

CMD ["./main"]
