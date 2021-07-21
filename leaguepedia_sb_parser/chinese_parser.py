import re
from leaguepedia_sb_parser.parser import Parser
from lol_esports_parser import get_chinese_series
from lol_esports_parser import get_qq_series
from lol_esports_parser import get_wp_series


class ChineseParser(Parser):
    
    def parse_series(self, match_id, include_header=True):
        # allow to be compatible with receiving data from multi_series_parser
        # which will just blindly split by newlines and return lists
        # easier to correct here than to add correction to both this and riot_parser i guess
        if isinstance(match_id, list):
            match_id = match_id[0]
        if isinstance(match_id, str):
            match_id = int(match_id)
        if len(str(match_id)) == 5:
            series = get_wp_series(self.wp_url(match_id), patch=self.patch)
        else:
            try:
                series = get_chinese_series(match_id, patch=self.patch)
            except Exception as e:
                self.warnings.append(str(e))
                series = get_qq_series(self.qq_url(match_id), patch=self.patch)
        output_parts = []
        for i, game in enumerate(series['games']):
            self.populate_teams(game)
            output_parts.append(self.parse_one_game(game, self.qq_url(match_id)))
        if include_header:
            output_parts.insert(0, self.make_match_header())
        return '\n'.join(output_parts)
    
    def parse_game(self, url):
        pass

    def get_player_ingame_name(self, ingame_name, team_name):
        # remove all hanzi characters from team_name
        # these are like random city names added at the start of the name in 2021 season
        team_name = re.search(r'[A-Za-z0-9 ]*$', team_name)[0]
        return re.sub(r'^' + team_name, '', ingame_name.strip())
    
    def get_resolved_patch(self, patch):
        # whatever we get from the game is gonna be completely garbage
        return self.patch

    def get_checksum(self, game):
        return hex(game['sources']['wp']['id'])

    @staticmethod
    def qq_url(match_id):
        return "https://lpl.qq.com/es/stats.shtml?bmid={}".format(str(match_id))

    @staticmethod
    def wp_url(match_id):
        return "https://www.wanplus.com/schedule/{}.html".format(str(match_id))
