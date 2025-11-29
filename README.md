# TicketPro Support System
A comprehensive support ticket management system built with Django, featuring real-time chat, ticket tracking, and a responsive dashboard.

## 🚀 Features

### User Management
- Multi-role system (Regular Users, Support Staff, Administrators)
- Secure authentication with JWT
- Customizable user profiles

### Ticket Management
- Complete ticket lifecycle (Open → In Progress → Resolved → Closed)
- Priority-based ticket assignment
- SLA enforcement and monitoring
- File attachment support

### Real-time Communication
- Live chat between users and support staff
- WebSocket-powered messaging
- Read receipts and typing indicators
- Message history preservation

### Dashboard & Analytics
- Real-time status monitoring
- Performance metrics for support staff
- Ticket volume analytics
- Customer satisfaction tracking

### Notifications
- Event-driven notification system
- Configurable delivery preferences (email, in-app)
- Critical alert escalation
- Smart notification batching

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Redis (for WebSocket and caching)

## 🛠️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/support_system.git
cd support_system
```

2. **Create and activate a virtual environment**

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your_secret_key_here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Create a superuser**

```bash
python manage.py createsuperuser
```

7. **Run the development server**

```bash
python manage.py runserver
```

8. **Access the application**

Open your browser and navigate to `http://127.0.0.1:8000`

## 🏗️ Project Structure

```
support_system/
├── accounts/            # User authentication and profiles
├── chat/                # Real-time messaging functionality
├── frontend/            # Templates and static files
├── tickets/             # Ticket management system
├── support_system/      # Project settings and configuration
├── manage.py            # Django management script
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## 💻 Usage

### User Types and Permissions

- **Regular Users**: Can create tickets, communicate with support staff, and track their ticket status
- **Support Staff**: Can manage assigned tickets, communicate with users, and update ticket status
- **Administrators**: Full system access, including user management and system configuration

### Ticket Workflow

1. User creates a ticket with a description, category, and priority
2. Support staff is assigned based on expertise and workload
3. Real-time communication occurs through the integrated chat system
4. Ticket progresses through status updates until resolution
5. User confirms resolution to close the ticket

## 🔒 Security Features

- JWT-based authentication
- Permission-based access control
- Data encryption for sensitive information
- Rate limiting on API endpoints
- Session timeout protection

## 📊 API Documentation

API documentation is available through Swagger UI at `/api/docs/` when the server is running.

## 🧪 Running Tests

```bash
python manage.py test
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
