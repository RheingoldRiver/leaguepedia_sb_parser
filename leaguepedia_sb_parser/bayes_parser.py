import lol_esports_parser
from lol_esports_parser.bayes import get_game

from leaguepedia_sb_parser.riot_parser import RiotParser


class BayesParser(RiotParser):
    statslink = 'rpgid'
    version = 5

    @staticmethod
    def get_series(urls):
        return lol_esports_parser.bayes.get_series(urls, get_details=True)

    def parse_game(self, platform_game_id):
        game = get_game(platform_game_id)
        return self.parse_one_game(game, platform_game_id, key="riot_platform_game_id")
