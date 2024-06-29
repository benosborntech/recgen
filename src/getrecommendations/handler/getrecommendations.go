package handler

import (
	"fmt"

	"github.com/benosborntech/recgen/goutils/config"
	"github.com/benosborntech/recgen/goutils/constants"
	"github.com/benosborntech/recgen/goutils/misc"
	"github.com/gofiber/fiber"
	"github.com/redis/go-redis/v9"
)

func GetRecommendations(cfg *config.Config, rdb *redis.Client) func(c *fiber.Ctx) {
	return func(c *fiber.Ctx) {
		userId := c.Params("userId")

		res, err := rdb.ZRevRange(cfg.Context, misc.KeyConcat(constants.SET_PREFIX, userId), 0, -1).Result()
		if err != nil {
			err = fmt.Errorf("failed to retrieve list: %v", err)

			cfg.Logger.Error(err.Error())
			c.Status(fiber.StatusBadRequest).Send(err.Error())
		}

		if err := c.Status(fiber.StatusOK).JSON(res); err != nil {
			err = fmt.Errorf("failed to serialize: %v", err)

			cfg.Logger.Error(err.Error())
			c.Status(fiber.StatusInternalServerError).Send(err.Error())
		} else {
			cfg.Logger.Info("successfully retrieved recommendations")
		}
	}
}
