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
    'use_tls': True,    # True für STARTTLS (Port 587)
    'use_ssl': False,   # True für SSL (Port 465)
    'sender_email': 'ihre@email.com',
    'password': 'ihr_passwort',
    'recipient_email': 'empfaenger@email.com'
}
```

Hinweis für Gmail:
- Verwenden Sie `smtp.gmail.com` als `smtp_server`.
- Für STARTTLS (empfohlen) setzen Sie `smtp_port` auf `587` und `use_tls=True`.
- Für SSL setzen Sie `smtp_port` auf `465` und `use_ssl=True`.
- Google blockiert häufig direkte SMTP-Zugriffe; wenn Sie 2‑Faktor‑Authentifizierung (2FA) verwenden, erstellen Sie ein "App-Passwort" in Ihrem Google-Konto und verwenden dieses hier als `password`.
- Wenn Sie kein App-Passwort haben, kann der Login fehlschlagen (Google hat die Option für "weniger sichere Apps" abgeschafft). Siehe: https://support.google.com/accounts/answer/185833

Beispiel für Gmail mit STARTTLS:
```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'use_ssl': False,
    'sender_email': 'me@gmail.com',
    'password': 'APP_PASSWORD',
    'recipient_email': 'you@example.com'
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

### Manueller Start

```bash
python gpio_monitor.py
```

Zugriff auf das Web-Interface:
- Lokal: `http://localhost:8080`
- Netzwerk: `http://<raspberry-ip>:8080`

### Installation als System Service

Für automatischen Start beim Booten:

```bash
# Erstelle Installationsverzeichnis
sudo mkdir -p /opt/gpio-monitor

# Kopiere Projektdateien
sudo cp -r * /opt/gpio-monitor/

# Installiere Service
sudo cp gpio-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gpio-monitor
sudo systemctl start gpio-monitor
```

Service Status prüfen:
```bash
sudo systemctl status gpio-monitor
```

Log anzeigen:
```bash
sudo journalctl -u gpio-monitor -f
```

## Pin-Status Farben

- Grün: Aktiv (Standard)
- Gelb: Warnung
- Rot: Fehler/Kritisch
- Grau: Inaktiv

## Lizenz

MIT License