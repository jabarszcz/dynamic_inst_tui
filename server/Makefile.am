AUTOMAKE_OPTIONS = subdir-objects

lib_LTLIBRARIES = libdynamic-inst-server.la

libdynamic_inst_server_la_SOURCES = dynamic-server.c mongoose/mongoose.c frozen/frozen.c symbol.c dynamic-symbols.c
libdynamic_inst_server_la_CPPFLAGS = -include config.h
libdynamic_inst_server_la_LIBADD = -lelf -llttng-mcount
