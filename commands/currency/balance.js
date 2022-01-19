const { SlashCommandBuilder } = require("@discordjs/builders");
const { Users } = require("../../database/dbObjects.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("balance")
    .setDescription("Replies with member's ARC coin balance."),
  async execute(interaction) {
    const from = (
      await Users.findOrCreate({
        where: { user_id: interaction.member.id },
      })
    )[0];

    // Collect info on wallet data

    await interaction.reply(`You have ${from.balance_owed} ARC coins`);
  },
};
