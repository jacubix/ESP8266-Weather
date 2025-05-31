import machine
import time
import ssd1306
import network
import urequests
import ntptime

# --- Konfiguracja Wi-Fi ---
SSID = '<NAZWA SIECI WIFI>'
PASSWORD = '<HASLO SIECI WIFI'

# --- Konfiguracja OpenWeather ---
API_KEY = <WPISZ KLUCZ WEATHERAPI>'
CITY = 'Gdynia'
WEATHER_URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

# --- Słownik tłumaczeń pogody ---
weather_translation = {
    'clear sky': 'czyste niebo',
    'few clouds': 'kilka chmur',
    'scattered clouds': 'rozproszone chmury',
    'broken clouds': 'zachmurzenie',
    'shower rain': 'przelotne opady deszczu',
    'rain': 'deszcz',
    'thunderstorm': 'burza',
    'snow': 'snieg',
    'mist': 'mgla',
    'fog': 'mgla',
    'haze': 'mgla',
    'dust': 'kurz',
    'sand': 'piasek',
    'ash': 'popiol',
    'squall': 'wichura',
    'tornado': 'tornado'
}

# --- Funkcje pomocnicze ---

def connect_wifi(ssid, password):
    """Łączenie z siecią Wi-Fi."""
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print('Łączenie z Wi-Fi...')
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    print('Połączono! IP:', sta_if.ifconfig()[0])

def sync_time():
    """Synchronizacja czasu z NTP."""
    try:
        ntptime.settime()
        print('Czas NTP ustawiony.')
    except Exception as e:
        print('Błąd synchronizacji czasu NTP:', e)

def get_weather():
    """Pobiera dane pogodowe z OpenWeather."""
    try:
        response = urequests.get(WEATHER_URL)
        weather_data = response.json()
        response.close()  # Zwolnienie pamięci
        return weather_data
    except Exception as e:
        print('Błąd pobierania danych pogodowych:', e)
        return None

def display_weather(weather_data, oled):
    """Wyświetla dane pogodowe na ekranie OLED."""
    oled.fill(0)

    # Pobranie aktualnego czasu
    current_time = time.localtime()
    hours = (current_time[3] + 2) % 24  # Korekta czasu na polski (UTC+2)
    minutes = current_time[4]

    # Formatowanie godziny i minut
    time_str = f'{hours:02}:{minutes:02}'

    # Wyświetlanie godziny i miasta
    oled.text(f'{time_str} {CITY}:', 0, 0)

    # Wyświetlanie danych pogodowych
    if weather_data:
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        weather_desc = weather_data["weather"][0]["description"]

        # Tłumaczenie opisu pogody
        translated_desc = weather_translation.get(weather_desc, weather_desc)
        translated_desc = (translated_desc.replace('ś', 's')
                                          .replace('ć', 'c')
                                          .replace('ż', 'z')
                                          .replace('ń', 'n')
                                          .replace('ó', 'o')
                                          .replace('ą', 'a')
                                          .replace('ę', 'e'))

        oled.text(f'Temp: {temp} C', 0, 20)
        oled.text(f'Wilgotnosc: {humidity}%', 0, 30)
        oled.text(f'Cisn.: {pressure} hPa', 0, 40)
        oled.text(f'{translated_desc}', 0, 50)
    else:
        oled.text('Blad pobierania', 0, 20)
        oled.text('pogody', 0, 30)

    oled.show()

# --- Program główny ---

def main():
    # Połączenie Wi-Fi
    connect_wifi(SSID, PASSWORD)

    # Synchronizacja czasu
    sync_time()

    # Inicjalizacja wyświetlacza OLED
    i2c = machine.I2C(scl=machine.Pin(12), sda=machine.Pin(14))  # D5, D6
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    # Główna pętla
    while True:
        weather_data = get_weather()
        display_weather(weather_data, oled)
        time.sleep(10)  # Aktualizacja co 10 sekund

# --- Start programu ---
main()
