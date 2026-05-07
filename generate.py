#!/usr/bin/env python3
"""FixAnything - Claude API minimal token usage"""
import argparse, json, os, random, re, sys, time, urllib.request, urllib.parse
from pathlib import Path
from anthropic import Anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
TUTORIALS_FILE = Path(__file__).parent / "data" / "tutorials.json"

CATEGORIES = ["Home & Plumbing", "Home & Cleaning", "Home & Repair", "Home & Electrical",
    "Home & Pets", "Kitchen & Appliances", "Kitchen & Cookware", "Kitchen & Pests",
    "Clothing & Laundry", "Clothing & Shoes", "Clothing & Repair", "Personal Care"]

TOPICS = [
    # Clothing & Laundry
    "remove paint stains jeans", "remove ink from fabric", "fix stuck zipper",
    "remove deodorant stains shirt", "unshrink wool sweater", "remove blood stain fabric",
    "wash down jacket at home", "remove red wine from white shirt", "fix hole in jeans",
    "remove sweat stains collar", "wash silk blouse at home", "remove grass stains",
    "remove bleach stain clothing", "fix stretched out collar", "remove lipstick from fabric",
    "remove chocolate stain clothes", "wash delicate fabrics by hand", "remove mud from clothes",
    "fix pilling on sweater", "remove static cling clothes",
    # Clothing & Shoes
    "fix squeaky new shoes", "remove salt stains boots", "waterproof leather shoes",
    "stretch tight shoes at home", "remove scuff marks leather shoes", "clean white sneakers",
    "fix broken shoe sole", "remove water stains suede", "clean canvas shoes",
    "remove smell from shoes", "fix worn down shoe heel", "clean patent leather shoes",
    "remove mold from shoes", "fix cracked leather boots", "clean shoe insoles",
    # Home & Cleaning
    "remove tape residue walls", "clean bathroom mold", "remove wax buildup floor",
    "clean oven window inside", "remove hard water shower glass", "clean grout between tiles",
    "remove smoke smell room", "clean ceiling fan blades", "remove crayon from wall",
    "clean window tracks", "remove rust from bathtub", "clean under refrigerator",
    "remove mildew from shower curtain", "clean garbage disposal smell", "remove pet hair carpet",
    "clean baseboards quickly", "remove yellow stains from white wall", "clean light switches",
    "remove limescale from toilet", "clean air vents dust", "remove candle wax carpet",
    "clean washing machine drum", "remove soap scum shower door", "clean stainless steel sink",
    "remove coffee stain carpet", "clean microwave splatter", "remove mold from caulk",
    "clean oven racks without chemicals", "remove grease kitchen backsplash", "clean refrigerator coils",
    # Home & Plumbing
    "fix loose shower grout", "fix dripping faucet", "unclog bathroom sink",
    "fix running toilet", "increase low water pressure", "fix leaky pipe joint",
    "unclog shower drain", "fix toilet that won't flush", "replace toilet flapper",
    "fix garbage disposal hum", "stop pipes banging walls", "fix slow draining tub",
    "replace showerhead", "fix outdoor faucet drip", "unclog kitchen sink without chemicals",
    "fix toilet rocking base", "replace sink aerator", "fix shower diverter",
    "stop toilet tank condensation", "fix sump pump alarm",
    # Home & Repair
    "fix squeaky hinges", "remove sticker residue", "patch hole in drywall",
    "fix loose door knob", "fix door that sticks", "fix squeaky floorboard",
    "repair window screen hole", "fix loose cabinet hinge", "reattach peeling wallpaper",
    "fix sagging cabinet door", "repair chipped wooden furniture", "fix sticky drawer",
    "reglue loose laminate floor", "fix cracked tile without replacing", "repair torn window screen",
    "fix loose towel bar", "repair dent in wood floor", "fix door that won't latch",
    "repair split wood furniture", "fix wobbly chair leg",
    # Home & Electrical
    "fix flickering light", "reset tripped circuit breaker", "fix loose electrical outlet",
    "replace light switch", "fix ceiling fan wobble", "replace doorbell button",
    "fix lamp that flickers", "replace bathroom exhaust fan", "fix dead outlet",
    "wire new light fixture",
    # Kitchen & Appliances
    "clean coffee maker holes", "descale electric kettle", "fix refrigerator not cooling",
    "clean dishwasher filter", "fix microwave turntable", "descale coffee machine",
    "clean toaster crumb tray", "fix ice maker not working", "clean blender properly",
    "fix oven temperature inaccurate", "clean range hood filter", "fix dishwasher not draining",
    "clean food processor blades", "fix slow coffee maker", "clean electric griddle",
    # Kitchen & Cookware
    "remove coffee ring wood table", "season cast iron pan", "fix warped pan",
    "remove burnt food pot", "clean stained cutting board", "remove rust cast iron",
    "restore nonstick pan", "clean copper pots", "remove mineral deposits kettle",
    "sharpen kitchen knives at home",
    # Kitchen & Pests
    "get rid of fruit flies fast", "remove ants from kitchen", "get rid of pantry moths",
    "keep mice out of kitchen", "get rid of cockroaches kitchen", "remove drain flies",
    "keep spiders out of house", "get rid of gnats houseplants", "remove silverfish bathroom",
    "prevent weevils in flour",
    # Home & Pets
    "remove pet smell plastic", "clean pet urine from mattress", "remove dog smell sofa",
    "clean pet hair from car seats", "remove cat scratch marks furniture",
    "get rid of fleas in carpet", "remove skunk smell dog", "clean pet water bowl slime",
    "remove pet hair from clothes dryer", "fix cat scratch on leather sofa",
    # Personal Care
    "fix broken nail at home", "remove slime from hair", "get gum out of hair",
    "fix frizzy hair humidity", "remove hair dye from skin", "treat ingrown hair",
    "remove gel nail polish at home", "fix chapped lips fast", "remove fake tan streaks",
    "treat sunburn at home", "remove hair from drain", "fix dry cracked heels",
    "remove mascara without remover", "treat razor burn", "remove wax from eyebrows at home",
]

client = Anthropic(api_key=API_KEY)

def fetch_pexels_image(query):
    """Fetch a relevant photo URL from Pexels."""
    if not PEXELS_KEY:
        return None
    try:
        q = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?query={q}&per_page=1&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["large"]
    except Exception:
        pass
    return None

def load_tutorials():
    return json.load(open(TUTORIALS_FILE)) if TUTORIALS_FILE.exists() else []

def save_tutorials(tutorials):
    with open(TUTORIALS_FILE, "w") as f:
        json.dump(tutorials, f, indent=2)
        f.write("\n")

def generate_tutorial(topic, existing_ids):
    """Ultra-minimal token usage with Haiku"""
    # Extremely terse prompt - ~30 tokens
    prompt = f"""Topic: {topic}. JSON (5 steps min, 2+ items): {{"id":"slug","title":"How to","category":"Home & Cleaning","difficulty":"Easy","time":"15min","tags":["a","b","c","d","e"],"description":"one line","intro":"2-3 lines","whatYouNeed":["item1","item2"],"steps":[{{"title":"step","content":"details"}}],"warnings":[],"relatedIds":["a","b","c"]}}"""
    
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            system="Output ONLY valid JSON. No markdown."
        )
        
        text = response.content[0].text.strip()

        # Extract JSON - find { and try parsing backwards from end
        start = text.find('{')
        if start < 0:
            return None

        # Try from end, moving backward in chunks
        for end in range(len(text), start, -1):
            try:
                article = json.loads(text[start:end])
                break  # Found valid JSON
            except json.JSONDecodeError:
                pass
        else:
            return None
        
        # Minimal validation
        if not article.get("id") or not article.get("title"):
            return None

        if article["id"] in existing_ids:
            article["id"] = article["id"] + "-alt"

        # Fetch topic-relevant image from Pexels
        if not article.get("image"):
            img = fetch_pexels_image(article.get("title", topic))
            if img:
                article["image"] = img
            else:
                # Fallback: unique picsum image
                seed = abs(hash(article["id"])) % 1000
                article["image"] = f"https://picsum.photos/seed/{seed}/800/450"

        return article
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--topic", type=str)
    args = parser.parse_args()

    tutorials = load_tutorials()
    existing_ids = {t["id"] for t in tutorials}

    print(f"Generating {args.count} tutorial(s) (Haiku - minimal tokens)...\n")
    
    topics = [args.topic] if args.topic else random.sample(TOPICS, min(args.count, len(TOPICS)))
    generated = []

    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] {topic[:30]}...", end=" ", flush=True)
        
        article = generate_tutorial(topic, existing_ids)
        
        if article:
            existing_ids.add(article["id"])
            tutorials.append(article)
            generated.append(article)
            print("✓")
        else:
            print("✗")

    if generated:
        save_tutorials(tutorials)
        print(f"\nSaved {len(generated)} → Total: {len(tutorials)}")
    else:
        print("\nNo tutorials generated.")

if __name__ == "__main__":
    main()
