"""
8 Puzzle - No Observation Search (Tìm kiếm không quan sát / Sensorless / Conformant)
Mô phỏng agent không thể quan sát trạng thái puzzle:
  - Bắt đầu với belief state = tập các trạng thái có thể
  - Áp dụng hành động hoạt động bất kể trạng thái thực
  - Theo dõi sự giảm kích thước belief state
  - Sử dụng BFS trên belief states
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
from collections import deque

# ======================== THUẬT TOÁN NO OBSERVATION SEARCH ========================

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def find_blank(state):
    """Tìm vị trí ô trống (0)"""
    return state.index(0)

def get_possible_actions(state):
    """Lấy các hành động có thể từ trạng thái"""
    blank = find_blank(state)
    r, c = blank // 3, blank % 3
    actions = []
    if r > 0: actions.append('Lên')
    if r < 2: actions.append('Xuống')
    if c > 0: actions.append('Trái')
    if c < 2: actions.append('Phải')
    return actions

def apply_action(state, action):
    """Áp dụng hành động lên trạng thái, trả về trạng thái mới hoặc None nếu không hợp lệ"""
    blank = find_blank(state)
    r, c = blank // 3, blank % 3

    if action == 'Lên' and r > 0:
        new_pos = blank - 3
    elif action == 'Xuống' and r < 2:
        new_pos = blank + 3
    elif action == 'Trái' and c > 0:
        new_pos = blank - 1
    elif action == 'Phải' and c < 2:
        new_pos = blank + 1
    else:
        return None  # Hành động không hợp lệ

    lst = list(state)
    lst[blank], lst[new_pos] = lst[new_pos], lst[blank]
    return tuple(lst)

def generate_initial_belief(start_state, num_states=6):
    """
    Tạo belief state ban đầu bằng cách thực hiện random walk từ start_state.
    Trả về tập hợp các trạng thái có thể.
    """
    belief = {start_state}
    current = start_state
    all_actions = ['Lên', 'Xuống', 'Trái', 'Phải']

    # Tạo các trạng thái gần với start_state
    queue = deque([start_state])
    visited = {start_state}

    while len(belief) < num_states and queue:
        state = queue.popleft()
        for action in all_actions:
            new_state = apply_action(state, action)
            if new_state and new_state not in visited:
                visited.add(new_state)
                belief.add(new_state)
                queue.append(new_state)
                if len(belief) >= num_states:
                    break

    return frozenset(belief)

def predict_belief(belief, action):
    """
    Dự đoán belief state sau khi thực hiện hành động.
    Áp dụng hành động lên mỗi trạng thái trong belief.
    Nếu hành động không hợp lệ cho trạng thái nào đó, giữ nguyên trạng thái đó.
    """
    new_belief = set()
    for state in belief:
        result = apply_action(state, action)
        if result is not None:
            new_belief.add(result)
        else:
            new_belief.add(state)  # Giữ nguyên nếu không thực hiện được
    return frozenset(new_belief)

def is_goal_belief(belief):
    """Kiểm tra tất cả trạng thái trong belief đều là đích"""
    return all(s == GOAL for s in belief)

def belief_heuristic(belief):
    """Heuristic cho belief state: max manhattan distance trong belief"""
    max_dist = 0
    for state in belief:
        dist = 0
        for i, val in enumerate(state):
            if val != 0:
                goal_pos = val - 1
                dist += abs(i // 3 - goal_pos // 3) + abs(i % 3 - goal_pos % 3)
        max_dist = max(max_dist, dist)
    return max_dist

def no_observation_search(initial_belief, max_steps=200):
    """
    BFS trên belief states.
    Tìm chuỗi hành động đưa TẤT CẢ trạng thái trong belief đến đích.
    """
    trace_log = []
    nodes_explored = 0

    start_time = time.time()
    trace_log.append("=" * 55)
    trace_log.append("THUẬT TOÁN NO OBSERVATION SEARCH (Sensorless)")
    trace_log.append("Agent KHÔNG thể quan sát trạng thái")
    trace_log.append("=" * 55)
    trace_log.append(f"Kích thước belief ban đầu: {len(initial_belief)}")
    trace_log.append(f"Các trạng thái có thể:")
    for i, s in enumerate(sorted(initial_belief)):
        state_str = ''.join(str(x) for x in s)
        trace_log.append(f"  Trạng thái {i+1}: {state_str}")
    trace_log.append("-" * 55)

    if is_goal_belief(initial_belief):
        trace_log.append("✓ Belief state đã là đích!")
        elapsed = time.time() - start_time
        return [], trace_log, nodes_explored, elapsed, [initial_belief]

    # BFS trên belief states
    queue = deque()
    queue.append((initial_belief, []))
    visited = {initial_belief}

    all_actions = ['Lên', 'Xuống', 'Trái', 'Phải']

    while queue and nodes_explored < max_steps:
        current_belief, actions_so_far = queue.popleft()
        nodes_explored += 1

        trace_log.append(f"\n--- Duyệt nút #{nodes_explored} ---")
        trace_log.append(f"  Kích thước belief: {len(current_belief)}")
        trace_log.append(f"  Hành động đã thực hiện: {len(actions_so_far)}")
        if actions_so_far:
            trace_log.append(f"  Chuỗi: {' → '.join(actions_so_far)}")

        for action in all_actions:
            new_belief = predict_belief(current_belief, action)

            trace_log.append(f"  Thử '{action}': belief {len(current_belief)} → {len(new_belief)} trạng thái")

            if is_goal_belief(new_belief):
                new_actions = actions_so_far + [action]
                elapsed = time.time() - start_time

                trace_log.append(f"\n{'=' * 55}")
                trace_log.append(f"✓ TÌM THẤY LỜI GIẢI!")
                trace_log.append(f"Số bước: {len(new_actions)}")
                trace_log.append(f"Chuỗi hành động: {' → '.join(new_actions)}")
                trace_log.append(f"Số nút duyệt: {nodes_explored}")
                trace_log.append(f"Thời gian: {elapsed:.4f}s")

                # Xây dựng chuỗi belief states
                belief_path = [initial_belief]
                b = initial_belief
                for a in new_actions:
                    b = predict_belief(b, a)
                    belief_path.append(b)

                trace_log.append(f"\nThay đổi kích thước belief:")
                for idx, bp in enumerate(belief_path):
                    trace_log.append(f"  Bước {idx}: {len(bp)} trạng thái")

                return new_actions, trace_log, nodes_explored, elapsed, belief_path

            if new_belief not in visited:
                visited.add(new_belief)
                queue.append((new_belief, actions_so_far + [action]))

    elapsed = time.time() - start_time
    trace_log.append(f"\n{'=' * 55}")
    trace_log.append(f"✗ Không tìm thấy lời giải trong {max_steps} bước!")
    trace_log.append(f"Thời gian: {elapsed:.4f}s")
    return None, trace_log, nodes_explored, elapsed, []


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
    BELIEF_COLOR = '#f0a500'

    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - No Observation Search")
        self.root.geometry("950x700")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.default_start = (1, 2, 3, 0, 4, 6, 7, 5, 8)
        self.current_display_state = self.default_start
        self.solution_actions = []
        self.belief_path = []
        self.step_index = 0
        self.is_solved = False

        self._build_gui()
        self._draw_board(self.current_display_state)

    def _build_gui(self):
        # Tiêu đề
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill='x', padx=15, pady=(10, 5))
        tk.Label(title_frame, text="🧩 8 Puzzle - No Observation Search",
                 font=("Segoe UI", 18, "bold"), fg=self.HIGHLIGHT, bg=self.BG).pack(side='left')
        tk.Label(title_frame, text="Agent không thể quan sát (Sensorless)",
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

        # Thông tin belief state
        self.belief_label = tk.Label(left_frame, text="Belief: chưa khởi tạo",
                                      font=("Segoe UI", 11), fg=self.BELIEF_COLOR, bg=self.PANEL)
        self.belief_label.pack()

        self.step_label = tk.Label(left_frame, text="Bước: 0/0",
                                    font=("Segoe UI", 11), fg=self.TEXT, bg=self.PANEL)
        self.step_label.pack()

        self.status_label = tk.Label(left_frame, text="Sẵn sàng",
                                      font=("Segoe UI", 10), fg=self.SUCCESS, bg=self.PANEL)
        self.status_label.pack(pady=(2, 5))

        # Nút
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

        # Ô nhập
        input_frame = tk.Frame(left_frame, bg=self.PANEL)
        input_frame.pack(fill='x', padx=15, pady=(0, 8))
        tk.Label(input_frame, text="Trạng thái đầu (VD: 1,2,3,4,0,6,7,5,8):",
                 font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.PANEL).pack(anchor='w')
        self.entry_state = tk.Entry(input_frame, font=("Consolas", 10),
                                     bg='#0d1b2a', fg=self.TEXT, insertbackground=self.TEXT,
                                     relief='flat', bd=0)
        self.entry_state.pack(fill='x', ipady=4)
        self.entry_state.insert(0, ','.join(str(x) for x in self.default_start))

        # Belief size indicator
        self.belief_bar_canvas = tk.Canvas(left_frame, width=280, height=30,
                                            bg=self.PANEL, highlightthickness=0)
        self.belief_bar_canvas.pack(padx=15, pady=(0, 10))

        # === BẢNG PHẢI ===
        right_frame = tk.Frame(main_frame, bg=self.PANEL, relief='flat', bd=0)
        right_frame.pack(side='right', fill='both', expand=True)

        tk.Label(right_frame, text="📋 Quá trình tìm kiếm Sensorless",
                 font=("Segoe UI", 13, "bold"), fg=self.TEXT, bg=self.PANEL).pack(pady=(12, 5))

        self.trace_text = scrolledtext.ScrolledText(
            right_frame, font=("Consolas", 9), bg='#0d1b2a', fg=self.TEXT,
            insertbackground=self.TEXT, relief='flat', bd=0, wrap='word',
            selectbackground=self.ACCENT)
        self.trace_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.trace_text.tag_configure('header', foreground=self.HIGHLIGHT, font=("Consolas", 10, "bold"))
        self.trace_text.tag_configure('success', foreground=self.SUCCESS)
        self.trace_text.tag_configure('info', foreground='#88aaff')
        self.trace_text.tag_configure('belief', foreground=self.BELIEF_COLOR)
        self.trace_text.tag_configure('step', foreground='#ffcc00')

    def _draw_board(self, state, unknown_positions=None):
        """Vẽ bảng puzzle, unknown_positions = set các vị trí agent không biết"""
        self.board_canvas.delete("all")
        cell_size = 90
        offset_x = 15
        offset_y = 15

        for i in range(9):
            r, c = i // 3, i % 3
            x1 = offset_x + c * cell_size
            y1 = offset_y + r * cell_size
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
                self.board_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(val), font=("Segoe UI", 24, "bold"), fill='white')

    def _draw_belief_bar(self, current_size, max_size):
        """Vẽ thanh hiển thị kích thước belief state"""
        self.belief_bar_canvas.delete("all")
        bar_width = 260
        bar_height = 20
        x0, y0 = 10, 5

        # Nền
        self.belief_bar_canvas.create_rectangle(x0, y0, x0 + bar_width, y0 + bar_height,
                                                 fill='#0d1b2a', outline='#3a3a6e')
        # Thanh tiến trình
        ratio = current_size / max(max_size, 1)
        fill_width = int(bar_width * ratio)
        color = self.SUCCESS if current_size == 1 else self.BELIEF_COLOR if ratio < 0.5 else self.HIGHLIGHT
        self.belief_bar_canvas.create_rectangle(x0, y0, x0 + fill_width, y0 + bar_height,
                                                 fill=color, outline='')
        self.belief_bar_canvas.create_text(x0 + bar_width / 2, y0 + bar_height / 2,
                                            text=f"Belief: {current_size}/{max_size}",
                                            font=("Segoe UI", 9, "bold"), fill='white')

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

        self.current_display_state = start_state
        self.status_label.config(text="Đang tìm kiếm...", fg='#ffcc00')
        self.root.update()

        # Tạo belief state ban đầu
        initial_belief = generate_initial_belief(start_state, num_states=6)

        # Chạy No Observation Search
        actions, trace_log, nodes, elapsed, belief_path = no_observation_search(initial_belief, max_steps=500)

        # Hiển thị trace
        self.trace_text.delete('1.0', tk.END)
        for line in trace_log:
            if line.startswith("="):
                self.trace_text.insert(tk.END, line + "\n", 'header')
            elif "✓" in line or "TÌM" in line:
                self.trace_text.insert(tk.END, line + "\n", 'success')
            elif "belief" in line.lower() or "Belief" in line or "Kích thước" in line:
                self.trace_text.insert(tk.END, line + "\n", 'belief')
            elif "Bước" in line or "Thời gian" in line or "Số" in line:
                self.trace_text.insert(tk.END, line + "\n", 'info')
            else:
                self.trace_text.insert(tk.END, line + "\n")

        if actions is not None:
            self.solution_actions = actions
            self.belief_path = belief_path
            self.step_index = 0

            # Xây dựng đường đi trạng thái (dùng start_state làm đại diện)
            self.state_path = [start_state]
            current = start_state
            for action in actions:
                result = apply_action(current, action)
                if result:
                    current = result
                self.state_path.append(current)

            self.status_label.config(text=f"✓ Tìm thấy! {len(actions)} bước", fg=self.SUCCESS)
            self.btn_prev.config(state='normal')
            self.btn_next.config(state='normal')
            self._update_display()
        else:
            self.status_label.config(text="✗ Không tìm được lời giải!", fg=self.HIGHLIGHT)
            self.btn_prev.config(state='disabled')
            self.btn_next.config(state='disabled')

    def _update_display(self):
        """Cập nhật hiển thị cho bước hiện tại"""
        if not self.belief_path:
            return

        idx = self.step_index
        belief = self.belief_path[idx]
        display_state = self.state_path[idx] if idx < len(self.state_path) else list(belief)[0]

        self._draw_board(display_state)
        self.step_label.config(text=f"Bước: {idx}/{len(self.solution_actions)}")

        max_belief = len(self.belief_path[0])
        self._draw_belief_bar(len(belief), max_belief)
        self.belief_label.config(text=f"Belief: {len(belief)} trạng thái có thể")

        if idx < len(self.solution_actions):
            action_text = self.solution_actions[idx]
            self.status_label.config(text=f"Hành động tiếp: {action_text}", fg='#88aaff')
        else:
            self.status_label.config(text="🎉 Đã đạt đích!", fg=self.SUCCESS)

    def _next_step(self):
        if self.step_index < len(self.solution_actions):
            self.step_index += 1
            self._update_display()

    def _prev_step(self):
        if self.step_index > 0:
            self.step_index -= 1
            self._update_display()

    def _reset(self):
        self.current_display_state = self.default_start
        self.solution_actions = []
        self.belief_path = []
        self.step_index = 0
        self.is_solved = False
        self._draw_board(self.default_start)
        self.step_label.config(text="Bước: 0/0")
        self.belief_label.config(text="Belief: chưa khởi tạo")
        self.status_label.config(text="Sẵn sàng", fg=self.SUCCESS)
        self.btn_prev.config(state='disabled')
        self.btn_next.config(state='disabled')
        self.trace_text.delete('1.0', tk.END)
        self.belief_bar_canvas.delete("all")
        self.entry_state.delete(0, tk.END)
        self.entry_state.insert(0, ','.join(str(x) for x in self.default_start))


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
