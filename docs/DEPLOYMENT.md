# Deployment Guide

## Sistem Pengaduan Mahasiswa UIR Berbasis RAG

---

## Prerequisites

1. **MongoDB Atlas Cluster**
   - Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a database user
   - Whitelist IP `0.0.0.0/0` for initial setup (restrict later)

2. **OpenAI API Key**
   - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Ensure you have credits available

3. **Server with Docker** (for production)
   - Ubuntu 20.04+ recommended
   - Docker and Docker Compose installed

---

## Local Development Deployment

### Step 1: Clone and Setup

```bash
git clone <repository-url>
cd "SEMESTER 6/IMPLEMENTASI PRANGKAT LUNAK"
cd backend
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
DEBUG=True
MONGODB_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/uir_complaints
MONGODB_DB_NAME=uir_complaints
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=generate-a-secure-random-string
```

### Step 5: Run MongoDB Index Setup (One-time)

The application automatically creates indexes on startup. Make sure MongoDB is accessible first.

### Step 6: Start Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Create Initial Admin

Access `/docs` and use the register endpoint, or create admin manually via MongoDB shell:

```javascript
// Connect to MongoDB Atlas
db.users.insertOne({
  email: "admin@uir.ac.id",
  name: "System Admin",
  password_hash: "$2b$12$...", // bcrypt hash of password
  role: "admin",
  npm: null,
  is_active: true,
  created_at: new Date(),
  updated_at: new Date()
})
```

---

## Docker Deployment

### Step 1: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
DEBUG=False
MONGODB_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/uir_complaints
MONGODB_DB_NAME=uir_complaints
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=generate-a-secure-random-string
```

### Step 2: Build and Run

```bash
docker-compose up --build -d
```

### Step 3: Check Logs

```bash
docker-compose logs -f backend
```

### Step 4: Verify

```bash
curl http://localhost:8000/health
```

---

## Cloud Deployment Options

### Option 1: Railway

1. Connect GitHub repository
2. Add environment variables
3. Deploy

### Option 2: Render

1. Create Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Option 3: VPS (Ubuntu 20.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <repo-url>
cd "SEMESTER 6/IMPLEMENTASI PRANGKAT LUNAK"
cp .env.example .env
# Edit .env with production values
docker-compose up -d
```

### Option 4: Google Cloud Run

1. Build container:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/uir-complaints
   ```

2. Deploy:
   ```bash
   gcloud run deploy uir-complaints --image gcr.io/PROJECT_ID/uir-complaints --platform managed
   ```

---

## Production Checklist

### Security

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Use HTTPS
- [ ] Restrict MongoDB IP access
- [ ] Enable MongoDB authentication

### Performance

- [ ] Set up MongoDB Atlas autoscaling
- [ ] Configure proper indexes
- [ ] Enable response caching
- [ ] Use CDN for static assets (frontend)

### Monitoring

- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Configure alerts

### Backup

- [ ] Enable MongoDB Atlas backup
- [ ] Test backup restoration
- [ ] Document recovery procedures

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEBUG` | Debug mode | No | `False` |
| `SECRET_KEY` | JWT signing key | Yes | - |
| `MONGODB_URL` | MongoDB connection string | Yes | - |
| `MONGODB_DB_NAME` | Database name | Yes | `uir_complaints` |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | GPT model | No | `gpt-4o` |
| `EMBEDDING_MODEL` | Embedding model | No | `text-embedding-3-small` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | No | `1440` |

---

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB Atlas connectivity
mongosh "mongodb+srv://<connection-string>"
```

### OpenAI API Issues

```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Docker Issues

```bash
# Check container logs
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache

# Remove and restart
docker-compose down -v
docker-compose up -d
```

---

## Scaling

### Horizontal Scaling

The backend is stateless and can be scaled horizontally behind a load balancer.

```yaml
# docker-compose.yml modification
services:
  backend:
    deploy:
      replicas: 3
```

### MongoDB Atlas Scaling

- Start with M0 (free tier)
- Upgrade to M10/M20 as needed
- Enable auto-scaling

---

## Support

For issues, please create an issue in the repository or contact the development team.
