CC=clang
CFLAGS=-Wall -Wextra -pedantic

all: sdbm sdbm_sanity

sdbm: escape.o sdbm.o main.o

sdbm_sanity: escape.o sdbm.o sdbm_sanity.c

main.o: main.c

escape.o: escape.c

sdbm.o: sdbm.c 

clean:
	rm sdbm sdbm_sanity escape.o sdbm.o main.o
