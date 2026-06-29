# =============================================================================
# CỜ CARO 3x3 (Tic-Tac-Toe) - Thuật toán MINIMAX
# =============================================================================
# Trò chơi Cờ Caro 3x3 với AI sử dụng thuật toán Minimax
# Người chơi: X (đi trước) | AI: O (đi sau)
# Điều kiện thắng: 3 ô liên tiếp (ngang, dọc, chéo)
# =============================================================================

import tkinter as tk
from tkinter import font as tkfont
import time
import copy

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
    # Kiểm tra có người thắng không
    if evaluate(board) != 0:
        return True

    # Kiểm tra bàn cờ đầy (hòa)
    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                return False  # Còn ô trống, chưa kết thúc
    return True  # Bàn cờ đầy


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
# THUẬT TOÁN MINIMAX
# =============================================================================

# Biến đếm số nút đã duyệt (dùng biến toàn cục)
nodes_explored = 0


def minimax(board, depth, is_maximizing):
    """
    Thuật toán Minimax - duyệt toàn bộ cây trò chơi.

    Tham số:
        board: trạng thái bàn cờ hiện tại (ma trận 3x3)
        depth: độ sâu hiện tại trong cây tìm kiếm
        is_maximizing: True nếu đang là lượt AI (tối đa hóa),
                       False nếu đang là lượt người chơi (tối thiểu hóa)

    Trả về:
        Điểm đánh giá tốt nhất cho trạng thái hiện tại
    """
    global nodes_explored
    nodes_explored += 1  # Đếm số nút đã duyệt

    # Trường hợp cơ sở: trạng thái kết thúc
    score = evaluate(board)
    if score == +10:
        return score - depth   # AI thắng, ưu tiên thắng nhanh
    if score == -10:
        return score + depth   # Người chơi thắng, trì hoãn thua
    if len(get_empty_cells(board)) == 0:
        return 0               # Hòa

    if is_maximizing:
        # Lượt AI: tìm nước đi có điểm CAO NHẤT
        best_score = float('-inf')
        for (row, col) in get_empty_cells(board):
            board[row][col] = AI               # Thử đặt quân AI
            current_score = minimax(board, depth + 1, False)
            board[row][col] = ''               # Hoàn tác
            best_score = max(best_score, current_score)
        return best_score
    else:
        # Lượt Người chơi: tìm nước đi có điểm THẤP NHẤT
        best_score = float('inf')
        for (row, col) in get_empty_cells(board):
            board[row][col] = HUMAN            # Thử đặt quân người chơi
            current_score = minimax(board, depth + 1, True)
            board[row][col] = ''               # Hoàn tác
            best_score = min(best_score, current_score)
        return best_score


def best_move(board):
    """
    Tìm nước đi tốt nhất cho AI bằng thuật toán Minimax.

    Trả về:
        (row, col): tọa độ nước đi tốt nhất
        best_score: điểm đánh giá của nước đi
        nodes_explored: số nút đã duyệt
        max_depth: độ sâu tối đa đã duyệt
    """
    global nodes_explored
    nodes_explored = 0  # Reset bộ đếm

    best_score = float('-inf')
    move = None
    empty_cells = get_empty_cells(board)
    max_depth = len(empty_cells)  # Độ sâu tối đa = số ô trống

    for (row, col) in empty_cells:
        board[row][col] = AI                    # Thử đặt quân AI
        score = minimax(board, 1, False)        # Gọi minimax cho đối thủ
        board[row][col] = ''                    # Hoàn tác

        if score > best_score:
            best_score = score
            move = (row, col)

    return move, best_score, nodes_explored, max_depth


# =============================================================================
# GIAO DIỆN TKINTER
# =============================================================================

class CoCaRoMinimax:
    """Lớp giao diện trò chơi Cờ Caro với AI Minimax."""

    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Caro 3×3 — Thuật toán Minimax")
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
            title_frame, text="Thuật toán Minimax",
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

                # Hiệu ứng hover (di chuột vào/ra)
                btn.bind("<Enter>", lambda e, b=btn: self._on_hover_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self._on_hover_leave(b))

                self.buttons[row][col] = btn

        # ===== THỐNG KÊ AI =====
        stats_frame = tk.Frame(self.root, bg="#0f1a2e", bd=2, relief="groove")
        stats_frame.pack(pady=12, padx=30, fill="x")

        tk.Label(
            stats_frame, text="📊 Thống kê AI (Minimax)",
            font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
            fg=ACCENT_COLOR, bg="#0f1a2e"
        ).pack(pady=(8, 4))

        self.stats_nodes = tk.Label(
            stats_frame, text="Số nút đã duyệt:  —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_nodes.pack(padx=20, anchor="w")

        self.stats_depth = tk.Label(
            stats_frame, text="Độ sâu tìm kiếm:  —",
            font=self.stats_font, fg="#aaaacc", bg="#0f1a2e", anchor="w"
        )
        self.stats_depth.pack(padx=20, anchor="w")

        self.stats_score = tk.Label(
            stats_frame, text="Điểm đánh giá:    —",
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

        # Hiệu ứng hover cho nút Chơi lại
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
        # Kiểm tra ô đã được đánh chưa hoặc game đã kết thúc
        if self.board[row][col] != '' or self.game_over:
            return

        # Người chơi đặt quân X
        self.board[row][col] = HUMAN
        self.buttons[row][col].config(
            text="X", fg=X_COLOR, bg=BOARD_BG,
            cursor="arrow"
        )

        # Kiểm tra kết thúc sau nước đi của người chơi
        if self._check_game_over():
            return

        # Chuyển lượt cho AI
        self.status_label.config(text="🤖 AI đang suy nghĩ...", fg="#ffcc00")
        self.root.update()

        # AI thực hiện nước đi (dùng after để UI cập nhật mượt)
        self.root.after(100, self._ai_move)

    def _ai_move(self):
        """AI thực hiện nước đi bằng thuật toán Minimax."""
        start_time = time.time()

        # Tìm nước đi tốt nhất
        move, score, nodes, depth = best_move(self.board)
        elapsed = time.time() - start_time

        if move is not None:
            row, col = move
            self.board[row][col] = AI
            self.buttons[row][col].config(
                text="O", fg=O_COLOR, bg=BOARD_BG,
                cursor="arrow"
            )

            # Cập nhật thống kê
            score_text = f"+{score}" if score > 0 else str(score)
            if score > 0:
                score_desc = f"{score_text} (AI có lợi thế)"
            elif score < 0:
                score_desc = f"{score_text} (Người chơi có lợi thế)"
            else:
                score_desc = f"{score_text} (Cân bằng / Hòa)"

            self.stats_nodes.config(text=f"Số nút đã duyệt:  {nodes:,}")
            self.stats_depth.config(text=f"Độ sâu tìm kiếm:  {depth}")
            self.stats_score.config(text=f"Điểm đánh giá:    {score_desc}")
            self.stats_time.config(
                text=f"Thời gian suy nghĩ: {elapsed*1000:.1f} ms"
            )

        # Kiểm tra kết thúc sau nước đi của AI
        if not self._check_game_over():
            self.status_label.config(
                text="🟢 Lượt của bạn (X)", fg=TEXT_COLOR
            )

    def _check_game_over(self):
        """
        Kiểm tra trò chơi đã kết thúc chưa.
        Cập nhật giao diện tương ứng.
        """
        score = evaluate(self.board)
        winner_line = get_winner_line(self.board)

        if score == -10:
            # Người chơi thắng
            self.game_over = True
            self.status_label.config(
                text="🎉 Bạn thắng!", fg="#00ff88"
            )
            if winner_line:
                self._highlight_winner(winner_line, X_COLOR)
            return True

        elif score == +10:
            # AI thắng
            self.game_over = True
            self.status_label.config(
                text="🤖 AI thắng!", fg="#ff4444"
            )
            if winner_line:
                self._highlight_winner(winner_line, O_COLOR)
            return True

        elif len(get_empty_cells(self.board)) == 0:
            # Hòa
            self.game_over = True
            self.status_label.config(
                text="🤝 Hòa!", fg="#ffcc00"
            )
            self._highlight_draw()
            return True

        return False

    def _highlight_winner(self, line, color):
        """Tô sáng các ô thắng với hiệu ứng."""
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
                    text="", bg=BOARD_BG, fg=TEXT_COLOR,
                    cursor="hand2"
                )

        self.status_label.config(
            text="🟢 Lượt của bạn (X)", fg=TEXT_COLOR
        )

        # Reset thống kê
        self.stats_nodes.config(text="Số nút đã duyệt:  —")
        self.stats_depth.config(text="Độ sâu tìm kiếm:  —")
        self.stats_score.config(text="Điểm đánh giá:    —")
        self.stats_time.config(text="Thời gian suy nghĩ: —")


# =============================================================================
# CHẠY CHƯƠNG TRÌNH
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CoCaRoMinimax(root)
    root.mainloop()
