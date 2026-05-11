# Gym_Management_System
🏋️‍♂️This project is a database-driven management system developed to meet the operational needs of a modern fitness center. Created as part of the Database Systems course , the application centrally manages member registrations, subscription tracking, trainer specialties, class schedules, and equipment inventory through a SQL database.  
🚀 FeaturesReal-Time Dashboard: Provides an administrative overview displaying critical metrics such as total revenue, active/passive member counts, and equipment status on a single screen.  
Access Control System (Check-In): Acts as a primary security layer by querying a unique Member ID to check membership status ('Active'/'Passive') and remaining days, granting or denying access accordingly.  
Dynamic Class Schedule: Manages weekly timetables (e.g., CrossFit, Yoga, Spinner) and trainers, preventing scheduling conflicts using UNIQUE KEY constraints.  
Membership & Financial Management: Defines different membership plans, records payment details during member registration, and executes operations using an "all-or-nothing" transaction principle to ensure data integrity.  Equipment Tracking: Monitors physical assets in the gym categorized by quantity and purchase date.  
🛠️ Technology StackFrontend: Python, PyQt6   Backend: MySQL   Architecture: Modular Python scripts , Relational Database Design , and Stored Procedures.  
🗄️ Database ArchitectureThe system is built on a normalized relational schema consisting of 10 main tables. To ensure data integrity and improve performance, complex logical operations are handled at the database layer using Stored Procedures:  GetDashboardStats: Aggregates and returns all statistics across multiple tables with a single call.  
CheckMemberAccess: Simultaneously evaluates the member's active status and checks if the membership plan has expired.  
GetMemberWithRemaining: Retrieves detailed member information and dynamically calculates the remaining subscription days.  

⚙️ Installation & SetupClone the Repository: Bashgit clone https://github.com/ay2-k/gym-management-system.git
cd gym-management-system
Install Dependencies:Bashpip install mysql-connector-python PyQt6
Database Configuration:Open db_manager.py and setup_database.py.  Replace 'your_password_here' with your local MySQL root password in the connection configurations.Initialize the Database:
Run the setup script to automatically create the gym_db database, necessary tables, constraints, and stored procedures:  Bashpython setup_database.py
Run the Application:
Start the main entry point of the application:  Bashpython main.py
