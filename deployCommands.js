const { getJSFiles } = require("./util/getJSFiles.js");
const { REST } = require("@discordjs/rest");
const { Routes } = require("discord-api-types/v9");
const { clientId, guildId, botToken } = require("./config.json");

const commands = [];
for (const file of getJSFiles("./commands")) {
  const command = require(file);
  commands.push(command.data.toJSON());
}

const rest = new REST({ version: "9" }).setToken(botToken);

rest
  .put(Routes.applicationGuildCommands(clientId, guildId), { body: commands })
  .then(() => console.log("Successfully registered application commands."))
  .catch(console.error);
