# 🎯 Guía de Vibe Coding para Robótica

## ¿Qué es Vibe Coding?

Programar pidiéndole a una IA (Claude, ChatGPT) que escriba el código.
Vos le describís qué querés que haga el robot, la IA genera el código,
y vos lo probás y ajustás en el robot real.

No necesitás saber programar desde cero. Pero sí necesitás:
- Saber describir bien lo que querés
- Entender los errores que aparecen
- Tener paciencia para iterar

## El ciclo

```
DESCRIBIR → GENERAR → PROBAR → OBSERVAR → AJUSTAR
    ↑                                        |
    └────────────────────────────────────────↩
```

### 1. DESCRIBIR
Contale a la IA: qué robot tenés, qué querés que haga,
qué tan preciso necesitás, y si hay restricciones.

### 2. GENERAR
La IA escribe el código. Pedí que sea completo, con
comentarios en español, y listo para copiar y pegar.

### 3. PROBAR
Copiá a [code.pybricks.com](https://code.pybricks.com) y correlo.

### 4. OBSERVAR
¿Se mueve derecho? ¿Los giros son exactos? ¿Patina?
¿Hay error en la consola?

### 5. AJUSTAR
Contale a la IA exactamente qué observaste.
"El robot patina cuando arranca y después de 4 giros
termina desviado unos 5 grados"

## Herramientas

- **Pybricks**: [code.pybricks.com](https://code.pybricks.com)
- **Claude**: [claude.ai](https://claude.ai)
- **Este repo**: Guardá todo lo que funcione

## Niveles

### 🟢 Principiante
- Copiar ejemplos y modificar números
- Usar el prompt de `directivas-ia/system-prompts/`
- Programas simples (avanzar, girar, cuadrado)

### 🟡 Intermedio
- Combinar funciones (avanzar + girar + sensor)
- Entender el PID básico
- Calibrar el robot
- Crear propios prompts

### 🔴 Avanzado
- Escribir propias funciones
- Tunear PID
- Crear rutinas de competencia
- Contribuir skills y directivas
