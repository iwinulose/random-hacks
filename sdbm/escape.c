#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "escape.h"

typedef struct translation {
	const size_t len;
	const char *str;
} translation_s;

static const translation_s _lookup[] = {
	{3, "%00"},
	{3, "%01"},
	{3, "%02"},
	{3, "%03"},
	{3, "%04"},
	{3, "%05"},
	{3, "%06"},
	{3, "%07"},
	{3, "%08"},
	{3, "%09"},
	{3, "%0a"},
	{3, "%0b"},
	{3, "%0c"},
	{3, "%0d"},
	{3, "%0e"},
	{3, "%0f"},
	{3, "%10"},
	{3, "%11"},
	{3, "%12"},
	{3, "%13"},
	{3, "%14"},
	{3, "%15"},
	{3, "%16"},
	{3, "%17"},
	{3, "%18"},
	{3, "%19"},
	{3, "%1a"},
	{3, "%1b"},
	{3, "%1c"},
	{3, "%1d"},
	{3, "%1e"},
	{3, "%1f"},
	{3, "%20"},
	{3, "%21"},
	{3, "%22"},
	{3, "%23"},
	{3, "%24"},
	{3, "%25"},
	{3, "%26"},
	{3, "%27"},
	{3, "%28"},
	{3, "%29"},
	{3, "%2a"},
	{3, "%2b"},
	{3, "%2c"},
	{3, "%2d"},
	{3, "%2e"},
	{3, "%2f"},
	{1, "0"},
	{1, "1"},
	{1, "2"},
	{1, "3"},
	{1, "4"},
	{1, "5"},
	{1, "6"},
	{1, "7"},
	{1, "8"},
	{1, "9"},
	{3, "%3a"},
	{3, "%3b"},
	{3, "%3c"},
	{3, "%3d"},
	{3, "%3e"},
	{3, "%3f"},
	{3, "%40"},
	{1, "A"},
	{1, "B"},
	{1, "C"},
	{1, "D"},
	{1, "E"},
	{1, "F"},
	{1, "G"},
	{1, "H"},
	{1, "I"},
	{1, "J"},
	{1, "K"},
	{1, "L"},
	{1, "M"},
	{1, "N"},
	{1, "O"},
	{1, "P"},
	{1, "Q"},
	{1, "R"},
	{1, "S"},
	{1, "T"},
	{1, "U"},
	{1, "V"},
	{1, "W"},
	{1, "X"},
	{1, "Y"},
	{1, "Z"},
	{3, "%5b"},
	{3, "%5c"},
	{3, "%5d"},
	{3, "%5e"},
	{3, "%5f"},
	{3, "%60"},
	{1, "a"},
	{1, "b"},
	{1, "c"},
	{1, "d"},
	{1, "e"},
	{1, "f"},
	{1, "g"},
	{1, "h"},
	{1, "i"},
	{1, "j"},
	{1, "k"},
	{1, "l"},
	{1, "m"},
	{1, "n"},
	{1, "o"},
	{1, "p"},
	{1, "q"},
	{1, "r"},
	{1, "s"},
	{1, "t"},
	{1, "u"},
	{1, "v"},
	{1, "w"},
	{1, "x"},
	{1, "y"},
	{1, "z"},
	{3, "%7b"},
	{3, "%7c"},
	{3, "%7d"},
	{3, "%7e"},
	{3, "%7f"}
};

int escape_string(char *dest, const char *src, const size_t dest_len) {
	if (!dest || !src || !dest_len) {
		return 1;
	}
	char c = '\0';
	size_t dest_remain = dest_len - 1;
	bool stop = false;
	while((c = *src++) && dest_remain && !stop) {
		const translation_s *translate = &_lookup[(int)c];
		const size_t len = translate->len;
		const char *escape = translate->str;
		stop = dest_remain < len;
		if (!stop) {
			for (size_t i = 0; i < len; i++) {
				*dest++ = escape[i];
			}
			dest_remain -= len;
		}
	}
	*dest = '\0';
	return stop;
}

char *escape_string_dynamic(const char *string) {
	if (!string) {
		return NULL;
	}
	size_t len = strlen(string);
	size_t escaped_len = len * ESCAPE_SEQ_LEN + 1;
	char *escape_buf = calloc(1, escaped_len);
	if(escape_buf) {
		escape_string(escape_buf, string, escaped_len);
	}
	return escape_buf;
}
