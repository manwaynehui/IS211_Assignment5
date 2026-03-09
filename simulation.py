import argparse
import csv
from collections import deque


class Request:
    def __init__(self, arrival_time, path, process_time):
        # We convert to int here; the encoding fix prevents the \ufeff error
        self.arrival_time = int(arrival_time)
        self.path = path
        self.process_time = int(process_time)

    def calculate_wait(self, current_time):
        """Returns how long the request waited in the queue."""
        return current_time - self.arrival_time


class Server:
    """Simulates a web server processing requests."""
    def __init__(self):
        self.current_task = None
        self.time_remaining = 0
    def is_busy(self):
        return self.current_task is not None
    def tick(self):
        """Decrements the timer for the current task."""
        if self.is_busy():
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.current_task = None
    def start_next(self, new_task):
        """Assigns a new task to the server."""
        self.current_task = new_task
        self.time_remaining = new_task.process_time


def get_requests_from_file(filename):
    """Reads the CSV and handles the hidden BOM encoding issue."""
    requests = []
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                if not row[0].isdigit():
                    continue
                requests.append(Request(row[0], row[1], row[2]))
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    return requests


def simulateOneServer(filename):
    requests = get_requests_from_file(filename)
    if not requests:
        return

    server = Server()
    queue = deque()
    wait_times = []
    current_time = 0
    req_idx = 0

    while req_idx < len(requests) or queue or server.is_busy():

        while req_idx < len(requests) and requests[req_idx].arrival_time == current_time:
            queue.append(requests[req_idx])
            req_idx += 1

        if not server.is_busy() and queue:
            next_req = queue.popleft()
            wait_times.append(next_req.calculate_wait(current_time))
            server.start_next(next_req)

        server.tick()
        current_time += 1

    avg_wait = sum(wait_times) / len(wait_times)
    print(f"Average Wait Time (1 Server): {avg_wait:6.2f} secs")
    return avg_wait


def simulateManyServers(filename, num_servers):
    requests = get_requests_from_file(filename)
    if not requests:
        return

    servers = [Server() for _ in range(num_servers)]
    queues = [deque() for _ in range(num_servers)]
    wait_times = []
    current_time = 0
    req_idx = 0
    rr_index = 0

    while req_idx < len(requests) or any(q for q in queues) or any(s.is_busy() for s in servers):
        while req_idx < len(requests) and requests[req_idx].arrival_time == current_time:
            queues[rr_index].append(requests[req_idx])
            rr_index = (rr_index + 1) % num_servers
            req_idx += 1

        for i in range(num_servers):
            if not servers[i].is_busy() and queues[i]:
                next_req = queues[i].popleft()
                wait_times.append(next_req.calculate_wait(current_time))
                servers[i].start_next(next_req)

            servers[i].tick()

        current_time += 1

    avg_wait = sum(wait_times) / len(wait_times)
    print(f"Average Wait Time ({num_servers} Servers): {avg_wait:6.2f} secs")
    return avg_wait


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to the CSV file", required=True)
    parser.add_argument("--servers", help="Number of servers", type=int)
    args = parser.parse_args()

    if args.servers and args.servers > 1:
        simulateManyServers(args.file, args.servers)
    else:
        simulateOneServer(args.file)


if __name__ == "__main__":
    main()