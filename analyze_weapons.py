#!/usr/bin/env python3
"""
analyze_weapons.py — Static DECORATE weapon stats analyzer for DoomRLA Arsenal.
Reports fire rate, damage, reload time, and spread for each weapon in the base
(unmodded) configuration.

Usage:
    python analyze_weapons.py                      # colored terminal output + progress
    python analyze_weapons.py > out.txt            # plain text (color stripped automatically)
    python analyze_weapons.py --no-progress        # suppress progress bar
    python analyze_weapons.py --weapons-dir PATH   # custom weapons folder
    python analyze_weapons.py --no-color           # force plain text in terminal too
    python analyze_weapons.py --debug              # show dev specified debugging output
    python analyze_weapons.py --help               # show usage

Tic counting rules (ZDoom 2.8.1 DECORATE):
  - Each tic ≈ 1/35 second
  - Frame line:  SPRT ABCDE N  →  len("ABCDE") × N tics contributed
  - Logic line:  TNT1 A 0 A_JumpIfInventory(...)  →  0 tics (skipped)
  - Fire rate = tics in FireFinish state up to A_ReFire or Goto Ready
  - Reload     = tics in base Reload path (TechnicalMod branches ignored)
  - Spread     = args 1 & 2 of A_FireBullets on the unmodded fire path
"""

from __future__ import annotations

import re
import sys
import argparse
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markup import escape as markup_escape
from rich.progress import track


# ---------------------------------------------------------------------------
# Tier metadata
# ---------------------------------------------------------------------------

_TIER_MAP: dict[str, str] = {
    "standard":  "Standard",
    "exotic":    "Exotic",
    "superior":  "Superior",
    "unique":    "Unique",
    "demonic":   "Demonic",
    "legendary": "Legendary",
    "basic":     "Basic Assembly",
    "advanced":  "Advanced Assembly",
    "master":    "Master Assembly",
}

_TIER_ORDER = [
    "Standard", "Exotic", "Superior", "Unique",
    "Demonic", "Legendary",
    "Basic Assembly", "Advanced Assembly", "Master Assembly",
    "Unknown",
]

# Actor parent names that identify a weapon
_WEAPON_BASES = {
    "rlweapon", "rlbaseweapon",
    "rlpistolweapon", "rlheavyweapon", "rlmarathonweapon",
}

# Known ZDoom 2.8.1 builtin projectile damage expressions (normalized).
# Damage N (plain) = N * random(1,8) → (8dN)
# Damage (expr)    = fixed expr       → (expr)
_ZDOOM_BUILTIN_PROJ_DAMAGE: dict[str, str] = {
    "plasmaball":   "(8d5)",    # Damage 5
    "rocket":       "(8d20)",   # Damage 20
    "bfgball":      "(8d100)",  # Damage (100*random(1,8))
    "arachnotron":  "(8d5)",    # plasma bolt, Damage 5
    "cacodemonball":"(8d3)",    # Damage 3
    "bruisershot":  "(8d8)",    # Baron fireball, Damage 8
    "headfx1":      "(8d6)",    # Heretic goldwand, Damage 6
}

# Weapons whose damage can't be statically resolved (cross-file chains, latch-explode, etc.)
# Keyed by lowercased actor name. Value: (damage_expr, reason).
# Applied as fallback when normal extraction returns "?", "", or "[proj:...]".
_WEAPON_DAMAGE_OVERRIDES: dict[str, tuple[str, str]] = {
    "rllaserpulselauncher": ("(6)",       "RLDefenceDrone -> RLDefenceDroneLaser, Damage (6)"),
    "rlplasmarefractor":    ("36 x (50)", "RLPlasmaRefractorImpact latches -> explodes into 36 x RLPlasmaRefractionBall @ fixed (50)"),
}
_WEAPON_SPREAD_OVERRIDES: dict[str, tuple[str, str]] = {
    "rlzeuscannon": ("N/A", "Zeus Cannon doesn't really have spread per-se")
}

# Set to True by --debug flag in main(); read by parse_file and helpers.
_DEBUG: bool = False

global_proj_lookup: dict[str, str] = dict(_ZDOOM_BUILTIN_PROJ_DAMAGE)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class WeaponStats:
    name: str
    tier: str
    file: Path
    fire_tics_min: int = 0
    fire_tics_max: int = 0
    reload_tics: int = 0          # 0 = N/A
    reload_per_shell: bool = False
    radius: Optional[float] = None
    spread_h: Optional[float] = None
    spread_v: Optional[float] = None
    spread_override: Optional[str] = None   # set for charge weapons with range spreads
    damage_expr: str = "?"
    is_melee: bool = False
    charge_stages: int = 0        # >0 = charge weapon
    charge_tics_total: int = 0    # LC: sum of fire1..fireN tics; 0 for HPB
    parse_notes: list[str] = field(default_factory=list)

    @property
    def fire_rate_str(self) -> str:
        lo, hi = self.fire_tics_min, self.fire_tics_max
        if lo == 0 and hi == 0:
            return "?"
        if lo == hi:
            base = f"{lo} tics ({lo / 35:.2f}s)"
        else:
            mid = (lo + hi) // 2
            var = hi - mid
            base = (
                f"{mid} tics +/- {var} tics "
                f"({mid / 35:.2f}s +/- {var / 35:.2f}s)"
            )
        if self.charge_tics_total > 0:
            ct = self.charge_tics_total
            return f"{base} | Full Charge: {ct} tics ({ct / 35:.2f}s)"
        return base

    @property
    def reload_str(self) -> str:
        if self.reload_tics == 0:
            return "N/A"
        t = self.reload_tics
        s = f"{t} tics ({t / 35:.2f}s)"
        if self.reload_per_shell:
            s += " [per shell]"
        return s

    @property
    def spread_str(self) -> str:
        if self.is_melee:
            return "melee"
        if self.spread_override is not None:
            return self.spread_override
        if self.spread_h is None:
            return "?"
        def _fmt(v: float) -> str:
            return str(int(v)) if v == int(v) else str(v)
        h = _fmt(self.spread_h)
        v = _fmt(self.spread_v) if self.spread_v is not None else "?"
        return f"{h} x {v}"


# ---------------------------------------------------------------------------
# Low-level DECORATE line helpers
# ---------------------------------------------------------------------------

# Standard sprite frame:  SPRT ABCDE N [actions...]
_FRAME_STD_RE = re.compile(
    r"^\s*[A-Za-z0-9_]{4}\s+([A-Za-z#\[\]]+)\s+(-?\d+)",
)
# Quoted sprite frame:  "####" "ABCDE" N [actions...]
_FRAME_QUOTED_RE = re.compile(
    r'^\s*"[^"]+"\s+"([^"]+)"\s+(-?\d+)',
)

_WEAPON_SPAWN_EXCLUSION_RE = re.compile(
    r"(Recoil|Pickup|Modded|Clip|Assembled|DRPG|Shells|Trail|Smoke|Shrapnel|HaximusMaximus)\"", 
    re.IGNORECASE
)

# Projectile Damage property in actor body (before States block)
_DAMAGE_FIXED_RE = re.compile(
    r'^\s*Damage\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)', 
    re.IGNORECASE | re.MULTILINE
)

_DAMAGE_PLAIN_RE = re.compile(
    r'^\s*Damage\s+(\d+(?:\.\d+)?)\s*$', 
    re.IGNORECASE | re.MULTILINE
)

# Flag check
_RIPPER_FLAG_RE = re.compile(
    r'^\s*\+RIPPER\s*$',
    re.IGNORECASE | re.MULTILINE
)

# Labels to skip when following Goto or fall-through (mod/powerup variants)
_SKIP_TARGET_RE = re.compile(
    r'^firefinish[fa]|^firefinishpowerupcheckconfirmed', 
    re.IGNORECASE
)

def count_frame_tics(line: str) -> int:
    """Return total tics a DECORATE frame line contributes (0 for logic-only lines)."""
    bare = re.sub(r"//.*$", "", line).rstrip()

    m = _FRAME_QUOTED_RE.match(bare)
    if m:
        return len(m.group(1)) * max(0, int(m.group(2)))

    m = _FRAME_STD_RE.match(bare)
    if m:
        return len(m.group(1)) * max(0, int(m.group(2)))

    return 0


def _bare(line: str) -> str:
    """Strip inline comment and trailing whitespace."""
    return re.sub(r"//.*$", "", line).rstrip()


def _is_goto_ready(line: str) -> bool:
    s = line.strip().lower()
    return (
        s.startswith("goto ready")
        or s.startswith("goto readymain")
        or s == "loop"
    )


def _is_refire(line: str) -> bool:
    return bool(re.search(r"\bA_ReFire\b", line, re.IGNORECASE))


def _goto_target(line: str) -> Optional[str]:
    """If the line is an unconditional Goto, return the target label (lower-cased)."""
    s = _bare(line).strip().lower()
    m = re.match(r"^goto\s+(\w+)", s)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# States block extractor
# ---------------------------------------------------------------------------

def _extract_states_text(actor_text: str) -> str:
    """Return the raw text inside the States { } block (empty string if absent)."""
    m = re.search(r"\bStates\s*\{", actor_text, re.IGNORECASE)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(actor_text) and depth > 0:
        c = actor_text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return actor_text[start : i - 1]


# A label line: optional whitespace, word chars, colon, optional comment, nothing else
_LABEL_RE = re.compile(r"^\s*(\w+)\s*:\s*(?://.*)?$")

def tokenize_states(actor_text: str) -> dict[str, list[str]]:
    """
    Parse the States block from actor_text and return
    {label_lower: [raw_lines]} for every state label found.
    """
    states_text = _extract_states_text(actor_text)
    if not states_text:
        return {}

    result: dict[str, list[str]] = {}
    current_label: Optional[str] = None
    current_lines: list[str] = []

    for raw in states_text.splitlines():
        # Check against comment-stripped line for label detection
        stripped = _bare(raw)
        m = _LABEL_RE.match(stripped)
        if m:
            if current_label is not None:
                result[current_label] = current_lines
            current_label = m.group(1).lower()
            current_lines = []
        elif current_label is not None and stripped.strip():
            current_lines.append(raw)

    if current_label is not None:
        result[current_label] = current_lines

    return result


# ---------------------------------------------------------------------------
# Parenthesis-aware function argument parser
# ---------------------------------------------------------------------------

def parse_func_args(text: str, func_name: str) -> list[str]:
    """
    Find func_name(...) in text and return its comma-separated arguments,
    correctly handling nested parentheses (e.g. random(1,3)*5).
    """
    pat = re.compile(rf"\b{re.escape(func_name)}\s*\(", re.IGNORECASE)
    m = pat.search(text)
    if not m:
        return []

    start = m.end()
    args: list[str] = []
    buf: list[str] = []
    depth = 0

    for c in text[start:]:
        if c == "(":
            depth += 1
            buf.append(c)
        elif c == ")":
            if depth == 0:
                args.append("".join(buf).strip())
                break
            depth -= 1
            buf.append(c)
        elif c == "," and depth == 0:
            args.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)

    return args


# ---------------------------------------------------------------------------
# Fire rate extraction
# ---------------------------------------------------------------------------

def _sum_label_tics(
    states: dict[str, list[str]],
    label: str,
    *,
    stop_before_goto: Optional[str] = None,
) -> int:
    """
    Sum non-zero tics in `label`, optionally stopping just before a specific
    Goto target.  Does NOT follow Goto jumps — caller chains manually.
    Stops at A_ReFire, Goto Ready/ReadyMain, Loop, or end of lines.
    """
    total = 0
    for line in states.get(label, []):
        bare = _bare(line)
        if _is_refire(bare) or _is_goto_ready(bare):
            break
        target = _goto_target(bare)
        if target is not None:
            if stop_before_goto and target == stop_before_goto.lower():
                break   # stop here; caller gets the min
            break       # any other Goto also terminates this label's scan
        total += count_frame_tics(line)
    return total


def extract_fire_rate(states: dict[str, list[str]]) -> tuple[int, int]:
    """
    Return (min_tics, max_tics) for the unmodded base fire cycle.

    Two variance patterns handled:
      A) FireFinishContinue split (CombatShotgun):
         FireFinish has conditional → Goto FireFinishContinue for pump anim.
         min = tics in FireFinish before that Goto
         max = min + tics in FireFinishContinue
      B) Single FireFinish (most weapons):
         Sum all tics up to A_ReFire / Goto Ready, following one Goto if needed.
    """
    if "firefinish" not in states:
        # Fallback: scan Fire: directly (unusual weapons)
        t = _scan_state_chain(states, "fire")
        return t, t

    # Pattern A: FireFinishContinue exists
    if "firefinishcontinue" in states:
        min_t = _scan_state_chain(states, "firefinish", stop_before="firefinishcontinue")
        cont_t = _scan_state_chain(states, "firefinishcontinue")
        return min_t, min_t + cont_t

    # Pattern B: single FireFinish (may chain to one sub-label via Goto)
    t = _scan_state_chain(states, "firefinish")
    return t, t

def _scan_state_chain(
    states: dict[str, list[str]],
    start: str,
    max_hops: int = 8,
    stop_before: Optional[str] = None
) -> int:
    """
    Sum non-zero tics starting at `start`, following unconditional Gotos
    up to max_hops times.  Stops at A_ReFire, Goto Ready/ReadyMain, Loop.
    Does NOT follow FireFinishF* mod-variant labels.
    """
    visited: set[str] = set()
    label = start.lower()
    total = 0
    
    label_order = list(states.keys()) # insertion order = file order

    for _ in range(max_hops):
        if label in visited:
            break
        visited.add(label)

        next_label: Optional[str] = None
        found_exit: bool = False
        for line in states.get(label, []):
            bare = _bare(line)
            if _is_refire(bare) or _is_goto_ready(bare):
                return total
            target = _goto_target(bare)
            if target is not None:
                # For Pattern A: stop before falling INTO the continue label
                if stop_before and target == stop_before.lower():
                    return total
                if _SKIP_TARGET_RE.match(target):
                    return total          # mod-variant branch — bail
                # Don't follow mod-variant FireFinish labels (F1, F2, ...)
                if target.startswith("firefinishf"):
                    return total
                next_label = target
                found_exit = True
                break
            total += count_frame_tics(line)

        if found_exit:
            label = next_label
        else:
            try:
                idx = label_order.index(label)
                fallthrough = label_order[idx + 1] if idx + 1 < len(label_order) else None
            except ValueError:
                fallthrough = None

            if fallthrough is None:
                break
            if _SKIP_TARGET_RE.match(fallthrough):
                return total
            if stop_before and fallthrough == stop_before.lower():
                break

            label = fallthrough

    return total


# ---------------------------------------------------------------------------
# Attack call extraction
# ---------------------------------------------------------------------------

def _parse_damage_expr(pellets_raw: str, damage_raw: str, flags: str = "", frame_mult: int = 1) -> str:
    """Convert A_FireBullets pellet+damage args into a human-readable expression."""
    pellets_raw = pellets_raw.strip()
    m = re.match(r'^\(\s*(-?\d+)\s*\)$', damage_raw)
    if m:
        damage_raw = m.group(1)
    else:
        damage_raw = damage_raw.strip()

    norandom = "FBF_NORANDOM" in flags.upper()

    try:
        pellets = int(pellets_raw)
    except ValueError:
        # Non-integer pellet count — normalize the damage expression as-is
        return _normalize_damage_expr(raw=damage_raw, norandom=norandom, frame_mult=frame_mult)

    try:
        dmg = int(damage_raw)
    except ValueError:
        # Complex damage expression (e.g. random(1,3)*5 - 1)
        inner = _normalize_damage_expr(raw=damage_raw, norandom=norandom, frame_mult=frame_mult)
        return f"{pellets} x {inner}" if pellets > 1 else inner

    # Integer damage — multi-frame firing takes priority over pellet count
    if frame_mult > 1 and pellets in (-1, 1):
        return _normalize_damage_expr(raw=str(dmg), norandom=norandom, dice=3, frame_mult=frame_mult)

    # pellets -1 or 1 both mean "single bullet" in A_FireBullets
    if pellets in (-1, 1):
        return _normalize_damage_expr(raw=str(dmg), norandom=norandom, dice=3)

    inner = _normalize_damage_expr(raw=str(dmg), norandom=norandom, dice=3)
    return f"{pellets} x {inner}"

# At this point it would be easier to bake a blacklist for the modded states
base_fire_states = [
    "fire", "firestart", "firerepeat", "firebegin", "firespin", "firecontinue", "firedualleftcontinue", "firedualrightcontinue", "firenormal", "hold", "firestartbuildup", 
    "firedisrupted", "firestable", "overload", "normalleft", "firefinishpowerupcheckdone",
    
    "firemainmissileleft", "firemainmissileright", "fireammocheckdone","fireammocheck", "firemain", "firemainbasic", 
    
    # LC
    "firemain1", "firemain2", "firemain3", "firemain4", "firemain5", "firemainanim",
    
    # HPB
    "fire1", "fire2", "fire3", "fire4", "fire5", "fire6", "fire7", "fire8", "fire9", "fire10", "fire11", "fire12", "fire13", "fire14", "fire15", "fire16", "fire17", "fire18", "fire19", "fire20",
    
    # MM
    "fireafterammocheck", "firestandard", "firestandard", "fireshotgun", "firespread", "firerailgun", "fireexplosive", "fireocto", "firebfg10ksequence", "fireknockback", "firefinalshot", "fireammo",
    
    # NAG
    "firehk416", "fireak74", "fireump45", "firemp5", "firefamas", "firesr3m", "firem14", "firem4a1", "firescar", "firecyclone", 
    
    # ye ende
    "firefinish"
]

def extract_attack_function(
    states: dict[str, list[str]]
) -> tuple[str, list[str]]:
    """
    Search Fire: and FireFinish: for the first A_FireBullets / A_Saw /
    A_CustomBulletAttack / A_FireCustomMissile call on the base 
    (unmodded) path.

    Returns function name and args.
    """
    
    search_labels = base_fire_states + [
        k for k in states if k.startswith("firefinish") and k != "firefinish"
    ]

    for label in search_labels:
        for line in states.get(label, []):
            bare = _bare(line)

            # A_Saw — melee weapon
            if re.search(r"\bA_Saw\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_Saw")
                return "A_Saw", args
            # A_FireBullets
            if re.search(r"\bA_FireBullets\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_FireBullets")
                return "A_FireBullets", args
            # A_CustomBulletAttack
            if re.search(r"\bA_CustomBulletAttack\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_CustomBulletAttack")
                return "A_CustomBulletAttack", args
            # A_FireCustomMissile
            if re.search(r"\bA_FireCustomMissile\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_FireCustomMissile")
                return "A_FireCustomMissile", args
            # A_CustomMissile
            if re.search(r"\bA_CustomMissile\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_CustomMissile")
                return "A_CustomMissile", args
            # A_RailAttack
            if re.search(r"\bA_RailAttack\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_RailAttack")
                return "A_RailAttack", args
            
    return "", [""]

def extract_attack_call(
    states: dict[str, list[str]],
    proj_lookup: dict = {}
) -> tuple[str, Optional[float], Optional[float], Optional[float], bool]:
    """
    Single pass over fire states. Collects:
      - Primary attack (first of: A_Saw, A_CustomPunch, A_FireBullets,
        A_CustomBulletAttack, A_RailAttack, A_FireCustomMissile, A_SpawnItemEx)
      - Blast radius from A_Explode (independent of primary; also used as
        damage source if no other attack call found)

    Returns (damage_expr, spread_h, spread_v, radius, is_melee).
    """
    search_labels = base_fire_states + [
        k for k in states if k.startswith("firefinish") and k != "firefinish"
    ]

    damage_expr: str = "?"
    spread_h: Optional[float] = None
    spread_v: Optional[float] = None
    radius: Optional[float] = None
    is_melee: bool = False
    primary_found: bool = False
    explode_damage: Optional[str] = None  # fallback if no other primary

    out_console = Console(highlight=False)
    for label in search_labels:
        for line in states.get(label, []):
            bare = _bare(line)
            
            if _DEBUG: out_console.print(f"bare line:[yellow]{bare}[/yellow]")
            
            # Ignore ANY effect spawns, as they've been skewing reporting!
            if _WEAPON_SPAWN_EXCLUSION_RE.search(bare):
                continue

            # --- A_Explode: always collect radius; note damage as fallback ---
            if _DEBUG: out_console.print(f"A_Explode? [bold]{re.search(r"\bA_Explode\b", bare, re.IGNORECASE)}[/bold]")
            if re.search(r"\bA_Explode\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_Explode")
                if args:
                    m_frame = _FRAME_STD_RE.match(bare)
                    frame_mult = 1
                    if m_frame and int(m_frame.group(2)) == 0:
                        frame_mult = len(m_frame.group(1))
                    explode_damage = _parse_damage_expr(
                        pellets_raw="1", damage_raw=args[0],
                        flags=args[2] if len(args) > 2 else "",
                        frame_mult=frame_mult,
                    )
                    if len(args) >= 2:
                        try:
                            radius = float(args[1].strip())
                        except ValueError:
                            pass
                continue  # A_Explode is never the spread/damage primary

            if primary_found:
                continue

            # --- A_CustomPunch / A_Saw — melee ---
            for melee_fn, dmg_arg in (("A_CustomPunch", 0), ("A_Saw", 2)):
                if _DEBUG: out_console.print(f"A_CustomPunch | A_Saw? [bold]{re.search(rf"\b{melee_fn}\b", bare, re.IGNORECASE)}[/bold]")
                if re.search(rf"\b{melee_fn}\b", bare, re.IGNORECASE):
                    args = parse_func_args(bare, melee_fn)
                    if len(args) > dmg_arg:
                        try:
                            dmg = int(args[dmg_arg].strip())
                            damage_expr = _normalize_damage_expr(raw=str(dmg), norandom=False, dice=3)
                        except ValueError:
                            damage_expr = args[dmg_arg].strip()
                    else:
                        damage_expr = "?"
                    is_melee = True
                    primary_found = True
                    break
            if primary_found:
                continue

            # --- A_FireBullets ---
            if _DEBUG: out_console.print(f"bA_FireBullets? [bold]{re.search(r"\bA_FireBullets\b", bare, re.IGNORECASE)}[/bold]")
            if re.search(r"\bA_FireBullets\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_FireBullets")
                if len(args) >= 4:
                    try:
                        spread_h = float(args[0].strip())
                    except ValueError:
                        pass
                    try:
                        spread_v = float(args[1].strip())
                    except ValueError:
                        pass
                    m_frame = _FRAME_STD_RE.match(bare)
                    frame_mult = 1
                    if m_frame and int(m_frame.group(2)) == 0:
                        frame_mult = len(m_frame.group(1))
                    damage_expr = _parse_damage_expr(
                        pellets_raw=args[2], damage_raw=args[3],
                        flags=args[5] if len(args) > 5 else "",
                        frame_mult=frame_mult,
                    )
                    primary_found = True
                    continue

            # --- A_CustomBulletAttack ---
            if _DEBUG: out_console.print(f"bA_CustomBulletAttack? [bold]{re.search(r"\bA_CustomBulletAttack\b", bare, re.IGNORECASE)}[/bold]")
            if re.search(r"\bA_CustomBulletAttack\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_CustomBulletAttack")
                if len(args) >= 4:
                    try:
                        spread_h = float(args[0].strip())
                    except ValueError:
                        pass
                    try:
                        spread_v = float(args[1].strip())
                    except ValueError:
                        pass
                    m_frame = _FRAME_STD_RE.match(bare)
                    frame_mult = 1
                    if m_frame and int(m_frame.group(2)) == 0:
                        frame_mult = len(m_frame.group(1))
                    damage_expr = _parse_damage_expr(
                        pellets_raw=args[2], damage_raw=args[3],
                        flags=args[6] if len(args) > 6 else "",
                        frame_mult=frame_mult,
                    )
                    primary_found = True
                    continue

            # --- A_RailAttack — always fixed damage (no random(1,3) multiplier) ---
            if _DEBUG: out_console.print(f"bA_RailAttack? [bold]{re.search(r"\bA_RailAttack\b", bare, re.IGNORECASE)}[/bold]")
            if re.search(r"\bA_RailAttack\b", bare, re.IGNORECASE):
                args = parse_func_args(bare, "A_RailAttack")
                # Skip decorative 0-damage ring/visual calls (e.g. HPB ring effect).
                # Do NOT skip based on useammo=0 — some weapons (e.g. EnergySaw) handle
                # ammo separately and legitimately pass useammo=0 on their real attack.
                if args and args[0].strip() != "0":
                    m_frame = _FRAME_STD_RE.match(bare)
                    frame_mult = 1
                    if m_frame and int(m_frame.group(2)) == 0:
                        frame_mult = len(m_frame.group(1))
                    damage_expr = _normalize_damage_expr(
                        raw=args[0].strip(), norandom=True, frame_mult=frame_mult,
                    )
                    # Spread at args[8]/[9] — only present in longer calls
                    if len(args) >= 10:
                        try:
                            spread_h = float(args[8].strip())
                        except ValueError:
                            pass
                        try:
                            spread_v = float(args[9].strip())
                        except ValueError:
                            pass
                    primary_found = True
                    continue

            # --- A_FireCustomMissile / A_SpawnItemEx — projectile launch ---
            for proj_fn in ("A_FireCustomMissile", "A_SpawnItemEx", "A_CustomMissile"):
                if _DEBUG: out_console.print(f"A_FireCustomMissile | A_SpawnItemEx | A_CustomMissile? [bold]{re.search(rf"\b{proj_fn}\b", bare, re.IGNORECASE)}[/bold]")
                if re.search(rf"\b{proj_fn}\b", bare, re.IGNORECASE):
                    args = parse_func_args(bare, proj_fn)
                    if args:
                        proj_name = args[0].strip().strip('"\'').split('",')[0]
                        dmg = proj_lookup.get(proj_name.lower())
                        damage_expr = dmg or f"[proj:{proj_name}]"
                        primary_found = True
                    break
            if _DEBUG: out_console.print(f"_________________");

    # If only A_Explode was found, use its damage as the primary
    if not primary_found and explode_damage is not None:
        damage_expr = explode_damage

    return damage_expr, spread_h, spread_v, radius, is_melee


def _normalize_damage_expr(
    raw: str = "",
    norandom: bool = False,
    dice: int = 3,
    ripper: bool = False,
    frame_mult: int = 1
):
    raw = raw.strip()

    # Unwrap (N) integer wrapper only
    m = re.match(r'^\(\s*(-?\d+)\s*\)$', raw)
    if m:
        raw = m.group(1).strip()

    def _sfx(s: str) -> str:
        return s + "!" if ripper else s

    def _fmt(s) -> str:
        try:
            f = float(str(s))
            return str(int(f)) if f == int(f) else str(f)
        except (ValueError, TypeError):
            return str(s)

    def _wrap(inner: str) -> str:
        return _sfx(f"{frame_mult} x {inner}") if frame_mult > 1 else _sfx(inner)

    # Integer
    try:
        n = int(raw)
        return _wrap(f"({n})" if norandom else f"({dice}d{n})")
    except ValueError:
        pass

    # (random(1,3)*N) - C  →  (3dN) - C
    m = re.match(
        r'\(random\(1\s*,\s*3\)\s*\*\s*(\d+(?:\.\d+)?)\)\s*-\s*(\d+(?:\.\d+)?)',
        raw, re.IGNORECASE,
    )
    if m:
        return _wrap(f"(3d{_fmt(m.group(1))}) - {_fmt(m.group(2))}")

    # random(1,3)*N  →  (3dN)
    m = re.match(r'random\(1\s*,\s*3\)\s*\*\s*(\d+(?:\.\d+)?)', raw, re.IGNORECASE)
    if m:
        return _wrap(f"(3d{_fmt(m.group(1))})")

    # N*random(1,3)  →  (3dN)  [reversed order]
    m = re.match(r'(\d+(?:\.\d+)?)\s*\*\s*random\(1\s*,\s*3\)', raw, re.IGNORECASE)
    if m:
        return _wrap(f"(3d{_fmt(m.group(1))})")

    # (f?random(X,Y)*N)  →  ((X~Y)*N)
    m = re.match(
        r'\(?f?random\((\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\)\s*\*\s*(\d+(?:\.\d+)?)\)?',
        raw, re.IGNORECASE,
    )
    if m:
        return _wrap(f"(({_fmt(m.group(1))}~{_fmt(m.group(2))})*{_fmt(m.group(3))})")

    # N*(f?random(X,Y))  →  ((X~Y)*N)  [reversed order]
    m = re.match(
        r'(\d+(?:\.\d+)?)\s*\*\s*\(?f?random\((\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\)\)?',
        raw, re.IGNORECASE,
    )
    if m:
        return _wrap(f"(({_fmt(m.group(2))}~{_fmt(m.group(3))})*{_fmt(m.group(1))})")

    # f?random(X,Y)  →  (X~Y)
    m = re.match(
        r'f?random\((\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\)',
        raw, re.IGNORECASE,
    )
    if m:
        return _wrap(f"({_fmt(m.group(1))}~{_fmt(m.group(2))})")

    # Fallback verbatim — ensure wrapped in parens
    inner = raw if (raw.startswith("(") and raw.endswith(")")) else f"({raw})"
    return _wrap(inner)

# ---------------------------------------------------------------------------
# Charge weapon helpers
# ---------------------------------------------------------------------------

def _count_charge_stages(states: dict) -> int:
    """
    Count sequential fire1…fireN keys in states.
    Returns 0 if fewer than 2 consecutive stages found (avoids false positives).
    """
    n = 0
    while f"fire{n + 1}" in states:
        n += 1
    return n if n >= 2 else 0


def _detect_charge_type(states: dict) -> str:
    """
    Returns 'lc' if weapon has firemain1 (LC-style: charges in fireN, fires in firemainN),
    'hpb' if fireN states contain attack calls (HPB-style: fires each stage),
    or '' if not a charge weapon.
    """
    if _count_charge_stages(states) == 0:
        return ""
    if "firemain1" in states:
        return "lc"
    # HPB: fire1 should contain an attack call
    for line in states.get("fire1", []):
        bare = _bare(line)
        if re.search(
            r"\bA_FireBullets\b|\bA_CustomBulletAttack\b|\bA_RailAttack\b"
            r"|\bA_FireCustomMissile\b|\bA_Saw\b",
            bare, re.IGNORECASE,
        ):
            return "hpb"
    return ""


def _build_range_expr(exprs: list[str]) -> str:
    """
    Given a list of per-stage damage expression strings, return a single expression.
    If all stages are identical, returns the common value.
    Otherwise returns (first~last) with outer parens stripped from each endpoint.
    """
    if not exprs:
        return "?"
    unique = list(dict.fromkeys(exprs))  # deduplicate, preserve order
    if len(unique) == 1:
        return unique[0]

    def _strip(s: str) -> str:
        """Strip a single layer of outer parens if balanced."""
        s = s.strip()
        m = re.match(r'^\((.+)\)$', s)
        if m:
            inner = m.group(1)
            if inner.count("(") == inner.count(")"):
                return inner
        return s

    return f"({_strip(unique[0])}~{_strip(unique[-1])})"


def _spread_range_str(values: list) -> Optional[str]:
    """
    Given a list of Optional[float] spread values (one per stage), return:
      - None  if all values are None
      - single formatted value if all non-None values are equal
      - 'min~max' string if they differ
    """
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    def _fmt(v: float) -> str:
        return str(int(v)) if v == int(v) else str(v)
    if len(set(clean)) == 1:
        return _fmt(clean[0])
    return f"{_fmt(min(clean))}~{_fmt(max(clean))}"


def extract_charge_weapon_stats(
    states: dict[str, list[str]],
    proj_lookup: dict = {},
) -> tuple[str, Optional[str], int, int]:
    """
    For charge weapons (LC / HPB), extract damage range, spread range,
    fire rate, and total charge time.

    Returns:
        damage_expr        — range string e.g. '(3d5~3d25)' or single expr
        spread_str_override — e.g. '2~8 x 2' or None if uniform / unknown
        fire_tics          — LC: firemainanim tics; HPB: fire1 tics (constant rate)
        charge_tics_total  — LC: sum of fire1..fireN tics; HPB: 0
    """
    charge_type = _detect_charge_type(states)
    stages = _count_charge_stages(states)

    if charge_type == "lc":
        # Charge time: sum tics across fire1..fireN
        charge_tics = 0
        for i in range(1, stages + 1):
            for line in states.get(f"fire{i}", []):
                charge_tics += count_frame_tics(line)

        # Count firemain stages
        m_stages = 0
        while f"firemain{m_stages + 1}" in states:
            m_stages += 1

        damages: list[str] = []
        spreads_h: list = []
        spreads_v: list = []

        for i in range(1, m_stages + 1):
            lbl = f"firemain{i}"
            dmg, sh, sv, _, _ = extract_attack_call({lbl: states[lbl]}, proj_lookup)
            if dmg != "?":
                damages.append(dmg)
            spreads_h.append(sh)
            spreads_v.append(sv)

        # Fire rate = recovery tics in firemainanim
        fire_tics = _scan_state_chain(states, "firemainanim")

        damage_expr = _build_range_expr(damages)
        sh_str = _spread_range_str(spreads_h)
        sv_str = _spread_range_str(spreads_v)
        spread_str = (
            f"{sh_str or '?'} x {sv_str or '?'}"
            if (sh_str is not None or sv_str is not None) else None
        )
        return damage_expr, spread_str, fire_tics, charge_tics

    elif charge_type == "hpb":
        # HPB: fire1=strongest, fire20=weakest — collect in order then reverse for (min~max)
        damages: list[str] = []
        spreads_h: list = []
        spreads_v: list = []

        for i in range(1, stages + 1):
            lbl = f"fire{i}"
            dmg, sh, sv, _, _ = extract_attack_call({lbl: states[lbl]}, proj_lookup)
            if dmg != "?":
                damages.append(dmg)
            spreads_h.append(sh)
            spreads_v.append(sv)

        # fire1=weakest, fire20=strongest — natural order gives (min~max)
        damage_expr = _build_range_expr(damages)

        # Fire rate = tics in fire1 (constant across all stages)
        fire_tics = sum(count_frame_tics(line) for line in states.get("fire1", []))

        sh_str = _spread_range_str(spreads_h)
        sv_str = _spread_range_str(spreads_v)
        spread_str = (
            f"{sh_str or '?'} x {sv_str or '?'}"
            if (sh_str is not None or sv_str is not None) else None
        )
        return damage_expr, spread_str, fire_tics, 0

    return "?", None, 0, 0


# ---------------------------------------------------------------------------
# Reload extraction
# ---------------------------------------------------------------------------

def extract_reload(states: dict[str, list[str]]) -> tuple[int, bool]:
    """
    Sum non-zero tics in the base (no TechnicalMod) Reload path.
    Returns (total_tics, per_shell_flag).
    """
    reload_lines = states.get("reload", [])
    if not reload_lines:
        return 0, False

    total = 0
    per_shell = False
    _tech_mod_re = re.compile(r"technicalmod", re.IGNORECASE)

    for line in reload_lines:
        bare = _bare(line)
        s = bare.strip().lower()

        # Skip TechnicalMod conditional branches (faster reload paths)
        if _tech_mod_re.search(bare):
            continue

        # Detect per-shell loop
        if "reloadworking" in s:
            per_shell = True

        # Stop at Ready transition
        if _is_goto_ready(s):
            break
        # Stop at per-shell loop entry (don't double-count the loop body)
        if "goto reloadworking" in s or "goto reloadstart" in s:
            break

        total += count_frame_tics(line)

    return total, per_shell


# ---------------------------------------------------------------------------
# Actor block splitter
# ---------------------------------------------------------------------------

_ACTOR_DECL_RE = re.compile(
    r"^ACTOR\s+(\w+)(?:\s*:\s*(\w+))?",
    re.IGNORECASE | re.MULTILINE,
)


def _split_actor_blocks(text: str) -> list[tuple[str, str, str]]:
    """Return [(name, parent, block_text), ...] for each ACTOR in the file."""
    matches = list(_ACTOR_DECL_RE.finditer(text))
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(1), m.group(2) or "", text[m.start() : end]))
    return out


def _infer_tier(path: Path) -> str:
    for part in path.parts:
        if part.lower() in _TIER_MAP:
            return _TIER_MAP[part.lower()]
    return "Unknown"


def _pretty_name(actor_name: str) -> str:
    """RLCombatShotgun → Combat Shotgun (strips RL prefix, adds spaces)."""
    name = re.sub(r"^RL", "", actor_name)
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)


# ---------------------------------------------------------------------------
# File parser
# ---------------------------------------------------------------------------

def _build_proj_lookup(actor_blocks) -> dict[str, str]:
    # Seed with known ZDoom builtin projectile damages
    # lookup: dict[str, str] = dict(_ZDOOM_BUILTIN_PROJ_DAMAGE)
    lookup: dict[str, str] = {**global_proj_lookup}
    parents: dict[str, str] = {}  # name.lower() -> parent.lower()

    # Pass 1: explicit Damage properties from file (override builtins if redefined)
    for name, parent, block in actor_blocks:
        name_lower: str = name.lower()
        if parent.lower() in _WEAPON_BASES:
            continue
        parents[name_lower] = parent.lower()
        sm: re.Match[str] | None = re.search(r'\bStates\s*\{', block, re.IGNORECASE)
        props = block[:sm.start()] if sm else block

        m: re.Match[str] | None = _DAMAGE_FIXED_RE.search(props)
        if m:
            lookup[name_lower] = _normalize_damage_expr(raw=m.group(1).strip(), norandom=True)
            continue

        m = _DAMAGE_PLAIN_RE.search(props)
        if m:
            lookup[name_lower] = _normalize_damage_expr(raw=m.group(1), norandom=False, dice=8)

        if _RIPPER_FLAG_RE.search(props):
            existing = lookup.get(name_lower, "?")
            lookup[name_lower] = existing + "!"

    # Pass 2: walk parent chain until no new entries can be resolved
    changed = True
    while changed:
        changed = False
        for name, parent in parents.items():
            if name not in lookup and parent in lookup:
                lookup[name] = lookup[parent]
                changed = True

    return lookup

def parse_file(path: Path, filter: str = "") -> list[WeaponStats]:
    """Parse one .txt file; return WeaponStats for each valid weapon actor."""
    try:
        text: str = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    tier: str = _infer_tier(path)
    results: list[WeaponStats] = []
    
    out_console = Console(highlight=False)

    actor_blocks: list[tuple[str, str, str]] = _split_actor_blocks(text)
    # lookup_table = _build_proj_lookup(actor_blocks)
    lookup_table = {**(global_proj_lookup or {}), **_build_proj_lookup(actor_blocks)}
    
    for name, parent, block in actor_blocks:
        if filter and name.lower() != filter.lower():
            continue
        
        if parent.lower() not in _WEAPON_BASES:
            continue
        
        notes: list[str] = []
        states: dict[str, list[str]] = tokenize_states(block)

        if not states:
            notes.append("no States block found")
            results.append(
                WeaponStats(name=_pretty_name(name), tier=tier, file=path,
                            parse_notes=notes)
            )
            continue
        
        if _DEBUG:
            attack_func, attack_args = extract_attack_function(states)
            if attack_func and attack_args:
                out_console.print(f"\n")
                out_console.print(
                    f"[bold]{name}[/bold] [{tier}]: [dim]{parent}[/dim] -> [bold]{attack_func}[/bold]({attack_args})"
                )
            else:
                out_console.print(f"\n")
                out_console.print(
                    f"[bold]{name}[/bold] [{tier}]: {parent} -> [red]{attack_func}({attack_args})[/red]"
                )

        charge_type = _detect_charge_type(states)
        charge_stages = _count_charge_stages(states)
        spread_override: Optional[str] = None
        radius: Optional[float] = None

        if charge_type in ("lc", "hpb"):
            damage_expr, spread_override, fire_tics, charge_tics_total = \
                extract_charge_weapon_stats(states, lookup_table)
            fire_min = fire_max = fire_tics
            spread_h = spread_v = None
            is_melee = False
        else:
            charge_stages = 0
            charge_tics_total = 0
            fire_min, fire_max = extract_fire_rate(states)
            damage_expr, spread_h, spread_v, radius, is_melee = extract_attack_call(states, lookup_table)

        reload_tics, per_shell = extract_reload(states)

        if _DEBUG:
            out_console.print(
                f"[bold]{name}[/bold]: {markup_escape(damage_expr)}"
            )

        if name == "RLCombatTranslocator":
            damage_expr = "TELEFRAG"

        # Drone/helper-launched weapons: cross-file chain can't be resolved statically.
        # Triggers on "?", "", or unresolved [proj:...] references.
        if damage_expr in ("?", "") or damage_expr.startswith("[proj:"):
            override = _WEAPON_DAMAGE_OVERRIDES.get(name.lower())
            if override:
                damage_expr, override_reason = override
                notes.append(f"manual override: ({override_reason})")
        
        # Allow spread overrides on applicable weapons
        if spread_h is None or spread_v is None:
            override = _WEAPON_SPREAD_OVERRIDES.get(name.lower())
            if override:
                spread_override, override_reason = override
                notes.append(f"manual override: ({override_reason})")

        if fire_min == 0 and fire_max == 0:
            notes.append("could not determine fire rate")
        if damage_expr == "?":
            notes.append("attack call not found")

        results.append(WeaponStats(
            name=_pretty_name(name),
            tier=tier,
            file=path,
            fire_tics_min=fire_min,
            fire_tics_max=fire_max,
            reload_tics=reload_tics,
            reload_per_shell=per_shell,
            radius=radius,
            spread_h=spread_h,
            spread_v=spread_v,
            spread_override=spread_override,
            damage_expr=damage_expr,
            is_melee=is_melee,
            charge_stages=charge_stages,
            charge_tics_total=charge_tics_total,
            parse_notes=notes,
        ))

    return results


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------

# Column widths for aligned labels
_LABEL_W = 11  # "Fire rate  "


def _field(label: str, value: str, color: str, console: Console) -> None:
    pad = _LABEL_W - len(label)
    console.print(f"    [{color}]{label}[/{color}]{' ' * pad}: {markup_escape(value)}")


def render_weapon(w: WeaponStats, console: Console) -> None:
    console.print(f"  [bold]{w.name}[/bold]")
    _field("Fire rate",   w.fire_rate_str, "cyan",    console)
    _field("Damage",      w.damage_expr,   "green",   console)
    _field("Reload",      w.reload_str,    "yellow",  console)
    _field("Spread",      w.spread_str,    "magenta", console)
    for note in w.parse_notes:
        console.print(f"    [dim][!] {note}[/dim]")
    console.print()


def render_all(weapons: list[WeaponStats], console: Console) -> None:
    from collections import defaultdict
    by_tier: dict[str, list[WeaponStats]] = defaultdict(list)
    for w in weapons:
        by_tier[w.tier].append(w)

    for tier in _TIER_ORDER:
        group = sorted(by_tier.get(tier, []), key=lambda w: w.name)
        if not group:
            continue
        console.rule(f"[bold]{tier}[/bold]")
        console.print()
        for w in group:
            render_weapon(w, console)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Analyze DoomRLA Arsenal weapon DECORATE files for base stats."
    )
    ap.add_argument(
        "--weapons-dir", type=Path,
        default=Path(__file__).parent / "weapons",
        metavar="PATH",
        help="Path to the weapons/ folder (default: ./weapons next to this script)",
    )
    ap.add_argument(
        "--no-progress", action="store_true",
        help="Suppress the progress bar",
    )
    ap.add_argument(
        "--no-color", action="store_true",
        help="Force plain-text output even in a terminal",
    )
    ap.add_argument(
        "--debug", action="store_true",
        help="Show raw weapon, tier, matching action call, and resulting damage",
    )
    ap.add_argument(
        "--filter", type=str,
        default="",
        metavar="RLBFG9000",
        help="Search only for a specific weapon",
    )
    args = ap.parse_args()

    global _DEBUG
    _DEBUG = args.debug
    
    if not args.weapons_dir.is_dir():
        print(
            f"Error: weapons directory not found: {args.weapons_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    # stdout console — rich auto-strips ANSI when not a tty (e.g. piped to file)
    out_console = Console(highlight=False, no_color=args.no_color)
    # stderr console for progress bar — always visible even when stdout is piped
    err_console = Console(stderr=True, highlight=False)
    
    start_time = time.time()
    
    files = sorted(args.weapons_dir.rglob("*.txt"))
    if not files:
        err_console.print("[yellow]No .txt files found in weapons directory.[/yellow]")
        sys.exit(0)

    # We need to build the projectile lookup table first, otherwise we lose some valuable info
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        blocks = _split_actor_blocks(text)
        global_proj_lookup.update(_build_proj_lookup(blocks));

    if args.no_progress:
        iterator = iter(files)
    else:
        iterator = track(
            files,
            description="Parsing weapons...",
            console=err_console,
            transient=True,
        )

    all_weapons: list[WeaponStats] = []
    for f in iterator:
        if (args.filter):
            all_weapons.extend(parse_file(f, args.filter))
        else:
            all_weapons.extend(parse_file(f))

    if _DEBUG:
        out_console.print(all_weapons)
    else:
        render_all(all_weapons, out_console)

    end_time = time.time()
    err_console.print(
        f"[dim]Parsed[/dim] [bold]{len(all_weapons)} weapons[/bold] [dim]from[/dim] [bold]{len(files)}[/bold] [dim]files in[/dim] [bold]{end_time - start_time}s[/bold][dim].[/dim]"
    )

    unresolved = [
        w for w in all_weapons
        if w.damage_expr.startswith("[proj:")
    ]
    if unresolved:
        err_console.print()
        err_console.print(
            "[yellow]Unresolved projectile damage - add entries to "
            "_WEAPON_DAMAGE_OVERRIDES (or _ZDOOM_BUILTIN_PROJ_DAMAGE if a ZDoom "
            "builtin):[/yellow]"
        )
        for w in unresolved:
            err_console.print(
                f"  [dim]{w.name}[/dim]  ->  {markup_escape(w.damage_expr)}"
            )


if __name__ == "__main__":
    main()
