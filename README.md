
# Gopher Indexing

* * *
Author: Zihan Ai, u7528678
* * *

## Wireshark Analysis of Initial Response

![avatar](initial_response.png)

The following is a detailed breakdown of the Wireshark capture initial_response.pcapng which documented the TCP communication to and from the Gopher server on port 70. To view this specific traffic, a filter `tcp.port == 70` was applied in Wireshark, which isolated the relevant packets. The capture consisted of 11 significant packets:

1. TCP SYN: The client initiates the session with a SYN packet to the server, requesting to open a connection.
2. TCP SYN-ACK: The server acknowledges the request by replying with a SYN-ACK packet.
3. TCP ACK: The client sends an ACK packet, completing the three-way handshake, and the TCP connection is established.
4. Gopher Request: The client sends a Gopher request immediately after the handshake is complete.
5. TCP ACK: The server acknowledges the Gopher request with a TCP ACK.
6. Gopher Response: The server responds to the Gopher request with the requested information.
7. Gopher Response: The server continues to transmit unfinished data
8. TCP FIN-ACK: The server initiates the termination of the session with a FIN-ACK packet, indicating that it has finished sending its response.
9. TCP ACK: The client acknowledges the server's attempt to terminate the session with an ACK.
10. TCP FIN-ACK: The client sends its own FIN-ACK, requesting to terminate the session from its end.
11. TCP ACK: The server sends a final ACK, confirming the closure of the session.

Throughout this exchange, the connection was stable with no packet loss, and all data was transmitted and acknowledged in full. The detailed packet-by-packet exchange provides a clear map of the TCP communication process and the efficiency of the data transfer between the client and the server. The Wireshark summary included in the initial_response.pcapng file can be referred to for an in-depth view of each packet's contents and protocol-specific details.

* * *

## Introduction
The Gopher Crawler is a Python script designed to interact with a Gopher server. It systematically scans through the server's directories, downloads text and binary files, and compiles statistics about the items found during its crawl.

## Requirements
- Python 3.x
- Access to the Gopher server ( `comp3310.ddns.net` on port `70`)

## Installation
No installation is necessary for the script to run, aside from the Python interpreter itself.

## Code Structure

The Gopher Crawler is designed with simplicity and readability in mind. It consists of two primary Python scripts:
- `gopher_crawler.py`: This is the main module that contains all the crawling logic. It recursively scans through the directories on the server, following links, and downloading files while avoiding loops.
- `main.py`: This is the entry point of the application. It sets up logging, triggers the crawling process using `gopher_crawler.py`, and saves the crawled data to both logs and a statistics file.


### Modifying the Crawler

The crawler can be easily adapted to suit different needs:

- **Server and Port Configuration**: You can change the host and port in `main.py` to target a different Gopher server.
- **Crawling Logic**: If you need to modify the crawling behavior, `gopher_crawler.py` is where you can add or adjust the existing functionality.
- **Output Formatting**: To change how the data is logged or saved, simply modify the respective sections in `main.py`.
- **Error Handling**: The crawler is set up to log detailed error messages. You can add more sophisticated error handling in the `gopher_request` function.


### Ease of Use

The project is well-documented with clear logging, making it straightforward for new developers to pick up the code, understand the flow, and make changes as necessary. Comments and docstrings are used throughout to explain the purpose of functions and their parameters.
For any questions or clarifications, please refer to the comments in the code, or contact the repository maintainers.

---

## Usage
To execute the Gopher Crawler, run the `main.py` script using Python from your command line:
```sh
python main.py
```

### Output
The script will produce the following output:
- A log file (`gopher_requests.log`) detailing all requests made and responses received.
- A statistics file (`gopher_stats.txt`) summarizing the crawl's findings, including:
1. The number of Gopher directories on the server. 
2. The number and a list of all simple text files (full path) 
3. The number and a list of all binary (i.e. non-text) files (full path) 
4. The contents of the smallest text file. 
5. The size of the largest text file. 
6. The size of the smallest and the largest binary files. 
7.  The number of unique invalid references (those with an “error” type) 
8.  A list of external servers (those on a different host and/or port) that were referenced, and whether they were "up" (i.e. whether they accepted a connection on the specified port). 
9. Any references that have “issues/errors”. 

### Logging
The script logs all its operations, both to the console and to a file named `gopher_requests.log`. This log includes timestamps for each request sent, aiding in debugging and monitoring the crawl process.

### Handling Errors and External Servers
The script is designed to handle a variety of common network errors, such as timeouts and connection refusals. In addition, it can **only** crawl dictionarys, text files and binary files, all other types are considered as 'unknown type' and an error will be thrown out.

## Credits
Developed for the COMP6331 at ANU. All connections are made to `comp3310.ddns.net`, which is the server set up for the purposes of this course.
