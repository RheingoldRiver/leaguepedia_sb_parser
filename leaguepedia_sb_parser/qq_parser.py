import re

from lol_qq_parser.parsers.match_detail import get_series_basic_info

from leaguepedia_sb_parser.parser import Parser


class QQParser(Parser):
    def parse_series(self, match_id, include_header=True):
        if isinstance(match_id, list):
            match_id = match_id[0]
        if isinstance(match_id, str):
            match_id = int(match_id)
        series = get_series_basic_info(match_id)
        output_parts = []
        for i, game in enumerate(series.games):
            self.populate_teams(game)
            output_parts.append(self.parse_one_game(game, self.qq_url(match_id)))
        if include_header:
            output_parts.insert(0, self.make_match_header())
        return '\n'.join(output_parts)

    @staticmethod
    def qq_url(match_id):
        return "https://lpl.qq.com/es/stats.shtml?bmid={}".format(str(match_id))

    def parse_game(self, url):
        pass

    def get_player_ingame_name(self, ingame_name, team_name):
        # remove all hanzi characters from team_name
        # these are like random city names added at the start of the name in 2021 season
        team_name = re.search(r'[A-Za-z0-9 ]*$', team_name)[0]
        return re.sub(r'^' + team_name, '', ingame_name.strip())

    def get_initial_team_name(self, team):
        return team.sources.qq.tag.strip()

    def get_resolved_patch(self, patch):
        # whatever we get from the game is gonna be completely garbage
        return self.patch
