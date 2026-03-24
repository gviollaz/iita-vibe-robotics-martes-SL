# 🎯 Skill: Mission Strategy Planner

## Cuándo usar

Cuando tenés el scoring de la competencia y necesitás decidir QUÉ misiones hacer, en qué ORDEN, y con qué PRIORIDAD.

## Prompt

```
Sos un estratega de robótica de competencia. Ayudame a planificar la estrategia óptima.

DATOS DE LA COMPETENCIA:
- Tiempo por ronda: [X] minutos
- Scoring: [pegar tabla de puntos]
- Número de runs/intentos permitidos: [X]
- Penalidades: [describir]

MI ROBOT:
- Tipo: [ej: Spike Prime 2WD con 2 motores attachment]
- Sensores: [ej: 2 color, 1 ultrasónico]
- Velocidad: [ej: ~350 mm/s]
- Attachments disponibles: [listar]

Necesito:

1. MATRIZ DE PRIORIDAD:
   Para cada misión: puntos, dificultad (1-5), tiempo estimado, 
   attachments necesarios, y ratio puntos/segundo.
   Ordenar por ratio puntos/segundo descendente.

2. PLAN DE RUNS:
   Agrupar misiones en runs según:
   - Proximidad geográfica en el campo
   - Mismo attachment
   - Secuencia lógica (una prepara la siguiente)
   Cada run: misiones incluidas, tiempo estimado, puntos esperados.

3. PLAN B:
   Para cada run, qué hacer si la misión principal falla:
   - ¿Saltar y seguir con la siguiente?
   - ¿Abortar el run y volver a base?
   - ¿Intentar una versión simplificada?

4. GESTIÓN DEL TIEMPO:
   Timeline minuto a minuto de la ronda ideal.
   Incluir tiempo de cambio de attachment (~5 seg).

5. EXPECTED VALUE:
   Puntos esperados si todo sale bien.
   Puntos esperados con 70% de éxito por misión.
   Puntos mínimos garantizados (misiones fáciles solamente).
```

## Ejemplo de uso para FLL

Con 2:30 minutos y ~15 misiones posibles:
- Run 1 (0:00-0:30): 3 misiones cercanas a la base, sin attachment especial → 60 pts
- Run 2 (0:35-1:05): 2 misiones zona central con attachment A → 80 pts  
- Run 3 (1:10-1:40): 2 misiones zona lejana con attachment B → 70 pts
- Run 4 (1:45-2:15): 1 misión de bonus si sobra tiempo → 30 pts
- Buffer: 15 segundos para imprevistos
- **Total esperado: 240 pts** / **Garantizado: 140 pts** (solo runs 1-2)

## Regla de oro

Consistencia > ambición. Es mejor planificar 200 puntos con 95% de éxito que 350 con 50%.
