WHITE_SPACE = 0
MY_EMITTER = 1
THEIR_EMITTER = 2
BLOCK = 3
MY_LASER = 4
THEIR_LASER = 5
BOTH_LASERS = 6
DIRECTIONS = [-1, 0, 1]


class Board:
    def __init__(self):
        self.board_size = 0
        self.num_elements = 0
        self.board = []
        self.element_count = 0
        self.my_score = 0
        self.their_score = 0

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
        print('Board {}x{} - {} vs {}'.format(self.board_size, self.board_size, self.my_score, self.their_score))
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
                return cell
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
    def plant_laser(self, row, col, player_id):
        self.board[row][col] = player_id
        mark_id = MY_LASER if player_id == MY_EMITTER else THEIR_LASER
        score = 1

        for x in DIRECTIONS:
            for y in DIRECTIONS:
                if x != 0 or y != 0:
                    score += self.__mark_along_axis__(row, col, x, y, mark_id)

        return score


board = Board()
board.pretty_print()
