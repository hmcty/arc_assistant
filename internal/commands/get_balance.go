package commands

import (
	"fmt"

	m "github.com/hmccarty/arc-assistant/internal/models"
	c "github.com/hmccarty/arc-assistant/internal/services/config"
)

type GetBalance struct{}

func (_ *GetBalance) Name() string {
	return "getbalance"
}

func (_ *GetBalance) Description() string {
	return "GetBalance for the tip!"
}

func (_ *GetBalance) Options() []m.CommandOption {
	return []m.CommandOption{
		{
			Name:     "user",
			Type:     m.UserOption,
			Required: true,
		},
	}
}

func (_ *GetBalance) Run(opts []m.CommandOption, conf c.Config, client m.DbClient) string {
	if len(opts) != 1 {
		return "Invalid number of options"
	}

	userID := opts[0].Value.(string)
	balance, _ := client.GetUserBalance(userID)
	return fmt.Sprintf("You have %f in your account", balance)
}
