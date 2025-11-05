"""
Streamlit 俄羅斯方塊遊戲

如何執行：
1. 確保已安裝 streamlit: pip install streamlit
2. 在終端機中執行: streamlit run tetris.py
"""

import streamlit as st
import random
import time

# --- 遊戲核心常數 ---
FIELD_WIDTH = 12
FIELD_HEIGHT = 18
BLOCK_SIZE = 25 # 每個方塊的像素大小 (Streamlit 側邊欄較窄，改小一點)

# 方塊（"Tetromino"）的形狀 (4x4 網格)
tetromino = [
    "..X...X...X...X.", # 0: I 方塊
    "..X..XX..X......", # 1: Z 方塊
    ".X...XX...X.....", # 2: S 方塊
    ".....XX..XX.....", # 3: O 方塊
    ".X...X...XX.....", # 4: L 方塊
    "..X...X..XX.....", # 5: J 方塊
    ".X...XX...X....."  # 6: T 方塊
]

# 方塊顏色 (0=空白, 1=I, 2=Z, ..., 9=邊界)
COLORS = [
    "#1E1E1E", # 0: 空白 (深灰色背景)
    "cyan",    # 1: I
    "red",     # 2: Z
    "green",   # 3: S
    "yellow",  # 4: O
    "orange",  # 5: L
    "blue",    # 6: J
    "purple",  # 7: T
    "white",   # 8: 消除動畫 (未使用)
    "#555555"  # 9: 邊界 (灰色)
]

# --- 核心邏輯函式 ---

def rotate(px, py, r):
    """
    根據旋轉角度 r (0, 1, 2, 3) 回傳 4x4 網格中的索引
    """
    index = 0
    r = r % 4
    if r == 0:   # 0 度
        index = py * 4 + px
    elif r == 1: # 90 度
        index = 12 + py - (px * 4)
    elif r == 2: # 180 度
        index = 15 - (py * 4) - px
    elif r == 3: # 270 度
        index = 3 - py + (px * 4)
    return index

def does_piece_fit(field, n_tetromino, n_rotation, n_pos_x, n_pos_y):
    """
    檢查目前方塊在指定位置是否會碰撞
    """
    for px in range(4):
        for py in range(4):
            pi = rotate(px, py, n_rotation)
            if tetromino[n_tetromino][pi] == 'X':
                fi_x = n_pos_x + px
                fi_y = n_pos_y + py
                
                if fi_x < 0 or fi_x >= FIELD_WIDTH or \
                   fi_y < 0 or fi_y >= FIELD_HEIGHT:
                    return False # 碰撞 (邊界外)
                
                if field[fi_y][fi_x] != 0:
                    return False # 碰撞
    return True # 沒有碰撞

# --- 遊戲狀態管理 (使用 st.session_state) ---

def initialize_game():
    """初始化或重置遊戲狀態"""
    if 'field' not in st.session_state:
        # 0 = 空白, 1-7 = 方塊, 9 = 邊界
        st.session_state.field = [[0] * FIELD_WIDTH for _ in range(FIELD_HEIGHT)]
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if x == 0 or x == FIELD_WIDTH - 1 or y == FIELD_HEIGHT - 1:
                    st.session_state.field[y][x] = 9 # 設置邊界
        
        st.session_state.score = 0
        st.session_state.game_over = False
        st.session_state.speed = 20 # 20 ticks (20 * 50ms = 1秒)
        st.session_state.speed_counter = 0
        st.session_state.piece_count = 0
        
        new_piece()

def new_piece():
    """產生一個新的方塊"""
    st.session_state.current_piece = random.randint(0, 6)
    st.session_state.current_rotation = 0
    st.session_state.current_x = FIELD_WIDTH // 2 - 2
    st.session_state.current_y = 0
    
    # 檢查是否遊戲結束
    if not does_piece_fit(st.session_state.field, 
                          st.session_state.current_piece, 
                          st.session_state.current_rotation, 
                          st.session_state.current_x, 
                          st.session_state.current_y):
        st.session_state.game_over = True

def lock_piece():
    """將目前方塊鎖定到遊戲區域 (field) 上"""
    field = st.session_state.field
    piece = st.session_state.current_piece
    rot = st.session_state.current_rotation
    x_pos = st.session_state.current_x
    y_pos = st.session_state.current_y

    for px in range(4):
        for py in range(4):
            pi = rotate(px, py, rot)
            if tetromino[piece][pi] == 'X':
                field[y_pos + py][x_pos + px] = piece + 1
    st.session_state.field = field

def check_lines():
    """檢查並消除已滿的行"""
    field = st.session_state.field
    lines_to_clear = []
    
    for y in range(FIELD_HEIGHT - 2, -1, -1): # 從下往上檢查 (跳過底邊)
        is_line = True
        for x in range(1, FIELD_WIDTH - 1): # 只檢查非邊界
            if field[y][x] == 0:
                is_line = False
                break
        if is_line:
            lines_to_clear.append(y)

    if lines_to_clear:
        lines_cleared = len(lines_to_clear)
        # 增加分數
        st.session_state.score += (1 << lines_cleared) * 100
        
        # 移除行
        for y_line in lines_to_clear:
            field.pop(y_line)
        
        # 在頂部插入新行
        for _ in range(lines_cleared):
            new_row = [0] * FIELD_WIDTH
            new_row[0] = 9
            new_row[FIELD_WIDTH - 1] = 9
            field.insert(0, new_row)
        
        st.session_state.field = field

# --- 按鈕處理函式 ---

def handle_left():
    if does_piece_fit(st.session_state.field, st.session_state.current_piece, st.session_state.current_rotation, st.session_state.current_x - 1, st.session_state.current_y):
        st.session_state.current_x -= 1

def handle_right():
    if does_piece_fit(st.session_state.field, st.session_state.current_piece, st.session_state.current_rotation, st.session_state.current_x + 1, st.session_state.current_y):
        st.session_state.current_x += 1

def handle_down():
    if does_piece_fit(st.session_state.field, st.session_state.current_piece, st.session_state.current_rotation, st.session_state.current_x, st.session_state.current_y + 1):
        st.session_state.current_y += 1
        st.session_state.speed_counter = 0 # 重置自動下降計時器

def handle_rotate():
    if does_piece_fit(st.session_state.field, st.session_state.current_piece, st.session_state.current_rotation + 1, st.session_state.current_x, st.session_state.current_y):
        st.session_state.current_rotation += 1

# --- 繪圖函式 ---

def draw_board_svg():
    """使用 SVG 繪製遊戲板"""
    svg_parts = []
    width = FIELD_WIDTH * BLOCK_SIZE
    height = FIELD_HEIGHT * BLOCK_SIZE
    
    # 繪製背景和已固定的方塊
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            color_index = st.session_state.field[y][x]
            color = COLORS[color_index]
            svg_parts.append(
                f'<rect x="{x * BLOCK_SIZE}" y="{y * BLOCK_SIZE}" '
                f'width="{BLOCK_SIZE}" height="{BLOCK_SIZE}" '
                f'fill="{color}" stroke="black" stroke-width="1" />'
            )
            
    # 繪製目前方塊
    piece = st.session_state.current_piece
    rot = st.session_state.current_rotation
    x_pos = st.session_state.current_x
    y_pos = st.session_state.current_y
    color = COLORS[piece + 1]
    
    for px in range(4):
        for py in range(4):
            if tetromino[piece][rotate(px, py, rot)] == 'X':
                x = x_pos + px
                y = y_pos + py
                svg_parts.append(
                    f'<rect x="{x * BLOCK_SIZE}" y="{y * BLOCK_SIZE}" '
                    f'width="{BLOCK_SIZE}" height="{BLOCK_SIZE}" '
                    f'fill="{color}" stroke="black" stroke-width="1" />'
                )

    # 組裝 SVG
    return (
        f'<svg width="{width}" height="{height}" style="background-color:{COLORS[0]};border: 2px solid grey;">'
        + "".join(svg_parts)
        + "</svg>"
    )

# --- Streamlit 應用程式主體 ---

st.set_page_config(page_title="Streamlit 俄羅斯方塊", layout="centered")
st.title("Streamlit 俄羅斯方塊")

# 初始化遊戲狀態
initialize_game()

# 遊戲結束畫面
if st.session_state.game_over:
    st.error("遊戲結束!")
    st.metric("最終分數", st.session_state.score)
    if st.button("重新開始"):
        st.session_state.clear() # 清空所有狀態
        st.rerun()
    st.stop() # 停止執行

# --- 側邊欄 (操控介面) ---
st.sidebar.metric("分數", st.session_state.score)
st.sidebar.markdown("---")
st.sidebar.header("操控")

col1, col2, col3 = st.sidebar.columns([1,1,1])
with col1:
    st.button("← 左", on_click=handle_left, use_container_width=True)
with col2:
    st.button("↓ 下", on_click=handle_down, use_container_width=True)
with col3:
    st.button("→ 右", on_click=handle_right, use_container_width=True)

st.sidebar.button("↻ 旋轉", on_click=handle_rotate, use_container_width=True)

# --- 遊戲主畫布 (使用 SVG) ---
board_placeholder = st.empty()
board_placeholder.markdown(draw_board_svg(), unsafe_allow_html=True)

# --- 遊戲循環邏輯 ---
st.session_state.speed_counter += 1
force_down = (st.session_state.speed_counter >= st.session_state.speed)

if force_down:
    st.session_state.speed_counter = 0
    if does_piece_fit(st.session_state.field, st.session_state.current_piece, st.session_state.current_rotation, st.session_state.current_x, st.session_state.current_y + 1):
        st.session_state.current_y += 1
    else:
        # 鎖定方塊
        lock_piece()
        # 檢查消除行
        check_lines()
        # 產生新方塊
        new_piece()
        
        # 遊戲加速
        st.session_state.piece_count += 1
        if st.session_state.piece_count % 10 == 0 and st.session_state.speed > 10:
            st.session_state.speed -= 1

# --- 自動重新整理 ---
# 這是 Streamlit 遊戲循環的關鍵
# 每次腳本執行到這裡，它會暫停 50ms，然後觸發一次完整的重新執行
time.sleep(0.05) # 50ms
st.rerun()

