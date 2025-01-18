import smbus
import pyaudio
import numpy as np
import time
from typing import Tuple, Dict

class SensorManager:
    # Constantes ADXL345
    ADXL345_ADDRESS = 0x53
    POWER_CTL = 0x2D
    DATA_FORMAT = 0x31
    DATAX0 = 0x32

    def __init__(self):
        # Configuración I2C para ADXL345
        self.bus = smbus.SMBus(1)
        self.setup_accelerometer()
        
        # Configuración PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

    def setup_accelerometer(self):
        """Configura el acelerómetro ADXL345"""
        self.bus.write_byte_data(self.ADXL345_ADDRESS, self.POWER_CTL, 0x08)  # Medición
        self.bus.write_byte_data(self.ADXL345_ADDRESS, self.DATA_FORMAT, 0x08)  # ±2g

    def read_acceleration(self) -> Dict[str, float]:
        """Lee los datos del acelerómetro"""
        bytes = self.bus.read_i2c_block_data(self.ADXL345_ADDRESS, self.DATAX0, 6)
        
        x = bytes[0] | (bytes[1] << 8)
        y = bytes[2] | (bytes[3] << 8)
        z = bytes[4] | (bytes[5] << 8)
        
        # Convierte a valores con signo de 16 bits
        x = x if x < 32768 else x - 65536
        y = y if y < 32768 else y - 65536
        z = z if z < 32768 else z - 65536
        
        # Convierte a g (±2g)
        x = x * 0.004
        y = y * 0.004
        z = z * 0.004
        
        return {'x': x, 'y': y, 'z': z}

    def read_audio(self, duration: float = 1.0) -> np.ndarray:
        """Lee datos de audio durante un período específico"""
        frames = []
        for _ in range(int(44100 * duration / 1024)):
            data = self.stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.float32))
        return np.concatenate(frames)

    def cleanup(self):
        """Limpia los recursos"""
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def get_sensor_data(self, audio_duration: float = 1.0) -> Tuple[Dict[str, float], np.ndarray]:
        """Obtiene datos de ambos sensores"""
        accel_data = self.read_acceleration()
        audio_data = self.read_audio(audio_duration)
        return accel_data, audio_data 