import RPi.GPIO as GPIO
import smtplib
from email.mime.text import MIMEText
import time
import requests
import config
from config import EMAIL_CONFIG, PIN_CONFIG, THINGSPEAK_CONFIG, CONTROL_PINS
import logging
from threading import Thread
from threading import Lock
from flask import Flask, render_template, jsonify
from datetime import datetime
from collections import defaultdict

# Flask App initialisieren
app = Flask(__name__)

# Globale Variablen für Pin-Status und letzte Änderungen
pin_states = {}
last_changes = defaultdict(str)
# Steuerbare Ausgänge Status
control_states = {}

# Lock für thread-sicheren Zugriff auf pin_states/last_changes
pin_lock = Lock()

# Pins, für die Event-Detection nicht möglich war und deshalb polled werden
polling_pins = set()

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
    # Setup für steuerbare Ausgänge
    for pin, info in CONTROL_PINS.items():
        try:
            GPIO.setup(pin, GPIO.OUT)
            initial = bool(info.get('initial', False))
            GPIO.output(pin, initial)
            control_states[pin] = initial
            logging.info(f"Control-Pin {pin} ({info.get('name')}) als OUTPUT initialisiert (state={initial})")
        except Exception as e:
            logging.error(f"Fehler beim Initialisieren von Control-Pin {pin}: {e}")

def send_email(subject, message):
    """E-Mail versenden"""
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        # SMTP-Verbindung aufbauen (unterstützt SSL oder STARTTLS je nach config)
        smtp_server = EMAIL_CONFIG.get('smtp_server')
        smtp_port = EMAIL_CONFIG.get('smtp_port')
        use_ssl = EMAIL_CONFIG.get('use_ssl', False)
        use_tls = EMAIL_CONFIG.get('use_tls', True)

        if use_ssl:
            logging.info('Verwende SMTP_SSL für E-Mail-Versand')
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['password'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['password'])
                server.send_message(msg)
        
        logging.info(f"E-Mail versendet: {subject}")
    except Exception as e:
        logging.error(f"Fehler beim E-Mail-Versand: {str(e)}")

def pin_changed(pin):
    """Callback-Funktion für Pin-Änderungen"""
    pin_state = GPIO.input(pin)
    pin_config = PIN_CONFIG[pin]
    # Status und Zeitstempel aktualisieren (thread-sicher)
    with pin_lock:
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
            # Sammle den Status aller Pins (lokal, ohne globales Überschreiben)
            pin_values = {pin: GPIO.input(pin) for pin in PIN_CONFIG.keys()}
            
            # Option: Aktualisiere globalen Status (thread-sicher)
            with pin_lock:
                for pin, v in pin_values.items():
                    pin_states[pin] = v

            # Bereite die Daten für ThingSpeak vor
            data = {f'field{i+1}': int(state) 
                   for i, (_, state) in enumerate(pin_values.items())}
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
                         config=config)

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
        , 'control_states': control_states
    })


@app.route('/api/control', methods=['POST'])
def control_pin():
    """Setzt einen steuerbaren Pin auf 0/1 via JSON payload {"pin": 5, "state": 1} """
    try:
        data = None
        # Flask's request isn't imported at module top to avoid circular imports in tests; import locally
        from flask import request
        data = request.get_json(force=True)
        pin = int(data.get('pin'))
        state = bool(int(data.get('state')))
    except Exception as e:
        logging.error(f"Ungültige Steuer-Anfrage: {e}")
        return jsonify({'ok': False, 'error': 'invalid payload'}), 400

    if pin not in CONTROL_PINS:
        return jsonify({'ok': False, 'error': 'pin not controllable'}), 400

    try:
        GPIO.output(pin, state)
        with pin_lock:
            control_states[pin] = state
        logging.info(f"Control-Pin {pin} gesetzt auf {int(state)}")
        return jsonify({'ok': True, 'pin': pin, 'state': int(state)})
    except Exception as e:
        logging.error(f"Fehler beim Setzen von Pin {pin}: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

def start_flask():
    """Flask-Server starten"""
    app.run(host='0.0.0.0', port=8080)


def poll_pins(interval=0.5):
    """Pollt Pins, für die kein Edge-Detection verfügbar war."""
    logging.info(f"Polling-Thread gestartet für Pins: {sorted(polling_pins)}")
    while True:
        try:
            with pin_lock:
                # Erzeuge eine Kopie der aktuellen polling_pins
                pins_to_check = list(polling_pins)
            # Prüfe außerhalb der Sperre
            for pin in pins_to_check:
                current = GPIO.input(pin)
                with pin_lock:
                    prev = pin_states.get(pin)
                if prev is None:
                    with pin_lock:
                        pin_states[pin] = current
                    continue
                if current != prev:
                    try:
                        pin_changed(pin)
                    except Exception as e:
                        logging.error(f"Fehler im Polling handler für Pin {pin}: {e}")
        except Exception as e:
            logging.error(f"Polling-Thread Fehler: {e}")
        time.sleep(interval)

def main():
    """Hauptprogramm"""
    try:
        setup_gpio()
        logging.info("GPIO-Überwachung gestartet")

        # Event Detection für jeden Pin einrichten (mit Fallback auf Polling)
        for pin in PIN_CONFIG.keys():
            try:
                GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_changed, bouncetime=300)
            except Exception as e:
                # Edge detection konnte nicht hinzugefügt werden -> Polling als Fallback
                logging.error(f"Failed to add edge detection for pin {pin}: {e}")
                polling_pins.add(pin)

        # Starte ThingSpeak Update Thread
        thingspeak_thread = Thread(target=update_thingspeak, daemon=True)
        thingspeak_thread.start()
        logging.info("ThingSpeak Überwachung gestartet")

        # Starte Flask Webserver
        flask_thread = Thread(target=start_flask, daemon=True)
        flask_thread.start()
        logging.info("Webserver gestartet auf http://0.0.0.0:8080")

        # Starte Polling-Thread, falls nötig
        if polling_pins:
            poll_thread = Thread(target=poll_pins, daemon=True)
            poll_thread.start()
            logging.info(f"Polling-Thread gestartet für Pins: {sorted(polling_pins)}")

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