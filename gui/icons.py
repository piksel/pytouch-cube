from PyQt6.QtGui import QIcon, QColor, QImage, QPainterPath, QPainter, QPixmap
from PyQt6.QtCore import QPointF, Qt


def get_error_icon() -> QIcon:
    img = QImage(32, 32, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.white)
    with QPainter(img) as p:
        pen = p.pen()
        pen.setColor(QColor(0, 0, 0))
        p.setPen(pen)

        mn, md, mx = 1, 15.5, 30
        triangle = QPainterPath(QPointF(mn, mx))
        triangle.lineTo(QPointF(md, mn))
        triangle.lineTo(QPointF(mx, mx))
        triangle.lineTo(QPointF(mn, mx))

        p.fillPath(triangle, QColor(255, 197, 74))
        p.drawPath(triangle)

        font = p.font()
        font.setPixelSize(26)
        p.setFont(font)

        p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, '!')

        return QIcon(QPixmap.fromImage(img))

def get_generic_icon(letter: str, valid: bool = True) -> QIcon:
    img = QImage(32, 32, QImage.Format.Format_ARGB32)
    img.fill(QColor(200, 200, 200))
    with QPainter(img) as p:
        pen = p.pen()
        pen.setColor(QColor(0, 0, 0) if valid else QColor(255, 0, 0))
        p.setPen(pen)

        p.drawRect(1, 1, 30, 30)

        font = p.font()
        font.setPixelSize(32)
        p.setFont(font)

        p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, letter[0])

    return QIcon(QPixmap.fromImage(img))

def get_bluetooth_icon() -> QIcon:
    img = QImage(32, 32, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.white)
    with QPainter(img) as p:
        pen = p.pen()
        pen.setColor(QColor(0, 0, 0))
        p.setPen(pen)

        mn, md, mx = 1, 15.5, 30
        mt1 = 7
        mt2 = 23
        triangle = QPainterPath(QPointF(md, mn))
        triangle.lineTo(QPointF(mx, mt1))
        triangle.lineTo(QPointF(md, md))
        triangle.lineTo(QPointF(mx, mt2))
        triangle.lineTo(QPointF(md, mx))
        triangle.lineTo(QPointF(md, mn))

        # p.fillPath(triangle, QColor(255, 197, 74))
        p.drawPath(triangle)

        font = p.font()
        font.setPixelSize(26)
        p.setFont(font)

        #p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, '!')

        return QIcon(QPixmap.fromImage(img))