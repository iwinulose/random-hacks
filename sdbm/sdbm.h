/*
** $Id: sdbm.h 1343 2012-10-06 02:53:31Z phf $
**
** sdbm: Simple Data Base Management
**
** Copyright (c) 2006-2007 by Peter H. Froehlich <phf@acm.org>.
** All rights reserved. The file COPYING has more details.
**
** If you get this interface as part of an assignment you
** can ignore the legalese above. :-)
*/

#ifndef _SDBM_H
#define _SDBM_H

#include <stdbool.h>

/**
 * Minimum and maximum length of key and value strings,
 * including '\0' terminator.
 */
#define MIN_KEY_LENGTH 2
#define MAX_KEY_LENGTH 1024
#define MIN_VALUE_LENGTH 2
#define MAX_VALUE_LENGTH (32*1024)

/**
 * Create new database with given name. You still have
 * to sdbm_open() the database to access it. Return true
 * on success, false on failure.
 */
bool sdbm_create(const char *name);

/**
 * Open existing database with given name. Return true on
 * success, false on failure.
 */
bool sdbm_open(const char *name);

/**
 * Synchronize all changes in database (if any) to disk.
 * Useful if implementation caches intermediate results
 * in memory instead of writing them to disk directly.
 * Return true on success, false on failure.
 */
bool sdbm_sync();

/**
 * Close database, synchronizing changes (if any). Return
 * true on success, false on failure.
 */
bool sdbm_close();

/**
 * Return error code for last failed database operation.
 */
int sdbm_error();

/**
 * Is given key in database?
 */
bool sdbm_has(const char *key);

/**
 * Get value associated with given key in database.
 * Return true on success, false on failure.
 *
 * Precondition: sdbm_has(key)
 */
bool sdbm_get(const char *key, char *value);

/**
 * Update value associated with given key in database
 * to given value. Return true on success, false on
 * failure.
 *
 * Precondition: sdbm_has(key)
 */
bool sdbm_put(const char *key, const char *value);

/**
 * Insert given key and value into database as a new
 * association. Return true on success, false on
 * failure.
 *
 * Precondition: !sdbm_has(key)
 */
bool sdbm_insert(const char *key, const char *value);

/**
 * Remove given key and associated value from database.
 * Return true on success, false on failure.
 *
 * Precondition: sdbm_has(key)
 */
bool sdbm_remove(const char *key);

#endif /* _SDBM_H */
