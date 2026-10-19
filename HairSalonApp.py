import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import unittest
import tempfile
import sys


DB_NAME = 'salon.db'


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            duration INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("SELECT COUNT(*) FROM services")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO services (name, category, price, duration) VALUES (?, ?, ?, ?)",
            [
                ('Стрижка женская', 'Стрижка', 1500.0, 60),
                ('Стрижка мужская', 'Стрижка', 1000.0, 45),
                ('Окрашивание «Балаяж»', 'Окрашивание', 4500.0, 180),
                ('Укладка вечерняя', 'Укладка', 2000.0, 60),
                ('Маникюр классический', 'Ногти', 1200.0, 50),
            ],
        )
        cur.executemany(
            "INSERT INTO clients (full_name, phone) VALUES (?, ?)",
            [
                ('Смирнова Ольга', '+7-900-111-22-33'),
                ('Козлов Дмитрий', '+7-900-444-55-66'),
            ],
        )

    conn.commit()
    conn.close()


def add_service(name, category, price, duration):
    conn = get_connection()
    conn.execute(
        "INSERT INTO services (name, category, price, duration) VALUES (?, ?, ?, ?)",
        (name, category, price, duration),
    )
    conn.commit()
    conn.close()


def get_services(search=None):
    conn = get_connection()
    cur = conn.cursor()
    if search:
        cur.execute(
            "SELECT id, name, category, price, duration FROM services "
            "WHERE name LIKE ? ORDER BY name",
            (f'%{search}%',),
        )
    else:
        cur.execute("SELECT id, name, category, price, duration FROM services ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_client(full_name, phone):
    conn = get_connection()
    conn.execute("INSERT INTO clients (full_name, phone) VALUES (?, ?)", (full_name, phone))
    conn.commit()
    conn.close()


def get_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, phone FROM clients ORDER BY full_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_appointment(client_id, service_id, quantity, total):
    conn = get_connection()
    conn.execute(
        "INSERT INTO appointments (client_id, service_id, quantity, total) VALUES (?, ?, ?, ?)",
        (client_id, service_id, quantity, total),
    )
    conn.commit()
    conn.close()


def get_appointments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, c.full_name, s.name, a.quantity, a.total, a.created_at
        FROM appointments a
        JOIN clients c ON c.id = a.client_id
        JOIN services s ON s.id = a.service_id
        ORDER BY a.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


class HairSalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HairSalon — Парикмахерская")
        self.root.geometry("950x600")

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tab_services = tk.Frame(notebook)
        self.tab_clients = tk.Frame(notebook)
        self.tab_appointments = tk.Frame(notebook)
        self.tab_search = tk.Frame(notebook)

        notebook.add(self.tab_services, text='Услуги')
        notebook.add(self.tab_clients, text='Клиенты')
        notebook.add(self.tab_appointments, text='Записи')
        notebook.add(self.tab_search, text='Поиск')

        self.build_services()
        self.build_clients()
        self.build_appointments()
        self.build_search()

    def build_services(self):
        form = tk.LabelFrame(self.tab_services, text="Добавить услугу")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="Название:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.s_name = tk.Entry(form, width=25)
        self.s_name.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Категория:").grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.s_category = ttk.Combobox(form, values=["Стрижка", "Окрашивание", "Укладка", "Ногти", "Уход"], width=18)
        self.s_category.grid(row=0, column=3, padx=4, pady=4)
        self.s_category.set("Стрижка")

        tk.Label(form, text="Цена:").grid(row=1, column=0, padx=4, pady=4, sticky='w')
        self.s_price = tk.Entry(form, width=25)
        self.s_price.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(form, text="Длительность (мин):").grid(row=1, column=2, padx=4, pady=4, sticky='w')
        self.s_duration = tk.Entry(form, width=18)
        self.s_duration.grid(row=1, column=3, padx=4, pady=4)

        tk.Button(form, text="Добавить", command=self.add_service_click).grid(
            row=2, column=0, columnspan=4, pady=6
        )

        cols = ('ID', 'Название', 'Категория', 'Цена', 'Длительность')
        self.tree_services = ttk.Treeview(self.tab_services, columns=cols, show='headings')
        for c in cols:
            self.tree_services.heading(c, text=c)
            self.tree_services.column(c, width=150, anchor='center')
        self.tree_services.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_services()

    def add_service_click(self):
        try:
            name = self.s_name.get().strip()
            if not name:
                raise ValueError("Введите название")
            price = float(self.s_price.get())
            duration = int(self.s_duration.get())
            if price <= 0 or duration <= 0:
                raise ValueError("Цена > 0, длительность > 0")
            add_service(name, self.s_category.get(), price, duration)
            self.s_name.delete(0, tk.END)
            self.s_price.delete(0, tk.END)
            self.s_duration.delete(0, tk.END)
            self.refresh_services()
            messagebox.showinfo("Готово", "Услуга добавлена")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такая услуга уже есть")

    def refresh_services(self):
        for row in self.tree_services.get_children():
            self.tree_services.delete(row)
        for row in get_services():
            self.tree_services.insert('', 'end', values=row)

    def build_clients(self):
        form = tk.LabelFrame(self.tab_clients, text="Добавить клиента")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="ФИО:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.c_name = tk.Entry(form, width=30)
        self.c_name.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Телефон:").grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.c_phone = tk.Entry(form, width=20)
        self.c_phone.grid(row=0, column=3, padx=4, pady=4)

        tk.Button(form, text="Добавить", command=self.add_client_click).grid(
            row=1, column=0, columnspan=4, pady=6
        )

        cols = ('ID', 'ФИО', 'Телефон')
        self.tree_clients = ttk.Treeview(self.tab_clients, columns=cols, show='headings')
        for c in cols:
            self.tree_clients.heading(c, text=c)
            self.tree_clients.column(c, width=200, anchor='center')
        self.tree_clients.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_clients()

    def add_client_click(self):
        try:
            full_name = self.c_name.get().strip()
            phone = self.c_phone.get().strip()
            if not full_name or not phone:
                raise ValueError("Введите ФИО и телефон")
            add_client(full_name, phone)
            self.c_name.delete(0, tk.END)
            self.c_phone.delete(0, tk.END)
            self.refresh_clients()
            messagebox.showinfo("Готово", "Клиент добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Клиент с таким телефоном уже есть")

    def refresh_clients(self):
        for row in self.tree_clients.get_children():
            self.tree_clients.delete(row)
        for row in get_clients():
            self.tree_clients.insert('', 'end', values=row)

    def build_appointments(self):
        form = tk.LabelFrame(self.tab_appointments, text="Новая запись")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="Клиент:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.a_client = ttk.Combobox(form, width=30, state='readonly')
        self.a_client.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Услуга:").grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.a_service = ttk.Combobox(form, width=30, state='readonly')
        self.a_service.grid(row=0, column=3, padx=4, pady=4)

        tk.Label(form, text="Количество:").grid(row=1, column=0, padx=4, pady=4, sticky='w')
        self.a_qty = tk.Entry(form, width=10)
        self.a_qty.grid(row=1, column=1, padx=4, pady=4)
        self.a_qty.insert(0, "1")

        tk.Button(form, text="Записать", command=self.add_appointment_click).grid(
            row=2, column=0, columnspan=4, pady=6
        )

        cols = ('ID', 'Клиент', 'Услуга', 'Кол-во', 'Итого', 'Дата')
        self.tree_appointments = ttk.Treeview(self.tab_appointments, columns=cols, show='headings')
        for c in cols:
            self.tree_appointments.heading(c, text=c)
            self.tree_appointments.column(c, width=140, anchor='center')
        self.tree_appointments.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_appointments()
        self.refresh_comboboxes()

    def refresh_comboboxes(self):
        clients = get_clients()
        self.a_client['values'] = [f"{c[0]} — {c[1]}" for c in clients]
        services = get_services()
        self.a_service['values'] = [f"{s[0]} — {s[1]} ({s[3]} ₽)" for s in services]

    def add_appointment_click(self):
        try:
            if not self.a_client.get() or not self.a_service.get():
                raise ValueError("Выберите клиента и услугу")
            client_id = int(self.a_client.get().split(' — ')[0])
            service_id = int(self.a_service.get().split(' — ')[0])
            qty = int(self.a_qty.get())
            if qty <= 0:
                raise ValueError("Количество > 0")
            services = dict((s[0], s) for s in get_services())
            total = services[service_id][3] * qty
            add_appointment(client_id, service_id, qty, total)
            self.a_qty.delete(0, tk.END)
            self.a_qty.insert(0, "1")
            self.refresh_appointments()
            messagebox.showinfo("Готово", "Запись создана")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_appointments(self):
        for row in self.tree_appointments.get_children():
            self.tree_appointments.delete(row)
        for row in get_appointments():
            self.tree_appointments.insert('', 'end', values=row)

    def build_search(self):
        form = tk.LabelFrame(self.tab_search, text="Поиск услуг")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="Название:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.search_entry = tk.Entry(form, width=30)
        self.search_entry.grid(row=0, column=1, padx=4, pady=4)

        tk.Button(form, text="Найти", command=self.search_click).grid(
            row=0, column=2, padx=4, pady=4
        )
        tk.Button(form, text="Сбросить", command=self.reset_search).grid(
            row=0, column=3, padx=4, pady=4
        )

        cols = ('ID', 'Название', 'Категория', 'Цена', 'Длительность')
        self.tree_search = ttk.Treeview(self.tab_search, columns=cols, show='headings')
        for c in cols:
            self.tree_search.heading(c, text=c)
            self.tree_search.column(c, width=150, anchor='center')
        self.tree_search.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_search()

    def search_click(self):
        self.refresh_search(self.search_entry.get().strip() or None)

    def reset_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_search()

    def refresh_search(self, query=None):
        for row in self.tree_search.get_children():
            self.tree_search.delete(row)
        for row in get_services(query):
            self.tree_search.insert('', 'end', values=row)


if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = HairSalonApp(root)
    root.mainloop()
