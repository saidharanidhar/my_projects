import os
import sys
from time import sleep
from functools import reduce
import shutil
import json
cmd=['pip3 install bs4', 'pip3 install requests']
for c in cmd:
    os.system('clear')
    os.system(c)
from bs4 import BeautifulSoup
import requests


class GetCricket:
    def __init__(self, game_id, note='Match', feature = True):
        self.match_id = game_id
        os.system('notify-send ' + "\'configuring \'" + "\'" + note + "\'")
        self.url = 'http://www.cricbuzz.com/match-api/' + str(self.match_id) + '/commentary.json'
        self.data = requests.get(self.url).json()
        self.player = {i.get('id'): i.get('name') for i in self.data.get('players')}
        self.team = {self.data.get('team1').get('id'): self.data.get('team1').get('s_name'),
                     self.data.get('team2').get('id'): self.data.get('team2').get('s_name')}
        self.team_sum = reduce(lambda a, b: int(a) + int(b), self.team.keys())
        self.match_title = ' vs '.join(self.team.values())
        self.notify_for = ['six', 'four', 'wicket', 'over-break']
        if feature:
            self.notify_for.append('other')
        self.base_temp_folder = '.cric_info_temp'
        self.logo = 'http://i.cricketcb.com/i/stats/flags/web/official_flags/team_{0}.png'
        self.icon = {
            'four': 'http://www.clker.com/cliparts/E/t/R/J/1/h/green-number-4-hi.png',
            'six': 'http://www.clker.com/cliparts/6/V/c/a/Y/A/number-6-green-square-th.png',
            'wicket': 'http://www.clker.com/cliparts/l/G/J/H/P/n/wickets-hi.png',
        }
        for team_id, team_name in self.team.items():
            self.icon[team_name] = self.logo.format(team_id)
        self.temp_icon()
        self.update_changes()
        self.icon['other'] = self.over_break
        self.head = ''
        self.body = ''

    def temp_icon(self):
        self.make_temp()
        new_icon_dict = {}
        for k, v in self.icon.items():
            with open(self.base_temp_folder + '/' + v.split('/')[-1], 'wb') as img:
                img.write(requests.get(v).content)
            new_icon_dict[k] = os.path.abspath('') + '/' + self.base_temp_folder + '/' + v.split('/')[-1]
        self.icon = new_icon_dict

    def make_temp(self):
        if not os.path.exists(self.base_temp_folder):
            os.mkdir(self.base_temp_folder)

    def remove_temp(self):
        if os.path.exists(self.base_temp_folder):
            shutil.rmtree(self.base_temp_folder)

    def make_batsman(self, bat, run, ball, s=''):
        batsman_score = self.player.get(bat) + ':' + run + '(' + ball + ')'
        if s == '1':
            batsman_score += '*'
        return batsman_score + '\n'

    def make_batsman_board(self):
        score_board = ''
        for bat in self.score.get('batsman',[]):
            score_board += self.make_batsman(bat.get('id'), bat.get('r'), bat.get('b'), bat.get('strike'))
        return score_board + '='*33 + '\n'

    def make_bowler(self, bowl, o, m, r, w):
        return self.player.get(bowl) + ' ' + o + '-' + m + '-' + r + '-' + w + '\n'

    def make_bowler_board(self):
        score_board = ''
        for bowl in self.score.get('bowler',[]):
            score_board += self.make_bowler(bowl.get('id'), bowl.get('o'), bowl.get('m'), bowl.get('r'), bowl.get('w'))
        return score_board + '=' * 33 + '\n'

    def last_wicket(self):
        return 'Last Wicket: '+self.player.get(self.score.get('last_wkt'), 'No') + ' ' +\
               self.score.get('last_wkt_score', 'Wicket') + '\n' + self.over_flow + '\n' + \
               self.commentary.get('comm', '')

    def in_command(self):
        self.head = ''.join(self.head.split('"'))
        self.body = ''.join(self.body.split('"'))
        return "\"" + self.head + "\n\" \"" + self.body + "\""

    def make_notification_command(self):
        event = False
        board = ['notify-send', ' -i'] #specific for ubuntu, Customize here
        if self.event in self.notify_for:
            event = True
            board.append(str(self.icon.get(self.event, self.over_break)))
            board.append(self.in_command())
        return ' '.join(board), event

    def update_changes(self):
        self.score = self.data.get('score',{})
        self.state = self.data.get('state','')
        self.status = self.data.get('status','')
        self.commentary = self.data.get('comm_lines', [{}])[0]
        self.event = self.commentary.get('evt','')

        self.batting_team = self.team.get(self.score.get('batting', {}).get('id'), '')
        self.batting_score = self.score.get('batting', {}).get('score', '').replace('Ovs', '')
        self.bowling_team = self.team.get(self.score.get('bowling', {}).get(
            'id', str(self.team_sum-int(self.score.get('batting', {}).get('id',0)))), '')
        self.bowling_score = self.score.get('bowling', {}).get('score', 'Not Played').replace('Ovs', '')
        self.over_break = self.icon.get(self.batting_team)
        self.over_flow = self.score.get('prev_overs', self.commentary.get('o_summary', ''))

        self.head = self.batting_team + ':' + self.batting_score + ' ' + self.bowling_team + ':' +\
                    self.bowling_score + '\n'
        self.body = self.make_batsman_board() + '\n' + self.make_bowler_board() + '\n' + self.last_wicket()

    def start_notifications(self):
        old_cmd = ''
        count=0
        while self.state != 'complete':
            self.data = requests.get(self.url).json()
            self.update_changes()
            cmd, flag = self.make_notification_command()
            if flag and old_cmd != cmd:
                if os.system(cmd) != 0:
                    with open('.log_cric_cmd','a') as file:
                        file.write(json.dumps([dict(body=self.data,command=cmd)],indent=4))
                old_cmd = cmd
                sleep(5)
            elif flag:
                count +=1
                if count==10:
                    count=0
                    os.system(cmd)
                    sleep(5)
            sleep(10)
        os.system("notify-send "+self.status)
        self.remove_temp()


def control():
    os.system('clear')
    req = requests.get('http://www.cricbuzz.com/api/html/homepage-scag')
    soup = BeautifulSoup(req.content, 'html.parser')

    title_dict = {}

    for i in soup.findAll('a', {"class": "cb-font-12"}):
        title = i['title']
        match_id = i['href'].split('/')[2]
        state = i.find('div', class_=' cb-ovr-flo cb-text-complete')
        if state:
            title_dict[title] = state.text
        else:
            title_dict[match_id] = title
    for k, v in title_dict.items():
        print(k, v)

    while True:
        inp = input('Enter match-id:')
        if inp in title_dict.keys() and inp.isdigit():
            break
        print('No in choice')
    feature = input('All notifications (y/n)?')
    feature = True if feature.lower()=='y' else False
    print('configuring...')
    x = GetCricket(inp, note=title_dict[inp], feature=feature)
    print('configured...')
    x.start_notifications()


if __name__ == '__main__':
    try:
        control()
    except KeyboardInterrupt:
        print('Stopping...')
    except Exception as err:
        import traceback
        traceback.print_tb(err.__traceback__)
        print('Error while receiving. try again.')
    finally:
        os.system('notify-send ' + 'Notifications Stopped.')
        os.system('clear')
        sys.exit(0)
