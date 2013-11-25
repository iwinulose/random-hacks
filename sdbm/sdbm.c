#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <unistd.h>

#include "sdbm.h"
#include "escape.h"


#define ESCAPED_KEY_BUF_LEN ((MAX_KEY_LENGTH - 1) * ESCAPE_SEQ_LEN + 1)

typedef enum db_error {
	DB_NO_ERR,
	DB_PARAM_ERR,
	DB_EXISTS,
	DB_NEXISTS,
	DB_INVALID,
	DB_OPEN,
	DB_NOT_OPEN,
	DB_IO_ERR,
	DB_NOMEM,
	DB_KEY_EXISTS,
	DB_KEY_NEXISTS,
	DB_UNKNOWN_ERR,
} db_error_e;

static const char *_error_strings[] = {
	[DB_NO_ERR] 		= "No error.",
	[DB_PARAM_ERR] 		= "Bad parameter.",
	[DB_EXISTS]			= "Database of the given name already exists",
	[DB_NEXISTS]		= "Database of the given name doesnt exist",
	[DB_INVALID]		= "Database is invalid.",
	[DB_OPEN] 			= "Database already open.",
	[DB_NOT_OPEN] 		= "Database not open.",
	[DB_IO_ERR] 		= "IO error.",
	[DB_KEY_EXISTS]		= "Key exists in database.",
	[DB_KEY_NEXISTS]	= "Key doesn't exist in database.",
	[DB_UNKNOWN_ERR] 	= "Unknown error.",
};

static const char *_current_db = NULL;
static db_error_e _last_err = DB_NO_ERR;
static char _escaped_key_buf[ESCAPED_KEY_BUF_LEN];

static bool _is_db_open(void) {
	return _current_db != NULL;
}

static char *_make_path_for_key(const char *key) {
	char *path = NULL;
	escape_string(_escaped_key_buf, key, ESCAPED_KEY_BUF_LEN);
	asprintf(&path, "%s/%s", _current_db, _escaped_key_buf);
	return path;
}

static void _set_err(db_error_e err) {
	_last_err = err;
}

#define DB_GUARD_EXPAND(expect, err_state) \
if (_is_db_open() != (expect)) { \
	_set_err((err_state)); \
	return false; \
} (void) 0

#define DB_OPEN_GUARD() DB_GUARD_EXPAND(true, DB_NOT_OPEN)
#define DB_CLOSED_GUARD() DB_GUARD_EXPAND(false, DB_OPEN)


/**
 * Create new database with given name. You still have
 * to sdbm_open() the database to access it. Return true
 * on success, false on failure.
 */
bool sdbm_create(const char *name) {
	if (!name) {
		_set_err(DB_PARAM_ERR);
		return false;
	}
	bool ret = false;
	char *escaped_name = escape_string_dynamic(name);
	struct stat st;
	if (!escaped_name) {
		_set_err(DB_PARAM_ERR);
	}
	else if (stat(escaped_name, &st) != -1) {
		_set_err(DB_EXISTS);
	}
	else if (mkdir(escaped_name, 0755) != 0) {
		_set_err(DB_IO_ERR);
	}
	else {
		ret = true;
	}
	if (escaped_name) { free(escaped_name); };
	return ret;
}

/**
 * Open existing database with given name. Return true on
 * success, false on failure.
 */
 
bool sdbm_open(const char *name) {
	if (!name) {
		_set_err(DB_PARAM_ERR);
		return false;
	}
	DB_CLOSED_GUARD();
	bool ret = false;
	char *escaped_name = escape_string_dynamic(name);
	struct stat st;
	if(!escaped_name) {
		_set_err(DB_PARAM_ERR);
	}
	else if(stat(escaped_name, &st) == -1) {
		_set_err(DB_NEXISTS);
	}
	else if (!S_ISDIR(st.st_mode)) {
		_set_err(DB_INVALID);
	}
	else {
		ret = true;
	}
	if (ret) {
		_current_db = realpath(escaped_name, NULL);;
	}
	if (escaped_name) { free(escaped_name); }
	return ret;
}

/**
 * Synchronize all changes in database (if any) to disk.
 * Useful if implementation caches intermediate results
 * in memory instead of writing them to disk directly.
 * Return true on success, false on failure.
 */
bool sdbm_sync(void) {
	DB_OPEN_GUARD();
	return true;
}

/**
 * Close database, synchronizing changes (if any). Return
 * true on success, false on failure.
 */
bool sdbm_close(void) {
	DB_OPEN_GUARD();
	free((void*)_current_db);
	_current_db = NULL;
	return true;
}

/**
 * Return error code for last failed database operation.
 */
int sdbm_error(void) {
	return _last_err;
}


static bool _file_exists(const char *path) {
	return access(path, F_OK) == 0;
}

/**
 * Is given key in database?
 */
bool sdbm_has(const char *key) {
	DB_OPEN_GUARD();
	if (!key) {
		_set_err(DB_PARAM_ERR);
		return false;
	}
	bool ret = false;
	char *path = _make_path_for_key(key);
	if (!path) {
		_set_err(DB_NOMEM);
		return false;
	}
	ret = _file_exists(path);
	free(path);
	return ret;
}

/**
 * Get value associated with given key in database.
 * Return true on success, false on failure.
 *
 * Precondition: sdbm_has(key)
 */
bool sdbm_get(const char *key, char *value) {
	DB_OPEN_GUARD();
	if (!key || !value) {
		_set_err(DB_PARAM_ERR);
		return false;
	}
	char *path = _make_path_for_key(key);
	if (!path) {
		_set_err(DB_NOMEM);
		return false;
	}
	FILE *fp = fopen(path, "r");
	free(path);
	if (!fp) {
		_set_err(DB_IO_ERR);
		return false;
	}
	fread(value, 1, MAX_VALUE_LENGTH, fp);
	bool ret = true;
	if (ferror(fp)) {
		ret = false;
		_set_err(DB_IO_ERR);
	}
	fclose(fp);
	return ret;
}

static bool _update_db(const char *key, const char *value, bool should_exist) {
	if (!key || !value) {
		_set_err(DB_PARAM_ERR);
		return false;
	}
	char *path = _make_path_for_key(key);
	if (!path) {
		_set_err(DB_NOMEM);
		return false;
	}
	bool exists = _file_exists(path);
	if (exists != should_exist) {
		free(path);
		_set_err(exists ? DB_KEY_EXISTS : DB_KEY_NEXISTS);
		return false;
	}
	FILE *fp = fopen(path, "w");
	free(path);
	if (!fp) {
		_set_err(DB_IO_ERR);
		return false;
	}
	size_t count = fwrite(value, strlen(value) + 1, 1, fp);
	fclose(fp);
	if (count != 1) {
		_set_err(DB_IO_ERR);
		return false;
	}
	return true;
}

/**
 * Update value associated with given key in database
 * to given value. Return true on success, false on
 * failure.
 *
 * Precondition: sdbm_has(key)
 */
bool sdbm_put(const char *key, const char *value) {
	DB_OPEN_GUARD();
	return _update_db(key, value, true);
}

/**
 * Insert given key and value into database as a new
 * association. Return true on success, false on
 * failure.
 *
 * Precondition: !sdbm_has(key)
 */
bool sdbm_insert(const char *key, const char *value) {
	DB_OPEN_GUARD();
	return _update_db(key, value, false);
}

/**
 * Remove given key and associated value from database.
 * Return true on success, false on failure.
 *
 * Precondition: sdbm_has(key)
 */
bool sdbm_remove(const char *key) {
	DB_OPEN_GUARD();
	if (!key) {
		_set_err(DB_PARAM_ERR);
		return false;
	}
	char *path = _make_path_for_key(key);
	if (!path) {
		_set_err(DB_NOMEM);
		return false;
	}
	bool ret = (remove(path) == 0);
	free(path);
	if (!ret) {
		_set_err(DB_IO_ERR);
	}
	return ret;
}

