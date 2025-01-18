from data_acquisition import SensorManager
from signal_processing import SignalProcessor
import time
import requests
import json
from typing import Dict, Any

class MotorMonitor:
    def __init__(self, thingspeak_api_key: str):
        self.sensor_manager = SensorManager()
        self.signal_processor = SignalProcessor()
        self.api_key = thingspeak_api_key
        self.thingspeak_url = f"https://api.thingspeak.com/update?api_key={self.api_key}"

    def process_and_upload_data(self) -> Dict[str, Any]:
        """Procesa y sube datos a ThingSpeak"""
        # Obtener datos de los sensores
        accel_data, audio_data = self.sensor_manager.get_sensor_data()
        
        # Procesar señales
        vibration_features = self.signal_processor.process_vibration(accel_data)
        audio_features = self.signal_processor.process_audio(audio_data)
        
        # Preparar datos para ThingSpeak
        payload = {
            'field1': vibration_features['magnitude'],
            'field2': audio_features['rms'],
            'field3': audio_features['spectral_centroid']
        }
        
        # Subir a ThingSpeak
        try:
            response = requests.get(self.thingspeak_url, params=payload)
            if response.status_code == 200:
                print("Datos subidos exitosamente")
            else:
                print(f"Error al subir datos: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión: {e}")
        
        return {**vibration_features, **audio_features}

    def run_monitoring(self, interval: float = 5.0):
        """Ejecuta el monitoreo continuo"""
        try:
            while True:
                data = self.process_and_upload_data()
                print(f"Magnitud de vibración: {data['magnitude']:.3f}g")
                print(f"RMS de audio: {data['rms']:.3f}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nDeteniendo el monitoreo...")
        finally:
            self.sensor_manager.cleanup()

if __name__ == "__main__":
    API_KEY = "TK4ZIWJ5T5TWHKJK6"
    monitor = MotorMonitor(API_KEY)
    monitor.run_monitoring() 