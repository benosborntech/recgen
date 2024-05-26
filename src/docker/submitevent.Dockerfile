FROM golang:alpine AS build

WORKDIR /build

COPY go.mod .
COPY go.sum .
RUN go mod download

COPY main.go .

RUN go build -o main main.go

FROM alpine:latest as run

WORKDIR /app

COPY --from=build /build/main .

CMD ["./main"]
