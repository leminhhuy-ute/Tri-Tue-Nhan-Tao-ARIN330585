"""
Random-Restart Hill Climbing - Máy Hút Bụi
Leo đồi dốc nhất với khởi động lại ngẫu nhiên.
File standalone - chạy độc lập.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import re
import random

# ============================================================
# XỬ LÝ MA TRẬN VÀ LOGIC MÁY HÚT BỤI
# ============================================================

def parse_matrix(text):
    lines = text.strip().splitlines()
    matrix = []
    robot_pos = None
    robot_count = 0

    for r, line in enumerate(lines):
        row = list(map(int, re.findall(r"\d+", line)))
        if not row:
            continue
        matrix.append(row)
        for c, value in enumerate(row):
            if value not in [0, 1, 2, 3]:
                raise ValueError("Ma trận chỉ được dùng các số 0, 1, 2, 3")
            if value in (2, 3):
                robot_pos = (r, c)
                robot_count += 1

    if not matrix:
        raise ValueError("Ma trận không được rỗng")
    if robot_count != 1:
        raise ValueError("Ma trận phải có đúng 1 robot (số 2 hoặc 3)")

    col_count = len(matrix[0])
    for row in matrix:
        if len(row) != col_count:
            raise ValueError("Các hàng phải có cùng số cột")

    robot_r, robot_c = robot_pos
    dirt_grid = []
    for r in range(len(matrix)):
        dirt_row = []
        for c in range(len(matrix[0])):
            if r == robot_r and c == robot_c:
                dirt_row.append(1 if matrix[r][c] == 3 else 0)
            elif matrix[r][c] == 1:
                dirt_row.append(1)
            else:
                dirt_row.append(0)
        dirt_grid.append(tuple(dirt_row))

    return (robot_r, robot_c, tuple(dirt_grid))

def is_goal(state):
    _, _, dirt_grid = state
    for row in dirt_grid:
        if 1 in row:
            return False
    return True

def get_neighbors(state):
    robot_r, robot_c, dirt_grid = state
    rows = len(dirt_grid)
    cols = len(dirt_grid[0])
    neighbors = []

    for action, dr, dc in [("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)]:
        new_r, new_c = robot_r + dr, robot_c + dc
        if 0 <= new_r < rows and 0 <= new_c < cols:
            new_grid = [list(row) for row in dirt_grid]
            new_grid[new_r][new_c] = 0
            new_state = (new_r, new_c, tuple(tuple(r) for r in new_grid))
            neighbors.append((action, new_state))

    return neighbors

def heuristic(state):
    robot_r, robot_c, dirt_grid = state
    dirty = [(r, c) for r in range(len(dirt_grid)) for c in range(len(dirt_grid[0])) if dirt_grid[r][c] == 1]
    if not dirty:
        return 0
    min_dist = min(abs(robot_r - r) + abs(robot_c - c) for r, c in dirty)
    return len(dirty) + min_dist

# ============================================================
# SEARCH VỚI TRACE
# ============================================================

def generate_random_state(rows, cols):
    robot_r = random.randint(0, rows-1)
    robot_c = random.randint(0, cols-1)
    dirt_grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            # 30% chance of being dirty, except robot position
            if r == robot_r and c == robot_c:
                row.append(0)
            else:
                row.append(1 if random.random() < 0.3 else 0)
        dirt_grid.append(tuple(row))
    return (robot_r, robot_c, tuple(dirt_grid))

def random_restart_hill_climbing(start_state):
    trace = []
    path = []
    
    rows = len(start_state[2])
    cols = len(start_state[2][0])
    
    global_step = 0
    max_restarts = 10
    
    for restart in range(max_restarts + 1):
        if restart == 0:
            current = start_state
            trace.append(f"--- KHỞI ĐẦU TỪ TRẠNG THÁI GỐC (h={heuristic(current)}) ---")
        else:
            current = generate_random_state(rows, cols)
            trace.append(f"--- RESTART LẦN {restart}: Random State (h={heuristic(current)}) ---")
            path.append((f"Restart_{restart}", current))
            
        step = 0
        while step < 100:
            step += 1
            global_step += 1
            
            if is_goal(current):
                trace.append(f"Bước {global_step}: ĐÃ TÌM THẤY LỜI GIẢI!")
                return path, trace
                
            current_h = heuristic(current)
            neighbors = get_neighbors(current)
            
            best_neighbor = None
            best_h = current_h
            
            for action, next_state in neighbors:
                h = heuristic(next_state)
                if h < best_h:
                    best_h = h
                    best_neighbor = (action, next_state)
                    
            if best_neighbor is None:
                trace.append(f"Bước {global_step}: Bị kẹt tại local minimum (h={current_h}).")
                break # Break out of inner loop to restart
                
            action, next_state = best_neighbor
            trace.append(f"Bước {global_step}: Chọn '{action}' có h={best_h} (h_cũ={current_h}).")
            path.append((action, next_state))
            current = next_state
            
    trace.append(f"Đã thử {max_restarts} lần khởi động lại nhưng không tìm được lời giải.")
    return None, trace

# ============================================================
# GIAO DIỆN TKINTER
# ============================================================

class VacuumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy Hút Bụi - Random-Restart Hill Climbing")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2d3436")
        self.root.resizable(False, False)

        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0

        self._build_gui()

    def _build_gui(self):
        title = tk.Label(self.root, text="MÁY HÚT BỤI — Random-Restart Hill Climbing",
                         font=("Segoe UI", 16, "bold"), bg="#2d3436", fg="white")
        title.pack(pady=(10, 5))

        main_frame = tk.Frame(self.root, bg="#2d3436")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_frame, bg="#2d3436", width=400)
        left_frame.pack(side="left", fill="both", padx=(0, 5))

        input_panel = tk.LabelFrame(left_frame, text=" Nhập ma trận ", font=("Segoe UI", 10, "bold"),
                                    bg="#dfe6e9", fg="#2d3436", padx=10, pady=10)
        input_panel.pack(fill="x", pady=(0, 5))

        tk.Label(input_panel, text="0=sạch  1=bẩn  2=robot(sạch)  3=robot(bẩn)",
                 font=("Segoe UI", 8), bg="#dfe6e9", fg="#636e72").pack(anchor="w")

        self.matrix_input = tk.Text(input_panel, width=30, height=5, font=("Consolas", 13),
                                    relief="solid", borderwidth=1)
        self.matrix_input.pack(pady=(5, 0))
        self.matrix_input.insert("1.0", "3 0 1\n0 1 0\n1 0 0")

        grid_panel = tk.LabelFrame(left_frame, text=" Mô phỏng lưới ", font=("Segoe UI", 10, "bold"),
                                   bg="#dfe6e9", fg="#2d3436", padx=10, pady=10)
        grid_panel.pack(fill="both", expand=True, pady=(0, 5))

        self.grid_frame = tk.Frame(grid_panel, bg="#dfe6e9")
        self.grid_frame.pack(expand=True)

        right_frame = tk.Frame(main_frame, bg="#2d3436")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        control_panel = tk.Frame(right_frame, bg="#dfe6e9", padx=10, pady=8)
        control_panel.pack(fill="x", pady=(0, 5))

        tk.Label(control_panel, text="Thuật toán:", font=("Segoe UI", 10, "bold"),
                 bg="#dfe6e9").grid(row=0, column=0, padx=(0, 5))

        self.algo_var = tk.StringVar(value="Random-Restart Hill Climbing")
        algo_menu = ttk.Combobox(control_panel, textvariable=self.algo_var, state="disabled",
                                 values=["Random-Restart Hill Climbing"], width=25, font=("Segoe UI", 10))
        algo_menu.grid(row=0, column=1, padx=5)

        btn_style = {"font": ("Segoe UI", 9, "bold"), "width": 14, "cursor": "hand2", "relief": "flat"}

        tk.Button(control_panel, text="▶ Chạy", bg="#00b894", fg="white",
                  command=self.solve, **btn_style).grid(row=0, column=2, padx=3)
        tk.Button(control_panel, text="◀ Bước trước", bg="#0984e3", fg="white",
                  command=self.prev_step, **btn_style).grid(row=0, column=3, padx=3)
        tk.Button(control_panel, text="Bước tiếp ▶", bg="#0984e3", fg="white",
                  command=self.next_step, **btn_style).grid(row=0, column=4, padx=3)
        tk.Button(control_panel, text="↺ Reset", bg="#d63031", fg="white",
                  command=self.reset, **btn_style).grid(row=0, column=5, padx=3)

        self.status_label = tk.Label(right_frame, text="Nhấn '▶ Chạy' để bắt đầu.",
                                     font=("Segoe UI", 11), bg="#2d3436", fg="#55efc4", anchor="w")
        self.status_label.pack(fill="x", pady=(0, 2))

        trace_panel = tk.LabelFrame(right_frame, text=" Bảng Trace Log ",
                                    font=("Segoe UI", 10, "bold"), bg="#dfe6e9", fg="#2d3436", padx=5, pady=5)
        trace_panel.pack(fill="both", expand=True)

        self.trace_text = tk.Text(trace_panel, wrap="word", font=("Consolas", 11),
                                  bg="#0f172a", fg="#dbeafe", relief="solid", borderwidth=1, padx=10, pady=10)
        self.trace_text.configure(state="disabled")

        y_scroll = ttk.Scrollbar(trace_panel, orient="vertical", command=self.trace_text.yview)
        self.trace_text.configure(yscrollcommand=y_scroll.set)

        self.trace_text.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

    def draw_grid(self, state):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        robot_r, robot_c, dirt_grid = state
        rows = len(dirt_grid)
        cols = len(dirt_grid[0])

        for r in range(rows):
            for c in range(cols):
                if r == robot_r and c == robot_c:
                    text = "🤖"
                    bg_color = "white"
                    fg_color = "#2d3436"
                elif dirt_grid[r][c] == 1:
                    text = "1\nBẩn"
                    bg_color = "#ffab91"
                    fg_color = "#d63031"
                else:
                    text = "0\nSạch"
                    bg_color = "#c8e6c9"
                    fg_color = "#00b894"

                cell = tk.Label(self.grid_frame, text=text, width=6, height=3,
                                bg=bg_color, fg=fg_color, relief="solid", borderwidth=1,
                                font=("Segoe UI", 11, "bold"))
                cell.grid(row=r, column=c, padx=2, pady=2)

    def show_trace(self):
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        for line in self.trace:
            self.trace_text.insert(tk.END, line + "\n")
        self.trace_text.configure(state="disabled")

    def solve(self):
        try:
            text = self.matrix_input.get("1.0", tk.END)
            self.start_state = parse_matrix(text)
            self.solution, self.trace = random_restart_hill_climbing(self.start_state)
            self.current_step = 0
            self.draw_grid(self.start_state)
            self.show_trace()

            if self.solution is None:
                self.status_label.config(text="Random-Restart: Thất bại sau 10 lần khởi động lại!")
                return

            self.status_label.config(text=f"Random-Restart: Tìm thấy lời giải sau {len(self.solution)} bước!")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def next_step(self):
        if not self.solution:
            messagebox.showwarning("Thông báo", "Hãy chạy thuật toán trước!")
            return
        if self.current_step < len(self.solution):
            action, state = self.solution[self.current_step]
            self.current_step += 1
            self.draw_grid(state)
            self.status_label.config(text=f"Bước {self.current_step}/{len(self.solution)}: {action}")
        else:
            self.status_label.config(text="✅ Hoàn thành! Tất cả ô đã sạch.")

    def prev_step(self):
        if not self.solution:
            messagebox.showwarning("Thông báo", "Hãy chạy thuật toán trước!")
            return
        if self.current_step > 0:
            self.current_step -= 1
            if self.current_step == 0:
                self.draw_grid(self.start_state)
                self.status_label.config(text="Bước 0: Trạng thái ban đầu")
            else:
                action, state = self.solution[self.current_step - 1]
                self.draw_grid(state)
                self.status_label.config(text=f"Bước {self.current_step}/{len(self.solution)}: {action}")

    def reset(self):
        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.configure(state="disabled")
        self.status_label.config(text="Đã reset. Nhấn '▶ Chạy' để bắt đầu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VacuumApp(root)
    root.mainloop()
