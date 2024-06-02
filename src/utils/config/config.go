package config

import (
	"context"
	"os"

	"github.com/benosborntech/recgen/utils/logger"
)

type Config struct {
	Logger  *logger.Logger
	Port    string
	Context context.Context
}

func NewConfig() *Config {
	logger := logger.NewLogger()

	port, ok := os.LookupEnv("PORT")
	if !ok {
		port = "3000"
	}

	return &Config{
		logger,
		port,
		context.Background(),
	}
}
