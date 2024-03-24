
cols = 3
rows = 4

def create_board(X, Y):
    return [[0] * X for _ in range(Y)]

board_history = [create_board(cols, rows)]

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


def ascii_go_board(board):
    ascii_board = ''
    for row in board:
        for stone in row:
            if stone == 0:
                ascii_board += '[ ]'  # Empty box
            elif stone == 1:
                ascii_board += ' X '  # Black stone
            elif stone == 2:
                ascii_board += ' O '  # White stone
        ascii_board += '\n'
    return ascii_board


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
        print("Already Filled")
        return False

    #if is a location with liberties
    liberties = get_neighbors(x,y,0, board)
    if len(liberties) > 0:
        print('Valid because it has a at least 1 liberty')
        print(liberties)
        return True
    
    #if is joining chain that has some liberties
    the_chain_liberties = get_chain_and_liberites(x,y,color, board)['liberties']
    print('Chain Liberties Checker')
    print(the_chain_liberties)
    if len(the_chain_liberties) > 0:
          print('Valid because it is joining a chain that has a at least 1 liberty')
          return True
      
    #if is capturing
    it_does_capture = does_move_capture(x,y,color, board)
    if(it_does_capture):
        print('Valid because though it has no liberties, it is capturing enemy stones')
        return True

        
    
    


def attempt_move(x, y, color):
    board = board_history[-1]
    if is_valid_move(x, y, color, board):
        newBoard =  deep_copy_array(board_history[-1])
        update_board(x, y, color, newBoard)  # Place the new stone on the board
        captured_stones = get_captured_stones(x,y,color,board)
        if len(captured_stones) > 0:
            print("We're capturing stones")
            print(captured_stones)
        for stone in captured_stones:
            update_board(stone[0], stone[1], 0, newBoard)


        #check for Ko move 
        if len(board_history) > 2:
            same = are_boards_the_same(board_history[-2], newBoard)
            if(same == False):
                board_history.append(newBoard)  
                #change turn
            else:
                print("Can't play there, KO!")
        else:
            board_history.append(newBoard)  


        print("new board")
        print(ascii_go_board(board_history[-1]))
    else:
        print('illegal move attempted')

attempt_move(1,0,1) #move 1
attempt_move(0,1,1) 
attempt_move(2,1,1)
attempt_move(1,2,1)
attempt_move(0,2,2)
attempt_move(1,3,2)
attempt_move(2,2,2)
attempt_move(1,1,2)
attempt_move(1,2,1)

 




