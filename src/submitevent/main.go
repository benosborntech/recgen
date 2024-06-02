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

	logger.Info("using kafka broker %s", kafkaBroker)

	// Create topics
	logger.Info("initializing controller")

	cKafka, err := ckafka.NewCKafka(kafkaBroker)
	if err != nil {
		logger.Fatal("failed to create ckafka: %v", err)
	}
	defer cKafka.Close()

	logger.Info("creating topics")

	topics := []kafka.TopicConfig{
		{
			Topic:             constants.EventTopic,
			NumPartitions:     1,
			ReplicationFactor: 1,
		},
	}
	if err := cKafka.CreateTopics(topics); err != nil {
		logger.Fatal("failed to create topic: %v", err)
	}

	// Initialize application
	logger.Info("initializing writer")

	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{kafkaBroker},
		Topic:   constants.EventTopic,
	})
	defer writer.Close()

	config := config.NewConfig(logger, writer)

	logger.Info("starting app")

	app := fiber.New()

	app.Post("/", handler.SubmitEvent(config))

	app.Listen(port)
}
