# projects
# игра крестики нолики
def display_board(board):
    print('\n'*100)
    print(board[1] + ' | ' + board[2] + ' | ' + board[3])
    print(board[4] + ' | ' + board[5] + ' | ' + board[6])
    print(board[7] + ' | ' + board[8] + ' | ' + board[9])

def player_input():
    marker = ''
    while not(marker == 'X' or marker == '0'):
        marker = input('Игрок 1: Кем вы хотите играть, X или 0? ').upper()
    if marker == 'X':
        return ('X', '0')
    else:
        return ('0', 'X')

def place_marker(board, marker, position):
    board[position] = marker

def win_check(board,mark):
    return ((board[7] == mark and board[8] == mark and board[9] == mark) or
         (board[4] == mark and board[5] == mark and board[6] == mark) or
         (board[1] == mark and board[2] == mark and board[3] == mark) or
         (board[7] == mark and board[4] == mark and board[1] == mark) or
         (board[8] == mark and board[5] == mark and board[2] == mark) or
         (board[9] == mark and board[6] == mark and board[3] == mark) or
         (board[7] == mark and board[5] == mark and board[3] == mark) or
         (board[9] == mark and board[5] == mark and board[1] == mark))

import random

def choose_first():
    if random.randint(0, 1) == 0:
        return 'Игрок 2'
    else:
        return 'Игрок 1'

def space_check(board, position):
    return board[position] == ' '

def full_board_check(board):
    for i in range(1,10):
        if space_check(board,i):
            return False
    return True

def player_choice(board):
    position = 0
    while position not in [1,2,3,4,5,6,7,8,9] or not space_check(board, position):
        position = int(input('Укажите поле: (1-9) '))
    return position

def replay():
    choise = input('Хотите играть снова? Введите Yes или No ').lower()
    return choise == 'yes'

print('Добро пожаловать в игру Крестики-Нолики! ')

while True:
    the_board = [' ']*10
    player1_marker, player2_marker = player_input()

    turn = choose_first()
    print(turn +' Ходит первым')

    play_game = input('Вы готовы играть? Введите Yes или No ').lower()

    if play_game == 'yes':
        game_on = True
    else:
        game_on = False

    while game_on:
        if turn == 'Игрок 1':
            display_board(the_board)
            position = player_choice(the_board)
            place_marker(the_board, player1_marker, position)
            if win_check(the_board, player1_marker):
                display_board(the_board)
                print('Игрок 1 выиграл!')
                game_on = False
            else:
                if full_board_check(the_board):
                    display_board(the_board)
                    print('Ничья!')
                    game_on = False
                else:
                    turn = 'Игрок 2'
        else:
            display_board(the_board)
            position = player_choice(the_board)
            place_marker(the_board, player2_marker, position)
            if win_check(the_board, player2_marker):
                display_board(the_board)
                print('Игрок 2 выиграл!')
                game_on = False
            else:
                if full_board_check(the_board):
                    display_board(the_board)
                    print('Ничья!')
                    game_on = False
                else:
                    turn = 'Игрок 1'

    if not replay():
        break
