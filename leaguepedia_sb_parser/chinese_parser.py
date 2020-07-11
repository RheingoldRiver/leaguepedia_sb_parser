import re
from leaguepedia_sb_parser.parser import Parser
from lol_esports_parser import get_qq_series


class ChineseParser(Parser):
    
    def parse_series(self, url: str, include_header=True):
        series = get_qq_series(url)
        teams = self.determine_teams_from_game_1(series)
        output_parts = []
        if include_header:
            output_parts.append(self.make_match_header(teams))
        for i, game in enumerate(series['games']):
            output_parts.append(self.parse_one_game(game, url))
        return '\n'.join(output_parts)
    
    def parse_game(self, url):
        pass

    def get_player_ingame_name(self, ingame_name, team_name):
        return re.sub(r'^' + team_name, '', ingame_name)
