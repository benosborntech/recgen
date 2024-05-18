FROM golang:latest AS build

WORKDIR /build

COPY go.mod .
COPY go.sum .
COPY main.go .

RUN go build -o main main.go

FROM alpine:latest as run

COPY --from=build /build/main .

CMD ["./main"]
