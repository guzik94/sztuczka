import unittest
from pygejm.constants import none_vis_id, game_height
from pygame import Rect
from pygejm.observation import Observation, x_distance_function, y_distance_function
from pygejm.observation import CommonSensors
from pygejm.visible_object import VisibleObject


class TestDistance(unittest.TestCase):
    def setUp(self):
        self.x_rect = Rect((0, 0), (10, 10))
        self.ac_rect = Rect((10, 0), (10, 10))

        self.x_rect2 = Rect((0, 0), (10, 10))
        self.ac_rect2 = Rect((20, 20), (10, 10))

        self.y_rect = Rect((2, 0), (10, 10))
        self.y_rect2 = Rect((8, 9), (10, 10))

    def test_distance_horizontal(self):
        dist = x_distance_function(self.x_rect, self.ac_rect)
        self.assertEqual(0, dist)

    def test_distance_horizontal_2(self):
        dist = x_distance_function(self.x_rect2, self.ac_rect2)
        self.assertEqual(10, dist)

    def test_distance_vertical(self):
        dist = y_distance_function(self.x_rect, self.ac_rect)
        self.assertEqual(0, dist)

    def test_distance_vertical_2(self):
        dist = y_distance_function(self.x_rect2, self.ac_rect2)
        self.assertEqual(10, dist)

    def test_collides_means_minus1_distance(self):
        dist = x_distance_function(self.ac_rect, self.y_rect)
        self.assertEqual(-1, dist)

    def test_collides_means_minus1_distance_y(self):
        dist = y_distance_function(self.ac_rect, self.y_rect2)
        self.assertEqual(-1, dist)


class TestSensor(unittest.TestCase):
    def setUp(self):
        self.x_rect = VisibleObject(Rect((0, 0), (10, 10)), 2)
        self.ac_rect = VisibleObject(Rect((10, 0), (10, 10)), 1)

        self.x_rect2 = VisibleObject(Rect((0, 0), (10, 10)), 2)
        self.ac_rect2 = VisibleObject(Rect((20, 20), (10, 10)), 1)

    def test_sensor_doesnt_see_actor(self):
        s = CommonSensors.left(self.ac_rect.rect)
        s.add_objects_if_visible([self.ac_rect])

        self.assertEqual([], s.get_nearest())

    def test_sensor_left(self):
        left_sensor = CommonSensors.left(self.ac_rect.rect)
        left_sensor.add_objects_if_visible([self.x_rect])

        self.assertEqual([0, 2], left_sensor.get_nearest())

    def test_sensor_down(self):
        s = CommonSensors.down(self.x_rect.rect)
        s.add_objects_if_visible(
            [VisibleObject(Rect((5, 100), (10, 10)), 1)])

        self.assertEqual([90, 1], s.get_nearest())

    def test_sensor_with_multiple_objects(self):
        s = CommonSensors.down(self.x_rect.rect)

        vos = [VisibleObject(Rect((5, i), (10, 10)), 1) for i in range(120, 150)]
        s.add_objects_if_visible(vos)

        self.assertEqual(30, len(s.get_nearest(100)))
        self.assertEqual([[110, 1],
                          [111, 1],
                          [112, 1]],
                         s.get_nearest(3))


class TestObservation(unittest.TestCase):
    def setUp(self):
        self.x_rect = VisibleObject(Rect((0, 0), (10, 10)), 2)
        self.ac_rect = VisibleObject(Rect((10, 0), (10, 10)), 1)

    def test_get_observation_from_directional_sensors(self):
        vos = [VisibleObject(Rect((5, i*20), (10, 10)), i)
               for i in range(2, 10)]

        obs = Observation()
        obs.update_sensors(self.x_rect)

        '''
        Map is like following (. :actor, * :visible object)
0       |.|
10      | |
        | |
        | |
40      |*|
        | |
60      |*|
        '''

        prepr_obs = obs.get_observation(self.x_rect, vos,
                                        preproc_mode='')

        z = none_vis_id
        x = [0, 0, 30, 0, z, z, 2, z] == prepr_obs
        self.assertTrue(x.all())

    def test_feature_collide(self):
        vos = [VisibleObject(Rect((5, i*20), (10, 10)), i+1)
               for i in range(2, 10)]
        vos.append(VisibleObject(Rect((0, 9), (10, 10)), 10))

        obs = Observation(max_id=10)
        obs.update_sensors(self.x_rect)

        '''
        Map is like following (. :actor, * :visible object)
0       |.|
10      |*|
        | |
        | |
40      |*|
        | |
60      |*|
        '''

        prepr_obs = obs.get_observation(self.x_rect, vos,
                                        preproc_mode=['collide'])

        z = none_vis_id
        x = [0, 0, 0, 0,
             z, z, 10, z,
             0, 0, 1, 0] == prepr_obs

        self.assertTrue(x.all())

    def test_feature_collide_2(self):
        vos = [VisibleObject(Rect((5, i*20), (10, 10)), i+1)
               for i in range(2, 10)]
        # colliding objects
        vos.append(VisibleObject(Rect((0, 9), (10, 10)), 10))
        vos.append(VisibleObject(Rect((9, 0), (10, 10)), 11))

        obs = Observation(max_id=11)
        obs.update_sensors(self.x_rect)

        '''
        Map is like following (. :actor, * :visible object)
0       |.|*|
9       |*| |
        | | |
        | | |
40      |*| |
        | | |
60      |*| |
        '''

        prepr_obs = obs.get_observation(self.x_rect, vos,
                                        preproc_mode=['collide'])

        z = none_vis_id
        x = [0, 0,  0, 0,
             z, 11, 10, z,
             0, 1,  1, 0] == prepr_obs

        self.assertTrue(x.all())

    def test_feature_collide_scale(self):
        vos = [VisibleObject(Rect((5, i * 20), (10, 10)), i + 1)
               for i in range(2, 10)]
        # colliding objects
        vos.append(VisibleObject(Rect((0, 9), (10, 10)), 10))
        vos.append(VisibleObject(Rect((30, 0), (10, 10)), 11))

        obs = Observation(max_id=11)
        obs.update_sensors(self.x_rect)

        '''
        Map is like following (. :actor, * :visible object)
0       |.| | |*|
9       |*| |
        | | |
        | | |
40      |*| |
        | | |
60      |*| |
        '''

        prepr_obs = obs.get_observation(self.x_rect, vos,
                                        preproc_mode=['collide', 'scale'])

        z = none_vis_id
        x = [0, 20/game_height, 0, 0,
             z, 11,            10, z,
             0, 0,              1, 0] == prepr_obs

        self.assertTrue(x.all())


if __name__ == '__main__':
    unittest.main()
