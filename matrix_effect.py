import curses
import random
import signal
import time
import sys

# Init allowed characters
ALNUMS = [code for code in range(0x30, 0x5E)]
JIS_X0201_KATAKANA = [code for code in range(0xFF61, 0xFF9F + 1)]
CHARACTERS = ALNUMS + JIS_X0201_KATAKANA
CURRENT_STREAM_LENGTH = []

# Generate a new row of characters with a random chance a character is visible or 'blank'
def generate_row(max_x):
    global CURRENT_STREAM_LENGTH
    
    p_visible = 60
    row = []
    for i in range(max_x):
        if i % 2 == 0:
            p_mod = CURRENT_STREAM_LENGTH[i] * 3
            character = chr(random.choice(CHARACTERS)) if random.random()*100 + p_mod < p_visible else ' '
            row.insert(i, character)
            if character == ' ':
                CURRENT_STREAM_LENGTH[i] -= 1
            else: 
                CURRENT_STREAM_LENGTH[i] += 1
        else:
           row.insert(i, ' ')
    return row


def matrix_effect(stdscr):
    # Hide cursor
    curses.curs_set(0)

    # Init colours
    L_GREEN = 1
    D_GREEN = 2

    curses.start_color()
    curses.init_color(L_GREEN, 0, 1000, 0)
    curses.init_color(D_GREEN, 0, 500, 0)
    curses.init_pair(L_GREEN, L_GREEN, curses.COLOR_BLACK)
    curses.init_pair(D_GREEN, D_GREEN, curses.COLOR_BLACK)

    # Get max screen coords
    max_y, max_x = stdscr.getmaxyx()
    max_x -= 1
    max_y -= 1

    # Init lists to keep track of current pos of chars in each col & length of each stream
    SCREEN_MATRIX = [['' for _ in range(max_x)] for _ in range(max_y)]
    global CURRENT_STREAM_LENGTH
    CURRENT_STREAM_LENGTH = [0] * max_x
    
    start_time = time.time()
    while True:
      current_time = time.time()
      
      SCREEN_MATRIX.insert(0, generate_row(max_x))
      SCREEN_MATRIX.pop()
      
      screen_str = ''
      for row in SCREEN_MATRIX:
          screen_str += ''.join(str(item) for item in row)
          screen_str += '\n'
    
      stdscr.addstr(0,0,screen_str,curses.color_pair(D_GREEN))

      stdscr.refresh()
      time.sleep(0.05)

      if current_time - start_time > 10:
        break
      
    stdscr.clear()
    curses.endwin()


def signal_handler(sig, frame):
    curses.endwin()
    sys.exit(0)

if __name__ == "__main__":
  # Set up a signal handler to handle interrupts
  signal.signal(signal.SIGINT, signal_handler)
  curses.wrapper(matrix_effect)