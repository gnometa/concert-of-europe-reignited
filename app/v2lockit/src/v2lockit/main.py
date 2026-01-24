"""
V2LocKit Main Entry Point
=========================

Launches the V2LocKit GUI application.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from v2lockit.ui.main_window import MainWindow


def apply_dark_theme(app: QApplication):
    """Apply a dark theme to the application."""
    app.setStyle("Fusion")
    
    palette = QPalette()
    
    # Base colors
    dark = QColor(30, 30, 30)
    darker = QColor(20, 20, 20)
    lighter = QColor(50, 50, 50)
    text = QColor(220, 220, 220)
    highlight = QColor(42, 130, 218)
    disabled = QColor(127, 127, 127)
    
    palette.setColor(QPalette.ColorRole.Window, dark)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, darker)
    palette.setColor(QPalette.ColorRole.AlternateBase, dark)
    palette.setColor(QPalette.ColorRole.ToolTipBase, dark)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, lighter)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, highlight)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled)
    
    app.setPalette(palette)


def main():
    """Main entry point for V2LocKit."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("V2LocKit")
    app.setOrganizationName("CoE-RoI-R")
    app.setApplicationVersion("0.1.0")
    
    # Apply dark theme
    apply_dark_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
