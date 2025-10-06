from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_images():
    """Create placeholder book cover images"""
    # Create directories if they don't exist
    os.makedirs('static/images/books', exist_ok=True)
    
    # List of all book cover images we need
    book_covers = [
        'great_gatsby.jpg', 'mockingbird.jpg', '1984.jpg', 'pride_prejudice.jpg',
        'catcher_rye.jpg', 'lotr.jpg', 'hobbit.jpg', 'brave_new_world.jpg',
        'alchemist.jpg', 'kite_runner.jpg', 'davinci_code.jpg', 'gone_girl.jpg',
        'dragon_tattoo.jpg', 'silent_patient.jpg', 'big_little_lies.jpg',
        'woman_window.jpg', 'sharp_objects.jpg', 'in_the_woods.jpg',
        'detective_agency.jpg', 'cuckoos_calling.jpg', 'dune.jpg', 'foundation.jpg',
        'neuromancer.jpg', 'martian.jpg', 'snow_crash.jpg', 'enders_game.jpg',
        'left_hand.jpg', 'hyperion.jpg', 'ready_player_one.jpg', 'three_body.jpg',
        'harry_potter.jpg', 'game_of_thrones.jpg', 'name_of_wind.jpg', 'way_of_kings.jpg',
        'mistborn.jpg', 'lightning_thief.jpg', 'american_gods.jpg', 'color_magic.jpg',
        'eye_world.jpg', 'assassin_apprentice.jpg', 'notebook.jpg', 'pride_romance.jpg',
        'outlander.jpg', 'the_bride.jpg', 'the_wedding.jpg', 'it_ends_us.jpg',
        'hating_game.jpg', 'spanish_love.jpg', 'beach_read.jpg', 'love_hypothesis.jpg',
        'girl_train.jpg', 'silent_thriller.jpg', 'the_reversal.jpg', 'couple_next.jpg',
        'behind_doors.jpg', 'wife_between.jpg', 'then_she.jpg', 'nightingale.jpg',
        'guest_list.jpg', 'one_by_one.jpg', 'steve_jobs.jpg', 'becoming.jpg',
        'educated.jpg', 'anne_frank.jpg', 'elon_musk.jpg', 'caged_bird.jpg',
        'wright_brothers.jpg', 'alexander_hamilton.jpg', 'helen_keller.jpg', 'mandela.jpg',
        'sapiens.jpg', 'guns_germs.jpg', 'peoples_history.jpg', 'silk_roads.jpg',
        'third_reich.jpg', '1776.jpg', 'crusades.jpg', 'spqr.jpg', 'ww2.jpg', 'short_history.jpg',
        'brief_history.jpg', 'selfish_gene.jpg', 'cosmos.jpg', 'the_gene.jpg',
        'emperor_maladies.jpg', 'double_helix.jpg', 'elegant_universe.jpg', 'infinity.jpg',
        'henrietta_lacks.jpg', 'sixth_extinction.jpg', 'hungry_caterpillar.jpg',
        'wild_things.jpg', 'goodnight_moon.jpg', 'charlottes_web.jpg', 'cat_hat.jpg',
        'harry_children.jpg', 'lion_witch.jpg', 'matilda.jpg', 'peter_rabbit.jpg', 'green_eggs.jpg'
    ]
    
    # Colors for different genres
    genre_colors = {
        'Fiction': '#3498db',
        'Mystery': '#e74c3c', 
        'Science Fiction': '#9b59b6',
        'Fantasy': '#f39c12',
        'Romance': '#e91e63',
        'Thriller': '#34495e',
        'Biography': '#16a085',
        'History': '#795548',
        'Science': '#27ae60',
        'Children': '#f1c40f'
    }
    
    for cover in book_covers:
        # Extract book title from filename
        title = cover.replace('.jpg', '').replace('_', ' ').title()
        
        # Determine genre from title (simplified mapping)
        genre = 'Fiction'  # default
        for g in genre_colors:
            if g.lower() in title.lower() or any(keyword in title.lower() for keyword in [
                'potter', 'rings', 'hobbit', 'dragon', 'magic']):
                if g == 'Fantasy': genre = g
            elif any(keyword in title.lower() for keyword in ['mystery', 'detective', 'crime']):
                if g == 'Mystery': genre = g
            elif any(keyword in title.lower() for keyword in ['sci', 'space', 'martian', 'dune']):
                if g == 'Science Fiction': genre = g
            elif any(keyword in title.lower() for keyword in ['romance', 'love', 'bride', 'wedding']):
                if g == 'Romance': genre = g
            elif any(keyword in title.lower() for keyword in ['thriller', 'suspense', 'girl']):
                if g == 'Thriller': genre = g
            elif any(keyword in title.lower() for keyword in ['biography', 'jobs', 'becoming']):
                if g == 'Biography': genre = g
            elif any(keyword in title.lower() for keyword in ['history', 'war', 'reich']):
                if g == 'History': genre = g
            elif any(keyword in title.lower() for keyword in ['science', 'gene', 'universe']):
                if g == 'Science': genre = g
            elif any(keyword in title.lower() for keyword in ['children', 'cat', 'rabbit', 'hat']):
                if g == 'Children': genre = g
        
        color = genre_colors.get(genre, '#3498db')
        
        # Create image
        img = Image.new('RGB', (300, 400), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add title text
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Split title into multiple lines if needed
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Simple line break logic
            if len(test_line) > 20:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text
        y_position = 150
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (300 - text_width) / 2
            draw.text((x, y_position), line, fill='white', font=font)
            y_position += text_height + 5
        
        # Add genre label
        draw.text((10, 10), genre, fill='white', font=font)
        
        # Save image
        img.save(f'static/images/books/{cover}')
        print(f'Created: {cover}')
    
    # Create default.jpg
    img = Image.new('RGB', (300, 400), color='#95a5a6')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((80, 180), 'No Cover', fill='white', font=font)
    draw.text((60, 220), 'Available', fill='white', font=font)
    img.save('static/images/books/default.jpg')
    print('Created: default.jpg')
    
    print(f"\nCreated {len(book_covers) + 1} placeholder images!")

if __name__ == '__main__':
    create_placeholder_images()