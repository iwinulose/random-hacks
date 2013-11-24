#ifndef _ESCAPE_H_
#define _ESCAPE_H_

#define ESCAPE_SEQ_LEN 3
extern int escape_string(char *dest, const char *src, const size_t dest_len);
extern char *escape_string_dynamic(const char *string);
#endif
