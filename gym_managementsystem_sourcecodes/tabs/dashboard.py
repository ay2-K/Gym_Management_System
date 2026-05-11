from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        lbl_title = QLabel("Overview")
        lbl_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #333; margin-bottom: 10px;")
        self.layout.addWidget(lbl_title)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(20)
        self.layout.addLayout(self.cards_grid)
        
        self.layout.addStretch()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        stats = self.db.get_dashboard_stats()
        member_detail_text = f"Active: {stats['active_members']}   |   Passive: {stats['passive_members']}"

        cards_data = [
            ("Total Revenue", f"{stats['revenue']:,.2f} $", "#00838F", "💰", None),
            ("Total Members", str(stats['total_members']), "#2E7D32", "👥", member_detail_text), 
            ("Plans", str(stats['total_plans']), "#1565C0", "📋", None),
            ("Class Types", str(stats['total_classes']), "#AD1457", "🧘", None),
            ("Trainers", str(stats['trainers']), "#EF6C00", "💪", None),
            ("Equipment", str(stats['equipments']), "#6A1B9A", "🏋️", None)
        ]

        row, col = 0, 0
        for title, value, color, icon, detail in cards_data:
            card = self.create_stat_card(title, value, color, icon, detail)
            self.cards_grid.addWidget(card, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

    def create_stat_card(self, title, value, color, icon, detail=None):
        card = QFrame()
        card.setFixedHeight(170) 
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                color: white;
            }}
            QFrame:hover {{
                border: 2px solid white;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        val_lbl.setStyleSheet("border:none; background: transparent; color: white;")
        left_layout.addWidget(val_lbl)
        
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 14))
        title_lbl.setStyleSheet("border:none; background: transparent; color: #E0E0E0;")
        left_layout.addWidget(title_lbl)

        if detail:
            detail_lbl = QLabel(detail)
            detail_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            detail_lbl.setStyleSheet("border:none; background: transparent; color: #C8E6C9; margin-top: 5px;")
            left_layout.addWidget(detail_lbl)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 50))
        icon_lbl.setStyleSheet("border:none; background: transparent; opacity: 0.6;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(left_layout)
        layout.addWidget(icon_lbl)
        
        return card