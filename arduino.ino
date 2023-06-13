#include <Filters.h>

const int SIGNAL_PIN = A0;
const int PIN_LO_PLUS = 11;
const int PIN_LO_MINUS = 10;

const float SAMPLE_RATE = 66.67; // Frecuencia de muestreo en Hz
const float LOW_FREQ_CUTOFF = 0.2; // Frecuencia de corte inferior en Hz
const float HIGH_FREQ_CUTOFF = 40.0; // Frecuencia de corte superior en Hz
const float SCALE_FACTOR = 1.0; // Factor de escala para reducir la amplitud de la señal

FilterOnePole lowPassFilter(LOWPASS, HIGH_FREQ_CUTOFF, 1 / SAMPLE_RATE);
FilterOnePole highPassFilter(HIGHPASS, LOW_FREQ_CUTOFF, 1 / SAMPLE_RATE);

void setup() {
  Serial.begin(115200);
  
  pinMode(SIGNAL_PIN, INPUT);
  pinMode(PIN_LO_PLUS, INPUT);
  pinMode(PIN_LO_MINUS, INPUT);
  
  attachInterrupt(digitalPinToInterrupt(PIN_LO_PLUS), leadOffDetect, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_LO_MINUS), leadOffDetect, CHANGE);
}

void loop() {
  int ecgValue = analogRead(SIGNAL_PIN);

  // Aplicar el filtro pasa-banda de Butterworth
  float filteredValue = highPassFilter.input(lowPassFilter.input(ecgValue));

  // Reducir la escala de la señal
  float scaledValue = filteredValue / SCALE_FACTOR;

  // Enviar el valor escalado a través de la comunicación serial
  Serial.println(scaledValue);

  // Esperar un tiempo corto (reemplazar 10 por el tiempo de muestreo deseado en ms)
  delay(15);
}

void leadOffDetect() {
  if (digitalRead(PIN_LO_PLUS) == HIGH || digitalRead(PIN_LO_MINUS) == HIGH) {
    Serial.println("Electrodos desconectados.");
  }
}