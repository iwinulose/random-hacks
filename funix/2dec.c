#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
	if (argc < 2) {
		fprintf(stderr, "No argument\n");
		return 1;
	}
	long long in = strtoll(argv[1], NULL, 0);
	printf("%lld\n", in);
	return 0;
}

