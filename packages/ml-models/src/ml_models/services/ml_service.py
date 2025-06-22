import random
import asyncio

DUMMY_LABELS = [
    "cat", "dog", "car", "tree", "house", "person", "bicycle", "sky", "road"
]

async def annotate_image(image_bytes: bytes) -> list[str]:
    """
    A mock, non-blocking ML model function.
    """
    # Simulate model processing time without blocking the event loop
    await asyncio.sleep(0.5)
    num_labels = random.randint(1, 4)
    predicted_labels = random.sample(DUMMY_LABELS, num_labels)
    return predicted_labels