package commands

import (
	"github.com/hmccarty/arc-assistant/internal/models"
)

var Status = models.Command{
	Name:        "status",
	Description: "Shows the current status of the bot",
	Handler: func(options []*models.CommandOption) string {
		return "Hello from golang!"
	},
}
