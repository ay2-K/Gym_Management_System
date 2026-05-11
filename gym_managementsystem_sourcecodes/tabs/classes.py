from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont

BTN_GREEN = "QPushButton { background-color: #4CAF50; color: white; border-radius: 20px; font-weight: bold; } QPushButton:hover { background-color: #388E3C; }"
BTN_BLUE_DIALOG = "QPushButton { background-color: #1565C0; color: white; padding: 10px; font-weight: bold; border-radius: 5px; }"
BTN_RED_OUTLINE = "QPushButton { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; border-radius: 15px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #ffcdd2; border: 1px solid #e57373; }"
TABLE_STYLE = "QTableWidget { background-color: white; alternate-background-color: #f8fcf8; border: 1px solid #ddd; font-size: 13px; } QHeaderView::section { background-color: #607D8B; color: white; padding: 12px; font-weight: bold; border: none; border-right: 1px solid #455A64; } QTableWidget::item { padding-left: 10px; border-bottom: 1px solid #eee; border-right: 1px solid #e0e0e0; }"


class AddClassDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Class")
        self.setFixedSize(300, 200)
        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.inp_name = QLineEdit()
        self.inp_desc = QLineEdit()
        
        form.addRow("Name:", self.inp_name)
        form.addRow("Desc:", self.inp_desc)
        
        self.layout.addLayout(form)
        btn = QPushButton("Save")
        btn.setStyleSheet(BTN_BLUE_DIALOG)
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)

    def get_data(self):
        return (self.inp_name.text().strip(), self.inp_desc.text().strip())

class AddScheduleDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Schedule")
        self.setFixedSize(350, 300)
        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.combo_class = QComboBox()

        self.class_map = {} 
        for c in db.get_all_gym_classes():

            self.combo_class.addItem(c[1], c[0])
            self.class_map[c[1].lower()] = c[0]
            
        self.combo_trainer = QComboBox()
        self.trainer_specialties = {}
        
        for t in db.get_all_trainers():
            full_name = f"{t[1]} {t[2]}"
            t_id = t[0]
            spec = t[3]
            
            self.combo_trainer.addItem(full_name, t_id)
            self.trainer_specialties[t_id] = spec

        self.combo_trainer.currentIndexChanged.connect(self.update_class_based_on_trainer)
            
        self.combo_day = QComboBox()
        self.combo_day.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        self.time_start = QTimeEdit(QTime(10,0))
        self.time_end = QTimeEdit(QTime(11,0))
        
        form.addRow("Class:", self.combo_class)
        form.addRow("Trainer:", self.combo_trainer)
        form.addRow("Day:", self.combo_day)
        form.addRow("Start:", self.time_start)
        form.addRow("End:", self.time_end)
        
        self.layout.addLayout(form)
        btn = QPushButton("Create")
        btn.setStyleSheet(BTN_BLUE_DIALOG)
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)

        self.update_class_based_on_trainer()

    def update_class_based_on_trainer(self):
        trainer_id = self.combo_trainer.currentData()
        
        specialty = self.trainer_specialties.get(trainer_id)
        
        if specialty:
            class_id = self.class_map.get(specialty.lower())
            
            if class_id:
                index = self.combo_class.findData(class_id)
                if index >= 0:
                    self.combo_class.setCurrentIndex(index)

    def get_data(self):
        return (self.combo_class.currentData(), self.combo_trainer.currentData(), self.combo_day.currentText(), self.time_start.time().toString("HH:mm"), self.time_end.time().toString("HH:mm"))

class AddEnrollDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Enroll")
        self.setFixedSize(400, 200)
        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.combo_member = QComboBox()
        for m in db.get_all_members():
            self.combo_member.addItem(f"{m[1]} {m[2]}", m[0])
            
        self.combo_schedule = QComboBox()
        for s in db.get_all_schedules():
            self.combo_schedule.addItem(f"{s[1]} - {s[2]} ({s[3]})", s[0])
            
        form.addRow("Member:", self.combo_member)
        form.addRow("Session:", self.combo_schedule)
        
        self.layout.addLayout(form)
        btn = QPushButton("Save")
        btn.setStyleSheet(BTN_BLUE_DIALOG)
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)

    def get_data(self):
        return (self.combo_member.currentData(), self.combo_schedule.currentData())

class GymClassesPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        top = QHBoxLayout()
        header = QLabel("Gym Class Types")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        btn_add = QPushButton("+ Add Class")
        btn_add.setFixedSize(150, 40)
        btn_add.setStyleSheet(BTN_GREEN)
        btn_add.clicked.connect(self.open_add_gym_class)
        
        top.addWidget(header)
        top.addStretch()
        top.addWidget(btn_add)
        layout.addLayout(top)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background-color: transparent;")
        
        self.content = QWidget()
        self.cards_layout = QHBoxLayout(self.content)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        
        self.load_gym_classes()

    def load_gym_classes(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        classes = self.db.get_all_gym_classes()
        if not classes:
            self.cards_layout.addWidget(QLabel("No classes defined yet."))
            return

        for row in classes:
            card = self.create_card(row[0], row[1], row[2])
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    def create_card(self, class_id, name, description):
        card = QFrame()
        card.setFixedSize(250, 200) 
        card.setStyleSheet("QFrame { background-color: white; border-radius: 15px; border: 1px solid #ddd; } QFrame:hover { border: 2px solid #1565C0; }")
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_name = QLabel(name.upper())
        lbl_name.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl_name.setStyleSheet("background: transparent; border: none; color: #333;")
        layout.addWidget(lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)

        if description:
            lbl_desc = QLabel(description)
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("background: transparent; border: none; color: #555; font-style: italic;")
            layout.addWidget(lbl_desc, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            layout.addStretch()

        btn_del = QPushButton("Delete")
        btn_del.setFixedSize(100, 30)
        btn_del.setStyleSheet("background-color: #d32f2f; color: white; border-radius: 15px;")
        btn_del.clicked.connect(lambda _, cid=class_id: self.delete_class(cid))
        layout.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignCenter)
        return card

    def open_add_gym_class(self):
        d = AddClassDialog()
        if d.exec():
            name, desc = d.get_data()
            if name: 
                self.db.add_gym_class(name, desc)
                self.load_gym_classes()

    def delete_class(self, cid):
        if QMessageBox.question(self, "Delete", "Sure?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.delete_gym_class(cid)
            self.load_gym_classes()

class SchedulePage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        top = QHBoxLayout()
        btn = QPushButton("+ Add Schedule")
        btn.setFixedSize(140, 40)
        btn.setStyleSheet(BTN_GREEN)
        btn.clicked.connect(self.open_add)
        
        top.addWidget(QLabel("Weekly Schedule", font=QFont("Arial", 20, QFont.Weight.Bold)))
        top.addStretch()
        top.addWidget(btn)
        layout.addLayout(top)

        self.table = QTableWidget(14, 7)
        self.table.setHorizontalHeaderLabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        self.table.setVerticalHeaderLabels([f"{h}:00" for h in range(9, 23)])
        self.table.setStyleSheet("QTableWidget { background-color: white; border: 1px solid #ddd; } QHeaderView::section { background-color: #f5f5f5; font-weight: bold; }")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.load_schedules()

    def load_schedules(self):
        self.table.clearContents()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for s in self.db.get_all_schedules():
            try:
                c = days.index(s[3])
                r = int(str(s[4]).split(':')[0]) - 9
                if 0 <= r < 14:
                    w = QWidget()
                    w.setStyleSheet("background-color: #E3F2FD; border-left: 4px solid #1565C0; border-radius: 4px;")
                    l = QVBoxLayout(w)
                    l.setContentsMargins(2, 2, 2, 2)
                    
                    lbl_cls = QLabel(s[1])
                    lbl_cls.setFont(QFont("Arial", 13, QFont.Weight.Bold))
                    lbl_cls.setStyleSheet("color: #1565C0; border: none;")
                    
                    lbl_tr = QLabel(s[2])
                    lbl_tr.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                    lbl_tr.setStyleSheet("color: #555; border: none;")
                    
                    top_lay = QHBoxLayout()
                    top_lay.addWidget(lbl_cls)
                    top_lay.addStretch()
                    
                    btn = QPushButton("x")
                    btn.setFixedSize(15, 15)
                    btn.setStyleSheet("color: red; font-weight: bold; border: none;")
                    btn.clicked.connect(lambda _, sid=s[0]: self.delete_sch(sid))
                    top_lay.addWidget(btn)
                    
                    l.addLayout(top_lay)
                    l.addWidget(lbl_tr)
                    l.addStretch()
                    
                    self.table.setCellWidget(r, c, w)
            except: pass

    def open_add(self):
        d = AddScheduleDialog(self.db)
        if d.exec():
            self.db.add_schedule(*d.get_data())
            self.load_schedules()

    def delete_sch(self, sid):
        if QMessageBox.question(self, "Delete", "Sure?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db.delete_schedule(sid)
            self.load_schedules()

class EnrollmentPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        top = QHBoxLayout()
        btn = QPushButton("+ Enroll Member")
        btn.setFixedSize(160, 40)
        btn.setStyleSheet(BTN_GREEN)
        btn.clicked.connect(self.open_add)
        
        top.addWidget(QLabel("Enrollments", font=QFont("Arial", 20, QFont.Weight.Bold)))
        top.addStretch()
        top.addWidget(btn)
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Member", "Class", "Day", "Time", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        
        layout.addWidget(self.table)
        self.load_enrollments()

    def load_enrollments(self):
        self.table.setRowCount(0)
        for r, row in enumerate(self.db.get_all_enrollments()):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 50)
            
            for c, val in enumerate([row[0], row[1], row[2], row[3]]):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
            
            time_str = str(row[4])
            self.table.setItem(r, 4, QTableWidgetItem(time_str[:5] if len(time_str) > 5 else time_str))

            btn = QPushButton("Cancel")
            btn.setFixedSize(80, 25)
            btn.setStyleSheet(BTN_RED_OUTLINE)
            btn.clicked.connect(lambda _, eid=row[0]: self.delete_enr(eid))
            
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(btn)
            self.table.setCellWidget(r, 5, w)

    def open_add(self):
        d = AddEnrollDialog(self.db) 
        if d.exec():
            try:
                self.db.add_enrollment(*d.get_data())
                self.load_enrollments()
            except Exception as e:
                QMessageBox.warning(self)

    def delete_enr(self, eid):
        self.db.delete_enrollment(eid)
        self.load_enrollments()