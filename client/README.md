# dynamic_inst_client

## Command line interface
    python3 -m dynamic_inst_client [-h] [-p PORT] [-f FILTER]
             [{ui,list,activate,deactivate}] [functions [functions ...]]

### Commands
- no command: Same as ui
- ui : Starts the client in graphical mode.
- list : Lists the functions in the server process. You can apply a filter to this list.
- activate/deactivate: Activates/deactivates a list of functions.

### Arguments
- -h : Shows the help
- -p,--port PORT : Sets the connection port.
- -f,--filter FILTER : Uses a filter, only usable with the list command.
- functions : Functions to activate/deactivate.