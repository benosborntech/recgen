package main

import (
	"os"

	"github.com/benosborntech/recgen/submitevent/config"
	"github.com/benosborntech/recgen/submitevent/handler"
	"github.com/benosborntech/recgen/utils/ckafka"
	"github.com/benosborntech/recgen/utils/constants"
	"github.com/benosborntech/recgen/utils/logger"
	"github.com/gofiber/fiber"
	"github.com/segmentio/kafka-go"
)

func main() {
	// Setup
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

	// Create topics
	cKafka, err := ckafka.NewCKafka(kafkaBroker)
	if err != nil {
		logger.Fatal("failed to create ckafka: %w", err)
	}
	defer cKafka.Close()

	topics := []kafka.TopicConfig{
		{Topic: constants.EventTopic, NumPartitions: 1, ReplicationFactor: 1},
	}
	if err := cKafka.CreateTopics(topics); err != nil {
		logger.Fatal("failed to create topic: %w", err)
	}

	// Initialize application
	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{kafkaBroker},
		Topic:   constants.EventTopic,
	})
	defer writer.Close()

	config := config.NewConfig(logger, writer)

	app := fiber.New()

	app.Post("/", handler.SubmitEvent(config))

	app.Listen(port)
}
