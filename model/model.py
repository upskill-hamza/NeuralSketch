"""
NeuralSketch CNN — compact 4-block convolutional network for sketch classification.
Input:  (B, 1, 28, 28) grayscale bitmap
Output: (B, 50) class logits
~1.2M parameters
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    """Conv2d → BatchNorm2d → ReLU → MaxPool2d"""

    def __init__(self, in_ch: int, out_ch: int, pool: bool = True):
        super().__init__()
        layers = [
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        ]
        if pool:
            layers.append(nn.MaxPool2d(2, 2))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class SketchCNN(nn.Module):
    """
    Lightweight CNN for 28×28 sketch classification.

    Architecture:
        Conv Block 1: 1   → 32  ch, pool → 14×14
        Conv Block 2: 32  → 64  ch, pool → 7×7
        Conv Block 3: 64  → 128 ch, pool → 3×3
        Conv Block 4: 128 → 256 ch, no pool
        AdaptiveAvgPool → 1×1
        FC 256 → 512 → num_classes
    """

    def __init__(self, num_classes: int = 50, dropout: float = 0.4):
        super().__init__()

        self.features = nn.Sequential(
            ConvBlock(1, 32, pool=True),    # 28→14
            ConvBlock(32, 64, pool=True),   # 14→7
            ConvBlock(64, 128, pool=True),  # 7→3
            ConvBlock(128, 256, pool=False),
        )

        self.pool = nn.AdaptiveAvgPool2d(1)
        self.dropout = nn.Dropout(dropout)

        self.classifier = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.classifier(x)
        return x


def get_model(num_classes: int = 50, pretrained_path: str = None) -> SketchCNN:
    """Instantiate model, optionally load weights."""
    model = SketchCNN(num_classes=num_classes)
    if pretrained_path:
        state = torch.load(pretrained_path, map_location="cpu")
        model.load_state_dict(state)
        model.eval()
    return model


if __name__ == "__main__":
    model = SketchCNN()
    x = torch.randn(4, 1, 28, 28)
    out = model(x)
    print(f"Output shape: {out.shape}")  # (4, 50)
    total = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {total:,}")
