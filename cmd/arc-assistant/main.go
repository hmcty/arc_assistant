package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/hmccarty/arc-assistant/internal/commands"
	"github.com/hmccarty/arc-assistant/internal/models"
	"github.com/hmccarty/arc-assistant/internal/services/discord"
)

var (
	commandList = []models.Command{
		commands.Status,
	}
)

func main() {
	session, err := discord.CreateSession()
	if err != nil {
		log.Fatal(err)
	}
	session.InitCommands(commandList)

	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
	<-sc

	session.Close()
}
