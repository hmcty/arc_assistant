const { google } = require("googleapis");
const { MessageEmbed } = require("discord.js");
const { SlashCommandBuilder } = require("@discordjs/builders");
const { googleCalendarApiKey, googleCalendarId } = require("../../config.json");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("today")
    .setDescription("Sends all calendar events scheduled for today."),
  async execute(interaction) {
    const calendar = google.calendar({
      version: "v3",
      auth: googleCalendarApiKey,
    });

    const today = new Date();
    const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);
    const res = await calendar.events.list({
      calendarId: googleCalendarId,
      timeMin: today.toISOString(),
      timeMax: tomorrow.toISOString(),
      maxResults: 25,
      singleEvents: true,
      orderBy: "startTime",
    });

    const events = res.data.items;
    if (events.length) {
      const embed = new MessageEmbed()
        .setColor("#0099ff")
        .setTitle("Today's Events");
      events.map((event, i) => {
        const date = new Date(event.start.dateTime || event.start.date);
        embed.addField(event.summary, date.toDateString());
      });

      await interaction.reply({ embeds: [embed] });
    } else {
      await interaction.reply("No events scheduled for today.");
    }
  },
};
