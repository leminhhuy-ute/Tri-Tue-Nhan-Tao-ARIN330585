"""
8 Puzzle - Partially Observable Search (Tìm kiếm quan sát một phần)
Mô phỏng agent chỉ quan sát được một phần trạng thái:
  - Agent chỉ thấy các ô cùng hàng/cột với ô trống
  - Belief state cập nhật dựa trên quan sát
  - Hiển thị ô nào agent thấy/không thấy
  - Dùng A* trên belief states với heuristic = min manhattan
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import heapq
from collections import deque

# ======================== THUẬT TOÁN PARTIALLY OBSERVABLE SEARCH ========================

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def find_blank(state):
    return state.index(0)

def get_observable_positions(state):
    """
    Trả về tập vị trí mà agent có thể quan sát.
    Agent thấy: các ô cùng hàng và cùng cột với ô trống.
    """
    blank = find_blank(state)
    r, c = blank // 3, blank % 3
    observable = set()
    # Cùng hàng
    for cc in range(3):
        observable.add(r * 3 + cc)
    # Cùng cột
    for rr in range(3):
        observable.add(rr * 3 + c)
    return observable

def get_observation(state):
    """
    Tạo observation từ trạng thái.
    Trả về dict {vị_trí: giá_trị} cho các vị trí quan sát được.
    """
    observable = get_observable_positions(state)
    obs = {}
    for pos in observable:
        obs[pos] = state[pos]
    return obs

def observation_matches(state, observation):
    """Kiểm tra trạng thái có khớp với observation không"""
    for pos, val in observation.items():
        if state[pos] != val:
            return False
    return True

def apply_action(state, action):
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
        return None

    lst = list(state)
    lst[blank], lst[new_pos] = lst[new_pos], lst[blank]
    return tuple(lst)

def get_possible_actions(state):
    blank = find_blank(state)
    r, c = blank // 3, blank % 3
    actions = []
    if r > 0: actions.append('Lên')
    if r < 2: actions.append('Xuống')
    if c > 0: actions.append('Trái')
    if c < 2: actions.append('Phải')
    return actions

def manhattan_distance(state):
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            goal_pos = val - 1
            dist += abs(i // 3 - goal_pos // 3) + abs(i % 3 - goal_pos % 3)
    return dist

def generate_initial_belief(start_state, num_states=6):
    """Tạo belief state ban đầu từ các trạng thái gần start_state"""
    belief = {start_state}
    queue = deque([start_state])
    visited = {start_state}
    all_actions = ['Lên', 'Xuống', 'Trái', 'Phải']

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
    """Dự đoán belief state sau hành động"""
    new_belief = set()
    for state in belief:
        result = apply_action(state, action)
        if result is not None:
            new_belief.add(result)
        else:
            new_belief.add(state)
    return frozenset(new_belief)

def update_belief_with_observation(belief, observation):
    """Cập nhật belief state dựa trên observation mới"""
    updated = set()
    for state in belief:
        if observation_matches(state, observation):
            updated.add(state)
    return frozenset(updated) if updated else belief

def belief_heuristic_min_manhattan(belief):
    """Heuristic: min manhattan distance trong belief"""
    return min(manhattan_distance(s) for s in belief)

def is_goal_belief(belief):
    return all(s == GOAL for s in belief)

def partially_observable_search(start_state, initial_belief, max_nodes=1000):
    """
    A* trên belief states với partial observation.
    Sau mỗi hành động, agent nhận observation và cập nhật belief.
    """
    trace_log = []
    nodes_explored = 0

    start_time = time.time()
    trace_log.append("=" * 55)
    trace_log.append("THUẬT TOÁN PARTIALLY OBSERVABLE SEARCH")
    trace_log.append("Agent chỉ thấy ô cùng hàng/cột với ô trống")
    trace_log.append("=" * 55)
    trace_log.append(f"Kích thước belief ban đầu: {len(initial_belief)}")

    # Quan sát ban đầu
    init_obs = get_observation(start_state)
    observable_pos = get_observable_positions(start_state)
    trace_log.append(f"Vị trí quan sát được: {sorted(observable_pos)}")
    trace_log.append(f"Observation: {dict(sorted(init_obs.items()))}")

    # Cập nhật belief với observation ban đầu
    current_belief = update_belief_with_observation(initial_belief, init_obs)
    trace_log.append(f"Belief sau observation: {len(current_belief)} trạng thái")
    trace_log.append("-" * 55)

    if is_goal_belief(current_belief):
        elapsed = time.time() - start_time
        trace_log.append("✓ Đã ở đích!")
        return [], trace_log, 0, elapsed, [(current_belief, observable_pos, start_state)]

    # A* search trên belief states
    counter = 0
    # (f, counter, g, belief, actual_state, actions, history)
    h0 = belief_heuristic_min_manhattan(current_belief)
    start_item = (h0, counter, 0, current_belief, start_state, [], [(current_belief, observable_pos, start_state)])
    open_set = [start_item]
    visited = {current_belief}

    all_actions = ['Lên', 'Xuống', 'Trái', 'Phải']

    while open_set and nodes_explored < max_nodes:
        f, _, g, belief, actual_state, actions_so_far, history = heapq.heappop(open_set)
        nodes_explored += 1

        trace_log.append(f"\n--- Nút #{nodes_explored}, f={f}, g={g} ---")
        trace_log.append(f"  Belief: {len(belief)} trạng thái")

        for action in all_actions:
            # Dự đoán belief mới
            new_belief = predict_belief(belief, action)

            # Thực hiện hành động trên trạng thái thực
            new_actual = apply_action(actual_state, action)
            if new_actual is None:
                continue

            # Nhận observation mới
            new_obs = get_observation(new_actual)
            new_observable = get_observable_positions(new_actual)

            # Cập nhật belief với observation
            filtered_belief = update_belief_with_observation(new_belief, new_obs)

            trace_log.append(f"  '{action}': belief {len(belief)}→{len(new_belief)}→{len(filtered_belief)} (sau obs)")

            new_actions = actions_so_far + [action]
            new_history = history + [(filtered_belief, new_observable, new_actual)]

            if is_goal_belief(filtered_belief):
                elapsed = time.time() - start_time
                trace_log.append(f"\n{'=' * 55}")
                trace_log.append(f"✓ TÌM THẤY LỜI GIẢI!")
                trace_log.append(f"Số bước: {len(new_actions)}")
                trace_log.append(f"Hành động: {' → '.join(new_actions)}")
                trace_log.append(f"Số nút duyệt: {nodes_explored}")
                trace_log.append(f"Thời gian: {elapsed:.4f}s")

                trace_log.append(f"\nThay đổi belief:")
                for idx, (b, obs_pos, st) in enumerate(new_history):
                    obs_count = len(obs_pos)
                    trace_log.append(f"  Bước {idx}: belief={len(b)}, quan sát {obs_count} ô")

                return new_actions, trace_log, nodes_explored, elapsed, new_history

            if filtered_belief not in visited:
                visited.add(filtered_belief)
                new_g = g + 1
                new_h = belief_heuristic_min_manhattan(filtered_belief)
                new_f = new_g + new_h
                counter += 1
                heapq.heappush(open_set, (new_f, counter, new_g, filtered_belief, new_actual, new_actions, new_history))

    elapsed = time.time() - start_time
    trace_log.append(f"\n{'=' * 55}")
    trace_log.append(f"✗ Không tìm thấy lời giải trong {max_nodes} nút!")
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
    OBSERVABLE_BG = '#1a5276'
    HIDDEN_BG = '#2c2c3e'
    BELIEF_COLOR = '#f0a500'

    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Partially Observable Search")
        self.root.geometry("950x700")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.default_start = (1, 2, 3, 0, 4, 6, 7, 5, 8)
        self.current_state = self.default_start
        self.solution_actions = []
        self.history = []
        self.step_index = 0

        self._build_gui()
        self._draw_board(self.current_state)

    def _build_gui(self):
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill='x', padx=15, pady=(10, 5))
        tk.Label(title_frame, text="🧩 8 Puzzle - Partially Observable Search",
                 font=("Segoe UI", 17, "bold"), fg=self.HIGHLIGHT, bg=self.BG).pack(side='left')
        tk.Label(title_frame, text="Quan sát một phần",
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

        # Legend
        legend_frame = tk.Frame(left_frame, bg=self.PANEL)
        legend_frame.pack(fill='x', padx=15)
        tk.Label(legend_frame, text="🔵 Quan sát được (cùng hàng/cột blank)",
                 font=("Segoe UI", 8), fg='#5dade2', bg=self.PANEL).pack(anchor='w')
        tk.Label(legend_frame, text="⬛ Không quan sát được (ẩn)",
                 font=("Segoe UI", 8), fg='#777', bg=self.PANEL).pack(anchor='w')
        tk.Label(legend_frame, text="🟢 Đúng vị trí",
                 font=("Segoe UI", 8), fg=self.SUCCESS, bg=self.PANEL).pack(anchor='w')

        # Info
        self.belief_label = tk.Label(left_frame, text="Belief: --",
                                      font=("Segoe UI", 11), fg=self.BELIEF_COLOR, bg=self.PANEL)
        self.belief_label.pack(pady=(5, 0))

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
        input_frame.pack(fill='x', padx=15, pady=(0, 10))
        tk.Label(input_frame, text="Trạng thái đầu (VD: 1,2,3,4,0,6,7,5,8):",
                 font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.PANEL).pack(anchor='w')
        self.entry_state = tk.Entry(input_frame, font=("Consolas", 10),
                                     bg='#0d1b2a', fg=self.TEXT, insertbackground=self.TEXT,
                                     relief='flat', bd=0)
        self.entry_state.pack(fill='x', ipady=4)
        self.entry_state.insert(0, ','.join(str(x) for x in self.default_start))

        # === BẢNG PHẢI ===
        right_frame = tk.Frame(main_frame, bg=self.PANEL, relief='flat', bd=0)
        right_frame.pack(side='right', fill='both', expand=True)

        tk.Label(right_frame, text="📋 Quá trình tìm kiếm Partially Observable",
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
        self.trace_text.tag_configure('obs', foreground='#5dade2')

    def _draw_board(self, state, observable_positions=None):
        """Vẽ bảng puzzle với highlight cho ô quan sát được"""
        self.board_canvas.delete("all")
        cell_size = 90
        ox, oy = 15, 15

        if observable_positions is None:
            observable_positions = set(range(9))  # Mặc định thấy hết

        for i in range(9):
            r, c = i // 3, i % 3
            x1 = ox + c * cell_size
            y1 = oy + r * cell_size
            x2 = x1 + cell_size - 4
            y2 = y1 + cell_size - 4

            val = state[i]
            is_observable = i in observable_positions

            if val == 0:
                self.board_canvas.create_rectangle(x1, y1, x2, y2,
                    fill=self.EMPTY_BG, outline='#5dade2' if is_observable else '#2a2a4e', width=3 if is_observable else 2)
                self.board_canvas.create_text((x1+x2)/2, (y1+y2)/2,
                    text="□", font=("Segoe UI", 20), fill='#5dade2')
            elif is_observable:
                correct = (val == i + 1)
                fill = self.SUCCESS if correct else self.OBSERVABLE_BG
                self.board_canvas.create_rectangle(x1, y1, x2, y2,
                    fill=fill, outline='#5dade2', width=3)
                self.board_canvas.create_text((x1+x2)/2, (y1+y2)/2,
                    text=str(val), font=("Segoe UI", 24, "bold"), fill='white')
            else:
                # Ô ẩn - agent không thấy
                self.board_canvas.create_rectangle(x1, y1, x2, y2,
                    fill=self.HIDDEN_BG, outline='#444466', width=2)
                self.board_canvas.create_text((x1+x2)/2, (y1+y2)/2,
                    text="?", font=("Segoe UI", 24, "bold"), fill='#666688')

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
        self.status_label.config(text="Đang tìm kiếm...", fg='#ffcc00')
        self.root.update()

        initial_belief = generate_initial_belief(start_state, num_states=6)
        actions, trace_log, nodes, elapsed, history = partially_observable_search(
            start_state, initial_belief, max_nodes=2000)

        self.trace_text.delete('1.0', tk.END)
        for line in trace_log:
            if line.startswith("="):
                self.trace_text.insert(tk.END, line + "\n", 'header')
            elif "✓" in line or "TÌM" in line:
                self.trace_text.insert(tk.END, line + "\n", 'success')
            elif "belief" in line.lower() or "Belief" in line:
                self.trace_text.insert(tk.END, line + "\n", 'belief')
            elif "quan sát" in line.lower() or "Observation" in line:
                self.trace_text.insert(tk.END, line + "\n", 'obs')
            elif "Bước" in line or "Thời gian" in line:
                self.trace_text.insert(tk.END, line + "\n", 'info')
            else:
                self.trace_text.insert(tk.END, line + "\n")

        if actions is not None:
            self.solution_actions = actions
            self.history = history
            self.step_index = 0
            self.status_label.config(text=f"✓ Tìm thấy! {len(actions)} bước, {nodes} nút",
                                      fg=self.SUCCESS)
            self.btn_prev.config(state='normal')
            self.btn_next.config(state='normal')
            self._update_display()
        else:
            self.status_label.config(text="✗ Không tìm được!", fg=self.HIGHLIGHT)

    def _update_display(self):
        if not self.history:
            return
        idx = self.step_index
        belief, obs_positions, actual_state = self.history[idx]
        self._draw_board(actual_state, obs_positions)
        self.step_label.config(text=f"Bước: {idx}/{len(self.solution_actions)}")
        self.belief_label.config(text=f"Belief: {len(belief)} trạng thái | Quan sát: {len(obs_positions)} ô")

        if idx < len(self.solution_actions):
            self.status_label.config(text=f"Hành động: {self.solution_actions[idx]}", fg='#88aaff')
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
        self.current_state = self.default_start
        self.solution_actions = []
        self.history = []
        self.step_index = 0
        self._draw_board(self.default_start)
        self.step_label.config(text="Bước: 0/0")
        self.belief_label.config(text="Belief: --")
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
