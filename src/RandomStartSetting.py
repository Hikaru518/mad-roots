import random

def RandomStart(a, b, c):
    # 创建一个空的7x7网格，外层包裹一圈"o"
    grid = [['o' for i in range(7)] for j in range(7)]

    # 放置A类道具
    for i in range(a):
        x, y = random.randint(1, 5), random.randint(1, 5)
        while grid[x][y] != 'o':
            x, y = random.randint(1, 5), random.randint(1, 5)
        grid[x][y] = '+'

    # 放置B类道具
    for i in range(b):
        x, y = random.randint(1, 5), random.randint(1, 5)
        while grid[x][y] != 'o':
            x, y = random.randint(1, 5), random.randint(1, 5)
        grid[x][y] = '-'

    # 放置C类道具
    for i in range(c):
        x, y = random.randint(1, 5), random.randint(1, 5)
        while grid[x][y] != 'o':
            x, y = random.randint(1, 5), random.randint(1, 5)
        grid[x][y] = 'x'

    # 打印结果
    for row in grid:
        print(' '.join(row))

RandomStart(3,3,1)