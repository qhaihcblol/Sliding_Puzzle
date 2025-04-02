# import các thư viện
from os import path
import random
import cv2
import numpy as np
from PySide6.QtCore import Qt, QObject, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from Controller.PuzzlePiece import PuzzlePiece
from collections import deque
from Model.AStar import AStarSolver
from Model.BFS import BFSSolver

class PuzzleGame(QObject):
    def __init__(self, image_path, grid_size=3, graphics_view=None):
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
        """Xáo trộn các mảnh ghép sao cho trạng thái luôn có thể giải được"""

        def is_solvable(puzzle, empty_row):
            """Kiểm tra xem trạng thái hiện tại có thể giải được không"""
            flat_puzzle = [num for row in puzzle for num in row if num != 0]
            inversions = sum(
                1
                for i in range(len(flat_puzzle))
                for j in range(i + 1, len(flat_puzzle))
                if flat_puzzle[i] > flat_puzzle[j]
            )

            if self.grid_size % 2 == 1:  # Lưới kích thước lẻ
                return inversions % 2 == 0
            else:  # Lưới kích thước chẵn
                return (inversions + empty_row) % 2 == 1

        while True:
            positions = list(self.puzzle_pieces.keys())
            random.shuffle(positions)

            new_pieces = {}
            for old_pos, new_pos in zip(self.puzzle_pieces.keys(), positions):
                new_pieces[new_pos] = self.puzzle_pieces[old_pos]

            self.puzzle_pieces = new_pieces

            # Lấy trạng thái hiện tại sau khi trộn
            state = self.getCurrentState()
            empty_row = (
                self.grid_size - self.empty_position[0]
            )  # Hàng ô trống tính từ dưới lên

            if is_solvable(state, empty_row):
                break  # Nếu trạng thái hợp lệ, thoát vòng lặp

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


    def getCurrentState(self):
        """Trả về trạng thái hiện tại của trò chơi dưới dạng ma trận"""
        state_matrix = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        for (row, col), piece in self.puzzle_pieces.items():
            state_matrix[row][col] = piece.piece_number

        # Xuất thông tin về pos, row, col và piece_number
        for (row, col), piece in self.puzzle_pieces.items():
            print(f"Pos: ({row}, {col}) - piece_number: {piece.piece_number}")

        return state_matrix

    def solvePuzzle(self, algorithm):
        """Giải quyết trò chơi bằng thuật toán AI"""
        current_state = self.getCurrentState()
        print(current_state)
        if algorithm == "BFS":
            print("BFS")
            solver = BFSSolver(self.grid_size)
            path = solver.solve(current_state)
            print(path)
        elif algorithm == "A* H1":
            print("A* H1")
            solver = AStarSolver(self.grid_size)
            path = solver.solve(current_state, heuristic="H1")
            print(path)
        else:
            print("Thuật toán không hợp lệ")
