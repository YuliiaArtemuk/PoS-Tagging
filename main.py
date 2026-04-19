import os
import spacy
from langdetect import detect

nlp_en = spacy.load("en_core_web_sm")
nlp_uk = spacy.load("uk_core_news_sm")

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

def process_text_folder(input_folder, output_folder, global_log_file):
    if not os.path.exists(input_folder):
        print(f"Помилка: Папку '{input_folder}' не знайдено.")
        return

    os.makedirs(output_folder, exist_ok=True)

    all_unknown_logs = []
    processed_count = 0

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue  

        input_path = os.path.join(input_folder, filename)
        
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}_output.txt"
        output_path = os.path.join(output_folder, output_filename)

        print(f"Обробка: {filename}...", end=" ")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
                print("Файл порожній. Пропуск.")
                continue

            try:
                language = detect(text)
            except:
                language = 'en'

            if language == 'uk':
                doc = nlp_uk(text)
            else:
                doc = nlp_en(text) 

            numbers = []
            file_unknown_logs = [] 

            for token in doc:
                if token.is_space or token.is_punct or token.pos_ == "SYM":
                    continue
                
                pos_tag = token.pos_

                if pos_tag == "X":
                    continue

                number = POS_MAP.get(pos_tag, -1)
                
                if number == -1:
                    log_message = f"  - Слово '{token.text}' має тег '{pos_tag}'\n"
                    file_unknown_logs.append(log_message)

                numbers.append(str(number))

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(" ".join(numbers))

            if file_unknown_logs:
                all_unknown_logs.append(f"--- У файлі: {filename} ---\n")
                all_unknown_logs.extend(file_unknown_logs)
                all_unknown_logs.append("\n")
                print("Готово (знайдено невідомі теги).")
            else:
                print("Готово.")

            processed_count += 1

        except Exception as e:
            print(f"Помилка зчитування: {e}")

    if all_unknown_logs:
        with open(global_log_file, 'w', encoding='utf-8') as log_f:
            log_f.writelines(all_unknown_logs)
        print(f"\nЗавершено! Оброблено {processed_count} файлів. Логи збережено у '{global_log_file}'.")
    else:
        print(f"\nЗавершено! Оброблено {processed_count} файлів. Усі теги розпізнано ідеально.")


if __name__ == "__main__":
    INPUT_DIR = "ai_texts\Mistral"        
    OUTPUT_DIR = "results\Mistral_results"   
    LOG_FILE = "unknown_tags\Mistral_unknown_tags.txt"

    process_text_folder(INPUT_DIR, OUTPUT_DIR, LOG_FILE)