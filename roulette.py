from random import choice, seed


class Roulette:
    test_spin = 0
    test_numbers = []
    wheel_numbers = []
    odd_count = 0
    even_count = 0
    zero_count = 0

    def __init__(self, zero_count_on_wheel=1, test_numbers=[]):
        self.test_numbers = test_numbers
        self.wheel_numbers = list(range(0, 37))
        for _ in range(1, zero_count_on_wheel + 1):
            self.wheel_numbers.append(0)
        seed()

    def spin(self):
        if len(self.test_numbers) > 0:
            spin_number = self.test_numbers[self.test_spin]
            self.test_spin += 1

        else:
            spin_number = choice(self.wheel_numbers)

        if spin_number == 0:
            self.zero_count += 1
            return 'zero'
        elif spin_number % 2 == 0:
            self.even_count += 1
            return 'even'
        elif spin_number % 2 != 0:
            self.odd_count += 1
            return 'odd'


class Player:
    # player stats
    loses_count = 0
    wins_count = 0
    bets_count = 0
    zero_count = 0

    # player thoughts
    equal_spins = 0
    lose_series = 0
    prev_spin_result = ''

    def __init__(self, player_profile):
        self.money = player_profile['money']
        self.start_money = player_profile['money']
        self.max_lose_count = player_profile['max_lose_count']
        self.bet_value = player_profile['bet_value']
        self.skip_spins = player_profile['skip_spins']

    def make_bet(self):
        return [choice(('odd', 'even')), 0]


class MartingalePlayer(Player):
    def make_bet(self):
        # if self.prev_spin_result == 'zero':
        #     self.lose_series = 0

        if self.equal_spins < self.skip_spins or self.lose_series > self.max_lose_count:
            bet_sum = 0
            bet_type = 'skip'
            self.lose_series = 0
        else:
            bet_sum = self.bet_value * (1 if self.lose_series == 0 else 2 ** self.lose_series)
            if self.prev_spin_result == 'even':
                bet_type = 'odd'
            elif self.prev_spin_result == 'odd':
                bet_type = 'even'
            else:
                bet_type = choice(('odd', 'even'))
        return [bet_type, bet_sum]
        
        
class FibonacciPlayer(Player):

    current_fib_position = 0
    current_choice = ''

    def fibo(self, n):
        n1 = 0
        n2 = 1
        for _ in range(n):
            n1, n2 = n2, n1 + n2
        return n1

    def make_bet(self):
        if self.prev_spin_result == '':
            self.current_choice = choice(('odd', 'even'))
            return [self.current_choice, 0]
        elif self.lose_series != 0:
            self.current_fib_position += 1
            return [self.current_choice, self.bet_value * self.fibo(self.current_fib_position)]
        elif self.lose_series == 0:
            if self.current_fib_position - 2 < 0:
                self.current_choice = 'odd' if self.current_choice == 'even' else 'even'
            self.current_fib_position = abs(self.current_fib_position - 2)
            return [self.current_choice, self.bet_value * self.fibo(self.current_fib_position)]
            

class Game:
    def __init__(self, game_number, spin_count, show_spin_stats):
        self.game_number = game_number
        self.spin_count = spin_count
        self.show_spin_stats = show_spin_stats

    def take_bet(self, p, bet):
        p.money -= bet[1]
        if p.money < 0:
            raise Exception('Not enough money to make a bet: {}, {}'.format(bet[0], bet[1]))
        if bet[1] > 0:
            p.bets_count += 1

    def check_result(self, p, bet, spin_result):
        if spin_result == p.prev_spin_result:
            p.equal_spins += 1
        else:
            p.equal_spins = 1
        p.prev_spin_result = spin_result

        if spin_result == bet[0]:
            p.wins_count += 1
            p.lose_series = 0
            p.money += bet[1] * 2
        elif bet[0] != 'skip':
            p.loses_count += 1
            p.lose_series += 1

        if spin_result == 'zero' and bet[0] != 'skip':
            p.zero_count += 1

        if p.money < p.bet_value:
            return 'Out of money'
        else:
            return 'Continue playing'

    def play(self, r, p):
        i = 1
        while i <= self.spin_count:
            bet = p.make_bet()
            self.take_bet(p, bet)
            spin_result = r.spin()
            player_state = self.check_result(p, bet, spin_result)

            if self.show_spin_stats:
                print('Spin {:4d} = {:<4} | Bet = {:<4}, {:4d}$ | Money = {:4d}$'
                      .format(i
                              , spin_result
                              , bet[0]
                              , bet[1]
                              , p.money))

            if player_state == 'Out of money':
                print('')
                print('Player is out of money: Loses = {}; Zeros = {}; Wins = {}; '
                      'Win rate = {:.2%}; Bets = {}; Spins = {}.'
                      .format(p.loses_count
                              , p.zero_count
                              , p.wins_count
                              , (p.wins_count / (p.loses_count + p.wins_count)) if (p.loses_count + p.wins_count) else 0
                              , p.bets_count
                              , i))
                break
            if i == game_profile['spin_count']:
                print('Game {:3d} result | Loses = {:<4} | Zeros = {:<5} | Wins = {:<4} | '
                      'Win rate = {:<7.2%} | Bets = {:<7} | Money = {:<5} | Profit = {:>+7.2%}'
                      .format(self.game_number
                              , p.loses_count
                              , p.zero_count
                              , p.wins_count
                              , (p.wins_count / (p.loses_count + p.wins_count)) if (p.loses_count + p.wins_count) else 0
                              , p.bets_count
                              , p.money
                              , (p.money - p.start_money) / p.start_money))
            i += 1
        return player_state


################################################################################

if __name__ == '__main__':
    # make test_numbers empty [] if random sequence needed
    test_numbers = [28,26,34,9,6,23,25,10,11,6,21,24,33,28,20,20,0,34,20,22,5,
                    33,9,32,32,21,14,16,24,5,10,34,28,20,10,3,12,11,5,22,2,33,
                    32,7,22,32,13,27,30,21,34,7,21,7,5,3,31,10,23,1,29,3,26,32,
                    32,12,35,31,9,27,19,0,2,27,2,36,12,21,7,34,10,27,8,7,12,22,
                    8,32,14,19,6,13,10,9,4,4,31,32,15,13]
    
    player_profile = {'money': 100            # sum of money for the first game (next game gets this value from previous one)
                      , 'max_lose_count': 10  # continue playing with initial bet value
                      , 'bet_value': 1        # sum of money per bet
                      , 'skip_spins': 0       # wait for several equal results in a row
                      }

    game_profile = {'spin_count': 100          # per 1 game
                    , 'games_count': 10        # see 'money' key comment
                    , 'zero_count_on_wheel': 1 # depending on the rules the wheel could have more than 1 zero point
                    , 'show_spin_stats': True  # if false then only whole game stats displayed
                    }

    # for implicit sequence 'spin count' and 'games count' will be ignored
    if len(test_numbers) > 0:
        game_profile['spin_count'] = len(test_numbers)
        game_profile['games_count'] = 1
        print('TEST NUMBERS: ', str(test_numbers))

    print('Games started with {} spins, player has {}$ per game. Player will wait for {} equal spins. '
          'Player skip a spin after {} loses. Initial bet is {}$.'
          .format(game_profile['spin_count']
                  , player_profile['money']
                  , player_profile['skip_spins']
                  , player_profile['max_lose_count']
                  , player_profile['bet_value']))

    total_profit = 0
    start_season_money = player_profile['money']
    for game in range(1, game_profile['games_count'] + 1):

        if game > 1:
            player_profile['money'] = p.money  # to check if money is up after several games

        p = FibonacciPlayer(player_profile) # put preferred player (strategy) here
        r = Roulette(game_profile['zero_count_on_wheel'], test_numbers)
        g = Game(game, game_profile['spin_count'], game_profile['show_spin_stats'])

        if game_profile['show_spin_stats']:
            print('')

        player_state = g.play(r, p)
        if player_state == 'Out of money':
            break
    print('Games ended with Total Profit = {:<+7.2%}'.format((p.money - start_season_money) / start_season_money))
    # print('Total of Zero = {}, Odd = {}, Even = {}'.format(r.zero_count, r.odd_count, r.even_count))
