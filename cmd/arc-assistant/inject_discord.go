//go:build wireinject
// +build wireinject

package main

import (
	"github.com/google/wire"

	"github.com/hmccarty/arc-assistant/internal/models"
	"github.com/hmccarty/arc-assistant/internal/services/config"
	"github.com/hmccarty/arc-assistant/internal/services/database"
	"github.com/hmccarty/arc-assistant/internal/services/discord"
)

func createSession() (*DiscordSession, error) {
	wire.Build(
		config.NewConfig,
		database.OpenClient,
		NewDiscordSession,
	)
	return &DiscordSession{}, nil
}
