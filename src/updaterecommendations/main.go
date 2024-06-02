package main

import (
	"encoding/json"
	"os"

	"github.com/benosborntech/recgen/updaterecommendations/handler"
	"github.com/benosborntech/recgen/utils/config"
	"github.com/benosborntech/recgen/utils/constants"
	"github.com/benosborntech/recgen/utils/model"
	"github.com/bsm/redislock"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"
)

func main() {
	c := config.NewConfig()

	kafkaBroker, ok := os.LookupEnv("KAFKA_BROKER")
	if !ok {
		c.Logger.Fatal("failed to get kafka broker")
	}

	redisAddr, ok := os.LookupEnv("REDIS_ADDR")
	if !ok {
		c.Logger.Fatal("failed to get redis address")
	}

	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers: []string{kafkaBroker},
		Topic:   constants.EventTopic,
	})
	defer reader.Close()

	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})
	defer rdb.Close()

	lockClient := redislock.New(rdb)

	for {
		msg, err := reader.ReadMessage(c.Context)
		if err != nil {
			c.Logger.Error("failed to read message: %v", err)
			continue
		}

		var body model.Body
		if err := json.Unmarshal(msg.Value, &body); err != nil {
			c.Logger.Error("failed to parse body: %v", err)
			continue
		}

		if err := handler.UpdateRecommendations(c, body, rdb, lockClient); err != nil {
			c.Logger.Error("update recommendations failed: %v", err)
			continue
		}
	}
}
