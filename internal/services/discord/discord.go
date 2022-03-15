package discord

import (
	"log"

	dg "github.com/bwmarrin/discordgo"
	"github.com/hmccarty/arc-assistant/internal/models"
	m "github.com/hmccarty/arc-assistant/internal/models"
	c "github.com/hmccarty/arc-assistant/internal/services/config"
)

type DiscordHandler func(*dg.Session, *dg.InteractionCreate)

type DiscordSession struct {
	Session            *dg.Session
	registeredCommands []*dg.ApplicationCommand
}

func NewDiscordSession(config *c.Config, commands []m.Command) (*DiscordSession, error) {
	discordSession := new(DiscordSession)

	session, err := dg.New(config.DiscordToken)
	if err != nil {
		return nil, err
	}
	discordSession.Session = session

	discordCommands := make([]*dg.ApplicationCommand, len(commands))
	discordHandlers := map[string]DiscordHandler{}
	for i, v := range commands {
		discordCommands[i] = appFromCommand(v)
		discordHandlers[v.Name()] = createDiscordHandler(v)
	}

	discordSession.Session.AddHandler(func(s *dg.Session, i *dg.InteractionCreate) {
		if h, ok := discordHandlers[i.ApplicationCommandData().Name]; ok {
			h(s, i)
		}
	})

	err = session.Open()
	if err != nil {
		log.Fatalf("Cannot open the session: %v", err)
	}

	discordSession.registeredCommands = make([]*dg.ApplicationCommand, len(commands))
	for i, v := range discordCommands {
		cmd, err := discordSession.Session.ApplicationCommandCreate(
			config.DiscordAppID, config.DiscordGuildID, v)
		if err != nil {
			log.Panicf("cannot create '%v' command: %v", v.Name, err)
		}
		discordSession.registeredCommands[i] = cmd
	}

	return discordSession, nil
}

func (d *DiscordSession) Close() {
	for _, v := range d.registeredCommands {
		err := d.Session.ApplicationCommandDelete(d.Session.State.User.ID, "", v.ID)
		if err != nil {
			log.Panicf("cannot delete '%v' command: %v", v.Name, err)
		}
	}

	d.Session.Close()
}

func appFromCommand(command m.Command) *dg.ApplicationCommand {
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
	option := m.CommandOption{
		Name:  interactionData.Name,
		Type:  m.CommandOptionType(interactionData.Type),
		Value: interactionData.Value,
	}
	return option, nil
}

func createDiscordHandler(command m.Command) DiscordHandler {
	return func(s *dg.Session, i *dg.InteractionCreate) {
		options := make([]m.CommandOption, len(i.ApplicationCommandData().Options))
		for i, v := range i.ApplicationCommandData().Options {
			option, err := optionFromInteractionData(v)
			if err != nil {
				log.Println(err)
			}
			options[i] = option
		}

		content := command.Run(options)
		s.InteractionRespond(i.Interaction, &dg.InteractionResponse{
			Type: dg.InteractionResponseChannelMessageWithSource,
			Data: &dg.InteractionResponseData{
				Content: content,
			},
		})
	}
}
