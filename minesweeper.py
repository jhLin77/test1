import tkinter as tk
from tkinter import messagebox
import random
import time

class Minesweeper:
    def __init__(self, root, rows=9, cols=9, mines=10, cell_size=32):
        self.root = root
        self.root.title("扫雷 - Minesweeper")

        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cell_size = cell_size

        self.first_click = True
        self.game_over = False
        self.start_time = None
        self.timer_job = None

        self.flags_left = mines

        self._build_ui()
        self._new_game()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(padx=10, pady=10, fill="x")

        self.info_var = tk.StringVar(value="准备开始")
        self.flags_var = tk.StringVar(value=f"🚩 {self.flags_left}")
        self.time_var = tk.StringVar(value="⏱ 0")

        tk.Label(top, textvariable=self.flags_var, font=("Arial", 12)).pack(side="left")
        tk.Label(top, textvariable=self.time_var, font=("Arial", 12)).pack(side="right")
        tk.Label(top, textvariable=self.info_var, font=("Arial", 12)).pack(side="top")

        btns = tk.Frame(self.root)
        btns.pack(padx=10, pady=(0, 10), fill="x")

        tk.Button(btns, text="新游戏", command=self._new_game).pack(side="left")

        # 难度选择
        self.level_var = tk.StringVar(value="初级 9x9 10雷")
        levels = [
            ("初级 9x9 10雷", (9, 9, 10)),
            ("中级 16x16 40雷", (16, 16, 40)),
            ("高级 16x30 99雷", (16, 30, 99)),
        ]
        self.level_map = {name: cfg for name, cfg in levels}
        opt = tk.OptionMenu(btns, self.level_var, *[n for n, _ in levels], command=self._change_level)
        opt.pack(side="right")

        self.board_frame = tk.Frame(self.root, bd=2, relief="groove")
        self.board_frame.pack(padx=10, pady=10)

    def _change_level(self, _):
        self._new_game()

    def _new_game(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.first_click = True
        self.game_over = False
        self.start_time = None

        name = self.level_var.get()
        self.rows, self.cols, self.mines = self.level_map.get(name, (9, 9, 10))
        self.flags_left = self.mines
        self.flags_var.set(f"🚩 {self.flags_left}")
        self.time_var.set("⏱ 0")
        self.info_var.set("左键翻开 / 右键插旗")

        # 清空旧棋盘
        for w in self.board_frame.winfo_children():
            w.destroy()

        # 数据结构
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]  # -1 表示雷
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # 先不放雷，等第一次点击再放（保证第一次点不会死）
        for r in range(self.rows):
            for c in range(self.cols):
                b = tk.Button(
                    self.board_frame,
                    width=2,
                    height=1,
                    font=("Consolas", 12, "bold"),
                    relief="raised"
                )
                b.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

                b.bind("<Button-1>", lambda e, rr=r, cc=c: self._on_left_click(rr, cc))
                b.bind("<Button-3>", lambda e, rr=r, cc=c: self._on_right_click(rr, cc))
                # macOS 触控板右键可能触发 Button-2
                b.bind("<Button-2>", lambda e, rr=r, cc=c: self._on_right_click(rr, cc))

                self.buttons[r][c] = b

        # 让格子随窗口缩放（可选）
        for r in range(self.rows):
            self.board_frame.grid_rowconfigure(r, weight=1)
        for c in range(self.cols):
            self.board_frame.grid_columnconfigure(c, weight=1)

    def _start_timer(self):
        self.start_time = time.time()
        self._tick()

    def _tick(self):
        if self.game_over or self.start_time is None:
            return
        elapsed = int(time.time() - self.start_time)
        self.time_var.set(f"⏱ {elapsed}")
        self.timer_job = self.root.after(200, self._tick)

    def _place_mines(self, safe_r, safe_c):
        # 把第一次点击以及周围 8 格都设为“安全区”，避免一上来就被迫猜
        safe = set()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = safe_r + dr, safe_c + dc
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    safe.add((rr, cc))

        positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) not in safe]
        random.shuffle(positions)
        mines_pos = positions[:self.mines]

        for r, c in mines_pos:
            self.grid[r][c] = -1

        # 计算数字
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    continue
                self.grid[r][c] = self._count_adjacent_mines(r, c)

    def _count_adjacent_mines(self, r, c):
        cnt = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.rows and 0 <= cc < self.cols and self.grid[rr][cc] == -1:
                    cnt += 1
        return cnt

    def _on_left_click(self, r, c):
        if self.game_over:
            return
        if self.flagged[r][c]:
            return

        if self.first_click:
            self.first_click = False
            self._place_mines(r, c)
            self._start_timer()

        if self.grid[r][c] == -1:
            self._reveal_mine(r, c)
            self._lose()
            return

        self._reveal_cell(r, c)
        self._check_win()

    def _on_right_click(self, r, c):
        if self.game_over:
            return
        if self.revealed[r][c]:
            return

        if not self.flagged[r][c]:
            if self.flags_left <= 0:
                return
            self.flagged[r][c] = True
            self.flags_left -= 1
            self.buttons[r][c].config(text="🚩", fg="red")
        else:
            self.flagged[r][c] = False
            self.flags_left += 1
            self.buttons[r][c].config(text="", fg="black")

        self.flags_var.set(f"🚩 {self.flags_left}")
        self._check_win()

    def _reveal_cell(self, r, c):
        if self.revealed[r][c] or self.flagged[r][c]:
            return

        self.revealed[r][c] = True
        val = self.grid[r][c]
        b = self.buttons[r][c]
        b.config(relief="sunken", state="disabled", disabledforeground="black")

        if val == 0:
            b.config(text="")
            # 扩散
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        if not self.revealed[rr][cc]:
                            self._reveal_cell(rr, cc)
        else:
            b.config(text=str(val))
            # 简单颜色映射
            color_map = {
                1: "blue", 2: "green", 3: "red", 4: "navy",
                5: "maroon", 6: "teal", 7: "black", 8: "gray"
            }
            b.config(disabledforeground=color_map.get(val, "black"))

    def _reveal_mine(self, r, c):
        b = self.buttons[r][c]
        b.config(text="💣", bg="#ffcccc")

    def _reveal_all(self, show_mines=True):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.revealed[r][c]:
                    continue
                if self.grid[r][c] == -1 and show_mines:
                    self.buttons[r][c].config(text="💣", relief="sunken", state="disabled")
                elif self.grid[r][c] != -1:
                    # 只翻开非雷（用于胜利时）
                    if show_mines is False:
                        self._reveal_cell(r, c)

    def _lose(self):
        self.game_over = True
        self.info_var.set("💥 你踩雷了！")
        self._reveal_all(show_mines=True)
        messagebox.showinfo("游戏结束", "你踩雷了！点“新游戏”再来一局。")

    def _check_win(self):
        if self.game_over:
            return

        # 胜利条件：所有非雷都翻开
        revealed_count = sum(self.revealed[r][c] for r in range(self.rows) for c in range(self.cols))
        total_cells = self.rows * self.cols
        if revealed_count == total_cells - self.mines:
            self._win()

    def _win(self):
        self.game_over = True
        self.info_var.set("🎉 胜利！")
        # 自动插旗所有雷
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    self.buttons[r][c].config(text="🚩", fg="red", relief="sunken", state="disabled")
        messagebox.showinfo("恭喜", "你赢了！")

def main():
    root = tk.Tk()
    Minesweeper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
