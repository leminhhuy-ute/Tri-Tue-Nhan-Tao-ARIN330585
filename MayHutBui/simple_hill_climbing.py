"""
Simple Hill Climbing - Máy Hút Bụi
===================================
Thuật toán: Chọn láng giềng ĐẦU TIÊN có h thấp hơn trạng thái hiện tại.
Nếu không có láng giềng nào tốt hơn → dừng (kẹt tại local optimum).

Heuristic h(state) = số ô bẩn + khoảng cách Manhattan tới ô bẩn gần nhất
"""

import tkinter as tk
from tkinter import messagebox, ttk
import re

# ============================================================
# XỬ LÝ MA TRẬN VÀ TRẠNG THÁI
# ============================================================

def parse_matrix(text):
    """Đọc ma trận từ text, trả về state = (robot_r, robot_c, dirt_grid)"""
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
    """Sinh các trạng thái láng giềng (Up, Down, Left, Right)"""
    robot_r, robot_c, dirt_grid = state
    rows = len(dirt_grid)
    cols = len(dirt_grid[0])
    neighbors = []
    actions = [("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)]

    for action_name, dr, dc in actions:
        new_r, new_c = robot_r + dr, robot_c + dc
        if 0 <= new_r < rows and 0 <= new_c < cols:
            new_grid = [list(row) for row in dirt_grid]
            new_grid[new_r][new_c] = 0  # Robot dọn bụi khi đi tới
            new_grid_tuple = tuple(tuple(row) for row in new_grid)
            neighbors.append((action_name, (new_r, new_c, new_grid_tuple)))

    return neighbors


def heuristic(state):
    """h(state) = số ô bẩn + Manhattan tới ô bẩn gần nhất"""
    robot_r, robot_c, dirt_grid = state
    dirty = []
    for r in range(len(dirt_grid)):
        for c in range(len(dirt_grid[0])):
            if dirt_grid[r][c] == 1:
                dirty.append((r, c))

    if not dirty:
        return 0

    min_dist = min(abs(robot_r - r) + abs(robot_c - c) for r, c in dirty)
    return len(dirty) + min_dist


def state_to_text(state):
    """Chuyển state thành chuỗi hiển thị ma trận"""
    robot_r, robot_c, dirt_grid = state
    lines = []
    for r in range(len(dirt_grid)):
        row_text = []
        for c in range(len(dirt_grid[0])):
            if r == robot_r and c == robot_c:
                row_text.append("R")
            elif dirt_grid[r][c] == 1:
                row_text.append("1")
            else:
                row_text.append("0")
        lines.append(" ".join(row_text))
    return "\n".join(lines)


# ============================================================
# SIMPLE HILL CLIMBING
# ============================================================

MAX_STEPS = 100

def simple_hill_climbing(start_state):
    """
    Simple Hill Climbing:
    - Tại mỗi bước, duyệt láng giềng theo thứ tự
    - Chọn láng giềng ĐẦU TIÊN có h < h hiện tại
    - Dừng khi không có láng giềng nào tốt hơn hoặc đạt goal
    """
    current = start_state
    current_h = heuristic(current)
    path = []  # [(action, state, h_value)]
    trace = []  # Bảng trace

    trace.append({
        "step": 0,
        "state": state_to_text(current),
        "h": current_h,
        "action": "Khởi tạo",
        "neighbors": "",
        "note": "Trạng thái ban đầu"
    })

    for step in range(1, MAX_STEPS + 1):
        if is_goal(current):
            trace[-1]["note"] = "✓ GOAL - Tất cả ô đã sạch!"
            break

        neighbors = get_neighbors(current)
        neighbor_info = []
        chosen = None

        for action, neighbor in neighbors:
            h_val = heuristic(neighbor)
            neighbor_info.append(f"{action}: h={h_val}")
            if h_val < current_h and chosen is None:
                chosen = (action, neighbor, h_val)

        neighbors_text = " | ".join(neighbor_info)

        if chosen is None:
            trace[-1]["note"] = "✗ Kẹt! Không có láng giềng nào tốt hơn (Local Optimum)"
            break

        action, next_state, next_h = chosen
        path.append((action, next_state))
        current = next_state
        current_h = next_h

        trace.append({
            "step": step,
            "state": state_to_text(current),
            "h": current_h,
            "action": action,
            "neighbors": neighbors_text,
            "note": f"Chọn {action} (h={next_h}) - láng giềng đầu tiên tốt hơn"
        })

    return path, trace


# ============================================================
# GIAO DIỆN TKINTER
# ============================================================

class SimpleHillClimbingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Hill Climbing - Máy Hút Bụi")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2d3436")

        self.start_state = None
        self.path = []
        self.trace = []
        self.current_step = 0

        self._build_gui()

    def _build_gui(self):
        # ====== TIÊU ĐỀ ======
        title = tk.Label(
            self.root, text="🧹 SIMPLE HILL CLIMBING - MÁY HÚT BỤI",
            font=("Segoe UI", 16, "bold"), bg="#2d3436", fg="white"
        )
        title.pack(pady=(10, 5))

        subtitle = tk.Label(
            self.root, text="Chọn láng giềng ĐẦU TIÊN có h thấp hơn",
            font=("Segoe UI", 10, "italic"), bg="#2d3436", fg="#b2bec3"
        )
        subtitle.pack()

        # ====== KHUNG CHÍNH ======
        main_frame = tk.Frame(self.root, bg="#2d3436")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # === BÊN TRÁI: Input + Grid ===
        left_frame = tk.Frame(main_frame, bg="#dfe6e9", relief="ridge", bd=2)
        left_frame.pack(side="left", fill="both", padx=(0, 5), pady=5)

        # Input ma trận
        input_label = tk.Label(left_frame, text="Nhập ma trận (0=sạch, 1=bẩn, 2=robot, 3=robot+bẩn):",
                               font=("Segoe UI", 9, "bold"), bg="#dfe6e9")
        input_label.pack(padx=10, pady=(10, 2), anchor="w")

        self.matrix_input = tk.Text(left_frame, width=25, height=5, font=("Consolas", 12),
                                     relief="solid", bd=1)
        self.matrix_input.insert("1.0", "3 0 1\n0 1 0\n1 0 0")
        self.matrix_input.pack(padx=10, pady=5)

        # Buttons
        btn_frame = tk.Frame(left_frame, bg="#dfe6e9")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="▶ Chạy", width=10, bg="#00b894", fg="white",
                  font=("Segoe UI", 10, "bold"), command=self.solve
                  ).grid(row=0, column=0, padx=3, pady=2)
        tk.Button(btn_frame, text="◀ Bước trước", width=10, bg="#636e72", fg="white",
                  font=("Segoe UI", 10), command=self.prev_step
                  ).grid(row=0, column=1, padx=3, pady=2)
        tk.Button(btn_frame, text="Bước tiếp ▶", width=10, bg="#636e72", fg="white",
                  font=("Segoe UI", 10), command=self.next_step
                  ).grid(row=0, column=2, padx=3, pady=2)
        tk.Button(btn_frame, text="↺ Reset", width=10, bg="#d63031", fg="white",
                  font=("Segoe UI", 10, "bold"), command=self.reset
                  ).grid(row=0, column=3, padx=3, pady=2)

        # Status
        self.status_label = tk.Label(left_frame, text="Nhấn 'Chạy' để bắt đầu",
                                      font=("Segoe UI", 10), bg="#dfe6e9", fg="#2d3436",
                                      wraplength=350)
        self.status_label.pack(padx=10, pady=5)

        # Grid visualization
        grid_label = tk.Label(left_frame, text="Mô phỏng lưới:", font=("Segoe UI", 9, "bold"),
                              bg="#dfe6e9")
        grid_label.pack(padx=10, pady=(5, 2), anchor="w")

        self.grid_frame = tk.Frame(left_frame, bg="#dfe6e9")
        self.grid_frame.pack(padx=10, pady=5, expand=True)

        # Heuristic display
        self.h_label = tk.Label(left_frame, text="h(state) = --",
                                 font=("Segoe UI", 12, "bold"), bg="#dfe6e9", fg="#6c5ce7")
        self.h_label.pack(padx=10, pady=(0, 10))

        # === BÊN PHẢI: Trace ===
        right_frame = tk.Frame(main_frame, bg="#dfe6e9", relief="ridge", bd=2)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)

        trace_label = tk.Label(right_frame, text="Bảng Trace - Simple Hill Climbing",
                               font=("Segoe UI", 11, "bold"), bg="#dfe6e9")
        trace_label.pack(padx=10, pady=(10, 5), anchor="w")

        trace_container = tk.Frame(right_frame, bg="#dfe6e9")
        trace_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.trace_text = tk.Text(trace_container, wrap="none", font=("Consolas", 9),
                                   bg="white", relief="solid", bd=1)
        self.trace_text.configure(state="disabled")

        y_scroll = ttk.Scrollbar(trace_container, orient="vertical", command=self.trace_text.yview)
        x_scroll = ttk.Scrollbar(trace_container, orient="horizontal", command=self.trace_text.xview)
        self.trace_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.trace_text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        trace_container.rowconfigure(0, weight=1)
        trace_container.columnconfigure(0, weight=1)

    # ========================================================
    # VẼ LƯỚI MÔ PHỎNG
    # ========================================================

    def draw_grid(self, state):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        robot_r, robot_c, dirt_grid = state
        for r in range(len(dirt_grid)):
            for c in range(len(dirt_grid[0])):
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

                cell = tk.Label(self.grid_frame, text=text, width=8, height=3,
                                bg=bg_color, fg=fg_color, relief="solid", bd=1,
                                font=("Segoe UI", 12, "bold"))
                cell.grid(row=r, column=c, padx=2, pady=2)

        self.h_label.config(text=f"h(state) = {heuristic(state)}")

    # ========================================================
    # TẠO BẢNG TRACE
    # ========================================================

    def make_trace_text(self):
        if not self.trace:
            return ""

        step_w = 6
        h_w = 6
        action_w = 12
        neighbors_w = 50
        note_w = 45

        border = f"+{'-'*(step_w+2)}+{'-'*(h_w+2)}+{'-'*(action_w+2)}+{'-'*(neighbors_w+2)}+{'-'*(note_w+2)}+"
        header = (f"| {'Bước'.ljust(step_w)} | {'h(n)'.ljust(h_w)} | {'Hành động'.ljust(action_w)} "
                  f"| {'Láng giềng (h)'.ljust(neighbors_w)} | {'Ghi chú'.ljust(note_w)} |")

        lines = [border, header, border]

        for row in self.trace:
            step_str = str(row['step']).ljust(step_w)
            h_str = str(row['h']).ljust(h_w)
            action_str = row['action'].ljust(action_w)

            # Wrap neighbors
            nb_text = row['neighbors'] if row['neighbors'] else "--"
            note_text = row['note']

            nb_lines = self._wrap(nb_text, neighbors_w)
            note_lines = self._wrap(note_text, note_w)
            max_lines = max(len(nb_lines), len(note_lines))

            while len(nb_lines) < max_lines:
                nb_lines.append("")
            while len(note_lines) < max_lines:
                note_lines.append("")

            for i in range(max_lines):
                if i == 0:
                    lines.append(
                        f"| {step_str} | {h_str} | {action_str} "
                        f"| {nb_lines[i].ljust(neighbors_w)} | {note_lines[i].ljust(note_w)} |"
                    )
                else:
                    lines.append(
                        f"| {''.ljust(step_w)} | {''.ljust(h_w)} | {''.ljust(action_w)} "
                        f"| {nb_lines[i].ljust(neighbors_w)} | {note_lines[i].ljust(note_w)} |"
                    )

            lines.append(border)

        return "\n".join(lines)

    def _wrap(self, text, width):
        if not text:
            return [""]
        result = []
        for line in text.splitlines():
            while len(line) > width:
                cut = line.rfind(" ", 0, width)
                if cut <= 0:
                    cut = line.rfind("|", 0, width)
                if cut <= 0:
                    cut = width
                result.append(line[:cut].rstrip())
                line = line[cut:].lstrip()
            result.append(line)
        return result

    def show_trace(self):
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert("1.0", self.make_trace_text())
        self.trace_text.configure(state="disabled")

    # ========================================================
    # CHẠY THUẬT TOÁN
    # ========================================================

    def solve(self):
        try:
            text = self.matrix_input.get("1.0", tk.END)
            self.start_state = parse_matrix(text)
            self.path, self.trace = simple_hill_climbing(self.start_state)
            self.current_step = 0

            self.draw_grid(self.start_state)
            self.show_trace()

            n_steps = len(self.path)
            found = is_goal(self.path[-1][1]) if self.path else is_goal(self.start_state)

            if found:
                self.status_label.config(
                    text=f"✓ Tìm thấy lời giải sau {n_steps} bước!",
                    fg="#00b894"
                )
            else:
                self.status_label.config(
                    text=f"✗ Kẹt tại local optimum sau {n_steps} bước",
                    fg="#d63031"
                )

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ========================================================
    # ĐIỀU HƯỚNG BƯỚC
    # ========================================================

    def next_step(self):
        if not self.path:
            messagebox.showwarning("Thông báo", "Chạy thuật toán trước!")
            return
        if self.current_step < len(self.path):
            action, state = self.path[self.current_step]
            self.current_step += 1
            self.draw_grid(state)
            h = heuristic(state)
            self.status_label.config(
                text=f"Bước {self.current_step}/{len(self.path)}: {action} → h={h}",
                fg="#2d3436"
            )
        else:
            self.status_label.config(text="Đã hết các bước.", fg="#636e72")

    def prev_step(self):
        if not self.path:
            messagebox.showwarning("Thông báo", "Chạy thuật toán trước!")
            return
        if self.current_step > 0:
            self.current_step -= 1
            if self.current_step == 0:
                self.draw_grid(self.start_state)
                self.status_label.config(text="Bước 0: Trạng thái ban đầu", fg="#2d3436")
            else:
                action, state = self.path[self.current_step - 1]
                self.draw_grid(state)
                h = heuristic(state)
                self.status_label.config(
                    text=f"Bước {self.current_step}/{len(self.path)}: {action} → h={h}",
                    fg="#2d3436"
                )

    def reset(self):
        self.start_state = None
        self.path = []
        self.trace = []
        self.current_step = 0

        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.configure(state="disabled")

        self.status_label.config(text="Đã reset. Nhấn 'Chạy' để bắt đầu.", fg="#2d3436")
        self.h_label.config(text="h(state) = --")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    root.after(1000, lambda: root.attributes("-topmost", False))
    app = SimpleHillClimbingApp(root)
    root.mainloop()
