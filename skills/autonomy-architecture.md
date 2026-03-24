# 🤖 Skill: Autonomy Architecture Generator

## Cuándo usar

Cuando el robot necesita tomar decisiones autónomas: seguir línea con intersecciones, detectar colores y actuar diferente, manejar obstáculos, o resolver misiones WRO con aleatoriedad.

## Prompt

```
Sos un arquitecto de software para robots autónomos de competencia.
Ayudame a diseñar la arquitectura del programa.

MI ROBOT:
- Plataforma: [Spike Prime / Arduino / etc]
- Sensores: [listar todos con puertos]
- Actuadores: [motores de tracción + attachments]

LA MISIÓN:
[Describir qué tiene que hacer el robot paso a paso,
incluyendo qué puede variar entre rondas]

Necesito:

1. DIAGRAMA DE ESTADOS (State Machine):
   - Lista de estados posibles
   - Transiciones entre estados (qué sensor/condición dispara cada una)
   - Estado inicial y estados finales
   - Estados de error/recovery

2. PSEUDOCÓDIGO de la máquina de estados

3. MÓDULOS SEPARADOS:
   - Percepción (lectura y procesamiento de sensores)
   - Decisión (lógica de estados y transiciones)
   - Acción (control de motores y actuadores)
   - Recovery (qué hacer cuando algo sale mal)

4. FAILURE MODES:
   - ¿Qué pasa si el sensor no detecta la línea?
   - ¿Qué pasa si el robot se traba (stall)?
   - ¿Qué pasa si se pasa de tiempo?
   - Para cada failure: acción de recovery

5. PARÁMETROS CONFIGURABLES:
   - Lista de todos los valores que hay que tunear
   - Valor inicial sugerido para cada uno
   - Cómo testearlo

Formato: código Pybricks completo con comentarios
```

## Ejemplo: WRO con detección de color

```
Estados:
  INICIO → BUSCAR_LINEA → SEGUIR_LINEA → DETECTAR_COLOR
  DETECTAR_COLOR → ACCION_ROJA | ACCION_AZUL | ACCION_VERDE
  ACCION_* → SEGUIR_LINEA (continuar)
  cualquier_estado → TIMEOUT → FIN
  SEGUIR_LINEA → LINEA_PERDIDA → BUSCAR_LINEA
```

## Patrón Pybricks

```python
# Definir estados como constantes
BUSCAR = 0; SEGUIR = 1; DETECTAR = 2; ACTUAR = 3; FIN = 4
estado = BUSCAR
reloj = StopWatch()

while estado != FIN:
    if reloj.time() > TIMEOUT_MS:
        estado = FIN  # Safety timeout
    
    elif estado == BUSCAR:
        robot.drive(100, 0)
        if sensor.reflection() < 20:
            estado = SEGUIR
    
    elif estado == SEGUIR:
        # PID line following
        error = sensor.reflection() - TARGET
        robot.drive(VEL, KP * error)
        if sensor_color.color() != Color.NONE:
            estado = DETECTAR
        if sensor.reflection() > 80:  # Perdió línea
            estado = BUSCAR
    
    elif estado == DETECTAR:
        robot.stop()
        color = sensor_color.color()
        acciones[color]()  # Ejecutar acción según color
        estado = SEGUIR
    
    wait(10)

robot.stop()
```

## Regla de oro

Cada estado debe tener:
1. Una condición de ENTRADA clara
2. Una acción que ejecuta
3. Condiciones de SALIDA a otros estados
4. Un TIMEOUT de seguridad
5. Un camino de RECOVERY si algo falla
