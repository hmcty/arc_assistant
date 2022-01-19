const { SlashCommandBuilder } = require('@discordjs/builders');
const { MessageEmbed } = require('discord.js');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('poll')
		.setDescription('Creates poll with "Yes", "No", and "Maybe" options.')
        .addStringOption(option =>
            option.setName('title')
                .setDescription('Title of the poll')
                .setRequired(true)),
	async execute(interaction) {
        const embed = new MessageEmbed()
            .setColor('#0099ff')
            .setTitle(interaction.options.getString('title'))
            .setDescription('Poll created by: ' + interaction.user.username + ', react to vote!')
		await interaction.reply({embeds:[embed]});
        const message = await interaction.fetchReply();
        message.react('👍');
        message.react('👎');
        message.react('🤷');
	},
};