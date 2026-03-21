import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────
BASE_MODEL  = "mistralai/Mistral-7B-Instruct-v0.2"
OUTPUT_DIR  = "./models/travel-crm-mistral"
TRAIN_FILE  = "data/train.jsonl"
VAL_FILE    = "data/val.jsonl"
HF_TOKEN    = os.getenv("HF_TOKEN")

# ── Step 1: 4-bit Quantization config ────────────────────────
# This allows training a 7B model on a normal GPU
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# ── Step 2: Load base model ───────────────────────────────────
print("\n📥 Loading base model (this may take 5-10 mins first time)...")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    token=HF_TOKEN,
    trust_remote_code=True
)
model = prepare_model_for_kbit_training(model)

# ── Step 3: Load tokenizer ────────────────────────────────────
print("📝 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    token=HF_TOKEN,
    trust_remote_code=True
)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# ── Step 4: LoRA config ───────────────────────────────────────
# Only trains ~0.6% of total parameters — very efficient!
print("⚙️  Setting up LoRA adapters...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[
        "q_proj", "k_proj", "v_proj",
        "o_proj", "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ── Step 5: Load dataset ──────────────────────────────────────
print("\n📂 Loading training data...")
dataset = load_dataset(
    "json",
    data_files={
        "train"     : TRAIN_FILE,
        "validation": VAL_FILE
    }
)
print(f"  Train samples : {len(dataset['train'])}")
print(f"  Val samples   : {len(dataset['validation'])}")

# ── Step 6: Training arguments ────────────────────────────────
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=5,
    evaluation_strategy="steps",
    eval_steps=20,
    save_strategy="epoch",
    load_best_model_at_end=True,
    warmup_ratio=0.05,
    lr_scheduler_type="cosine",
    optim="paged_adamw_8bit",
    report_to="none",           # change to "wandb" if you set up W&B
    run_name="travel-crm-v1",
)

# ── Step 7: Train ─────────────────────────────────────────────
print("\n🚀 Starting fine-tuning...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    dataset_text_field="text",
    max_seq_length=1024,
    args=training_args,
    packing=True,
)

trainer.train()

# ── Step 8: Save ──────────────────────────────────────────────
print("\n💾 Saving fine-tuned model...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\n✅ Fine-tuning complete!")
print(f"   Model saved to → {OUTPUT_DIR}")
print(f"\n👉 Next step: run  python finetune/merge_model.py")