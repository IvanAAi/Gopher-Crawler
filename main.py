import logging

from gopher_crawler import crawl_gopher


def main():
    # Request user input for the Gopher server address and port
    host = input("Enter the Gopher server address: ")
    port_input = input("Enter the Gopher server port: ")

    # Validate and convert the port to an integer
    try:
        port = int(port_input)
        if not (0 <= port <= 65535):
            raise ValueError("Port number must be between 0 and 65535.")
    except ValueError as e:
        print(f"Invalid port number: {e}")
        return
    # Setting logs
    # Configure logging to write messages to files and print to console
    # Note: Set Mode to 'w' to overwrite old logs
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler("gopher_requests.log", 'w', 'utf-8'),
                                  logging.StreamHandler()])

    # Start request process
    stats = crawl_gopher(host, port)

    # Save statistical data to a separate file
    with open('gopher_stats.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total directories: {stats['dirs']}\n")

        f.write(f"Text files: {len(stats['text_files'])}\n")
        for file_name, size in stats['text_files']:
            f.write(f"{file_name} with size {size} bytes\n")

        f.write(f"Binary files: {len(stats['binary_files'])}\n")
        for file_name, size in stats['binary_files']:
            f.write(f"{file_name} with size {size} bytes\n")

        f.write(f"Smallest text file: {stats['smallest_text']}\n")
        if 'smallest_text_content' in stats:
            f.write("Contents of the smallest text file:\n")
            f.write(stats['smallest_text_content'] + "\n")

        f.write(f"Largest text file: {stats['largest_text']}\n")

        f.write(f"Smallest binary file: {stats['smallest_binary']}\n")
        f.write(f"Largest binary file: {stats['largest_binary']}\n")

        f.write(f"Errors encountered: {stats['errors']}\n")

        f.write(f"External servers checked: {stats['external_servers']}\n")

        if stats['error_details']:
            f.write("Error details:\n")
            for detail in stats['error_details']:
                f.write(str(detail) + "\n")


if __name__ == "__main__":
    main()
