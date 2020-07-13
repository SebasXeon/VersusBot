#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------
# Import modules
# ---------------------------
import sys, os, json, random, facebook, textwrap
from PIL import Image, ImageFont, ImageDraw

# ---------------------------
# Vars
# ---------------------------
parts = []
config = []
msg = ""
wmsg = ""

reacts = ['Love','Haha','Wow','Sad','Angry']

# // Dirs
data_dir = 'data/'
assets_dir = 'assets/'
backgrounds_dir = assets_dir + 'backgrounds/'
reacts_dir = assets_dir + 'reactions/'
sources_dir = 'sources/'


# // Designs
duels_overlay = [
    {
        "over1":"duel_type1_overlay1.png",
        "over2":"duel_type1_overlay2.png",
        "text_wrap":11,
        "font_size":72,
        "text_offset":75,
        "text_wrap2":17,
        "font_size2":45
    },
    {
        "over1":"duel_type2_overlay1.png",
        "over2":"duel_type2_overlay2.png"
    },
    {
        "over1":"duel_type3_overlay1.png",
        "over2":"duel_type3_overlay2.png",
        "text_wrap":12,
        "font_size":45,
        "text_offset":50,
        "text_wrap2":14,
        "font_size2":35
    }
]
duels_design = [
    [
        {
            "x":15,
            "y":430,
            "size":475,
            "react_x":179,
            "react_y":834,
            "react_size":145,
            "font_x":253,
            "font_y":255
        },
        {
            "x":510,
            "y":430,
            "size":475,
            "react_x":675,
            "react_y":834,
            "react_size":145,
            "font_x":748,
            "font_y":255
        }
    ],
    [],
    [
        {
            "x":128,
            "y":216,
            "size":250,
            "react_x":63,
            "react_y":415,
            "react_size":115,
            "font_x":252,
            "font_y":80
        },
        {
            "x":657,
            "y":216,
            "size":250,
            "react_x":856,
            "react_y":415,
            "react_size":115,
            "font_x":782,
            "font_y":80
        },
        {
            "x":128,
            "y":678,
            "size":250,
            "react_x":311,
            "react_y":877,
            "react_size":115,
            "font_x":252,
            "font_y":546
        },
        {
            "x":657,
            "y":678,
            "size":250,
            "react_x":592,
            "react_y":877,
            "react_size":115,
            "font_x":782,
            "font_y":546
        }
    ]
]
type2_winners_design = [
    {
        "x":250,
        "y":345,
        "size":300,
        "react_x":294,
        "react_y":220,
        "react_size":86,
        "font_x":442,
        "font_y":240,
        "font_size":34
    },
    {
        "x":19,
        "y":614,
        "size":200,
        "react_x":21,
        "react_y":516,
        "react_size":64,
        "font_x":123,
        "font_y":530,
        "font_size":26
    },
    {
        "x":580,
        "y":614,
        "size":200,
        "react_x":716,
        "react_y":516,
        "react_size":64,
        "font_x":678,
        "font_y":530,
        "font_size":26
    },
]

# ---------------------------
# Functions
# ---------------------------
def load_parts():
    global parts
    with open(data_dir + "parts.json", encoding='utf-8') as f:
        parts = json.load(f)
def load_config():
    global config
    with open(data_dir + "config.json", encoding='utf-8') as f:
        config = json.load(f)
def save_config():
    with open(data_dir + "config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
def get_random_from(arr, size):
    props = []
    while len(props) < size:
        prop = random.choice(arr)
        if not prop in props:
            props.append(prop)
    return props
def white_thumb(imgto, size):
    imgto.thumbnail(size,Image.ANTIALIAS)
    imgto = imgto.convert("RGBA")
    background = Image.new('RGBA', size, (255, 255, 255, 255))
    img_w, img_h = imgto.size
    bg_w, bg_h = background.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(imgto, offset, mask=imgto)
    
    return background
# ---------------------------
# Classes
# ---------------------------
class FB:
    def __init__(self):
        self.graph = facebook.GraphAPI(access_token = config["access_token"])
    def post(self, msg, filename):
        return self.graph.put_photo(image=open(filename, 'rb'), message=msg)
    def reacts(self, post_id, reaction):
        post = self.graph.get_object(id="{}_{}".format(config['page_id'], post_id), fields='reactions.type({}).limit(0).summary(total_count)'.format(str(reaction).upper()))
        return int(post['reactions']['summary']['total_count'])
    def comment_photo(self, post_id, msg, filename):
        response = self.graph.put_photo(image=open(filename, 'rb'), no_story=True, published=False)
        self.graph.put_object(parent_object="{}_{}".format(config['page_id'], post_id), connection_name='comments', message=msg, attachment_id=response['id'])
    def comment(self, post_id, msg):
        self.graph.put_object(parent_object="{}_{}".format(config['page_id'], post_id), connection_name='comments', message=msg)

# ---------------------------
# Bot Functions & Classes
# ---------------------------
class last_round:
    def __init__(self):
        global wmsg
        face = FB()
        print("--- Getting last round reacts")
        last_duel = []

        tmp_entry = {}
        tmp_entry["id"] = config['last_post']['fighter1']
        tmp_entry["reacts"] = face.reacts(config['last_post']['post_id'], config['last_post']['reaction1'])
        tmp_entry["react_type"] = config['last_post']['reaction1']
        last_duel.append(tmp_entry)

        tmp_entry = {}
        tmp_entry["id"] = config['last_post']['fighter2']
        tmp_entry["reacts"] = face.reacts(config['last_post']['post_id'], config['last_post']['reaction2'])
        tmp_entry["react_type"] = config['last_post']['reaction2']
        last_duel.append(tmp_entry)

        if config['last_post']['type'] >= 1:
            tmp_entry = {}
            tmp_entry["id"] = config['last_post']['fighter3']
            tmp_entry["reacts"] = face.reacts(config['last_post']['post_id'], config['last_post']['reaction3'])
            tmp_entry["react_type"] = config['last_post']['reaction3']
            last_duel.append(tmp_entry)
        if config['last_post']['type'] == 2:
            tmp_entry = {}
            tmp_entry["id"] = config['last_post']['fighter4']
            tmp_entry["reacts"] = face.reacts(config['last_post']['post_id'], config['last_post']['reaction4'])
            tmp_entry["react_type"] = config['last_post']['reaction4']
            last_duel.append(tmp_entry)
        
        print("--- Calculating racts")
        # Get winner & redact Winners message
        self.results = sorted(last_duel, key = lambda i: i['reacts'],reverse=True)

        print(self.results)
        wmsg = "Last round winner: {0}, got {1} votes.\n\nResults:\n 1) {0}, {1} Votes.\n 2) {2}, {3} Votes".format(parts[self.results[0]["id"]]["name"], self.results[0]["reacts"], parts[self.results[1]["id"]]["name"], self.results[1]["reacts"])
        if config['last_post']['type'] >= 1:
            wmsg = "{}\n 3) {}, {} Votes.".format(wmsg, parts[self.results[2]["id"]]["name"], self.results[2]["reacts"])
        if config['last_post']['type'] == 2:
            wmsg = "{}\n 4) {}, {} Votes.".format(wmsg, parts[self.results[3]["id"]]["name"], self.results[3]["reacts"])
        print(wmsg)
        # Render image
        print("--- Rendering Winners image")
        self.image()

    def image(self):
        # // Create blank image
        img_final = Image.new('RGBA', (800, 1000), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img_final)    
        # // Dual 
        if config['last_post']['type'] == 0:
            # // Load & paste winner image
            img_entry = Image.open(sources_dir + parts[self.results[0]["id"]]["image_filename"],'r')
            img_entry = white_thumb(img_entry, (500, 500))
            img_final.paste(img_entry, (145, 225))

            # // Load & paste overlay
            img_overlay = Image.open(assets_dir + "winner1_overlay.png",'r')   
            img_final.paste(img_overlay, (0, 0), mask=img_overlay)

            # // Load & paste react
            img_react = Image.open(reacts_dir + self.results[0]["react_type"] + ".png",'r')   
            img_final.paste(img_react, (575, 650), mask=img_react)

            # // Load font & wrap name
            font = ImageFont.truetype(assets_dir + "RobotoMono-Bold.ttf", 64)
            wrapped_name = ""
            for line in textwrap.wrap(parts[self.results[0]["id"]]["name"], width=19):
                wrapped_name += line + "\n"
            w, h = draw.textsize(wrapped_name, font=font)
            
            # // Paste name & reacts
            draw.multiline_text((400 - (w / 2), 775), wrapped_name, (0,0,0),font=font, align="center")
            font = ImageFont.truetype(assets_dir + "RobotoMono-Bold.ttf", 32)
            w, h = draw.textsize(str(self.results[0]["reacts"]), font=font)
            draw.multiline_text((524 - (w / 2), 683), str(self.results[0]["reacts"]), (255,255,255),font=font, align="right")

        elif config['last_post']['type'] >= 1:
            # // Load & paste overlay
            img_overlay = Image.open(assets_dir + "winner2_overlay.png",'r')   
            img_final.paste(img_overlay, (0, 0), mask=img_overlay)

            for winner_dsg in type2_winners_design:
                index = type2_winners_design.index(winner_dsg)
                # // Load & paste winner image
                img_entry = Image.open(sources_dir + parts[self.results[index]["id"]]["image_filename"],'r')
                img_entry = white_thumb(img_entry, (winner_dsg["size"], winner_dsg["size"]))
                img_final.paste(img_entry, (winner_dsg["x"], winner_dsg["y"]))

                # // Load & paste react
                img_react = Image.open(reacts_dir + self.results[index]["react_type"] + ".png",'r')   
                img_react.thumbnail((winner_dsg["react_size"], winner_dsg["react_size"]),Image.ANTIALIAS)
                img_final.paste(img_react, (winner_dsg["react_x"], winner_dsg["react_y"]), mask=img_react)

                # // Paste name & reacts
                font = ImageFont.truetype(assets_dir + "RobotoMono-Bold.ttf", winner_dsg["font_size"])
                w, h = draw.textsize(str(self.results[index]["reacts"]), font=font)
                draw.multiline_text((winner_dsg["font_x"] - (w / 2), winner_dsg["font_y"]), str(self.results[index]["reacts"]), (255,255,255),font=font, align="center")

        # // Save final image
        img_final.save('tmp/winner_image.png')
            

class versus:
    def __init__(self):
        global msg
        self.duel_type = random.choice([0, 0, 2])

        self.fighters = get_random_from(parts, 2 + self.duel_type)
        self.reactions = get_random_from(reacts, 2 + self.duel_type)
        self.fighters[0]["figther_id"] = int(str(self.fighters[0]["image_filename"]).replace(".png",""))
        self.fighters[1]["figther_id"] = int(str(self.fighters[1]["image_filename"]).replace(".png",""))
        
        if self.duel_type >= 1: self.fighters[2]["figther_id"] = int(str(self.fighters[2]["image_filename"]).replace(".png",""))
        if self.duel_type == 2: self.fighters[3]["figther_id"] = int(str(self.fighters[3]["image_filename"]).replace(".png",""))

        msg = "{} vs {}".format(self.fighters[0]["name"], self.fighters[1]["name"])
        if self.duel_type >= 1: msg = "{} vs {}".format(msg, self.fighters[2]["name"])
        if self.duel_type == 2: msg = "{} vs {}".format(msg, self.fighters[3]["name"])
        msg = "{}\n\n{}".format(msg, wmsg)

        print(msg)

        print("--- Rendering versus image")
        self.image()  

        print("--- Posting versus")
        face = FB()
        graph_response = face.post(msg, 'tmp/versus_image.png')

        print("--- Commenting new post")
        if config['last_post']['post_id'] != "0":
            face.comment_photo(graph_response['id'], wmsg, 'tmp/winner_image.png')
        face.comment(graph_response['id'], "Love VersusBot? support me <3\nhttps://www.buymeacoffee.com/VersusBot")

        print("--- Saving config")
        config['last_post']['type'] = self.duel_type
        config['last_post']['post_id'] = graph_response['id']
        config['last_post']['fighter1'] = self.fighters[0]['figther_id']
        config['last_post']['fighter2'] = self.fighters[1]['figther_id']
        config['last_post']['reaction1'] = self.reactions[0]
        config['last_post']['reaction2'] = self.reactions[1]
        if self.duel_type >= 1: 
            config['last_post']['fighter3'] = self.fighters[2]['figther_id']
            config['last_post']['reaction3'] = self.reactions[2]
        if self.duel_type == 2: 
            config['last_post']['fighter4'] = self.fighters[3]['figther_id']
            config['last_post']['reaction4'] = self.reactions[3]
        save_config()
    def image(self):
        # // Create blank image
        img_final = Image.new('RGBA', (1000, 1000), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img_final)
        
        # // Render
        # // Load & paste overlay1
        img_background = Image.open(backgrounds_dir + "/" + random.choice(os.listdir(backgrounds_dir)),'r')   
        img_final.paste(img_background, (0, 0))
        # // Load & paste overlay1
        img_overlay = Image.open(assets_dir + duels_overlay[self.duel_type]["over1"],'r')   
        img_final.paste(img_overlay, (0, 0), mask=img_overlay)

        for fighter in self.fighters:
            index = self.fighters.index(fighter)
            # // Load & paste winner image
            img_entry = Image.open(sources_dir + fighter["image_filename"],'r')
            img_entry = white_thumb(img_entry, (duels_design[self.duel_type][index]["size"], duels_design[self.duel_type][index]["size"]))
            img_final.paste(img_entry, (duels_design[self.duel_type][index]["x"], duels_design[self.duel_type][index]["y"]))

            # // Load & paste react
            img_react = Image.open(reacts_dir + self.reactions[index] + ".png",'r')   
            img_react.thumbnail((duels_design[self.duel_type][index]["react_size"], duels_design[self.duel_type][index]["react_size"]),Image.ANTIALIAS)
            img_final.paste(img_react, (duels_design[self.duel_type][index]["react_x"], duels_design[self.duel_type][index]["react_y"]), mask=img_react)

            # // Load font & wrap name
            lines = 1
            if (len(fighter["name"]) <= duels_overlay[self.duel_type]["text_wrap"]*2):
                font = ImageFont.truetype(assets_dir + "RobotoMono-Bold.ttf", duels_overlay[self.duel_type]["font_size"])
                wrapped_name = ""
                for line in textwrap.wrap(fighter["name"], width=duels_overlay[self.duel_type]["text_wrap"]):
                    wrapped_name += line + "\n"
                    lines += 1
            if (len(fighter["name"]) > duels_overlay[self.duel_type]["text_wrap"]*2) or lines > 2:
                font = ImageFont.truetype(assets_dir + "RobotoMono-Bold.ttf", duels_overlay[self.duel_type]["font_size2"])
                wrapped_name = ""
                lx = 0
                for line in textwrap.wrap(fighter["name"], width=duels_overlay[self.duel_type]["text_wrap2"]):
                    wrapped_name += line + "\n"
                    lines += 1
                    lx += 1
                    if lx == 3:
                        wrapped_name = wrapped_name[:-1]+"..."
                        break
            w, h = draw.textsize(wrapped_name, font=font)
            
            x = duels_design[self.duel_type][index]["font_x"] - (w / 2)
            y = duels_design[self.duel_type][index]["font_y"]
            if lines == 1:
                y += duels_overlay[self.duel_type]["text_offset"]

            # // Paste name text border
            draw.multiline_text((x-1, y-1), wrapped_name, (0,0,0),font=font, align="center")
            draw.multiline_text((x+1, y-1), wrapped_name, (0,0,0),font=font, align="center")
            draw.multiline_text((x-1, y+1), wrapped_name, (0,0,0),font=font, align="center")
            draw.multiline_text((x+1, y+1), wrapped_name, (0,0,0),font=font, align="center")
            # // Paste name text
            draw.multiline_text((x, y), wrapped_name, (255,255,255),font=font, align="center")

        # // Load & paste overlay2
        img_overlay = Image.open(assets_dir + duels_overlay[self.duel_type]["over2"],'r')   
        img_final.paste(img_overlay, (0, 0), mask=img_overlay)
        # // Save final image
        img_final.save('tmp/versus_image.png')
# ---------------------------
# Bot
# ---------------------------
def main():
    global msg, config
    print("--- Loading...")
    load_config()
    load_parts()
    print(config['last_post']['post_id'])
    if "tournament" in sys.argv:
        print("--- Tournament mode")
    else:
        print("--- Normal mode")
        if config['last_post']['post_id'] != "0":
            print("--- Getting last round winner")
            last_round()
        versus()

# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    print("--- Starting...")
    main()