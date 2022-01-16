module.exports = (sequelize, DataTypes) => {
	return sequelize.define('user_wallet', {
		user: DataTypes.STRING,
		wallet_address: DataTypes.STRING,
	}, {
		timestamps: false,
	});
};