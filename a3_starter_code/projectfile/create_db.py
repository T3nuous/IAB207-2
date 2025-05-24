from website import db, create_app

from website.models import event_category

app = create_app()
ctx = app.app_context()
ctx.push()

def add_sample_categories():
    categories_to_add = [
        {'name': 'Music Concert', 'description': 'Live music performances.'},
        {'name': 'Theater Show', 'description': 'Plays and theatrical performances.'},
        {'name': 'Workshop', 'description': 'Educational workshops and seminars.'},
        {'name': 'Conference', 'description': 'Professional and academic conferences.'},
        {'name': 'Exhibition', 'description': 'Art and other exhibitions.'}
    ]
    
    for cat_data in categories_to_add:
        category = db.session.scalar(db.select(event_category).filter_by(name=cat_data['name']))
        if not category:
            new_category = event_category(name=cat_data['name'], description=cat_data['description'])
            db.session.add(new_category)
            print(f"Added category: {cat_data['name']}")
    
    db.session.commit()
    print("Sample categories checked/added.")

add_sample_categories()

print("Database tables created and sample categories processed.")
ctx.pop()

quit()