# Author: Griffin Hurley
# Date: 3-4-20
# Portfolio Project
# Description: Xiangqi game simulator with move validation.


class Pieces:
    """
    Parent class for Xiangqi pieces. Initializes color, and methods for
    determining if a piece has crossed the river or is in the palace.
    Individual classes contain is_valid_move which checks if move is pseudo-legal,
    leaving considering if it puts the general in check for the XiangQiGame make_move function.
    """
    def __init__(self, color, piece_type):
        self._color = color
        self._type = piece_type
        self._num_board = set()
        for x in range(0, 100, 10):
            self._num_board = self._num_board.union(*{range(x, x + 9)})

    def get_color(self):
        """
        Returns piece color
        """
        return self._color

    def get_type(self):
        return self._type

    def past_river(self, color, coordinates):
        """
        Returns True if input coordinates are across the river,
        in the direction of the enemy
        """
        if color == 'RED':
            if int(str(coordinates)[0]) > 4:
                return True
            else:
                return False
        else:
            if int(str(coordinates)[0]) < 5:
                return True
            else:
                return False

    def in_palace(self, color, coordinates):
        """
        Returns True if input coordinates are inside palace,
        for respective color.
        """
        if color == 'RED':
            return coordinates in {3, 4, 5, 13, 14, 15, 23, 24, 25}
        else:
            return coordinates in {73, 74, 75, 83, 84, 85, 93, 94, 95}

    def in_board(self, coordinates):
        return coordinates in self._num_board

class Soldier(Pieces):
    def __init__(self, color, piece_type='Soldier'):
        super().__init__(color, piece_type)
        # ways that piece moves, +10 for red, -10 for black.
        self._move_directions = [10 * (-1 if self._color == 'BLACK' else 1)]

    def pseudo_legal_moves(self, start, board):
        moves = set()
        if self.past_river(self.get_color(), start):
            self._move_directions.extend([1, -1])
        for move in self._move_directions:
            if self.in_board(start + move) and not board[start + move]\
                    or self.get_color() != board[start + move].get_color():
                moves.add(start + move)
        return moves

    def is_valid_move(self, start, end, board):
        """
        Checks if end square can be reached using allowed moves
        """
        # # if soldier is past river, let it move horizontally
        # if self.past_river(self.get_color(), start):
        #     self._move_directions.extend([1, -1])
        # # if target square isn't in the list of possible moves, move isn't valid.
        # if end not in [start + x for x in self._move_directions]:
        #     return False
        # return True
        return end in self.pseudo_legal_moves(start, board)

    # def blocking_squares(self, start, end, board):
    #     return {}


class General(Pieces):
    def __init__(self, color, piece_type='General'):
        super().__init__(color, piece_type)
        self._move_directions = [1, -1, 10, -10]

    def pseudo_legal_moves(self, start, board):
        moves = set()
        for move in self._move_directions:
            if self.in_palace(board[start].get_color(), start+move) \
                and (not board[start + move] \
                    or board[start + move].get_color() != self.get_color()):
                moves.add(start+move)
        return moves

    def is_valid_move(self, start, end, board):
        # General can't leave palace
        return end in self.pseudo_legal_moves(start, board)

    def blocking_squares(self, start, end, board):
        return {}


class Advisor(Pieces):
    def __init__(self, color, piece_type='Advisor'):
        super().__init__(color, piece_type)
        self._move_directions = [11, -11, 9, -9]

    def pseudo_legal_moves(self, start, board):
        moves = set()
        for move in self._move_directions:
            if self.in_palace(board[start].get_color(), start + move) \
                and (not board[start + move]
                    or board[start + move].get_color() != self.get_color()):
                moves.add(start + move)
        return moves

    def is_valid_move(self, start, end, board):
        # Advisor can't leave palace
        return end in self.pseudo_legal_moves(start, board)

    def blocking_squares(self, start, end, board):
        return {}


class Chariot(Pieces):
    def __init__(self, color, piece_type='Chariot'):
        super().__init__(color, piece_type)
        self._move_directions = [1, -1, 10, -10]
        self._blocks = set()

    def pseudo_legal_moves(self, start, board):
        moves = set()
        for move in self._move_directions:
            coord = start + move
            while self.in_board(coord):
                if not board[coord]:
                    moves.add(coord)
                    coord += move
                else:
                    if board[coord].get_color() == self.get_color():
                        break
                    else:
                        moves.add(coord)
                        break
        return moves

    def is_valid_move(self, start, end, board):
        # end has to be on either same row or same column as start
        # single digit doesn't work so well with this method make it '01'? then conversion function has to change.
        # If in same row, first digit will be same or both will be single digits
        # if start <= 8 and end <= 8 or str(start)[0] == str(end)[0]:
        #     # Check each row between start and end for an occupied square
        #     for intervening in range(min(start, end) + 1, max(start, end)):
        #         if board[intervening]:
        #             return False
        #     return True
        # # If in same column, difference is multiple of ten
        # if abs(end - start) % 10:
        #     for intervening in range(min(start, end) + 10, max(start, end), 10):
        #         if board[intervening]:
        #             return False
        #     return True
        # # Can't move there if its not orthogonal
        # return False
        return end in self.pseudo_legal_moves(start, board)

    def blocking_squares(self, start, end, _):
        # If in same row, can be blocked at any square in the rank
        if start <= 8 and end <= 8 or str(start)[0] == str(end)[0]:
            for intervening in range(min(start, end) + 1, max(start, end)):
                self._blocks.add(intervening)
        # If in same column, can be blocked at any square in the file
        if abs(end - start) % 10:
            for intervening in range(min(start, end) + 10, max(start, end), 10):
                self._blocks.add(intervening)
        return self._blocks


class Elephant(Pieces):
    def __init__(self, color, piece_type='Elephant'):
        super().__init__(color, piece_type)
        self._elephant_eye = [11, -11, 9, -9]
        self._move_directions = [22, -22, 18, -18]
        self._blocks = set()

    def pseudo_legal_moves(self, start, board):
        moves = set()
        for move in self._move_directions:
            if self.in_board(start + move//2) and not board[start + move//2]:
                if self.in_board(start + move) \
                        and (not board[start + move] or not board[start + move].get_color() == self.get_color()) \
                        and not self.past_river(self.get_color(), start+move):
                    moves.add(start + move)
        return moves

    def is_valid_move(self, start, end, board):
        # # Elephant can't cross river
        # if self.past_river(self.get_color(), end):
        #     return False
        # # Elephant moves two diagonals but first can't be blocked
        # if end not in [start + direction for direction in self._move_directions if not board[start + direction//2]]:
        #     return False
        # return True
        return end in self.pseudo_legal_moves(start, board)

    def blocking_squares(self, start, _, __):
        self._blocks.union(*[{start + x} for x in self._elephant_eye])
        return self._blocks


class Horse(Pieces):
    def __init__(self, color, piece_type='Horse'):
        super().__init__(color, piece_type)
        self._orthogonals = [1, -1, 10, -10]
        self._diagonals = {1: [11, -9], -1: [-11, 9], 10: [9, 11], -10: [-9, -11]}
        self._blocks = set()

    def pseudo_legal_moves(self, start, board):
        moves = set()
        for orthogonal_move in self._orthogonals:
            first_move = start + orthogonal_move
            if self.in_board(first_move) and not board[first_move]:
                for diagonal_move in self._diagonals[orthogonal_move]:
                    second_move = first_move + diagonal_move
                    if self.in_board(second_move) and (not board[second_move]\
                            or not self.get_color() == board[second_move].get_color()):
                        moves.add(second_move)
        return moves

    def is_valid_move(self, start, end, board):
        # non_hobbled = [start + orthogonal for orthogonal in self._orthogonals if not board[start + orthogonal]]
        # if end not in [move + diagonal for move in non_hobbled for diagonal in self._diagonals]:
        #     return False
        # return True
        return end in self.pseudo_legal_moves(start, board)

    def blocking_squares(self, start, _, __):
        self._blocks.union(*[{start + x} for x in self._orthogonals])
        return self._blocks


class Cannon(Pieces):
    def __init__(self, color, piece_type='Cannon'):
        super().__init__(color, piece_type)
        self._move_directions = [1, -1, 10, -10]
        self._pao_tai_cnt = 0
        self._blocks = set()
        self._pao_tai = None
        self._attack_direction = None

    def get_attack_direction(self):
        return self._attack_direction

    def get_pao_tai(self, start, end, board):
        if start <= 8 and end <= 8 or str(start)[0] == str(end)[0]:
            self._attack_direction = 1 if end > start else -1
            for intervening in range(min(start, end) + 1, max(start, end)):
                 if board[intervening]:
                     return intervening
        elif abs(end - start) % 10:
            self._attack_direction = 10 if end > start else -10
            for intervening in range(min(start, end) + 10, max(start, end), 10):
                 if board[intervening]:
                     return intervening
        return

    def pseudo_legal_moves(self, start, board):
        moves = set()
        for move in self._move_directions:
            pao_tai_cnt = 0
            coord = start + move
            while self.in_board(coord):
                if not board[coord]:
                    moves.add(coord)
                    coord += move
                else:
                    if board[coord].get_color() == board[start].get_color:
                        if pao_tai_cnt > 0:
                            break
                    else:
                        if pao_tai_cnt == 1:
                            moves.add(coord)
                        pao_tai_cnt += 1
                        if pao_tai_cnt > 1:
                            break
                    coord += move
        return moves

    def is_valid_move(self, start, end, board):

        return end in self.pseudo_legal_moves(start, board)
        # # reset pao tai and count
        # self._pao_tai_cnt = 0
        # self._pao_tai = None
        #
        # # end has to be on either same row or same column as start
        # # single digit doesn't work so well with this method make it '01'? then conversion function has to change.
        # # If in same row, first digit will be same or both will be single digits
        # if start <= 8 and end <= 8 or str(start)[0] == str(end)[0]:
        #     # Check each row between start and end for an occupied square
        #     for intervening in range(min(start, end) + 1, max(start, end)):
        #         if board[intervening]:
        #             self._pao_tai_cnt += 1
        #             self._pao_tai = intervening
        #     # Move is valid if there are no occupied squares and move isn't a capture or if
        #     # there is one occupied square and move is a capture
        #     if self._pao_tai_cnt == 0 and not board[end]:
        #         return True
        #     elif self._pao_tai_cnt == 1 and board[end]:
        #         self._attack_direction = [1, -1]
        #     else:
        #         return False
        # # If in same column, difference is multiple of ten
        # if abs(end - start) % 10:
        #     for intervening in range(min(start, end) + 10, max(start, end), 10):
        #         if board[intervening]:
        #             self._pao_tai_cnt += 1
        #             self._pao_tai = intervening
        #         if self._pao_tai_cnt == 0 and not board[end]:
        #             return True
        #         elif self._pao_tai_cnt == 1 and board[end]:
        #             self._attack_direction = [10, -10]
        #         else:
        #             return False
        # # Can't move there if its not orthogonal
        # return False

    def blocking_squares(self, start, end, board):
        # blocks require adding another pao tai because there can't be an attack if there isn't one already
        if start <= 8 and end <= 8 or str(start)[0] == str(end)[0]:
            # Check each row between start and end for an occupied square
            for intervening in range(min(start, end) + 1, max(start, end)):
                if not board[intervening]:
                    self._blocks.add(intervening)

        # If in same column, difference is multiple of ten
        if (end - start) % 10:
            for intervening in range(min(start, end) + 10, max(start, end), 10):
                if not board[intervening]:
                    self._blocks.add(intervening)

        return self._blocks


class XiangqiGame:
    # PIECES
    # General: One move orthogonally, within palace, can't face other general
    # Advisor, one move diagonally, within palace
    # Elephant, two moves diagonally, no jumping, can't cross river
    # Horse, one orthogonal then one diagonal, no jumping
    # Cannon, any distance orthogonally, has to jump a single piece to capture though
    # Chariot, any distance orthogonally, no jump
    # Soldier: One forward, until after river, then sideways too, no backward

    def __init__(self):
        # Whose turn it is
        self._turn = 'RED'

        # 'UNFINISHED' until a player is checkmated, then 'RED_WON' or 'BLACK_WON'
        self._game_state = 'UNFINISHED'

        # Locations of each piece
        self._board = {0: Chariot('RED'), 1: Horse('RED'), 2: Elephant('RED'), 3: Advisor('RED'), 4: General('RED')
                       , 5: Advisor('RED'), 6: Elephant('RED'), 7: Horse('RED'), 8: Chariot('RED'), 10: None,
                       11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None,
                       20: None, 21: Cannon('RED'), 22: None, 23: None, 24: None, 25: None, 26: None, 27: Cannon('RED'),
                       28: None, 30: Soldier('RED'), 31: None, 32: Soldier('RED'), 33: None, 34: Soldier('RED'),
                       35: None, 36: Soldier('RED'), 37: None, 38: Soldier('RED'), 40: None, 41: None, 42: None,
                       43: None, 44: None, 45: None, 46: None, 47: None, 48: None, 50: None, 51: None, 52: None,
                       53: None, 54: None, 55: None, 56: None, 57: None, 58: None, 60: Soldier('BLACK'),
                       61: None, 62: Soldier('BLACK'), 63: None, 64: Soldier('BLACK'), 65: None, 66: Soldier('BLACK'),
                       67: None, 68: Soldier('BLACK'), 70: None, 71: Cannon('BLACK'), 72: None, 73: None,
                       74: None, 75: None, 76: None, 77: Cannon('BLACK'), 78: None, 80: None, 81: None,
                       82: None, 83: None, 84: None, 85: None, 86: None, 87: None, 88: None, 90: Chariot('BLACK'),
                       91: Horse('BLACK'), 92: Elephant('BLACK'), 93: Advisor('BLACK'), 94: General('BLACK'),
                       95: Advisor('BLACK'), 96: Elephant('BLACK'), 97: Horse('BLACK'), 98: Chariot('BLACK')}

        # Locations for pieces of each color
        #self._pieces = {'RED': {0, 1, 2, 3, 4, 5, 6, 7, 8, 21, 27, 30, 32, 34, 36, 38},
                        #'BLACK': {60, 62, 64, 66, 68, 71, 77, 90, 91, 92, 93, 94, 95, 96, 97, 98}}
        # Current location for general of each color.
        self._general_location = {'RED': 4, 'BLACK': 94}
        self._saved_board = self._board
        #self._saved_pieces = self._pieces
        self._saved_generals = self._general_location
        # True if a general of that color is in check, else False
        self._in_check = {'RED': False, 'BLACK': False}

    def change_turns(self):
        """Switches to other players turn."""
        if self._turn == 'BLACK':
            self._turn = 'RED'
        else:
            self._turn = 'BLACK'

    def save_game(self):
        self._saved_board = self._board.copy()
        # new_red = set()
        # new_black = set()
        # new_red = new_red.union(self._pieces['RED'])
        # new_black = new_black.union(self._pieces['BLACK'])
        # self._saved_pieces = {'RED': new_red, 'BLACK': new_black}
        self._saved_generals = self._general_location.copy()

    def restore_game(self):
        self._board = self._saved_board.copy()
        # new_red = set()
        # new_black = set()
        # new_red = new_red.union(self._saved_pieces['RED'])
        # new_black = new_black.union(self._saved_pieces['BLACK'])
        # self._saved_pieces = {'RED': new_red, 'BLACK': new_black}
        self._general_location = self._saved_generals.copy()

    def set_board(self, new_board):
        """Sets board state to new_board"""
        self._board = new_board

    def update_board(self, start_move_square, end_move_square):
        """
        Remove piece from board if captured.
        Change board to reflect move made.
        """
        start_color = self._board[start_move_square].get_color()
        # if start_move_square in self._pieces['RED']:
        #     self._pieces['RED'].add(end_move_square)
        #     self._pieces['RED'].remove(start_move_square)
        #     if end_move_square in self._pieces['BLACK']:
        #         self._pieces['BLACK'].remove(end_move_square)
        # elif start_move_square in self._pieces['BLACK']:
        #     self._pieces['BLACK'].add(end_move_square)
        #     self._pieces['BLACK'].remove(start_move_square)
        #     if end_move_square in self._pieces['RED']:
        #         self._pieces['RED'].remove(end_move_square)


        # Update general location if general was piece moved
        if start_move_square == self._general_location[start_color]:
            self._general_location[start_color] = end_move_square
        self._board[end_move_square] = self._board[start_move_square]
        self._board[start_move_square] = None

    def get_game_state(self):
        """Returns game state"""
        return self._game_state

    def convert_algebraic(self, notation):
        """Converts algebraic board notation to the matching integer for self._board"""
        return ord(notation[0]) - 97 + 10 * (int(notation[1:]) - 1)

    def flying_general(self):
        """
        Returns True if generals are facing each other on same file with no intervening pieces.
        Otherwise, False.
        """
        # If generals aren't on same file, no flying general
        start, end = tuple(sorted((self._general_location['RED'], self._general_location['BLACK'])))
        if (end - start) % 10:
            return False
        # If there is a piece in the way, no flying general
        for intervening in range(start + 10, end, 10):
            if self._board[intervening]:
                return False
        return True

    def general_is_attacked(self, color):
        """
        If the general of input color is being threatened by any pieces,
        returns an array of those pieces. Otherwise returns False.
        """
        # Opposite color of general
        enemy = 'BLACK' if color == 'RED' else 'RED'
        # array to hold coordinates from which general is being threatened
        attacks = []
        # for every enemy piece, check if it can attack general
        for coord in self._board:
            if self._board[coord] and self._board[coord].get_color() == enemy:
                if self._board[coord].get_type() in ['General', 'Advisor', "Elephant"]:
                    continue
                if self._board[coord].is_valid_move(coord, self._general_location[color], self._board):
                    print('general attacked by', coord)
                    attacks.append(coord)
        if self.flying_general():
            print('flying general')
            attacks.append(self._general_location[enemy])
        return attacks

    def generate_all_moves(self, color):
        all_moves = []
        legal_moves = []
        for coord in self._board:
            if self._board[coord] and self._board[coord].get_color() == color:
                all_moves.extend([(coord, move) for move in self._board[coord].pseudo_legal_moves(coord, self._board)])
        self.save_game()
        print(self._saved_board)
        for move in all_moves:
            self.update_board(move[0], move[1])
            if not self.general_is_attacked(color):
                legal_moves.append(move)
            self.restore_game()
        self.restore_game()


        return legal_moves

    def is_in_check(self, color):
        """
        Returns True if input color is in check
        """
        return self._in_check[color.upper()]

    def is_stalemated(self, color):
        return not self.is_in_check(color) and not self.generate_all_moves(color)

    def is_checkmated(self, color):
        """
        Returns true if input color is checkmated
        """
        return self.is_in_check(color) and not self.generate_all_moves(color)
        # self.save_game()
        # # First check if king can move to any adjacent palace squares without being in check. If so, not checkmate.
        # general_square = self._general_location[color]
        # general_moves = self._board[general_square].pseudo_legal_moves(general_square, self._board)
        # if general_moves:
        #     # Save locations of pieces
        #
        #     for move in general_moves:
        #         # Update board to reflect possible move
        #         self.update_board(general_square, move)
        #         # If general is still in check, check next move. If not, not checkmate.
        #         if self.general_is_attacked(color):
        #             self.restore_game()
        #             continue
        #         else:
        #             self.restore_game()
        #             return False
        #
        # # Next check if attacking piece can be captured.
        # if len(attacks) == 1:
        #     for piece in self._pieces[color]:
        #         if self._board[piece].is_valid_move(piece, attacks[0], self._board):
        #             self.update_board(piece, attacks[0])
        #             # If general is still in check, check next move. If not, not checkmate.
        #             if self.general_is_attacked(color):
        #                 self.restore_game()
        #                 continue
        #             return False
        #
        # # Next check if they can be blocked. Blocking will depend on piece type.
        # # Soldier has to be captured, no blocking.
        # pt = None
        # pt_moves = {}
        # attacks = [attack for attack in attacks if self._board[attack].get_type() != 'Soldier']
        # if attacks:
        #     # Starting with set of all possible blocking squares
        #     block_squares = set(self._board.keys())
        #     # Find intersection of blocking square sets for each attacking piece
        #     for attack in attacks:
        #         block_squares &= self._board[attack].blocking_squares(attack, general_square, self._board)
        #         if self._board[attack].get_type() == 'Cannon':
        #             pt = self._board[attack].get_pao_tai(attack, general_square, self._board)
        #             if pt:
        #                 attack_direction = self._board[attack].get_attack_direction()
        #                 pt_moves = self._board[pt].pseudo_legal_moves(pt, self._board)
        #                 # Need to generate all moves for pao tai that aren't in that direction
        #
        #     # If a piece can move to any of the squares left in the set, it blocks all attacks
        #     # Except if its a cannon and we need a second piece to jump, can't move current pao tai
        #     # because end result is still one pao tai. Need to move current pao tai out of attack vector
        #     # or any other piece into it.
        #     # Set of squares for most pieces, set of squares for pao tai.
        #     # Pao tai has to move off attack vector.
        #     for piece in self._pieces[color]:
        #         for square in block_squares:
        #             if self._board[piece].is_valid_move(piece, square, self._board):
        #                 # Update board to reflect possible move
        #                 self.update_board(piece, square)
        #                 # If general is still in check, check next move. If not, not checkmate.
        #                 if self.general_is_attacked(color):
        #                     self.restore_game()
        #                     continue
        #                 else:
        #                     self.restore_game()
        #                     return False
        #     if pt:
        #         block_squares |= pt_moves
        #         for square in block_squares:
        #             if self._board[pt].is_valid_move(pt, square, self._board):
        #                 # Update board to reflect possible move
        #                 self.update_board(pt, square)
        #                 # If general is still in check, check next move. If not, not checkmate.
        #                 if self.general_is_attacked(color):
        #                     self.restore_game()
        #                     continue
        #                 else:
        #                     self.restore_game()
        #                     return False
        # return True



    def make_move(self, start, end):
        """
        Checks if given move is legal.
        If not returns False.
        If it is, updates board and game state as necessary.
        """
        start = self.convert_algebraic(start)
        end = self.convert_algebraic(end)
        # If game is over, can't make move
        if self.get_game_state() != 'UNFINISHED':
            print('game over')
            return False
        # If there isn't a piece on start square can't move
        if not self._board[start]:
            print('no piece on that square')
            return False
        # If there is a piece on end square
        start_color = self._board[start].get_color()
        # If it isn't piece's color's turn, return False

        if start_color != self._turn:
            print('not your turn')
            return False
        if self._board[end]:
            # If the piece is the same color as the moving piece, can't capture it
            if self._board[end].get_color() == start_color:
                print('cant capture same color')

                return False
        # Otherwise we're good and just need to check that piece can legally move there
        if not self._board[start].is_valid_move(start, end, self._board):
            print('not valid move')
            return False
        # Save board. Update, then see if move puts player in check.
        self.save_game()
        self.update_board(start, end)
        # If move would put player in check, revert board state and return False
        if self.general_is_attacked(start_color):
            print('cant put yourself in check')
            self.restore_game()
            return False
        # If general isn't attacked, can clear check.
        self._in_check[start_color] = False
        # Check if move puts other player in check
        enemy_color = 'BLACK' if start_color == 'RED' else 'RED'
        # Places from which general is attacked
        attacks = self.general_is_attacked(enemy_color)
        # Place enemy color in check if attacks array isn't empty. Check for checkmate
        if attacks:
            print('CHECK!')
            self._in_check[enemy_color] = True
            if self.is_checkmated(enemy_color):
                print('CHECKMATE')
                self._game_state = start_color + '_WON'
        else:
            self._in_check[enemy_color] = False

        # Switch player turns
        self.change_turns()
        return True
