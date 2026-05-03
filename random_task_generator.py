import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

class TaskManager:
    def __init__(self, filename="tasks_history.json"):
        self.filename = filename
        self.categories = {
            "Учёба": ["Прочитать статью", "Решить задачу", "Выучить 10 слов", "Посмотреть лекцию"],
            "Спорт": ["Сделать зарядку", "Пробежать 2 км", "Отжаться 20 раз", "Присесть 30 раз"],
            "Работа": ["Проверить почту", "Создать отчёт", "Позвонить клиенту", "Назначить встречу"]
        }
        self.history = []
        self.load_history()
    
    def load_history(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_history(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_all_tasks(self):
        all_tasks = []
        for category, tasks in self.categories.items():
            for task in tasks:
                all_tasks.append({"task": task, "category": category})
        return all_tasks
    
    def generate_random_task(self, category_filter=None):
        if category_filter and category_filter in self.categories:
            tasks = [{"task": task, "category": category_filter} for task in self.categories[category_filter]]
        else:
            tasks = self.get_all_tasks()
        
        if not tasks:
            return None, None
        selected = random.choice(tasks)
        return selected["task"], selected["category"]
    
    def add_custom_task(self, task, category):
        task = task.strip()
        if not task:
            return False
        if category not in self.categories:
            self.categories[category] = []
        if task not in self.categories[category]:
            self.categories[category].append(task)
            return True
        return False
    
    def add_to_history(self, task, category):
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"task": task, "category": category, "timestamp": timestamp})
        self.save_history()
    
    def get_history(self, category_filter=None):
        if category_filter and category_filter != "Все":
            return [item for item in self.history if item["category"] == category_filter]
        return self.history.copy()
    
    def clear_history(self):
        self.history = []
        self.save_history()
    
    def get_categories(self):
        return list(self.categories.keys())


class RandomTaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("800x600")
        
        self.task_manager = TaskManager()
        self.current_category_filter = tk.StringVar(value="Все")
        
        self.create_widgets()
        self.refresh_history()
    
    def create_widgets(self):
        # Панель генерации
        top_frame = ttk.LabelFrame(self.root, text="Генерация задачи", padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text="Категория:").grid(row=0, column=0, padx=5)
        categories = ["Все"] + self.task_manager.get_categories()
        self.category_combo = ttk.Combobox(top_frame, textvariable=self.current_category_filter, values=categories, state="readonly")
        self.category_combo.grid(row=0, column=1, padx=5)
        
        self.generate_btn = ttk.Button(top_frame, text="Сгенерировать задачу", command=self.generate_task)
        self.generate_btn.grid(row=0, column=2, padx=20)
        
        ttk.Label(top_frame, text="Результат:").grid(row=1, column=0, padx=5, pady=10)
        self.task_display = tk.Text(top_frame, height=3, width=60, wrap="word")
        self.task_display.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        self.task_display.config(state="disabled")
        
        # Панель добавления задачи
        middle_frame = ttk.LabelFrame(self.root, text="Добавить свою задачу", padding=10)
        middle_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(middle_frame, text="Название:").grid(row=0, column=0, padx=5)
        self.new_task_entry = ttk.Entry(middle_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(middle_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.new_category_combo = ttk.Combobox(middle_frame, values=self.task_manager.get_categories(), state="readonly")
        self.new_category_combo.grid(row=0, column=3, padx=5)
        if self.task_manager.get_categories():
            self.new_category_combo.current(0)
        
        self.add_btn = ttk.Button(middle_frame, text="Добавить", command=self.add_custom_task)
        self.add_btn.grid(row=0, column=4, padx=10)
        
        # Панель истории
        history_frame = ttk.LabelFrame(self.root, text="История", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Фильтр:").pack(side="left", padx=5)
        self.history_filter = ttk.Combobox(filter_frame, values=["Все"] + self.task_manager.get_categories(), state="readonly")
        self.history_filter.pack(side="left", padx=5)
        self.history_filter.set("Все")
        self.history_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_history())
        
        self.clear_btn = ttk.Button(filter_frame, text="Очистить историю", command=self.clear_history)
        self.clear_btn.pack(side="right", padx=5)
        
        columns = ("№", "Категория", "Задача", "Время")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        self.history_tree.heading("№", text="№")
        self.history_tree.heading("Категория", text="Категория")
        self.history_tree.heading("Задача", text="Задача")
        self.history_tree.heading("Время", text="Время")
        
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.statusbar = ttk.Label(self.root, text="Готов", relief="sunken", anchor="w")
        self.statusbar.pack(side="bottom", fill="x")
    
    def generate_task(self):
        category = self.current_category_filter.get()
        if category == "Все":
            task, cat = self.task_manager.generate_random_task()
        else:
            task, cat = self.task_manager.generate_random_task(category)
        
        if task:
            self.task_display.config(state="normal")
            self.task_display.delete(1.0, tk.END)
            self.task_display.insert(1.0, f"Задача: {task}\nКатегория: {cat}")
            self.task_display.config(state="disabled")
            self.task_manager.add_to_history(task, cat)
            self.refresh_history()
            self.statusbar.config(text=f"Сгенерировано: {task}")
        else:
            messagebox.showerror("Ошибка", "Нет задач в выбранной категории")
    
    def add_custom_task(self):
        task = self.new_task_entry.get()
        category = self.new_category_combo.get()
        
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return
        if not task or not task.strip():
            messagebox.showerror("Ошибка", "Введите задачу")
            return
        
        if self.task_manager.add_custom_task(task, category):
            self.new_task_entry.delete(0, tk.END)
            self.statusbar.config(text=f"Добавлено: {task}")
            messagebox.showinfo("Успех", f"Задача '{task}' добавлена")
            # Обновляем списки
            categories = self.task_manager.get_categories()
            self.category_combo["values"] = ["Все"] + categories
            self.history_filter["values"] = ["Все"] + categories
            self.new_category_combo["values"] = categories
        else:
            messagebox.showwarning("Ошибка", "Задача уже существует")
    
    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        filter_cat = self.history_filter.get()
        history = self.task_manager.get_history(filter_cat)
        
        for i, item in enumerate(history, 1):
            self.history_tree.insert("", "end", values=(i, item["category"], item["task"], item["timestamp"]))
        
        self.statusbar.config(text=f"Записей: {len(history)}")
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.task_manager.clear_history()
            self.refresh_history()
            self.statusbar.config(text="История очищена")


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskApp(root)
    root.mainloop()
