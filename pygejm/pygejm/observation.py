import numpy as np
from pygejm.constants import game_height, game_width, none_vis_id
from sklearn.preprocessing import LabelBinarizer
from pygame import Rect
import pandas as pd


def x_distance_function(vis_obj_rect, actor_rect):
    if vis_obj_rect.colliderect(actor_rect):
        return -1
    return min(abs(vis_obj_rect.left - actor_rect.left),
               abs(vis_obj_rect.right - actor_rect.left),
               abs(vis_obj_rect.left - actor_rect.right),
               abs(vis_obj_rect.right - actor_rect.right))


def y_distance_function(vis_obj_rect, actor_rect):
    if vis_obj_rect.colliderect(actor_rect):
        return -1
    return min(abs(vis_obj_rect.top - actor_rect.top),
               abs(vis_obj_rect.bottom - actor_rect.top),
               abs(vis_obj_rect.top - actor_rect.bottom),
               abs(vis_obj_rect.bottom - actor_rect.bottom))


class Sensor:
    def __init__(self, actor_rect, rect, distance_function):
        self._distance = distance_function
        self.actor_rect = actor_rect
        self.sensor_rect = rect
        self.objs = []

    def add_objects_if_visible(self, vis_objs):
        collides = self.sensor_rect.collidelistall(vis_objs)
        self.objs += [vis_objs[idx] for idx in collides]
        return len(collides)

    def _get_nearest(self, n):
        objs_cp = np.array(self.objs.copy())
        distances = np.array([self.distance(o.rect) for o in objs_cp])
        sorted_idx = np.argsort(distances)
        distances_sorted = distances[sorted_idx]
        ids_sorted = [o.id for o in objs_cp[sorted_idx]]

        # change tuple to list
        return list(map(list, zip(distances_sorted[:n], ids_sorted[:n])))

    def get_nearest(self, n=1):
        distances_with_ids = self._get_nearest(n)
        if n == 1 and len(distances_with_ids) > 0:
            return distances_with_ids[0]
        else:
            return distances_with_ids

    def distance(self, r1):
        r2 = self.actor_rect

        if self._distance == 'x':
            return x_distance_function(r1, r2)
        elif self._distance == 'y':
            return y_distance_function(r1, r2)
        else:
            raise AttributeError('Bad distance_function: %r' % self._distance
                                 + '\nShould be either x or y')


class CommonSensors:
    @staticmethod
    def up(rect):
        return Sensor(rect, Rect((rect.x, 0), (rect.w, rect.y)), 'y')

    @staticmethod
    def right(rect):
        return Sensor(rect, Rect((rect.right, rect.top),
                                 (game_width - rect.right, rect.h)), 'x')

    @staticmethod
    def down(rect):
        return Sensor(rect, Rect((rect.x, rect.bottom),
                                 (rect.w, game_height - rect.bottom)), 'y')

    @staticmethod
    def left(rect):
        return Sensor(rect, Rect((0, rect.top), (rect.x, rect.h)), 'x')


class Observation:
    def __init__(self, max_id=3):
        self.object_ids = list(range(max_id+1))
        self.sensors = {}
        self.ohe = LabelBinarizer().fit(self.object_ids)
        self._n_sensors = 0

    def update_sensors(self, actor):
        actor_idx = id(actor)
        actor_rect = actor.rect

        sensors = [
            CommonSensors.up(actor_rect),
            CommonSensors.right(actor_rect),
            CommonSensors.down(actor_rect),
            CommonSensors.left(actor_rect)
        ]

        self._n_sensors = len(sensors)
        self.sensors[actor_idx] = sensors

    def __ohe(self, obs, categ_fts):
        obs = np.array(obs)

        to_binarize = obs[categ_fts].copy()
        obs = np.delete([obs], categ_fts, axis=1)

        to_binarize = self.ohe.transform(to_binarize).reshape(1, -1)
        obs = np.insert(obs, [0], to_binarize, axis=1)

        return obs

    def _get_dist_id_or_default(self, nearest):
        return nearest if len(nearest) > 0 else [0, none_vis_id]

    def get_observation(self, actor, vos,
                        preproc_mode=('lb', 'scale'), n_nearest=1):

        columns = []
        colliding_columns = ['collides_%d' % d for d in range(self._n_sensors)]

        distance_cols = ['s_%d' % d for d in range(self._n_sensors)]
        id_cols = ['sid_%d' % d for d in range(self._n_sensors)]

        columns += distance_cols
        columns += id_cols

        add_colliding_ft = 'collide' in preproc_mode
        if add_colliding_ft:
            columns += colliding_columns

        data = pd.DataFrame(columns=columns)

        for idx, sensor in enumerate(self.sensors[id(actor)]):
            dist_col = distance_cols[idx]
            id_col = id_cols[idx]

            sensor.add_objects_if_visible(vos)

            result = self._get_dist_id_or_default(sensor.get_nearest(n_nearest))

            data[dist_col] = pd.Series(max(0, result[0]))
            data[id_col] = pd.Series(result[1])

            if add_colliding_ft:
                data[colliding_columns[idx]] =\
                    1 if (result[0] == -1 and result[1] != none_vis_id) else 0

        self._scale(data, distance_cols, preproc_mode)

        return np.array(data.values).flatten()

    def _scale(self, df, distance_cols, preproc_mode):
        if 'scale' in preproc_mode or 'scalev' in preproc_mode:
            for c in distance_cols:
                df[c] /= game_height

    def _binarize(self, nearest, preproc_mode):
        if 'lb' in preproc_mode or 'lbv' in preproc_mode:
            nearest = np.array(nearest).reshape((1, -1))[0]

            if 'lbv' in preproc_mode:
                print('Nearest shape before lb: %s' % str(nearest.shape))
                print(nearest)

            nearest = self.__ohe(nearest, list(range(1, len(nearest), 3)))[0]

            if 'lbv' in preproc_mode:
                print('Nearest after lb: %s' % str(nearest.shape))
                print(nearest)

        return nearest
