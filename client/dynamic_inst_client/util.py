
import re


class Filter:
    """
    Function filter, used to filter function based on status, selection and name.
    :ivar __status_filter: None for no filter, 'active' for active functions, 'nopped' for nopped functions
    :ivar __selected filter: None for no filter, 'selected' for selected functions,
        'unselected' for un-selected functions
    :ivar __regex: The regex for the function name, empty or None for no filter
    :cvar filter: The filter property, uses the __set_filter function to modify the filter
    The filter's format is:
        [op1]:[op2]:[regex]
        Where op1 and op2 can be:
            active/nopped: To filter based on the function's status
            selected/unselected: To filter based on the current selection
        The regex must follow the Python's regex rules.
        All the parameters are optional, an empty filters accepts all, the op's must be followed by the ':' character
        Examples:
            active:-> Filters currently active functions
            active:do_.*-> Filters currently active functions witht the name that respects 'do_.*'
            nopped:selected:-> Filters currently nopped functions that are selected
            nopped:unselected:main-> Filters currently nopped functions that are not selected and that start with 'main'
    """
    def __init__(self, regex=None):
        """
        :param regex: The filter to apply.
        """
        self.__status_filter = None
        self.__selected_filter = None
        self.__regex = None
        if regex is not None:
            self.filter = regex

    def __set_filter(self, regex):
        """
        Filter setter, sets the filters parameters. Used by the 'filter' property
        :param regex: The filter to use
        :raise ValueError: If the filter is invalid
        """
        if regex is None:
            self.__status_filter = None
            self.__regex = None
            return

        split = regex.split(':')
        regex = split[-1]
        split = split[:-1]

        self.__status_filter = None
        self.__selected_filter = None
        for s in split:
            if s == 'active':
                if self.__status_filter is not None:
                    raise ValueError()
                self.__status_filter = 'active'
            elif s == 'nopped':
                if self.__status_filter is not None:
                    raise ValueError()
                self.__status_filter = 'nopped'
            elif s == 'selected':
                if self.__selected_filter is not None:
                    raise ValueError()
                self.__selected_filter = 'selected'
            elif s == 'unselected':
                if self.__selected_filter is not None:
                    raise ValueError()
                self.__selected_filter = 'unselected'
            else:
                raise ValueError()
        try:
            self.__regex = re.compile(regex)
        except re.error:
            raise ValueError()

    filter = property(fset=__set_filter)

    def __call__(self, func, active=None, selected=None):
        """
        Applies the filter to a function
        :param func: The name of the function
        :param active: If the function is active, None if you don't care
        :param selected: If the function is selected, None if you don't care
        :return: True if the function respects the filter
        """
        if active is not None:
            if self.__status_filter == 'active' and not active:
                return False
            if self.__status_filter == 'nopped' and active:
                return False
        if selected is not None:
            if self.__selected_filter == 'selected' and not selected:
                return False
            if self.__selected_filter == 'unselected' and selected:
                return False
        if self.__regex is not None:
            return self.__regex.match(func) is not None
        return True
