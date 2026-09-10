% =====================================================================
% KNOWLEDGE BASE AGGIORNATA: Analisi Multi-Fattoriale (Acqua + Azoto)
% =====================================================================

:- dynamic coltura_prevista/2.
:- dynamic umidita_rilevata/2.
:- dynamic azoto_rilevato/2.

% 1. CONOSCENZA DI DOMINIO: Fabbisogno Idrico
necessita_acqua(rice, alta).
necessita_acqua(jute, alta).
necessita_acqua(maize, media).
necessita_acqua(lentil, bassa).
necessita_acqua(Coltura, media) :- 
    \+ member(Coltura, [rice, jute, maize, lentil]).

% 2. CONOSCENZA DI DOMINIO: Fabbisogno Nutrizionale (Azoto)
necessita_azoto(maize, alto).
necessita_azoto(cotton, alto).
necessita_azoto(rice, alto).
necessita_azoto(Coltura, medio) :- 
    \+ member(Coltura, [maize, cotton, rice]).

% 3. REGOLE INFERENZIALI COMPLESSE
% Regola 1: Doppia emergenza (Acqua + Nutrienti)
azione_consigliata(Campo, 'EMERGENZA TOTALE: Irrigazione massima e invio drone spargiconcime') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, alta), umidita_rilevata(Campo, bassa),
    necessita_azoto(Coltura, alto), azoto_rilevato(Campo, basso).

% Regola 2: Solo emergenza nutrizionale
azione_consigliata(Campo, 'FERTILIZZAZIONE: Carenza di Azoto, inviare drone spargiconcime') :-
    coltura_prevista(Campo, Coltura),
    necessita_azoto(Coltura, alto), azoto_rilevato(Campo, basso),
    umidita_rilevata(Campo, alta).

% Regola 3: Emergenza idrica standard
azione_consigliata(Campo, 'EMERGENZA IDRICA: Attivare irrigazione massima e inviare drone pompa') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, alta), umidita_rilevata(Campo, bassa),
    azoto_rilevato(Campo, ottimale).

% Regola 4: Monitoraggio e prevenzione funghi
azione_consigliata(Campo, 'MONITORAGGIO: Terreno umido e nutrito, condizioni ottimali') :-
    umidita_rilevata(Campo, alta),
    azoto_rilevato(Campo, ottimale).
    
% Regola 5: Intervento standard per colture a fabbisogno medio con terreno secco
azione_consigliata(Campo, 'INTERVENTO STANDARD: Avviare irrigazione moderata di routine') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, media), umidita_rilevata(Campo, bassa).

% Regola 6: Fallback per colture a basso fabbisogno idrico
azione_consigliata(Campo, 'PREVENZIONE: Coltura a basso fabbisogno idrico, ispezione visiva') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, bassa).

% Regola 7: Carenza di Azoto per colture a fabbisogno medio
azione_consigliata(Campo, 'FERTILIZZAZIONE: Carenza di Azoto, inviare drone spargiconcime') :-
    coltura_prevista(Campo, Coltura),
    necessita_azoto(Coltura, medio), azoto_rilevato(Campo, basso),
    umidita_rilevata(Campo, alta).