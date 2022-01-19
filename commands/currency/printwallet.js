const { SlashCommandBuilder } = require("@discordjs/builders");
const { Users } = require("../../database/dbObjects.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("printwallet")
    .setDescription("DMs current wallet address of user."),
  async execute(interaction) {
    const user = (
      await Users.findOrCreate({
        where: { user_id: interaction.member.id },
      })
    )[0];

    const wallet = await user.getWallet();
    if (wallet) {
      await interaction.reply(
        "Current wallet address is `" + wallet.wallet_address + "`"
      );
    } else {
      await interaction.reply(
        "No wallet address set, use `/setwallet <address>`"
      );
    }
  },
};
