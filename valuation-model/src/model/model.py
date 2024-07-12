import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

task_description = "go to Twitter and share OpenAI's most recent tweet"

# Load images
images = [
    preprocess(Image.open(f"./test_images/success/{i}.png")).unsqueeze(0).to(device)
    for i in range(1, 12)
]

# Encode text
text = clip.tokenize([task_description]).to(device)

# Compute image features and concatenate
image_features = [model.encode_image(image) for image in images]
concatenated_image_features = torch.cat(image_features, dim=0).mean(dim=0, keepdim=True)

# Compute text features
text_features = model.encode_text(text)

# Compute similarity
similarity = torch.nn.functional.cosine_similarity(concatenated_image_features, text_features).item()

# Print the similarity score
print(f"Similarity to task: {similarity * 100:.2f}%")
