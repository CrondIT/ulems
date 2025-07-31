posgres 5433
postgres Snn296_pgs
db_ulems db_ulems_user Snn314_ulms

2. Выбор интерпретатора в VS Code:
Откройте VS Code и перейдите в папку вашего проекта.
Нажмите Ctrl+Shift+P (или Cmd+Shift+P на macOS) и начните вводить "Python: Select Interpreter".
Выберите пункт "Python: Select Interpreter".
Выберите пункт "Enter interpreter path".
Укажите полный путь к python.exe внутри папки вашего виртуального окружения (например, C:\Users\ВашПользователь\MyProject\myenv\Scripts\python.exe).


Ошибка:
.\venv\Scripts\activate : Невозможно загрузить файл C:\path\venv\Scripts\activate.ps1, так как выполнение сценариев отключено в этой системе. 
Для получения дополнительных сведений см. about_Execution_Policies по адресу http://go.microsoft.com/fwlink/?LinkID=135170.
строка:1 знак:1
.\venv\Scripts\activate
~~~~~~~~~~~~~~~~~~~~~~~
CategoryInfo          : Ошибка безопасности: (:) [], PSSecurityException
FullyQualifiedErrorId : UnauthorizedAccess

Решение проблемы:
- Открываем терминал PowerShell от админа.
- Вставляем и запускаем - Set-ExecutionPolicy RemoteSigned
- На вопрос отвечаем - A