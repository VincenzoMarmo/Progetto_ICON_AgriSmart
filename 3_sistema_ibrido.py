import os
import pickle
from pyswip import Prolog
from constraint import Problem, AllDifferentConstraint

def main():
    cartella_progetto = r"C:\Users\VINCENZO\Desktop\Progetto_ICON"
    file_modello = os.path.join(cartella_progetto, "modello_agricolo.pkl")
    file_prolog = os.path.join(cartella_progetto, "regole.pl")
    
    print("=== AGRISMART: SISTEMA IBRIDO MULTI-PARADIGMA ===")
    
    # 1. CARICAMENTO MACHINE LEARNING (Argomento 3)
    try:
        with open(file_modello, 'rb') as f:
            modello, le_target = pickle.load(f)
    except FileNotFoundError:
        print("Errore: file del modello non trovato.")
        return

    # Simuliamo la lettura dei sensori per 3 campi agricoli diversi
    # Valori: [N, P, K, temperature, humidity, ph, rainfall]
    campi = {
        "Campo_Nord":  [90, 42, 43, 20.8, 18.0, 6.5, 202.9], # Terreno molto secco (bassa umidità)
        "Campo_Sud":   [10, 50, 50, 28.0, 85.0, 7.0, 150.0], # Terreno umido
        "Campo_Ovest": [60, 55, 40, 24.0, 20.0, 6.0, 100.0]  # Terreno secco
    }

    # 2. INIZIALIZZAZIONE PROLOG (Argomento 1)
    prolog = Prolog()
    percorso_prolog = file_prolog.replace("\\", "/")
    prolog.consult(percorso_prolog)
    
    azioni_campi = {}

    print("\n--- FASE 1 & 2: PREDIZIONE ML E RAGIONAMENTO LOGICO ---")
    for nome_campo, dati_sensori in campi.items():
        # A. Predizione con ML
        predizione_num = modello.predict([dati_sensori])[0]
        coltura_suggerita = le_target.inverse_transform([predizione_num])[0]
        
        # B. Dati estratti dai sensori per la logica
        livello_umidita = "bassa" if dati_sensori[4] < 40.0 else "alta"
        
        print(f"\n[{nome_campo}] Coltura ideale prevista dal ML: {coltura_suggerita.upper()}")
        print(f"[{nome_campo}] Umidità rilevata: {livello_umidita}")
        
        # C. Passaggio dati a Prolog
        nome_campo_pl = nome_campo.lower()
        prolog.retractall(f"coltura_prevista({nome_campo_pl}, _)")
        prolog.retractall(f"umidita_rilevata({nome_campo_pl}, _)")
        
        prolog.assertz(f"coltura_prevista({nome_campo_pl}, {coltura_suggerita})")
        prolog.assertz(f"umidita_rilevata({nome_campo_pl}, {livello_umidita})")
        
        # D. Inferenza Logica (Backward Chaining)
        query = f"azione_consigliata({nome_campo_pl}, Azione)"
        risultati = list(prolog.query(query))
        
        if risultati:
            azione = risultati[0]['Azione']
            if isinstance(azione, bytes):
                azione = azione.decode('utf-8')
            azioni_campi[nome_campo] = azione
            print(f">>> RISPOSTA SISTEMA ESPERTO: {azione}")

    # 3. RISOLUZIONE DEI VINCOLI / CSP (Argomento 2)
    print("\n--- FASE 3: ALLOCAZIONE RISORSE (CSP) ---")
    problema = Problem()
    
    # Variabili: i campi che necessitano intervento
    campi_da_coprire = list(azioni_campi.keys())
    
    # Domini: i droni a disposizione dell'azienda
    droni_disponibili = ["Drone_Standard_1", "Drone_Standard_2", "Drone_Pompa_Pesante"]
    problema.addVariables(campi_da_coprire, droni_disponibili)
    
    # Vincolo 1: Un drone può trovarsi in un solo campo alla volta
    problema.addConstraint(AllDifferentConstraint(), campi_da_coprire)
    
    # Vincolo 2: Logica avanzata. Il 'Drone_Pompa_Pesante' DEVE essere assegnato 
    # ai campi in "EMERGENZA IDRICA" (se ce ne sono).
    def vincolo_emergenza(campo_nord, campo_sud, campo_ovest):
        assegnazioni = {"Campo_Nord": campo_nord, "Campo_Sud": campo_sud, "Campo_Ovest": campo_ovest}
        for campo, azione in azioni_campi.items():
            if "EMERGENZA IDRICA" in azione:
                if assegnazioni[campo] != "Drone_Pompa_Pesante":
                    return False
        return True

    problema.addConstraint(vincolo_emergenza, ["Campo_Nord", "Campo_Sud", "Campo_Ovest"])
    
    soluzioni = problema.getSolutions()
    
    if soluzioni:
        print("Trovata l'allocazione ottimale dei Droni nel rispetto dei vincoli:")
        miglior_soluzione = soluzioni[0]
        for campo, drone in miglior_soluzione.items():
            print(f" -> {campo}: assegnato a {drone}")
    else:
        print("Impossibile trovare un'allocazione che rispetti tutti i vincoli.")

if __name__ == "__main__":
    main()