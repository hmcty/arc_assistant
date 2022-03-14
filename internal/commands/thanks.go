package currency

import (
	"fmt"

	"github.com/hmccarty/arc-assistant/internal/models"
)

type Thanks struct{}

func (t Thanks) Name() string {
	return "thanks"
}

func (t Thanks) Description() string {
	return "Thanks for the tip!"
}

func (t Thanks) Options() []*models.CommandOption {
	return nil
}

func (t Thanks) Run(config *models.Config, client *models.DbClient, options []*models.CommandOption) string {
	balance := client.GetUserBalance("317846778848346112")
	return fmt.Sprintf("You have %f in your account", balance)
}
