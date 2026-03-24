# 🧭 Guía Definitiva del Giroscopio — Pybricks + Spike Prime
## Para competencia: FLL, WRO, RoboCup Junior

---

## 1. CÓMO FUNCIONA EL GYRO

El Spike Prime tiene un IMU con giroscopio 3 ejes + acelerómetro 3 ejes. El gyro mide **velocidad angular** (°/s), NO ángulos directamente. Pybricks integra esa velocidad en el tiempo para estimar el ángulo. Cualquier error se **acumula**.

### Fuentes de error

| Fuente | Descripción | Impacto |
|--------|-------------|---------|
| **Bias** | Reporta velocidad ≠0 estando quieto | 0.5-3 °/s |
| **Scale error** | Cada hub ±1% diferente para 360° | ±3.6°/vuelta |
| **Drift térmico** | Bias cambia con temperatura | Peor en frío |
| **Vibración** | Motores afectan lecturas | Variable |

**Benchmark** (Instructables 2025): Error promedio 10 giros 90°: Pybricks 8.6°, SPIKE App 9.6°, Word Blocks 17.1°.

---

## 2. INICIALIZACIÓN CORRECTA

```python
# 1. LED rojo = no tocar
hub.light.on(Color.RED)

# 2. Motores en coast (no vibran → permite calibración)
motor_izq.stop()
motor_der.stop()

# 3. Esperar calibración automática (MEJOR que wait fijo)
while not hub.imu.ready():
    wait(100)

# 4. Reset heading UNA SOLA VEZ
hub.imu.reset_heading(0)
wait(500)

# 5. Activar gyro en DriveBase
robot.use_gyro(True)

# 6. LED verde = listo
hub.light.on(Color.GREEN)
```

### ¿Por qué `hub.imu.ready()` y no `wait(1500)`?

`ready()` retorna True cuando el hub confirmó quietud y completó calibración. `wait(1500)` es fijo y puede no ser suficiente si alguien tocó el robot justo antes. `ready()` es False si el hub acaba de encenderse, alguien lo movió, o no calibró en >10 min.

### Auto-calibración continua (v3.6+)

Pybricks auto-recalibra el bias cuando el hub está quieto >1 segundo. **Condiciones**: todos los motores en coast (no hold), vibraciones debajo del umbral. Entre misiones FLL, si el robot está quieto esperando cambio de attachment, el gyro se recalibra solo.

### Umbrales para halls ruidosos

```python
# Default: angular_velocity_threshold=2, acceleration_threshold=2500
# En competencia ruidosa:
hub.imu.settings(
    angular_velocity_threshold=4,
    acceleration_threshold=3500,
)
# Verificar: hub.imu.stationary() debe ser True quieto, False moviéndose
```

---

## 3. heading_correction — CALIBRACIÓN DE ESCALA

Cada hub tiene ±1% de error de escala. Sin calibrar: 20 giros × 90° = ±18° error.

### Programa de calibración (correr UNA VEZ por hub)

```python
from pybricks.hubs import PrimeHub
from pybricks.parameters import Axis, Button, Color
from pybricks.tools import wait

hub = PrimeHub()
hub.imu.reset_heading(0)
wait(2000)

hub.display.text("5x")
hub.light.on(Color.YELLOW)
hub.speaker.beep(800, 300)

# Girar robot A MANO 5 vueltas completas, volver a posición inicial
# Apretar botón central
while Button.CENTER not in hub.buttons.pressed():
    wait(50)
wait(500)

raw = hub.imu.rotation(-Axis.Z, calibrated=False)
correction = raw / 5.0
hub.imu.settings(heading_correction=correction)

hub.display.number(int(correction))
hub.light.on(Color.GREEN)
print("Saved:", correction, "°/turn")  # Debe ser ~360
```

Se guarda en flash del hub. Persiste hasta cambio de firmware.

**Calibración 3D completa** (v3.6+): `import _imu_calibrate` en REPL — calibra acelerómetro + gyro en 3 ejes rotando el hub.

---

## 4. NUNCA RESETEAR DURANTE COMPETENCIA

### El patrón correcto: heading absoluto

```python
# ✅ CORRECTO
hub.imu.reset_heading(0)  # UNA VEZ al inicio
for i in range(20):  # 5 vueltas
    avanzar(1000)
    girar_pid((i + 1) * 90)  # 90, 180, 270... 1800

# ❌ INCORRECTO
for i in range(20):
    avanzar(1000)
    hub.imu.reset_heading(0)  # Cada reset = incertidumbre
    girar_pid(90)              # Errores se acumulan random
```

### Excepción: entre RUNS de FLL

```python
def iniciar_run():
    robot.stop()
    hub.light.on(Color.RED)
    motor_izq.stop()  # Coast para permitir recalibración
    motor_der.stop()
    while not hub.imu.ready():
        wait(100)
    hub.imu.reset_heading(0)
    wait(500)
    robot.use_gyro(True)
    hub.light.on(Color.GREEN)
```

### reset_heading() vs robot.reset()

- `hub.imu.reset_heading(0)`: solo heading. NO se puede llamar mientras DriveBase está activo → OSError.
- `robot.reset()`: detiene robot + resetea distancia + heading. Seguro siempre.

---

## 5. AVANCE RECTO CON GYRO

### Método 1: `robot.straight()` (simple, bueno)

```python
robot.use_gyro(True)
robot.straight(1000)  # DriveBase corrige heading automáticamente
```

### Método 2: `robot.drive()` (velocidad variable)

```python
robot.drive(300, 0)  # 300 mm/s, turn_rate=0 → gyro corrige
```

### Método 3: PID manual (máximo control)

```python
def avanzar_pid(dist_mm, heading_target, vel_max=370):
    KP_H = 3.0
    motor_izq.reset_angle(0); motor_der.reset_angle(0)
    while True:
        dist = (abs(motor_izq.angle()) + abs(motor_der.angle())) / 2.0 * MM_PER_DEG
        if dist_mm - dist <= 2.0: break
        vel = min((2*300*max(dist,0.5))**0.5, (2*500*max(dist_mm-dist,0.5))**0.5, vel_max)
        h_err = heading_target - hub.imu.heading()
        correction = KP_H * h_err
        robot.drive(vel, correction)
        wait(10)
    robot.stop()
```

### Frecuencia de lectura del gyro

| Hz | wait() | Uso |
|:--:|:------:|-----|
| 100 | 10ms | PID giro/recta (RECOMENDADO) |
| 50 | 20ms | Line following |
| 20 | 50ms | Monitoreo simple |

El chip IMU muestrea a ~100 Hz. Más rápido no tiene sentido.

---

## 6. GIROS CON GYRO

### robot.turn() vs PID manual

| | robot.turn(90) | PID sobre heading() |
|---|:-:|:-:|
| Precisión | ±2-3° | ±0.5° |
| Depende de axle_track | Sí | No |
| Complejidad | Mínima | Media |

### PID de giro competition-grade

```python
def girar_pid(heading_objetivo):
    KP, KI, KD = 6.0, 0.15, 8.0
    MAX_RATE = 500; SETTLE_ERR = 0.7; SETTLE_N = 5
    h = hub.imu.heading()
    err_prev = heading_objetivo - h
    integral = 0.0; settled = 0; reloj = StopWatch()
    while True:
        h = hub.imu.heading()
        err = heading_objetivo - h
        p = KP * err
        if abs(err) < 15:
            integral = clamp(integral + KI * err, -30, 30)
        else:
            integral *= 0.3
        d = KD * (err - err_prev); err_prev = err
        out = clamp(p + integral + d, -MAX_RATE, MAX_RATE)
        if abs(err) < SETTLE_ERR and abs(out) < 5: out = 0
        robot.drive(0, out)
        if abs(err) < SETTLE_ERR:
            settled += 1
            if settled >= SETTLE_N: break
        else: settled = 0
        if reloj.time() > 2000: break
        wait(10)
    robot.stop()
```

### ¿Por qué settle de 5 ciclos?

El gyro tiene ruido. Puede pasar por 0.5° un instante sin haberse estabilizado. 5 ciclos (50ms) confirma que realmente se detuvo.

### El integral: solo cerca del target

Si acumula durante todo el giro → overshoot masivo (windup). Solo acumular cuando `abs(error) < 15°`. Anti-windup: clamp a ±30. Decay: `integral *= 0.3` cuando estamos lejos.

---

## 7. TROUBLESHOOTING

| Problema | Causa | Solución |
|----------|-------|----------|
| Se desvía en straight() | Vel >85% max | Bajar a 350-370 mm/s |
| Giros acumulan error | heading_correction no calibrado | Calibrar (sección 3) |
| Giros acumulan error | Reseteando heading cada giro | Heading absoluto (sección 4) |
| Drift estando quieto | No esperó calibración | Usar hub.imu.ready() |
| Drift estando quieto | Motor hold vibra | Motores en coast cuando quieto |
| Drift en hall ruidoso | Umbrales muy bajos | Subir a threshold=4 |
| OSError en reset_heading | DriveBase activo con gyro | robot.stop() primero |
| Heading mal al posar robot | Solo funciona plano | hub.imu.heading('3D') experimental |

---

## 8. CHECKLIST COMPETENCIA

### Una vez por hub:
- [ ] heading_correction calibrado (5 vueltas)
- [ ] _imu_calibrate 3D (opcional, máxima precisión)
- [ ] Firmware Pybricks v3.6+

### Cada sesión:
- [ ] Batería >7200 mV
- [ ] Robot quieto al encender, esperar ready()
- [ ] Test 360° → vuelve al mismo lugar

### Día de competencia:
- [ ] NO resetear heading durante un run
- [ ] Resetear SOLO al inicio de cada run
- [ ] Hall ruidoso → subir angular_velocity_threshold
- [ ] LED rojo/verde para que el equipo sepa cuándo NO tocar

---

## Fuentes

Pybricks v3.6.1 Docs, Issues #933/#989/#1032/#1678/#1907, Discussions #675/#1329/#1595, Instructables benchmark 2025, Pybricks v3.6.0 Release Notes.
