class ApiWrapper:
	def __init__(self):
		self.configuration = cfbd.Configuration()
		self.configuration.api_key['Autorization'] = 'SZ8CksG6lAmx+awFAWXID/ppD0/IhB0bfzBxjlnW4b4GawTpG+OIGygfds82qgOK'
		self.configuration.api_key_prefix['Authorization'] = 'Bearer'
		self.gamesapi = cfbd.GamesApi(cfbd.ApiClient(self.configuration))
		self.scoreboardapi = cfbd.ScoreboardGame(cfbd.ApiClient(self.configuration))
		self.teamsapi = cfbd.TeamsApi(cfbd.ApiClient(self.configuration))
		self.statsapi = cfbd.StatsApi(cfbd.ApiClient(self.configuration))

	def get_team_api_call(self):
		teams = self.teamsapi.get_fbs_teams(year = 2021)
		return teams

	def get_teams_dict(self):
		team_dict: Dict[int, Team] = dict()
		o = self.get_teams_api_call()
		for i, rawschool in enumerate(o):
			abbreviation = rawschool.abbreviation
			school = rawschool.school
			mascot = rawschool.mascot
			conference = rawschool.conference
			id = rawschool.id
			team = Team(id, school, mascot, abbreviation, conference)
			team_dict[school] = team
		return team_dict

	def insert_team_record_for_team(self, team: Team):
		record: cfbd.TeamRecord = self.gamesapi.get_team_records(team = team.school, year=2021)
		record = record[0]
		team_record = TeamRecord(record.total["games"],
								record.total["wins"],
								record.total["losses"])
		team.set_team_record(team_record)

	def insert_stats_for_team(self, team: Team):
		stats: cfbd.AdvancedSeasonStat = self.statsapi.get_advanced_team_season_stats(team = team.school, year = 2021)
		stats = stats[0]
		record: cfbd.TeamRecord = self.gamesapi.get_team_records(team = team.school, year = 2021)
		record = record[0]
		seasonal_stats = SeasonStats(stats.offense["plays"],
									stats.offense["successRate"],
									stats.offense["explosiveness"],
									stats.offense["rushingPlays"]["rate"],
									stats.offense["rushingPlays"]["successRate"],
									stats.offense["rushingPlays"]["explosiveness"],
									stats.offense["passingPlays"]["rate"],
									stats.offense["passingPlays"]["successRate"],
									stats.offense["passingPlays"]["explosiveness"],
									stats.defense["plays"],
									stats.defense["successRate"],
									stats.defense["explosiveness"],
									stats.defense["rushingPlays"]["rate"],
									stats.defense["rushingPlays"]["successRate"],
									stats.defense["rushingPlays"]["explosiveness"],
									stats.defense["passingPlays"]["rate"],
									stats.defense["passingPlays"]["successRate"],
									stats.defense["passingPlays"]["explosiveness"],
									record.total["games"], 
									record.total["wins"],
									record.total["losses"])
		team.set_season_stats(season_stats)

class SeasonStats:
	def __init__(self,
				offense_play,
				offense_success_rate,
				offense_explosiveness,
				offense_rushing_rate,
				offense_rushing_success_rate,
				offense_rushing_explosiveness,
				offense_passing_rate,
				offense_passing_success_rate,
				offense_passing_explosiveness,
				defense_play,
				defense_success_rate,
				defense_explosiveness,
				defense_rushing_rate,
				defense_rushing_success_rate,
				defense_rushing_explosiveness,
				defense_passing_rate,
				defense_passing_success_rate,
				defense_passing_explosiveness,
				team_games,
				team_wins,
				team_losses):
		#Regular Stats
		self.offense_play = offense_play
		self.offense_success_rate = offense_success_rate
		self.offence_explosiveness = offense_explosiveness
		self.offense_rushing_rate = offense_rushing_rate
		self.offense_rushing_success_rate = offense_rushing_success_rate
		self.offense_rushing_explosiveness = offense_rushing_explosiveness
		self.offense_passing_rate = offense_passing_rate
		self.offense_passing_success_rate = offense_passing_success_rate
		self.offense_passing_explosiveness = offense_passing_explosiveness
		self.defense_play = defense_play
		self.defense_success_rate = defense_success_rate
		self.defense_explosiveness = defense_explosiveness
		self.defense_rushing_rate = defense_rushing_rate
		self.defense_rushing_success_rate = defense_rushing_success_rate
		self.defense_rushing_explosiveness = defense_rushing_explosiveness
		self.defense_passing_rate = defense_passing_rate
		self.defense_passing_success_rate = defense_passing_success_rate
		self.defense_passing_explosiveness = defense_passing_explosiveness
		
		self.team_games = team_games
		self.team_wins = team_wins
		self.team_losses = team_losses

		#New Stats
		self.offensive_run_pass_ratrion = self.calc_offensive_run_pass_ratio()
		self.dsr_osr_ratio = self.calc_dsr_osr_ratio()
		self.de_osr_ratio = self.calc_de_osr_ratio()
		self.dsr_wins_ratio = self.calc_dsr_wins_ratio()
		self.winloss_ratio = self.calc_win_loss()

	def calc_offensive_run_pass_ratio(self):
		if self.offense_passing_ratio != 0:
			return self.offense_rushing_rate / self.offense_passing_success_rate
		return 0

	def calc_dsr_osr_ratio(self):
		if self.offense_success_rate != 0:
			return self.defense_success_rate / self.offense_success_rate
		return 0

	def calc_de_osr_ratio(self):
		if self.offense_success_rate != 0:
			return self.defense_explosiveness / self.offense_success_rate
		return 0

	def calc_dsr_wins_ratio(self):
		if self.team_wins != 0:
			return self.defense_success_rate / self.team_wins
		return 0

	def calc_win_loss(self):
		if self.team_losses != 0:
			return self.team_wins / self.team_losses
		return 0


class Team(self):
	def __init__(self, id: int, school: str, mascot: str, abbreviation: str, conference: str, season_stats: SeasonStats = None):
		self.id: int = id
		self.school: str = school
		self.mascot: str = mascot
		self.abbreviation: str = abbreviation
		self.conference: str = conference
		self.season_stats: SeasonStats = season_stats

	def set_season_stats(self, stats: SeasonStats):
		self.season_stats = stats

class GameChanger:
	def __init__(self):
		self.apiwrapper = ApiWrapper()
		self.teams_dict = self.apiwrapper.get_teams_dict()
		self.team_names = self.get_all_team_names()
		for i in self.teams_dict.values():
			self.season_stats = self.apiwrapper.insert_stats_for_team(i)

	def get_all_team_names(self) -> List[str]:
		names = []
		for team in self.teams_dict.values():
			names.append(team.school)
		return names

	def run(self):
		loop = True
		print("What Would You Like to Do? (Input Number)")
		while loop:
			userinput = input("\n1 - Show Seasonal Stats of a Specific Team\n2 - Show Indepth Stats\n3 - Show Scatter Plots\nQ - Quit\n")
			if userinput == "1":
				print(self.team_names)
				team = self.ask_for_team()
				self.show_team(team)
			if userinput == "2":
				print(self.team_names)
				team = self.ask_for_team()
				self.indepth_stats(team)
			if userinput == "3":
				self.wins_to_playstyle()
				self.wins_to_defense_success()
			if userinput == "Q":
				exit()

	def wins_to_defense_success(self):
		for data_dict in self.teams_dict.values():
			if data_dict.season_stats is None:
				self.apiwrapper.insert_stats_for_team(data_dict)
			x = data_dict.season_stats.team_wins
			y = data_dict.season_stats.defense_success_rate
			plt.scatter(x, y)
		plt.xlabel("# of Wins")
		plt.ylabel("Defense Success Rate")
		plt.show()
		return

	def ask_for_team(self) -> Team:
		#todo: check for if team is real
		team = input("What team are you interested in?\n")
		if team not in self.team_names:
			print("Not a valid school")
		else:
			team_object = self.teams_dict[team]
		return team_object

	def show_team(self, team: Team):
		#print team and its stats
		if team.season_stats is None:
			self.apiwrapper.insert_stats_for_team(team)

		table_data_offense = [["Offense", "Defense", "Record"],
							["\tPlays: "+str(team.season_stats.offense_play), "\tPlays: "+str(team.season_stats.defense_play), "\tTotal Games Played: "+str(team.season_stats.team_games)],
							["\tSuccess Rate: "+str(team.season_stats.offense_success_rate), "\tSuccess Rate: "+str(team.season_stats.defense_success_rate), "\tWins: "+str(team.season_stats.team_wins)],
							["\t\tRate: "+str(team.season_stats.offense_rushing_rate), "\t\tRate: "+str(team.season_stats.defense_rushing_rate), ""],
							["\t\tSuccess Rate: "+str(team.season_stats.offense_rushing_success_rate), "\t\tSuccess Rate: "+str(team.season_stats.defense_rushing_success_rate)],
							["\t\tExplosiveness: "+str(team.season_stats.offense_rushing_explosiveness), "\t\tSuccess Rate: "+str(team.season_stats.defense_rushing_explosiveness)],
							["\tPassing: ", "\tPassing: ", ""],
							["\t\tRate: "+str(team.season_stats.offense_passing_rate), "\t\tRate: "+str(team.season_stats.defense_passing_rate), ""],
							["\t\tSuccess Rate: "+str(team.season_stats.offense_passing_success_rate), "\t\tSuccess Rate: "+str(team.season_stats.defense_passing_success_rate)],
							["\t\tExplosiveness: "+str(team.season_stats.offense_passing_explosiveness), "\t\tSuccess Rate: "+str(team.season_stats.defense_passing_explosiveness)]]
		for row in table_data_offense:
			print("{: < 50}{: <60}{: <50}".format(*row))

	def indepth_stats(self, team: Team):
		if team.season_stats is None:
			self.apiwrapper.insert_stats_for_team(team)

		print("\nIn-Depth Statistics: ")
		print("\nWin-Loss Ratio: " + str(team.season_stats.winloss_ratio))
		print("\nRun - To - Pass Ratio: " + str(team.season_stats.offensive_run_pass_ratio))
		print("\nDefensive Success Rate - To - Offense Success Rate: " + str(team.season_stats.dsr_osr_ratio))
		print("\nDefensive Explosiveness - To - Offense Success Rate: " + str(team.season_stats.de_osr_ratio))
		print("\nDefensive Success Rate - To - Wins: " + str(team.season_stats.dsr_wins_ratio))



if __name__ == "__main__":
	print("Welcome to GameChanger!")
	print("Loading Data...")
	print("May Take A Few Minutes")
	gamechanger = GameChanger()
	gamechanger.run()
	team = Team()











