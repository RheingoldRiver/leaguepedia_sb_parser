from typing import List

from leaguepedia_sb_parser.riot_parser import RiotParser
from lol_esports_parser.riot import get_live_series


class LiveParser(RiotParser):
    statslink = 'rpgid'
    version = 5

    SERVER_TO_REGION = {
        'NA1': 'AMERICAS',
        'BR1': 'AMERICAS',
        'LA1': 'AMERICAS',
        'LA2': 'AMERICAS',
        'OC1': 'AMERICAS',
        'KR': 'ASIA',
        'JP1': 'ASIA',
        'EUN1': 'EUROPE',
        'EUW1': 'EUROPE',
        'TR1': 'EUROPE',
        'RU': 'EUROPE',
    }

    @staticmethod
    def get_series(urls: List[str]):
        url1 = urls[0]
        server = url1.split('_')[0]
        region = LiveParser.SERVER_TO_REGION[server]
        return get_live_series(region, urls, 'team1', 'team2')

    @staticmethod
    def is_live_server(url: str) -> bool:
        if LiveParser.SERVER_TO_REGION.get(url.split('_')[0]) is not None:
            return True
        return False
