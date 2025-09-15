# Chatbot Authentication API

A clean, focused FastAPI authentication system for chatbots with customer ID, email, and password authentication.

## 🚀 Features

- **Customer ID Authentication** - Login with customer ID and password
- **User Registration** - Signup with customer ID, email, and password
- **Password Reset** - Secure password reset with tokens
- **JWT Authentication** - Secure token-based authentication
- **MongoDB Integration** - Persistent user data storage
- **Input Validation** - Comprehensive request validation
- **API Documentation** - Automatic OpenAPI/Swagger docs

## 📁 Project Structure

```
chatbot_V2/
├── auth_api.py           # Main FastAPI application
├── test_auth_api.py     # Test client
├── requirements.txt     # Dependencies
├── env.example         # Environment configuration
└── README.md          # This documentation
```

## 🛠️ Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
copy env.example .env

# Edit .env file with your configuration
```

Required environment variables:
```env
SECRET_KEY=your_secret_key_here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=chatbot_auth
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Start MongoDB service
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux/macOS
```

**Option B: MongoDB Atlas (Cloud)**
- Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
- Create cluster and get connection string
- Update `MONGODB_URI` in `.env`

### 4. Run the API

```bash
python auth_api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication Endpoints

#### POST `/auth/signup`
Register a new user.

**Request Body:**
```json
{
  "customer_id": "CUST001",
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "customer_id": "CUST001",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

#### POST `/auth/login`
Login with customer ID and password.

**Request Body:**
```json
{
  "customer_id": "CUST001",
  "password": "SecurePass123"
}
```

**Response:** Same as signup response.

#### GET `/auth/me`
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

#### POST `/auth/forgot-password`
Request password reset token.

**Request Body:**
```json
{
  "customer_id": "CUST001"
}
```

#### POST `/auth/reset-password`
Reset password using token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "NewSecurePass123"
}
```

#### POST `/auth/change-password`
Change user password (requires authentication).

**Request Body:**
```json
{
  "current_password": "OldPass123",
  "new_password": "NewPass123"
}
```

#### POST `/auth/logout`
Logout user (requires authentication).

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Signup/Login** - Receive JWT token
2. **Include Token** - Add `Authorization: Bearer <token>` header
3. **Token Expiration** - Tokens expire after 30 minutes (configurable)

### Example Usage with curl:

```bash
# Signup
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "CUST001", "email": "test@example.com", "password": "TestPass123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "CUST001", "password": "TestPass123"}'

# Get user info (with token)
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your_token>"
```

## 🧪 Testing

### Automated Testing

```bash
python test_auth_api.py
```

### Interactive Testing

```bash
python test_auth_api.py interactive
```

### Manual Testing

Visit http://localhost:8000/docs for interactive API documentation.

## 📊 Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "customer_id": "CUST001",
  "email": "user@example.com",
  "password": "hashed_password",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "is_active": true,
  "email_verified": false,
  "reset_tokens": [
    {
      "token": "reset_token",
      "expires_at": "datetime",
      "used": false
    }
  ]
}
```

## 🔒 Security Features

- **JWT Tokens** - Secure, stateless authentication
- **Password Hashing** - SHA-256 with salt
- **Input Validation** - Pydantic models validate all inputs
- **CORS Protection** - Configurable cross-origin policies
- **Token Expiration** - Automatic token invalidation
- **Password Strength** - Enforced password requirements
- **Customer ID Validation** - Format validation (6-20 alphanumeric)

## 📋 Validation Rules

### Customer ID
- Must be 6-20 characters long
- Must contain only alphanumeric characters
- Must be unique

### Password
- Minimum 8 characters
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Must contain at least one number

### Email
- Must be valid email format
- Must be unique

## 🚀 Production Deployment

### Environment Variables for Production

```env
SECRET_KEY=very_secure_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=chatbot_auth_prod
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "auth_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```bash
   # Check MongoDB status
   python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/').admin.command('ping')"
   ```

2. **JWT Token Issues**
   - Check `SECRET_KEY` in environment
   - Verify token format in Authorization header
   - Check token expiration

3. **Import Errors**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

4. **Port Already in Use**
   ```bash
   # Change port in auth_api.py
   uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

## 📈 API Documentation

The FastAPI application automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the GenAI with LangChain learning repository.

---

**Ready for your chatbot integration! 🚀**
