"""
Dataset utilities for Quick, Draw! .npy files.
Downloads 50 category files from Google Cloud Storage,
prepares PyTorch DataLoaders.
"""

import os
import shutil
import subprocess
import time
import urllib.parse
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split

from categories import CATEGORIES

BASE_URL  = "https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/"
GS_BASE   = "gs://quickdraw_dataset/full/numpy_bitmap/"   # gsutil fallback
DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
SAMPLES_PER_CLASS = 5000
IMG_SIZE  = 28

_CHUNK = 1 << 20   # 1 MB read chunks

def _http_download(url: str, dest: str, retries: int = 3) -> bool:
    """Download *url* to *dest* via HTTPS with retry/backoff. Returns True on success."""
    import urllib.request
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NeuralSketch/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp, \
                 open(dest, "wb") as out:
                while chunk := resp.read(_CHUNK):
                    out.write(chunk)
            return True
        except Exception as exc:
            print(f"   attempt {attempt}/{retries} failed: {exc}")
            if os.path.exists(dest):
                os.remove(dest)
            if attempt < retries:
                time.sleep(2 ** attempt)   # 2s, 4s back-off
    return False

def _gsutil_download(gs_url: str, dest: str) -> bool:
    """Fallback: use gsutil (gcloud SDK) to copy from gs:// to local path."""
    if not shutil.which("gsutil"):
        return False
    print("   → retrying with gsutil ...")
    result = subprocess.run(
        ["gsutil", "-q", "cp", gs_url, dest],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"   gsutil error: {result.stderr.strip()}")
        if os.path.exists(dest):
            os.remove(dest)
        return False
    return True

def download_data(data_dir: str = DATA_DIR, samples: int = SAMPLES_PER_CLASS):
    os.makedirs(data_dir, exist_ok=True)
    failed = []

    for cat in CATEGORIES:
        safe_name  = cat.replace(" ", "_")
        fname_enc  = urllib.parse.quote(cat + ".npy")
        dest       = os.path.join(data_dir, safe_name + ".npy")

        if os.path.exists(dest):
            print(f"[skip]     {cat}")
            continue

        url    = BASE_URL + fname_enc
        gs_url = GS_BASE + urllib.parse.quote(cat + ".npy")
        print(f"[download] {cat}  →  {url}")

        ok = _http_download(url, dest)
        if not ok:
            ok = _gsutil_download(gs_url, dest)

        if ok:
            print(f"           ✓ {cat}")
        else:
            print(f"           ❌ {cat} — giving up")
            failed.append(cat)

    if failed:
        raise RuntimeError(
            f"\n{len(failed)} categories failed to download:\n  "
            + "\n  ".join(failed)
            + "\n\nTry running:  pip install gcloud  then  gcloud init"
            + "\nor download manually with gsutil:"
            + f"\n  gsutil -m cp '{GS_BASE}*.npy' {data_dir}"
        )
    print("All downloads complete.")

class QuickDrawDataset(Dataset):
    """
    Loads Quick, Draw! .npy files.
    Each sample: (1, 28, 28) float32 tensor in [0, 1], label int.
    """

    def __init__(self, data_dir: str = DATA_DIR, samples_per_class: int = SAMPLES_PER_CLASS):
        self.images = []
        self.labels = []

        for idx, cat in enumerate(CATEGORIES):
            path = os.path.join(data_dir, cat.replace(" ", "_") + ".npy")
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Missing file: {path}. Run download_data() first."
                )
            data = np.load(path)
            n = min(samples_per_class, len(data))
            self.images.append(data[:n])
            self.labels.extend([idx] * n)

        self.images = np.concatenate(self.images, axis=0).astype(np.float32) / 255.0
        self.labels = np.array(self.labels, dtype=np.int64)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img = torch.tensor(self.images[idx]).reshape(1, IMG_SIZE, IMG_SIZE)
        label = torch.tensor(self.labels[idx])
        return img, label

def get_loaders(
    data_dir: str = DATA_DIR,
    samples_per_class: int = SAMPLES_PER_CLASS,
    batch_size: int = 256,
    val_split: float = 0.1,
    num_workers: int = 2,
):
    """Return train and validation DataLoaders."""
    dataset = QuickDrawDataset(data_dir=data_dir, samples_per_class=samples_per_class)
    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True
    )
    print(f"Train: {len(train_ds):,} | Val: {len(val_ds):,}")
    return train_loader, val_loader

if __name__ == "__main__":
    print("Downloading Quick, Draw! dataset...")
    download_data()
    train_loader, val_loader = get_loaders()
    imgs, labels = next(iter(train_loader))
    print(f"Batch shape: {imgs.shape}, Labels: {labels[:5]}")
