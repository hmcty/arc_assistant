package commands

import (
	"fmt"

	"github.com/hmccarty/arc-assistant/internal/models"
)

type SetBalance struct{}

func (t SetBalance) Name() string {
	return "setbalance"
}

func (t SetBalance) Description() string {
	return "SetBalance for the tip!"
}

func (t SetBalance) Options() []models.CommandOption {
	return nil
}

func (t SetBalance) Run(config models.Config, client models.DbClient, options []models.CommandOption) string {
	balance, _ := client.GetUserBalance("317846778848346112")
	return fmt.Sprintf("You have %f in your account", balance)
}
