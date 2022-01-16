const { SlashCommandBuilder } = require('@discordjs/builders');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('8ball')
		.setDescription('Makes a decision.'),
	async execute(interaction) {
        const options = ["yes", "no", "certainly", "definetly not"]
        const index = Math.floor(Math.random() * options.length);
		await interaction.reply("My answer is: " + options[index]);
	},
};