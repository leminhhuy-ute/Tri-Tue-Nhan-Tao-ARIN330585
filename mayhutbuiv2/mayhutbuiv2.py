import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from collections import deque
import heapq
import re


# ============================================================
# XỬ LÝ MA TRẬN
# ============================================================

def parse_matrix(text):
    lines = text.strip().splitlines()

    matrix = []
    robot_pos = None
    robot_count = 0

    for r, line in enumerate(lines):
        row = list(map(int, re.findall(r"\d+", line)))

        if not row:
            continue

        matrix.append(row)

        for c, value in enumerate(row):
            if value not in [0, 1, 2, 3]:
                raise ValueError("Ma trận chỉ được dùng các số 0, 1, 2, 3")

            if value == 2 or value == 3:
                robot_pos = (r, c)
                robot_count += 1

    if not matrix:
        raise ValueError("Ma trận không được rỗng")

    if robot_count != 1:
        raise ValueError("Ma trận phải có đúng 1 robot, dùng số 2 hoặc 3")

    col_count = len(matrix[0])

    for row in matrix:
        if len(row) != col_count:
            raise ValueError("Các hàng trong ma trận phải có cùng số cột")

    robot_r, robot_c = robot_pos

    dirt_grid = []

    for r in range(len(matrix)):
        dirt_row = []

        for c in range(len(matrix[0])):
            value = matrix[r][c]

            # Ô robot chỉ là vị trí robot, không tính là ô bẩn hay ô sạch
            if r == robot_r and c == robot_c:
                dirt_row.append(0)

            elif value == 1:
                dirt_row.append(1)

            else:
                dirt_row.append(0)

        dirt_grid.append(tuple(dirt_row))

    return (robot_r, robot_c, tuple(dirt_grid))


def is_goal(state):
    robot_r, robot_c, dirt_grid = state

    for row in dirt_grid:
        if 1 in row:
            return False

    return True


# ============================================================
# ĐẶT TÊN NODE A, B, C, D...
# ============================================================

def number_to_label(number):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    while True:
        result = letters[number % 26] + result
        number = number // 26 - 1

        if number < 0:
            break

    return result


def get_label(state, node_name, node_order):
    if state not in node_name:
        label = number_to_label(len(node_name))
        node_name[state] = label
        node_order.append(state)

    return node_name[state]


# ============================================================
# CHUYỂN STATE THÀNH MA TRẬN TEXT
# ============================================================

def state_to_matrix_text(state):
    robot_r, robot_c, dirt_grid = state

    result = []

    for r in range(len(dirt_grid)):
        row_text = []

        for c in range(len(dirt_grid[0])):
            if r == robot_r and c == robot_c:
                row_text.append("x")
            else:
                row_text.append(str(dirt_grid[r][c]))

        result.append(" ".join(row_text))

    return "\n".join(result)


def state_to_node_text(state, node_name):
    label = node_name[state]
    matrix_text = state_to_matrix_text(state)

    return f"{label}\n{matrix_text}"


# ============================================================
# SINH NODE CON
# ============================================================

def get_neighbors(state, version):
    robot_r, robot_c, dirt_grid = state

    rows = len(dirt_grid)
    cols = len(dirt_grid[0])

    neighbors = []

    # Version 1: ưu tiên giống vở: Right, Down, Left, Up
    if version == 1:
        actions = ["Right", "Down", "Left", "Up"]

    # Version 2: thứ tự khác để so sánh
    else:
        actions = ["Up", "Down", "Left", "Right"]

    for action in actions:
        new_r = robot_r
        new_c = robot_c

        if action == "Right":
            if robot_c < cols - 1:
                new_c = robot_c + 1
            else:
                continue

        elif action == "Down":
            if robot_r < rows - 1:
                new_r = robot_r + 1
            else:
                continue

        elif action == "Left":
            if robot_c > 0:
                new_c = robot_c - 1
            else:
                continue

        elif action == "Up":
            if robot_r > 0:
                new_r = robot_r - 1
            else:
                continue

        # Tạo ma trận bụi mới
        new_grid = [list(row) for row in dirt_grid]

        # Khi robot đi tới ô bẩn, ô đó tự động thành sạch
        new_grid[new_r][new_c] = 0

        new_grid = tuple(tuple(row) for row in new_grid)

        new_state = (new_r, new_c, new_grid)

        neighbors.append((action, new_state))

    return neighbors


# ============================================================
# FORMAT FRONTIER, REACHED
# ============================================================

def format_reached(visited_order, node_name):
    if not visited_order:
        return "[]"

    labels = []

    for state in visited_order:
        labels.append(f"{node_name[state]}.state")

    return ", ".join(labels)


def action_short(action):
    short_name = {
        "Right": "R",
        "Down": "D",
        "Left": "L",
        "Up": "U"
    }

    return short_name.get(action, action)


def remember_node_info(node_info, state, parent_state, action, cost, node_name, f_value=None, h_value=None):
    parent_label = None

    if parent_state is not None:
        parent_label = node_name[parent_state]

    node_info[state] = {
        "parent": parent_label,
        "action": action_short(action) if action else None,
        "cost": cost
    }

    if f_value is not None:
        node_info[state]["f"] = f_value

    if h_value is not None:
        node_info[state]["h"] = h_value


def format_frontier_item(state, node_name, node_info):
    label = node_name[state]
    info = node_info.get(state, {})
    parent_label = info.get("parent")
    action = info.get("action")
    cost = info.get("cost", 1)
    f_value = info.get("f")
    h_value = info.get("h")
    value_parts = []

    if f_value is not None:
        value_parts.append(f"f(n)={f_value}")

    if h_value is not None:
        value_parts.append(f"h(n)={h_value}")

    value_text = ""

    if value_parts:
        value_text = ", " + ", ".join(value_parts)

    rows = state_to_matrix_text(state).splitlines()

    if parent_label is None:
        return label + value_text + "\n" + state_to_matrix_text(state)

    result = []

    for index, row in enumerate(rows):
        if index == 0:
            result.append("{(" + row + ")")
        elif index == len(rows) - 1:
            result.append(f" ({row}), {parent_label}, {action}, {cost}}} {label}{value_text}")
        else:
            result.append(" (" + row + ")")

    return "\n".join(result)


def format_frontier_states(states, node_name, node_info):
    if not states:
        return "[]"

    result = []

    for state in states:
        result.append(format_frontier_item(state, node_name, node_info))

    return "\n\n".join(result)


def format_frontier_sections(frontier_before, children_text, frontier_after=None, extra_text=None):
    sections = []

    if frontier_before and frontier_before != "[]":
        sections.append(frontier_before)

    if children_text and children_text != "[]":
        sections.append(children_text)

    if not sections and frontier_after:
        sections.append(frontier_after)

    if extra_text:
        sections.append(extra_text)

    if not sections:
        return "[]"

    return "\n\n".join(sections)


def format_frontier_after(children_added, node_name, node_info, parent_state=None):
    parent_label = None

    if parent_state is not None:
        parent_label = node_name[parent_state]

    if not children_added:
        return "Không sinh thêm node mới"

    result = []

    for child in children_added:
        state = child[1]
        result.append(format_frontier_item(state, node_name, node_info))

    return "\n\n".join(result)


def format_frontier_list(frontier, node_name, algo, node_info=None):
    if not frontier:
        return "[]"

    if node_info is None:
        labels = []

        for item in frontier:
            state = item[0]
            labels.append(node_name[state])

        return "[" + ", ".join(labels) + "]"

    if algo == "UCS":
        states = []

        for item in sorted(frontier, key=lambda value: (value[0], value[1])):
            states.append(item[2])

        return format_frontier_states(states, node_name, node_info)

    states = []

    for item in frontier:
        states.append(item[0])

    return format_frontier_states(states, node_name, node_info)




# ============================================================
# HEURISTIC CHO GREEDY VÀ A*
# ============================================================

def get_dirty_positions(state):
    robot_r, robot_c, dirt_grid = state
    dirty_positions = []

    for r in range(len(dirt_grid)):
        for c in range(len(dirt_grid[0])):
            if dirt_grid[r][c] == 1:
                dirty_positions.append((r, c))

    return dirty_positions


def manhattan(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    return abs(r1 - r2) + abs(c1 - c2)


def heuristic(state):
    """
    h(n) dùng cho máy hút bụi:
    - Nếu hết bụi: h = 0
    - Nếu còn bụi: h = số ô bẩn còn lại + khoảng cách Manhattan tới ô bẩn gần nhất
    """
    robot_r, robot_c, dirt_grid = state
    dirty_positions = get_dirty_positions(state)

    if not dirty_positions:
        return 0

    min_distance = min(
        manhattan((robot_r, robot_c), dirt_pos)
        for dirt_pos in dirty_positions
    )

    return len(dirty_positions) + min_distance


# ============================================================
# FORMAT RIÊNG CHO GREEDY VÀ A*
# ============================================================

def format_frontier_after_greedy(children_added, node_name, node_info, parent_state=None):
    if not children_added:
        return "Không sinh thêm node mới"

    result = []

    for action, state in children_added:
        result.append(format_frontier_item(state, node_name, node_info))

    return "\n\n".join(result)


def format_frontier_after_astar(children_added, node_name, node_info, g_score, parent_state=None):
    if not children_added:
        return "Không sinh thêm node mới"

    result = []

    for action, state in children_added:
        result.append(format_frontier_item(state, node_name, node_info))

    return "\n\n".join(result)


def format_priority_frontier_list(frontier, node_name, algo, reached=None, node_info=None):
    if not frontier:
        return "[]"

    states = []
    reached = reached or set()

    for item in sorted(frontier, key=lambda value: (value[0], value[1])):
        state = item[2]

        if state in reached:
            continue

        states.append(state)

    if not states:
        return "[]"

    if node_info is None:
        labels = []

        for state in states:
            labels.append(node_name[state])

        return "[" + ", ".join(labels) + "]"

    return format_frontier_states(states, node_name, node_info)


# ============================================================
# BFS CÓ TRACE
# ============================================================

def bfs_with_trace(start_state, version):
    check_goal_when_generated = version == 2
    neighbor_version = 1
    queue = deque()
    queue.append((start_state, []))

    discovered = set()
    discovered.add(start_state)

    node_name = {}
    node_order = []

    get_label(start_state, node_name, node_order)
    node_info = {}
    remember_node_info(node_info, start_state, None, None, 0, node_name)

    visited_order = []

    trace = []
    step = 0

    if check_goal_when_generated and is_goal(start_state):
        visited_order.append(start_state)
        trace.append({
            "step": 1,
            "node": node_name[start_state],
            "frontier": "GOAL",
            "reached": format_reached(visited_order, node_name)
        })

        return [], trace, node_name

    while queue:
        current_state, path = queue.popleft()
        step += 1

        # Reached là các node đã được duyệt
        if current_state not in visited_order:
            visited_order.append(current_state)

        if is_goal(current_state) and not check_goal_when_generated:
            trace.append({
                "step": step,
                "node": node_name[current_state],
                "frontier": "GOAL",
                "reached": format_reached(visited_order, node_name)
            })

            return path, trace, node_name

        frontier_before = format_frontier_list(queue, node_name, "BFS", node_info)
        children_added = []

        for action, next_state in get_neighbors(current_state, neighbor_version):
            if next_state not in discovered:
                discovered.add(next_state)

                get_label(next_state, node_name, node_order)
                remember_node_info(node_info, next_state, current_state, action, 1, node_name)

                new_path = path + [(action, next_state)]
                queue.append((next_state, new_path))

                children_added.append((action, next_state))

                if check_goal_when_generated and is_goal(next_state):
                    children_text = format_frontier_after(children_added, node_name, node_info, current_state)
                    frontier_after = format_frontier_list(queue, node_name, "BFS", node_info)
                    frontier_text = format_frontier_sections(
                        frontier_before,
                        children_text,
                        frontier_after,
                        f"GOAL khi sinh node {node_name[next_state]}"
                    )

                    trace.append({
                        "step": step,
                        "node": node_name[current_state],
                        "frontier": frontier_text,
                        "reached": format_reached(visited_order, node_name)
                    })

                    return new_path, trace, node_name

        children_text = format_frontier_after(children_added, node_name, node_info, current_state)
        frontier_after = format_frontier_list(queue, node_name, "BFS", node_info)
        frontier_text = format_frontier_sections(
            frontier_before,
            children_text,
            frontier_after
        )

        trace.append({
            "step": step,
            "node": node_name[current_state],
            "frontier": frontier_text,
            "reached": format_reached(visited_order, node_name)
        })

    return None, trace, node_name


# ============================================================
# DFS CÓ TRACE
# ============================================================

def dfs_with_trace(start_state, version, max_depth=25):
    check_goal_when_generated = version == 2
    neighbor_version = 1
    stack = []
    stack.append((start_state, []))

    discovered = set()
    discovered.add(start_state)

    node_name = {}
    node_order = []

    get_label(start_state, node_name, node_order)
    node_info = {}
    remember_node_info(node_info, start_state, None, None, 0, node_name)

    visited_order = []

    trace = []
    step = 0

    if check_goal_when_generated and is_goal(start_state):
        visited_order.append(start_state)
        trace.append({
            "step": 1,
            "node": node_name[start_state],
            "frontier": "GOAL",
            "reached": format_reached(visited_order, node_name)
        })

        return [], trace, node_name

    while stack:
        current_state, path = stack.pop()
        step += 1

        # Reached là các node đã được duyệt
        if current_state not in visited_order:
            visited_order.append(current_state)

        if is_goal(current_state) and not check_goal_when_generated:
            trace.append({
                "step": step,
                "node": node_name[current_state],
                "frontier": "GOAL",
                "reached": format_reached(visited_order, node_name)
            })

            return path, trace, node_name

        frontier_before = format_frontier_list(stack, node_name, "DFS", node_info)

        if len(path) >= max_depth:
            children_text = "Cắt nhánh vì đạt max depth"
            frontier_text = format_frontier_sections(
                frontier_before,
                children_text,
                format_frontier_list(stack, node_name, "DFS", node_info)
            )

            trace.append({
                "step": step,
                "node": node_name[current_state],
                "frontier": frontier_text,
                "reached": format_reached(visited_order, node_name)
            })

            continue

        neighbors = get_neighbors(current_state, neighbor_version)

        children_added = []

        for action, next_state in neighbors:
            if next_state not in discovered:
                discovered.add(next_state)

                get_label(next_state, node_name, node_order)
                remember_node_info(node_info, next_state, current_state, action, 1, node_name)

                children_added.append((action, next_state))

                if check_goal_when_generated and is_goal(next_state):
                    children_text = format_frontier_after(children_added, node_name, node_info, current_state)
                    frontier_text = format_frontier_sections(
                        frontier_before,
                        children_text,
                        format_frontier_list(stack, node_name, "DFS", node_info),
                        f"GOAL khi sinh node {node_name[next_state]}"
                    )

                    trace.append({
                        "step": step,
                        "node": node_name[current_state],
                        "frontier": frontier_text,
                        "reached": format_reached(visited_order, node_name)
                    })

                    return path + [(action, next_state)], trace, node_name

        # DFS dùng stack.
        # Muốn Step 2 duyệt Node B thì Node B phải nằm trên đỉnh stack.
        for action, next_state in reversed(children_added):
            stack.append((next_state, path + [(action, next_state)]))

        children_text = format_frontier_after(children_added, node_name, node_info, current_state)
        frontier_after = format_frontier_list(stack, node_name, "DFS", node_info)
        frontier_text = format_frontier_sections(
            frontier_before,
            children_text,
            frontier_after
        )

        trace.append({
            "step": step,
            "node": node_name[current_state],
            "frontier": frontier_text,
            "reached": format_reached(visited_order, node_name)
        })

    return None, trace, node_name


# ============================================================
# UCS CÓ TRACE
# ============================================================

def get_action_cost(action):
    return 1


def ucs_with_trace(start_state, version):
    priority_queue = []
    order = 0

    heapq.heappush(priority_queue, (0, order, start_state, []))

    best_cost = {}
    best_cost[start_state] = 0

    node_name = {}
    node_order = []
    get_label(start_state, node_name, node_order)
    node_info = {}
    remember_node_info(node_info, start_state, None, None, 0, node_name)

    visited_order = []
    trace = []
    step = 0

    while priority_queue:
        current_cost, _, current_state, path = heapq.heappop(priority_queue)

        if current_cost != best_cost[current_state]:
            continue

        step += 1

        if current_state not in visited_order:
            visited_order.append(current_state)

        if is_goal(current_state):
            trace.append({
                "step": step,
                "node": node_name[current_state],
                "frontier": f"GOAL\ng(n) = {current_cost}",
                "reached": format_reached(visited_order, node_name)
            })

            return path, trace, node_name

        frontier_before = format_frontier_list(priority_queue, node_name, "UCS", node_info)
        children_added = []

        for action, next_state in get_neighbors(current_state, version):
            new_cost = current_cost + get_action_cost(action)

            if next_state not in best_cost or new_cost < best_cost[next_state]:
                best_cost[next_state] = new_cost
                get_label(next_state, node_name, node_order)
                remember_node_info(node_info, next_state, current_state, action, get_action_cost(action), node_name)

                order += 1
                heapq.heappush(
                    priority_queue,
                    (new_cost, order, next_state, path + [(action, next_state)])
                )

                children_added.append((action, next_state, new_cost))

        children_text = format_frontier_after(children_added, node_name, node_info, current_state)
        frontier_after = format_frontier_list(priority_queue, node_name, "UCS", node_info)
        frontier_text = format_frontier_sections(
            frontier_before,
            children_text,
            frontier_after,
            f"g(n) = {current_cost}"
        )

        trace.append({
            "step": step,
            "node": node_name[current_state],
            "frontier": frontier_text,
            "reached": format_reached(visited_order, node_name)
        })

    return None, trace, node_name


# ============================================================
# IDFS CÓ TRACE
# ============================================================

def depth_limited_search(start_state, version, limit, node_name, node_order, node_info):
    stack = []
    stack.append((start_state, []))

    discovered = set()
    discovered.add(start_state)

    visited_order = []

    trace = []
    step = 0

    get_label(start_state, node_name, node_order)
    remember_node_info(node_info, start_state, None, None, 0, node_name)

    while stack:
        current_state, path = stack.pop()
        step += 1

        if current_state not in visited_order:
            visited_order.append(current_state)

        current_depth = len(path)

        if is_goal(current_state):
            trace.append({
                "step": step,
                "node": node_name[current_state],
                "depth": current_depth,
                "frontier": f"GOAL\nDepth Limit = {limit}",
                "reached": format_reached(visited_order, node_name)
            })

            return path, trace, True

        frontier_before = format_frontier_list(stack, node_name, "DFS", node_info)

        if current_depth >= limit:
            children_text = "Cắt nhánh vì đạt Depth Limit"
            frontier_text = format_frontier_sections(
                frontier_before,
                children_text,
                format_frontier_list(stack, node_name, "DFS", node_info),
                f"Depth hiện tại = {current_depth}\nDepth Limit = {limit}"
            )

            trace.append({
                "step": step,
                "node": node_name[current_state],
                "depth": current_depth,
                "frontier": frontier_text,
                "reached": format_reached(visited_order, node_name)
            })

            continue

        neighbors = get_neighbors(current_state, version)

        children_added = []

        for action, next_state in neighbors:
            if next_state not in discovered:
                discovered.add(next_state)

                get_label(next_state, node_name, node_order)
                remember_node_info(node_info, next_state, current_state, action, 1, node_name)

                children_added.append((action, next_state))

        # IDFS bên trong dùng DFS có giới hạn độ sâu.
        # Đảo lại để Node B được duyệt trước.
        for action, next_state in reversed(children_added):
            stack.append((next_state, path + [(action, next_state)]))

        children_text = format_frontier_after(children_added, node_name, node_info, current_state)
        frontier_after = format_frontier_list(stack, node_name, "DFS", node_info)
        frontier_text = format_frontier_sections(
            frontier_before,
            children_text,
            frontier_after,
            f"Depth hiện tại = {current_depth}\nDepth Limit = {limit}"
        )

        trace.append({
            "step": step,
            "node": node_name[current_state],
            "depth": current_depth,
            "frontier": frontier_text,
            "reached": format_reached(visited_order, node_name)
        })

    return None, trace, False


def idfs_with_trace(start_state, version, max_depth=25):
    node_name = {}
    node_order = []
    node_info = {}

    get_label(start_state, node_name, node_order)
    remember_node_info(node_info, start_state, None, None, 0, node_name)

    all_trace = []
    total_step = 0

    for limit in range(max_depth + 1):
        path, trace, found = depth_limited_search(
            start_state,
            version,
            limit,
            node_name,
            node_order,
            node_info
        )

        for row in trace:
            total_step += 1

            all_trace.append({
                "step": total_step,
                "node": row["node"],
                "depth": row["depth"],
                "frontier": (
                    f"IDFS đang chạy với Depth Limit = {limit}\n\n"
                    + row["frontier"]
                ),
                "reached": row["reached"]
            })

        if found:
            return path, all_trace, node_name

    return None, all_trace, node_name




# ============================================================
# GREEDY BEST-FIRST SEARCH CÓ TRACE
# ============================================================

def greedy_with_trace(start_state, version):
    heap = []
    order = 0
    heapq.heappush(heap, (heuristic(start_state), order, start_state, []))

    in_frontier = set()
    in_frontier.add(start_state)

    reached = set()
    node_name = {}
    node_order = []
    get_label(start_state, node_name, node_order)
    node_info = {}
    remember_node_info(node_info, start_state, None, None, 0, node_name)

    visited_order = []
    trace = []
    step = 0

    while heap:
        h_current, _, current_state, path = heapq.heappop(heap)

        if current_state in reached:
            continue

        in_frontier.discard(current_state)
        reached.add(current_state)
        step += 1

        if current_state not in visited_order:
            visited_order.append(current_state)

        if is_goal(current_state):
            trace.append({
                "step": step,
                "node": node_name[current_state],
                "frontier": "GOAL",
                "reached": format_reached(visited_order, node_name)
            })
            return path, trace, node_name

        frontier_before = format_priority_frontier_list(heap, node_name, "Greedy", reached, node_info)
        children_added = []

        for action, next_state in get_neighbors(current_state, version):
            if next_state not in reached and next_state not in in_frontier:
                get_label(next_state, node_name, node_order)
                remember_node_info(
                    node_info,
                    next_state,
                    current_state,
                    action,
                    1,
                    node_name,
                    h_value=heuristic(next_state)
                )
                order += 1
                heapq.heappush(
                    heap,
                    (heuristic(next_state), order, next_state, path + [(action, next_state)])
                )
                in_frontier.add(next_state)
                children_added.append((action, next_state))

        children_text = format_frontier_after_greedy(children_added, node_name, node_info, current_state)
        frontier_after = format_priority_frontier_list(heap, node_name, "Greedy", reached, node_info)
        frontier_text = format_frontier_sections(
            frontier_before,
            children_text,
            frontier_after
        )

        trace.append({
            "step": step,
            "node": node_name[current_state],
            "frontier": frontier_text,
            "reached": format_reached(visited_order, node_name)
        })

    return None, trace, node_name


# ============================================================
# A* SEARCH CÓ TRACE
# ============================================================

def astar_with_trace(start_state, version):
    heap = []
    order = 0
    g_score = {}
    g_score[start_state] = 0

    f_start = g_score[start_state] + heuristic(start_state)
    heapq.heappush(heap, (f_start, order, start_state, []))

    reached = set()
    node_name = {}
    node_order = []
    get_label(start_state, node_name, node_order)
    node_info = {}
    remember_node_info(node_info, start_state, None, None, 0, node_name, f_start)

    visited_order = []
    trace = []
    step = 0

    while heap:
        f_current, _, current_state, path = heapq.heappop(heap)

        if current_state in reached:
            continue

        reached.add(current_state)
        step += 1

        if current_state not in visited_order:
            visited_order.append(current_state)

        g_current = g_score[current_state]
        h_current = heuristic(current_state)

        if is_goal(current_state):
            trace.append({
                "step": step,
                "node": node_name[current_state],
                "frontier": "GOAL",
                "reached": format_reached(visited_order, node_name)
            })
            return path, trace, node_name

        frontier_before = format_priority_frontier_list(heap, node_name, "A*", reached, node_info)
        children_added = []

        for action, next_state in get_neighbors(current_state, version):
            new_g = g_current + 1

            if next_state in reached and new_g >= g_score.get(next_state, 999999):
                continue

            if new_g < g_score.get(next_state, 999999):
                get_label(next_state, node_name, node_order)
                g_score[next_state] = new_g
                new_f = new_g + heuristic(next_state)
                remember_node_info(node_info, next_state, current_state, action, 1, node_name, new_f)
                order += 1
                heapq.heappush(
                    heap,
                    (new_f, order, next_state, path + [(action, next_state)])
                )
                children_added.append((action, next_state))

        children_text = format_frontier_after_astar(children_added, node_name, node_info, g_score, current_state)
        frontier_after = format_priority_frontier_list(heap, node_name, "A*", reached, node_info)
        frontier_text = format_frontier_sections(
            frontier_before,
            children_text,
            frontier_after
        )

        trace.append({
            "step": step,
            "node": node_name[current_state],
            "frontier": frontier_text,
            "reached": format_reached(visited_order, node_name)
        })

    return None, trace, node_name


# ============================================================
# GIAO DIỆN TKINTER
# ============================================================

class VacuumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng máy hút bụi")
        self.root.geometry("1250x780")

        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0
        self.node_name = {}

        title = tk.Label(
            root,
            text="MÔ PHỎNG MÁY HÚT BỤI",
            font=("Arial", 17, "bold")
        )
        title.pack(pady=8)

        # ====================================================
        # KHUNG TRÊN
        # ====================================================

        top_frame = tk.Frame(root)
        top_frame.pack(pady=5)

        input_frame = tk.LabelFrame(
            top_frame,
            text="Nhập ma trận",
            padx=10,
            pady=10
        )
        input_frame.grid(row=0, column=0, padx=10)

        self.matrix_input = tk.Text(
            input_frame,
            width=28,
            height=6,
            font=("Consolas", 13)
        )
        self.matrix_input.pack()

        default_matrix = """3 0 1
0 1 0
1 0 0"""
        self.matrix_input.insert("1.0", default_matrix)

        note = tk.Label(
            top_frame,
            text=(
                "Quy ước nhập:\n"
                "0 = ô sạch\n"
                "1 = ô bẩn\n"
                "2 = robot ở ô sạch\n"
                "3 = robot ở ô bẩn\n\n"
                "Khi hiển thị:\n"
                "x = vị trí robot\n"
                "Ô x không ghi sạch/bẩn\n"
                "Robot đi tới ô bẩn thì ô đó tự sạch\n"
                "Node đầu tiên = A"
            ),
            justify="left",
            font=("Arial", 11)
        )
        note.grid(row=0, column=1, padx=10)

        option_frame = tk.LabelFrame(
            top_frame,
            text="Chọn thuật toán",
            padx=10,
            pady=10
        )
        option_frame.grid(row=0, column=2, padx=10)

        self.algo_var = tk.StringVar()
        self.algo_var.set("BFS - TC1 (goal khi xét)")

        algo_options = [
            "BFS - TC1 (goal khi xét)",
            "BFS - TC2 (goal khi sinh)",
            "DFS - TC1 (goal khi xét)",
            "DFS - TC2 (goal khi sinh)",
            "IDFS",
            "UCS",
            "Greedy_search",
            "A*"
        ]

        self.algo_menu = tk.OptionMenu(
            option_frame,
            self.algo_var,
            *algo_options
        )
        self.algo_menu.config(width=28)
        self.algo_menu.pack(pady=5)

        # ====================================================
        # BUTTON
        # ====================================================

        button_frame = tk.Frame(root)
        button_frame.pack(pady=8)

        tk.Button(
            button_frame,
            text="Chạy thuật toán",
            width=16,
            bg="#4CAF50",
            fg="white",
            command=self.solve
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Bước trước",
            width=16,
            command=self.prev_step
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="Bước tiếp",
            width=16,
            command=self.next_step
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            button_frame,
            text="Reset",
            width=16,
            bg="#f44336",
            fg="white",
            command=self.reset
        ).grid(row=0, column=3, padx=5)

        # ====================================================
        # TRẠNG THÁI VÀ ĐƯỜNG ĐI
        # ====================================================

        self.status_label = tk.Label(
            root,
            text="Nhấn 'Chạy thuật toán' để bắt đầu.",
            font=("Arial", 12),
            fg="blue"
        )
        self.status_label.pack(pady=5)

        self.path_label = tk.Label(
            root,
            text="Đường đi lời giải: ",
            font=("Arial", 11),
            wraplength=1150,
            justify="left"
        )
        self.path_label.pack(pady=5)

        # ====================================================
        # KHUNG GIỮA: MA TRẬN + BẢNG
        # ====================================================

        middle_frame = tk.Frame(root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.grid_frame = tk.LabelFrame(
            middle_frame,
            text="Ma trận mô phỏng",
            padx=10,
            pady=10
        )
        self.grid_frame.pack(side="left", fill="both", padx=10)

        table_frame = tk.LabelFrame(
            middle_frame,
            text="Bảng duyệt chi tiết: Node - Frontier - Reached",
            padx=5,
            pady=5
        )
        table_frame.pack(side="right", fill="both", expand=True, padx=10)

        self.trace_text = tk.Text(
            table_frame,
            wrap="none",
            font=("Consolas", 10),
            width=105,
            height=24,
            bg="white",
            relief="solid",
            borderwidth=1
        )
        self.trace_text.configure(state="disabled")

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.trace_text.yview
        )

        x_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.trace_text.xview
        )

        self.trace_text.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.trace_text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    # ========================================================
    # VẼ MA TRẬN MÔ PHỎNG BÊN TRÁI
    # ========================================================

    def draw_grid(self, state):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        robot_r, robot_c, dirt_grid = state

        for r in range(len(dirt_grid)):
            for c in range(len(dirt_grid[0])):
                dirt = dirt_grid[r][c]

                if r == robot_r and c == robot_c:
                    text = "x"
                    bg_color = "white"
                else:
                    if dirt == 1:
                        text = "1\nBẩn"
                        bg_color = "#ffab91"
                    else:
                        text = "0\nSạch"
                        bg_color = "#c8e6c9"

                cell = tk.Label(
                    self.grid_frame,
                    text=text,
                    width=10,
                    height=4,
                    bg=bg_color,
                    relief="solid",
                    borderwidth=1,
                    font=("Arial", 14, "bold")
                )

                cell.grid(row=r, column=c, padx=3, pady=3)

    # ========================================================
    # HIỂN THỊ TRACE VÀO BẢNG
    # ========================================================

    def wrap_table_line(self, text, width):
        text = str(text)

        if text == "":
            return [""]

        result = []

        for line in text.splitlines():
            if line == "":
                result.append("")
                continue

            while len(line) > width:
                cut = line.rfind(" ", 0, width + 1)

                if cut <= 0:
                    cut = line.rfind(",", 0, width + 1)

                if cut <= 0:
                    cut = width

                result.append(line[:cut].rstrip())
                line = line[cut:].lstrip()

            result.append(line)

        return result

    def make_trace_table_text(self):
        has_depth_column = any("depth" in row for row in self.trace)
        node_width = 8
        depth_width = 8
        frontier_width = 60 if has_depth_column else 64
        reached_width = 34 if has_depth_column else 36

        if has_depth_column:
            border = (
                "+"
                + "-" * (node_width + 2)
                + "+"
                + "-" * (depth_width + 2)
                + "+"
                + "-" * (frontier_width + 2)
                + "+"
                + "-" * (reached_width + 2)
                + "+"
            )
        else:
            border = (
                "+"
                + "-" * (node_width + 2)
                + "+"
                + "-" * (frontier_width + 2)
                + "+"
                + "-" * (reached_width + 2)
                + "+"
            )

        if has_depth_column:
            def line_text(node, depth, frontier, reached):
                return (
                    "| "
                    + node.ljust(node_width)
                    + " | "
                    + depth.ljust(depth_width)
                    + " | "
                    + frontier.ljust(frontier_width)
                    + " | "
                    + reached.ljust(reached_width)
                    + " |"
                )
        else:
            def line_text(node, frontier, reached):
                return (
                    "| "
                    + node.ljust(node_width)
                    + " | "
                    + frontier.ljust(frontier_width)
                    + " | "
                    + reached.ljust(reached_width)
                    + " |"
                )

        table_lines = [border]

        if has_depth_column:
            table_lines.append(line_text("Node", "Depth", "Frontier", "Reached"))
        else:
            table_lines.append(line_text("Node", "Frontier", "Reached"))

        table_lines.append(border)

        for row in self.trace:
            node_lines = self.wrap_table_line(row["node"], node_width)
            depth_lines = self.wrap_table_line(row.get("depth", ""), depth_width)
            frontier_lines = self.wrap_table_line(row["frontier"], frontier_width)
            reached_lines = self.wrap_table_line(row["reached"], reached_width)
            row_height = max(len(node_lines), len(depth_lines), len(frontier_lines), len(reached_lines))

            while len(node_lines) < row_height:
                node_lines.append("")

            while len(depth_lines) < row_height:
                depth_lines.append("")

            while len(frontier_lines) < row_height:
                frontier_lines.append("")

            while len(reached_lines) < row_height:
                reached_lines.append("")

            for index in range(row_height):
                if has_depth_column:
                    table_lines.append(
                        line_text(
                            node_lines[index],
                            depth_lines[index],
                            frontier_lines[index],
                            reached_lines[index]
                        )
                    )
                else:
                    table_lines.append(
                        line_text(
                            node_lines[index],
                            frontier_lines[index],
                            reached_lines[index]
                        )
                    )

            table_lines.append(border)

        return "\n".join(table_lines)

    def show_trace_table(self):
        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.insert("1.0", self.make_trace_table_text())
        self.trace_text.configure(state="disabled")

    # ========================================================
    # CHẠY THUẬT TOÁN
    # ========================================================

    def solve(self):
        try:
            text = self.matrix_input.get("1.0", tk.END)
            self.start_state = parse_matrix(text)

            algo = self.algo_var.get()

            if algo == "BFS - TC1 (goal khi xét)":
                self.solution, self.trace, self.node_name = bfs_with_trace(
                    self.start_state,
                    version=1
                )

            elif algo == "BFS - TC2 (goal khi sinh)":
                self.solution, self.trace, self.node_name = bfs_with_trace(
                    self.start_state,
                    version=2
                )

            elif algo == "DFS - TC1 (goal khi xét)":
                self.solution, self.trace, self.node_name = dfs_with_trace(
                    self.start_state,
                    version=1
                )

            elif algo == "DFS - TC2 (goal khi sinh)":
                self.solution, self.trace, self.node_name = dfs_with_trace(
                    self.start_state,
                    version=2
                )

            elif algo == "IDFS":
                self.solution, self.trace, self.node_name = idfs_with_trace(
                    self.start_state,
                    version=1
                )

            elif algo == "UCS":
                self.solution, self.trace, self.node_name = ucs_with_trace(
                    self.start_state,
                    version=1
                )

            elif algo == "Greedy_search":
                self.solution, self.trace, self.node_name = greedy_with_trace(
                    self.start_state,
                    version=1
                )

            elif algo == "A*":
                self.solution, self.trace, self.node_name = astar_with_trace(
                    self.start_state,
                    version=1
                )

            self.current_step = 0
            self.draw_grid(self.start_state)
            self.show_trace_table()

            if self.solution is None:
                self.status_label.config(
                    text=f"{algo}: Không tìm thấy lời giải."
                )
                self.path_label.config(
                    text="Đường đi lời giải: Không có"
                )
                return

            path_text = []
            current_state = self.start_state
            current_label = self.node_name[current_state]

            for action, next_state in self.solution:
                next_label = self.node_name[next_state]
                path_text.append(f"{current_label} --{action}--> {next_label}")

                current_state = next_state
                current_label = next_label

            self.status_label.config(
                text=f"{algo}: Tìm thấy lời giải gồm {len(self.solution)} bước. Node đầu là A."
            )

            self.path_label.config(
                text="Đường đi lời giải: " + " | ".join(path_text)
            )

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ========================================================
    # BƯỚC TIẾP
    # ========================================================

    def next_step(self):
        if self.start_state is None or not self.solution:
            messagebox.showwarning(
                "Thông báo",
                "Bạn cần chạy thuật toán trước."
            )
            return

        if self.current_step < len(self.solution):
            action, state = self.solution[self.current_step]
            self.current_step += 1

            self.draw_grid(state)

            label = self.node_name[state]

            self.status_label.config(
                text=f"Bước {self.current_step}: {action} → Node {label}"
            )

        else:
            self.status_label.config(
                text="Đã hoàn thành. Tất cả ô đã sạch."
            )

    # ========================================================
    # BƯỚC TRƯỚC
    # ========================================================

    def prev_step(self):
        if self.start_state is None or not self.solution:
            messagebox.showwarning(
                "Thông báo",
                "Bạn cần chạy thuật toán trước."
            )
            return

        if self.current_step > 0:
            self.current_step -= 1

            if self.current_step == 0:
                self.draw_grid(self.start_state)
                self.status_label.config(text="Bước 0: Node A")
            else:
                action, state = self.solution[self.current_step - 1]
                self.draw_grid(state)

                label = self.node_name[state]

                self.status_label.config(
                    text=f"Bước {self.current_step}: {action} → Node {label}"
                )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        self.start_state = None
        self.solution = []
        self.trace = []
        self.current_step = 0
        self.node_name = {}

        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.trace_text.configure(state="normal")
        self.trace_text.delete("1.0", tk.END)
        self.trace_text.configure(state="disabled")

        self.status_label.config(
            text="Đã reset. Nhấn 'Chạy thuật toán' để bắt đầu."
        )

        self.path_label.config(
            text="Đường đi lời giải: "
        )


# ============================================================
# MAIN
# ============================================================

root = tk.Tk()

root.lift()
root.attributes("-topmost", True)
root.after(1000, lambda: root.attributes("-topmost", False))

app = VacuumApp(root)

root.mainloop()
