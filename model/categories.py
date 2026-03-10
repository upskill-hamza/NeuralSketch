"""
50 Quick, Draw! categories used for training and inference.
"""

CATEGORIES = [
    "airplane", "apple", "bicycle", "bird", "book",
    "bridge", "butterfly", "car", "cat", "chair",
    "circle", "clock", "cloud", "crown", "diamond",
    "dog", "door", "eye", "fish", "flower",
    "guitar", "hammer", "hat", "bear", "house",
    "key", "knife", "lightning", "lion", "moon",
    "mountain", "mushroom", "palm tree", "pencil", "pizza",
    "rabbit", "rainbow", "shark", "shoe", "frog",
    "snake", "snowflake", "star", "sun", "sword",
    "tree", "triangle", "umbrella", "whale", "windmill",
]

CATEGORY_EMOJIS = {
    "airplane": "✈️", "apple": "🍎", "bicycle": "🚲", "bird": "🐦", "book": "📚",
    "bridge": "🌉", "butterfly": "🦋", "car": "🚗", "cat": "🐱", "chair": "🪑",
    "circle": "⭕", "clock": "🕐", "cloud": "☁️", "crown": "👑", "diamond": "💎",
    "dog": "🐶", "door": "🚪", "eye": "👁️", "fish": "🐟", "flower": "🌸",
    "guitar": "🎸", "hammer": "🔨", "hat": "🎩", "bear": "🐻", "house": "🏠",
    "key": "🔑", "knife": "🔪", "lightning": "⚡", "lion": "🦁", "moon": "🌙",
    "mountain": "⛰️", "mushroom": "🍄", "palm tree": "🌴", "pencil": "✏️", "pizza": "🍕",
    "rabbit": "🐰", "rainbow": "🌈", "shark": "🦈", "shoe": "👟", "frog": "🐸",
    "snake": "🐍", "snowflake": "❄️", "star": "⭐", "sun": "☀️", "sword": "⚔️",
    "tree": "🌳", "triangle": "🔺", "umbrella": "☂️", "whale": "🐋", "windmill": "🌬️",
}

NUM_CLASSES = len(CATEGORIES)
