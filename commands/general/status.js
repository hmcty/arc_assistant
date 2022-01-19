const { SlashCommandBuilder } = require('@discordjs/builders');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('status')
		.setDescription('Replies with the current status of the bot.'),
	async execute(interaction) {
		await interaction.reply('still alive lol');
	},
};