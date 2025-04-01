from itertools import chain
import sys
from tkinter import Image
import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QGraphicsScene,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap, QImage
from View.Form import Ui_Main
from Controller.PuzzleGame import PuzzleGame


class Form(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.puzzle_game = PuzzleGame(
            "Image/Picture.jpeg", graphics_view=self.graphicsView
        )
        self.setupSignal()

    def setupSignal(self):
        self.jumble_Btn.clicked.connect(self.puzzle_game.shufflePieces)
        self.reset_Btn.clicked.connect(self.puzzle_game.resetPieces)
        self.aiSolve_Btn.clicked.connect(self.solvePuzzle)

    def solvePuzzle(self):
        selected_algorithm = self.algorithm_Cbb.currentText()
        self.puzzle_game.solvePuzzle(selected_algorithm)
