package config

import (
	"os"

	"gopkg.in/yaml.v2"
)

type Config struct {
	DatabaseType   string `yaml:"database_type"`
	DiscordToken   string `yaml:"discord_token"`
	DiscordAppID   string `yaml:"discord_app_id"`
	DiscordGuildID string `yaml:"discord_guild_id"`
}

func NewConfig(filename string) (Config, error) {
	file, err := os.ReadFile(filename)

	var c Config
	err = yaml.Unmarshal(file, &c)
	if err != nil {
		return Config{}, err
	}
	return c, nil
}
