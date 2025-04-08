'''
我来doc一下我的implementation

plates：每一个小块块，represented by type + location + relative coordinate + color 
board：一个大的container，里面有很多个plates，负责绘制所有的plates
round：一个回合，包含一个board和一个target number，负责判断这个回合是否完成


gridLength gridHeight: 40, 30 

'''


#plate color: 初始为白色，点击后选择颜色

    

import pygame 
import sys
import math
import numpy

class Plates:
    def __init__(self, plate_type, plate_color, plate_location, plate_xys):
        self.plate_type = plate_type
        self.plate_color = plate_color
        self.plate_location = plate_location 
        self.plate_xys = plate_xys
        self.plate_coordinates = [(0, 0) for _ in range(len(plate_xys))]
        self.button_rect = pygame.Rect(0, 0, 10, 10)  # Move handle
        self.xy_to_coordinates()
        self.dragging = False
        self.update_button_position()

    def draw_plate(self, screen):
        # Create a transparent surface
        temp_surface = pygame.Surface((800, 600), pygame.SRCALPHA)

        if self.plate_type == 1:
            pygame.draw.polygon(temp_surface, self.plate_color, self.plate_coordinates)
        elif self.plate_type == 2:
            center = (self.plate_location[0]*15 + 100, self.plate_location[1]*15 + 75)
            radius = self.plate_xys[0][0]*15
            pygame.draw.circle(temp_surface, self.plate_color, center, radius)

        # Blit the shape onto the screen with transparency
        screen.blit(temp_surface, (0, 0))

        # Draw the tiny move button (opaque)
        pygame.draw.rect(screen, (0, 0, 0), self.button_rect)

    def xy_to_coordinates(self):
        for i in range(len(self.plate_xys)):
            self.plate_coordinates[i] = (
                (self.plate_xys[i][0] + self.plate_location[0]) * 15 + 100,
                (self.plate_xys[i][1] + self.plate_location[1]) * 15 + 75
            )
        self.update_button_position()

    def update_button_position(self):
        x = self.plate_location[0] * 15 + 100 - 5
        y = self.plate_location[1] * 15 + 75 - 5
        self.button_rect.topleft = (x, y)

class Board:
    def __init__(self):
        self.le = 40
        self.he = 30
        self.plates = []
        
        self.boardStartX = 100
        self.boardStartY = 75
        self.width = 600
        self.height = 450
        self.cellWidth = 15

    def draw_grid(self):
        for x in range(41):
            pygame.draw.line(screen, LIGHT_GRID, (self.boardStartX + x*self.cellWidth, self.boardStartY), (self.boardStartX + x*self.cellWidth, self.height + self.boardStartY), 1)
        for y in range(31):
            pygame.draw.line(screen, LIGHT_GRID, (self.boardStartX, self.boardStartY + y*self.cellWidth), (self.boardStartX + self.width, self.boardStartY + y*self.cellWidth), 1)

    def add_plate(self, plate):
        self.plates.append(plate)

    def draw_board(self, screen):
        for plate in self.plates:
            plate.draw_plate(screen)

    def get_plate_at(self, pos):
        for plate in reversed(self.plates):
            if plate.button_rect.collidepoint(pos):
                return plate
        return None

    def bring_to_top(self, plate):
        if plate in self.plates:
            self.plates.remove(plate)
            self.plates.append(plate)

class IsoBoard: 
    startX = 160
    startY = 180

    def __init__(self, plates):
        self.plates = plates
        self.isoPlates = self.compute_iso_plates(plates, scale=1, offset=(IsoBoard.startX, IsoBoard.startY))

    @staticmethod
    def compute_iso_plates(plates, scale=1, offset=(0, 0)):
        """Shared method to generate isometric plate data"""
        def conversion(x, y):
            ex = scale * (x + 5 * x) + offset[0]
            ey = scale * (y + 5 * y + 2 * x) + offset[1]
            return (ex, ey)

        isoPlates = []

        for plate in plates:
            if plate.plate_type == 1:
                isoP = []
                for (x, y) in plate.plate_xys:
                    ex = plate.plate_location[0] + x
                    ey = plate.plate_location[1] + y
                    isoP.append(conversion(ex, ey))
                isoPlates.append((1, plate.plate_color, isoP))
            elif plate.plate_type == 2:
                cx, cy = plate.plate_location
                radius = plate.plate_xys[0][0]

                A = conversion(cx - radius, cy - radius)
                B = conversion(cx + radius, cy - radius)
                C = conversion(cx - radius, cy + radius)
                D = conversion(cx + radius, cy + radius)

                def bilinear_map(u, v):
                    x = (1 - u) * (1 - v) * A[0] + u * (1 - v) * B[0] + (1 - u) * v * C[0] + u * v * D[0]
                    y = (1 - u) * (1 - v) * A[1] + u * (1 - v) * B[1] + (1 - u) * v * C[1] + u * v * D[1]
                    return (x, y)

                points = []
                resolution = 60
                for i in range(resolution):
                    angle = 2 * math.pi * i / resolution
                    u = 0.5 + 0.5 * math.cos(angle)
                    v = 0.5 + 0.5 * math.sin(angle)
                    points.append(bilinear_map(u, v))

                isoPlates.append((2, plate.plate_color, points))

        return isoPlates

    def draw_board(self, screen, blit_position=(0, 0)):
        width, height = screen.get_size()
        blended_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        blended_array = numpy.zeros((width, height, 3), dtype=numpy.uint16)

        for plate in self.isoPlates:
            shape_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(shape_surface, plate[1], plate[2])
            shape_array = pygame.surfarray.pixels3d(shape_surface)
            blended_array += shape_array

        numpy.clip(blended_array, 0, 255, out=blended_array)
        final_surface = pygame.surfarray.make_surface(blended_array.astype(numpy.uint8))
        final_surface.set_alpha(255)
        
        # Only draw to the screen at the specified position
        screen.blit(final_surface, blit_position)

    def draw_grid(self):
        for x in range(0, 41, 5):
            pygame.draw.line(screen, LIGHT_GRID, self.conversion(x, 0), self.conversion(x, 30), 1)
        for y in range(0, 31, 5):
            pygame.draw.line(screen, LIGHT_GRID, self.conversion(0, y), self.conversion(40, y), 1)

    @staticmethod
    def conversion(x, y):
        return IsoBoard.compute_conversion(x, y, 1, (IsoBoard.startX, IsoBoard.startY))

    @staticmethod
    def compute_conversion(x, y, scale, offset):
        ex = scale * (x + 5 * x) + offset[0]
        ey = scale * (y + 5 * y + 2 * x) + offset[1]
        return (ex, ey)

class IsoProjection:
    def __init__(self, plates, scale=2, offset=(500, 100)):
        self.isoPlates = IsoBoard.compute_iso_plates(plates, scale=scale, offset=offset)
        self.scale = scale
        self.offset = offset

    def draw_projection(self, screen, blit_position=(500, 0)):
        width, height = screen.get_size()
        blended_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        blended_array = numpy.zeros((width, height, 3), dtype=numpy.uint16)

        for plate in self.isoPlates:
            shape_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(shape_surface, plate[1], plate[2])
            shape_array = pygame.surfarray.pixels3d(shape_surface)
            blended_array += shape_array

        numpy.clip(blended_array, 0, 255, out=blended_array)
        final_surface = pygame.surfarray.make_surface(blended_array.astype(numpy.uint8))
        final_surface.set_alpha(255)
        
        screen.blit(final_surface, blit_position)


# class IsoBoard: 
#     startX = 160
#     startY = 180
#     def __init__(self, plates):
#         self.plates = plates
#         self.isoPlates = [] 
#         # (type, color, locations)
#         # (type, color, locations )

#         for plate in self.plates:
#             if plate.plate_type == 1:
#                 isoP = []
#                 for (x, y) in plate.plate_xys:
#                     ex = plate.plate_location[0] + x
#                     ey = plate.plate_location[1] + y
#                     isoP.append(IsoBoard.conversion(ex, ey))
#                 self.isoPlates.append((1, plate.plate_color, isoP))
#             elif plate.plate_type == 2:
#                 exy = (plate.plate_location[0], plate.plate_location[1])
#                 #radiusx = (plate.plate_xys[0][0] * 10, plate.plate_xys[0][0] * 10)
#                 # self.isoPlates.append((2, plate.plate_color, [exy, radiusx]))

#                 radius = plate.plate_xys[0][0]  # Using x radius (assumed uniform)

#                 # Define the parallelogram around the circle
#                 # Matches your previous pattern: A, B, C, D
#                 A = IsoBoard.conversion(exy[0] - radius, exy[1] - radius)
#                 B = IsoBoard.conversion(exy[0] + radius, exy[1] - radius)
#                 C = IsoBoard.conversion(exy[0] - radius, exy[1] + radius)
#                 D = IsoBoard.conversion(exy[0] + radius, exy[1] + radius)

#                 def bilinear_map(u, v, A, B, C, D):
#                     x = (1 - u) * (1 - v) * A[0] + u * (1 - v) * B[0] + (1 - u) * v * C[0] + u * v * D[0]
#                     y = (1 - u) * (1 - v) * A[1] + u * (1 - v) * B[1] + (1 - u) * v * C[1] + u * v * D[1]
#                     return (x, y)

#                 # Generate circle points in normalized space
#                 points = []
#                 resolution = 60
#                 for i in range(resolution):
#                     angle = 2 * math.pi * i / resolution
#                     u = 0.5 + 0.5 * math.cos(angle)
#                     v = 0.5 + 0.5 * math.sin(angle)
#                     point = bilinear_map(u, v, A, B, C, D)
#                     points.append(point)
#                 self.isoPlates.append((2, plate.plate_color, points))

#                 print(points)
                

    def draw_board(self, screen):
        width, height = screen.get_size()
        
        # Create blank surface and NumPy array for blending
        blended_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        blended_array = numpy.zeros((width, height, 3), dtype=numpy.uint16)  # Use 16-bit to prevent overflow

        for plate in self.isoPlates:
            # Draw each plate on a temp surface
            shape_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(shape_surface, plate[1], plate[2])

            # Convert surface to NumPy array (RGB only)
            shape_array = pygame.surfarray.pixels3d(shape_surface)

            # Add RGB values to accumulator (clip later)
            blended_array += shape_array

        # Clip values to max 255 and convert to 8-bit
        numpy.clip(blended_array, 0, 255, out=blended_array)
        blended_array = blended_array.astype(numpy.uint8)

        # Copy final RGB to surface
        final_surface = pygame.surfarray.make_surface(blended_array)

        # Add alpha channel (optional: you can skip if full opaque)
        final_surface.set_alpha(255)
        screen.blit(final_surface, (0, 0))


            # elif plate[0] == 2:
            #     pygame.draw.ellipse(screen, plate[1], (plate[2][0][0], plate[2][0][1], plate[2][1][0], plate[2][1][1]))
                

    def draw_grid(self):
        for x in range(0, 41, 5):
            pygame.draw.line(screen, LIGHT_GRID, (IsoBoard.conversion(x, 0)), (IsoBoard.conversion(x, 30)), 1)
        for y in range(0, 31, 5):
            pygame.draw.line(screen, LIGHT_GRID, (IsoBoard.conversion(0, y)), (IsoBoard.conversion(40, y)), 1)

    @staticmethod
    def conversion(x, y):
        ex = x + 5 * x + IsoBoard.startX
        ey = y + 5 * y + 2 * x + IsoBoard.startY
        return (ex, ey)


pygame.init()

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luminara: Draw Shape Demo")

# Semi-transparent Colors
LIGHT_GRID = (230, 230, 230, 255)
WHITE  = (255, 255, 255, 255)
GRAY   = (220, 220, 220, 160)
REDD    = (255, 0, 0, 160)
GREEND  = (0, 255, 0, 160)
BLUED   = (0, 0, 255, 160)

# Draw Color Selection Buttons
color_buttons = [(REDD, pygame.Rect(720, 150, 50, 50)),
                  (GREEND, pygame.Rect(720, 250, 50, 50)),
                  (BLUED, pygame.Rect(720, 350, 50, 50))]

selected_color = None

def draw_color_buttons():
    for color, rect in color_buttons:
        pygame.draw.rect(screen, color, rect)

board = Board()
plate1 = Plates(1, GRAY, (0, 0), [(0, 0), (10, 0), (10, 10), (0, 10)])
plate2 = Plates(1, GRAY, (20, 20), [(0, 0), (10, 0), (10, 10), (0, 10)])
plate3 = Plates(2, GRAY, (15, 15), [(5, 5)])
board.add_plate(plate1)
board.add_plate(plate2)
board.add_plate(plate3)

selected_plate = None

# New button for toggling views
toggle_button = pygame.Rect(30, 30, 120, 40)
FONT = pygame.font.SysFont(None, 24)

# Start in 2D view
show_isometric = False


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a color button is clicked
            if toggle_button.collidepoint(event.pos):
                show_isometric = not show_isometric

            for color, rect in color_buttons:
                if rect.collidepoint(event.pos):
                    selected_color = color
                    break
            else:
                # If no color is selected, check for a plate
                selected_plate = board.get_plate_at(event.pos)
                if selected_plate:
                    if selected_color:
                        selected_plate.plate_color = selected_color
                        selected_color = None
                    else:
                        selected_plate.dragging = True
                        board.bring_to_top(selected_plate)

        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_plate:
                # Snap to nearest grid
                x = round((event.pos[0] - 100) / 15)
                y = round((event.pos[1] - 75) / 15)
                selected_plate.plate_location = (x, y)
                selected_plate.xy_to_coordinates()
                selected_plate.dragging = False
                selected_plate = None

        elif event.type == pygame.MOUSEMOTION and selected_plate and selected_plate.dragging:
            # Update position while dragging
            x = (event.pos[0] - 100) / 15
            y = (event.pos[1] - 75) / 15
            selected_plate.plate_location = (x, y)
            selected_plate.xy_to_coordinates()

    # Draw toggle button
    screen.fill(WHITE)

    if show_isometric:
        isoBoard = IsoBoard(board.plates)
        isoProjection = IsoProjection(board.plates, scale=2, offset=(-100, 50))
        isoBoard.draw_board(screen)      # Draw plates
        isoBoard.draw_grid()             # Draw grid on top
        isoProjection.draw_projection(screen, blit_position=(420, 0))
    else:
        board.draw_grid()                # Draw grid
        board.draw_board(screen)         # Draw plates
        draw_color_buttons()            # Optional color buttons

    # Draw toggle button LAST so it's always visible
    pygame.draw.rect(screen, (180, 180, 180), toggle_button)
    button_text = FONT.render("Toggle View", True, (0, 0, 0))
    screen.blit(button_text, (toggle_button.x + 10, toggle_button.y + 10))

    pygame.display.flip()



pygame.quit()
sys.exit()
