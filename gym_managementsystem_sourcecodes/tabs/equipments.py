from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont, QBrush, QColor

class AddEquipmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Add Equipment"); self.setFixedSize(350, 250); self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.inp_name = QLineEdit(); self.inp_qty = QSpinBox(); self.inp_qty.setRange(1, 1000)
        self.inp_date = QDateEdit(); self.inp_date.setCalendarPopup(True); self.inp_date.setDate(QDate.currentDate()); self.inp_date.setDisplayFormat("dd.MM.yyyy")
        form.addRow("Name:", self.inp_name); form.addRow("Quantity:", self.inp_qty); form.addRow("Date:", self.inp_date)
        self.layout.addLayout(form); self.btn = QPushButton("Save"); self.btn.setStyleSheet("background:#4CAF50; color:white; padding:10px; font-weight:bold"); self.btn.clicked.connect(self.accept); self.layout.addWidget(self.btn)

    def get_data(self): return (self.inp_name.text().strip().title(), self.inp_qty.value(), self.inp_date.date().toString("yyyy-MM-dd"))

class EquipmentPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(15)
        
        top_bar = QHBoxLayout()
        header_lbl = QLabel("Equipment Inventory")
        header_lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header_lbl.setStyleSheet("color: #333;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedWidth(300); self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("border: 1px solid #ccc; border-radius: 20px; padding-left: 15px; background: white;")
        self.search_input.textChanged.connect(self.filter_equipments)

        btn_add = QPushButton("+ Add Equipment")
        btn_add.setFixedSize(140, 40)
        btn_add.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 20px; font-weight: bold; } QPushButton:hover { background-color: #388E3C; }")
        btn_add.clicked.connect(self.open_add_equipment)
        
        top_bar.addWidget(header_lbl); top_bar.addStretch(); top_bar.addWidget(self.search_input); top_bar.addWidget(btn_add)
        layout.addLayout(top_bar)

        self.tree_equip = QTreeWidget()
        self.tree_equip.setColumnCount(4)
        self.tree_equip.setHeaderLabels(["Item Name", "Quantity", "Date", "Action"])
        self.tree_equip.setColumnWidth(0, 300) 
        self.tree_equip.setColumnWidth(1, 100)
        self.tree_equip.setColumnWidth(2, 140)
        self.tree_equip.setColumnWidth(3, 160)
        self.tree_equip.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tree_equip.setStyleSheet("""
            QTreeWidget { background-color: white; alternate-background-color: #fafafa; border: 1px solid #e0e0e0; border-radius: 10px; font-size: 14px; outline: none; }
            QHeaderView::section { background-color: #607D8B; color: white; padding: 12px; font-weight: bold; border: none; border-right: 1px solid #455A64; }
            QTreeWidget::item { padding: 5px; border-bottom: 1px solid #eee; }
            QTreeWidget::item:selected { background-color: #CFD8DC; color: #37474F; }
            QTreeWidget::item:hover { background-color: #f5f5f5; }
        """)
        layout.addWidget(self.tree_equip)
        self.load_equipments()

    def load_equipments(self):
        self.all_equipment_data = self.db.get_all_equipments()
        self.populate_equipment_table(self.all_equipment_data)

    def populate_equipment_table(self, data):
        self.tree_equip.clear()
        groups = {}
        for row in data:
            name = row[1]; key = name.strip().title()
            if key not in groups: groups[key] = []
            groups[key].append(row)
        
        for name, rows in groups.items():
            total_qty = sum(row[2] for row in rows)
            latest_date = max(row[3] for row in rows)
            date_str = latest_date.strftime("%d.%m.%Y") if hasattr(latest_date, 'strftime') else str(latest_date)

            parent_item = QTreeWidgetItem([name, str(total_qty), f"Last: {date_str}"])
            parent_item.setFont(0, QFont("Arial", 13, QFont.Weight.Bold))
            parent_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter); parent_item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter); parent_item.setSizeHint(0, QSize(0, 45))
            self.tree_equip.addTopLevelItem(parent_item)
            
            btn_del_all = QPushButton("Delete All")
            btn_del_all.setFixedSize(90, 30); btn_del_all.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del_all.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; border-radius: 5px; font-weight: bold; font-size: 11px;} QPushButton:hover { background-color: #b71c1c; }")
            btn_del_all.clicked.connect(lambda _, n=name: self.delete_equipment_group(n))
            w_parent = QWidget(); l_p = QHBoxLayout(w_parent); l_p.setContentsMargins(0,0,0,0); l_p.setAlignment(Qt.AlignmentFlag.AlignCenter); l_p.addWidget(btn_del_all)
            self.tree_equip.setItemWidget(parent_item, 3, w_parent)

            for row in rows:
                r_date = row[3].strftime("%d.%m.%Y") if hasattr(row[3], 'strftime') else str(row[3])
                child_item = QTreeWidgetItem([name, str(row[2]), r_date])
                child_font = QFont("Arial", 10); child_font.setItalic(True)
                child_item.setFont(0, child_font); child_item.setForeground(0, QBrush(QColor("black"))); child_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter); child_item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter); child_item.setSizeHint(0, QSize(0, 35))
                parent_item.addChild(child_item)
                
                btn_del_one = QPushButton("Del")
                btn_del_one.setFixedSize(60, 24); btn_del_one.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_del_one.setStyleSheet("QPushButton { background-color: #ff9800; color: white; border-radius: 4px; font-weight: bold; font-size: 11px;} QPushButton:hover { background-color: #f57c00; }")
                btn_del_one.clicked.connect(lambda _, rid=row[0]: self.delete_equipment_single(rid))
                w_child = QWidget(); l_c = QHBoxLayout(w_child); l_c.setContentsMargins(0,0,0,0); l_c.setAlignment(Qt.AlignmentFlag.AlignCenter); l_c.addWidget(btn_del_one)
                self.tree_equip.setItemWidget(child_item, 3, w_child)
            parent_item.setExpanded(True)

    def filter_equipments(self):
        search_text = self.search_input.text().lower()
        if not hasattr(self, 'all_equipment_data'): return
        filtered = [row for row in self.all_equipment_data if search_text in str(row[1]).lower()]
        self.populate_equipment_table(filtered)

    def open_add_equipment(self):
        d = AddEquipmentDialog(self)
        if d.exec(): self.db.add_equipment(*d.get_data()); self.load_equipments()

    def delete_equipment_group(self, name):
        ret = QMessageBox.question(self, "Delete All", f"Delete ALL entries for '{name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes: self.db.delete_equipment_by_name(name); self.load_equipments()

    def delete_equipment_single(self, eq_id):
        ret = QMessageBox.question(self, "Delete", "Delete this item?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes: self.db.delete_equipment_by_id(eq_id); self.load_equipments()