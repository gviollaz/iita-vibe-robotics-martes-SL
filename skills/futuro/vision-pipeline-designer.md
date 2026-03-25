---
name: vision-pipeline-designer
description: design robust computer vision pipelines for student competition robots under real field constraints. use when a user needs to choose sensors, detection methods, calibration steps, latency budgets, fallback logic, or experiments for line following, ball tracking, tags, object detection, localization, or mixed perception tasks in robocup junior, wro, fll, first, and similar leagues.
---

# Vision Pipeline Designer

> **Estado**: 🔮 FUTURO — Activar cuando se incorporen cámaras al taller

## Overview

Diseñar pipelines de visión que funcionen en cancha real, con presupuesto de cómputo limitado y variación de iluminación. Elegir sensores, procesamiento, calibración, métricas, fallbacks y pruebas antes de escribir código definitivo.

## Principio rector

Diseñar para robustez competitiva, no para demos perfectas. Preferir la solución más simple que entregue detección estable, latencia aceptable y recuperación clara ante fallas.

## Flujo de diseño

1. **Caracterizar la tarea visual**
   - Identificar qué debe estimarse: seguimiento de línea, detección de pelota, lectura de color, detección de tags/landmarks, localización relativa, segmentación, o combinación.
   - Definir si la salida es: `binary decision`, `class label`, `centroid or angle`, `pose`, o `tracking over time`.

2. **Caracterizar el entorno real**
   - Resumir fondo, color dominante, sombras, reflejos, LEDs, brillo, oclusiones, vibración y velocidad del robot.
   - Anotar qué cambia entre rondas: iluminación, posición de objetos, piezas del campo.
   - Si el reglamento admite fake targets o distractores, modelarlos como requisito explícito.

3. **Elegir la arquitectura sensorial**
   - Comparar cámara RGB, global shutter, sensor de color, sensor de distancia, IMU, odometría, tags, iluminación activa.
   - No forzar visión si un sensor más simple resuelve mejor una parte crítica.
   - Recomendar fusión sensorial cuando la cámara sola no cubra robustez o frecuencia.

4. **Elegir la familia de algoritmos**
   - Para cada objetivo, seleccionar y justificar:
     - umbralización y morfología;
     - detección de contornos y geometría;
     - filtros por color en HSV, LAB;
     - template matching;
     - optical flow;
     - tags fiduciales;
     - modelos de aprendizaje automático;
     - pipeline híbrido.
   - No usar modelos pesados si una heurística geométrica calibrada alcanza.
   - No usar umbrales fijos si la iluminación cambia mucho.

5. **Definir la cadena completa**
   - Etapas en orden: adquisición → preprocesado → segmentación/detección → filtrado temporal → estimación geométrica → validación de confianza → salida para control.
   - Para cada etapa: qué entra, qué sale, qué parámetro es crítico.

6. **Fijar presupuesto de tiempo y cómputo**
   - Frame rate objetivo, resolución de trabajo, latencia tolerable, uso de CPU estimado.
   - Qué etapa manda el costo y cómo recortar si el hardware no alcanza.

7. **Diseñar calibración**
   - Separar `factory calibration`, `pit calibration` y `pre-run quick check`.
   - Definir qué puede tocar el equipo sin romper reproducibilidad.

8. **Diseñar fallbacks y recovery**
   - Qué hace el robot si la confianza cae, el objetivo sale del frame o aparece ambigüedad.
   - Modos degradados: reducción de velocidad, búsqueda activa, confirmación con segundo sensor, retorno a estado seguro.

## Reglas de decisión

### Elegir el tipo de pipeline

| Situación | Pipeline recomendado |
|-----------|---------------------|
| Línea con alto contraste | Segmentación + features geométricas + control por error lateral |
| Pelota u objeto dinámico | Detección por color/forma + tracking temporal + filtro de falsas detecciones |
| Pose relativa a marcador | Tags fiduciales + calibración de cámara |
| Entorno muy variable | Modelo entrenado con dataset realista + plan de fallback |

### Evitar errores comunes

- No asumir iluminación uniforme.
- No evaluar solo en una mesa o cancha.
- No mezclar resolución alta con latencia no medida.
- No entregar "usar OpenCV" como respuesta — entregar pipeline, parámetros, métricas y pruebas.
- No usar red neuronal sin plan de dataset, inferencia y control del sesgo.

## Entregables obligatorios

### 1. `vision_design.md`

```markdown
# Vision design

## Task definition
## Environment assumptions
## Recommended sensor stack
## Pipeline stages
## Confidence and filtering
## Latency budget
## Failure modes and fallbacks
## First implementation plan
```

### 2. `parameter_table.md`

```markdown
| stage | parameter | initial value | tuning direction | effect on performance | notes |
|-------|-----------|---------------|------------------|-----------------------|-------|
```

### 3. `calibration_checklist.md`

Montaje y rigidez de cámara; enfoque y exposure; ROI; thresholds o normalización; chequeo de intrínsecos; verificación previa a cada run.

### 4. `vision_test_plan.md`

Pruebas por dificultad creciente: banco controlado, iluminación lateral, sombras duras, vibración, velocidad máxima, distractores visuales, oclusión parcial, variación entre canchas.

## Métricas mínimas

| Métrica | Qué mide |
|---------|----------|
| Tasa de detección útil | % frames con detección correcta |
| Falsas detecciones | % frames con detección errónea |
| Jitter de salida | Estabilidad de la estimación |
| Latencia extremo a extremo | Tiempo cámara→acción |
| Distancia máxima confiable | Rango útil de detección |
| Desempeño post-recalibración | Robustez ante cambio de escena |

## Formato de respuesta recomendado

1. resumen de la tarea visual;
2. sensor stack recomendado y por qué;
3. pipeline propuesto etapa por etapa;
4. parámetros críticos a tunear;
5. fallbacks;
6. plan de pruebas;
7. criterio para decidir si hace falta solución más compleja.
