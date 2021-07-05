from lol_esports_parser import get_riot_series
from lol_esports_parser import get_riot_game
from leaguepedia_sb_parser.parser import Parser


class RiotParser(Parser):
    
    def parse_series(self, urls: list, include_header=True):
        series = get_riot_series(urls, get_timeline=True, add_names=True)
        output_parts = []
        for i, game in enumerate(series['games']):
            self.populate_teams(game, url=urls[i])
            output_parts.append(self.parse_one_game(game, urls[i]))
        if include_header:
            output_parts.insert(0, self.make_match_header())
        return '\n'.join(output_parts)
    
    def parse_game(self, url):
        game = get_riot_game(url)
        return self.parse_one_game(game, url)
    
    def get_player_ingame_name(self, ingame_name, team_name):
        if ingame_name is None:
            return None
        return ' '.join(ingame_name.strip().split(' ')[1:].strip())
    
    def determine_teams_from_wiki(self, url):
        result = self.site.query_riot_mh(url)
        self.teams = [result['Blue'], result['Red']]
