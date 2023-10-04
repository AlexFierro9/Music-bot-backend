from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

sentiment_tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-emotion")
sentiment_model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-emotion")
tokenizer = AutoTokenizer.from_pretrained("microsoft/GODEL-v1_1-large-seq2seq")
model = AutoModelForSeq2SeqLM.from_pretrained("microsoft/GODEL-v1_1-large-seq2seq")


def generate_response(dialog):
    knowledge = ''
    instruction = f'Instruction: given a dialog context, you need to response empathically.'
    dialog_text = ' EOS '.join(dialog)
    query = f"{instruction} [CONTEXT] {dialog_text} {knowledge}"

    input_ids = tokenizer.encode(query, return_tensors="pt")
    output = model.generate(input_ids, max_length=16, min_length=2, top_p=0.9, do_sample=True)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text


def sentiment_finder(user_dialog):
    input_ids = sentiment_tokenizer.encode(user_dialog + '</s>', return_tensors='pt')
    output = sentiment_model.generate(input_ids=input_ids, max_length=2)
    emotion = [sentiment_tokenizer.decode(ids) for ids in output][0]
    return emotion[6:]
