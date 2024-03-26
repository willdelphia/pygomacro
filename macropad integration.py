import time
from adafruit_macropad import MacroPad

macropad = MacroPad()
previous_position = macropad.encoder


red = (20,0,0)
blue = (0,0,20)

cols = 3
rows = 4

review_offset = 0
menu_mode = False
review_mode = False

def create_board(X, Y):
    return [[0] * X for _ in range(Y)]

board_history = [create_board(cols, rows)]
capture_history = [(0,0)]


def reset_game():
    global board_history
    global capture_history
    board_history = [create_board(cols, rows)]
    capture_history = [(0,0)]
    update_display('New Game')
    paint_stones()

def update_display(line2):
    text_lines = macropad.display_text(title="GO!")

    i = len(board_history)
    if i % 2:
        text_lines[1].text = "Red's Turn" 
    else:
        text_lines[1].text = "Blue's Turn" 
    
    text_lines[2].text = line2
    capture1, capture2 = capture_history[-1]
    text_lines[3].text = "Red: " + str(capture1) + " | Blue: " + str(capture2)
    text_lines.show()

def update_display_review():
    text_lines = macropad.display_text(title="Review Mode")
    text_lines[1].text = "Move " + str(len(board_history) + review_offset)
    text_lines[2].text = "Click to continue"
    text_lines[3].text = "from this position"
    text_lines.show()



def deep_copy_array(original):
    if not isinstance(original, list):
        return original  # Return the original element if it's not a list

    # Create a new list to hold the deep copy
    copied_array = []
    for sublist in original:
        # Recursively deep copy each sublist
        copied_sublist = deep_copy_array(sublist)
        copied_array.append(copied_sublist)

    return copied_array

def are_boards_the_same(board1, board2):
    # Check if boards have the same dimensions
    if len(board1) != len(board2) or any(len(row1) != len(row2) for row1, row2 in zip(board1, board2)):
        return False
    
    # Compare corresponding elements
    for row1, row2 in zip(board1, board2):
        for elem1, elem2 in zip(row1, row2):
            if elem1 != elem2:
                return False
    
    return True


def keyToIntersction(number):
    x = number % cols
    y = number // cols
    
    return x, y

def coordinates_to_number(x, y):
    return y * cols + x


def update_board(x, y, color ,board):
  board[y][x] = color

def is_color(x,y,color, board):
    if board[y][x] == color:
        return True
    else:
      return False
    

def get_neighbors(x, y, color, board):
    neighbors = []
    # Above
    if y > 0:
        if is_color(x, y - 1, color, board):
            neighbors.append((x, y - 1))
    # Below
    if y < rows - 1:
        if is_color(x, y + 1, color, board):
            neighbors.append((x, y + 1))
    # Left
    if x > 0:
        if is_color(x - 1, y, color, board):
            neighbors.append((x - 1, y))
    # Right
    if x < cols - 1:
        if is_color(x + 1, y, color, board):
            neighbors.append((x + 1, y))
    return neighbors


def get_chain_and_liberites(x, y, color, board):
    chain = set()  # Set to store the coordinates of stones in the chain
    visited = set()  # Set to keep track of visited intersections

    def dfs_chain(xx, yy):
        # Check if the current intersection is of the given color and not visited yet
        if (xx, yy) not in visited and is_color(xx, yy, color, board) or (xx == x and yy == y):
            visited.add((xx, yy))
            chain.add((xx, yy))
            neighbors = get_neighbors(xx, yy, color, board)
            # Recursively call dfs_chain for neighboring intersections
            for nx, ny in neighbors:
                dfs_chain(nx, ny)

    dfs_chain(x, y)

    liberties = set()  # Set to store the liberties of the chain

    # For each stone in the chain, find its neighboring intersections

    for cx, cy in chain:
        neighbors = get_neighbors(cx, cy, 0, board)  # Find liberties (color = 0) around the stone
        liberties.update(neighbors)

    return {"liberties": list(liberties), "chain": list(chain)}


def does_move_capture(x, y, color, board):
    captures = False

    #only accept 1 or 2 as color for this function
    if color == 0:
        return False

    #find neighbors of opposite color
    opposite_color = 2 if color == 1 else 1
    oppositeNeighbors = get_neighbors(x,y,opposite_color, board)

    for neighbor in oppositeNeighbors:
        if len(get_chain_and_liberites(neighbor[0], neighbor[1], opposite_color, board)['liberties']) == 1:
            captures = True
    return captures

def get_captured_stones(x, y, color, board):
    captured_stones = []
    opposite_color = 2 if color == 1 else 1
    oppositeNeighbors = get_neighbors(x,y,opposite_color, board)

    for neighbor in oppositeNeighbors:
        report = get_chain_and_liberites(neighbor[0], neighbor[1], opposite_color, board)
        liberties, chain = report.values()
        if len(liberties) == 1:
            captured_stones.extend(chain)
    return captured_stones

def is_valid_move(x,y,color, board):
    #if it is already filled with stone, return False
    if board[y][x] != 0:
        update_display('Filled Already')
        return False

    #if is a location with liberties
    liberties = get_neighbors(x,y,0, board)
    if len(liberties) > 0:
        # print('Valid because it has a at least 1 liberty')
        return True
    
    #if is joining chain that has some liberties
    the_chain_liberties = get_chain_and_liberites(x,y,color, board)['liberties']
    # print('Chain Liberties Checker')
    # print(the_chain_liberties)


    if len(the_chain_liberties) > 1:
        return True
    else:
      update_display('No Liberties')

      
    #if is capturing
    it_does_capture = does_move_capture(x,y,color, board)
    if(it_does_capture):
        # print('Valid because though it has no liberties, it is capturing enemy stones')
        return True

    return False


    
def paint_stones(board=None):
    if board == None:
        board = board_history[-1]
    for row_index, row in enumerate(board):
        for col_index, col in enumerate(row):
            number = coordinates_to_number(col_index, row_index)
            value = (0,0,0)
            if col == 1:
                value = red
            elif col == 2:
                value = blue
            macropad.pixels[number] = value



def attempt_move(x, y, color):
    global capture_history
    board = board_history[-1]
    if is_valid_move(x, y, color, board):
        newBoard =  deep_copy_array(board_history[-1])
        update_board(x, y, color, newBoard)  # Place the new stone on the board
        captured_stones = get_captured_stones(x,y,color,board)
        if len(captured_stones) > 0:
            update_display('Capturing...')
        for stone in captured_stones:
            update_board(stone[0], stone[1], 0, newBoard)
        newCapture1 = capture_history[-1][0]
        newCapture2 = capture_history[-1][1]
        if color == 1:
            newCapture1 = newCapture1 + len(captured_stones)
        elif color == 2:
            newCapture2 = newCapture2 + len(captured_stones)


        #check for Ko move 
        if len(board_history) > 2:
            same = are_boards_the_same(board_history[-2], newBoard)
            if(same == False):
                #new turn
                board_history.append(newBoard) 
                capture_history.append((newCapture1, newCapture2))
                update_display('...') 
                #change turn
            else:
                update_display('Invalid Move: Ko')
        else:
            #new turn
            board_history.append(newBoard)
            capture_history.append((newCapture1, newCapture2))
            update_display('...')



        # print("new board")
        paint_stones()
        # print(ascii_go_board(board_history[-1]))



def resume_game_from_review():
    global review_offset
    # update_display(str(review_offset))
    global review_mode
    global board_history
    global capture_history
    del board_history[review_offset:]
    del capture_history[review_offset:]
    review_offset = 0
    paint_stones()
    update_display("Resume Game")
    review_mode = False


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def enter_menu():
    global menu_mode
    menu_mode = True
    render_menu()

def pass_turn():
     newCapture1 = capture_history[-1][0]
     newCapture2 = capture_history[-1][1]
     newBoard =  deep_copy_array(board_history[-1])
     board_history.append(newBoard)
     capture_history.append((newCapture1, newCapture2))
     update_display('Player passed...')
     paint_stones()

def enter_review_mode():
    global review_offset
    global review_mode
    review_offset = 0
    review_mode = True
    update_display_review()


menu_options = [
    ('PASS', 'Pass'),
    ('RESUME', 'Resume Game'),
    ('REVIEW', 'Review Mode'),
    ('NEW', 'New Game'),
]

def render_menu():
    option_len = len(menu_options)
    text_lines = macropad.display_text(title="Menu")


    text_lines[1].text = "-> " + str(menu_options[current_position % option_len][1])
    text_lines[2].text = "   " + str(menu_options[(current_position + 1) % option_len][1])
    text_lines[3].text = "   " + str(menu_options[(current_position + 2) % option_len ][1])
    text_lines.show()

def execute_menu_action():
    global menu_mode
    global review_mode
    global review_offset
    global board_history
    menu_mode = False
    option_len = len(menu_options)
    action = menu_options[current_position % option_len][0]
    if action == 'PASS':
        pass_turn()
    elif action == 'RESUME':
        update_display("...")
    elif action == 'REVIEW':
        if len(board_history) > 1:
            enter_review_mode()
        else:
            update_display("Play some moves first")
    elif action == 'NEW':
        reset_game()

# Main loop
        
update_display('New Game')

while True:
    current_position = macropad.encoder
    if current_position != previous_position:
        if menu_mode:
            render_menu()
        elif review_mode:
            diff = current_position - previous_position
            new_review_offset_value = review_offset + diff
            review_offset = clamp(new_review_offset_value, -1 * (len(board_history) - 1), 0)

            paint_stones(board_history[len(board_history) - 1 + review_offset])
            update_display_review()

        previous_position = current_position

    if macropad.encoder_switch:
        if review_mode == True:
            resume_game_from_review()
        else:
            if menu_mode == False:
                enter_menu()
            else: 
                execute_menu_action()

            
        

    key_event = macropad.keys.events.get()
    if key_event:
        key_number = key_event.key_number
        pressed = key_event.pressed
        if pressed:  
            if review_mode == False and menu_mode == False:
                i = len(board_history)
                if i % 2:
                    #"Red's Turn"
                    color = 1
                else:
                    #"Blue's Turn"
                    color = 2
                intersection = keyToIntersction(key_number)
                attempt_move(intersection[0], intersection[1], color)

        
    time.sleep(0.1)