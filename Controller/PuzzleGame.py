# import các thư viện
import random
import cv2
import numpy as np
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from Controller.PuzzlePiece import PuzzlePiece
from collections import deque

class PuzzleGame(QObject):
    def __init__(self, image_path, grid_size=5, graphics_view=None):
        super().__init__()
        self.image_path = image_path
        self.grid_size = grid_size
        self.puzzle_pieces = {}  # Lưu mảnh ghép theo vị trí (row, col)
        self.graphics_view = graphics_view
        self.scene = QGraphicsScene() if graphics_view else None
        self.empty_position = (grid_size - 1, grid_size - 1)  # Ô trống ban đầu
        self.loadAndSplitImage()
        if self.graphics_view:
            self.setupScene()

    def loadAndSplitImage(self):
        """Tải hình ảnh và chia nó thành các mảnh ghép"""
        img = self.loadImage()
        piece_width, piece_height = self.calculatePieceDimensions(img)

        self.splitImageIntoPieces(img, piece_width, piece_height)

    def loadImage(self):
        """Tải hình ảnh từ đường dẫn và chuẩn bị cho việc chia nhỏ"""
        img = cv2.imread(self.image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        view_width = self.graphics_view.width()
        view_height = self.graphics_view.height()

        img_h, img_w, _ = img.shape
        scale = min(view_width / img_w, view_height / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return img

    def calculatePieceDimensions(self, img):
        """Tính toán kích thước mảnh ghép dựa trên kích thước lưới"""
        img_h, img_w, _ = img.shape
        piece_width = img_w // self.grid_size
        piece_height = img_h // self.grid_size
        return piece_width, piece_height

    def splitImageIntoPieces(self, img, piece_width, piece_height):
        """Chia hình ảnh thành các mảnh ghép"""
        piece_number = 1  # Số thứ tự bắt đầu từ 1
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) == self.empty_position:
                    continue
                piece = img[
                    i * piece_height : (i + 1) * piece_height,
                    j * piece_width : (j + 1) * piece_width,
                ].copy()

                # Thêm khung viền và số thứ tự vào mảnh ghép
                self.addFrameAndTextToPiece(piece, piece_width, piece_height, i, j)

                # Chuyển đổi mảnh ghép thành QPixmap và lưu vào danh sách
                self.createAndStorePixmap(
                    piece, piece_width, piece_height, i, j, piece_number
                )

                # Tăng số thứ tự của mảnh ghép
                piece_number += 1

    def addFrameAndTextToPiece(self, piece, piece_width, piece_height, i, j):
        """Thêm viền và số thứ tự vào mảnh ghép"""
        cv2.rectangle(piece, (0, 0), (piece_width - 1, piece_height - 1), (0, 0, 0), 1)
        text = f"{i * self.grid_size + j + 1}"
        cv2.putText(
            piece,
            text,
            (piece_width // 3, piece_height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

    def createAndStorePixmap(
        self, piece, piece_width, piece_height, i, j, piece_number
    ):
        """Chuyển đổi mảnh ghép thành QPixmap và lưu vào danh sách"""
        bytes_per_line = piece_width * 3
        qimage = QImage(
            piece.data, piece_width, piece_height, bytes_per_line, QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage)

        # Tạo đối tượng PuzzlePiece và truyền số thứ tự vào đó
        puzzle_piece = PuzzlePiece(pixmap, i, j, self, piece_number)

        self.puzzle_pieces[(i, j)] = puzzle_piece

    def setupScene(self):
        """Tạo và hiển thị các mảnh ghép lên scene"""
        if not self.graphics_view:
            return

        self.graphics_view.setScene(self.scene)
        for (i, j), puzzle_piece in self.puzzle_pieces.items():
            item = PuzzlePiece(
                puzzle_piece.pixmap(), i, j, self, puzzle_piece.piece_number
            )
            item.setPos(
                j * puzzle_piece.pixmap().width(), i * puzzle_piece.pixmap().height()
            )
            self.scene.addItem(item)

    def tryMove(self, piece):
        """Kiểm tra và thực hiện di chuyển mảnh ghép nếu hợp lệ"""
        row, col = piece.row, piece.col
        empty_row, empty_col = self.empty_position

        if abs(row - empty_row) + abs(col - empty_col) == 1:
            self.puzzle_pieces[(empty_row, empty_col)] = self.puzzle_pieces.pop(
                (row, col)
            )
            piece.setPos(
                empty_col * piece.pixmap().width(), empty_row * piece.pixmap().height()
            )
            piece.row, piece.col = empty_row, empty_col
            self.empty_position = (row, col)
            return True
        return False

    def shufflePieces(self):
        """Xáo trộn các mảnh ghép"""
        positions = list(self.puzzle_pieces.keys())
        random.shuffle(positions)

        new_pieces = {}
        for old_pos, new_pos in zip(self.puzzle_pieces.keys(), positions):
            new_pieces[new_pos] = self.puzzle_pieces[old_pos]

        self.puzzle_pieces = new_pieces
        self.scene.clear()
        self.setupScene()

    def resetPieces(self):
        """Đặt lại các mảnh ghép về trạng thái ban đầu"""
        self.puzzle_pieces.clear()
        self.empty_position = (self.grid_size - 1, self.grid_size - 1)
        self.loadAndSplitImage()
        self.scene.clear()
        self.setupScene()

    def checkComplete(self):
        """Kiểm tra xem các mảnh ghép đã được sắp xếp đúng chưa."""
        for (row, col), piece in self.puzzle_pieces.items():
            # Vị trí mong đợi của mảnh ghép trong lưới
            expected_pos = row * self.grid_size + col + 1

            # Số thứ tự thực tế của mảnh ghép
            current_pos = piece.piece_number

            # Nếu số thứ tự không khớp với vị trí mong đợi, trò chơi chưa hoàn thành
            if expected_pos != current_pos:
                return False

        return True

    def solvePuzzle(self, algorithm):
        """Giải quyết trò chơi bằng thuật toán AI"""
        if algorithm == "BFS":
            print("BFS")
            path = self.solveWithBFS()
            print(path)
        elif algorithm == "A* H1":
            print("A* H1")
            path = self.solveWithAStar("H1")
        elif algorithm == "A* H2":
            print("A* H2")
            path = self.solveWithAStar("H2")
        elif algorithm == "A* H3":
            print("A* H3")
            path = self.solveWithAStar("H3")
        else:
            print("Thuật toán không hợp lệ")
        current_state = self.getCurrentState()
        print(current_state)
    def solveWithBFS(self):
        """Giải quyết trò chơi bằng thuật toán BFS"""

        # Trạng thái mục tiêu (giải quyết theo dạng ma trận 5x5)
        goal_state = [
            [
                (i * self.grid_size + j + 1) % (self.grid_size * self.grid_size)
                for j in range(self.grid_size)
            ]
            for i in range(self.grid_size)
        ]

        # Chuyển trạng thái hiện tại thành một tuple để dễ dàng so sánh
        start_state = tuple(tuple(row) for row in self.getCurrentState())

        # Kiểm tra nếu trạng thái ban đầu đã là trạng thái mục tiêu
        if start_state == tuple(tuple(row) for row in goal_state):
            print("Trò chơi đã hoàn thành!")
            return []

        # BFS: Khởi tạo hàng đợi, danh sách đã thăm và các phép di chuyển
        queue = deque(
            [(start_state, [])]
        )  # Lưu trạng thái hiện tại và chuỗi các mảnh ghép cần di chuyển
        visited = set()  # Để tránh thăm lại trạng thái đã kiểm tra

        visited.add(start_state)

        # Các phép di chuyển hợp lệ (lên, xuống, trái, phải)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Di chuyển theo chiều (row, col)

        while queue:
            current_state, path = queue.popleft()

            # Tìm vị trí của ô trống (0)
            empty_pos = next(
                (r, c)
                for r in range(self.grid_size)
                for c in range(self.grid_size)
                if current_state[r][c] == 0
            )
            empty_row, empty_col = empty_pos

            # Thực hiện các phép di chuyển từ ô trống
            for move in moves:
                new_row, new_col = empty_row + move[0], empty_col + move[1]

                if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                    # Di chuyển mảnh ghép và tạo ra trạng thái mới
                    new_state = list(
                        list(row) for row in current_state
                    )  # Sao chép trạng thái hiện tại
                    new_state[empty_row][empty_col], new_state[new_row][new_col] = (
                        new_state[new_row][new_col],
                        new_state[empty_row][empty_col],
                    )
                    new_state = tuple(
                        tuple(row) for row in new_state
                    )  # Chuyển thành tuple để so sánh

                    # Nếu chưa thăm trạng thái này, thêm vào hàng đợi
                    if new_state not in visited:
                        visited.add(new_state)
                        new_path = path + [
                            new_state[new_row][new_col]
                        ]  # Thêm mảnh ghép di chuyển vào đường đi

                        # Kiểm tra nếu đã đến trạng thái mục tiêu
                        if new_state == tuple(tuple(row) for row in goal_state):
                            print("Đã giải quyết trò chơi!")
                            return (
                                new_path  # Trả về danh sách các mảnh ghép cần di chuyển
                            )

                        queue.append((new_state, new_path))

        print("Không thể giải quyết trò chơi với BFS!")
        return []

    def solveWithAStar(self, heuristic):
        pass

    def getCurrentState(self):
        """Trả về trạng thái hiện tại của trò chơi dưới dạng ma trận 5x5"""
        state_matrix = [
            [0 for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]

        for (row, col), piece in self.puzzle_pieces.items():
            state_matrix[row][col] = piece.piece_number

        return state_matrix
