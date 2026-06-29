# =============================================================================
# CỜ CARO 3x3 (Tic-Tac-Toe) - Thuật toán EXPECTIMAX
# =============================================================================
# Trò chơi Cờ Caro 3x3 với AI sử dụng thuật toán Expectimax
# Đối thủ được mô hình hóa xác suất: 70% chơi tối ưu, 30% chơi ngẫu nhiên
# Người chơi: X (đi trước) | AI: O (đi sau)
# Điều kiện thắng: 3 ô liên tiếp (ngang, dọc, chéo)
# =============================================================================

import tkinter as tk
from tkinter import font as tkfont
import time

# =============================================================================
# HẰNG SỐ VÀ CẤU HÌNH GIAO DIỆN
# =============================================================================
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 800
BG_COLOR = "#1b1b2f"          # Màu nền chính (tối sang trọng)
BOARD_BG = "#162447"           # Màu nền bàn cờ
X_COLOR = "#e43f5a"            # Màu quân X (đỏ hồng)
O_COLOR = "#1f4068"            # Màu quân O (xanh đậm)
HOVER_COLOR = "#1e3a5f"        # Màu khi di chuột vào ô trống
BUTTON_BG = "#0f3460"          # Màu nền các nút điều khiển
TEXT_COLOR = "#e0e0e0"         # Màu chữ chính
ACCENT_COLOR = "#e43f5a"       # Màu nhấn mạnh
WIN_COLOR = "#00d2ff"          # Màu hiển thị khi thắng
CELL_SIZE = 150                # Kích thước mỗi ô (pixel)

HUMAN = 'X'   # Người chơi
AI = 'O'       # Máy

# Xác suất mô hình đối thủ
PROB_OPTIMAL = 0.7   # 70% đối thủ chơi nước đi tối ưu
PROB_RANDOM = 0.3    # 30% đối thủ chơi ngẫu nhiên

# =============================================================================
# HÀM ĐÁNH GIÁ VÀ KIỂM TRA TRẠNG THÁI BÀN CỜ
# =============================================================================

def evaluate(board):
    """
    Hàm đánh giá trạng thái bàn cờ.
    Trả về:
        +10 nếu AI (O) thắng
        -10 nếu Người chơi (X) thắng
        0 nếu hòa hoặc chưa kết thúc
    """
    # Kiểm tra các hàng ngang
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != '':
            if board[row][0] == AI:
                return +10
            else:
                return -10

    # Kiểm tra các cột dọc
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '':
            if board[0][col] == AI:
                return +10
            else:
                return -10

    # Kiểm tra đường chéo chính (trái trên -> phải dưới)
    if board[0][0] == board[1][1] == board[2][2] != '':
        if board[0][0] == AI:
            return +10
        else:
            return -10

    # Kiểm tra đường chéo phụ (phải trên -> trái dưới)
    if board[0][2] == board[1][1] == board[2][0] != '':
        if board[0][2] == AI:
            return +10
        else:
            return -10

    # Không ai thắng
    return 0


def is_terminal(board):
    """
    Kiểm tra trạng thái kết thúc của trò chơi.
    Trả về True nếu có người thắng hoặc bàn cờ đầy.
    """
    if evaluate(board) != 0:
        return True

    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                return False
    return True


def get_empty_cells(board):
    """
    Lấy danh sách các ô trống trên bàn cờ.
    Trả về danh sách các tuple (hàng, cột).
    """
    cells = []
    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                cells.append((row, col))
    return cells


def get_winner_line(board):
    """
    Tìm đường thắng (3 ô liên tiếp).
    Trả về danh sách các tọa độ ô thắng, hoặc None.
    """
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != '':
            return [(row, 0), (row, 1), (row, 2)]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return [(0, col), (1, col), (2, col)]

    if board[0][0] == board[1][1] == board[2][2] != '':
        return [(0, 0), (1, 1), (2, 2)]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return [(0, 2), (1, 1), (2, 0)]

    return None


# =============================================================================
# THUẬT TOÁN EXPECTIMAX
# =============================================================================

nodes_explored = 0
chance_nodes_count = 0


def expectimax(board, depth, is_maximizing):
    """
    Thuật toán Expectimax - xử lý đối thủ theo mô hình xác suất.

    Khác biệt so với Minimax:
        - Nút MAX (lượt AI): giống Minimax, chọn giá trị lớn nhất
        - Nút CHANCE (lượt đối thủ): thay vì MIN, tính giá trị kỳ vọng
          dựa trên mô hình xác suất của đối thủ

    Mô hình đối thủ:
        - 70% xác suất: đối thủ chọn nước đi tối ưu (giá trị nhỏ nhất)
        - 30% xác suất: phân bố đều cho TẤT CẢ các nước đi có thể

    Tham số:
        board: trạng thái bàn cờ hiện tại
        depth: độ sâu hiện tại
        is_maximizing: True nếu đang là lượt AI (nút MAX),
                       False nếu đang là lượt đối thủ (nút CHANCE)

    Trả về:
        Giá trị kỳ vọng (expected value) cho trạng thái hiện tại
    """
    global nodes_explored, chance_nodes_count
    nodes_explored += 1

    # Trường hợp cơ sở: trạng thái kết thúc
    score = evaluate(board)
    if score == +10:
        return score - depth   # AI thắng
    if score == -10:
        return score + depth   # Người chơi thắng
    if len(get_empty_cells(board)) == 0:
        return 0               # Hòa

    empty_cells = get_empty_cells(board)

    if is_maximizing:
        # ===== NÚT MAX (Lượt AI) =====
        # AI chọn nước đi có giá trị CAO NHẤT (giống Minimax)
        best_score = float('-inf')
        for (row, col) in empty_cells:
            board[row][col] = AI
            current_score = expectimax(board, depth + 1, False)
            board[row][col] = ''
            best_score = max(best_score, current_score)
        return best_score
    else:
        # ===== NÚT CHANCE (Lượt đối thủ - mô hình xác suất) =====
        chance_nodes_count += 1

        # Bước 1: Tìm giá trị tối ưu (nước đi tốt nhất của đối thủ)
        #          Đối thủ muốn MINIMIZE điểm của AI
        optimal_score = float('inf')
        all_scores = []

        for (row, col) in empty_cells:
            board[row][col] = HUMAN
            current_score = expectimax(board, depth + 1, True)
            board[row][col] = ''
            all_scores.append(current_score)
            optimal_score = min(optimal_score, current_score)

        # Bước 2: Tính giá trị ngẫu nhiên (trung bình cộng tất cả nước đi)
        random_score = sum(all_scores) / len(all_scores)

        # Bước 3: Tính giá trị kỳ vọng (expected value)
        # E[v] = P(optimal) × V(optimal) + P(random) × V(random)
        expected_value = PROB_OPTIMAL * optimal_score + PROB_RANDOM * random_score

        return expected_value


def best_move(board):
    """
    Tìm nước đi tốt nhất cho AI bằng thuật toán Expectimax.

    Trả về:
        move: (row, col) - tọa độ nước đi tốt nhất
        best_score: giá trị kỳ vọng của nước đi
        nodes: số nút đã duyệt
        chance_nodes: số nút CHANCE đã xử lý
        max_depth: độ sâu tối đa
    """
    global nodes_explored, chance_nodes_count
    nodes_explored = 0
    chance_nodes_count = 0

    best_score = float('-inf')
    move = None
    empty_cells = get_empty_cells(board)
    max_depth = len(empty_cells)

    for (row, col) in empty_cells:
        board[row][col] = AI
        score = expectimax(board, 1, False)
        board[row][col] = ''

        if score > best_score:
            best_score = score
            move = (row, col)

    return move, best_score, nodes_explored, chance_nodes_count, max_depth


# =============================================================================
# GIAO DIỆN TKINTER
# =============================================================================

class CoCaRoExpectimax:
    """Lớp giao diện trò chơi Cờ Caro với AI Expectimax."""

    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro 3×3 — Thuật toán Expectimax")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Trạng thái trò chơi
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.game_over = False
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        # Thiết lập font chữ
        self.title_font = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.cell_font = tkfont.Font(family="Segoe UI", size=48, weight="bold")
        self.status_font = tkfont.Font(family="Segoe UI", size=16)
        self.stats_font = tkfont.Font(family="Consolas", size=11)
        self.btn_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")

        self._create_widgets()

    def _create_widgets(self):
        """Tạo các widget giao diện."""

        # ===== TIÊU ĐỀ =====
        title_frame = tk.Frame(self.root, bg=BG_COLOR)
        title_frame.pack(pady=(18, 5))

        tk.Label(
            title_frame, text="🎮 CỜ CARO 3×3",
            font=self.title_font, fg=ACCENT_COLOR, bg=BG_COLOR
        ).pack()

        tk.Label(
            title_frame, text="Thuật toán Expectimax",
            font=tkfont.Font(family="Segoe UI", size=13),
            fg="#8888aa", bg=BG_COLOR
        ).pack()

        # ===== TRẠNG THÁI =====
        self.status_label = tk.Label(
            self.root, text="🟢 Lượt của bạn (X)",
            font=self.status_font, fg=TEXT_COLOR, bg=BG_COLOR
        )
        self.status_label.pack(pady=(10, 8))

        # ===== BÀN CỜ =====
        board_frame = tk.Frame(self.root, bg="#0d1b2a", bd=3, relief="ridge")
        board_frame.pack(pady=8)

        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    board_frame,
                    text="",
                    font=self.cell_font,
                    width=4, height=1,
                    bg=BOARD_BG, fg=TEXT_COLOR,
                    activebackground=HOVER_COLOR,
                    activeforeground=TEXT_COLOR,
                    relief="flat", bd=2,
                    cursor="hand2",
                    command=lambda r=row, c=col: self._on_click(r, c)
                )
                btn.grid(row=row, column=col, padx=3, pady=3)

                btn.bind("<Enter>", lambda e, b=btn: self._on_hover_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self._on_hover_leave(b))

                self.buttons[row][col] = btn

        # ===== THỐNG KÊ AI =====
        stats_frame = tk.Frame(self.root, bg="#0f1a2e", bd=2, relief="groove")
        stats_frame.pack(pady=12, padx=30, fill="x")

        tk.Label(
            stats_frame, text="📊 Thống kê AI (Expectimax)",
            font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
            fg=ACCENT_COLOR, bg="#0f1a2e"
        ).pack(pady=(8, 4))

        tk.Label(
            stats_frame,
            text=f"Mô hình đối thủ: {int(PROB_OPTIMAL*100)}% tối ưu,"
                 f" {int(PROB_RANDOM*100)}% ngẫu nhiên",
            font=tkfont.Font(family="Consolas", size=10),
            fg="#ffcc00", bg="#0f1a2e"
        ).pack(padx=20, anchor="w")

        self.stats_nodes = tk.Label(
            stats_frame, text="Số nút đã duyệt:    —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_nodes.pack(padx=20, anchor="w")

        self.stats_chance = tk.Label(
            stats_frame, text="Nút CHANCE xử lý:   —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_chance.pack(padx=20, anchor="w")

        self.stats_depth = tk.Label(
            stats_frame, text="Độ sâu tìm kiếm:    —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_depth.pack(padx=20, anchor="w")

        self.stats_score = tk.Label(
            stats_frame, text="Giá trị kỳ vọng:    —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_score.pack(padx=20, anchor="w")

        self.stats_time = tk.Label(
            stats_frame, text="Thời gian suy nghĩ: —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_time.pack(padx=20, pady=(0, 8), anchor="w")

        # ===== NÚT CHƠI LẠI =====
        self.reset_btn = tk.Button(
            self.root, text="🔄 Chơi lại",
            font=self.btn_font,
            bg=BUTTON_BG, fg=TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            activeforeground="white",
            relief="flat", bd=0,
            cursor="hand2",
            padx=30, pady=8,
            command=self._reset_game
        )
        self.reset_btn.pack(pady=12)

        self.reset_btn.bind("<Enter>",
            lambda e: self.reset_btn.config(bg=ACCENT_COLOR))
        self.reset_btn.bind("<Leave>",
            lambda e: self.reset_btn.config(bg=BUTTON_BG))

    # -------------------------------------------------------------------------
    # XỬ LÝ SỰ KIỆN
    # -------------------------------------------------------------------------

    def _on_hover_enter(self, btn):
        """Hiệu ứng khi di chuột vào ô trống."""
        if btn["text"] == "" and not self.game_over:
            btn.config(bg=HOVER_COLOR)

    def _on_hover_leave(self, btn):
        """Hiệu ứng khi di chuột ra khỏi ô."""
        if btn["text"] == "" and not self.game_over:
            btn.config(bg=BOARD_BG)

    def _on_click(self, row, col):
        """Xử lý khi người chơi nhấn vào ô."""
        if self.board[row][col] != '' or self.game_over:
            return

        # Người chơi đặt quân X
        self.board[row][col] = HUMAN
        self.buttons[row][col].config(
            text="X", fg=X_COLOR, bg=BOARD_BG, cursor="arrow"
        )

        if self._check_game_over():
            return

        self.status_label.config(text="🤖 AI đang suy nghĩ...", fg="#ffcc00")
        self.root.update()
        self.root.after(100, self._ai_move)

    def _ai_move(self):
        """AI thực hiện nước đi bằng Expectimax."""
        start_time = time.time()

        move, score, nodes, chance_nodes, depth = best_move(self.board)
        elapsed = time.time() - start_time

        if move is not None:
            row, col = move
            self.board[row][col] = AI
            self.buttons[row][col].config(
                text="O", fg=O_COLOR, bg=BOARD_BG, cursor="arrow"
            )

            # Mô tả giá trị kỳ vọng
            if score > 0:
                score_desc = f"{score:+.2f} (AI có lợi thế)"
            elif score < 0:
                score_desc = f"{score:+.2f} (Người chơi có lợi thế)"
            else:
                score_desc = f"{score:+.2f} (Cân bằng)"

            # Cập nhật thống kê
            self.stats_nodes.config(
                text=f"Số nút đã duyệt:    {nodes:,}"
            )
            self.stats_chance.config(
                text=f"Nút CHANCE xử lý:   {chance_nodes:,}"
            )
            self.stats_depth.config(
                text=f"Độ sâu tìm kiếm:    {depth}"
            )
            self.stats_score.config(
                text=f"Giá trị kỳ vọng:    {score_desc}"
            )
            self.stats_time.config(
                text=f"Thời gian suy nghĩ: {elapsed*1000:.1f} ms"
            )

        if not self._check_game_over():
            self.status_label.config(
                text="🟢 Lượt của bạn (X)", fg=TEXT_COLOR
            )

    def _check_game_over(self):
        """Kiểm tra trò chơi đã kết thúc chưa."""
        score = evaluate(self.board)
        winner_line = get_winner_line(self.board)

        if score == -10:
            self.game_over = True
            self.status_label.config(text="🎉 Bạn thắng!", fg="#00ff88")
            if winner_line:
                self._highlight_winner(winner_line, X_COLOR)
            return True

        elif score == +10:
            self.game_over = True
            self.status_label.config(text="🤖 AI thắng!", fg="#ff4444")
            if winner_line:
                self._highlight_winner(winner_line, O_COLOR)
            return True

        elif len(get_empty_cells(self.board)) == 0:
            self.game_over = True
            self.status_label.config(text="🤝 Hòa!", fg="#ffcc00")
            self._highlight_draw()
            return True

        return False

    def _highlight_winner(self, line, color):
        """Tô sáng các ô thắng."""
        for (row, col) in line:
            self.buttons[row][col].config(bg="#1a3a1a", fg=WIN_COLOR)

    def _highlight_draw(self):
        """Hiệu ứng khi hòa."""
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(bg="#2a2a1a")

    def _reset_game(self):
        """Khởi động lại trò chơi."""
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.game_over = False

        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    text="", bg=BOARD_BG, fg=TEXT_COLOR, cursor="hand2"
                )

        self.status_label.config(
            text="🟢 Lượt của bạn (X)", fg=TEXT_COLOR
        )

        self.stats_nodes.config(text="Số nút đã duyệt:    —")
        self.stats_chance.config(text="Nút CHANCE xử lý:   —")
        self.stats_depth.config(text="Độ sâu tìm kiếm:    —")
        self.stats_score.config(text="Giá trị kỳ vọng:    —")
        self.stats_time.config(text="Thời gian suy nghĩ: —")


# =============================================================================
# CHẠY CHƯƠNG TRÌNH
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CoCaRoExpectimax(root)
    root.mainloop()
