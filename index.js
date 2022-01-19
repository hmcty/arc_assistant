const { Op } = require("sequelize");
const { Client, Collection, Intents } = require("discord.js");
const { botToken } = require("./config.json");
const { getJSFiles } = require("./util/getJSFiles.js");
const { Users, UserWallet, UserVerify } = require("./database/dbObjects.js");

const client = new Client({
  intents: ["GUILDS", "GUILD_MEMBERS", "GUILD_MESSAGES", "DIRECT_MESSAGES"],
  partials: ["CHANNEL"],
});

// Setup currency cache
const currency = new Collection();

Reflect.defineProperty(currency, "add", {
  /* eslint-disable-next-line func-name-matching */
  value: async function add(id, amount) {
    const user = currency.get(id);

    if (user) {
      user.balance += Number(amount);
      return user.save();
    }

    const newUser = await Users.create({ user_id: id, balance: amount });
    currency.set(id, newUser);

    return newUser;
  },
});

Reflect.defineProperty(currency, "getBalance", {
  /* eslint-disable-next-line func-name-matching */
  value: function getBalance(id) {
    const user = currency.get(id);
    return user ? user.balance : 0;
  },
});

// Load commands
client.commands = new Collection();
for (const file of getJSFiles("./commands")) {
  const command = require(file);
  client.commands.set(command.data.name, command);
}

// Load events
for (const file of getJSFiles("./events")) {
  const event = require(file);
  if (event.once) {
    client.once(event.name, (...args) => event.execute(...args));
  } else {
    client.on(event.name, (...args) => event.execute(...args));
  }
}

client.login(botToken);
