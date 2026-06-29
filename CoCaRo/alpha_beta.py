# =============================================================================
# CỜ CARO 3x3 (Tic-Tac-Toe) - Thuật toán ALPHA-BETA PRUNING
# =============================================================================
# Trò chơi Cờ Caro 3x3 với AI sử dụng thuật toán Alpha-Beta Pruning
# (Cải tiến từ Minimax bằng cách cắt tỉa các nhánh không cần thiết)
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
    # Kiểm tra hàng ngang
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != '':
            return [(row, 0), (row, 1), (row, 2)]

    # Kiểm tra cột dọc
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return [(0, col), (1, col), (2, col)]

    # Kiểm tra đường chéo
    if board[0][0] == board[1][1] == board[2][2] != '':
        return [(0, 0), (1, 1), (2, 2)]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return [(0, 2), (1, 1), (2, 0)]

    return None


# =============================================================================
# THUẬT TOÁN MINIMAX (để so sánh hiệu suất)
# =============================================================================

minimax_nodes = 0  # Bộ đếm nút cho Minimax thuần


def minimax_pure(board, depth, is_maximizing):
    """
    Minimax thuần (không cắt tỉa) - chỉ để đếm số nút so sánh.
    """
    global minimax_nodes
    minimax_nodes += 1

    score = evaluate(board)
    if score == +10:
        return score - depth
    if score == -10:
        return score + depth
    if len(get_empty_cells(board)) == 0:
        return 0

    if is_maximizing:
        best = float('-inf')
        for (r, c) in get_empty_cells(board):
            board[r][c] = AI
            best = max(best, minimax_pure(board, depth + 1, False))
            board[r][c] = ''
        return best
    else:
        best = float('inf')
        for (r, c) in get_empty_cells(board):
            board[r][c] = HUMAN
            best = min(best, minimax_pure(board, depth + 1, True))
            board[r][c] = ''
        return best


# =============================================================================
# THUẬT TOÁN ALPHA-BETA PRUNING
# =============================================================================

# Biến đếm toàn cục
ab_nodes_explored = 0
ab_pruned_branches = 0


def alpha_beta(board, depth, alpha, beta, is_maximizing):
    """
    Thuật toán Alpha-Beta Pruning - cải tiến từ Minimax.

    Nguyên lý:
        - Alpha: giá trị tốt nhất mà Maximizer (AI) đã tìm được
        - Beta: giá trị tốt nhất mà Minimizer (Người chơi) đã tìm được
        - Cắt tỉa khi alpha >= beta (nhánh không thể tốt hơn)

    Tham số:
        board: trạng thái bàn cờ hiện tại
        depth: độ sâu hiện tại
        alpha: giới hạn dưới (khởi tạo = -∞)
        beta: giới hạn trên (khởi tạo = +∞)
        is_maximizing: True nếu đang là lượt AI

    Trả về:
        Điểm đánh giá tốt nhất cho trạng thái hiện tại
    """
    global ab_nodes_explored, ab_pruned_branches
    ab_nodes_explored += 1

    # Trường hợp cơ sở: trạng thái kết thúc
    score = evaluate(board)
    if score == +10:
        return score - depth   # AI thắng, ưu tiên thắng nhanh
    if score == -10:
        return score + depth   # Người thắng, trì hoãn thua
    if len(get_empty_cells(board)) == 0:
        return 0               # Hòa

    if is_maximizing:
        # Lượt AI: tìm nước đi có điểm CAO NHẤT
        best_score = float('-inf')
        for (row, col) in get_empty_cells(board):
            board[row][col] = AI
            current_score = alpha_beta(board, depth + 1, alpha, beta, False)
            board[row][col] = ''

            best_score = max(best_score, current_score)
            alpha = max(alpha, best_score)

            # CẮT TỈA BETA: nhánh này không thể tốt hơn
            if alpha >= beta:
                ab_pruned_branches += 1
                break  # Cắt tỉa! Không cần duyệt thêm

        return best_score
    else:
        # Lượt Người chơi: tìm nước đi có điểm THẤP NHẤT
        best_score = float('inf')
        for (row, col) in get_empty_cells(board):
            board[row][col] = HUMAN
            current_score = alpha_beta(board, depth + 1, alpha, beta, True)
            board[row][col] = ''

            best_score = min(best_score, current_score)
            beta = min(beta, best_score)

            # CẮT TỈA ALPHA: nhánh này không thể tốt hơn
            if alpha >= beta:
                ab_pruned_branches += 1
                break  # Cắt tỉa! Không cần duyệt thêm

        return best_score


def best_move(board):
    """
    Tìm nước đi tốt nhất cho AI bằng Alpha-Beta Pruning.
    Đồng thời chạy Minimax thuần để so sánh hiệu suất.

    Trả về:
        move: (row, col) - tọa độ nước đi tốt nhất
        best_score: điểm đánh giá
        ab_nodes: số nút Alpha-Beta đã duyệt
        pruned: số nhánh đã cắt tỉa
        mm_nodes: số nút Minimax thuần đã duyệt (để so sánh)
        max_depth: độ sâu tối đa
    """
    global ab_nodes_explored, ab_pruned_branches, minimax_nodes

    # Reset bộ đếm
    ab_nodes_explored = 0
    ab_pruned_branches = 0
    minimax_nodes = 0

    best_score = float('-inf')
    move = None
    empty_cells = get_empty_cells(board)
    max_depth = len(empty_cells)

    # Chạy Alpha-Beta Pruning
    for (row, col) in empty_cells:
        board[row][col] = AI
        score = alpha_beta(board, 1, float('-inf'), float('inf'), False)
        board[row][col] = ''

        if score > best_score:
            best_score = score
            move = (row, col)

    # Chạy Minimax thuần để so sánh (trên bản sao)
    import copy
    board_copy = copy.deepcopy(board)
    for (row, col) in get_empty_cells(board_copy):
        board_copy[row][col] = AI
        minimax_pure(board_copy, 1, False)
        board_copy[row][col] = ''

    return move, best_score, ab_nodes_explored, ab_pruned_branches, \
           minimax_nodes, max_depth


# =============================================================================
# GIAO DIỆN TKINTER
# =============================================================================

class CoCaRoAlphaBeta:
    """Lớp giao diện trò chơi Cờ Caro với AI Alpha-Beta Pruning."""

    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro 3×3 — Thuật toán Alpha-Beta Pruning")
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
            title_frame, text="Thuật toán Alpha-Beta Pruning",
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

                # Hiệu ứng hover
                btn.bind("<Enter>", lambda e, b=btn: self._on_hover_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self._on_hover_leave(b))

                self.buttons[row][col] = btn

        # ===== THỐNG KÊ AI =====
        stats_frame = tk.Frame(self.root, bg="#0f1a2e", bd=2, relief="groove")
        stats_frame.pack(pady=12, padx=30, fill="x")

        tk.Label(
            stats_frame, text="📊 Thống kê AI (Alpha-Beta Pruning)",
            font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
            fg=ACCENT_COLOR, bg="#0f1a2e"
        ).pack(pady=(8, 4))

        self.stats_ab_nodes = tk.Label(
            stats_frame, text="Nút duyệt (Alpha-Beta): —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_ab_nodes.pack(padx=20, anchor="w")

        self.stats_mm_nodes = tk.Label(
            stats_frame, text="Nút duyệt (Minimax):    —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_mm_nodes.pack(padx=20, anchor="w")

        self.stats_pruned = tk.Label(
            stats_frame, text="Nhánh đã cắt tỉa:      —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_pruned.pack(padx=20, anchor="w")

        self.stats_savings = tk.Label(
            stats_frame, text="Tiết kiệm:              —",
            font=self.stats_font, fg="#00ff88", bg="#0f1a2e", anchor="w"
        )
        self.stats_savings.pack(padx=20, anchor="w")

        self.stats_score = tk.Label(
            stats_frame, text="Điểm đánh giá:          —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_score.pack(padx=20, anchor="w")

        self.stats_time = tk.Label(
            stats_frame, text="Thời gian suy nghĩ:     —",
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

        # Chuyển lượt cho AI
        self.status_label.config(text="🤖 AI đang suy nghĩ...", fg="#ffcc00")
        self.root.update()
        self.root.after(100, self._ai_move)

    def _ai_move(self):
        """AI thực hiện nước đi bằng Alpha-Beta Pruning."""
        start_time = time.time()

        # Tìm nước đi tốt nhất
        move, score, ab_nodes, pruned, mm_nodes, depth = best_move(self.board)
        elapsed = time.time() - start_time

        if move is not None:
            row, col = move
            self.board[row][col] = AI
            self.buttons[row][col].config(
                text="O", fg=O_COLOR, bg=BOARD_BG, cursor="arrow"
            )

            # Tính phần trăm tiết kiệm so với Minimax
            if mm_nodes > 0:
                savings = (1 - ab_nodes / mm_nodes) * 100
                savings_text = f"{savings:.1f}% số nút (so với Minimax)"
            else:
                savings_text = "—"

            # Mô tả điểm số
            score_text = f"+{score}" if score > 0 else str(score)
            if score > 0:
                score_desc = f"{score_text} (AI có lợi thế)"
            elif score < 0:
                score_desc = f"{score_text} (Người chơi có lợi thế)"
            else:
                score_desc = f"{score_text} (Cân bằng / Hòa)"

            # Cập nhật thống kê
            self.stats_ab_nodes.config(
                text=f"Nút duyệt (Alpha-Beta): {ab_nodes:,}"
            )
            self.stats_mm_nodes.config(
                text=f"Nút duyệt (Minimax):    {mm_nodes:,}"
            )
            self.stats_pruned.config(
                text=f"Nhánh đã cắt tỉa:      {pruned:,}"
            )
            self.stats_savings.config(
                text=f"Tiết kiệm:              {savings_text}"
            )
            self.stats_score.config(
                text=f"Điểm đánh giá:          {score_desc}"
            )
            self.stats_time.config(
                text=f"Thời gian suy nghĩ:     {elapsed*1000:.1f} ms"
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

        self.stats_ab_nodes.config(text="Nút duyệt (Alpha-Beta): —")
        self.stats_mm_nodes.config(text="Nút duyệt (Minimax):    —")
        self.stats_pruned.config(text="Nhánh đã cắt tỉa:      —")
        self.stats_savings.config(text="Tiết kiệm:              —")
        self.stats_score.config(text="Điểm đánh giá:          —")
        self.stats_time.config(text="Thời gian suy nghĩ:     —")


# =============================================================================
# CHẠY CHƯƠNG TRÌNH
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CoCaRoAlphaBeta(root)
    root.mainloop()
