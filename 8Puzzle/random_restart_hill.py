"""
8 Puzzle - Random Restart Hill Climbing
Chạy Steepest Hill Climbing, nếu kẹt thì khởi động lại với trạng thái ngẫu nhiên.
Tối đa 10 lần khởi động lại. Tạo trạng thái ngẫu nhiên bằng cách xáo trộn từ GOAL.
"""
import tkinter as tk
from tkinter import messagebox
import random

# ======================== CONSTANTS ========================
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
DEFAULT_START = (1, 2, 3, 0, 4, 6, 7, 5, 8)
MAX_STEPS = 100
MAX_RESTARTS = 10
TILE_SIZE = 70
BOARD_PAD = 18

BG        = "#1a1a2e"
PANEL     = "#16213e"
ACCENT    = "#0f3460"
HIGHLIGHT = "#e94560"
TRACE_BG  = "#0f172a"
TRACE_FG  = "#dbeafe"
TILE_FG   = "#e2e8f0"
TILE_BG   = "#0f3460"
EMPTY_BG  = "#1a1a2e"
BTN_FG    = "#e2e8f0"

# ======================== ALGORITHM ========================

def manhattan(state):
    dist = 0
    for i, val in enumerate(state):
        if val == 0:
            continue
        goal_idx = val - 1
        r1, c1 = divmod(i, 3)
        r2, c2 = divmod(goal_idx, 3)
        dist += abs(r1 - r2) + abs(c1 - c2)
    return dist


def get_neighbors(state):
    idx = state.index(0)
    r, c = divmod(idx, 3)
    moves = []
    directions = [(-1, 0, "Lên"), (1, 0, "Xuống"), (0, -1, "Trái"), (0, 1, "Phải")]
    for dr, dc, name in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nidx = nr * 3 + nc
            lst = list(state)
            lst[idx], lst[nidx] = lst[nidx], lst[idx]
            ns = tuple(lst)
            moves.append((name, ns, manhattan(ns)))
    return moves


def generate_random_solvable():
    """Tạo trạng thái ngẫu nhiên giải được bằng cách xáo trộn từ GOAL."""
    state = list(GOAL)
    idx = state.index(0)
    num_shuffles = random.randint(20, 60)
    for _ in range(num_shuffles):
        r, c = divmod(idx, 3)
        possible = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                possible.append(nr * 3 + nc)
        nidx = random.choice(possible)
        state[idx], state[nidx] = state[nidx], state[idx]
        idx = nidx
    return tuple(state)


def steepest_climb(start, max_steps=MAX_STEPS):
    """Steepest Hill Climbing đơn lẻ – trả về (path, trace, solved)."""
    current = start
    h = manhattan(current)
    path = [current]
    trace = []

    for step in range(max_steps):
        if current == GOAL:
            trace.append(f"  ✅ Đạt đích tại bước {step}!")
            return path, trace, True

        neighbors = get_neighbors(current)
        best_move, best_state, best_h = min(neighbors, key=lambda x: x[2])

        if best_h >= h:
            trace.append(f"  ⛔ Kẹt h={h}, best neighbor h={best_h}")
            return path, trace, False

        trace.append(f"  Bước {step+1}: '{best_move}' → h={best_h}")
        current = best_state
        h = best_h
        path.append(current)

    trace.append(f"  ⛔ Đạt giới hạn {max_steps} bước.")
    return path, trace, False


def random_restart_hill_climbing(start):
    """Random Restart Hill Climbing."""
    all_trace = []
    best_path = None

    # Lần đầu dùng start gốc
    current_start = start
    for restart in range(MAX_RESTARTS + 1):
        h_start = manhattan(current_start)
        label = "Lần chạy ban đầu" if restart == 0 else f"Khởi động lại #{restart}"
        all_trace.append(f"{'='*40}")
        all_trace.append(f"{label}: start={current_start}, h={h_start}")
        all_trace.append(f"{'='*40}")

        path, trace, solved = steepest_climb(current_start)
        all_trace.extend(trace)

        if solved:
            all_trace.append(f"\n🎉 Giải thành công sau {restart} lần khởi động lại!")
            return path, all_trace, restart

        # Khởi động lại với trạng thái ngẫu nhiên
        if restart < MAX_RESTARTS:
            current_start = generate_random_solvable()
            all_trace.append(f"→ Tạo trạng thái ngẫu nhiên mới...\n")

    all_trace.append(f"\n⛔ Không giải được sau {MAX_RESTARTS} lần khởi động lại.")
    return path, all_trace, MAX_RESTARTS


# ======================== GUI ========================

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Random Restart Hill Climbing")
        self.root.geometry("900x650")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.path = []
        self.trace_lines = []
        self.step_idx = 0

        self._build_ui()
        self._draw_board(DEFAULT_START)

    def _build_ui(self):
        tk.Label(
            self.root, text="8 Puzzle – Random Restart Hill Climbing",
            font=("Segoe UI", 17, "bold"), fg=HIGHLIGHT, bg=BG
        ).pack(pady=(12, 4))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=4)

        # Left
        left = tk.Frame(body, bg=PANEL, bd=0, highlightthickness=1, highlightbackground=ACCENT)
        left.pack(side="left", padx=(0, 10), pady=4)

        tk.Label(left, text="Bảng trạng thái", font=("Segoe UI", 11, "bold"),
                 fg=TRACE_FG, bg=PANEL).pack(pady=(8, 2))

        self.canvas = tk.Canvas(
            left, width=TILE_SIZE*3 + BOARD_PAD*2,
            height=TILE_SIZE*3 + BOARD_PAD*2, bg=PANEL, highlightthickness=0
        )
        self.canvas.pack(padx=14, pady=(2, 10))

        inp_frame = tk.Frame(left, bg=PANEL)
        inp_frame.pack(pady=(0, 8))
        tk.Label(inp_frame, text="Start (vd: 1,2,3,4,0,6,7,5,8):",
                 font=("Segoe UI", 9), fg=TRACE_FG, bg=PANEL).pack()
        self.entry = tk.Entry(inp_frame, width=24, font=("Consolas", 11),
                              bg=TRACE_BG, fg=TRACE_FG, insertbackground=TRACE_FG,
                              relief="flat", bd=4)
        self.entry.insert(0, ",".join(map(str, DEFAULT_START)))
        self.entry.pack(pady=2)

        # Right
        right = tk.Frame(body, bg=PANEL, bd=0, highlightthickness=1, highlightbackground=ACCENT)
        right.pack(side="left", fill="both", expand=True, pady=4)

        btn_bar = tk.Frame(right, bg=PANEL)
        btn_bar.pack(fill="x", padx=10, pady=(10, 4))

        btn_cfg = dict(font=("Segoe UI", 10, "bold"), fg=BTN_FG, bg=ACCENT,
                       activebackground=HIGHLIGHT, activeforeground=BTN_FG,
                       relief="flat", bd=0, padx=12, pady=4, cursor="hand2")

        tk.Button(btn_bar, text="Giải", command=self._solve, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_bar, text="Bước trước", command=self._prev, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_bar, text="Bước tiếp", command=self._next, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_bar, text="Reset", command=self._reset, **btn_cfg).pack(side="left", padx=3)

        self.status_var = tk.StringVar(value="Nhấn 'Giải' để bắt đầu")
        tk.Label(right, textvariable=self.status_var, font=("Segoe UI", 10),
                 fg=HIGHLIGHT, bg=PANEL, anchor="w").pack(fill="x", padx=12, pady=(4, 2))

        tk.Label(right, text="Quá trình tìm kiếm:", font=("Segoe UI", 10, "bold"),
                 fg=TRACE_FG, bg=PANEL, anchor="w").pack(fill="x", padx=12)

        trace_frame = tk.Frame(right, bg=TRACE_BG)
        trace_frame.pack(fill="both", expand=True, padx=10, pady=(2, 10))

        self.trace_text = tk.Text(
            trace_frame, bg=TRACE_BG, fg=TRACE_FG, font=("Consolas", 10),
            relief="flat", bd=6, wrap="word", state="disabled",
            selectbackground=ACCENT, selectforeground=TRACE_FG
        )
        scrollbar = tk.Scrollbar(trace_frame, command=self.trace_text.yview,
                                 bg=ACCENT, troughcolor=TRACE_BG)
        self.trace_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.trace_text.pack(side="left", fill="both", expand=True)

    def _draw_board(self, state):
        self.canvas.delete("all")
        for i, val in enumerate(state):
            r, c = divmod(i, 3)
            x = BOARD_PAD + c * TILE_SIZE
            y = BOARD_PAD + r * TILE_SIZE
            if val == 0:
                self.canvas.create_rectangle(x, y, x+TILE_SIZE, y+TILE_SIZE,
                                             fill=EMPTY_BG, outline=ACCENT, width=2)
            else:
                self.canvas.create_rectangle(x, y, x+TILE_SIZE, y+TILE_SIZE,
                                             fill=TILE_BG, outline=ACCENT, width=2)
                self.canvas.create_text(x+TILE_SIZE//2, y+TILE_SIZE//2,
                                        text=str(val), fill=TILE_FG,
                                        font=("Segoe UI", 22, "bold"))

    def _set_trace(self, lines):
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", "end")
        self.trace_text.insert("end", "\n".join(lines))
        self.trace_text.configure(state="disabled")
        self.trace_text.see("end")

    def _parse_start(self):
        try:
            vals = list(map(int, self.entry.get().split(",")))
            assert sorted(vals) == list(range(9))
            return tuple(vals)
        except Exception:
            messagebox.showerror("Lỗi", "Trạng thái không hợp lệ!")
            return None

    def _solve(self):
        start = self._parse_start()
        if start is None:
            return
        self.path, self.trace_lines, restarts = random_restart_hill_climbing(start)
        self.step_idx = 0
        self._draw_board(self.path[0])
        self._set_trace(self.trace_lines)
        h = manhattan(self.path[0])
        total = len(self.path) - 1
        reached = self.path[-1] == GOAL
        res = f"Thành công ✅ ({restarts} restarts)" if reached else f"Thất bại ⛔ ({restarts} restarts)"
        self.status_var.set(f"Bước: 0/{total} | h={h} | {res}")

    def _prev(self):
        if not self.path or self.step_idx <= 0:
            return
        self.step_idx -= 1
        self._show_step()

    def _next(self):
        if not self.path or self.step_idx >= len(self.path) - 1:
            return
        self.step_idx += 1
        self._show_step()

    def _show_step(self):
        state = self.path[self.step_idx]
        self._draw_board(state)
        h = manhattan(state)
        total = len(self.path) - 1
        reached = self.path[-1] == GOAL
        res = "Thành công ✅" if reached else "Chưa xong"
        self.status_var.set(f"Bước: {self.step_idx}/{total} | h={h} | {res}")

    def _reset(self):
        self.path = []
        self.trace_lines = []
        self.step_idx = 0
        self.entry.delete(0, "end")
        self.entry.insert(0, ",".join(map(str, DEFAULT_START)))
        self._draw_board(DEFAULT_START)
        self._set_trace([])
        self.status_var.set("Nhấn 'Giải' để bắt đầu")


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
