from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftModel
import torch
import json

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
MODEL_PATH = "./models/travel-crm-merged"

class BookingAgent:
    def __init__(self):
        print("Loading fine-tuned model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
            device_map="cpu"
        )
        self.model = PeftModel.from_pretrained(base_model, MODEL_PATH)
        self.tokenizer = tokenizer
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,
            temperature=0.2,
            do_sample=True,
        )
        print("✅ Model loaded!")

    def _ask(self, instruction: str) -> str:
        prompt = f"<s>[INST] {instruction} [/INST]"
        output = self.pipe(prompt)[0]["generated_text"]
        return output.split("[/INST]")[-1].strip()

    def create_booking(self, customer_name: str, details: str) -> str:
        instruction = f"Create a booking for {customer_name}. {details}"
        return self._ask(instruction)

    def generate_itinerary(self, destination: str, days: int,
                           interests: str, budget: int) -> str:
        instruction = f"Generate a {days}-day itinerary for {destination}. Interests: {interests}. Budget: {budget}."
        return self._ask(instruction)