# GPIO Monitor für Raspberry Pi

Ein Python-Programm zur Überwachung von GPIO-Pins auf dem Raspberry Pi mit E-Mail-Benachrichtigungen und Web-Interface.

## Features

- Überwachung von 8 GPIO-Pins
- E-Mail-Benachrichtigungen bei Statusänderungen
- Webbasiertes Dashboard
- ThingSpeak Integration für Online-Monitoring
- Konfigurierbare Pin-Farben und Aktualisierungsintervalle
- Selektive E-Mail-Benachrichtigungen pro Pin

## Installation

1. Repository klonen:
```bash
git clone https://github.com/IHR_USERNAME/Portuberwachung.git
cd Portuberwachung
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. Konfiguration anpassen:
   - Öffnen Sie `config.py`
   - Tragen Sie Ihre E-Mail-Einstellungen ein
   - Konfigurieren Sie ThingSpeak API-Schlüssel
   - Passen Sie Pin-Einstellungen an

## Konfiguration

### E-Mail-Einstellungen

In `config.py` unter `EMAIL_CONFIG`:
```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'sender_email': 'ihre@email.com',
    'password': 'ihr_passwort',
    'recipient_email': 'empfaenger@email.com'
}
```

### ThingSpeak-Einstellungen

In `config.py` unter `THINGSPEAK_CONFIG`:
```python
THINGSPEAK_CONFIG = {
    'api_key': 'IHR_API_KEY',
    'channel_id': 'IHR_CHANNEL_ID',
    'update_interval': 30
}
```

### Pin-Konfiguration

Jeder Pin kann individuell konfiguriert werden:
- Name
- E-Mail-Betreff und Nachricht
- Ob E-Mails gesendet werden sollen
- Farben für verschiedene Zustände

## Verwendung

Programm starten:
```bash
python gpio_monitor.py
```

Zugriff auf das Web-Interface:
- Lokal: `http://localhost:8080`
- Netzwerk: `http://<raspberry-ip>:8080`

## Pin-Status Farben

- Grün: Aktiv (Standard)
- Gelb: Warnung
- Rot: Fehler/Kritisch
- Grau: Inaktiv

## Lizenz

MIT License