package config

import (
	"github.com/benosborntech/recgen/utils/logger"
	"github.com/segmentio/kafka-go"
)

type Config struct {
	Logger *logger.Logger
	Writer *kafka.Writer
}

func NewConfig(logger *logger.Logger, writer *kafka.Writer) *Config {
	return &Config{
		logger,
		writer,
	}
}
