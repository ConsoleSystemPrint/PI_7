import socket
from urllib.parse import urlparse


class PI_7:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        print(f'Слушаю {self.host}:{self.port}')

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f'Принятое соединение от {addr}')
            self.handle_client(client_socket)

    def handle_client(self, client_socket):
        request = client_socket.recv(4096)
        if not request:
            client_socket.close()
            return

        headers = request.decode().split('\n')
        if headers:
            first_line = headers[0].strip()
            method, url, _ = first_line.split(' ')
            parsed_url = urlparse(url)
            target_host = parsed_url.hostname
            target_port = 80 if parsed_url.port is None else parsed_url.port

            try:
                proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                proxy_socket.connect((target_host, target_port))
                proxy_socket.send(request)

                while True:
                    data = proxy_socket.recv(4096)
                    if len(data):
                        if "e1.ru" in target_host or "vk.com" in target_host:
                            data = self.filter_data(data)
                        client_socket.send(data)
                    else:
                        break
                proxy_socket.close()
                client_socket.close()
            except socket.error as e:
                print(f"Ошибка при подключении к {target_host}:{target_port} - {e}")
                client_socket.close()

    def filter_data(self, data):
        filtered_data = data.replace(b"<script", b"<!--<script").replace(b"</script>", b"</script>-->")
        return filtered_data

    def stop(self):
        self.server_socket.close()


if __name__ == '__main__':
    proxy = PI_7()
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
        print('Прокси-сервер остановлен')