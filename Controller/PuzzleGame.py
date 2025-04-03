from math import e
import random
import cv2
import numpy as np
from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene
from Model.AStar import AStarSolver
from Model.BFS import BFSSolver
from Controller.PuzzlePiece import PuzzlePiece


class PuzzleGame(QObject):
    def __init__(
        self, image_path, grid_size=3, graphics_view=None, step_line_edit=None,stop_btn=None
    ):
        super().__init__()
        self.image_path = image_path
        self.grid_size = grid_size
        self.graphics_view = graphics_view
        self.step_line_edit = step_line_edit  # LineEdit để hiển thị số bước
        self.stop_btn = stop_btn
        self.scene = QGraphicsScene() if graphics_view else None

        # Các biến và mảng ban đầu
        self.state = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.empty_position = (grid_size - 1, grid_size - 1)
        self.pieces = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.all_pieces = {}
        self.target_state = [
            [
                i * grid_size + j + 1 if (i, j) != (grid_size - 1, grid_size - 1) else 0
                for j in range(grid_size)
            ]
            for i in range(grid_size)
        ]

        self.loadAndSplitImage()
        if self.graphics_view:
            self.setupScene()
        if self.stop_btn:
            self.stop_btn.setEnabled(False)

    def loadAndSplitImage(self):
        """Tải hình ảnh, chia nhỏ và tạo các PuzzlePiece với số thứ tự đúng."""
        img = cv2.imread(self.image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Tính kích thước hiển thị phù hợp nếu graphics_view có sẵn
        if self.graphics_view:
            view_width = self.graphics_view.width()
            view_height = self.graphics_view.height()
            img_h, img_w, _ = img.shape
            scale = min(view_width / img_w, view_height / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            new_h, new_w = img.shape[:2]

        piece_width = new_w // self.grid_size
        piece_height = new_h // self.grid_size

        # Khởi tạo trạng thái ban đầu: tạo PuzzlePiece cho mỗi ô ngoại trừ ô trống.
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) == self.empty_position:
                    self.state[i][j] = 0
                    self.pieces[i][j] = None
                    continue

                # Cắt mảnh ảnh tương ứng.
                piece_img = img[
                    i * piece_height : (i + 1) * piece_height,
                    j * piece_width : (j + 1) * piece_width,
                ].copy()
                # Thêm khung và số thứ tự (theo thứ tự mục tiêu)
                piece_number = i * self.grid_size + j + 1
                self.addFrameAndText(piece_img, piece_width, piece_height, piece_number)

                # Chuyển đổi sang QPixmap.
                bytes_per_line = piece_width * 3
                qimage = QImage(
                    piece_img.data,
                    piece_width,
                    piece_height,
                    bytes_per_line,
                    QImage.Format_RGB888,
                )
                pixmap = QPixmap.fromImage(qimage)

                # Tạo PuzzlePiece với thông tin ban đầu.
                piece = PuzzlePiece(pixmap, i, j, self, piece_number)
                self.pieces[i][j] = piece
                self.state[i][j] = piece_number
                # Lưu lại PuzzlePiece vào all_pieces
                self.all_pieces[piece_number] = piece

    def addFrameAndText(self, img_piece, piece_width, piece_height, piece_number):
        """Thêm khung viền và số thứ tự vào mảnh ghép."""
        cv2.rectangle(
            img_piece, (0, 0), (piece_width - 1, piece_height - 1), (0, 0, 0), 1
        )
        text = str(piece_number)
        cv2.putText(
            img_piece,
            text,
            (piece_width // 3, piece_height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

    def setupScene(self):
        """Cập nhật lại QGraphicsScene mà không xóa (delete) các đối tượng đã tạo."""
        if not self.graphics_view:
            return

        # Thay vì gọi clear() (sẽ delete các PuzzlePiece), ta sẽ remove các item khỏi scene
        for item in self.scene.items():
            self.scene.removeItem(item)

        self.graphics_view.setScene(self.scene)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                piece = self.pieces[i][j]
                if piece is None:
                    continue
                # Cập nhật vị trí hiển thị theo vị trí mới
                piece.setPos(j * piece.pixmap().width(), i * piece.pixmap().height())
                self.scene.addItem(piece)

    def tryMove(self, piece):
        """Thử di chuyển một mảnh ghép nếu nó kề với ô trống."""
        r, c = piece.row, piece.col
        empty_r, empty_c = self.empty_position
        if abs(r - empty_r) + abs(c - empty_c) == 1:
            # Hoán đổi vị trí trong mảng pieces và state.
            self.pieces[empty_r][empty_c] = piece
            self.state[empty_r][empty_c] = piece.piece_number

            self.pieces[r][c] = None
            self.state[r][c] = 0

            # Cập nhật vị trí của PuzzlePiece và ô trống.
            piece.row, piece.col = empty_r, empty_c
            self.empty_position = (r, c)

            # Cập nhật lại vị trí hiển thị.
            piece.setPos(
                empty_c * piece.pixmap().width(), empty_r * piece.pixmap().height()
            )
            return True
        return False

    def shufflePieces(self):
        """Xáo trộn các mảnh ghép sao cho trạng thái luôn có thể giải được."""

        def is_solvable(flat_list):
            inversions = 0
            for i in range(len(flat_list)):
                for j in range(i + 1, len(flat_list)):
                    if (
                        flat_list[i] > flat_list[j]
                        and flat_list[i] != 0
                        and flat_list[j] != 0
                    ):
                        inversions += 1
            if self.grid_size % 2 == 1:
                return inversions % 2 == 0
            else:
                # Tính vị trí của ô trống tính từ dưới lên
                empty_row_from_bottom = self.grid_size - self.empty_position[0]
                return (inversions + empty_row_from_bottom) % 2 == 0

        # Tạo danh sách các số (0 là ô trống)
        flat = [
            self.state[i][j]
            for i in range(self.grid_size)
            for j in range(self.grid_size)
        ]
        while True:
            random.shuffle(flat)
            # Chuyển đổi thành ma trận mới và tìm vị trí ô trống.
            new_state = []
            for i in range(self.grid_size):
                row = flat[i * self.grid_size : (i + 1) * self.grid_size]
                new_state.append(row)
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if new_state[i][j] == 0:
                        new_empty = (i, j)
                        break

            self.empty_position = new_empty
            if is_solvable(flat):
                break

        # Cập nhật lại state và tạo lại mảng pieces dựa trên new_state.
        self.state = new_state
        new_pieces = [
            [None for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                num = self.state[i][j]
                if num == 0:
                    new_pieces[i][j] = None
                else:
                    # Lấy PuzzlePiece từ all_pieces thay vì từ mảng pieces hiện tại.
                    piece = self.all_pieces.get(num)
                    new_pieces[i][j] = piece
                    # Cập nhật vị trí mới cho PuzzlePiece.
                    piece.row, piece.col = i, j
        self.pieces = new_pieces
        if self.graphics_view:
            self.setupScene()

    def resetPieces(self):
        """Đặt lại các mảnh ghép về trạng thái ban đầu."""
        # Dùng target_state và all_pieces để khôi phục lại toàn bộ trạng thái
        self.state = [row[:] for row in self.target_state]
        self.empty_position = (self.grid_size - 1, self.grid_size - 1)
        new_pieces = [
            [None for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) == self.empty_position:
                    new_pieces[i][j] = None
                else:
                    # Lấy lại PuzzlePiece từ all_pieces
                    piece = self.all_pieces.get(self.target_state[i][j])
                    piece.row, piece.col = i, j
                    new_pieces[i][j] = piece
        self.pieces = new_pieces
        if self.graphics_view:
            self.setupScene()

    def checkComplete(self):
        """Kiểm tra xem trạng thái hiện tại có khớp với trạng thái mục tiêu không."""
        return self.state == self.target_state

    def solvePuzzle(self, algorithm):
        """Giải quyết trò chơi bằng thuật toán AI."""
        current_state = self.state
        print("Trạng thái ban đầu:", current_state)

        if algorithm == "BFS":
            solver = BFSSolver(self.grid_size)
            path = solver.solve(current_state)
            print("Path tìm được bằng BFS:", path)
        elif algorithm == "A* H1":
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H1")
            print("Path tìm được bằng A* H1:", path)
        elif algorithm == "A* H2":
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H2")
            print("Path tìm được bằng A* H2:", path)
        elif algorithm == "A* H3":
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H3")
            print("Path tìm được bằng A* H3:", path)
        elif algorithm == "A* H4":
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H4")
            print("Path tìm được bằng A* H4:", path)
        elif algorithm == "A* H5":
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H5")
            print("Path tìm được bằng A* H5:", path)
        elif algorithm == "A* H6":
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H6")
            print("Path tìm được bằng A* H6:", path)
        else:
            print("Thuật toán không hợp lệ")
            return

        self.animateSolution(path)

    def animateSolution(self, path):
        if not path:
            return

        self.move_steps = path.copy()
        self.current_step = 0
        if self.step_line_edit:
            self.step_line_edit.setText(str(self.current_step))

        # Khi bắt đầu giải, kích hoạt nút stop
        if self.stop_btn:
            self.stop_btn.setEnabled(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.performNextMove)
        self.timer.start(300)

    def performNextMove(self):
        if not self.move_steps:
            # Animation kết thúc -> dừng timer và vô hiệu hóa nút stop
            self.timer.stop()
            if self.stop_btn:
                self.stop_btn.setEnabled(False)
            return

        row, col = self.move_steps.pop(0)
        piece = self.pieces[row][col]
        if piece:
            self.tryMove(piece)
        else:
            print(f"Không tìm thấy mảnh tại vị trí ({row}, {col})")

        self.current_step += 1
        if self.step_line_edit:
            self.step_line_edit.setText(str(self.current_step))
        if self.graphics_view:
            self.graphics_view.viewport().update()

    def stopAnimation(self):
        """Phương thức dừng animation khi nhấn nút stop."""
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()
        if self.stop_btn:
            self.stop_btn.setEnabled(False)
