"""
Tô Màu Bản Đồ - CSP Backtracking
Sử dụng Heuristic MRV.
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

class BacktrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tô Màu Bản Đồ - Backtracking (MRV)")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.coloring = {r: None for r in REGIONS}
        self.steps = []
        self.current_step = -1

        self._build_ui()
        self._draw_graph()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🗺️ Tô Màu Bản Đồ - Backtracking & MRV",
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

        log_frame = tk.LabelFrame(right_panel, text="  Nhật ký  ", font=HEADER_FONT, bg=PANEL_COLOR)
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

        self.btn_solve = tk.Button(btn_frame, text="▶ Giải", bg="#27ae60", fg="white", command=self._solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=2, pady=5)
        self.btn_prev = tk.Button(btn_frame, text="◀ Trước", bg="#2980b9", fg="white", command=self._prev_step, state=tk.DISABLED, **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=2, pady=5)
        self.btn_next = tk.Button(btn_frame, text="Tiếp ▶", bg="#2980b9", fg="white", command=self._next_step, state=tk.DISABLED, **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=2, pady=5)
        self.btn_reset = tk.Button(btn_frame, text="↺ Reset", bg="#e74c3c", fg="white", command=self._reset, **btn_style)
        self.btn_reset.pack(side=tk.LEFT, padx=2, pady=5)

    def _draw_graph(self):
        self.canvas.delete("all")
        self.canvas.create_text(280, 25, text="Backtracking with MRV", font=("Segoe UI", 13, "bold"), fill="#2c3e50")

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

    def _generate_steps(self):
        self.steps = []
        assignment = {}
        
        def is_consistent(var, color, assign):
            for r1, r2 in ADJACENCY:
                if r1 == var and r2 in assign and assign[r2] == color: return False
                if r2 == var and r1 in assign and assign[r1] == color: return False
            return True

        def select_mrv(assign):
            # Chọn biến có MRV (Minimum Remaining Values)
            unassigned = [v for v in REGIONS if v not in assign]
            best_var = None
            min_val = 999
            for v in unassigned:
                valid_colors = sum(1 for c in COLOR_NAMES if is_consistent(v, c, assign))
                if valid_colors < min_val:
                    min_val = valid_colors
                    best_var = v
            return best_var

        def backtrack(assign):
            if len(assign) == len(REGIONS):
                self.steps.append({"type": "solution", "assign": dict(assign), "msg": "Tìm thấy lời giải!"})
                return True
                
            var = select_mrv(assign)
            self.steps.append({"type": "info", "assign": dict(assign), "msg": f"Chọn biến {var} (MRV heuristic)"})
            
            for color in COLOR_NAMES:
                if is_consistent(var, color, assign):
                    assign[var] = color
                    self.steps.append({"type": "assign", "assign": dict(assign), "msg": f"Gán {var} = {color}"})
                    if backtrack(assign):
                        return True
                    del assign[var]
                    self.steps.append({"type": "backtrack", "assign": dict(assign), "msg": f"Quay lui, bỏ gán {var}"})
            return False

        backtrack(assignment)

    def _apply_step(self, step_idx):
        step = self.steps[step_idx]
        assign = step["assign"]
        self.status_var.set(f"Bước {step_idx + 1}: {step['msg']}")
        
        for region in REGIONS:
            circle, text = self.node_items[region]
            if region in assign:
                self.canvas.itemconfig(circle, fill=COLORS[assign[region]], outline="#2c3e50", width=2)
            else:
                self.canvas.itemconfig(circle, fill=UNCOLORED, outline="#2c3e50", width=2)

    def _solve(self):
        self._reset()
        self._generate_steps()
        self.log_text.config(state=tk.NORMAL)
        for i, s in enumerate(self.steps):
            self.log_text.insert(tk.END, f"[{i+1}] {s['msg']}\n")
        self.log_text.config(state=tk.DISABLED)
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
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_prev.config(state=tk.DISABLED)
        self.status_var.set("Sẵn sàng.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BacktrackingApp(root)
    root.mainloop()
