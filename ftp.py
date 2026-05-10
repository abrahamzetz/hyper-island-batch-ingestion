import ftplib
import os

HOST = "ftp.dewa.nu"
USER = os.environ["DEWA_FTP_USER"]
PASSWORD = os.environ["DEWA_FTP_PASSWORD"]
REMOTE_DIR = "/orders"

ftp = ftplib.FTP(HOST)
ftp.login(USER, PASSWORD)
ftp.cwd(REMOTE_DIR)

files = ftp.nlst()
latest = sorted(files)[-1]

filename = f"data/{latest}"

os.makedirs("data", exist_ok=True)
with open(filename, "wb") as f:
    ftp.retrbinary(f"RETR {latest}", f.write)

ftp.quit()
print(f"Saved {filename}")
