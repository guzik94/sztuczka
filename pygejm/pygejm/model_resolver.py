class ModelResolver:
    @staticmethod
    def resolve(model_identifier, **kwargs):
        if model_identifier is None: return None
        if isinstance(model_identifier, str):
            if model_identifier == 'seqnn':
                from pygejm.ann_model import Model
                load_path = kwargs.get('load_path', '')
                return Model({}, load_path)
            elif model_identifier == 'actor_critic':
                from pygejm.actors.models.actor_critic import ActorCritic
                return ActorCritic()

