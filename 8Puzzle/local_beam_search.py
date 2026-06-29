"""
8 Puzzle - Local Beam Search
Duy trì k=3 trạng thái đồng thời.
Mỗi bước: sinh TẤT CẢ láng giềng của k trạng thái, chọn k trạng thái tốt nhất.
Dừng khi đạt đích hoặc không cải thiện.
"""
import tkinter as tk
from tkinter import messagebox
import random

# ======================== CONSTANTS ========================
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
DEFAULT_START = (1, 2, 3, 0, 4, 6, 7, 5, 8)
MAX_STEPS = 100
K_BEAMS = 3
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
    """Tạo trạng thái giải được bằng cách xáo trộn từ GOAL."""
    state = list(GOAL)
    idx = state.index(0)
    for _ in range(random.randint(15, 40)):
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


def local_beam_search(start, k=K_BEAMS):
    """
    Local Beam Search: duy trì k trạng thái, chọn k tốt nhất từ tất cả láng giềng.
    Trả về (path_of_best, trace_lines).
    path_of_best: đường đi của beam tốt nhất (để hiển thị từng bước).
    """
    # Khởi tạo k trạng thái: start + (k-1) trạng thái ngẫu nhiên
    beams = [start]
    for _ in range(k - 1):
        beams.append(generate_random_solvable())

    # Lưu lịch sử: parent[state] = parent_state
    parent = {s: None for s in beams}
    trace = []
    trace.append(f"Khởi tạo {k} beams:")
    for i, s in enumerate(beams):
        trace.append(f"  Beam {i+1}: h={manhattan(s)} | {s}")

    best_h_prev = min(manhattan(s) for s in beams)

    for step in range(MAX_STEPS):
        # Kiểm tra đích
        for s in beams:
            if s == GOAL:
                trace.append(f"\n✅ Đạt đích tại bước {step}!")
                # Truy vết đường đi
                path = []
                cur = s
                while cur is not None:
                    path.append(cur)
                    cur = parent.get(cur)
                path.reverse()
                return path, trace

        # Sinh tất cả láng giềng
        all_successors = []
        for s in beams:
            for move, ns, nh in get_neighbors(s):
                if ns not in parent:  # tránh lặp vòng
                    all_successors.append((ns, nh, s))

        if not all_successors:
            trace.append(f"⛔ Không còn trạng thái mới nào để khám phá.")
            break

        # Sắp xếp và chọn k tốt nhất
        all_successors.sort(key=lambda x: x[1])
        new_beams = []
        for ns, nh, ps in all_successors:
            if ns not in parent and len(new_beams) < k:
                new_beams.append(ns)
                parent[ns] = ps

        if not new_beams:
            trace.append(f"⛔ Tất cả láng giềng đã được duyệt.")
            break

        beams = new_beams
        best_h = min(manhattan(s) for s in beams)
        trace.append(
            f"Bước {step+1}: best h={best_h} | "
            f"{len(all_successors)} successors → chọn {len(beams)} beams"
        )
        for i, s in enumerate(beams):
            trace.append(f"  Beam {i+1}: h={manhattan(s)}")

        # Kiểm tra cải thiện
        if best_h >= best_h_prev:
            trace.append(f"⛔ Không cải thiện (h vẫn là {best_h}). Dừng.")
            break
        best_h_prev = best_h

    # Trả về đường đi của beam tốt nhất
    best_beam = min(beams, key=manhattan)
    path = []
    cur = best_beam
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    if best_beam != GOAL:
        trace.append(f"\n⛔ Không đạt đích. Best h={manhattan(best_beam)}")
    return path, trace


# ======================== GUI ========================

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Local Beam Search")
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
            self.root, text="8 Puzzle – Local Beam Search (k=3)",
            font=("Segoe UI", 18, "bold"), fg=HIGHLIGHT, bg=BG
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
        self.path, self.trace_lines = local_beam_search(start)
        self.step_idx = 0
        self._draw_board(self.path[0])
        self._set_trace(self.trace_lines)
        h = manhattan(self.path[0])
        total = len(self.path) - 1
        reached = self.path[-1] == GOAL
        res = "Thành công ✅" if reached else "Không đạt đích ⛔"
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
        res = "Thành công ✅" if reached else "Không đạt đích ⛔"
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
