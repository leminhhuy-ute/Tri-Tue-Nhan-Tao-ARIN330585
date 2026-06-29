"""
DFS (Depth-First Search) - Máy Hút Bụi
Thuật toán tìm kiếm theo chiều sâu dùng stack, giới hạn độ sâu 30.
File standalone - chạy độc lập.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import re


# ============================================================
# XỬ LÝ MA TRẬN VÀ LOGIC MÁY HÚT BỤI
# ============================================================

def parse_matrix(text):
    """Phân tích text thành state: (robot_r, robot_c, dirt_grid_tuple)"""
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
    """Kiểm tra tất cả ô đã sạch chưa"""
    _, _, dirt_grid = state
    for row in dirt_grid:
        if 1 in row:
            return False
    return True


def get_neighbors(state):
    """Sinh các trạng thái con: Up, Down, Left, Right"""
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
    """h(n) = số ô bẩn + khoảng cách Manhattan tới ô bẩn gần nhất"""
    robot_r, robot_c, dirt_grid = state
    dirty = [(r, c) for r in range(len(dirt_grid)) for c in range(len(dirt_grid[0])) if dirt_grid[r][c] == 1]
    if not dirty:
        return 0
    min_dist = min(abs(robot_r - r) + abs(robot_c - c) for r, c in dirty)
    return len(dirty) + min_dist


# ============================================================
# ĐẶT TÊN NODE
# ============================================================

def number_to_label(n):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    while True:
        result = letters[n % 26] + result
        n = n // 26 - 1
        if n < 0:
            break
    return result


def state_to_matrix_text(state):
    robot_r, robot_c, dirt_grid = state
    lines = []
    for r in range(len(dirt_grid)):
        row_text = []
        for c in range(len(dirt_grid[0])):
            if r == robot_r and c == robot_c:
                row_text.append("R")
            else:
                row_text.append(str(dirt_grid[r][c]))
        lines.append(" ".join(row_text))
    return "\n".join(lines)


# ============================================================
# DFS VỚI TRACE (giới hạn độ sâu 30)
# ============================================================

def dfs_search(start_state, max_depth=30):
    """DFS dùng stack với giới hạn độ sâu. Trả về (path, trace, node_names)"""
    stack = [(start_state, [])]
    discovered = {start_state}
    node_names = {}
    node_counter = [0]

    def get_name(st):
        if st not in node_names:
            node_names[st] = number_to_label(node_counter[0])
            node_counter[0] += 1
        return node_names[st]

    get_name(start_state)
    trace = []
    step = 0

    while stack:
        current, path = stack.pop()
        step += 1
        current_name = get_name(current)

        if is_goal(current):
            trace.append({
                "step": step,
                "node": current_name,
                "frontier": "GOAL",
                "reached": ", ".join(node_names[s] for s in node_names if s in discovered)
            })
            return path, trace, node_names

        # Kiểm tra giới hạn độ sâu
        if len(path) >= max_depth:
            frontier_names = [get_name(s) for s, _ in stack]
            trace.append({
                "step": step,
                "node": current_name,
                "frontier": f"Cắt nhánh (depth={len(path)} >= {max_depth})\n[{', '.join(frontier_names)}]",
                "reached": ", ".join(node_names[s] for s in node_names if s in discovered)
            })
            continue

        children_added = []
        for action, next_state in get_neighbors(current):
            if next_state not in discovered:
                discovered.add(next_state)
                child_name = get_name(next_state)
                children_added.append((action, next_state, child_name))

        # DFS: đảo ngược để duyệt đúng thứ tự
        for action, next_state, _ in reversed(children_added):
            stack.append((next_state, path + [(action, next_state)]))

        frontier_items = [get_name(s) for s, _ in stack]
        frontier_text = "[" + ", ".join(frontier_items) + "]" if frontier_items else "[]"
        if children_added:
            frontier_text = "Thêm: " + ", ".join(n for _, _, n in children_added) + "\n" + frontier_text

        reached_list = [node_names[s] for s in node_names if s in discovered]
        trace.append({
            "step": step,
            "node": current_name,
            "frontier": frontier_text,
            "reached": ", ".join(reached_list)
        })

    return None, trace, node_names


# ============================================================
# GIAO DIỆN TKINTER
# ============================================================

class VacuumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy Hút Bụi - DFS (Depth-First Search)")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2d3436")
        self.root.resizable(False, False)

        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0
        self.node_names = {}

        self._build_gui()

    def _build_gui(self):
        title = tk.Label(self.root, text="MÁY HÚT BỤI — DFS (Depth-First Search)",
                         font=("Segoe UI", 16, "bold"), bg="#2d3436", fg="white")
        title.pack(pady=(10, 5))

        main_frame = tk.Frame(self.root, bg="#2d3436")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # ========== BÊN TRÁI ==========
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

        # ========== BÊN PHẢI ==========
        right_frame = tk.Frame(main_frame, bg="#2d3436")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        control_panel = tk.Frame(right_frame, bg="#dfe6e9", padx=10, pady=8)
        control_panel.pack(fill="x", pady=(0, 5))

        tk.Label(control_panel, text="Thuật toán:", font=("Segoe UI", 10, "bold"),
                 bg="#dfe6e9").grid(row=0, column=0, padx=(0, 5))

        self.algo_var = tk.StringVar(value="DFS (Depth-First Search)")
        algo_menu = ttk.Combobox(control_panel, textvariable=self.algo_var, state="disabled",
                                 values=["DFS (Depth-First Search)"], width=30, font=("Segoe UI", 10))
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

        self.path_label = tk.Label(right_frame, text="Đường đi: —",
                                   font=("Segoe UI", 10), bg="#2d3436", fg="#dfe6e9",
                                   anchor="w", wraplength=650, justify="left")
        self.path_label.pack(fill="x", pady=(0, 5))

        trace_panel = tk.LabelFrame(right_frame, text=" Bảng Trace: Step | Node | Frontier | Reached ",
                                    font=("Segoe UI", 10, "bold"), bg="#dfe6e9", fg="#2d3436", padx=5, pady=5)
        trace_panel.pack(fill="both", expand=True)

        self.trace_text = tk.Text(trace_panel, wrap="none", font=("Consolas", 9),
                                  bg="white", relief="solid", borderwidth=1)
        self.trace_text.configure(state="disabled")

        y_scroll = ttk.Scrollbar(trace_panel, orient="vertical", command=self.trace_text.yview)
        x_scroll = ttk.Scrollbar(trace_panel, orient="horizontal", command=self.trace_text.xview)
        self.trace_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.trace_text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        trace_panel.rowconfigure(0, weight=1)
        trace_panel.columnconfigure(0, weight=1)

    def draw_grid(self, state):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        robot_r, robot_c, dirt_grid = state
        rows, cols = len(dirt_grid), len(dirt_grid[0])
        for r in range(rows):
            for c in range(cols):
                if r == robot_r and c == robot_c:
                    text, bg_color, fg_color = "🤖", "white", "#2d3436"
                elif dirt_grid[r][c] == 1:
                    text, bg_color, fg_color = "1\nBẩn", "#ffab91", "#d63031"
                else:
                    text, bg_color, fg_color = "0\nSạch", "#c8e6c9", "#00b894"
                cell = tk.Label(self.grid_frame, text=text, width=6, height=3,
                                bg=bg_color, fg=fg_color, relief="solid", borderwidth=1,
                                font=("Segoe UI", 11, "bold"))
                cell.grid(row=r, column=c, padx=2, pady=2)

    def make_trace_table(self):
        step_w, node_w, frontier_w, reached_w = 6, 6, 50, 30
        border = "+" + "-" * (step_w + 2) + "+" + "-" * (node_w + 2) + "+" + "-" * (frontier_w + 2) + "+" + "-" * (reached_w + 2) + "+"

        def fmt(s, n, f, r):
            return "| " + s.ljust(step_w) + " | " + n.ljust(node_w) + " | " + f.ljust(frontier_w) + " | " + r.ljust(reached_w) + " |"

        lines = [border, fmt("Step", "Node", "Frontier", "Reached"), border]
        for row in self.trace:
            sl = [str(row["step"])]
            nl = [row["node"]]
            fl = str(row["frontier"]).split("\n")
            rl = self._wrap(row["reached"], reached_w)
            h = max(len(sl), len(nl), len(fl), len(rl))
            sl += [""] * (h - len(sl)); nl += [""] * (h - len(nl))
            fl += [""] * (h - len(fl)); rl += [""] * (h - len(rl))
            for i in range(h):
                lines.append(fmt(sl[i], nl[i], fl[i][:frontier_w], rl[i][:reached_w]))
            lines.append(border)
        return "\n".join(lines)

    def _wrap(self, text, width):
        text = str(text)
        if not text:
            return [""]
        result = []
        for line in text.split("\n"):
            while len(line) > width:
                cut = line.rfind(", ", 0, width)
                if cut <= 0: cut = width
                result.append(line[:cut])
                line = line[cut:].lstrip(", ")
            result.append(line)
        return result

    def show_trace(self):
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert("1.0", self.make_trace_table())
        self.trace_text.configure(state="disabled")

    def solve(self):
        try:
            text = self.matrix_input.get("1.0", tk.END)
            self.start_state = parse_matrix(text)
            self.solution, self.trace, self.node_names = dfs_search(self.start_state, max_depth=30)
            self.current_step = 0
            self.draw_grid(self.start_state)
            self.show_trace()

            if self.solution is None:
                self.status_label.config(text="DFS: Không tìm thấy lời giải!")
                self.path_label.config(text="Đường đi: Không có")
                return

            path_parts = []
            cur = self.start_state
            for action, ns in self.solution:
                path_parts.append(f"{self.node_names[cur]} —{action}→ {self.node_names[ns]}")
                cur = ns

            self.status_label.config(text=f"DFS: Tìm thấy lời giải gồm {len(self.solution)} bước! (max depth=30)")
            self.path_label.config(text="Đường đi: " + " | ".join(path_parts))
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
            label = self.node_names.get(state, "?")
            self.status_label.config(text=f"Bước {self.current_step}/{len(self.solution)}: {action} → Node {label}")
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
                label = self.node_names.get(state, "?")
                self.status_label.config(text=f"Bước {self.current_step}/{len(self.solution)}: {action} → Node {label}")

    def reset(self):
        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0
        self.node_names = {}
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.configure(state="disabled")
        self.status_label.config(text="Đã reset. Nhấn '▶ Chạy' để bắt đầu.")
        self.path_label.config(text="Đường đi: —")


if __name__ == "__main__":
    root = tk.Tk()
    app = VacuumApp(root)
    root.mainloop()
