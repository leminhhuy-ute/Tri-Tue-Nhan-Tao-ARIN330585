"""
8 Puzzle - AND-OR Search (Tìm kiếm AND-OR)
Mô phỏng môi trường không xác định (nondeterministic):
  - Mỗi hành động có thể có nhiều kết quả khác nhau
  - 80% di chuyển đúng ô mong muốn, 20% di chuyển ô lân cận khác
  - Nút AND: tất cả kết quả phải dẫn đến đích
  - Nút OR: ít nhất một hành động dẫn đến đích
  - Xây dựng kế hoạch có điều kiện (conditional plan)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import copy
import random

# ======================== THUẬT TOÁN AND-OR SEARCH ========================

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
DIRECTIONS = {'Lên': -3, 'Xuống': 3, 'Trái': -1, 'Phải': 1}

def tuple_to_grid(state):
    """Chuyển tuple thành lưới 3x3"""
    return [list(state[i*3:(i+1)*3]) for i in range(3)]

def grid_to_tuple(grid):
    """Chuyển lưới 3x3 thành tuple"""
    return tuple(grid[0] + grid[1] + grid[2])

def find_blank(state):
    """Tìm vị trí ô trống (0)"""
    return state.index(0)

def get_neighbors(pos):
    """Lấy các vị trí lân cận hợp lệ"""
    r, c = pos // 3, pos % 3
    neighbors = []
    if r > 0: neighbors.append(('Lên', pos - 3))
    if r < 2: neighbors.append(('Xuống', pos + 3))
    if c > 0: neighbors.append(('Trái', pos - 1))
    if c < 2: neighbors.append(('Phải', pos + 1))
    return neighbors

def apply_move(state, blank_pos, tile_pos):
    """Áp dụng di chuyển: hoán đổi ô trống với ô tại tile_pos"""
    lst = list(state)
    lst[blank_pos], lst[tile_pos] = lst[tile_pos], lst[blank_pos]
    return tuple(lst)

def get_nondeterministic_outcomes(state, action_name):
    """
    Trả về các kết quả có thể của một hành động trong môi trường không xác định.
    - Kết quả chính (80%): di chuyển ô mong muốn
    - Kết quả phụ (20%): di chuyển một ô lân cận khác (nếu có)
    """
    blank_pos = find_blank(state)
    neighbors = get_neighbors(blank_pos)

    # Tìm hành động chính
    primary_target = None
    other_targets = []
    for name, pos in neighbors:
        if name == action_name:
            primary_target = pos
        else:
            other_targets.append(pos)

    if primary_target is None:
        return []

    outcomes = []
    # Kết quả chính
    primary_state = apply_move(state, blank_pos, primary_target)
    outcomes.append(('chính', primary_state))

    # Kết quả phụ - chọn 1 ô lân cận khác (nếu có)
    if other_targets:
        alt_target = other_targets[0]  # lấy ô lân cận khác đầu tiên
        alt_state = apply_move(state, blank_pos, alt_target)
        outcomes.append(('phụ', alt_state))

    return outcomes

def manhattan_distance(state):
    """Khoảng cách Manhattan đến trạng thái đích"""
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            goal_pos = val - 1
            dist += abs(i // 3 - goal_pos // 3) + abs(i % 3 - goal_pos % 3)
    return dist

class ConditionalPlan:
    """Kế hoạch có điều kiện (conditional plan)"""
    def __init__(self, action=None, outcomes=None, is_goal=False, is_failure=False, state=None):
        self.action = action          # Hành động tại nút OR
        self.outcomes = outcomes or {} # {tên_kết_quả: ConditionalPlan con}
        self.is_goal = is_goal
        self.is_failure = is_failure
        self.state = state

    def __repr__(self):
        if self.is_goal:
            return "[ĐẠT ĐÍCH]"
        if self.is_failure:
            return "[THẤT BẠI]"
        return f"[Hành động: {self.action}, Kết quả: {list(self.outcomes.keys())}]"

def and_or_search(initial_state, depth_limit=15):
    """
    Thuật toán AND-OR Search cho 8-puzzle
    Trả về (plan, trace_log)
    """
    trace_log = []
    nodes_explored = [0]

    def or_search(state, path, depth):
        """Nút OR: chọn một hành động dẫn đến đích"""
        nodes_explored[0] += 1

        if state == GOAL:
            trace_log.append(f"  {'  ' * depth}[OR] Trạng thái đích! ✓")
            return ConditionalPlan(is_goal=True, state=state)

        if depth >= depth_limit:
            trace_log.append(f"  {'  ' * depth}[OR] Vượt giới hạn độ sâu {depth_limit}")
            return ConditionalPlan(is_failure=True, state=state)

        if state in path:
            trace_log.append(f"  {'  ' * depth}[OR] Phát hiện chu trình!")
            return ConditionalPlan(is_failure=True, state=state)

        blank_pos = find_blank(state)
        neighbors = get_neighbors(blank_pos)

        # Sắp xếp theo heuristic
        actions = []
        for name, pos in neighbors:
            new_state = apply_move(state, blank_pos, pos)
            actions.append((manhattan_distance(new_state), name))
        actions.sort()

        state_str = ''.join(str(x) for x in state)
        trace_log.append(f"  {'  ' * depth}[OR] Trạng thái: {state_str}, h={manhattan_distance(state)}")

        for _, action_name in actions:
            trace_log.append(f"  {'  ' * depth}  Thử hành động: {action_name}")
            outcomes = get_nondeterministic_outcomes(state, action_name)
            plan = and_search(outcomes, path | {state}, depth + 1, action_name)
            if plan is not None and not plan.is_failure:
                return ConditionalPlan(action=action_name, outcomes=plan.outcomes, state=state)

        trace_log.append(f"  {'  ' * depth}[OR] Không tìm được hành động phù hợp")
        return ConditionalPlan(is_failure=True, state=state)

    def and_search(outcomes, path, depth, action_name):
        """Nút AND: tất cả kết quả phải dẫn đến đích"""
        trace_log.append(f"  {'  ' * depth}[AND] Hành động '{action_name}' có {len(outcomes)} kết quả")
        result_plans = {}

        for outcome_name, outcome_state in outcomes:
            trace_log.append(f"  {'  ' * depth}  Kết quả {outcome_name}:")
            sub_plan = or_search(outcome_state, path, depth + 1)
            if sub_plan.is_failure:
                trace_log.append(f"  {'  ' * depth}  Kết quả {outcome_name} thất bại → bỏ hành động")
                return ConditionalPlan(is_failure=True)
            result_plans[outcome_name] = sub_plan

        nodes_explored[0] += 1
        return ConditionalPlan(action=action_name, outcomes=result_plans)

    start_time = time.time()
    trace_log.append("=" * 50)
    trace_log.append("THUẬT TOÁN AND-OR SEARCH")
    trace_log.append("Môi trường không xác định (Nondeterministic)")
    trace_log.append("=" * 50)
    trace_log.append(f"Trạng thái ban đầu: {initial_state}")
    trace_log.append(f"Trạng thái đích: {GOAL}")
    trace_log.append(f"Giới hạn độ sâu: {depth_limit}")
    trace_log.append("-" * 50)

    plan = or_search(initial_state, set(), 0)
    elapsed = time.time() - start_time

    trace_log.append("-" * 50)
    if not plan.is_failure:
        trace_log.append("✓ Tìm thấy kế hoạch có điều kiện!")
    else:
        trace_log.append("✗ Không tìm thấy kế hoạch!")
    trace_log.append(f"Số nút đã duyệt: {nodes_explored[0]}")
    trace_log.append(f"Thời gian: {elapsed:.4f}s")

    return plan, trace_log, nodes_explored[0], elapsed

def extract_primary_path(plan, initial_state):
    """Trích xuất đường đi chính (theo kết quả chính 80%) từ kế hoạch"""
    path = [initial_state]
    current = plan

    while current and not current.is_goal and not current.is_failure:
        if current.action is None:
            break
        # Di chuyển theo kết quả chính
        state = path[-1]
        blank_pos = find_blank(state)
        neighbors = get_neighbors(blank_pos)
        for name, pos in neighbors:
            if name == current.action:
                new_state = apply_move(state, blank_pos, pos)
                path.append(new_state)
                break

        # Đi theo nhánh chính
        if 'chính' in current.outcomes:
            current = current.outcomes['chính']
        elif current.outcomes:
            current = list(current.outcomes.values())[0]
        else:
            break

    return path

def format_plan_tree(plan, indent=0):
    """Hiển thị cây kế hoạch dạng text"""
    lines = []
    prefix = "  " * indent

    if plan.is_goal:
        lines.append(f"{prefix}✓ ĐẠT ĐÍCH")
        return lines
    if plan.is_failure:
        lines.append(f"{prefix}✗ THẤT BẠI")
        return lines

    if plan.action:
        lines.append(f"{prefix}[OR] Hành động: {plan.action}")
        if plan.outcomes:
            for outcome_name, sub_plan in plan.outcomes.items():
                lines.append(f"{prefix}  [AND] Nếu kết quả '{outcome_name}':")
                lines.extend(format_plan_tree(sub_plan, indent + 2))

    return lines


# ======================== GIAO DIỆN TKINTER ========================

class PuzzleApp:
    # Màu sắc giao diện
    BG = '#1a1a2e'
    PANEL = '#16213e'
    ACCENT = '#0f3460'
    HIGHLIGHT = '#e94560'
    TEXT = '#ffffff'
    TEXT_DIM = '#a0a0b0'
    TILE_BG = '#0f3460'
    TILE_FG = '#ffffff'
    EMPTY_BG = '#16213e'
    SUCCESS = '#4ecca3'
    AND_COLOR = '#f0a500'
    OR_COLOR = '#4ecca3'

    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - AND-OR Search")
        self.root.geometry("950x700")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.default_start = (1, 2, 3, 0, 4, 6, 7, 5, 8)
        self.current_state = self.default_start
        self.solution_path = []
        self.step_index = 0
        self.plan = None
        self.is_solved = False

        self._build_gui()
        self._draw_board(self.current_state)

    def _build_gui(self):
        # Tiêu đề
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill='x', padx=15, pady=(10, 5))
        tk.Label(title_frame, text="🧩 8 Puzzle - AND-OR Search",
                 font=("Segoe UI", 18, "bold"), fg=self.HIGHLIGHT, bg=self.BG).pack(side='left')
        tk.Label(title_frame, text="Tìm kiếm trong môi trường không xác định",
                 font=("Segoe UI", 10), fg=self.TEXT_DIM, bg=self.BG).pack(side='right')

        # Khung chính
        main_frame = tk.Frame(self.root, bg=self.BG)
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)

        # === BẢNG TRÁI: Puzzle Board ===
        left_frame = tk.Frame(main_frame, bg=self.PANEL, relief='flat', bd=0)
        left_frame.pack(side='left', fill='both', padx=(0, 10), pady=0)

        tk.Label(left_frame, text="Bảng Puzzle", font=("Segoe UI", 13, "bold"),
                 fg=self.TEXT, bg=self.PANEL).pack(pady=(12, 5))

        self.board_canvas = tk.Canvas(left_frame, width=300, height=300,
                                       bg=self.PANEL, highlightthickness=0)
        self.board_canvas.pack(padx=30, pady=10)

        # Thông tin trạng thái
        info_frame = tk.Frame(left_frame, bg=self.PANEL)
        info_frame.pack(fill='x', padx=15, pady=5)

        self.step_label = tk.Label(info_frame, text="Bước: 0/0",
                                    font=("Segoe UI", 11), fg=self.TEXT, bg=self.PANEL)
        self.step_label.pack()

        self.status_label = tk.Label(info_frame, text="Sẵn sàng",
                                      font=("Segoe UI", 10), fg=self.SUCCESS, bg=self.PANEL)
        self.status_label.pack(pady=(2, 5))

        # Nút điều khiển
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

        # Ô nhập trạng thái
        input_frame = tk.Frame(left_frame, bg=self.PANEL)
        input_frame.pack(fill='x', padx=15, pady=(0, 10))
        tk.Label(input_frame, text="Trạng thái đầu (VD: 1,2,3,4,0,6,7,5,8):",
                 font=("Segoe UI", 8), fg=self.TEXT_DIM, bg=self.PANEL).pack(anchor='w')
        self.entry_state = tk.Entry(input_frame, font=("Consolas", 10),
                                     bg='#0d1b2a', fg=self.TEXT, insertbackground=self.TEXT,
                                     relief='flat', bd=0)
        self.entry_state.pack(fill='x', ipady=4)
        self.entry_state.insert(0, ','.join(str(x) for x in self.default_start))

        # Chú thích AND-OR
        legend_frame = tk.Frame(left_frame, bg=self.PANEL)
        legend_frame.pack(fill='x', padx=15, pady=(0, 10))
        tk.Label(legend_frame, text="● OR: Chọn 1 hành động",
                 font=("Segoe UI", 9), fg=self.OR_COLOR, bg=self.PANEL).pack(anchor='w')
        tk.Label(legend_frame, text="● AND: Mọi kết quả phải OK",
                 font=("Segoe UI", 9), fg=self.AND_COLOR, bg=self.PANEL).pack(anchor='w')

        # === BẢNG PHẢI: Trace Output ===
        right_frame = tk.Frame(main_frame, bg=self.PANEL, relief='flat', bd=0)
        right_frame.pack(side='right', fill='both', expand=True, pady=0)

        tk.Label(right_frame, text="📋 Quá trình tìm kiếm AND-OR",
                 font=("Segoe UI", 13, "bold"), fg=self.TEXT, bg=self.PANEL).pack(pady=(12, 5))

        self.trace_text = scrolledtext.ScrolledText(
            right_frame, font=("Consolas", 9), bg='#0d1b2a', fg=self.TEXT,
            insertbackground=self.TEXT, relief='flat', bd=0, wrap='word',
            selectbackground=self.ACCENT)
        self.trace_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Cấu hình tag màu
        self.trace_text.tag_configure('header', foreground=self.HIGHLIGHT, font=("Consolas", 10, "bold"))
        self.trace_text.tag_configure('success', foreground=self.SUCCESS)
        self.trace_text.tag_configure('and_node', foreground=self.AND_COLOR)
        self.trace_text.tag_configure('or_node', foreground=self.OR_COLOR)
        self.trace_text.tag_configure('info', foreground='#88aaff')
        self.trace_text.tag_configure('step', foreground='#ffcc00')

    def _draw_board(self, state):
        """Vẽ bảng puzzle 3x3"""
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
                # Kiểm tra ô đã đúng vị trí chưa
                correct = (val == i + 1)
                fill = self.SUCCESS if correct else self.TILE_BG
                self.board_canvas.create_rectangle(x1, y1, x2, y2,
                    fill=fill, outline='#3a3a6e', width=2)
                self.board_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(val), font=("Segoe UI", 24, "bold"), fill='white')

    def _solve(self):
        """Giải puzzle bằng AND-OR Search"""
        # Đọc trạng thái từ ô nhập
        try:
            text = self.entry_state.get().strip()
            nums = [int(x.strip()) for x in text.split(',')]
            if sorted(nums) != list(range(9)) or len(nums) != 9:
                raise ValueError
            start_state = tuple(nums)
        except ValueError:
            messagebox.showerror("Lỗi", "Trạng thái không hợp lệ!\nNhập 9 số từ 0-8, cách nhau bởi dấu phẩy.")
            return

        self.current_state = start_state
        self.status_label.config(text="Đang tìm kiếm...", fg='#ffcc00')
        self.root.update()

        # Chạy AND-OR Search
        plan, trace_log, nodes, elapsed = and_or_search(start_state, depth_limit=15)
        self.plan = plan

        # Hiển thị trace
        self.trace_text.delete('1.0', tk.END)
        for line in trace_log:
            if line.startswith("="):
                self.trace_text.insert(tk.END, line + "\n", 'header')
            elif "[AND]" in line:
                self.trace_text.insert(tk.END, line + "\n", 'and_node')
            elif "[OR]" in line:
                self.trace_text.insert(tk.END, line + "\n", 'or_node')
            elif "✓" in line or "Tìm thấy" in line:
                self.trace_text.insert(tk.END, line + "\n", 'success')
            elif "Bước" in line or "Thời gian" in line or "Số nút" in line:
                self.trace_text.insert(tk.END, line + "\n", 'info')
            else:
                self.trace_text.insert(tk.END, line + "\n")

        if not plan.is_failure:
            # Trích xuất đường đi chính
            self.solution_path = extract_primary_path(plan, start_state)
            self.step_index = 0

            # Hiển thị cây kế hoạch
            self.trace_text.insert(tk.END, "\n" + "=" * 50 + "\n", 'header')
            self.trace_text.insert(tk.END, "CÂY KẾ HOẠCH CÓ ĐIỀU KIỆN:\n", 'header')
            self.trace_text.insert(tk.END, "=" * 50 + "\n", 'header')
            tree_lines = format_plan_tree(plan)
            for line in tree_lines[:50]:  # Giới hạn hiển thị
                if "[OR]" in line:
                    self.trace_text.insert(tk.END, line + "\n", 'or_node')
                elif "[AND]" in line:
                    self.trace_text.insert(tk.END, line + "\n", 'and_node')
                elif "✓" in line:
                    self.trace_text.insert(tk.END, line + "\n", 'success')
                else:
                    self.trace_text.insert(tk.END, line + "\n")

            # Hiển thị đường đi chính
            self.trace_text.insert(tk.END, "\n" + "=" * 50 + "\n", 'header')
            self.trace_text.insert(tk.END, f"ĐƯỜNG ĐI CHÍNH (kết quả 80%):\n", 'header')
            self.trace_text.insert(tk.END, f"Số bước: {len(self.solution_path) - 1}\n", 'info')
            for idx, st in enumerate(self.solution_path):
                state_str = ''.join(str(x) for x in st)
                self.trace_text.insert(tk.END, f"  Bước {idx}: {state_str}\n", 'step')

            self.status_label.config(text=f"✓ Tìm thấy! {len(self.solution_path)-1} bước, {nodes} nút",
                                      fg=self.SUCCESS)
            self.btn_prev.config(state='normal')
            self.btn_next.config(state='normal')
            self._draw_board(self.solution_path[0])
            self.step_label.config(text=f"Bước: 0/{len(self.solution_path)-1}")
        else:
            self.solution_path = []
            self.status_label.config(text="✗ Không tìm được kế hoạch!", fg=self.HIGHLIGHT)
            self.btn_prev.config(state='disabled')
            self.btn_next.config(state='disabled')

        self.is_solved = True

    def _next_step(self):
        """Bước tiếp theo"""
        if self.step_index < len(self.solution_path) - 1:
            self.step_index += 1
            self._draw_board(self.solution_path[self.step_index])
            self.step_label.config(text=f"Bước: {self.step_index}/{len(self.solution_path)-1}")
            if self.solution_path[self.step_index] == GOAL:
                self.status_label.config(text="🎉 Đã đạt đích!", fg=self.SUCCESS)

    def _prev_step(self):
        """Bước trước"""
        if self.step_index > 0:
            self.step_index -= 1
            self._draw_board(self.solution_path[self.step_index])
            self.step_label.config(text=f"Bước: {self.step_index}/{len(self.solution_path)-1}")

    def _reset(self):
        """Reset về trạng thái ban đầu"""
        self.current_state = self.default_start
        self.solution_path = []
        self.step_index = 0
        self.plan = None
        self.is_solved = False
        self._draw_board(self.default_start)
        self.step_label.config(text="Bước: 0/0")
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
