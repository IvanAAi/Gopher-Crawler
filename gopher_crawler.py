import socket
import logging


def gopher_request(host, port, selector, stats, timeout=5, max_size=1048576):
    """
    Send a request to a gopher server and receive a response.

    :param host: The hostname of the gopher server.
    :param port: The port number of the gopher server.
    :param selector: The selector string to specify the resource on the gopher server.
    :param stats: A dictionary to keep track of various statistics including errors.
    :param timeout: The timeout duration in seconds for the connection attempt.
    :param max_size: The maximum size in bytes for the response data.

    :return: The response data as bytes, or None if an error occurred.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        request = selector + "\r\n"
        logging.info(f"Sending request to {host}:{port}: {request.strip()}")
        try:
            s.connect((host, port))
            s.sendall(request.encode())
            response = b""
            while True:
                data = s.recv(1024)
                if not data:
                    break
                response += data
                if len(response) > max_size:    # Prevent excessive data
                    error_msg = f"Data exceeded {max_size} bytes, skipping file."
                    logging.info(f"{error_msg}")
                    stats['errors'] += 1
                    stats['error_details'].append((selector, error_msg))  # Record the error message in detail
                    return None
            return response
        except ConnectionRefusedError:  # If the server refused to connect
            error_msg = "Connection refused."
            logging.info(f"{error_msg}")
            stats['errors'] += 1
            stats['error_details'].append((selector, error_msg))
            return None
        except socket.timeout:  # If the transmission speed of information is too slow or unable to connect
            error_msg = "Connection timed out."
            logging.info(f"{error_msg}")
            stats['errors'] += 1
            stats['error_details'].append((selector, error_msg))
            return None


def parse_directory(response):
    """
    Parse the directory listing from a gopher server response.

    :param response: The byte string response received from the server.

    :return: A list of tuples containing the type, display string, selector, host, and port.
    """
    items = []
    try:
        decoded_response = response.decode('utf-8')  # Attempt to decode response
    except UnicodeDecodeError:
        decoded_response = response.decode('iso-8859-1')  # Handling decoding errors

    lines = decoded_response.splitlines()
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 4:  # Ensure that the format of the data is correct
            item_type = parts[0][0]
            display_string = parts[0][1:].strip()
            selector = parts[1]
            host = parts[2]
            try:
                port = int(parts[3])
                # In general, the port number will not be zero.
                # Here, we mainly distinguish some 'invalid: 0' issues encountered during data processing
                if port == 0:
                    continue
                items.append((item_type, display_string, selector, host, port))
            except ValueError:
                logging.info(f"Error parsing port for line: {line}")
    return items


def check_server_active(host, port):
    """
    Check if a server is active by attempting to connect to it.

    :param host: The hostname of the server to check.
    :param port: The port number of the server to check.

    :return: True if the server is active, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((host, port))
            return True
    except socket.error as e:   # Unable to connect external server
        logging.info(f"Failed to connect to {host}:{port} - {e}")
        return False


# Used to record visited paths and checked external servers
# Prevent duplicate visit of a path
visited_paths = set()
external_servers_checked = set()


def crawl_gopher(host, port, selector="", stats=None, original_host=None):
    """
    Recursively crawl a gopher server to retrieve directory and file information.

    :param host: The hostname of the gopher server.
    :param port: The port number of the gopher server.
    :param selector: The initial selector to start crawling from.
    :param stats: A dictionary to collect statistics and information during crawling.
    :param original_host: The original host to compare for external server checks.

    :return: The stats dictionary updated with the information collected.
    """

    if stats is None:
        stats = {
            'dirs': 0, 'files': 0, 'text_files': [], 'binary_files': [],
            'smallest_text': ('', float('inf')), 'largest_text': ('', 0),
            'smallest_binary': ('', float('inf')), 'largest_binary': ('', 0),
            'smallest_text_content': '',
            'external_servers': {}, 'errors': 0, 'error_details': [],
            'all_files': [], 'all_directories': set()
        }

    global visited_paths
    if original_host is None:
        original_host = host

    path = f"{host}:{port}{selector}"
    if path in visited_paths:
        return stats
    visited_paths.add(path)

    response = gopher_request(host, port, selector, stats)
    if response is None:
        stats['error_details'].append((selector, "Failed to receive any response from server."))
        stats['errors'] += 1
        return stats

    items = parse_directory(response)
    for item in items:
        item_type, display_string, selector, new_host, new_port = item
        if new_host != original_host or new_port != port:
            # This is an external server, and there is no need to crawl its content
            server_key = f"{new_host}:{new_port}"
            if server_key not in stats['external_servers']:
                active = check_server_active(new_host, new_port)
                stats['external_servers'][server_key] = active
            continue

        full_path = f"{new_host}:{new_port}{selector}"
        if new_host == original_host and new_port == port:
            if item_type == '1':    # The type is 'dictionary'
                if full_path not in stats['all_directories']:
                    stats['dirs'] += 1
                    stats['all_directories'].add(full_path)
                    crawl_gopher(new_host, new_port, selector, stats, original_host)
            elif item_type in ['0', '9']:   # '0' means text file and '9' means binary file
                file_response = gopher_request(new_host, new_port, selector, stats)
                if file_response is not None:
                    process_file(item, stats, file_response, is_binary=(item_type == '9'))

            elif item_type == 'i':  # Information item
                continue
            else:   # All other type are considered as unknown type and an error will be thrown out
                error_msg = f"Unknown item type encountered: {item_type}"
                stats['error_details'].append((selector, error_msg))
                stats['errors'] += 1

    return stats


def process_file(item, stats, response, is_binary=False):
    """
    Process a file received from the gopher server and update statistics.

    :param item: A tuple containing information about the file (type, display string, selector, host, port).
    :param stats: A dictionary where file statistics will be updated.
    :param response: The byte string response representing the file content.
    :param is_binary: A flag indicating if the file is binary or text.
    """
    item_type, display_string, selector, new_host, new_port = item
    original_file_path = f"{new_host}:{new_port}{selector}"
    safe_selector = selector[-100:]  # Handling long file names
    safe_file_path = f"{new_host}:{new_port}{safe_selector}".replace('/', '_')
    # Replace '/' with '_' to prevent mistaking file names for paths
    file_size = len(response)

    if is_binary:
        with open(safe_file_path, 'wb') as f:
            f.write(response)
        stats['binary_files'].append((original_file_path, file_size))
        if file_size < stats['smallest_binary'][1]:
            stats['smallest_binary'] = (original_file_path, file_size)
        if file_size > stats['largest_binary'][1]:
            stats['largest_binary'] = (original_file_path, file_size)

    else:
        response_text = response.decode('utf-8')
        with open(safe_file_path, 'w', encoding='utf-8') as f:
            f.write(response_text)
        stats['text_files'].append((original_file_path, file_size))
        if file_size < stats['smallest_text'][1]:
            stats['smallest_text'] = (original_file_path, file_size)
            stats['smallest_text_content'] = response_text
        if file_size > stats['largest_text'][1]:
            stats['largest_text'] = (original_file_path, file_size)

    original_file_path = f"{new_host}:{new_port}{selector}".replace('_', '/')
    stats['all_files'].append((original_file_path, file_size))
    stats['files'] += 1
    logging.info(
        f"Processed {'binary' if is_binary else 'text'} file: {original_file_path} with size {file_size} bytes")
