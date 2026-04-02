import spacy

nlp = spacy.load("en_core_web_sm")

POS_MAP = {
    "NOUN": 0,  
    "PROPN": 0,  # Власні назви 
    "VERB": 1,
    "AUX": 1,    # Допоміжне дієслово 
    "PRON": 2,   # Займенник 
    "ADJ": 3,    # Прикметник 
    "ADV": 4,    # Прислівник 
    "ADP": 5,    # Прийменник 
    "DET": 6,    # Артикль
    "CONJ": 7,   # Сполучник 
    "CCONJ": 7,  # Сурядний сполучник 
    "SCONJ": 7,  # Підрядний сполучник 
    "NUM": 8,    
    "PART": 9,   # Частки (to, not, 's) 
    "INTJ": 10,  # Вигуки 
}

def convert_text_to_pos_numbers(input_file, output_file, log_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        doc = nlp(text)

        numbers = []
        unknown_logs = [] 

        for token in doc:
            if token.is_space or token.is_punct:
                continue
            
            pos_tag = token.pos_

            if pos_tag == "X":
                continue

            number = POS_MAP.get(pos_tag, -1)
            
            if number == -1:
                log_message = f"Невідомий тег: слово '{token.text}' має тег '{pos_tag}'\n"
                unknown_logs.append(log_message)

            numbers.append(str(number))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(" ".join(numbers))

        if unknown_logs:
            with open(log_file, 'w', encoding='utf-8') as log_f:
                log_f.writelines(unknown_logs)
            print(f"Знайдено невідомі теги")
        else:
            print("Усі теги розпізнано")

    except FileNotFoundError:
        print("Вхідний файл не знайдено.")

if __name__ == "__main__":
    convert_text_to_pos_numbers("Blyton, Enid - Famous Five 03 - Five Run Away Together.txt", "output2.txt", "unknown_tags.txt")