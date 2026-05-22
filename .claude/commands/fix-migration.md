# Fix lỗi Migration trên VPS (PostgreSQL có data cũ)

Dùng khi deploy gặp lỗi:
- `IntegrityError: could not create unique index` — thêm unique field vào bảng có data
- `ProgrammingError: column does not exist` — migration bị fake nhưng cột chưa được tạo
- `relation already exists` — migration chạy dở rồi bị lỗi, index/bảng còn lại

## Chẩn đoán

Hỏi người dùng: lỗi cụ thể là gì? (`IntegrityError`, `ProgrammingError`, hay `relation already exists`)

Kiểm tra trạng thái migration:
```bash
python3 manage.py showmigrations <app_name>
```

## Quy trình fix chuẩn

### Trường hợp 1: `IntegrityError` — unique field, data cũ có giá trị trùng

```bash
# 1. Thêm cột không unique trước
python3 manage.py dbshell
```
```sql
ALTER TABLE <tên_bảng> ADD COLUMN IF NOT EXISTS <cột> varchar(200) NOT NULL DEFAULT '';
\q
```
```bash
# 2. Điền data cho cột (ví dụ: slug từ title)
python3 manage.py shell -c "
from apps.<app>.models import <Model>, vi_slugify
for obj in <Model>.objects.all():
    base = vi_slugify(obj.title)
    slug = base; i = 2
    while <Model>.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
        slug = f'{base}-{i}'; i += 1
    <Model>.objects.filter(pk=obj.pk).update(slug=slug)
print('Done')
"
# 3. Thêm unique constraint
python3 manage.py dbshell
```
```sql
ALTER TABLE <tên_bảng> ADD CONSTRAINT <tên>_unique UNIQUE (<cột>);
\q
```
```bash
# 4. Fake migration rồi chạy tiếp
python3 manage.py migrate <app> <số_migration> --fake
python3 manage.py migrate
```

### Trường hợp 2: `ProgrammingError: column does not exist`

Migration đã bị fake nhưng cột chưa tồn tại trong DB. Thêm thủ công rồi restart:

```bash
python3 manage.py dbshell
```
```sql
-- Thêm từng cột còn thiếu
ALTER TABLE <tên_bảng> ADD COLUMN IF NOT EXISTS <cột1> <kiểu> NOT NULL DEFAULT <default>;
ALTER TABLE <tên_bảng> ADD COLUMN IF NOT EXISTS <cột2> <kiểu>;
\q
```
```bash
sudo systemctl restart adcare.service
```

### Trường hợp 3: `relation already exists` — index còn lại từ lần chạy hỏng

```bash
python3 manage.py dbshell
```
```sql
DROP INDEX IF EXISTS <tên_index>;
\q
```
```bash
python3 manage.py migrate
```

## Kiểu dữ liệu PostgreSQL thường dùng

| Django field | PostgreSQL type |
|---|---|
| `CharField(max_length=200)` | `varchar(200) NOT NULL DEFAULT ''` |
| `TextField` | `text NOT NULL DEFAULT ''` |
| `BooleanField(default=False)` | `boolean NOT NULL DEFAULT false` |
| `PositiveSmallIntegerField(default=0)` | `smallint NOT NULL DEFAULT 0` |
| `ForeignKey(null=True)` | `integer` (nullable, không cần DEFAULT) |

## Sau khi fix

```bash
python3 manage.py check
sudo systemctl restart adcare.service
# Kiểm tra https://adcare.vn hoạt động
```
