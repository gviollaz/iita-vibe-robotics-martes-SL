# ⚽ Tracking y Predicción de Objetos Móviles en Campo de Juego

## Estimación de posición, velocidad, orientación y trayectorias futuras
### Para pelota, compañeros, adversarios — incluyendo fusión multi-robot

---

## 1. EL PROBLEMA

En RoboCup Soccer, en cada instante necesitás saber:
- **Pelota**: ¿dónde está? ¿a qué velocidad va? ¿dónde va a estar en 500ms?
- **Compañero**: ¿dónde está? ¿hacia dónde va? ¿puede recibir un pase?
- **Adversarios**: ¿dónde están? ¿van hacia mi arco? ¿puedo interceptar?

Y todo esto con sensores ruidosos, oclusiones, latencia, y objetos que cambian de dirección impredeciblemente.

---

## 2. MODELOS DE MOVIMIENTO

### 2.1 Constant Velocity (CV) — El más básico

Asume que el objeto se mueve en línea recta a velocidad constante.

```
Estado: [x, y, vx, vy]

Predicción:
  x(t+dt) = x(t) + vx × dt
  y(t+dt) = y(t) + vy × dt
  vx(t+dt) = vx(t)
  vy(t+dt) = vy(t)

Matriz de transición:
  F = | 1  0  dt  0  |
      | 0  1  0   dt |
      | 0  0  1   0  |
      | 0  0  0   1  |
```

**Sirve para**: pelota rodando en línea recta, robot moviéndose sin girar
**Falla cuando**: el objeto gira, frena, o rebota

### 2.2 Constant Acceleration (CA) — Detecta frenado/aceleración

```
Estado: [x, y, vx, vy, ax, ay]

Predicción:
  x(t+dt) = x(t) + vx×dt + ½×ax×dt²
  vx(t+dt) = vx(t) + ax×dt
  ax(t+dt) = ax(t)

Matriz de transición:
  F = | 1  0  dt  0   ½dt²  0    |
      | 0  1  0   dt  0     ½dt² |
      | 0  0  1   0   dt    0    |
      | 0  0  0   1   0     dt   |
      | 0  0  0   0   1     0    |
      | 0  0  0   0   0     1    |
```

**Sirve para**: pelota que frena por fricción, robot que acelera o frena

### 2.3 Constant Turn Rate and Velocity (CTRV) — Para objetos que giran

```
Estado: [x, y, v, θ, ω]
  v = velocidad (magnitud)
  θ = heading (dirección)
  ω = velocidad angular (tasa de giro)

Predicción (no lineal, necesita EKF/UKF):
  Si ω ≈ 0:
    x(t+dt) = x(t) + v×cos(θ)×dt
    y(t+dt) = y(t) + v×sin(θ)×dt
  Si ω ≠ 0:
    x(t+dt) = x(t) + (v/ω)×[sin(θ+ω×dt) - sin(θ)]
    y(t+dt) = y(t) + (v/ω)×[cos(θ) - cos(θ+ω×dt)]
  v(t+dt) = v(t)
  θ(t+dt) = θ(t) + ω×dt
  ω(t+dt) = ω(t)
```

**Sirve para**: robots adversarios que giran, pelota con efecto

### 2.4 Pelota con fricción — Modelo específico para soccer

```python
class BallPhysicsModel:
    """
    Modelo de pelota rodando en campo de juego.
    Incluye fricción (la pelota se frena) y rebote en paredes.
    """
    def __init__(self):
        self.friction = 0.015      # coeficiente de fricción rodante
        self.restitution = 0.5     # coeficiente de rebote en paredes
        self.field_width = 1220    # mm (RCJ Junior)
        self.field_length = 1830   # mm
    
    def predict(self, state, dt):
        """state = [x, y, vx, vy]"""
        x, y, vx, vy = state
        
        # Velocidad con fricción exponencial
        decay = math.exp(-self.friction * dt * 30)  # 30 = escala empírica
        vx_new = vx * decay
        vy_new = vy * decay
        
        # Posición
        x_new = x + (vx + vx_new) / 2 * dt
        y_new = y + (vy + vy_new) / 2 * dt
        
        # Rebote en paredes
        if x_new < 0 or x_new > self.field_width:
            vx_new *= -self.restitution
            x_new = max(0, min(self.field_width, x_new))
        if y_new < 0 or y_new > self.field_length:
            vy_new *= -self.restitution
            y_new = max(0, min(self.field_length, y_new))
        
        return [x_new, y_new, vx_new, vy_new]
```

---

## 3. ALGORITMOS DE TRACKING

### 3.1 EKF Ball Tracker (implementación completa)

```python
import numpy as np
import math

class EKF_BallTracker:
    """
    Extended Kalman Filter para tracking de pelota en soccer.
    Estado: [x, y, vx, vy]
    Predice posición Y velocidad.
    Maneja mediciones de múltiples fuentes (local + compañero).
    """
    def __init__(self):
        self.x = np.zeros(4)            # [x, y, vx, vy]
        self.P = np.eye(4) * 1000       # incertidumbre alta al inicio
        self.friction = 0.97            # decay de velocidad por ciclo
        self.initialized = False
    
    def predict(self, dt):
        """Predicción: modelo de velocidad constante + fricción."""
        F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, self.friction, 0],
            [0, 0, 0, self.friction]
        ])
        
        # Ruido del proceso (pelota puede ser pateada)
        q_pos = 2.0    # mm² — incertidumbre en posición
        q_vel = 50.0   # (mm/s)² — puede cambiar de velocidad bruscamente
        Q = np.diag([q_pos, q_pos, q_vel, q_vel])
        
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
    
    def update(self, z_pos, R_meas):
        """Actualizar con medición de posición [x, y]."""
        if not self.initialized:
            self.x[:2] = z_pos
            self.initialized = True
            return
        
        H = np.array([[1, 0, 0, 0],
                       [0, 1, 0, 0]])  # medimos posición
        
        y = z_pos - H @ self.x                    # innovación
        S = H @ self.P @ H.T + R_meas              # cov. innovación
        K = self.P @ H.T @ np.linalg.inv(S)        # Kalman gain
        
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P
    
    def get_position(self):
        return self.x[:2]
    
    def get_velocity(self):
        return self.x[2:4]
    
    def predict_future(self, dt_ms):
        """¿Dónde estará la pelota en dt_ms milisegundos?"""
        dt = dt_ms / 1000.0
        steps = int(dt / 0.01)  # simular en pasos de 10ms
        x, y, vx, vy = self.x
        for _ in range(steps):
            vx *= self.friction
            vy *= self.friction
            x += vx * 0.01
            y += vy * 0.01
        return np.array([x, y])
    
    def time_to_reach(self, target_pos):
        """¿Cuántos ms hasta que la pelota llegue a target_pos?
        Retorna -1 si no va en esa dirección."""
        dx = target_pos[0] - self.x[0]
        dy = target_pos[1] - self.x[1]
        dist = math.sqrt(dx**2 + dy**2)
        speed = math.sqrt(self.x[2]**2 + self.x[3]**2)
        if speed < 10:  # casi quieta
            return -1
        
        # Verificar que va en la dirección correcta
        dot = dx * self.x[2] + dy * self.x[3]
        if dot < 0:
            return -1  # va en dirección opuesta
        
        # Estimación simple con fricción
        # t ≈ dist / (speed_promedio)
        avg_speed = speed * 0.7  # estimación con fricción
        return int(dist / avg_speed * 1000) if avg_speed > 0 else -1
```

### 3.2 Interacting Multiple Model (IMM) — Para objetos que cambian de comportamiento

El IMM es el algoritmo estrella para tracking de oponentes. Corre múltiples filtros en paralelo, cada uno con un modelo de movimiento diferente, y los mezcla dinámicamente.

```
IMM para tracking de robot oponente:

  Modelo 1: Constant Velocity (va recto)
  Modelo 2: Constant Turn (está girando)
  Modelo 3: Constant Acceleration (está acelerando/frenando)

  Cada modelo tiene su propio EKF.
  En cada ciclo:
    1. INTERACCIÓN: Mezclar estados de los modelos según probabilidades
    2. PREDICCIÓN: Cada modelo predice independientemente
    3. UPDATE: Cada modelo se actualiza con la medición
    4. COMBINAR: Calcular probabilidad de cada modelo
    5. ESTIMAR: Estado final = promedio ponderado por probabilidades

  Si el oponente va recto → Modelo 1 tiene alta probabilidad
  Si empieza a girar → Modelo 2 gana probabilidad rápidamente
  El IMM se adapta en ~2-3 mediciones al cambio de comportamiento
```

```python
class IMM_Tracker:
    """
    Interacting Multiple Model para tracking de oponentes/pelota.
    Combina CV + CA + CT para manejar cambios de comportamiento.
    """
    def __init__(self):
        # 3 filtros EKF con diferentes modelos
        self.filters = [
            EKF_CV(),    # Constant Velocity
            EKF_CA(),    # Constant Acceleration  
            EKF_CT(),    # Constant Turn
        ]
        self.n_models = 3
        
        # Probabilidades iniciales (equiprobables)
        self.mu = np.array([0.4, 0.3, 0.3])
        
        # Matriz de transición de modelos
        # Probabilidad de pasar de modelo i a modelo j
        self.T = np.array([
            [0.90, 0.05, 0.05],  # CV: 90% sigue recto
            [0.10, 0.80, 0.10],  # CA: 80% sigue acelerando
            [0.10, 0.10, 0.80],  # CT: 80% sigue girando
        ])
    
    def cycle(self, z_measurement, dt):
        """Un ciclo completo del IMM."""
        
        # PASO 1: Calcular probabilidades de mezcla
        c_bar = self.T.T @ self.mu
        mu_mix = np.zeros((self.n_models, self.n_models))
        for i in range(self.n_models):
            for j in range(self.n_models):
                mu_mix[i, j] = self.T[i, j] * self.mu[i] / c_bar[j]
        
        # PASO 2: Mezclar estados de entrada
        for j in range(self.n_models):
            x_mixed = sum(mu_mix[i, j] * self.filters[i].x 
                         for i in range(self.n_models))
            # Mezclar covarianzas también (simplificado)
            self.filters[j].x = x_mixed
        
        # PASO 3: Predict + Update cada filtro
        likelihoods = np.zeros(self.n_models)
        for j, f in enumerate(self.filters):
            f.predict(dt)
            innovation = z_measurement - f.get_expected_measurement()
            S = f.get_innovation_covariance()
            likelihoods[j] = gaussian_likelihood(innovation, S)
            f.update(z_measurement)
        
        # PASO 4: Actualizar probabilidades de modelos
        self.mu = c_bar * likelihoods
        self.mu /= self.mu.sum()  # normalizar
        
        # PASO 5: Estado combinado
        x_combined = sum(self.mu[j] * self.filters[j].x 
                        for j in range(self.n_models))
        return x_combined
    
    def get_most_likely_behavior(self):
        """¿Qué está haciendo el oponente?"""
        behaviors = ['recto', 'acelerando', 'girando']
        return behaviors[np.argmax(self.mu)]
    
    def predict_future(self, dt_ms):
        """Predecir posición futura usando el modelo más probable."""
        best = np.argmax(self.mu)
        return self.filters[best].predict_future(dt_ms)
```

---

## 4. PREDICCIÓN DE TRAYECTORIAS

### 4.1 Predicción lineal (simple pero efectiva)

```python
def predecir_posicion_lineal(pos, vel, dt_ms):
    """Predicción asumiendo velocidad constante."""
    dt = dt_ms / 1000.0
    return pos + vel * dt

# Ejemplo:
ball_pos = np.array([500, 300])    # mm
ball_vel = np.array([-200, 100])   # mm/s (va hacia mi arco)

# ¿Dónde estará en 500ms?
future_pos = predecir_posicion_lineal(ball_pos, ball_vel, 500)
# Resultado: [400, 350]
```

### 4.2 Predicción con fricción (para pelota)

```python
def predecir_pelota(pos, vel, dt_ms, friction=0.97):
    """Predicción de pelota con fricción.
    La pelota se frena gradualmente."""
    dt = dt_ms / 1000.0
    steps = int(dt / 0.01)
    x, y = pos
    vx, vy = vel
    for _ in range(steps):
        vx *= friction
        vy *= friction
        x += vx * 0.01
        y += vy * 0.01
    return np.array([x, y]), np.array([vx, vy])

# ¿Dónde se detiene la pelota?
def posicion_final_pelota(pos, vel, friction=0.97, vel_min=5):
    """Simular hasta que la pelota se detenga."""
    x, y = pos
    vx, vy = vel
    t = 0
    while math.sqrt(vx**2 + vy**2) > vel_min:
        vx *= friction
        vy *= friction
        x += vx * 0.01
        y += vy * 0.01
        t += 10  # ms
    return np.array([x, y]), t
```

### 4.3 Punto de interceptación (crucial para soccer)

```python
def calcular_interceptacion(robot_pos, robot_vel_max,
                             ball_pos, ball_vel, ball_friction=0.97):
    """
    ¿A dónde debería ir el robot para interceptar la pelota?
    
    Busca el punto donde el robot puede llegar al mismo tiempo
    que la pelota. Usa búsqueda binaria en tiempo.
    """
    for t_ms in range(50, 3000, 50):  # probar 50ms a 3000ms
        # ¿Dónde estará la pelota en t_ms?
        ball_future, _ = predecir_pelota(ball_pos, ball_vel, t_ms, ball_friction)
        
        # ¿Cuánto tardaría el robot en llegar ahí?
        dist_robot = np.linalg.norm(ball_future - robot_pos)
        t_robot = dist_robot / robot_vel_max * 1000  # ms
        
        # Si el robot puede llegar antes que la pelota
        if t_robot <= t_ms:
            return {
                'intercept_point': ball_future,
                'time_ms': t_ms,
                'robot_needs_ms': t_robot,
                'feasible': True
            }
    
    return {'feasible': False}  # No puede interceptar
```

### 4.4 Predicción de trayectoria de oponente

```python
def predecir_oponente(opp_tracker, dt_horizonte_ms):
    """
    Generar múltiples trayectorias probables del oponente.
    Útil para planificar defensa.
    """
    behavior = opp_tracker.get_most_likely_behavior()
    pos = opp_tracker.get_position()
    vel = opp_tracker.get_velocity()
    
    trayectorias = []
    
    # Trayectoria principal (modelo más probable)
    traj_principal = []
    for t in range(0, dt_horizonte_ms, 50):
        future = opp_tracker.predict_future(t)
        traj_principal.append(future)
    trayectorias.append(('principal', traj_principal))
    
    # Trayectorias alternativas (qué pasa si cambia de comportamiento)
    if behavior == 'recto':
        # Podría girar a la izquierda o derecha
        for angulo in [-30, 30]:  # grados
            traj = []
            x, y = pos
            v = np.linalg.norm(vel)
            theta = math.atan2(vel[1], vel[0])
            omega = math.radians(angulo)  # rad/s de giro
            for t in range(0, dt_horizonte_ms, 50):
                dt = 0.05
                theta += omega * dt
                x += v * math.cos(theta) * dt
                y += v * math.sin(theta) * dt
                traj.append(np.array([x, y]))
            trayectorias.append(('giro_' + str(angulo), traj))
    
    return trayectorias
```

---

## 5. FUSIÓN MULTI-ROBOT PARA TRACKING

### 5.1 El escenario: RoboCup Soccer 2:2

```
Robot A (atacante) ve:        Robot B (arquero) ve:
- Pelota: sí, de cerca        - Pelota: sí, de lejos
- Oponente 1: sí              - Oponente 1: parcial (ocluido)
- Oponente 2: no (detrás)     - Oponente 2: sí

Fusión: entre los dos ven TODO el campo
```

### 5.2 Protocolo de comunicación

```python
class TrackingMessage:
    """Mensaje que cada robot envía al compañero."""
    def __init__(self):
        self.timestamp = 0
        self.my_pos = [0, 0, 0]       # x, y, θ
        self.my_confidence = 0         # 0-1
        
        self.ball_seen = False
        self.ball_pos = [0, 0]         # en coordenadas de campo
        self.ball_vel = [0, 0]         # velocidad estimada
        self.ball_cov = [[0,0],[0,0]]  # covarianza 2×2
        
        self.opponents = []            # lista de {pos, vel, confidence}
```

### 5.3 Fusión de detecciones de pelota

```python
def fusionar_ball_detections(mi_deteccion, deteccion_companero):
    """
    Fusión óptima de Kalman de dos detecciones independientes.
    Cada detección tiene posición + covarianza.
    El resultado es mejor que cualquiera de las dos.
    """
    if mi_deteccion is None:
        return deteccion_companero
    if deteccion_companero is None:
        return mi_deteccion
    
    z1, R1 = mi_deteccion['pos'], mi_deteccion['cov']
    z2, R2 = deteccion_companero['pos'], deteccion_companero['cov']
    
    z1, R1 = np.array(z1), np.array(R1)
    z2, R2 = np.array(z2), np.array(R2)
    
    # Covarianza fusionada (siempre MENOR que ambas)
    P_fused = np.linalg.inv(np.linalg.inv(R1) + np.linalg.inv(R2))
    
    # Posición fusionada (promedio ponderado por precisión)
    z_fused = P_fused @ (np.linalg.inv(R1) @ z1 + np.linalg.inv(R2) @ z2)
    
    return {'pos': z_fused, 'cov': P_fused}
```

### 5.4 Tracking de oponentes cooperativo

```python
class CooperativeOpponentTracker:
    """Tracking de oponentes fusionando detecciones de 2 robots."""
    
    def __init__(self, n_opponents=2):
        # Un tracker por oponente
        self.trackers = [IMM_Tracker() for _ in range(n_opponents)]
    
    def update_from_local(self, detections):
        """Actualizar con mis propias detecciones."""
        for det in detections:
            opp_id = self.associate(det)  # ¿cuál oponente es?
            if opp_id >= 0:
                R = self.estimate_measurement_noise(det['distance'])
                self.trackers[opp_id].update(det['pos'], R)
    
    def update_from_teammate(self, teammate_detections, delay_ms):
        """Actualizar con detecciones del compañero.
        Compensar delay de comunicación."""
        for det in teammate_detections:
            opp_id = self.associate(det)
            if opp_id >= 0:
                # Predecir posición actual (compensar delay)
                pos_compensated = det['pos'] + det['vel'] * delay_ms/1000
                R = det['cov'] * (1 + delay_ms * 0.005)  # más incertidumbre por delay
                self.trackers[opp_id].update(pos_compensated, R)
    
    def associate(self, detection):
        """Asociar detección a oponente conocido (nearest neighbor)."""
        min_dist = float('inf')
        best_id = -1
        for i, tracker in enumerate(self.trackers):
            if tracker.initialized:
                dist = np.linalg.norm(detection['pos'] - tracker.get_position())
                if dist < min_dist and dist < 300:  # max 30cm de error
                    min_dist = dist
                    best_id = i
        return best_id
    
    def estimate_measurement_noise(self, distance):
        """Ruido de medición proporcional a la distancia.
        Más lejos = menos preciso."""
        sigma = 5.0 + distance * 0.03  # 5mm + 3% de la distancia
        return np.diag([sigma**2, sigma**2])
```

---

## 6. APLICACIONES TÁCTICAS

### 6.1 ¿Debería ir a la pelota o interceptar?

```python
def decision_tactica(world_model, my_pos, my_vel_max):
    """Decidir si ir directo a la pelota o al punto de intercepción."""
    ball_pos = world_model.ball_pos
    ball_vel = world_model.ball_vel
    ball_speed = np.linalg.norm(ball_vel)
    
    if ball_speed < 30:  # Pelota casi quieta
        return {'action': 'ir_a_pelota', 'target': ball_pos}
    
    # Calcular punto de intercepción
    intercept = calcular_interceptacion(my_pos, my_vel_max,
                                         ball_pos, ball_vel)
    if intercept['feasible']:
        return {'action': 'interceptar', 'target': intercept['intercept_point']}
    else:
        # No puedo interceptar → ir a donde va a parar
        pos_final, _ = posicion_final_pelota(ball_pos, ball_vel)
        return {'action': 'ir_a_destino', 'target': pos_final}
```

### 6.2 ¿Puede el oponente llegar antes que yo?

```python
def analisis_de_competencia(my_pos, opp_pos, ball_pos, ball_vel,
                             my_vel_max, opp_vel_max):
    """¿Quién llega primero a la pelota?"""
    # Predicción de pelota
    for t_ms in range(50, 2000, 50):
        ball_future, _ = predecir_pelota(ball_pos, ball_vel, t_ms)
        
        # ¿Puedo llegar yo?
        mi_dist = np.linalg.norm(ball_future - my_pos)
        mi_tiempo = mi_dist / my_vel_max * 1000
        
        # ¿Puede llegar el oponente?
        opp_dist = np.linalg.norm(ball_future - opp_pos)
        opp_tiempo = opp_dist / opp_vel_max * 1000
        
        if mi_tiempo <= t_ms:
            if opp_tiempo > t_ms:
                return 'yo_primero'
            elif mi_tiempo < opp_tiempo:
                return 'yo_primero_ajustado'
            else:
                return 'competencia_cerrada'
    
    return 'oponente_primero'
```

### 6.3 ¿A dónde pasar? (predicción de recepción)

```python
def evaluar_pase(my_pos, teammate_pos, teammate_vel,
                  opponents, kick_speed=500):
    """Evaluar si un pase al compañero es viable."""
    # Dirección del pase
    pase_dir = teammate_pos - my_pos
    pase_dist = np.linalg.norm(pase_dir)
    pase_dir_norm = pase_dir / pase_dist
    
    # Tiempo que tarda la pelota en llegar
    t_pase = pase_dist / kick_speed * 1000  # ms
    
    # ¿Dónde estará el compañero cuando llegue la pelota?
    mate_future = teammate_pos + teammate_vel * t_pase / 1000
    
    # ¿Puede algún oponente interceptar?
    for opp in opponents:
        for t in range(0, int(t_pase), 50):
            ball_t = my_pos + pase_dir_norm * kick_speed * t / 1000
            opp_future = opp['pos'] + opp['vel'] * t / 1000
            if np.linalg.norm(ball_t - opp_future) < 100:  # 10cm
                return {'viable': False, 'razon': 'oponente intercepta'}
    
    # Pase viable: pasar a la posición FUTURA del compañero
    return {
        'viable': True,
        'target': mate_future,  # ¡No a donde ESTÁ sino a donde VA A ESTAR!
        'lead_angle': math.degrees(math.atan2(
            mate_future[1] - my_pos[1],
            mate_future[0] - my_pos[0]
        ))
    }
```

---

## 7. COMPARATIVA DE MÉTODOS

| Método | Precisión tracking | Predicción | CPU | Cambios bruscos | Ideal para |
|--------|:-:|:-:|:-:|:-:|------|
| CV + KF | ⭐⭐ | ⭐⭐ | ⭐ | ❌ | Pelota rodando recto |
| CA + EKF | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Pelota frenando |
| CTRV + EKF | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Robot girando |
| UKF | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | No-linearidad fuerte |
| IMM (CV+CA+CT) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Oponentes (cambian!)** |
| Particle Filter | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Multimodal, oclusiones |
| DES (Double Exp) | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | Predicción simple |
| SPRLS | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Fricción variable |
| Deep RL (implícito) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Si hay GPU |

**Recomendación para RCJ Junior Soccer:**
- **Pelota**: EKF con modelo de fricción + predict_future()
- **Compañero**: CV + KF (comportamiento predecible)
- **Oponentes**: IMM (CV+CA+CT) — es el más importante
- **Fusión multi-robot**: Kalman fusion de detecciones

---

## 8. IMPLEMENTACIÓN INCREMENTAL

### Paso 1 (Arduino): EKF pelota simple
```
Sensores: 1 cámara + IR
→ Detectar pelota → EKF → posición + velocidad
→ predict_future(500ms) → ir al punto de intercepción
```

### Paso 2 (Arduino+): Agregar tracking de oponentes
```
Sensores: cámara + ultrasonido/ToF
→ Detectar oponentes → CV tracker por oponente
→ ¿Va hacia mi arco? → decisión defensiva
```

### Paso 3 (RPi): IMM para oponentes + fricción para pelota
```
→ IMM tracker por oponente (sabe si gira, frena, acelera)
→ Modelo de fricción para pelota
→ Punto de intercepción óptimo
```

### Paso 4 (Multi-robot): Fusión cooperativa
```
→ Comunicar detecciones entre robots
→ Fusión Kalman de pelota multi-robot
→ Tracking cooperativo de oponentes
→ Predicción de pase al compañero
```

---

## FUENTES

- Seekircher et al. (2011): "Accurate Ball Tracking with EKF" — RoboCup 3D Simulation
- Quinlan & Middleton (2010): "Multiple Model Kalman Filters" — RoboCup SPL
- Dias et al. (2012): "Real-Time 3D Ball Trajectory Estimation" — RoboCup MSL (CAMBADA)
- Birbach et al. (2009): "Tracking Ball Trajectories with Camera-Inertial Sensor" — RoboCup
- Schmitt et al. (2002): "Cooperative Probabilistic State Estimation" — IEEE Trans. Robotics
- Beetz et al. (2003): "Probabilistic Vision-Based Opponent Tracking" — RoboCup
- Haarnoja et al. (2024): "Learning Agile Soccer Skills" — Science Robotics (DeepMind)
- Blodow et al. (2006): "Interacting Multiple Model for Maneuvering Targets" — MATLAB/Simulink
- Prediction of Ball Trajectory for Humanoid Robots (2019) — Springer LNCS
- MDPI Sensors (2025): "Sensor-Fusion Based Navigation for AMR" — Review
