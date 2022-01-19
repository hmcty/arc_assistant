module.exports = (sequelize, DataTypes) => {
	return sequelize.define('user_verify', {
		user: DataTypes.STRING,
		email: DataTypes.STRING,
		code: DataTypes.STRING,
	});
};