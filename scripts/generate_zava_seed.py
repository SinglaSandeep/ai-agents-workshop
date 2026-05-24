"""One-shot generator for Zava products + campaigns seed JSON.

Run from repo root:

    python scripts/generate_zava_seed.py

Writes:
    src/mcp_servers/products/seed/products_seed.json
    src/mcp_servers/marketing/seed/marketing_seed.json

Deterministic — uses a fixed RNG seed so re-runs produce identical files.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

RNG = random.Random(42)

STORES = ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett", "online"]

# (category_id, prefix, label)
CATEGORIES = [
    ("paint", "PNT", "Paint"),
    ("power-tools", "PWT", "Power Tools"),
    ("hand-tools", "HND", "Hand Tools"),
    ("garden", "GRD", "Garden"),
    ("lumber", "LMB", "Lumber"),
    ("electrical", "ELC", "Electrical"),
    ("plumbing", "PLM", "Plumbing"),
    ("hardware", "HDW", "Hardware"),
]

# 6 products per category — name, brand, unit, price, description, tags
PRODUCTS_BY_CAT: dict[str, list[dict]] = {
    "paint": [
        {"name": "Premium Interior Paint — Eggshell White", "brand": "Zava Pro", "unit": "1 gallon", "price": 32.99,
         "description": "Low-VOC interior paint, dries in 1 hour, 400 sq ft coverage.", "tags": ["interior", "white", "low-voc"]},
        {"name": "Exterior Acrylic Latex — Slate Gray", "brand": "Zava Pro", "unit": "1 gallon", "price": 41.99,
         "description": "Weather-resistant exterior paint with 10-year warranty.", "tags": ["exterior", "gray", "acrylic"]},
        {"name": "Primer & Sealer — Stain Blocking", "brand": "Zava Basics", "unit": "1 gallon", "price": 24.99,
         "description": "High-hide primer for drywall, wood, and previously painted surfaces.", "tags": ["primer", "white"]},
        {"name": "Ceiling Paint — Flat White", "brand": "Zava Basics", "unit": "2 gallon", "price": 38.99,
         "description": "Splatter-resistant flat ceiling paint, one-coat coverage.", "tags": ["ceiling", "white", "flat"]},
        {"name": "Chalkboard Paint — Black", "brand": "Hobby House", "unit": "1 quart", "price": 14.99,
         "description": "Smooth matte finish for chalk-friendly walls and crafts.", "tags": ["specialty", "black"]},
        {"name": "Deck & Fence Stain — Cedar", "brand": "Zava Pro", "unit": "1 gallon", "price": 36.49,
         "description": "Semi-transparent oil-based stain, UV protection for outdoor wood.", "tags": ["exterior", "stain", "cedar"]},
    ],
    "power-tools": [
        {"name": "20V Cordless Drill / Driver Kit", "brand": "TorqueMax", "unit": "kit", "price": 129.00,
         "description": "1/2 in chuck, 2-speed, includes 2 batteries and charger.", "tags": ["cordless", "drill"]},
        {"name": "7-1/4 in Circular Saw — Corded", "brand": "TorqueMax", "unit": "each", "price": 89.00,
         "description": "15 amp motor, 5500 RPM, laser guide.", "tags": ["saw", "corded"]},
        {"name": "Compact Impact Driver — 18V", "brand": "TorqueMax", "unit": "kit", "price": 159.00,
         "description": "1500 in-lb torque, brushless motor, belt clip.", "tags": ["impact", "cordless"]},
        {"name": "Random Orbit Sander — 5 in", "brand": "FinishCraft", "unit": "each", "price": 64.99,
         "description": "Variable speed 7,000–12,000 OPM, hook-and-loop disc.", "tags": ["sander"]},
        {"name": "Reciprocating Saw — 12 amp", "brand": "TorqueMax", "unit": "each", "price": 99.00,
         "description": "Tool-free blade change, orbital action, 1-1/8 in stroke.", "tags": ["saw", "corded"]},
        {"name": "Wet/Dry Shop Vacuum — 12 gal", "brand": "ShopBuddy", "unit": "each", "price": 119.00,
         "description": "6 HP, HEPA filter, on-board accessory storage.", "tags": ["vacuum", "cleanup"]},
    ],
    "hand-tools": [
        {"name": "16 oz Steel Claw Hammer", "brand": "GripWell", "unit": "each", "price": 18.99,
         "description": "Forged steel head, hickory handle, balanced for framing.", "tags": ["hammer"]},
        {"name": "25 ft Tape Measure — Magnetic Hook", "brand": "GripWell", "unit": "each", "price": 22.49,
         "description": "1-1/4 in blade, nylon coating, belt clip.", "tags": ["measuring"]},
        {"name": "10 in Adjustable Wrench", "brand": "GripWell", "unit": "each", "price": 16.99,
         "description": "Chrome-vanadium steel, knurled thumb wheel, 1-1/8 in jaw capacity.", "tags": ["wrench"]},
        {"name": "Screwdriver Set — 12 Piece", "brand": "GripWell", "unit": "set", "price": 27.99,
         "description": "Phillips and slotted, magnetic tips, cushion grip.", "tags": ["screwdriver", "set"]},
        {"name": "Carpenter's Level — 24 in", "brand": "TrueLine", "unit": "each", "price": 32.99,
         "description": "Aluminum frame, 3 vials, magnetic base.", "tags": ["level"]},
        {"name": "Utility Knife with 10 Blades", "brand": "GripWell", "unit": "each", "price": 9.99,
         "description": "Retractable blade, quick-change mechanism.", "tags": ["knife"]},
    ],
    "garden": [
        {"name": "Bypass Pruner — 8 in", "brand": "Greenline", "unit": "each", "price": 24.99,
         "description": "High-carbon steel blade, ergonomic grip, sap groove.", "tags": ["pruner"]},
        {"name": "Garden Hose — 50 ft", "brand": "Greenline", "unit": "each", "price": 32.99,
         "description": "Kink-resistant, 5/8 in diameter, brass fittings.", "tags": ["hose"]},
        {"name": "All-Purpose Potting Mix", "brand": "Greenline", "unit": "1.5 cu ft bag", "price": 9.49,
         "description": "Peat moss, perlite, slow-release fertilizer.", "tags": ["soil"]},
        {"name": "Round-Point Shovel — 47 in", "brand": "DigPro", "unit": "each", "price": 28.99,
         "description": "Fiberglass handle, forged steel head, lifetime warranty.", "tags": ["shovel"]},
        {"name": "Drip Irrigation Starter Kit", "brand": "AquaFlow", "unit": "kit", "price": 49.99,
         "description": "50 ft tubing, 20 emitters, timer included.", "tags": ["irrigation"]},
        {"name": "LED Solar Path Lights — 8 pack", "brand": "Greenline", "unit": "pack", "price": 39.99,
         "description": "Dusk-to-dawn sensor, stainless steel finish.", "tags": ["lighting", "solar"]},
    ],
    "lumber": [
        {"name": "2x4x8 ft SPF Stud", "brand": "Zava Mill", "unit": "each", "price": 4.29,
         "description": "Construction-grade spruce-pine-fir, kiln dried.", "tags": ["framing"]},
        {"name": "Pressure-Treated 4x4x8 ft Post", "brand": "Zava Mill", "unit": "each", "price": 18.99,
         "description": "Ground-contact rated, .40 CCA treatment.", "tags": ["post", "treated"]},
        {"name": "3/4 in Plywood — 4x8 Sheet", "brand": "Zava Mill", "unit": "sheet", "price": 64.99,
         "description": "ACX grade, sanded one side, for cabinetry and shelving.", "tags": ["plywood"]},
        {"name": "Cedar Fence Board — 1x6x6 ft", "brand": "Zava Mill", "unit": "each", "price": 6.99,
         "description": "Western Red Cedar, dog-eared, naturally rot-resistant.", "tags": ["fence", "cedar"]},
        {"name": "OSB Sheathing — 7/16 in 4x8", "brand": "Zava Mill", "unit": "sheet", "price": 22.99,
         "description": "Structural panel for roof decking and wall sheathing.", "tags": ["sheathing"]},
        {"name": "Composite Deck Board — 12 ft Gray", "brand": "DeckLife", "unit": "each", "price": 42.99,
         "description": "Capped composite, 25-year fade warranty.", "tags": ["decking", "composite"]},
    ],
    "electrical": [
        {"name": "14/2 NM-B Romex — 250 ft", "brand": "SafeWire", "unit": "roll", "price": 89.00,
         "description": "Indoor copper electrical cable, 15 amp residential circuits.", "tags": ["wire", "romex"]},
        {"name": "15 Amp Decora Outlet — White", "brand": "SafeWire", "unit": "each", "price": 2.49,
         "description": "Tamper-resistant, residential grade.", "tags": ["outlet"]},
        {"name": "Smart Wi-Fi Light Switch", "brand": "BrightHome", "unit": "each", "price": 32.99,
         "description": "Works with Alexa & Google, no hub required.", "tags": ["smart", "switch"]},
        {"name": "LED A19 Bulb — 60W Equiv, 4-pack", "brand": "BrightHome", "unit": "pack", "price": 11.99,
         "description": "Soft white 2700K, 800 lumens, 15-year life.", "tags": ["bulb", "led"]},
        {"name": "GFCI Outlet — 20 Amp", "brand": "SafeWire", "unit": "each", "price": 18.99,
         "description": "Self-test, weather-resistant, for kitchens/baths/outdoors.", "tags": ["outlet", "gfci"]},
        {"name": "Extension Cord — 50 ft Outdoor 12 AWG", "brand": "SafeWire", "unit": "each", "price": 36.99,
         "description": "Heavy-duty, lighted end, 15 amp.", "tags": ["extension-cord"]},
    ],
    "plumbing": [
        {"name": "PEX Tubing — 1/2 in x 100 ft Red", "brand": "FlowRight", "unit": "roll", "price": 42.99,
         "description": "Hot-water rated PEX-B tubing.", "tags": ["pex", "tubing"]},
        {"name": "Single-Handle Kitchen Faucet — Brushed Nickel", "brand": "FlowRight", "unit": "each", "price": 119.00,
         "description": "Pull-down sprayer, ceramic cartridge, lifetime warranty.", "tags": ["faucet", "kitchen"]},
        {"name": "Wax Toilet Ring with Flange", "brand": "FlowRight", "unit": "each", "price": 5.49,
         "description": "Standard 3 in or 4 in toilet flange.", "tags": ["toilet"]},
        {"name": "Pipe Wrench — 14 in", "brand": "GripWell", "unit": "each", "price": 28.99,
         "description": "Cast iron, self-cleaning threads.", "tags": ["wrench", "plumbing"]},
        {"name": "Flexible Supply Line — 3/8 x 20 in", "brand": "FlowRight", "unit": "each", "price": 7.49,
         "description": "Braided stainless steel, for faucets and toilets.", "tags": ["supply-line"]},
        {"name": "PVC Cement & Primer Kit", "brand": "FlowRight", "unit": "kit", "price": 12.99,
         "description": "8 oz each, for schedule 40 PVC pipe joints.", "tags": ["pvc", "adhesive"]},
    ],
    "hardware": [
        {"name": "Drywall Screws — #6 x 1-5/8 in 1 lb", "brand": "FastenIt", "unit": "1 lb box", "price": 6.99,
         "description": "Phillips bugle head, coarse thread, black phosphate.", "tags": ["screws", "drywall"]},
        {"name": "Deck Screws — #10 x 3 in 5 lb", "brand": "FastenIt", "unit": "5 lb box", "price": 32.99,
         "description": "Star drive, coated for treated lumber.", "tags": ["screws", "deck"]},
        {"name": "Construction Adhesive — 10 oz", "brand": "BondMax", "unit": "tube", "price": 5.99,
         "description": "Heavy-duty polyurethane, indoor/outdoor.", "tags": ["adhesive"]},
        {"name": "Concrete Anchor Set — 3/8 x 3 in 25 pack", "brand": "FastenIt", "unit": "pack", "price": 19.99,
         "description": "Wedge anchors for fastening to concrete.", "tags": ["anchor", "concrete"]},
        {"name": "Cabinet Pull — 5 in Brushed Nickel 10 pack", "brand": "ZavaTouch", "unit": "pack", "price": 24.99,
         "description": "Modern handle pull for kitchen / bath cabinets.", "tags": ["cabinet", "pull"]},
        {"name": "Entry Lockset — Keyed Satin Nickel", "brand": "SafeGuard", "unit": "each", "price": 49.99,
         "description": "ANSI Grade 3, 6-pin keyway, 2 keys included.", "tags": ["lock", "entry"]},
    ],
}


def make_inventory(category: str, idx: int) -> tuple[dict, int]:
    """Per-store stock + reorder threshold.

    Special low-stock outliers are seeded for the killer demo query:
    paint at Seattle gets very low numbers so the orchestrator can detect
    soft sales + stock shortage during the Spring Paint Sale.
    """
    threshold = RNG.choice([10, 15, 20, 25])
    inv: dict[str, int] = {}
    for store in STORES:
        if store == "online":
            inv[store] = RNG.randint(150, 400)
        else:
            inv[store] = RNG.randint(15, 80)

    # Seattle paint shortage — drives the demo's killer query.
    if category == "paint":
        if idx == 0:  # ZV-PNT-001 (Premium Interior Eggshell)
            inv["seattle"] = 3
            inv["bellevue"] = 12
            inv["redmond"] = 7
        if idx == 1:  # ZV-PNT-002 (Exterior Slate Gray)
            inv["seattle"] = 8
        if idx == 2:  # primer
            inv["seattle"] = 11

    # A couple of other realistic low-stock outliers
    if category == "power-tools" and idx == 0:
        inv["spokane"] = 2
    if category == "lumber" and idx == 4:
        inv["everett"] = 5

    return inv, threshold


def build_products() -> list[dict]:
    products: list[dict] = []
    for category, prefix, _ in CATEGORIES:
        for idx, p in enumerate(PRODUCTS_BY_CAT[category], start=1):
            pid = f"ZV-{prefix}-{idx:03d}"
            inv, thresh = make_inventory(category, idx - 1)
            products.append(
                {
                    "id": pid,
                    "name": p["name"],
                    "category": category,
                    "brand": p["brand"],
                    "sku": pid,
                    "price_usd": p["price"],
                    "unit": p["unit"],
                    "description": p["description"],
                    "tags": [category] + p["tags"],
                    "inventory_by_store": inv,
                    "reorder_threshold": thresh,
                }
            )
    return products


# ---- Campaigns ---------------------------------------------------------
CAMPAIGNS: list[dict] = [
    # Active
    {"id": "ZV-CMP-2026-001", "name": "Spring Paint Sale 2026", "status": "active",
     "category": "paint", "start_date": "2026-04-01", "end_date": "2026-05-31",
     "stores": ["seattle", "bellevue", "tacoma", "online"],
     "featured_products": ["ZV-PNT-001", "ZV-PNT-002", "ZV-PNT-005"],
     "discount_percent": 20, "channel": ["in-store", "email", "social"],
     "target_audience": "DIY homeowners, weekend renovators",
     "budget_usd": 180000, "spend_usd": 62000,
     "impressions": 1850000, "clicks": 32000, "roi": None,
     "kb_brief": "ZV-CMP-2026-001_brief.md"},
    {"id": "ZV-CMP-2026-002", "name": "Pro Power-Tool Days", "status": "active",
     "category": "power-tools", "start_date": "2026-03-15", "end_date": "2026-04-15",
     "stores": ["seattle", "bellevue", "redmond", "kirkland", "online"],
     "featured_products": ["ZV-PWT-001", "ZV-PWT-003", "ZV-PWT-006"],
     "discount_percent": 15, "channel": ["in-store", "email", "youtube"],
     "target_audience": "Contractors, pro tradespeople",
     "budget_usd": 220000, "spend_usd": 95000,
     "impressions": 2400000, "clicks": 41000, "roi": None,
     "kb_brief": "ZV-CMP-2026-002_brief.md"},
    {"id": "ZV-CMP-2026-003", "name": "Garden Kickoff Weekend", "status": "active",
     "category": "garden", "start_date": "2026-03-21", "end_date": "2026-03-29",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett"],
     "featured_products": ["ZV-GRD-002", "ZV-GRD-003", "ZV-GRD-005"],
     "discount_percent": 25, "channel": ["in-store", "social", "radio"],
     "target_audience": "Suburban homeowners, garden enthusiasts",
     "budget_usd": 95000, "spend_usd": 88000,
     "impressions": 1100000, "clicks": 24000, "roi": None,
     "kb_brief": "ZV-CMP-2026-003_brief.md"},
    {"id": "ZV-CMP-2026-004", "name": "Deck-Building Workshop Series", "status": "active",
     "category": "lumber", "start_date": "2026-04-05", "end_date": "2026-06-30",
     "stores": ["bellevue", "redmond", "kirkland"],
     "featured_products": ["ZV-LMB-002", "ZV-LMB-006", "ZV-HDW-002"],
     "discount_percent": 10, "channel": ["in-store", "email"],
     "target_audience": "DIY homeowners with outdoor projects",
     "budget_usd": 45000, "spend_usd": 12000,
     "impressions": 380000, "clicks": 8200, "roi": None,
     "kb_brief": "ZV-CMP-2026-004_brief.md"},
    {"id": "ZV-CMP-2026-005", "name": "Smart Home Lighting Bundle", "status": "active",
     "category": "electrical", "start_date": "2026-03-01", "end_date": "2026-04-30",
     "stores": ["seattle", "bellevue", "online"],
     "featured_products": ["ZV-ELC-003", "ZV-ELC-004"],
     "discount_percent": 15, "channel": ["online", "social"],
     "target_audience": "Tech-forward homeowners",
     "budget_usd": 60000, "spend_usd": 38000,
     "impressions": 920000, "clicks": 19000, "roi": None,
     "kb_brief": None},
    # Planned
    {"id": "ZV-CMP-2026-006", "name": "Summer Project BBQ Hardware Promo", "status": "planned",
     "category": "hardware", "start_date": "2026-06-01", "end_date": "2026-07-04",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett", "online"],
     "featured_products": ["ZV-HDW-002", "ZV-HDW-004"],
     "discount_percent": 12, "channel": ["in-store", "email", "social"],
     "target_audience": "Outdoor DIY weekend warriors",
     "budget_usd": 70000, "spend_usd": 0,
     "impressions": 0, "clicks": 0, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-007", "name": "Back-to-School Tool Kit Giveaway", "status": "planned",
     "category": "hand-tools", "start_date": "2026-08-15", "end_date": "2026-09-15",
     "stores": ["seattle", "bellevue", "online"],
     "featured_products": ["ZV-HND-004", "ZV-HND-002"],
     "discount_percent": 0, "channel": ["social", "in-store"],
     "target_audience": "Students and new homeowners",
     "budget_usd": 28000, "spend_usd": 0,
     "impressions": 0, "clicks": 0, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-008", "name": "Plumbing-Pro Loyalty Push", "status": "planned",
     "category": "plumbing", "start_date": "2026-05-01", "end_date": "2026-05-31",
     "stores": ["tacoma", "everett", "spokane"],
     "featured_products": ["ZV-PLM-001", "ZV-PLM-004"],
     "discount_percent": 10, "channel": ["email"],
     "target_audience": "Independent plumbers",
     "budget_usd": 18000, "spend_usd": 0,
     "impressions": 0, "clicks": 0, "roi": None,
     "kb_brief": None},
    # Post-mortem (last year's results — Spring Paint Sale 2025 is required for the killer query)
    {"id": "ZV-CMP-2025-101", "name": "Spring Paint Sale 2025", "status": "post-mortem",
     "category": "paint", "start_date": "2025-04-01", "end_date": "2025-05-31",
     "stores": ["seattle", "bellevue", "tacoma", "online"],
     "featured_products": ["ZV-PNT-001", "ZV-PNT-002"],
     "discount_percent": 20, "channel": ["in-store", "email", "social"],
     "target_audience": "DIY homeowners, weekend renovators",
     "budget_usd": 160000, "spend_usd": 158400,
     "impressions": 1620000, "clicks": 29800, "roi": 1.42,
     "kb_brief": "post_mortem_2025_spring_paint.md"},
    {"id": "ZV-CMP-2025-102", "name": "Pro Power-Tool Days 2025", "status": "post-mortem",
     "category": "power-tools", "start_date": "2025-03-15", "end_date": "2025-04-15",
     "stores": ["seattle", "bellevue", "redmond", "online"],
     "featured_products": ["ZV-PWT-001", "ZV-PWT-003"],
     "discount_percent": 15, "channel": ["in-store", "email", "youtube"],
     "target_audience": "Contractors, pro tradespeople",
     "budget_usd": 200000, "spend_usd": 196000,
     "impressions": 2280000, "clicks": 38600, "roi": 2.18,
     "kb_brief": "post_mortem_2025_pro_power_tools.md"},
    {"id": "ZV-CMP-2025-103", "name": "Holiday Hardware Gift Guide 2025", "status": "post-mortem",
     "category": "hardware", "start_date": "2025-11-15", "end_date": "2025-12-24",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett", "online"],
     "featured_products": ["ZV-HDW-005", "ZV-HDW-006"],
     "discount_percent": 18, "channel": ["online", "social", "email"],
     "target_audience": "Gift-givers, last-minute shoppers",
     "budget_usd": 120000, "spend_usd": 118000,
     "impressions": 2050000, "clicks": 47000, "roi": 1.85,
     "kb_brief": None},
    {"id": "ZV-CMP-2025-104", "name": "Fall Garden Cleanup 2025", "status": "post-mortem",
     "category": "garden", "start_date": "2025-09-15", "end_date": "2025-10-31",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett"],
     "featured_products": ["ZV-GRD-001", "ZV-GRD-004"],
     "discount_percent": 20, "channel": ["in-store", "email"],
     "target_audience": "Suburban homeowners",
     "budget_usd": 55000, "spend_usd": 53800,
     "impressions": 720000, "clicks": 15300, "roi": 1.61,
     "kb_brief": None},
    {"id": "ZV-CMP-2025-105", "name": "Bathroom Refresh 2025", "status": "post-mortem",
     "category": "plumbing", "start_date": "2025-06-01", "end_date": "2025-07-15",
     "stores": ["seattle", "bellevue", "online"],
     "featured_products": ["ZV-PLM-002", "ZV-PLM-005"],
     "discount_percent": 15, "channel": ["online", "social"],
     "target_audience": "Homeowners doing bath remodels",
     "budget_usd": 70000, "spend_usd": 68500,
     "impressions": 980000, "clicks": 22000, "roi": 1.32,
     "kb_brief": None},
    # A few more for volume
    {"id": "ZV-CMP-2026-009", "name": "Lumber Member Pricing Week", "status": "active",
     "category": "lumber", "start_date": "2026-03-20", "end_date": "2026-03-27",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett"],
     "featured_products": ["ZV-LMB-001", "ZV-LMB-003"],
     "discount_percent": 8, "channel": ["in-store", "email"],
     "target_audience": "Pro contractors, frequent buyers",
     "budget_usd": 35000, "spend_usd": 21000,
     "impressions": 410000, "clicks": 9700, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-010", "name": "Hand-Tool Essentials Promo", "status": "active",
     "category": "hand-tools", "start_date": "2026-04-01", "end_date": "2026-04-30",
     "stores": ["online"],
     "featured_products": ["ZV-HND-001", "ZV-HND-002", "ZV-HND-003"],
     "discount_percent": 10, "channel": ["online", "email"],
     "target_audience": "First-time homeowners",
     "budget_usd": 22000, "spend_usd": 9500,
     "impressions": 280000, "clicks": 6100, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-011", "name": "Smart Plumbing Demo Days", "status": "planned",
     "category": "plumbing", "start_date": "2026-06-15", "end_date": "2026-06-22",
     "stores": ["seattle", "bellevue"],
     "featured_products": ["ZV-PLM-002"],
     "discount_percent": 12, "channel": ["in-store", "social"],
     "target_audience": "Kitchen remodelers",
     "budget_usd": 16000, "spend_usd": 0,
     "impressions": 0, "clicks": 0, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-012", "name": "Pro Day — Electrical Contractors", "status": "active",
     "category": "electrical", "start_date": "2026-03-10", "end_date": "2026-03-31",
     "stores": ["seattle", "tacoma", "spokane"],
     "featured_products": ["ZV-ELC-001", "ZV-ELC-005"],
     "discount_percent": 12, "channel": ["in-store", "email"],
     "target_audience": "Licensed electricians",
     "budget_usd": 38000, "spend_usd": 27000,
     "impressions": 490000, "clicks": 11200, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-013", "name": "Earth Day Garden Bundle", "status": "planned",
     "category": "garden", "start_date": "2026-04-22", "end_date": "2026-04-29",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "online"],
     "featured_products": ["ZV-GRD-003", "ZV-GRD-005"],
     "discount_percent": 15, "channel": ["social", "email"],
     "target_audience": "Eco-conscious homeowners",
     "budget_usd": 30000, "spend_usd": 0,
     "impressions": 0, "clicks": 0, "roi": None,
     "kb_brief": None},
    {"id": "ZV-CMP-2025-106", "name": "Winter Storm Prep 2025", "status": "post-mortem",
     "category": "electrical", "start_date": "2025-11-01", "end_date": "2025-12-15",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett"],
     "featured_products": ["ZV-ELC-006"],
     "discount_percent": 10, "channel": ["in-store", "email"],
     "target_audience": "PNW homeowners",
     "budget_usd": 25000, "spend_usd": 24500,
     "impressions": 380000, "clicks": 8800, "roi": 1.47,
     "kb_brief": None},
    {"id": "ZV-CMP-2026-014", "name": "DIY Saturday Workshops", "status": "active",
     "category": "hand-tools", "start_date": "2026-03-01", "end_date": "2026-12-31",
     "stores": ["seattle", "bellevue", "tacoma", "redmond", "kirkland", "spokane", "everett"],
     "featured_products": ["ZV-HND-001", "ZV-HND-005"],
     "discount_percent": 0, "channel": ["in-store", "social"],
     "target_audience": "New homeowners, hobbyists",
     "budget_usd": 50000, "spend_usd": 11000,
     "impressions": 220000, "clicks": 4900, "roi": None,
     "kb_brief": None},
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    products_path = root / "src" / "mcp_servers" / "products" / "seed" / "products_seed.json"
    campaigns_path = root / "src" / "mcp_servers" / "marketing" / "seed" / "marketing_seed.json"

    products = build_products()
    products_path.write_text(json.dumps(products, indent=2), encoding="utf-8")
    campaigns_path.write_text(json.dumps(CAMPAIGNS, indent=2), encoding="utf-8")

    print(f"wrote {len(products)} products -> {products_path}")
    print(f"wrote {len(CAMPAIGNS)} campaigns -> {campaigns_path}")


if __name__ == "__main__":
    main()
