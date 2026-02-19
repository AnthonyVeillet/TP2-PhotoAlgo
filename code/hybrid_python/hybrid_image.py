import skimage
import pathlib
import numpy as np

# Vérifier si on veux print dans le terminal des lignes de debug
#DEBUG = True
DEBUG = False

def hybrid_image(im1, im2, cutoff_low, cutoff_high):
    # you supply this code
    img1 = im1
    img2 = im2

    # Si image en gris
    if img1.ndim == 2 and img2.ndim == 2:
        # Mettre les images en float64 pour les calculs
        if img1.dtype != np.float64:
            img1 = img1.astype(np.float64)
        if img2.dtype != np.float64:
            img2 = img2.astype(np.float64)
        
        # Normaliser les images si elles sont dans l'intervalle [0, 255]
        if img1.max() > 1.0 and img1.max() <= 255.0:
            img1 = img1 / 255.0
        if img2.max() > 1.0 and img2.max() <= 255.0:
            img2 = img2 / 255.0

        print(f"Image 1 :\n    Shape {img1.shape}\n    Type {img1.dtype}")
        print(f"Image 2 :\n    Shape {img2.shape}\n    Type {img2.dtype}")

        # Calcul du filtre Gaussien (Low-pass)
        img1GaussLow = skimage.filters.gaussian(img1, cutoff_low)
        img2GaussLow = skimage.filters.gaussian(img2, cutoff_low)

        # Calcul du filtre Gaussien (High-pass)
        img1GaussHigh = img1 - skimage.filters.gaussian(img1, cutoff_high)
        img2GaussHigh = img2 - skimage.filters.gaussian(img2, cutoff_high)

        if DEBUG:
            print(f"Valeur max filtre Gaussien img1GaussLow: {img1GaussLow.max()}, Min: {img1GaussLow.min()}")
            print(f"Valeur max filtre Gaussien img2GaussLow: {img2GaussLow.max()}, Min: {img2GaussLow.min()}")
            print(f"Valeur max filtre Gaussien img2GaussHigh: {img2GaussHigh.max()}, Min: {img2GaussHigh.min()}")
            print(f"Valeur max filtre Gaussien img1GaussHigh: {img1GaussHigh.max()}, Min: {img1GaussHigh.min()}")

        # Combiner les images Low-Pass et High-Pass
        img1Low_2High = img1GaussLow + img2GaussHigh
        img1High_2Low = img1GaussHigh + img2GaussLow

        # Normaliser les images pour les mettre dans l'intervalle [0, 255]
        img1Low_2High_clip255 = np.clip(img1Low_2High, 0, 1) * 255.0
        img1High_2Low_clip255 = np.clip(img1High_2Low, 0, 1) * 255.0

        # Convertir les images en uint8
        img1Low_2High_uft8 = img1Low_2High_clip255.astype(np.uint8)
        img1High_2Low_uft8 = img1High_2Low_clip255.astype(np.uint8)

    # Si image de couleur
    elif img1.ndim == 3 and img2.ndim == 3:
        # Mettre les images en float64 pour les calculs
        if img1.dtype != np.float64:
            img1 = img1.astype(np.float64)
        if img2.dtype != np.float64:
            img2 = img2.astype(np.float64)
        
        # Normaliser les images si elles sont dans l'intervalle [0, 255]
        if img1.max() > 1.0 and img1.max() <= 255.0:
            img1 = img1 / 255.0
        if img2.max() > 1.0 and img2.max() <= 255.0:
            img2 = img2 / 255.0
        
        # Si l'image a un canal alpha (transparance), le mettre dans une variable et s'assurer qu'il est dans l'intervalle [0, 255]
        alpha_img1 = None
        alpha_img2 = None
        
        if img1.shape[2] == 4:
            alpha_img1 = img1[:, :, 3]
            img1 = img1[:, :, 0:3]
            if alpha_img1.max() > 0.0 and alpha_img1.max() <= 1.0:
                alpha_img1 = alpha_img1 * 255.0
            alpha_img1 = np.clip(alpha_img1, 0, 255).astype(np.uint8)

        if img2.shape[2] == 4:
            alpha_img2 = img2[:, :, 3]
            img2 = img2[:, :, 0:3]
            if alpha_img2.max() > 0.0 and alpha_img2.max() <= 1.0:
                alpha_img2 = alpha_img2 * 255.0
            alpha_img2 = np.clip(alpha_img2, 0, 255).astype(np.uint8)


        # Séparer les composantes de couleur
        r_img1, g_img1, b_img1 = img1[:, :, 0], img1[:, :, 1], img1[:, :, 2]
        r_img2, g_img2, b_img2 = img2[:, :, 0], img2[:, :, 1], img2[:, :, 2]

        print(f"Image 1 :\n    Shape {img1.shape}\n    Type {img1.dtype}")
        print(f"Image 2 :\n    Shape {img2.shape}\n    Type {img2.dtype}")

        # Calcul du filtre Gaussien (Low-pass)
        img1GaussLow = skimage.filters.gaussian(img1, cutoff_low)
        img2GaussLow = skimage.filters.gaussian(img2, cutoff_low)

        # Calcul du filtre Gaussien (Low-pass) pour chaque composante de couleur
        r_img1GaussLow = skimage.filters.gaussian(r_img1, cutoff_low)
        r_img2GaussLow = skimage.filters.gaussian(r_img2, cutoff_low)
        g_img1GaussLow = skimage.filters.gaussian(g_img1, cutoff_low)
        g_img2GaussLow = skimage.filters.gaussian(g_img2, cutoff_low)
        b_img1GaussLow = skimage.filters.gaussian(b_img1, cutoff_low)
        b_img2GaussLow = skimage.filters.gaussian(b_img2, cutoff_low)

        # Calcul du filtre Gaussien (High-pass)
        img1GaussHigh = img1 - skimage.filters.gaussian(img1, cutoff_high)
        img2GaussHigh = img2 - skimage.filters.gaussian(img2, cutoff_high)

        # Calcul du filtre Gaussien (High-pass) pour chaque composante de couleur
        r_img1GaussHigh = r_img1 - skimage.filters.gaussian(r_img1, cutoff_high)
        r_img2GaussHigh = r_img2 - skimage.filters.gaussian(r_img2, cutoff_high)
        g_img1GaussHigh = g_img1 - skimage.filters.gaussian(g_img1, cutoff_high)
        g_img2GaussHigh = g_img2 - skimage.filters.gaussian(g_img2, cutoff_high)
        b_img1GaussHigh = b_img1 - skimage.filters.gaussian(b_img1, cutoff_high)
        b_img2GaussHigh = b_img2 - skimage.filters.gaussian(b_img2, cutoff_high)

        if DEBUG:
            print(f"Valeur max filtre Gaussien img1GaussLow: {img1GaussLow.max()}, Min: {img1GaussLow.min()}")
            print(f"Valeur max filtre Gaussien img2GaussLow: {img2GaussLow.max()}, Min: {img2GaussLow.min()}")
            print(f"Valeur max filtre Gaussien img2GaussHigh: {img2GaussHigh.max()}, Min: {img2GaussHigh.min()}")
            print(f"Valeur max filtre Gaussien img1GaussHigh: {img1GaussHigh.max()}, Min: {img1GaussHigh.min()}")

        # Combiner les images Low-Pass et High-Pass
        r_img1Low_2High = r_img1GaussLow + r_img2GaussHigh
        r_img1High_2Low = r_img1GaussHigh + r_img2GaussLow
        g_img1Low_2High = g_img1GaussLow + g_img2GaussHigh
        g_img1High_2Low = g_img1GaussHigh + g_img2GaussLow
        b_img1Low_2High = b_img1GaussLow + b_img2GaussHigh
        b_img1High_2Low = b_img1GaussHigh + b_img2GaussLow

        # Faire l'image de couleur (image 1 Low-Pass + image 2 High-Pass)
        img1Low_2High = (np.stack((r_img1Low_2High, g_img1Low_2High, b_img1Low_2High), axis=2))

        # Faire l'image de couleur (image 1 High-Pass + image 2 Low-Pass)
        img1High_2Low = (np.stack((r_img1High_2Low, g_img1High_2Low, b_img1High_2Low), axis=2))

        # Normaliser les images pour les mettre dans l'intervalle [0, 255]
        img1Low_2High_clip255 = np.clip(img1Low_2High, 0, 1) * 255.0
        img1High_2Low_clip255 = np.clip(img1High_2Low, 0, 1) * 255.0

        # Convertir les images en uint8
        img1Low_2High_uft8 = img1Low_2High_clip255.astype(np.uint8)
        img1High_2Low_uft8 = img1High_2Low_clip255.astype(np.uint8)

        # Remettre le canal alpha si les images originales en avaient un
        if alpha_img1 is not None:
            img1Low_2High_uft8 = np.dstack((img1Low_2High_uft8, alpha_img1))
            img1High_2Low_uft8 = np.dstack((img1High_2Low_uft8, alpha_img1))
        if alpha_img2 is not None:
            img1Low_2High_uft8 = np.dstack((img1Low_2High_uft8, alpha_img2))
            img1High_2Low_uft8 = np.dstack((img1High_2Low_uft8, alpha_img2))

    else:
        raise ValueError("Les images doivent être soit en gris (2D) soit en couleur (3D)")

    return img1Low_2High_uft8
