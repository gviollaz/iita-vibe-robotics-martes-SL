# 🧠 Skills de Robótica de Competencia

Cada skill es un conjunto de instrucciones que guían a la IA para producir no solo código, sino también plan de pruebas, failure modes, parámetros a tunear, y documentación. En robótica competitiva, eso vale más que "más líneas de código".

## Skills ACTIVOS (usar ahora)

| Skill | Archivo | Qué hace |
|-------|---------|----------|
| 🧭 Giroscopio | `guia-giroscopio.md` | Inicialización, calibración, PID giros, anti-drift |
| 📋 Rulebook → Spec | `rulebook-to-spec.md` | Convierte reglas de competencia en spec de ingeniería |
| 🎯 Mission Strategy | `mission-strategy-planner.md` | Scoring → plan de runs con expected value |
| 🤖 Autonomy Architecture | `autonomy-architecture.md` | State machines + recovery para misiones |
| 📝 Judge Doc Writer | `judge-doc-writer.md` | Documentación para jueces, notebook, video, README |

## Skills FUTUROS (en `futuro/`)

| Skill | Archivo | Cuándo activar |
|-------|---------|----------------|
| 👁️ Vision Pipeline | `futuro/vision-pipeline-designer.md` | Cuando se conecte cámara |
| 🛤️ Trajectory Planner | `futuro/trajectory-control-planner.md` | FTC/FRC/WRO FE |
| 🤝 Multi-Robot | `futuro/multi-robot-coordinator.md` | RCJ Soccer 2:2 |
| 🔌 Platform Adapter | `futuro/platform-adapter.md` | Arduino/RPi/ROS2 |
| 📊 Telemetry Analyzer | `futuro/telemetry-log-analyzer.md` | Debug complejo |
| 📡 Sensor Fusion | `futuro/sensor-fusion-positioning.md` | Posicionamiento multi-sensor |
| ⚽ Object Tracking | `futuro/object-tracking-prediction.md` | Tracking pelota/oponentes con IMM |

## Cómo usar

1. Abrí el skill `.md` que necesitás
2. Copiá el contenido y pegalo como primer mensaje en Claude/ChatGPT
3. La IA va a seguir el flujo de trabajo del skill automáticamente
4. El skill le pide a la IA que entregue no solo código sino también pruebas, parámetros, y documentación

## Origen

Los skills activos fueron creados combinando investigación propia (Claude) + skills de ingeniería (ChatGPT). Los skills futuros se basan en investigación de papers de RoboCup, WRO, y FIRST.
