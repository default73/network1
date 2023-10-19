import subprocess

# Команда, которую вы хотите выполнить
command = "ping ya.ru"

# Выполнение команды с использованием cmd.exe
process = subprocess.Popen(['cmd.exe', '/c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Ждем, пока команда завершит выполнение
output, error = process.communicate()

# Вывод результатов
if process.returncode == 0:
    print("Команда выполнена успешно")
    print("Результат выполнения команды:")
    print(output)
else:
    print("Произошла ошибка при выполнении команды")
    print("Сообщение об ошибке:")
    print(error)
