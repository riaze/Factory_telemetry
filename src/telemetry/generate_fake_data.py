import json
from pathlib import Path

def create_fake_jsonl() -> None:
    """Génère un fichier .jsonl de test incluant des cas valides et corrompus."""
    
    records = [
        # Ligne 1 : Valide (Machine M1, capteur temp)
        '{"machine": "M1", "sensor": "temp", "value": 71.2, "ts": "2026-01-01T10:00:00+00:00"}',
        
        # Ligne 2 : PIÈGE (Ligne vide - doit être sautée silencieusement)
        '   ',
        
        # Ligne 3 : Valide (Machine M2, capteur vibration, format UTC alternatif Z)
        '{"machine": "M2", "sensor": "vibration", "value": 0.45, "ts": "2026-01-01T10:01:00Z"}',
        
        # Ligne 4 : PIÈGE (Texte brut - lève une json.JSONDecodeError)
        'not json',
        
        # Ligne 5 : PIÈGE (Tableau JSON vide - lève une TypeError)
        '[]',
        
        # Ligne 6 : PIÈGE (Champ manquant "ts" - lève une KeyError)
        '{"machine": "M1", "sensor": "temp", "value": 23.4}',
        
        # Ligne 7 : PIÈGE (Valeur booléenne True - doit être rejetée)
        '{"machine": "M1", "sensor": "temp", "value": true, "ts": "2026-01-01T10:02:00Z"}',
        
        # Ligne 8 : PIÈGE (Valeur infinie inf - doit être rejetée)
        '{"machine": "M1", "sensor": "temp", "value": Infinity, "ts": "2026-01-01T10:03:00Z"}',
        
        # Ligne 9 : PIÈGE (Pas de fuseau horaire dans le ts - doit être rejeté)
        '{"machine": "M3", "sensor": "pressure", "value": 101.3, "ts": "2026-01-01T10:04:00"}',
        
        # Ligne 10 : Valide (Machine M3, capteur pressure)
        '{"machine": "M3", "sensor": "pressure", "value": 98.7, "ts": "2026-01-01T10:05:00-05:00"}'
    ]
    
    # Écriture du fichier en utilisant pathlib et l'encodage imposé
    file_path = Path("fake_telemetry.jsonl")
    
    # On assemble les lignes avec des retours à la ligne
    file_path.write_text("\n".join(records) + "\n", encoding="utf-8")
    print(f"✅ Fichier de test généré avec succès : {file_path.resolve()}")

if __name__ == "__main__":
    create_fake_jsonl()
