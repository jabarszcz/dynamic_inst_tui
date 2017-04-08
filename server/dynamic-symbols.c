#include <stddef.h>
#include <malloc.h>
#include <lttng-mcount/dynamic.h>

#include "dynamic-symbols.h"

int set_instrumentation_sym(struct sym *sym, int enable)
{
	return set_instrumentation(sym->addr, enable);
}

void free_instrumented_funcs(struct list_head *list)
{
	struct instrumented_func *pos, *tmp;
	list_for_each_entry_safe(pos, tmp, list, list) {
		list_del(&pos->list);
		free(pos);
	}
}
struct list_head *get_instrumented_funcs(struct symtab *symtab,
					 struct list_head *ifs)
{
	int ret;
	unsigned i;
	struct sym *sym;
	enum lttng_mcount_patch status;
	struct instrumented_func *new = NULL;

	for (i = 0; i < symtab->nr_sym; i++) {
		sym = &symtab->sym[i];

		ret = get_instrumentation(sym->addr, &status);
		if (ret || status == NO_PATCH)
			continue;

		new = malloc(sizeof(*new));
		INIT_LIST_HEAD(&new->list);
		new->active = (int) status;
		new->sym = sym;

		list_add_tail(&new->list, ifs);
	}
	
	return ifs;
}
