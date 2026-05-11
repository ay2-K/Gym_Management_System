import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from db_manager import GymDatabase

from tabs.dashboard import DashboardPage
from tabs.manage import MemberPage, TrainerPage
from tabs.plans import PlansPage
from tabs.checkin import CheckinPage
from tabs.equipments import EquipmentPage
from tabs.classes import GymClassesPage, SchedulePage, EnrollmentPage

class GymMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = GymDatabase()
        
        self.setWindowTitle("Gym Management System")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet("background-color: #f4f6f9;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_sidebar()
        
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        self.page_dash = DashboardPage(self.db)
        self.page_member = MemberPage(self.db)
        self.page_trainer = TrainerPage(self.db)
        self.page_plans = PlansPage(self.db)
        self.page_checkin = CheckinPage(self.db)
        self.page_equip = EquipmentPage(self.db)
        self.page_classes = GymClassesPage(self.db)
        self.page_schedule = SchedulePage(self.db)
        self.page_enroll = EnrollmentPage(self.db)

        self.content_area.addWidget(self.page_dash)
        self.content_area.addWidget(self.page_member)
        self.content_area.addWidget(self.page_trainer)
        self.content_area.addWidget(self.page_plans)
        self.content_area.addWidget(self.page_checkin)
        self.content_area.addWidget(self.page_equip)
        self.content_area.addWidget(self.page_classes)
        self.content_area.addWidget(self.page_schedule)
        self.content_area.addWidget(self.page_enroll)

        self.switch_page(0, self.btn_main)

    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("""
            QFrame { background-color: #033e63; color: white; min-width: 240px; max-width: 240px; }
            QPushButton { 
                background-color: transparent; border: none; text-align: left; padding-left: 25px; 
                color: white; font-size: 16px; font-weight: bold; height: 50px;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:checked { background-color: #0D47A1; border-left: 5px solid white; font-weight: bold;}
        """)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 20, 0, 20); layout.setSpacing(5)

        title = QLabel("Gym System")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin-bottom: 20px; background-color: transparent;")
        layout.addWidget(title)

        self.btn_main = self.add_menu_button(layout, "🏠 Dashboard", 0)

        self.btn_manage = self.add_dropdown_header(layout, "👥 Manage ▼")
        self.sub_manage_frame = self.add_sub_menu(layout, [("Member", 1), ("Trainer", 2)])
        self.btn_manage.clicked.connect(lambda: self.toggle_menu(self.sub_manage_frame, self.btn_manage))

        self.btn_plans = self.add_menu_button(layout, "📋 Plans", 3)
        self.btn_checkin = self.add_menu_button(layout, "⏱️ Check-in", 4)
        self.btn_equip = self.add_menu_button(layout, "🏋️ Equipments", 5)
        

        self.btn_classes = self.add_dropdown_header(layout, "📅 Classes ▼")
        self.sub_classes_frame = self.add_sub_menu(layout, [("Gym Class", 6), ("Schedule", 7), ("Enrollment", 8)])
        self.btn_classes.clicked.connect(lambda: self.toggle_menu(self.sub_classes_frame, self.btn_classes))

        layout.addStretch()
        self.main_layout.addWidget(self.sidebar)
        
        self.all_nav_buttons = [self.btn_main, self.btn_plans, self.btn_checkin, self.btn_equip]

    def add_menu_button(self, layout, text, idx):
        btn = QPushButton(text)
        btn.clicked.connect(lambda: self.switch_page(idx, btn))
        layout.addWidget(btn)
        return btn
    
    def add_dropdown_header(self, layout, text):
        btn = QPushButton(text)
        btn.setStyleSheet("background-color: #033e63; color: white; text-align: left; padding-left: 20px; height: 45px;")
        layout.addWidget(btn)
        return btn

    def add_sub_menu(self, layout, items):
        f = QFrame(); f.setVisible(False)
        f.setStyleSheet("background-color: #033e63;") 
        l = QVBoxLayout(f); l.setContentsMargins(0,0,0,0); l.setSpacing(0)
        for t, i in items:
            b = QPushButton(f"    • {t}")
            b.clicked.connect(lambda c, idx=i, btn=b: self.switch_page(idx, btn))
            b.setStyleSheet("background-color: transparent; color: #ddd; text-align: left; padding-left: 20px; height: 35px;")
            l.addWidget(b)
            if not hasattr(self, 'all_sub_buttons'): self.all_sub_buttons = []
            self.all_sub_buttons.append(b)
        layout.addWidget(f); return f

    def toggle_menu(self, frame, btn):
        vis = frame.isVisible(); frame.setVisible(not vis)
        btn.setText(btn.text().replace("▲", "▼") if vis else btn.text().replace("▼", "▲"))

    def switch_page(self, idx, btn):
        self.content_area.setCurrentIndex(idx)
        
        for b in self.all_nav_buttons: b.setChecked(False)
        if hasattr(self, 'all_sub_buttons'):
            for b in self.all_sub_buttons: b.setChecked(False)
        btn.setChecked(True)

        current_widget = self.content_area.widget(idx)
        
        if idx == 0: current_widget.refresh_dashboard()
        elif idx == 1: current_widget.load_members()
        elif idx == 2: current_widget.load_trainers()
        elif idx == 3: current_widget.load_plans()
        elif idx == 5: current_widget.load_equipments()
        elif idx == 6: current_widget.load_gym_classes()
        elif idx == 7: current_widget.load_schedules()
        elif idx == 8: current_widget.load_enrollments()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GymMainWindow()
    window.show()
    sys.exit(app.exec())