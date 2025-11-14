import arcade
from view import SimulationView
from simulacion import CalidadSimulacion

if __name__ == "__main__":
    window = arcade.Window(
        title = "Gravity Sandbox",
        resizable=True,
        center_window= True,
    )
    sim = SimulationView(
        CalidadSimulacion.BAJA
    )
    window.show_view(sim)
    arcade.run()
