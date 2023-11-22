import os
import socket
import subprocess


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.settimeout(100000)  # Устанавливаем таймаут в 10 секунд

    def open_in_notepad(self, file_path):
        try:
            subprocess.Popen(['notepad.exe', file_path])
        except FileNotFoundError:
            print("Блокнот не найден. Убедитесь, что он установлен и доступен в системном пути.")

    def send_command(self, command):
        command += "\r\n"
        encoded_command = command.encode("utf-8")  # Кодируем команду в байты
        self.client_socket.send(encoded_command)  # Отправляем команду на сервер
        print("Команда отправлена:", command)

    def receive_file_and_decrypt(self, output_file):
        with open(output_file, 'wb') as f_out:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    self.open_in_notepad(output_file)
                    break
                f_out.write(data)

                # Проверяем, достигнут ли конец файла
                if len(data) < 1024:
                    self.open_in_notepad(output_file)
                    break

        print("Файл успешно принят и расшифрован.")

    def send_file_with_command(self, file_path, password):
        file_size = os.path.getsize(file_path)
        # Формируем команду
        command = f"encrypt {os.path.basename(file_path)} {password} {file_size}\r\n"

        # Отправляем команду
        self.client_socket.send(command.encode("utf-8"))

        # Отправляем байты файла
        with open(file_path, "rb") as file:
            data = file.read()
            # while data:
            #     self.client_socket.send(data)
            #     data = file.read(1024)
            #self.client_socket.sendall(data)
            self.client_socket.send(data)

        print("Файл успешно отправлен.")

        # response = self.client_socket.recv(1024)
        # filename, file_extension = os.path.splitext(file_path)
        # output_file = filename + "v2" + file_extension
        #
        # with open(output_file, 'wb') as f_out:
        #     self.open_in_notepad(output_file)
        #     f_out.write(response)

        # Принимаем и расшифровываем файл
        output_file = "decrypted_" + os.path.basename(file_path)
        self.receive_file_and_decrypt(output_file)
        self.client_socket.send(b"")


    def receive_response(self):
        try:
            response = self.client_socket.recv(1024).decode("utf-8")   # Принимаем ответ от сервера
        except Exception as e:
            response = f"Ошибка при получении ответа от сервера: {e}"
        return response # Декодируем ответ в строку

    def close(self):
        self.client_socket.close()


if __name__ == "__main__":
    client = Client("127.0.0.1", 12345)

    # Пример отправки команды на сервер
    command = "asdfasd"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    command = "hello 4"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    command = "hello 3"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")


    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    command = "asdfasd"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    client.send_file_with_command("C:\\Users\\AAristarkhov\\PycharmProjects\\network1\\text.txt", "ваш_пароль")
    # response = client.receive_response()
    # print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    command = "bye 4"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    command = "bye 3"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    # Пример отправки команды на сервер
    command = "bye 3"
    client.send_command(command)
    # Пример получения ответа от сервера
    response = client.receive_response()
    print(f"Ответ от сервера: {response}")

    #client.close()
