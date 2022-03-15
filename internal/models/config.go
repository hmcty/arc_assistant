package models

type Config interface {
	GetDatabaseType() string
	GetDiscordToken() string
}
