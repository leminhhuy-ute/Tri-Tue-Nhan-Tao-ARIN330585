# Bài Tập Cá Nhân - Môn Trí Tuệ Nhân Tạo 🤖

**Thông tin sinh viên:**
- **Họ và tên:** Lê Minh Huy
- **MSSV:** 24110019
- **Học phần:** Trí Tuệ Nhân Tạo (Artificial Intelligence)

---

## 🎯 Giới thiệu Đồ án
Dự án này là tập hợp các bài tập và thuật toán mô phỏng Trí tuệ nhân tạo được xây dựng hoàn toàn bằng ngôn ngữ Python (kèm giao diện trực quan bằng thư viện Tkinter). Đồ án cung cấp một ứng dụng trung tâm cho phép người dùng chạy thử, quan sát cách hoạt động (trace log), và hiểu sâu hơn về cơ chế của các thuật toán AI kinh điển.

Dự án được chia thành 4 bài toán/chủ đề chính:

1. 🧩 **8-Puzzle (`8Puzzle/`)**
   Giải quyết trò chơi 8 ô chữ với nhiều nhóm thuật toán khác nhau:
   - *Uninformed Search*: BFS, DFS, UCS, IDS
   - *Informed Search*: Greedy Best-First, A*, IDA*
   - *Local Search*: Hill Climbing (Simple, Steepest, Stochastic, Random-Restart), Local Beam Search, Simulated Annealing
   - *Complex Environments*: AND-OR Search, No Observation, Partially Observable, Online Search

2. 🧹 **Máy Hút Bụi (`MayHutBui/`)**
   Mô phỏng robot dọn dẹp trong một lưới không gian (grid environment) ứng dụng các thuật toán tìm kiếm đường đi cơ bản và nâng cao để làm sạch toàn bộ bản đồ.

3. 🗺️ **Tô Màu Bản Đồ (`ToMauBanDo/`)**
   Giải quyết bài toán thỏa mãn ràng buộc (CSP) dựa trên đồ thị Bản đồ Thủ Đức (12 phường). Ứng dụng các kỹ thuật như: *CSP Backtracking (với MRV heuristic)*, *AC-3 (Constraint Propagation)*, *Path Consistency*, *Min-Conflicts*...

4. ❌⭕ **Cờ Ca-rô (`CoCaRo/`)**
   Xây dựng AI chơi cờ Ca-rô áp dụng nhóm thuật toán Adversarial Search: *Minimax*, *Alpha-Beta Pruning*, và *Expectimax*.

---

## 🚀 Hướng dẫn chạy chương trình
Toàn bộ dự án được quản lý bởi một Menu Launcher duy nhất. Bạn không cần phải chạy thủ công từng file.
Chỉ cần mở Terminal/Command Prompt tại thư mục dự án và gõ lệnh:

```bash
python main_app.py
```
*Giao diện Menu chính sẽ hiện ra cho phép bạn chọn và trải nghiệm bất kỳ thuật toán nào!*

---

## 📚 Quá Trình Học Tập (`QuaTrinhHocTap/`)
Trong suốt khóa học, các bài tập thực hành trên lớp, bài tập về nhà (Jupyter Notebook, code nháp...) và các version cũ đã được gom gọn lại trong thư mục **`QuaTrinhHocTap/`**. 
Thư mục này mang tính chất lưu giữ lại hành trình học tập, tìm tòi và phát triển mã nguồn từ những bài thực hành nhỏ nhất cho đến khi hoàn thiện thành một hệ thống đồ án UI hoàn chỉnh như hiện tại.
