package handler

import (
	"encoding/json"
	"fmt"

	"github.com/benosborntech/recgen/submitevent/config"
	"github.com/gofiber/fiber"
	"github.com/segmentio/kafka-go"
)

type Body struct {
	UserId string `json:"userId"`
	RecId  string `json:"recId"`
}

func SubmitEvent(cfg *config.Config) func(c *fiber.Ctx) {
	return func(c *fiber.Ctx) {
		var body Body

		if err := json.Unmarshal([]byte(c.Body()), &body); err != nil {
			c.Status(fiber.StatusBadRequest).Send(fmt.Errorf("failed to parse: %w", err).Error())

			return
		}

		encoded, err := json.Marshal(body)
		if err != nil {
			c.Status(fiber.StatusInternalServerError).Send(fmt.Errorf("failed to encode: %w", err).Error())

			return
		}

		message := kafka.Message{
			Value: encoded,
		}
		if err := cfg.Writer.WriteMessages(c.Context(), message); err != nil {
			c.Status(fiber.StatusInternalServerError).Send(fmt.Errorf("failed to send: %w", err).Error())

			return
		}

		c.Status(fiber.StatusOK).Send("success")
	}
}
