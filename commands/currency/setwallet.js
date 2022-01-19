const { SlashCommandBuilder } = require("@discordjs/builders");
const { Users } = require("../../database/dbObjects.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("setwallet")
    .setDescription("Stores wallet address of sender.")
    .addStringOption((option) =>
      option
        .setName("wallet")
        .setDescription("Wallet address to be set")
        .setRequired(true)
    ),
  async execute(interaction) {
    // TODO: verify wallet

    const user = (
      await Users.findOrCreate({
        where: { user_id: interaction.member.id },
      })
    )[0];

    await user.setWallet(interaction.options.getString("wallet"));
    await interaction.reply("Updated wallet address");
  },
};
