from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AddPlanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Plan"); self.setFixedSize(300, 250); self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.inp_name = QLineEdit(); self.inp_months = QSpinBox(); self.inp_months.setRange(1,60)
        self.inp_price = QDoubleSpinBox(); self.inp_price.setRange(0, 100000); self.inp_price.setSuffix(" $")
        form.addRow("Plan Name:", self.inp_name); form.addRow("Duration (Mo):", self.inp_months); form.addRow("Price:", self.inp_price)
        self.layout.addLayout(form); self.btn_save = QPushButton("Save"); self.btn_save.setStyleSheet("background-color: #1565C0; color: white; padding: 10px; font-weight: bold;"); self.btn_save.clicked.connect(self.accept); self.layout.addWidget(self.btn_save)

    def get_data(self): return (self.inp_name.text(), self.inp_months.value(), self.inp_price.value())

class PlansPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        header_lbl = QLabel("Membership Plans"); header_lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        btn_add = QPushButton("+ Add Plan"); btn_add.setFixedSize(120, 40)
        btn_add.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 20px; font-weight: bold; } QPushButton:hover { background-color: #388E3C; }")
        btn_add.clicked.connect(self.open_add_plan)
        
        top_bar.addWidget(header_lbl); top_bar.addStretch(); top_bar.addWidget(btn_add); layout.addLayout(top_bar)
        
        self.scroll_area = QScrollArea(); self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")
        self.scroll_content = QWidget(); self.cards_layout_plans = QHBoxLayout(self.scroll_content)
        self.cards_layout_plans.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop); self.cards_layout_plans.setSpacing(20)
        self.scroll_area.setWidget(self.scroll_content); layout.addWidget(self.scroll_area)
        self.load_plans()

    def load_plans(self):
        while self.cards_layout_plans.count():
            item = self.cards_layout_plans.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        plans = self.db.get_all_plans()
        if not plans: 
            self.cards_layout_plans.addWidget(QLabel("No plans added."))
            return

        for p in plans:
            card = self.create_plan_card(p) 
            self.cards_layout_plans.addWidget(card)
        
        self.cards_layout_plans.addStretch()

    def create_plan_card(self, data):
        p_id, name, months, price = data
        
        card = QFrame()
        card.setFixedSize(300, 560)
        card.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #e0e0e0; } 
            QFrame:hover { border: 2px solid #b71c1c; }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(15)
        
        lbl_name = QLabel(name.upper())
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl_name.setStyleSheet("background: transparent; border: none; color: #333;")
        
        btn_price = QPushButton(f"{price} $ / {months} Mo")
        btn_price.setFixedHeight(45)
        btn_price.setStyleSheet("""
            background-color: #b71c1c; color: white; border-radius: 22px; 
            font-weight: bold; border: none; font-size: 14px;
        """)
        
        features_layout = QVBoxLayout()
        features_layout.setSpacing(10)
        features = ["Unlimited Gym Access", "Locker & Shower Access", "Free WiFi", "Cardio & Strength Area", "All Group Classes Included", "Free Body Measurements"]
            
        for f in features:
            row = QHBoxLayout()
            icon = QLabel("✓")
            icon.setStyleSheet("background: transparent; color: #d32f2f; font-weight: bold; font-size: 16px; border: none;")
            txt = QLabel(f)
            txt.setWordWrap(True)
            txt.setStyleSheet("background: transparent; color: #555; font-size: 13px; border: none;")
            row.addWidget(icon)
            row.addWidget(txt, 1)
            features_layout.addLayout(row)
            
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("background-color:#eee; border:none; max-height:1px;")

        btn_delete = QPushButton("Delete Plan")
        btn_delete.setFixedSize(140, 35)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton { background-color: #ff5252; color: white; border-radius: 17px; font-weight: bold; font-size: 13px; border: none; }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        btn_delete.clicked.connect(lambda _, pid=p_id: self.delete_plan_action(pid))
        
        layout.addWidget(lbl_name)
        layout.addWidget(btn_price)
        layout.addSpacing(10)
        layout.addWidget(line)
        layout.addLayout(features_layout)
        layout.addStretch()
        layout.addWidget(btn_delete, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return card

    def open_add_plan(self):
        d = AddPlanDialog(self)
        if d.exec(): self.db.add_plan(*d.get_data()); self.load_plans()

    def delete_plan_action(self, plan_id):
        confirm = QMessageBox.question(self, "Delete", "Delete this plan?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db.delete_plan(plan_id):
                self.load_plans()
            else:
                QMessageBox.critical(self, "Error", "Could not delete plan.")