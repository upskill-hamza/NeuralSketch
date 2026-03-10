"""
Training script for NeuralSketch CNN.
Usage:
    python train.py [--epochs 30] [--lr 1e-3] [--batch-size 256]
"""

import os
import argparse
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

from model import SketchCNN
from dataset import download_data, get_loaders
from categories import NUM_CLASSES

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
BEST_MODEL_PATH = os.path.join(WEIGHTS_DIR, "best_model.pth")


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        logits = model(imgs)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * imgs.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        total += imgs.size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def val_epoch(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        logits = model(imgs)
        loss = criterion(logits, labels)
        total_loss += loss.item() * imgs.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        total += imgs.size(0)
    return total_loss / total, correct / total


def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # --- Data ---
    print("Preparing data ...")
    download_data()
    train_loader, val_loader = get_loaders(
        batch_size=args.batch_size,
        samples_per_class=args.samples_per_class
    )

    # --- Model ---
    model = SketchCNN(num_classes=NUM_CLASSES).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)

    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    best_val_acc = 0.0
    patience, patience_counter = 5, 0

    print(f"\nTraining for {args.epochs} epochs ...\n")
    header = f"{'Epoch':>6} | {'Train Loss':>10} | {'Train Acc':>9} | {'Val Loss':>9} | {'Val Acc':>8} | {'Time':>6}"
    print(header)
    print("-" * len(header))

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        tloss, tacc = train_epoch(model, train_loader, criterion, optimizer, device)
        vloss, vacc = val_epoch(model, val_loader, criterion, device)
        scheduler.step()
        elapsed = time.time() - t0

        print(f"{epoch:>6} | {tloss:>10.4f} | {tacc:>8.2%} | {vloss:>9.4f} | {vacc:>7.2%} | {elapsed:>5.1f}s")

        if vacc > best_val_acc:
            best_val_acc = vacc
            torch.save(model.state_dict(), BEST_MODEL_PATH)
            print(f"         ✓ Saved best model (val acc: {vacc:.2%})")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\nEarly stopping triggered after {epoch} epochs.")
                break

    print(f"\nBest val accuracy: {best_val_acc:.2%}")
    print(f"Weights saved to: {BEST_MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NeuralSketch CNN")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--samples-per-class", type=int, default=5000)
    args = parser.parse_args()
    main(args)
