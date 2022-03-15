package discord

import (
	"log"

	dg "github.com/bwmarrin/discordgo"
	"github.com/hmccarty/arc-assistant/internal/models"
	"github.com/hmccarty/arc-assistant/internal/services/database"
)

func appFromCommand(command models.Command) *dg.ApplicationCommand {
	var appOptions []*dg.ApplicationCommandOption = nil
	if len(command.Options()) > 0 {
		appOptions = make([]*dg.ApplicationCommandOption, len(command.Options()))
		for i, v := range command.Options() {
			appOptions[i] = &dg.ApplicationCommandOption{
				Type:        dg.ApplicationCommandOptionType(v.Type),
				Name:        v.Name,
				Required:    v.Required,
				Description: "Description",
			}
		}
	}

	return &dg.ApplicationCommand{
		Name:        command.Name(),
		Description: command.Description(),
		Options:     appOptions,
	}
}

func optionFromInteractionData(interactionData *dg.ApplicationCommandInteractionDataOption) (models.CommandOption, error) {
	option := models.CommandOption{
		Name:  interactionData.Name,
		Type:  models.CommandOptionType(interactionData.Type),
		Value: interactionData.Value,
	}
	return option, nil
}

func createDiscordHandler(config models.Config, command models.Command) DiscordHandler {
	return func(s *dg.Session, i *dg.InteractionCreate) {
		options := make([]models.CommandOption, len(i.ApplicationCommandData().Options))
		for i, v := range i.ApplicationCommandData().Options {
			option, err := optionFromInteractionData(v)
			if err != nil {
				log.Println(err)
			}
			options[i] = option
		}

		client, _ := database.OpenClient(config)
		content := command.Run(config, client, options)
		s.InteractionRespond(i.Interaction, &dg.InteractionResponse{
			Type: dg.InteractionResponseChannelMessageWithSource,
			Data: &dg.InteractionResponseData{
				Content: content,
			},
		})
	}
}
