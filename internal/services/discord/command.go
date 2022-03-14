package discord

import (
	"log"

	dg "github.com/bwmarrin/discordgo"
	"github.com/hmccarty/arc-assistant/internal/models"
	"github.com/hmccarty/arc-assistant/internal/services/database"
)

func createDiscordCommand(command models.Command) *dg.ApplicationCommand {
	return &dg.ApplicationCommand{
		Name:        command.Name(),
		Description: command.Description(),
	}
}

func createOption(discordOption *dg.ApplicationCommandInteractionDataOption) (models.CommandOption, error) {
	option := models.CommandOption{
		Name:  discordOption.Name,
		Type:  models.CommandOptionType(discordOption.Type),
		Value: discordOption.Value,
	}
	return option, nil
}

func createDiscordHandler(config models.Config, command models.Command) DiscordHandler {
	return func(s *dg.Session, i *dg.InteractionCreate) {
		options := make([]models.CommandOption, len(i.ApplicationCommandData().Options))
		for i, v := range i.ApplicationCommandData().Options {
			option, err := createOption(v)
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
