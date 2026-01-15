# 🚀 Quick Start Guide: GoRules BRE Platform

Start the entire Business Rule Engine platform—including the Backend, Database, and Visual Rule Editor—with a single command.

## 📋 Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine (Linux)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## 💻 Windows (PowerShell)

### Option 1: Automated Script (Recommended)
This script checks prerequisites, sets up the environment, and starts all services.
```powershell
.\start-simple.ps1
```

### Option 2: Pure Docker Command
```powershell
docker-compose -f docker-compose.simple.yml up -d
```

---

## 🐧 Linux / 🍎 macOS (Terminal)

### Option 1: Automated Script (Recommended)
```bash
chmod +x start-simple.sh
./start-simple.sh
```

### Option 2: Pure Docker Command
```bash
docker-compose -f docker-compose.simple.yml up -d
```

---

## 🌐 Accessing Services

Once started, you can access the following services:

| Service | URL | Description |
| :--- | :--- | :--- |
| **Visual Rule Editor** | [http://localhost:3000](http://localhost:3000) | Dashboard & Decision Table Editor |
| **API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger/OpenAPI docs |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | System status endpoint |

---

## 🛠️ Useful Commands

- **View Logs**: `docker-compose -f docker-compose.simple.yml logs -f`
- **Stop All**: `docker-compose -f docker-compose.simple.yml down`
- **Restart**: `docker-compose -f docker-compose.simple.yml restart`
- **Reset Everything**: `docker-compose -f docker-compose.simple.yml down -v` (Deletes DB data)

---

## 📖 Further Documentation
- [Rule Editor Guide](docs/EDITOR_SETUP.md)
- [KYC Testing Guide](docs/kyc_rule_guide.md)
