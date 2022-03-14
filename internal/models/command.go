package models

import (
	"github.com/hmccarty/arc-assistant/internal/services/config"
)

type Command interface {
	Name() string
	Description() string
	Options() []CommandOption
	Run(config *config.Config, client *DbClient, options []CommandOption) string
}

type CommandOptionType uint8

const (
	SubCommandOption      CommandOptionType = 1
	SubCommandGroupOption                   = 2
	StringOption                            = 3
	IntegerOption                           = 4
	BooleanOption                           = 5
	UserOption                              = 6
	ChannelOption                           = 7
	RoleOption                              = 8
	MentionableOption                       = 9
	Number                                  = 10
	AttachmentOption                        = 11
)

type CommandOption struct {
	Name    string
	Type    CommandOptionType
	Value   interface{}
	Options []*CommandOption
}
