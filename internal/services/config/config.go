package config

import (
	"os"

	"gopkg.in/yaml.v2"
)

type Config struct {
	DatabaseType string `yaml:"database_type"`
	DiscordToken string `yaml:"discord_token"`
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

func (c Config) GetDatabaseType() string {
	return c.DatabaseType
}

func (c Config) GetDiscordToken() string {
	return c.DiscordToken
}
