import copy

__llm_config_dict = {
    'config_name': {
        'model': 'model_name',
        'base_url': 'https://api.example.com/v1',
        'api_key': 'xxxxxxxxxxx'
    },
    'config_name2': {
        'model': 'model_name',
        'base_url': 'https://api.example.com/v1',
        'api_key': 'xxxxxxxxxxx'
    }
}

__default_llm_config = {
    'model': 'gpt-4o',
    'base_url': 'https://api.openai.com/v1',
    'api_key': 'xxxxxxxxxxx'
}

def get_llm_config_by_config_name(config_name: str=None) -> dict:
    if config_name is None:
        return copy.deepcopy(__default_llm_config)
    elif config_name in __llm_config_dict:
        return copy.deepcopy(__llm_config_dict[config_name])
    else:
        raise Exception(f"Config name '{config_name}' not found in llm_config.py")

def get_llm_config_by_model_name(model_name: str=None) -> dict:
    if model_name is None:
        return copy.deepcopy(__default_llm_config)
    else:
        for config in __llm_config_dict.values():
            if config['model'] == model_name:
                return copy.deepcopy(config)
        raise Exception(f"Model name '{model_name}' not found in llm_config.py")


