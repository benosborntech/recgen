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

func (l *Logger) Info(a ...any) {
	l.info.Println(a...)
}

func (l *Logger) Error(a ...any) {
	l.err.Println(a...)
}

func (l *Logger) Fatal(a ...any) {
	l.fatal.Println(a...)
	os.Exit(1)
}
