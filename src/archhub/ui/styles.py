SEPARATOR_LINE_STYLE = "background-color: palette(midlight);"
SQUARE_LABEL_STYLE = """
QFrame.QSquareLabel { 
    margin: 8px 4px;
    padding: 8px;
    background-color: palette(window);
    border: 1px solid palette(midlight);
    border-radius: 8px; 
}
"""
PAGE_BUTTON_STYLE = """
QPushButton.QPageButton { 
    font-size: 18px;
    text-align: left;
    margin: 4px;
    padding: 8px;
    border: 1px solid transparent;
    border-radius: 8px;
}
QPushButton.QPageButton:pressed, QPushButton.QPageButton:checked {
    border: 1px solid palette(midlight); 
    border-radius: 8px;
    background-color: palette(midlight);
}
"""
SUB_PAGE_BUTTON_STYLE = """
QPushButton.QSubPageButton { 
    font-size: 14px;
    text-align: left;
    margin: 2px;
    margin-left: 16px;
    padding: 4px;
    border: 1px solid transparent;
    border-radius: 8px;
}
QPushButton.QSubPageButton:pressed, QPushButton.QSubPageButton:checked {
    border: 1px solid palette(midlight);
    border-radius: 8px;
    background-color: palette(midlight);
}
"""