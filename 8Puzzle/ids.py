"""
8 Puzzle - Iterative Deepening Search (IDS)
Giải bài toán 8-Puzzle bằng thuật toán tìm kiếm sâu dần.
Kết hợp tính đầy đủ của BFS với bộ nhớ thấp của DFS.
Chạy DFS lặp lại với giới hạn độ sâu tăng dần: 0, 1, 2, ...
File standalone - chạy trực tiếp: python ids.py
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import time

# ========================== TRẠNG THÁI & LOGIC ==========================

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
DEFAULT_START = (1, 2, 3, 0, 4, 6, 7, 5, 8)

# Các hướng di chuyển ô trống: (tên, delta_row, delta_col)
MOVES = [("Lên", -1, 0), ("Xuống", 1, 0), ("Trái", 0, -1), ("Phải", 0, 1)]


def manhattan(state):
    """Tính tổng khoảng cách Manhattan của trạng thái đến đích."""
    dist = 0
    for i, val in enumerate(state):
        if val == 0:
            continue
        goal_r, goal_c = divmod(val - 1, 3)
        cur_r, cur_c = divmod(i, 3)
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)
    return dist


def get_neighbors(state):
    """Trả về danh sách (tên_bước, trạng_thái_mới) khi di chuyển ô trống."""
    idx = state.index(0)
    r, c = divmod(idx, 3)
    neighbors = []
    for name, dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_idx = nr * 3 + nc
            lst = list(state)
            lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
            neighbors.append((name, tuple(lst)))
    return neighbors


def board_text(state):
    """Định dạng trạng thái thành chuỗi hiển thị bảng 3x3."""
    lines = []
    for r in range(3):
        row = []
        for c in range(3):
            val = state[r * 3 + c]
            row.append(str(val) if val != 0 else " ")
        lines.append(" | ".join(row))
    return "\n---------\n".join(lines)


# ========================== THUẬT TOÁN IDS ==========================

def _depth_limited_dfs(start, limit):
    """
    DFS giới hạn độ sâu. Hàm phụ trợ cho IDS.
    Trả về: (đường_đi hoặc None, số_nút_duyệt, có_bị_cắt_không)
    """
    if start == GOAL:
        return [start], 0, False

    stack = [(start, [start], 0)]
    visited = {start}
    explored = 0
    cutoff_occurred = False

    while stack:
        state, path, depth = stack.pop()
        explored += 1

        if state == GOAL:
            return path, explored, False

        if depth >= limit:
            cutoff_occurred = True
            continue

        for move_name, neighbor in reversed(get_neighbors(state)):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor], depth + 1))

    return None, explored, cutoff_occurred


def solve_ids(start, max_depth=80):
    """
    Tìm kiếm sâu dần (IDS).
    Lặp lại DFS với giới hạn độ sâu tăng dần: 0, 1, 2, ...
    Kết hợp ưu điểm BFS (đầy đủ, tối ưu) và DFS (bộ nhớ thấp).
    Trả về: (đường_đi, tổng_nút_duyệt, thông_tin_trace)
    """
    if start == GOAL:
        return [start], 0, ["Trạng thái ban đầu đã là đích!"]

    trace = []
    total_explored = 0

    for depth_limit in range(max_depth + 1):
        path, explored, cutoff = _depth_limited_dfs(start, depth_limit)
        total_explored += explored

        trace.append(
            f"── Giới hạn sâu = {depth_limit:3d} | "
            f"Nút duyệt lần này: {explored:6d} | "
            f"Tổng cộng: {total_explored:8d}"
        )

        if path is not None:
            trace.append(f"\n✔ Tìm thấy lời giải tại giới hạn sâu {depth_limit}!")
            trace.append(f"  Tổng nút duyệt (mọi lần lặp): {total_explored}")
            trace.append(f"  Độ dài đường đi: {len(path) - 1} bước")
            trace.append(f"  Số lần lặp DFS: {depth_limit + 1}")
            return path, total_explored, trace

        if not cutoff:
            # Đã duyệt hết không gian trạng thái mà không bị cắt
            break

    trace.append(f"\n✘ Không tìm thấy lời giải trong giới hạn {max_depth} mức!")
    trace.append(f"  Tổng nút duyệt: {total_explored}")
    return None, total_explored, trace


# ========================== GIAO DIỆN TKINTER ==========================

# Bảng màu
BG = "#1a1a2e"
PANEL = "#16213e"
ACCENT = "#0f3460"
HIGHLIGHT = "#e94560"
TRACE_BG = "#0f172a"
TRACE_FG = "#dbeafe"
TILE_NORMAL = "#0f3460"
TILE_EMPTY = "#1a1a2e"
TILE_TEXT = "#e2e8f0"
TILE_GOAL = "#10b981"
BTN_FG = "#e2e8f0"

TILE_SIZE = 70
BOARD_PAD = 20


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - IDS (Iterative Deepening Search)")
        self.root.geometry("900x650")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.start_state = DEFAULT_START
        self.current_state = self.start_state
        self.solution_path = []
        self.step_index = 0
        self.explored = 0
        self.solve_time = 0.0

        self._build_gui()
        self._draw_board(self.current_state)

    # -------------------- Xây dựng giao diện --------------------

    def _build_gui(self):
        # Tiêu đề
        title_frame = tk.Frame(self.root, bg=BG)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(
            title_frame, text="8 PUZZLE — IDS", font=("Arial", 18, "bold"),
            fg=HIGHLIGHT, bg=BG
        ).pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="Iterative Deepening Search (Tìm kiếm sâu dần)",
            font=("Arial", 10), fg="#94a3b8", bg=BG
        ).pack(side=tk.LEFT, padx=(15, 0))

        # Container chính
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ===== Panel trái: Bảng puzzle =====
        left = tk.Frame(main, bg=PANEL, bd=0, relief=tk.FLAT)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)

        tk.Label(
            left, text="Bảng trạng thái", font=("Arial", 11, "bold"),
            fg=TRACE_FG, bg=PANEL
        ).pack(pady=(10, 5))

        canvas_size = TILE_SIZE * 3 + BOARD_PAD * 2
        self.canvas = tk.Canvas(
            left, width=canvas_size, height=canvas_size,
            bg=PANEL, highlightthickness=0
        )
        self.canvas.pack(padx=15, pady=5)

        # Thông tin bước
        self.step_label = tk.Label(
            left, text="Bước: 0 / 0", font=("Arial", 11),
            fg=TRACE_FG, bg=PANEL
        )
        self.step_label.pack(pady=(10, 2))

        self.info_label = tk.Label(
            left, text="Nhấn 'Giải' để bắt đầu", font=("Arial", 10),
            fg="#94a3b8", bg=PANEL
        )
        self.info_label.pack(pady=(0, 5))

        # Nhập trạng thái
        input_frame = tk.Frame(left, bg=PANEL)
        input_frame.pack(pady=(5, 5), padx=10, fill=tk.X)

        tk.Label(
            input_frame, text="Trạng thái đầu (9 số, 0=trống):",
            font=("Arial", 9), fg="#94a3b8", bg=PANEL
        ).pack(anchor=tk.W)

        self.state_entry = tk.Entry(
            input_frame, font=("Consolas", 11), bg=TRACE_BG, fg=TRACE_FG,
            insertbackground=TRACE_FG, relief=tk.FLAT, bd=5
        )
        self.state_entry.pack(fill=tk.X, pady=(2, 0))
        self.state_entry.insert(0, ",".join(map(str, DEFAULT_START)))

        # Giới hạn độ sâu tối đa
        depth_frame = tk.Frame(left, bg=PANEL)
        depth_frame.pack(pady=(2, 5), padx=10, fill=tk.X)

        tk.Label(
            depth_frame, text="Giới hạn sâu tối đa:",
            font=("Arial", 9), fg="#94a3b8", bg=PANEL
        ).pack(side=tk.LEFT)

        self.depth_entry = tk.Entry(
            depth_frame, font=("Consolas", 11), bg=TRACE_BG, fg=TRACE_FG,
            insertbackground=TRACE_FG, relief=tk.FLAT, bd=5, width=5
        )
        self.depth_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.depth_entry.insert(0, "80")

        # Nút điều khiển
        btn_frame = tk.Frame(left, bg=PANEL)
        btn_frame.pack(pady=10, padx=10, fill=tk.X)

        btn_style = dict(
            font=("Arial", 10, "bold"), fg=BTN_FG, relief=tk.FLAT,
            bd=0, padx=10, pady=6, cursor="hand2"
        )

        self.btn_solve = tk.Button(
            btn_frame, text="⚡ Giải", bg=HIGHLIGHT, activebackground="#c73e54",
            command=self._solve, **btn_style
        )
        self.btn_solve.pack(fill=tk.X, pady=2)

        nav_frame = tk.Frame(btn_frame, bg=PANEL)
        nav_frame.pack(fill=tk.X, pady=2)

        self.btn_prev = tk.Button(
            nav_frame, text="◀ Bước trước", bg=ACCENT, activebackground="#0a2647",
            command=self._prev_step, state=tk.DISABLED, **btn_style
        )
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_next = tk.Button(
            nav_frame, text="Bước tiếp ▶", bg=ACCENT, activebackground="#0a2647",
            command=self._next_step, state=tk.DISABLED, **btn_style
        )
        self.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        self.btn_reset = tk.Button(
            btn_frame, text="↺ Reset", bg="#334155", activebackground="#475569",
            command=self._reset, **btn_style
        )
        self.btn_reset.pack(fill=tk.X, pady=2)

        # ===== Panel phải: Trace output =====
        right = tk.Frame(main, bg=PANEL, bd=0)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=0)

        tk.Label(
            right, text="Quá trình tìm kiếm (Trace)", font=("Arial", 11, "bold"),
            fg=TRACE_FG, bg=PANEL
        ).pack(pady=(10, 5), padx=10, anchor=tk.W)

        self.trace_text = scrolledtext.ScrolledText(
            right, font=("Consolas", 10), bg=TRACE_BG, fg=TRACE_FG,
            insertbackground=TRACE_FG, relief=tk.FLAT, bd=10,
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.trace_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # ===== Thanh trạng thái =====
        status = tk.Frame(self.root, bg=ACCENT, height=30)
        status.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(
            value="Sẵn sàng | Thuật toán: IDS (Iterative Deepening Search)"
        )
        tk.Label(
            status, textvariable=self.status_var, font=("Consolas", 9),
            fg=TRACE_FG, bg=ACCENT, anchor=tk.W, padx=10
        ).pack(fill=tk.X, pady=4)

    # -------------------- Vẽ bảng --------------------

    def _draw_board(self, state):
        self.canvas.delete("all")
        for i, val in enumerate(state):
            r, c = divmod(i, 3)
            x = BOARD_PAD + c * TILE_SIZE
            y = BOARD_PAD + r * TILE_SIZE

            if val == 0:
                color = TILE_EMPTY
                self.canvas.create_rectangle(
                    x, y, x + TILE_SIZE, y + TILE_SIZE,
                    fill=color, outline="#334155", width=2, dash=(4, 4)
                )
            else:
                goal_pos = val - 1
                color = TILE_GOAL if i == goal_pos else TILE_NORMAL
                self.canvas.create_rectangle(
                    x, y, x + TILE_SIZE, y + TILE_SIZE,
                    fill=color, outline="#1e293b", width=2
                )
                self.canvas.create_text(
                    x + TILE_SIZE // 2, y + TILE_SIZE // 2,
                    text=str(val), font=("Arial", 22, "bold"), fill=TILE_TEXT
                )

    # -------------------- Thêm trace --------------------

    def _append_trace(self, text):
        self.trace_text.config(state=tk.NORMAL)
        self.trace_text.insert(tk.END, text + "\n")
        self.trace_text.see(tk.END)
        self.trace_text.config(state=tk.DISABLED)

    def _clear_trace(self):
        self.trace_text.config(state=tk.NORMAL)
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.config(state=tk.DISABLED)

    # -------------------- Phân tích đầu vào --------------------

    def _parse_input(self):
        raw = self.state_entry.get().strip()
        try:
            nums = [int(x.strip()) for x in raw.replace(" ", ",").split(",") if x.strip()]
            if sorted(nums) != list(range(9)):
                raise ValueError
            return tuple(nums)
        except ValueError:
            messagebox.showerror(
                "Lỗi", "Nhập 9 số từ 0-8 (không trùng), cách nhau bằng dấu phẩy.\nVí dụ: 2,6,5,1,3,7,4,8,0"
            )
            return None

    def _parse_depth(self):
        try:
            d = int(self.depth_entry.get().strip())
            if d < 1:
                raise ValueError
            return d
        except ValueError:
            messagebox.showerror("Lỗi", "Giới hạn độ sâu phải là số nguyên dương.")
            return None

    # -------------------- Xử lý sự kiện --------------------

    def _solve(self):
        state = self._parse_input()
        if state is None:
            return
        max_depth = self._parse_depth()
        if max_depth is None:
            return

        self.start_state = state
        self.current_state = state
        self._clear_trace()
        self._append_trace("=" * 50)
        self._append_trace("  THUẬT TOÁN: IDS (Iterative Deepening Search)")
        self._append_trace("  Tìm kiếm sâu dần — DFS lặp lại")
        self._append_trace("=" * 50)
        self._append_trace(f"\nTrạng thái đầu:\n{board_text(state)}")
        self._append_trace(f"\nManhattan distance ban đầu: {manhattan(state)}")
        self._append_trace(f"Giới hạn sâu tối đa: {max_depth}")
        self._append_trace("\nBắt đầu lặp DFS với giới hạn sâu tăng dần...\n")

        self.root.update()

        t0 = time.perf_counter()
        path, explored, trace_lines = solve_ids(state, max_depth)
        t1 = time.perf_counter()
        self.solve_time = t1 - t0
        self.explored = explored

        for line in trace_lines:
            self._append_trace(line)

        if path is None:
            self._append_trace("\n✘ Không tìm được lời giải!")
            self.status_var.set(
                f"Không có lời giải | Đã duyệt: {explored} nút | Thời gian: {self.solve_time:.3f}s"
            )
            return

        self.solution_path = path
        self.step_index = 0
        self._draw_board(path[0])

        total = len(path) - 1
        self._append_trace(f"\n{'='*50}")
        self._append_trace(f"  KẾT QUẢ: {total} bước | {explored} nút (tổng) | {self.solve_time:.3f}s")
        self._append_trace(f"{'='*50}")
        self._append_trace("\nDùng 'Bước trước / Bước tiếp' để xem từng bước.\n")

        for i in range(1, len(path)):
            prev = path[i - 1]
            curr = path[i]
            blank_curr = curr.index(0)
            moved_val = prev[blank_curr]
            self._append_trace(f"Bước {i}: Di chuyển ô {moved_val}")

        self._update_nav()
        self.status_var.set(
            f"Đã giải xong | Bước: {total} | Nút duyệt (tổng): {explored} | "
            f"Thời gian: {self.solve_time:.3f}s"
        )

    def _prev_step(self):
        if self.step_index > 0:
            self.step_index -= 1
            self._draw_board(self.solution_path[self.step_index])
            self._update_nav()

    def _next_step(self):
        if self.step_index < len(self.solution_path) - 1:
            self.step_index += 1
            self._draw_board(self.solution_path[self.step_index])
            self._update_nav()

    def _reset(self):
        self.start_state = DEFAULT_START
        self.current_state = DEFAULT_START
        self.solution_path = []
        self.step_index = 0
        self.explored = 0
        self.solve_time = 0.0
        self.state_entry.delete(0, tk.END)
        self.state_entry.insert(0, ",".join(map(str, DEFAULT_START)))
        self.depth_entry.delete(0, tk.END)
        self.depth_entry.insert(0, "80")
        self._draw_board(DEFAULT_START)
        self._clear_trace()
        self.step_label.config(text="Bước: 0 / 0")
        self.info_label.config(text="Nhấn 'Giải' để bắt đầu")
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.status_var.set("Sẵn sàng | Thuật toán: IDS (Iterative Deepening Search)")

    def _update_nav(self):
        total = len(self.solution_path) - 1 if self.solution_path else 0
        self.step_label.config(text=f"Bước: {self.step_index} / {total}")

        if self.step_index == 0:
            self.info_label.config(text="Trạng thái ban đầu")
        elif self.step_index == total:
            self.info_label.config(text="✔ Trạng thái đích!")
        else:
            prev = self.solution_path[self.step_index - 1]
            curr = self.solution_path[self.step_index]
            blank_curr = curr.index(0)
            moved_val = prev[blank_curr]
            self.info_label.config(text=f"Di chuyển ô {moved_val}")

        self.btn_prev.config(state=tk.NORMAL if self.step_index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.step_index < total else tk.DISABLED)


# ========================== CHẠY CHƯƠNG TRÌNH ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
