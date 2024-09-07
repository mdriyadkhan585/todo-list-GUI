import sys
import sqlite3
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                                QLineEdit, QListWidget, QMessageBox, QHBoxLayout, QInputDialog, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

DATABASE = 'todo_list.db'

class ToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Application")
        self.setGeometry(100, 100, 400, 550)  # Increased height to accommodate the new buttons

        self.is_light_theme = True

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Top Layout for Exit and Theme Change Buttons
        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: #F44336; color: white; padding: 10px; border-radius: 5px;")
        self.exit_button.clicked.connect(self.close)
        self.top_layout.addWidget(self.exit_button)

        # Theme Change Button
        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.top_layout.addWidget(self.theme_button)

        # Header
        self.header = QLineEdit()
        self.header.setText("To-Do List")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        self.layout.addWidget(self.header)

        # Input Field
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task")
        self.task_input.setStyleSheet("padding: 10px; border: 2px solid #4CAF50; border-radius: 5px;")
        self.layout.addWidget(self.task_input)

        # Button Layout
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Task")
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.add_button.clicked.connect(self.add_task)
        self.button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Task")
        self.edit_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px;")
        self.edit_button.clicked.connect(self.edit_task)
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Task")
        self.delete_button.setStyleSheet("background-color: #F44336; color: white; padding: 10px; border-radius: 5px;")
        self.delete_button.clicked.connect(self.delete_task)
        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

        # Task List
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("border: 2px solid #4CAF50; border-radius: 5px;")
        self.layout.addWidget(self.task_list)

        # Save to XML Button
        self.save_xml_button = QPushButton("Save to XML")
        self.save_xml_button.setStyleSheet("background-color: #FF9800; color: white; padding: 10px; border-radius: 5px;")
        self.save_xml_button.clicked.connect(self.save_to_xml)
        self.layout.addWidget(self.save_xml_button)

        # Import from XML Button
        self.import_xml_button = QPushButton("Import from XML")
        self.import_xml_button.setStyleSheet("background-color: #03A9F4; color: white; padding: 10px; border-radius: 5px;")
        self.import_xml_button.clicked.connect(self.import_from_xml)
        self.layout.addWidget(self.import_xml_button)

        self.load_tasks()
        self.update_theme()

    def open_database(self):
        return sqlite3.connect(DATABASE)

    def create_table(self):
        conn = self.open_database()
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL
            );
            """)
        conn.close()

    def add_task(self):
        task = self.task_input.text().strip()
        if not task:
            QMessageBox.warning(self, "Input Error", "Task cannot be empty.")
            return

        conn = self.open_database()
        with conn:
            conn.execute("INSERT INTO tasks (task) VALUES (?);", (task,))
        conn.close()

        self.task_input.clear()
        self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        conn = self.open_database()
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM tasks;")
        tasks = cursor.fetchall()
        conn.close()
        
        for task in tasks:
            self.task_list.addItem(f"{task[0]}. {task[1]}")

    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a task to delete.")
            return

        task_id = int(selected_item.text().split(".")[0])
        conn = self.open_database()
        with conn:
            conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        conn.close()

        self.load_tasks()

    def edit_task(self):
        selected_item = self.task_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a task to edit.")
            return
        
        task_id = int(selected_item.text().split(".")[0])
        current_task = selected_item.text().split(". ", 1)[1]
        
        new_task, ok = QInputDialog.getText(self, "Edit Task", "Edit task:", text=current_task)
        if ok and new_task.strip():
            conn = self.open_database()
            with conn:
                conn.execute("UPDATE tasks SET task = ? WHERE id = ?;", (new_task.strip(), task_id))
            conn.close()
            self.load_tasks()

    def toggle_theme(self):
        self.is_light_theme = not self.is_light_theme
        self.update_theme()

    def update_theme(self):
        if self.is_light_theme:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#F5F5F5"))
            palette.setColor(QPalette.Button, QColor("#4CAF50"))
            palette.setColor(QPalette.ButtonText, QColor("white"))
            self.setStyleSheet("background-color: #F5F5F5; color: black;")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#212121"))
            palette.setColor(QPalette.Button, QColor("#424242"))
            palette.setColor(QPalette.ButtonText, QColor("white"))
            self.setStyleSheet("background-color: #212121; color: white;")
        QApplication.instance().setPalette(palette)

    def save_to_xml(self):
        tasks = []
        conn = self.open_database()
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM tasks;")
        tasks = cursor.fetchall()
        conn.close()

        root = ET.Element("Tasks")
        for task in tasks:
            task_element = ET.SubElement(root, "Task", id=str(task[0]))
            task_element.text = task[1]

        tree = ET.ElementTree(root)
        with open("tasks.xml", "wb") as file:
            tree.write(file)

        QMessageBox.information(self, "Success", "Tasks saved to tasks.xml")

    def import_from_xml(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open XML File", "", "XML Files (*.xml)")
        if not file_path:
            return

        tree = ET.parse(file_path)
        root = tree.getroot()

        conn = self.open_database()
        with conn:
            conn.execute("DELETE FROM tasks;")  # Clear existing tasks

            for task_element in root.findall("Task"):
                task_id = task_element.get("id")
                task_text = task_element.text
                conn.execute("INSERT INTO tasks (id, task) VALUES (?, ?);", (task_id, task_text))
        conn.close()

        self.load_tasks()
        QMessageBox.information(self, "Success", "Tasks imported from XML file")

def main():
    app = QApplication(sys.argv)
    
    window = ToDoApp()
    window.create_table()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
