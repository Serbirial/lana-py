module.exports = {
	apps : [{
		script: './cluster_launch.py',
		name: 'Lana AR (Bot Cluster)',
		interpreter: "python3.11"
	}, {
		script: './api.py',
		name: 'Lana AR (API)',
		interpreter: "python3.11"
	}, {
		script: './dashboard.py',
		name: 'Lana AR (Dashboard)',
		interpreter: "python3.11"
	},],
};