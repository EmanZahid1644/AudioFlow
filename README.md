# 🎧 AudioFlow

A secure and modern Audio Transfer Platform built with **FastAPI**, **Streamlit**, **MongoDB**, **Cloudinary**, and **JWT Authentication**.

Users can securely register, log in, upload audio files to Cloudinary, and access their personal audio library.

---

## 🚀 Features

- 🔐 User Registration
- 🔑 User Login
- 🔒 JWT Authentication & Authorization
- 🔐 Password Hashing (bcrypt)
- ☁️ Audio Upload to Cloudinary
- 🎵 Personal Audio Library
- 📂 MongoDB Database
- 🎨 Modern Streamlit UI
- 📱 Responsive Dashboard

---

## 🛠 Tech Stack

### Backend
- FastAPI
- Python
- MongoDB
- PyMongo
- Cloudinary
- JWT Authentication
- Passlib (bcrypt)

### Frontend
- Streamlit
- HTML
- CSS

---

## 📂 Project Structure

```
AudioFlow/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── cloudinary_config.py
│   ├── cloudinary_service.py
│   ├── requirements.txt
│   ├── vercel.json
│   └── .env
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/AudioFlow.git
```

```bash
cd AudioFlow
```

---

### 2. Backend Setup

```bash
cd backend
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run backend

```bash
uvicorn main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

---

### 3. Frontend Setup

Open a new terminal

```bash
cd frontend
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run Streamlit

```bash
streamlit run app.py
```

Frontend URL

```
http://localhost:8501
```

---

## 🔑 Environment Variables

Create a `.env` file inside the `backend` folder.

```env
MONGO_URI=your_mongodb_connection_string

SECRET_KEY=your_secret_key

CLOUDINARY_CLOUD_NAME=your_cloud_name

CLOUDINARY_API_KEY=your_api_key

CLOUDINARY_API_SECRET=your_api_secret
```

---

## 📌 API Endpoints

### Register User

```
POST /register
```

### Login User

```
POST /login
```

### Upload Audio

```
POST /receive
```

Requires JWT Token.

---

### Get User Audios

```
GET /audios
```

Requires JWT Token.

---

## 🔒 Authentication

AudioFlow uses **JWT (JSON Web Token)** authentication.

After successful login, the backend returns an Access Token.

Example:

```
Authorization: Bearer your_access_token
```

---

## ☁️ Cloudinary

Uploaded audio files are securely stored on Cloudinary instead of the local server.

Each upload stores:

- Audio URL
- Public ID
- Upload Time
- User Email

---

## 🗄 Database

MongoDB stores:

### Users

- Name
- Email
- Password (Hashed)

### Audios

- Filename
- Cloudinary URL
- Public ID
- Uploaded By
- Upload Date

---

## 🎯 Future Improvements

- Email Verification
- Forgot Password
- Delete Audio
- Rename Audio
- Search Audio
- Audio Sharing
- User Profile
- Admin Dashboard
- Drag & Drop Upload
- Audio Waveform Preview

---

## 👩‍💻 Author

**Eman Zahid**

BS Computer Science  


---

