from lol_esports_parser import get_riot_series
from lol_esports_parser import get_riot_game
from leaguepedia_sb_parser.parser import Parser


class RiotParser(Parser):
    
    def parse_series(self, urls: list, include_header=True):
        series = get_riot_series(urls, get_timeline=True, add_names=True)
        teams = self.determine_teams_from_game_1(series)
        output_parts = []
        if include_header:
            output_parts.append(self.make_match_header(teams))
        for i, game in enumerate(series['games']):
            output_parts.append(self.parse_one_game(game, urls[i]))
        return '\n'.join(output_parts)
    
    def parse_game(self, url):
        game = get_riot_game(url)
        return self.parse_one_game(game, url)
    
    def get_player_ingame_name(self, ingame_name, team_name):
        return ' '.join(ingame_name.split(' ')[1:])
