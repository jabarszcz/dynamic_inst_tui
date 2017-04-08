#ifndef _DYNAMIC_SYMBOLS_H_
#define _DYNAMIC_SYMBOLS_H_

#include "symbol.h"
#include "list.h"

struct instrumented_func {
	struct list_head list;
	int active;
	struct sym *sym;
};

int set_instrumentation_sym(struct sym *sym, int enable);
void free_instrumented_funcs(struct list_head *list);
struct list_head *get_instrumented_funcs(struct symtab *symtab, struct list_head *ifs);

#endif // _DYNAMIC_SYMBOLS_H_
