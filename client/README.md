# uftrace_dynamic_client
This client is meant to be used with uftrace with the dynamic tracing enabled.

It is used to activate and deactivate trace points in a running uftrace
instance.

## Command line interface
`python3 -m uftrace_dynamic_client [-h] [-p PORT] [-f FILTER]
                   [{ui,list,activate,deactivate}] [functions [functions ...]]`

### Commands
- no command: Same as ui
- ui : Starts the client in graphical mode.
- list : Lists the functions in the uftrace'd process. You can apply a filter to this list.
- activate/deactivate: Activates/deactivates a list of functions.

### Arguments
- -h : Shows the help
- -p,--port PORT : Sets the connection port, must be the same as uftrace.
- -f,--filter FILTER : Uses a filter, only usable witht the list command.
- functions : Functions to activate/deactivate.