const { SlashCommandBuilder } = require("@discordjs/builders");
const { coinValue } = require("../../config.json");
const { Users } = require("../../database/dbObjects.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("set")
    .setDescription("Sets current balance of member.")
    .addUserOption((option) =>
      option
        .setName("recipient")
        .setDescription("Member to receive ARC coin")
        .setRequired(true)
    )
    .addIntegerOption((option) =>
      option
        .setName("amount")
        .setDescription("Amount to send")
        .setRequired(true)
    ),
  async execute(interaction) {
    const to = (
      await Users.findOrCreate({
        where: { user_id: interaction.options.getUser("recipient").id },
      })
    )[0];
    await to.update({
      balance_owed: to.balance_owed + interaction.options.getInteger("amount"),
    });
  },
};
