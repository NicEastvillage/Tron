from dataclasses import dataclass

from rlbot.utils.game_state_util import GameState, BallState, Physics

from vec import Vec3


class Trail:
    def __init__(self, index, team):
        self.index = index
        self.team = team
        self.points = []

        self.duration = 12

        self.segment_size = 115

    def clear(self):
        self.points = []

    def update(self, car, time):

        pos = Vec3(car.physics.location) + Vec3(z=12)
        if len(self.points) == 0:
            # Initial point
            point = TrailPoint(pos, time)
            self.points.append(point)
        else:
            # Add points
            prev = self.points[-1]
            diff = pos - prev.pos
            if diff.longer_than(self.segment_size):
                point = TrailPoint(pos, time)
                self.points.append(point)

        # Remove points
        earliest = self.points[0]
        if earliest.time + self.duration < time:
            self.points = self.points[1:]

    def do_collisions(self, script, packet):
        ball_pos = Vec3(packet.game_ball.physics.location)
        for i in range(len(self.points) - 2):
            seq_start = self.points[i].pos
            seq_end = self.points[i + 1].pos

            seq = seq_end - seq_start
            ball_pos_from_seq_pov = ball_pos - seq_start
            t = (ball_pos_from_seq_pov.dot(seq) / seq.dot(seq))
            ball_proj_seq = seq * t
            seq_ball = (ball_pos_from_seq_pov - ball_proj_seq)
            if 0 <= t <= 1 and not seq_ball.longer_than(100):
                # Collision
                seq_ball_u = seq_ball.unit()
                vel = Vec3(packet.game_ball.physics.velocity)
                refl_vel = vel - 2 * vel.dot(seq_ball_u) * seq_ball_u
                ball_pos_moved = seq_start + ball_proj_seq + seq_ball_u * 101
                script.set_game_state(GameState(ball=BallState(physics=Physics(
                    location=ball_pos_moved.to_desired_vec(),
                    velocity=refl_vel.to_desired_vec())
                )))
                pass

    def render(self, renderer):
        if len(self.points) > 1:
            renderer.begin_rendering(f"trail-{self.index}-mid")
            points = list(map(lambda p: p.pos, self.points))
            renderer.draw_polyline_3d(points, renderer.white())
            renderer.end_rendering()

            renderer.begin_rendering(f"trail-{self.index}-top")
            blue = renderer.create_color(255, 0, 150, 255)
            orange = renderer.orange()
            points = list(map(lambda p: p.pos + Vec3(z=10), self.points))
            color = blue if self.team == 0 else orange
            renderer.draw_polyline_3d(points, color)
            renderer.end_rendering()

            renderer.begin_rendering(f"trail-{self.index}-bottom")
            blue = renderer.create_color(255, 0, 150, 255)
            orange = renderer.orange()
            points = list(map(lambda p: p.pos + Vec3(z=-10), self.points))
            color = blue if self.team == 0 else orange
            renderer.draw_polyline_3d(points, color)
            renderer.end_rendering()


@dataclass
class TrailPoint:
    pos: Vec3
    time: float