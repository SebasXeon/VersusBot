#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------
# Import modules
# ---------------------------
import pymongo, logging, random, colorsys, textwrap, json, facebook, os
from PIL import Image, ImageFont, ImageDraw, ImageOps
from bson.objectid import ObjectId

# ---------------------------
# Connect to DB
# ---------------------------
client = pymongo.MongoClient("ADD-MONGODB-URL")
db = client.VersusBot
entrys_col = db["entrys"]
week_col = db["week"]

# ---------------------------
# Vars and Settings
# ---------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s -[%(levelname)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

path = os.path.dirname(__file__) + '/'
dir_assets = path +'assets'
dir_font = path +'assets/font.ttf'
dir_data = 'data'
dir_entrys = 'images/'


# config
config = {}

# Reactions
reactions = [ "Love", "Wow", "Haha", "Sad"]

# Versus design
vs_design = [
    {
        'image_posX':15,
        'image_posY':228,
        'title_posX':15,
        'title_posY':65,
        'window_title_posX':25,
        'window_title_posY':206,
        "reaction_posX":228,
        "reaction_posY":769,
        "window_react_posX":238,
        "window_react_posY":747
    },
    {
        'image_posX':528,
        'image_posY':228,
        'title_posX':528,
        'title_posY':65,
        'window_title_posX':538,
        'window_title_posY':206,
        "reaction_posX":741,
        "reaction_posY":769,
        "window_react_posX":751,
        "window_react_posY":747
    }
]

# ---------------------------
# Functions
# ---------------------------
def load_config():
    # Load json
    with open(dir_data + '/config.json') as json_file:
        data = json.load(json_file)
    return data
    
def save_config(conf):
    # Save json
    with open(dir_data + '/config.json', 'w') as outfile:
        json.dump(conf, outfile, indent=4,  ensure_ascii=False)

def get_random_from_array(array, size):
    return random.sample(array, size)

def update_from_id(_id, update):
    filter = {"_id": ObjectId(_id)}
    newvalues = { "$set": update }
    entrys_col.update_one(filter, newvalues)

def make_white_thumbnail(imgto, size):
    # Make thumbnail from image
    imgto.thumbnail(size, resample =3)
    imgto = imgto.convert("RGBA")
    # Make white background
    background = Image.new('RGBA', size, (255, 255, 255, 255))
    # Center and paste image
    img_w, img_h = imgto.size
    bg_w, bg_h = background.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(imgto, offset, mask=imgto)
    # Return image
    return background
def flip_img(imgto, axis):
    if axis == 'x':
        imgto = ImageOps.mirror(imgto)
    elif axis == 'y':
        imgto = ImageOps.flip(imgto)
    return imgto

def make_thumbnail(imgto, size):
    # Make thumbnail from image
    imgto.thumbnail(size, resample =3)
    # Return image
    return imgto

def paste_images(img1, img2, size):
    background = Image.new('RGBA', size, (255, 255, 255, 255))
    bg_w, bg_h = background.size
    img_w, img_h = img1.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img1, offset, mask=img1)
    img_w, img_h = img2.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img2, offset, mask=img2)
    # Return image
    return background

def hsv2rgb(h, s, v):
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h / 360, s / 100, v / 100))

def get_text_dimensions(text, font):
    # Get text dimensions
    img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(text, font=font)
    return w, h

def make_winner_image(winner):
    # Make background image
    img_versus = Image.new('RGBA', (1024, 1024), hsv2rgb(random.randint(0, 359), 65, 99))
    # Make grid image
    img_grid = Image.open(dir_assets + '/FB_grid.png')
    # Paste grid image
    img_versus.paste(img_grid, (0, 0), mask=img_grid)
    # Make draw
    draw = ImageDraw.Draw(img_versus)
    # Draw winner
    # Get image
    img = Image.open(f"{dir_entrys}{winner['image_filename']}")
    # Resize image
    img = make_white_thumbnail(img, (480, 480))
    # Draw image
    img_versus.paste(img, (413,75))
    img_versus.paste(img, (272,197))
    # --------------------------------- TODO IMPROVE
    # Draw title
    wrapped_name = textwrap.wrap(winner['name'], width=30)[0:3]
    box_space_x = 20
    box_space_y = 70
    name_x = 83
    if len(wrapped_name) == 1: name_y = 800
    if len(wrapped_name) == 2: name_y = 780
    if len(wrapped_name) == 3: name_y = 760
    title_font = ImageFont.truetype(dir_font, 42)
    for line in wrapped_name:
        textW, textH = get_text_dimensions(line, title_font)
        # Draw black rectangle
        draw.rectangle((name_x, name_y, name_x + textW + box_space_x, name_y + box_space_y), fill=(0, 0, 0, 255))
        # Draw text
        draw.text((name_x + 14, name_y + 16), line, fill=(255, 255, 255, 255), font=title_font)
        name_y += 80
    # Load and paste overlay
    img_overlay = Image.open(dir_assets + '/FB_winner_overlay.png')
    img_versus.paste(img_overlay, (0, 0), mask=img_overlay)
    # Wrap name
    wrapped_name = textwrap.wrap(winner['name'], width=35)
    if len(wrapped_name) > 1:
        wrapped_name = wrapped_name[0] + '...'
    else: wrapped_name = wrapped_name[0]
    # Draw title in window
    draw.text((422, 53), wrapped_name, fill='#000000', font=ImageFont.truetype(dir_font, 14))
    draw.text((280, 175), wrapped_name, fill='#000000', font=ImageFont.truetype(dir_font, 14))

    # Save image
    logging.info('Saving image...')
    img_versus.save('winner.png')

def make_versus_image(entrys, reacts):
    # Make background image
    img_versus = Image.new('RGBA', (1024, 1024), hsv2rgb(random.randint(0, 359), 65, 99))
    # Random bool to add grid
    if random.randint(0, 1):
        # Make grid image
        img_grid = Image.open(dir_assets + '/FB_grid.png')
        # Paste grid image
        img_versus.paste(img_grid, (0, 0), mask=img_grid)
    # Make draw
    draw = ImageDraw.Draw(img_versus)
    # Draw entrys
    for i in range(0, 2):
        # Get entry
        entry = entrys[i]
        # Get reaction
        reaction = reacts[i]
        # Get image
        img = Image.open(f"{dir_entrys}{entry['image_filename']}")
        # Especials
        if entry['type'] == 1:
            img_o = Image.open(f"{dir_entrys}{entrys[i -1]['image_filename']}")
            img_o = make_thumbnail(img_o, (480, 480))
            img_o = flip_img(img_o, 'x')
            img = make_thumbnail(img, (480, 480))
            img = paste_images(img_o, img, (480, 480))
        elif entry['type'] == 2:
            img = Image.open(f"{dir_entrys}{entrys[i -1]['image_filename']}")
            img = flip_img(img, 'y')
            img.save(f"{dir_entrys}{entrys[i]['image_filename']}")
        elif entry['type'] == 3:
            img = Image.open(f"{dir_entrys}{entrys[i -1]['image_filename']}")
            img = ImageOps.invert(img)
            img.save(f"{dir_entrys}{entrys[i]['image_filename']}")

        # Resize image
        img = make_white_thumbnail(img, (480, 480))
        # Draw image
        img_versus.paste(img, (vs_design[i]['image_posX'], vs_design[i]['image_posY']))
        # --------------------------------- TODO IMPROVE
        # Draw title
        wrapped_name = textwrap.wrap(entry['name'], width=20)
        box_space_x = 20
        if len(wrapped_name) == 2:
            wrapped_name = wrapped_name[0:2]
            vs_design[i]['title_posY'] -= 32
        if len(wrapped_name) > 2:
            wrapped_name = textwrap.wrap(entry['name'], width=30)[0:3]
            vs_design[i]['title_posY'] = 8
            if len(wrapped_name) == 2: vs_design[i]['title_posY'] = 40
            text_space = 58
            box_space_y = 60
            title_font = ImageFont.truetype(dir_font, 24)
        else: 
            text_space = 68
            box_space_y = 70
            title_font = ImageFont.truetype(dir_font, 32)
        for line in wrapped_name:
            textW, textH = get_text_dimensions(line, title_font)
            # Draw black rectangle
            draw.rectangle((vs_design[i]['title_posX'], vs_design[i]['title_posY'], vs_design[i]['title_posX'] + textW + box_space_x, vs_design[i]['title_posY'] + box_space_y), fill=(0, 0, 0, 255))
            # Draw text
            draw.text((vs_design[i]['title_posX'] + 14, vs_design[i]['title_posY'] + 16), line, fill=(255, 255, 255, 255), font=title_font)
            vs_design[i]['title_posY'] += text_space
        # Load reaction
        img_reaction = Image.open(dir_assets + '/reactions/' + reaction + '.png')
        # Resize image
        img_reaction = make_white_thumbnail(img_reaction, (200, 200))
        # Paste reaction
        img_versus.paste(img_reaction, (vs_design[i]['reaction_posX'], vs_design[i]['reaction_posY']), mask=img_reaction)

    # Load and paste overlay
    img_overlay = Image.open(dir_assets + '/FB_overlay.png')
    img_versus.paste(img_overlay, (0, 0), mask=img_overlay)
    # Draw window title
    for i in range(0, 2):
        # Get entry
        entry = entrys[i]
        # Get reaction
        reaction = reacts[i]
        # Wrap name
        wrapped_name = textwrap.wrap(entry['name'], width=35)
        if len(wrapped_name) > 1:
            wrapped_name = wrapped_name[0] + '...'
        else: wrapped_name = wrapped_name[0]
        # Draw title in window
        draw.text((vs_design[i]['window_title_posX'], vs_design[i]['window_title_posY']), wrapped_name, fill='#000000', font=ImageFont.truetype(dir_font, 14))
        # Draw reaction title in window
        draw.text((vs_design[i]['window_react_posX'], vs_design[i]['window_react_posY']), reaction, fill='#000000', font=ImageFont.truetype(dir_font, 14))
    # Draw VersusBot title
    draw.text((380, 548), 'VersusBot', fill='#000000', font=ImageFont.truetype(dir_font, 14))
    # Save image
    logging.info('Saving image...')
    img_versus.save('versus.png')
# ---------------------------
# main
# ---------------------------
def main():
    global config
    logging.info('VersusBot started')
    # Load config
    config = load_config()
    # Get two random entries
    logging.info('Picking two random entries')
    
    entrys = []
    trys = 0
    while len(entrys) < 2:
        if trys > 5:
            logging.error('Could not pick two random entries from DB')
            return
        try:
            entrys = list(entrys_col.aggregate([{ '$sample': { 'size': 2 } }]))
            if 's_name' in entrys[0].keys() and 's_name' in entrys[1].keys():
                entrys = []
            elif week_col.find({'entry_id': str(entrys[0]['_id'])}).count() > 0 or week_col.find({'entry_id': str(entrys[1]['_id'])}).count() > 0:
                entrys = []
        except Exception as e:
            logging.error(e)
            logging.info('Trying again')
            trys += 1
    
    # Convert _id to str
    for i in range(0, 2):
        entrys[i]['_id'] = str(entrys[i]['_id'])
        if 's_name' in entrys[i].keys():
            entrys[i]['name'] = str(entrys[i]['s_name']).replace('[name]', entrys[i -1]['name'])
            update_from_id(entrys[i]['_id'], {'name': entrys[i]['name']})
    
    # Get two random reactions
    reacts = get_random_from_array(reactions, 2)

    
    # Make Facebook Graph API connection
    logging.info('Connecting to Facebook Graph API')
    graph = facebook.GraphAPI(access_token=config['page_token'])

    # Get last round winner
    if config['last_round_id'] != "0":
        logging.info('Cheking last round winner')
        inp1_data = entrys_col.find_one({"_id": ObjectId(config['last_round'][0]['_id'])})
        inp2_data = entrys_col.find_one({"_id": ObjectId(config['last_round'][1]['_id'])})
        

        post = graph.get_object(id=f"{config['page_id']}_{config['last_round_id']}", fields='reactions.type({}).limit(0).summary(total_count)'.format(str(config['last_round'][0]['reaction']).upper()))
        inp1_data['votes'] = int(post['reactions']['summary']['total_count'])
        post = graph.get_object(id=f"{config['page_id']}_{config['last_round_id']}", fields='reactions.type({}).limit(0).summary(total_count)'.format(str(config['last_round'][1]['reaction']).upper()))
        inp2_data['votes'] = int(post['reactions']['summary']['total_count'])

        results = [inp1_data, inp2_data]

        results = sorted(results, key=lambda d: d['votes'], reverse=True) 

        last_msg = f"[LAST ROUND]\n{results[0]['name']} beat {results[1]['name']}\n\n{results[0]['name']} [{results[0]['votes']} reactions] - {results[1]['name']} [{results[1]['votes']} reactions]"


        logging.info('Making winner image')
        #make_winner_image(results[0])

        week_winner = {
            "entry_id":str(results[0]['_id']),
            "votes":results[0]['votes'],
            "won":True
        }
        week_looser= {
            "entry_id":str(results[1]['_id']),
            "votes":results[1]['votes'],
            "won":False
        }
        logging.info('Adding winner to week DB')
        week_col.insert_one(week_winner)
        week_col.insert_one(week_looser)
    else:
        last_msg = ""
    # TODO
    # Make versus msg
    vs_msg = f"'{entrys[0]['name']}' vs '{entrys[1]['name']}'\n\n{last_msg}"
    logging.info(vs_msg)
    # Make versus image
    logging.info('Making versus image')
    make_versus_image(entrys, reacts)
    # Upload image to Facebook
    logging.info('Uploading image to Facebook')
    post_response =  graph.put_photo(image=open('versus.png', 'rb'), message=f"{vs_msg}")
    # Upload last round winner comment | API not working
    """
    if last_msg != "":
        logging.info('Trying to post winner comment')
        try:
            response = graph.put_photo(image=open('winner.png', 'rb'), no_story=True, published=False)
            graph.put_object(parent_object="{}_{}".format(config['page_id'], post_response['id']), connection_name='comments', message=last_msg, attachment_id=response['id'])
        except:
            logging.info('Failing at posting comment')
            pass
    """
    # Set entrys to config
    config['last_round_id'] = post_response['id']
    config['last_round'] = [
        {
            '_id': entrys[0]['_id'],
            'reaction': reacts[0]
        },
        {
            '_id': entrys[1]['_id'],
            'reaction': reacts[1]
        }
    ]
    # Save config
    save_config(config)


if __name__ == "__main__":
    main()