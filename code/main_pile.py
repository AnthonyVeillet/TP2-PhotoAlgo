# main_pile.py
from __future__ import annotations

from pathlib import Path

import numpy as np
from skimage import io, img_as_float
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.util import img_as_ubyte


def load_gray_image(path: Path) -> np.ndarray:
    # Load une image et la convertie en float grayscale normalisé [0,1]
    img = io.imread(str(path))
    img = img_as_float(img)

    # Couleur -> gris
    if img.ndim == 3:
        if img.shape[2] == 4:
            img = img[:, :, :3]
        img = rgb2gray(img)

    return np.clip(img, 0.0, 1.0)


def gaussian_stack(
    img: np.ndarray,
    n_levels: int = 6,
    sigma0: float = 2.0,
    sigma_mult: float = 2.0,
) -> tuple[np.ndarray, list[float]]:
    #Pile gaussienne (même taille, sigma double, chaque niveau depuis l'original)
    H, W = img.shape
    stack = np.zeros((H, W, n_levels), dtype=np.float32)
    sigmas: list[float] = []

    sigma = sigma0
    for i in range(n_levels):
        g = gaussian(img, sigma=sigma, preserve_range=True, channel_axis=None)
        stack[:, :, i] = np.clip(g, 0.0, 1.0)
        sigmas.append(float(sigma))
        sigma *= sigma_mult

    return stack, sigmas


def laplacian_stack(gauss_stack: np.ndarray) -> np.ndarray:
    # Pile laplacienne: L_i = G_i - G_{i+1}, dernier = G_last
    H, W, L = gauss_stack.shape
    lap = np.zeros_like(gauss_stack, dtype=np.float32)

    for i in range(L - 1):
        lap[:, :, i] = gauss_stack[:, :, i] - gauss_stack[:, :, i + 1]
    lap[:, :, L - 1] = gauss_stack[:, :, L - 1]
    return lap


def normalize_for_save(x: np.ndarray) -> np.ndarray:
    # Normalise 2D -> uint8
    x = x.astype(np.float32)
    mn, mx = float(x.min()), float(x.max())
    if np.isclose(mx - mn, 0.0):
        return np.zeros_like(x, dtype=np.uint8)
    x01 = (x - mn) / (mx - mn)
    return img_as_ubyte(np.clip(x01, 0.0, 1.0))


def save_stack_images(
    stack: np.ndarray,
    out_dir: Path,
    prefix: str,
    sigmas: list[float] | None = None,
    laplacian: bool = False,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _, _, L = stack.shape

    for i in range(L):
        level = stack[:, :, i]
        img8 = normalize_for_save(level) if laplacian else img_as_ubyte(np.clip(level, 0.0, 1.0))

        sigma_txt = f"_sigma{sigmas[i]:g}" if sigmas is not None else ""
        out_path = out_dir / f"{prefix}_lvl{i:02d}{sigma_txt}.png"
        io.imsave(str(out_path), img8)


def make_grid(
    stacks_u8: list[np.ndarray],
    n_cols: int,
    pad: int = 8,
    pad_value: int = 0,
) -> np.ndarray:
    # Crée un montage grid à partir d'une liste d'images uint8 2D (H,W).
    # Retourne une image uint8 2D.
    assert len(stacks_u8) > 0, "Liste vide pour make_grid()"
    H, W = stacks_u8[0].shape
    for im in stacks_u8:
        assert im.shape == (H, W), "Toutes les images doivent avoir la même taille"

    n_imgs = len(stacks_u8)
    n_rows = int(np.ceil(n_imgs / n_cols))

    grid_h = n_rows * H + (n_rows - 1) * pad
    grid_w = n_cols * W + (n_cols - 1) * pad
    grid = np.full((grid_h, grid_w), pad_value, dtype=np.uint8)

    for idx, im in enumerate(stacks_u8):
        r = idx // n_cols
        c = idx % n_cols
        y0 = r * (H + pad)
        x0 = c * (W + pad)
        grid[y0 : y0 + H, x0 : x0 + W] = im

    return grid


def make_two_row_montage(
    gauss_stack: np.ndarray,
    lap_stack: np.ndarray,
    out_path: Path,
    pad: int = 8,
    pad_value: int = 0,
) -> None:

    _, _, L = gauss_stack.shape

    gauss_u8 = [img_as_ubyte(np.clip(gauss_stack[:, :, i], 0.0, 1.0)) for i in range(L)]
    lap_u8 = [normalize_for_save(lap_stack[:, :, i]) for i in range(L)]

    row1 = make_grid(gauss_u8, n_cols=L, pad=pad, pad_value=pad_value)
    row2 = make_grid(lap_u8, n_cols=L, pad=pad, pad_value=pad_value)

    # Empile verticalement avec un pad entre les deux rangées
    pad_row = np.full((pad, row1.shape[1]), pad_value, dtype=np.uint8)
    montage = np.vstack([row1, pad_row, row2])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    io.imsave(str(out_path), montage)


def main() -> None:
    in_path = Path("web/images/data/Partie2.jpg")
    out_dir = Path("web/images/pile/")

    img = load_gray_image(in_path)

    # Paramètres
    n_levels = 6
    sigma0 = 2.0
    sigma_mult = 2.0

    g_stack, sigmas = gaussian_stack(img, n_levels=n_levels, sigma0=sigma0, sigma_mult=sigma_mult)
    l_stack = laplacian_stack(g_stack)

    # Sauver chaque niveau
    save_stack_images(g_stack, out_dir, prefix="gauss", sigmas=sigmas, laplacian=False)
    save_stack_images(l_stack, out_dir, prefix="lap", sigmas=sigmas, laplacian=True)

    # Montage grid (2 rangées, N colonnes)
    montage_path = out_dir / "montage_gauss_lap.png"
    make_two_row_montage(g_stack, l_stack, montage_path, pad=8, pad_value=0)

    print("Piles + montage générés:")
    print(f" - Input : {in_path}")
    print(f" - Output: {out_dir.resolve()}")
    print(f" - Montage: {montage_path.resolve()}")
    print(f" - Niveaux: {n_levels}")
    print(f" - Sigmas : {sigmas}")


if __name__ == "__main__":
    main()
