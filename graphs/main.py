import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import warnings
from matplotlib.ticker import MultipleLocator  

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

folder_path = "graphs\Mistral" 

file_pattern = os.path.join(folder_path, '*.xlsx')
files = glob.glob(file_pattern)

if not files:
    print(f"У папці '{folder_path}' не знайдено Excel файлу.")
else:
    plt.figure(figsize=(12, 6))

    for file in files:
        df = pd.read_excel(file)
        file_name = os.path.basename(file)
        x = df.iloc[:, 0] 
        y = df.iloc[:, 1]
        
        plt.plot(x, y, linewidth=1, label=file_name)

    plt.title('')
    plt.xlabel('t')
    plt.ylabel('V(t)')
    plt.gca().yaxis.set_major_locator(MultipleLocator(0.02))
    plt.legend(loc='best') 
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig('graphs\combined_plot_mistral.png')
    #plt.show()