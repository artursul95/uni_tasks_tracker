import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QInputDialog, QMessageBox, QDialog, QDateEdit, QFormLayout, QDialogButtonBox, QTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QDate

FILE_NAME = "tasks.json"
disciplines = {}  # {"Math": [{"task": "HW", "deadline": datetime or None}, ...]}

# =================== ЛОГИКА ===================
def save_data():
    data = {}
    for disc, tasks in disciplines.items():
        data[disc] = []
        for t in tasks:
            data[disc].append({
                "task": t["task"],
                "deadline": t["deadline"].strftime("%Y-%m-%d") if t["deadline"] else None
            })
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    global disciplines
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            for disc, tasks in data.items():
                disciplines[disc] = []
                for t in tasks:
                    deadline = datetime.strptime(t["deadline"], "%Y-%m-%d") if t["deadline"] else None
                    disciplines[disc].append({"task": t["task"], "deadline": deadline})

# =================== ГЛАВНОЕ ОКНО ===================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учебные задачи")
        self.resize(800, 450)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Левый фрейм (дисциплины)
        self.left_layout = QVBoxLayout()
        self.layout.addLayout(self.left_layout)

        self.label_disc = QLabel("Дисциплины")
        self.left_layout.addWidget(self.label_disc)
        self.list_disciplines = QListWidget()
        self.left_layout.addWidget(self.list_disciplines)

        self.btn_add_disc = QPushButton("➕ Добавить дисциплину")
        self.btn_add_disc.clicked.connect(self.add_discipline)
        self.btn_del_disc = QPushButton("❌ Удалить дисциплину")
        self.btn_del_disc.clicked.connect(self.delete_discipline)

        self.left_layout.addWidget(self.btn_add_disc)
        self.left_layout.addWidget(self.btn_del_disc)

        # Правый фрейм (задачи)
        self.right_layout = QVBoxLayout()
        self.layout.addLayout(self.right_layout)

        self.label_tasks = QLabel("Задачи")
        self.right_layout.addWidget(self.label_tasks)
        self.list_tasks = QListWidget()
        self.right_layout.addWidget(self.list_tasks)

        self.btn_layout = QHBoxLayout()
        self.right_layout.addLayout(self.btn_layout)
        self.btn_add_task = QPushButton("➕ Добавить")
        self.btn_add_task.clicked.connect(self.add_task)
        self.btn_edit_task = QPushButton("✏️ Редактировать")
        self.btn_edit_task.clicked.connect(self.edit_task)
        self.btn_del_task = QPushButton("❌ Удалить")
        self.btn_del_task.clicked.connect(self.delete_task)
        self.btn_top5 = QPushButton("📅 задачи")
        self.btn_top5.clicked.connect(self.show_tasks)

        for b in [self.btn_add_task, self.btn_edit_task, self.btn_del_task, self.btn_top5]:
            self.btn_layout.addWidget(b)

        # события
        self.list_disciplines.currentRowChanged.connect(self.update_tasks)

        # загрузка данных
        load_data()
        self.update_disciplines()

    # =================== ДИСЦИПЛИНЫ ===================
    def update_disciplines(self):
        self.list_disciplines.clear()
        for disc in disciplines.keys():
            self.list_disciplines.addItem(disc)
        self.update_tasks()

    def add_discipline(self):
        text, ok = QInputDialog.getText(self, "Добавить дисциплину", "Название дисциплины:")
        if ok and text.strip():
            name = text.strip()
            if name in disciplines:
                QMessageBox.warning(self, "Ошибка", "Такая дисциплина уже существует!")
            else:
                disciplines[name] = []
                self.update_disciplines()
                save_data()

    def delete_discipline(self):
        idx = self.list_disciplines.currentRow()
        if idx < 0:
            return
        disc = self.list_disciplines.currentItem().text()
        reply = QMessageBox.question(
            self, "Удалить дисциплину",
            f"Вы уверены, что хотите удалить дисциплину '{disc}' вместе со всеми задачами?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            disciplines.pop(disc)
            self.update_disciplines()
            save_data()

    # =================== ЗАДАЧИ ===================
    def update_tasks(self):
        self.list_tasks.clear()
        idx = self.list_disciplines.currentRow()
        if idx < 0:
            return
        disc = self.list_disciplines.currentItem().text()
        for t in disciplines[disc]:
            deadline_text = t["deadline"].strftime("%d.%m.%Y") if t["deadline"] else "без дедлайна"
            display = f"{t['task']} (до {deadline_text})"
            self.list_tasks.addItem(display)
            if t["deadline"] and t["deadline"] < datetime.now():
                self.list_tasks.item(self.list_tasks.count() - 1).setForeground(Qt.red)
            elif t["deadline"] and (t["deadline"] - datetime.now()).days <= 2:
                self.list_tasks.item(self.list_tasks.count() - 1).setForeground(Qt.darkGreen)

    def add_task(self):
        idx = self.list_disciplines.currentRow()
        if idx < 0:
            return
        disc = self.list_disciplines.currentItem().text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить задачу")
        layout = QFormLayout(dialog)

        task_name, ok = QInputDialog.getText(self, "Добавить задачу", "Название задачи:")
        if not ok or not task_name.strip():
            return

        date_edit = QDateEdit(calendarPopup=True)
        date_edit.setDate(QDate.currentDate())
        no_deadline = QCheckBox("Без дедлайна")
        layout.addRow("Дедлайн:", date_edit)
        layout.addRow(no_deadline)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            if no_deadline.isChecked():
                deadline = None
            else:
                deadline = datetime(date_edit.date().year(), date_edit.date().month(), date_edit.date().day())
            disciplines[disc].append({"task": task_name.strip(), "deadline": deadline})
            self.update_tasks()
            save_data()

    def edit_task(self):
        idx_disc = self.list_disciplines.currentRow()
        idx_task = self.list_tasks.currentRow()
        if idx_disc < 0 or idx_task < 0:
            return
        disc = self.list_disciplines.currentItem().text()
        task_obj = disciplines[disc][idx_task]

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать задачу")
        layout = QFormLayout(dialog)

        task_name, ok = QInputDialog.getText(self, "Редактировать задачу", "Название задачи:", text=task_obj["task"])
        if not ok or not task_name.strip():
            return

        date_edit = QDateEdit(calendarPopup=True)
        date_edit.setDate(QDate.currentDate())
        no_deadline = QCheckBox("Без дедлайна")
        if task_obj["deadline"]:
            date_edit.setDate(QDate(task_obj["deadline"].year, task_obj["deadline"].month, task_obj["deadline"].day))
        else:
            no_deadline.setChecked(True)
        layout.addRow("Дедлайн:", date_edit)
        layout.addRow(no_deadline)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            task_obj["task"] = task_name.strip()
            if no_deadline.isChecked():
                task_obj["deadline"] = None
            else:
                task_obj["deadline"] = datetime(date_edit.date().year(), date_edit.date().month(), date_edit.date().day())
            self.update_tasks()
            save_data()

    def delete_task(self):
        idx_disc = self.list_disciplines.currentRow()
        idx_task = self.list_tasks.currentRow()
        if idx_disc < 0 or idx_task < 0:
            return
        disc = self.list_disciplines.currentItem().text()
        disciplines[disc].pop(idx_task)
        self.update_tasks()
        save_data()

    def show_tasks(self):
        all_tasks = []
        for disc, tasks in disciplines.items():
            for t in tasks:
                all_tasks.append((disc, t["task"], t["deadline"]))
        all_tasks.sort(key=lambda x: (x[2] is None, x[2] if x[2] else datetime.max))
        top5 = all_tasks
        dlg = QDialog(self)
        dlg.setWindowTitle("Топ-5 задач")
        layout = QVBoxLayout(dlg)
        txt = QTextEdit()
        txt.setReadOnly(True)
        content = ""
        for i, (disc, task, deadline) in enumerate(top5, start=1):
            deadline_text = deadline.strftime("%d.%m.%Y") if deadline else "без дедлайна"
            content += f"{i}. [{disc}] {task} (до {deadline_text})\n"
        txt.setText(content)
        layout.addWidget(txt)
        dlg.exec()

# =================== ЗАПУСК ===================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
