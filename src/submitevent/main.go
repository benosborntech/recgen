package main

import (
	"os"

	"github.com/benosborntech/recgen/submitevent/config"
	"github.com/benosborntech/recgen/submitevent/handler"
	"github.com/benosborntech/recgen/utils/constants"
	"github.com/benosborntech/recgen/utils/logger"
	"github.com/gofiber/fiber"
	"github.com/segmentio/kafka-go"
)

func main() {
	logger := logger.NewLogger()

	port, ok := os.LookupEnv("PORT")
	if !ok {
		port = "3000"
	}
	logger.Info("using port %s", port)

	kafkaBroker, ok := os.LookupEnv("KAFKA_BROKER")
	if !ok {
		logger.Fatal("failed to get broker")
	}

	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{kafkaBroker},
		Topic:   constants.EventTopic,
	})
	defer writer.Close()

	config := config.NewConfig(logger, writer)

	app := fiber.New()
	v1 := app.Group("/v1")

	v1.Post("/event", handler.SubmitEvent(config))

	app.Listen(port)
}
