#include <arduinoFFT.h>

#define LEFT_EAR 4  // GPIO4 (D2 on ESP32)
#define RIGHT_EAR 2 // GPIO2 (D4 on ESP32)
const uint16_t samples = 64; // Number of samples
const float samplingFrequency = 50; // Hz
unsigned int sampling_period_us;
unsigned long microseconds;
const float noiseThreshold = 10.0; // Adjust based on your noise level

ArduinoFFT<float> FFT; // Use float instead of double

float vReal_left[samples];
float vImag_left[samples];

float vReal_right[samples];
float vImag_right[samples];

void setup() {
  sampling_period_us = round(1000000 * (1.0 / samplingFrequency));
  Serial.begin(115200);
  calibrateBaseline();
}

void loop() {
  /* SAMPLING */
  microseconds = micros();
  for (int i = 0; i < samples; i++) {
    vReal_left[i] = analogRead(LEFT_EAR) - 512.0; // modified for zero balance
    vReal_right[i] = analogRead(RIGHT_EAR) - 512.0; // modified for zero balance
    vImag_left[i] = 0;
    vImag_right[i] = 0;
    while (micros() - microseconds < sampling_period_us) {
      // empty loop
    }
    microseconds += sampling_period_us;
  }

  /* PROCESSING LEFT EAR */
  FFT.windowing(vReal_left, samples, FFT_WIN_TYP_HAMMING, FFT_FORWARD); /* Weigh data */
  FFT.compute(vReal_left, vImag_left, samples, FFT_FORWARD); /* Compute FFT */
  FFT.complexToMagnitude(vReal_left, vImag_left, samples); /* Compute magnitudes */

  /* PROCESSING RIGHT EAR */
  FFT.windowing(vReal_right, samples, FFT_WIN_TYP_HAMMING, FFT_FORWARD); /* Weigh data */
  FFT.compute(vReal_right, vImag_right, samples, FFT_FORWARD); /* Compute FFT */
  FFT.complexToMagnitude(vReal_right, vImag_right, samples); /* Compute magnitudes */

  /* CALCULATE POWER IN FREQUENCY BANDS */
  float alpha_power_left = 0;
  float beta_power_left = 0;
  float alpha_power_right = 0;
  float beta_power_right = 0;

  for (int i = 0; i < (samples >> 1); i++) {
    float frequency = i * (samplingFrequency / samples);
    if (frequency >= 8 && frequency <= 12) {
      alpha_power_left += vReal_left[i] * vReal_left[i];
      alpha_power_right += vReal_right[i] * vReal_right[i];
    } else if (frequency >= 13 && frequency <= 30) {
      beta_power_left += vReal_left[i] * vReal_left[i];
      beta_power_right += vReal_right[i] * vReal_right[i];
    }
  }

  /* CALCULATE ATTENTION/FOCUS LEVEL */
  float attention_left = (beta_power_left > noiseThreshold) ? beta_power_left / alpha_power_left : 0;
  float attention_right = (beta_power_right > noiseThreshold) ? beta_power_right / alpha_power_right : 0;

  /* PRINT RESULTS */
  Serial.print("Attention_Left:");
  Serial.print(attention_left, 2);
  Serial.print("\t");
  Serial.print("Attention_Right:");
  Serial.println(attention_right, 2);

  //delay(2000); /* Repeat after delay */
}

void calibrateBaseline() {
  float leftSum = 0;
  float rightSum = 0;
  const int calibrationSamples = 100;
  
  for (int i = 0; i < calibrationSamples; i++) {
    leftSum += analogRead(LEFT_EAR);
    rightSum += analogRead(RIGHT_EAR);
    delay(10);
  }

  float baselineLeft = leftSum / calibrationSamples;
  float baselineRight = rightSum / calibrationSamples;

  for (int i = 0; i < samples; i++) {
    vReal_left[i] = baselineLeft - 512.0;
    vReal_right[i] = baselineRight - 512.0;
  }
}
