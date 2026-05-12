import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "AVG.xlsx")
OUTPUT_DIR = os.path.join(BASE_DIR, "T_Test_Results" )

COL_FILENAME = "text"         
COL_REGULAR_AVG = "average (regular)" 
COL_POS_AVG = "average (pos)"      

BASELINE_KEYWORD = "theNewPenguinHistoryOfTheWorld"
AI_KEYWORDS = ["Claude", "Gemini", "GPT", "Llama", "Mistral"]

def clean_numeric_column(series):
    if series.dtype == 'object':
        return series.astype(str).str.replace(',', '.').apply(pd.to_numeric, errors='coerce')
    return pd.to_numeric(series, errors='coerce')

def perform_analysis_and_plot(nat_arr, ai_arr, ai_name, metric_name, mode_name, output_folder):
    nat_arr = nat_arr[~np.isnan(nat_arr)]
    ai_arr = ai_arr[~np.isnan(ai_arr)]
    
    if len(nat_arr) < 2 or len(ai_arr) < 2:
        print(f"  [Пропуск] Недостатньо даних для {ai_name} у {metric_name} ({mode_name})")
        return

    mean_nat, mean_ai = np.mean(nat_arr), np.mean(ai_arr)
    std_nat, std_ai = np.std(nat_arr, ddof=1), np.std(ai_arr, ddof=1)
    var_nat, var_ai = np.var(nat_arr, ddof=1), np.var(ai_arr, ddof=1)
    
    t_stat, p_value = stats.ttest_ind(nat_arr, ai_arr, equal_var=False)
    
    df_welch = ((var_nat/len(nat_arr) + var_ai/len(ai_arr))**2) / \
               ((var_nat/len(nat_arr))**2/(len(nat_arr)-1) + (var_ai/len(ai_arr))**2/(len(ai_arr)-1))

    report = (
        f"=== Режим: {mode_name} | Дані: {metric_name} ===\n\n"
        f"Порівняння: NL vs {ai_name}\n"
        f"--------------------------------------------------\n"
        f"Кількість текстів (NL):     {len(nat_arr)}\n"
        f"Кількість текстів ({ai_name}):     {len(ai_arr)}\n\n"
        f"Середнє (NL):     {mean_nat:.6f}\n"
        f"Середнє ({ai_name}):     {mean_ai:.6f}\n\n"
        f"Станд. відхилення (NL):     {std_nat:.6f}\n"
        f"Станд. відхилення ({ai_name}):     {std_ai:.6f}\n\n"
        f"Дисперсія (NL):     {var_nat:.6e}\n"
        f"Дисперсія ({ai_name}):     {var_ai:.6e}\n\n"
        f"--- Результати T-Тесту ---\n"
        f"T-статистика:             {t_stat:.6f}\n"
        f"Ступені вільності (df):   {df_welch:.4f}\n"
        f"P-значення (p-value):     {p_value:.6e} (або {p_value:.6f})\n"
        f"Ймовірність схожості:     {p_value * 100:.4f}%\n"
    )

    safe_metric = "Regular" if "regular" in metric_name.lower() else "POS_Tagging"
    base_filename = f"{mode_name}_{safe_metric}_{ai_name.capitalize()}_vs_NL"
    txt_path = os.path.join(output_folder, base_filename + ".txt")
    png_path = os.path.join(output_folder, base_filename + ".png")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report)

    df_plot = pd.DataFrame({
        'Значення': np.concatenate([nat_arr, ai_arr]),
        'Текст': ['NL']*len(nat_arr) + [f'{ai_name.capitalize()} (AI)']*len(ai_arr)
    })

    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=df_plot, x='Значення', hue='Текст', fill=True, 
                palette={'NL': 'blue', f'{ai_name.capitalize()} (AI)': 'red'}, 
                alpha=0.4, linewidth=2)
    sns.rugplot(data=df_plot, x='Значення', hue='Текст', 
                palette={'NL': 'blue', f'{ai_name.capitalize()} (AI)': 'red'}, 
                height=0.05, linewidth=2)

    plt.title(f'[{mode_name}] {metric_name}: NL vs {ai_name.capitalize()}', fontsize=14)
    plt.xlabel('Середнє значення V(t)', fontsize=12)
    plt.ylabel('Щільність', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    text_info = f"T-stat: {t_stat:.2f}\nP-value: {p_value:.2e}\nMean NL: {mean_nat:.3f}\nMean AI: {mean_ai:.3f}"
    plt.gca().text(0.05, 0.95, text_info, transform=plt.gca().transAxes, fontsize=11,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()


def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Помилка: Файл {EXCEL_FILE} не знайдено!")
        return

    xls = pd.ExcelFile(EXCEL_FILE)

    for sheet_name in xls.sheet_names:
        print(f"\nОбробка режиму: {sheet_name}")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        if COL_FILENAME not in df.columns:
            print(f"  [Помилка] Не знайдено колонку '{COL_FILENAME}' на листку {sheet_name}. Пропуск.")
            continue
            
        df[COL_REGULAR_AVG] = clean_numeric_column(df[COL_REGULAR_AVG])
        df[COL_POS_AVG] = clean_numeric_column(df[COL_POS_AVG])

        baseline_df = df[df[COL_FILENAME].str.contains(BASELINE_KEYWORD, case=False, na=False)]
        nat_regular = baseline_df[COL_REGULAR_AVG].values
        nat_pos = baseline_df[COL_POS_AVG].values

        sheet_folder_reg = os.path.join(OUTPUT_DIR, sheet_name, "Regular_Text")
        sheet_folder_pos = os.path.join(OUTPUT_DIR, sheet_name, "POS_Tagging")
        os.makedirs(sheet_folder_reg, exist_ok=True)
        os.makedirs(sheet_folder_pos, exist_ok=True)

        for ai in AI_KEYWORDS:
            ai_df = df[df[COL_FILENAME].str.contains(ai, case=False, na=False)]
            ai_regular = ai_df[COL_REGULAR_AVG].values
            ai_pos = ai_df[COL_POS_AVG].values

            perform_analysis_and_plot(nat_regular, ai_regular, ai, "Regular Text", sheet_name, sheet_folder_reg)
            
            perform_analysis_and_plot(nat_pos, ai_pos, ai, "POS-Tagging", sheet_name, sheet_folder_pos)
            
            print(f"Збережено порівняння: NL vs {ai}")

if __name__ == "__main__":
    main()