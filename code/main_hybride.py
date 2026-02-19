import os
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread, imsave
import skimage.filters
import numpy as np

HYBRID_DIR = Path(__file__).resolve().parent / "hybrid_python"
sys.path.insert(0, str(HYBRID_DIR))

from align_images import align_images
from crop_image import crop_image
from hybrid_image import hybrid_image

def crop_to_overlap(im1, im2, thr=0.0, pad=2):
    # Crop im1 et im2 à la zone où les deux ont des pixels valides (non-noirs).
    # Seuil pour considérer un pixel valide (0.0 ok si images float; sinon mets 1)
    # Petite marge pour éviter de crop trop serré

    a = im1.astype(np.float64)
    b = im2.astype(np.float64)

    # Masques de validité (en gris: a.ndim==2)
    if a.ndim == 2:
        m1 = a > thr
        m2 = b > thr
    else:
        # couleur valide si au moins 1 canal
        m1 = np.any(a > thr, axis=2)
        m2 = np.any(b > thr, axis=2)

    m = m1 & m2
    ys, xs = np.where(m)

    # Si jamais le masque est vide, on retourne tel quel
    if len(ys) == 0 or len(xs) == 0:
        return im1, im2

    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()

    # pad + clamp
    y0 = max(y0 - pad, 0)
    x0 = max(x0 - pad, 0)
    y1 = min(y1 + pad, im1.shape[0] - 1)
    x1 = min(x1 + pad, im1.shape[1] - 1)

    return im1[y0:y1+1, x0:x1+1], im2[y0:y1+1, x0:x1+1]

def mettre_float01(img):
    # Convertit en float [0,1] (accepte uint8 ou float)
    x = img.astype(np.float64, copy=False)
    if x.max() > 1.0:
        x = x / 255.0
    return np.clip(x, 0.0, 1.0)


def fft_log_amplitude(imageGris):
    # Amplitude log de la FFT2 (comme demandé)
    g = mettre_float01(imageGris)
    return np.log(np.abs(np.fft.fftshift(np.fft.fft2(g))) + 1e-8)


def save_amplitude_image(imageGris, out_path):
    # Sauvegarde une image (PNG) de l’amplitude log FFT2, normalisée pour affichage
    amp = fft_log_amplitude(imageGris)

    # normaliser pour sauvegarde (0..1) sinon c'est trop sombre/bright
    amin, amax = amp.min(), amp.max()
    if np.isclose(amax - amin, 0.0):
        amp_norm = np.zeros_like(amp)
    else:
        amp_norm = (amp - amin) / (amax - amin)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.imsave(str(out_path), amp_norm, cmap="gray")


def main():
    # Aller cherhcher les images dans le dossier "code/hybrid_python"
    img1_path = Path("code/hybrid_python/Albert_Einstein.png")
    img2_path = Path("code/hybrid_python/Marilyn_Monroe.png")

    out_dir = Path("web/images/hybrid")
    out_amp_dir = Path("web/images/hybrid/amplitude")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_amp_dir.mkdir(parents=True, exist_ok=True)

    # Lecture des images (grayscale comme le starter)
    im1 = imread(str(img1_path), pilmode="L")
    im2 = imread(str(img2_path), pilmode="L")

    # Align une fois
    print("Alignement: clique 2 points sur l'image 1, puis 2 points sur l'image 2.")
    im1_aligned, im2_aligned = align_images(im1, im2)

    im1_aligned, im2_aligned = crop_to_overlap(im1_aligned, im2_aligned, thr=0.0, pad=2)
    print("Après overlap crop:", im1_aligned.shape, im2_aligned.shape)


    # Crop une fois sur chacune
    #print("Crop: clique 2 points (haut-gauche puis bas-droit) pour im1 alignée.")
    #im1_cropped = crop_image(im1_aligned)
    im1_cropped = im1_aligned

    #print("Crop: clique 2 points (haut-gauche puis bas-droit) pour im2 alignée.")
    #im2_cropped = crop_image(im2_aligned)
    im2_cropped = im2_aligned

    # FFT amplitude des 2 images initiales
    save_amplitude_image(im1_cropped, out_amp_dir / "amp_original_img1.png")
    save_amplitude_image(im2_cropped, out_amp_dir / "amp_original_img2.png")
    print("Saved FFT amplitudes for original images.")

    # Valeurs de cutoff
    cutoff_lows = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    cutoff_highs = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

    # Convertir une fois en float [0,1] pour filtres/FFT
    im1_f = mettre_float01(im1_cropped)
    im2_f = mettre_float01(im2_cropped)

    # Boucles pour générer les hybrides et leurs FFT pour chaque combo de cutoff
    for low in cutoff_lows:
        for high in cutoff_highs:
            print(f"Génère hybrid: cutoff_low={low}, cutoff_high={high}")

            # Hybride via ma fonction (pour l'image à sauvegarder)
            hyb_u8 = hybrid_image(im1_cropped, im2_cropped, low, high)
            #hyb_u8 = crop_image(hyb_u8)

            if hyb_u8.dtype != np.uint8:
                hyb_u8 = np.clip(hyb_u8, 0, 255).astype(np.uint8)

            # Nom de fichier
            img_filename = f"hybrid_cutoff{low}_{high}.png"
            imsave(str(out_dir / img_filename), hyb_u8)

            # Recalcule low/high ici (pour sauvegarder leurs FFT)
            #    (comme dans l’article/énoncé: low = blur(img1), high = img2 - blur(img2))
            low_img = skimage.filters.gaussian(im1_f, sigma=low)
            high_img = im2_f - skimage.filters.gaussian(im2_f, sigma=high)

            # Hybride float (pour FFT) = low + high
            hyb_f = np.clip(low_img + high_img, 0.0, 1.0)

            # FFT amplitude: 2 images filtrées + hybride (pour chaque combo)
            tag = f"{low}_{high}"
            save_amplitude_image(low_img, out_amp_dir / f"amp_low_cutoff{tag}.png")
            save_amplitude_image(high_img, out_amp_dir / f"amp_high_cutoff{tag}.png")
            save_amplitude_image(hyb_f, out_amp_dir / f"amp_hybrid_cutoff{tag}.png")

            print(f"Saved hybrid + FFT amplitudes pour cutoff_low={low}, cutoff_high={high}")

    print("Tâche terminée. Images hybrides et FFT sauvegardées dans 'web/images/hybrid/'.")


if __name__ == "__main__":
    main()
