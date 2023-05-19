import random

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