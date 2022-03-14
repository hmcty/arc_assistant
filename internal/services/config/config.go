package config

type Config struct{}

func (c Config) GetDatabaseType() string {
	return "redis"
}
