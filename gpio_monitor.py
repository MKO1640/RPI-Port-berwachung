import RPi.GPIO as GPIO
import smtplib
from email.mime.text import MIMEText
import time
import requests
from config import EMAIL_CONFIG, PIN_CONFIG, THINGSPEAK_CONFIG
import logging
from threading import Thread
from flask import Flask, render_template, jsonify
from datetime import datetime
from collections import defaultdict

# Flask App initialisieren
app = Flask(__name__)

# Globale Variablen für Pin-Status und letzte Änderungen
pin_states = {}
last_changes = defaultdict(str)

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='gpio_monitor.log'
)

def setup_gpio():
    """GPIO initialisieren"""
    GPIO.setmode(GPIO.BCM)
    for pin in PIN_CONFIG.keys():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pin_states[pin] = GPIO.input(pin)  # Initialen Status speichern
        logging.info(f"Pin {pin} ({PIN_CONFIG[pin]['name']}) initialisiert")

def send_email(subject, message):
    """E-Mail versenden"""
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']

        # SMTP-Verbindung aufbauen
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['password'])
            server.send_message(msg)
        
        logging.info(f"E-Mail versendet: {subject}")
    except Exception as e:
        logging.error(f"Fehler beim E-Mail-Versand: {str(e)}")

def pin_changed(pin):
    """Callback-Funktion für Pin-Änderungen"""
    pin_state = GPIO.input(pin)
    pin_config = PIN_CONFIG[pin]
    # Status und Zeitstempel aktualisieren
    pin_states[pin] = pin_state
    last_changes[pin] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    logging.info(f"Statusänderung an Pin {pin} ({pin_config['name']}): {pin_state}")
    
    # E-Mail nur senden, wenn für diesen Pin aktiviert
    if pin_config.get('send_email', True):
        message = f"{pin_config['message']} Neuer Status: {'HIGH' if pin_state else 'LOW'}"
        send_email(pin_config['subject'], message)

def update_thingspeak():
    """Aktualisiert ThingSpeak mit dem aktuellen Pin-Status"""
    while True:
        try:
            # Sammle den Status aller Pins
            pin_states = {pin: GPIO.input(pin) for pin in PIN_CONFIG.keys()}
            
            # Bereite die Daten für ThingSpeak vor
            data = {f'field{i+1}': int(state) 
                   for i, (_, state) in enumerate(pin_states.items())}
            data['api_key'] = THINGSPEAK_CONFIG['api_key']
            
            # Sende Daten an ThingSpeak
            response = requests.post(
                f'https://api.thingspeak.com/update',
                data=data
            )
            
            if response.status_code == 200:
                logging.info("ThingSpeak erfolgreich aktualisiert")
            else:
                logging.error(f"ThingSpeak Fehler: Status {response.status_code}")
                
        except Exception as e:
            logging.error(f"Fehler bei ThingSpeak Update: {str(e)}")
            
        time.sleep(THINGSPEAK_CONFIG['update_interval'])

# Flask Routen
@app.route('/')
def index():
    """Hauptseite anzeigen"""
    # Erstelle ein Dictionary mit den aktuellen Pin-Farben
    pin_colors = {}
    for pin, state in pin_states.items():
        color_state = PIN_CONFIG[pin]['status_color'][state]
        pin_colors[pin] = color_state

    return render_template('index.html', 
                         pins=PIN_CONFIG, 
                         pin_states=pin_states,
                         pin_colors=pin_colors,
                         last_changes=last_changes,
                         config=globals())

@app.route('/api/pin-states')
def get_pin_states():
    """API-Endpunkt für Pin-Status"""
    # Erstelle ein Dictionary mit den aktuellen Pin-Farben
    pin_colors = {}
    for pin, state in pin_states.items():
        color_state = PIN_CONFIG[pin]['status_color'][state]
        pin_colors[pin] = color_state

    return jsonify({
        'pin_states': pin_states,
        'last_changes': last_changes,
        'pin_colors': pin_colors
    })

def start_flask():
    """Flask-Server starten"""
    app.run(host='0.0.0.0', port=8080)

def main():
    """Hauptprogramm"""
    try:
        setup_gpio()
        logging.info("GPIO-Überwachung gestartet")

        # Event Detection für jeden Pin einrichten
        for pin in PIN_CONFIG.keys():
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_changed, bouncetime=300)

        # Starte ThingSpeak Update Thread
        thingspeak_thread = Thread(target=update_thingspeak, daemon=True)
        thingspeak_thread.start()
        logging.info("ThingSpeak Überwachung gestartet")

        # Starte Flask Webserver
        flask_thread = Thread(target=start_flask, daemon=True)
        flask_thread.start()
        logging.info("Webserver gestartet auf http://0.0.0.0:8080")

        # Programm am Laufen halten
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Programm durch Benutzer beendet")
    except Exception as e:
        logging.error(f"Unerwarteter Fehler: {str(e)}")
    finally:
        GPIO.cleanup()
        logging.info("GPIO aufgeräumt")

if __name__ == "__main__":
    main()