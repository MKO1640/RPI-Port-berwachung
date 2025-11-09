# E-Mail Konfiguration
# Webinterface Konfiguration
WEB_CONFIG = {
    'update_interval': 5,  # Aktualisierungsintervall der Weboberfläche in Sekunden
    'pin_colors': {
        'active': '#4CAF50',    # Grün für aktive Pins
        'warning': '#FFC107',   # Gelb für Warnungen
        'error': '#F44336',     # Rot für Fehler/kritische Zustände
        'inactive': '#9E9E9E'   # Grau für inaktive Pins
    }
}

# E-Mail Konfiguration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.example.com',  # SMTP Server
    'smtp_port': 587,                   # SMTP Port (587 for STARTTLS, 465 for SSL)
    'use_tls': True,                    # Wenn True, benutzt STARTTLS (port 587)
    'use_ssl': False,                   # Wenn True, benutzt smtplib.SMTP_SSL (port 465)
    'sender_email': 'your@email.com',   # Absender E-Mail
    'password': 'your_password',        # E-Mail Passwort oder App-Passwort
    'recipient_email': 'recipient@email.com'  # Empfänger E-Mail
}

# ThingSpeak Konfiguration
THINGSPEAK_CONFIG = {
    'api_key': 'YOUR_WRITE_API_KEY',    # ThingSpeak Write API Key
    'channel_id': 'YOUR_CHANNEL_ID',    # ThingSpeak Channel ID
    'update_interval': 30               # Update-Intervall in Sekunden
}

# GPIO Pin Konfiguration
PIN_CONFIG = {
    17: {
        'name': 'Pin 1',
        'subject': 'Warnung: Status Pin 1 geändert',
        'message': 'Der Status von Pin 1 hat sich geändert.',
        'send_email': True,     # E-Mail bei Statusänderung senden
        'status_color': {
            True: 'active',     # Farbe wenn Pin aktiv (HIGH)
            False: 'inactive'   # Farbe wenn Pin inaktiv (LOW)
        }
    },
    18: {
        'name': 'Pin 2',
        'subject': 'Warnung: Status Pin 2 geändert',
        'message': 'Der Status von Pin 2 hat sich geändert.',
        'send_email': True,
        'status_color': {
            True: 'warning',    # Beispiel: Dieser Pin verwendet Gelb wenn aktiv
            False: 'inactive'
        }
    },
    27: {
        'name': 'Pin 3',
        'subject': 'Warnung: Status Pin 3 geändert',
        'message': 'Der Status von Pin 3 hat sich geändert.',
        'send_email': False,    # Keine E-Mail bei Statusänderung
        'status_color': {
            True: 'error',      # Beispiel: Dieser Pin verwendet Rot wenn aktiv
            False: 'inactive'
        }
    },
    22: {
        'name': 'Pin 4',
        'subject': 'Warnung: Status Pin 4 geändert',
        'message': 'Der Status von Pin 4 hat sich geändert.',
        'send_email': True,
        'status_color': {
            True: 'active',
            False: 'inactive'
        }
    },
    23: {
        'name': 'Pin 5',
        'subject': 'Warnung: Status Pin 5 geändert',
        'message': 'Der Status von Pin 5 hat sich geändert.',
        'send_email': True,
        'status_color': {
            True: 'active',
            False: 'inactive'
        }
    },
    24: {
        'name': 'Pin 6',
        'subject': 'Warnung: Status Pin 6 geändert',
        'message': 'Der Status von Pin 6 hat sich geändert.',
        'send_email': True,
        'status_color': {
            True: 'active',
            False: 'inactive'
        }
    },
    25: {
        'name': 'Pin 7',
        'subject': 'Warnung: Status Pin 7 geändert',
        'message': 'Der Status von Pin 7 hat sich geändert.',
        'send_email': True,
        'status_color': {
            True: 'active',
            False: 'inactive'
        }
    },
    4: {
        'name': 'Pin 8',
        'subject': 'Warnung: Status Pin 8 geändert',
        'message': 'Der Status von Pin 8 hat sich geändert.',
        'send_email': True,
        'status_color': {
            True: 'active',
            False: 'inactive'
        }
    }
}

# Steuerbare Ausgänge (über Webinterface schaltbar)
# Tragen Sie hier die Pins ein, die Sie per Web einschalten möchten.
# Beispiel: drei Relais an GPIO 5, 6 und 13
CONTROL_PINS = {
    5: {
        'name': 'Relais 1',
        'initial': False
    },
    6: {
        'name': 'Relais 2',
        'initial': False
    },
    13: {
        'name': 'Relais 3',
        'initial': False
    }
}