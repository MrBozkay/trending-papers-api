# Trending Papers API

FastAPI tabanlı araştırma paper'ları arama ve analiz API'si - Railway Cloud Deployment Ready

## 🚀 Cloud Deployment

Bu repository Railway'de deploy etmeye hazır!

### Railway Deployment Adımları

1. **GitHub Repository**: https://github.com/MrBozkay/trending-papers-api
2. **Railway.app'ta hesap oluştur**
3. **"New Project" → "Deploy from GitHub repo" seç**
4. **Repository'yi seç**: `MrBozkay/trending-papers-api`
5. **Environment Variables Set Et**:
   ```
   PORT=8000
   CORS_ORIGINS=*
   ENVIRONMENT=production
   ```
6. **Deploy Tamamla** - Railway otomatik build yapacak

### Deployment Sonrası

- **Public URL**: `https://trending-papers-api.railway.app` (örnek)
- **API Docs**: `https://your-app.railway.app/docs`
- **Health Check**: `https://your-app.railway.app/api/health`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Sağlık kontrolü |
| `/api/trending` | GET | Trending paper'lar |
| `/api/search` | POST | Paper arama |
| `/api/paper/{id}` | GET | Paper detayları |
| `/api/analyze` | POST | Paper analizi |
| `/api/similar/{id}` | GET | Benzer paper'lar |
| `/api/repositories` | GET | GitHub repository arama |
| `/api/export/search` | GET | Sonuçları export et |

## 🧪 Test Komutları

```bash
# Health check
curl https://your-app.railway.app/api/health

# Trending papers
curl https://your-app.railway.app/api/trending

# Search papers
curl -X POST https://your-app.railway.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "filters": {"max_results": 10}}'
```

## 🏗️ Architecture

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **MockMCPClient** - Mock data provider (development)
- **CORS** - Cross-origin support
- **Pydantic** - Data validation
- **Requirements.txt** - Cloud dependencies
- **Procfile** - Railway deployment config

## 🔧 Local Development

```bash
# Dependencies yükle
pip install -r requirements.txt

# Uvicorn ile çalıştır
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Veya cloud entry ile
python cloud_entry.py
```

## 📊 Features

- ✅ Real-time paper search
- ✅ ArXiv integration ready
- ✅ GitHub repository discovery
- ✅ Paper analysis and insights
- ✅ Relevance filtering
- ✅ Export functionality (JSON/CSV)
- ✅ Mock data for testing
- ✅ Cloud deployment ready
- ✅ CORS enabled
- ✅ Health check endpoints
- ✅ Comprehensive error handling

## 🔄 CI/CD

- GitHub push → Railway otomatik deploy
- Her commit için yeni build
- Environment variables auto-set

## 📄 License

MIT License

---

**🔗 GitHub**: https://github.com/MrBozkay/trending-papers-api  
**☁️ Cloud Ready**: Railway deployment configured  
**📚 API Docs**: Automatic with FastAPI Swagger UI