package ckafka

import (
	"net"
	"strconv"

	"github.com/segmentio/kafka-go"
)

type CKafka struct {
	conn *kafka.Conn
}

func NewCKafka(broker string) (*CKafka, error) {
	conn, err := kafka.Dial("tcp", broker)
	if err != nil {
		return nil, err
	}
	defer conn.Close()

	controller, err := conn.Controller()
	if err != nil {
		return nil, err
	}

	controllerConn, err := kafka.Dial("tcp", net.JoinHostPort(controller.Host, strconv.Itoa(controller.Port)))
	if err != nil {
		return nil, err
	}

	return &CKafka{
		conn: controllerConn,
	}, nil
}

func (c *CKafka) CreateTopics(topics []kafka.TopicConfig) error {
	err := c.conn.CreateTopics(topics...)

	return err
}

func (c *CKafka) Close() error {
	return c.conn.Close()
}
