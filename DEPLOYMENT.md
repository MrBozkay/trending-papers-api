# Trending Papers API - Cloud Deployment

FastAPI tabanlı araştırma paper'ları arama ve analiz API'si.

## 🚀 Cloud Deployment

### Railway Deployment (UPDATED)

Railway build hatasını çözmek için gerekli konfigürasyonlar eklenmiştir:

#### ✅ Gerekli Dosyalar Kontrolü
- ✅ `pyproject.toml` - Python build dependencies
- ✅ `nixpacks.toml` - System packages for Railway
- ✅ `Procfile` - Process definition
- ✅ `requirements.txt` - Python dependencies

#### 1. **GitHub Repository Oluştur/Güncelle**
   ```bash
   git init
   git add .
   git commit -m "Fixed Railway deployment: Added pyproject.toml and nixpacks.toml"
   git branch -M main
   git remote add origin https://github.com/MrBozkay/trending-papers-api.git
   git push -u origin main
   ```

#### 2. **Railway'de Deploy Et**
   - Railway.app'ta hesap oluştur/giriş yap
   - "New Project" → "Deploy from GitHub repo" seç
   - `MrBozkay/trending-papers-api` repository'yi seç ve deploy et
   - **BUILD ERROR ÇÖZÜLDİ**: `nixpacks.toml` ve `pyproject.toml` ile sistem bağımlılıkları eklendi

#### 3. **Environment Variables Set Et**
   ```
   PORT=8000
   CORS_ORIGINS=*
   ENVIRONMENT=production
   ```

#### 4. **Deploy Tamamla**
   - Railway otomatik build yapacak (sistem paketleri ile)
   - Public URL alacaksınız: `https://your-app.railway.app`

### 🧪 Local API Test (Port 8001'de Çalışıyor)

```bash
# Backend test server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Health check
curl http://localhost:8001/api/health

# Trending papers
curl http://localhost:8001/api/trending

# Search papers
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "filters": {"max_results": 10}}'

# Paper detayları
curl http://localhost:8001/api/paper/arxiv:2301.00001

# Benzer paper'lar
curl http://localhost:8001/api/similar/arxiv:2301.00001

# GitHub repository arama
curl http://localhost:8001/api/repositories?query=machine+learning

# Export sonuçları
curl http://localhost:8001/api/export/search?format=json
```

## 📡 API Endpoints

- `GET /api/health` - Sağlık kontrolü
- `GET /api/trending` - Trending paper'lar
- `POST /api/search` - Paper arama
- `GET /api/paper/{id}` - Paper detayları
- `POST /api/analyze` - Paper analizi
- `GET /api/similar/{id}` - Benzer paper'lar
- `GET /api/repositories` - GitHub repository arama
- `GET /api/export/search` - Sonuçları export et

## 🏗️ Build Hatası Çözümü

**Önceki Hata:**
```
error: failed-wheel-build-for-install
× Failed to build installable wheels for some pyproject.toml based projects
╰─> lxml, pydantic-core
```

**Çözüm:**
1. `nixpacks.toml` - Railway build environment'ına sistem paketleri ekler
2. `pyproject.toml` - Python build dependencies belirtir
3. Sistem paketleri: `build-essential`, `python3-dev`, `libxml2-dev`, `libxslt1-dev`, `pkg-config`

## 📚 API Documentation

- Swagger UI: `https://your-app.railway.app/docs`
- ReDoc: `https://your-app.railway.app/redoc`

## 🏗️ Architecture

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **MockMCPClient** - Mock data provider
- **CORS** - Cross-origin support for web apps

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use run script
python run.py
```

## 📝 Configuration

Environment variables:
- `PORT` - Server port (default: 8000)
- `CORS_ORIGINS` - CORS allowed origins (default: *)
- `ENVIRONMENT` - Environment name

## 🔄 CI/CD

GitHub push'larında Railway otomatik deploy yapar.
Her commit için yeni build ve deploy tetiklenir.

## 🔧 Troubleshooting

### Railway Build Hatası
Eğer hala build hatası alırsanız:
1. Railway dashboard → Build Logs'u kontrol edin
2. `nixpacks.toml` dosyasının doğru şekilde parse edildiğinden emin olun
3. Gerekirse Railway support ile iletişime geçin

### Local Development
```bash
# Test specific endpoint
curl -v http://localhost:8001/api/health

# Check all available endpoints
curl http://localhost:8001/docs
```

## 📄 License

MIT License