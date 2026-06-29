"""
Tô Màu Bản Đồ - Định nghĩa CSP (Constraint Satisfaction Problem)
Bài toán tô màu bản đồ Úc với 7 vùng và 4 màu.
Hiển thị công thức CSP: Biến, Miền giá trị, Ràng buộc.
Sử dụng phương pháp vét cạn để tìm lời giải hợp lệ.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import random
import itertools

# ========================== CẤU HÌNH ==========================

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
BG_COLOR = "#ecf0f1"
PANEL_COLOR = "#ffffff"
TITLE_FONT = ("Segoe UI", 16, "bold")
HEADER_FONT = ("Segoe UI", 12, "bold")
NORMAL_FONT = ("Segoe UI", 10)
SMALL_FONT = ("Segoe UI", 9)

# Màu sắc cho tô bản đồ
COLORS = {
    "Đỏ": "#e74c3c",
    "Xanh dương": "#3498db",
    "Xanh lá": "#2ecc71",
    "Vàng": "#f1c40f"
}
COLOR_NAMES = list(COLORS.keys())
UNCOLORED = "#bdc3c7"

# Các vùng của Úc (biến trong CSP)
REGIONS = ["Linh Xuân", "Bình Chiểu", "Linh Trung", "Tam Bình", "Tam Phú", 
           "H.B.Phước", "H.B.Chánh", "Linh Đông", "Linh Tây", "Linh Chiểu", 
           "Trường Thọ", "Bình Thọ"]

ADJACENCY = [
    ("Bình Chiểu", "H.B.Phước"), ("Bình Chiểu", "Tam Bình"), ("Bình Chiểu", "Linh Xuân"),
    ("Linh Xuân", "Linh Trung"),
    ("H.B.Phước", "Tam Bình"), ("H.B.Phước", "Tam Phú"), ("H.B.Phước", "H.B.Chánh"),
    ("Tam Bình", "Linh Trung"), ("Tam Bình", "Linh Tây"), ("Tam Bình", "Tam Phú"),
    ("Tam Phú", "H.B.Chánh"), ("Tam Phú", "Linh Đông"), ("Tam Phú", "Linh Tây"),
    ("Linh Tây", "Linh Trung"), ("Linh Tây", "Linh Chiểu"), ("Linh Tây", "Trường Thọ"), ("Linh Tây", "Linh Đông"),
    ("Linh Trung", "Linh Chiểu"),
    ("H.B.Chánh", "Linh Đông"),
    ("Linh Đông", "Trường Thọ"),
    ("Linh Chiểu", "Trường Thọ"), ("Linh Chiểu", "Bình Thọ"),
    ("Trường Thọ", "Bình Thọ")
]

POSITIONS = {
    "Bình Chiểu": (220, 100),
    "H.B.Phước": (80, 200),
    "Tam Bình": (280, 200),
    "Linh Xuân": (480, 100),
    "Linh Trung": (450, 230),
    "Tam Phú": (180, 300),
    "Linh Tây": (340, 300),
    "Linh Chiểu": (480, 350),
    "H.B.Chánh": (120, 420),
    "Linh Đông": (260, 420),
    "Trường Thọ": (380, 480),
    "Bình Thọ": (500, 480)
}

NODE_RADIUS = 36


class CSPDefinitionApp:
    """Ứng dụng minh họa Định nghĩa CSP cho bài toán tô màu bản đồ."""

    def __init__(self, root):
        self.root = root
        self.root.title("Tô Màu Bản Đồ - Định nghĩa CSP")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Trạng thái
        self.coloring = {r: None for r in REGIONS}  # Màu hiện tại của từng vùng
        self.steps = []          # Danh sách các bước giải
        self.current_step = -1   # Bước hiện tại
        self.is_solving = False  # Đang giải hay không
        self.solution_found = False

        self._build_ui()
        self._draw_graph()
        self._show_csp_definition()

    # ====================== GIAO DIỆN ======================

    def _build_ui(self):
        """Xây dựng giao diện."""
        # Tiêu đề
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🗺️ Tô Màu Bản Đồ - Định Nghĩa CSP",
                 font=TITLE_FONT, bg="#2c3e50", fg="white").pack(expand=True)

        # Khung chính
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === Panel trái: Canvas vẽ bản đồ ===
        left_panel = tk.LabelFrame(main_frame, text="  Bản đồ Thủ Đức  ",
                                   font=HEADER_FONT, bg=PANEL_COLOR,
                                   relief=tk.GROOVE, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.canvas = tk.Canvas(left_panel, bg=PANEL_COLOR,
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # === Panel phải: Thông tin & điều khiển ===
        right_panel = tk.Frame(main_frame, bg=BG_COLOR, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)

        # Thông tin CSP
        info_frame = tk.LabelFrame(right_panel, text="  Công thức CSP  ",
                                   font=HEADER_FONT, bg=PANEL_COLOR,
                                   relief=tk.GROOVE, bd=2)
        info_frame.pack(fill=tk.X, pady=(0, 5))

        self.info_text = scrolledtext.ScrolledText(
            info_frame, font=SMALL_FONT, bg="#fafafa", fg="#2c3e50",
            height=10, wrap=tk.WORD, state=tk.DISABLED, bd=0)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)

        # Nhật ký thuật toán
        log_frame = tk.LabelFrame(right_panel, text="  Nhật ký thuật toán  ",
                                  font=HEADER_FONT, bg=PANEL_COLOR,
                                  relief=tk.GROOVE, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, font=SMALL_FONT, bg="#1e1e1e", fg="#00ff00",
            height=12, wrap=tk.WORD, state=tk.DISABLED, bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.tag_configure("success", foreground="#2ecc71")
        self.log_text.tag_configure("error", foreground="#e74c3c")
        self.log_text.tag_configure("info", foreground="#3498db")
        self.log_text.tag_configure("warn", foreground="#f1c40f")

        # Thanh trạng thái
        status_frame = tk.Frame(right_panel, bg=PANEL_COLOR, relief=tk.GROOVE, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        self.status_var = tk.StringVar(value="Sẵn sàng. Nhấn 'Giải' để bắt đầu.")
        tk.Label(status_frame, textvariable=self.status_var, font=SMALL_FONT,
                 bg=PANEL_COLOR, fg="#7f8c8d").pack(padx=5, pady=3)

        # Nút điều khiển
        btn_frame = tk.Frame(right_panel, bg=BG_COLOR)
        btn_frame.pack(fill=tk.X)

        btn_style = {"font": NORMAL_FONT, "width": 10, "cursor": "hand2", "bd": 0, "relief": tk.FLAT}

        self.btn_solve = tk.Button(btn_frame, text="▶ Giải", bg="#27ae60", fg="white",
                                   command=self._solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=2, pady=5)

        self.btn_prev = tk.Button(btn_frame, text="◀ Bước trước", bg="#2980b9", fg="white",
                                  command=self._prev_step, state=tk.DISABLED, **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=2, pady=5)

        self.btn_next = tk.Button(btn_frame, text="Bước tiếp ▶", bg="#2980b9", fg="white",
                                  command=self._next_step, state=tk.DISABLED, **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=2, pady=5)

        self.btn_reset = tk.Button(btn_frame, text="↺ Reset", bg="#e74c3c", fg="white",
                                   command=self._reset, **btn_style)
        self.btn_reset.pack(side=tk.LEFT, padx=2, pady=5)

    # ====================== VẼ ĐỒ THỊ ======================

    def _draw_graph(self):
        """Vẽ đồ thị bản đồ Úc."""
        self.canvas.delete("all")

        # Vẽ tiêu đề trên canvas
        self.canvas.create_text(280, 25, text="Bản đồ Thủ Đức (Đồ thị)",
                                font=("Segoe UI", 13, "bold"), fill="#2c3e50")

        # Vẽ các cạnh (ràng buộc)
        for r1, r2 in ADJACENCY:
            x1, y1 = POSITIONS[r1]
            x2, y2 = POSITIONS[r2]
            self.canvas.create_line(x1, y1, x2, y2, fill="#95a5a6",
                                    width=2, dash=(4, 2), tags="edge")

        # Vẽ các nút (vùng)
        self.node_items = {}
        for region in REGIONS:
            x, y = POSITIONS[region]
            color = UNCOLORED
            if self.coloring[region]:
                color = COLORS[self.coloring[region]]

            # Vòng tròn nền
            shadow = self.canvas.create_oval(
                x - NODE_RADIUS + 2, y - NODE_RADIUS + 2,
                x + NODE_RADIUS + 2, y + NODE_RADIUS + 2,
                fill="#bdc3c7", outline="", tags=f"shadow_{region}")

            circle = self.canvas.create_oval(
                x - NODE_RADIUS, y - NODE_RADIUS,
                x + NODE_RADIUS, y + NODE_RADIUS,
                fill=color, outline="#2c3e50", width=2, tags=f"node_{region}")

            text = self.canvas.create_text(
                x, y, text=region.replace(" ", "\n"), font=("Segoe UI", 9, "bold"),
                fill="white" if color != UNCOLORED else "#2c3e50",
                tags=f"text_{region}")

            self.node_items[region] = (circle, text, shadow)

        # Chú thích màu
        legend_y = 590
        self.canvas.create_text(100, legend_y - 15, text="Bảng màu:",
                                font=("Segoe UI", 10, "bold"), fill="#2c3e50")
        for i, (name, color) in enumerate(COLORS.items()):
            cx = 60 + i * 120
            self.canvas.create_rectangle(cx, legend_y, cx + 20, legend_y + 20,
                                         fill=color, outline="#2c3e50")
            self.canvas.create_text(cx + 25, legend_y + 10, text=name,
                                    anchor=tk.W, font=SMALL_FONT, fill="#2c3e50")

    def _update_node_color(self, region, color_name=None, highlight=False):
        """Cập nhật màu một nút."""
        circle, text, shadow = self.node_items[region]
        if color_name:
            fill_color = COLORS[color_name]
            text_color = "white"
        else:
            fill_color = UNCOLORED
            text_color = "#2c3e50"

        outline_color = "#e74c3c" if highlight else "#2c3e50"
        outline_width = 4 if highlight else 2

        self.canvas.itemconfig(circle, fill=fill_color,
                               outline=outline_color, width=outline_width)
        self.canvas.itemconfig(text, fill=text_color)

    # ====================== HIỂN THỊ CSP ======================

    def _show_csp_definition(self):
        """Hiển thị định nghĩa CSP."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)

        info = "═══ ĐỊNH NGHĨA CSP ═══\n\n"
        info += "▸ BIẾN (Variables):\n"
        info += f"  X = {{{', '.join(REGIONS)}}}\n"
        info += f"  |X| = {len(REGIONS)} vùng\n\n"

        info += "▸ MIỀN GIÁ TRỊ (Domains):\n"
        for r in REGIONS:
            info += f"  D({r}) = {{{', '.join(COLOR_NAMES)}}}\n"
        info += f"\n"

        info += "▸ RÀNG BUỘC (Constraints):\n"
        info += f"  Tổng: {len(ADJACENCY)} ràng buộc\n"
        for r1, r2 in ADJACENCY:
            info += f"  C: {r1} ≠ {r2}\n"

        info += f"\n▸ KHÔNG GIAN TÌM KIẾM:\n"
        total = len(COLOR_NAMES) ** len(REGIONS)
        info += f"  {len(COLOR_NAMES)}^{len(REGIONS)} = {total:,} tổ hợp\n"

        self.info_text.insert("1.0", info)
        self.info_text.config(state=tk.DISABLED)

    # ====================== LOG ======================

    def _log(self, message, tag=None):
        """Ghi nhật ký."""
        self.log_text.config(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        """Xóa nhật ký."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ====================== THUẬT TOÁN ======================

    def _generate_steps(self):
        """Tạo các bước giải bằng phương pháp vét cạn (brute-force) có cắt tỉa."""
        self.steps = []
        assignment = {}

        def is_consistent(var, color, assignment):
            """Kiểm tra tính nhất quán."""
            for r1, r2 in ADJACENCY:
                if r1 == var and r2 in assignment and assignment[r2] == color:
                    return False
                if r2 == var and r1 in assignment and assignment[r1] == color:
                    return False
            return True

        def backtrack(idx, assignment):
            """Vét cạn có cắt tỉa."""
            if idx == len(REGIONS):
                # Tìm được lời giải
                self.steps.append({
                    "type": "solution",
                    "assignment": dict(assignment),
                    "message": "✅ Tìm được lời giải hợp lệ!"
                })
                return True

            var = REGIONS[idx]
            for color in COLOR_NAMES:
                # Ghi bước thử gán
                self.steps.append({
                    "type": "try",
                    "var": var,
                    "color": color,
                    "assignment": dict(assignment),
                    "message": f"Thử gán {var} = {color}"
                })

                if is_consistent(var, color, assignment):
                    assignment[var] = color
                    self.steps.append({
                        "type": "assign",
                        "var": var,
                        "color": color,
                        "assignment": dict(assignment),
                        "message": f"✓ Gán {var} = {color} (hợp lệ)"
                    })

                    if backtrack(idx + 1, assignment):
                        return True

                    # Quay lui
                    del assignment[var]
                    self.steps.append({
                        "type": "backtrack",
                        "var": var,
                        "color": color,
                        "assignment": dict(assignment),
                        "message": f"↩ Quay lui: bỏ gán {var} = {color}"
                    })
                else:
                    # Vi phạm ràng buộc
                    conflicts = []
                    for r1, r2 in ADJACENCY:
                        if r1 == var and r2 in assignment and assignment[r2] == color:
                            conflicts.append(r2)
                        if r2 == var and r1 in assignment and assignment[r1] == color:
                            conflicts.append(r1)
                    self.steps.append({
                        "type": "conflict",
                        "var": var,
                        "color": color,
                        "conflicts": conflicts,
                        "assignment": dict(assignment),
                        "message": f"✗ {var}={color} xung đột với {', '.join(conflicts)}"
                    })

            return False

        backtrack(0, assignment)

    def _apply_step(self, step_idx):
        """Áp dụng một bước."""
        if step_idx < 0 or step_idx >= len(self.steps):
            return

        step = self.steps[step_idx]
        assignment = step["assignment"]

        # Cập nhật màu tất cả vùng
        for region in REGIONS:
            if region in assignment:
                highlight = False
                if step["type"] == "conflict" and region in step.get("conflicts", []):
                    highlight = True
                if step["type"] in ("try", "assign", "conflict") and region == step.get("var"):
                    highlight = step["type"] == "conflict"
                self._update_node_color(region, assignment[region], highlight)
            else:
                highlight = (step["type"] in ("try", "conflict") and
                             region == step.get("var"))
                self._update_node_color(region, None, highlight)

        # Nếu đang thử gán, hiển thị tạm thời
        if step["type"] == "try":
            var = step["var"]
            color = step["color"]
            self._update_node_color(var, color, True)

        self.status_var.set(f"Bước {step_idx + 1}/{len(self.steps)}: {step['message']}")

    # ====================== ĐIỀU KHIỂN ======================

    def _solve(self):
        """Bắt đầu giải."""
        if self.is_solving:
            return

        self._reset()
        self.is_solving = True
        self.btn_solve.config(state=tk.DISABLED)

        self._log("═══ BẮT ĐẦU GIẢI - VÉT CẠN CÓ CẮT TỈA ═══", "info")
        self._log(f"Biến: {REGIONS}", "info")
        self._log(f"Màu: {COLOR_NAMES}", "info")
        self._log(f"Ràng buộc: {len(ADJACENCY)} cặp kề nhau", "info")
        self._log("─" * 40)

        # Tạo các bước
        self._generate_steps()

        self._log(f"Tổng số bước: {len(self.steps)}", "info")
        self._log("─" * 40)

        # Hiển thị log cho từng bước
        for i, step in enumerate(self.steps):
            tag = None
            if step["type"] == "solution":
                tag = "success"
            elif step["type"] == "conflict":
                tag = "error"
            elif step["type"] == "backtrack":
                tag = "warn"
            elif step["type"] == "assign":
                tag = "success"
            self._log(f"[{i+1}] {step['message']}", tag)

        # Kích hoạt nút bước
        self.btn_next.config(state=tk.NORMAL)
        self.btn_prev.config(state=tk.NORMAL)
        self.current_step = -1
        self.is_solving = False
        self.status_var.set(f"Đã tạo {len(self.steps)} bước. Nhấn 'Bước tiếp' để xem.")

    def _next_step(self):
        """Bước tiếp theo."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._apply_step(self.current_step)

    def _prev_step(self):
        """Bước trước."""
        if self.current_step > 0:
            self.current_step -= 1
            self._apply_step(self.current_step)
        elif self.current_step == 0:
            self.current_step = -1
            for region in REGIONS:
                self._update_node_color(region, None, False)
            self.status_var.set("Đã quay lại đầu.")

    def _reset(self):
        """Đặt lại trạng thái."""
        self.coloring = {r: None for r in REGIONS}
        self.steps = []
        self.current_step = -1
        self.is_solving = False
        self.solution_found = False

        self._draw_graph()
        self._clear_log()
        self.btn_solve.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_prev.config(state=tk.DISABLED)
        self.status_var.set("Sẵn sàng. Nhấn 'Giải' để bắt đầu.")


# ========================== CHẠY ỨNG DỤNG ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = CSPDefinitionApp(root)
    root.mainloop()
