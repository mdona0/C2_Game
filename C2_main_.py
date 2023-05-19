import random
from C2_piece import Piece, KingPiece, RevivePiece, ConfusePiece, AttractPiece, ArcherPiece
from C2_piece import BubblePiece, WitchPiece, SpyPiece, Songstress, GroundedPiece, Angel

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


def Next(game, player, max_attempts=1000):
    attempts = 0
    while attempts < max_attempts:
        x, y = random.randint(0, 6), random.randint(0, 6)
        new_x, new_y = random.randint(0, 6), random.randint(0, 6)

        piece = game.board.board[y][x]
        if piece is not None and piece.player == player:
            if game.move_piece(x, y, new_x, new_y):
                return x, y, new_x, new_y
        attempts += 1
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

