import re


class FileIO:
    logfile = open("chess.log", 'w')

    def read_file(self, file):
        file = open(file, 'r')
        return file

    def line_to_piece(self, line):
        types = {'K': King, 'Q': Queen, 'B': Bishop, 'R': Rook, 'N': Knight, 'P': Pawn}
        colors = {'l': 'White', 'd': 'Black'}

        piece_type = types[line[:1]]
        color = colors[line[1:2]]
        location = line[-2:]
        piece = piece_type(color, location)
        return piece

    def parse_input(self, line):
        if re.match('[KQBRNP][ld][a-h][1-8]', line):
            piece = self.line_to_piece(line[:4])
            print('Placed: ' + line)

            for square in Chessboard.chess_board:
                if square.get_loc() == line[2:4]:
                    square.set_piece(piece)
                    get_square(line[2:4]).set_piece(piece)

        elif re.match('\s*[a-h][1-8]\s+[a-h][1-8]\*?$', line):
            move_from = line.split()[0].strip()
            move_to = line.split()[1].strip()
            can_capture = False

            if '*' in move_to:
                can_capture = True
                move_to = move_to.replace('*', '')

            move_piece(move_from, move_to, can_capture)
        elif re.match("[a-h][1-8]\*?$", line):
            display_moves(line)
        else:
            print("ERROR: INVALID INPUT. PLEASE TRY AGAIN.")


class Square:
    __piece = None
    __location = None

    def __init__(self, location):
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


class Chessboard:
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
        print('')

    def clear_board(self):
        for square in self.chess_board:
            square.set_piece(None)

    def has_piece(self, piece_rep):
        for square in self.chess_board:
            if square.get_piece() is not None:
                if square.get_piece().get_rep() == piece_rep:
                    return True
        return False


def get_square(pos):
    # return self.chess_board["abcdefgh".index(pos[0])]["12345678".index(pos[1])]
    for square in Chessboard.chess_board:
        if square.get_loc() == pos:
            return square


class Player:
    def __init__(self, color):
        self.__color = color


def move_piece(move_from=None, move_to=None, can_capture=False):
    if get_square(move_from).has_piece():
        piece = get_square(move_from).get_piece()
        moves = display_moves(move_from)
        # Check to see if move is valid
        if len(moves) > 0:
            if move_to in moves:

                # If there's no piece in that spot
                if not get_square(move_to).has_piece():
                    piece.update_location(move_to)
                    get_square(move_to).set_piece(piece)
                    get_square(move_from).set_piece(None)
                # if there is a piece in that spot
                elif piece.get_color != get_square(move_to).get_piece().get_color():
                    if can_capture:
                        print("Captured " + get_square(move_to).get_piece().get_color() + get_square(
                            move_to).get_piece().get_rep())
                        piece.update_location(move_to)
                        get_square(move_to).set_piece(piece)
                        get_square(move_from).set_piece(None)
                        print(get_square(move_to).get_loc())
                    print("THERE's A PIECE HERE")

            else:
                print("ERROR: INVALID MOVE!!!")
    else:
        print("ERROR: No Piece in that Spot!!!")


def display_moves(line):
    piece = get_square(line.strip()).get_piece()
    if piece is not None:
        piece_moves = piece.get_moves(Chessboard.chess_board)
        print("Possible Moves!!!: " + str(piece_moves))
        if piece_moves is not None:
            return piece_moves
        return []
    else:
        print("Not a valid Piece! Select again!")
        return []


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
            print(move_to)
            if re.match('[a-h][1-8]\s*$', move_to):
                if not get_square(move_to).has_piece():
                    pass
                # if color is the same, we don't want it moving there
                elif self.get_color() == get_square(move_to).get_piece().get_color():
                    print("REMOVED: " + move_to)
                    possible_moves.remove(move_to)
        if len(possible_moves) == 0:
            print("NO POSSIBLE MOVES!!!")
        return possible_moves


class King(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " K " if color == "White" else " k "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        move_directions = [(1, 1), (1, 0), (1, -1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)]
        possible_moves = self.check_if_valid_move(move_directions)
        possible_moves = self.remove_impossible_moves(possible_moves, chessboard)
        return possible_moves


class Queen(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " Q " if color == "White" else " q "

    def get_rep(self):
        return self.__rep


class Bishop(Piece):
    def __init__(self, color, location):
        super().__init__(color, location)
        self.__rep = " B " if color == "White" else " b "

    def get_rep(self):
        return self.__rep

    def get_moves(self, chessboard):
        possible_offsets = [(x, x) for x in range(-8, 8)]
        possible_offsets.extend([(x, -x) for x in range(-8, 8)])
        print(possible_offsets)
        possible_moves = self.check_if_valid_move(possible_offsets)
        possible_moves = self.remove_impossible_moves(possible_moves, chessboard)
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
        print("CURRENT LOCATION: " + self.get_location())
        move_directions = []
        if self.get_color() == 'Black':
            move_directions.append((0, -1))
            if '7' in self.get_location() and not get_square((self.get_location()[0]) + str(6)).has_piece():
                move_directions.append((0, -2))
        else:
            move_directions.append((0, 1))
            if '2' in self.get_location() and not get_square((self.get_location()[0]) + str(3)).has_piece():
                move_directions.append((0, 2))
        possible_offsets = self.check_if_valid_move(move_directions)
        for move in possible_offsets:
            # if there's a pawn in front of it, it can't move there
            if get_square(move).has_piece():
                possible_offsets.remove(move)

        # Attack moves
        if self.get_color() == 'Black':
            for move in self.check_if_valid_move([(-1, -1), (-1, 1)]):
                if get_square(move).has_piece():
                    if get_square(move).get_piece().get_color() == 'White':
                        possible_offsets.append(move)
        else:
            for move in self.check_if_valid_move([(-1, 1), (1, 1)]):
                if get_square(move).has_piece():
                    if get_square(move).get_piece().get_color() == 'Black':
                        possible_offsets.append(move)

        print(possible_offsets)
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
            print("X: " + str(x + 1))
            move1 = self.check_if_valid_move([(0, x + 1)])  # Going Up
        for x in range(8):
            print("X: " + str(x))
            move2 = self.check_if_valid_move([(0, (x + 1) * -1)])  # Going Down
        for x in range(8):
            print("X: " + str(x))
            move3 = self.check_if_valid_move([(x + 1, 0)])  # Going Right
        for x in range(8):
            print("X: " + str(x))
            move4 = self.check_if_valid_move([((x + 1) * -1, 0)])  # Going Left


class Main:
    f = FileIO()
    chessboard = Chessboard()
    player1 = Player('White')
    player2 = Player('Black')

    # Sets up the board
    places = f.read_file("input1.log")

    for line in places:
        print("LINE: " + line)
        f.parse_input(line)
        chessboard.print_chessboard()

    # Starts game
    line = ""
    while line != "ESC" and (chessboard.has_piece(' K ') and chessboard.has_piece(' k ')):
        line = input("Enter a move or a piece to see where it can go. Type ESC to exit. ")
        f.parse_input(line)
        chessboard.print_chessboard()


if __name__ == 'main':
    Main()
