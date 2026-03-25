---
name: rulebook-to-spec
description: convert competition rulebooks, rubrics, q&a updates, and local addenda into an engineering-ready spec for student robotics teams. use when a user shares rules for robocup junior, wro, fll, first, or similar competitions and needs a compliance checklist, scoring priorities, field model, edge cases, and a test plan before designing code, hardware, or strategy.
---

# Rulebook To Spec

## Overview

Convertir reglas de competencia en una especificación de ingeniería accionable. Tomar PDFs, páginas web, Q&A, rúbricas, updates y notas del organizador y transformarlos en restricciones duras, objetivos de scoring, supuestos abiertos y pruebas verificables.

## Flujo de trabajo

1. **Construir el mapa de fuentes**
   - Listar cada fuente disponible con su tipo: `rulebook`, `rubric`, `q&a`, `update`, `local_addendum`, `forum clarification`, `mentor note`.
   - Priorizar en este orden cuando haya conflicto: `local_addendum` > `official update or q&a` > `main rulebook` > `rubric` > material histórico.
   - Marcar cada conflicto de interpretación de forma explícita. No resolver silenciosamente ambigüedades.

2. **Separar tipos de exigencia**
   - Etiquetar cada hallazgo como una de estas clases:
     - `hard_constraint`: descalifica, limita o prohíbe.
     - `scoring_rule`: suma, resta o condiciona puntos.
     - `field_condition`: describe geometría, tolerancias, iluminación, objetos, aleatoriedad o setup.
     - `match_flow`: inicio, stop, resets, tiempo, intervención humana, checkpoints.
     - `documentation_requirement`: video, github, engineering notebook, CAD, wiring, evidencias.
     - `recommendation`: sugerencia no obligatoria.
   - No mezclar reglas obligatorias con consejos de diseño.

3. **Traducir reglas a implicancias de ingeniería**
   - Derivar impactos reales sobre percepción, control, mecánica, energía y estrategia.
   - Buscar especialmente restricciones implícitas que suelen pasarse por alto:
     - tamaño y peso en condiciones reales, no solo en CAD;
     - condiciones de inicio y orientación;
     - si el campo puede cambiar entre rondas;
     - si está prohibido precargar el mapa;
     - tolerancias de color, reflectancia, obstáculos, rampas o iluminación;
     - cuándo se permite tocar el robot;
     - qué información puede o no recibir el robot del exterior;
     - evidencias mínimas exigidas para jueces.

4. **Convertir scoring en prioridades operativas**
   - Identificar objetivos de alto valor, bajo riesgo y baja dependencia.
   - Marcar acciones con alto puntaje pero alta fragilidad.
   - Señalar dependencias críticas: misiones que solo valen si una condición previa se cumplió.
   - Priorizar consistencia y reproducibilidad por encima del caso ideal cuando el reglamento premie runs confiables.

5. **Derivar un modelo del campo y del run**
   - Resumir el campo como entidades medibles: líneas, paredes, zonas, tags, pelotas, víctimas, objetivos, obstáculos, checkpoints.
   - Resumir el run como estados: `start`, `search`, `align`, `pickup`, `deliver`, `recovery`, `stop`, u otros equivalentes.
   - Si el reglamento usa aleatoriedad o variantes del setup, producir una lista de escenarios válidos.

6. **Emitir artefactos listos para usar**
   - Generar siempre los entregables de la sección siguiente.
   - Si falta información, completar con `unknown` y un bloque de `questions_to_resolve`.

## Entregables obligatorios

### 1. `competition_spec.yaml`

```yaml
competition:
  name:
  season:
  league:
  source_priority:
    - local_addendum
    - official_update
    - main_rulebook
    - rubric

hard_constraints:
  - id:
    rule:
    source:
    engineering_impact:

scoring_objectives:
  - id:
    objective:
    points_or_value:
    prerequisites:
    risk_level:
    automation_notes:

field_model:
  entities:
    - name:
      type:
      measurable_properties:
  variants:
    - description:
      impact:

run_flow:
  time_limit:
  start_conditions:
  allowed_human_intervention:
  stop_conditions:
  resets_and_penalties:

perception_requirements:
  targets:
  lighting_or_color_notes:
  ambiguity_risks:

control_requirements:
  precision_needs:
  speed_needs:
  recovery_needs:

documentation_requirements:
  required_artifacts:
  judging_emphasis:

unknowns:
  - item:
    why_it_matters:

questions_to_resolve:
  - question:
    blocking_level:
```

### 2. `compliance_checklist.md`

```markdown
# Compliance checklist

## Robot eligibility
- [ ] Dimensiones y peso verificados en condición de competencia
- [ ] Actuadores, energía y materiales cumplen reglas

## Match procedure
- [ ] Inicio configurado exactamente como exige el reglamento
- [ ] Condiciones de intervención humana claras para el equipo

## Autonomy and sensing
- [ ] El robot no usa información prohibida
- [ ] La calibración posible en evento está definida y ensayada

## Documentation and judging
- [ ] README, video, notebook, CAD y wiring listos si aplican

## Open questions
- [ ] ...
```

### 3. `strategy_priorities.md`

Incluir: top objetivos de alto valor esperado; objetivos de alto riesgo para segunda iteración; estrategia segura de run; estrategia agresiva de run; qué capacidades construir primero.

### 4. `test_matrix.md`

```markdown
| id | requirement | test setup | success condition | failure mode | priority |
|----|-------------|------------|-------------------|--------------|----------|
```

## Heurísticas de calidad

- Citar siempre el origen de cada restricción usando página, sección o URL.
- No inventar tolerancias numéricas que la fuente no diga.
- Explicar qué parte es texto oficial y qué parte es inferencia de ingeniería.
- Convertir toda ambigüedad importante en una pregunta concreta para juez u organizador.
- Resaltar dependencias entre reglas y documentación.

## Patrones por tipo de liga

### Ligas con navegación y misiones (FLL, WRO RoboMission)
- Modelar el problema como secuencia de tareas con precondiciones y recuperación.
- Distinguir puntaje base de puntaje por precisión o bonus.

### Ligas con pelota, oponentes o multi-robot (RCJ Soccer, WRO RoboSports)
- Separar reglas de interacción física, visión dinámica y estrategia de roles.
- Marcar incertidumbre por oclusión, rebotes y decisiones distribuidas.

### Ligas con judging técnico fuerte (WRO FE, FTC)
- Extraer artefactos exigidos por la rúbrica como requisitos de primer orden, no como tarea final opcional.

## Formato de respuesta recomendado

1. resumen ejecutivo corto;
2. principales restricciones duras;
3. prioridades de scoring;
4. ambigüedades o conflictos detectados;
5. `competition_spec.yaml`;
6. checklist de compliance;
7. matriz de pruebas.
