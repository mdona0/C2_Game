import random

class Board:
    def __init__(self):
        self.board = [[None for _ in range(7)] for _ in range(7)]

    def __getitem__(self, index):
        return self.board[index]

    def place_piece(self, piece, x, y):
        if self.board[y][x] is not None:
            return False
        self.board[y][x] = piece
        return True

    def move_piece(self, x, y, new_x, new_y):
        if self.board[y][x] is None:
            return False
        piece = self.board[y][x]
        if piece.move(self, x, y, new_x, new_y):
            self.board[new_y][new_x] = piece
            self.board[y][x] = None
            return True
        return False

    def display(self):
        print("  0 1 2 3 4 5 6")
        for y, row in enumerate(self.board):
            row_display = []
            for cell in row:
                if cell is None:
                    row_display.append(".")
                else:
                    row_display.append(cell.name)
            print(f"{y} {' '.join(row_display)}")
        print("\n")

class Game:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.board = Board()
        self.turn = 0
        self.extra_move_piece = {1: None, 2: None}

    def play_turn(self, player):
        print(f"Player {player.number}'s turn")
        self.print_board()
        self.select_and_move_piece(player)
        if self.extra_move_piece[player.number] is not None:
            print("You have an extra move for the following piece:")
            print(self.extra_move_piece[player.number].name)
            self.select_and_move_piece(player)
            self.extra_move_piece[player.number] = None

    def place_piece(self, piece, x, y):
        return self.board.place_piece(piece, x, y)

    def move_piece(self, x, y, new_x, new_y):
        piece = self.board.board[y][x]
        if piece is not None and not piece.blocked and piece.move(self.board, x, y, new_x, new_y):
            self.board.move_piece(x, y, new_x, new_y)
            effect_result = piece.effect_func(self, new_x, new_y)
            if effect_result:
                self.check_win()
            return True
        return False
    
    def display(self):
        self.board.display()
    
    def special_win(self, player):
        print(f"Player {player} wins with a special victory condition!")
        self.game_over = True

    def capture_piece(self, x, y):
        piece = self.board.board[y][x]
        if piece is not None:
            # もし取られた駒が「忍者」であれば、対象の駒が動けるようになる
            if isinstance(piece, GroundedPiece) and piece.locked_target is not None:
                piece.locked_target.locked = False
            self.players[piece.player - 1].captured_pieces.append(piece)
            self.board.board[y][x] = None

    def initial_piece_placement(self, player):
        print(f"Player {player.number}, place your pieces:")
        self.print_board()
    
        for _ in range(5):
            print("Select a piece to place (type 'Angel of Nina' to summon the special piece):")
            for i, piece in enumerate(player.hand):
                print(f"{i + 1}. {piece.name}")
            piece_name = input("Enter the name or index of the piece: ")
    
            if piece_name.lower() == "Angel of Nina":
                piece = Angel(player.number)
            else:
                piece_index = int(piece_name) - 1
                piece = player.hand.pop(piece_index)
    
            x, y = self.select_coordinates(player.number)
            while not self.board.is_valid_coordinate(x, y) or not self.board.is_empty(x, y) or y > 1:
                print("Invalid position. Please select a valid position within your army lines.")
                x, y = self.select_coordinates(player.number)
    
            self.board.board[y][x] = piece
            piece.player = player

#class Piece:
#    def __init__(self, name, player, move_func=None, effect_func=None, effect_target_func=None):
#        self.name = name
#        self.player = player
#        self.move_func = move_func if move_func is not None else lambda *args: False
#        self.effect_func = effect_func
#        self.effect_target_func = effect_target_func
#        self.blocked = False
#        self.is_immune = False
#
#    def move(self, board, x, y, new_x, new_y):
#        if self.move_func is None:
#          return False
#        return self.move_func(board, x, y, new_x, new_y)
#
#    def move_piece(self, x, y, new_x, new_y):
#        piece = self.board.board[y][x]
#        if piece is None:
#            return False
#        if not piece.move(self, x, y, new_x, new_y):
#            return False
#        self.board.board[y][x] = None
#        self.board.board[new_y][new_x]
#
#    def effect(self, board, x, y):
#        if self.effect_func is None:
#            return
#        self.effect_func(board, x, y)

class Piece:
    def __init__(self, name, player, move_func, effect_func, effect_target_func=None):
        self.name = name
        self.player = player
        self.move_func = move_func
        self.effect_func = effect_func
        self.effect_target_func = effect_target_func
        self.blocked = False
        self.is_immune = False

    def move(self, board, x, y, new_x, new_y):
        if self.move_func is None:
            return False
        return self.move_func(board, x, y, new_x, new_y)

    def effect(self, board, x, y):
        if self.effect_func is None:
            return
        self.effect_func(board, x, y)

class KingPiece(Piece):
    def __init__(self, player):
        super().__init__("皇", player, self.move_func, self.effect_func)
        self.is_immune = True

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = abs(new_y - y)
        if (dx <= 1 and dy <= 1) or (dx == 0 and dy == 2) or (dx == 2 and dy == 0):
            return True
        return False

    def effect_func(self, board, x, y):
        pass


#蘇るレイラ（Rivive of Layla)
class RevivePiece(Piece):
    def __init__(self, player):
        super().__init__("蘇",player, self.move_func, self.effect_func)
        self.player = player
        self.can_revive = True

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = new_y - y if self.player == 1 else y - new_y
        if dy == 1 and (dx == 0 or dx == 1):
            return True
        return False

    def effect_func(self, board, x, y):
        if not self.can_revive:
            return

        enemy_piece = board.board[y][x]
        if enemy_piece is not None and enemy_piece.name != "King" and enemy_piece.player != self.player:
            self.can_revive = False
            # 自軍ライン以内で駒を再配置できる場所を探す
            for ry in range(2):
                for rx in range(7):
                    if board.board[ry if self.player == 1 else 6 - ry][rx] is None:
                        # 駒を再配置する
                        board.board[ry if self.player == 1 else 6 - ry][rx] = self
                        return

#翻弄のヴァネッサ(Trickster of Vanessa)
class ConfusePiece(Piece):
    def __init__(self, player):
        super().__init__("舞",player, self.move_func, self.effect_func)
        self.player = player

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = abs(new_y - y)
        if dx == 0 and dy == 1:
            return True
        return False

    def effect_func(self, game, x, y):
        print("Would you like to swap this piece with another one? (y/n)")
        choice = input().lower()
        if choice == "y":
            swap_x, swap_y = map(int, input("Enter the position of the piece to swap with (x y): ").split())
            other_piece = game.board.board[swap_y][swap_x]
            if other_piece is not None and other_piece.player == self.player:
                game.board.board[swap_y][swap_x] = self
                game.board.board[y][x] = other_piece


#誘引のエリー(Attract of Eliy)
class AttractPiece(Piece):
    def __init__(self, player):
        super().__init__("誘",player, self.move_func, self.effect_func)
        self.player = player

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = new_y - y if self.player == 1 else y - new_y
        if dy == 1 and (dx == 0 or dx == 1):
            return True
        return False

    def effect_func(self, game, x, y):
        print("Would you like to summon a piece behind this piece? (y/n)")
        choice = input().lower()
        if choice == "y":
            behind_y = y - 1 if self.player == 1 else y + 1
            if 0 <= behind_y < 7 and game.board.board[behind_y][x] is None:
                # 選択可能な呼び出し駒を表示
                print("Select the piece to summon:")
                for i, piece in enumerate(game.players[self.player - 1].hand):
                    print(f"{i + 1}. {piece.name}")
                piece_index = int(input("Enter the index of the piece to summon: ")) - 1
                summoned_piece = game.players[self.player - 1].hand.pop(piece_index)
                game.board.board[behind_y][x] = summoned_piece
                summoned_piece.blocked = False

def move_in_line(board, x, y, new_x, new_y):
    dx, dy = new_x - x, new_y - y
    if dx == 0 or dy == 0 or abs(dx) == abs(dy):
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        x += step_x
        y += step_y
        while x != new_x or y != new_y:
            if board.board[y][x] is not None:
                return False
            x += step_x
            y += step_y
        return True
    return False

class ArcherPiece(Piece):
    def __init__(self, player):
        super().__init__("弦", player, move_func=move_in_line,
                         effect_func=self.effect_func,
                         effect_target_func=self.effect_target_func)
        self.arrow_count = 3

    def effect_func(self, game, x, y):
        if self.arrow_count > 0:
            targets = self.effect_target_func(game, x, y)
            if targets:
                # Select a target and remove it
                target = random.choice(targets)
                target_x, target_y = target
                target_piece = game.board.board[target_y][target_x]
                target_piece.player.pieces_on_board.remove(target_piece)
                game.board.board[target_y][target_x] = None

                # Decrement the arrow count
                self.arrow_count -= 1

    def effect_target_func(self, game, x, y):
        targets = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 7 and 0 <= new_y < 7:
                target_piece = game.board.board[new_y][new_x]
                if target_piece is not None and target_piece.player != self.player:
                    targets.append((new_x, new_y))
        return targets


#泡沫のアリア(Bubble of Alia)泡
class BubblePiece(Piece):
    def __init__(self, player):
        super().__init__("朧",player, self.move_func, self.effect_func)
        self.player = player

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = abs(new_y - y)
        if dx == 1 and dy == 1:
            return True
        return False

    def effect_func(self, game, x, y):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (dx == 0) != (dy == 0):  # 前後左右1マス
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < 7 and 0 <= new_y < 7:
                        target_piece = game.board.board[new_y][new_x]
                        if target_piece is not None and target_piece.player != self.player and not target_piece.is_immune:
                            target_piece.blocked = True
    


#見習い魔女リズ(Witch if Liz)
class WitchPiece(Piece):
    def __init__(self, player):
        super().__init__("妖",player, self.move_func, self.effect_func)
        self.player = player

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = new_y - y if self.player == 1 else y - new_y
        if dx == 1 and dy == 2:
            return True
        return False

    def effect_func(self, game, x, y):
        new_x, new_y = game.get_target_position(x, y)
        target_piece = game.board.board[new_y][new_x]
        if target_piece is not None and target_piece.player != self.player and not target_piece.is_immune:
            target_piece.blocked = True

#密偵グレース(Spy of Grace)
class SpyPiece(Piece):
    def __init__(self, player):
        super().__init__("隠",player, self.move_func, self.effect_func)


    def move_func(self, board, x, y, new_x, new_y):
        dx, dy = abs(new_x - x), abs(new_y - y)
        if self.player == 1:
            forward_move = new_y - y
        else:
            forward_move = y - new_y

        if (dx == 1 and dy == 0) or (dx == 0 and dy == 1) or (dx == 0 and forward_move == 2):
            return True
        return False

    def effect_func(self, game, x, y):
        if (x == 0 or x == 6) and ((self.player == 1 and y == 6) or (self.player == 2 and y == 0)):
            game.special_win(self.player)



#禁足のウィロウ(Grounded of Willow)
class GroundedPiece(Piece):
    def __init__(self, player):
        super().__init__("忍", player, self.move_func, self.effect_func)
        self.locked = False
        self.locked_target = None

    def move_func(self, board, x, y, new_x, new_y):
        if not self.locked:
            dx, dy = abs(new_x - x), abs(new_y - y)
            return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)
        return False

    def effect_func(self, game, x, y):
        if self.locked_target is None:
            # 選択可能な敵の駒を表示
            print("Select the enemy piece to lock:")
            enemy_player = game.players[2 - self.player]
            for i, piece in enumerate(enemy_player.pieces_on_board()):
                print(f"{i + 1}. {piece.name}")
            piece_index = int(input("Enter the index of the piece to lock: ")) - 1
            locked_piece = enemy_player.pieces_on_board()[piece_index]

            # 対象の駒が剣王であれば効果を適用しない
            if not isinstance(locked_piece, KingPiece):
                self.locked_target = locked_piece
                locked_piece.locked = True
            else:
                print("You cannot lock the King.")


#歌姫ステラ(Songstress of Stella)
class Songstress(Piece):
    def __init__(self, player):
        super().__init__("囃", player ,self.move_func, self.effect_func)

    def move_func(self, board, x, y, new_x, new_y):
        return abs(new_x - x) == 1 and abs(new_y - y) == 1

    def effect_func(self, game, x, y):
        # 歌姫を盤面から取り除く
        game.board.board[y][x] = None
        self.player.pieces_on_board().remove(self)
    
        # 選択可能な味方の駒を表示
        print("Select one of your pieces to have an extra move next turn:")
        for i, piece in enumerate(self.player.pieces_on_board()):
            print(f"{i + 1}. {piece.name}")
        piece_index = int(input("Enter the index of the piece: ")) - 1
        target_piece = self.player.pieces_on_board()[piece_index]
    
        # 剣王を指定できないようにする
        if not isinstance(target_piece, KingPiece):
            game.extra_move_piece[self.player.number] = target_piece  # この行で効果を与える
        else:
            print("You cannot give an extra move to the Sword King.")

#聖天女ニナンナ(Angel of Nina)
class Angel(Piece):
    def __init__(self, player):
        super().__init__("巫",player, self.move_func, self.effect_func)
        self.player = player
        self.is_immune = True #

    def move_func(self, board, x, y, new_x, new_y):
        dx = abs(new_x - x)
        dy = abs(new_y - y)
        return (dx == 1 and dy == 1) or (dx == 0 and dy == 1)

    def effect_func(self, game, x, y):
        # 剣王と同じ効果のため、ここでは何も実装しない
        pass

# 他の駒を追加する場合、Piece クラスを継承した新しいクラスを作成し、
# move_func と effect_func を実装してください。

def generate_all_pieces(player_number):
    pieces = []

    # 駒の数を定義（各駒2個ずつ）
    num_pieces = {
        RevivePiece: 2,
        ConfusePiece: 2,
        AttractPiece: 2,
        ArcherPiece: 2,
        BubblePiece: 2,
        WitchPiece: 2,
        SpyPiece: 2,
        GroundedPiece: 2,
        Songstress: 2,
    }

    for piece_class, count in num_pieces.items():
        for _ in range(count):
            # プレイヤーの駒を生成
            pieces.append(piece_class(player_number))

    return pieces



def distribute_pieces(pieces):
    random.shuffle(pieces)
    player1_pieces = pieces[:7]
    player2_pieces = pieces[7:14]
    return player1_pieces, player2_pieces

def is_king_captured(game, player):
    king = "King" if player == 1 else "King"
    for y in range(7):
        for x in range(7):
            if game.board.board[y][x] is not None and game.board.board[y][x].name == king:
                return False
    return True

def is_valid_position(x, y, player):
    if player == 1:
        return 0 <= y <= 1
    elif player == 2:
        return 5 <= y <= 6
    return False

class Player:
    def __init__(self, player_number):
        self.player_number = player_number
        self.hand = []

    def generate_hand(self):
        all_pieces = generate_all_pieces(self.player_number)
        self.hand = random.sample(all_pieces, 7)
        return self.hand
    
    def generate_hand_5(self):
        all_pieces = generate_all_pieces(self.player_number)
        random.shuffle(all_pieces)
        return all_pieces[:5]

    def remove_piece_from_hand(self, piece):
        self.hand.remove(piece)


def main():
    print("Welcome to the game!")
    
    player1 = Player(1)
    player2 = Player(2)
    
    game = Game(player1, player2)


    

    # プレイヤーごとに手札を初期化し、ランダムに7枚の駒を配る
    player1_pieces = player1.generate_hand()
    player2_pieces = player2.generate_hand()

    # 剣王を配置
    player1_king = KingPiece(1)
    player2_king = KingPiece(2)
    
    game.board.place_piece(player1_king, 3, 0)
    game.board.place_piece(player2_king, 3, 6)

    # プレイヤーが選択した5枚の駒を配置
    for player, pieces in enumerate([player1_pieces, player2_pieces], start=1):
        for i in range(5):
            game.display()
            print(f"Player {player}'s pieces: {', '.join(piece.name for piece in pieces)}")
            #print("To summon the Angel of Nina, type 'Angel of Nina'")
            while True:
                piece_name = input(f"Player {player}, choose piece {i + 1} to place: ")
    
                if piece_name == "AngelCode:22":
                    chosen_piece = Angel(player)
                else:
                    chosen_piece = next((piece for piece in pieces if piece.name == piece_name), None)
    
                if chosen_piece is None:
                    print("Invalid piece name or piece already placed, please try again.")
                    continue
    
                if piece_name != "AngelCode:22":
                    pieces.remove(chosen_piece)
    
                while True:
                    x, y = map(int, input(f"Player {player}, enter the position for {chosen_piece.name} (x y): ").split())
                    if is_valid_position(x, y, player) and game.place_piece(chosen_piece, x, y):
                        break
                    print("Invalid position, please try again.")
                break
    

    # ゲームの進行
    current_player = 1
    while True:
        game.display()
        print(f"Player {current_player}'s turn.")
        x, y = map(int, input(f"Player {current_player}, choose piece to move (x y): ").split())
        new_x, new_y = map(int, input(f"Player {current_player}, enter the new position (new_x new_y): ").split())

        if game.move_piece(x, y, new_x, new_y):
            if is_king_captured(game, 3 - current_player):
                print(f"Player {current_player} wins!")
                break
            current_player = 3 - current_player
        else:
            print("Invalid move, please try again.")


def main2():
    player1 = Player(1)
    player2 = Player(2)
    game = Game(player1, player2)

        # 剣王を配置
    player1_king = KingPiece(1)
    player2_king = KingPiece(2)
    
    game.board.place_piece(player1_king, 3, 0)
    game.board.place_piece(player2_king, 3, 6)
    
    # 駒を配布
    player1_pieces = player1.generate_hand_5()
    player2_pieces = player2.generate_hand_5()
    
   # 配布された駒を自軍ラインにランダムに配置
    player1_start_positions = [(x, y) for x in range(5) for y in range(2)]
    player2_start_positions = [(x, y) for x in range(5) for y in range(5, 7)]

    random.shuffle(player1_start_positions)
    random.shuffle(player2_start_positions)

    for piece, (x, y) in zip(player1_pieces, player1_start_positions):
        game.place_piece(piece, x, y)

    for piece, (x, y) in zip(player2_pieces, player2_start_positions):
        game.place_piece(piece, x, y)

        # ゲームのメインループ
    current_player = 1
    while True:
        game.display()
        print(f"Player {current_player}'s turn.")

        valid_move = False
        while not valid_move:
            x, y = map(int, input(f"Player {current_player}, choose piece to move (x y): ").split())
            new_x, new_y = map(int, input(f"Player {current_player}, enter the new position (new_x new_y): ").split())

            if game.move_piece(x, y, new_x, new_y) is not None:
                valid_move = True
                if is_king_captured(game, 3 - current_player):
                    print(f"Player {current_player} wins!")
                    break
                current_player = 3 - current_player
            else:
                print("Invalid move, please try again.")



def Next (game, player_number):
    valid_moves = []

    for y in range(7):
        for x in range(7):
            piece = game.board.board[y][x]
            if piece is not None and piece.player == player_number:
                for new_y in range(7):
                    for new_x in range(7):
                        if game.move_piece(x, y, new_x, new_y):
                            valid_moves.append((x, y, new_x, new_y))
                            game.board.move_piece(new_x, new_y, x, y)  # 駒を元の位置に戻します

    if valid_moves:
        return random.choice(valid_moves)
    else:
        raise ValueError("No valid moves available")

def main2_auto():
    player1 = Player(1)
    player2 = Player(2)
    game = Game(player1, player2)

        # 剣王を配置
    player1_king = KingPiece(1)
    player2_king = KingPiece(2)
    
    game.board.place_piece(player1_king, 3, 0)
    game.board.place_piece(player2_king, 3, 6)
    
    # 駒を配布
    player1_pieces = player1.generate_hand_5()
    player2_pieces = player2.generate_hand_5()
    
   # 配布された駒を自軍ラインにランダムに配置
    player1_start_positions = [(x, y) for x in range(5) for y in range(2)]
    player2_start_positions = [(x, y) for x in range(5) for y in range(5, 7)]

    random.shuffle(player1_start_positions)
    random.shuffle(player2_start_positions)

    for piece, (x, y) in zip(player1_pieces, player1_start_positions):
        game.place_piece(piece, x, y)

    for piece, (x, y) in zip(player2_pieces, player2_start_positions):
        game.place_piece(piece, x, y)

    # ゲームの進行
    current_player = 1
    move_history = []  # 追加: 移動履歴のリスト
    while True:
        game.display()
        print(f"Player {current_player}'s turn.")

        x, y, new_x, new_y = Next (game, game.players[current_player - 1])

        if game.move_piece(x, y, new_x, new_y):  # 追加: 駒を動かす処理
            move_history.append((current_player, x, y, new_x, new_y))  # 追加: 移動履歴に追加
            print(f"Player {current_player} moved from ({x}, {y}) to ({new_x}, {new_y})")

            if is_king_captured(game, 3 - current_player):
                print(f"Player {current_player} wins!")
                break

            current_player = 3 - current_player

        # 追加: 入力履歴を表示
        print("Move history:")
        for i, move in enumerate(move_history, start=1):
            player, x, y, new_x, new_y = move
            print(f"{i}. Player {player} moved from ({x}, {y}) to ({new_x}, {new_y})")
        print("\n")


if __name__ == "__main__":
    main2_auto()

