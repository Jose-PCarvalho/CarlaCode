import pygame
import numpy as np
import numpy.random as random
import carla

from agents.navigation.basic_agent import BasicAgent
from agents.navigation.behavior_agent import BehaviorAgent
from agents.navigation.constant_velocity_agent import ConstantVelocityAgent
from sim.utils import HUD, World, KeyboardControl


class Simulation(object):
    """ Class representing the simulation """
    def __init__(self):

        self.world = None
        self.client = None
        self.traffic_manager = None
        self.sim_world = None
        self.settings = None
        pygame.init()
        pygame.font.init()
        self.display = None
        self.hud = None
        self.controller = None
        self.clock = None
        self.spawn_points = None
        self.destination  = None
        self.args = None
        self.agent = None

    def init(self,args):
        self.args = args
        if args.seed:
            random.seed(args.seed)

        self.client = carla.Client(args.host, args.port)
        self.client.set_timeout(args.timeout)
        self.client.load_world(args.map)
        self.traffic_manager = self.client.get_trafficmanager()
        self.sim_world = self.client.get_world()

        if args.sync:
            self.settings = self.sim_world.get_settings()
            self.settings.synchronous_mode = True
            self.settings.fixed_delta_seconds = args.fixed_step
            self.sim_world.apply_settings(self.settings)
            self.traffic_manager.set_synchronous_mode(True)

        self.display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.hud = HUD(args.width, args.height)
        self.world = World(self.client.get_world(), self.hud, args)
        self.controller = KeyboardControl()

        if args.agent == "Basic":
            self.agent = BasicAgent(self.world.player, 30)
            self.agent.follow_speed_limits(True)
        elif args.agent == "Behavior":
            self.agent = BehaviorAgent(self.world.player, behavior=args.behavior)

        # Set the agent destination
        self.spawn_points = self.world.map.get_spawn_points()
        self.destination = random.choice(self.spawn_points).location
        self.agent.set_destination(self.destination)
        self.clock = pygame.time.Clock()

    def step(self):
        self.clock.tick()
        if self.args.sync:
            self.world.world.tick()
        else:
            self.world.world.wait_for_tick()
        if self.controller.parse_events():
            return
        self.world.tick(self.clock)
        self.world.render(self.display)
        pygame.display.flip()

        if self.agent.done():
            return True

        control = self.agent.run_step()
        control.manual_gear_shift = False
        self.world.player.apply_control(control)
        return False

    def destroy(self):
        if self.world is not None:
            settings = self.world.world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            self.world.world.apply_settings(settings)
            self.traffic_manager.set_synchronous_mode(True)

            self.world.destroy()

        pygame.quit()
