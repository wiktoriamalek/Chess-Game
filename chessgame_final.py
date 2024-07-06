from vpython import *

class ChessPiece:
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.graphics = []

    def draw(self):
        pass

class Pawn(ChessPiece):
    def draw(self):
        self.graphics = [
            sphere(pos=self.position + vector(0, 0, 0.6), radius=0.3, color=self.color),
            cylinder(pos=self.position, axis=vector(0, 0, 0.5), radius=0.3, color=self.color),
            cylinder(pos=self.position + vector(0, 0, 0.5), axis=vector(0, 0, 0.1), radius=0.15, color=self.color)
        ]

class Rook(ChessPiece):
    def draw(self):
        self.graphics = [
            box(pos=self.position + vector(0, 0, 0.5), size=vector(0.6, 0.6, 1), color=self.color),
            cylinder(pos=self.position, axis=vector(0, 0, 0.5), radius=0.3, color=self.color)
        ]

class Knight(ChessPiece):
    def draw(self):
        self.graphics = [
            sphere(pos=self.position + vector(0, 0, 0.8), radius=0.4, color=self.color),
            box(pos=self.position + vector(0, 0, 0.4), size=vector(0.6, 0.3, 0.8), color=self.color),
            cylinder(pos=self.position, axis=vector(0, 0, 0.4), radius=0.3, color=self.color)
        ]

    def is_valid_move(self, start, end, pieces):
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

class Bishop(ChessPiece):
    def draw(self):
        self.graphics = [
            cone(pos=self.position + vector(0, 0, 0.5), axis=vector(0, 0, 1), radius=0.3, color=self.color),
            cylinder(pos=self.position, axis=vector(0, 0, 0.5), radius=0.3, color=self.color)
        ]

class Queen(ChessPiece):
    def draw(self):
        self.graphics = [
            pyramid(pos=self.position + vector(0, 0, 1), size=vector(0.8, 0.8, 1.2), color=self.color),
            cylinder(pos=self.position, axis=vector(0, 0, 0.8), radius=0.4, color=self.color),
            ring(pos=self.position + vector(0, 0, 1.4), axis=vector(0, 0, 1), radius=0.5, thickness=0.1, color=self.color)
        ]

class King(ChessPiece):
    def draw(self):
        self.graphics = [
            pyramid(pos=self.position + vector(0, 0, 1.2), size=vector(0.8, 0.8, 1.5), color=self.color),
            cylinder(pos=self.position, axis=vector(0, 0, 0.8), radius=0.4, color=self.color),
            sphere(pos=self.position + vector(0, 0, 2.1), radius=0.2, color=self.color)
        ]

class ChessGame:
    def __init__(self):
        self.camera_pos = vector(0, -10, 10)
        self.camera_target = vector(0, 0, 0)
        self.camera_up = vector(0, 0, 1)
        self.camera_speed = 0.5
        self.rotation_speed = 0.5
        self.selected_piece = None
        self.selected_piece_pos = None
        self.highlight_ring = None
        self.highlight_tiles = []
        self.dragging = False
        self.last_mouse_pos = vector(0, 0, 0)
        self.current_turn = 'white'
        self.menu_open = False
        self.game_over = False

        self.board_size = 8
        self.tile_size = 1
        self.pieces = {}

        self.move_history = []

        self.scene = canvas(title='Chess Game', width=800, height=800, center=vector(0, 0, 0), background=color.gray(0.5))

        self.draw_chessboard()
        self.draw_pieces()
        self.update_camera()

        self.scene.bind('keydown', self.handle_key_event)
        self.scene.bind('mousedown', self.handle_mouse_down)
        self.scene.bind('mouseup', self.handle_mouse_up)
        self.scene.bind('mousemove', self.handle_mouse_move)
        self.scene.bind('click', self.handle_mouse_click)

        self.button_new_game = button(bind=self.restart_game, text='New Game', pos=self.scene.title_anchor)
        self.undo_button = button(bind=self.undo_last_move, text='Undo', pos=self.scene.title_anchor)
        self.instruction_button = button(bind=self.show_instruction, text='Instruction', pos=self.scene.title_anchor)
        self.authors_button = button(bind=self.show_authors, text='Authors', pos=self.scene.title_anchor)
        self.back_button = button(bind=self.hide_instruction, text='Back', pos=self.scene.title_anchor)
        self.exit_button = button(bind=self.exit_game, text='Exit', pos=self.scene.title_anchor)
        self.message_text = wtext(text='', pos=self.scene.title_anchor)

    def draw_chessboard(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                tile_color = color.white if (i + j) % 2 == 0 else color.black
                box(pos=vector(i - self.board_size / 2 + 0.5, j - self.board_size / 2 + 0.5, 0),
                    size=vector(self.tile_size, self.tile_size, 0.1),
                    color=tile_color)

    def draw_pieces(self):
        self.pieces = {}
        for i in range(8):
            self.pieces[(i, 1)] = Pawn(vector(i - self.board_size / 2 + 0.5, 1 - self.board_size / 2 + 0.5, 0.1), color.white)
            self.pieces[(i, 6)] = Pawn(vector(i - self.board_size / 2 + 0.5, 6 - self.board_size / 2 + 0.5, 0.1), color.black)

        self.pieces[(0, 0)] = Rook(vector(0 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(7, 0)] = Rook(vector(7 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(0, 7)] = Rook(vector(0 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)
        self.pieces[(7, 7)] = Rook(vector(7 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)

        self.pieces[(1, 0)] = Knight(vector(1 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(6, 0)] = Knight(vector(6 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(1, 7)] = Knight(vector(1 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)
        self.pieces[(6, 7)] = Knight(vector(6 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)

        self.pieces[(2, 0)] = Bishop(vector(2 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(5, 0)] = Bishop(vector(5 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(2, 7)] = Bishop(vector(2 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)
        self.pieces[(5, 7)] = Bishop(vector(5 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)

        self.pieces[(3, 0)] = Queen(vector(3 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(3, 7)] = Queen(vector(3 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)

        self.pieces[(4, 0)] = King(vector(4 - self.board_size / 2 + 0.5, 0 - self.board_size / 2 + 0.5, 0.1), color.white)
        self.pieces[(4, 7)] = King(vector(4 - self.board_size / 2 + 0.5, 7 - self.board_size / 2 + 0.5, 0.1), color.black)

        for piece in self.pieces.values():
            piece.draw()

    def handle_key_event(self, evt):
        key = evt.key
        if key == 'w':
            self.camera_pos += vector(0, 0, -self.camera_speed)
        elif key == 's':
            self.camera_pos += vector(0, 0, self.camera_speed)
        elif key == 'a':
            self.camera_pos += vector(-self.camera_speed, 0, 0)
        elif key == 'd':
            self.camera_pos += vector(self.camera_speed, 0, 0)
        elif key == 'q':
            self.camera_pos += vector(0, -self.camera_speed, 0)
        elif key == 'e':
            self.camera_pos += vector(0, self.camera_speed, 0)
        elif key == 'up':
            self.camera_target.z += self.rotation_speed
        elif key == 'down':
            self.camera_target.z -= self.rotation_speed
        elif key == 'left':
            self.camera_target.x -= self.rotation_speed
        elif key == 'right':
            self.camera_target.x += self.rotation_speed
        self.update_camera()

    def update_camera(self):
        self.scene.camera.pos = self.camera_pos
        self.scene.camera.axis = self.camera_target - self.camera_pos
        self.scene.camera.up = self.camera_up

    def handle_mouse_click(self, evt):
        if self.menu_open or self.game_over:
            return
        pos = evt.pos
        x = int(pos.x + self.board_size / 2)
        y = int(pos.y + self.board_size / 2)
        print(f"Clicked position: {x}, {y}")

        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            if self.selected_piece:
                if (x, y) != self.selected_piece_pos and ((x, y) not in self.pieces or self.pieces[(x, y)].color != self.selected_piece.color):
                    print(f"Attempting to move piece from {self.selected_piece_pos} to {(x, y)}")
                    if self.is_valid_move(self.selected_piece_pos, (x, y)):
                        print(f"Valid move for piece from {self.selected_piece_pos} to {(x, y)}")
                        self.move_piece(self.selected_piece_pos, (x, y))
                        if self.is_in_check(self.current_turn):
                            print(f"{self.current_turn.capitalize()} is in check!")
                            if self.is_checkmate(self.current_turn):
                                print(f"Checkmate! {self.current_turn.capitalize()} loses!")
                                self.display_winner('black' if self.current_turn == 'white' else 'white')
                        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                    else:
                        print(f"Invalid move for piece from {self.selected_piece_pos} to {(x, y)}")
                else:
                    print(f"Cannot move to the same position or invalid destination {(x, y)}")
                self.selected_piece = None
                self.selected_piece_pos = None
                if self.highlight_ring:
                    self.highlight_ring.visible = False
                    self.highlight_ring = None
                for tile in self.highlight_tiles:
                    tile.visible = False
                self.highlight_tiles = []
            else:
                if (x, y) in self.pieces and (
                    (self.pieces[(x, y)].color == color.white and self.current_turn == 'white') or
                    (self.pieces[(x, y)].color == color.black and self.current_turn == 'black')
                ):
                    self.selected_piece = self.pieces[(x, y)]
                    self.selected_piece_pos = (x, y)
                    print(f"Selected piece at: {self.selected_piece_pos}")
                    if self.highlight_ring:
                        self.highlight_ring.visible = False
                    self.highlight_ring = ring(pos=self.pieces[(x, y)].graphics[0].pos, axis=vector(0, 0, 1), radius=0.5, thickness=0.1, color=color.yellow)
                    self.highlight_tiles = self.highlight_moves(self.selected_piece_pos)

    def highlight_moves(self, pos):
        moves = []
        piece = self.pieces[pos]

        if isinstance(piece, Rook):
            moves.extend(self.highlight_straight_line_moves(pos, (1, 0)))  
            moves.extend(self.highlight_straight_line_moves(pos, (-1, 0)))  
            moves.extend(self.highlight_straight_line_moves(pos, (0, 1)))  
            moves.extend(self.highlight_straight_line_moves(pos, (0, -1)))  
        elif isinstance(piece, Knight):
            knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                            (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for move in knight_moves:
                x, y = pos[0] + move[0], pos[1] + move[1]
                if 0 <= x < self.board_size and 0 <= y < self.board_size:
                    if self.is_valid_move(pos, (x, y)):
                        tile = box(pos=vector(x - self.board_size / 2 + 0.5, y - self.board_size / 2 + 0.5, 0.05),
                                   size=vector(self.tile_size, self.tile_size, 0.1), color=color.blue, opacity=0.5)
                        moves.append(tile)
        else:
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.is_valid_move(pos, (x, y)):
                        tile = box(pos=vector(x - self.board_size / 2 + 0.5, y - self.board_size / 2 + 0.5, 0.05),
                                size=vector(self.tile_size, self.tile_size, 0.1), color=color.blue, opacity=0.5)
                        moves.append(tile)
        return moves

    def highlight_straight_line_moves(self, start, direction):
        moves = []
        x, y = start
        dx, dy = direction
        x += dx
        y += dy
        while 0 <= x < self.board_size and 0 <= y < self.board_size:
            if (x, y) in self.pieces:
                if self.pieces[(x, y)].color != self.pieces[start].color:
                    tile = box(pos=vector(x - self.board_size / 2 + 0.5, y - self.board_size / 2 + 0.5, 0.05),
                            size=vector(self.tile_size, self.tile_size, 0.1), color=color.blue, opacity=0.5)
                    moves.append(tile)
                break
            tile = box(pos=vector(x - self.board_size / 2 + 0.5, y - self.board_size / 2 + 0.5, 0.05),
                    size=vector(self.tile_size, self.tile_size, 0.1), color=color.blue, opacity=0.5)
            moves.append(tile)
            x += dx
            y += dy
        return moves

    def move_piece(self, start, end):
        print(f"Moving piece from {start} to {end}")
        if end in self.pieces:
            if isinstance(self.pieces[end], King):
                self.display_winner('white' if self.pieces[end].color == color.black else 'black')
                return
            for part in self.pieces[end].graphics:
                part.visible = False
            del self.pieces[end]

        piece = self.pieces.pop(start)
        for part in piece.graphics:
            part.pos = vector(end[0] - self.board_size / 2 + 0.5, end[1] - self.board_size / 2 + 0.5, part.pos.z)
        self.pieces[end] = piece
        self.move_history.append((start, end))
        print(f"Moved piece from {start} to {end}")

    def is_valid_move(self, start, end):
        print(f"Validating move from {start} to {end}")
        if start == end:
            print("Start and end positions are the same")
            return False

        if end[0] < 0 or end[0] >= self.board_size or end[1] < 0 or end[1] >= self.board_size:
            print("End position is out of board bounds")
            return False

        piece = self.pieces[start]

        if isinstance(piece, Pawn):
            direction = 1 if piece.color == color.white else -1
            start_row = 1 if piece.color == color.white else 6
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if dx == 0:
                if dy == direction and end not in self.pieces:
                    return True
                if dy == 2 * direction and start[1] == start_row and end not in self.pieces and (start[0], start[1] + direction) not in self.pieces:
                    return True
            elif abs(dx) == 1 and dy == direction and end in self.pieces and self.pieces[end].color != piece.color:
                return True
        elif isinstance(piece, Rook):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if dx == 0 or dy == 0:
                return self.is_clear_path_rook(start, end)
        elif isinstance(piece, Bishop):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if abs(dx) == abs(dy):
                return self.is_clear_path_bishop(start, end)
        elif isinstance(piece, Queen):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if dx == 0 or dy == 0:
                return self.is_clear_path_rook(start, end)
            if abs(dx) == abs(dy):
                return self.is_clear_path_bishop(start, end)
        elif isinstance(piece, King):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if abs(dx) <= 1 and abs(dy) <= 1:
                return True
        elif isinstance(piece, Knight):
            return piece.is_valid_move(start, end, self.pieces)

        return False

    def is_clear_path_rook(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if dx != 0 and dy != 0:
            print("Rook move is not in a straight line")
            return False
        
        step_x = int(dx / abs(dx)) if dx != 0 else 0
        step_y = int(dy / abs(dy)) if dy != 0 else 0
        x, y = start[0] + step_x, start[1] + step_y
        
        while (x, y) != end:
            if (x, y) in self.pieces:
                print(f"Rook move blocked by piece at {(x, y)}")
                return False
            x += step_x
            y += step_y

        return True

    def is_clear_path_bishop(self, start, end):
        dx = 1 if start[0] < end[0] else -1
        dy = 1 if start[1] < end[1] else -1
        x, y = start[0] + dx, start[1] + dy
        while (x, y) != end:
            if (x, y) in self.pieces:
                return False
            x += dx
            y += dy
        return True

    def is_in_check(self, color):
        king_pos = None
        for pos, piece in self.pieces.items():
            if isinstance(piece, King) and piece.color == color:
                king_pos = pos
                break
        if king_pos is None:
            return False

        for pos, piece in self.pieces.items():
            if piece.color != color:
                if self.is_valid_move(pos, king_pos):
                    return True
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        for pos, piece in self.pieces.items():
            if piece.color == color:
                for x in range(self.board_size):
                    for y in range(self.board_size):
                        if self.is_valid_move(pos, (x, y)):
                            original_pos = piece.position
                            self.move_piece(pos, (x, y))
                            if not self.is_in_check(color):
                                self.move_piece((x, y), pos)
                                return False
                            self.move_piece((x, y), pos)
                            piece.position = original_pos
        return True

    def display_winner(self, winner_color):
        self.game_over = True
        msg = f"{winner_color.capitalize()} wins by checkmate!"
        self.message_text.text = msg
        print(msg)

    def handle_mouse_down(self, evt):
        self.dragging = True
        self.last_mouse_pos = evt.pos

    def handle_mouse_up(self, evt):
        self.dragging = False

    def handle_mouse_move(self, evt):
        if self.dragging:
            dx = evt.pos.x - self.last_mouse_pos.x
            dy = evt.pos.y - self.last_mouse_pos.y
            self.last_mouse_pos = evt.pos
            self.camera_pos.x -= dx * self.camera_speed * 0.1
            self.camera_pos.y += dy * self.camera_speed * 0.1
            self.update_camera()

    def exit_game(self):
        print("Exiting the game...")
        self.close_game()

    def restart_game(self):
        self.current_turn = 'white'
        self.selected_piece = None
        self.selected_piece_pos = None
        if self.highlight_ring:
            self.highlight_ring.visible = False
            self.highlight_ring = None
        for tile in self.highlight_tiles:
            tile.visible = False
        self.highlight_tiles = []
        
        for piece in self.pieces.values():
            for part in piece.graphics:
                part.visible = False
        self.pieces = {}
        
        self.move_history = []
        self.draw_pieces()
        self.game_over = False
        self.message_text.text = ''

    def undo_last_move(self):
        if len(self.move_history) > 0:
            last_move = self.move_history.pop()
            start_pos, end_pos = last_move
            self.move_piece(end_pos, start_pos)
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def close_game(self):
        self.scene.delete()
        self.button_new_game.delete()
        self.undo_button.delete()
        self.exit_button.delete()

    def show_instruction(self):
        self.message_text.text = instruction_text

    def hide_instruction(self):
        self.message_text.text = ''

    def show_authors(self):
        self.message_text.text = authors_text

    def hide_authors(self):
        self.message_text.text = ''

authors_text = """
Authors: 
Patrycja Pieńkowska 193452
Wiktoria Malek 193323
kierunek: Automatyka, Cybernetyka i Robotyka
Semestr: 4
Grupa: 2
data: xx.06.2023r.
"""

instruction_text = """
Chess Instructions:

1. Each player starts with 16 pieces: one king, one queen, two rooks, two knights, two bishops, and eight pawns.
2. The objective of the game is to checkmate the opponent's king, meaning it is in a position to be captured and cannot escape.
3. Players take turns to make a move, starting with the white player.
4. Each type of piece moves differently:
   - King: Moves one square in any direction.
   - Queen: Moves any number of squares in any direction (diagonally, horizontally, or vertically).
   - Rook: Moves any number of squares horizontally or vertically.
   - Bishop: Moves any number of squares diagonally.
   - Knight: Moves in an L-shape, two squares in one direction and then one square in a perpendicular direction.
   - Pawn: Moves forward one square, but captures diagonally.
5. Pawns have special rules:
   - Pawns can move forward two squares on their first move.
   - Pawns can capture en passant if an opponent's pawn moves two squares forward from its starting position and lands next to the capturing pawn.
   - Pawns can promote to any other piece (except a king) if they reach the opponent's back rank.
6. The game ends when one player checkmates the other, or when a draw is declared due to stalemate, insufficient material, or other conditions.
"""

if __name__ == "__main__":
    game = ChessGame()
    while True:
        rate(30)
        if game.game_over:
            break
