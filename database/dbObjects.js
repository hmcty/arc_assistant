const Sequelize = require('sequelize');

const sequelize = new Sequelize('database', 'username', 'password', {
	host: 'localhost',
	dialect: 'sqlite',
	logging: false,
	storage: 'database.sqlite',
});

const Users = require('./models/Users.js')(sequelize, Sequelize.DataTypes);
const UserWallet = require('./models/UserWallet.js')(sequelize, Sequelize.DataTypes);
UserWallet.belongsTo(Users, { foreignKey: 'user', as: 'user_id' });

const UserVerify = require('./models/UserVerify.js')(sequelize, Sequelize.DataTypes);
UserVerify.belongsTo(Users, { foreignKey: 'user', as: 'user_id' });
Reflect.defineProperty(Users.prototype, 'startVerify', {
	value: async function startVerify(guildId, email, code) {
		return UserVerify.create({ user: this.user_id, guild: guildId, email: email, code: code });
	},
})

Reflect.defineProperty(Users.prototype, 'getLatestVerify', {
	value: async function getLatestVerify() {
		return UserVerify.findOne({
			where: { user: this.user_id },
			order: [['createdAt', 'DESC']],
		});
	},
})

module.exports = { Users };