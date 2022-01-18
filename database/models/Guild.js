module.exports = (sequelize, DataTypes) => {
	return sequelize.define('guilds', {
		guild_id: {
			type: DataTypes.STRING,
			primaryKey: true,
		},
		verified_role: DataTypes.STRING,
	}, {
		timestamps: false,
	});
};