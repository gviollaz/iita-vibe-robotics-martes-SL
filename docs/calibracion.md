# 🔧 Guía de Calibración

Antes de programar cosas complejas, calibrá tu robot.
Un robot mal calibrado nunca va a andar bien.

## Orden recomendado

1. Cargar batería al 100%
2. Calibrar heading_correction (se guarda en el hub)
3. Calibrar diámetro de rueda
4. Calibrar distancia entre ejes
5. ¡Programar!

## 1. Diámetro de rueda

**Qué es**: El diámetro real de tus ruedas en milímetros.
El nominal es 56mm pero puede variar ±0.5mm.

**Cómo calibrar**:
1. Usá `codigo-ejemplo/calibracion/test-distancia.py`
2. Medí con cinta métrica la distancia real que recorrió
3. Calculá: `nuevo = 56.0 × (1000 / distancia_real_mm)`
4. Actualizá DIAMETRO_RUEDA en tu programa

**Error de 1mm** = 1.8% = 18mm por metro

## 2. Distancia entre ejes (axle track)

**Qué es**: Distancia entre los puntos de contacto de las ruedas.

**Cómo calibrar**:
1. Usá `codigo-ejemplo/calibracion/test-giro.py`
2. Marcá el frente del robot con cinta
3. Contá cuántas vueltas completas hizo
4. Calculá: `nuevo = 112.0 × (grados_reales / 3600)`

**Error de 2mm** = en 20 giros de 90° → ~32° de error total

## 3. Heading Correction del giroscopio

**Qué es**: Cada hub tiene un gyro ligeramente diferente.
Algunos reportan 357° por cada vuelta real de 360°.

**Cómo calibrar**:
1. Usá `codigo-ejemplo/calibracion/test-gyro-correction.py`
2. Girá el robot A MANO exactamente 5 vueltas
3. El programa calcula y guarda la corrección en el hub

**Sin calibrar**: ±1% = ±0.9° por giro → en 20 giros = ±18° de error
**Con calibrar**: error < 0.1° por giro

## 4. Batería

La velocidad del motor cambia con el nivel de batería.

```python
print(hub.battery.voltage())  # Full: ~8300mV, Bajo: ~6500mV
```

Calibrá siempre con batería similar a la de uso.
