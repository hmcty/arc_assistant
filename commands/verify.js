const { SlashCommandBuilder } = require("@discordjs/builders");
const { Users } = require("../database/dbObjects.js");
const { verifyDomain } = require("../config.json");
const nodemailer = require("nodemailer");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("verify")
    .setDescription("Initiates verification of the user's account."),
  async execute(interaction) {
    const id = interaction.user.id;
    const guildId = interaction.guildId;
    const user = (await Users.findOrCreate({ where: { user_id: id } }))[0];
    await user.startVerify(null, null);

    const dm = await interaction.user.createDM(true);
    await dm.send(
      "Reply with your `" +
        verifyDomain +
        "` email address to verify your account."
    );
    await interaction.reply("Verification started, check your DMs!");
  },
};
