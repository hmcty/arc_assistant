module.exports = {
	name: 'ready',
	once: true,
	execute(client) {
		console.log(`Ready! Logged in as ${client.user.tag}`);
        client.user.setPresence({ 
            activities: [{ name: 'github.com/hmccarty/arc_assistant' }],
            status: 'online',
        });
	},
};