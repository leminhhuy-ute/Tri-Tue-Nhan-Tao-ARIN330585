# =============================================================================
# 8 Puzzle - Greedy Best-First Search
# Tìm kiếm tham lam theo heuristic Manhattan Distance
# File standalone - chạy trực tiếp: python greedy.py
# =============================================================================

import tkinter as tk
from tkinter import messagebox, scrolledtext
import heapq
import time

# ========================== CẤU HÌNH BÀI TOÁN ==========================
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GOAL_POS = {v: i for i, v in enumerate(GOAL)}  # vị trí đích của mỗi ô
DEFAULT_START = (1, 2, 3, 0, 4, 6, 7, 5, 8)

# ========================== HÀM HEURISTIC ==============================
def manhattan(state):
    """Tính tổng khoảng cách Manhattan cho tất cả các ô (trừ ô trống)."""
    dist = 0
    for i, val in enumerate(state):
        if val == 0:
            continue
        goal_i = GOAL_POS[val]
        r1, c1 = divmod(i, 3)
        r2, c2 = divmod(goal_i, 3)
        dist += abs(r1 - r2) + abs(c1 - c2)
    return dist

# ========================== SINH TRẠNG THÁI LÂN CẬN ====================
def get_neighbors(state):
    """Trả về danh sách (tên_bước, trạng_thái_mới) từ trạng thái hiện tại."""
    neighbors = []
    idx = state.index(0)
    r, c = divmod(idx, 3)
    moves = [("Lên", -1, 0), ("Xuống", 1, 0), ("Trái", 0, -1), ("Phải", 0, 1)]
    for name, dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_idx = nr * 3 + nc
            lst = list(state)
            lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
            neighbors.append((name, tuple(lst)))
    return neighbors

# ========================== ĐỊNH DẠNG BẢNG ==============================
def board_text(state):
    """Chuyển trạng thái thành chuỗi hiển thị 3x3."""
    lines = []
    for r in range(3):
        row = []
        for c in range(3):
            val = state[r * 3 + c]
            row.append(str(val) if val != 0 else " ")
        lines.append(" ".join(row))
    return "\n".join(lines)

# ========================== THUẬT TOÁN GREEDY ===========================
def greedy_search(start):
    """
    Greedy Best-First Search: luôn mở rộng nút có h(n) nhỏ nhất.
    f(n) = h(n) = manhattan(n)
    Trả về: (đường_đi, số_nút_đã_duyệt, trace_log)
    """
    if start == GOAL:
        return [start], 0, ["Trạng thái ban đầu đã là đích!"]

    h_start = manhattan(start)
    # (h, counter, state, path)
    counter = 0
    open_heap = [(h_start, counter, start, [start])]
    closed = set()
    trace = []
    nodes_explored = 0

    trace.append(f"═══ GREEDY BEST-FIRST SEARCH ═══")
    trace.append(f"Trạng thái đầu: {start}")
    trace.append(f"h(start) = {h_start}")
    trace.append(f"{'─' * 40}")

    while open_heap:
        h, _, current, path = heapq.heappop(open_heap)

        if current in closed:
            continue

        closed.add(current)
        nodes_explored += 1

        trace.append(f"[Bước {nodes_explored}] Mở rộng nút | h = {h}")
        trace.append(board_text(current))
        trace.append("")

        if current == GOAL:
            trace.append(f"✓ ĐÃ TÌM THẤY ĐÍCH!")
            trace.append(f"Số bước: {len(path) - 1}")
            trace.append(f"Số nút đã duyệt: {nodes_explored}")
            return path, nodes_explored, trace

        for move_name, neighbor in get_neighbors(current):
            if neighbor not in closed:
                h_n = manhattan(neighbor)
                counter += 1
                heapq.heappush(open_heap, (h_n, counter, neighbor, path + [neighbor]))
                trace.append(f"  → {move_name}: h = {h_n}")

        trace.append("")

    trace.append("✗ Không tìm thấy lời giải!")
    return None, nodes_explored, trace

# ========================== GIAO DIỆN TKINTER ===========================
class PuzzleApp:
    # Màu sắc giao diện
    BG = "#1a1a2e"
    PANEL = "#16213e"
    ACCENT = "#0f3460"
    HIGHLIGHT = "#e94560"
    TEXT_BG = "#0f172a"
    TEXT_FG = "#dbeafe"
    TILE_COLORS = {
        0: "#16213e",       # ô trống
        1: "#e94560",
        2: "#0f3460",
        3: "#00b4d8",
        4: "#06d6a0",
        5: "#ffd166",
        6: "#ef476f",
        7: "#118ab2",
        8: "#073b4c",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Greedy Best-First Search")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        self.start_state = DEFAULT_START
        self.solution_path = []
        self.current_step = 0
        self.nodes_explored = 0
        self.solve_time = 0.0
        self.is_solved = False

        self._build_ui()
        self._draw_board(self.start_state)

    def _build_ui(self):
        """Xây dựng giao diện."""
        # === TIÊU ĐỀ ===
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        tk.Label(
            title_frame, text="🧩 8 Puzzle — Greedy Best-First Search",
            font=("Arial", 16, "bold"), fg=self.HIGHLIGHT, bg=self.BG
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="f(n) = h(n) = Manhattan Distance",
            font=("Arial", 10), fg="#8892b0", bg=self.BG
        ).pack(side=tk.RIGHT)

        # === KHUNG CHÍNH ===
        main_frame = tk.Frame(self.root, bg=self.BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # --- Panel trái: Bảng puzzle ---
        left_panel = tk.Frame(main_frame, bg=self.PANEL, bd=0, relief=tk.FLAT)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(
            left_panel, text="Bảng Puzzle", font=("Arial", 12, "bold"),
            fg=self.TEXT_FG, bg=self.PANEL
        ).pack(pady=(15, 10))

        self.canvas = tk.Canvas(
            left_panel, width=240, height=240, bg=self.PANEL,
            highlightthickness=0
        )
        self.canvas.pack(padx=30, pady=(0, 10))

        # Nhãn bước hiện tại
        self.step_label = tk.Label(
            left_panel, text="Bước: 0 / 0", font=("Arial", 11),
            fg=self.TEXT_FG, bg=self.PANEL
        )
        self.step_label.pack(pady=(5, 5))

        # Nút điều khiển
        btn_frame = tk.Frame(left_panel, bg=self.PANEL)
        btn_frame.pack(pady=(5, 10))

        btn_style = dict(
            font=("Arial", 10, "bold"), fg="white", bg=self.ACCENT,
            activebackground=self.HIGHLIGHT, activeforeground="white",
            bd=0, padx=10, pady=5, cursor="hand2"
        )

        self.btn_solve = tk.Button(btn_frame, text="🔍 Giải", command=self._solve, **btn_style)
        self.btn_solve.grid(row=0, column=0, columnspan=2, padx=3, pady=3, sticky="ew")

        self.btn_prev = tk.Button(btn_frame, text="◀ Bước trước", command=self._prev_step, **btn_style)
        self.btn_prev.grid(row=1, column=0, padx=3, pady=3)

        self.btn_next = tk.Button(btn_frame, text="Bước tiếp ▶", command=self._next_step, **btn_style)
        self.btn_next.grid(row=1, column=1, padx=3, pady=3)

        self.btn_reset = tk.Button(
            btn_frame, text="↻ Reset", command=self._reset,
            font=("Arial", 10, "bold"), fg="white", bg=self.HIGHLIGHT,
            activebackground="#ff6b81", activeforeground="white",
            bd=0, padx=10, pady=5, cursor="hand2"
        )
        self.btn_reset.grid(row=2, column=0, columnspan=2, padx=3, pady=3, sticky="ew")

        # Nhập trạng thái
        input_frame = tk.Frame(left_panel, bg=self.PANEL)
        input_frame.pack(pady=(5, 15), padx=15)

        tk.Label(
            input_frame, text="Trạng thái đầu (9 số, 0=trống):",
            font=("Arial", 9), fg="#8892b0", bg=self.PANEL
        ).pack()

        self.entry_state = tk.Entry(
            input_frame, font=("Consolas", 11), bg=self.TEXT_BG,
            fg=self.TEXT_FG, insertbackground=self.TEXT_FG,
            relief=tk.FLAT, justify=tk.CENTER, width=22
        )
        self.entry_state.pack(pady=3)
        self.entry_state.insert(0, ",".join(map(str, DEFAULT_START)))

        self.btn_apply = tk.Button(
            input_frame, text="Áp dụng", command=self._apply_state,
            font=("Arial", 9, "bold"), fg="white", bg=self.ACCENT,
            bd=0, padx=8, pady=2, cursor="hand2"
        )
        self.btn_apply.pack(pady=3)

        # --- Panel phải: Trace output ---
        right_panel = tk.Frame(main_frame, bg=self.PANEL, bd=0)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            right_panel, text="Quá trình tìm kiếm (Trace)",
            font=("Arial", 12, "bold"), fg=self.TEXT_FG, bg=self.PANEL
        ).pack(pady=(15, 10))

        self.trace_text = scrolledtext.ScrolledText(
            right_panel, font=("Consolas", 10), bg=self.TEXT_BG,
            fg=self.TEXT_FG, insertbackground=self.TEXT_FG,
            relief=tk.FLAT, wrap=tk.WORD, state=tk.DISABLED
        )
        self.trace_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # === THANH TRẠNG THÁI ===
        status_frame = tk.Frame(self.root, bg=self.ACCENT, height=35)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame, text="Sẵn sàng — Nhấn 'Giải' để bắt đầu",
            font=("Arial", 10), fg=self.TEXT_FG, bg=self.ACCENT
        )
        self.status_label.pack(side=tk.LEFT, padx=15)

        self.stats_label = tk.Label(
            status_frame, text="",
            font=("Arial", 10), fg="#ffd166", bg=self.ACCENT
        )
        self.stats_label.pack(side=tk.RIGHT, padx=15)

    def _draw_board(self, state):
        """Vẽ bảng puzzle 3x3 trên canvas."""
        self.canvas.delete("all")
        tile_size = 70
        margin = (240 - 3 * tile_size) // 2

        for i, val in enumerate(state):
            r, c = divmod(i, 3)
            x1 = margin + c * tile_size
            y1 = margin + r * tile_size
            x2 = x1 + tile_size
            y2 = y1 + tile_size

            if val == 0:
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=self.TILE_COLORS[0],
                    outline="#2a2a4e", width=2
                )
            else:
                color = self.TILE_COLORS.get(val, self.ACCENT)
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color,
                    outline="#ffffff", width=2
                )
                self.canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text=str(val), font=("Arial", 22, "bold"), fill="white"
                )

    def _write_trace(self, text):
        """Ghi nội dung vào vùng trace."""
        self.trace_text.config(state=tk.NORMAL)
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert(tk.END, text)
        self.trace_text.see(tk.END)
        self.trace_text.config(state=tk.DISABLED)

    def _solve(self):
        """Chạy thuật toán Greedy Best-First Search."""
        self.status_label.config(text="Đang giải...")
        self.root.update()

        t0 = time.time()
        path, nodes, trace = greedy_search(self.start_state)
        t1 = time.time()
        self.solve_time = t1 - t0
        self.nodes_explored = nodes

        if path is None:
            self.status_label.config(text="Không tìm thấy lời giải!")
            self._write_trace("\n".join(trace))
            return

        self.solution_path = path
        self.current_step = 0
        self.is_solved = True

        self._draw_board(self.solution_path[0])
        self.step_label.config(text=f"Bước: 0 / {len(self.solution_path) - 1}")
        self.status_label.config(text="Đã giải xong! Dùng nút điều hướng để xem từng bước.")
        self.stats_label.config(
            text=f"Bước: {len(self.solution_path) - 1} | "
                 f"Nút duyệt: {self.nodes_explored} | "
                 f"Thời gian: {self.solve_time:.4f}s"
        )
        self._write_trace("\n".join(trace))

    def _next_step(self):
        """Chuyển sang bước tiếp theo."""
        if not self.is_solved or not self.solution_path:
            return
        if self.current_step < len(self.solution_path) - 1:
            self.current_step += 1
            self._draw_board(self.solution_path[self.current_step])
            self.step_label.config(
                text=f"Bước: {self.current_step} / {len(self.solution_path) - 1}"
            )

    def _prev_step(self):
        """Quay lại bước trước."""
        if not self.is_solved or not self.solution_path:
            return
        if self.current_step > 0:
            self.current_step -= 1
            self._draw_board(self.solution_path[self.current_step])
            self.step_label.config(
                text=f"Bước: {self.current_step} / {len(self.solution_path) - 1}"
            )

    def _reset(self):
        """Reset về trạng thái ban đầu."""
        self.solution_path = []
        self.current_step = 0
        self.is_solved = False
        self.nodes_explored = 0
        self.solve_time = 0.0
        self._draw_board(self.start_state)
        self.step_label.config(text="Bước: 0 / 0")
        self.status_label.config(text="Sẵn sàng — Nhấn 'Giải' để bắt đầu")
        self.stats_label.config(text="")
        self._write_trace("")

    def _apply_state(self):
        """Áp dụng trạng thái mới từ ô nhập."""
        try:
            raw = self.entry_state.get().strip()
            nums = [int(x.strip()) for x in raw.split(",")]
            if sorted(nums) != list(range(9)):
                raise ValueError("Phải chứa đúng các số 0-8")
            self.start_state = tuple(nums)
            self._reset()
            self._draw_board(self.start_state)
            self.status_label.config(text=f"Đã áp dụng trạng thái mới: {self.start_state}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Trạng thái không hợp lệ:\n{e}")

# ========================== CHẠY CHƯƠNG TRÌNH ===========================
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
