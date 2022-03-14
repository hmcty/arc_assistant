package models

type DbClient interface {
	GetUserBalance(string) (float32, error)
	SetUserBalance(string, float32) error
}
