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
    print(f"Righe totali caricate: {len(df)}")

    print("\n2. Pre-processing dei dati...")
    # Il nostro 'Target' (ciò che vogliamo indovinare) è la colonna 'label' (la coltura)
    # Trasformiamo i nomi delle colture (es. 'rice', 'maize') in numeri per l'algoritmo
    le_target = LabelEncoder()
    df['label_encoded'] = le_target.fit_transform(df['label'])

    # Definiamo le Features (X) e il Target (y)
    # Le features sono tutti i parametri chimici e climatici
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label_encoded']

    # Dividiamo i dati: 80% per l'addestramento, 20% per il test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\n3. Addestramento dell'Albero di Decisione...")
    # Addestriamo il modello
    modello = DecisionTreeClassifier(max_depth=10, random_state=42)
    modello.fit(X_train, y_train)
    print("Modello addestrato con successo!")

    print("\n4. Generazione delle metriche di valutazione...")
    y_pred = modello.predict(X_test)
    
    # Calcoliamo l'accuratezza (da inserire poi nella documentazione)
    accuratezza = accuracy_score(y_test, y_pred)
    print(f"Accuratezza Globale (Accuracy): {accuratezza:.4f}")

    # Estraiamo i nomi delle colture per il report
    nomi_colture = [str(cls) for cls in le_target.classes_]

    print("\nReport di Classificazione Dettagliato:")
    print(classification_report(
        y_test, 
        y_pred, 
        target_names=nomi_colture, 
        zero_division=0
    ))

    print("\n5. Esportazione del modello...")
    # Salviamo il modello e l'encoder per usarli poi con Prolog
    with open(file_modello, 'wb') as f:
        pickle.dump((modello, le_target), f)
    print(f"File '{file_modello}' creato correttamente.\n")

if __name__ == "__main__":
    main()