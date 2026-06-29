# Sistem Pengaduan Mahasiswa Universitas Islam Riau Berbasis RAG

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/fastapi-0.109.0-red)
![MongoDB](https://img.shields.io/badge/mongodb-atlas-green)

Sistem Pengaduan Mahasiswa Universitas Islam Riau Berbasis Retrieval-Augmented Generation (RAG) adalah aplikasi berbasis web yang dirancang untuk memfasilitasi mahasiswa dalam menyampaikan pengaduan secara terpusat dengan bantuan Artificial Intelligence untuk analisis dan klasifikasi.

##  Fitur Utama

- **Penyampaian Pengaduan Terpusat** - Media terpusat bagi mahasiswa untuk menyampaikan pengaduan
- **Dashboard Admin** - Pengelolaan seluruh pengaduan dalam satu dashboard
- **Analisis AI Berbasis RAG** - Automatic classification dan analysis menggunakan dokumen resmi universitas
- **Rekomendasi Otomatis** - Kategori, prioritas, unit tujuan, dan ringkasan
- **Tracking Status** - Pantau status pengaduan dari awal hingga selesai
- **Analytics Dashboard** - Statistik dan visualisasi data pengaduan

## 🛠️ Tech Stack

### Backend

- **Python 3.11+**
- **FastAPI** - REST API Framework
- **MongoDB Atlas** - Primary Database + Vector Search
- **OpenAI API** - LLM untuk RAG Analysis
- **Pydantic** - Data Validation

### Frontend (Coming Soon)

- **React.js / Vue.js**
- **TailwindCSS**

##  Prerequisites

1. **Python 3.11+**
2. **MongoDB Atlas Account** ([Sign up here](https://www.mongodb.com/cloud/atlas))
3. **OpenAI API Key** ([Get key here](https://platform.openai.com/api-keys))

##  Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd "SEMESTER 6/IMPLEMENTASI PRANGKAT LUNAK"
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# MONGODB_URL=mongodb+srv://...
# OPENAI_API_KEY=sk-...
# SECRET_KEY=your-secret-key
```

### 4. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

##  Running with Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── database.py      # MongoDB connection
│   │   └── security.py      # JWT & auth
│   ├── auth/                # Authentication module
│   ├── complaints/          # Complaints module
│   │   ├── rag_engine.py    # RAG implementation
│   │   └── ...
│   ├── documents/           # Knowledge base module
│   └── analytics/           # Analytics module
├── tests/                   # Unit tests
├── requirements.txt
├── Dockerfile
└── .env.example

frontend/                    # Coming soon
├── src/
├── package.json
└── ...

docs/
├── PRD.md                   # Product Requirement Document
└── SAD.md                   # System Analysis and Design

docker-compose.yml
README.md
```

## 🔐 API Endpoints

### Authentication

| Method | Endpoint             | Description      |
| ------ | -------------------- | ---------------- |
| POST   | `/api/auth/register` | Register student |
| POST   | `/api/auth/login`    | Login            |
| GET    | `/api/auth/me`       | Get current user |

### Complaints

| Method | Endpoint               | Description          |
| ------ | ---------------------- | -------------------- |
| POST   | `/api/complaints`      | Submit complaint     |
| GET    | `/api/complaints`      | Get my complaints    |
| GET    | `/api/complaints/{id}` | Get complaint detail |

### Admin Complaints

| Method | Endpoint                                | Description        |
| ------ | --------------------------------------- | ------------------ |
| GET    | `/api/complaints/admin/all`             | Get all complaints |
| PUT    | `/api/admin/complaints/{id}`            | Update complaint   |
| PUT    | `/api/admin/complaints/{id}/status`     | Update status      |
| POST   | `/api/admin/complaints/{id}/re-analyze` | Re-run RAG         |

### Documents (Admin)

| Method | Endpoint                      | Description     |
| ------ | ----------------------------- | --------------- |
| POST   | `/api/admin/documents`        | Create document |
| GET    | `/api/admin/documents`        | List documents  |
| POST   | `/api/admin/documents/upload` | Upload file     |

### Analytics (Admin)

| Method | Endpoint                          | Description     |
| ------ | --------------------------------- | --------------- |
| GET    | `/api/admin/analytics/overview`   | Dashboard stats |
| GET    | `/api/admin/analytics/trends`     | Trends data     |
| GET    | `/api/admin/analytics/categories` | Category stats  |

##  Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## 📚 RAG Knowledge Base

Sistem ini menggunakan dokumen resmi universitas sebagai referensi:

- SOP Akademik
- SOP Administrasi
- Struktur Organisasi
- Pembagian Tugas Unit
- Panduan Layanan Mahasiswa
- Peraturan Kampus

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (mahasiswa/admin)
- Input validation with Pydantic
- CORS protection

## 📊 Output Analisis RAG

```json
{
  "category": "Fasilitas Kampus",
  "priority": "medium",
  "summary": "Mahasiswa mengeluhkan kondisi AC...",
  "recommended_unit": "Bagian Maintenance",
  "reason": "Berdasarkan SOP Pengelolaan...",
  "confidence_score": 0.87
}
```

## 👥 Roles

### Mahasiswa

- Submit pengaduan
- Lihat riwayat pengaduan
- Pantau status pengaduan

### Admin

- Kelola semua pengaduan
- Update status dan disposisi
- Upload dokumen knowledge base
- View analytics dashboard

##  License

This project is for academic purposes - Universitas Islam Riau.

##  Author

Developed as part of Software Implementation course.

##  Acknowledgments

- Universitas Islam Riau
- Dosen Pembimbing
- OpenAI for GPT-4o API
- MongoDB Atlas
