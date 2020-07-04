import time
from lol_esports_parser import get_riot_series, get_riot_game
from river_mwclient.esports_client import EsportsClient
from river_mwclient.wiki_time_parser import time_from_str

HEADER_TEXT = "{{{{MatchRecapS8/Header|{}|{}}}}}"

# |{blue}{1}={args}{items}
PLAYER_TEXT = '|{}{}={{{{MatchRecapS8/Player{}{}}}}}'

GAME_TEXT = '{{{{MatchRecapS8{}{}}}}}'

TEAMS = ['BLUE', 'RED']

# team args, team bans, player args
TEAM_TEXT = '{}{}{}'


class Parser(object):
    def __init__(self, site: EsportsClient, event: str):
        self.site = site
        self.event = site.target(event)
    
    @staticmethod
    def concat_args(lookup: list):
        ret = ''
        for pair in lookup:
            pair: dict
            for key in pair.keys():
                if pair[key] is None:
                    ret = ret + '|{}= '.format(key)
                else:
                    ret = ret + '|{}= {} '.format(key, str(pair[key]))
        return ret
    
    @staticmethod
    def list_args(args: list, param_prefix: str):
        ret = ''
        for i, arg in enumerate(args):
            ret = ret + '|{}{}= {}'.format(param_prefix, str(i + 1), arg)
        return ret
    
    def parse_riot_series(self, urls: list, teams: list = None):
        series = get_riot_series(urls)
        if teams is None:
            teams = self.determine_teams_from_game_1(series)
        output_parts = [self.make_match_header(teams)]
        for game in series['games']:
            output_parts.append(self.parse_one_game(game))
        return '\n'.join(output_parts)
    
    @staticmethod
    def determine_teams_from_game_1(series):
        game = series['games'][0]
        ret = [
            game['teams']['BLUE']['name'],
            game['teams']['RED']['name'],
        ]
        return ret
    
    def make_match_header(self, teams: list):
        return HEADER_TEXT.format(
            self.site.cache.get_team_from_event_tricode(self.event, teams[0]),
            self.site.cache.get_team_from_event_tricode(self.event, teams[1])
        )
    
    def parse_one_game(self, game):
        return GAME_TEXT.format(
            self.concat_args(self.extract_game_args(game)),
            self.parse_teams(game)
        )
    
    def extract_game_args(self, game):
        timestamp = time_from_str(game['start'])
        game_args = [
            {'patch': game['patch']},
            {'winner': 1 if game['winner'] == 'BLUE' else 2},
            {'gamelength': self.get_duration(game['duration']) if 'duration' in game else None},
            {'timezone': 'CET'},
            {'date': timestamp.cet_date},
            {'dst': timestamp.dst},
            {'time': timestamp.cet_time},
        ]
        return game_args
    
    @staticmethod
    def get_duration(duration):
        if duration is None:
            return None
        # format hh:mm:ss and then strip leading 0's for games under 1 hour (aka most games)
        return time.strftime('%H:%M:%S', time.gmtime(duration)).replace('00:', '')
    
    def parse_teams(self, game):
        ret = []
        for i, team in enumerate(TEAMS):
            teamname = 'team{}'.format(str(i+1))
            ret.append(TEAM_TEXT.format(
                self.concat_args(self.extract_team_args(game['teams'][team], teamname)),
                self.list_args(game['teams'][team]['bansNames'], '{}ban'.format(teamname)),
                self.parse_players(team.lower(), game['teams'][team])
            ))
        return '\n'.join(ret)
    
    def extract_team_args(self, team, teamname):
        team_args = [
            {teamname + '': self.site.cache.get_team_from_event_tricode(self.event, team['name'])},
            {teamname + 'g': sum(player['endOfGameStats']['gold'] for player in team['players'])},
            {teamname + 'k': sum(player['endOfGameStats']['kills'] for player in team['players'])},
            {teamname + 'd': team['endOfGameStats']['dragonKills']},
            {teamname + 'b': team['endOfGameStats']['baronKills']},
            {teamname + 't': team['endOfGameStats']['towerKills']},
            {teamname + 'rh': team['endOfGameStats']['riftHeraldKills']},
            {teamname + 'i': team['endOfGameStats']['inhibitorKills']},
        ]
        return team_args
    
    def parse_players(self, side_name, team):
        ret = []
        for i in range(5):
            ret.append(PLAYER_TEXT.format(
                side_name,
                str(i + 1),
                self.concat_args(self.extract_player_args(team['players'][i], team)),
                self.list_args(
                    # don't include the last item because that's actually the trinket
                    [item['name'] for item in team['players'][i]['endOfGameStats']['items'][:-1]],
                    'item'
                )
            ))
        return '\n'.join(ret)
    
    def extract_player_args(self, player, team):
        player_args = [
            {'link': self.site.cache.get_disambiguated_player_from_event(
                self.event,
                self.site.cache.get_team_from_event_tricode(self.event, team['name']),
                ' '.join(player['inGameName'].split(' ')[1:])
            )},
            {'champion': player['championName']},
            {'kills': player['endOfGameStats']['kills']},
            {'deaths': player['endOfGameStats']['deaths']},
            {'assists': player['endOfGameStats']['assists']},
            {'gold': player['endOfGameStats']['gold']},
            {'cs': player['endOfGameStats']['cs']},
            {'visionscore': player['endOfGameStats']['visionScore']},
            {'summonerspell1': player['summonerSpells'][0]['name']},
            {'summonerspell2': player['summonerSpells'][1]['name']},
            {'pentakills': player['endOfGameStats']['pentaKills']},
            {'keystone': player['runes'][0]['name'] if 'runes' in player else None},
            {'secondary': player['secondaryRuneTreeName']},
            {'trinket': player['endOfGameStats']['items'][6]['name']}
        ]
        return player_args
