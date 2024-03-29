import pygame
from Fonctions import *
import os


class Bouton(pygame.sprite.Sprite):
    def __init__(self, position, image_normal=None, action=None, difficulte=None, boutons_music_file=None):
        super().__init__()

        self.image_normal = None
        self.image_hover = None  # Ajoutez cette ligne pour éviter une erreur dans clic()

        if difficulte is not None:
            self.corruption = lire_valeur(f'{difficulte}')  # 0 ou 1
            self.difficulte = difficulte

            if self.corruption == 0:
                self.image_normal = pygame.image.load(
                    f'assets/menus/selection_difficulte_menu/assets_corrompu/Bouton_{difficulte}_Normal.png').convert_alpha()
                self.image_hover = pygame.image.load(
                    f'assets/menus/selection_difficulte_menu/assets_corrompu/Bouton_{difficulte}_Hover.png').convert_alpha()
            elif self.corruption == 1:
                pass
        else:
            self.image_normal = pygame.image.load(image_normal).convert_alpha()

            chemin_image_hover = image_normal[:-10] + "Hover.png"
            if os.path.exists(chemin_image_hover):
                self.image_hover = pygame.image.load(chemin_image_hover).convert_alpha()

        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=position)
        self.mask = pygame.mask.from_surface(self.image)

        # Fonction à exécuter lors du clic sur le bouton
        self.action = action

        # Charger le son pour les boutons
        if boutons_music_file is not None:
            self.boutons_sound = pygame.mixer.Sound(boutons_music_file)
            self.son_joue = False

    def est_pixel_non_transparent(self, x, y):
        return self.mask.get_at((x - self.rect.x, y - self.rect.y))

    def update_bouton(self):
        # Changer l'image lorsque la souris survole le bouton
        coord_x, coord_y = pygame.mouse.get_pos()
        if self.rect.collidepoint(coord_x, coord_y) and self.est_pixel_non_transparent(coord_x, coord_y):
            if self.image_hover:
                self.image = self.image_hover
                # Jouer le son des boutons
                if hasattr(self, 'boutons_sound') and self.son_joue == False:
                    self.boutons_sound.play()
                    self.son_joue = True
        else:
            self.image = self.image_normal
            self.son_joue = False

    def clic(self):
        # Exécuter l'action associée au clic sur le bouton
        if self.action:
            self.action()
            self.son_joue = False

class Pieces_mouvement:
    def est_pixel_non_transparent(self, x, y):
        return self.mask.get_at((x - self.rect.x, y - self.rect.y))

    def deplacer(self, nouvelle_x, nouvelle_y, liste_axe_coord, liste_pieces):
        if self.type != 15:
            if self not in self.pieces_en_collision:
                self.pieces_en_collision.append(self)
            self.rect.x, self.rect.y = self.ajuster_deplacement_diagonal(
                self.rect.x, self.rect.y, nouvelle_x, nouvelle_y, liste_axe_coord, liste_pieces
            )
            self.liste_positions = self.calculer_positions()

    def detecter_collision(self, liste_pieces, tolerance=150):
        for autre_piece in liste_pieces:
            if autre_piece != self:
                # Vérifiez si les rectangles englobants se chevauchent
                if self.rect.colliderect(autre_piece.rect):
                    # Si les rectangles se chevauchent, vérifiez la collision par masque avec tolérance
                    offset = (autre_piece.rect.x - self.rect.x, autre_piece.rect.y - self.rect.y)
                    overlap_area = self.mask.overlap_area(autre_piece.mask, offset)
                    if overlap_area > tolerance:
                        if autre_piece.type != 15:
                            if autre_piece not in self.pieces_en_collision:
                                self.pieces_en_collision.append(autre_piece)
                            return True
                        else:
                            return True
        return None  # Aucune collision détectée

    def autoriser_deplacement(self, x, y, liste_segments, liste_pieces, limite_x_min, limite_x_max, limite_y_min,
                              limite_y_max,
                              ecart_maximal=10):

        if self.detecter_collision(liste_pieces):
            return False

        for position in self.liste_positions:
            pos_x, pos_y = position
            if not (limite_x_min <= pos_x <= limite_x_max and limite_y_min <= pos_y <= limite_y_max):
                return False

        for segment in liste_segments:
            x1, y1 = segment[0]
            x2, y2 = segment[1]
            # Calcul de la distance entre le point et le segment
            distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5

            if distance <= ecart_maximal and limite_x_min <= x <= limite_x_max and limite_y_min <= y <= limite_y_max:
                return True
        return False

    def ajuster_deplacement_diagonal(self, x, y, nouvelle_x, nouvelle_y, liste_axe_coord, liste_pieces):
        diff_x = nouvelle_x - x
        diff_y = nouvelle_y - y

        if abs(diff_x) - 60 < abs(diff_y) < abs(diff_x) + 60:
            if abs(diff_x) > 30 and abs(diff_y) > 30:
                facteur_interpolation = 0.2
                new_x = x + facteur_interpolation * diff_x
                new_y = y + facteur_interpolation * (abs(diff_x) if diff_y > 0 else -abs(diff_x))

                # Vérification si la nouvelle position est sur un segment:
                if self.autoriser_deplacement(new_x, new_y, liste_axe_coord, liste_pieces, 600, 1194, 100, 694):
                    return int(new_x), int(new_y)
        return x, y

    def force_position(self):
        distances = []
        for pos_x, pos_y_list in Piece.pos_possible.items():
            for pos_y in pos_y_list:
                distances.append(((pos_x - self.rect.x) ** 2 + (pos_y[1] - self.rect.y) ** 2) ** 0.5)

        indice_position_proche = distances.index(min(distances))
        nouvelle_position = Piece.pos_possible_list[indice_position_proche]
        self.rect.x, self.rect.y = nouvelle_position

        self.liste_positions = self.calculer_positions()
        self.pieces_en_collision = []

    def obtenir_piece_collision(self):
        return self.pieces_en_collision


class Piece(pygame.sprite.Sprite, Pieces_mouvement):
    # Positions possibles pour les pièces
    pos_possible = {
        600: [(600, 100), (600, 298), (600, 496), (600, 694)],
        699: [(699, 199), (699, 397), (699, 595)],
        798: [(798, 100), (798, 298), (798, 496), (798, 694)],
        897: [(897, 199), (897, 397), (897, 595)],
        996: [(996, 100), (996, 298), (996, 496), (996, 694)],
        1095: [(1095, 199), (1095, 397), (1095, 595)],
        1194: [(1194, 100), (1194, 298), (1194, 496), (1194, 694)]
    }

    # Liste des positions possibles
    pos_possible_list = [pos for positions in pos_possible.values() for pos in positions]

    def __init__(self, x, y, type_piece):
        super().__init__()

        self.type = type_piece

        self.charger_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        # Nouvelle liste pour les positions occupées par la pièce
        self.liste_positions = self.calculer_positions()

        self.pieces_en_collision = []

    def charger_image(self):
        chemin_image = f"assets/Pieces/{'Virus' if self.type == 'Virus' else f'Piece [{self.type}]'}.png"
        self.image = pygame.image.load(chemin_image).convert_alpha()


    def calculer_positions(self):
        # Calculer les positions occupées par la pièce en fonction de son type
        if self.type == 'Virus':
            return [(self.rect.x, self.rect.y), (self.rect.x + 99, self.rect.y + 99)]
        #if self.type == 1:#problème
            #return [(self.rect.x + 99, self.rect.y), (self.rect.x, self.rect.y + 99)]
        if self.type == 2:
            return [(self.rect.x, self.rect.y), (self.rect.x + 99, self.rect.y + 99)]
        elif self.type == 3:
            return [(self.rect.x, self.rect.y), (self.rect.x + 198, self.rect.y)]
        elif self.type == 4:
            return [(self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 198)]
        elif self.type == 5:
            return [(self.rect.x, self.rect.y), (self.rect.x + 198, self.rect.y)]
        elif self.type == 6:
            return [(self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 198)]
        #elif self.type == 7:  #problème
            #return [(self.rect.x + 99, self.rect.y), (self.rect.x, self.rect.y + 99), (self.rect.x + 198, self.rect.y + 99)]
        elif self.type == 8:
            return [(self.rect.x, self.rect.y), (self.rect.x + 198, self.rect.y), (self.rect.x + 99, self.rect.y + 99)]
        #elif self.type == 9:  #problème
            #return [(self.rect.x + 99, self.rect.y), (self.rect.x, self.rect.y + 99), (self.rect.x + 99, self.rect.y + 198)]
        elif self.type == 10:
            return [(self.rect.x, self.rect.y), (self.rect.x + 99, self.rect.y + 99), (self.rect.x, self.rect.y + 198)]
        elif self.type == 11:
            return [(self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 198), (self.rect.x + 198, self.rect.y + 198)]
        elif self.type == 12:
            return [(self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 198), (self.rect.x + 198, self.rect.y)]
        elif self.type == 13:
            return [(self.rect.x, self.rect.y), (self.rect.x + 198, self.rect.y + 198), (self.rect.x + 198, self.rect.y)]
        #elif self.type == 14:  #problème
            #return [(self.rect.x, self.rect.y + 198), (self.rect.x + 198, self.rect.y + 198), (self.rect.x + 198, self.rect.y)]
        elif self.type == 15:
            return [(self.rect.x, self.rect.y)]
        elif self.type == 16:
            return [(self.rect.x, self.rect.y), (self.rect.x + 99, self.rect.y + 99), (self.rect.x + 99, self.rect.y + 297)]
        #elif self.type == 17: #problème
            #return [(self.rect.x + 99, self.rect.y), (self.rect.x + 99, self.rect.y + 198), (self.rect.x, self.rect.y + 297)]
        #elif self.type == 18: #problème
            #return [(self.rect.x + 99, self.rect.y), (self.rect.x, self.rect.y + 99), (self.rect.x, self.rect.y + 297)]
        elif self.type == 19:
            return [(self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 198), (self.rect.x, self.rect.y + 297)]
        elif self.type == 20:
            return [(self.rect.x, self.rect.y), (self.rect.x, self.rect.y + 198), (self.rect.x, self.rect.y + 396)]
        elif self.type == 21:
            return [(self.rect.x, self.rect.y), (self.rect.x + 198, self.rect.y), (self.rect.x + 396, self.rect.y)]

class Piece_groupe(pygame.sprite.Sprite, Pieces_mouvement):
    pos_possible = {
        600: [(600, 100), (600, 298), (600, 496), (600, 694)],
        699: [(699, 199), (699, 397), (699, 595)],
        798: [(798, 100), (798, 298), (798, 496), (798, 694)],
        897: [(897, 199), (897, 397), (897, 595)],
        996: [(996, 100), (996, 298), (996, 496), (996, 694)],
        1095: [(1095, 199), (1095, 397), (1095, 595)],
        1194: [(1194, 100), (1194, 298), (1194, 496), (1194, 694)]
    }
    def __init__(self, liste_pieces):
        super().__init__()

        # Initialisation des attributs du groupe
        self.liste_pieces = liste_pieces

        self.liste_piece_type = []
        for element in liste_pieces:
            self.liste_piece_type.append(element.type)

        self.rect = self.calculer_rect()
        self.image = self.calculer_image()
        self.mask = pygame.mask.from_surface(self.image)
        self.type = 'groupe_pieces'

        self.coord_initiale = None

        self.liste_indexe = []
        self.liste_positions = self.calculer_positions()

        self.pieces_en_collision = []


    def calculer_rect(self):
        # Calcul du rectangle englobant toutes les pièces
        left = min(piece.rect.left for piece in self.liste_pieces)
        top = min(piece.rect.top for piece in self.liste_pieces)
        right = max(piece.rect.right for piece in self.liste_pieces)
        bottom = max(piece.rect.bottom for piece in self.liste_pieces)

        width = right - left
        height = bottom - top

        return pygame.Rect(left, top, width, height)

    def calculer_image(self):
        # Création d'une surface englobant toutes les images
        width, height = self.rect.width, self.rect.height
        image = pygame.Surface((width, height), pygame.SRCALPHA)

        for piece in self.liste_pieces:
           image.blit(piece.image, (piece.rect.left - self.rect.left, piece.rect.top - self.rect.top))

        return image

    def calculer_positions(self):
        # Calculer les positions occupées par le groupe
        positions_groupe = []

        if self.coord_initiale:
            decalage_x = self.rect.x - self.coord_initiale[0]
            decalage_y = self.rect.y - self.coord_initiale[1]

            for position in self.liste_positions:
                if position:
                    nouvelle_position = (position[0] + decalage_x, position[1] + decalage_y)
                    positions_groupe.append(nouvelle_position)

            self.coord_initiale = (self.rect.x, self.rect.y)

        else:
            for piece in self.liste_pieces:
                position_piece = piece.calculer_positions()
                self.liste_indexe.append(len(position_piece))
                positions_groupe.extend(position_piece)
                self.coord_initiale = (self.rect.x, self.rect.y)


        return positions_groupe

    def obtenir_liste_groupe_type(self):
        return self.liste_piece_type