package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/hmccarty/arc-assistant/internal/commands"
	"github.com/hmccarty/arc-assistant/internal/models"
	"github.com/hmccarty/arc-assistant/internal/services/config"
	"github.com/hmccarty/arc-assistant/internal/services/discord"
)

var (
	commandList = []models.Command{
		commands.SetBalance{},
		commands.GetBalance{},
	}
)

func main() {
	conf, err := config.NewConfig("config/main.yml")

	session, err := discord.NewDiscordSession(commandList, conf)
	if err != nil {
		log.Fatal(err)
	}

	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
	<-sc

	session.Close()
}
