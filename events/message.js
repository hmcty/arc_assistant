const nodemailer = require("nodemailer");
const { Users } = require('../database/dbObjects.js');
const { verifyDomain, smtpServer, smtpPort, smtpUser, smtpPass } = require('../config.json');

module.exports = {
	name: 'messageCreate',
    async execute(message) {
		if (message.inGuild()) return;
        const id = message.author.id;
        const user = await Users.findOne({ where: { user_id: id }});
        if (user === null) return;

        await user.getLatestVerify()
            .then(async (latest) => {
                if (latest === null) {
                    return;
                } else if (latest.email === null) {
                    const emailRegex = new RegExp(`\\w+@${verifyDomain}`);
                    let email = message.content.match(emailRegex);
                    if (!email || email.length == 0) {
                        await message.reply("Invalid email address. Please reply with your `" + verifyDomain + "` email address to verify your account.");
                        return;
                    }
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

                    transporter.close()

                    await user.startVerify(id, message.content, code);
                    await message.reply("Reply with the verification code sent to your email!");
                } else {
                    if (message.content === latest.code) {
                        await message.reply("Verified!");
                    } else {
                        await message.reply("Incorrect code!");
                    }
                }
            })
	},
};