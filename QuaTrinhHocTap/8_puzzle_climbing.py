import random
import tkinter as tk
from tkinter import ttk


START = (1, 2, 3, 4, 0, 6, 7, 5, 8)
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
SIZE = 3
MAX_STEPS = 80

GOAL_POS = {value: index for index, value in enumerate(GOAL)}
MOVES = [
    ("Len", -1, 0),
    ("Xuong", 1, 0),
    ("Trai", 0, -1),
    ("Phai", 0, 1),
]


def row(index):
    return index // SIZE


def col(index):
    return index % SIZE


def manhattan(state):
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue

        goal_index = GOAL_POS[tile]
        total += abs(row(index) - row(goal_index)) + abs(col(index) - col(goal_index))

    return total


def get_neighbors(state):
    blank = state.index(0)
    blank_row = row(blank)
    blank_col = col(blank)
    neighbors = []

    for move_name, d_row, d_col in MOVES:
        next_row = blank_row + d_row
        next_col = blank_col + d_col

        if not (0 <= next_row < SIZE and 0 <= next_col < SIZE):
            continue

        next_index = next_row * SIZE + next_col
        next_state = list(state)
        next_state[blank], next_state[next_index] = next_state[next_index], next_state[blank]
        next_state = tuple(next_state)

        neighbors.append({
            "move": move_name,
            "state": next_state,
            "h": manhattan(next_state),
        })

    return neighbors


def solve_ida_star():
    bound = manhattan(START)
    visited = 0
    path = [{"state": START, "move": "Start"}]
    log = [f"Nguong ban dau = h(S) = {bound}"]

    def search(g_value, bound_limit):
        nonlocal visited
        visited += 1

        current = path[-1]["state"]
        h_value = manhattan(current)
        f_value = g_value + h_value

        if f_value > bound_limit:
            return f_value

        if current == GOAL:
            return "FOUND"

        minimum = float("inf")
        states_in_path = {item["state"] for item in path}
        neighbors = sorted(get_neighbors(current), key=lambda item: item["h"])

        for neighbor in neighbors:
            if neighbor["state"] in states_in_path:
                continue

            path.append({"state": neighbor["state"], "move": neighbor["move"]})
            result = search(g_value + 1, bound_limit)

            if result == "FOUND":
                return "FOUND"

            if result < minimum:
                minimum = result

            path.pop()

        return minimum

    while bound < 80:
        log.append(f"Dang tim voi nguong f <= {bound}")
        result = search(0, bound)

        if result == "FOUND":
            return {
                "found": True,
                "path": path[:],
                "visited": visited,
                "log": log,
                "message": f"IDA* tim thay loi giai sau {len(path) - 1} buoc.",
            }

        if result == float("inf"):
            break

        bound = result
        log.append(f"Tang nguong len {bound}")

    return {
        "found": False,
        "path": path[:],
        "visited": visited,
        "log": log,
        "message": "IDA* khong tim thay loi giai trong gioi han hien tai.",
    }


def solve_simple_hill_climbing():
    current = START
    path = [{"state": START, "move": "Start"}]
    seen = {START}
    visited = 0
    log = []

    for step in range(MAX_STEPS):
        if current == GOAL:
            return make_result(True, path, visited, log, "Leo doc don gian")

        current_h = manhattan(current)
        neighbors = get_neighbors(current)
        visited += len(neighbors)
        log.append(f"Buoc {step}: h={current_h}, xet lan luot cac hang xom.")

        next_state = None
        for neighbor in neighbors:
            if neighbor["h"] < current_h and neighbor["state"] not in seen:
                next_state = neighbor
                break

        if next_state is None:
            return {
                "found": False,
                "path": path,
                "visited": visited,
                "log": log,
                "message": "Leo doc don gian dung lai vi khong co hang xom tot hon.",
            }

        current = next_state["state"]
        seen.add(current)
        path.append({"state": current, "move": next_state["move"]})
        log.append(f"Chon {next_state['move']}, h={next_state['h']}.")

    return limit_result(path, visited, log, "Leo doc don gian")


def solve_random_hill_climbing():
    current = START
    path = [{"state": START, "move": "Start"}]
    seen = {START}
    visited = 0
    log = []

    for step in range(MAX_STEPS):
        if current == GOAL:
            return make_result(True, path, visited, log, "Leo doc ngau nhien")

        current_h = manhattan(current)
        neighbors = get_neighbors(current)
        better_neighbors = [
            neighbor
            for neighbor in neighbors
            if neighbor["h"] < current_h and neighbor["state"] not in seen
        ]
        visited += len(neighbors)
        log.append(
            f"Buoc {step}: h={current_h}, co {len(better_neighbors)} hang xom tot hon."
        )

        if not better_neighbors:
            return {
                "found": False,
                "path": path,
                "visited": visited,
                "log": log,
                "message": "Leo doc ngau nhien dung lai vi khong co hang xom tot hon.",
            }

        next_state = random.choice(better_neighbors)
        current = next_state["state"]
        seen.add(current)
        path.append({"state": current, "move": next_state["move"]})
        log.append(f"Chon ngau nhien {next_state['move']}, h={next_state['h']}.")

    return limit_result(path, visited, log, "Leo doc ngau nhien")


def solve_steepest_hill_climbing():
    current = START
    path = [{"state": START, "move": "Start"}]
    seen = {START}
    visited = 0
    log = []

    for step in range(MAX_STEPS):
        if current == GOAL:
            return make_result(True, path, visited, log, "Leo doc doc nhat")

        current_h = manhattan(current)
        all_neighbors = get_neighbors(current)
        neighbors = [neighbor for neighbor in all_neighbors if neighbor["state"] not in seen]
        visited += len(all_neighbors)
        neighbors.sort(key=lambda item: item["h"])
        log.append(f"Buoc {step}: h={current_h}, chon hang xom co h nho nhat.")

        best = neighbors[0] if neighbors else None
        if best is None or best["h"] >= current_h:
            return {
                "found": False,
                "path": path,
                "visited": visited,
                "log": log,
                "message": "Leo doc doc nhat dung lai vi trang thai tot nhat khong cai thien h.",
            }

        current = best["state"]
        seen.add(current)
        path.append({"state": current, "move": best["move"]})
        log.append(f"Chon {best['move']}, h={best['h']}.")

    return limit_result(path, visited, log, "Leo doc doc nhat")


def make_result(found, path, visited, log, algorithm_name):
    return {
        "found": found,
        "path": path,
        "visited": visited,
        "log": log,
        "message": f"{algorithm_name} tim thay dich sau {len(path) - 1} buoc.",
    }


def limit_result(path, visited, log, algorithm_name):
    return {
        "found": False,
        "path": path,
        "visited": visited,
        "log": log,
        "message": f"{algorithm_name} dung lai do vuot qua gioi han so buoc.",
    }


def board_text(state):
    lines = []
    for i in range(0, len(state), SIZE):
        row_values = ["_" if value == 0 else str(value) for value in state[i:i + SIZE]]
        lines.append(" ".join(row_values))
    return "\n".join(lines)


class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8 Puzzle - IDA* va Leo doc")
        self.geometry("900x620")
        self.minsize(760, 520)

        self.start_cells = []
        self.goal_cells = []
        self.active_button = None

        self.configure(bg="#f5f7f2")
        self.create_widgets()
        self.draw_board(self.start_cells, START)
        self.draw_board(self.goal_cells, GOAL)
        self.show_initial_text()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f7f2")
        style.configure("Panel.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("TLabel", background="#f5f7f2", foreground="#1f2933")
        style.configure("Panel.TLabel", background="#ffffff", foreground="#1f2933")
        style.configure("Title.TLabel", font=("Arial", 22, "bold"))
        style.configure("Info.TLabel", font=("Arial", 10), foreground="#64748b")
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=8)

        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)

        title = ttk.Label(root, text="8 Puzzle", style="Title.TLabel")
        title.pack(anchor="w")

        subtitle = ttk.Label(
            root,
            text="S = [1 2 3 4 0 6 7 5 8], G = [1 2 3 4 5 6 7 8 0]",
            style="Info.TLabel",
        )
        subtitle.pack(anchor="w", pady=(2, 14))

        content = ttk.Frame(root)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=0, minsize=270)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left = ttk.Frame(content, style="Panel.TFrame", padding=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ttk.Label(left, text="Trang thai ban dau", style="Panel.TLabel").pack(anchor="w")
        self.start_board = tk.Frame(left, bg="#ffffff")
        self.start_board.pack(pady=(10, 18))
        self.start_cells = self.make_board_cells(self.start_board, size=66, font_size=24)

        ttk.Label(left, text="Trang thai dich", style="Panel.TLabel").pack(anchor="w")
        self.goal_board = tk.Frame(left, bg="#ffffff")
        self.goal_board.pack(pady=(10, 0), anchor="w")
        self.goal_cells = self.make_board_cells(self.goal_board, size=44, font_size=15)

        right = ttk.Frame(content, style="Panel.TFrame", padding=14)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(5, weight=1)

        ttk.Label(right, text="Chon thuat toan", style="Panel.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        button_frame = ttk.Frame(right, style="Panel.TFrame")
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 12))
        button_frame.columnconfigure((0, 1), weight=1)

        buttons = [
            ("IDA*", solve_ida_star),
            ("Leo doc don gian", solve_simple_hill_climbing),
            ("Leo doc ngau nhien", solve_random_hill_climbing),
            ("Leo doc doc nhat", solve_steepest_hill_climbing),
        ]

        for index, (label, solver) in enumerate(buttons):
            button = ttk.Button(
                button_frame,
                text=label,
                style="Accent.TButton",
                command=lambda s=solver, name=label: self.run_solver(name, s),
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=4, pady=4)

        self.status = ttk.Label(
            right,
            text="Hay chon mot thuat toan de giai bai toan.",
            style="Panel.TLabel",
            wraplength=520,
        )
        self.status.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.stats = ttk.Label(
            right,
            text=f"So buoc: 0    So nut xet: 0    h(S): {manhattan(START)}",
            style="Panel.TLabel",
        )
        self.stats.grid(row=3, column=0, sticky="w", pady=(0, 8))

        ttk.Label(right, text="Duong di va nhat ky", style="Panel.TLabel").grid(
            row=4, column=0, sticky="w"
        )

        self.output = tk.Text(
            right,
            height=18,
            wrap="word",
            bg="#0f172a",
            fg="#dbeafe",
            insertbackground="#dbeafe",
            relief="flat",
            padx=10,
            pady=10,
            font=("Consolas", 10),
        )
        self.output.grid(row=5, column=0, sticky="nsew", pady=(8, 0))

    def make_board_cells(self, parent, size, font_size):
        cells = []
        for r_index in range(SIZE):
            parent.rowconfigure(r_index, minsize=size)
            for c_index in range(SIZE):
                parent.columnconfigure(c_index, minsize=size)
                label = tk.Label(
                    parent,
                    width=3,
                    height=1,
                    bg="#eef6f4",
                    fg="#115e59",
                    relief="ridge",
                    font=("Arial", font_size, "bold"),
                )
                label.grid(row=r_index, column=c_index, sticky="nsew", padx=3, pady=3)
                cells.append(label)
        return cells

    def draw_board(self, cells, state):
        for label, value in zip(cells, state):
            if value == 0:
                label.config(text="", bg="#dbe4ea")
            else:
                label.config(text=str(value), bg="#eef6f4")

    def show_initial_text(self):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "Trang thai ban dau:\n")
        self.output.insert(tk.END, board_text(START))
        self.output.insert(tk.END, "\n\nTrang thai dich:\n")
        self.output.insert(tk.END, board_text(GOAL))

    def run_solver(self, algorithm_name, solver):
        result = solver()
        self.status.config(text=result["message"])
        self.stats.config(
            text=(
                f"So buoc: {len(result['path']) - 1}    "
                f"So nut xet: {result['visited']}    "
                f"h(S): {manhattan(START)}"
            )
        )
        self.draw_board(self.start_cells, result["path"][-1]["state"])
        self.show_result(algorithm_name, result)

    def show_result(self, algorithm_name, result):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"{algorithm_name}\n")
        self.output.insert(tk.END, f"{result['message']}\n\n")

        for index, item in enumerate(result["path"]):
            self.output.insert(tk.END, f"Buoc {index} - {item['move']}\n")
            self.output.insert(tk.END, board_text(item["state"]))
            self.output.insert(tk.END, f"\nh = {manhattan(item['state'])}\n\n")

        self.output.insert(tk.END, "Nhat ky:\n")
        for line in result["log"]:
            self.output.insert(tk.END, f"- {line}\n")


if __name__ == "__main__":
    app = PuzzleApp()
    app.mainloop()
