WHITE_SPACE = 0
MY_EMITTER = 1
THEIR_EMITTER = 2
BLOCK = 3
MY_LASER = 4
THEIR_LASER = 5
BOTH_LASERS = 6
DIRECTIONS = [-1, 0, 1]


class Board(object):
    def __init__(self, old_board=None):
        self.board_size = 0
        self.board = []
        self.action_set = set()
        self.my_score = 0
        self.their_score = 0

        if old_board is None:
            self.read_board()
        else:
            self.board_size = old_board.board_size
            self.board = [board_row[:] for board_row in old_board.board]
            self.action_set = set(old_board.action_set)
            self.my_score = old_board.my_score
            self.their_score = old_board.their_score

    def read_board(self):
        with open('input.txt', 'r') as fp:
            for row_idx, line in enumerate(fp):
                line = line.rstrip('\r\n')
                if row_idx == 0:
                    self.board_size = int(line)
                else:
                    board_row = []
                    for col_idx, char in enumerate(line):
                        board_row.append(int(char))
                        if char == '0':
                            self.action_set.add((row_idx-1, col_idx))

                    self.board.append(board_row)

        # Resolve Current Board
        for row in xrange(self.board_size):
            for col in xrange(self.board_size):
                if self.board[row][col] == MY_EMITTER:
                    self.__plant_laser__(row, col, MY_EMITTER)
                elif self.board[row][col] == THEIR_EMITTER:
                    self.__plant_laser__(row, col, THEIR_EMITTER)

    def pretty_print(self):
        print('Board {}x{} - {} vs {} - {} left'.format(self.board_size, self.board_size, self.my_score, self.their_score, len(self.action_set)))
        for board_row in self.board:
            row = ''
            for board_col in board_row:
                row += '{} '.format(board_col)
            print(row)

    def __mark_along_axis__(self, row, col, x, y, mark_id):
        marked_locations = 0
        for step in xrange(3):  # Always take three steps from emitter location
            row += x
            col += y
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                cell = self.board[row][col]
                if cell == WHITE_SPACE:
                    self.board[row][col] = mark_id
                    marked_locations += 1
                    # Remove one action for each white space the emitter's laser occupies
                    self.action_set.remove((row, col))
                elif cell != BLOCK and cell != mark_id:
                    # This condition is enough because a Laser can never hit another emitter
                    # We need to check if the cell is not mark_id because you don't want to double tag a laser count
                    self.board[row][col] = BOTH_LASERS
                    marked_locations += 1
                elif cell == BLOCK:
                    break
            else:
                break
        return marked_locations

    # Should be called on empty space only. This is done to avoid unnecessary == 0 check.
    # Return: Get Score
    def __plant_laser__(self, row, col, player_id):
        self.board[row][col] = player_id
        if (row, col) in self.action_set:
            self.action_set.remove((row, col))

        mark_id = MY_LASER if player_id == MY_EMITTER else THEIR_LASER
        score = 1

        for x in DIRECTIONS:
            for y in DIRECTIONS:
                if x != 0 or y != 0:
                    score += self.__mark_along_axis__(row, col, x, y, mark_id)

        # Keep Tracking of whites
        if player_id == MY_EMITTER:
            self.my_score += score
        else:
            self.their_score += score

    # Out-of-place action application
    def apply_action(self, row, col, player_id):
        applied_board = Board(self)
        applied_board.__plant_laser__(row, col, player_id)
        return applied_board

    def get_utility(self, for_player):
        if for_player == MY_EMITTER:
            return int(self.my_score > self.their_score)
        else:
            return int(self.their_score > self.my_score)


class MiniMaxSolver:
    def __init__(self, initial_board, player_id):
        self.initial_state = initial_board
        self.player_id = player_id

    def solve(self, debug=False):
        def get_max(current_state, turn, alpha, beta, level):
            lvl_str = '--' * level

            if len(current_state.action_set) == 0:
                if debug:
                    print(lvl_str + 'MaxTerminal@{} with {} Utility'.format(level, current_state.get_utility(self.player_id)))
                return current_state.get_utility(self.player_id), None

            utility_value = -float('inf')  # Because utility can only be 0 or 1
            next_turn = THEIR_EMITTER if turn == MY_EMITTER else MY_EMITTER
            good_move = None

            for row, col in current_state.action_set:
                updated_state = current_state.apply_action(row, col, turn)
                if debug:
                    print(lvl_str + 'Max@{}-({}, {}) => {}vs{}'.format(level, row, col, updated_state.my_score, updated_state.their_score))

                min_val, _ = get_min(updated_state, next_turn, alpha, beta, level + 1)
                if min_val > utility_value:
                    utility_value = min_val
                    good_move = (row, col)
                    if debug:
                        print(lvl_str + 'UpdatedMax@{} -> {}'.format(level, utility_value))

                alpha = max(utility_value, alpha)
                if beta <= alpha:
                    break

            return utility_value, good_move

        def get_min(current_state, turn, alpha, beta, level):
            lvl_str = '--' * level

            if len(current_state.action_set) == 0:
                if debug:
                    print(lvl_str + 'MinTerminal@{} with {} Utility'.format(level, current_state.get_utility(self.player_id)))
                return current_state.get_utility(self.player_id), None

            utility_value = float('inf')  # Because utility can only be 0 or 1
            next_turn = THEIR_EMITTER if turn == MY_EMITTER else MY_EMITTER
            good_move = None

            for row, col in current_state.action_set:
                updated_state = current_state.apply_action(row, col, turn)
                if debug:
                    print(lvl_str + 'Min@{}-({}, {}) => {}vs{}'.format(level, row, col, updated_state.my_score, updated_state.their_score))

                max_val, _ = get_max(updated_state, next_turn, alpha, beta, level + 1)
                if max_val < utility_value:
                    utility_value = max_val
                    good_move = (row, col)
                    if debug:
                        print(lvl_str + 'UpdatedMin@{} -> {}'.format(level, utility_value))

                beta = min(utility_value, beta)
                if beta <= alpha:
                    break

            return utility_value, good_move

        sol_utility, sol = get_max(self.initial_state, self.player_id, -float('inf'), float('inf'), 0)

        return sol[0], sol[1]


board = Board()
board.read_board()
#board.pretty_print()

cur_player = MY_EMITTER
#cur_player = THEIR_EMITTER
solver = MiniMaxSolver(board, cur_player)
solution_row, solution_col = solver.solve(debug=False)

output_fp = open('output.txt', 'w')
output_fp.write('{} {}'.format(solution_row, solution_col))
