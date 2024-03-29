/*
 * Sean Middleditch
 * sean@sourcemud.org
 *
 * The author or authors of this code dedicate any and all copyright interest
 * in this code to the public domain. We make this dedication for the benefit
 * of the public at large and to the detriment of our heirs and successors. We
 * intend this dedication to be an overt act of relinquishment in perpetuity of
 * all present and future rights to this code under copyright law. 
 */

#include <stdarg.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <poll.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <unistd.h>

#ifdef HAVE_ZLIB
#include "zlib.h"
#endif

#include "libtelnet.h"

#ifdef ENABLE_COLOR
# define COLOR_SERVER "\e[35m"
# define COLOR_CLIENT "\e[34m"
# define COLOR_BOLD "\e[1m"
# define COLOR_UNBOLD "\e[22m"
# define COLOR_NORMAL "\e[0m"
#else
# define COLOR_SERVER ""
# define COLOR_CLIENT ""
# define COLOR_BOLD ""
# define COLOR_UNBOLD ""
# define COLOR_NORMAL ""
#endif

#ifdef DEBUG_COMM
#define DEBUG(args)	printf args
#else
#define DEBUG(args)
#endif

struct conn_t {
	const char *name;
	int sock;
	telnet_t telnet;
	struct conn_t *remote;
};

void os_log(char *format, ...) {
	va_list ap;

	fprintf(stdout, "os_log: ");
	va_start(ap, format);
	vfprintf(stdout, format, ap);
	va_end(ap);
	fprintf(stdout, "\n");
	fflush(stdout);
}

static const char *get_cmd(unsigned char cmd) {
	static char buffer[4];

	switch (cmd) {
	case 255: return "IAC";
	case 254: return "DONT";
	case 253: return "DO";
	case 252: return "WONT";
	case 251: return "WILL";
	case 250: return "SB";
	case 249: return "GA";
	case 248: return "EL";
	case 247: return "EC";
	case 246: return "AYT";
	case 245: return "AO";
	case 244: return "IP";
	case 243: return "BREAK";
	case 242: return "DM";
	case 241: return "NOP";
	case 240: return "SE";
	case 239: return "EOR";
	case 238: return "ABORT";
	case 237: return "SUSP";
	case 236: return "xEOF";
	default:
		snprintf(buffer, sizeof(buffer), "%d", (int)cmd);
		return buffer;
	}
}

static const char *get_opt(unsigned char opt) {
	switch (opt) {
	case 0: return "BINARY";
	case 1: return "ECHO";
	case 2: return "RCP";
	case 3: return "SGA";
	case 4: return "NAMS";
	case 5: return "STATUS";
	case 6: return "TM";
	case 7: return "RCTE";
	case 8: return "NAOL";
	case 9: return "NAOP";
	case 10: return "NAOCRD";
	case 11: return "NAOHTS";
	case 12: return "NAOHTD";
	case 13: return "NAOFFD";
	case 14: return "NAOVTS";
	case 15: return "NAOVTD";
	case 16: return "NAOLFD";
	case 17: return "XASCII";
	case 18: return "LOGOUT";
	case 19: return "BM";
	case 20: return "DET";
	case 21: return "SUPDUP";
	case 22: return "SUPDUPOUTPUT";
	case 23: return "SNDLOC";
	case 24: return "TTYPE";
	case 25: return "EOR";
	case 26: return "TUID";
	case 27: return "OUTMRK";
	case 28: return "TTYLOC";
	case 29: return "3270REGIME";
	case 30: return "X3PAD";
	case 31: return "NAWS";
	case 32: return "TSPEED";
	case 33: return "LFLOW";
	case 34: return "LINEMODE";
	case 35: return "XDISPLOC";
	case 36: return "ENVIRON";
	case 37: return "AUTHENTICATION";
	case 38: return "ENCRYPT";
	case 39: return "NEW-ENVIRON";
	case 70: return "MSSP";
	case 85: return "COMPRESS";
	case 86: return "COMPRESS2";
	case 93: return "ZMP";
	case 255: return "EXOPL";
	default: return "unknown";
	}
}

static void print_buffer(const char *buffer, size_t size) {
	size_t i;
	for (i = 0; i != size; ++i) {
		if (buffer[i] == ' ' || (isprint(buffer[i]) && !isspace(buffer[i])))
			DEBUG(("%c", (char)buffer[i]));
		else if (buffer[i] == '\n')
			DEBUG(("<" COLOR_BOLD "0x%02X" COLOR_UNBOLD ">\n",
					(int)buffer[i]));
		else
			DEBUG(("<" COLOR_BOLD "0x%02X" COLOR_UNBOLD ">", (int)buffer[i]));
	}
}

static void _send(int sock, const char *buffer, size_t size) {
	int rs;

	/* send data */
	while (size > 0) {
		if ((rs = send(sock, buffer, size, 0)) == -1) {
			if (errno != EINTR && errno != ECONNRESET) {
				fprintf(stderr, "send() failed: %s\n", strerror(errno));
				exit(1);
			} else {
				return;
			}
		} else if (rs == 0) {
			fprintf(stderr, "send() unexpectedly returned 0\n");
			exit(1);
		}

		/* update pointer and size to see if we've got more to send */
		buffer += rs;
		size -= rs;
	}
}

#define BUFFER_SIZE 160

/* additional 1-byte for safe '\0' */
char s_cmd[BUFFER_SIZE + 1] = "";
char c_cmd[BUFFER_SIZE + 1] = "";
char prompt[BUFFER_SIZE + 1] = "NONE";

#define CLI	(source == 'C')
#define SVR	(source == 'S')

int os_logger(char source, const char *str, int len)
{
	register int i;
	char *buffer = NULL;
	char dr[5];

	if (SVR) {
		buffer = s_cmd;
		sprintf(dr, "<<< ");
	} else if (CLI) {
		buffer = c_cmd;
		sprintf(dr, ">>> ");
	} else {
		os_log("_INFO: unknown connection to log: %c", source);
		return 1;
	}

	/* FIXME straight forward implementation. optimaziation needed. */
	for (i = 0; i < len; i++) {
		//DEBUG(("icurrent char: (0x%02x)\n", str[i]));
		if ((char)str[i] == 0x0D) {
			if (CLI && strstr(prompt, "word:")) {
				os_log("%sPASSWD PROTECTED (experimental)", dr);
			} else {
				os_log("%s%s,%d", dr, buffer, strlen(buffer));
			}
			buffer[0] = '\0';
			if ((char)str[i+1] == 0x0A || (char)str[i+1] == 0x00) {
				i++;
			}
		} else if (CLI && str[i] == 0x7f) {
			if (strlen(buffer)) {
				buffer[strlen(buffer)-1] = '\0';
			}
			/* else ignore backspace to empty buffer */
		} else {
			sprintf(buffer, "%s%c", buffer, (char)str[i]);
		}

		if (strlen(buffer) >= (BUFFER_SIZE)) {
			/* print out current log string with mark: */
			char tmp[BUFFER_SIZE + 1];
			strncpy(tmp, buffer, BUFFER_SIZE - 5);
			tmp[BUFFER_SIZE - 5] = '\0';
			os_log("%s%s:CONT,%d", dr, tmp, strlen(tmp));
			/* buggy? but buffer_size is enough to. */
			sprintf(buffer, "%s", buffer + BUFFER_SIZE - 5);
			/* we need tail of previous buffer.
			 * to detect server's prompt
			 */
		}
	}

	if (SVR && strlen(s_cmd) && strncmp(prompt, s_cmd, strlen(prompt))) {
		os_log("_INFO: prompt changed from '%s' to '%s'.",
				prompt, s_cmd);
		strcpy(prompt, s_cmd);
	}

	return 0;
}



static void _event_handler(telnet_t *telnet, telnet_event_t *ev,
		void *user_data) {
	struct conn_t *conn = (struct conn_t*)user_data;

	switch (ev->type) {
	/* data received */
	case TELNET_EV_DATA:
		DEBUG(("%s DATA: ", conn->name));
		print_buffer(ev->buffer, ev->size);
		DEBUG((COLOR_NORMAL "\n"));

		telnet_send(&conn->remote->telnet, ev->buffer, ev->size);
		os_logger(conn->name[0], ev->buffer, ev->size);

		break;
	/* data must be sent */
	case TELNET_EV_SEND:
		/* DONT SPAM
		DEBUG(("%s SEND: ", conn->name));
		print_buffer(ev->buffer, ev->size);
		DEBUG((COLOR_BOLD "\n"));
		*/

		_send(conn->sock, ev->buffer, ev->size);
		break;
	/* IAC command */
	case TELNET_EV_IAC:
		DEBUG(("%s IAC %s" COLOR_NORMAL "\n", conn->name,
				get_cmd(ev->command)));

		telnet_iac(&conn->remote->telnet, ev->command);
		break;
	/* negotiation, WILL */
	case TELNET_EV_WILL:
		DEBUG(("%s IAC WILL %d (%s)" COLOR_NORMAL "\n", conn->name,
				(int)ev->telopt, get_opt(ev->telopt)));
		telnet_negotiate(&conn->remote->telnet, TELNET_WILL,
				ev->telopt);
		break;
	/* negotiation, WONT */
	case TELNET_EV_WONT:
		DEBUG(("%s IAC WONT %d (%s)" COLOR_NORMAL "\n", conn->name,
				(int)ev->telopt, get_opt(ev->telopt)));
		telnet_negotiate(&conn->remote->telnet, TELNET_WONT,
				ev->telopt);
		break;
	/* negotiation, DO */
	case TELNET_EV_DO:
		DEBUG(("%s IAC DO %d (%s)" COLOR_NORMAL "\n", conn->name,
				(int)ev->telopt, get_opt(ev->telopt)));
		telnet_negotiate(&conn->remote->telnet, TELNET_DO,
				ev->telopt);
		break;
	case TELNET_EV_DONT:
		DEBUG(("%s IAC DONT %d (%s)" COLOR_NORMAL "\n", conn->name,
				(int)ev->telopt, get_opt(ev->telopt)));
		telnet_negotiate(&conn->remote->telnet, TELNET_DONT,
				ev->telopt);
		break;
	/* subnegotiation */
	case TELNET_EV_SUBNEGOTIATION:
		if (ev->telopt == TELNET_TELOPT_ZMP) {
			if (ev->argc != 0) {
				size_t i;
				DEBUG(("%s ZMP [%zi params]", conn->name, ev->argc));
				for (i = 0; i != ev->argc; ++i) {
					DEBUG((" \""));
					print_buffer(ev->argv[i], strlen(ev->argv[i]));
					DEBUG(("\""));
				}
				DEBUG((COLOR_NORMAL "\n"));
			} else {
				DEBUG(("%s ZMP (malformed!) [%zi bytes]",
						conn->name, ev->size));
				print_buffer(ev->buffer, ev->size);
				DEBUG((COLOR_NORMAL "\n"));
			}
		} else if (ev->telopt == TELNET_TELOPT_TTYPE ||
				ev->telopt == TELNET_TELOPT_ENVIRON ||
				ev->telopt == TELNET_TELOPT_NEW_ENVIRON ||
				ev->telopt == TELNET_TELOPT_MSSP) {
			size_t i;
			DEBUG(("%s %s [%zi parts]", conn->name, get_opt(ev->telopt),
					ev->argc));
			for (i = 0; i != ev->argc; ++i) {
				DEBUG((" \""));
				print_buffer(ev->argv[i], strlen(ev->argv[i] + 1) + 1);
				DEBUG(("\""));
			}
			DEBUG((COLOR_NORMAL "\n"));
		} else {
			DEBUG(("%s SUB %d (%s)", conn->name, (int)ev->telopt,
					get_opt(ev->telopt)));
			if (ev->size > 0) {
				DEBUG((" [%zi bytes]: ", ev->size));
				print_buffer(ev->buffer, ev->size);
			}
			DEBUG((COLOR_NORMAL "\n"));
		}

		/* forward */
		telnet_subnegotiation(&conn->remote->telnet, ev->telopt,
				ev->buffer, ev->size);
		break;
	/* compression notification */
	case TELNET_EV_COMPRESS:
		DEBUG(("%s COMPRESSION %s" COLOR_NORMAL "\n", conn->name,
				ev->command ? "ON" : "OFF"));
		break;
	/* warning */
	case TELNET_EV_WARNING:
		DEBUG(("%s WARNING: %s" COLOR_NORMAL "\n", conn->name, ev->buffer));
		break;
	/* error */
	case TELNET_EV_ERROR:
		DEBUG(("%s ERROR: %s" COLOR_NORMAL "\n", conn->name, ev->buffer));
		exit(1);
	}
}

int main(int argc, char **argv) {
	char buffer[512];
	short listen_port;
	int listen_sock;
	int rs;
	struct sockaddr_in addr;
	socklen_t addrlen;
	struct pollfd pfd[2];
	struct conn_t server;
	struct conn_t client;
	struct addrinfo *ai;
	struct addrinfo hints;

	/* check usage */
	if (argc != 5) {
		fprintf(stderr, "Usage: %s target_ip target_port "
				"client_ip local_port\n", argv[0]);
		return 1;
	}

	/* parse listening port */
	listen_port = strtol(argv[4], 0, 10);

	os_log("_INFO: tunnel from %s to %s is drilled.", argv[3], argv[1]);
	/* loop forever, until user kills process */
	for (;;) {
		/* create listening socket */
		if ((listen_sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
			fprintf(stderr, "socket() failed: %s\n", strerror(errno));
			return 1;
		}

		/* reuse address option */
		rs = 1;
		setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &rs, sizeof(rs));

		/* bind to listening addr/port */
		memset(&addr, 0, sizeof(addr));
		addr.sin_family = AF_INET;
		addr.sin_addr.s_addr = INADDR_ANY;
		addr.sin_port = htons(listen_port);
		if (bind(listen_sock, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
			fprintf(stderr, "bind() failed: %s\n", strerror(errno));
			return 1;
		}

		DEBUG(("LISTENING ON PORT %d\n", listen_port));

		/* maybe we need timeout here. with alarm? */

		/* wait for client */
		if (listen(listen_sock, 1) == -1) {
			fprintf(stderr, "listen() failed: %s\n", strerror(errno));
			return 1;
		}
		addrlen = sizeof(addr);
		if ((client.sock = accept(listen_sock, (struct sockaddr *)&addr,
				&addrlen)) == -1) {
			fprintf(stderr, "accept() failed: %s\n", strerror(errno));
			return 1;
		}

		DEBUG(("CLIENT CONNECTION RECEIVED\n"));
		
		/* stop listening now that we have a client */
		close(listen_sock);

		/* so what? ok, here is the point of checking peer is valid.
		 * check ip_address and port! oh! can I use revert connection?
		 * it is safe for firewall environment and more secure.
		 * ok, then we need so called "local proxy" too. ok, but it
		 * need some problem. for example... windows os firewall. yep.
		 * just go ahead!
		 *
		 * if we use ssh for client-gateway connection, then we can
		 * use one-time-keypair.
		 */

		if (strcmp(argv[3], inet_ntoa(addr.sin_addr))) {
			os_log("_INFO: connection from unauthorized host(%s)."
					" reject and continue.",
					inet_ntoa(addr.sin_addr));
			close(client.sock);
			continue;
		}

		/* look up server host */
		memset(&hints, 0, sizeof(hints));
		hints.ai_family = AF_UNSPEC;
		hints.ai_socktype = SOCK_STREAM;
		if ((rs = getaddrinfo(argv[1], argv[2], &hints, &ai)) != 0) {
			fprintf(stderr, "getaddrinfo() failed for %s: %s\n", argv[1],
					gai_strerror(rs));
			return 1;
		}
		
		/* create server socket */
		if ((server.sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
			fprintf(stderr, "socket() failed: %s\n", strerror(errno));
			return 1;
		}

		/* bind server socket */
		memset(&addr, 0, sizeof(addr));
		addr.sin_family = AF_INET;
		if (bind(server.sock, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
			fprintf(stderr, "bind() failed: %s\n", strerror(errno));
			return 1;
		}

		/* connect */
		if (connect(server.sock, ai->ai_addr, ai->ai_addrlen) == -1) {
			fprintf(stderr, "server() failed: %s\n", strerror(errno));
			return 1;
		}

		os_log("_INFO: connection established. (%s to %s)",
				argv[4], argv[1]);

		/* free address lookup info */
		freeaddrinfo(ai);

		DEBUG(("SERVER CONNECTION ESTABLISHED\n"));

		/* initialize connection structs */
		server.name = COLOR_SERVER "SERVER";
		server.remote = &client;
		client.name = COLOR_CLIENT "CLIENT";
		client.remote = &server;

		/* initialize telnet boxes */
		telnet_init(&server.telnet, 0, _event_handler, TELNET_FLAG_PROXY,
				&server);
		telnet_init(&client.telnet, 0, _event_handler, TELNET_FLAG_PROXY,
				&client);

		/* initialize poll descriptors */
		memset(pfd, 0, sizeof(pfd));
		pfd[0].fd = server.sock;
		pfd[0].events = POLLIN;
		pfd[1].fd = client.sock;
		pfd[1].events = POLLIN;

		/* loop while both connections are open */
		while (poll(pfd, 2, -1) != -1) {
			/* read from server */
			if (pfd[0].revents & POLLIN) {
				if ((rs = recv(server.sock, buffer, sizeof(buffer), 0)) > 0) {
					telnet_recv(&server.telnet, buffer, rs);
				} else if (rs == 0) {
					DEBUG(("%s DISCONNECTED" COLOR_NORMAL "\n", server.name));
					break;
				} else {
					if (errno != EINTR && errno != ECONNRESET) {
						fprintf(stderr, "recv(server) failed: %s\n",
								strerror(errno));
						exit(1);
					}
				}
			}

			/* read from client */
			if (pfd[1].revents & POLLIN) {
				if ((rs = recv(client.sock, buffer, sizeof(buffer), 0)) > 0) {
					telnet_recv(&client.telnet, buffer, rs);
				} else if (rs == 0) {
					DEBUG(("%s DISCONNECTED" COLOR_NORMAL "\n", client.name));
					break;
				} else {
					if (errno != EINTR && errno != ECONNRESET) {
						fprintf(stderr, "recv(server) failed: %s\n",
								strerror(errno));
						exit(1);
					}
				}
			}
		}

		/* clean up */
		telnet_free(&server.telnet);
		telnet_free(&client.telnet);
		close(server.sock);
		close(client.sock);

		/* all done */
		DEBUG(("BOTH CONNECTIONS CLOSED\n"));
		/* loop is forever but serve once.
		 * inifinite loop is for case of connection failed by...
		 */
		break;
	}
	os_log("_INFO: mission completed! yiman...", argv[4], argv[1]);

	/* not that we can reach this, but GCC will cry if it's not here */
	return 0;
}
