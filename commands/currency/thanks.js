const { SlashCommandBuilder } = require("@discordjs/builders");
const { coinValue } = require("../../config.json");
const { Users } = require("../../database/dbObjects.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("thanks")
    .setDescription("Pays gratitude towards another member using ARC coins.")
    .addUserOption((option) =>
      option
        .setName("recipient")
        .setDescription("Member to receive ARC coin")
        .setRequired(true)
    ),
  async execute(interaction) {
    const from = (
      await Users.findOrCreate({
        where: { user_id: interaction.member.id },
      })
    )[0];

    if (from.balance_owed < coinValue) {
      await interaction.reply("Insufficient balance of ARC coins.");
      return;
    }

    const toId = interaction.options.getUser("recipient").id;
    const to = (
      await Users.findOrCreate({
        where: { user_id: toId },
      })
    )[0];

    await from.update({ balance_owed: from.balance_owed - coinValue });
    await to.update({ balance_owed: to.balance_owed + coinValue });
    await interaction.reply(`Thanked <@${toId}> with ${coinValue} ARC coins`);
  },
};
