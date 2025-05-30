# AmpUpEvents - Event Management Platform

A comprehensive Flask-based web application for creating, managing, and booking music events. This platform allows users to create events, book tickets, and discover new music experiences.

## 🎵 Features

### User Management
- **User Registration & Authentication**: Secure signup/login system with email validation
- **Profile Management**: Users can update personal information, address, and password
- **Role-based Access**: Different permissions for event creators and attendees

### Event Management
- **Event Creation**: Create detailed music events with rich information
- **Image Upload**: Support for both file uploads and external image URLs
- **Event Editing**: Update event details, images, and ticket information
- **Event Categories**: Organize events by music genres (Blues, Classical, Country, Electronic, Funk, Hip Hop, Jazz, Metal, Pop, R&B, Reggae, Rock)
- **Event Status Management**: Open, Sold Out, Cancelled, Completed, Inactive statuses
- **Event Cancellation**: Event creators can cancel their events with confirmation

### Smart Event Discovery
- **Upcoming Events**: Chronological display of future active events
- **Popular Events**: Shows events with highest ticket sales
- **Recommended Events**: Promotes events with lowest sales (helping new/struggling events)
- **Genre Filtering**: Filter events by music genre
- **Search & Browse**: Comprehensive event browsing capabilities

### Booking System
- **Multi-ticket Types**: Support for General Admission and VIP tickets
- **Real-time Availability**: Live ticket quantity tracking
- **Secure Booking Process**: Integrated booking with inventory management
- **Order Management**: Complete order history and confirmation system
- **Booking History**: Users can view their past and upcoming bookings

### Social Features
- **Event Comments**: Users can comment on events
- **Comment Management**: Edit and delete your own comments
- **Event Reviews**: Community engagement through feedback

### Advanced Features
- **Image Upload System**: Secure file handling with validation
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Flash Messaging**: Real-time user feedback
- **Error Handling**: Comprehensive error management
- **Debug Support**: Extensive logging for troubleshooting

## 🛠️ Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2 templating
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms validation
- **Security**: Flask-CSRF protection, secure file uploads
- **Password Hashing**: Flask-Bcrypt
- **File Handling**: Werkzeug secure filename handling

## 📁 Project Structure

```
projectfile/
├── main.py                 # Application entry point
├── website/
│   ├── __init__.py        # Flask app factory
│   ├── models.py          # Database models
│   ├── forms.py           # WTForms form definitions
│   ├── views.py           # Main routes (homepage, profile)
│   ├── events.py          # Event-related routes
│   ├── auth.py            # Authentication routes
│   ├── static/
│   │   ├── style/         # CSS stylesheets
│   │   ├── img/           # Images and uploads
│   │   │   ├── events/    # Event image uploads
│   │   │   └── genre icons
│   │   └── js/            # JavaScript files
│   └── templates/
│       ├── base.html      # Base template
│       ├── index.html     # Homepage
│       ├── auth/          # Authentication templates
│       └── events/        # Event-related templates
├── instance/
│   └── database.db       # SQLite database
└── requirements.txt      # Python dependencies
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd IAB207-2/a3_starter_code/projectfile
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file (or set environment variables):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/database.db
```

### 5. Initialize Database
```bash
# The database will be created automatically on first run
python create_db.py
```

### 6. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## 📋 Usage Guide

### For Event Attendees

1. **Register/Login**: Create an account or sign in
2. **Browse Events**: 
   - View upcoming events on the homepage
   - Check out popular events (most ticket sales)
   - Discover recommended events (need more attention)
   - Filter by music genre
3. **Book Tickets**: 
   - Select event → Choose ticket types → Book tickets
   - View booking confirmation and history
4. **Engage**: Comment on events and interact with the community

### For Event Creators

1. **Create Events**: 
   - Navigate to "Create Event"
   - Fill in event details, upload image
   - Set ticket types and pricing
2. **Manage Events**:
   - Edit event information
   - Update images and descriptions
   - Cancel events if needed
3. **Track Performance**:
   - View booking history
   - Monitor ticket sales
   - Check revenue and attendance

### Admin Features

- Monitor all events and users
- Manage event statuses
- View platform analytics

## 🎨 Event Categories

The platform supports the following music genres:
- Blues
- Classical  
- Country
- Electronic
- Funk
- Hip Hop
- Jazz
- Metal
- Pop
- R&B
- Reggae
- Rock

## 🔧 Configuration

### Database Models
- **User**: User accounts and profiles
- **Event**: Event information and metadata
- **Genre**: Music genre categories
- **ticket_type**: Ticket types (General, VIP) with pricing
- **Booking**: Individual booking records
- **Order**: Order management
- **Comment**: Event comments and reviews

### Image Upload Settings
- **Supported formats**: JPG, JPEG, PNG, WEBP
- **Upload directory**: `website/static/img/events/`
- **Security**: Secure filename handling, file validation

## 🚨 Troubleshooting

### Common Issues

1. **Database Issues**: Delete `instance/database.db` and restart app
2. **Image Upload Problems**: Check file permissions in `static/img/events/`
3. **Genre Loading Errors**: Ensure genre data is populated in database

### Debug Mode
Enable debug mode by setting:
```python
app.run(debug=True)
```

## 🔐 Security Features

- CSRF protection on all forms
- Secure password hashing with Bcrypt
- Input validation and sanitization
- Secure file upload handling
- Session management
- SQL injection prevention through ORM

## 📊 Smart Event Promotion

The platform features an intelligent event promotion system:

- **Popular Events**: Showcases events with highest ticket sales
- **Recommended Events**: Promotes events with fewer sales to help struggling events gain visibility
- **Balanced Discovery**: Ensures both successful and new events get exposure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is developed for educational purposes as part of IAB207 coursework.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask documentation
3. Check SQLAlchemy documentation for database issues

---

**Built with ❤️ using Flask and modern web technologies** 