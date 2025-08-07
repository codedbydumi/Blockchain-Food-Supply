# 🌱 FoodChain Tracker

<div align="center">

![FoodChain Tracker Logo](https://img.shields.io/badge/🌱-FoodChain%20Tracker-16a34a?style=for-the-badge&logoColor=white)

**Blockchain-Powered Supply Chain Transparency**

*Track your food's journey from farm to fork using secure blockchain technology*

[![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Blockchain](https://img.shields.io/badge/Blockchain-Enabled-16a34a?style=flat-square&logo=bitcoin&logoColor=white)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

[🚀 Live Demo](https://foodchain.duminduthushan.com/) • [📖 Documentation](#features) • [🐛 Report Bug](../../issues) • [✨ Request Feature](../../issues)

</div>

---

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [📱 Usage](#-usage)
- [🔗 API Documentation](#-api-documentation)
- [🎨 UI/UX](#-uiux)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)


---

## 🌟 Overview

**FoodChain Tracker** is a cutting-edge blockchain-powered supply chain management system that ensures complete transparency and traceability in the food industry. From farm to fork, every step of your food's journey is securely recorded on an immutable blockchain, providing unprecedented visibility into food safety, quality, and authenticity.

### 🎯 Mission
Revolutionize food safety and supply chain transparency through blockchain technology, empowering consumers with complete visibility into their food's journey while helping businesses build trust and ensure compliance.

### 🌍 Impact
- **Food Safety**: Rapid contamination source identification
- **Transparency**: Complete supply chain visibility
- **Trust**: Immutable blockchain verification
- **Sustainability**: Environmental impact tracking
- **Compliance**: Automated regulatory adherence

---

## ✨ Features

### 🔐 Blockchain Core
- **Immutable Records**: Tamper-proof transaction history
- **Smart Contracts**: Automated compliance and quality triggers
- **Cryptographic Security**: End-to-end data protection
- **Consensus Mechanism**: Distributed network validation
- **Multi-chain Support**: Ethereum, Polygon compatibility

### 👥 Multi-Role System
- **🚜 Farmers/Producers**: Product registration and tracking
- **🚚 Distributors**: Supply chain transfer management  
- **🏪 Retailers**: Inventory and quality verification
- **🔍 Inspectors**: Compliance monitoring and auditing
- **👤 Consumers**: Product authenticity verification

### 📊 Advanced Analytics
- **Real-time Dashboard**: Live supply chain monitoring
- **Predictive Analytics**: AI-powered insights
- **Quality Metrics**: Automated quality scoring
- **Fraud Detection**: Anomaly identification
- **Sustainability Tracking**: Carbon footprint monitoring

### 🌐 Modern Web Interface
- **Responsive Design**: Mobile-first approach
- **Dark/Light Themes**: User preference support
- **Progressive Web App**: App-like experience
- **Real-time Updates**: WebSocket integration
- **Multilingual Support**: Global accessibility

### 📱 Mobile Features
- **QR Code Scanning**: Instant product verification
- **GPS Tracking**: Location-based verification
- **Offline Mode**: Work without internet connectivity
- **Push Notifications**: Real-time alerts
- **Camera Integration**: Photo documentation

---

## 🏗️ Architecture

```mermaid
graph TB
    A[Frontend - HTML/CSS/JS] --> B[Flask Web Framework]
    B --> C[Authentication System]
    B --> D[Product Management]
    B --> E[Analytics Engine]
    C --> F[User Roles & Permissions]
    D --> G[Blockchain Integration]
    E --> H[Data Visualization]
    G --> I[Immutable Ledger]
    G --> J[Smart Contracts]
    B --> K[Database Layer]
    K --> L[SQLAlchemy ORM]
    L --> M[(PostgreSQL/SQLite)]
    
    subgraph "External Integrations (soon.. )"
        N[IoT Sensors]
        O[GPS Tracking]
        P[Government APIs]
        Q[Payment Gateways]
    end
    
    B --> N
    B --> O
    B --> P
    B --> Q
```

### 🛡️ Security Architecture
- **JWT Authentication**: Secure user sessions
- **Role-Based Access Control**: Granular permissions
- **Data Encryption**: AES-256 encryption at rest
- **HTTPS/TLS**: Secure data transmission
- **Input Validation**: SQL injection prevention
- **Rate Limiting**: DDoS protection

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend assets)
- Git
- Modern web browser

### ⚡ One-Click Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/foodchain-tracker.git
cd foodchain-tracker

# Run setup script
chmod +x setup.sh
./setup.sh

# Start the application
python app.py
```

🎉 **That's it!** Visit `http://localhost:5000` to see your FoodChain Tracker in action.

---

## 📦 Installation

### 🐳 Docker Installation (Recommended)
```bash
# Using Docker Compose
docker-compose up -d

# Access the application
open http://localhost:5000
```

### 🐍 Manual Installation
```bash
# 1. Clone repository
git clone https://github.com/yourusername/foodchain-tracker.git
cd foodchain-tracker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 5. Create admin user
python create_admin.py

# 6. Start development server
flask run --debug
```

### 📋 System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| RAM | 2GB | 4GB+ |
| Storage | 1GB | 5GB+ |
| CPU | 2 cores | 4+ cores |

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Application Settings
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///foodchain.db
# For PostgreSQL: postgresql://user:password@localhost/foodchain

# Blockchain Settings
BLOCKCHAIN_NETWORK=development
ETHEREUM_RPC_URL=http://localhost:8545
CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890

# Security
JWT_SECRET_KEY=your-jwt-secret-key
BCRYPT_LOG_ROUNDS=12

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Cloud Storage (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=foodchain-storage

# Analytics (Optional)
GOOGLE_ANALYTICS_ID=GA-XXXXX-X
```

### 🔧 Advanced Configuration
```python
# config.py
class Config:
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_ENABLED = True
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    
    # Blockchain settings
    BLOCKCHAIN_ENABLED = True
    SMART_CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
```

---

## 📱 Usage

### 🚜 For Farmers/Producers
1. **Register Products**: Add new products with origin details
2. **Set Quality Metrics**: Define quality parameters and certifications
3. **Track Harvests**: Record harvest dates and environmental conditions
4. **Generate QR Codes**: Create trackable product labels
5. **Transfer Products**: Send products to distributors

### 🚚 For Distributors
1. **Receive Products**: Accept products from farmers
2. **Monitor Conditions**: Track temperature, humidity during transport
3. **Update Locations**: Record GPS coordinates throughout journey
4. **Quality Checks**: Perform and record quality inspections
5. **Forward Products**: Transfer to retailers or other distributors

### 🏪 For Retailers
1. **Inventory Management**: Track received products
2. **Customer Information**: Provide transparency to consumers
3. **Quality Assurance**: Final quality checks before sale
4. **Sales Tracking**: Record product sales and feedback
5. **Waste Management**: Track unsold/expired products

### 👤 For Consumers
1. **Scan QR Codes**: Instantly verify product authenticity
2. **View History**: See complete farm-to-fork journey
3. **Check Quality**: Access quality scores and certifications
4. **Report Issues**: Flag quality or safety concerns
5. **Provide Feedback**: Rate products and suppliers

---

## 🔗 API Documentation

### Authentication Endpoints
```http
POST /api/auth/login
POST /api/auth/register
POST /api/auth/logout
GET  /api/auth/profile
PUT  /api/auth/profile
```

### Product Management
```http
GET    /api/products                 # List all products
POST   /api/products                 # Create new product
GET    /api/products/{id}            # Get product details
PUT    /api/products/{id}            # Update product
DELETE /api/products/{id}            # Delete product
GET    /api/products/{id}/history    # Get product history
POST   /api/products/{id}/transfer   # Transfer product
```

### Blockchain Operations
```http
GET  /api/blockchain/status          # Blockchain network status
POST /api/blockchain/verify          # Verify transaction
GET  /api/blockchain/blocks          # Get recent blocks
GET  /api/blockchain/transactions    # Get transactions
```

### Analytics
```http
GET /api/analytics/dashboard         # Dashboard statistics
GET /api/analytics/supply-chain      # Supply chain metrics
GET /api/analytics/quality           # Quality analysis
GET /api/analytics/fraud-detection   # Fraud alerts
```

### 📖 Interactive API Documentation
Visit `/api/docs` when running the application to access the interactive Swagger documentation.

---

## 🎨 UI/UX

### 🎭 Theme System
- **Light Theme**: Professional white interface (default)
- **Dark Theme**: Modern dark interface with proper contrast
- **Auto Theme**: Follows system preferences
- **Custom Themes**: Extensible theming system

### 📱 Responsive Design
- **Mobile First**: Optimized for smartphones and tablets
- **Progressive Web App**: App-like experience on mobile
- **Touch Gestures**: Intuitive touch interactions
- **Offline Support**: Critical features work offline

### ♿ Accessibility
- **WCAG 2.1 AA Compliant**: Meets accessibility standards
- **Screen Reader Support**: Full compatibility
- **Keyboard Navigation**: Complete keyboard accessibility
- **High Contrast**: Enhanced visibility options
- **Internationalization**: Multi-language support

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
```

### Test Coverage
```bash
# Generate coverage report
coverage run -m pytest
coverage report -m
coverage html  # Generate HTML report
```

### 🔍 Quality Assurance
- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Complete user journey testing
- **Security Testing**: Vulnerability scanning
- **Performance Testing**: Load and stress testing

---

## 🚀 Deployment

### 🐳 Docker Deployment
```bash
# Build and deploy with Docker
docker build -t foodchain-tracker .
docker run -p 5000:5000 foodchain-tracker
```

### ☁️ Cloud Deployment

#### Heroku
```bash
# Deploy to Heroku
heroku create your-app-name
git push heroku main
heroku run flask db upgrade
```

#### AWS/GCP/Azure
```bash
# Use provided deployment scripts
./deploy/aws-deploy.sh
./deploy/gcp-deploy.sh
./deploy/azure-deploy.sh
```

### 🔧 Production Configuration
```nginx
# Nginx configuration
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### 🚀 Getting Started
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/foodchain-tracker.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes: `pytest`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to the branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

### 📋 Contribution Guidelines
- **Code Style**: Follow PEP 8 for Python code
- **Testing**: Add tests for new features
- **Documentation**: Update docs for API changes
- **Commit Messages**: Use conventional commit format
- **Issues**: Use provided issue templates

### 🏷️ Areas for Contribution
- 🐛 **Bug Fixes**: Help us squash bugs
- ✨ **New Features**: Add exciting new functionality
- 📚 **Documentation**: Improve our docs
- 🎨 **UI/UX**: Enhance user experience
- 🔒 **Security**: Strengthen our security
- 🌐 **Internationalization**: Add language support

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 FoodChain Tracker Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---


## 📊 Project Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/yourusername/foodchain-tracker?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/foodchain-tracker?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/foodchain-tracker?style=social)

![GitHub issues](https://img.shields.io/github/issues/yourusername/foodchain-tracker)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/foodchain-tracker)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/foodchain-tracker)

![Lines of code](https://img.shields.io/tokei/lines/github/yourusername/foodchain-tracker)
![Code size](https://img.shields.io/github/languages/code-size/yourusername/foodchain-tracker)
![Repo size](https://img.shields.io/github/repo-size/yourusername/foodchain-tracker)

</div>

---

## 🌟 Acknowledgments

- 🙏 **Blockchain Community** for foundational technologies
- 💡 **Open Source Contributors** for amazing libraries
- 🌱 **Sustainable Agriculture Movement** for inspiration
- 🚀 **Early Adopters** for valuable feedback
- 💚 **Environmental Organizations** for guidance

---

## 📞 Support & Contact

<div align="center">

### 💬 Get Help


[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:duminduthushan9@gmail.com)

### 🌐 Links

[🏠 Website](https://foodchain.duminduthushan.com/) •
[📖 Documentation](https://docs.foodchaintracker.com) •
[🐛 Issues](../../issues) •
[💡 Feature Requests](../../issues/new?template=feature_request.md) •
[🔒 Security](SECURITY.md)

---

**Made with ❤️ by [**codedbydumi**](https://github.com/codedbydumi) for a more transparent and sustainable food system**

*"Transforming food supply chains, one block at a time"*

</div>
