# ShareIt - He thong quan ly muon do noi bo

Ung dung Django cho xom tro/van phong/cau lac bo de dang mon do va cho muon noi bo.

## Tinh nang

- Quan ly mon do va trang thai `San sang` / `Dang cho muon`.
- Lich muon theo ngay bat dau - ngay tra (DatePicker trong form Django).
- Yeu cau muon co quy trinh `Cho duyet`, `Da duyet`, `Tu choi`, `Da tra`.
- Tin nhan noi bo theo tung luot muon de hen gio nhan/tra do.

## Cai dat

1. Tao virtualenv va kich hoat.
2. Cai thu vien:

```bash
pip install -r requirements.txt
```

3. Tao migration va database:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Tao tai khoan admin:

```bash
python manage.py createsuperuser
```

5. Chay server:

```bash
python manage.py runserver
```

## Su dung nhanh

- Dang nhap va vao `Dang mon do` de tao mon do.
- Vao danh sach mon do, mo chi tiet, gui `Yeu cau muon`.
- Chu do vao chi tiet mon do de duyet/tu choi.
- Hai ben vao `Mở chat` de nhan tin hen gio nhan do.

# sharelt
