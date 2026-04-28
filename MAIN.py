import random
import string
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "password_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Загрузка истории
        self.history = []
        self.load_history()
        
        # Создание интерфейса
        self.create_control_frame()
        self.create_password_display()
        self.create_history_frame()
        
        # Генерация первого пароля
        self.generate_password()
        
        # Сохранение при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_control_frame(self):
        """Панель управления с настройками пароля"""
        control_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Длина пароля
        ttk.Label(control_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(control_frame, from_=4, to=32, variable=self.length_var, 
                                       orient="horizontal", command=self.update_length_label)
        self.length_slider.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.length_label = ttk.Label(control_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Чекбоксы для выбора символов
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(control_frame, text="Строчные буквы (a-z)", variable=self.use_lowercase).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="Заглавные буквы (A-Z)", variable=self.use_uppercase).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(control_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Кнопки
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.generate_btn = ttk.Button(button_frame, text="🔐 Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.pack(side="left", padx=5)
        
        self.copy_btn = ttk.Button(button_frame, text="📋 Копировать", command=self.copy_to_clipboard)
        self.copy_btn.pack(side="left", padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="💾 Сохранить в историю", command=self.save_to_history)
        self.save_btn.pack(side="left", padx=5)
        
        control_frame.columnconfigure(1, weight=1)
    
    def create_password_display(self):
        """Область отображения сгенерированного пароля"""
        display_frame = ttk.LabelFrame(self.root, text="Сгенерированный пароль", padding=10)
        display_frame.pack(fill="x", padx=10, pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(display_frame, textvariable=self.password_var, 
                                        font=("Courier", 14), state="readonly")
        self.password_entry.pack(fill="x", padx=5, pady=5)
        
        # Индикатор сложности
        self.strength_label = ttk.Label(display_frame, text="Сложность: ")
        self.strength_label.pack(pady=5)
    
    def create_history_frame(self):
        """Таблица истории паролей"""
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы
        columns = ("date", "password", "length", "strength")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("strength", text="Сложность")
        
        self.tree.column("date", width=150)
        self.tree.column("password", width=250)
        self.tree.column("length", width=80)
        self.tree.column("strength", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления историей
        history_buttons = ttk.Frame(history_frame)
        history_buttons.pack(fill="x", pady=5)
        
        ttk.Button(history_buttons, text="🗑 Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(history_buttons, text="📋 Скопировать выбранный", command=self.copy_selected).pack(side="left", padx=5)
        
        self.update_history_display()
    
    def update_length_label(self, event=None):
        """Обновление метки длины"""
        self.length_label.config(text=str(int(self.length_var.get())))
    
    def generate_password(self):
        """Генерация пароля на основе выбранных параметров"""
        length = int(self.length_var.get())
        
        # Проверка валидации
        if not self.validate_settings():
            return
        
        # Сбор символов для генерации
        characters = ""
        if self.use_lowercase.get():
            characters += string.ascii_lowercase
        if self.use_uppercase.get():
            characters += string.ascii_uppercase
        if self.use_digits.get():
            characters += string.digits
        if self.use_symbols.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Генерация пароля
        password = ''.join(random.choice(characters) for _ in range(length))
        self.password_var.set(password)
        
        # Обновление индикатора сложности
        self.update_strength_indicator(password)
    
    def validate_settings(self):
        """Проверка корректности настроек"""
        length = int(self.length_var.get())
        
        # Проверка длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа!")
            self.length_var.set(4)
            self.update_length_label()
            return False
        
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа!")
            self.length_var.set(32)
            self.update_length_label()
            return False
        
        # Проверка выбора хотя бы одного набора символов
        if not (self.use_lowercase.get() or self.use_uppercase.get() or 
                self.use_digits.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return False
        
        return True
    
    def update_strength_indicator(self, password):
        """Оценка сложности пароля"""
        score = 0
        length = len(password)
        
        # Критерии сложности
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        # Определение сложности
        if score <= 2:
            strength = "Очень слабый"
            color = "red"
        elif score <= 4:
            strength = "Слабый"
            color = "orange"
        elif score <= 6:
            strength = "Средний"
            color = "yellow"
        else:
            strength = "Сильный"
            color = "green"
        
        self.strength_label.config(text=f"Сложность: {strength}", foreground=color)
    
    def save_to_history(self):
        """Сохранение текущего пароля в историю"""
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Предупреждение", "Нет пароля для сохранения!")
            return
        
        # Проверка на дубликаты
        for entry in self.history:
            if entry["password"] == password:
                messagebox.showinfo("Информация", "Этот пароль уже есть в истории!")
                return
        
        # Сохранение
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": len(password),
            "strength": self.strength_label.cget("text").replace("Сложность: ", "")
        }
        
        self.history.append(history_entry)
        self.save_history()
        self.update_history_display()
        messagebox.showinfo("Успех", "Пароль сохранён в историю!")
    
    def update_history_display(self):
        """Обновление отображения истории"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        for entry in reversed(self.history):  # Новые сверху
            self.tree.insert("", "end", values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["strength"]
            ))
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования!")
    
    def copy_selected(self):
        """Копирование выбранного пароля из истории"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пароль из истории!")
            return
        
        values = self.tree.item(selected[0], "values")
        password = values[1]
        
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        messagebox.showinfo("Успех", "Пароль из истории скопирован!")
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            messagebox.showinfo("Успех", "История очищена!")
    
    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.history = []
        else:
            self.history = []
    
    def save_history(self):
        """Сохранение истории в JSON"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def on_close(self):
        """При закрытии приложения"""
        self.save_history()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()