import streamlit as st
import random
import time


def make_puzzle():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    blanks = [(i, j) for i in range(9) for j in range(9) if puzzle[i][j] == 0]
    for i, j in random.sample(blanks, 10):
        puzzle[i][j] = solution[i][j]
    rows = [3 * band + r for band in random.sample(range(3), 3)
            for r in random.sample(range(3), 3)]
    cols = [3 * stack + c for stack in random.sample(range(3), 3)
            for c in random.sample(range(3), 3)]
    digits = [0] + random.sample(range(1, 10), 9)
    puzzle = [[digits[puzzle[i][j]] for j in cols] for i in rows]
    solution = [[digits[solution[i][j]] for j in cols] for i in rows]
    if random.choice([True, False]):
        puzzle = [list(row) for row in zip(*puzzle)]
        solution = [list(row) for row in zip(*solution)]
    return puzzle, solution


def new_game():
    puzzle, solution = make_puzzle()
    st.session_state.puzzle = puzzle
    st.session_state.solution = solution
    st.session_state.started = time.time()
    st.session_state.finished = False
    st.session_state.elapsed = 0
    st.session_state.message = ''
    for i in range(9):
        for j in range(9):
            st.session_state[f'sudoku_{i}_{j}'] = str(puzzle[i][j]) if puzzle[i][j] else ''


def check_solution():
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            value = st.session_state[f'sudoku_{i}_{j}'].strip()
            if value not in '123456789' or len(value) != 1:
                st.session_state.message = '빈칸을 모두 1~9의 숫자로 채워 주세요.'
                return
            row.append(int(value))
        board.append(row)
    valid = set(range(1, 10))
    groups = board + [[board[i][j] for i in range(9)] for j in range(9)]
    groups += [[board[r+i][c+j] for i in range(3) for j in range(3)]
               for r in (0, 3, 6) for c in (0, 3, 6)]
    if any(set(group) != valid for group in groups):
        st.session_state.message = '틀린 숫자가 있어요. 행, 열, 3×3 구역을 다시 확인해 주세요.'
        return
    if not st.session_state.finished:
        st.session_state.elapsed = time.time() - st.session_state.started
        st.session_state.finished = True
    st.session_state.message = ''


st.set_page_config(page_title='스도쿠', layout='centered')
if 'sudoku_version' not in st.session_state or st.session_state.sudoku_version != 2:
    st.session_state.sudoku_version = 2
    new_game()

st.title('스도쿠')
st.caption('주어진 숫자는 고정되어 있어요. 빈칸을 채워 각 행·열·3×3 구역에 1~9가 한 번씩 나오게 하세요.')
left, right = st.columns(2)
left.button('새 게임 (Shuffle)', on_click=new_game, use_container_width=True)
right.button('정답 확인 (Finish)', on_click=check_solution, use_container_width=True,
             disabled=st.session_state.finished)

st.markdown('''
<style>
.block-container {max-width: 650px; padding-top: 2rem;}
div[data-testid="stTextInput"] input {
    text-align: center; font-size: 20px; padding: 0; min-height: 38px;
}
div[data-testid="stTextInput"] input:disabled {
    -webkit-text-fill-color: #172554; color: #172554;
    background-color: #e2e8f0; opacity: 1; font-weight: bold;
}
div[data-testid="stTextInput"] {margin-bottom: -12px;}
hr {margin: 10px 0 !important; border-top: 2px solid #64748b !important;}
</style>
''', unsafe_allow_html=True)

for i in range(9):
    if i in (3, 6):
        st.markdown('---')
    boxes = st.columns(3, gap='small')
    for box in range(3):
        with boxes[box]:
            cells = st.columns(3, gap='small')
            for offset in range(3):
                j = box * 3 + offset
                with cells[offset]:
                    st.text_input(f'{i+1}행 {j+1}열', key=f'sudoku_{i}_{j}',
                                  max_chars=1, label_visibility='collapsed',
                                  disabled=bool(st.session_state.puzzle[i][j]) or st.session_state.finished)

if st.session_state.finished:
    minutes, seconds = divmod(int(st.session_state.elapsed), 60)
    st.success(f'정답입니다! 완료 시간: {minutes}분 {seconds}초')
elif st.session_state.message:
    st.warning(st.session_state.message)
