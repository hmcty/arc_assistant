package commands

import (
	"fmt"

	"github.com/hmccarty/arc-assistant/internal/models"
)

type SetBalance struct{}

func (c SetBalance) Name() string {
	return "setbalance"
}

func (c SetBalance) Description() string {
	return "SetBalance for the tip!"
}

func (c SetBalance) Options() []models.CommandOption {
	return []models.CommandOption{
		{
			Name:     "user",
			Type:     models.UserOption,
			Required: true,
		},
		{
			Name:     "amount",
			Type:     models.NumberOption,
			Required: true,
		},
	}
}

func (c SetBalance) Run(config models.Config, client models.DbClient, options []models.CommandOption) string {
	if len(options) != 2 {
		return "Invalid number of options"
	}

	var userID string
	var amount float64
	for _, option := range options {
		switch option.Name {
		case "user":
			userID = option.Value.(string)
		case "amount":
			amount = option.Value.(float64)
		}
	}

	client.SetUserBalance(userID, amount)
	balance, _ := client.GetUserBalance(userID)
	return fmt.Sprintf("You have %f in your account", balance)
}
