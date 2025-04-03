from collections import deque


class BFSSolver:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.goal_state = [
            [
                (
                    i * self.grid_size + j + 1
                    if i * self.grid_size + j + 1 < self.grid_size * self.grid_size
                    else 0
                )
                for j in range(self.grid_size)
            ]
            for i in range(self.grid_size)
        ]

    def get_empty_pos(self, state):
        """Tìm vị trí ô trống (0) trong trạng thái"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if state[r][c] == 0:
                    return (r, c)
        return None

    def get_piece_position(self, piece_value, state):
        """Trả về vị trí (row, col) của mảnh có giá trị 'piece_value' trong trạng thái"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if state[r][c] == piece_value:
                    return (r, c)
        return None

    def solve(self, start_state):
        """Giải quyết trò chơi bằng BFS, trả về danh sách vị trí mảnh cần sắp xếp"""
        start_state = tuple(tuple(row) for row in start_state)
        goal_state_tuple = tuple(tuple(row) for row in self.goal_state)
        if start_state == goal_state_tuple:
            print("Trò chơi đã hoàn thành!")
            return []

        queue = deque([(start_state, [])])
        visited = set()
        visited.add(start_state)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            current_state, path = queue.popleft()
            empty_row, empty_col = self.get_empty_pos(current_state)

            for move in moves:
                new_row, new_col = empty_row + move[0], empty_col + move[1]
                if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                    new_state = [list(row) for row in current_state]
                    moved_value = new_state[new_row][
                        new_col
                    ]  # Lưu giá trị mảnh di chuyển
                    new_state[empty_row][empty_col], new_state[new_row][new_col] = (
                        new_state[new_row][new_col],
                        new_state[empty_row][empty_col],
                    )
                    new_state = tuple(tuple(row) for row in new_state)

                    if new_state not in visited:
                        visited.add(new_state)
                        new_path = path + [
                            self.get_piece_position(moved_value, current_state)
                        ]
                        if new_state == goal_state_tuple:
                            print("Đã giải quyết trò chơi!")
                            return new_path
                        queue.append((new_state, new_path))

        print("Không thể giải quyết trò chơi với BFS!")
        return []
