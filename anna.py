import dns.resolver
import socket
import sys
import time
import random
from threading import Thread
from queue import Queue
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define ports for protocols
PORTS = {
    'smtp': {
        'standard': [25],
        'secure': [465, 587, 2525, 26],
        'alternative': [80, 443, 587, 2525],
    },
    'pop3': {
        'standard': [110],
        'secure': [995],
        'alternative': [8110, 8123],
    },
    'imap': {
        'standard': [143],
        'secure': [993],
        'alternative': [220],
    }
}

# Function to display a banner with colored output
def banner():
    clear = "\x1b[0m"
    colors = [36, 32, 34, 35, 31, 37]

    x = """
       ___
     o|* *|o  ╔╦═╦╗╔╦╗╔╦═╦╗
     o|* *|o  ║║╔╣╚╝║║║║║║║
     o|* *|o  ║║╚╣╔╗║╚╝║╩║║
      ║===/   ║╚═╩╝╚╩══╩╩╝║
       |||    ╚═══════════╝
       |||  K.E.U.R - E.M.A.I.L
       |||    ╔═╦═╦╦═╦╦═╗╔═╦╦══╦══╦╦╗
       |||    ║╩║║║║║║║╩║║╚║╠╗╔╩╗╔╩╗║
    ___|||___ ╚╩╩╩═╩╩═╩╩╝╚═╩╝╚╝ ╚╝ ╚╝

      By : AnnaQitty
      Github : github.com/annaqitty    
                                              
                          
                          
                                      """
    for N, line in enumerate(x.split("\n")):
        sys.stdout.write("\x1b[1;%dm%s%s\n" % (random.choice(colors), line, clear))
        time.sleep(0.05)

# Function to check MX records for a domain
def check_mx_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [r.exchange.to_text() for r in answers]
        return mx_records
    except Exception as e:
        print(Fore.RED + f"3RR0R R3tR1PP3D {domain}")
        return []

# Function to check if a protocol is supported by connecting to the server
def check_protocol_support(server, protocol):
    ports = PORTS[protocol]['standard'] + PORTS[protocol]['secure'] + PORTS[protocol]['alternative']
    supported_ports = []
    for port in ports:
        try:
            with socket.create_connection((server, port), timeout=5):
                supported_ports.append(port)
        except (socket.timeout, ConnectionRefusedError):
            continue
    return supported_ports

# Function to save results to a file without color codes
def save_results(file_name, results):
    with open(file_name, "a") as file:  # Open in append mode
        for server in results:
            domain = results[server]['domain']
            file.write(f"{domain}, {server}\n")  # Write each result on a new line

# Function to process each domain
def process_domain(domain):
    mx_records = check_mx_records(domain)
    if not mx_records:
        print(Fore.RED + f"N0 R.E.C.O.R.D_MX {domain}.")
        return

    results = {'smtp': {}, 'pop3': {}, 'imap': {}}

    for server in mx_records:
        for protocol in PORTS:
            supported_ports = check_protocol_support(server, protocol)
            if supported_ports:
                results[protocol][server] = {
                    'domain': domain,
                    'supported_ports': supported_ports
                }
        
        # Save results for each protocol
        for protocol in results:
            save_results(f'{protocol.upper()}-Server.txt', results[protocol])

    print(Fore.BLUE + f"O.P.E.N {domain} and S.A.V.E.D")

# Worker thread class to handle tasks
class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(Fore.RED + str(e))
            self.tasks.task_done()

# ThreadPool class to manage multiple worker threads
class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        self.tasks.join()

# Main function to read domains from a file and process them
def main(input_file):
    banner()  # Display the banner

    # Get the number of threads from user input
    num_threads = int(input(Fore.LIGHTGREEN_EX + '+[+] Threads : ' + Style.RESET_ALL))
    pool = ThreadPool(num_threads)
    
    with open(input_file, "r") as file:
        domains = [line.strip() for line in file if line.strip()]

    # Add tasks to the pool
    for domain in domains:
        pool.add_task(process_domain, domain)
    
    # Wait for all tasks to complete
    pool.wait_completion()
    
    print(Fore.BLUE + "C.O.M.P.L.E.T.E.D")

# Entry point of the script
if __name__ == "__main__":
    input_file = input("Enter D.O.M.A.I.N Files: ")
    main(input_file)
