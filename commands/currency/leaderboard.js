const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("leaderboard")
    .setDescription("Replies with highest holders of ARC coin."),
  async execute(interaction) {
    await interaction.reply("still alive lol");
  },
};
