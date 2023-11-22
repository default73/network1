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
            while True:
                data = client_socket.recv(1024)  # Принимаем данные от клиента
                if not data:
                    break  # Если нет данных, выходим из цикла
                command = data.decode("utf-8").strip()  # Декодируем и очищаем от лишних пробелов
                print(f"Получена команда от клиента: {command}")

                # Разбиваем команду на части
                parts = command.split()
                # Проверяем, является ли команда "hello" и содержит ли она число
                if len(parts) == 2 and parts[0].lower() == "hello" and parts[1].isdigit():
                    number = int(parts[1])
                    if number == self.variant:
                        if client_socket not in self.registered_clients:
                            self.registered_clients.add(client_socket)
                            response = "Клиент успешно зарегистрирован."
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
                                client_socket.close()
                        else:
                            response = "Запрос отклонен, указан неккоректный вариант."
                            client_socket.send(response.encode("utf-8"))

                    elif parts[0].lower() == "encrypt" or parts[0].lower() == "decrypt":
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
                        #decrypted_data = self.decrypt_file(received_data, password)
                        crypted_data = self.encrypt_decrypt_file(received_data, password)
                        client_socket.send(crypted_data)
                        # Сохраняем расшифрованный файл
                        # with open(file_name, "wb") as file:
                        #     file.write(crypted_data)

                        # response = "Файл успешно преобразован и отправлен."
                        # client_socket.send(response.encode("utf-8"))
                        # print(response)


                    else:
                        response = "Неизвестная команда."
                        client_socket.send(response.encode("utf-8"))

                else:
                    response = "Неизвестная команда. Клиент не зарегистрирован."
                    client_socket.send(response.encode("utf-8"))
        except Exception as e:
            print(f"Ошибка обработки команды: {e}")
        finally:
            if client_socket in self.registered_clients:
                self.registered_clients.remove(client_socket)
            client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Принято соединение от {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()


if __name__ == "__main__":
    server = Server("127.0.0.1", 12345)
    server.start()
