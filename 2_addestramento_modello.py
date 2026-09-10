import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

def main():
    cartella_progetto = r"C:\Users\VINCENZO\Desktop\Progetto_ICON"
    file_csv = os.path.join(cartella_progetto, "dati_agricoli_puliti.csv")
    file_modello = os.path.join(cartella_progetto, "modello_agricolo.pkl")
    
    print("1. Caricamento del dataset agricolo...")
    df = pd.read_csv(file_csv)
    
    print("\n2. Pre-processing dei dati...")
    le_target = LabelEncoder()
    df['label_encoded'] = le_target.fit_transform(df['label'])

    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label_encoded']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\n3. Addestramento dell'Albero di Decisione...")
    modello = DecisionTreeClassifier(max_depth=10, random_state=42)
    modello.fit(X_train, y_train)
    
    print("\n4. Valutazione e Feature Importance...")
    y_pred = modello.predict(X_test)
    print(f"Accuratezza Globale: {accuracy_score(y_test, y_pred):.4f}")
    
    print("\nImportanza delle singole caratteristiche (Feature Importance):")
    feature_nomi = X.columns
    importanza = modello.feature_importances_
    
    # Stampiamo l'impatto di ogni feature ordinato
    for nome, imp in zip(feature_nomi, importanza):
        print(f" - {nome.upper()}: {imp*100:.2f}%")

    print("\n5. Esportazione del modello...")
    with open(file_modello, 'wb') as f:
        pickle.dump((modello, le_target), f)
    print("Modello aggiornato e salvato con successo!\n")

if __name__ == "__main__":
    main()