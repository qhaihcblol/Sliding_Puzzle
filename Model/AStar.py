import heapq


class AStarSolver:
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
        self.goal_positions = {}
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                value = self.goal_state[r][c]
                if value != 0:
                    self.goal_positions[value] = (r, c)

    def get_empty_pos(self, state):
        """Tìm vị trí ô trống (0) trong trạng thái"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if state[r][c] == 0:
                    return (r, c)
        return None

    def h1(self, state):
        """Heuristic 1: Số ô không đúng vị trí"""
        total = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if state[r][c] != self.goal_state[r][c]:
                    total += 1
        return total

    def h2(self, state):
        """Heuristic 2: Tổng khoảng cách Manhattan"""
        total = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                value = state[r][c]
                if value != 0:
                    target_r, target_c = self.goal_positions[value]
                    total += abs(r - target_r) + abs(c - target_c)
        return total

    def h3(self, state):
        """Heuristic 3: Manhattan + Linear Conflict"""
        manhattan = self.h2(state)
        conflicts = 0
        for r in range(self.grid_size):
            row = state[r]
            for i in range(self.grid_size - 1):
                for j in range(i + 1, self.grid_size):
                    val1, val2 = row[i], row[j]
                    if val1 != 0 and val2 != 0:
                        target_r1, target_c1 = self.goal_positions[val1]
                        target_r2, target_c2 = self.goal_positions[val2]
                        if target_r1 == target_r2 == r and target_c1 > target_c2:
                            conflicts += 2
        for c in range(self.grid_size):
            col = [state[r][c] for r in range(self.grid_size)]
            for i in range(self.grid_size - 1):
                for j in range(i + 1, self.grid_size):
                    val1, val2 = col[i], col[j]
                    if val1 != 0 and val2 != 0:
                        target_r1, target_c1 = self.goal_positions[val1]
                        target_r2, target_c2 = self.goal_positions[val2]
                        if target_c1 == target_c2 == c and target_r1 > target_r2:
                            conflicts += 2
        return manhattan + conflicts

    def h4(self, state):
        """Heuristic 4: Corner Tiles Heuristic"""
        total = 0
        # Kiểm tra 4 ô góc
        corners = [
            (0, 0),
            (0, self.grid_size - 1),
            (self.grid_size - 1, 0),
            (self.grid_size - 1, self.grid_size - 1),
        ]
        for r, c in corners:
            value = state[r][c]
            goal_value = self.goal_state[r][c]
            if value != 0 and value != goal_value:
                # Nếu ô góc sai, tính khoảng cách Manhattan
                target_r, target_c = self.goal_positions[value]
                total += abs(r - target_r) + abs(c - target_c)
                # Thêm chi phí nếu ô góc không đúng thứ tự
                if (
                    (r == 0 and c == 0 and value > 1)
                    or (r == 0 and c == self.grid_size - 1 and value > self.grid_size)
                    or (
                        r == self.grid_size - 1
                        and c == 0
                        and value > self.grid_size * (self.grid_size - 1) + 1
                    )
                    or (
                        r == self.grid_size - 1
                        and c == self.grid_size - 1
                        and value != 0
                    )
                ):
                    total += 2  # Phạt thêm vì sai vị trí quan trọng
        return total

    def h5(self, state):
        """Heuristic 5: Walking Distance"""
        total = 0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                value = state[r][c]
                if value != 0:
                    target_r, target_c = self.goal_positions[value]
                    total += max(abs(r - target_r), abs(c - target_c))
        return total

    def h6(self, state):
        """Heuristic 6: Sequence Score"""
        total = 0
        # Kiểm tra thứ tự liên tiếp trong hàng và cột
        for r in range(self.grid_size):
            row = state[r]
            for c in range(self.grid_size - 1):
                val1, val2 = row[c], row[c + 1]
                if val1 != 0 and val2 != 0:
                    target_r1, target_c1 = self.goal_positions[val1]
                    target_r2, target_c2 = self.goal_positions[val2]
                    # Nếu không liên tiếp trong hàng mục tiêu
                    if (
                        target_r1 == target_r2
                        and abs(target_c1 - target_c2) == 1
                        and val1 > val2
                    ):
                        total += 2

        for c in range(self.grid_size):
            col = [state[r][c] for r in range(self.grid_size)]
            for r in range(self.grid_size - 1):
                val1, val2 = col[r], col[r + 1]
                if val1 != 0 and val2 != 0:
                    target_r1, target_c1 = self.goal_positions[val1]
                    target_r2, target_c2 = self.goal_positions[val2]
                    # Nếu không liên tiếp trong cột mục tiêu
                    if (
                        target_c1 == target_c2
                        and abs(target_r1 - target_r2) == 1
                        and val1 > val2
                    ):
                        total += 2
        return total + self.h1(state)  # Kết hợp với H1 để tăng độ chính xác


    def solve(self, start_state, heuristic="H2"):
        """Giải quyết trò chơi bằng thuật toán A* với heuristic được chọn"""
        start_state = tuple(tuple(row) for row in start_state)
        goal_state_tuple = tuple(tuple(row) for row in self.goal_state)
        if start_state == goal_state_tuple:
            print("Trò chơi đã hoàn thành!")
            return []

        heuristic_func = {
            "H1": self.h1,
            "H2": self.h2,
            "H3": self.h3,
            "H4": self.h4,
            "H5": self.h5,
            "H6": self.h6,
        }.get(heuristic, self.h2)

        open_set = [(heuristic_func(start_state), 0, start_state, [])]
        visited = set()
        g_scores = {start_state: 0}
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while open_set:
            f_score, g_score, current_state, path = heapq.heappop(open_set)
            if current_state in visited:
                continue
            visited.add(current_state)

            if current_state == goal_state_tuple:
                print(f"Đã giải quyết trò chơi bằng A* với {heuristic}!")
                return path

            empty_row, empty_col = self.get_empty_pos(current_state)
            for move in moves:
                new_row, new_col = empty_row + move[0], empty_col + move[1]
                if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                    new_state = [list(row) for row in current_state]
                    moved_value = new_state[new_row][new_col]
                    new_state[empty_row][empty_col], new_state[new_row][new_col] = (
                        new_state[new_row][new_col],
                        new_state[empty_row][empty_col],
                    )
                    new_state = tuple(tuple(row) for row in new_state)

                    if new_state not in visited:
                        g_new = g_score + 1
                        h_new = heuristic_func(new_state)
                        f_new = g_new + h_new

                        if new_state not in g_scores or g_new < g_scores[new_state]:
                            g_scores[new_state] = g_new
                            new_path = path + [
                                (new_row, new_col)
                            ]  # Lưu vị trí của mảnh ghép
                            heapq.heappush(open_set, (f_new, g_new, new_state, new_path))

        print(f"Không thể giải quyết trò chơi với A* ({heuristic})!")
        return []
