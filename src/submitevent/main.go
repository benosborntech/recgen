package main

import (
	"os"

	"github.com/benosborntech/recgen/submitevent/handler"
	"github.com/benosborntech/recgen/utils/config"
	"github.com/benosborntech/recgen/utils/constants"
	"github.com/gofiber/fiber"
	"github.com/segmentio/kafka-go"
)

func main() {
	c := config.NewConfig()

	kafkaBroker, ok := os.LookupEnv("KAFKA_BROKER")
	if !ok {
		c.Logger.Fatal("failed to get kafka broker")
	}

	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{kafkaBroker},
		Topic:   constants.EventTopic,
	})
	defer writer.Close()

	app := fiber.New()

	app.Post("/", handler.SubmitEvent(c, writer))

	app.Listen(c.Port)
}
