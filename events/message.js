const nodemailer = require("nodemailer");
const { Users } = require("../database/dbObjects.js");
const {
  guildId,
  verifiedRoleId,
  verifyDomain,
  smtpServer,
  smtpPort,
  smtpUser,
  smtpPass,
} = require("../config.json");

module.exports = {
  name: "messageCreate",
  async execute(message) {
    if (message.inGuild()) return;
    const id = message.author.id;
    const user = await Users.findOne({ where: { user_id: id } });
    if (user === null) return;

    await user.getLatestVerify().then(async (latest) => {
      if (latest === null) {
        // User hasn't started verification process
        return;
      } else if (latest.email === null) {
        // User needs to input email
        const emailRegex = new RegExp(`\\w+@${verifyDomain}`);
        let email = message.content.match(emailRegex);
        if (!email || email.length == 0) {
          await message.reply(
            "Invalid email address. Please reply with your `" +
              verifyDomain +
              "` email address to verify your account."
          );
          return;
        }

        // Generate and send code
        const code = Math.floor(Math.random() * 9999).toString();

        const transporter = nodemailer.createTransport({
          host: smtpServer,
          port: smtpPort,
          secure: smtpPort == 465,
          auth: {
            user: smtpUser,
            pass: smtpPass,
          },
        });

        await transporter.sendMail({
          from: "Purdue ARC <" + smtpUser + ">",
          to: email,
          subject: "Discord Server Verification",
          text: "Your verification code is: " + code,
        });

        transporter.close();

        // Save email and code
        await user.startVerify(message.content, code);
        await message.reply(
          "Reply with the verification code sent to your email!"
        );
      } else {
        // Check that code is correct and set role accordingly
        if (message.content === latest.code) {
          const guild = await message.client.guilds.fetch(guildId);
          if (guild == null) {
            throw new Error("Guild could not be found.");
          }

          const member = await guild.members.fetch(id);
          if (member == null) {
            throw new Error("Member could not be found");
          }

          const role = await guild.roles.fetch(verifiedRoleId);
          if (role == null) {
            throw new Error("Role could not be found");
          }

          await member.roles.add(role);
          await message.reply("Verified!");
        } else {
          await message.reply("Incorrect code!");
        }
      }
    });
  },
};
