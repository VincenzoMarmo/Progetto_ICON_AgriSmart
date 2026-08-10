import pandas as pd
import os

# Definiamo i percorsi esatti
cartella_progetto = r"C:\Users\VINCENZO\Desktop\Progetto_ICON"
file_input = os.path.join(cartella_progetto, "crop_data.csv")
file_output = os.path.join(cartella_progetto, "dati_agricoli_puliti.csv")

print("1. Caricamento del dataset agricolo in corso...")

# Leggiamo il dataset
df = pd.read_csv(file_input)

# Puliamo i nomi delle colonne da eventuali spazi invisibili
df.columns = df.columns.str.strip()

print("\nDataset caricato! Ecco le colonne originali:")
print(df.columns.tolist())
print("-" * 50)

# Rimuoviamo eventuali righe con dati mancanti per sicurezza
df_pulito = df.dropna().copy()

print("Anteprima dei dati pronti per il Machine Learning:")
print(df_pulito.head())

# Salviamo il dataset pulito
df_pulito.to_csv(file_output, index=False)
print(f"\nFase 1 completata! File salvato in: {file_output}")