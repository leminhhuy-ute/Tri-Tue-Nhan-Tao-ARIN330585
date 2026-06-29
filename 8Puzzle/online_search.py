"""
8 Puzzle - Online Search / LRTA* (Learning Real-Time A*)
Mô phỏng agent không biết trước không gian trạng thái:
  - Agent chỉ phát hiện các hàng xóm khi đến thăm nút
  - Duy trì bảng H (heuristic ước lượng, cập nhật qua học)
  - Tại mỗi bước: di chuyển đến hàng xóm có f = cost + H thấp nhất
  - Cập nhật H[current] = max(H[current], 1 + min H[neighbor])
  - Hiển thị quá trình cập nhật bảng H
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import time

# ======================== THUẬT TOÁN LRTA* ========================

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def find_blank(state):
    return state.index(0)

def manhattan_distance(state):
    """Khoảng cách Manhattan đến đích"""
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            goal_pos = val - 1
            dist += abs(i // 3 - goal_pos // 3) + abs(i % 3 - goal_pos % 3)
    return dist

def get_neighbors(state):
    """Lấy các trạng thái hàng xóm + tên hành động"""
    blank = find_blank(state)
    r, c = blank // 3, blank % 3
    neighbors = []

    moves = []
    if r > 0: moves.append(('Lên', blank - 3))
    if r < 2: moves.append(('Xuống', blank + 3))
    if c > 0: moves.append(('Trái', blank - 1))
    if c < 2: moves.append(('Phải', blank + 1))

    for action, new_pos in moves:
        lst = list(state)
        lst[blank], lst[new_pos] = lst[new_pos], lst[blank]
        neighbors.append((action, tuple(lst)))

    return neighbors

def lrta_star(initial_state, max_steps=500):
    """
    Learning Real-Time A* (LRTA*)
    Agent khám phá online, cập nhật heuristic khi di chuyển.
    """
    trace_log = []
    H = {}  # Bảng heuristic đã học
    explored_states = set()  # Các trạng thái đã khám phá
    result = {}  # result[s, a] = s' - bản đồ đã học

    def get_h(state):
        """Lấy giá trị H, dùng manhattan nếu chưa có"""
        if state not in H:
            H[state] = manhattan_distance(state)
        return H[state]

    start_time = time.time()
    trace_log.append("=" * 55)
    trace_log.append("THUẬT TOÁN LRTA* (Learning Real-Time A*)")
    trace_log.append("Agent khám phá online, không biết trước bản đồ")
    trace_log.append("=" * 55)
    trace_log.append(f"Trạng thái ban đầu: {''.join(str(x) for x in initial_state)}")
    trace_log.append(f"Trạng thái đích:     {''.join(str(x) for x in GOAL)}")
    trace_log.append(f"H ban đầu: {manhattan_distance(initial_state)} (Manhattan)")
    trace_log.append("-" * 55)

    current = initial_state
    path = [current]
    actions_taken = []
    h_updates = []  # Lịch sử cập nhật H
    previous_state = None
    previous_action = None

    for step in range(max_steps):
        if current == GOAL:
            elapsed = time.time() - start_time
            trace_log.append(f"\n{'=' * 55}")
            trace_log.append(f"🎉 ĐẠT ĐÍCH sau {step} bước!")
            trace_log.append(f"Số trạng thái đã khám phá: {len(explored_states)}")
            trace_log.append(f"Số cập nhật H: {len(h_updates)}")
            trace_log.append(f"Thời gian: {elapsed:.4f}s")
            trace_log.append(f"\nBảng H cuối cùng ({len(H)} entries):")
            # Hiển thị 20 entries đầu
            sorted_h = sorted(H.items(), key=lambda x: x[1])
            for s, h in sorted_h[:20]:
                state_str = ''.join(str(x) for x in s)
                trace_log.append(f"  {state_str}: H={h}")
            if len(H) > 20:
                trace_log.append(f"  ... và {len(H)-20} entries khác")

            return path, actions_taken, trace_log, len(explored_states), elapsed, h_updates

        # Khám phá trạng thái hiện tại
        explored_states.add(current)
        state_str = ''.join(str(x) for x in current)

        # Phát hiện hàng xóm (agent chỉ biết hàng xóm khi đến)
        neighbors = get_neighbors(current)

        trace_log.append(f"\n--- Bước {step + 1} ---")
        trace_log.append(f"  Trạng thái: {state_str}")
        trace_log.append(f"  H hiện tại: {get_h(current)}")
        trace_log.append(f"  Phát hiện {len(neighbors)} hàng xóm:")

        # Ghi nhận result
        for action, neighbor in neighbors:
            result[(current, action)] = neighbor
            neighbor_str = ''.join(str(x) for x in neighbor)
            is_new = "MỚI" if neighbor not in explored_states else "đã biết"
            trace_log.append(f"    {action} → {neighbor_str} (H={get_h(neighbor)}) [{is_new}]")

        # Nếu có trạng thái trước, cập nhật result
        if previous_state is not None and previous_action is not None:
            result[(previous_state, previous_action)] = current

        # LRTA* update: H[current] = max(H[current], 1 + min H[neighbor])
        old_h = get_h(current)
        min_neighbor_h = min(get_h(n) for _, n in neighbors)
        new_h = max(old_h, 1 + min_neighbor_h)

        if new_h != old_h:
            H[current] = new_h
            h_updates.append((step, current, old_h, new_h))
            trace_log.append(f"  📈 Cập nhật H: {old_h} → {new_h} (1 + min_H_neighbor = 1 + {min_neighbor_h})")
        else:
            trace_log.append(f"  H giữ nguyên: {old_h}")

        # Chọn hàng xóm có f = 1 + H[neighbor] nhỏ nhất
        best_action = None
        best_neighbor = None
        best_f = float('inf')

        for action, neighbor in neighbors:
            f = 1 + get_h(neighbor)
            if f < best_f:
                best_f = f
                best_action = action
                best_neighbor = neighbor

        trace_log.append(f"  → Chọn: {best_action} (f = 1 + {get_h(best_neighbor)} = {best_f})")

        previous_state = current
        previous_action = best_action
        current = best_neighbor
        path.append(current)
        actions_taken.append(best_action)

    elapsed = time.time() - start_time
    trace_log.append(f"\n{'=' * 55}")
    trace_log.append(f"✗ Không đạt đích trong {max_steps} bước!")
    trace_log.append(f"Thời gian: {elapsed:.4f}s")
    return path, actions_taken, trace_log, len(explored_states), elapsed, h_updates


# ======================== GIAO DIỆN TKINTER ========================

class PuzzleApp:
    BG = '#1a1a2e'
    PANEL = '#16213e'
    ACCENT = '#0f3460'
    HIGHLIGHT = '#e94560'
    TEXT = '#ffffff'
    TEXT_DIM = '#a0a0b0'
    TILE_BG = '#0f3460'
    EMPTY_BG = '#16213e'
    SUCCESS = '#4ecca3'
    H_UPDATE_COLOR = '#f0a500'

    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Online Search (LRTA*)")
        self.root.geometry("950x700")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.default_start = (1, 2, 3, 0, 4, 6, 7, 5, 8)
        self.current_state = self.default_start
        self.solution_path = []
        self.actions_taken = []
        self.h_updates = []
        self.step_index = 0
        self.explored_at_step = {}  # step -> set of explored states

        self._build_gui()
        self._draw_board(self.current_state)

    def _build_gui(self):
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill='x', padx=15, pady=(10, 5))
        tk.Label(title_frame, text="🧩 8 Puzzle - Online Search (LRTA*)",
                 font=("Segoe UI", 17, "bold"), fg=self.HIGHLIGHT, bg=self.BG).pack(side='left')
        tk.Label(title_frame, text="Learning Real-Time A*",
                 font=("Segoe UI", 10), fg=self.TEXT_DIM, bg=self.BG).pack(side='right')

        main_frame = tk.Frame(self.root, bg=self.BG)
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)

        # === BẢNG TRÁI ===
        left_frame = tk.Frame(main_frame, bg=self.PANEL, relief='flat', bd=0)
        left_frame.pack(side='left', fill='both', padx=(0, 10))

        tk.Label(left_frame, text="Bảng Puzzle", font=("Segoe UI", 13, "bold"),
                 fg=self.TEXT, bg=self.PANEL).pack(pady=(12, 5))

        self.board_canvas = tk.Canvas(left_frame, width=300, height=300,
                                       bg=self.PANEL, highlightthickness=0)
        self.board_canvas.pack(padx=30, pady=10)

        # H value display
        self.h_label = tk.Label(left_frame, text="H(current) = --",
                                 font=("Segoe UI", 12, "bold"), fg=self.H_UPDATE_COLOR, bg=self.PANEL)
        self.h_label.pack()

        self.explored_label = tk.Label(left_frame, text="Đã khám phá: 0 trạng thái",
                                        font=("Segoe UI", 10), fg='#88aaff', bg=self.PANEL)
        self.explored_label.pack()

        self.step_label = tk.Label(left_frame, text="Bước: 0/0",
                                    font=("Segoe UI", 11), fg=self.TEXT, bg=self.PANEL)
        self.step_label.pack()

        self.status_label = tk.Label(left_frame, text="Sẵn sàng",
                                      font=("Segoe UI", 10), fg=self.SUCCESS, bg=self.PANEL)
        self.status_label.pack(pady=(2, 5))

        # Buttons
        btn_frame = tk.Frame(left_frame, bg=self.PANEL)
        btn_frame.pack(fill='x', padx=15, pady=(5, 8))

        btn_style = {'font': ("Segoe UI", 10, "bold"), 'relief': 'flat', 'bd': 0,
                     'cursor': 'hand2', 'padx': 12, 'pady': 6}

        self.btn_solve = tk.Button(btn_frame, text="🔍 Giải", bg=self.HIGHLIGHT, fg='white',
                                    command=self._solve, **btn_style)
        self.btn_solve.pack(fill='x', pady=2)

        nav_frame = tk.Frame(btn_frame, bg=self.PANEL)
        nav_frame.pack(fill='x', pady=2)
        self.btn_prev = tk.Button(nav_frame, text="◀ Bước trước", bg=self.ACCENT, fg='white',
                                   command=self._prev_step, state='disabled', **btn_style)
        self.btn_prev.pack(side='left', expand=True, fill='x', padx=(0, 2))
        self.btn_next = tk.Button(nav_frame, text="Bước tiếp ▶", bg=self.ACCENT, fg='white',
                                   command=self._next_step, state='disabled', **btn_style)
        self.btn_next.pack(side='right', expand=True, fill='x', padx=(2, 0))

        self.btn_reset = tk.Button(btn_frame, text="🔄 Reset", bg='#333355', fg='white',
                                    command=self._reset, **btn_style)
        self.btn_reset.pack(fill='x', pady=2)

        # Input
        input_frame = tk.Frame(left_frame, bg=self.PANEL)
        input_frame.pack(fill='x', padx=15, pady=(0, 8))
        tk.Label(input_frame, text="Trạng thái đầu (VD: 1,2,3,4,0,6,7,5,8):",
                 font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.PANEL).pack(anchor='w')
        self.entry_state = tk.Entry(input_frame, font=("Consolas", 10),
                                     bg='#0d1b2a', fg=self.TEXT, insertbackground=self.TEXT,
                                     relief='flat', bd=0)
        self.entry_state.pack(fill='x', ipady=4)
        self.entry_state.insert(0, ','.join(str(x) for x in self.default_start))

        # Chú thích LRTA*
        note_frame = tk.Frame(left_frame, bg=self.PANEL)
        note_frame.pack(fill='x', padx=15, pady=(0, 10))
        tk.Label(note_frame, text="LRTA*: Học heuristic qua khám phá",
                 font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.PANEL).pack(anchor='w')
        tk.Label(note_frame, text="H[s] = max(H[s], 1+min H[neighbor])",
                 font=("Consolas", 8), fg=self.H_UPDATE_COLOR, bg=self.PANEL).pack(anchor='w')

        # === BẢNG PHẢI ===
        right_frame = tk.Frame(main_frame, bg=self.PANEL, relief='flat', bd=0)
        right_frame.pack(side='right', fill='both', expand=True)

        tk.Label(right_frame, text="📋 Quá trình LRTA* & Bảng H",
                 font=("Segoe UI", 13, "bold"), fg=self.TEXT, bg=self.PANEL).pack(pady=(12, 5))

        self.trace_text = scrolledtext.ScrolledText(
            right_frame, font=("Consolas", 9), bg='#0d1b2a', fg=self.TEXT,
            insertbackground=self.TEXT, relief='flat', bd=0, wrap='word',
            selectbackground=self.ACCENT)
        self.trace_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.trace_text.tag_configure('header', foreground=self.HIGHLIGHT, font=("Consolas", 10, "bold"))
        self.trace_text.tag_configure('success', foreground=self.SUCCESS)
        self.trace_text.tag_configure('info', foreground='#88aaff')
        self.trace_text.tag_configure('h_update', foreground=self.H_UPDATE_COLOR)
        self.trace_text.tag_configure('step', foreground='#ffcc00')
        self.trace_text.tag_configure('explore', foreground='#bb86fc')

    def _draw_board(self, state, h_value=None):
        """Vẽ bảng puzzle"""
        self.board_canvas.delete("all")
        cell_size = 90
        ox, oy = 15, 15

        for i in range(9):
            r, c = i // 3, i % 3
            x1 = ox + c * cell_size
            y1 = oy + r * cell_size
            x2 = x1 + cell_size - 4
            y2 = y1 + cell_size - 4

            val = state[i]
            if val == 0:
                self.board_canvas.create_rectangle(x1, y1, x2, y2,
                    fill=self.EMPTY_BG, outline='#2a2a4e', width=2)
            else:
                correct = (val == i + 1)
                fill = self.SUCCESS if correct else self.TILE_BG
                self.board_canvas.create_rectangle(x1, y1, x2, y2,
                    fill=fill, outline='#3a3a6e', width=2)
                self.board_canvas.create_text((x1+x2)/2, (y1+y2)/2,
                    text=str(val), font=("Segoe UI", 24, "bold"), fill='white')

    def _solve(self):
        try:
            text = self.entry_state.get().strip()
            nums = [int(x.strip()) for x in text.split(',')]
            if sorted(nums) != list(range(9)) or len(nums) != 9:
                raise ValueError
            start_state = tuple(nums)
        except ValueError:
            messagebox.showerror("Lỗi", "Trạng thái không hợp lệ!")
            return

        self.current_state = start_state
        self.status_label.config(text="Đang chạy LRTA*...", fg='#ffcc00')
        self.root.update()

        path, actions, trace_log, explored_count, elapsed, h_updates = lrta_star(start_state, max_steps=500)

        self.solution_path = path
        self.actions_taken = actions
        self.h_updates = h_updates
        self.step_index = 0

        # Tính explored tại mỗi bước
        explored_set = set()
        self.explored_at_step = {}
        for i, s in enumerate(path):
            explored_set.add(s)
            self.explored_at_step[i] = len(explored_set)

        # Hiển thị trace
        self.trace_text.delete('1.0', tk.END)
        for line in trace_log:
            if line.startswith("="):
                self.trace_text.insert(tk.END, line + "\n", 'header')
            elif "📈" in line or "Cập nhật H" in line:
                self.trace_text.insert(tk.END, line + "\n", 'h_update')
            elif "✓" in line or "🎉" in line or "ĐẠT ĐÍCH" in line:
                self.trace_text.insert(tk.END, line + "\n", 'success')
            elif "MỚI" in line:
                self.trace_text.insert(tk.END, line + "\n", 'explore')
            elif "Bước" in line and "---" in line:
                self.trace_text.insert(tk.END, line + "\n", 'step')
            elif "Chọn" in line:
                self.trace_text.insert(tk.END, line + "\n", 'info')
            else:
                self.trace_text.insert(tk.END, line + "\n")

        if path and path[-1] == GOAL:
            self.status_label.config(
                text=f"✓ Đạt đích! {len(actions)} bước, khám phá {explored_count} trạng thái",
                fg=self.SUCCESS)
        else:
            self.status_label.config(text=f"✗ Chưa đạt đích sau {len(actions)} bước", fg=self.HIGHLIGHT)

        self.btn_prev.config(state='normal')
        self.btn_next.config(state='normal')
        self._update_display()

    def _update_display(self):
        if not self.solution_path:
            return

        idx = self.step_index
        state = self.solution_path[idx]
        h_val = manhattan_distance(state)

        self._draw_board(state)
        self.step_label.config(text=f"Bước: {idx}/{len(self.actions_taken)}")
        self.h_label.config(text=f"H(current) = {h_val}")

        explored_count = self.explored_at_step.get(idx, 0)
        self.explored_label.config(text=f"Đã khám phá: {explored_count} trạng thái")

        if idx < len(self.actions_taken):
            self.status_label.config(text=f"Hành động: {self.actions_taken[idx]}", fg='#88aaff')
        elif state == GOAL:
            self.status_label.config(text="🎉 Đã đạt đích!", fg=self.SUCCESS)

    def _next_step(self):
        if self.step_index < len(self.solution_path) - 1:
            self.step_index += 1
            self._update_display()

    def _prev_step(self):
        if self.step_index > 0:
            self.step_index -= 1
            self._update_display()

    def _reset(self):
        self.current_state = self.default_start
        self.solution_path = []
        self.actions_taken = []
        self.h_updates = []
        self.step_index = 0
        self.explored_at_step = {}
        self._draw_board(self.default_start)
        self.step_label.config(text="Bước: 0/0")
        self.h_label.config(text="H(current) = --")
        self.explored_label.config(text="Đã khám phá: 0 trạng thái")
        self.status_label.config(text="Sẵn sàng", fg=self.SUCCESS)
        self.btn_prev.config(state='disabled')
        self.btn_next.config(state='disabled')
        self.trace_text.delete('1.0', tk.END)
        self.entry_state.delete(0, tk.END)
        self.entry_state.insert(0, ','.join(str(x) for x in self.default_start))


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
