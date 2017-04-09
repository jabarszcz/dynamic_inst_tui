from functools import partial

import urwid as uw

from uftrace_dynamic_client.util import Filter


def make_enableable(obj):
    """
    Function that makes a urwid selectable object enableable.
    To do this, it subclasses the obj's class and defines three functions :
        selectable: Function that takes into account the enable status of the object,
        enable: To enable selection,
        disable: To disable selection
    :param obj: The object to make enableable
    :return: The modified object
    """

    class Subclass(obj.__class__):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__is_selectable = True

        def selectable(self):
            if not super().selectable():
                return False
            try:
                return self.__is_selectable
            except AttributeError:
                self.__is_selectable = True
                return True

        def enable(self):
            self.__is_selectable = True

        def disable(self):
            self.__is_selectable = False

    # Re-class the object
    obj.__class__ = Subclass
    return obj


class SelectableFunctionText(uw.Text):
    """
    Text that is selectable, works like a button but with a different appearance
    :ivar name: The name of the function
    :ivar on_select: Called when the text is selected
    """
    def __init__(self, name, activated, on_select):
        """
        :param name: The name of the text
        :param activated: Active status, influences the string
        :param on_select: Callback for selection
        """
        markup = name
        if activated:
            markup += ' (active)'
        else:
            markup += ' (nopped)'
        super().__init__(markup, align=uw.CENTER)
        self.name = name
        self.on_select = on_select

    def selectable(self):
        return True

    def keypress(self, _, key):
        if key == 'enter' or key == ' ':
            self.on_select(self.name)
            return None
        return key


class FilterFunctionWalker(uw.ListWalker):
    """
    Custom walker for the list, takes into account the function list
    :ivar __function_list: The list of functions
    :ivar __function_names: The list of function names
    :ivar __selected: The set of currently selected functions
    :ivar __on_change: The callback that is called when there is a change in the list (called by notify_change)
    """

    def __init__(self, function_list, fil=None, on_change=None):
        """
        :param function_list: The list of functions to show
        :param fil: The filter object to use
        :param on_change: The callback
        """
        self.__function_list = function_list
        if fil is None:
            self.__filter = Filter()
        else:
            self.__filter = fil
        self.__function_names = sorted([f for f in function_list])
        self.__selected = set()
        self.focus = self.__get_first_matching(0, False)
        self.__on_change = on_change

    def __getitem__(self, item):
        w = SelectableFunctionText(self.__function_names[item], self.__function_list[self.__function_names[item]],
                                   partial(FilterFunctionWalker.__on_function_select, self))
        if self.__function_names[item] in self.__selected:
            if self.__function_list[self.__function_names[item]]:
                return uw.AttrMap(w, 'function.active.selected', 'function.active.selected.focus')
            else:
                return uw.AttrMap(w, 'function.selected', 'function.selected.focus')
        else:
            if self.__function_list[self.__function_names[item]]:
                return uw.AttrMap(w, 'function.active', 'function.active.focus')
            else:
                return uw.AttrMap(w, 'function', 'function.focus')

    def next_position(self, position):
        pos = self.__get_first_matching(position + 1, False)
        if pos is None:
            raise IndexError()
        return pos

    def prev_position(self, position):
        pos = self.__get_first_matching(position - 1, True)
        if pos is None:
            raise IndexError()
        return pos

    def set_focus(self, position):
        self.focus = position
        self.notify_change()

    def notify_change(self):
        """
        Owning object must call this whenever there is a change to the filter or the function_list.
        It will notify the UI of the update.
        This function will call __on_change()
        """
        if self.focus is None:
            self.focus = self.__get_first_matching(0, False)
        else:
            current = self.focus
            self.focus = self.__get_first_matching(current, True)
            if self.focus is None:
                self.focus = self.__get_first_matching(current, False)
        self._modified()
        if self.__on_change is not None:
            self.__on_change()

    @property
    def position(self):
        """
        Read-only property that gets the current position and the number of filtered items.
        position is None and total is 0 if the list is empty.
        position starts at 1.
        :return: (position, total)
        """
        total = 0
        pos = None
        for i, f in enumerate(self.__function_names):
            if self.__filter(f, self.__function_list[f], f in self.__selected):
                total += 1
                if i == self.focus:
                    pos = total
        return pos, total

    @property
    def selected(self):
        """
        Read-only property that gets the current selection
        :return: The current selection
        """
        return self.__selected

    def __get_first_matching(self, start_position, reverse):
        """
        Gets the first position that matches the filter
        :param start_position: The position to start from
        :param reverse: False to look forward, True to look backward
        :return: The next position, None if none found
        """
        if reverse:
            iterable = reversed(range(start_position + 1))
        else:
            iterable = range(start_position, len(self.__function_names))
        for i in iterable:
            if self.__filter(self.__function_names[i],
                             self.__function_list[self.__function_names[i]],
                             self.__function_names[i] in self.__selected):
                return i
        return None

    def __on_function_select(self, name):
        """
        Callback called by the SelectableFunctionText when selected
        :param name: The name of the function
        """
        if name in self.__selected:
            self.__selected.remove(name)
        else:
            self.__selected.add(name)
        self.notify_change()

    def select_all(self):
        """
        Selects all filtered items
        """
        for f in self.__function_list:
            if self.__filter(f, self.__function_list[f], False):
                self.__selected.add(f)
        self.notify_change()

    def clear_selection(self):
        """
        Deselects all filtered items
        """
        for f in self.__function_list:
            if self.__filter(f, self.__function_list[f], True):
                try:
                    self.__selected.remove(f)
                except KeyError:
                    pass
        self.notify_change()


class FilterEdit(uw.Edit):
    """
    Edit for the filter, simply calls the done_callback when pressing enter or esc
    :ivar __done_callback: The callback to call on enter or esc
    """
    def __init__(self, done_callback, *args, **kwargs):
        """
        :param done_callback: The callback to call on enter or esc
        :param args: The args to pass to urwid.Edit.__init__
        :param kwargs: The kwargs to pass urwid.Edit.__init__
        """
        super().__init__(*args, **kwargs)
        self.__done_callback = done_callback

    def keypress(self, size, key):
        if key == 'enter':
            self.__done_callback()
            return None
        elif key == 'esc':
            self.set_edit_text('')
            self.__done_callback()
            return None
        return super().keypress(size, key)


class Ui:
    """
    Ui class, runs the UI loop
    """
    PALETTE = [
        ('function', 'white', 'black'),
        ('function.focus', 'light green', 'black'),
        ('function.selected', 'white', 'dark blue'),
        ('function.selected.focus', 'light green', 'light blue'),
        ('function.active', 'white,bold', 'black'),
        ('function.active.focus', 'light green,bold', 'black'),
        ('function.active.selected', 'white,bold', 'dark blue'),
        ('function.active.selected.focus', 'light green,bold', 'light blue'),
        ('edit.normal', 'white', 'black'),
        ('edit.error', 'white', 'dark red')
    ]

    HELP_TEXT = "'f' or '/'\n" \
                "  to search, format is\n" \
                "    [op1]:[op2]:[regex]\n" \
                "    The options are\n" \
                "      [active:nopped] for the status of the functions\n" \
                "      [selected:unselected] for the current selection\n" \
                "    press enter to apply filter\n" \
                "    press esc to clear filter\n\n" \
                "'s'\n" \
                "  to select all filtered\n\n" \
                "'c'\n" \
                "  to clear all filtered selection\n\n" \
                "'a/d'\n" \
                "  to activate/deactivate the selected functions\n\n" \
                "'r'\n" \
                "  to refresh the function list\n\n" \
                "'q'/'Ctrl+c'\n" \
                "  to quit"

    def __init__(self, communicator):
        self.comm = communicator

        self.filter = Filter()
        self.func_list_walker = FilterFunctionWalker(self.comm.function_list,
                                                     self.filter,
                                                     partial(Ui.__handle_list_change, self))
        self.ui_func_list = make_enableable(uw.ListBox(self.func_list_walker))
        self.ui_func_list_box = uw.LineBox(self.ui_func_list)
        self.ui_filter_edit = uw.AttrMap(
            make_enableable(FilterEdit(partial(Ui.__edit_is_done, self))), 'edit.normal')
        self.func_list_walker.notify_change()
        self.ui_filter_edit_box = uw.AttrMap(uw.LineBox(uw.Filler(self.ui_filter_edit)), 'edit.normal')
        self.ui_filter_edit.base_widget.disable()

        self.ui_help = uw.LineBox(uw.Filler(uw.Text(Ui.HELP_TEXT)))

        self.cols = uw.Columns([('weight', 60, self.ui_func_list_box), ('weight', 40, self.ui_help)])
        self.top = uw.Pile([self.cols, (3, self.ui_filter_edit_box)])

        self.loop = uw.MainLoop(self.top,
                                palette=Ui.PALETTE,
                                unhandled_input=partial(Ui.__handle_keyboard, self))

    def run(self):
        self.loop.run()

    def __edit_is_done(self):
        try:
            self.filter.filter = self.ui_filter_edit.base_widget.get_edit_text()
            self.func_list_walker.notify_change()
            self.ui_func_list.enable()
            self.ui_filter_edit.base_widget.disable()
            self.top.set_focus(0)
            self.ui_filter_edit_box.set_attr_map({None: 'edit.normal'})
        except ValueError:
            self.ui_filter_edit_box.set_attr_map({None: 'edit.error'})

    def __handle_keyboard(self, key):
        if key == 'q':
            raise uw.ExitMainLoop()
        elif key == 'f' or key == '/':
            self.ui_func_list.disable()
            self.ui_filter_edit.base_widget.enable()
            self.top.set_focus(1)
        elif key == 's':
            self.func_list_walker.select_all()
        elif key == 'c':
            self.func_list_walker.clear_selection()
        elif key == 'a':
            funcs = {f: True for f in self.func_list_walker.selected if self.filter(f)}
            self.comm.function_list = funcs
            self.func_list_walker.notify_change()
        elif key == 'd':
            funcs = {f: False for f in self.func_list_walker.selected if self.filter(f)}
            self.comm.function_list = funcs
            self.func_list_walker.notify_change()
        elif key == 'r':
            self.comm.refresh()
            self.func_list_walker.notify_change()

    def __handle_list_change(self):
        pos, total = self.func_list_walker.position
        if pos is None:
            pos = 0
        self.ui_func_list_box.set_title('Item %s of %s' % (pos, total))
