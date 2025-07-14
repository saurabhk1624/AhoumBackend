# API Documentation

## Overview

This documentation covers two main services:
1. **Main API Service** - Primary booking and event management system (Port 8000)
2. **CRM Service** - Customer relationship management and notifications (Port 8003)

## Base URLs

- **Main API**: `http://localhost:8000`
- **CRM Service**: `http://localhost:8003`

---

## Main API Service

### Authentication

The main API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

#### Register User
- **POST** `/api/auth/register`
- **Description**: Register a new user account
- **Authentication**: None required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "created_at": "2024-01-01T12:00:00",
    "is_active": true
  }
}
```

#### Login
- **POST** `/api/auth/login`
- **Description**: Authenticate user and get access tokens
- **Authentication**: None required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "created_at": "2024-01-01T12:00:00",
    "is_active": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Google Login
- **POST** `/api/auth/google-login`
- **Description**: Authenticate using Google OAuth token
- **Authentication**: None required

**Request Body:**
```json
{
  "token": "google_oauth_token_here"
}
```

#### Refresh Token
- **POST** `/api/auth/refresh`
- **Description**: Get new access token using refresh token
- **Authentication**: Refresh token required

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get Profile
- **GET** `/api/auth/profile`
- **Description**: Get current user profile
- **Authentication**: JWT required

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "created_at": "2024-01-01T12:00:00",
    "is_active": true
  }
}
```

### Events Endpoints

#### Get Events
- **GET** `/api/events/`
- **Description**: Get list of available events with filtering and pagination
- **Authentication**: JWT required

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)
- `type` (string): Event type filter (`session` or `retreat`)
- `facilitator_id` (int): Filter by facilitator ID
- `status` (string): Event status (default: `active`)
- `search` (string): Search in title and description

**Response (200):**
```json
{
  "events": [
    {
      "id": 1,
      "title": "Morning Meditation Session",
      "description": "Start your day with mindfulness",
      "event_type": "SESSION",
      "facilitator": {
        "id": 1,
        "name": "Jane Smith",
        "bio": "Certified meditation instructor"
      },
      "start_datetime": "2024-01-15T07:00:00",
      "end_datetime": "2024-01-15T08:00:00",
      "location": "Wellness Center",
      "virtual_link": null,
      "max_participants": 20,
      "current_participants": 5,
      "available_spots": 15,
      "price": 25.00,
      "status": "ACTIVE",
      "requirements": "Bring your own mat",
      "is_full": false,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 3,
    "per_page": 10,
    "total": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Event Details
- **GET** `/api/events/<event_id>`
- **Description**: Get detailed information about a specific event
- **Authentication**: JWT required

**Response (200):**
```json
{
  "event": {
    "id": 1,
    "title": "Morning Meditation Session",
    "description": "Start your day with mindfulness",
    "event_type": "SESSION",
    "facilitator": {
      "id": 1,
      "name": "Jane Smith",
      "bio": "Certified meditation instructor"
    },
    "start_datetime": "2024-01-15T07:00:00",
    "end_datetime": "2024-01-15T08:00:00",
    "location": "Wellness Center",
    "virtual_link": null,
    "max_participants": 20,
    "current_participants": 5,
    "available_spots": 15,
    "price": 25.00,
    "status": "ACTIVE",
    "requirements": "Bring your own mat",
    "is_full": false,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

#### Get Event Types
- **GET** `/api/events/types`
- **Description**: Get list of available event types
- **Authentication**: JWT required

**Response (200):**
```json
{
  "event_types": [
    {"key": "SESSION", "value": 1},
    {"key": "RETREAT", "value": 2}
  ]
}
```

### Bookings Endpoints

#### Create Booking
- **POST** `/api/bookings/`
- **Description**: Create a new booking for an event
- **Authentication**: JWT required

**Request Body:**
```json
{
  "event_id": 1,
  "notes": "Looking forward to this session"
}
```

**Response (201):**
```json
{
  "message": "Booking created successfully",
  "booking": {
    "id": 1,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "event": {
      "id": 1,
      "title": "Morning Meditation Session",
      "event_type": "SESSION",
      "start_datetime": "2024-01-15T07:00:00"
    },
    "booking_date": "2024-01-01T12:00:00",
    "status": "CONFIRMED",
    "notes": "Looking forward to this session",
    "payment_status": "pending",
    "created_at": "2024-01-01T12:00:00"
  },
  "crm_notified": true
}
```

#### Get User Bookings
- **GET** `/api/bookings/`
- **Description**: Get current user's bookings with filtering and pagination
- **Authentication**: JWT required

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)
- `status` (string): Booking status filter
- `upcoming` (boolean): Filter for upcoming events only (default: false)

**Response (200):**
```json
{
  "bookings": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "event": {
        "id": 1,
        "title": "Morning Meditation Session",
        "event_type": "SESSION",
        "start_datetime": "2024-01-15T07:00:00"
      },
      "booking_date": "2024-01-01T12:00:00",
      "status": "CONFIRMED",
      "notes": "Looking forward to this session",
      "payment_status": "pending",
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 2,
    "per_page": 10,
    "total": 15,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Booking Details
- **GET** `/api/bookings/<booking_id>`
- **Description**: Get detailed information about a specific booking
- **Authentication**: JWT required

#### Cancel Booking
- **PUT** `/api/bookings/<booking_id>/cancel`
- **Description**: Cancel a specific booking
- **Authentication**: JWT required

**Response (200):**
```json
{
  "message": "Booking cancelled successfully",
  "booking": {
    "id": 1,
    "status": "CANCELLED",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

### Facilitators Endpoints

#### Get Facilitators
- **GET** `/api/facilitators/`
- **Description**: Get list of active facilitators with pagination
- **Authentication**: JWT required

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)

#### Get Facilitator Details
- **GET** `/api/facilitators/<facilitator_id>`
- **Description**: Get detailed information about a specific facilitator
- **Authentication**: JWT required

#### Get Facilitator Events
- **GET** `/api/facilitators/<facilitator_id>/events`
- **Description**: Get all events for a specific facilitator
- **Authentication**: JWT required

#### Facilitator Login
- **POST** `/api/facilitators/login`
- **Description**: Login endpoint for facilitators
- **Authentication**: None required

### Health Check

#### Health Check
- **GET** `/health`
- **Description**: Check API health and database connectivity
- **Authentication**: None required

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## CRM Service

### Authentication

The CRM service uses Bearer token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <bearer_token>
```

Default token: `crm-static-bearer-token-123` (configurable via `CRM_BEARER_TOKEN` environment variable)

### CRM Endpoints

#### Receive Booking Notification
- **POST** `/api/notify`
- **Description**: Receive booking notifications from the main service
- **Authentication**: Bearer token required

**Request Body:**
```json
{
  "booking_id": 1,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890"
  },
  "event": {
    "id": 1,
    "title": "Morning Meditation Session",
    "type": "session",
    "start_datetime": "2024-01-15T07:00:00",
    "location": "Wellness Center"
  },
  "facilitator_id": 1,
  "booking_date": "2024-01-01T12:00:00",
  "notes": "Looking forward to this session"
}
```

**Response (200):**
```json
{
  "message": "Booking notification received successfully",
  "notification_id": 1,
  "status": "success"
}
```

#### Get All Booking Notifications
- **GET** `/api/bookings`
- **Description**: Get all received booking notifications with filtering and pagination
- **Authentication**: Bearer token required

**Query Parameters:**
- `facilitator_id` (int): Filter by facilitator ID
- `event_id` (int): Filter by event ID
- `user_id` (int): Filter by user ID
- `status` (string): Filter by booking status
- `crm_status` (string): Filter by CRM status (`new`, `reviewed`, `contacted`, `confirmed`, `completed`)
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "bookings": [
    {
      "id": 1,
      "booking_id": 1,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "phone": "+1234567890"
      },
      "event": {
        "id": 1,
        "title": "Morning Meditation Session",
        "type": "session"
      },
      "facilitator_id": 1,
      "received_at": "2024-01-01T12:00:00",
      "status": "received",
      "crm_status": "new"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "facilitator_id": null,
    "event_id": null,
    "user_id": null,
    "status": null,
    "crm_status": null
  },
  "summary": {
    "total_notifications": 25,
    "filtered_results": 25
  }
}
```

#### Get Facilitator Bookings
- **GET** `/api/facilitators/<facilitator_id>/bookings`
- **Description**: Get all bookings for a specific facilitator with statistics
- **Authentication**: Bearer token required

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10, max: 100)
- `status` (string): Filter by booking status
- `event_type` (string): Filter by event type
- `crm_status` (string): Filter by CRM status

**Response (200):**
```json
{
  "facilitator_id": 1,
  "bookings": [
    {
      "id": 1,
      "booking_id": 1,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe"
      },
      "event": {
        "id": 1,
        "title": "Morning Meditation Session",
        "type": "session"
      },
      "received_at": "2024-01-01T12:00:00",
      "crm_status": "new"
    }
  ],
  "statistics": {
    "total_bookings": 15,
    "session_bookings": 10,
    "retreat_bookings": 5,
    "recent_bookings": 3,
    "unique_users": 12,
    "unique_events": 8
  },
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 15,
    "pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Facilitator Dashboard
- **GET** `/api/facilitators/<facilitator_id>/dashboard`
- **Description**: Get comprehensive dashboard data for a facilitator
- **Authentication**: Bearer token required

**Response (200):**
```json
{
  "facilitator_id": 1,
  "summary": {
    "total_bookings": 15,
    "session_bookings": 10,
    "retreat_bookings": 5,
    "recent_bookings_count": 3,
    "unique_events": 8,
    "unique_users": 12
  },
  "popular_events": [
    {
      "event_id": 1,
      "event_title": "Morning Meditation Session",
      "event_type": "session",
      "booking_count": 8
    }
  ],
  "recent_bookings": [
    {
      "id": 1,
      "booking_id": 1,
      "user": {
        "id": 1,
        "name": "John Doe",
        "email": "user@example.com"
      },
      "event": {
        "id": 1,
        "title": "Morning Meditation Session"
      },
      "received_at": "2024-01-01T12:00:00"
    }
  ],
  "booking_trends": {
    "sessions_vs_retreats": {
      "sessions": 10,
      "retreats": 5
    }
  },
  "generated_at": "2024-01-01T12:00:00"
}
```

#### Get Specific Booking
- **GET** `/api/bookings/<booking_id>`
- **Description**: Get specific booking notification by booking ID
- **Authentication**: Bearer token required

**Response (200):**
```json
{
  "booking": {
    "id": 1,
    "booking_id": 1,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "phone": "+1234567890"
    },
    "event": {
      "id": 1,
      "title": "Morning Meditation Session",
      "type": "session"
    },
    "facilitator_id": 1,
    "received_at": "2024-01-01T12:00:00",
    "status": "received",
    "crm_status": "new"
  }
}
```

#### Update Booking CRM Status
- **PUT** `/api/bookings/<booking_id>/status`
- **Description**: Update the CRM status of a booking
- **Authentication**: Bearer token required

**Request Body:**
```json
{
  "crm_status": "contacted",
  "notes": "Called customer to confirm attendance"
}
```

**Valid CRM Statuses:**
- `new` - Newly received notification
- `reviewed` - Notification has been reviewed
- `contacted` - Customer has been contacted
- `confirmed` - Booking confirmed with customer
- `completed` - Event completed

**Response (200):**
```json
{
  "message": "Booking status updated successfully",
  "booking_id": 1,
  "old_status": "new",
  "new_status": "contacted",
  "updated_at": "2024-01-01T12:00:00"
}
```

### CRM Health Check

#### CRM Health Check
- **GET** `/health`
- **Description**: Check CRM service health and statistics
- **Authentication**: None required

**Response (200):**
```json
{
  "status": "healthy",
  "service": "CRM Notification Service",
  "port": 8003,
  "timestamp": "2024-01-01T12:00:00",
  "notifications_received": 25,
  "unique_facilitators": 5,
  "unique_events": 12,
  "endpoints": [
    "/health",
    "/api/notify",
    "/api/bookings",
    "/api/facilitators/{id}/bookings",
    "/api/facilitators/{id}/dashboard",
    "/api/bookings/{id}",
    "/api/bookings/{id}/status"
  ]
}
```

---

## Data Models

### User Model
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "created_at": "2024-01-01T12:00:00",
  "is_active": true
}
```

### Event Model
```json
{
  "id": 1,
  "title": "Morning Meditation Session",
  "description": "Start your day with mindfulness",
  "event_type": "SESSION",
  "facilitator": {
    "id": 1,
    "name": "Jane Smith",
    "bio": "Certified meditation instructor"
  },
  "start_datetime": "2024-01-15T07:00:00",
  "end_datetime": "2024-01-15T08:00:00",
  "location": "Wellness Center",
  "virtual_link": null,
  "max_participants": 20,
  "current_participants": 5,
  "available_spots": 15,
  "price": 25.00,
  "status": "ACTIVE",
  "requirements": "Bring your own mat",
  "is_full": false,
  "created_at": "2024-01-01T12:00:00"
}
```

### Booking Model
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "event": {
    "id": 1,
    "title": "Morning Meditation Session",
    "event_type": "SESSION",
    "start_datetime": "2024-01-15T07:00:00"
  },
  "booking_date": "2024-01-01T12:00:00",
  "status": "CONFIRMED",
  "notes": "Looking forward to this session",
  "payment_status": "pending",
  "created_at": "2024-01-01T12:00:00"
}
```

---

## Error Responses

### Common Error Format
```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required or invalid
- **403 Forbidden** - Access denied
- **404 Not Found** - Resource not found
- **409 Conflict** - Resource already exists
- **500 Internal Server Error** - Server error

---

## Environment Configuration

### Main API Service
- `FLASK_ENV` - Environment (development/production)
- `JWT_SECRET_KEY` - JWT signing secret
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `CRM_SERVICE_URL` - CRM service URL
- `CRM_BEARER_TOKEN` - Token for CRM service communication

### CRM Service
- `CRM_BEARER_TOKEN` - Bearer token for authentication (default: `crm-static-bearer-token-123`)

---

## Setup and Running

### Main API Service
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The main API will be available at `http://localhost:8000`

### CRM Service
```bash
# Run the CRM service
python crm_service.py
```

The CRM service will be available at `http://localhost:8003`

---

## API Features

### Main API Service Features
- JWT-based authentication with refresh tokens
- Google OAuth integration
- Event management with filtering and pagination
- Booking system with conflict prevention
- Automatic CRM notifications
- Comprehensive error handling
- Database relationships and constraints
- Swagger documentation integration

### CRM Service Features
- Bearer token authentication
- Booking notification handling
- Facilitator dashboard analytics
- Booking status tracking
- Data persistence with file backup
- Comprehensive filtering and pagination
- Real-time statistics and reporting