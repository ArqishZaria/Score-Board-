#to change the tasks file, edit line 93 of main.py & line 254 of avl_pygame_visualizer.py
import pygame
import sys
import math
import builtins
import traceback
import main as avl_main  # import main module under alias to avoid shadowing

# override built-in print to route through our on-screen buffer
def _print_override(*args, **kwargs):
    _messages.append(" ".join(str(a) for a in args))
builtins.print = _print_override

# message buffer and scrolling for print panel
_messages = []
prints_scroll = 0  # vertical scroll offset for prints

# Configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 750
FONT_SIZE = 20
NODE_BASE_RADIUS = 40
LEVEL_HEIGHT = 100
BUTTON_WIDTH, BUTTON_HEIGHT = 100, 60
BUTTON_MARGIN = 20
ANIM_FRAMES = 15
ANIM_DELAY_MS = 30
HIGHLIGHT_DURATION_FRAMES = 30
PRINT_PANEL_WIDTH = 300
TASK_PANEL_WIDTH = 300
SCROLL_SPEED = FONT_SIZE + 4  # pixels per scroll

# Colors
EDGE_COLOR = (50, 50, 50)
BUTTON_COLOR = (70, 130, 180)
BUTTON_TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (30, 30, 30)
PANEL_BG_COLOR = (245, 245, 245)
PANEL_TEXT_COLOR = (60, 60, 60)
PANEL_HIGHLIGHT_COLOR = (70, 130, 180)
SCROLLBAR_BG = (200, 200, 200)
SCROLLBAR_FG = (100, 100, 100)
PRINT_TEXT_COLOR = (0, 0, 0)

# Task state
tasks = []
task_index = 0
last_op_node = None
highlight_timer = 0
tasks_scroll = 0  # vertical scroll offset for tasks

# Load tasks
def load_tasks(filename):
    try:
        with open(filename) as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{filename} not found.")
        sys.exit(1)

# Load initial data into tree
def load_data(filename):
    try:
        with open(filename) as f:
            for line in f:
                name, score_str = line.strip().split(',')
                score = int(score_str)
                avl_main.root = avl_main.insert_node(avl_main.root, name, score)
    except FileNotFoundError:
        pass  # start with empty

def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node['left']) + count_nodes(node['right'])

# Layout
def layout_positions(node, x_min, x_max, y, positions):
    if node is None:
        return
    # figure out how many nodes are in each subtree
    total = count_nodes(node)
    left_count = count_nodes(node['left'])
    # position this node at ½ a slot past the left subtree
    # +0.5 so we center in its “block”
    frac = (left_count + 0.5) / total
    x = int(x_min + frac * (x_max - x_min))
    positions[id(node)] = (x, y)
    # recursively carve out the left and right sub‐intervals
    layout_positions(node['left'],  x_min, x,       y + LEVEL_HEIGHT, positions)
    layout_positions(node['right'], x,     x_max,   y + LEVEL_HEIGHT, positions)

# Background
def draw_gradient_bg(screen):
    for yi in range(SCREEN_HEIGHT):
        ratio = yi / SCREEN_HEIGHT
        r = int(255*(1-ratio) + 200*ratio)
        g = int(255*(1-ratio) + 230*ratio)
        b = int(255*(1-ratio) + 210*ratio)
        pygame.draw.line(screen, (r, g, b),
                         (PRINT_PANEL_WIDTH, yi),
                         (SCREEN_WIDTH - TASK_PANEL_WIDTH, yi))

# Draw edges and nodes
def draw_edges(screen, positions, node):
    if not node:
        return
    x, y = positions[id(node)]
    for child in ('left', 'right'):
        c = node[child]
        if c:
            cx, cy = positions[id(c)]
            pygame.draw.aaline(screen, EDGE_COLOR, (x, y), (cx, cy))
    draw_edges(screen, positions, node['left'])
    draw_edges(screen, positions, node['right'])


def draw_nodes(screen, font, positions, node):
    global highlight_timer
    if not node:
        return
    x, y = positions[id(node)]
    score = node['score']
    t = min(score / 2500, 1.0)
    node_color = (
        int(100*(1-t) + 60*t),
        int(149*(1-t) + 200*t),
        int(237*(1-t) + 100*t)
    )
    is_high = (highlight_timer > 0 and id(node) == last_op_node)
    radius = NODE_BASE_RADIUS + (10 if is_high else 0)
    if is_high:
        pulse = math.sin((HIGHLIGHT_DURATION_FRAMES - highlight_timer) /
                          HIGHLIGHT_DURATION_FRAMES * math.pi)
        radius += int(15 * pulse)
    pygame.draw.circle(screen, (200,200,200), (x+4, y+4), radius)
    pygame.draw.circle(screen, node_color, (x, y), radius)
    txt = font.render(f"{node['name']} : {score}", True, (20,20,20))
    screen.blit(txt, txt.get_rect(center=(x, y)))
    draw_nodes(screen, font, positions, node['left'])
    draw_nodes(screen, font, positions, node['right'])

# Button
def draw_button(screen, font, x, y, text):
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=8)
    txt = font.render(text, True, BUTTON_TEXT_COLOR)
    screen.blit(txt, txt.get_rect(center=rect.center))
    return rect

# Print panel on left
def draw_print_panel(screen, font):
    global prints_scroll
    # background
    screen.fill(PANEL_BG_COLOR, (0, 0, PRINT_PANEL_WIDTH, SCREEN_HEIGHT))

    # title
    title = font.render("Output:", True, TITLE_COLOR)
    screen.blit(title, (10, 10))

    # layout metrics
    top_y = 40
    line_h = FONT_SIZE + 4
    total_h = len(_messages) * line_h
    max_scroll = max(0, total_h - (SCREEN_HEIGHT - top_y - 10))

    # clamp scroll
    prints_scroll = max(0, min(prints_scroll, max_scroll))

    # render each message, highlight the last one
    total_msgs = len(_messages)
    for i, msg in enumerate(_messages):
        y = top_y + i * line_h - prints_scroll
        if top_y - line_h <= y <= SCREEN_HEIGHT - line_h:
            color = PANEL_HIGHLIGHT_COLOR if i == total_msgs - 1 else PRINT_TEXT_COLOR
            screen.blit(font.render(msg, True, color), (10, y))

    # draw scrollbar if needed
    if total_h > SCREEN_HEIGHT - top_y - 10:
        bx = PRINT_PANEL_WIDTH - 15
        by = top_y
        bw = 8
        bh = SCREEN_HEIGHT - top_y - 10
        pygame.draw.rect(screen, SCROLLBAR_BG, (bx, by, bw, bh), border_radius=4)
        thumb_h = max(20, int(bh * (bh / total_h)))
        ty = by + int(prints_scroll / max_scroll * (bh - thumb_h)) if max_scroll > 0 else by
        pygame.draw.rect(screen, SCROLLBAR_FG, (bx, ty, bw, thumb_h), border_radius=4)

# Task panel on right
def draw_tasks_panel(screen, font):
    global tasks_scroll
    panel_x = SCREEN_WIDTH - TASK_PANEL_WIDTH
    screen.fill(PANEL_BG_COLOR, (panel_x, 0, TASK_PANEL_WIDTH, SCREEN_HEIGHT))
    title = font.render("Tasks:", True, TITLE_COLOR)
    screen.blit(title, (panel_x + 10, 10))
    top_y = 40
    line_h = FONT_SIZE + 4
    total_h = len(tasks) * line_h
    max_scroll = max(0, total_h - (SCREEN_HEIGHT - top_y - 10))
    tasks_scroll = max(0, min(tasks_scroll, max_scroll))
    for i, task in enumerate(tasks):
        y = top_y + i*line_h - tasks_scroll
        if top_y - line_h <= y <= SCREEN_HEIGHT - line_h:
            color = PANEL_HIGHLIGHT_COLOR if i == task_index else PANEL_TEXT_COLOR
            screen.blit(font.render(task, True, color), (panel_x + 10, y))
    if total_h > SCREEN_HEIGHT - top_y - 10:
        bx = panel_x + TASK_PANEL_WIDTH - 15
        by = top_y
        bw = 8
        bh = SCREEN_HEIGHT - top_y - 10
        pygame.draw.rect(screen, SCROLLBAR_BG, (bx, by, bw, bh), border_radius=4)
        thumb_h = max(20, int(bh * (bh/total_h)))
        ty = by + int(tasks_scroll/max_scroll * (bh - thumb_h)) if max_scroll>0 else by
        pygame.draw.rect(screen, SCROLLBAR_FG, (bx, ty, bw, thumb_h), border_radius=4)

# Full frame draw
def draw_frame(screen, font, positions):
    global highlight_timer
    draw_gradient_bg(screen)
    draw_edges(screen, positions, avl_main.root)
    draw_nodes(screen, font, positions, avl_main.root)
    title = f"AVL Visualizer — Task {task_index}/{len(tasks)-1}" if task_index>0 else "AVL Visualizer — Start"
    screen.blit(font.render(title, True, TITLE_COLOR), (PRINT_PANEL_WIDTH + 10, 10))
    next_btn = draw_button(screen, font,
        SCREEN_WIDTH - TASK_PANEL_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN,
        SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN,
        "Next")
    draw_print_panel(screen, font)
    draw_tasks_panel(screen, font)
    if highlight_timer > 0:
        highlight_timer -= 1
    return next_btn

# Animate transitions
def animate_transition(screen, font, old_pos, new_pos):
    for frame in range(ANIM_FRAMES + 1):
        interp = {k: (
            old_pos.get(k, new_pos[k])[0] + (new_pos[k][0] - old_pos.get(k, new_pos[k])[0]) * frame/ANIM_FRAMES,
            old_pos.get(k, new_pos[k])[1] + (new_pos[k][1] - old_pos.get(k, new_pos[k])[1]) * frame/ANIM_FRAMES
        ) for k in new_pos}
        draw_frame(screen, font, interp)
        pygame.display.flip()
        pygame.time.delay(ANIM_DELAY_MS)

# Main loop
def main():
    global task_index, last_op_node, highlight_timer, tasks_scroll, prints_scroll
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AVL Tree Visualizer")
    font = pygame.font.SysFont(None, FONT_SIZE)
    # load data and tasks
    avl_main.root = None
    load_data('data.txt')
    tasks[:] = load_tasks('tasks,h3.txt')
    task_index = -1
    tasks_scroll = 0
    prints_scroll = 0
    clock = pygame.time.Clock()
    positions = {}
    layout_positions(avl_main.root, PRINT_PANEL_WIDTH, SCREEN_WIDTH - TASK_PANEL_WIDTH, 60, positions)
    next_btn = draw_frame(screen, font, positions)
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if next_btn.collidepoint(event.pos) and task_index < len(tasks) - 1:
                    old_pos = {}
                    layout_positions(avl_main.root, PRINT_PANEL_WIDTH, SCREEN_WIDTH - TASK_PANEL_WIDTH, 60, old_pos)
                    task_index += 1
                    try:
                        parts = [p.strip() for p in tasks[task_index].split(',')]
                        cmd = parts[0].lower()
                        if cmd == 'insert':
                            avl_main.insert_player(parts[1])
                            node = avl_main.search_player(avl_main.root, parts[1])
                            last_op_node = id(node) if node else None
                            highlight_timer = HIGHLIGHT_DURATION_FRAMES
                        elif cmd == 'update':
                            avl_main.update_player(parts[1], int(parts[2]))
                            node = avl_main.search_player(avl_main.root, parts[1])
                            last_op_node = id(node) if node else None
                            highlight_timer = HIGHLIGHT_DURATION_FRAMES
                        elif cmd == 'delete':
                            node = avl_main.search_player(avl_main.root, parts[1])
                            last_op_node = id(node) if node else None
                            highlight_timer = HIGHLIGHT_DURATION_FRAMES
                            avl_main.delete_player(parts[1])
                        elif cmd == 'search':
                            player = avl_main.search_player(avl_main.root, parts[1])
                            print(f"Found player: {player['name']} with score {player['score']}" if player else f"Player {parts[1]} not found.")
                            last_op_node = id(player) if player else None
                            highlight_timer = HIGHLIGHT_DURATION_FRAMES
                        elif cmd == 'top':
                            avl_main.get_top_players(avl_main.root)
                            top = avl_main.root
                            while top and top['right']:
                                top = top['right']
                            last_op_node = id(top) if top else None
                            highlight_timer = HIGHLIGHT_DURATION_FRAMES
                        elif cmd == 'leaderboard':
                            print("Leaderboard:")
                            avl_main.print_leaderboard(avl_main.root)
                            last_op_node = None
                            highlight_timer = HIGHLIGHT_DURATION_FRAMES
                        else:
                            print(f"Unknown task or wrong number of parameters: {cmd}")
                        # save
                        with open('data.txt', 'w') as f:
                            avl_main.save_leaderboard(avl_main.root, f)
                    except Exception as e:
                        print("Error executing task:")
                        print(str(e))
                        print(traceback.format_exc())
                    # animate
                    new_pos = {}
                    layout_positions(avl_main.root, PRINT_PANEL_WIDTH, SCREEN_WIDTH - TASK_PANEL_WIDTH, 60, new_pos)
                    animate_transition(screen, font, old_pos, new_pos)
            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if mx < PRINT_PANEL_WIDTH:
                    prints_scroll -= event.y * SCROLL_SPEED
                elif mx > SCREEN_WIDTH - TASK_PANEL_WIDTH:
                    tasks_scroll -= event.y * SCROLL_SPEED
            positions = {}
            layout_positions(avl_main.root, PRINT_PANEL_WIDTH, SCREEN_WIDTH - TASK_PANEL_WIDTH, 60, positions)
            next_btn = draw_frame(screen, font, positions)
            pygame.display.flip()
        clock.tick(60)
    pygame.quit()  # ensure clean exit without error
    # avoid sys.exit to prevent propagation


if __name__ == '__main__':
    main()