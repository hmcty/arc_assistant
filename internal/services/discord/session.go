package discord

import (
	"log"

	dg "github.com/bwmarrin/discordgo"

	"github.com/hmccarty/arc-assistant/internal/models"
)

type DiscordHandler func(*dg.Session, *dg.InteractionCreate)

type DiscordSession struct {
	Session            *dg.Session
	registeredCommands []*dg.ApplicationCommand
}

func NewDiscordSession(commands []models.Command, config *models.Config, db *models.DbClient) (*DiscordSession, error) {
	discordSession := new(DiscordSession)

	session, err := dg.New("Bot OTI5MjI3NjUzMTc1NzI2MTgx.YdkQsA.IMtmD_QRM5E8Uo7_fSxyZoIYc5s")
	if err != nil {
		return nil, err
	}
	discordSession.Session = session

	discordCommands := make([]*dg.ApplicationCommand, len(commands))
	discordHandlers := map[string]DiscordHandler{}
	for i, v := range commands {
		discordCommands[i] = createDiscordCommand(v)
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
			discordSession.Session.State.User.ID, "", v)
		if err != nil {
			log.Panicf("Cannot create '%v' command: %v", v.Name, err)
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
