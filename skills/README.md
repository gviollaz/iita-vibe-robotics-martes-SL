# 🧠 Skills de Claude para Robótica

Los "Skills" son archivos que le dan conocimiento especializado a Claude.

## Skills disponibles

| Skill | Archivo | Qué hace |
|-------|---------|----------|
| Pybricks Competition | `pybricks-competition-robotics.md` | API completa + patrones de competencia |

## ¿Cómo usar?

**Opción 1** (mejor): Instalá el `.skill` en Claude.ai → Settings → Skills

**Opción 2**: Copiá el contenido del `.md` y pegalo como primer mensaje en Claude

## Pybricks Competition Quick Reference

### Límites de Hardware

| Motor           | Max con carga (°/s) | Con rueda 56mm (mm/s) |
|-----------------|:-------------------:|:---------------------:|
| Grande angular  | ~850                | ~415                  |
| Mediano angular | ~900                | ~440                  |

**Regla del 85%**: Velocidad segura = max con carga × 0.85

### Errores más comunes

1. Velocidad > capacidad del motor → robot se desvía
2. Aceleración > grip de las ruedas → patinaje
3. Reset de heading en cada giro → error se acumula
4. No esperar calibración del gyro → drift
5. Motores izq/der invertidos → gira en lugar de avanzar

### PID de Giro — Valores iniciales

| Param | Valor | Qué controla |
|-------|:-----:|-------------------------------|
| Kp    | 6.0   | Velocidad de respuesta |
| Ki    | 0.15  | Elimina error residual |
| Kd    | 8.0   | Frena antes de llegar (anti-overshoot) |

### Heading absoluto (nunca resetear)

```
Vuelta 1: 90° → 180° → 270° → 360°
Vuelta 2: 450° → 540° → 630° → 720°
```
