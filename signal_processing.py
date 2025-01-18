import numpy as np
from scipy import signal
import librosa
from typing import Dict, Any

class SignalProcessor:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process_vibration(self, accel_data: Dict[str, float]) -> Dict[str, float]:
        """Procesa datos de vibración"""
        # Calcula la magnitud total de la vibración
        magnitude = np.sqrt(
            accel_data['x']**2 + 
            accel_data['y']**2 + 
            accel_data['z']**2
        )
        
        return {
            'magnitude': magnitude,
            'x_accel': accel_data['x'],
            'y_accel': accel_data['y'],
            'z_accel': accel_data['z']
        }

    def process_audio(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Procesa datos de audio"""
        # Calcula el espectrograma
        D = librosa.stft(audio_data)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # Calcula características de audio
        rms = librosa.feature.rms(y=audio_data)[0]
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)[0]
        
        # FFT para análisis de frecuencia
        fft = np.fft.fft(audio_data)
        freq = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        
        return {
            'rms': np.mean(rms),
            'spectral_centroid': np.mean(spectral_centroid),
            'fft': fft,
            'frequencies': freq,
            'spectrogram': S_db
        } 