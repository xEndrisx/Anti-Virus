import csv


def lire_csv(chemin):
    contenu = {}
    with open(chemin, newline='', encoding='utf-8') as fichier_csv:
        lecteur = csv.reader(fichier_csv, delimiter=';')
        next(lecteur)  # Ignorer l'en-tête du CSV

        for ligne in lecteur:
            # Vérifier que la ligne a suffisamment d'éléments
            if len(ligne) >= 6:
                difficulte = ligne[0]

                # Vérifier si la valeur de la colonne B (niveau) est vide
                niveau = int(ligne[1]) if ligne[1] else None

                pieces = [piece.strip(' "') for piece in ligne[2].split(',')]

                # Gérer les valeurs vides dans la colonne D (coordonnées)
                coord_piece = (
                    [tuple(map(int, coord.strip(' ()').split(','))) for coord in ligne[3].split('), (')]
                    if ligne[3] else None
                )

                # Gérer les valeurs None dans les colonnes E et F (chrono et score)
                chrono = str(ligne[4]) if ligne[4] is not None and ligne[4] != '' else None
                score = str(ligne[5]) if ligne[5] is not None and ligne[5] != '' else None

                # Remplacer les chaînes vides par None dans la colonne C
                pieces = None if all(piece == '' for piece in pieces) else pieces

                if difficulte in contenu:
                    contenu[difficulte].append([niveau, pieces, coord_piece, chrono, score])
                else:
                    contenu[difficulte] = [[niveau, pieces, coord_piece, chrono, score]]

    return contenu


def ecrire_csv(chemin, contenu):
    with open(chemin, mode='w', newline='', encoding='utf-8') as fichier_csv:
        ecrivain = csv.writer(fichier_csv, delimiter=';')

        # Écrire l'en-tête
        en_tete = ["difficulté", "niveau", "pieces", "coord_piece", "chrono", "score"]
        ecrivain.writerow(en_tete)

        # Écrire les données
        for difficulte, niveaux in contenu.items():
            for niveau in niveaux:
                ligne = [
                    difficulte,
                    str(niveau[0]) if niveau[0] is not None else '',  # Niveau
                    ', '.join(f'"{piece}"' for piece in niveau[1]) if niveau[1] else '',  # Pieces
                    ', '.join(f'({x}, {y})' for x, y in niveau[2]) if niveau[2] and all(niveau[2]) else '',  # coord_piece
                    str(niveau[3]) if niveau[3] is not None else '',  # Chrono
                    str(niveau[4]) if niveau[4] is not None else ''  # Score
                ]
                # Remplace les chaînes vides par None avant d'écrire dans le CSV
                ligne = [None if cellule == '' else cellule for cellule in ligne]
                ecrivain.writerow(ligne)

def lire_valeur(argument):
    with open('properties.txt', 'r', encoding='utf-8') as fichier:
        for ligne in fichier:
            if argument in ligne:
                # Trouvé la ligne avec l'argument, extraire la valeur
                valeur_str = ligne.split('=')[-1].strip()
                return int(valeur_str)

    # Si on ne trouve pas la ligne, retourner une valeur par défaut ou gérer l'erreur selon le cas
    return None