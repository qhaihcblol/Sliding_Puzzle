import cv2
import numpy as np
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt


class PuzzlePiece(QGraphicsPixmapItem):
    def __init__(self, pixmap, row, col, game, piece_number):
        super().__init__(pixmap)
        self.row = row
        self.col = col
        self.game = game
        self.piece_number = piece_number

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.game.tryMove(self)
