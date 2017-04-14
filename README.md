# dynamic_inst_tui

This tool provides a user interface (in the terminal) for dynamic
instrumentation. It uses
[lttng-mcount](https://github.com/jabarszcz/lttng-mcount) to do the
actual dynamic instrumentation and adds a simple in-process rest
server (mongoose/frozen) and a TUI client to allow users to control
it.

## How to

1. Install [lttng-mcount](https://github.com/jabarszcz/lttng-mcount) and
this library.

2. Compile the program that you want to trace as explained in the [lttng-mcount README](https://github.com/jabarszcz/lttng-mcount/blob/master/README.md).

3. Start an lttng session and enable relevant events:

        lttng create my-session
        lttng enable-event -u "lttng_mcount:*"

4. Run the program with both libraries preloaded :

        LD_PRELOAD="liblttng-mcount.so libdynamic-inst-server.so" <your program>

 This starts a simple mongoose server that controls which function's
 entry/exit are being traced.

5. Connect to the server with the TUI client:

        python3 -m dynamic_inst_client [OPTIONS]

 See more details in the [client's readme](https://github.com/jabarszcz/dynamic_inst_tui/blob/master/client/README.md).

6. Enable tracing for the desired functions from the client and start
tracing.
