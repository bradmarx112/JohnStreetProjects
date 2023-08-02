from utils import Point, BLOCK_SIZE

def spiral(w, h) -> list:
    hor_blocks = w // BLOCK_SIZE
    vert_blocks = h // BLOCK_SIZE
    
    x = w - (BLOCK_SIZE*2)
    y = h - BLOCK_SIZE
    path_pts = [Point(x, y)]
    y_mv = vert_blocks - 2
    x_mv = hor_blocks - 3
    finished = False
    dir_idx = -1
    while not finished:
        if x_mv <= 1:
            finished = True
        else:
            for y_pos in range(y_mv):
                y += dir_idx*BLOCK_SIZE
                path_pts.append(Point(x=x, y=y))
            y_mv -= 2
        
        if x_mv <= 1:
            finished = True
        else:
            for x_pos in range(x_mv):
                x += dir_idx*BLOCK_SIZE
                path_pts.append(Point(x=x, y=y))
            x_mv -= 2
        
        dir_idx *= -1

    brick_grid = [Point(x*BLOCK_SIZE, y*BLOCK_SIZE) for x in range(hor_blocks) for y in range(vert_blocks) \
                    if Point(x*BLOCK_SIZE, y*BLOCK_SIZE) not in path_pts]

    return brick_grid

    
if __name__ == '__main__':
    spiral(w=640, h=480)
    print('bp')

