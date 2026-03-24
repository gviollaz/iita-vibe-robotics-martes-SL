# 📝 Skill: Judge Doc & GitHub Writer

## Cuándo usar

Para preparar la documentación que piden los jueces en competencia: engineering notebook, poster, video técnico, README del repo.

## Prompt para Engineering Notebook

```
Sos un mentor de robótica que ayuda a documentar para competencia.
Ayudame a escribir la entrada del engineering notebook de hoy.

FECHA: [fecha]
QUÉ HICIMOS: [describir]
QUÉ FUNCIONÓ: [describir]
QUÉ NO FUNCIONÓ: [describir]
QUÉ CAMBIARÍAMOS: [describir]
FOTOS/VIDEOS: [sí/no, describir]

Generá una entrada de notebook con:
1. Objetivo de la sesión
2. Diseño/cambios realizados
3. Resultados de las pruebas (con datos si hay)
4. Lecciones aprendidas
5. Próximos pasos

Tono: como si lo escribiera un estudiante de secundaria, claro y directo.
Idioma: español.
```

## Prompt para README de GitHub

```
Generá un README.md para nuestro repo de competencia:

EQUIPO: [nombre]
COMPETENCIA: [FLL/WRO/RoboCup]
ROBOT: [descripción corta]
LENGUAJE: Pybricks (Python)

Secciones:
1. Nombre del equipo y competencia
2. Descripción del robot (con foto si hay)
3. Estructura del código
4. Cómo correr el programa
5. Calibración necesaria
6. Resultados de pruebas
7. Integrantes del equipo
```

## Prompt para Video Técnico

```
Ayudame a planificar un video técnico de 1 minuto para los jueces.

ROBOT: [describir]
COMPETENCIA: [cuál]

Generá:
1. Guión (qué decir en cada segmento de ~10 segundos)
2. Tomas sugeridas (qué mostrar)
3. Puntos clave que los jueces quieren ver

Segmentos sugeridos:
- 0:00-0:10 → Presentación equipo + robot
- 0:10-0:25 → Mecánica innovadora
- 0:25-0:40 → Estrategia de software
- 0:40-0:55 → Demo funcionando
- 0:55-1:00 → Cierre
```

## Checklist de documentación por competencia

### FLL
- [ ] Engineering notebook (proceso de diseño)
- [ ] Poster o presentación de Innovation Project
- [ ] Core Values preparados
- [ ] Robot puede ser explicado por TODOS los miembros

### WRO
- [ ] Robot construido desde cero en cuarentena (si aplica)
- [ ] Código limpio y comentado
- [ ] El equipo puede explicar cada línea de código
- [ ] Estrategia documentada

### RoboCup Junior
- [ ] Technical Description Paper/Video
- [ ] Poster (en algunas categorías)
- [ ] El equipo puede explicar sensores, código y estrategia
- [ ] Código en GitHub (recomendado/requerido según liga)

## Regla de oro

Los jueces evalúan el PROCESO, no solo el resultado. Un equipo que documenta bien sus fracasos y lo que aprendió, puntúa más que uno que solo muestra el robot funcionando.
