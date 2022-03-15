package models

type DbClient interface {
	GetUserBalance(string) (float64, error)
	SetUserBalance(string, float64) error
}
