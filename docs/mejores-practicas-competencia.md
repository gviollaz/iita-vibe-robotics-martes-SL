# 🏆 Mejores Prácticas para Robótica de Competencia

## Guía completa para FLL, WRO, y RoboCup Junior
### Investigación compilada — Marzo 2026

---

## PARTE 1: DISEÑO MECÁNICO

### 1.1 Centro de gravedad

El factor #1 de consistencia es que el centro de gravedad esté sobre o ligeramente detrás del eje de las ruedas motrices. Equipos campeones de FLL reportan que cuando el peso estaba adelante, los giros eran imprecisos. Al mover los motores al centro, la precisión mejoró.

**Reglas**: CG sobre el eje = giros precisos. Peso adelante = pivota mal. Peso atrás = rueda loca frena. Al agregar attachments, verificar que el CG no se mueva.

### 1.2 Box Robots (FLLCasts)

Chasis compactos tipo caja para máxima repetibilidad: forma rectangular, attachments modulares que se deslizan por arriba, motores cerca del centro, sensores de color adelante de las ruedas. Ejemplos: Kriket, Boxver, Whakatae (17x15 unidades LEGO).

### 1.3 Attachments modulares

Un robot, múltiples attachments intercambiables. Diseñar "pinless" para cambio rápido (<5 seg). Usar deslizamiento sobre rieles. Cada attachment = 1-3 misiones. Rubber bands para bloqueo/liberación.

### 1.4 Rueda loca

Ball caster (no rueda fija), lo más atrás posible, verificar que no se trabe.

---

## PARTE 2: PROGRAMACIÓN FUNDAMENTOS

### 2.1 Arquitectura de código

Equipos top: main.py (menú), base_robot.py (config), mission_N.py (cada misión), utils.py (PID, alineación). Auto-avanzar entre misiones ahorra 5-10 segundos. Equipo campeón: 650 líneas, ~200 ejecutables, 80% comentarios, VS Code + GitHub.

### 2.2 Velocidad vs Precisión

Pybricks default = 40% max. Equipos competitivos = 80%. NUNCA 100%. Aceleración: reducir a 50% del default para robots pesados.

### 2.3 Giroscopio

Cada hub tiene ±1% error de escala. Calibrar heading_correction: girar 5 vueltas a mano, leer rotation(-Axis.Z, calibrated=False), dividir por 5, guardar en hub. En halls ruidosos: subir angular_velocity_threshold a 3-4.

### 2.4 Consistencia es Rey

"Consistencia > velocidad. 5 misiones confiables > 8 que fallan la mitad." Técnicas: alineación a pared, alineación a línea con 2 sensores, posición de inicio exacta, mismo nivel de batería, reducir velocidad en puntos críticos.

---

## PARTE 3: TÉCNICAS AVANZADAS

### 3.1 PID Tuning — Método de 5 pasos

1. Kp=Ki=Kd=0. 2. Subir Kp hasta oscilar. 3. Reducir Kp al 70%. 4. Subir Kd hasta que oscilación pare. 5. Agregar Ki pequeño si queda error.

Valores iniciales: Giro=Kp6/Ki0.15/Kd8. Line follow 1 sensor=Kp2/Ki0.05/Kd10. Line follow 2 sensores=Kp1/Ki0.02/Kd5.

### 3.2 Seguimiento de línea

1 sensor: `error = sensor.reflection() - TARGET`. 2 sensores: `error = izq.reflection() - der.reflection()`. Velocidad adaptativa: `vel = VEL_MAX - abs(error) * FACTOR`.

### 3.3 Alineación a línea (squaring)

Avanzar hasta que un sensor detecte línea. Girar lento hasta que el segundo también la detecte. Resultado: robot perpendicular a la línea.

### 3.4 Alineación a pared

Retroceder con robot.drive(-100, 0) hasta robot.stalled(). Luego robot.reset() para resetear encoders y heading.

### 3.5 Máquinas de estado

Para WRO/RoboCup: definir estados (BUSCAR, SEGUIR, DETECTAR, ACTUAR, VOLVER). Loop principal con switch de estados. Cada estado transiciona al siguiente según condiciones de sensores.

### 3.6 Multitasking (v3.3+)

```python
async def mision():
    await multitask(robot.straight(500), brazo.run_angle(300, 180))
run_task(mision())
```

### 3.7 Perfil trapezoidal

Aceleración suave (250-350 mm/s²), crucero a 80% max, frenada agresiva (500-600 mm/s²). Fórmula: v = sqrt(2 * accel * distancia).

---

## PARTE 4: POR COMPETENCIA

### 4.1 FLL

2:30 min/ronda. 4-5 runs con cambio de attachment. Auto-avanzar entre runs. Priorizar alto puntaje + baja complejidad. Timeout por misión. Plan B siempre.

### 4.2 WRO

Robot max 250x250x250mm. Line following PID esencial. Reglas sorpresa. Detección de color con calibración in-situ. Máquinas de estado. Arrays para secuencias de colores. Robot debe ser reconstruido en cuarentena.

### 4.3 RoboCup Junior

Soccer Standard: LEGO, sensor IR, max 22cm/1kg. Soccer Open: cámara + neural networks. Rescue Line: sensor flotante, 5mm de superficie, tape difusor. Desde 2026: pelota IR 42mm (antes 74mm).

---

## PARTE 5: DEBUGGING Y TESTING

### 5.1 Protocolo

1. Test unitario por función. 2. Repetibilidad x10. 3. Test batería 100%/70%. 4. Test superficie real. 5. Stress test x5 completo.

### 5.2 Xbox controller

Mover robot manualmente para tomar medidas exactas. Elimina guess-and-check. Pybricks soporta Xbox nativo.

### 5.3 Robots duplicados

Technic Hub como clon barato (~$18). Mismo código modular en ambas plataformas. Más alumnos practicando al mismo tiempo.

### 5.4 Logging

```python
print("Heading:", hub.imu.heading(), "Bat:", hub.battery.voltage())
```

---

## PARTE 6: DÍA DE COMPETENCIA

### Checklist

Batería 100%. heading_correction calibrado. Diámetro y axle track calibrados. Misiones probadas ≥5 veces. Attachments etiquetados. Código en USB backup.

### Adaptación al campo real

Recalibrar sensores de color en campo real. Tiempos de wait pueden necesitar ajuste. WRO: reglas sorpresa requieren flexibilidad.

---

## Fuentes

Pybricks Docs v3.6.1, Pybricks GitHub Discussions, FLLCasts (15+ años), Noddin Robotmakers, Monongahela Cryptid Cooperative, WRO 2025-2026 Rules, RoboCup Junior Soccer Rules 2025, RoboCup Junior Australia, Primelessons.org, Carnegie Mellon Robotics Academy.
