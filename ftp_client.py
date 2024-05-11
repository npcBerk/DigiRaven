import os
import wx
from ftplib import FTP
from pubsub import pub
from ftp_threads import Path

def send_status(message, topic='update_status'):
    """Durum güncellemelerini yayınlar."""
    wx.CallAfter(pub.sendMessage, topic, message=message)

class FTP:
    """FTP bağlantısını yöneten sınıf."""

    def __init__(self, folder=None):
        self.folder = folder

    def connect(self, host, port, username, password):
        """FTP sunucusuna bağlanır."""
        try:
            self.ftp = FTP()
            self.ftp.connect(host, port)
            self.ftp.login(username, password)
            send_status(self.ftp.getwelcome())
            send_status('Connected', topic='update_statusbar')
            self.get_dir_listing()
        except Exception as e:
            send_status(f'Disconnected: {str(e)}', topic='update_statusbar')

    def disconnect(self):
        """FTP sunucusundan bağlantıyı keser."""
        self.ftp.quit()

    def change_directory(self, folder):
        """Sunucu üzerindeki dizini değiştirir."""
        self.ftp.cwd(folder)
        self.get_dir_listing()
        current_directory = self.ftp.pwd()
        send_status(f'Changed directory to {current_directory}')

    def get_dir_listing(self):
        """Dizin listesini alır."""
        if self.ftp:
            data = []
            self.ftp.dir(data.append)
            self.parse_data(data)

    def parse_data(self, data):
        """Dizin verilerini analiz eder."""
        paths = []
        for item in data:
            parts = item.split()
            ftype = parts[0]
            size = parts[4]
            if len(parts) > 9:
                filename = ' '.join(parts[8:])
            else:
                filename = parts[8]
            date = '{month} {day} {t}'.format(
                month=parts[5], day=parts[6], t=parts[7])
            if filename == '.':
                continue
            paths.append(Path(ftype, size, filename, date))

        wx.CallAfter(pub.sendMessage, 'update', paths=paths)

    def delete_file(self, filename):
        """Dosyayı siler."""
        try:
            self.ftp.delete(filename)
            send_status(f'{filename} deleted successfully')
            self.get_dir_listing()
        except Exception as e:
            send_status(f'Unable to delete {filename}: {str(e)}')

    def download_files(self, paths, local_folder):
        """Dosyaları indirir."""
        for path in paths:
            try:
                full_path = os.path.join(local_folder, path)
                with open(full_path, 'wb') as local_file:
                    self.ftp.retrbinary('RETR ' + path, local_file.write)
                    message = f'Downloaded: {path}'
                    send_status(message)
            except Exception as e:
                send_status(f'Error downloading {path}: {str(e)}')

    def upload_files(self, paths):
        """Dosyaları sunucuya yükler."""
        txt_files = [".txt", ".htm", ".html"]
        for path in paths:
            _, ext = os.path.splitext(path)
            if ext in txt_files:
                with open(path) as fobj:
                    self.ftp.storlines('STOR ' + os.path.basename(path), fobj)
            else:
                with open(path, 'rb') as fobj:
                    self.ftp.storbinary('STOR ' + os.path.basename(path), fobj, 1024)
            send_status(f'Uploaded {path}')
        count = len(paths)
        send_status(f'{count} file(s) uploaded successfully')
        self.get_dir_listing()

class FTPDialog(wx.Frame):
    """FTP istemcisini gösteren pencere sınıfı."""

    def __init__(self, parent, title):
        super(FTPDialog, self).__init__(parent, title=title, size=(400, 400))

        # Ana panel oluştur
        panel = wx.Panel(self)
        # Sizer oluştur
        sizer = wx.BoxSizer(wx.VERTICAL)
        logo_path = "digi.png"
        image = wx.Image(logo_path, wx.BITMAP_TYPE_ANY)
        image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
        wx_image = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(image))
        sizer.Add(wx_image, 0, wx.CENTER)

        # Bağlantı bilgileri için alanlar
        host_label = wx.StaticText(panel, label="Host:")
        self.host_text = wx.TextCtrl(panel, value="example.com")

        username_label = wx.StaticText(panel, label="Username:")
        self.username_text = wx.TextCtrl(panel, value="Enter Username")

        password_label = wx.StaticText(panel, label="Password:")
        self.password_text = wx.TextCtrl(panel, value="Enter Password", style=wx.TE_PASSWORD)

        port_label = wx.StaticText(panel, label="Port:")
        self.port_text = wx.TextCtrl(panel, value="22")

        # Bağlanma butonu
        connect_button = wx.Button(panel, label="Connect")
        connect_button.Bind(wx.EVT_BUTTON, self.on_connect)

        # Sizer'a bileşenleri ekle
        sizer.Add(host_label, 0, wx.CENTER)
        sizer.Add(self.host_text, 0, wx.CENTER)
        sizer.Add(username_label, 0, wx.CENTER)
        sizer.Add(self.username_text, 0, wx.CENTER)
        sizer.Add(password_label, 0, wx.CENTER)
        sizer.Add(self.password_text, 0, wx.CENTER)
        sizer.Add(port_label, 0, wx.CENTER)
        sizer.Add(self.port_text, 0, wx.CENTER)
        sizer.Add(connect_button, 0, wx.CENTER)

        # Panel için sizer'ı ayarla
        panel.SetSizer(sizer)

        # Pencereyi göster
        self.Show()

    def on_connect(self, event):
        """Bağlantıyı kurar ve FTP işlemlerini gerçekleştirir."""
        # Bağlantı bilgilerini al
        host = self.host_text.GetValue()
        username = self.username_text.GetValue()
        password = self.password_text.GetValue()
        port_str = self.port_text.GetValue()

        # Port değerini kontrol et ve uygun bir şekilde işle
        if port_str.strip():  # Port değeri boş olmadığından emin ol
            try:
                port = int(port_str)  # Port değerini integer'a çevir
                if 0 < port <= 65535:  # Geçerli bir port aralığında olduğundan emin ol
                    self.SetStatusText('Connecting...', 1)
                    self.ftp = FTP()
                    try:
                        self.ftp.connect(host, port)
                        self.ftp.login(username, password)
                        self.SetStatusText('Connected', 1)
                        print("FTP connection successful!")
                        # Bağlantı başarılıysa burada yapılacak işlemleri gerçekleştirin
                    except Exception as e:
                        self.SetStatusText('Connection failed', 1)
                        print(f"Bağlantı hatası: {str(e)}")
                else:
                    self.SetStatusText('Invalid port', 1)
            except ValueError:
                self.SetStatusText('Invalid port', 1)
        else:
            self.SetStatusText('Port is empty', 1)

if __name__ == "__main__":
    app = wx.App()
    dialog = FTPDialog(None, title="FTP Client")
    app.MainLoop()
