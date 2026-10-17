"""Tkinter GUI — работает только через HTTP API."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from app.client import PhoneBookClient
from app.models import Contact


class PhoneBookGUI(tk.Tk):
    def __init__(self, api_url: str):
        super().__init__()
        self.title(f"Телефонный справочник — {api_url}")
        self.geometry("720x480")
        self.client = PhoneBookClient(api_url)
        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Поиск:").pack(side="left")
        self.q = tk.StringVar()
        ttk.Entry(top, textvariable=self.q, width=40).pack(side="left", padx=4)
        ttk.Button(top, text="Найти", command=self.refresh).pack(side="left")

        # таблица
        cols = ("id", "name", "phone", "email", "note")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, t in zip(cols, ("ID", "Имя", "Телефон", "E-mail", "Заметка")):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=120 if c != "note" else 160)
        self.tree.pack(fill="both", expand=True, padx=8, pady=4)
        self.tree.bind("<Double-1>", lambda _e: self.edit())

        # кнопки
        btns = ttk.Frame(self, padding=8)
        btns.pack(fill="x")
        ttk.Button(btns, text="Добавить", command=self.add).pack(side="left")
        ttk.Button(btns, text="Изменить", command=self.edit).pack(side="left", padx=4)
        ttk.Button(btns, text="Удалить", command=self.delete).pack(side="left")
        ttk.Button(btns, text="Обновить", command=self.refresh).pack(side="right")
        self.refresh()

    def refresh(self):
        try:
            rows = self.client.list(self.q.get().strip())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список:\n{e}")
            return
        self.tree.delete(*self.tree.get_children())
        for c in rows:
            self.tree.insert("", "end", values=(c.id, c.name, c.phone, c.email, c.note))

    def _form(self, title: str, c: Optional[Contact] = None) -> Optional[Contact]:
        win = tk.Toplevel(self)
        win.title(title)
        win.grab_set()
        fields: dict[str, tk.StringVar] = {}
        for i, (key, label) in enumerate(
            [("name", "Имя*"), ("phone", "Телефон*"), ("email", "E-mail"), ("note", "Заметка")]
        ):
            ttk.Label(win, text=label).grid(row=i, column=0, sticky="w", padx=8, pady=4)
            v = tk.StringVar(value=getattr(c, key) if c else "")
            ttk.Entry(win, textvariable=v, width=40).grid(row=i, column=1, padx=8, pady=4)
            fields[key] = v

        result: dict[str, Optional[Contact]] = {"value": None}

        def ok():
            result["value"] = Contact(
                id=c.id if c else None,
                name=fields["name"].get(),
                phone=fields["phone"].get(),
                email=fields["email"].get(),
                note=fields["note"].get(),
            )
            win.destroy()

        bar = ttk.Frame(win)
        bar.grid(row=len(fields), column=0, columnspan=2, pady=8)
        ttk.Button(bar, text="OK", command=ok).pack(side="left")
        ttk.Button(bar, text="Отмена", command=win.destroy).pack(side="left", padx=4)
        self.wait_window(win)
        return result["value"]

    def add(self):
        c = self._form("Новый контакт")
        if not c:
            return
        try:
            self.client.create(c)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def edit(self):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(self.tree.item(sel[0], "values")[0])
        cur = self.client.get(cid)
        if not cur:
            return
        c = self._form("Изменить контакт", cur)
        if not c:
            return
        try:
            self.client.update(c)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(self.tree.item(sel[0], "values")[0])
        if messagebox.askyesno("Удалить?", "Удалить выбранный контакт?"):
            try:
                self.client.delete(cid)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
