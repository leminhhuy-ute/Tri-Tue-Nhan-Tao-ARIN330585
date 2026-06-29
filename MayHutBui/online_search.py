"""
Máy Hút Bụi - Online Search
"""

import tkinter as tk
from tkinter import messagebox, ttk
import re
import random
import time

# ============================================================
# XỬ LÝ MA TRẬN VÀ LOGIC MÁY HÚT BỤI (CÓ VẬT CẢN)
# ============================================================
def parse_matrix(text):
    lines = text.strip().splitlines()
    matrix = []
    robot_pos = None
    robot_count = 0

    for r, line in enumerate(lines):
        row = list(map(int, re.findall(r"\d+", line)))
        if not row: continue
        matrix.append(row)
        for c, value in enumerate(row):
            if value not in [0, 1, 2, 3, 4]:
                raise ValueError("Ma trận chỉ được dùng các số 0, 1, 2, 3, 4 (4=Vật cản)")
            if value in (2, 3):
                robot_pos = (r, c)
                robot_count += 1

    if not matrix: raise ValueError("Ma trận không được rỗng")
    if robot_count != 1: raise ValueError("Ma trận phải có đúng 1 robot")

    col_count = len(matrix[0])
    for row in matrix:
        if len(row) != col_count: raise ValueError("Các hàng phải bằng nhau")

    robot_r, robot_c = robot_pos
    grid = []
    for r in range(len(matrix)):
        grid_row = []
        for c in range(len(matrix[0])):
            if r == robot_r and c == robot_c:
                grid_row.append(1 if matrix[r][c] == 3 else 0)
            else:
                grid_row.append(matrix[r][c]) # 4 = vật cản, 1 = bẩn, 0 = sạch
        grid.append(tuple(grid_row))

    return (robot_r, robot_c, tuple(grid))

def is_goal(state):
    _, _, grid = state
    for row in grid:
        if 1 in row: return False
    return True

def get_neighbors(state):
    robot_r, robot_c, grid = state
    rows, cols = len(grid), len(grid[0])
    neighbors = []
    for action, dr, dc in [("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)]:
        new_r, new_c = robot_r + dr, robot_c + dc
        if 0 <= new_r < rows and 0 <= new_c < cols:
            if grid[new_r][new_c] != 4: # Không đi vào vật cản
                new_grid = [list(row) for row in grid]
                if new_grid[new_r][new_c] == 1:
                    new_grid[new_r][new_c] = 0 
                neighbors.append((action, (new_r, new_c, tuple(tuple(r) for r in new_grid))))
    return neighbors

def number_to_label(n):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = ""
    while True:
        res = letters[n % 26] + res
        n = n // 26 - 1
        if n < 0: break
    return res


def run_algorithm(start_state, app):
    app.append_trace("Online Search (LRTA*).")
    H = {}
    path = []
    current = start_state
    def h(st):
        d = [(r, c) for r in range(len(st[2])) for c in range(len(st[2][0])) if st[2][r][c] == 1]
        return len(d) + (min(abs(st[0]-dr)+abs(st[1]-dc) for dr,dc in d) if d else 0)

    for _ in range(30):
        if is_goal(current): break
        if current not in H: H[current] = h(current)
        neighbors = get_neighbors(current)
        if not neighbors: break
        
        best_f = 999
        best_n = None
        for act, st in neighbors:
            if st not in H: H[st] = h(st)
            if 1 + H[st] < best_f:
                best_f = 1 + H[st]
                best_n = (act, st)
                
        H[current] = max(H[current], best_f)
        app.append_trace(f"Cập nhật H({current[0]},{current[1]}) = {H[current]}")
        path.append((best_n[1], f"Đi {best_n[0]} | H={H[best_n[1]]}"))
        current = best_n[1]
    return path


# ============================================================
# GIAO DIỆN TKINTER
# ============================================================
class VacuumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy Hút Bụi - Online Search")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2d3436")
        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0
        self.node_names = {}
        self._build_gui()

    def _build_gui(self):
        tk.Label(self.root, text="MÁY HÚT BỤI — Online Search", font=("Segoe UI", 16, "bold"), bg="#2d3436", fg="white").pack(pady=(10, 5))
        main_frame = tk.Frame(self.root, bg="#2d3436")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_frame, bg="#2d3436", width=400)
        left_frame.pack(side="left", fill="both", padx=(0, 5))

        input_panel = tk.LabelFrame(left_frame, text=" Nhập ma trận (4x4) ", font=("Segoe UI", 10, "bold"), bg="#dfe6e9", padx=10, pady=10)
        input_panel.pack(fill="x", pady=(0, 5))
        tk.Label(input_panel, text="0=sạch  1=bẩn  2=robot(sạch)  3=robot(bẩn)  4=vật cản", font=("Segoe UI", 8), bg="#dfe6e9").pack(anchor="w")
        self.matrix_input = tk.Text(input_panel, width=30, height=6, font=("Consolas", 13))
        self.matrix_input.pack(pady=5)
        self.matrix_input.insert("1.0", "2 0 4 1\n0 4 0 0\n0 1 4 0\n0 0 1 0")

        grid_panel = tk.LabelFrame(left_frame, text=" Mô phỏng lưới ", font=("Segoe UI", 10, "bold"), bg="#dfe6e9", padx=10, pady=10)
        grid_panel.pack(fill="both", expand=True, pady=(0, 5))
        self.grid_frame = tk.Frame(grid_panel, bg="#dfe6e9")
        self.grid_frame.pack(expand=True)

        right_frame = tk.Frame(main_frame, bg="#2d3436")
        right_frame.pack(side="right", fill="both", expand=True)

        control_panel = tk.Frame(right_frame, bg="#dfe6e9", padx=10, pady=8)
        control_panel.pack(fill="x", pady=(0, 5))
        tk.Button(control_panel, text="▶ Chạy", bg="#00b894", fg="white", font=("Segoe UI", 9, "bold"), width=12, command=self.solve).grid(row=0, column=0, padx=3)
        tk.Button(control_panel, text="◀ Bước trước", bg="#0984e3", fg="white", font=("Segoe UI", 9, "bold"), width=12, command=self.prev_step).grid(row=0, column=1, padx=3)
        tk.Button(control_panel, text="Bước tiếp ▶", bg="#0984e3", fg="white", font=("Segoe UI", 9, "bold"), width=12, command=self.next_step).grid(row=0, column=2, padx=3)
        tk.Button(control_panel, text="↺ Reset", bg="#d63031", fg="white", font=("Segoe UI", 9, "bold"), width=12, command=self.reset).grid(row=0, column=3, padx=3)

        self.status_label = tk.Label(right_frame, text="Nhấn '▶ Chạy' để bắt đầu.", font=("Segoe UI", 11), bg="#2d3436", fg="#55efc4", anchor="w")
        self.status_label.pack(fill="x")
        self.path_label = tk.Label(right_frame, text="Log: —", font=("Segoe UI", 10), bg="#2d3436", fg="#dfe6e9", anchor="w", wraplength=650, justify="left")
        self.path_label.pack(fill="x", pady=5)

        trace_panel = tk.LabelFrame(right_frame, text=" Trace Log ", font=("Segoe UI", 10, "bold"), bg="#dfe6e9", padx=5, pady=5)
        trace_panel.pack(fill="both", expand=True)
        self.trace_text = tk.Text(trace_panel, wrap="none", font=("Consolas", 10), bg="white")
        self.trace_text.pack(fill="both", expand=True)

    def draw_grid(self, state):
        for w in self.grid_frame.winfo_children(): w.destroy()
        robot_r, robot_c, grid = state
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                val = grid[r][c]
                if r == robot_r and c == robot_c:
                    txt, bg, fg = "🤖", "white", "black"
                elif val == 4:
                    txt, bg, fg = "XXXX\nXXXX", "#636e72", "white"
                elif val == 1:
                    txt, bg, fg = "1\nBẩn", "#ffab91", "black"
                else:
                    txt, bg, fg = "0\nSạch", "#c8e6c9", "black"
                tk.Label(self.grid_frame, text=txt, width=6, height=3, bg=bg, fg=fg, relief="solid", bd=1, font=("Segoe UI", 11, "bold")).grid(row=r, column=c, padx=2, pady=2)

    def append_trace(self, text):
        self.trace_text.insert(tk.END, text + "\n")
        self.trace_text.see(tk.END)

    def solve(self):
        try:
            self.trace_text.delete("1.0", tk.END)
            self.start_state = parse_matrix(self.matrix_input.get("1.0", tk.END))
            self.draw_grid(self.start_state)
            self.solution = run_algorithm(self.start_state, self)
            self.current_step = 0
            self.status_label.config(text="Đã chạy xong. Dùng Bước tiếp/trước để xem.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def next_step(self):
        if self.solution and self.current_step < len(self.solution):
            self.current_step += 1
            if self.current_step <= len(self.solution):
                state, msg = self.solution[self.current_step - 1]
                self.draw_grid(state)
                self.path_label.config(text=f"Bước {self.current_step}: {msg}")

    def prev_step(self):
        if self.solution and self.current_step > 1:
            self.current_step -= 1
            state, msg = self.solution[self.current_step - 1]
            self.draw_grid(state)
            self.path_label.config(text=f"Bước {self.current_step}: {msg}")
        elif self.current_step == 1:
            self.current_step = 0
            self.draw_grid(self.start_state)
            self.path_label.config(text="Trạng thái ban đầu")

    def reset(self):
        self.trace_text.delete("1.0", tk.END)
        self.solution = []
        self.current_step = 0
        self.status_label.config(text="Nhấn '▶ Chạy' để bắt đầu.")
        self.path_label.config(text="Log: —")

if __name__ == "__main__":
    root = tk.Tk()
    app = VacuumApp(root)
    root.mainloop()
