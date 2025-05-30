from website import db, create_app
from website.models import Genre

# Create the Flask app and push the context to allow database operations
app = create_app()
ctx = app.app_context()
ctx.push()
# Create all database tables based on the defined models
db.create_all()

def add_sample_genres():
    """Add the predefined genres to the database"""
    genres_to_add = [
        {'name': 'Blues', 'description': 'Blues music genre', 'image_filename': 'img/Blues.png'},
        {'name': 'Classical', 'description': 'Classical music genre', 'image_filename': 'img/Classical.png'},
        {'name': 'Country', 'description': 'Country music genre', 'image_filename': 'img/Country.png'},
        {'name': 'Electronic', 'description': 'Electronic music genre', 'image_filename': 'img/Electronic.png'},
        {'name': 'Funk', 'description': 'Funk music genre', 'image_filename': 'img/Funk.png'},
        {'name': 'Hip Hop', 'description': 'Hip Hop music genre', 'image_filename': 'img/Hip Hop.png'},
        {'name': 'Jazz', 'description': 'Jazz music genre', 'image_filename': 'img/Jazz.png'},
        {'name': 'Metal', 'description': 'Metal music genre', 'image_filename': 'img/Metal.png'},
        {'name': 'Pop', 'description': 'Pop music genre', 'image_filename': 'img/Pop.png'},
        {'name': 'R&B', 'description': 'R&B music genre', 'image_filename': 'img/R&B.png'},
        {'name': 'Reggae', 'description': 'Reggae music genre', 'image_filename': 'img/Reggae.png'},
        {'name': 'Rock', 'description': 'Rock music genre', 'image_filename': 'img/Rock.png'},
    ]
    
    for genre_data in genres_to_add:
        # Check if the genre already exists in the database
        existing_genre = db.session.scalar(db.select(Genre).filter_by(name=genre_data['name']))
        if not existing_genre:
            new_genre = Genre(
                name=genre_data['name'], 
                description=genre_data['description'],
                image_filename=genre_data['image_filename']
            )
            db.session.add(new_genre)
            print(f"Added genre: {genre_data['name']}")
    
    # Commit the changes to the database
    db.session.commit()
    print("Sample genres checked/added.")

# Add sample genres to the database
add_sample_genres()

print("Database tables created successfully.")
print("Genre system initialized with predefined music genres.")
ctx.pop()

# Quit the script
quit()