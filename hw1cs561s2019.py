import copy

WHITE_SPACE = 0
MY_EMITTER = 1
THEIR_EMITTER = 2
BLOCK = 3
MY_LASER = 4
THEIR_LASER = 5
BOTH_LASERS = 6
DIRECTIONS = [-1, 0, 1]


class Board(object):
    def __init__(self):
        self.board_size = 0
        self.num_elements = 0
        self.board = []
        self.element_count = 0
        self.my_score = 0
        self.their_score = 0
        self.actions_count = 0

        with open('input.txt', 'rU') as fp:
            row = -1
            for line in fp:
                line = line.rstrip('\n')
                if row < 0:
                    self.board_size = int(line)
                    self.num_elements = self.board_size * self.board_size
                else:
                    board_row = []
                    for char in line:
                        board_row.append(int(char))
                        if char == '0':
                            self.actions_count += 1

                    self.board.append(board_row)
                row += 1

        # Resolve Current Board
        for row in xrange(self.board_size):
            for col in xrange(self.board_size):
                if self.board[row][col] == MY_EMITTER:
                    self.my_score += self.plant_laser(row, col, MY_EMITTER)
                elif self.board[row][col] == THEIR_EMITTER:
                    self.their_score += self.plant_laser(row, col, THEIR_EMITTER)

    def pretty_print(self):
        print('Board {}x{} - {} vs {} - {} left'.format(self.board_size, self.board_size, self.my_score, self.their_score, self.actions_count))
        for board_row in self.board:
            row = ''
            for board_col in board_row:
                row += '{} '.format(board_col)
            print(row)

    def __iter__(self):
        return self

    # Iterates on all empty spaces only
    def next(self):
        if self.element_count == self.num_elements:
            self.element_count = 0
            raise StopIteration
        else:
            row = self.element_count // self.board_size
            col = self.element_count % self.board_size

            self.element_count += 1
            cell = self.board[row][col]
            if cell == WHITE_SPACE:
                return cell, row, col
            else:
                return self.next()

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
                    self.actions_count -= 1  # Remove one action for each white space the emitter's laser occupies
                elif cell != BLOCK:  # This condition is enough because a Laser can never hit another emitter
                    self.board[row][col] = BOTH_LASERS
                    marked_locations += 1
                else:
                    break
            else:
                break
        return marked_locations

    # Should be called on empty space only. This is done to avoid unnecessary == 0 check.
    # Return: Get Score
    def __plant_laser__(self, row, col, player_id):
        self.board[row][col] = player_id
        self.actions_count -= 1  # Remove one action because emitter is here

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
        applied_board = copy.deepcopy(self)
        applied_board.__plant_laser__(row, col, player_id)
        return applied_board

    def get_utility(self):
        return int(self.my_score > self.their_score)


class MiniMaxSolver:
    def __init__(self, initial_board):
        self.initial_state = initial_board
        self.lookup = dict()

    def solve(self, player_id):
        def get_max(current_state, turn):
            max_row = -1
            max_col = -1

            if current_state.actions_count == 0:
                return current_state.get_utility(), max_row, max_col

            utility_value = -1  # Because utility can only be 0 or 1
            next_turn = THEIR_EMITTER if turn == MY_EMITTER else MY_EMITTER
            for cell, row, col in current_state:
                updated_state = current_state.apply_action(row, col, turn)
                min_val, min_row, min_col = get_min(updated_state, next_turn)

                if min_val > utility_value:
                    utility_value = min_val
                    max_row = row
                    max_col = col

            return utility_value, max_row, max_col

        def get_min(current_state, turn):
            min_row = -1
            min_col = -1

            if current_state.actions_count == 0:
                return current_state.get_utility(), min_row, min_col

            utility_value = 2  # Because utility can only be 0 or 1
            next_turn = THEIR_EMITTER if turn == MY_EMITTER else MY_EMITTER
            for cell, row, col in current_state:
                updated_state = current_state.apply_action(row, col, turn)
                max_val, max_row, max_col = get_max(updated_state, next_turn)

                if max_val < utility_value:
                    utility_value = max_val
                    min_row = row
                    min_col = col

            return utility_value, min_row, min_col

        sol_utility, sol_row, sol_col = get_max(self.initial_state, player_id)

        return sol_row, sol_col


board = Board()
solver_1 = MiniMaxSolver(board)

board.pretty_print()

solution_row, solution_col = solver_1.solve(MY_EMITTER)
print('Applied {}, {}'.format(solution_row, solution_col))

action_applied = board.apply_action(solution_row, solution_col, MY_EMITTER)
action_applied.pretty_print()


# Second test
solver_2 = MiniMaxSolver(action_applied)
solution_row, solution_col = solver_2.solve(THEIR_EMITTER)

print('Applied {}, {}'.format(solution_row, solution_col))

action_applied = action_applied.apply_action(solution_row, solution_col, THEIR_EMITTER)
action_applied.pretty_print()


# Third test
solver_3 = MiniMaxSolver(action_applied)
solution_row, solution_col = solver_3.solve(MY_EMITTER)

print('Applied {}, {}'.format(solution_row, solution_col))

action_applied = action_applied.apply_action(solution_row, solution_col, MY_EMITTER)
action_applied.pretty_print()


# Fourth test
solver_4 = MiniMaxSolver(action_applied)
solution_row, solution_col = solver_4.solve(THEIR_EMITTER)

print('Applied {}, {}'.format(solution_row, solution_col))

action_applied = action_applied.apply_action(solution_row, solution_col, THEIR_EMITTER)
action_applied.pretty_print()