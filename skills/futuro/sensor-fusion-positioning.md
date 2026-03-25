# 📡 Posicionamiento por Fusión de Sensores Multi-Robot

## Documento técnico completo para robótica de competencia
### Con énfasis en RoboCup Junior Soccer y aplicaciones multi-robot

---

## PARTE 1: FUNDAMENTOS — POR QUÉ FUSIONAR SENSORES

### 1.1 El problema fundamental

Ningún sensor es perfecto. Cada uno tiene limitaciones específicas:

| Sensor | Qué mide bien | Debilidad | Freq típica |
|--------|--------------|-----------|:-----------:|
| **Encoders** | Distancia relativa precisa | Acumula drift, pierde en slip | 100-1000 Hz |
| **IMU/Gyro** | Rotación rápida | Drift de bias, scale error | 100-1000 Hz |
| **ToF (VL53L0X/L1X)** | Distancia puntual (1-2m) | Rango corto, un solo punto | 30-50 Hz |
| **LiDAR (RPLidar)** | Mapa 360° distancias | Costoso, reflejos engañan | 5-10 Hz (scan) |
| **Cámara** | Objetos, colores, formas | Depende de luz, latencia | 30-60 Hz |
| **Brújula** | Heading absoluto | Interferencia magnética | 50-100 Hz |
| **UWB** | Posición absoluta indoor | Necesita infraestructura | 10-100 Hz |

**Fusión de sensores** = combinar datos de múltiples sensores para obtener una estimación del estado que es **mejor que cualquier sensor individual**.

### 1.2 El concepto clave: Estado del robot

El "estado" que queremos estimar típicamente es:

```
Estado = [x, y, θ, vx, vy, ω]

x, y   = posición en el campo (mm)
θ      = orientación / heading (grados)
vx, vy = velocidad lineal (mm/s)
ω      = velocidad angular (°/s)
```

En RoboCup Soccer, también queremos estimar:
```
Estado del mundo = [
    robot_propio: [x, y, θ, vx, vy],
    pelota: [bx, by, bvx, bvy],
    compañero: [cx, cy, cθ],           ← fusión multi-robot
    oponentes: [{ox, oy}, {ox, oy}],   ← detección
]
```

### 1.3 Tipos de fusión

```
Nivel 1: FUSIÓN DE DATOS (un solo robot, múltiples sensores)
    Encoders + IMU → odometría mejorada
    ToF + LiDAR → mapa de distancias
    Cámara + LiDAR → detección + distancia

Nivel 2: FUSIÓN DE ESTIMACIONES (un solo robot, estimadores independientes)
    Odometría local + detección de landmarks → posición corregida
    Modelo de movimiento + mediciones → filtro de Kalman

Nivel 3: FUSIÓN MULTI-ROBOT (múltiples robots, info compartida)
    Mi estado + estado reportado por compañero → estado cooperativo
    Mi detección de pelota + detección del compañero → posición mejorada
```

---

## PARTE 2: ODOMETRÍA — LA BASE DE TODO

### 2.1 Odometría diferencial (2 ruedas)

```
Datos de entrada:
    ΔL = cambio en encoder izquierdo (grados → mm)
    ΔR = cambio en encoder derecho (grados → mm)
    W  = distancia entre ruedas (mm)

Cálculo:
    Δd = (ΔL + ΔR) / 2              # distancia lineal promedio
    Δθ = (ΔR - ΔL) / W              # cambio de ángulo (radianes)
    
    # Actualizar posición global
    x += Δd × cos(θ + Δθ/2)
    y += Δd × sin(θ + Δθ/2)
    θ += Δθ
```

### 2.2 Odometría mejorada con gyro (IMU fusion)

El gyro mide θ directamente (más preciso que calcularlo de encoders):

```python
# En vez de Δθ = (ΔR - ΔL) / W:
Δθ = gyro.heading() - θ_anterior     # más preciso

# Mantener el cálculo de Δd de encoders (eso es bueno)
Δd = (ΔL + ΔR) / 2

# Posición actualizada con heading del gyro
x += Δd * math.cos(θ_gyro + Δθ/2)
y += Δd * math.sin(θ_gyro + Δθ/2)
θ = θ_gyro  # el gyro tiene la verdad sobre rotación
```

Esto es la fusión más básica y ya da resultados excelentes. La odometría pura de encoders acumula ~5% de error en heading por metro. Con gyro baja a ~0.5%.

### 2.3 Dead wheels (odometría pasiva)

Ruedas no motorizadas que solo miden. Eliminan el problema de slip de las ruedas motrices. Configuraciones comunes:

```
2-wheel + gyro:   Encoder X + Encoder Y + IMU heading
3-wheel:          3 encoders omnidireccionales (redundante)
```

Usado en FTC con RoadRunner. Para RoboCup Junior con robots omnidireccionales es muy valioso.

---

## PARTE 3: FILTRO DE KALMAN — EL CORAZÓN DE LA FUSIÓN

### 3.1 Intuición

Imaginate que estás en una habitación oscura. Tenés dos formas de saber dónde estás:
1. **Predicción**: "Di un paso adelante, así que debo estar 50cm más adelante" (pero no es exacto, quizá fueron 48 o 52)
2. **Medición**: "La pared está a 120cm según el sensor" (pero el sensor tiene ±5cm de error)

El filtro de Kalman combina predicción + medición dándole MÁS PESO al que tiene MENOS error.

### 3.2 Kalman Filter lineal — Ecuaciones

```
═══ PASO 1: PREDICCIÓN (modelo de movimiento) ═══

x̂⁻ = F × x̂ + B × u       # predecir estado
P⁻ = F × P × Fᵀ + Q       # predecir incertidumbre

Donde:
  x̂  = estado estimado [x, y, θ, v, ω]
  F   = matriz de transición de estado (modelo del robot)
  B   = matriz de control
  u   = control aplicado (velocidad comandada)
  P   = covarianza del error (qué tan seguros estamos)
  Q   = ruido del proceso (qué tan impreciso es el modelo)

═══ PASO 2: ACTUALIZACIÓN (mediciones de sensores) ═══

K = P⁻ × Hᵀ × (H × P⁻ × Hᵀ + R)⁻¹   # Kalman Gain
x̂ = x̂⁻ + K × (z - H × x̂⁻)              # actualizar estado
P = (I - K × H) × P⁻                   # actualizar incertidumbre

Donde:
  K   = ganancia de Kalman (cuánto confiar en la medición)
  H   = matriz de observación (qué mide el sensor)
  z   = medición real del sensor
  R   = ruido de medición (qué tan ruidoso es el sensor)
  I   = matriz identidad
```

### 3.3 Extended Kalman Filter (EKF) — Para robots

El robot no es un sistema lineal (usa sin/cos), así que necesitamos el **EKF** que lineariza en cada paso:

```python
import math
import numpy as np

class EKF_Robot:
    def __init__(self):
        # Estado: [x, y, θ]
        self.x = np.zeros(3)
        
        # Covarianza inicial (alta incertidumbre)
        self.P = np.diag([100.0, 100.0, 0.1])  # mm², mm², rad²
        
        # Ruido del proceso (qué tan impreciso es el modelo)
        self.Q = np.diag([5.0, 5.0, 0.01])  # ajustar empíricamente
    
    def predict(self, v, omega, dt):
        """Predicción basada en modelo de movimiento."""
        theta = self.x[2]
        
        # Modelo de movimiento diferencial
        if abs(omega) > 0.001:
            # Movimiento con rotación
            dx = (v / omega) * (math.sin(theta + omega * dt) - math.sin(theta))
            dy = (v / omega) * (math.cos(theta) - math.cos(theta + omega * dt))
        else:
            # Movimiento recto
            dx = v * dt * math.cos(theta)
            dy = v * dt * math.sin(theta)
        
        dtheta = omega * dt
        
        self.x[0] += dx
        self.x[1] += dy
        self.x[2] += dtheta
        
        # Jacobiano del modelo (linearización)
        F = np.eye(3)
        F[0, 2] = -v * dt * math.sin(theta)  # ∂x/∂θ
        F[1, 2] = v * dt * math.cos(theta)   # ∂y/∂θ
        
        # Actualizar covarianza
        self.P = F @ self.P @ F.T + self.Q
    
    def update_position(self, z_pos, R_pos):
        """Actualizar con medición de posición [x, y]."""
        H = np.array([[1, 0, 0],
                       [0, 1, 0]])  # medimos x, y
        
        y = z_pos - H @ self.x           # innovación
        S = H @ self.P @ H.T + R_pos     # covarianza innovación
        K = self.P @ H.T @ np.linalg.inv(S)  # Kalman gain
        
        self.x = self.x + K @ y
        self.P = (np.eye(3) - K @ H) @ self.P
    
    def update_heading(self, z_heading, R_heading):
        """Actualizar con medición de heading (gyro/brújula)."""
        H = np.array([[0, 0, 1]])  # medimos θ
        
        y = z_heading - H @ self.x
        # Normalizar ángulo
        y[0] = (y[0] + math.pi) % (2 * math.pi) - math.pi
        
        S = H @ self.P @ H.T + R_heading
        K = self.P @ H.T @ np.linalg.inv(S)
        
        self.x = self.x + (K @ y).flatten()
        self.P = (np.eye(3) - K @ H) @ self.P
```

### 3.4 Unscented Kalman Filter (UKF)

Mejor que EKF para sistemas muy no-lineales. En vez de linearizar con Jacobianos, propaga "sigma points" (puntos representativos de la distribución) a través de la función no-lineal real. Más preciso que EKF, similar costo computacional.

### 3.5 Particle Filter (Monte Carlo Localization)

Para situaciones multimodales ("puedo estar en 2 lugares distintos"):

```python
class ParticleFilter:
    def __init__(self, n_particles=200):
        # Cada partícula es una hipótesis de posición
        self.particles = np.random.uniform(
            low=[0, 0, 0],
            high=[campo_ancho, campo_largo, 2*math.pi],
            size=(n_particles, 3)
        )
        self.weights = np.ones(n_particles) / n_particles
    
    def predict(self, v, omega, dt):
        """Mover partículas según modelo + ruido."""
        for p in self.particles:
            # Agregar ruido al movimiento
            v_noisy = v + np.random.normal(0, v * 0.05)
            omega_noisy = omega + np.random.normal(0, 0.02)
            
            p[0] += v_noisy * dt * math.cos(p[2])
            p[1] += v_noisy * dt * math.sin(p[2])
            p[2] += omega_noisy * dt
    
    def update(self, measurements):
        """Actualizar pesos según qué tan bien cada partícula
        explica las mediciones."""
        for i, p in enumerate(self.particles):
            expected = predict_measurements(p)  # qué mediría en esta posición
            error = np.linalg.norm(measurements - expected)
            self.weights[i] = math.exp(-error**2 / (2 * sigma**2))
        
        # Normalizar
        self.weights /= self.weights.sum()
    
    def resample(self):
        """Eliminar partículas de baja probabilidad,
        duplicar las de alta."""
        indices = np.random.choice(
            len(self.particles),
            size=len(self.particles),
            p=self.weights
        )
        self.particles = self.particles[indices]
        self.weights = np.ones(len(self.particles)) / len(self.particles)
    
    def estimate(self):
        """Posición estimada = promedio ponderado."""
        return np.average(self.particles, weights=self.weights, axis=0)
```

**En RoboCup**: Los particle filters son populares porque manejan bien la ambigüedad (el campo es simétrico, al inicio no sabés en qué mitad estás). El Multiple-Model Kalman Filter (MM-EKF) es una alternativa que usa múltiples EKFs en paralelo.

---

## PARTE 4: FUSIÓN POR TIPO DE SENSOR

### 4.1 Encoders + IMU (fusión básica)

```
┌──────────────┐     ┌──────────────┐
│  Encoders    │     │   IMU/Gyro   │
│  ΔL, ΔR      │     │  ω, a, θ     │
└──────┬───────┘     └──────┬───────┘
       │    EKF Predict      │
       │  (modelo movimiento)│
       └───────┬─────────────┘
               ↓
        ┌──────────────┐
        │  Estado:     │
        │  x, y, θ,    │
        │  v, ω        │
        └──────────────┘

Predict: usar encoders para Δd + gyro para Δθ
Update: sin update externo → solo odometría
Resultado: odometría precisa pero con drift acumulado
```

### 4.2 Odometría + ToF (corrección de distancia)

```python
# ToF mide distancia a una pared conocida
dist_pared = tof_sensor.distance()  # mm

# Si sabemos que la pared está en x=0:
x_medido = dist_pared  # posición X desde la pared

# Update del EKF con esta medición
ekf.update_position(
    z_pos=np.array([x_medido, ekf.x[1]]),  # solo actualizamos X
    R_pos=np.diag([25.0, 99999.0])  # ±5mm en X, no info en Y
)
```

### 4.3 Odometría + LiDAR 2D (SLAM lite)

```
┌──────────────┐     ┌──────────────┐
│  Odometría   │     │   LiDAR      │
│  x,y,θ local │     │  scan 360°   │
└──────┬───────┘     └──────┬───────┘
       │                     │
       ↓                     ↓
  EKF Predict         Feature Extraction
  (modelo mov.)       (líneas, esquinas)
       │                     │
       └───────┬─────────────┘
               ↓
          EKF Update
       (landmark matching)
               ↓
        ┌──────────────┐
        │  Posición     │
        │  corregida    │
        └──────────────┘
```

Para RoboCup Soccer: las paredes de la cancha son landmarks conocidos. Un scan LiDAR puede detectar las 4 paredes y los arcos, dando posición absoluta.

### 4.4 Odometría + Cámara (Visual Landmarks)

En RoboCup, los landmarks pueden ser:
- Líneas del campo (blancas)
- Arcos (estructuras conocidas)
- Pelota (naranja, posición variable)
- Otros robots (obstáculos)

```python
# Detección de arco por cámara → bearing angle
arco_angulo = camera.detect_goal_angle()  # grados relativos
arco_distancia = camera.estimate_goal_distance()  # por tamaño aparente

# Convertir a posición relativa
arco_x_rel = arco_distancia * math.cos(math.radians(arco_angulo))
arco_y_rel = arco_distancia * math.sin(math.radians(arco_angulo))

# Si sabemos que el arco propio está en [0, campo_y/2]:
# Nuestra posición = arco_pos - relativa (rotada por heading)
x_est = arco_known_x - arco_x_rel * cos(θ) + arco_y_rel * sin(θ)
y_est = arco_known_y - arco_x_rel * sin(θ) - arco_y_rel * cos(θ)

# Update del EKF
ekf.update_position(np.array([x_est, y_est]), R_vision)
```

### 4.5 Fusión completa: Encoders + IMU + ToF + Cámara

```
Loop principal @ 100 Hz:

1. PREDICT (cada ciclo, 10ms):
   - Leer encoders → Δd
   - Leer gyro → Δθ
   - ekf.predict(v, omega, dt=0.01)

2. UPDATE TOF (cada 30ms, cuando hay lectura nueva):
   - dist = tof.distance()
   - Si dist < rango_max:
     ekf.update_distance(dist, pared_conocida)

3. UPDATE CÁMARA (cada 33ms, cuando hay frame nuevo):
   - landmarks = camera.detect_landmarks()
   - Para cada landmark:
     ekf.update_landmark(landmark_pos, landmark_R)

4. UPDATE BRÚJULA (cada 50ms):
   - heading = compass.heading()
   - ekf.update_heading(heading, R_compass)

5. OUTPUT:
   - posicion = ekf.x  # estado fusionado
```

---

## PARTE 5: FUSIÓN MULTI-ROBOT (RoboCup Soccer)

### 5.1 El problema

En RoboCup Junior Soccer 2:2, cada equipo tiene 2 robots. Cada uno tiene sus propios sensores con sus propios errores. Pero pueden comunicarse. La pregunta es: **¿cómo combinar la información de ambos robots para que AMBOS tengan mejor conocimiento del estado del mundo?**

### 5.2 Qué compartir entre robots

```
Mensaje de Robot A → Robot B:
{
    timestamp: 1234567,          # para sincronización
    my_pos: [x, y, θ],          # mi posición estimada
    my_pos_confidence: [σx, σy, σθ],  # qué tan seguro estoy
    ball_pos: [bx, by],          # posición de pelota (si la veo)
    ball_confidence: σ_ball,     # confianza en mi detección
    ball_velocity: [bvx, bvy],   # velocidad estimada de pelota
    i_see_ball: true/false,      # si tengo detección válida
    opponents: [{ox,oy}, ...],   # oponentes detectados
    my_role: "attacker",         # para coordinación
    battery: 85,                 # para decisiones de equipo
}
```

### 5.3 Fusión de posición de pelota (caso estrella)

Dos robots ven la pelota desde ángulos diferentes. Cada uno tiene un error diferente (depende de distancia, ángulo, sensor).

```python
def fusionar_pelota(mi_deteccion, deteccion_companero):
    """
    Fusión de Kalman de dos observaciones de la pelota.
    
    mi_deteccion = {
        'pos': [bx, by],      # posición estimada
        'cov': [[σxx, σxy],   # covarianza 2x2
                [σxy, σyy]]   # (incertidumbre)
    }
    """
    z1 = np.array(mi_deteccion['pos'])
    R1 = np.array(mi_deteccion['cov'])
    
    z2 = np.array(deteccion_companero['pos'])
    R2 = np.array(deteccion_companero['cov'])
    
    # Fusión óptima de Kalman para dos mediciones gaussianas:
    # La medición con MENOR incertidumbre tiene MÁS peso
    
    R_inv_sum = np.linalg.inv(R1) + np.linalg.inv(R2)
    P_fused = np.linalg.inv(R_inv_sum)  # covarianza fusionada
    
    z_fused = P_fused @ (np.linalg.inv(R1) @ z1 + np.linalg.inv(R2) @ z2)
    
    return z_fused, P_fused
    # Resultado: posición más precisa que cualquiera de las dos,
    # con incertidumbre menor que ambas
```

**Intuición**: Si Robot A ve la pelota a 45° (buena resolución angular pero distancia incierta) y Robot B la ve de frente (buena distancia pero ángulo incierto), la fusión da una posición precisa en ambas dimensiones.

### 5.4 Fusión cooperativa de posición (Multi-Robot EKF)

Cada robot mantiene un estado extendido que incluye al compañero:

```
Estado extendido de Robot A:
  x_A = [x_a, y_a, θ_a,    # mi posición
         x_b, y_b, θ_b,    # posición estimada de compañero
         bx, by, bvx, bvy] # pelota

Update con datos recibidos de Robot B:
  z_B = [x_b_reportado, y_b_reportado, θ_b_reportado]
  R_B = diag(σ²_xb, σ²_yb, σ²_θb)  # incertidumbre reportada por B
  
  H_B = [0 0 0 | 1 0 0 | 0 0 0 0]  # mide posición de B
  
  # Standard Kalman update
  K = P @ H_B.T @ inv(H_B @ P @ H_B.T + R_B)
  x_A = x_A + K @ (z_B - H_B @ x_A)
  P = (I - K @ H_B) @ P
```

### 5.5 Distributed Kalman Filter (DKF)

En vez de un EKF centralizado (un robot calcula todo), cada robot corre su propio "mini-Kalman" y solo comparten actualizaciones:

```
Robot A (local):                    Robot B (local):
┌──────────────────┐                ┌──────────────────┐
│ Predict con mis  │                │ Predict con mis  │
│ encoders + IMU   │                │ encoders + IMU   │
├──────────────────┤                ├──────────────────┤
│ Update con mis   │                │ Update con mis   │
│ sensores (ToF,   │                │ sensores (ToF,   │
│ cámara, LiDAR)   │                │ cámara, LiDAR)   │
├──────────────────┤                ├──────────────────┤
│ Enviar:          │ ←────────────→ │ Enviar:          │
│ mi_estado,       │  comunicación  │ mi_estado,       │
│ mi_covarianza,   │   (BT/radio)   │ mi_covarianza,   │
│ pelota_detectada │                │ pelota_detectada │
├──────────────────┤                ├──────────────────┤
│ Update con datos │                │ Update con datos │
│ del compañero    │                │ del compañero    │
└──────────────────┘                └──────────────────┘
```

### 5.6 Manejo de latencia en comunicación

La comunicación entre robots tiene delay (10-50ms típico). Si usamos datos del compañero "viejos", el estado ya cambió.

**Solución**: Predecir hacia adelante usando el modelo de movimiento:

```python
def recibir_estado_companero(msg, t_actual):
    # El mensaje fue enviado en msg.timestamp
    dt_delay = t_actual - msg.timestamp  # latencia en ms
    
    # Predecir dónde ESTÁ el compañero AHORA
    # (no dónde estaba cuando envió el mensaje)
    x_predicho = msg.x + msg.vx * dt_delay / 1000
    y_predicho = msg.y + msg.vy * dt_delay / 1000
    theta_predicho = msg.theta + msg.omega * dt_delay / 1000
    
    # Aumentar la incertidumbre por la predicción
    sigma_extra = dt_delay * 0.01  # 1% por ms de delay
    R_compensado = msg.covariance + np.eye(3) * sigma_extra
    
    return [x_predicho, y_predicho, theta_predicho], R_compensado
```

### 5.7 Detección y tracking de pelota multi-robot

```python
class BallTracker:
    def __init__(self):
        # Estado: [x, y, vx, vy]
        self.x = np.zeros(4)
        self.P = np.eye(4) * 1000
        
        # Modelo: velocidad constante con desaceleración por fricción
        self.friction = 0.98  # pelota se frena por fricción
    
    def predict(self, dt):
        F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, self.friction, 0],
            [0, 0, 0, self.friction]
        ])
        self.x = F @ self.x
        Q = np.diag([1, 1, 5, 5])  # ruido del modelo
        self.P = F @ self.P @ F.T + Q
    
    def update_from_sensor(self, z_ball, R_ball, source="local"):
        """Actualizar con detección local o del compañero."""
        H = np.array([[1, 0, 0, 0],
                       [0, 1, 0, 0]])  # medimos posición
        
        y = z_ball - H @ self.x
        S = H @ self.P @ H.T + R_ball
        K = self.P @ H.T @ np.linalg.inv(S)
        
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P
    
    def get_prediction(self, dt_futuro):
        """Predecir dónde estará la pelota en dt_futuro ms.
        Útil para interceptar."""
        return np.array([
            self.x[0] + self.x[2] * dt_futuro / 1000,
            self.x[1] + self.x[3] * dt_futuro / 1000
        ])
```

### 5.8 World Model completo para Soccer

```python
class WorldModel:
    """Estado completo del mundo para un robot de soccer."""
    
    def __init__(self):
        self.self_ekf = EKF_Robot()          # mi posición
        self.ball_tracker = BallTracker()     # pelota
        self.teammate_pos = None              # compañero
        self.teammate_confidence = 0
        self.opponents = []                   # oponentes detectados
        self.last_comm_time = 0
    
    def cycle(self, dt, encoders, imu, local_sensors, comm_msg=None):
        """Un ciclo completo de fusión."""
        
        # 1. Predict mi posición
        v, omega = compute_odometry(encoders, imu)
        self.self_ekf.predict(v, omega, dt)
        
        # 2. Predict pelota
        self.ball_tracker.predict(dt)
        
        # 3. Update con mis sensores locales
        if local_sensors.ball_detected:
            ball_global = local_to_global(
                local_sensors.ball_local, self.self_ekf.x)
            R_ball = estimate_ball_covariance(
                local_sensors.ball_distance)  # más lejos = más error
            self.ball_tracker.update_from_sensor(
                ball_global, R_ball, source="local")
        
        # 4. Update con datos del compañero
        if comm_msg is not None:
            # Posición del compañero (con compensación de delay)
            mate_pos, mate_R = recibir_estado_companero(
                comm_msg, time.ticks_ms())
            self.teammate_pos = mate_pos
            self.teammate_confidence = 1.0 / np.trace(mate_R)
            
            # Pelota del compañero
            if comm_msg.ball_detected:
                ball_from_mate = comm_msg.ball_pos
                R_mate_ball = comm_msg.ball_cov
                
                # Fusionar con mi estimación
                self.ball_tracker.update_from_sensor(
                    ball_from_mate, R_mate_ball, source="teammate")
        
        # 5. Update con landmarks (si hay LiDAR o cámara)
        for landmark in local_sensors.landmarks:
            self.self_ekf.update_landmark(landmark)
        
        return self.get_state()
    
    def get_state(self):
        return {
            'my_pos': self.self_ekf.x[:2],
            'my_heading': self.self_ekf.x[2],
            'ball_pos': self.ball_tracker.x[:2],
            'ball_vel': self.ball_tracker.x[2:4],
            'ball_prediction_500ms': self.ball_tracker.get_prediction(500),
            'teammate': self.teammate_pos,
            'opponents': self.opponents,
        }
```

---

## PARTE 6: IMPLEMENTACIÓN PRÁCTICA POR NIVEL

### Nivel 1: Spike Prime + Pybricks (actual del taller)

```
Sensores: 2 encoders (motores) + IMU (gyro integrado)
Fusión: Encoders para distancia + Gyro para heading
Resultado: Odometría básica con heading preciso
→ YA LO HACEMOS con robot.use_gyro(True)
```

### Nivel 2: Arduino + sensores discretos

```
Sensores: Encoders + MPU6050 (gyro) + 2-4 VL53L0X (ToF) + brújula
Fusión: EKF simple en Arduino (estado [x,y,θ])
Predict: encoders + gyro
Update: ToF → distancia a paredes, brújula → heading absoluto
→ VIABLE con Arduino Mega, ~50Hz loop
```

### Nivel 3: Raspberry Pi + LiDAR + cámara

```
Sensores: Encoders + IMU + RPLidar A1 + Pi Camera
Fusión: EKF completo o particle filter en Python
Predict: encoders + IMU
Update: LiDAR → paredes/landmarks, cámara → pelota/arco/líneas
→ VIABLE a 30Hz con RPi 4, ideal para RoboCup Junior
```

### Nivel 4: Multi-robot con comunicación

```
Sensores: Todo nivel 3 × 2 robots
Comunicación: nRF24L01 (1ms latencia) o BT (~50ms)
Fusión: Distributed KF, cada robot corre su EKF local
+ updates del compañero con compensación de delay
→ PARA COMPETENCIA SERIA de RoboCup Junior Soccer
```

---

## PARTE 7: PARÁMETROS CRÍTICOS Y TUNING

### 7.1 Matrices de ruido (las más importantes de tunear)

| Parámetro | Qué es | Cómo tunear |
|-----------|--------|-------------|
| **Q** (process noise) | Qué tan impreciso es tu modelo | Si el filtro no sigue al robot → subir Q. Si oscila → bajar Q |
| **R** (measurement noise) | Qué tan ruidoso es cada sensor | Medir varianza real del sensor estático. Empezar con ese valor |
| **P₀** (initial covariance) | Incertidumbre inicial | Alta al inicio (no sabés dónde estás), baja si conocés posición |

### 7.2 Procedimiento de tuning

1. **Medir ruido de cada sensor individualmente**:
   - Robot quieto, logear 1000 lecturas
   - Calcular varianza → ese es R para ese sensor

2. **Empezar con Q pequeño** (confiar en el modelo)
   - Si el filtro "se queda atrás" → subir Q
   - Si el filtro oscila mucho → bajar Q

3. **Validar con ground truth**:
   - Marcar posiciones conocidas en el campo
   - Mover robot por trayectoria conocida
   - Comparar estimación del filtro vs posición real

---

## PARTE 8: COMPARATIVA DE ALGORITMOS

| Algoritmo | Precisión | CPU | Multi-modal | Implementación | Para qué |
|-----------|:---------:|:---:|:-----------:|:--------------:|----------|
| Complementary filter | Baja | Mínima | No | Trivial | IMU + encoders básico |
| Kalman Filter (KF) | Media | Baja | No | Simple | Sistemas lineales |
| Extended KF (EKF) | Alta | Media | No | Media | La mayoría de robots |
| Unscented KF (UKF) | Muy alta | Media-Alta | No | Media | No-linearidad fuerte |
| Particle Filter (PF) | Alta | Alta | **Sí** | Alta | Kidnapped robot, inicio |
| Multi-Model KF | Muy alta | Alta | **Sí** | Alta | RoboCup (ambigüedad de campo) |
| Graph-SLAM | Excelente | Muy alta | No | Muy alta | Mapeo + localización |

**Recomendación por nivel**:
- Spike Prime: Complementary (ya integrado en Pybricks)
- Arduino: EKF simple
- RPi: EKF completo o UKF
- RoboCup serio: MM-EKF o Particle Filter + Distributed KF

---

## FUENTES

### Papers de RoboCup
- Quinlan & Middleton (2010): "Multiple Model Kalman Filters: A Localization Technique for RoboCup Soccer" — RoboCup 2009, Springer LNCS
- Liu, Zhao, Shi, Xu (2008): "Multi-robot Cooperative Localization through Collaborative Visual Object Tracking" — RoboCup 2007
- Schmitt, Hanek, Beetz (2002): "Cooperative Probabilistic State Estimation" — IEEE Trans. Robotics
- Silva, Lau, Rodrigues, Azevedo, Neves (2010): "Sensor and Information Fusion Applied to a Robotic Soccer Team" (CAMBADA) — RoboCup 2009
- Roumeliotis & Bekey (2002): "Distributed Multi-Robot Localization" — Distributed Autonomous Robotic Systems

### Reviews recientes (2025)
- PMC/MDPI (Feb 2025): "Sensor-Fusion Based Navigation for Autonomous Mobile Robot" — Sensors journal
- Springer (Mar 2025): "LiDAR, IMU, and camera fusion for SLAM: a systematic review" — AI Review
- Nature Scientific Reports (Mar 2025): "Multi-sensor fusion localization algorithm based on RNN"
- PMC/MDPI (Jul 2025): "Multi-Sensor Fusion Framework for Reliable Localization" — UWB+Odometry+AHRS

### Implementación
- OpenCV (calibración de cámara, detección)
- FilterPy (librería Python para Kalman filters)
- Robot_localization (paquete ROS 2 para EKF/UKF)
- WPILib (FRC/FTC path planning y pose estimation)
