from graphics import Canvas
import random
    
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

GRID_SIZE = 50
COLUMNS = 6
ROWS = 12
COLORS = ('red', 'orange', 'yellow', 'green', 'blue', 'purple')
MOVE_KEYS = ('ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'w', 'a', 's', 'd')
START_TIME = 300
EMPTY_SQUARE = {'id' : '', 'color' : '',  'state' : 'empty'}
START_FILL = 4
MULT = (0, 0, 0, 30, 50, 60, 100, 120, 150, 300, 500, 600, 700, 800, 1000)
SPEED = (500, 500, 450, 405, 365, 328, 295, 265, 240, 215, 194, 174, 156, 141, 127, 114, 100)

def main():

    ## SETUP
    canvas.set_canvas_background_color('black')

    start_screen() ## Waits for player to press Enter

    grid = []
    for i in range(COLUMNS):
        grid.append([])
        for j in range(ROWS):
            grid[i].append(EMPTY_SQUARE)

    initial_fill(grid)

    player = {'select' : player_create(0, 0), 'xy' : [0,0]}

    timer = {
        'timeleft' : START_TIME,
        'tick' : 0,
        'combo' : 0,
        'drop' : 20,
        'newline' : 500}
    
    level = 0
    score = 0

    white_list = set()
    death_list = []
    land_list = []
    drop_list = []

    title, clock, scoreboard, speedometer, plus_points = game_setup()


    ## MAIN GAME LOOP
    while True:
        time.sleep(.01) #100 frames per second ?
        update_time(timer, clock, drop_list)

        if timer['timeleft'] <= 0:
            end_game(title, 'TIMES UP')
            break
        elif timer['combo'] == 0 and timer['newline'] == 0:
            if grid_full(grid):
                end_game(title, 'GAME OVER')
                break
            else:
                newline(grid)
                player_move(player, 'w')
                timer['newline'] = SPEED[level]

    # PLAYER ACTIONS
        key = canvas.get_last_key_press()
        if key != None:
    # EXIT GAME
            if key == 'Escape':
                end_game(title, 'ESCAPE')
                break
    # MOVE CURSOR
            if key in MOVE_KEYS:
                player_move(player, key)
    # SWAP SQUARES
            elif key in ('Enter', 'j'):
                swaps = swap(player['xy'],grid, drop_list)
                if swaps != False:
                    match_check(grid,swaps,white_list)
                    if white_list != set():
                        update_whitelist(grid, white_list, death_list)
                        timer['combo'] += 50
                        white_list = set()
    # ERROR CHECK
            # elif key == 'f':
            #     error_check(grid,player)
            # elif key == 'g':
            #     print(drop_list)
            #     print(EMPTY_SQUARE)
    # ADD NEW LINE
            elif key in ('k', 'p'):
                if grid_full(grid):
                    end_game(title, 'TOO MUCH!')
                    break
                else:
                    newline(grid)
                    player_move(player, 'w')
    # SPEED UP
            elif key == 'l':
                timer['drop'] -= 5
            
            key = None

    # DROP FALLING SQUARES 5X PER SECOND
        if timer['drop'] < 1:
            drop(grid, drop_list, land_list)
            if land_list != []:
                match_check(grid, land_list, white_list)
                land_list = []
                if white_list != set():
                    update_whitelist(grid, white_list, death_list)
                    timer['combo'] += 50
                    white_list = set()
                
            timer['drop'] = 20

    # DELETE WHITE SQUARES, SCORE POINTS WHEN COMBO TIMER ENDS
        if timer['combo'] == 0 and death_list != []:
            points = delete_update(grid,death_list,drop_list)
            score += points
            canvas.change_text(plus_points, '+' + str(points))
            #canvas.set_hidden(plus_points, False)
            canvas.change_text(scoreboard, str(score))
            if level < 15:
                if score > level*level*50:
                    level += 1
                    canvas.change_text(speedometer, str(level))
            death_list = []
            


def drop(grid, drop_list, land_list):

    drop_sorted = []
    for square in drop_list:
        x,y = find_xy(square)
        drop_sorted.append((y,x))
    
    drop_sorted = sorted(drop_sorted)

    for yx in drop_sorted:
        x = yx[1]
        y = yx[0]
        square = grid[x][y]
        state = grid[x][y]['state']
        if state != 'dropping':
            print('SOMETHING ODD IN DROPLIST')
            continue
        #checkbelow
        if y == 0:
            grid[x][y]['state'] = 'alive'
            land_list.append(square['id'])
            drop_list.remove(square['id'])
            continue
        else:
            below = grid[x][y-1]['state']

        if below == 'alive' or below == 'dead':
            grid[x][y]['state'] = 'alive'
            land_list.append(square['id'])
            drop_list.remove(square['id'])
            continue

        elif below == 'dropping':
            print(f'DROP ERROR at {x},{y}')
            continue

        elif below == 'empty':
            canvas.move(square['id'], 0, GRID_SIZE)
            grid[x][y-1] = grid[x][y]
            grid[x][y] = EMPTY_SQUARE

def update_whitelist(grid, white_list, death_list):
    for square in white_list:
        x,y = find_xy(square)
        grid[x][y]['color'] = 'white'
        grid[x][y]['state'] = 'dead'
        canvas.set_color(square, 'white')
        death_list.append(square)

def delete_update(grid,death_list,drop_list):
    combo = len(death_list)
    for square in range(combo):
        square = death_list.pop()
        x,y = find_xy(square)
        grid[x][y] = EMPTY_SQUARE
        cavein_check(grid,drop_list,x,y)
        canvas.delete(square)
    if combo < 15:
        return MULT[combo]
    else:
        return 1000

def find_xy(square):
    x = canvas.get_left_x(square)
    y = canvas.get_top_y(square)
    x = int(x / GRID_SIZE)
    y = int(ROWS - (y / GRID_SIZE)) - 1
    return x,y

def cavein_check(grid, drop_list, x, y):
    if y > 10:
        return
    # if grid[x][y]['state'] != 'empty':
    #     return
    #print(f'CAVEIN CHECK AT {x},{y}')
    for i in range(11-y):
        if grid[x][y+i+1]['state'] == 'alive':
            grid[x][y+i+1]['state'] = 'dropping'
            # if EMPTY_SQUARE['state'] != 'empty':
            #     raise ValueError('CAVEIN ERROR')
            drop_list.append(grid[x][y+i+1]['id'])

        else:
            break

def drop_check(grid, square, drop_list):

    x,y = find_xy(square)
    
    if y < 1:
        return

    #print(f'DROP CHECK at {x}, {y}')
    if grid[x][y]['state'] == 'alive' and grid[x][y-1]['state'] == 'empty':
        grid[x][y]['state'] = 'dropping'
        # if EMPTY_SQUARE['state'] != 'empty':
        #     raise ValueError('DROPCHECK ERROR')
        drop_list.append(square)

def match_check(grid, squares, white_list):
    for square in squares:
        x,y = find_xy(square)

    # ONLY CHECK LIVE SQUARES (Not Dead, Dropping, or Empty)
        state = grid[x][y]['state']
        if state != 'alive':
            continue

        #print(f'DELETE CHECK at {x},{y}')
        color = grid[x][y]['color']

    # CHECK LEFT
        if x > 1: 
            square2 = grid[x-1][y]
            square3 = grid[x-2][y]
            if color == square2['color'] == square3['color']:
                if state == square2['state'] == square3['state']:
                    white_list |= {square, square2['id'], square3['id']}

    # CHECK RIGHT
        if x < 4: 
            square2 = grid[x+1][y]
            square3 = grid[x+2][y]
            if color == square2['color'] == square3['color']:
                if state == square2['state'] == square3['state']:
                    white_list |= {square, square2['id'], square3['id']}
    # CHECK HORIZONTAL
        if x > 0 and x < 5: 
            square2 = grid[x-1][y]
            square3 = grid[x+1][y]
            if color == square2['color'] == square3['color']:
                if state == square2['state'] == square3['state']:
                    white_list |= {square, square2['id'], square3['id']}
    # CHECK DOWN
        if y > 1:
            square2 = grid[x][y-1]
            square3 = grid[x][y-2]
            if color == square2['color'] == square3['color']:
                if state == square2['state'] == square3['state']:
                    white_list |= {square, square2['id'], square3['id']}
    # CHECK UP
        if y < 10:
            square2 = grid[x][y+1]
            square3 = grid[x][y+2]
            if color == square2['color'] == square3['color']:
                if state == square2['state'] == square3['state']:
                    white_list |= {square, square2['id'], square3['id']}
    # CHECK VERTICAL
        if y < 11 and y > 0:
            square2 = grid[x][y-1]
            square3 = grid[x][y+1]
            if color == square2['color'] == square3['color']:
                if state == square2['state'] == square3['state']:
                    white_list |= {square, square2['id'], square3['id']}

def swap(xy,grid,drop_list):
    #print(f'SWAP at {xy}')
    left = xy[0]
    right = xy[0]+1
    y = xy[1]

    square1 = grid[left][y]
    square2 = grid[right][y]

    if square1['state'] == 'dead' or square2['state'] == 'dead':
        return False
    if square1['state'] == square2['state'] == 'empty':
        return False

    if square1['id'] != '':
        canvas.move(square1['id'], GRID_SIZE, 0)
    if square2['id'] != '':
        canvas.move(square2['id'], -GRID_SIZE, 0)


    grid[left][y] = square2
    grid[right][y] = square1

    if square2['state'] == 'empty':
        cavein_check(grid,drop_list, left, y)
    elif square1['state'] == 'empty':
        cavein_check(grid,drop_list, right, y)

    if square2['state'] == 'alive':
        drop_check(grid,square2['id'],drop_list)
    if square1['state'] == 'alive':
        drop_check(grid,square1['id'],drop_list)

    templist = []

    if grid[left][y]['state'] == 'alive':
        templist.append(square2['id'])
    if grid[right][y]['state'] == 'alive':
        templist.append(square1['id'])

    if len(templist) > 0:
        return templist
    else:
        return False

def player_create(x ,y):
    return canvas.create_image(
        x * GRID_SIZE,
        CANVAS_HEIGHT-GRID_SIZE-(y*GRID_SIZE),
        'swaparrow.png'
    )
    # return canvas.create_rectangle(
    #     x * GRID_SIZE,
    #     CANVAS_HEIGHT-GRID_SIZE-(y*GRID_SIZE),
    #     (x*GRID_SIZE) + GRID_SIZE*2,
    #     CANVAS_HEIGHT-(y*GRID_SIZE),
    #     'transparent',
    #     'white'
    # )

def player_move(player, key):
    x = player['xy'][0]
    y = player['xy'][1]
    
    if key in ('ArrowLeft', 'a'):
        if x > 0:
            player['xy'][0] -= 1
            x -= 1    
    elif key in ('ArrowRight', 'd'):
        if x < 4:
            player['xy'][0] += 1
            x += 1
    elif key in ('ArrowUp', 'w'):
        if y < 11:
            player['xy'][1] += 1
            y += 1    
    elif key in ('ArrowDown','s'):
        if y > 0:
            player['xy'][1] -= 1
            y -= 1
    canvas.delete(player['select'])
    player['select'] = player_create(x, y)

    #print(player['xy'])

def initial_fill(grid):
    color = ''
    below = ''
    for row in range(START_FILL):
        left = ''
        for column in range(COLUMNS):
            left = color
            if row >= 1:
                below = grid[column][row-1]['color']
            while color == below or color == left:
                color = random.choice(COLORS)
            temp = create_square(column, row, color)
            grid[column][row] = {'id' : temp, 'color' : color, 'state' : 'alive'}

            time.sleep(.01)

def create_square(column, row, color):
    return canvas.create_rectangle(
        (column)*GRID_SIZE,
        (11-row)*GRID_SIZE,
        (column+1)*GRID_SIZE,
        (12-row)*GRID_SIZE,
        color,
        'black'
    )

def update_time(timer,clock,drop_list):
    timer['tick'] += 1
    if timer['tick'] >= 100:
        timer['tick'] = 0
        timer['timeleft'] -= 1
        canvas.change_text(clock, str(timer['timeleft']))
    if timer['drop'] > 0:
        timer['drop'] -= 1
    if timer['combo'] == 0:
        #if drop_list == []:
        if timer['newline'] > 0:
            timer['newline'] -= 1
    elif timer['combo'] > 0:
        timer['combo'] -= 1

def start_screen():
    start_text = canvas.create_text(
        50,
        100,
        'TETRIS ATTACK',
        font_size = 25,
        color = 'white'
    )
    start_text2 = canvas.create_text(
        50,
        200,
        'Press J or Enter to SWAP',
        font_size = 25,
        color = 'white'
    )

    start_text3 = canvas.create_text(
        50,
        300,
        'Arrow Keys or WASD to move',
        font_size = 25,
        color = 'white'
    )

    start_text4 = canvas.create_text(
        50,
        400,
        'Match colors to score points',
        font_size = 25,
        color = 'white'
    )
    
    while not canvas.get_new_key_presses():
        pass

    canvas.clear()

def end_game(title, text):
    canvas.change_text(title, text)

def game_setup():
    title = canvas.create_text(
        350,
        100,
        'TETRIS ATTACK',
        font_size = 25,
        color = 'white'
    )

    canvas.create_text(
        350,
        150,
        str('TIME LEFT'),
        font_size = 20,
        color = 'white'
    )

    clock = canvas.create_text(
        400,
        200,
        str(START_TIME),
        font_size = 20,
        color = 'white'
    )

    canvas.create_text(
        350,
        250,
        'SCORE',
        font_size = 20,
        color = 'white'
    )

    plus_points = canvas.create_text(
        475,
        250,
        '-',
        font_size = 20,
        color = 'gold'        
    )

    #canvas.set_hidden(plus_points, True)
    
    scoreboard = canvas.create_text(
        400,
        300,
        '0',
        font_size = 20,
        color = 'white'
    )

    canvas.create_text(
        350,
        350,
        'SPEED',
        font_size = 20,
        color = 'white'
    )

    speedometer = canvas.create_text(
        400,
        400,
        '0',
        font_size = 20,
        color = 'white'
    )

    canvas.create_rectangle(
        300,
        0,
        310,
        CANVAS_HEIGHT,
        'white'
    )

    return title, clock, scoreboard, speedometer, plus_points

def grid_full(grid):
    for column in grid:
        if column[11]['id'] != '':
                return True
    return False

def newline(grid):
    x = 0
    y = 11
    for column in grid:
        for square in reversed(column):
            if square['id'] != '':
                canvas.move(square['id'], 0, -GRID_SIZE)
                grid[x][y+1] = grid[x][y]
                grid[x][y] = EMPTY_SQUARE
            y-=1
        x+=1
        y=11
    bottom_fill(grid)

def bottom_fill(grid):
    left = ''
    color = ''
    for i in range(COLUMNS):
        above = grid[i][1]['color']
        left = color
        while color == left or color == above:
            color = random.choice(COLORS)
        temp = create_square(i, 0, color)
        grid[i][0] = {'id' : temp, 'color' : color, 'state' : 'alive'}

def error_check(grid,player):
    x = player['xy'][0]
    y = player['xy'][1]
    print(grid[x][y])
    print(grid[x+1][y])        

if __name__ == '__main__':
    main()