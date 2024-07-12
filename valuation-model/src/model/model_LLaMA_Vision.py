# https://huggingface.co/qresearch/llama-3-vision-alpha-hf

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig

bnb_cfg = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    llm_int8_skip_modules=["mm_projector", "vision_model"],
)

model_id = "qresearch/llama-3-vision-alpha-hf"
model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=model_id,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    quantization_config=bnb_cfg,
)

tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    use_fast=True,
)

# Load images
images = [
    Image.open(f"./test_images/success/{i}.png")
    for i in range(1, 12)
]

task_description = "go to Twitter and share OpenAI's most recent tweet"

question = f"The images that you have been provided with are screenshots taken from a user's device. In sequence, they represent the steps that a user must take in order to complete a given task. Analyze the ordered sequence of images to determine how accurately and completely the task '{task_description}' was performed. Provide a valuation between 0 and 100, where 0 indicates the task was not performed at all and 100 indicates the task was performed perfectly. Include a brief explanation for the score."

print(
    tokenizer.decode(
        model.answer_question(images, question, tokenizer),
        skip_special_tokens=True,
    )
)
