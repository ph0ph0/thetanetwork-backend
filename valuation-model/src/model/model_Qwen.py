import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

torch.manual_seed(1234)

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-VL-Chat", device_map="auto", trust_remote_code=True).eval()

# Specify hyperparameters for generation
model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)

# Load image paths
image_paths = [
    f"./test_images/success/{i}.png"
    for i in range(1, 12)
]

queries = [{'image': path} for path in image_paths]
queries.append({'text': "Analyze the ordered sequence of images to determine how accurately and completely the task 'go to Twitter and share OpenAI's most recent tweet' was performed. Only provide a 1 sentence summary of what the images show, but also provide a valuation between 0 and 100, where 0 indicates the task was not performed at all and 100 indicates the task was performed perfectly."})

# Create the query
query = tokenizer.from_list_format(queries)

# Generate a response
response, history = model.chat(tokenizer, query=query, history=None)

# Print the response
print(response)
