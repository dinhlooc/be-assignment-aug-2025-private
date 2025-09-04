# Task Management Backend

Task Management Backend là một dự án được xây dựng với **FastAPI**, hỗ trợ quản lý người dùng, tổ chức, dự án, nhiệm vụ và báo cáo.  
Kiến trúc hệ thống gồm nhiều service (Auth, User, Project, Task, Notification, Report, …) được tổ chức theo **clean architecture** và chạy trong container.

![Architecture](docs/architecture.png)

---

## 🚀 Yêu cầu hệ thống

- Python >= 3.10
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Just](https://github.com/casey/just) (task runner thay cho Makefile)

---

## 🔧 Cài đặt & Chạy dự án

### 1. Clone repository

```bash
git clone https://github.com/your-username/task-management-backend.git
cd task-management-backend
```

### 2. Build Docker image

```bash
just docker-build
```

### 3. Chạy container

```bash
just docker-run
```

Ứng dụng sẽ chạy tại:

- Nginx Proxy: [http://localhost](http://localhost)
- FastAPI Service trực tiếp: [http://localhost:8000](http://localhost:8000)

### 4. Khởi tạo database

```bash
just docker-db-setup
```

### 5. Seed dữ liệu mẫu

```bash
just docker-db-seed
```

---

## ⚙️ Các lệnh hữu ích với `just`

- Chạy app local (không Docker):

  ```bash
  just run
  ```

- Chạy test:

  ```bash
  just test
  ```

- Format code:

  ```bash
  just format
  ```

- Migration database:

  ```bash
  just db-migrate message="init migration"
  just db-upgrade
  ```

---

## 🧪 Kiểm tra API

Sau khi chạy xong container, có thể test API qua **Swagger UI**:

- Thông qua **Nginx Proxy**  
  👉 [http://localhost/docs#/](http://localhost/docs#/)

- Thông qua **FastAPI trực tiếp**  
  👉 [http://localhost:8000/docs#/](http://localhost:8000/docs#/)

---

## 📂 Cấu trúc chính

```
.
├── app/                # Source code FastAPI
├── scripts/            # Script setup, seed DB
├── tests/              # Unit & integration tests
├── docker-compose.yml
├── Justfile
└── README.md
```

---

## 📝 License

MIT License. Xem chi tiết tại [LICENSE](LICENSE).
