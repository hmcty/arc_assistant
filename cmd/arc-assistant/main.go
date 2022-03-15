package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/hmccarty/arc-assistant/internal/commands"
	"github.com/hmccarty/arc-assistant/internal/models"
	"github.com/hmccarty/arc-assistant/internal/services/config"
	"github.com/hmccarty/arc-assistant/internal/services/discord"
	"github.com/hmccarty/arc-assistant/internal/services/redis"
)

func main() {
	conf, err := config.NewConfig("config/main.yml")
	if err != nil {
		fmt.Println(err)
	}

	createDbClient := func() models.DbClient {
		return redis.OpenRedisClient(conf)
	}

	var commandList = []models.Command{
		commands.NewGetBalanceCommand(createDbClient),
		commands.NewSetBalanceCommand(createDbClient),
	}

	session, err := discord.NewDiscordSession(conf, commandList)
	if err != nil {
		log.Fatal(err)
	}

	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
	<-sc

	session.Close()
}
