import random
import os

class EightPuzzle:
    def __init__(self):
        self.goal = [[1, 2, 3],
                     [4, 5, 6],
                     [7, 8, 0]]   # 0 đại diện ô trống
        self.board = self._generate_solvable_board()
        self.empty_pos = self._find_empty()
    def _find_empty(self):
        """Trả về vị trí (hàng, cột) của ô trống."""
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def _generate_solvable_board(self):
        """Tạo bảng có thể giải bằng cách xáo trộn từ đích, đảm bảo ô trống tại (0,0)."""
        # Bắt đầu từ đích
        board = [row[:] for row in self.goal]
        empty_r, empty_c = 2, 2  # vị trí ô trống ở đích
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # lên, xuống, trái, phải

        # Thực hiện khoảng 100 lần di chuyển ngẫu nhiên hợp lệ
        for _ in range(100):
            valid_moves = []
            for dr, dc in moves:
                nr, nc = empty_r + dr, empty_c + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    valid_moves.append((nr, nc))
            if valid_moves:
                nr, nc = random.choice(valid_moves)
                # Đổi chỗ ô trống với ô kề
                board[empty_r][empty_c], board[nr][nc] = board[nr][nc], board[empty_r][empty_c]
                empty_r, empty_c = nr, nc

        # Bây giờ tiếp tục di chuyển ngẫu nhiên cho đến khi ô trống về (0,0)
        while (empty_r, empty_c) != (0, 0):
            valid_moves = []
            for dr, dc in moves:
                nr, nc = empty_r + dr, empty_c + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    valid_moves.append((nr, nc))
            if not valid_moves:   # trường hợp hy hữu nhưng không bao giờ xảy ra ở 3x3
                break
            nr, nc = random.choice(valid_moves)
            board[empty_r][empty_c], board[nr][nc] = board[nr][nc], board[empty_r][empty_c]
            empty_r, empty_c = nr, nc

        # Kiểm tra xem bảng có giải được không (dù luôn đúng vì tạo từ đích)
        if not self._is_solvable(board):
            # Nếu lạ thay không giải được, gọi đệ quy để tạo lại
            return self._generate_solvable_board()
        return board

    def _is_solvable(self, board):
        """Kiểm tra xem bảng có thể giải được không dựa trên số nghịch đảo."""
        flat = [tile for row in board for tile in row if tile != 0]
        inv = 0
        for i in range(len(flat)):
            for j in range(i+1, len(flat)):
                if flat[i] > flat[j]:
                    inv += 1
        return inv % 2 == 0  # với lưới 3x3, số nghịch đảo chẵn thì giải được

    def move(self, direction):
        """Di chuyển ô trống theo hướng (W/A/S/D). Trả về True nếu di chuyển hợp lệ."""
        r, c = self.empty_pos
        dr, dc = 0, 0
        if direction.upper() == 'W':   
            dr, dc = -1, 0
        elif direction.upper() == 'S': 
            dr, dc = 1, 0
        elif direction.upper() == 'A': 
            dr, dc = 0, -1
        elif direction.upper() == 'D': 
            dr, dc = 0, 1
        else:
            return False
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            # Đổi chỗ
            self.board[r][c], self.board[nr][nc] = self.board[nr][nc], self.board[r][c]
            self.empty_pos = (nr, nc)
            return True
        return False

    def is_goal(self):
        return self.board == self.goal

    def display(self):
        """In bảng trạng thái hiện tại."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("8-Puzzle - Di chuyển ô trống bằng W/A/S/D. Thoát: Q")
        print("Mục tiêu: sắp xếp thành 1 2 3 / 4 5 6 / 7 8 _")
        print("-" * 13)
        for i in range(3):
            row_str = "| "
            for j in range(3):
                if self.board[i][j] == 0:
                    row_str += "_ | "
                else:
                    row_str += f"{self.board[i][j]} | "
            print(row_str)
            print("-" * 13)
        print(f"Ô trống ở: {self.empty_pos}")

def main():
    game = EightPuzzle()
    while not game.is_goal():
        game.display()
        move = input("Nhập hướng (W/A/S/D) hoặc Q để thoát: ").strip()
        if move.upper() == 'Q':
            print("Bạn đã thoát game.")
            return
        if move.upper() in ['W', 'A', 'S', 'D']:
            if game.move(move):
                pass
            else:
                print("Hướng không hợp lệ (đâm tường). Nhấn Enter để tiếp tục...")
                input()
        else:
            print("Lệnh không hợp lệ. Nhấn Enter để tiếp tục...")
            input()
    game.display()
    print("Chúc mừng! Bạn đã giải được 8-puzzle!")

if __name__ == "__main__":
    main()
