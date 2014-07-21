#include <stdio.h>
#include "sdbm.h"

int main(void) {
	sdbm_create("helloworld");
	sdbm_open("helloworld");
	sdbm_insert("doge", "googogo");
	char buf[1024];
	sdbm_get("lalalal", buf);
	puts(buf);
	sdbm_close();
	return 0;
}

