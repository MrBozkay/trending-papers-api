# Trending Papers API

FastAPI tabanlı araştırma paper'ları arama ve analiz API'si.

## 🚀 Cloud Deployment Ready

Bu repository Railway'de deploy etmeye hazır.

## 📡 API Endpoints

- `GET /api/health` - Sağlık kontrolü
- `GET /api/trending` - Trending paper'lar
- `POST /api/search` - Paper arama
- `GET /api/paper/{id}` - Paper detayları
- `POST /api/analyze` - Paper analizi
- `GET /api/similar/{id}` - Benzer paper'lar
- `GET /api/repositories` - GitHub repository arama
- `GET /api/export/search` - Sonuçları export et

## 🏗️ Architecture

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **MockMCPClient** - Mock data provider
- **CORS** - Cross-origin support for web apps

## 📄 License

MIT License