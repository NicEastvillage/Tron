from rlbot.agents.base_script import BaseScript

from trail import Trail
from vec import Vec3


class Tron(BaseScript):
    def __init__(self):
        super().__init__("Tron")
        self.trails = []
        self.is_kickoff = True

    def run(self):
        while True:
            packet = self.wait_game_tick_packet()
            time = packet.game_info.seconds_elapsed

            ball_pos = Vec3(packet.game_ball.physics.location)

            if ball_pos.x == 0 and ball_pos.y == 0 and packet.game_info.is_kickoff_pause:
                # Kickoff
                if not self.is_kickoff:
                    # It was not kickoff previous frame
                    for trail in self.trails:
                        trail.clear(self.game_interface.renderer)

                self.is_kickoff = True

            else:
                self.is_kickoff = False

                # Update and render trails
                for index in range(packet.num_cars):
                    car = packet.game_cars[index]

                    if index >= len(self.trails):
                        self.trails.append(Trail(index, car.team))

                    trail = self.trails[index]
                    trail.update(car, time)
                    trail.do_collisions(self, packet)
                    trail.render(self.game_interface.renderer)


if __name__ == "__main__":
    script = Tron()
    script.run()
