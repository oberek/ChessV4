import random
from tkinter import *
import re
import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
import time

logfile = open("chess.log", 'w')
types_in_english = {'K': "King", 'Q': "Queen", 'B': "Bishop", 'R': "Rook", 'N': "Knight", 'P': "Pawn"}
colors = {'l': 'White', 'd': 'Black'}
Player_One = None
Player_Two = None


class FileIO:
    def read_file(self, file):
        file = open(file, 'r')
        return file

    def line_to_piece(self, line):
        piece_type = types[line[:1]]
        color = colors[line[1:2]]
        location = line[-2:]
        piece = piece_type(color, location)
        print(str(color) + " " + str(types_in_english[line[:1]]) + " placed on " + location)

        return piece

    def parse_input(self, line, chessboard):
        if re.match('[KQBRNP][ld][a-h][1-8]', line):
            piece = self.line_to_piece(line[:4])
            for square in Chessboard.chess_board:
                if square.get_loc() == line[2:4]:
                    square.set_piece(piece)
                    chessboard.get_square(line[2:4]).set_piece(piece)
            return False

        elif re.match('\s*[a-h][1-8]\s+[a-h][1-8]\*?$', line):
            move_from = line.split()[0].strip()
            move_to = line.split()[1].strip()

            result = chessboard.move_piece(move_from, move_to, chessboard)
            return result

        elif re.match("[a-h][1-8]\*?$", line):
            chessboard.display_moves(line, chessboard)
            return True

        else:
            print("ERROR: INVALID INPUT. PLEASE TRY AGAIN.")
            return False


class Square:
    def __init__(self, location):
        self.__piece = None
        self.__location = location

    def get_piece(self):
        return self.__piece

    def set_piece(self, piece):
        self.__piece = piece

    def get_loc(self):
        return self.__location

    def has_piece(self):
        if self.__piece is not None:
            return True
        return False


def promote_pawn(chessboard, move_to, piece):
    if 'p' in piece.get_rep().lower():
        if '8' in piece.get_location() or '1' in piece.get_location():
            square = chessboard.get_square(move_to)
            color = piece.get_color()
            response = ' '
            while response not in 'RQBN':
                player = Player_One if piece.get_color() == 'White' else Player_Two
                if player.get_nature() == 'Human':
                    response = input(
                        "Pawn Promoted! What piece would you like to Promote the Pawn to? [n]Knight [q]Queen [r]Rook [b]Bishop: "
                    ).upper().strip()
                else:
                    response = random.choice(['N', 'Q', 'R', 'B'])
                    print("Pawn on " + move_to + " Promoted via AI into a " + types_in_english[response])

            square.set_piece(types[response](color, move_to))


class Chessboard(object):
    chess_board = [Square(y + x) for x in "87654321" for y in "abcdefgh"]

    def print_chessboard(self):
        print('\n   A  B  C  D  E  F  G  H')
        for i in range(len(self.chess_board)):
            square = self.chess_board[i]
            if 'a' in square.get_loc():
                print(square.get_loc()[-1] + ' ', end='')
            if square.get_piece() is None and 'h' in square.get_loc():
                print(' - ')
            elif square.get_piece() is None:
                print(' - ', end='')
            elif 'h' in square.get_loc():
                print(square.get_piece().get_rep())
            else:
                print(square.get_piece().get_rep(), end='')
        print()

    def clear_board(self):
        for square in self.chess_board:
            square.set_piece(None)

    def has_piece(self, piece_rep):
        for square in self.chess_board:
            if square.get_piece() is not None:
                if square.get_piece().get_rep() == piece_rep:
                    return True
        return False

    def get_king(self, color):
        piece_rep = ' K ' if color == 'White' else ' k '
        for square in self.chess_board:
            if square.has_piece():
                if square.get_piece().get_rep() == piece_rep:
                    return square.get_piece()
        return None

    def get_square(self, pos):
        for square in self.chess_board:
            if square.get_loc() == pos:
                return square

    def get_possible_in_check_moves(self, color, chessboard):
        king = self.get_king(color)
        possible_moves = []
        if king.is_in_check():
            print("KING IN CHECK CONFIRMED")
            attackers = self.get_king_attackers(king, chessboard)
            for attacker in attackers:
                print("ATTACKER: " + types_in_english[
                    attacker.get_rep().strip().upper()] + " at " + attacker.get_location())

            # looks for pieces that can attack the attacking piece
            for square in self.chess_board:
                if square.has_piece() and square.get_piece().get_color() == color:
                    piece = square.get_piece()

                    for attacker in attackers:
                        if attacker.get_location() in piece.get_moves(chessboard):
                            line = piece.get_location() + " " + attacker.get_location()
                            possible_moves.append(line)
            for move in king.get_moves(chessboard):
                if len(self.get_king_attackers(King(color, move), chessboard)) == 0:
                    line = king.get_location() + " " + move
                    possible_moves.append(line)

        print("POSSIBLE IN CHECK MOVES: " + str(possible_moves))
        return possible_moves

    def move_piece(self, move_from=None, move_to=None, chessboard=None):
        if self.get_square(move_from).has_piece():
            piece = self.get_square(move_from).get_piece()
            moves = self.display_moves(move_from, chessboard)
            # Check to see if move is valid

            if len(moves) > 0:
                if move_to in moves:
                    print(piece.get_color() + " " + str(
                        types_in_english[
                            piece.get_rep().strip().upper()]) + " moved from " + move_from + " to " + move_to)

                    # If there's no piece in that spot
                    if not self.get_square(move_to).has_piece():
                        piece.update_location(move_to)
                        self.get_square(move_to).set_piece(piece)
                        self.get_square(move_from).set_piece(None)

                    # if there is a piece in that spot
                    elif piece.get_color() != self.get_square(move_to).get_piece().get_color():
                        print(
                            "Captured " + self.get_square(move_to).get_piece().get_color() + " " + types_in_english[
                                self.get_square(move_to).get_piece().get_rep().strip().upper()])
                        piece.update_location(move_to)
                        self.get_square(move_to).set_piece(piece)
                        self.get_square(move_from).set_piece(None)
                        print(self.get_square(move_to).get_loc())

                    # PAWN PROMOTION
                    promote_pawn(chessboard, move_to, piece, )

                    return True

                else:
                    print("ERROR: INVALID MOVE!!!")
                    return False
        else:
            print("ERROR: No Piece in that Spot!!!")

    def display_moves(self, line, chessboard):
        piece = self.get_square(line.strip()).get_piece()
        if piece is not None:
            piece_moves = piece.get_moves(chessboard)
            if piece_moves is not None:
                return piece_moves
            return []
        else:
            print("Not a valid Piece! Select again!")
            return []

    def get_king_attackers(self, king, chessboard):
        attackers = []
        for square in chessboard.chess_board:
            if square.has_piece() and square.get_piece().get_color() != king.get_color():
                piece = square.get_piece()
                if king.get_location() in piece.get_moves(chessboard):
                    attackers.append(piece)
        return attackers


class Player:
    def __init__(self, color, name):
        self.__name = name
        self.__nature = 'AI' if name == '' else 'Human'
        self.__won = False
        self.__has_king_in_check = False
        self.__color = color

    def get_nature(self):
        return self.__nature

    def take_turn(self, f, chessboard):
        print(self.__color.upper() + " PLAYER'S TURN.")
        king_in_check = self.check_if_in_check(chessboard)
        repeat = True
        if king_in_check:
            print(self.__color + " King is in check!")
        if self.__nature != 'AI':
            line = input("Enter a move or a piece to see where it can go. ")
        else:
            if not king_in_check:
                line = random.choice(list(self.get_valid_moves(chessboard)))
            else:
                print("KING IN CHECK SELECTOR")
                possible_moves = chessboard.get_possible_in_check_moves(self.__color, chessboard)
                if len(possible_moves) > 0:
                    line = random.choice(possible_moves)
                else:
                    print("NO POSSIBLE MOVES; CHECKMATE")
                    sys.exit("DONE")

        print("CHOICE: " + line)
        repeat = self.check_if_player_move_valid(f, line, chessboard, repeat, king_in_check)

        while repeat and chessboard.get_king(self.__color) is not None:
            if self.__nature != 'AI':
                line = input("Enter a move or a piece to see where it can go. ")
            else:
                line = random.choice(list(self.get_valid_moves(chessboard)))
            repeat = self.check_if_player_move_valid(f, line, chessboard, repeat, king_in_check)
        chessboard.print_chessboard()
        return self.check_if_won(chessboard)

    def check_if_player_move_valid(self, f, line, chessboard, repeat, king_in_check):
        if re.match('\s*[a-h][1-8]\s+[a-h][1-8]\*?$', line):
            if chessboard.get_square(line.split()[0]).has_piece():
                piece = chessboard.get_square(line.split()[0]).get_piece()
                if piece.get_color() != self.__color:
                    print("You can't move the other player's piece!! Try again!")
                else:
                    repeat = not f.parse_input(line, chessboard)
            else:
                print("There's nothing in that spot!! Try Again!")
        elif re.match("[a-h][1-8]\*?$", line):
            chessboard.display_moves(line, chessboard)
        return repeat

    def check_if_won(self, chessboard):
        white_king = chessboard.get_king('White')
        black_king = chessboard.get_king('Black')

        if self.__color == 'White':
            if black_king is None:
                self.__won = True
                return True
            if white_king is not None:
                if self.check_if_in_check(chessboard):
                    for attacker in chessboard.get_king_attackers(white_king, chessboard):
                        print("WARNING!!!: WHITE KING IS IN CHECK BY " + str(
                            attacker.get_color() + " " + types_in_english[
                                attacker.get_rep().upper().strip()]) + " at " + attacker.get_location())
                    white_king.set_in_check(True)
                elif not self.check_if_in_check(chessboard) and white_king.is_in_check():
                    white_king.set_in_check(False)

        else:
            if white_king is None:
                self.__won = True
                return True
            if black_king is not None:
                if self.check_if_in_check(chessboard):
                    for attacker in chessboard.get_king_attackers(black_king, chessboard):
                        print("WARNING!!!: BLACK KING IS IN CHECK BY " + str(
                            attacker.get_color() + " " + types_in_english[
                                attacker.get_rep().upper().strip()]) + " at " + attacker.get_location())
                    black_king.set_in_check(True)
                elif not self.check_if_in_check(chessboard) and black_king.is_in_check():
                    black_king.set_in_check(False)

        return False

    def check_if_in_check(self, chessboard):
        king = chessboard.get_king(self.__color)
        if king is not None:
            for square in chessboard.chess_board:
                if square.has_piece():
                    piece = square.get_piece()
                    if king.get_color() != piece.get_color():
                        if king.get_location() in piece.get_moves(chessboard):
                            king.set_in_check(True)
                            return True
            king.set_in_check(False)
            return False

    def won(self):
        return self.__won

    def get_valid_moves(self, chessboard):
        valid_moves = []
        for square in chessboard.chess_board:
            if square.has_piece():
                piece = square.get_piece()
                if piece.get_color() == self.__color:
                    if len(piece.get_moves(chessboard)) > 0:
                        for move_to in piece.get_moves(chessboard):
                            # should return a move in terms of a1 a3
                            move = piece.get_location() + ' ' + move_to
                            print("POSSIBLE MOVE: " + move)
                            # BLOODTHIRSTY AI
                            if chessboard.get_square(move_to).has_piece():
                                # This way, it adds it three times, so it has a higher probability of choosing it
                                valid_moves.append(move)
                                valid_moves.append(move)
                            valid_moves.append(move)
        return valid_moves


'''
****************
**** PIECES ****
****************
'''


class Piece(object):
    def __init__(self, color, location):
        self.__color = color
        self.__location = location
        self.__rep = ' - '

    def get_moves(self, chessboard):
        return []

    def get_rep(self):
        return self.__rep

    def get_color(self):
        return self.__color

    def get_location(self):
        return self.__location

    def update_location(self, location):
        self.__location = location

    def check_if_valid_move(self, move_directions):
        possible_moves = []
        for x, y in move_directions:
            column = self.__location[0]
            row = int(self.__location[1])
            column = chr(ord(column) + x)
            row += int(y)
            row = column + str(row)
            if re.match('[a-h][1-8]\s*$', row):
                possible_moves.append(row)
        return possible_moves

    def remove_impossible_moves(self, possible_moves, chessboard):
        for move_to in possible_moves:
            # if there's no piece there
            if re.match('[a-h][1-8]\s*$', move_to):
                if not chessboard.get_square(move_to).has_piece():
                    pass
                # if color is the same, we don't want it moving there
                elif self.get_color() == chessboard.get_square(move_to).get_piece().get_color():
                    possible_moves.remove(move_to)
        if len(possible_moves) == 0:
            print("NO POSSIBLE MOVES!!!")
            return []
        return possible_moves


class King(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " K " if color == "White" else " k "
        self.__in_check = False

    def get_rep(self):
        return self.__rep

    def set_in_check(self, in_check):
        self.__in_check = in_check

    def is_in_check(self):
        return self.__in_check

    def remove_king_bad_moves(self, possible_moves, chessboard):
        moves = possible_moves
        for move in possible_moves:
            if chessboard.get_square(move).has_piece():
                piece = chessboard.get_square(move).get_piece()
                if piece.get_color() == self.get_color():
                    moves.remove(move)
        return moves

    def get_moves(self, chessboard):
        move_directions = [(1, 1), (1, 0), (1, -1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)]
        possible_moves = self.check_if_valid_move(move_directions)
        possible_moves = self.remove_king_bad_moves(possible_moves, chessboard)
        return possible_moves


class Queen(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " Q " if color == "White" else " q "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        rook_moves = Rook.get_moves(self, chessboard)
        bishop_moves = Bishop.get_moves(self, chessboard)
        return rook_moves + bishop_moves


class Bishop(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " B " if color == "White" else " b "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        possible_moves = []
        for x in range(8):
            move = self.check_if_valid_move([(x + 1, x + 1)])  # Going UpRight
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        for x in range(8):
            move = self.check_if_valid_move([(x + 1, (x + 1) * -1)])  # Going Down
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        for x in range(8):
            move = self.check_if_valid_move([((x + 1) * -1, x + 1)])  # Going Right
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        for x in range(8):
            move = self.check_if_valid_move([((x + 1) * -1, (x + 1) * -1)])  # Going Left
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        return possible_moves


class Knight(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " N " if color == "White" else " n "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        move_directions = [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
        possible_moves = self.check_if_valid_move(move_directions)
        possible_moves = self.remove_impossible_moves(possible_moves, chessboard)
        return possible_moves


class Pawn(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " P " if color == "White" else " p "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        move_directions = []
        if self.get_color() == 'Black':
            move_directions.append((0, -1))
            if '7' in self.get_location() and not chessboard.get_square((self.get_location()[0]) + str(6)).has_piece():
                move_directions.append((0, -2))
        else:
            move_directions.append((0, 1))
            if '2' in self.get_location() and not chessboard.get_square((self.get_location()[0]) + str(3)).has_piece():
                move_directions.append((0, 2))
        possible_offsets = self.check_if_valid_move(move_directions)
        for move in possible_offsets:
            # if there's a pawn in front of it, it can't move there
            if chessboard.get_square(move).has_piece():
                possible_offsets.remove(move)

        # Attack moves
        if self.get_color() == 'Black':
            for move in self.check_if_valid_move([(-1, -1), (1, -1)]):
                if chessboard.get_square(move).has_piece():
                    if chessboard.get_square(move).get_piece().get_color() == 'White':
                        possible_offsets.append(move)
        else:
            for move in self.check_if_valid_move([(1, 1), (-1, 1)]):
                if chessboard.get_square(move).has_piece():
                    if chessboard.get_square(move).get_piece().get_color() == 'Black':
                        possible_offsets.append(move)

        return possible_offsets


class Rook(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " R " if color == "White" else " r "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        possible_moves = []
        for x in range(8):
            move = self.check_if_valid_move([(0, x + 1)])  # Going Up
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        for x in range(8):
            move = self.check_if_valid_move([(0, (x + 1) * -1)])  # Going Down
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        for x in range(8):
            move = self.check_if_valid_move([(x + 1, 0)])  # Going Right
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        for x in range(8):
            move = self.check_if_valid_move([((x + 1) * -1, 0)])  # Going Left
            if len(move) > 0:
                move = move[0]
                if chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() != self.get_color():
                    possible_moves.append(move)
                    break
                elif chessboard.get_square(move).has_piece() and chessboard.get_square(
                        move).get_piece().get_color() == self.get_color():
                    break
                else:
                    possible_moves.append(move)
        return possible_moves


types = {'K': King, 'Q': Queen, 'B': Bishop, 'R': Rook, 'N': Knight, 'P': Pawn}


def main():
    '''
    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(800, 600)
    w.move(600, 600)
    w.setWindowTitle('Simple')
    w.show()
    '''
    f = FileIO()
    chessboard = Chessboard()
    player1_name = input("Enter Player 1 Name or Leave It Blank for AI: ")
    player2_name = input("Enter Player 2 Name or Leave It Blank for AI: ")
    global Player_One, Player_Two
    Player_One = Player('White', player1_name)
    Player_Two = Player('Black', player2_name)
    player1_name = "Player 1 (AI)"
    player2_name = "Player 2 (AI)"
    begin_time = time.time()
    try:
        input_file = str(sys.argv[1])
        print("INPUT FILE: " + str(input_file))
        places = f.read_file(input_file)

        for line in places:
            print("LINE: " + line)
            f.parse_input(line, chessboard)
            chessboard.print_chessboard()

        while not Player_One.won() and not Player_Two.won():
            Player_One.take_turn(f, chessboard)
            if not Player_One.won():
                Player_Two.take_turn(f, chessboard)

        print("FINAL BOARD")
        chessboard.print_chessboard()
    except IndexError:
        print("OUT OF BOUNDS")
    if Player_One.won():
        print(player1_name + " has won the game!")
    elif Player_Two.won():
        print(player2_name + " has won the game!")
    else:
        print("GAME CRASHED WITHOUT ANYONE WINNING")
    print("--- %s seconds ---" % (time.time() - begin_time))
    sys.exit("GAME OVER")


if __name__ == '__main__':
    main()
