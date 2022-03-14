package database

import (
	"fmt"

	"github.com/hmccarty/arc-assistant/internal/models"
)

func OpenClient(config models.Config) (*models.DbClient, error) {
	switch config.GetDatabaseType() {
	case "redis":
		return OpenRedisClient(config)
	default:
		return nil, fmt.Errorf("unsupported database type: %s", config.GetDatabaseType())
	}
}
