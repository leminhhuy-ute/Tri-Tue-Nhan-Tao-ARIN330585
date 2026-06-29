"""
Tô Màu Bản Đồ - Global Constraints (AllDiff)
Hiển thị cách AllDiff giới hạn các miền giá trị trên các cụm kề nhau.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
BG_COLOR = "#ecf0f1"
PANEL_COLOR = "#ffffff"
TITLE_FONT = ("Segoe UI", 16, "bold")
HEADER_FONT = ("Segoe UI", 12, "bold")
NORMAL_FONT = ("Segoe UI", 10)
SMALL_FONT = ("Segoe UI", 9)

COLORS = {"Đỏ": "#e74c3c", "Xanh dương": "#3498db", "Xanh lá": "#2ecc71", "Vàng": "#f1c40f"}
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

class GlobalConstraintsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tô Màu Bản Đồ - Global Constraints")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.domains = {r: list(COLOR_NAMES) for r in REGIONS}
        self.steps = []
        self.current_step = -1

        self._build_ui()
        self._draw_graph()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🗺️ Tô Màu Bản Đồ - Global Constraints (AllDiff)",
                 font=TITLE_FONT, bg="#2c3e50", fg="white").pack(expand=True)

        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = tk.LabelFrame(main_frame, text="  Bản đồ Thủ Đức  ", font=HEADER_FONT, bg=PANEL_COLOR)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.canvas = tk.Canvas(left_panel, bg=PANEL_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_panel = tk.Frame(main_frame, bg=BG_COLOR, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)

        domain_frame = tk.LabelFrame(right_panel, text="  Miền Giá Trị  ", font=HEADER_FONT, bg=PANEL_COLOR)
        domain_frame.pack(fill=tk.X, pady=(0, 5))

        self.domain_text = scrolledtext.ScrolledText(domain_frame, font=SMALL_FONT, bg="#fafafa", height=6, state=tk.DISABLED)
        self.domain_text.pack(fill=tk.X, padx=5, pady=5)

        log_frame = tk.LabelFrame(right_panel, text="  Hoạt động AllDiff  ", font=HEADER_FONT, bg=PANEL_COLOR)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(log_frame, font=SMALL_FONT, bg="#1e1e1e", fg="#00ff00", height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        status_frame = tk.Frame(right_panel, bg=PANEL_COLOR, relief=tk.GROOVE, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        tk.Label(status_frame, textvariable=self.status_var, font=SMALL_FONT, bg=PANEL_COLOR).pack(padx=5, pady=3)

        btn_frame = tk.Frame(right_panel, bg=BG_COLOR)
        btn_frame.pack(fill=tk.X)
        btn_style = {"font": NORMAL_FONT, "width": 10, "cursor": "hand2"}

        self.btn_solve = tk.Button(btn_frame, text="▶ Chạy AllDiff", bg="#27ae60", fg="white", command=self._solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=2, pady=5)
        self.btn_prev = tk.Button(btn_frame, text="◀ Trước", bg="#2980b9", fg="white", command=self._prev_step, state=tk.DISABLED, **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=2, pady=5)
        self.btn_next = tk.Button(btn_frame, text="Tiếp ▶", bg="#2980b9", fg="white", command=self._next_step, state=tk.DISABLED, **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=2, pady=5)
        self.btn_reset = tk.Button(btn_frame, text="↺ Reset", bg="#e74c3c", fg="white", command=self._reset, **btn_style)
        self.btn_reset.pack(side=tk.LEFT, padx=2, pady=5)

    def _draw_graph(self):
        self.canvas.delete("all")
        self.canvas.create_text(280, 25, text="Global Constraint (AllDiff)", font=("Segoe UI", 13, "bold"), fill="#2c3e50")

        for r1, r2 in ADJACENCY:
            x1, y1 = POSITIONS[r1]
            x2, y2 = POSITIONS[r2]
            self.canvas.create_line(x1, y1, x2, y2, fill="#95a5a6", width=2, tags="edge")

        self.node_items = {}
        for region in REGIONS:
            x, y = POSITIONS[region]
            circle = self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS,
                                             fill=UNCOLORED, outline="#2c3e50", width=2)
            text = self.canvas.create_text(x, y, text=region.replace(" ", "\n"), font=("Segoe UI", 9, "bold"), fill="#2c3e50")
            self.node_items[region] = (circle, text)

    def _update_domains_display(self, domains):
        self.domain_text.config(state=tk.NORMAL)
        self.domain_text.delete("1.0", tk.END)
        for r in REGIONS:
            self.domain_text.insert(tk.END, f"{r}: {', '.join(domains[r])}\n")
        self.domain_text.config(state=tk.DISABLED)

    def _generate_steps(self):
        self.steps = []
        doms = {r: list(COLOR_NAMES) for r in REGIONS}
        
        self.steps.append({"msg": "Áp dụng AllDiff cho cụm {WA, NT, SA}", "doms": dict(doms), "highlight": ["WA", "NT", "SA"]})
        doms["WA"] = ["Đỏ"]
        doms["NT"] = ["Xanh dương"]
        doms["SA"] = ["Xanh lá"]
        self.steps.append({"msg": "-> Thu hẹp miền của các biến trong cụm", "doms": dict(doms), "highlight": ["WA", "NT", "SA"]})
        
        self.steps.append({"msg": "Áp dụng AllDiff cho cụm {NT, SA, Q}", "doms": dict(doms), "highlight": ["NT", "SA", "Q"]})
        doms["Q"] = ["Đỏ", "Vàng"]
        self.steps.append({"msg": "-> Q không thể nhận màu của NT và SA", "doms": dict(doms), "highlight": ["NT", "SA", "Q"]})

        self.steps.append({"msg": "Hoàn thành.", "doms": dict(doms), "highlight": []})

    def _apply_step(self, step_idx):
        step = self.steps[step_idx]
        self._update_domains_display(step["doms"])
        self.status_var.set(f"Bước {step_idx + 1}: {step['msg']}")
        
        for region in REGIONS:
            circle, text = self.node_items[region]
            if region in step["highlight"]:
                self.canvas.itemconfig(circle, outline="#e74c3c", width=4)
            else:
                self.canvas.itemconfig(circle, outline="#2c3e50", width=2)

    def _solve(self):
        self._reset()
        self._generate_steps()
        self.btn_next.config(state=tk.NORMAL)
        self.btn_prev.config(state=tk.NORMAL)
        self.status_var.set("Bắt đầu xem các bước.")

    def _next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._apply_step(self.current_step)

    def _prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self._apply_step(self.current_step)

    def _reset(self):
        self.current_step = -1
        self._draw_graph()
        self._update_domains_display({r: list(COLOR_NAMES) for r in REGIONS})
        self.btn_next.config(state=tk.DISABLED)
        self.btn_prev.config(state=tk.DISABLED)
        self.status_var.set("Sẵn sàng.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GlobalConstraintsApp(root)
    root.mainloop()
