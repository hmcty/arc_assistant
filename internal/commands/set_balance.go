package commands

import (
	"fmt"

	m "github.com/hmccarty/arc-assistant/internal/models"
	c "github.com/hmccarty/arc-assistant/internal/services/config"
)

type SetBalance struct{}

func (_ *SetBalance) Name() string {
	return "setbalance"
}

func (_ *SetBalance) Description() string {
	return "SetBalance for the tip!"
}

func (_ *SetBalance) Options() []m.CommandOption {
	return []m.CommandOption{
		{
			Name:     "user",
			Type:     m.UserOption,
			Required: true,
		},
		{
			Name:     "amount",
			Type:     m.NumberOption,
			Required: true,
		},
	}
}

func (_ *SetBalance) Run(opts []m.CommandOption, conf c.Config, client m.DbClient) string {
	if len(opts) != 2 {
		return "Invalid number of options"
	}

	var userID string
	var amount float64
	for _, option := range opts {
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
