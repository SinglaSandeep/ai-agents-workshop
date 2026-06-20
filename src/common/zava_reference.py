"""Shared Zava reference universe for the Insights-to-Action workshop.

The Sales, Inventory and Marketing datasets all join on the same stores,
regions, categories and product SKUs. Centralising those constants here keeps
the three Cosmos seeders consistent so cross-domain agent questions (e.g.
"sales of ZV-PNT-001 in the north region vs. distributor stock") line up.

All generators in the workshop seed deterministically (``random.seed(...)``)
so re-running a seeder reproduces the exact same rows.
"""

from __future__ import annotations

# --- Stores & regions -------------------------------------------------------
# Seven brick-and-mortar Zava stores plus the online fulfilment centre.
STORES: list[str] = [
    "seattle",
    "bellevue",
    "tacoma",
    "redmond",
    "kirkland",
    "spokane",
    "everett",
    "online",
]

# Each store rolls up to a sales/distribution region.
STORE_REGION: dict[str, str] = {
    "seattle": "north",
    "bellevue": "north",
    "kirkland": "north",
    "redmond": "north",
    "everett": "north",
    "tacoma": "south",
    "spokane": "east",
    "online": "online",
}

REGIONS: list[str] = ["north", "south", "east", "online"]

# --- Categories -------------------------------------------------------------
CATEGORIES: list[str] = [
    "paint",
    "power-tools",
    "hand-tools",
    "garden",
    "lumber",
    "electrical",
    "plumbing",
    "hardware",
]

# Three-letter SKU code per category (ZV-<CODE>-NNN).
CATEGORY_CODE: dict[str, str] = {
    "paint": "PNT",
    "power-tools": "PWT",
    "hand-tools": "HND",
    "garden": "GDN",
    "lumber": "LMB",
    "electrical": "ELC",
    "plumbing": "PLM",
    "hardware": "HDW",
}

CUSTOMER_SEGMENTS: list[str] = ["diy", "pro", "contractor"]
CHANNELS: list[str] = ["in-store", "online"]

# --- Distributors & warehouses (distributor-level inventory) ----------------
# Distributor-level inventory is held by regional distributors, each operating
# one or more warehouses that replenish the Zava stores in their region.
DISTRIBUTORS: list[dict] = [
    {
        "distributor_id": "DIST-NW-01",
        "distributor_name": "Cascade Supply Co.",
        "region": "north",
        "warehouses": ["WH-SEA", "WH-BEL"],
    },
    {
        "distributor_id": "DIST-SW-02",
        "distributor_name": "Rainier Wholesale Partners",
        "region": "south",
        "warehouses": ["WH-TAC"],
    },
    {
        "distributor_id": "DIST-E-03",
        "distributor_name": "Inland Northwest Distribution",
        "region": "east",
        "warehouses": ["WH-SPO"],
    },
    {
        "distributor_id": "DIST-ON-04",
        "distributor_name": "Zava Direct Fulfilment",
        "region": "online",
        "warehouses": ["WH-DC1", "WH-DC2"],
    },
]


# --- Product catalogue ------------------------------------------------------
# Six SKUs per category -> 48 deterministic products shared by all datasets.
_PRODUCT_NAMES: dict[str, list[str]] = {
    "paint": [
        "Premium Interior Paint - Eggshell White",
        "Exterior Acrylic Paint - Slate Grey",
        "Primer & Sealer - All Surface",
        "Cabinet Enamel - Satin Black",
        "Deck & Fence Stain - Cedar",
        "Ceiling Paint - Flat White",
    ],
    "power-tools": [
        "20V Cordless Drill Kit",
        "Brushless Impact Driver",
        "7-1/4 in. Circular Saw",
        "Random Orbital Sander",
        "Compact Reciprocating Saw",
        "Wet/Dry Shop Vacuum 12 gal",
    ],
    "hand-tools": [
        "16 oz. Fiberglass Claw Hammer",
        "25 ft. Tape Measure",
        "Adjustable Wrench Set",
        "Screwdriver Bit Set (40 pc)",
        "Utility Knife with Blades",
        "24 in. Box Level",
    ],
    "garden": [
        "Bypass Pruning Shears",
        "Expandable Garden Hose 50 ft.",
        "Cordless String Trimmer",
        "Raised Garden Bed Kit",
        "All-Purpose Potting Soil 2 cu ft",
        "Drip Irrigation Starter Kit",
    ],
    "lumber": [
        "2x4x8 Kiln-Dried Stud",
        "3/4 in. Birch Plywood Sheet",
        "Pressure-Treated Deck Board",
        "Cedar Fence Picket",
        "1x6 Pine Common Board",
        "7/16 in. OSB Sheathing 4x8",
    ],
    "electrical": [
        "15A Decorator Outlet (10 pk)",
        "14/2 Romex Cable 50 ft.",
        "LED Shop Light 4 ft.",
        "Single-Pole Smart Switch",
        "Weatherproof Outlet Cover",
        "20A GFCI Outlet",
    ],
    "plumbing": [
        "1/2 in. PEX Tubing 100 ft.",
        "Wax-Free Toilet Seal",
        "Pull-Down Kitchen Faucet",
        "Push-to-Connect Fittings (10 pk)",
        "Sump Pump 1/3 HP",
        "14 in. Pipe Wrench",
    ],
    "hardware": [
        "Exterior Wood Screws (1 lb)",
        "Heavy-Duty Door Hinge (3 pk)",
        "Concrete Anchor Kit",
        "Gate Latch - Galvanised",
        "Cabinet Pull - Brushed Nickel",
        "Keyed Entry Lockset - Satin Nickel",
    ],
}

# Indicative base unit price (USD) per category; varied per SKU below.
_CATEGORY_BASE_PRICE: dict[str, float] = {
    "paint": 32.0,
    "power-tools": 129.0,
    "hand-tools": 18.0,
    "garden": 39.0,
    "lumber": 7.0,
    "electrical": 22.0,
    "plumbing": 45.0,
    "hardware": 9.0,
}


def build_catalog() -> list[dict]:
    """Return the deterministic Zava product catalogue (48 SKUs).

    Each record::

        {
          "id": "ZV-PNT-001",
          "sku": "ZV-PNT-001",
          "name": "Premium Interior Paint - Eggshell White",
          "category": "paint",
          "price_usd": 32.99,
          "unit_cost_usd": 19.79,
        }
    """
    catalog: list[dict] = []
    for category in CATEGORIES:
        code = CATEGORY_CODE[category]
        base = _CATEGORY_BASE_PRICE[category]
        for idx, name in enumerate(_PRODUCT_NAMES[category], start=1):
            # Deterministic price spread around the category base price.
            price = round(base * (0.85 + 0.1 * idx), 2)
            sku = f"ZV-{code}-{idx:03d}"
            catalog.append(
                {
                    "id": sku,
                    "sku": sku,
                    "name": name,
                    "category": category,
                    "price_usd": price,
                    "unit_cost_usd": round(price * 0.62, 2),
                }
            )
    return catalog


# Eagerly built once; safe to import and index.
CATALOG: list[dict] = build_catalog()
PRODUCT_IDS: list[str] = [p["id"] for p in CATALOG]
PRODUCT_BY_ID: dict[str, dict] = {p["id"]: p for p in CATALOG}
