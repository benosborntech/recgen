package handler

import (
	"encoding/json"
	"fmt"

	"github.com/benosborntech/recgen/utils/config"
	"github.com/gofiber/fiber"
	"github.com/segmentio/kafka-go"
)

type Body struct {
	UserId string `json:"userId"`
	ItemId string `json:"itemId"`
}

func SubmitEvent(cfg *config.Config, writer *kafka.Writer) func(c *fiber.Ctx) {
	return func(c *fiber.Ctx) {
		var body Body

		if err := json.Unmarshal([]byte(c.Body()), &body); err != nil {
			err = fmt.Errorf("failed to parse: %v", err)

			cfg.Logger.Error(err.Error())
			c.Status(fiber.StatusBadRequest).Send(err.Error())

			return
		}

		encoded, err := json.Marshal(body)
		if err != nil {
			err = fmt.Errorf("failed to encode: %v", err)

			cfg.Logger.Error(err.Error())
			c.Status(fiber.StatusInternalServerError).Send(err.Error())

			return
		}

		message := kafka.Message{
			Value: encoded,
		}
		if err := writer.WriteMessages(c.Context(), message); err != nil {
			err = fmt.Errorf("failed to write message: %v", err)

			cfg.Logger.Error(err.Error())
			c.Status(fiber.StatusInternalServerError).Send(err.Error())

			return
		}

		msg := "successfully published event"

		cfg.Logger.Info(msg)
		c.Status(fiber.StatusOK).Send(msg)
	}
}
