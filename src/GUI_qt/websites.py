import os
from PyQt6.QtGui import QIcon
from GUI_qt.load_providers import base_path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLineEdit
import webbrowser

current_dir = os.path.join(base_path(), 'GUI_qt')
assets = os.path.join(current_dir, 'assets')

class WebSiteOpener(QWidget):
    def __init__(self, websites):
        super().__init__()
        
        layout = QVBoxLayout()

        self.listWidget = QListWidget()
        self.itens = []
        self.websites = websites
        for website in websites:
            if website.name not in self.itens:
                self.itens.append(website.name)
        self.listWidget.addItems(self.itens)
        
        layout.addWidget(self.listWidget)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Buscar site...")
        self.search_bar.textChanged.connect(self.filter_sites)
        layout.addWidget(self.search_bar)

        self.listWidget.itemClicked.connect(self.openSite)

        self.setLayout(layout)
        self.setWindowTitle('Lista de Sites Suportados')
        self.resize(300, 200)
        self.setWindowIcon(QIcon(os.path.join(assets, 'icon.ico')))
    
    def filter_sites(self):
        text = self.search_bar.text().lower()
        self.listWidget.clear()
        if text != '':
            filtered_sites = [website.name for website in self.websites if text in website.name.lower()]
            self.listWidget.addItems(filtered_sites)
        else:
            self.listWidget.addItems(self.itens)

    def openSite(self, item):
        for website in self.websites:
            if website.name == item.text():
                webbrowser.open(website.domain)