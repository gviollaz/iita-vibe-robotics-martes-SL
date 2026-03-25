---
name: judge-doc-and-github-writer
description: turn robotics project work into clear judge-facing documentation and reproducible github artifacts. use when a user needs readmes, engineering notebook entries, experiment logs, technical summaries, commit plans, repository cleanup, or evidence packages for robocup junior, wro, fll, first, and similar student robotics competitions.
---

# Judge Doc And GitHub Writer

## Overview

Convertir avances técnicos del robot en documentación que ayude a jueces, mentores y compañeros a entender qué se hizo, por qué se hizo y qué evidencia demuestra que funciona. Escribir para reproducibilidad, trazabilidad y credibilidad técnica.

## Principio rector

Escribir desde evidencia observable, no desde marketing. Toda afirmación fuerte debe apoyarse en prueba, comparación, dato, imagen, video, commit o experimento.

## Flujo de trabajo

1. **Inventariar evidencia disponible**
   - Recolectar cambios de hardware, software, estrategia y pruebas.
   - Listar assets: fotos, wiring, CAD, videos, tablas, logs, resultados, capturas, commits.
   - Detectar vacíos de evidencia antes de redactar.

2. **Elegir el paquete documental correcto**
   - Según la competencia y la etapa del proyecto, decidir cuáles artefactos producir:
     - `README.md` del repo;
     - `engineering_notebook_entry.md`;
     - `experiment_log.md`;
     - `technical_description.md`;
     - `video_outline.md`;
     - `judge_qa_brief.md`;
     - `repo_cleanup_checklist.md`.
   - No producir todos siempre si no agregan valor. Priorizar lo que la rúbrica pide.

3. **Redactar en formato técnico**
   - Explicar problema, hipótesis, implementación, evidencia, resultado y próximo paso.
   - Usar comparaciones antes/después cuando existan.
   - Traducir detalles complejos a lenguaje claro sin perder precisión.

4. **Conectar documentación con GitHub**
   - Alinear README, estructura de carpetas, nombres de archivos, releases, commits y evidencias.
   - Señalar archivos faltantes para que otro equipo pueda reconstruir el robot.
   - Convertir cambios grandes en un plan de commits significativo.

5. **Cerrar con trazabilidad**
   - Vincular cada afirmación importante con una prueba o un archivo.
   - Dejar próximos pasos concretos, no cierres vagos.

## Reglas de escritura

- Usar títulos descriptivos.
- Preferir frases concretas: "redujimos falsos positivos de 7/20 a 1/20" es mejor que "mejoramos bastante".
- Diferenciar claramente: lo implementado, lo probado una vez, y lo que es hipótesis.
- No ocultar fallas. Explicar causa probable, impacto y siguiente experimento.
- No inflar complejidad. Si una heurística simple resolvió el problema, decirlo.

## Artefactos y plantillas

### 1. `README.md`

```markdown
# Project name

## Goal
## Competition and season
## Robot architecture
## Hardware
## Software
## How to run
## Calibration steps
## Repository structure
## Current performance
## Known limitations
## Next steps
```

### 2. `engineering_notebook_entry.md`

```markdown
# Entry title

## Date
## Objective
## Change made
## Why this change was needed
## Evidence collected
## Result
## What we learned
## Next experiment
```

### 3. `experiment_log.md`

```markdown
| date | experiment | variable changed | expected effect | observed result | conclusion | next step |
|------|------------|------------------|-----------------|-----------------|------------|----------|
```

### 4. `technical_description.md`

Incluir: arquitectura del robot; sensores y actuadores; pipeline de percepción o control; estrategia de run o match; principales trade-offs; riesgos abiertos.

### 5. `video_outline.md`

1. problema o desafío de competencia;
2. arquitectura general;
3. subsistema más diferencial;
4. evidencia de pruebas;
5. resultado actual;
6. próximos pasos.

### 6. `judge_qa_brief.md`

Preparar respuestas cortas y verificables para preguntas típicas:
- ¿Qué hace diferente a este robot?
- ¿Qué falla encontraron y cómo la resolvieron?
- ¿Cómo calibran antes de competir?
- ¿Qué parte fue más difícil de diseñar?
- ¿Cómo validaron que la mejora era real?

### 7. `repo_cleanup_checklist.md`

- [ ] carpetas con nombres claros
- [ ] archivos muertos removidos o archivados
- [ ] README actualizado
- [ ] instrucciones de setup probadas en limpio
- [ ] parámetros críticos documentados
- [ ] evidencia enlazada desde el README o notebook
- [ ] commits agrupados por cambio lógico

## Reglas para commits y trazabilidad

- Commits pequeños con intención clara.
- Separar cambios de hardware, control, visión y documentación.
- Mensajes que expliquen el porqué además del qué.
- Cambios experimentales visibles en notebook aunque no queden en la solución final.

## Formato de respuesta recomendado

1. qué artefactos conviene producir para esta situación;
2. borradores listos para copiar;
3. evidencia faltante o débil;
4. mejoras de estructura para el repo;
5. plan de commits o checklist de cierre.
