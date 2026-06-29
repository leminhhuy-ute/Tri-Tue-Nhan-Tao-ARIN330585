"""
============================================================
TRUNG TÂM ĐIỀU KHIỂN - TRÍ TUỆ NHÂN TẠO
============================================================
App launcher chính - Chọn 1 trong 4 chế độ:
  1. Máy Hút Bụi (MayHutBui)
  2. 8 Puzzle
  3. Tô Màu Bản Đồ (ToMauBanDo)
  4. Cờ Ca Rô (CoCaRo)
============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

# ============================================================
# CẤU HÌNH THUẬT TOÁN
# ============================================================

ALGORITHMS = {
    "MayHutBui": {
        "title": "🤖 Máy Hút Bụi",
        "subtitle": "Robot dọn dẹp bụi bẩn trên lưới",
        "color": "#00b894",
        "hover": "#00cec9",
        "icon": "🧹",
        "groups": {
            "Nhóm 1 - Uninformed Search": [
                ("BFS (Breadth-First Search)", "bfs.py"),
                ("DFS (Depth-First Search)", "dfs.py"),
                ("UCS (Uniform Cost Search)", "ucs.py"),
                ("IDS (Iterative Deepening Search)", "ids.py"),
            ],
            "Nhóm 2 - Informed Search": [
                ("Greedy Best-First Search", "greedy.py"),
                ("A* Search", "astar.py"),
                ("IDA* (Iterative Deepening A*)", "ida_star.py"),
            ],
            "Nhóm 3 - Local Search": [
                ("Simple Hill Climbing", "simple_hill_climbing.py"),
                ("Steepest-Ascent Hill Climbing", "steepest_hill_climbing.py"),
                ("Stochastic Hill Climbing", "stochastic_hill_climbing.py"),
                ("Random-Restart Hill Climbing", "random_restart_hill.py"),
                ("Local Beam Search", "local_beam_search.py"),
                ("Simulated Annealing", "simulated_annealing.py"),
            ],
        },
    },
    "8Puzzle": {
        "title": "🧩 8 Puzzle",
        "subtitle": "Giải trò chơi xếp hình 8 ô",
        "color": "#6c5ce7",
        "hover": "#a29bfe",
        "icon": "🔢",
        "groups": {
            "Nhóm 1 - Uninformed Search": [
                ("BFS (Breadth-First Search)", "bfs.py"),
                ("DFS (Depth-First Search)", "dfs.py"),
                ("UCS (Uniform Cost Search)", "ucs.py"),
                ("IDS (Iterative Deepening Search)", "ids.py"),
            ],
            "Nhóm 2 - Informed Search": [
                ("Greedy Best-First Search", "greedy.py"),
                ("A* Search", "astar.py"),
                ("IDA* (Iterative Deepening A*)", "ida_star.py"),
            ],
            "Nhóm 3 - Local Search": [
                ("Simple Hill Climbing", "simple_hill_climbing.py"),
                ("Steepest-Ascent Hill Climbing", "steepest_hill_climbing.py"),
                ("Stochastic Hill Climbing", "stochastic_hill_climbing.py"),
                ("Random-Restart Hill Climbing", "random_restart_hill.py"),
                ("Local Beam Search", "local_beam_search.py"),
                ("Simulated Annealing", "simulated_annealing.py"),
            ],
            "Nhóm 4 - Complex Environments": [
                ("AND-OR Search", "and_or_search.py"),
                ("No Observation Search", "no_observation.py"),
                ("Partially Observable Search", "partially_observable.py"),
                ("Online Search (LRTA*)", "online_search.py"),
            ],
        },
    },
    "ToMauBanDo": {
        "title": "🗺️ Tô Màu Bản Đồ",
        "subtitle": "Constraint Satisfaction Problems",
        "color": "#e17055",
        "hover": "#fab1a0",
        "icon": "🎨",
        "groups": {
            "Constraint Satisfaction Problems": [
                ("CSP Definition", "csp_definition.py"),
                ("Constraint Propagation (AC-3)", "constraint_propagation.py"),
                ("Path Consistency (PC-2)", "path_consistency.py"),
                ("Global Constraints", "global_constraints.py"),
                ("CSP Backtracking", "csp_backtracking.py"),
                ("Min-Conflicts", "min_conflicts.py"),
            ],
        },
    },
    "CoCaRo": {
        "title": "⭕ Cờ Ca Rô",
        "subtitle": "Adversarial Search - Đấu với AI",
        "color": "#fd79a8",
        "hover": "#e84393",
        "icon": "🎮",
        "groups": {
            "Adversarial Search": [
                ("Minimax", "minimax.py"),
                ("Alpha-Beta Pruning", "alpha_beta.py"),
                ("Expectimax", "expectimax.py"),
            ],
        },
    },
}


# ============================================================
# GIAO DIỆN CHÍNH
# ============================================================

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trí Tuệ Nhân Tạo - Trung Tâm Điều Khiển")
        self.geometry("1100x750")
        self.configure(bg="#0a0a1a")
        self.minsize(900, 650)

        # Đường dẫn gốc project
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.current_frame = None
        self.build_main_menu()

    # ========================================================
    # CLEAR FRAME
    # ========================================================

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    # ========================================================
    # MAIN MENU - 4 NÚT LỚN
    # ========================================================

    def build_main_menu(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self, bg="#0a0a1a")
        self.current_frame.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(self.current_frame, bg="#0a0a1a")
        header.pack(fill="x", pady=(30, 10))

        tk.Label(
            header,
            text="🧠 TRÍ TUỆ NHÂN TẠO",
            font=("Arial", 32, "bold"),
            fg="#ffffff",
            bg="#0a0a1a",
        ).pack()

        tk.Label(
            header,
            text="Chọn một chế độ để khám phá các thuật toán AI",
            font=("Arial", 14),
            fg="#636e72",
            bg="#0a0a1a",
        ).pack(pady=(5, 0))

        # Cards container
        cards_frame = tk.Frame(self.current_frame, bg="#0a0a1a")
        cards_frame.pack(expand=True, fill="both", padx=60, pady=30)

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)
        cards_frame.rowconfigure(1, weight=1)

        # 4 cards
        modes = list(ALGORITHMS.keys())
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for mode_key, (r, c) in zip(modes, positions):
            mode = ALGORITHMS[mode_key]
            self._create_card(cards_frame, mode_key, mode, r, c)

        # Footer
        tk.Label(
            self.current_frame,
            text="ARIN330585 - Trí Tuệ Nhân Tạo © 2025",
            font=("Arial", 10),
            fg="#636e72",
            bg="#0a0a1a",
        ).pack(side="bottom", pady=15)

    def _create_card(self, parent, mode_key, mode, row, col):
        color = mode["color"]

        card = tk.Frame(
            parent,
            bg="#141428",
            highlightbackground=color,
            highlightthickness=2,
            cursor="hand2",
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        inner = tk.Frame(card, bg="#141428", padx=25, pady=20)
        inner.pack(fill="both", expand=True)

        # Icon
        tk.Label(
            inner,
            text=mode["icon"],
            font=("Segoe UI Emoji", 36),
            bg="#141428",
        ).pack(anchor="w")

        # Title
        tk.Label(
            inner,
            text=mode["title"],
            font=("Arial", 20, "bold"),
            fg=color,
            bg="#141428",
        ).pack(anchor="w", pady=(8, 2))

        # Subtitle
        tk.Label(
            inner,
            text=mode["subtitle"],
            font=("Arial", 11),
            fg="#b2bec3",
            bg="#141428",
        ).pack(anchor="w")

        # Algo count
        total = sum(len(algos) for algos in mode["groups"].values())
        tk.Label(
            inner,
            text=f"{total} thuật toán",
            font=("Arial", 10),
            fg="#636e72",
            bg="#141428",
        ).pack(anchor="w", pady=(8, 0))

        # Bind click
        def on_click(event, key=mode_key):
            self.show_algorithm_list(key)

        for widget in [card, inner] + inner.winfo_children():
            widget.bind("<Button-1>", on_click)

        # Hover effects
        def on_enter(event, c=card, clr=mode["hover"]):
            c.configure(highlightbackground=clr, highlightthickness=3)

        def on_leave(event, c=card, clr=color):
            c.configure(highlightbackground=clr, highlightthickness=2)

        for widget in [card, inner] + inner.winfo_children():
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    # ========================================================
    # DANH SÁCH THUẬT TOÁN
    # ========================================================

    def show_algorithm_list(self, mode_key):
        self.clear_frame()
        mode = ALGORITHMS[mode_key]
        color = mode["color"]

        self.current_frame = tk.Frame(self, bg="#0a0a1a")
        self.current_frame.pack(fill="both", expand=True)

        # Top bar
        top = tk.Frame(self.current_frame, bg="#0f0f23")
        top.pack(fill="x")

        back_btn = tk.Label(
            top,
            text="← Quay lại",
            font=("Arial", 12, "bold"),
            fg=color,
            bg="#0f0f23",
            cursor="hand2",
            padx=15,
            pady=12,
        )
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self.build_main_menu())

        tk.Label(
            top,
            text=f"{mode['icon']}  {mode['title']}",
            font=("Arial", 18, "bold"),
            fg="#ffffff",
            bg="#0f0f23",
            pady=12,
        ).pack(side="left", padx=10)

        # Scrollable content
        canvas = tk.Canvas(self.current_frame, bg="#0a0a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#0a0a1a")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=40, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Groups
        for group_name, algos in mode["groups"].items():
            # Group header
            group_header = tk.Frame(scroll_frame, bg="#0a0a1a")
            group_header.pack(fill="x", pady=(15, 8))

            tk.Label(
                group_header,
                text=f"▸ {group_name}",
                font=("Arial", 14, "bold"),
                fg=color,
                bg="#0a0a1a",
            ).pack(anchor="w")

            # Algorithm buttons
            for algo_name, algo_file in algos:
                self._create_algo_button(
                    scroll_frame, mode_key, algo_name, algo_file, color
                )

    def _create_algo_button(self, parent, mode_key, algo_name, algo_file, color):
        btn_frame = tk.Frame(
            parent,
            bg="#16162e",
            highlightbackground="#2d2d5e",
            highlightthickness=1,
            cursor="hand2",
        )
        btn_frame.pack(fill="x", pady=3, padx=10)

        inner = tk.Frame(btn_frame, bg="#16162e", padx=15, pady=10)
        inner.pack(fill="x")

        tk.Label(
            inner,
            text=f"▶  {algo_name}",
            font=("Arial", 12),
            fg="#dfe6e9",
            bg="#16162e",
            anchor="w",
        ).pack(side="left")

        tk.Label(
            inner,
            text=algo_file,
            font=("Consolas", 10),
            fg="#636e72",
            bg="#16162e",
        ).pack(side="right")

        def on_click(event, mk=mode_key, af=algo_file):
            self.launch_algorithm(mk, af)

        for widget in [btn_frame, inner] + inner.winfo_children():
            widget.bind("<Button-1>", on_click)

        def on_enter(event, bf=btn_frame):
            bf.configure(highlightbackground=color, highlightthickness=2)
            for w in bf.winfo_children():
                w.configure(bg="#1e1e40")
                for ww in w.winfo_children():
                    ww.configure(bg="#1e1e40")

        def on_leave(event, bf=btn_frame):
            bf.configure(highlightbackground="#2d2d5e", highlightthickness=1)
            for w in bf.winfo_children():
                w.configure(bg="#16162e")
                for ww in w.winfo_children():
                    ww.configure(bg="#16162e")

        for widget in [btn_frame, inner] + inner.winfo_children():
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    # ========================================================
    # CHẠY THUẬT TOÁN
    # ========================================================

    def launch_algorithm(self, mode_key, algo_file):
        file_path = os.path.join(self.base_dir, mode_key, algo_file)

        if not os.path.exists(file_path):
            messagebox.showerror(
                "Lỗi",
                f"Không tìm thấy file:\n{file_path}\n\nVui lòng kiểm tra lại.",
            )
            return

        try:
            subprocess.Popen(
                [sys.executable, file_path],
                cwd=os.path.join(self.base_dir, mode_key),
            )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chạy file:\n{e}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
