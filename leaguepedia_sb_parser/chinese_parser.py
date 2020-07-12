import re
from leaguepedia_sb_parser.parser import Parser
from lol_esports_parser import get_chinese_series


class ChineseParser(Parser):
    
    def parse_series(self, match_id, include_header=True):
        if isinstance(match_id, str):
            match_id = int(match_id)
        series = get_chinese_series(match_id)
        teams = self.determine_teams_from_game_1(series)
        output_parts = []
        if include_header:
            output_parts.append(self.make_match_header(teams))
        for i, game in enumerate(series['games']):
            output_parts.append(self.parse_one_game(game, self.qq_url(match_id)))
        return '\n'.join(output_parts)
    
    def parse_game(self, url):
        pass

    def get_player_ingame_name(self, ingame_name, team_name):
        return re.sub(r'^' + team_name, '', ingame_name)
    
    @staticmethod
    def qq_url(match_id):
        return "https://lpl.qq.com/es/stats.shtml?bmid={}".format(str(match_id))
