#!/usr/bin/env python3
"""FixAnything - Claude API minimal token usage"""
import argparse, json, os, re, sys, time, urllib.request, urllib.parse
from pathlib import Path
from anthropic import Anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
TUTORIALS_FILE = Path(__file__).parent / "data" / "tutorials.json"

CATEGORIES = ["Home & Plumbing", "Home & Cleaning", "Home & Repair", "Home & Electrical",
    "Home & Pets", "Kitchen & Appliances", "Kitchen & Cookware", "Kitchen & Pests",
    "Clothing & Laundry", "Clothing & Shoes", "Clothing & Repair", "Personal Care"]

TOPICS = [
    "remove paint stains jeans", "fix sagging cabinet door", "remove coffee ring wood",
    "fix loose shower grout", "remove tape residue walls", "clean coffee maker holes",
    "fix water stains leather", "remove ink fabric", "fix stuck zipper",
    "clean shower mineral buildup", "remove pet smell plastic", "fix squeaky hinges",
    "remove wax buildup floor", "clean kettle lime deposits", "fix cracked grout",
    "remove rust stains", "clean bathroom mold", "fix squeaky new shoes",
    "remove dried caulk", "clean garbage disposal", "remove paint splatter",
    "fix loose door knob", "remove sticker residue", "clean oven window",
] * 5  # Pool of topics

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
    
    topics = [args.topic] if args.topic else TOPICS[:args.count]
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
