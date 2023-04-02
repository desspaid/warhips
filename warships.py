from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы вышли за пределы доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже нанесли удар по этой клетке"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, start_point, length, orientation):
        self.startPoint = start_point
        self.length = length
        self.orientation = orientation
        self.lives = length
    
    @property
    def body(self):
        ship_body = []
        for i in range(self.length):
            cur_x = self.startPoint.x
            cur_y = self.startPoint.y
            
            if self.orientation == 0:
                cur_x += i
            
            elif self.orientation == 1:
                cur_y += i
            
            ship_body.append(Dot(cur_x, cur_y))
        
        return ship_body
    

class Board:
    def __init__(self, hide_ships = False, size = 6):
        self.size = size
        self.hideShips = hide_ships
        
        self.count = 0
        
        self.field = [ ["O"]*size for _ in range(size) ]
        
        self.busy = []
        self.ships = []
    
    def add_ship(self, ship):
        
        for dot in ship.body:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.body:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.body:
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "T"
                    self.busy.append(cur)
    
    def __str__(self):
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hideShips:
            res = res.replace("■", "О")
        return res
    
    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.body:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Палундра! Вы его потопили!!!")
                    return False
                else:
                    print("Есть пробитие!")
                    return True
        
        self.field[d.x][d.y] = "T"
        print("Не в этот раз, попробуйте еще раз.")
        return False
    
    def start(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as error:
                print(error)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход соперника: {dot.x+1} {dot.y+1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            cords = input("Капитан, куда стреляем?").split()
            
            if len(cords) != 2:
                print(" Уточни местоположение корабля точнее! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Выбери место для обстрела ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)


class Game:
    def __init__(self, size = 6):
        self.size = size
        player_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hideShips = True
        
        self.ai = AI(ai_board, player_board)
        self.us = User(player_board, ai_board)
    
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board
    
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.start()
        return board

    def greet(self):
        print("-------------------------------")
        print("Палундра, свистать всех наверх!")
        print("      Капитан на корабле       ")
        print("Начинаем нападение на соперника")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Ваше поле боя:")
            print(self.us.board)
            print("-"*20)
            print("Поле боя соперника:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходи капитан!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит соперник!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print("-"*20)
                print("Капитан одержал очередную победу!")
                break
            
            if self.us.board.count == 7:
                print("-"*20)
                print("Пороховая обезьяна нас подставила! Мы проиграли этот бой, срочно отступаем!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
            
g = Game()
g.start()
