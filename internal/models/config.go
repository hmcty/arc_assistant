package models

type Config interface {
	GetDatabaseType() string
}
