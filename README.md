# Taiko Drum Game

## Graphical Abstract

TAIKO DRUM GAME


[ GAME FLOW ]

Title Screen --> Song Selection --> Difficulty --> Gameplay
(UP/DOWN) (Easy/Normal/Hard/Master/Ultra) (F/J)

===================================================================
[ SCORING SYSTEM ]

PERFECT (< 0.15 sec) = 100 points x (1 + Combo/10)
GOOD (< 0.30 sec) = 50 points x (1 + Combo/10)
OK (< 0.50 sec) = 10 points x (1 + Combo/10)
MISS (> 0.50 sec) = 0 points, Combo breaks
ROLL (each hit) = 10 points, Combo continues

===================================================================
[ CONTROLS ]

[F] = Red Drum (DON)
[J] = Blue Drum (KA)

[SPACE] = Confirm / Continue / Resume from pause
[UP/DOWN] = Navigate Menus

===================================================================
 > Note:The game supports 5 difficulty levels (Easy, Normal, Hard, Master, Ultra) and dynamic BPM changes within a single song.
## Purpose

### Software Development Process Type

This project follows an **Agile** development process.

### Why Agile instead of Waterfall?

| Aspect | Waterfall | Agile (Chosen) |
|--------|-----------|----------------|
| Requirements | Fixed from start | Evolved over time |
| Feedback | Only at end | Continuous |
| Flexibility | Low | High |
| Delivery | Single final product | Multiple working increments |

This game started as a simple rhythm game and gradually added features:  
`Basic gameplay → Scoring & Combo → Audio → BPM changes → Difficulty levels → Roll notes → Result screen → Pause & resume`

Agile allowed me to test each feature immediately and adjust based on real feedback.

### Possible Usage (Target Market)

- **Casual gamers** looking for a free rhythm game
- **Music game enthusiasts** who enjoy timing-based challenges
- **Students learning Python/Pygame** as a reference project
- **Offline entertainment** on Windows/Linux/macOS

## Software Development Plan

### Development Process

The project was developed in **5 iterations**:

| Iteration | Focus | Deliverable |
|-----------|-------|-------------|
| 1 | Core game loop | Notes scrolling, hit detection |
| 2 | Scoring & UI | Score, Combo, Menus |
| 3 | Audio & Effects | Drum sounds, BGM, visual effects |
| 4 | Advanced features | BPM changes, Roll notes, Pause |
| 5 | Polish & Documentation | Result screen, Multiple difficulties, README |

### Members (Roles & Responsibilities)

Since this is an individual project, **one person** handled all roles:

| Role | Responsibility |
|------|----------------|
| Project Manager | Planning, timeline, feature prioritization |
| Programmer | All Python/Pygame coding, algorithm design |
| Tester | Manual testing, bug fixing, balancing |
| Documenter | README, comments, GitHub management |
| Artist/Designer | UI layout, colors, effects |

**Portion**: 100% completed by Leichonlam.

### Schedule

| Phase | Duration | Tasks |
|-------|----------|-------|
| Planning | 1 day | Define core mechanics, choose tech stack |
| Core development | 3 days | Game loop, notes, collision, scoring |
| Audio & UI | 2 days | Sound effects, menus, difficulty selection |
| Advanced features | 2 days | BPM changes, Roll notes, pause/resume |
| Testing & Polish | 1 day | Bug fixes, visual improvements, result screen |
| Documentation | 1 day | README, GitHub, demo video |

**Total:** ~10 days

### Algorithm

#### 1. Note Movement
x = target_x + (note.time - current_time) × speed

text
Notes start at x=800 (right edge) and move toward x=100 (left target).

#### 2. Hit Judgment
diff = abs(current_time - note.time)
if diff < 0.15 → PERFECT
elif diff < 0.30 → GOOD
elif diff < 0.50 → OK
else → MISS

text

#### 3. Score with Combo
score_add = base_score × (1 + combo ÷ 10)

text

#### 4. Beat to Time Conversion (BPM Changes)
For each tempo change `(beat, bpm)`:
time = offset + Σ (beat_difference × (60 / bpm))

text
This allows variable BPM within a single song.

#### 5. Roll Notes (Long notes)
- Scroll from right to left like normal notes
- Active during `[start_time, end_time]`
- Each hit gives +10 points, no penalty for missing
- Visual: yellow bar that grows longer as time progresses

### Current Status of Your Software

✅ **Fully functional pilot version**

| Feature | Status |
|---------|--------|
| Title screen | ✅ Complete |
| Song selection | ✅ Supports multiple songs |
| 5 difficulty levels | ✅ Easy, Normal, Hard, Master, Ultra |
| Note scrolling | ✅ Red/blue circles, yellow roll bars |
| Hit detection | ✅ Perfect/Good/OK/Miss |
| Scoring & Combo | ✅ With multiplier |
| Drum sounds | ✅ Don/Ka WAV files |
| Background music | ✅ Menu BGM + song BGM |
| BPM changes | ✅ Tempo table support |
| Pause & resume | ✅ Auto-pause on focus loss, 3s resume countdown |
| Result screen | ✅ Statistics, EXIT button (5s delay) |
| Portability | ✅ Uses relative paths, `__file__` |

### Future Plan

| Feature | Priority | Description |
|---------|----------|-------------|
| **.tja file support** | High | Load official Taiko charts directly |
| **High score saving** | Medium | Store best scores locally |
| **More songs** | Medium | Add community-made charts |
| **Particle effects** | Low | Explosions on PERFECT hit |
| **Multiplayer** | Low | Two-player local competition |
| **Packaging as EXE** | Low | Single-file executable for Windows |

## Installation

### Prerequisites
- Python 3.12+
- pip

### Steps

```bash
pip install pygame-ce
git clone https://github.com/leichonlam0906-source/taiko-drum-game.git
cd taiko-drum-game
python taiko_game.py
File Structure
text
taiko-drum-game/
├── taiko_game.py
├── README.md
├── sounds/
│   ├── Don.wav
│   └── Katsu.wav
├── bgm/
│   ├── Nebulite - Breath (freetouse.com).mp3
│   └── Walen - Nostalgia Gaming (freetouse.com).mp3
├── songs/
│   └── (MP3 files)
└── levels/
    └── (song folder)/
        ├── config.json
        ├── Easy.json
        ├── Normal.json
        ├── Hard.json
        ├── Master.json
        └── Ultra.json
Example JSON
config.json
json
{
    "title": "Example Song",
    "offset": 0.0,
    "bgm": "songs/example.mp3",
    "tempo_changes": [[1.0, 120]]
}
Easy.json
json
{
    "notes": [
        [1.0, "red"],
        [2.0, "blue"],
        [4.0, "roll_start", 6.0, "roll_end"]
    ]
}
Developer
Name: Leichonlam
GitHub: leichonlam0906-source
Date: 2026

Declaration
This project was developed as a coursework submission. All assets are used for educational purposes only.