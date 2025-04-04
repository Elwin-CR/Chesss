import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 800  # Keep the board fully square and large enough
SIDEBAR_WIDTH = 200  # Reduce sidebar width to make more room for board
WIDTH, HEIGHT = BOARD_SIZE + SIDEBAR_WIDTH, BOARD_SIZE  # Adjust height to fit
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_SIZE // COLS  # Ensure square tiles



# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 130, 180)
TEXT_COLOR = (255, 255, 255)
BOARD_WHITE = (238, 238, 210)
BOARD_BLACK = (118, 150, 86)
HIGHLIGHT_COLOR = (186, 202, 68, 150)
CHECK_COLOR = (255, 255, 0, 150)
CHECKMATE_COLOR = (255, 0, 0)
CASTLING_COLOR = (0, 255, 255, 150)
SIDEBAR_COLOR = (240, 240, 240)
CAPTURED_PIECE_SIZE = 40

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
pygame.display.update()

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 36)

class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.hover = False

    def draw(self):
        color = (BUTTON_COLOR[0] + 30, BUTTON_COLOR[1] + 30, BUTTON_COLOR[2] + 30) if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)
        
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            self.action()

def home_screen():
    title_text = font_large.render("CHESS", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))

    # Load and scale background once
    background = pygame.image.load('C:/Users/elwin/Desktop/Code/chess/chess_logo.jpg')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    start_button = Button("Start Game", WIDTH//2 - 100, HEIGHT//2, 200, 60, start_game)
    quit_button = Button("Quit", WIDTH//2 - 100, HEIGHT//2 + 100, 200, 60, quit_game)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Draw background first
        screen.blit(background, (0, 0))

        # Then draw title and buttons
        screen.blit(title_text, title_rect)

        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        start_button.draw()
        quit_button.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_button.check_click(mouse_pos)
                quit_button.check_click(mouse_pos)

        pygame.display.flip()

def quit_game():
    pygame.quit()
    sys.exit()

def load_pieces():
    pieces = {}
    piece_names = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
    colors = ['white', 'black']
    
    for color in colors:
        for name in piece_names:
            try:
                image = pygame.image.load(f'img/{color}-{name}.png')
                pieces[f'{color}_{name}'] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                # Create smaller version for captured pieces display
                pieces[f'small_{color}_{name}'] = pygame.transform.scale(image, (CAPTURED_PIECE_SIZE, CAPTURED_PIECE_SIZE))
            except:
                # Fallback: create simple colored rectangles
                surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                col = (255, 255, 255) if color == "white" else (50, 50, 50)
                pygame.draw.rect(surf, col, (5, 5, SQUARE_SIZE-10, SQUARE_SIZE-10), border_radius=5)
                text = font_small.render(name[0].upper(), True, (255, 0, 0) if color == "white" else (0, 255, 0))
                surf.blit(text, (SQUARE_SIZE//2 - text.get_width()//2, SQUARE_SIZE//2 - text.get_height()//2))
                pieces[f'{color}_{name}'] = surf
                # Create small version
                small_surf = pygame.Surface((CAPTURED_PIECE_SIZE, CAPTURED_PIECE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(small_surf, col, (2, 2, CAPTURED_PIECE_SIZE-4, CAPTURED_PIECE_SIZE-4), border_radius=3)
                small_text = font_small.render(name[0].upper(), True, (255, 0, 0) if color == "white" else (0, 255, 0))
                small_surf.blit(small_text, (CAPTURED_PIECE_SIZE//2 - small_text.get_width()//2, 
                                           CAPTURED_PIECE_SIZE//2 - small_text.get_height()//2))
                pieces[f'small_{color}_{name}'] = small_surf
                print(f"Could not load image for {color}_{name}, using fallback")
    
    return pieces

def initialize_board():
    return [
        ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_knight", "black_rook"],
        ["black_pawn"] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        ["white_pawn"] * 8,
        ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_knight", "white_rook"]
    ]

def promote_pawn(board, row, col, color):
    """Prompts the user to choose a promotion piece when a pawn reaches the last rank."""
    if (color == "white" and row == 0) or (color == "black" and row == 7):
        pieces = ["queen", "rook", "bishop", "knight"]

        # Create a Pygame popup window to choose the piece
        running = True
        while running:
            screen.fill((200, 200, 200))  # Light gray background
            font = pygame.font.Font(None, 50)
            prompt_text = font.render(f"Promote {color} pawn to:", True, (0, 0, 0))
            screen.blit(prompt_text, (WIDTH//2 - 150, HEIGHT//3 - 50))

            buttons = []
            for i, piece in enumerate(pieces):
                button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//3 + i * 70, 200, 50)
                pygame.draw.rect(screen, (255, 255, 255), button_rect)  # White button
                pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)  # Black border
                text_surf = font.render(piece.capitalize(), True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=button_rect.center)
                screen.blit(text_surf, text_rect)
                buttons.append((button_rect, piece))

            pygame.display.flip()

            # Handle user click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button_rect, chosen_piece in buttons:
                        if button_rect.collidepoint(mouse_pos):
                            board[row][col] = f"{color}_{chosen_piece}"  # Update board with chosen piece
                            running = False  # Exit loop



class ChessGame:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.pieces = load_pieces()
        self.board = initialize_board()
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.turn = "white"
        self.checkmate = False
        self.check = False
        self.white_captured = []
        self.black_captured = []
        self.is_moving = False
        self.move_start_pos = None
        self.move_end_pos = None
        self.move_progress = 0
        self.ANIMATION_SPEED = 15
        self.show_checkmate_dialog = False
        self.dialog_new_game_button = Button("New Game", WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, self.reset_game)
        self.dialog_quit_button = Button("Quit", WIDTH//2 - 100, HEIGHT//2 + 130, 200, 60, home_screen)
        self.white_king_moved = False
        self.white_rook_left_moved = False
        self.white_rook_right_moved = False
        self.black_king_moved = False
        self.black_rook_left_moved = False
        self.black_rook_right_moved = False

    def handle_click(self, pos):
        if self.is_moving or self.show_checkmate_dialog:
            return
            
        # Only handle clicks on the board area
        if pos[0] >= BOARD_SIZE:
            return

        col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        clicked_piece = self.board[row][col]
        
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                self.move_start_pos = self.selected_pos
                self.move_end_pos = (row, col)
                self.is_moving = True
                self.move_progress = 0
            self.selected_piece = None
            self.valid_moves = []
        else:
            if clicked_piece and clicked_piece.startswith(self.turn):
                self.selected_piece = clicked_piece
                self.selected_pos = (row, col)
                self.valid_moves = self.get_valid_moves(clicked_piece, (row, col))
                # Filter out moves that would leave king in check
                self.valid_moves = [move for move in self.valid_moves if not self.would_be_in_check((row, col), move)]

    def would_be_in_check(self, start_pos, end_pos):
        # Simulate the move
        temp_board = [row[:] for row in self.board]
        piece = temp_board[start_pos[0]][start_pos[1]]
        temp_board[end_pos[0]][end_pos[1]] = piece
        temp_board[start_pos[0]][start_pos[1]] = None
        
        # Find king position
        king_pos = None
        for row in range(ROWS):
            for col in range(COLS):
                p = temp_board[row][col]
                if p and p.startswith(self.turn) and p.endswith('king'):
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        # Check if king is under attack
        enemy_color = "black" if self.turn == "white" else "white"
        enemy_moves = []
        for row in range(ROWS):
            for col in range(COLS):
                p = temp_board[row][col]
                if p and p.startswith(enemy_color):
                    enemy_moves.extend(self.get_raw_moves(p, (row, col), temp_board))
        
        return king_pos in enemy_moves if king_pos else False

    def get_raw_moves(self, piece, pos, board):
        moves = []
        row, col = pos
        piece_type = piece.split('_')[1]
        color = piece.split('_')[0]

        if piece_type == "pawn":
            direction = -1 if color == "white" else 1
            start_row = 6 if color == "white" else 1

            if 0 <= row + direction < 8 and board[row + direction][col] is None:
                moves.append((row + direction, col))
                if row == start_row and board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))
            
            for dc in [-1, 1]:
                if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                    target = board[row + direction][col + dc]
                    if target and not target.startswith(color):
                        moves.append((row + direction, col + dc))

        elif piece_type == "rook":
            moves.extend(self.get_directional_moves([(1, 0), (-1, 0), (0, 1), (0, -1)], row, col, board, color))

        elif piece_type == "bishop":
            moves.extend(self.get_directional_moves([(1, 1), (-1, -1), (1, -1), (-1, 1)], row, col, board, color))

        elif piece_type == "queen":
            moves.extend(self.get_directional_moves([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)], row, col, board, color))

        elif piece_type == "knight":
            knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for move in knight_moves:
                r, c = row + move[0], col + move[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if not target or not target.startswith(color):
                        moves.append((r, c))

        elif piece_type == "king":
            king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for move in king_moves:
                r, c = row + move[0], col + move[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if not target or not target.startswith(color):
                        moves.append((r, c))

        return moves

    def get_valid_moves(self, piece, pos):
        moves = []
        row, col = pos
        piece_type = piece.split('_')[1]
        color = piece.split('_')[0]

        if piece_type == "pawn":
            direction = -1 if color == "white" else 1
            start_row = 6 if color == "white" else 1

            if 0 <= row + direction < 8 and self.board[row + direction][col] is None:
                moves.append((row + direction, col))
                if row == start_row and self.board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))
            
            for dc in [-1, 1]:
                if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                    target = self.board[row + direction][col + dc]
                    if target and not target.startswith(color):
                        moves.append((row + direction, col + dc))

        elif piece_type == "rook":
            moves.extend(self.get_directional_moves([(1, 0), (-1, 0), (0, 1), (0, -1)], row, col, self.board, color))

        elif piece_type == "bishop":
            moves.extend(self.get_directional_moves([(1, 1), (-1, -1), (1, -1), (-1, 1)], row, col, self.board, color))

        elif piece_type == "queen":
            moves.extend(self.get_directional_moves([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)], row, col, self.board, color))

        elif piece_type == "knight":
            knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for move in knight_moves:
                r, c = row + move[0], col + move[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if not target or not target.startswith(color):
                        moves.append((r, c))

        elif piece_type == "king":
            king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for move in king_moves:
                r, c = row + move[0], col + move[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if not target or not target.startswith(color):
                        moves.append((r, c))
            
            # Castling
            if not self.is_in_check(color):
                if color == "white" and not self.white_king_moved:
                    # Kingside castling
                    if (not self.white_rook_right_moved and 
                        self.board[7][5] is None and 
                        self.board[7][6] is None and
                        not self.is_square_under_attack(7, 5, "black") and
                        not self.is_square_under_attack(7, 6, "black")):
                        moves.append((7, 6))  # Castling kingside
                    # Queenside castling
                    if (not self.white_rook_left_moved and 
                        self.board[7][3] is None and 
                        self.board[7][2] is None and 
                        self.board[7][1] is None and
                        not self.is_square_under_attack(7, 3, "black") and
                        not self.is_square_under_attack(7, 2, "black")):
                        moves.append((7, 2))  # Castling queenside
                elif color == "black" and not self.black_king_moved:
                    # Kingside castling
                    if (not self.black_rook_right_moved and 
                        self.board[0][5] is None and 
                        self.board[0][6] is None and
                        not self.is_square_under_attack(0, 5, "white") and
                        not self.is_square_under_attack(0, 6, "white")):
                        moves.append((0, 6))  # Castling kingside
                    # Queenside castling
                    if (not self.black_rook_left_moved and 
                        self.board[0][3] is None and 
                        self.board[0][2] is None and 
                        self.board[0][1] is None and
                        not self.is_square_under_attack(0, 3, "white") and
                        not self.is_square_under_attack(0, 2, "white")):
                        moves.append((0, 2))  # Castling queenside

        return moves

    def is_square_under_attack(self, row, col, by_color):
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece and piece.startswith(by_color):
                    moves = self.get_raw_moves(piece, (r, c), self.board)
                    if (row, col) in moves:
                        return True
        return False

    def get_directional_moves(self, directions, row, col, board, color):
        moves = []
        for direction in directions:
            for i in range(1, 8):
                r, c = row + direction[0] * i, col + direction[1] * i
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if not target:
                        moves.append((r, c))
                    elif not target.startswith(color):
                        moves.append((r, c))
                        break
                    else:
                        break
        return moves

    def update_board(self):
        piece = self.board[self.move_start_pos[0]][self.move_start_pos[1]]
        target = self.board[self.move_end_pos[0]][self.move_end_pos[1]]
        piece_type = piece.split('_')[1]
        color = piece.split('_')[0]

        # Handle castling
        if piece_type == "king" and abs(self.move_start_pos[1] - self.move_end_pos[1]) == 2:
            # Kingside castling
            if self.move_end_pos[1] == 6:
                if color == "white":
                    # Move rook
                    self.board[7][5] = self.board[7][7]
                    self.board[7][7] = None
                    self.white_rook_right_moved = True
                else:
                    self.board[0][5] = self.board[0][7]
                    self.board[0][7] = None
                    self.black_rook_right_moved = True
            # Queenside castling
            elif self.move_end_pos[1] == 2:
                if color == "white":
                    # Move rook
                    self.board[7][3] = self.board[7][0]
                    self.board[7][0] = None
                    self.white_rook_left_moved = True
                else:
                    self.board[0][3] = self.board[0][0]
                    self.board[0][0] = None
                    self.black_rook_left_moved = True

        # Update king/rook moved status
        if piece_type == "king":
            if color == "white":
                self.white_king_moved = True
            else:
                self.black_king_moved = True
        elif piece_type == "rook":
            if color == "white":
                if self.move_start_pos == (7, 0):
                    self.white_rook_left_moved = True
                elif self.move_start_pos == (7, 7):
                    self.white_rook_right_moved = True
            else:
                if self.move_start_pos == (0, 0):
                    self.black_rook_left_moved = True
                elif self.move_start_pos == (0, 7):
                    self.black_rook_right_moved = True

        if target:
            if target.startswith('white'):
                self.white_captured.append(target)
            else:
                self.black_captured.append(target)

        self.board[self.move_end_pos[0]][self.move_end_pos[1]] = piece
        self.board[self.move_start_pos[0]][self.move_start_pos[1]] = None

    def draw_sidebar(self):
        # Draw sidebar background
        pygame.draw.rect(screen, SIDEBAR_COLOR, (BOARD_SIZE, 0, SIDEBAR_WIDTH, HEIGHT))
        
        # Draw captured pieces title
        captured_title = font_medium.render("Captured:", True, BLACK)
        screen.blit(captured_title, (BOARD_SIZE + 20, 20))
        
        # Draw white captured pieces
        white_title = font_small.render("White took:", True, BLACK)
        screen.blit(white_title, (BOARD_SIZE + 20, 70))
        for i, piece in enumerate(self.black_captured):
            x = BOARD_SIZE + 20 + (i % 4) * (CAPTURED_PIECE_SIZE + 5)
            y = 110 + (i // 4) * (CAPTURED_PIECE_SIZE + 5)
            screen.blit(self.pieces[f'small_{piece}'], (x, y))
        
        # Draw black captured pieces
        black_title = font_small.render("Black took:", True, BLACK)
        screen.blit(black_title, (BOARD_SIZE + 20, HEIGHT//2 + 20))
        for i, piece in enumerate(self.white_captured):
            x = BOARD_SIZE + 20 + (i % 4) * (CAPTURED_PIECE_SIZE + 5)
            y = HEIGHT//2 + 60 + (i // 4) * (CAPTURED_PIECE_SIZE + 5)
            screen.blit(self.pieces[f'small_{piece}'], (x, y))
        
        # Draw current turn indicator
        turn_text = font_medium.render(f"{self.turn.capitalize()}'s turn", True, 
                                     (0, 0, 0) if self.turn == "white" else (255, 255, 255))
        turn_bg = (255, 255, 255) if self.turn == "white" else (0, 0, 0)
        pygame.draw.rect(screen, turn_bg, (BOARD_SIZE + 20, HEIGHT - 100, SIDEBAR_WIDTH - 40, 60))
        screen.blit(turn_text, (BOARD_SIZE + (SIDEBAR_WIDTH - turn_text.get_width())//2, HEIGHT - 80))

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = BOARD_WHITE if (row + col) % 2 == 0 else BOARD_BLACK
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and (not self.is_moving or (row, col) != self.move_start_pos):
                    screen.blit(self.pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def animate_move(self):
        row1, col1 = self.move_start_pos
        row2, col2 = self.move_end_pos
        piece = self.board[row1][col1]
        
        move_x = (col2 - col1) * self.move_progress / SQUARE_SIZE * SQUARE_SIZE
        move_y = (row2 - row1) * self.move_progress / SQUARE_SIZE * SQUARE_SIZE
        screen.blit(self.pieces[piece], (col1 * SQUARE_SIZE + move_x, row1 * SQUARE_SIZE + move_y))

    def draw_valid_moves(self):
        for move in self.valid_moves:
            row, col = move
            # Check if this is a castling move
            if (self.selected_piece and self.selected_piece.endswith("king") and 
                abs(self.selected_pos[1] - col) == 2):
                color = CASTLING_COLOR
            else:
                color = HIGHLIGHT_COLOR
            
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill(color)
            screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def draw_selected_tile(self):
        if self.selected_pos:
            row, col = self.selected_pos
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

    def display_checkmate_dialog(self):
        # Darken background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Dialog box
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 150, HEIGHT//2 - 100, 300, 300), border_radius=15)
        
        # Checkmate text
        text = font_large.render("CHECKMATE!", True, CHECKMATE_COLOR)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 70))
        
        # Winner text
        winner = "White" if self.turn == "black" else "Black"
        winner_text = font_medium.render(f"{winner} wins!", True, BLACK)
        screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 20))
        
        # Draw dialog buttons
        mouse_pos = pygame.mouse.get_pos()
        self.dialog_new_game_button.check_hover(mouse_pos)
        self.dialog_quit_button.check_hover(mouse_pos)
        self.dialog_new_game_button.draw()
        self.dialog_quit_button.draw()

    def is_in_check(self, color):
        king_pos = None
        enemy_moves = []
        enemy_color = "black" if color == "white" else "white"

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.startswith(color) and piece.endswith('king'):
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.startswith(enemy_color):
                    enemy_moves.extend(self.get_raw_moves(piece, (row, col), self.board))

        return king_pos in enemy_moves if king_pos else False

    def has_king_escape(self):
        color = self.turn
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.startswith(color) and piece.endswith("king"):
                    valid_moves = self.get_valid_moves(piece, (row, col))
                    for move in valid_moves:
                        if not self.would_be_in_check((row, col), move):
                            return True
        
        # Check if any other piece can block or capture
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.startswith(color) and not piece.endswith("king"):
                    valid_moves = self.get_valid_moves(piece, (row, col))
                    for move in valid_moves:
                        temp_board = [r[:] for r in self.board]
                        temp_board[move[0]][move[1]] = piece
                        temp_board[row][col] = None
                        
                        temp_game = ChessGame()
                        temp_game.board = temp_board
                        temp_game.turn = color
                        
                        if not temp_game.is_in_check(color):
                            return True
        return False

    def update(self):
        if self.is_moving:
            self.move_progress += self.ANIMATION_SPEED
            if self.move_progress >= SQUARE_SIZE:
                self.is_moving = False
                self.move_progress = 0
                self.update_board()
                self.turn = "black" if self.turn == "white" else "white"
                self.check = self.is_in_check(self.turn)
                if self.check and not self.has_king_escape():
                    self.checkmate = True
                    self.show_checkmate_dialog = True

    def draw(self):
        self.draw_board()
        
        # Highlight check first (behind pieces)
        if self.check and not self.checkmate:
            king_pos = None
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.board[row][col]
                    if piece and piece.startswith(self.turn) and piece.endswith('king'):
                        king_pos = (row, col)
                        break
                if king_pos:
                    break
            
            if king_pos:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(CHECK_COLOR)
                screen.blit(s, (king_pos[1] * SQUARE_SIZE, king_pos[0] * SQUARE_SIZE))
        
        # Draw pieces and animations
        if self.is_moving:
            self.draw_pieces()
            self.animate_move()
        else:
            self.draw_pieces()
        
        # Draw highlights on top of pieces
        self.draw_valid_moves()
        self.draw_selected_tile()
        
        # Draw sidebar
        self.draw_sidebar()
        
        if self.show_checkmate_dialog:
            self.display_checkmate_dialog()

def start_game():
    game = ChessGame()
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(mouse_pos)
        
        game.update()
        
        screen.fill(BLACK)
        game.draw()
        
        pygame.display.flip()

if __name__ == "__main__":
    home_screen()