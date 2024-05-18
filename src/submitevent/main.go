package main

import (
	"fmt"
	"os"

	"github.com/gofiber/fiber"
)

func main() {
	port, ok := os.LookupEnv("PORT")
	if !ok {
		port = "3000"
	}

	identifier := os.Getenv("IDENTIFIER")

	app := fiber.New()

	app.Get("/", func(c *fiber.Ctx) {
		c.Send(fmt.Sprintf("Hello, World! %s", identifier))
	})

	app.Listen(port)
}
