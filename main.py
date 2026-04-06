import tkinter as tk
from tkinter import font as tkfont, messagebox
from storage import load_tasks, save_tasks, load_balance, save_balance

BG = "#ffffff"
BG_SELECTED = "#e8f0fe"
BG_DONE = "#f5f5f5"
FG_NORMAL = "#1a1a1a"
FG_DONE = "#aaaaaa"
FG_NUM = "#888888"

ITEMS = [
    {"name": "Старый телефон",     "emoji": "📱", "price": 5},
    {"name": "Велосипед",          "emoji": "🚲", "price": 10},
    {"name": "Подержанный автомобиль", "emoji": "🚗", "price": 20},
    {"name": "Дом",                "emoji": "🏠", "price": 35},
    {"name": "Бизнес",             "emoji": "💼", "price": 55},
    {"name": "Особняк",            "emoji": "🏰", "price": 80},
    {"name": "Яхта",               "emoji": "⛵", "price": 110},
]

CHARACTER_LEVELS = [
    {"emoji": "🧍", "status": "Бездомный",      "desc": "У тебя нет ничего. Ни крыши, ни цели. Но именно отсюда начинается путь."},
    {"emoji": "😓", "status": "Бедняк",          "desc": "Старый телефон в кармане — уже что-то. Ты на ногах, и это главное."},
    {"emoji": "🚴", "status": "Рабочий",         "desc": "Велосипед, мозоли и упорство. Ты работаешь и двигаешься вперёд."},
    {"emoji": "🧑", "status": "Средний класс",   "desc": "Свой автомобиль, стабильный доход. Жизнь наладилась — не останавливайся."},
    {"emoji": "🏡", "status": "Зажиточный",      "desc": "Собственный дом. Ты создал фундамент, на котором можно строить большее."},
    {"emoji": "💼", "status": "Предприниматель", "desc": "Бизнес под твоим управлением. Ты больше не работаешь на кого-то — на тебя работают."},
    {"emoji": "🤵", "status": "Богач",           "desc": "Особняк, роскошь, признание. Ты достиг того, о чём другие только мечтают."},
    {"emoji": "⛵", "status": "Миллионер",       "desc": "Яхта в открытом море. Ты свободен. Clarity помогла тебе стать лучшей версией себя."},
]


class ClarityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clarity")
        self.root.resizable(False, False)

        self.tasks = load_tasks()
        self.balance, self.items_owned = load_balance()
        self.selected_idx = None

        self._font = tkfont.Font(family="Segoe UI", size=12)
        self._font_strike = tkfont.Font(family="Segoe UI", size=12, overstrike=1)
        self._font_num = tkfont.Font(family="Segoe UI", size=11)

        self._build_ui()
        self._refresh_list()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Верхняя панель ───────────────────────────────────────────────
        top_frame = tk.Frame(self.root, padx=10, pady=8, bg=BG)
        top_frame.pack(fill=tk.X)

        level = CHARACTER_LEVELS[self.items_owned]
        tk.Label(top_frame, text="Статус:", font=("Segoe UI", 12),
                 bg=BG, fg="#888888").pack(side=tk.LEFT, padx=(0, 4))
        self.char_label = tk.Label(
            top_frame,
            text=f"{level['emoji']} {level['status']}",
            font=("Segoe UI", 12), bg=BG, fg="#555555", cursor="hand2"
        )
        self.char_label.pack(side=tk.LEFT, padx=(0, 10))
        self.char_label.bind("<Button-1>", lambda e: self._open_status_popup())
        self.balance_label = tk.Label(
            top_frame, text=f"$ {self.balance}",
            font=("Segoe UI", 12), bg=BG, fg="#b8860b"
        )
        self.balance_label.pack(side=tk.RIGHT, padx=(0, 4))
        tk.Button(top_frame, text="🏪", font=("Segoe UI", 12),
                  command=self._open_shop).pack(side=tk.RIGHT, padx=(0, 6))

        # ── Список задач (Canvas + прокрутка) ────────────────────────────
        container = tk.Frame(self.root, padx=10, bg=BG)
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, width=460, height=360,
                                highlightthickness=0, bg=BG)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                 command=self.canvas.yview)
        self.tasks_frame = tk.Frame(self.canvas, bg=BG)

        self.tasks_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Нижняя панель ────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, padx=10, pady=10, bg=BG)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Выполнено", font=("Segoe UI", 11),
                  command=self._mark_done).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(btn_frame, text="Удалить", font=("Segoe UI", 11),
                  fg="red", command=self._delete_task).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(btn_frame, text="↓", font=("Segoe UI", 13),
                  width=3, command=self._move_down_selected).pack(side=tk.RIGHT, padx=(4, 0))
        tk.Button(btn_frame, text="↑", font=("Segoe UI", 13),
                  width=3, command=self._move_up_selected).pack(side=tk.RIGHT)

        self.entry = tk.Entry(btn_frame, font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda e: self._add_task())

    # ── Отрисовка ─────────────────────────────────────────────────────────

    def _refresh_list(self):
        for w in self.tasks_frame.winfo_children():
            w.destroy()
        for i, task in enumerate(self.tasks):
            self._make_row(i, task)

    def _make_row(self, idx, task):
        is_sel = self.selected_idx == idx
        bg = BG_SELECTED if is_sel else (BG_DONE if task["done"] else BG)

        row = tk.Frame(self.tasks_frame, bg=bg, pady=5)
        row.pack(fill=tk.X, padx=4, pady=1)

        num = tk.Label(row, text=f"{idx + 1}.", font=self._font_num,
                       fg=FG_NUM, bg=bg, width=3, anchor="e")
        num.pack(side=tk.LEFT, padx=(2, 6))

        f = self._font_strike if task["done"] else self._font
        fg = FG_DONE if task["done"] else FG_NORMAL
        title = tk.Label(row, text=task["title"], font=f, fg=fg,
                         bg=bg, anchor="w")
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        for widget in (row, num, title):
            widget.bind("<Button-1>", lambda e, i=idx: self._select(i))

    # ── Логика ────────────────────────────────────────────────────────────

    def _select(self, idx):
        self.selected_idx = idx
        self._refresh_list()

    def _add_task(self):
        title = self.entry.get().strip()
        if not title:
            return
        insert_at = next(
            (i for i, t in enumerate(self.tasks) if t["done"]),
            len(self.tasks)
        )
        self.tasks.insert(insert_at, {"title": title, "done": False})
        save_tasks(self.tasks)
        self.entry.delete(0, tk.END)
        self.selected_idx = None
        self._refresh_list()

    def _require_selection(self):
        if self.selected_idx is None:
            messagebox.showinfo("Clarity", "Выберите задачу из списка.")
            return False
        return True

    def _update_balance(self, delta):
        self.balance = max(0, self.balance + delta)
        save_balance(self.balance, self.items_owned)
        self.balance_label.config(text=f"$ {self.balance}")

    def _update_character(self):
        level = CHARACTER_LEVELS[self.items_owned]
        self.char_label.config(text=f"{level['emoji']} {level['status']}")

    def _mark_done(self):
        if not self._require_selection():
            return
        task = self.tasks.pop(self.selected_idx)
        task["done"] = True
        self.tasks.append(task)
        self.selected_idx = None
        save_tasks(self.tasks)
        self._update_balance(+1)
        self._refresh_list()

    def _delete_task(self):
        if not self._require_selection():
            return

        if self.tasks[self.selected_idx]["done"]:
            self.tasks.pop(self.selected_idx)
            self.selected_idx = None
            save_tasks(self.tasks)
            self._refresh_list()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Причина удаления")
        dialog.resizable(False, False)
        dialog.grab_set()

        self.root.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - 150
        y = self.root.winfo_y() + self.root.winfo_height() // 2 - 60
        dialog.geometry(f"300x120+{x}+{y}")

        tk.Label(dialog, text="Почему удаляете задачу?",
                 font=("Segoe UI", 12), pady=12).pack()

        btn_row = tk.Frame(dialog)
        btn_row.pack()

        def confirm(reason):
            dialog.destroy()
            self.tasks.pop(self.selected_idx)
            self.selected_idx = None
            save_tasks(self.tasks)
            if reason == "undone":
                self._update_balance(-2)
            self._refresh_list()

        tk.Button(btn_row, text="Неактуально", font=("Segoe UI", 11), width=12,
                  command=lambda: confirm("irrelevant")).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_row, text="Не выполнено", font=("Segoe UI", 11), width=12,
                  command=lambda: confirm("undone")).pack(side=tk.LEFT, padx=8)

    def _move_up_selected(self):
        idx = self.selected_idx
        if idx is None or idx == 0 or self.tasks[idx - 1]["done"]:
            return
        self.tasks[idx], self.tasks[idx - 1] = self.tasks[idx - 1], self.tasks[idx]
        self.selected_idx = idx - 1
        save_tasks(self.tasks)
        self._refresh_list()

    def _move_down_selected(self):
        idx = self.selected_idx
        if idx is None or idx >= len(self.tasks) - 1 or self.tasks[idx + 1]["done"]:
            return
        self.tasks[idx], self.tasks[idx + 1] = self.tasks[idx + 1], self.tasks[idx]
        self.selected_idx = idx + 1
        save_tasks(self.tasks)
        self._refresh_list()

    def _open_status_popup(self):
        level = CHARACTER_LEVELS[self.items_owned]
        popup = tk.Toplevel(self.root)
        popup.title("Кто ты?")
        popup.resizable(False, False)
        popup.grab_set()

        self.root.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - 175
        y = self.root.winfo_y() + self.root.winfo_height() // 2 - 60
        popup.geometry(f"350x120+{x}+{y}")
        popup.configure(bg=BG)

        tk.Label(popup, text=f"{level['emoji']} {level['status']}",
                 font=("Segoe UI", 13, "bold"), bg=BG).pack(pady=(14, 6))
        tk.Label(popup, text=level["desc"], font=("Segoe UI", 11),
                 bg=BG, fg="#555555", wraplength=310, justify="center").pack(padx=16)

    def _open_shop(self):
        shop = tk.Toplevel(self.root)
        shop.title("Магазин")
        shop.resizable(False, False)
        shop.grab_set()

        self.root.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - 175
        y = self.root.winfo_y() + self.root.winfo_height() // 2 - 190
        shop.geometry(f"350x380+{x}+{y}")
        shop.configure(bg=BG)

        tk.Label(shop, text="Магазин", font=("Segoe UI", 14, "bold"),
                 bg=BG).pack(pady=(12, 8))

        for i, item in enumerate(ITEMS):
            owned = i < self.items_owned
            is_next = i == self.items_owned
            can_buy = is_next and self.balance >= item["price"]

            row = tk.Frame(shop, bg=BG, pady=5)
            row.pack(fill=tk.X, padx=16)

            status = "✅" if owned else ("  " if is_next else "🔒")
            fg = FG_NORMAL if (owned or is_next) else FG_DONE
            tk.Label(row, text=f"{status} {item['emoji']} {item['name']}",
                     font=("Segoe UI", 11), bg=BG, fg=fg, anchor="w"
                     ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            if owned:
                tk.Label(row, text="Куплено", font=("Segoe UI", 10),
                         bg=BG, fg="#aaaaaa").pack(side=tk.RIGHT)
            elif is_next:
                def buy(idx=i, window=shop):
                    self._buy_item(idx)
                    window.destroy()
                    self._open_shop()

                tk.Button(row, text=f"$ {item['price']}", font=("Segoe UI", 10),
                          command=buy,
                          state=tk.NORMAL if can_buy else tk.DISABLED
                          ).pack(side=tk.RIGHT)
            else:
                tk.Label(row, text=f"$ {item['price']}", font=("Segoe UI", 10),
                         bg=BG, fg=FG_DONE).pack(side=tk.RIGHT)

            tk.Frame(shop, bg="#eeeeee", height=1).pack(fill=tk.X, padx=16)

    def _buy_item(self, item_idx):
        item = ITEMS[item_idx]
        if self.balance < item["price"] or item_idx != self.items_owned:
            return
        self.balance -= item["price"]
        self.items_owned += 1
        save_balance(self.balance, self.items_owned)
        self.balance_label.config(text=f"$ {self.balance}")
        self._update_character()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClarityApp(root)
    root.mainloop()
