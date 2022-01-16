const { google } = require('googleapis');
const { MessageEmbed } = require('discord.js');
const { SlashCommandBuilder } = require('@discordjs/builders');
const { googleCalendarApiKey, googleCalendarId } = require('../config.json');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('week')
		.setDescription('Sends all calendar events scheduled for the week.'),
	async execute(interaction) {
		const calendar = google.calendar({version: 'v3', auth: googleCalendarApiKey});

		const today = new Date();
		const nextWeek = new Date(today.getTime() + (7 * 24 * 60 * 60 * 1000));
		const res = await calendar.events.list({
			calendarId: googleCalendarId,
			timeMin: today.toISOString(),
			timeMax: nextWeek.toISOString(),
			maxResults: 25,
			singleEvents: true,
			orderBy: 'startTime',
		  });

		const events = res.data.items;
		if (events.length) {
			const embed = new MessageEmbed()
				.setColor('#0099ff')
				.setTitle('This Week\'s Events')
			events.map((event, i) => {
				const date = new Date(event.start.dateTime || event.start.date);
				embed.addField(event.summary, date.toDateString());
			})
			
			await interaction.reply({embeds: [embed]})
		} else {
			await interaction.reply("No events this week.");
		}
	},
};