package logger

import (
	"log"
	"os"
)

type Logger struct {
	info  *log.Logger
	err   *log.Logger
	fatal *log.Logger
}

func NewLogger() *Logger {
	info := log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime)
	err := log.New(os.Stdout, "ERROR: ", log.Ldate|log.Ltime)
	fatal := log.New(os.Stdout, "FATAL: ", log.Ldate|log.Ltime)

	return &Logger{
		info:  info,
		err:   err,
		fatal: fatal,
	}
}

func (l *Logger) Info(msg string, a ...any) {
	l.info.Printf(msg+"\n", a...)
}

func (l *Logger) Error(msg string, a ...any) {
	l.err.Printf(msg+"\n", a...)
}

func (l *Logger) Fatal(msg string, a ...any) {
	l.fatal.Printf(msg+"\n", a...)
	os.Exit(1)
}
