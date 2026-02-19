import skimage
import pathlib
import numpy as np
import sys
import matplotlib.pyplot as plt


# Vérifier si on veux print dans le terminal des lignes de debug
#DEBUG = True
DEBUG = False

# Vérifier si on veut faire plein de png pour faire un vidéo dans Blender
VIDEO = False
#VIDEO = True

# Insérer les chemins vers les images
img_1_path = pathlib.Path("web/images/data/Iris.png")
img_2_path = pathlib.Path("web/images/data/Optimus.png")

# Vérifier que les fichiers existent
for p in (img_1_path, img_2_path):
    if not p.is_file():
        print(f"ERREUR: fichier introuvable -> {p.resolve()}")
        sys.exit(1)   # stop le programme avec code d’erreur

img_1_name = img_1_path.stem
img_2_name = img_2_path.stem

img_1_uft8 = skimage.io.imread(img_1_path)
img_2_uft8 = skimage.io.imread(img_2_path)

# Convertir les images en float64 pour les calculs
img_1 = img_1_uft8.astype(np.float64) / 255.0
img_2 = img_2_uft8.astype(np.float64) / 255.0

alpha_img_1 = None
alpha_img_2 = None

# Si l'image a un canal alpha (transparance), le supprimer
if img_1.shape[2] == 4:
    alpha_img_1 = img_1_uft8[:, :, 3]
    img_1 = img_1[:, :, 0: 3]
if img_2.shape[2] == 4:
    alpha_img_2 = img_2_uft8[:, :, 3]
    img_2 = img_2[:, :, 0: 3]

# Séparer les composantes de couleur
r_img_1, g_img_1, b_img_1 = img_1[:, :, 0], img_1[:, :, 1], img_1[:, :, 2]
r_img_2, g_img_2, b_img_2 = img_2[:, :, 0], img_2[:, :, 1], img_2[:, :, 2]

print(f"Image 1 {img_1_name} :\n    Shape {img_1.shape}\n    Type {img_1.dtype}")
print(f"Image 2 {img_2_name} :\n    Shape {img_2.shape}\n    Type {img_2.dtype}")

def filtre_Gauss(image, sig):
    # Calcul du filtre Gaussien
    img = skimage.filters.gaussian(image, sig)
    
    if DEBUG:
        print(f"Valeur max filtre Gaussien: {img.max()}, Min: {img.min()}")
    return img

def accentuation(image, sigma):
    # Appliquer le filtre Gaussien à l'image
    img_flou = filtre_Gauss(image, sigma)
    details = image - img_flou
    img_sharp = image + sigma*details

    if DEBUG:
        print(f"Valeur max sharpening: {img_sharp.max()}, Min: {img_sharp.min()}")
    return img_sharp

# Appliquer l'accentuation à chaque composante de couleur
listNoms = ['1', '2']
#listCouleurs = ['r', 'g', 'b']
sigma = [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]

if VIDEO:
    sigma = list(np.arange(0, 5.0, 0.01))

images_1 = []
images_2 = []

count = 0

for j in sigma:
    count += 1
    for i in listNoms:

        img_name = eval(f"img_{i}_name")

        if VIDEO == False:
            print(f"\n-------------{img_name}-------------")
        
        img_r = accentuation(eval(f"r_img_{i}"), j)
        img_g = accentuation(eval(f"g_img_{i}"), j)
        img_b = accentuation(eval(f"b_img_{i}"), j)
        img_sharp = (np.stack((img_r, img_g, img_b), axis=2)) * 255.0

        img_sharp_uft8 = np.clip(img_sharp, 0, 255).astype(np.uint8)

        if eval(f"alpha_img_{i}") is not None:
            img_sharp_uft8 = np.dstack((img_sharp_uft8, eval(f"alpha_img_{i}")))

        if DEBUG:
            print(f"Valeur max: {img_sharp_uft8.max()}, Min: {img_sharp_uft8.min()}")
            print(f"\nImage {i} {eval(f'img_{i}_name')} accentuée :\n    Shape {img_sharp_uft8.shape}\n    Type {img_sharp_uft8.dtype}")

        if VIDEO == True:
            # Sauvegarder l'image accentuée
            skimage.io.imsave(f"web/images/accentuation/video/{img_name}_sigma_{count}.png", img_sharp_uft8)

            img_path = pathlib.Path(f"web/images/accentuation/video/{img_name}_sigma_{count}.png")

        if VIDEO == False:
            # Sauvegarder l'image accentuée
            skimage.io.imsave(f"web/images/accentuation/{img_name}_sigma_{j}.png", img_sharp_uft8)

            img_path = pathlib.Path(f"web/images/accentuation/{img_name}_sigma_{j}.png")

            if img_path.exists():
                print(f"Image accentuée {img_name}_sigma_{j}.png sauvegardée avec succès.")
            else:
                print(f"Erreur lors de la sauvegarde de l'image accentuée {img_name}_sigma_{j}.png.")

            # Ajouter l'image accentuée à la liste pour l'affichage
            if i == '1':
                images_1.append(img_sharp_uft8)
            
            elif i == '2':
                images_2.append(img_sharp_uft8)


# Code fait par ChatGPT pour afficher les images accentuées
def save_sigma_montage(images, sigmas, out_path, title=None):
    """Sauvegarde un montage 1xN d'images, avec σ écrit sous chaque image."""
    n = len(sigmas)

    # Un peu plus haut pour laisser la place au texte plus gros
    fig, axes = plt.subplots(1, n, figsize=(4*n, 4.4))

    # si n==1, axes n'est pas itérable
    if n == 1:
        axes = [axes]

    for ax, s, im in zip(axes, sigmas, images):
        ax.imshow(im)
        ax.axis("off")
        ax.text(
            0.5, -0.07, f"σ = {s}",
            transform=ax.transAxes,
            ha="center", va="top",
            fontsize=26  # <-- plus gros
        )

    if title is not None:
        fig.suptitle(title)

    # Réduire l'espace entre sous-plots + marges
    fig.subplots_adjust(left=0.0, right=1.0, top=0.92, bottom=0.06, wspace=0.0)

    # Tight layout avec petit padding (optionnel mais aide)
    plt.tight_layout(pad=0.2)

    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

if VIDEO == False:
    save_sigma_montage(
        images_1, sigma,
        f"web/images/accentuation/montage_{img_1_name}.png",
        title=img_1_name
    )

    save_sigma_montage(
        images_2, sigma,
        f"web/images/accentuation/montage_{img_2_name}.png",
        title=img_2_name
    )
