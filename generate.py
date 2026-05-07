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
    # Clothing & Laundry — niche stain/fabric problems
    "remove ballpoint pen ink from microfiber couch cushion",
    "get dry erase marker out of cotton shirt",
    "remove set in armpit stain from colored shirt without bleach",
    "fix color bleed when washing mixed laundry load",
    "remove sunscreen white residue from black swimsuit",
    "get rid of musty smell in clothes left in washer too long",
    "remove motor oil stain from work jeans after washing",
    "fix shrunk wool cardigan that went through dryer",
    "remove yellow underarm stain from vintage white blouse",
    "get nail polish off denim without acetone",
    "remove self tanner stain from bed sheets",
    "fix white residue left on dark clothes after washing",
    "remove dry cleaning solvent smell from jacket",
    "get permanent marker off faux leather jacket",
    "remove fabric softener buildup from athletic wear",
    "fix velcro that has stopped sticking on jacket cuffs",
    "remove antiperspirant buildup from shirt underarms",
    "get chapstick residue out of dryer drum and clothes",
    "remove highlighter stain from school uniform shirt",
    "fix elastic waistband that has gone loose without sewing",
    # Clothing & Shoes — very specific shoe problems
    "remove black scuff mark from white rubber shoe sole",
    "fix leather boot heel that is separating from sole",
    "remove green oxidation from copper shoe eyelets",
    "get mold off leather dress shoes stored in humid closet",
    "fix suede shoe nap crushed flat by rain",
    "remove road salt tide marks from dark leather ankle boots",
    "fix shoe insole that keeps sliding forward while walking",
    "remove yellow glue stain left by old shoe insole",
    "restore faded black leather shoes without shoe polish",
    "fix patent leather shoes that have gone cloudy",
    "remove chewing gum stuck to sneaker sole",
    "fix canvas shoe toe box that has collapsed inward",
    "remove gasoline smell from work boots",
    "fix lace holes that have torn through canvas sneakers",
    "restore cracked rubber rain boot that leaks at fold",
    # Home & Cleaning — very specific niche problems
    "remove hard water stain ring inside stainless steel water bottle",
    "clean silicone baking mat that has absorbed fish smell",
    "remove rust stain left by shaving cream can on bathroom shelf",
    "get black mold out of rubber seal on front load washer door",
    "remove calcium deposits inside electric steam iron",
    "clean yellow residue left by hard water on chrome shower fixture",
    "remove cooking spray residue buildup from air fryer basket",
    "get rid of musty smell inside antique wooden dresser drawer",
    "remove grease splatter from painted kitchen wall behind stove",
    "clean inside of rarely used guest bathroom with pink mold",
    "remove brown tannin stain from inside white ceramic teapot",
    "get permanent marker off painted interior door",
    "remove adhesive left by command strip on painted drywall",
    "clean foggy headlight lens with household items",
    "remove water stain from popcorn ceiling without painting",
    "get rid of cigarette smell in room bought from smoker",
    "remove yellow wax buildup from old vinyl floor tiles",
    "clean inside of smelly top loading washing machine agitator",
    "remove dried liquid fabric softener spill from carpet",
    "get candle soot off white painted ceiling above fireplace",
    "remove sticky residue left by price tag on glass picture frame",
    "clean discolored silicone caulk around kitchen sink without replacing",
    "remove dried bird dropping stain from car paint",
    "get crayon off textured wallpaper without removing paint",
    "remove rust ring left by cast iron pan on granite countertop",
    # Home & Plumbing — niche specific problems
    "fix toilet that flushes but leaves skid marks every time",
    "stop single handle shower valve that drips only when set to hot",
    "fix bathroom sink that drains slowly only in winter months",
    "remove sulfur egg smell from hot water only not cold",
    "fix outdoor hose bib that drips from handle not spout",
    "stop washing machine drain hose from backing up into standpipe",
    "fix kitchen faucet that loses pressure when dishwasher runs",
    "remove brown sediment coming out of hot water tap only",
    "fix toilet that randomly runs for three seconds then stops",
    "stop condensation dripping from cold water pipes in summer",
    "fix showerhead that sprays sideways from one clogged hole",
    "remove pink bacteria stain from toilet bowl at waterline",
    "fix bathroom sink stopper that won't stay up when pulled",
    "stop kitchen sink from making gurgling noise when draining",
    "fix outside spigot that drips inside wall during winter",
    # Home & Repair — very specific niche fixes
    "fix hairline crack in plaster wall that keeps reappearing after painting",
    "repair laminate floor plank that has swollen at edge near bathroom",
    "fix door that swings open or closed on its own",
    "repair stripped screw hole in hollow core door hinge",
    "fix window that fogs between double pane glass",
    "repair vinyl floor tile corner that keeps lifting up",
    "fix bifold closet door that jumps off track when closing",
    "repair chip in porcelain bathtub surface with matching finish",
    "fix cabinet drawer bottom that has fallen out",
    "repair loose spindle on wooden stair banister",
    "fix window blind cord that is jammed and won't pull down",
    "repair bubbled paint on bathroom ceiling near shower",
    "fix sliding glass door that is hard to open in summer heat",
    "repair cracked wooden window sill with outdoor exposure",
    "fix interior door handle that turns but won't open latch",
    # Home & Electrical — safe DIY niche fixes
    "fix bathroom exhaust fan that rattles loudly when running",
    "fix outdoor motion sensor light that stays on all the time",
    "replace dimmer switch that buzzes with LED bulbs",
    "fix doorbell that only works sometimes",
    "replace outlet that has stopped working on one side only",
    "fix ceiling fan that wobbles only at high speed",
    "replace bathroom vanity light fixture without turning off breaker",
    "fix smart plug that keeps dropping wifi connection",
    "replace pull chain switch inside ceiling fan",
    "fix outdoor outlet that stopped working after heavy rain",
    # Kitchen & Appliances — niche specific issues
    "fix refrigerator that makes loud noise only at night",
    "remove burnt plastic smell from oven after melted bag incident",
    "fix dishwasher that leaves white film on glasses every cycle",
    "remove coffee oil rancid smell from automatic grinder hopper",
    "fix microwave that sparks when heating certain containers",
    "clean refrigerator drip pan that smells without moving fridge",
    "fix stand mixer that vibrates and walks across counter",
    "remove metallic taste from brand new stainless steel water bottle",
    "fix blender lid that leaks at gasket during use",
    "clean burner cap on gas stove that won't light after cleaning",
    "fix refrigerator ice maker that produces hollow or small cubes",
    "remove hard water buildup from humidifier ultrasonic plate",
    "fix slow drip coffee maker that takes forty minutes to brew",
    "clean mold from rubber gasket inside bread machine pan seal",
    "fix toaster oven that burns top of food but undercooks bottom",
    # Kitchen & Cookware — very niche cookware problems
    "remove blue discoloration from stainless steel pan after high heat",
    "fix warped cast iron griddle that rocks on flat stove top",
    "remove white haze from anodized aluminum baking sheet",
    "restore sticky carbon steel wok that was washed with soap",
    "remove fishy smell absorbed into wooden cutting board",
    "fix enameled dutch oven chip that is starting to rust",
    "remove brown residue baked onto outside of glass casserole dish",
    "restore copper pan lining that has turned dark and patchy",
    "fix loose handle rivet on stainless steel frying pan",
    "remove stuck food from ceramic nonstick without scratching",
    # Kitchen & Pests — niche specific pest problems
    "get rid of tiny black beetles in flour pantry not weevils",
    "remove ants that are nesting inside kitchen wall outlet",
    "get rid of booklice in humid kitchen cabinet near sink",
    "stop earwigs from coming inside kitchen through gap under door",
    "remove cluster of fungus gnats living in kitchen compost bin",
    "get rid of psocids dust mites in sealed cereal boxes",
    "remove phorid flies that breed under rarely moved appliance",
    "stop cricket from inside kitchen wall that chirps at night",
    "get rid of drugstore beetle in dried herbs and spice cabinet",
    "remove ghost ants trailing along kitchen countertop grout line",
    # Home & Pets — very specific pet problems
    "remove cat urine smell from air vent that was sprayed inside",
    "fix dog scratch damage on inside of wooden front door",
    "remove fish tank algae smell from room after tank removal",
    "get rid of hamster cage ammonia smell in small bedroom",
    "remove pet rabbit urine scale from plastic litter box corners",
    "fix carpet pull damage made by cat in front of closed door",
    "remove bird dander smell from room after cage removed",
    "clean white chalky mineral deposits in reptile water dish",
    "remove dog drool stain from fabric car seat headrest",
    "get rid of wet dog smell that soaked into foam sofa cushion",
    # Personal Care — very niche specific problems
    "remove self tanner from palms of hands after application",
    "fix broken powder compact that has shattered in makeup bag",
    "remove hair dye stain from grout around bathroom sink",
    "fix eyebrow pencil that has become too soft and waxy in summer",
    "remove green tint from blonde hair after swimming in chlorine pool",
    "fix perfume that has gone off and smells like vinegar",
    "remove mascara stain from pillowcase that has been through dryer",
    "treat contact dermatitis rash from new watch band metal",
    "fix nail polish that bubbles up every time it is applied",
    "remove semi permanent hair dye faster without bleach",
    "fix foundation that has separated in bottle and looks streaky",
    "remove fake tan streak lines from ankles and wrists",
    "treat white bumps on upper arms that look like permanent goosebumps",
    "remove lip liner stain from skin around lips after wearing all day",
    "fix cuticles that keep splitting and bleeding in dry winter months",
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
    """Generate a detailed, high-quality tutorial for AdSense approval and SEO."""
    prompt = f"""Write a detailed, practical how-to guide for: {topic}

Return valid JSON matching this exact structure:
{{
  "id": "url-slug-here",
  "title": "How to [specific title]",
  "category": "Home & Cleaning",
  "difficulty": "Easy",
  "time": "15 min",
  "tags": ["tag1","tag2","tag3","tag4","tag5"],
  "description": "One sentence summary of what this guide solves.",
  "intro": "2-3 sentences explaining why this problem happens and why this solution works. Be specific and helpful.",
  "whatYouNeed": ["item1","item2","item3","item4"],
  "steps": [
    {{"title": "Step title", "content": "Detailed 2-3 sentence explanation of exactly what to do and why it works."}}
  ],
  "warnings": ["Important caution if relevant"],
  "relatedIds": ["related-slug-1","related-slug-2","related-slug-3"]
}}

Requirements:
- Title must be specific and niche — include the exact material, product type, or scenario (e.g. "How to Remove Road Salt Stains from Dark Leather Ankle Boots" not "How to Clean Boots")
- At least 7 detailed steps with 2-3 sentences each explaining exactly what to do and why it works
- intro must explain specifically why this particular problem happens (the chemistry, the material, the cause) — not generic
- steps must have precise, actionable detail — include specific products, quantities, wait times, and motions where relevant
- warnings must flag anything that could damage the material or make the problem worse
- category must be one of: Home & Plumbing, Home & Cleaning, Home & Repair, Home & Electrical, Home & Pets, Kitchen & Appliances, Kitchen & Cookware, Kitchen & Pests, Clothing & Laundry, Clothing & Shoes, Clothing & Repair, Personal Care"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            system="Output ONLY valid JSON. No markdown fences. No commentary."
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

        # Fetch topic-relevant hero image from Pexels
        if not article.get("image"):
            img = fetch_pexels_image(article.get("title", topic))
            if img:
                article["image"] = img
            else:
                seed = abs(hash(article["id"])) % 1000
                article["image"] = f"https://picsum.photos/seed/{seed}/800/450"

        # Fetch step images for key steps (steps 1, 3, 5)
        if not article.get("stepImages") and article.get("steps"):
            step_imgs = []
            for idx in [0, 2, 4]:
                if idx < len(article["steps"]):
                    q = article["steps"][idx]["title"] + " " + topic
                    img = fetch_pexels_image(q)
                    step_imgs.append(img)
                else:
                    step_imgs.append(None)
            article["stepImages"] = step_imgs

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
