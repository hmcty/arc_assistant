package commands

import (
	"fmt"

	"github.com/hmccarty/arc-assistant/internal/models"
)

type GetBalance struct{}

func (c GetBalance) Name() string {
	return "getbalance"
}

func (c GetBalance) Description() string {
	return "GetBalance for the tip!"
}

func (c GetBalance) Options() []models.CommandOption {
	return []models.CommandOption{
		{
			Name:     "user",
			Type:     models.UserOption,
			Required: true,
		},
	}
}

func (c GetBalance) Run(config models.Config, client models.DbClient, options []models.CommandOption) string {
	if len(options) != 1 {
		return "Invalid number of options"
	}

	userID := options[0].Value.(string)
	balance, _ := client.GetUserBalance(userID)
	return fmt.Sprintf("You have %f in your account", balance)
}
