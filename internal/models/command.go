package models

type Command interface {
	Name() string
	Description() string
	Options() []CommandOption
	Run(config Config, client DbClient, options []CommandOption) string
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
	NumberOption                            = 10
	AttachmentOption                        = 11
)

type CommandOption struct {
	Name     string
	Type     CommandOptionType
	Required bool
	Value    interface{}
	Options  []*CommandOption
}

type User struct {
	ID            string
	Email         string
	Username      string
	Avatar        string
	Locale        string
	Discriminator string
	Token         string
	Verified      bool
	MFAEnabled    bool
	Banner        string
	AccentColor   int
	Bot           bool
	PublicFlags   UserFlags
	PremiumType   int
	System        bool
	Flags         int
}

type UserFlags int

const (
	UserFlagDiscordEmployee           UserFlags = 1 << 0
	UserFlagDiscordPartner            UserFlags = 1 << 1
	UserFlagHypeSquadEvents           UserFlags = 1 << 2
	UserFlagBugHunterLevel1           UserFlags = 1 << 3
	UserFlagHouseBravery              UserFlags = 1 << 6
	UserFlagHouseBrilliance           UserFlags = 1 << 7
	UserFlagHouseBalance              UserFlags = 1 << 8
	UserFlagEarlySupporter            UserFlags = 1 << 9
	UserFlagTeamUser                  UserFlags = 1 << 10
	UserFlagSystem                    UserFlags = 1 << 12
	UserFlagBugHunterLevel2           UserFlags = 1 << 14
	UserFlagVerifiedBot               UserFlags = 1 << 16
	UserFlagVerifiedBotDeveloper      UserFlags = 1 << 17
	UserFlagDiscordCertifiedModerator UserFlags = 1 << 18
)
