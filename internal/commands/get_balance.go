package commands

import (
	"fmt"

	"github.com/hmccarty/arc-assistant/internal/models"
)

type GetBalance struct{}

func (t GetBalance) Name() string {
	return "getbalance"
}

func (t GetBalance) Description() string {
	return "GetBalance for the tip!"
}

func (t GetBalance) Options() []models.CommandOption {
	return nil
}

func (t GetBalance) Run(config models.Config, client models.DbClient, options []models.CommandOption) string {
	balance, _ := client.GetUserBalance("317846778848346112")
	return fmt.Sprintf("You have %f in your account", balance)
}
