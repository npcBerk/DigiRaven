import wx
from pubsub import pub
from threading import Thread
from ftplib import FTP
import os





def send_status(message):
    """FTP işlem durumunu güncellemek için kullanılan fonksiyon.

       Args:
           message (str): Güncellenecek durum mesajı.
       """
    wx.CallAfter(pub.sendMessage, 'update_status', message=message)

class Path:
    """FTP sunucusundaki dosya veya dizinler için bir yol nesnesi."""
    def __init__(self, ftype, size, filename, date):
        if 'd' in ftype:
            self.folder = True
        else:
            self.folder = False
            self.size = size
            self.filename = filename
            self.last_modified = f'{date}'

class FTPThread(Thread):
    """FTP sunucusuna bağlanarak dizin içeriğini almak için kullanılan iş parçacığı sınıfı."""

    def __init__(self, ftp, folder=None):
        super().__init__()
        self.ftp = ftp
        self.folder = folder
        self.start()

    def run(self):
        """FTP sunucusundan dizin içeriğini alır ve GUI'yi günceller."""
        if self.folder:
            self.ftp.cwd(self.folder)
            message = f'Changing directory: {self.folder}'
            send_status(message)

        self.get_dir_listing()

    def get_dir_listing(self):

        """FTP sunucusundaki dizin içeriğini alır ve parse eder."""
        data = []
        contents = self.ftp.dir(data.append)
        self.parse_data(data)

    def parse_data(self, data):
        """FTP sunucusundan gelen veriyi işler ve Path nesneleri oluşturur.

             Args:
                 data (list): FTP sunucusundan gelen veri listesi.
             """
        paths = []
        for item in data:
            parts = item.split()
            ftype = parts[0]
            size = parts[4]
            filename = parts[-1]
            date = '{month} {day} {t}'.format(
                month=parts[5], day=parts[6], t=parts[7])
            if filename == '.':
                continue
            paths.append(Path(ftype, size, filename, date))

        wx.CallAfter(pub.sendMessage, 'update', paths=paths)


# Örnek Kullanım:
if __name__ == '__main__':
    # FTP bağlantısını başlat
    host = 'ftp.example.com'
    username = 'your_username'
    password = 'your_password'

    ftp = FTP(host)
    ftp.login(username, password)

    # FTPThread'i başlat
    folder = '/desired/folder/path'  # İsteğe bağlı olarak bir klasöre gitmek için
    thread = FTPThread(ftp, folder)

    # Uygulamayı çalıştır
    app = wx.App(False)  # wxPython uygulaması başlat
    app.MainLoop()  # Ana döngüyü başlat, GUI etkinleştir