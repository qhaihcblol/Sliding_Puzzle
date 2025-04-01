# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGraphicsView,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QWidget)

class Ui_Main(object):
    def setupUi(self, Main):
        if not Main.objectName():
            Main.setObjectName(u"Main")
        Main.resize(890, 600)
        self.centralwidget = QWidget(Main)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 10, 321, 581))
        self.aiSolve_Btn = QPushButton(self.widget)
        self.aiSolve_Btn.setObjectName(u"aiSolve_Btn")
        self.aiSolve_Btn.setGeometry(QRect(190, 360, 91, 26))
        self.jumble_Btn = QPushButton(self.widget)
        self.jumble_Btn.setObjectName(u"jumble_Btn")
        self.jumble_Btn.setGeometry(QRect(40, 290, 91, 26))
        self.reset_Btn = QPushButton(self.widget)
        self.reset_Btn.setObjectName(u"reset_Btn")
        self.reset_Btn.setGeometry(QRect(190, 290, 91, 26))
        self.algorithm_Lb = QLabel(self.widget)
        self.algorithm_Lb.setObjectName(u"algorithm_Lb")
        self.algorithm_Lb.setGeometry(QRect(50, 430, 111, 21))
        self.algorithm_Cbb = QComboBox(self.widget)
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.addItem("")
        self.algorithm_Cbb.setObjectName(u"algorithm_Cbb")
        self.algorithm_Cbb.setGeometry(QRect(170, 430, 111, 31))
        self.step_Le = QLineEdit(self.widget)
        self.step_Le.setObjectName(u"step_Le")
        self.step_Le.setGeometry(QRect(170, 490, 111, 31))
        self.step_Le.setReadOnly(True)
        self.step_Lb = QLabel(self.widget)
        self.step_Lb.setObjectName(u"step_Lb")
        self.step_Lb.setGeometry(QRect(50, 490, 111, 21))
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 10, 241, 241))
        self.label.setStyleSheet(u"background-color: rgb(192, 191, 188);")
        self.Image = QLabel(self.widget)
        self.Image.setObjectName(u"Image")
        self.Image.setGeometry(QRect(50, 20, 221, 221))
        self.Image.setPixmap(QPixmap(u"Image/Picture.jpeg"))
        self.Image.setScaledContents(True)
        self.stop_Btn = QPushButton(self.widget)
        self.stop_Btn.setObjectName(u"stop_Btn")
        self.stop_Btn.setEnabled(True)
        self.stop_Btn.setGeometry(QRect(40, 360, 91, 26))
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setGeometry(QRect(350, 10, 531, 581))
        self.graphicsView = QGraphicsView(self.widget_2)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(40, 30, 450, 450))
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(330, 10, 20, 581))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        Main.setCentralWidget(self.centralwidget)

        self.retranslateUi(Main)

        QMetaObject.connectSlotsByName(Main)
    # setupUi

    def retranslateUi(self, Main):
        Main.setWindowTitle(QCoreApplication.translate("Main", u"Main", None))
        self.aiSolve_Btn.setText(QCoreApplication.translate("Main", u"AI Gi\u1ea3i", None))
        self.jumble_Btn.setText(QCoreApplication.translate("Main", u"Tr\u1ed9n \u1ea3nh", None))
        self.reset_Btn.setText(QCoreApplication.translate("Main", u"Reset", None))
        self.algorithm_Lb.setText(QCoreApplication.translate("Main", u"Thu\u1eadt to\u00e1n", None))
        self.algorithm_Cbb.setItemText(0, QCoreApplication.translate("Main", u"BFS", None))
        self.algorithm_Cbb.setItemText(1, QCoreApplication.translate("Main", u"A* H1", None))
        self.algorithm_Cbb.setItemText(2, QCoreApplication.translate("Main", u"A* H2", None))
        self.algorithm_Cbb.setItemText(3, QCoreApplication.translate("Main", u"A* H3", None))
        self.algorithm_Cbb.setItemText(4, QCoreApplication.translate("Main", u"A* H4", None))
        self.algorithm_Cbb.setItemText(5, QCoreApplication.translate("Main", u"A* H5", None))
        self.algorithm_Cbb.setItemText(6, QCoreApplication.translate("Main", u"A* H6", None))

        self.step_Le.setText(QCoreApplication.translate("Main", u"0", None))
        self.step_Lb.setText(QCoreApplication.translate("Main", u"B\u01b0\u1edbc", None))
        self.label.setText("")
        self.Image.setText("")
        self.stop_Btn.setText(QCoreApplication.translate("Main", u"D\u1eebng", None))
    # retranslateUi

