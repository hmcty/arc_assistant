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

Reflect.defineProperty(Users.prototype, 'addItem', {
	/* eslint-disable-next-line func-name-matching */
	value: async function addItem(item) {
		const userItem = await UserItems.findOne({
			where: { user_id: this.user_id, item_id: item.id },
		});

		if (userItem) {
			userItem.amount += 1;
			return userItem.save();
		}

		return UserItems.create({ user_id: this.user_id, item_id: item.id, amount: 1 });
	},
});

Reflect.defineProperty(Users.prototype, 'getItems', {
	/* eslint-disable-next-line func-name-matching */
	value: function getItems() {
		return UserItems.findAll({
			where: { user_id: this.user_id },
			include: ['item'],
		});
	},
});

module.exports = { Users, UserWallet };