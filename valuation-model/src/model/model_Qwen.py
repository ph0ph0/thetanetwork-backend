import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

class ValuationModel:
    def __init__(self):
        print("Initializing Qwen model")
        torch.manual_seed(1234)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-VL-Chat", device_map="auto", trust_remote_code=True).eval()
        print(f"Model loaded: {model.__class__.__name__}")
        self.model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
        self.image_paths = []

    def load_images(self, image_paths=None):
        print("Loading images")
        if image_paths is None:
            # Default image loading logic
            self.image_paths = [
                f"./test_images/success/{i}.png"
                for i in range(1, 12)
            ]
        else:
            self.image_paths = image_paths

    def query_model(self, task_description):
        print("Querying model")
        if not self.image_paths:
            raise ValueError("No images loaded. Please call load_images() first.")

        queries = [{'image': path} for path in self.image_paths]
        queries.append({'text': f"Analyze the ordered sequence of images to determine how accurately and completely the task '{task_description}' was performed. Only provide a 1 sentence summary of what the images show, but also provide a valuation between 0 and 100, where 0 indicates the task was not performed at all and 100 indicates the task was performed perfectly."})
        
        # Create the query
        query = self.tokenizer.from_list_format(queries)

        # Generate a response
        response, _ = self.model.chat(self.tokenizer, query=query, history=None)

        return response

    def run_valuation(self, task_description, image_paths=None):
        self.load_images(image_paths)
        return self.query_model(task_description)


# TODO Remove
model = ValuationModel()
task = "go to Twitter and share OpenAI's most recent tweet"
result = model.run_valuation(task)
print(result)