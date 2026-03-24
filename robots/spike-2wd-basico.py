# ROBOT: Spike 2WD Básico
# Descripción: Chasis simple con 2 motores grandes y 2 ruedas medianas
# Puertos: Motor izq=E, Motor der=F
# Ruedas: Medianas Spike (56mm diámetro)
# Dist. ejes: 112mm (medir centro a centro)
# Vel. segura: 370 mm/s | Accel. segura: 250-350 mm/s²

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Direction, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
motor_izq = Motor(Port.E, Direction.COUNTERCLOCKWISE)
motor_der = Motor(Port.F)

DIAMETRO_RUEDA = 56.0   # mm — MEDIR CON CALIBRE
DISTANCIA_EJES = 112.0  # mm — MEDIR CENTRO A CENTRO

robot = DriveBase(motor_izq, motor_der,
                  wheel_diameter=DIAMETRO_RUEDA,
                  axle_track=DISTANCIA_EJES)
robot.use_gyro(True)

hub.imu.reset_heading(0)
wait(1500)

robot.settings(
    straight_speed=300,
    straight_acceleration=250,
    turn_rate=150,
    turn_acceleration=150,
)

hub.light.on(Color.GREEN)  # Listo

# ╔══════════════════════════════════════════╗
# ║  Tu código va acá abajo ↓               ║
# ╚══════════════════════════════════════════╝

