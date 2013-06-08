/* Copyright (c) 2013 Charles Duyk
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *     1. Redistributions of source code must retain the above copyright
 *        notice, this list of conditions and the following disclaimer.
 *     2. Redistributions in binary form must reproduce the above copyright
 *        notice, this list of conditions and the following disclaimer in the
 *        documentation and/or other materials provided with the distribution.
 *     3. Neither the names of the authors nor the names of other contributors
 *        may be used to endorse or promote products derived from this
 *        software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
 * TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

static bool asciiInput = false;
static bool asciiOutput = false;

static struct encoder {
	uint8_t schedule[256];
	int i;
	int j;
} arc4;

static void usage(const char *progName) {
	fprintf(stderr, "Usage: %s [-aAh] key [discarded]\n", progName);
	fprintf(stderr, "\n");
	fprintf(stderr, "Reads bytes from stdin, encodes them using arc4, outputs to stdout\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Positional arguments:\n");
	fprintf(stderr, "\tkey: the key to use for arc4 (1 <= keyLen <= 256)\n");
	fprintf(stderr, "\tdiscarded: number of bytes discarded (default: 4096)\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Optional arguments:\n");
	fprintf(stderr, "\t-a: translate output bytes to hex\n");
	// fprintf(stderr, "\t-A: translate input bytes from hex (each byte expected to be 2 ascii characters, whitespace ignored)\n");
	fprintf(stderr, "\t-k: output a byte of the key stream for each byte of the input stream (no encoding)\n");
	fprintf(stderr, "\t-h: print this help message to stderr\n");
	fprintf(stderr, "\n");
}

static void initialize_encoder(struct encoder *encoder, char *key, size_t keylen) {
	int i = 0;
	int j = 0;
	uint8_t tmp = 0;
	bzero(encoder, sizeof(struct encoder));
	uint8_t *schedule = encoder->schedule;
	for(i = 0; i < 256; i++) {
		schedule[i] = i;
	}
	for(i = 0; i < 256; i++) {
		int keyIdx = i % keylen;
		uint8_t keyByte = key[keyIdx];
		uint8_t schedByte = schedule[i];
		j = (j + schedByte + keyByte) % 256;
		schedule[i] = schedule[j];
		schedule[j] = schedByte;
	}
}

static char tick(struct encoder *encoder) {
	uint8_t *schedule = encoder->schedule;
	int i = encoder->i;
	int j = encoder->j;
	i = (i + 1) % 256;
	j = (j + schedule[i]) % 256;
	encoder->i = i;
	encoder->j = j;
	uint8_t tmp = schedule[i];
	schedule[i] = schedule[j];
	schedule[j] = tmp;
	int retIdx = (schedule[i] + schedule[j]) % 256;
	return schedule[retIdx];
}

static void emit(uint8_t c) {
	if(asciiOutput) {
		printf("%.2x ", c);
	}
	else {
		fwrite(&c, 1, 1, stdout);
	}
}

static bool next(uint8_t *in) {
	return fread(in, 1, 1, stdin) == 1;
}

int main(int argc, char **argv) {
	int optIdx = 0;
	int keyIdx = 1;
	int discardIdx = 2;
	bool keyOut = false;
	char *key = NULL;
	size_t discard = 4096L;
	uint8_t in = 0;
	if (argc < 2) {
		usage(argv[0]);
		return 1;
	}
	if (argv[1][0] == '-') {
		optIdx = 1;
		keyIdx = 2;
		discardIdx = 3;
	}
	if(keyIdx >= argc) {
		usage(argv[0]);
		return 1;
	}
	if (optIdx) {
		size_t len = strlen(argv[optIdx]);
		for(int i = 1; i < len; i++) {
			char opt = argv[optIdx][i];
			switch (opt) {
				case 'a':
					asciiOutput = true;
					break;
				// case 'A':
				// 	asciiInput = true;
				// 	break;
				case 'k':
					keyOut = true;
					break;
				case 'h':
					usage(argv[0]);
					return 0;
					break;
				default:
					fprintf(stderr, "Unknown option %c\n", opt);
					usage(argv[0]);
					return 1;
					break;
			}
		}
	}
	key = argv[keyIdx];
	if (discardIdx < argc) {
		discard = atoi(argv[discardIdx]);
	}
	initialize_encoder(&arc4, key, strlen(key));
	for(size_t i = 0; i < discard; i++) {
		tick(&arc4);
	}
	while(next(&in)) {
		char k = tick(&arc4);
		if (keyOut) {
			emit(k);
		}
		else {
			emit(k ^ in);
		}
	}
	return 0;
}
