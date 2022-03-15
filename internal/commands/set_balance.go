package commands

import (
	"fmt"

	m "github.com/hmccarty/arc-assistant/internal/models"
)

type SetBalance struct {
	createDbClient func() m.DbClient
}

func NewSetBalanceCommand(createDbClient func() m.DbClient) m.Command {
	return &SetBalance{
		createDbClient: createDbClient,
	}
}

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

func (command *SetBalance) Run(opts []m.CommandOption) string {
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

	client := command.createDbClient()
	client.SetUserBalance(userID, amount)
	balance, _ := client.GetUserBalance(userID)
	return fmt.Sprintf("You have %f in your account", balance)
}
