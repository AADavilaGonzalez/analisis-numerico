import random
from time import time
from typing import Hashable, Any
from dataclasses import dataclass

import arcade
import arcade.color as color
import arcade.gui as gui

from simulacion import (
    CalidadSimulacion,
    ObjetoGravitacional,
    SimulacionGravitacional2D,
    Punto 
)

@dataclass
class SimObj:
    x: float
    y: float
    r: float
    color: Any

object_colors = [
    color.RED,
    color.BLUE,
    color.AFRICAN_VIOLET,
    color.GREEN,
    color.AMBER,
    color.YELLOW
]

sim_quality_name = {
    CalidadSimulacion.BAJA: "Baja",
    CalidadSimulacion.MEDIA: "Media",
    CalidadSimulacion.ALTA: "Alta"
}

class SimulationView(arcade.View):

    VEL_MULT = 0.1
    CULL_RANGE = 0.9

    def vw(self, pcnt:float) -> float:
        return pcnt*self.width

    def vh(self, pcnt:float) -> float:
        return pcnt*self.height

    def to_ss(
        self,
        x:float, # [-1, 1]
        y:float  # [-1, 1]
    ) -> tuple[float, float]:
        x_center, y_center = self.center
        return (
            x_center + x*x_center,
            y_center + y*y_center
        )
    
    def to_ws(
        self,
        x:float, # [0, self.width]
        y:float  # [0, self.heigth]
    ) -> tuple[float, float]:
        x_center, y_center = self.center
        return (
            (x-x_center)/x_center,
            (y-y_center)/y_center
        )


    def cycle_sim_quality(self):
        match self.simulation.calidad_simulacion:
            case CalidadSimulacion.BAJA:
                self.simulation.calidad_simulacion = CalidadSimulacion.MEDIA
            case CalidadSimulacion.MEDIA:
                self.simulation.calidad_simulacion = CalidadSimulacion.ALTA
            case CalidadSimulacion.ALTA:
                self.simulation.calidad_simulacion = CalidadSimulacion.BAJA
        self.sim_quality_label.text = sim_quality_name.get(
            self.simulation.calidad_simulacion
        )


    def __init__(self, initial_quality: CalidadSimulacion):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.simulation = SimulacionGravitacional2D(
            [], h=0.1, capacidad_inicial=10,
            calidad = initial_quality
        )
        self.objects: dict[Hashable, SimObj] = {}
        self.next_id = 1

        self.last_click_pos: tuple[float, float] = (0, 0)
        self.last_click_time: float = time()

        self.ui = gui.UIManager()
        anchor = self.ui.add(gui.UIAnchorLayout())
        v_box = anchor.add(
            gui.UIBoxLayout(vertical=True).with_padding(all=10),
            anchor_x="right", anchor_y="top"
        )
        v_box.with_background(color=arcade.color.DARK_BLUE_GRAY)
        self.sim_quality_label = v_box.add(
            gui.UILabel(text = sim_quality_name[initial_quality], font_size=20)
        )
        cycle_button = v_box.add(gui.UIFlatButton(text="Cambiar Calidad", width=150))
        cycle_button.on_click = lambda event : self.cycle_sim_quality()

        self.cull_queue: set[Hashable] = set()
        arcade.schedule(self.mark_objects_to_cull, 5)
        arcade.schedule(self.log_object_count, 3)


    def log_object_count(self, delta_time):
        print(f"objetos simulados: {self.simulation.n}")


    def mark_objects_to_cull(self, delta_time):
        for id, obj in self.objects.items():
            cull_x = not (-self.CULL_RANGE < obj.x < self.CULL_RANGE)
            cull_y = not (-self.CULL_RANGE < obj.y < self.CULL_RANGE)
            if cull_x or cull_y: self.cull_queue.add(id)


    def cull_objects(self):
        for id in self.cull_queue:
            self.simulation.delete_objeto(id)
            self.objects.pop(id, None)
        self.cull_queue.clear()


    def on_show_view(self):
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()


    def on_draw(self):
        self.clear()
        for obj in self.objects.values():
            arcade.draw_circle_filled(
                *self.to_ss(obj.x,obj.y),
                self.vw(obj.r),
                obj.color
            )
        self.ui.draw()


    def on_update(self, delta_time):
        if self.simulation.n == 0: return

        self.simulation.avanzar_simulacion()
        for obj in self.simulation.get_objetos():
            simobj = self.objects[obj.id]
            simobj.x = obj.r.x
            simobj.y = obj.r.y

        if self.cull_queue:
            self.cull_objects()


    def on_mouse_press(self,x,y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.last_click_pos = self.to_ws(x,y)
            self.last_click_time = time()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            x, y = self.to_ws(x,y)
            lx, ly = self.last_click_pos
            dt = time() - self.last_click_time
            vx = self.VEL_MULT*(x-lx)/dt
            vy = self.VEL_MULT*(y-ly)/dt
            self.objects[self.next_id] = SimObj(
                x = x,
                y = y,
                r = 0.01+dt*0.01,
                color=random.choice(object_colors)
            )
            self.simulation.add_objeto(
                ObjetoGravitacional(
                    id= self.next_id,
                    m= 0.5+dt,
                    r= Punto(x,y),
                    v= Punto(vx,vy)
                )
            )
            self.next_id += 1
