# ⚡ Pybricks Cheatsheet

## Imports
```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Color, Button, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
```

## Hub
```python
hub = PrimeHub()
hub.speaker.beep(1000, 200)      # frecuencia Hz, duración ms
hub.light.on(Color.GREEN)         # LED del botón
hub.display.number(42)            # Pantalla 5×5
hub.buttons.pressed()             # → set de Button
hub.battery.voltage()             # → mV
```

## Giroscopio
```python
hub.imu.reset_heading(0)          # Solo al inicio!
hub.imu.heading()                 # → grados (acumula, no wrappea)
hub.imu.ready()                   # → bool (calibrado?)
hub.imu.stationary()              # → bool (quieto?)
hub.imu.settings(heading_correction=363.8)  # Calibrar
```

## Motor
```python
motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor.run(500)                    # Correr a 500°/s
motor.run_angle(500, 360)         # 500°/s por 360°
motor.run_time(500, 2000)         # 500°/s por 2 segundos
motor.stop() / .brake() / .hold()
motor.angle()                     # → posición actual
motor.speed()                     # → velocidad actual
motor.reset_angle(0)
```

## DriveBase
```python
robot = DriveBase(motor_izq, motor_der, wheel_diameter=56, axle_track=112)
robot.use_gyro(True)              # SIEMPRE
robot.settings(straight_speed=300, straight_acceleration=200,
               turn_rate=150, turn_acceleration=150)
robot.straight(500)               # Avanzar 500mm
robot.turn(90)                    # Girar 90° (horario)
robot.drive(300, 0)               # Continuo: 300mm/s, recto
robot.stop()
```

## Colores
```python
Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN,
Color.CYAN, Color.BLUE, Color.MAGENTA, Color.WHITE
```
