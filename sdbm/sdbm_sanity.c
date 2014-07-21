/*
** $Id: sdbm_sanity.c 1501 2013-03-05 01:50:01Z phf $
**
** sdbm: Simple Data Base Management
**
** Basic sanity test. When run for the first time, this
** program creates a new database, inserts a few items,
** and quits. When run for a second time it opens the
** database again, checks if the items are still there,
** and makes a few changes. It'll keep doing this until
** you delete the database again to start fresh.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sdbm.h"

#define SANITY_NAME "sanity"

static char *keys[] = {
    "one",
    "two",
    "three",
    "fourolololololololdasdfdololololololfourololol234234ololol23olol\n\nfjfjfjf\nasdfj\rasjdfkj\tsfasdffour"
};

static char *vals[] = {
    "Eins",
    "Zwei",
    "Drei",
    "Vier\v\nsdfjf\xffsfh"
};

#define LENGTH(x) ((int)(sizeof(x)/sizeof(*x)))

void fatal(const char *msg)
{
    fprintf(stderr, "sanity_test: %s (error code %d)\n", msg, sdbm_error());
    exit(EXIT_FAILURE);
}

void fill_database()
{

    if (!sdbm_open(SANITY_NAME)) {
        fatal("failed to open initial database");
    }

    for (int i = 0; i < LENGTH(keys); i++) {
        if (!sdbm_insert(keys[i], vals[i])) {
            fatal("failed to insert into initial database");
        }
    }

    if (!sdbm_close()) {
        fatal("failed to close initial database");
    }
}

void check_database()
{
    char value[MAX_VALUE_LENGTH];

    puts("checking database");

    for (int i = 0; i < LENGTH(keys); i++) {
        if (!sdbm_has(keys[i])) {
            fatal("failed to find expected key");
        }
        if (!sdbm_get(keys[i], value)) {
            fatal("failed to get value for expected key");
        }
        if (strcmp(value, vals[i]) != 0) {
            fatal("failed to get expected value for expected key");
        }
    }
}

void replace_random()
{
    bool k = rand() % LENGTH(keys);

    puts("replace random record");

    if (!sdbm_remove(keys[k])) {
        fatal("failed to remove expected key");
    }
    if (sdbm_has(keys[k])) {
        fatal("failed to *actually* remove expected key");
    }
    if (!sdbm_insert(keys[k], vals[k])) {
        fatal("failed to re-insert expected key");
    }
    if (!sdbm_has(keys[k])) {
        fatal("failed to *actually* re-insert expected key");
    }
}

void update_random()
{
    bool k = rand() % LENGTH(keys);
    char value[MAX_VALUE_LENGTH];
    const char *new = "no longer here :-/";

    puts("update random record");

    if (!sdbm_put(keys[k], new)) {
        fatal("failed to update expected key");
    }
    if (!sdbm_get(keys[k], value)) {
        fatal("failed to get value for expected key");
    }
    if (strcmp(value, new) != 0) {
        puts(value);
        puts(new);
        fatal("failed to get expected value for expected key");
    }

    if (!sdbm_put(keys[k], vals[k])) {
        fatal("failed to update expected key");
    }
    if (!sdbm_get(keys[k], value)) {
        fatal("failed to get value for expected key");
    }
    if (strcmp(value, vals[k]) != 0) {
        fatal("failed to get expected value for expected key");
    }
}

void evolve_database()
{
    puts("evolving database");
    replace_random();
    update_random();
}

int main(void)
{
    bool first_time = !sdbm_open(SANITY_NAME);

    if (first_time) {
        puts("running for the first time");
        if (!sdbm_create(SANITY_NAME)) {
            fatal("failed to create initial database");
        }
        fill_database();
    } else {
        puts("running for the second (or third, or fourth, ...) time");
        check_database();
        evolve_database();
        if (!sdbm_close()) {
            fatal("failed to close database");
        }
    }

    puts("sanity test complete (but that doesn't mean you'll get full points)");
    exit(EXIT_SUCCESS);
}
