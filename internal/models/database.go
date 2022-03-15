package models

import (
	c "github.com/hmccarty/arc-assistant/internal/services/config"
)

type DbClient interface {
	GetUserBalance(string) (float64, error)
	SetUserBalance(string, float64) error
}

type OpenClient func(config *c.Config) (DbClient, error)
