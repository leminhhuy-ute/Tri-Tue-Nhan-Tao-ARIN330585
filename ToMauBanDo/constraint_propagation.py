"""
Tô Màu Bản Đồ - Lan truyền ràng buộc (AC-3)
Thuật toán Arc Consistency 3 cho bài toán tô màu bản đồ Úc.
Hiển thị quá trình thu hẹp miền giá trị từng bước.
Sau AC-3, sử dụng Backtracking nếu cần.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import copy

# ========================== CẤU HÌNH ==========================

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
BG_COLOR = "#ecf0f1"
PANEL_COLOR = "#ffffff"
TITLE_FONT = ("Segoe UI", 16, "bold")
HEADER_FONT = ("Segoe UI", 12, "bold")
NORMAL_FONT = ("Segoe UI", 10)
SMALL_FONT = ("Segoe UI", 9)

COLORS = {
    "Đỏ": "#e74c3c",
    "Xanh dương": "#3498db",
    "Xanh lá": "#2ecc71",
    "Vàng": "#f1c40f"
}
COLOR_NAMES = list(COLORS.keys())
UNCOLORED = "#bdc3c7"

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


class ConstraintPropagationApp:
    """Ứng dụng minh họa AC-3 cho bài toán tô màu bản đồ."""

    def __init__(self, root):
        self.root = root
        self.root.title("Tô Màu Bản Đồ - Lan Truyền Ràng Buộc (AC-3)")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.coloring = {r: None for r in REGIONS}
        self.domains = {r: list(COLOR_NAMES) for r in REGIONS}
        self.steps = []
        self.current_step = -1
        self.is_solving = False

        self._build_ui()
        self._draw_graph()
        self._show_domains()

    # ====================== GIAO DIỆN ======================

    def _build_ui(self):
        """Xây dựng giao diện."""
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🗺️ Tô Màu Bản Đồ - AC-3 (Arc Consistency)",
                 font=TITLE_FONT, bg="#2c3e50", fg="white").pack(expand=True)

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel trái
        left_panel = tk.LabelFrame(main_frame, text="  Bản đồ Thủ Đức  ",
                                   font=HEADER_FONT, bg=PANEL_COLOR,
                                   relief=tk.GROOVE, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.canvas = tk.Canvas(left_panel, bg=PANEL_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Panel phải
        right_panel = tk.Frame(main_frame, bg=BG_COLOR, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)

        # Miền giá trị
        domain_frame = tk.LabelFrame(right_panel, text="  Miền giá trị (Domains)  ",
                                     font=HEADER_FONT, bg=PANEL_COLOR,
                                     relief=tk.GROOVE, bd=2)
        domain_frame.pack(fill=tk.X, pady=(0, 5))

        self.domain_text = scrolledtext.ScrolledText(
            domain_frame, font=SMALL_FONT, bg="#fafafa", fg="#2c3e50",
            height=8, wrap=tk.WORD, state=tk.DISABLED, bd=0)
        self.domain_text.pack(fill=tk.X, padx=5, pady=5)

        # Nhật ký
        log_frame = tk.LabelFrame(right_panel, text="  Nhật ký AC-3  ",
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
        self.log_text.tag_configure("header", foreground="#9b59b6")

        # Trạng thái
        status_frame = tk.Frame(right_panel, bg=PANEL_COLOR, relief=tk.GROOVE, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        self.status_var = tk.StringVar(value="Sẵn sàng. Nhấn 'Giải' để bắt đầu.")
        tk.Label(status_frame, textvariable=self.status_var, font=SMALL_FONT,
                 bg=PANEL_COLOR, fg="#7f8c8d").pack(padx=5, pady=3)

        # Nút
        btn_frame = tk.Frame(right_panel, bg=BG_COLOR)
        btn_frame.pack(fill=tk.X)

        btn_style = {"font": NORMAL_FONT, "width": 10, "cursor": "hand2",
                     "bd": 0, "relief": tk.FLAT}

        self.btn_solve = tk.Button(btn_frame, text="▶ Giải", bg="#27ae60",
                                   fg="white", command=self._solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=2, pady=5)

        self.btn_prev = tk.Button(btn_frame, text="◀ Bước trước", bg="#2980b9",
                                  fg="white", command=self._prev_step,
                                  state=tk.DISABLED, **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=2, pady=5)

        self.btn_next = tk.Button(btn_frame, text="Bước tiếp ▶", bg="#2980b9",
                                  fg="white", command=self._next_step,
                                  state=tk.DISABLED, **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=2, pady=5)

        self.btn_reset = tk.Button(btn_frame, text="↺ Reset", bg="#e74c3c",
                                   fg="white", command=self._reset, **btn_style)
        self.btn_reset.pack(side=tk.LEFT, padx=2, pady=5)

    # ====================== VẼ ĐỒ THỊ ======================

    def _draw_graph(self):
        """Vẽ đồ thị bản đồ Úc."""
        self.canvas.delete("all")
        self.canvas.create_text(280, 25, text="Bản đồ Thủ Đức (Đồ thị)",
                                font=("Segoe UI", 13, "bold"), fill="#2c3e50")

        for r1, r2 in ADJACENCY:
            x1, y1 = POSITIONS[r1]
            x2, y2 = POSITIONS[r2]
            self.canvas.create_line(x1, y1, x2, y2, fill="#95a5a6",
                                    width=2, dash=(4, 2))

        self.node_items = {}
        for region in REGIONS:
            x, y = POSITIONS[region]
            color = UNCOLORED
            if self.coloring[region]:
                color = COLORS[self.coloring[region]]

            shadow = self.canvas.create_oval(
                x - NODE_RADIUS + 2, y - NODE_RADIUS + 2,
                x + NODE_RADIUS + 2, y + NODE_RADIUS + 2,
                fill="#bdc3c7", outline="")
            circle = self.canvas.create_oval(
                x - NODE_RADIUS, y - NODE_RADIUS,
                x + NODE_RADIUS, y + NODE_RADIUS,
                fill=color, outline="#2c3e50", width=2)
            text = self.canvas.create_text(
                x, y - 8, text=region.replace(" ", "\n"), font=("Segoe UI", 9, "bold"),
                fill="white" if color != UNCOLORED else "#2c3e50")

            # Hiển thị kích thước miền
            domain_size = len(self.domains.get(region, COLOR_NAMES))
            domain_label = self.canvas.create_text(
                x, y + 12, text=f"|D|={domain_size}",
                font=("Segoe UI", 8), fill="#7f8c8d")

            self.node_items[region] = (circle, text, shadow, domain_label)

        # Chú thích
        legend_y = 590
        self.canvas.create_text(100, legend_y - 15, text="Bảng màu:",
                                font=("Segoe UI", 10, "bold"), fill="#2c3e50")
        for i, (name, color) in enumerate(COLORS.items()):
            cx = 60 + i * 120
            self.canvas.create_rectangle(cx, legend_y, cx + 20, legend_y + 20,
                                         fill=color, outline="#2c3e50")
            self.canvas.create_text(cx + 25, legend_y + 10, text=name,
                                    anchor=tk.W, font=SMALL_FONT, fill="#2c3e50")

    def _update_node(self, region, color_name=None, highlight=False, domain_size=None):
        """Cập nhật nút."""
        circle, text, shadow, domain_label = self.node_items[region]
        fill_color = COLORS[color_name] if color_name else UNCOLORED
        text_color = "white" if color_name else "#2c3e50"
        outline = "#e74c3c" if highlight else "#2c3e50"
        width = 4 if highlight else 2

        self.canvas.itemconfig(circle, fill=fill_color, outline=outline, width=width)
        self.canvas.itemconfig(text, fill=text_color)
        if domain_size is not None:
            self.canvas.itemconfig(domain_label, text=f"|D|={domain_size}")

    # ====================== HIỂN THỊ ======================

    def _show_domains(self, domains=None):
        """Hiển thị miền giá trị."""
        if domains is None:
            domains = self.domains
        self.domain_text.config(state=tk.NORMAL)
        self.domain_text.delete("1.0", tk.END)
        info = "═══ MIỀN GIÁ TRỊ HIỆN TẠI ═══\n\n"
        for r in REGIONS:
            d = domains.get(r, [])
            info += f"  D({r}) = {{{', '.join(d)}}}"
            info += f"  [{len(d)} giá trị]\n"
        self.domain_text.insert("1.0", info)
        self.domain_text.config(state=tk.DISABLED)

    def _log(self, message, tag=None):
        self.log_text.config(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ====================== AC-3 ======================

    def _get_neighbors(self, var):
        """Lấy các vùng kề."""
        neighbors = []
        for r1, r2 in ADJACENCY:
            if r1 == var:
                neighbors.append(r2)
            elif r2 == var:
                neighbors.append(r1)
        return neighbors

    def _generate_steps(self):
        """Tạo các bước cho AC-3 + Backtracking."""
        self.steps = []
        domains = {r: list(COLOR_NAMES) for r in REGIONS}

        # ===== GIAI ĐOẠN 1: AC-3 =====
        self.steps.append({
            "type": "phase",
            "phase": "AC-3",
            "domains": copy.deepcopy(domains),
            "assignment": {},
            "message": "═══ GIAI ĐOẠN 1: AC-3 ═══"
        })

        # Khởi tạo hàng đợi cung
        queue = []
        for r1, r2 in ADJACENCY:
            queue.append((r1, r2))
            queue.append((r2, r1))

        self.steps.append({
            "type": "init_queue",
            "queue_size": len(queue),
            "domains": copy.deepcopy(domains),
            "assignment": {},
            "message": f"Khởi tạo hàng đợi: {len(queue)} cung"
        })

        while queue:
            xi, xj = queue.pop(0)

            self.steps.append({
                "type": "process_arc",
                "arc": (xi, xj),
                "queue_size": len(queue),
                "domains": copy.deepcopy(domains),
                "assignment": {},
                "highlight": [xi, xj],
                "message": f"Xử lý cung ({xi}, {xj}) - Hàng đợi còn: {len(queue)}"
            })

            # Kiểm tra và thu hẹp miền
            revised = False
            removed_values = []
            for color in list(domains[xi]):
                # Kiểm tra có tồn tại giá trị khác cho xj
                has_support = any(c != color for c in domains[xj])
                if not has_support:
                    domains[xi].remove(color)
                    removed_values.append(color)
                    revised = True

            if revised:
                self.steps.append({
                    "type": "revise",
                    "var": xi,
                    "removed": removed_values,
                    "domains": copy.deepcopy(domains),
                    "assignment": {},
                    "highlight": [xi],
                    "message": f"Thu hẹp D({xi}): loại bỏ {removed_values}"
                })

                if not domains[xi]:
                    self.steps.append({
                        "type": "empty_domain",
                        "var": xi,
                        "domains": copy.deepcopy(domains),
                        "assignment": {},
                        "message": f"D({xi}) rỗng! Không có lời giải."
                    })
                    return

                # Thêm lại các cung liên quan
                for xk in self._get_neighbors(xi):
                    if xk != xj and (xk, xi) not in queue:
                        queue.append((xk, xi))
            else:
                self.steps.append({
                    "type": "no_change",
                    "arc": (xi, xj),
                    "domains": copy.deepcopy(domains),
                    "assignment": {},
                    "message": f"Cung ({xi}, {xj}): không thay đổi"
                })

        self.steps.append({
            "type": "ac3_done",
            "domains": copy.deepcopy(domains),
            "assignment": {},
            "message": "AC-3 hoàn tất! Miền giá trị đã được thu hẹp."
        })

        # ===== GIAI ĐOẠN 2: Backtracking =====
        self.steps.append({
            "type": "phase",
            "phase": "Backtracking",
            "domains": copy.deepcopy(domains),
            "assignment": {},
            "message": "═══ GIAI ĐOẠN 2: BACKTRACKING ═══"
        })

        def is_consistent(var, color, assignment):
            for r1, r2 in ADJACENCY:
                if r1 == var and r2 in assignment and assignment[r2] == color:
                    return False
                if r2 == var and r1 in assignment and assignment[r1] == color:
                    return False
            return True

        def backtrack(idx, assignment, domains):
            if idx == len(REGIONS):
                self.steps.append({
                    "type": "solution",
                    "assignment": dict(assignment),
                    "domains": copy.deepcopy(domains),
                    "message": "✅ Tìm được lời giải!"
                })
                return True

            var = REGIONS[idx]
            for color in domains[var]:
                self.steps.append({
                    "type": "bt_try",
                    "var": var,
                    "color": color,
                    "assignment": dict(assignment),
                    "domains": copy.deepcopy(domains),
                    "message": f"Thử {var} = {color}"
                })

                if is_consistent(var, color, assignment):
                    assignment[var] = color
                    self.steps.append({
                        "type": "bt_assign",
                        "var": var,
                        "color": color,
                        "assignment": dict(assignment),
                        "domains": copy.deepcopy(domains),
                        "message": f"✓ Gán {var} = {color}"
                    })
                    if backtrack(idx + 1, assignment, domains):
                        return True
                    del assignment[var]
                    self.steps.append({
                        "type": "bt_backtrack",
                        "var": var,
                        "assignment": dict(assignment),
                        "domains": copy.deepcopy(domains),
                        "message": f"↩ Quay lui: bỏ {var}"
                    })
                else:
                    self.steps.append({
                        "type": "bt_conflict",
                        "var": var,
                        "color": color,
                        "assignment": dict(assignment),
                        "domains": copy.deepcopy(domains),
                        "message": f"✗ {var}={color} xung đột!"
                    })
            return False

        backtrack(0, {}, domains)

    def _apply_step(self, step_idx):
        """Áp dụng bước."""
        if step_idx < 0 or step_idx >= len(self.steps):
            return
        step = self.steps[step_idx]
        domains = step.get("domains", {})
        assignment = step.get("assignment", {})
        highlight_list = step.get("highlight", [])

        self._show_domains(domains)

        for region in REGIONS:
            color = assignment.get(region, None)
            hl = region in highlight_list
            ds = len(domains.get(region, []))
            self._update_node(region, color, hl, ds)

        # Hiển thị tạm thời nếu đang thử
        if step["type"] in ("bt_try",):
            var = step.get("var")
            color = step.get("color")
            if var and color:
                self._update_node(var, color, True, len(domains.get(var, [])))

        self.status_var.set(f"Bước {step_idx + 1}/{len(self.steps)}: {step['message']}")

    # ====================== ĐIỀU KHIỂN ======================

    def _solve(self):
        if self.is_solving:
            return
        self._reset()
        self.is_solving = True
        self.btn_solve.config(state=tk.DISABLED)

        self._log("═══ THUẬT TOÁN AC-3 + BACKTRACKING ═══", "header")
        self._log(f"Biến: {REGIONS}", "info")
        self._log(f"Ràng buộc: {len(ADJACENCY)} cặp kề", "info")
        self._log("─" * 40)

        self._generate_steps()

        for i, step in enumerate(self.steps):
            tag = None
            t = step["type"]
            if t in ("solution", "bt_assign", "revise"):
                tag = "success"
            elif t in ("bt_conflict", "empty_domain"):
                tag = "error"
            elif t in ("bt_backtrack",):
                tag = "warn"
            elif t in ("phase",):
                tag = "header"
            elif t in ("process_arc", "init_queue"):
                tag = "info"
            self._log(f"[{i+1}] {step['message']}", tag)

        self.btn_next.config(state=tk.NORMAL)
        self.btn_prev.config(state=tk.NORMAL)
        self.current_step = -1
        self.is_solving = False
        self.status_var.set(f"Đã tạo {len(self.steps)} bước. Nhấn 'Bước tiếp'.")

    def _next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._apply_step(self.current_step)

    def _prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self._apply_step(self.current_step)
        elif self.current_step == 0:
            self.current_step = -1
            self.domains = {r: list(COLOR_NAMES) for r in REGIONS}
            self._draw_graph()
            self._show_domains()
            self.status_var.set("Đã quay lại đầu.")

    def _reset(self):
        self.coloring = {r: None for r in REGIONS}
        self.domains = {r: list(COLOR_NAMES) for r in REGIONS}
        self.steps = []
        self.current_step = -1
        self.is_solving = False

        self._draw_graph()
        self._show_domains()
        self._clear_log()
        self.btn_solve.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_prev.config(state=tk.DISABLED)
        self.status_var.set("Sẵn sàng. Nhấn 'Giải' để bắt đầu.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConstraintPropagationApp(root)
    root.mainloop()
