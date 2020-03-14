import base64
import datetime
import importlib
from abc import ABC, abstractmethod


class Persistence(ABC):

    FOLDER_NAME_MAIN = 'apps/cryptotrader-com'
    FOLDER_NAME_USERS = 'users'
    FOLDER_NAME_ITERATION = 'iterations'
    FOLDER_NAME_SETUPS = 'setups'
    FOLDER_NAME_STRATEGY_STATE = 'strategy-state'

    def __init__(self, path, name):
        self.path = path
        self.name = name

    def duplicate_setup(self, new_name):
        current_setup = self.get_setup()
        # If the target setup is already there - delete it to make the duplication overwriting old data
        self.delete_setup_impl(self.path, new_name)
        self.save_setup_impl(self.path, new_name, current_setup)

    def save_setup(self, setup):
        self.save_setup_impl(self.path, self.name, setup)

    def get_setup(self):
        return self.get_setup_impl(self.path, self.name)

    # TODO: Should read: Delete setup children.
    def delete_setup(self):
        return self.delete_setup_impl(self.path, self.name)

    def end_setup(self):
        self.update_setup_impl(self.path, self.name, {'event_stop': True})

    def update_setup(self, setup2change):
        self.update_setup_impl(self.path, self.name, setup2change)

    def get_exchange_config_path(self):
        return f'{self.get_config_path()}/exchange.json'

    def get_config_path(self):
        return f'{self.retrieve_user_path()}/configs'

    def retrieve_user_path(self):
        users_folder_index = self.path.rindex(Persistence.FOLDER_NAME_USERS)
        users_folder_name_length = len(Persistence.FOLDER_NAME_USERS)
        search_slash_from = users_folder_index + users_folder_name_length + 1
        user_path = self.path[:self.path.index('/', search_slash_from)]
        return user_path

    def get_exchange_config(self):
        return self.get_exchange_config_impl(self.get_exchange_config_path())

    def get_custom_result(self, parameter):
        get_class_instance = type(parameter) is dict and parameter.get("class_instance") is not None
        get_function_result = type(parameter) is dict and parameter.get("static_function_result") is not None
        if get_class_instance:
            instance = self.get_class_instance_from_dict(parameter.get("class_instance"))
            return instance
        elif get_function_result:
            function_result = self.get_static_function_result_from_dict(parameter.get("static_function_result"))
            return function_result
        else:
            return parameter

    def get_parameters(self, parameters):
        if parameters is None:
            return None
        new_parameters = {}
        for parameter in parameters:
            value = self.get_custom_result(parameters.get(parameter))
            new_parameters[parameter] = value
        return new_parameters

    def get_class_instance_from_dict(self, d):
        module_name = d.get("module_name")
        module = importlib.import_module(module_name)
        class_name = d.get("name")
        parameters = self.get_parameters(d.get("parameters"))
        instance = getattr(module, class_name)() if parameters is None else getattr(module, class_name)(**parameters)
        return instance

    def get_static_function_result_from_dict(self, d):
        module_name = d.get("module_name")
        module = importlib.import_module(module_name)
        class_name = d.get("class_name")
        clazz = getattr(module, class_name)
        function_name = d.get("function_name")
        parameters = self.get_parameters(d.get("parameters"))
        instance = getattr(clazz, function_name)() if parameters is None else getattr(clazz, function_name)(**parameters)
        return instance

    def get_act_instance_from_setup(self):
        retrieved_setup = self.get_setup()
        return self.get_custom_result(retrieved_setup.get("act"))

    @staticmethod
    def get_users_path(user):
        return f'{Persistence.FOLDER_NAME_MAIN}/{Persistence.FOLDER_NAME_USERS}/{user}'

    @staticmethod
    def get_week_path(user):
        today = datetime.datetime.today()
        return f"" \
            f"{Persistence.get_users_path(user)}/" \
            f"{Persistence.FOLDER_NAME_ITERATION}/{today.year}/{today.month}/{today.isocalendar()[1]}"

    @staticmethod
    def get_path(user, exchange, pair):
        week_path = Persistence.get_week_path(user)
        exchange = exchange.lower()
        pair = pair.replace('/', '').lower()
        path = f'{week_path}/{Persistence.FOLDER_NAME_SETUPS}/{exchange}/{pair}'
        return path

    @staticmethod
    def get_path_and_name_from_data(data):
        full_path = base64.b64decode(data['data']).decode('utf-8')
        start_index = full_path.rindex(Persistence.FOLDER_NAME_MAIN)
        last_slash_index = full_path.rindex('/')
        path = full_path[start_index:last_slash_index]
        name = full_path[last_slash_index+1:]
        return path, name

    @abstractmethod
    def get_setup_impl(self, path, name):
        pass

    @abstractmethod
    def save_setup_impl(self, path, name, setup):
        pass

    @abstractmethod
    def delete_setup_impl(self, path, name):
        pass

    @abstractmethod
    def update_setup_impl(self, path, name, setup):
        pass

    @abstractmethod
    def get_exchange_config_impl(self, path):
        pass

################################################################################################

    def save_strategy_state(self, new_candle_state_content, iteration_index):
        self.save_strategy_state_impl(new_candle_state_content, iteration_index)

    def get_last_strategy_state(self):
        return self.get_last_strategy_state_impl()

    @abstractmethod
    def save_strategy_state_impl(self, new_candle_state_content, prev_candle_state):
        pass

    @abstractmethod
    def get_last_strategy_state_impl(self):
        pass

