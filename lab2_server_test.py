import hashlib
import socket
import threading

class AdditiveGenerator:
    def __init__(self, seed):
        self.state = seed

    def generate(self, size):
        result = b""
        for _ in range(size):
            self.state = (self.state * 1103515245 + 12345) & 0xFFFFFFFF
            result += bytes([self.state & 0xFF])
        return result

class Server:
    def __init__(self, host, port):
        self.variant = 3
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.registered_clients = set()  # Множество зарегистрированных клиентов
        print(f"Сервер слушает на {self.host}:{self.port}")

    def hash_password_md4(self, password):
        password_bytes = password.encode('utf-8')
        md4_hash = hashlib.new('md4')
        md4_hash.update(password_bytes)
        print(md4_hash.hexdigest())
        return md4_hash.digest()

    def encrypt_decrypt_file(self, data, password):
        key = self.hash_password_md4(password)
        generator = AdditiveGenerator(int.from_bytes(key, byteorder='big'))

        encrypted_data = bytes(x ^ y for x, y in zip(data, generator.generate(len(data))))

        return encrypted_data

    def handle_client(self, client_socket):
        try:
            buffer = b""  # Буфер для неполных данных
            while True:
                data = client_socket.recv(1024)
                print(data)
                if not data:
                    break  # Если нет данных, выходим из цикла

                buffer += data
                commands = buffer.decode("utf-8").split('\r\n')  # Разделяем команды по символу новой строки

                for command in commands[:-1]:  # Итерируем по всем командам, кроме последней (неполной)
                    self.process_command(client_socket, command.strip())
                buffer = commands[-1].encode("utf-8")  # Сохраняем последнюю (неполную) команду в буфере

        except Exception as e:
            print(f"Ошибка обработки команды: {e}")
        # finally:
        #     if client_socket in self.registered_clients:
        #         self.registered_clients.remove(client_socket)
        #     client_socket.close()

    def send_encrypted_data(self, data, client_socket):
        chunk_size = 1024
        offset = 0

        while offset < len(data):
            chunk = data[offset:offset + chunk_size]
            client_socket.send(chunk)
            offset += chunk_size

    def process_command(self, client_socket, command):
        print(f"Получена команда от клиента: {command}")

        # Разбиваем команду на части
        parts = command.split()
        # Проверяем, является ли команда "hello" и содержит ли она число
        if len(parts) == 2 and parts[0].lower() == "hello" and parts[1].isdigit():
            number = int(parts[1])
            if number == self.variant:
                if client_socket not in self.registered_clients:
                    self.registered_clients.add(client_socket)
                    response = f"hello variant {self.variant}"
                    client_socket.send(response.encode("utf-8"))
                else:
                    response = "Клиент уже зарегистрирован."
                    client_socket.send(response.encode("utf-8"))
            else:
                response = "Регистрация отклонена, указан неккоректный вариант."
                client_socket.send(response.encode("utf-8"))
        elif client_socket in self.registered_clients:

            if len(parts) == 2 and parts[0].lower() == "bye" and parts[1].isdigit():
                number = int(parts[1])
                if number == self.variant:
                    if client_socket not in self.registered_clients:
                        self.registered_clients.add(client_socket)
                        response = "Клиент не был зарегистрирован."
                        client_socket.send(response.encode("utf-8"))
                    else:
                        response = f"bye {self.variant}"
                        client_socket.send(response.encode("utf-8"))
                        self.registered_clients.remove(client_socket)
                        # client_socket.close()
                else:
                    response = "Запрос отклонен, указан неккоректный вариант."
                    client_socket.send(response.encode("utf-8"))

            elif parts[0].lower() == "encrypt" or parts[0].lower() == "decrypt":
                if len(parts) == 4:
                    file_name = parts[1]
                    password = parts[2]
                    file_size = int(parts[3])
                    print(file_name, password, file_size)

                    # Получаем байты файла
                    received_data = b""
                    while len(received_data) < file_size:
                        data = client_socket.recv(1024)
                        received_data += data

                    # Расшифровываем файл
                    decrypted_data = self.encrypt_decrypt_file(received_data, password)
                    # crypted_data = self.encrypt_decrypt_file(received_data, password)
                    self.send_encrypted_data(decrypted_data, client_socket)
                    # client_socket.send(crypted_data)
                    # Сохраняем расшифрованный файл
                    # with open(file_name, "wb") as file:
                    #     file.write(crypted_data)

                    # response = "Файл успешно преобразован и отправлен."
                    # client_socket.send(response.encode("utf-8"))
                    # print(response)
                else:
                    response = "Запрос составлен неправильно."
                    client_socket.send(response.encode("utf-8"))


            else:
                response = "Неизвестная команда."
                client_socket.send(response.encode("utf-8"))

        else:
            response = "Неизвестная команда. Клиент не зарегистрирован."
            client_socket.send(response.encode("utf-8"))


    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            response = f"Принято соединение от {addr[0]}:{addr[1]}"
            print(f"Принято соединение от {addr[0]}:{addr[1]}")
            client_socket.send(response.encode("utf-8"))
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()


if __name__ == "__main__":
    server = Server("127.0.0.1", 12345)
    server.start()
