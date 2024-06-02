package main

import (
	"os"

	"github.com/benosborntech/recgen/getrecommendations/handler"
	"github.com/benosborntech/recgen/utils/config"
	"github.com/gofiber/fiber"
	"github.com/redis/go-redis/v9"
)

func main() {
	c := config.NewConfig()

	redisAddr, ok := os.LookupEnv("REDIS_ADDR")
	if !ok {
		c.Logger.Fatal("failed to get redis address")
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})
	defer rdb.Close()

	app := fiber.New()

	app.Post("/:userId", handler.GetRecommendations(c, rdb))

	app.Listen(c.Port)
}
