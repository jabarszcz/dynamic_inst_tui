
import requests
import json


class CommunicatorException(Exception):
    """
    Exception thrown by the Communicator
    """
    pass


class Communicator:
    """
    Objects that communicates with the uftrace'd process
    :ivar __session: The HTTP session, None if not connected
    :ivar __url: The HTTP url, None if not connected
    :ivar __cache: The function list cache, used so that there is not a request each time we read the function list
    :cvar function_list: Function list property that modifies __cache
    """
    URL_TEMPLATE = 'http://127.0.0.1:%d/instrumentation'

    def __init__(self):
        self.__session = None
        self.__url = None
        self.__cache = {}

    def connect(self, port):
        """
        Connects to the uftrace'd process
        :param port: The port
        :raise ValueError: When the port is invalid
        """
        self.disconnect()
        if not isinstance(port, int) or port < 0 or port > 65535:
            raise ValueError('Port must be an int between 0 and 65535')
        self.__session = requests.Session()
        self.__url = Communicator.URL_TEMPLATE % port
        self.__request_get_function_list()

    def disconnect(self):
        """
        Disconnects from the uftrace'd process
        """
        if self.__session is not None:
            self.__session.close()
            self.__url = None
            self.__cache = {}

    def refresh(self):
        """
        Manually refreshes the function list from the server
        """
        self.__request_get_function_list()

    def __get_function_status(self):
        """
        Function list getter
        :return: The function list
        """
        self.__check_connected()
        return self.__cache

    def __set_function_status(self, funcs):
        """
        Function list setter
        :param funcs: The dictionary of functions to modify
        :raise CommunicatorException: If one of the function in the list is not in the uftrace'd process
        """
        self.__check_connected()
        for f in funcs:
            if f in self.__cache:
                self.__cache[f] = funcs[f]
            else:
                raise CommunicatorException('Function not in the process')
        self.__request_put_function_list()

    function_list = property(__get_function_status, __set_function_status)

    def status(self):
        """
        Gets the status of the server
        :return: True if connected
        """
        return self.__session is not None

    def __request_get_function_list(self):
        """
        Does a HTTP GET to update the file list
        """
        try:
            r = self.__session.get(self.__url)
            r.raise_for_status()
        except Exception as e:
            raise CommunicatorException(e.args) from e
        self.__write_to_cache(r.json())

    def __request_put_function_list(self):
        """
        Does a HTTP PUT to set the function status in the uftrace'd process, updates the function list at the same time
        """
        self.__check_connected()
        try:
            r = self.__session.put(self.__url, data=self.__read_from_cache())
            r.raise_for_status()
        except Exception as e:
            raise CommunicatorException(e.args) from e
        self.__write_to_cache(r.json())

    def __write_to_cache(self, response):
        """
        Writes the HTTP response body to the function list
        :param response: HTTP response body
        """
        for f in response['functions']:
            self.__cache[f['name']] = f['active']

    def __read_from_cache(self):
        """
        Creates a HTTP request body from the function list
        :return:
        """
        data = []
        for f in self.__cache:
            data += [{'name': f, 'active': self.__cache[f]}]
        data = {'functions': data}
        return json.dumps(data)

    def __check_connected(self):
        """
        Checks if the communicator is connected
        :raise CommunicatorException: The communicator is not connected
        """
        if not self.status():
            raise CommunicatorException('Not connected')