

from transformers import AutoModelForSeq2SeqLM, TrainingArguments, Trainer
from datasets import load_dataset
import torch
import wandb

# Убедитесь, что NllbTokenizer доступен для импорта или обновите его на AutoTokenizer
from transformers import NllbTokenizer

MODEL_NAME = 'facebook/nllb-200-distilled-1.3B'

if __name__ == "__main__":

    wandb.login(key='c0a50a9f7bee09b750fb713034730bb5b700c9c6')
    MODEL_NAME = 'facebook/nllb-200-distilled-1.3B'

    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16, device_map='auto')
    tokenizer = NllbTokenizer.from_pretrained(MODEL_NAME, src_lang='azj_Latn', tgt_lang="eng_Latn")

    dataset = load_dataset("json", data_files="dev.jsonl")

    def tokenize_function(examples):
        return tokenizer([sample for sample in examples["source"]], text_target=examples["target"], return_tensors="pt", truncation=True, padding="max_length", max_length=512)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    train_dataset = tokenized_datasets["train"]

    training_args = TrainingArguments(
        output_dir='nllb-200-distilled-1.3b',
        num_train_epochs=1,
        logging_steps=10,
        save_steps=500,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        warmup_steps=100,
        weight_decay=0.01,
        bf16=True,
        torch_compile=True,
        optim="adamw_bnb_8bit",
        gradient_accumulation_steps=4,
        # Замените "wandb" на None, если не используете Weights & Biases
        report_to="wandb",
        save_total_limit=5,
        run_name='nllb-200-distilled-1.3b',
        learning_rate=1e-4
    )

    trainer = Trainer(
        model=model, args=training_args,
        train_dataset=train_dataset
    )

    trainer.train(resume_from_checkpoint=False)
    trainer.save_model()