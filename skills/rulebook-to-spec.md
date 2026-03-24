# 📋 Skill: Rulebook to Spec

## Cuándo usar

Antes de empezar a programar para una competencia. Pegale a la IA las reglas oficiales y pedile que genere un spec técnico.

## Prompt

```
Sos un analista técnico de robótica de competencia. Te voy a pasar las reglas de [COMPETENCIA]. Necesito que generes:

1. RESTRICCIONES DE HARDWARE:
   - Dimensiones máximas del robot (ancho × largo × alto)
   - Peso máximo
   - Sensores permitidos/prohibidos
   - Motores permitidos
   - Materiales permitidos/prohibidos
   - ¿Se puede expandir después de arrancar?

2. RESTRICCIONES DE SOFTWARE:
   - ¿Debe ser 100% autónomo? ¿Se permite control remoto en alguna fase?
   - ¿Un solo programa o múltiples?
   - ¿Se permite comunicación inalámbrica entre robots?
   - Lenguajes/plataformas permitidos

3. CHECKLIST DE COMPLIANCE (sí/no para verificar antes de competir):
   - [ ] Robot dentro de dimensiones
   - [ ] Peso dentro del límite
   - [ ] Solo sensores permitidos
   - [ ] Programa único identificable
   - [ ] (agregar según reglas)

4. MODELO DE SCORING:
   - Tabla de puntos por misión/acción
   - Penalidades
   - Criterio de desempate
   - Tiempo máximo por ronda

5. ELEMENTOS ALEATORIOS (si aplica):
   - ¿Qué cambia entre rondas?
   - ¿Hay reglas sorpresa?
   - ¿Se randomiza la posición de objetos?

6. DOCUMENTACIÓN REQUERIDA:
   - ¿Engineering notebook?
   - ¿Video técnico?
   - ¿Presentación ante jueces?
   - ¿GitHub/código fuente?

Formato: Markdown estructurado, listo para guardar como spec.md
```

## Por qué es importante

- WRO dice que su Q&A es parte oficial de las reglas
- RCJ avisa que puede haber aclaraciones en el foro antes de actualizar el PDF
- FLL publica Challenge Updates durante la temporada
- Cada organizador nacional puede tener variantes locales

## Tip

Descargar las reglas oficiales en PDF, pasárselas a Claude, y pedirle que genere el spec. Guardarlo en `competition-packs/[competencia]/spec.md` y revisarlo con el equipo.
