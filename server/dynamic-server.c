#include <pthread.h>
#include <stdbool.h>
#include <unistd.h>

#include "mongoose/mongoose.h"
#include "frozen/frozen.h"

#include "list.h"
#include "dynamic-symbols.h"

struct server_data {
	struct symtabs *symtabs;
	char *port;
};

#define EXEC_NAME_SIZE 1024
static const int CHUNKED = -1;
static const struct mg_str s_get_method = MG_MK_STR("GET");
static const struct mg_str s_put_method = MG_MK_STR("PUT");
static char *default_port = "8489";

static struct symtabs symtabs;

static int is_equal(const struct mg_str *s1, const struct mg_str *s2)
{
	return s1->len == s2->len && memcmp(s1->p, s2->p, s2->len) == 0;
}

static void handle_list(struct mg_connection *nc,
			struct http_message *hm)
{
	struct symtabs *symtabs;
	struct instrumented_func *pos;
	LIST_HEAD(ifs);
	symtabs = ((struct server_data*)nc->user_data)->symtabs;
	get_instrumented_funcs(&symtabs->symtab, &ifs);

	mg_send_head(nc, 200, CHUNKED, NULL);

	mg_printf_http_chunk(nc, "{ \"functions\": [");
	list_for_each_entry(pos, &ifs, list) {
		mg_printf_http_chunk(nc,
				     "{\"name\":\"%s\", "
				     "\"active\":%s}%s",
				     pos->sym->name,
				     pos->active ? "true" : "false",
				     list_is_last(&pos->list, &ifs) ?
				     "" : ", ");
	}
	mg_printf_http_chunk(nc, "] }\n");
	/* Send empty chunk, the end of response */
	mg_send_http_chunk(nc, "", 0);

	free_instrumented_funcs(&ifs);
}

static void handle_set(struct mg_connection *nc, struct http_message *hm)
{
	struct symtabs *symtabs;
	struct json_token t;
	int i;

	// parse JSON with frozen
	symtabs = ((struct server_data*)nc->user_data)->symtabs;
	for (i = 0;
	     json_scanf_array_elem(hm->body.p, hm->body.len,
				   ".functions", i, &t) > 0;
	     i++) {
		// for every function listed, set its status
		int active = 1;
		char *function = NULL;

		json_scanf(t.ptr, t.len, "{ name:%Q, active:%B }",
			   &function, &active);
		if (!function)
			continue;

		struct sym *s = find_symname(&symtabs->symtab, function);
		free(function);

		if (!s) {
			mg_http_send_error(nc, 400, NULL);
			return;
		}

		set_instrumentation_sym(s, active);
	}

	handle_list(nc, hm);
}

static void ev_handler(struct mg_connection *nc, int ev, void *ev_data)
{
	struct http_message *hm = (struct http_message *) ev_data;

	switch (ev) {
	case MG_EV_HTTP_REQUEST:
		if (mg_vcmp(&hm->uri, "/instrumentation") == 0) {
			if (is_equal(&hm->method, &s_get_method)) {
				handle_list(nc, hm);
			} else if (is_equal(&hm->method, &s_put_method)) {
				handle_set(nc, hm);
			} else {
				mg_http_send_error(nc, 405, NULL);
			}
		} else {
			mg_http_send_error(nc, 404, NULL);
		}
		break;
	default:
		break;
	}
}

static void *run_server(void *data) {
	struct mg_mgr mgr;
	struct mg_connection *nc;

	struct server_data *server_data = data;
	struct mg_bind_opts opts = {0};

	opts.user_data = data;

	mg_mgr_init(&mgr, NULL);

	nc = mg_bind_opt(&mgr, server_data->port, ev_handler, opts);
	if (nc == NULL) {
		fprintf(stderr, "Error starting server on port %s\n",
			server_data->port);
		exit(1);
	}

	mg_set_protocol_http_websocket(nc);

	fprintf(stderr, "Starting RESTful server on port %s\n",
		server_data->port);
	for (;;) {
		mg_mgr_poll(&mgr, 1000);
	}
	mg_mgr_free(&mgr);
}

void start_dyn_server(char *port, struct symtabs *s)
{
	pthread_t thread;
	struct server_data *data;

	data = malloc(sizeof(*data));
	data->symtabs = s;
	data->port = port;

	pthread_create(&thread, NULL, run_server, (void*)data);
}

__attribute__((constructor))
void init_dyn_server(void)
{
	char *port, *exec_name;
	int ret;

	/* Take port from environment or default */
	port = getenv("DYN_SERVER_PORT");
	if (!port)
		port = default_port;

	/* Find executable file name */
	exec_name = malloc(EXEC_NAME_SIZE);
	ret = readlink("/proc/self/exe", exec_name, EXEC_NAME_SIZE);
	if (ret < 0)
		goto err;
	exec_name[ret] = '\0';

	/* Init symtabs */
	load_symtabs(&symtabs, NULL, exec_name);

	/* Start server */
	start_dyn_server(port, &symtabs);
	return;
err:
	printf("Error while starting dynamic instrumentation server\n");
}
